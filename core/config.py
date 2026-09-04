"""
Central app configuration. Reads from environment / .env so nothing
sensitive (DB creds, API keys) lives in source.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "FinAI Pro India API"
    environment: str = "development"

    database_url: str = "sqlite+aiosqlite:///./finai.db"
    redis_url: str = "redis://localhost:6379/0"

    # External data
    news_api_key: str | None = None
    gemini_api_key: str | None = None

    # Caching / throttling — Indian data sources punish hammering
    price_cache_ttl_seconds: int = 60 * 15          # 15 min for quotes
    fundamentals_cache_ttl_seconds: int = 60 * 60 * 24  # 24h, changes quarterly at most

    # QGLP scoring weights — tune independently of the scoring logic
    qglp_weight_quality: float = 0.30
    qglp_weight_growth: float = 0.30
    qglp_weight_longevity: float = 0.20
    qglp_weight_price: float = 0.20


@lru_cache
def get_settings() -> Settings:
    return Settings()
