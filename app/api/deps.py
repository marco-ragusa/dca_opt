"""FastAPI dependency injection for shared resources."""

from functools import lru_cache

from app.market_data.base import AbstractMarketDataProvider
from app.market_data.yfinance_provider import YFinanceProvider


@lru_cache
def get_market_provider() -> AbstractMarketDataProvider:
    return YFinanceProvider()
