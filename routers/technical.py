from fastapi import APIRouter, HTTPException

from app.engines.technical_engine import TechnicalEngine
from app.schemas.schemas import TechnicalSignalOut
from app.services.data_fetcher import data_fetcher

router = APIRouter(prefix="/api/v1/technical", tags=["Technical"])
engine = TechnicalEngine()


@router.get("/{ticker}", response_model=TechnicalSignalOut)
async def get_technical_signal(ticker: str, exchange: str = "NSE"):
    normalized = data_fetcher.normalize_ticker(ticker, exchange)
    price_df = data_fetcher.get_price_history(normalized)

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
