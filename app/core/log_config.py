"""Logging configuration."""

import logging

from app.core.config import settings


def setup_logging() -> None:
    logging.basicConfig(
        level=settings.log_level,
        format="%(levelname)s: %(name)s: %(message)s",
    )
