"""Custom exception types and FastAPI exception handlers."""

from fastapi import Request
from fastapi.responses import JSONResponse


class MarketDataError(RuntimeError):
    """Raised when market prices cannot be retrieved."""


async def market_data_error_handler(request: Request, exc: MarketDataError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": str(exc)})
