"""
TradePilot — CSV Repository

The ONLY component that reads or writes CSV files.
All other layers are completely CSV-unaware.

File mapping (relative to settings.results_path):
    fresh_crossovers.csv           — scanner output
    backtest_trades.csv            — backtester trades
    equity_curve.csv               — portfolio simulator equity
    performance_summary.csv        — aggregated metrics
    portfolio_summary.csv          — capital summary
    exit_summary.csv               — exit reason counts
    entered_positions_status.csv   — live position status
    watchlist.json                 — watchlisted symbols
    strategies/{id}/config.json    — per-strategy config overrides

Note: The engine currently writes to a FLAT results/ directory.
      This repository reads from there. Multi-strategy isolation
      will use strategies/{id}/ subdirectories (already scaffolded
      in settings.strategies_config_path).
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

import pandas as pd

from app.core.config import get_settings
from app.core.exceptions import RepositoryError
from app.core.logging import get_logger
from app.infrastructure.repositories.base import BaseRepository

logger = get_logger(__name__)
_write_lock = threading.Lock()  # Protect concurrent CSV writes


class CSVRepository(BaseRepository):
    """
    CSV-backed repository. Thread-safe for reads; write-locked for writes.
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._results = self._settings.results_path

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _csv(self, filename: str) -> Path:
        return self._results / filename

    def _read_csv(self, filename: str) -> pd.DataFrame:
        path = self._csv(filename)
        if not path.exists():
            return pd.DataFrame()
        try:
            return pd.read_csv(path)
        except Exception as exc:
            logger.warning(f"CSVRepository: could not read {filename}: {exc}")
            return pd.DataFrame()

    def _to_records(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        if df.empty:
            return []
        # Convert NaN → None so JSON serialization works
        return df.where(pd.notna(df), None).to_dict(orient="records")

    def _read_json(self, path: Path, default: Any = None) -> Any:
        if not path.exists():
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.warning(f"CSVRepository: could not read {path}: {exc}")
            return default

    def _write_json(self, path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with _write_lock:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

    # ------------------------------------------------------------------
    # Scanner / Crossover Results
    # ------------------------------------------------------------------

    def load_fresh_crossovers(
        self, strategy_id: str, user_id: str = "default"
    ) -> list[dict[str, Any]]:
        df = self._read_csv("fresh_crossovers.csv")
        return self._to_records(df)

    def save_fresh_crossovers(
        self,
        strategy_id: str,
        crossovers: list[dict[str, Any]],
        user_id: str = "default",
    ) -> None:
        path = self._csv("fresh_crossovers.csv")
        with _write_lock:
            pd.DataFrame(crossovers).to_csv(path, index=False)

    # ------------------------------------------------------------------
    # Backtest Trades
    # ------------------------------------------------------------------

    def load_backtest_trades(
        self, strategy_id: str, user_id: str = "default"
    ) -> list[dict[str, Any]]:
        df = self._read_csv("backtest_trades.csv")
        return self._to_records(df)

    # ------------------------------------------------------------------
    # Equity Curve
    # ------------------------------------------------------------------

    def load_equity_curve(
        self, strategy_id: str, user_id: str = "default"
    ) -> list[dict[str, Any]]:
        df = self._read_csv("equity_curve.csv")
        # equity_curve.csv has columns: Date, Cash, Invested, Portfolio, Open Positions
        # Ensure the Date column is named correctly
        if not df.empty and "Date" not in df.columns and len(df.columns) >= 4:
            df.columns = ["Date", "Cash", "Invested", "Portfolio", "Open Positions"][:len(df.columns)]
        return self._to_records(df)

    # ------------------------------------------------------------------
    # Performance Summary
    # ------------------------------------------------------------------

    def load_performance_summary(
        self, strategy_id: str, user_id: str = "default"
    ) -> dict[str, Any]:
        df = self._read_csv("performance_summary.csv")
        if df.empty:
            return {}
        return df.iloc[0].where(pd.notna(df.iloc[0]), None).to_dict()

    # ------------------------------------------------------------------
    # Portfolio Summary
    # ------------------------------------------------------------------

    def load_portfolio_summary(
        self, strategy_id: str, user_id: str = "default"
    ) -> dict[str, Any]:
        df = self._read_csv("portfolio_summary.csv")
        if df.empty:
            return {}
        return df.iloc[0].where(pd.notna(df.iloc[0]), None).to_dict()

    # ------------------------------------------------------------------
    # Exit Summary
    # ------------------------------------------------------------------

    def load_exit_summary(
        self, strategy_id: str, user_id: str = "default"
    ) -> list[dict[str, Any]]:
        df = self._read_csv("exit_summary.csv")
        return self._to_records(df)

    # ------------------------------------------------------------------
    # Entered Positions
    # ------------------------------------------------------------------

    def load_entered_positions(
        self, strategy_id: str, user_id: str = "default"
    ) -> list[dict[str, Any]]:
        df = self._read_csv("entered_positions_status.csv")
        return self._to_records(df)

    def save_entered_positions(
        self,
        strategy_id: str,
        positions: list[dict[str, Any]],
        user_id: str = "default",
    ) -> None:
        path = self._csv("entered_positions_status.csv")
        with _write_lock:
            pd.DataFrame(positions).to_csv(path, index=False)

    # ------------------------------------------------------------------
    # Watchlist (JSON)
    # ------------------------------------------------------------------

    def _watchlist_path(self, strategy_id: str, user_id: str) -> Path:
        return self._settings.watchlist_path

    def load_watchlist(
        self, strategy_id: str, user_id: str = "default"
    ) -> list[str]:
        data = self._read_json(
            self._watchlist_path(strategy_id, user_id), default={}
        )
        if isinstance(data, dict):
            return data.get(strategy_id, [])
        return []

    def toggle_watchlist(
        self, strategy_id: str, symbol: str, user_id: str = "default"
    ) -> bool:
        path = self._watchlist_path(strategy_id, user_id)
        data = self._read_json(path, default={})
        if not isinstance(data, dict):
            data = {}

        symbols: list[str] = data.get(strategy_id, [])
        if symbol in symbols:
            symbols.remove(symbol)
            new_state = False
        else:
            symbols.append(symbol)
            new_state = True

        data[strategy_id] = symbols
        self._write_json(path, data)
        return new_state

    # ------------------------------------------------------------------
    # Strategy Config
    # ------------------------------------------------------------------

    def _config_path(self, strategy_id: str, user_id: str) -> Path:
        return (
            self._settings.strategies_config_path
            / strategy_id
            / "config.json"
        )

    def load_strategy_config(
        self, strategy_id: str, user_id: str = "default"
    ) -> dict[str, Any] | None:
        return self._read_json(self._config_path(strategy_id, user_id))

    def save_strategy_config(
        self,
        strategy_id: str,
        config: dict[str, Any],
        user_id: str = "default",
    ) -> None:
        self._write_json(self._config_path(strategy_id, user_id), config)
