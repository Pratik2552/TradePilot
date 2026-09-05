"""
TradePilot — Abstract Market Data Provider

Today: YahooProvider (wraps the existing data/downloader.py).
Tomorrow: NSEProvider, PolygonProvider, AlpacaProvider.

Strategies and services call this interface. They never know
where the data comes from.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class BaseMarketProvider(ABC):
    """Abstract market data provider."""

    @abstractmethod
    def get_ohlcv(self, symbol: str, refresh: bool = True) -> pd.DataFrame:
        """
        Return OHLCV DataFrame for the given symbol.
        Columns: Date, Open, High, Low, Close, Volume
        Args:
            symbol: Ticker symbol (e.g. "RELIANCE.NS")
            refresh: If True, update cache with latest candles
        """

    @abstractmethod
    def get_cached_ohlcv(self, symbol: str) -> pd.DataFrame:
        """
        Return cached OHLCV data without making any network requests.
        Used by the backtester which works on already-cached data.
        """

    @abstractmethod
    def get_symbols(self) -> list[str]:
        """Return the full list of available symbols for this provider."""

    @abstractmethod
    def refresh_universe(self) -> None:
        """Refresh the symbol universe (e.g. re-fetch NSE symbol list)."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable name of this provider."""
