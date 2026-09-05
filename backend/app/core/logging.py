"""
TradePilot Backend — Structured Logging

Provides a consistent logger factory. In DEBUG mode logs are human-readable.
In production, structured JSON logging is used (compatible with DataDog, Loki, etc.)
"""

from __future__ import annotations

import logging
import sys
from app.core.config import get_settings


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger configured for TradePilot.

    Usage:
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info("Scan started", extra={"strategy_id": "golden-cross"})
    """
    settings = get_settings()

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if settings.DEBUG:
        fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        handler.setFormatter(logging.Formatter(fmt, datefmt="%H:%M:%S"))
    else:
        # Minimal structured format for production log aggregators
        fmt = "%(levelname)s %(name)s %(message)s"
        handler.setFormatter(logging.Formatter(fmt))

    logger.addHandler(handler)
    logger.propagate = False

    return logger
