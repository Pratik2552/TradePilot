"""
TradePilot — CSV Repository

The ONLY component that reads or writes CSV files.
All other layers remain CSV-unaware.

File mapping (relative to settings.results_path):

    fresh_crossovers.csv
        Scanner output.

    backtest_trades.csv
        Strategy candidates after filtration.
        Used only as a fallback for older backtests.

    executed_trades.csv
        Actual portfolio trades that have CLOSED.

    open_trades.csv
        Actual portfolio positions that are still OPEN.

    equity_curve.csv
        Portfolio equity curve.

    performance_summary.csv
        Closed-trade performance metrics.

    portfolio_summary.csv
        Portfolio capital summary.

    exit_summary.csv
        Exit reason counts.

    entered_positions_status.csv
        Live entered-position status.

    watchlist.json
        Watchlisted symbols.

    strategies/{id}/config.json
        Per-strategy config overrides.


IMPORTANT:

The frontend historically consumed "backtest trades" from one API.

After adding proper OPEN-position support, portfolio trades are now split
between:

    executed_trades.csv
    open_trades.csv

To preserve backwards compatibility with the frontend,
load_backtest_trades() combines and normalizes those two files.

This means the frontend can continue using the same API endpoint.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

import pandas as pd

from app.core.config import get_settings
from app.infrastructure.repositories.base import BaseRepository
from app.core.logging import get_logger


logger = get_logger(__name__)

_write_lock = threading.Lock()


class CSVRepository(BaseRepository):
    """
    CSV-backed repository.

    Reads are safe for concurrent usage.
    Writes are protected by a lock.
    """

    def __init__(self) -> None:

        self._settings = get_settings()

        self._results = (
            self._settings.results_path
        )

    # ==================================================
    # INTERNAL HELPERS
    # ==================================================

    def _csv(
        self,
        filename: str,
    ) -> Path:

        return (
            self._results
            / filename
        )

    # --------------------------------------------------
    # READ CSV
    # --------------------------------------------------

    def _read_csv(
        self,
        filename: str,
    ) -> pd.DataFrame:

        path = self._csv(
            filename
        )

        if not path.exists():

            logger.debug(
                "CSVRepository: "
                f"{filename} does not exist."
            )

            return pd.DataFrame()

        try:

            return pd.read_csv(
                path
            )

        except Exception as exc:

            logger.warning(
                "CSVRepository: "
                f"could not read {filename}: "
                f"{exc}"
            )

            return pd.DataFrame()

    # --------------------------------------------------
    # DATAFRAME → JSON SAFE RECORDS
    # --------------------------------------------------

    def _to_records(
        self,
        df: pd.DataFrame,
    ) -> list[dict[str, Any]]:

        if df.empty:
            return []

        # Convert dataframe to object dtype first.
        #
        # Otherwise float columns may keep NaN even
        # after calling where(..., None).
        clean = df.astype(
            object
        ).where(
            pd.notna(df),
            None,
        )

        return clean.to_dict(
            orient="records"
        )

    # --------------------------------------------------
    # JSON
    # --------------------------------------------------

    def _read_json(
        self,
        path: Path,
        default: Any = None,
    ) -> Any:

        if not path.exists():
            return default

        try:

            with open(
                path,
                "r",
                encoding="utf-8",
            ) as file:

                return json.load(
                    file
                )

        except Exception as exc:

            logger.warning(
                "CSVRepository: "
                f"could not read {path}: "
                f"{exc}"
            )

            return default

    def _write_json(
        self,
        path: Path,
        data: Any,
    ) -> None:

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with _write_lock:

            with open(
                path,
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    data,
                    file,
                    indent=2,
                    default=str,
                )

    # ==================================================
    # VALUE HELPERS
    # ==================================================

    @staticmethod
    def _valid_value(
        value: Any,
    ) -> bool:

        if value is None:
            return False

        try:

            return not pd.isna(
                value
            )

        except Exception:

            return True

    @classmethod
    def _first_value(
        cls,
        row: pd.Series,
        *columns: str,
        default: Any = None,
    ) -> Any:

        for column in columns:

            if column not in row.index:
                continue

            value = row.get(
                column
            )

            if cls._valid_value(
                value
            ):

                return value

        return default

    # ==================================================
    # NORMALIZE PORTFOLIO TRADE
    # ==================================================

    def _normalize_trade(
        self,
        row: pd.Series,
        status: str,
    ) -> dict[str, Any]:

        status = (
            str(status)
            .upper()
            .strip()
        )

        symbol = self._first_value(
            row,
            "Symbol",
            "symbol",
        )

        entry_date = self._first_value(
            row,
            "Entry Date",
            "entry_date",
        )

        entry_price = self._first_value(
            row,
            "Entry Price",
            "entry_price",
        )

        shares = self._first_value(
            row,
            "Shares",
            "Quantity",
            "Qty",
            "shares",
            "quantity",
            "qty",
            default=0,
        )

        invested = self._first_value(
            row,
            "Invested",
            "invested",
        )

        # ==================================================
        # CLOSED
        # ==================================================

        if status == "CLOSED":

            exit_date = self._first_value(
                row,
                "Exit Date",
                "exit_date",
            )

            exit_price = self._first_value(
                row,
                "Exit Price",
                "exit_price",
            )

            pnl = self._first_value(
                row,
                "Realized P&L",
                "P&L",
                "PnL",
                "pnl",
                default=0,
            )

            return_pct = self._first_value(
                row,
                "Return %",
                "return_pct",
                default=0,
            )

            current_price = None

            pnl_type = "REALIZED"

        # ==================================================
        # OPEN
        # ==================================================

        else:

            # An OPEN position deliberately has NO exit.
            exit_date = None
            exit_price = None

            current_price = (
                self._first_value(
                    row,
                    "Current Price",
                    "current_price",
                )
            )

            pnl = self._first_value(
                row,
                "Unrealized P&L",
                "P&L",
                "PnL",
                "pnl",
                default=0,
            )

            return_pct = self._first_value(
                row,
                "Unrealized Return %",
                "Return %",
                "return_pct",
                default=0,
            )

            pnl_type = "UNREALIZED"

        # ==================================================
        # COMMON
        # ==================================================

        market_value = self._first_value(
            row,
            "Market Value",
            "market_value",
        )

        holding_days = self._first_value(
            row,
            "Holding Days",
            "holding_days",
        )

        exit_reason = self._first_value(
            row,
            "Exit Reason",
            "exit_reason",
        )

        pending_exit_reason = (
            self._first_value(
                row,
                "Pending Exit Reason",
                "pending_exit_reason",
            )
        )

        mfe = self._first_value(
            row,
            "MFE %",
            "mfe",
        )

        mae = self._first_value(
            row,
            "MAE %",
            "mae",
        )

        golden_cross_date = (
            self._first_value(
                row,
                "Golden Cross Date",
                "golden_cross_date",
            )
        )

        # ==================================================
        # NORMALIZED RESULT
        #
        # Keep original-style names AND convenient aliases.
        #
        # This maximizes compatibility with the existing
        # frontend/service code.
        # ==================================================

        trade = {

            # ------------------------------------------
            # Identity
            # ------------------------------------------

            "Symbol":
                symbol,

            "symbol":
                symbol,

            "Status":
                status,

            "status":
                status,

            # ------------------------------------------
            # Entry
            # ------------------------------------------

            "Entry Date":
                entry_date,

            "entry_date":
                entry_date,

            "Entry Price":
                entry_price,

            "entry_price":
                entry_price,

            # ------------------------------------------
            # Exit
            # ------------------------------------------

            "Exit Date":
                exit_date,

            "exit_date":
                exit_date,

            "Exit Price":
                exit_price,

            "exit_price":
                exit_price,

            # ------------------------------------------
            # Current mark
            # ------------------------------------------

            "Current Price":
                current_price,

            "current_price":
                current_price,

            # ------------------------------------------
            # Quantity
            # ------------------------------------------

            "Shares":
                shares,

            "shares":
                shares,

            "Quantity":
                shares,

            "quantity":
                shares,

            "Qty":
                shares,

            "qty":
                shares,

            # ------------------------------------------
            # Capital
            # ------------------------------------------

            "Invested":
                invested,

            "invested":
                invested,

            "Market Value":
                market_value,

            "market_value":
                market_value,

            # ------------------------------------------
            # P&L
            # ------------------------------------------

            "P&L":
                pnl,

            "PnL":
                pnl,

            "pnl":
                pnl,

            "P&L Type":
                pnl_type,

            "pnl_type":
                pnl_type,

            # ------------------------------------------
            # Return
            # ------------------------------------------

            "Return %":
                return_pct,

            "return_pct":
                return_pct,

            # ------------------------------------------
            # Strategy metadata
            # ------------------------------------------

            "Holding Days":
                holding_days,

            "holding_days":
                holding_days,

            "Exit Reason":
                exit_reason,

            "exit_reason":
                exit_reason,

            "Pending Exit Reason":
                pending_exit_reason,

            "pending_exit_reason":
                pending_exit_reason,

            "Golden Cross Date":
                golden_cross_date,

            "golden_cross_date":
                golden_cross_date,

            "MFE %":
                mfe,

            "mfe":
                mfe,

            "MAE %":
                mae,

            "mae":
                mae,
        }

        return trade

    # ==================================================
    # SCANNER / CROSSOVER RESULTS
    # ==================================================

    def load_fresh_crossovers(
        self,
        strategy_id: str,
        user_id: str = "default",
    ) -> list[dict[str, Any]]:

        df = self._read_csv(
            "fresh_crossovers.csv"
        )

        return self._to_records(
            df
        )

    def save_fresh_crossovers(
        self,
        strategy_id: str,
        crossovers: list[dict[str, Any]],
        user_id: str = "default",
    ) -> None:

        path = self._csv(
            "fresh_crossovers.csv"
        )

        with _write_lock:

            pd.DataFrame(
                crossovers
            ).to_csv(
                path,
                index=False,
            )

    # ==================================================
    # BACKTEST / PORTFOLIO TRADES
    # ==================================================

    def load_backtest_trades(
        self,
        strategy_id: str,
        user_id: str = "default",
    ) -> list[dict[str, Any]]:
        """
        Return ACTUAL portfolio trades for the dashboard.

        CLOSED positions:
            results/executed_trades.csv

        OPEN positions:
            results/open_trades.csv

        The method name is deliberately preserved because
        existing services/frontend already call
        load_backtest_trades().

        If the new portfolio CSV files are not available,
        we fall back to the older backtest_trades.csv.
        """

        closed_df = self._read_csv(
            "executed_trades.csv"
        )

        open_df = self._read_csv(
            "open_trades.csv"
        )

        records: list[
            dict[str, Any]
        ] = []

        # ==================================================
        # CLOSED PORTFOLIO TRADES
        # ==================================================

        if not closed_df.empty:

            for _, row in (
                closed_df.iterrows()
            ):

                records.append(
                    self._normalize_trade(
                        row,
                        status="CLOSED",
                    )
                )

        # ==================================================
        # OPEN PORTFOLIO TRADES
        # ==================================================

        if not open_df.empty:

            for _, row in (
                open_df.iterrows()
            ):

                records.append(
                    self._normalize_trade(
                        row,
                        status="OPEN",
                    )
                )

        # ==================================================
        # SORT BY ENTRY DATE
        # ==================================================

        if records:

            def sort_key(
                trade: dict[str, Any],
            ):

                value = trade.get(
                    "Entry Date"
                )

                try:

                    timestamp = pd.to_datetime(
                        value,
                        errors="coerce",
                    )

                    if pd.isna(timestamp):

                        return pd.Timestamp.min

                    return timestamp

                except Exception:

                    return pd.Timestamp.min

            records.sort(
                key=sort_key,
                reverse=True,
            )

            return records

        # ==================================================
        # FALLBACK FOR OLD BACKTEST OUTPUT
        # ==================================================

        logger.warning(
            "CSVRepository: "
            "executed_trades.csv and open_trades.csv "
            "were empty or unavailable. "
            "Falling back to backtest_trades.csv."
        )

        fallback_df = self._read_csv(
            "backtest_trades.csv"
        )

        return self._to_records(
            fallback_df
        )

    # ==================================================
    # EQUITY CURVE
    # ==================================================

    def load_equity_curve(
        self,
        strategy_id: str,
        user_id: str = "default",
    ) -> list[dict[str, Any]]:

        df = self._read_csv(
            "equity_curve.csv"
        )

        if df.empty:
            return []

        # Expected:
        #
        # Date
        # Cash
        # Invested
        # Portfolio
        # Open Positions

        if (
            "Date"
            not in df.columns
            and
            len(df.columns) >= 4
        ):

            expected_columns = [

                "Date",

                "Cash",

                "Invested",

                "Portfolio",

                "Open Positions",
            ]

            df.columns = (
                expected_columns[
                    :len(df.columns)
                ]
            )

        return self._to_records(
            df
        )

    # ==================================================
    # PERFORMANCE SUMMARY
    # ==================================================

    def load_performance_summary(
        self,
        strategy_id: str,
        user_id: str = "default",
    ) -> dict[str, Any]:

        df = self._read_csv(
            "performance_summary.csv"
        )

        if df.empty:
            return {}

        row = (
            df.iloc[0]
            .astype(object)
            .where(
                pd.notna(
                    df.iloc[0]
                ),
                None,
            )
        )

        return row.to_dict()

    # ==================================================
    # PORTFOLIO SUMMARY
    # ==================================================

    def load_portfolio_summary(
        self,
        strategy_id: str,
        user_id: str = "default",
    ) -> dict[str, Any]:

        df = self._read_csv(
            "portfolio_summary.csv"
        )

        if df.empty:
            return {}

        row = (
            df.iloc[0]
            .astype(object)
            .where(
                pd.notna(
                    df.iloc[0]
                ),
                None,
            )
        )

        return row.to_dict()

    # ==================================================
    # EXIT SUMMARY
    # ==================================================

    def load_exit_summary(
        self,
        strategy_id: str,
        user_id: str = "default",
    ) -> list[dict[str, Any]]:

        df = self._read_csv(
            "exit_summary.csv"
        )

        return self._to_records(
            df
        )

    # ==================================================
    # ENTERED POSITIONS
    # ==================================================

    def load_entered_positions(
        self,
        strategy_id: str,
        user_id: str = "default",
    ) -> list[dict[str, Any]]:

        df = self._read_csv(
            "entered_positions_status.csv"
        )

        return self._to_records(
            df
        )

    def save_entered_positions(
        self,
        strategy_id: str,
        positions: list[dict[str, Any]],
        user_id: str = "default",
    ) -> None:

        path = self._csv(
            "entered_positions_status.csv"
        )

        with _write_lock:

            pd.DataFrame(
                positions
            ).to_csv(
                path,
                index=False,
            )

    # ==================================================
    # WATCHLIST
    # ==================================================

    def _watchlist_path(
        self,
        strategy_id: str,
        user_id: str,
    ) -> Path:

        return (
            self._settings
            .watchlist_path
        )

    def load_watchlist(
        self,
        strategy_id: str,
        user_id: str = "default",
    ) -> list[str]:

        data = self._read_json(

            self._watchlist_path(
                strategy_id,
                user_id,
            ),

            default={},
        )

        if isinstance(
            data,
            dict,
        ):

            return data.get(
                strategy_id,
                [],
            )

        return []

    def toggle_watchlist(
        self,
        strategy_id: str,
        symbol: str,
        user_id: str = "default",
    ) -> bool:

        path = (
            self._watchlist_path(
                strategy_id,
                user_id,
            )
        )

        data = self._read_json(
            path,
            default={},
        )

        if not isinstance(
            data,
            dict,
        ):

            data = {}

        symbols: list[str] = (
            data.get(
                strategy_id,
                [],
            )
        )

        if symbol in symbols:

            symbols.remove(
                symbol
            )

            new_state = False

        else:

            symbols.append(
                symbol
            )

            new_state = True

        data[
            strategy_id
        ] = symbols

        self._write_json(
            path,
            data,
        )

        return new_state

    # ==================================================
    # STRATEGY CONFIG
    # ==================================================

    def _config_path(
        self,
        strategy_id: str,
        user_id: str,
    ) -> Path:

        return (
            self._settings
            .strategies_config_path
            / strategy_id
            / "config.json"
        )

    def load_strategy_config(
        self,
        strategy_id: str,
        user_id: str = "default",
    ) -> dict[str, Any] | None:

        return self._read_json(

            self._config_path(
                strategy_id,
                user_id,
            )
        )

    def save_strategy_config(
        self,
        strategy_id: str,
        config: dict[str, Any],
        user_id: str = "default",
    ) -> None:

        self._write_json(

            self._config_path(
                strategy_id,
                user_id,
            ),

            config,
        )