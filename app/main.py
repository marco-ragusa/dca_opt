"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.routes import rebalance
from app.core.exceptions import MarketDataError, market_data_error_handler
from app.core.log_config import setup_logging

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield


app = FastAPI(title="DCA Rebalancer API", version="2.0.0", lifespan=lifespan)
app.add_exception_handler(MarketDataError, market_data_error_handler)
app.include_router(rebalance.router, prefix="/v1")
