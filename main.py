from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.database import Base, engine
from app.routers import fundamentals, news, qglp, simulator, stocks, technical

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dev convenience only — use Alembic migrations for anything beyond local dev
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],  # set FRONTEND_ORIGIN env var to your Vercel URL in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router)
app.include_router(qglp.router)
app.include_router(technical.router)
app.include_router(fundamentals.router)
app.include_router(simulator.router)
app.include_router(news.router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}
