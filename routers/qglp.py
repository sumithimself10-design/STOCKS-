from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.database import get_db
from app.engines.qglp_engine import QGLPEngine
from app.schemas.schemas import QGLPBreakdown
from app.services.cache import cache_get, cache_set
from app.services.data_fetcher import data_fetcher
from app.services.financial_mapper import to_quarterly_records
from app.services.price_repository import get_pe_median

router = APIRouter(prefix="/api/v1/qglp", tags=["QGLP"])
settings = get_settings()


@router.get("/{ticker}", response_model=QGLPBreakdown)
async def get_qglp_score(ticker: str, exchange: str = "NSE", db: AsyncSession = Depends(get_db)):
    normalized = data_fetcher.normalize_ticker(ticker, exchange)

    cache_key = f"qglp:{normalized}"
    cached = await cache_get(cache_key)
    if cached:
        return QGLPBreakdown(**cached)

    quarterly_df = data_fetcher.get_quarterly_financials(normalized)
    if quarterly_df.empty:
        raise HTTPException(status_code=404, detail=f"No financial data found for {normalized}")

    records = to_quarterly_records(quarterly_df)
    eps, current_pe = data_fetcher.get_trailing_eps_and_pe(normalized)

    pe_5yr_median, is_full_history = await get_pe_median(db, normalized)
    extra_notes = []
    if pe_5yr_median is None:
        # No accumulated snapshots yet (fresh deploy, cron hasn't run) — fall
        # back to current PE rather than blocking the whole score, but say so.
        pe_5yr_median = current_pe
        extra_notes.append(
            "Price: no PE history accumulated yet, using current PE as a placeholder "
            "until the daily refresh job has run for a while"
        )
    elif not is_full_history:
        extra_notes.append("Price: PE median is based on under a year of accumulated history so far")

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
        notes=[*result.notes, *extra_notes],
    )
    await cache_set(cache_key, payload.model_dump(), settings.fundamentals_cache_ttl_seconds)
    return payload
