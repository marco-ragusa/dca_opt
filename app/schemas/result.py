"""Pydantic v2 schemas for the HTTP response boundary."""

from decimal import ROUND_DOWN, Decimal

from pydantic import BaseModel, field_serializer

_CENT = Decimal("0.01")


def _truncate2(v: float) -> float:
    return float(Decimal(str(v)).quantize(_CENT, rounding=ROUND_DOWN))


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
    def _fmt(self, v: float) -> float:
        return _truncate2(v)


class RebalanceResponse(BaseModel):
    results: list[AssetResultOut]
    total_fees: float
    change: float

    @field_serializer("total_fees", "change")
    def _fmt(self, v: float) -> float:
        return _truncate2(v)
