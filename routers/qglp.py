from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.engines.qglp_engine import QGLPEngine, QuarterlyRecord
from app.schemas.schemas import QGLPBreakdown
from app.services.cache import cache_get, cache_set
from app.services.data_fetcher import data_fetcher

router = APIRouter(prefix="/api/v1/qglp", tags=["QGLP"])
settings = get_settings()


@router.get("/{ticker}", response_model=QGLPBreakdown)
async def get_qglp_score(ticker: str, exchange: str = "NSE"):
    normalized = data_fetcher.normalize_ticker(ticker, exchange)

    cache_key = f"qglp:{normalized}"
    cached = await cache_get(cache_key)
    if cached:
        return QGLPBreakdown(**cached)

    quarterly_df = data_fetcher.get_quarterly_financials(normalized)
    if quarterly_df.empty:
        raise HTTPException(status_code=404, detail=f"No financial data found for {normalized}")

    records = _to_quarterly_records(quarterly_df)

    eps, current_pe = data_fetcher.get_trailing_eps_and_pe(normalized)
    # historical PE series would come from a stored price+EPS history table in production;
    # placeholder here uses current PE alone until that table is populated
    pe_5yr_median = current_pe

    engine = QGLPEngine(
        weight_quality=settings.qglp_weight_quality,
        weight_growth=settings.qglp_weight_growth,
        weight_longevity=settings.qglp_weight_longevity,
        weight_price=settings.qglp_weight_price,
    )
    result = engine.compute(records, current_pe=current_pe, pe_5yr_median=pe_5yr_median)

    payload = QGLPBreakdown(
        quality_score=result.quality_score,
        growth_score=result.growth_score,
        longevity_score=result.longevity_score,
        price_score=result.price_score,
        composite_score=result.composite_score,
        notes=result.notes,
    )
    await cache_set(cache_key, payload.model_dump(), settings.fundamentals_cache_ttl_seconds)
    return payload


def _to_quarterly_records(df) -> list[QuarterlyRecord]:
    """Maps the raw yfinance-shaped DataFrame into engine-ready records.
    Column names here are placeholders — pin them down once you've confirmed
    yfinance's actual column labels for Indian tickers during integration."""
    records = []
    for idx, row in df.iterrows():
        records.append(
            QuarterlyRecord(
                quarter_end=str(idx.date()) if hasattr(idx, "date") else str(idx),
                revenue=float(row.get("Total Revenue", 0) or 0),
                net_profit=float(row.get("Net Income", 0) or 0),
                eps=float(row.get("Basic EPS", 0) or 0),
                roce_pct=None,  # computed upstream or derived from EBIT/Capital Employed
                total_debt=float(row.get("Total Debt", 0) or 0),
                total_equity=float(row.get("Total Equity Gross Minority Interest", 0) or 0),
                cfo=float(row.get("Operating Cash Flow", 0) or 0),
                ebitda=float(row.get("EBITDA", 0) or 0),
            )
        )
    return records
