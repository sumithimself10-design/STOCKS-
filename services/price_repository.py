"""
Routers should prefer what's already in Postgres (populated by
scripts/refresh_data.py) over calling yfinance live. Live calls only
happen as a fallback for tickers the nightly job hasn't reached yet, or
during local dev before you've run the refresh script at all.
"""
import logging
from datetime import date, timedelta

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from statistics import median

from db.models import PERatioSnapshot, PriceBar, Stock
from services.data_fetcher import data_fetcher

logger = logging.getLogger(__name__)

MIN_ROWS_FOR_TECHNICAL = 200  # need a full SMA-200 window to trust the DB copy


async def get_stock(db: AsyncSession, ticker: str) -> Stock | None:
    result = await db.execute(select(Stock).where(Stock.ticker == ticker))
    return result.scalar_one_or_none()


async def get_price_series(db: AsyncSession, ticker: str) -> pd.DataFrame:
    """Returns a DataFrame with columns [close, volume], oldest -> newest.
    Prefers the DB; falls back to a live yfinance call if the DB doesn't
    have enough history for this ticker yet."""
    stock = await get_stock(db, ticker)
    if stock:
        result = await db.execute(
            select(PriceBar).where(PriceBar.stock_id == stock.id).order_by(PriceBar.trade_date)
        )
        bars = result.scalars().all()
        if len(bars) >= MIN_ROWS_FOR_TECHNICAL:
            return pd.DataFrame({"close": [b.close for b in bars], "volume": [b.volume for b in bars]})
        logger.info("Only %d cached price rows for %s, falling back to live fetch", len(bars), ticker)

    return data_fetcher.get_price_history(ticker)


async def get_pe_median(db: AsyncSession, ticker: str, lookback_years: int = 5) -> tuple[float | None, bool]:
    """
    Returns (median_pe, is_full_history). is_full_history is False when
    fewer than ~1 year of snapshots exist yet — the caller should surface
    that as a note rather than presenting the median as a real 5yr figure.
    """
    stock = await get_stock(db, ticker)
    if not stock:
        return None, False

    cutoff = date.today() - timedelta(days=365 * lookback_years)
    result = await db.execute(
        select(PERatioSnapshot.pe_ratio, PERatioSnapshot.snapshot_date)
        .where(PERatioSnapshot.stock_id == stock.id, PERatioSnapshot.snapshot_date >= cutoff)
        .order_by(PERatioSnapshot.snapshot_date)
    )
    rows = result.all()
    if not rows:
        return None, False

    values = [r.pe_ratio for r in rows if r.pe_ratio and r.pe_ratio > 0]
    if not values:
        return None, False

    earliest = min(r.snapshot_date for r in rows)
    is_full_history = (date.today() - earliest).days >= 365
    return round(median(values), 2), is_full_history
