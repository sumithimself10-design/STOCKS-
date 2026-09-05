import httpx
from fastapi import APIRouter, HTTPException

from core.config import get_settings
from services.cache import cache_get, cache_set

router = APIRouter(prefix="/api/v1/news", tags=["News"])
settings = get_settings()

NEWS_CACHE_TTL_SECONDS = 60 * 30  # news moves faster than fundamentals, shorter TTL


@router.get("/{company_name}")
async def get_stock_news(company_name: str, limit: int = 8):
    if not settings.news_api_key:
        raise HTTPException(
            status_code=503,
            detail="NEWS_API_KEY not configured — set it in the backend environment to enable news",
        )

    cache_key = f"news:{company_name.lower()}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": f'"{company_name}"',
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": limit,
                "apiKey": settings.news_api_key,
            },
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="News provider request failed")

    articles = resp.json().get("articles", [])
    result = [
        {
            "title": a["title"],
            "source": a["source"]["name"],
            "url": a["url"],
            "published_at": a["publishedAt"],
        }
        for a in articles
    ]
    await cache_set(cache_key, result, NEWS_CACHE_TTL_SECONDS)
    return result
