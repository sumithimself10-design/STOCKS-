from fastapi import APIRouter, HTTPException

from app.engines.fundamentals_engine import FundamentalsEngine
from app.routers.qglp import _to_quarterly_records
from app.schemas.schemas import FundamentalsOut
from app.services.data_fetcher import data_fetcher

router = APIRouter(prefix="/api/v1/fundamentals", tags=["Fundamentals"])
engine = FundamentalsEngine()


@router.get("/{ticker}", response_model=FundamentalsOut)
async def get_fundamentals(ticker: str, exchange: str = "NSE"):
    normalized = data_fetcher.normalize_ticker(ticker, exchange)

    quarterly_df = data_fetcher.get_quarterly_financials(normalized)
    if quarterly_df.empty:
        raise HTTPException(status_code=404, detail=f"No financial data found for {normalized}")
    records = _to_quarterly_records(quarterly_df)

    price_df = data_fetcher.get_price_history(normalized, lookback_days=30)
    if price_df.empty:
        raise HTTPException(status_code=404, detail=f"No price data found for {normalized}")
    latest_price = float(price_df["close"].iloc[-1])

    eps, current_pe = data_fetcher.get_trailing_eps_and_pe(normalized)
    interest_expenses = [0.0]  # placeholder until parsed from the income-statement DataFrame

    result = engine.compute(
        price=latest_price,
        trailing_eps=eps,
        historical_pe=[current_pe] if current_pe else [],
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
