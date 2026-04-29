# app/api/v1/routes/tickers.py
"""GET /v1/tickers/search endpoint."""

import asyncio
import logging

import yfinance as yf
from fastapi import APIRouter, HTTPException, Query

from app.schemas.ticker import TickerResult, TickerSearchResponse

router = APIRouter(tags=["tickers"])
logger = logging.getLogger(__name__)

_ALLOWED_TYPES = {"EQUITY", "ETF", "MUTUALFUND", "CRYPTOCURRENCY", "CURRENCY"}


def _fetch_quotes(q: str) -> list[dict]:
    return yf.Search(q).quotes or []


@router.get("/tickers/search", response_model=TickerSearchResponse)
async def search_tickers(q: str = Query(..., min_length=2)) -> TickerSearchResponse:
    loop = asyncio.get_running_loop()
    try:
        quotes = await loop.run_in_executor(None, _fetch_quotes, q)
    except Exception:
        logger.exception("yfinance Search failed for query %r", q)
        raise HTTPException(status_code=503, detail="Market data unavailable")

    results = [
        TickerResult(
            ticker=quote.get("symbol", ""),
            name=quote.get("shortname") or quote.get("longname") or "",
            exchange=quote.get("exchange", ""),
            type=quote.get("quoteType", ""),
        )
        for quote in quotes
        if quote.get("quoteType") in _ALLOWED_TYPES
    ]
    return TickerSearchResponse(results=results)
