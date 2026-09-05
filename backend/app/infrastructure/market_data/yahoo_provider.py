"""
TradePilot — Yahoo Finance Market Provider

Wraps the existing data/downloader.py engine module.
Handles sys.path setup so the engine can be imported from the backend.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from app.core.config import get_settings
from app.core.logging import get_logger
from app.infrastructure.market_data.base import BaseMarketProvider

logger = get_logger(__name__)


def _ensure_engine_path() -> None:
    """Add the engine root to sys.path so engine modules can be imported."""
    settings = get_settings()
    engine_root = str(settings.engine_root_path)
    if engine_root not in sys.path:
        sys.path.insert(0, engine_root)


class YahooProvider(BaseMarketProvider):
    """
    Market data provider backed by yfinance + local CSV cache.
    Delegates to the existing data/downloader.py engine module.
    """

    def __init__(self) -> None:
        _ensure_engine_path()
        self._settings = get_settings()

    @property
    def provider_name(self) -> str:
        return "Yahoo Finance (yfinance)"

    def get_ohlcv(self, symbol: str, refresh: bool = True) -> pd.DataFrame:
        try:
            from data.downloader import get_stock_data
            return get_stock_data(symbol)
        except Exception as exc:
            logger.error(f"YahooProvider.get_ohlcv({symbol}): {exc}")
            return pd.DataFrame()

    def get_cached_ohlcv(self, symbol: str) -> pd.DataFrame:
        try:
            from data.downloader import get_cached_stock_data
            return get_cached_stock_data(symbol)
        except Exception as exc:
            logger.error(f"YahooProvider.get_cached_ohlcv({symbol}): {exc}")
            return pd.DataFrame()

    def get_symbols(self) -> list[str]:
        try:
            from data.universe import load_symbols
            return load_symbols()
        except Exception as exc:
            logger.error(f"YahooProvider.get_symbols(): {exc}")
            return []

    def refresh_universe(self) -> None:
        try:
            from data.universe import refresh_universe
            refresh_universe()
        except Exception as exc:
            logger.error(f"YahooProvider.refresh_universe(): {exc}")


# ---- Singleton -----------------------------------------------------------

_yahoo_provider: YahooProvider | None = None


def get_yahoo_provider() -> YahooProvider:
    global _yahoo_provider
    if _yahoo_provider is None:
        _yahoo_provider = YahooProvider()
    return _yahoo_provider
