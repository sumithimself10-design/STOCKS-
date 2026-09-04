from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Stock

router = APIRouter(prefix="/api/v1/stocks", tags=["Stocks"])


@router.get("/search")
async def search_stocks(q: str, db: AsyncSession = Depends(get_db)):
    """Autocomplete against the locally-cached NSE/BSE symbol table —
    never hit yfinance/NSE live for a search-as-you-type box."""
    stmt = select(Stock).where(Stock.name.ilike(f"%{q}%") | Stock.ticker.ilike(f"%{q}%")).limit(10)
    result = await db.execute(stmt)
    stocks = result.scalars().all()
    return [{"ticker": s.ticker, "name": s.name, "exchange": s.exchange} for s in stocks]
