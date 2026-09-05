from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.engines.technical_engine import TechnicalEngine
from app.schemas.schemas import TechnicalSignalOut
from app.services.data_fetcher import data_fetcher
from app.services.price_repository import get_price_series

router = APIRouter(prefix="/api/v1/technical", tags=["Technical"])
engine = TechnicalEngine()


@router.get("/{ticker}", response_model=TechnicalSignalOut)
async def get_technical_signal(ticker: str, exchange: str = "NSE", db: AsyncSession = Depends(get_db)):
    normalized = data_fetcher.normalize_ticker(ticker, exchange)
    price_df = await get_price_series(db, normalized)

    if price_df.empty:
        raise HTTPException(status_code=404, detail=f"No price data found for {normalized}")

    result = engine.compute(price_df)
    return TechnicalSignalOut(
        ticker=normalized,
        close=result.close,
        sma_200=result.sma_200,
        price_vs_sma200_pct=result.price_vs_sma200_pct,
        volume_confirmed=result.volume_confirmed,
        signal=result.signal,
        rsi_14=result.rsi_14,
    )
