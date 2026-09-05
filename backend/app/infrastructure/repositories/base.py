"""
TradePilot — Abstract Repository Protocol

The repository is the ONLY layer that knows about storage.
Everything above (services, routes) works against this protocol.
Swap CSV → SQLite → PostgreSQL by implementing a new class.

user_id is included in all methods for future multi-user support.
Today it defaults to "default" and is essentially ignored.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseRepository(ABC):
    """Abstract base for all storage backends."""

    # ------------------------------------------------------------------
    # Scanner / Crossover Results
    # ------------------------------------------------------------------

    @abstractmethod
    def load_fresh_crossovers(
        self, strategy_id: str, user_id: str = "default"
    ) -> list[dict[str, Any]]:
        """Return all fresh crossover signals from the latest scan."""

    @abstractmethod
    def save_fresh_crossovers(
        self,
        strategy_id: str,
        crossovers: list[dict[str, Any]],
        user_id: str = "default",
    ) -> None:
        """Persist scanner results."""

    # ------------------------------------------------------------------
    # Backtest Trades
    # ------------------------------------------------------------------

    @abstractmethod
    def load_backtest_trades(
        self, strategy_id: str, user_id: str = "default"
    ) -> list[dict[str, Any]]:
        """Return all completed backtest trades."""

    # ------------------------------------------------------------------
    # Equity Curve
    # ------------------------------------------------------------------

    @abstractmethod
    def load_equity_curve(
        self, strategy_id: str, user_id: str = "default"
    ) -> list[dict[str, Any]]:
        """Return daily equity curve data points."""

    # ------------------------------------------------------------------
    # Performance Summary
    # ------------------------------------------------------------------

    @abstractmethod
    def load_performance_summary(
        self, strategy_id: str, user_id: str = "default"
    ) -> dict[str, Any]:
        """Return aggregated performance metrics dict."""

    # ------------------------------------------------------------------
    # Portfolio Summary
    # ------------------------------------------------------------------

    @abstractmethod
    def load_portfolio_summary(
        self, strategy_id: str, user_id: str = "default"
    ) -> dict[str, Any]:
        """Return portfolio-level summary (capital, cash, closed trades)."""

    # ------------------------------------------------------------------
    # Exit Summary
    # ------------------------------------------------------------------

    @abstractmethod
    def load_exit_summary(
        self, strategy_id: str, user_id: str = "default"
    ) -> list[dict[str, Any]]:
        """Return exit reason breakdown."""

    # ------------------------------------------------------------------
    # Entered Positions (Live Tracking)
    # ------------------------------------------------------------------

    @abstractmethod
    def load_entered_positions(
        self, strategy_id: str, user_id: str = "default"
    ) -> list[dict[str, Any]]:
        """Return currently entered positions for live tracking."""

    @abstractmethod
    def save_entered_positions(
        self,
        strategy_id: str,
        positions: list[dict[str, Any]],
        user_id: str = "default",
    ) -> None:
        """Persist live position entries."""

    # ------------------------------------------------------------------
    # Watchlist
    # ------------------------------------------------------------------

    @abstractmethod
    def load_watchlist(
        self, strategy_id: str, user_id: str = "default"
    ) -> list[str]:
        """Return list of watchlisted symbols."""

    @abstractmethod
    def toggle_watchlist(
        self, strategy_id: str, symbol: str, user_id: str = "default"
    ) -> bool:
        """Toggle symbol watchlist status. Returns new state (True = watchlisted)."""

    # ------------------------------------------------------------------
    # Strategy Config
    # ------------------------------------------------------------------

    @abstractmethod
    def load_strategy_config(
        self, strategy_id: str, user_id: str = "default"
    ) -> dict[str, Any] | None:
        """Return saved strategy configuration overrides."""

    @abstractmethod
    def save_strategy_config(
        self,
        strategy_id: str,
        config: dict[str, Any],
        user_id: str = "default",
    ) -> None:
        """Persist strategy configuration overrides."""
