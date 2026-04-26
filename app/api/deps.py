"""FastAPI dependency injection for shared resources."""

from functools import lru_cache

from app.core.config import get_settings
from app.market_data.base import AbstractMarketDataProvider
from app.market_data.cache import AbstractCache, LocalCache
from app.market_data.cached_provider import CachedMarketDataProvider
from app.market_data.yfinance_provider import YFinanceProvider


@lru_cache(maxsize=1)
def _build_cache() -> AbstractCache:
    s = get_settings()
    if s.cache_backend == "redis":
        if not s.redis_url:
            raise ValueError(
                "REDIS_URL must be set when CACHE_BACKEND=redis. "
                "Pass it as an environment variable."
            )
        from app.market_data.redis_cache import RedisCache
        return RedisCache(url=s.redis_url, ttl_seconds=s.cache_ttl_seconds)
    return LocalCache(ttl_seconds=s.cache_ttl_seconds)


@lru_cache(maxsize=1)
def _build_provider() -> AbstractMarketDataProvider:
    return CachedMarketDataProvider(YFinanceProvider(), _build_cache())


def get_market_provider() -> AbstractMarketDataProvider:
    return _build_provider()
