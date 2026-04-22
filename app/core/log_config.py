"""Logging configuration."""

import logging

from app.core.config import settings


def setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(levelname)s: %(name)s: %(message)s",
    )
