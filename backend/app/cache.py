import json
import hashlib
from typing import Optional, Any
import redis.asyncio as aioredis
from .config import settings

redis_client: Optional[aioredis.Redis] = None


async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = await aioredis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
            decode_responses=True,
        )
    return redis_client


def _make_key(prefix: str, params: dict = None) -> str:
    raw = f"{prefix}:{json.dumps(params or {}, sort_keys=True)}"
    return hashlib.md5(raw.encode()).hexdigest()


async def cache_get(prefix: str, params: dict = None) -> Optional[Any]:
    try:
        r = await get_redis()
        key = _make_key(prefix, params)
        data = await r.get(key)
        return json.loads(data) if data else None
    except Exception:
        return None


async def cache_set(prefix: str, data: Any, params: dict = None, ttl: int = None):
    try:
        r = await get_redis()
        key = _make_key(prefix, params)
        if hasattr(data, 'model_dump'):
            data = data.model_dump()
        elif hasattr(data, 'dict'):
            data = data.dict()
        await r.setex(key, ttl or settings.CACHE_TTL, json.dumps(data, default=str))
    except Exception:
        pass


async def cache_invalidate(pattern: str):
    try:
        r = await get_redis()
        keys = await r.keys(f"{pattern}:*")
        if keys:
            await r.delete(*keys)
    except Exception:
        pass
