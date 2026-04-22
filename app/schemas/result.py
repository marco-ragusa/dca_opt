"""Pydantic v2 schemas for the HTTP response boundary."""

from pydantic import BaseModel, field_serializer


class AssetResultOut(BaseModel):
    id: int
    ticker: str
    current_percentage: float
    desired_percentage: float
    shares: float
    allocated: float
    ticker_price: float
    fees: float
    buy: int

    @field_serializer(
        "current_percentage", "desired_percentage", "shares",
        "allocated", "ticker_price", "fees",
    )
    def _truncate2(self, v: float) -> float:
        return int(v * 100) / 100


class RebalanceResponse(BaseModel):
    results: list[AssetResultOut]
    total_fees: float
    change: float

    @field_serializer("total_fees", "change")
    def _truncate2(self, v: float) -> float:
        return int(v * 100) / 100
