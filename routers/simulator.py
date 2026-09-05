from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_api_key
from app.db.database import get_db
from app.db.models import SimulatedTrade, Stock
from app.schemas.schemas import SimulatedTradeIn, SimulatedTradeOut
from app.services.data_fetcher import data_fetcher

router = APIRouter(prefix="/api/v1/simulator", tags=["Simulator"])


@router.post("/trades", response_model=SimulatedTradeOut, dependencies=[Depends(require_api_key)])
async def log_trade(trade: SimulatedTradeIn, db: AsyncSession = Depends(get_db)):
    normalized = data_fetcher.normalize_ticker(trade.ticker, "NSE")
    stock = (await db.execute(select(Stock).where(Stock.ticker == normalized))).scalar_one_or_none()
    if not stock:
        raise HTTPException(status_code=404, detail=f"{normalized} is not tracked yet")

    record = SimulatedTrade(
        user_id=trade.user_id,
        stock_id=stock.id,
        action=trade.action.upper(),
        quantity=trade.quantity,
        entry_price=trade.entry_price,
        entry_date=trade.entry_date,
        note=trade.note,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return SimulatedTradeOut(**trade.model_dump(), id=record.id)


@router.get("/trades/{user_id}", response_model=list[SimulatedTradeOut])
async def list_trades(user_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(SimulatedTrade, Stock).join(Stock).where(SimulatedTrade.user_id == user_id)
    rows = (await db.execute(stmt)).all()

    out = []
    for trade, stock in rows:
        price_df = data_fetcher.get_price_history(stock.ticker, lookback_days=5)
        current_price = float(price_df["close"].iloc[-1]) if not price_df.empty else None
        return_pct = (
            round(((current_price - trade.entry_price) / trade.entry_price) * 100, 2)
            if current_price else None
        )
        out.append(
            SimulatedTradeOut(
                id=trade.id, user_id=trade.user_id, ticker=stock.ticker, action=trade.action,
                quantity=trade.quantity, entry_price=trade.entry_price, entry_date=trade.entry_date,
                note=trade.note, current_price=current_price, unrealized_return_pct=return_pct,
            )
        )
    return out
