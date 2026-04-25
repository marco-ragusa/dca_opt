"""FastAPI dependency injection for shared resources."""

from functools import lru_cache

from app.core.config import settings
from app.market_data.base import AbstractMarketDataProvider
from app.market_data.cache import AbstractCache, LocalCache
from app.market_data.cached_provider import CachedMarketDataProvider
from app.market_data.yfinance_provider import YFinanceProvider


@lru_cache(maxsize=1)
def _build_cache() -> AbstractCache:
    if settings.cache_backend == "redis":
        if not settings.redis_url:
            raise ValueError(
                "REDIS_URL must be set when CACHE_BACKEND=redis. "
                "Pass it as an environment variable."
            )
        from app.market_data.redis_cache import RedisCache
        return RedisCache(url=settings.redis_url, ttl_seconds=settings.cache_ttl_seconds)
    return LocalCache(ttl_seconds=settings.cache_ttl_seconds)


@lru_cache(maxsize=1)
def _build_provider() -> AbstractMarketDataProvider:
    return CachedMarketDataProvider(YFinanceProvider(), _build_cache())


def get_market_provider() -> AbstractMarketDataProvider:
    return _build_provider()
