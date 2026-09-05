"""
Run once (and again whenever you extend NSE_UNIVERSE):

    python -m app.scripts.seed_stocks

Idempotent — skips tickers that already exist rather than erroring.
"""
import asyncio

from sqlalchemy import select

from data.nse_universe import NSE_UNIVERSE
from db.database import AsyncSessionLocal, Base, engine
from db.models import Stock


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        existing = (await db.execute(select(Stock.ticker))).scalars().all()
        existing_set = set(existing)

        added = 0
        for entry in NSE_UNIVERSE:
            ticker = f"{entry['ticker']}.NS"
            if ticker in existing_set:
                continue
            db.add(Stock(ticker=ticker, exchange="NSE", name=entry["name"], sector=entry["sector"]))
            added += 1

        await db.commit()
        print(f"Seeded {added} new stocks ({len(existing_set)} already present).")


if __name__ == "__main__":
    asyncio.run(seed())
