"""Abstract interface for market data providers."""

from abc import ABC, abstractmethod


class AbstractMarketDataProvider(ABC):
    @abstractmethod
    def get_prices(self, tickers: list[str]) -> dict[str, float]: ...
