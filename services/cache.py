import json
from typing import Any

import redis.asyncio as redis

from core.config import get_settings

settings = get_settings()
_redis = redis.from_url(settings.redis_url, decode_responses=True)


async def cache_get(key: str) -> Any | None:
    raw = await _redis.get(key)
    return json.loads(raw) if raw else None


async def cache_set(key: str, value: Any, ttl_seconds: int) -> None:
    await _redis.set(key, json.dumps(value), ex=ttl_seconds)
