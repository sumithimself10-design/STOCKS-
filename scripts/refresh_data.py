"""
The actual data-fetching pipeline. Run on a schedule (daily after market
close is enough for EOD prices; quarterly financials only need a refresh
around results season) — see DEPLOYMENT.md for how to schedule this on
Railway/Render as a cron job rather than baking it into the API process.

    python -m app.scripts.refresh_data

Deliberately sequential with a delay between tickers, not concurrent —
yfinance/NSE apply undocumented IP-based throttling, and a burst of
parallel requests is the fastest way to get temporarily blocked.
"""
import asyncio
import logging
import time
from datetime import date

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from core.config import get_settings
from db.database import AsyncSessionLocal
from db.models import PERatioSnapshot, PriceBar, QuarterlyFinancial, Stock
from services.data_fetcher import data_fetcher
from services.financial_mapper import get_interest_expense, to_quarterly_records

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()

DELAY_BETWEEN_TICKERS_SECONDS = 2.0


async def refresh_prices(db, stock: Stock) -> int:
    df = data_fetcher.get_price_history(stock.ticker, lookback_days=400)
    if df.empty:
        logger.warning("No price data for %s, skipping", stock.ticker)
        return 0

    insert_fn = pg_insert if "postgresql" in str(db.bind.url) else sqlite_insert
    rows = [
        {
            "stock_id": stock.id,
            "trade_date": row_date,
            "open": float(row.get("open", row["close"])),
            "high": float(row.get("high", row["close"])),
            "low": float(row.get("low", row["close"])),
            "close": float(row["close"]),
            "volume": int(row["volume"]),
        }
        for row_date, row in zip(_date_range_for(df), df.to_dict("records"))
    ]
    if not rows:
        return 0

    stmt = insert_fn(PriceBar).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["stock_id", "trade_date"],
        set_={"close": stmt.excluded.close, "volume": stmt.excluded.volume},
    )
    await db.execute(stmt)
    return len(rows)


async def refresh_financials(db, stock: Stock) -> int:
    raw = data_fetcher.get_quarterly_financials(stock.ticker)
    if raw.empty:
        logger.warning("No financials for %s, skipping", stock.ticker)
        return 0

    records = to_quarterly_records(raw)
    interest_expenses = get_interest_expense(raw)
    insert_fn = pg_insert if "postgresql" in str(db.bind.url) else sqlite_insert

    rows = [
        {
            "stock_id": stock.id,
            "quarter_end": _safe_date(r.quarter_end),
            "revenue": r.revenue,
            "ebitda": r.ebitda,
            "net_profit": r.net_profit,
            "eps": r.eps,
            "total_debt": r.total_debt,
            "total_equity": r.total_equity,
            "interest_expense": interest_expenses[i] if i < len(interest_expenses) else 0.0,
            "cfo": r.cfo,
            "roce_pct": r.roce_pct,
            "promoter_holding_pct": r.promoter_holding_pct,
            "dividend_payout_pct": r.dividend_payout_pct,
        }
        for i, r in enumerate(records)
        if _safe_date(r.quarter_end) is not None
    ]
    if not rows:
        return 0

    stmt = insert_fn(QuarterlyFinancial).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["stock_id", "quarter_end"],
        set_={"revenue": stmt.excluded.revenue, "net_profit": stmt.excluded.net_profit},
    )
    await db.execute(stmt)
    return len(rows)


def _safe_date(value) -> date | None:
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _date_range_for(df):
    """yfinance's download index is a DatetimeIndex before reset_index(drop=True)
    stripped it in data_fetcher — for now approximate with today's date offset.
    Swap this for preserving the real index if you remove the drop=True upstream."""
    today = date.today()
    return [today.fromordinal(today.toordinal() - (len(df) - 1 - i)) for i in range(len(df))]


async def refresh_pe_snapshot(db, stock: Stock) -> bool:
    """One row per stock per day this runs — this is what accumulates into
    a real 'PE vs. its own history' figure over weeks/months of running the
    cron job. Skips silently if today's snapshot already exists (idempotent
    if refresh_data.py is re-run same-day)."""
    _, current_pe = data_fetcher.get_trailing_eps_and_pe(stock.ticker)
    if not current_pe or current_pe <= 0:
        return False

    insert_fn = pg_insert if "postgresql" in str(db.bind.url) else sqlite_insert
    stmt = insert_fn(PERatioSnapshot).values(
        stock_id=stock.id, snapshot_date=date.today(), pe_ratio=current_pe
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["stock_id", "snapshot_date"], set_={"pe_ratio": stmt.excluded.pe_ratio}
    )
    await db.execute(stmt)
    return True


async def main() -> None:
    async with AsyncSessionLocal() as db:
        stocks = (await db.execute(select(Stock))).scalars().all()
        if not stocks:
            logger.error("No stocks found — run `python -m app.scripts.seed_stocks` first")
            return

        for stock in stocks:
            logger.info("Refreshing %s (%s)", stock.ticker, stock.name)
            try:
                price_rows = await refresh_prices(db, stock)
                financial_rows = await refresh_financials(db, stock)
                pe_snapshot_taken = await refresh_pe_snapshot(db, stock)
                await db.commit()
                logger.info(
                    "  -> %d price bars, %d quarterly records, PE snapshot: %s",
                    price_rows, financial_rows, pe_snapshot_taken,
                )
            except Exception:
                logger.exception("Failed to refresh %s, continuing", stock.ticker)
                await db.rollback()
            time.sleep(DELAY_BETWEEN_TICKERS_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
