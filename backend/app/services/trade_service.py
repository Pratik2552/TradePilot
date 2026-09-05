"""
TradePilot — Trade Service

Handles:
- trade list retrieval
- filtering
- sorting
- pagination
- trade summaries
- CSV export

The repository returns normalized portfolio trades from:

    executed_trades.csv  -> CLOSED trades
    open_trades.csv      -> OPEN trades

IMPORTANT:

P&L and percentage return are different values.

CLOSED:
    pnl        = Realized P&L (₹)
    pnlPercent = Return %

OPEN:
    pnl        = Unrealized P&L (₹)
    pnlPercent = Unrealized Return %

Quantity comes from Shares.
"""

from __future__ import annotations

import csv
import hashlib
import io

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
)

from app.core.exceptions import (
    StrategyNotFoundError,
)

from app.core.logging import (
    get_logger,
)

from app.domain.strategy_registry import (
    get_strategy_registry,
)

from app.infrastructure.repositories.base import (
    BaseRepository,
)

from app.schemas.trade import (
    Trade,
    TradeSummary,
)


logger = get_logger(__name__)


# ==========================================================
# ENGINE EXIT REASON -> FRONTEND ENUM
# ==========================================================

EXIT_REASON_MAP: Dict[str, str] = {

    "Stop Loss":
        "stop_loss",

    "Gap + EMA Confirmation":
        "signal_reversal",

    "Confirmed Death Cross":
        "signal_reversal",

    "Target":
        "target",

    "Manual":
        "manual",

    "Time Exit":
        "time_exit",
}


class TradeService:

    def __init__(
        self,
        repository: BaseRepository,
    ) -> None:

        self._repo = repository

        self._registry = (
            get_strategy_registry()
        )

    # ==========================================================
    # SAFE VALUE HELPERS
    # ==========================================================

    @staticmethod
    def _float(
        value: Any,
        default: float = 0.0,
    ) -> float:

        if value is None:
            return default

        try:

            # Avoid strings such as "", "nan", "None"
            if isinstance(
                value,
                str,
            ):

                stripped = (
                    value.strip()
                )

                if stripped.lower() in {
                    "",
                    "nan",
                    "none",
                    "null",
                }:

                    return default

                value = stripped

            result = float(
                value
            )

            # NaN test
            if result != result:
                return default

            return result

        except (
            TypeError,
            ValueError,
        ):

            return default

    @classmethod
    def _int(
        cls,
        value: Any,
        default: int = 0,
    ) -> int:

        try:

            return int(
                cls._float(
                    value,
                    float(default),
                )
            )

        except Exception:

            return default

    @staticmethod
    def _value(
        raw: dict,
        *keys: str,
        default: Any = None,
    ) -> Any:

        for key in keys:

            if key not in raw:
                continue

            value = raw.get(
                key
            )

            if value is None:
                continue

            if isinstance(
                value,
                str,
            ):

                if value.strip().lower() in {
                    "",
                    "nan",
                    "none",
                    "null",
                }:

                    continue

            return value

        return default

    @staticmethod
    def _date(
        value: Any,
    ) -> Optional[str]:

        if value is None:
            return None

        value = str(
            value
        ).strip()

        if value.lower() in {
            "",
            "nan",
            "none",
            "null",
            "nat",
        }:

            return None

        # CSV dates may include:
        #
        # 2026-07-07
        # 2026-07-07 00:00:00
        #
        # Frontend only needs YYYY-MM-DD.
        return value[:10]

    # ==========================================================
    # STATUS
    # ==========================================================

    @classmethod
    def _status(
        cls,
        raw: dict,
    ) -> str:

        status = cls._value(
            raw,
            "Status",
            "status",
        )

        if status is not None:

            normalized = (
                str(status)
                .strip()
                .lower()
            )

            if normalized in {
                "open",
                "closed",
            }:

                return normalized

        # ------------------------------------------------------
        # FALLBACK FOR OLD DATA
        # ------------------------------------------------------

        exit_date = cls._value(
            raw,
            "Exit Date",
            "exit_date",
        )

        exit_price = cls._float(
            cls._value(
                raw,
                "Exit Price",
                "exit_price",
            ),
            0,
        )

        if (
            exit_date is not None
            and
            exit_price > 0
        ):

            return "closed"

        return "open"

    # ==========================================================
    # GET TRADES
    # ==========================================================

    def get_trades(
        self,
        strategy_id: str,
        user_id: str = "default",
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        symbol: Optional[str] = None,
        exit_reason: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        sort_field: str = "entryDate",
        sort_dir: str = "desc",
    ) -> Tuple[List[Trade], int]:

        if not self._registry.exists(
            strategy_id
        ):

            raise StrategyNotFoundError(
                strategy_id
            )

        raw = (
            self._repo
            .load_backtest_trades(
                strategy_id,
                user_id,
            )
        )

        trades = [

            self._map_trade(
                row,
                strategy_id,
                index,
            )

            for index, row
            in enumerate(raw)
        ]

        # ======================================================
        # FILTERS
        # ======================================================

        if status:

            normalized_status = (
                status.lower()
            )

            trades = [

                trade
                for trade in trades

                if (
                    trade.status
                    == normalized_status
                )
            ]

        if symbol:

            symbol_upper = (
                symbol.upper()
            )

            trades = [

                trade
                for trade in trades

                if (
                    symbol_upper
                    in trade.symbol.upper()
                )
            ]

        if exit_reason:

            trades = [

                trade
                for trade in trades

                if (
                    trade.exitReason
                    == exit_reason
                )
            ]

        if date_from:

            trades = [

                trade
                for trade in trades

                if (
                    trade.entryDate
                    and
                    trade.entryDate
                    >= date_from
                )
            ]

        if date_to:

            trades = [

                trade
                for trade in trades

                if (
                    trade.entryDate
                    and
                    trade.entryDate
                    <= date_to
                )
            ]

        # ======================================================
        # SORT
        # ======================================================

        reverse = (
            sort_dir.lower()
            == "desc"
        )

        field_map = {

            "entryDate":
                "entryDate",

            "pnlPercent":
                "pnlPercent",

            "holdingDays":
                "holdingDays",

            "symbol":
                "symbol",

            "pnl":
                "pnl",

            "quantity":
                "quantity",
        }

        sort_attr = (
            field_map.get(
                sort_field,
                "entryDate",
            )
        )

        def sort_key(
            trade: Trade,
        ):

            value = getattr(
                trade,
                sort_attr,
                None,
            )

            if value is None:
                return 0

            return value

        try:

            trades.sort(
                key=sort_key,
                reverse=reverse,
            )

        except TypeError:

            # Safe fallback for mixed old data.
            trades.sort(
                key=lambda trade:
                    str(
                        getattr(
                            trade,
                            sort_attr,
                            "",
                        )
                    ),
                reverse=reverse,
            )

        # ======================================================
        # PAGINATION
        # ======================================================

        total = len(
            trades
        )

        page = max(
            1,
            page,
        )

        page_size = max(
            1,
            page_size,
        )

        start = (
            (page - 1)
            * page_size
        )

        end = (
            start
            + page_size
        )

        return (
            trades[
                start:end
            ],
            total,
        )

    # ==========================================================
    # TRADE SUMMARY
    # ==========================================================

    def get_trade_summary(
        self,
        strategy_id: str,
        user_id: str = "default",
    ) -> TradeSummary:

        if not self._registry.exists(
            strategy_id
        ):

            raise StrategyNotFoundError(
                strategy_id
            )

        raw = (
            self._repo
            .load_backtest_trades(
                strategy_id,
                user_id,
            )
        )

        if not raw:

            return TradeSummary()

        # ======================================================
        # SPLIT OPEN / CLOSED
        # ======================================================

        closed_rows = []

        open_rows = []

        for row in raw:

            trade_status = (
                self._status(
                    row
                )
            )

            if (
                trade_status
                == "closed"
            ):

                closed_rows.append(
                    row
                )

            else:

                open_rows.append(
                    row
                )

        # ======================================================
        # CLOSED TRADE RETURNS
        #
        # Open trades MUST NOT affect:
        #
        # win rate
        # profit factor
        # avg win
        # avg loss
        # largest realized win/loss
        # ======================================================

        closed_returns = [

            self._float(

                self._value(
                    row,
                    "Return %",
                    "return_pct",
                )
            )

            for row
            in closed_rows
        ]

        wins = [

            value
            for value
            in closed_returns

            if value > 0
        ]

        losses = [

            value
            for value
            in closed_returns

            if value <= 0
        ]

        # ======================================================
        # HOLDING DAYS
        # ======================================================

        holding_days = [

            self._int(

                self._value(
                    row,
                    "Holding Days",
                    "holding_days",
                )
            )

            for row
            in closed_rows
        ]

        # ======================================================
        # PROFIT FACTOR
        #
        # Preserve previous behavior:
        # calculated from trade returns.
        # ======================================================

        gross_profit = sum(
            wins
        )

        gross_loss = abs(
            sum(
                losses
            )
        )

        profit_factor = (

            gross_profit
            / gross_loss

            if gross_loss > 0

            else (
                float("inf")
                if gross_profit > 0
                else 0.0
            )
        )

        # ======================================================
        # RUPEE P&L
        #
        # CLOSED = realized
        # OPEN   = unrealized
        # ======================================================

        closed_pnl = sum(

            self._float(

                self._value(
                    row,
                    "P&L",
                    "PnL",
                    "pnl",
                    "Realized P&L",
                )
            )

            for row
            in closed_rows
        )

        open_pnl = sum(

            self._float(

                self._value(
                    row,
                    "P&L",
                    "PnL",
                    "pnl",
                    "Unrealized P&L",
                )
            )

            for row
            in open_rows
        )

        total_pnl = (
            closed_pnl
            + open_pnl
        )

        # ======================================================
        # EXIT BREAKDOWN
        # CLOSED TRADES ONLY
        # ======================================================

        exit_breakdown: Dict[
            str,
            int,
        ] = {}

        for row in closed_rows:

            raw_reason = str(

                self._value(
                    row,
                    "Exit Reason",
                    "exit_reason",
                    default="",
                )
                or ""
            )

            if not raw_reason:
                continue

            mapped_reason = (
                EXIT_REASON_MAP.get(
                    raw_reason,
                    "signal_reversal",
                )
            )

            exit_breakdown[
                mapped_reason
            ] = (
                exit_breakdown.get(
                    mapped_reason,
                    0,
                )
                + 1
            )

        closed_count = len(
            closed_rows
        )

        return TradeSummary(

            totalTrades=
                len(raw),

            openTrades=
                len(open_rows),

            closedTrades=
                closed_count,

            winners=
                len(wins),

            losers=
                len(losses),

            winRate=(
                round(
                    len(wins)
                    / closed_count
                    * 100,
                    2,
                )
                if closed_count
                else 0
            ),

            avgWin=(
                round(
                    sum(wins)
                    / len(wins),
                    2,
                )
                if wins
                else 0
            ),

            avgLoss=(
                round(
                    sum(losses)
                    / len(losses),
                    2,
                )
                if losses
                else 0
            ),

            profitFactor=(
                round(
                    profit_factor,
                    2,
                )
                if (
                    profit_factor
                    != float("inf")
                )
                else 999.99
            ),

            # ----------------------------------------------
            # Now this is actual ₹ P&L,
            # not summed percentage returns.
            # ----------------------------------------------

            totalPnl=
                round(
                    total_pnl,
                    2,
                ),

            largestWin=(
                round(
                    max(wins),
                    2,
                )
                if wins
                else 0
            ),

            largestLoss=(
                round(
                    min(losses),
                    2,
                )
                if losses
                else 0
            ),

            avgHoldingDays=(
                round(
                    sum(
                        holding_days
                    )
                    / len(
                        holding_days
                    ),
                    1,
                )
                if holding_days
                else 0
            ),

            exitReasonBreakdown=
                exit_breakdown,
        )

    # ==========================================================
    # CSV EXPORT
    # ==========================================================

    def export_csv(
        self,
        strategy_id: str,
        user_id: str = "default",
    ) -> str:

        if not self._registry.exists(
            strategy_id
        ):

            raise StrategyNotFoundError(
                strategy_id
            )

        raw = (
            self._repo
            .load_backtest_trades(
                strategy_id,
                user_id,
            )
        )

        trades = [

            self._map_trade(
                row,
                strategy_id,
                index,
            )

            for index, row
            in enumerate(raw)
        ]

        output = io.StringIO()

        writer = csv.writer(
            output
        )

        writer.writerow(
            [
                "Symbol",
                "Status",
                "Entry Date",
                "Exit Date",
                "Entry Price",
                "Exit Price",
                "Quantity",
                "Entry Value",
                "P&L",
                "P&L %",
                "Holding Days",
                "Exit Reason",
                "MFE %",
                "MAE %",
            ]
        )

        for trade in trades:

            writer.writerow(
                [
                    trade.symbol,

                    trade.status,

                    trade.entryDate,

                    trade.exitDate
                    or "",

                    trade.entryPrice,

                    trade.exitPrice
                    if (
                        trade.exitPrice
                        is not None
                    )
                    else "",

                    trade.quantity,

                    trade.entryValue,

                    trade.pnl,

                    trade.pnlPercent,

                    trade.holdingDays,

                    trade.exitReason
                    or "",

                    trade.mfe
                    if (
                        trade.mfe
                        is not None
                    )
                    else "",

                    trade.mae
                    if (
                        trade.mae
                        is not None
                    )
                    else "",
                ]
            )

        return output.getvalue()

    # ==========================================================
    # RAW ROW -> FRONTEND TRADE
    # ==========================================================

    def _map_trade(
        self,
        raw: dict,
        strategy_id: str,
        index: int,
    ) -> Trade:

        # ======================================================
        # BASIC INFO
        # ======================================================

        symbol = str(

            self._value(
                raw,
                "Symbol",
                "symbol",
                default="",
            )
            or ""
        )

        status = (
            self._status(
                raw
            )
        )

        # ======================================================
        # ENTRY
        # ======================================================

        entry_date = (
            self._date(

                self._value(
                    raw,
                    "Entry Date",
                    "entry_date",
                )
            )
            or ""
        )

        entry_price = (
            self._float(

                self._value(
                    raw,
                    "Entry Price",
                    "entry_price",
                )
            )
        )

        # ======================================================
        # QUANTITY
        #
        # THIS FIXES THE ZERO-QTY BUG.
        # ======================================================

        quantity = (
            self._float(

                self._value(
                    raw,
                    "Shares",
                    "shares",
                    "Quantity",
                    "quantity",
                    "Qty",
                    "qty",
                )
            )
        )

        # ======================================================
        # ENTRY VALUE
        # ======================================================

        entry_value = (
            self._float(

                self._value(
                    raw,
                    "Invested",
                    "invested",
                )
            )
        )

        # Fallback if old data does not contain Invested.
        if (
            entry_value <= 0
            and
            quantity > 0
            and
            entry_price > 0
        ):

            entry_value = (
                quantity
                * entry_price
            )

        # ======================================================
        # RETURN %
        # ======================================================

        return_pct = (
            self._float(

                self._value(
                    raw,
                    "Return %",
                    "return_pct",
                    "Unrealized Return %",
                )
            )
        )

        # ======================================================
        # ACTUAL RUPEE P&L
        #
        # Repository already normalized:
        #
        # CLOSED -> Realized P&L
        # OPEN   -> Unrealized P&L
        #
        # THIS FIXES:
        #
        # 43.87% appearing as ₹44
        # ======================================================

        pnl = (
            self._float(

                self._value(
                    raw,
                    "P&L",
                    "PnL",
                    "pnl",
                    (
                        "Unrealized P&L"
                        if status
                        == "open"
                        else
                        "Realized P&L"
                    ),
                )
            )
        )

        # ======================================================
        # EXIT
        # ======================================================

        exit_date = None
        exit_price = None
        exit_reason = None

        if status == "closed":

            exit_date = self._date(

                self._value(
                    raw,
                    "Exit Date",
                    "exit_date",
                )
            )

            raw_exit_price = (
                self._float(

                    self._value(
                        raw,
                        "Exit Price",
                        "exit_price",
                    )
                )
            )

            if raw_exit_price > 0:

                exit_price = (
                    raw_exit_price
                )

            exit_reason_raw = str(

                self._value(
                    raw,
                    "Exit Reason",
                    "exit_reason",
                    default="",
                )
                or ""
            )

            if exit_reason_raw:

                exit_reason = (
                    EXIT_REASON_MAP.get(
                        exit_reason_raw,
                        "signal_reversal",
                    )
                )

        # ======================================================
        # TRADE ID
        # ======================================================

        trade_id = hashlib.md5(

            (
                f"{strategy_id}:"
                f"{symbol}:"
                f"{entry_date}:"
                f"{index}"
            ).encode()

        ).hexdigest()[:16]

        # ======================================================
        # HOLDING DAYS
        # ======================================================

        holding_days = (
            self._int(

                self._value(
                    raw,
                    "Holding Days",
                    "holding_days",
                )
            )
        )

        # ======================================================
        # STRATEGY STATS
        # ======================================================

        mfe_value = self._float(

            self._value(
                raw,
                "MFE %",
                "mfe",
            )
        )

        mae_value = self._float(

            self._value(
                raw,
                "MAE %",
                "mae",
            )
        )

        highest_gap_value = (
            self._float(

                self._value(
                    raw,
                    "Highest Gap",
                    "highestGap",
                )
            )
        )

        exit_gap_value = (
            self._float(

                self._value(
                    raw,
                    "Exit Gap %",
                    "exitGapPercent",
                )
            )
        )

        # ======================================================
        # RETURN FRONTEND MODEL
        # ======================================================

        return Trade(

            id=
                trade_id,

            strategyId=
                strategy_id,

            symbol=
                symbol,

            companyName=
                symbol.replace(
                    ".NS",
                    "",
                ),

            exchange=
                "NSE",

            direction=
                "long",

            # ----------------------------------------------
            # FIX:
            # no longer hard-coded "closed"
            # ----------------------------------------------

            status=
                status,

            entryDate=
                entry_date,

            entryPrice=
                entry_price,

            # ----------------------------------------------
            # FIX:
            # actual Shares from portfolio
            # ----------------------------------------------

            quantity=
                quantity,

            entryValue=
                entry_value,

            # ----------------------------------------------
            # OPEN -> None
            # CLOSED -> actual exit
            # ----------------------------------------------

            exitDate=
                exit_date,

            exitPrice=
                exit_price,

            exitReason=
                exit_reason,

            # ----------------------------------------------
            # FIX:
            # actual ₹ P&L
            # ----------------------------------------------

            pnl=
                round(
                    pnl,
                    2,
                ),

            # ----------------------------------------------
            # percentage remains separate
            # ----------------------------------------------

            pnlPercent=
                round(
                    return_pct,
                    2,
                ),

            holdingDays=
                holding_days,

            # Existing frontend strategy display fields
            stopLoss=
                (
                    round(
                        entry_price
                        * 0.85,
                        2,
                    )
                    if entry_price > 0
                    else 0
                ),

            target=
                (
                    round(
                        entry_price
                        * 1.20,
                        2,
                    )
                    if entry_price > 0
                    else 0
                ),

            riskRewardRatio=
                round(
                    0.20
                    / 0.15,
                    2,
                ),

            mfe=(
                mfe_value
                if mfe_value != 0
                else None
            ),

            mae=(
                mae_value
                if mae_value != 0
                else None
            ),

            highestGap=(
                highest_gap_value
                if (
                    highest_gap_value
                    != 0
                )
                else None
            ),

            exitGapPercent=(
                exit_gap_value
                if (
                    exit_gap_value
                    != 0
                )
                else None
            ),
        )