from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.engines.fundamentals_engine import FundamentalsEngine
from app.schemas.schemas import FundamentalsOut
from app.services.data_fetcher import data_fetcher
from app.services.financial_mapper import get_interest_expense, to_quarterly_records
from app.services.price_repository import get_pe_median

router = APIRouter(prefix="/api/v1/fundamentals", tags=["Fundamentals"])
engine = FundamentalsEngine()


@router.get("/{ticker}", response_model=FundamentalsOut)
async def get_fundamentals(ticker: str, exchange: str = "NSE", db: AsyncSession = Depends(get_db)):
    normalized = data_fetcher.normalize_ticker(ticker, exchange)

    quarterly_df = data_fetcher.get_quarterly_financials(normalized)
    if quarterly_df.empty:
        raise HTTPException(status_code=404, detail=f"No financial data found for {normalized}")
    records = to_quarterly_records(quarterly_df)
    interest_expenses = get_interest_expense(quarterly_df)

    price_df = data_fetcher.get_price_history(normalized, lookback_days=30)
    if price_df.empty:
        raise HTTPException(status_code=404, detail=f"No price data found for {normalized}")
    latest_price = float(price_df["close"].iloc[-1])

    eps, current_pe = data_fetcher.get_trailing_eps_and_pe(normalized)

    pe_median, _ = await get_pe_median(db, normalized)
    historical_pe = [pe_median] if pe_median else ([current_pe] if current_pe else [])

    result = engine.compute(
        price=latest_price,
        trailing_eps=eps,
        historical_pe=historical_pe,
        records=records,
        interest_expenses=interest_expenses,
    )

    return FundamentalsOut(
        ticker=normalized,
        pe_ratio=result.pe_ratio,
        pe_5yr_median=result.pe_5yr_median,
        debt_to_equity=result.debt_to_equity,
        interest_coverage=result.interest_coverage,
        quarterly_revenue=result.quarterly_revenue,
        quarterly_net_profit=result.quarterly_net_profit,
        quarterly_labels=result.quarterly_labels,
    )
