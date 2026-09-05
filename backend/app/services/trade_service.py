"""
TradePilot — Trade Service

Handles trade list retrieval, filtering, pagination, and CSV export.
All data comes from the repository — no direct file access here.
"""

from __future__ import annotations

import csv
import hashlib
import io
from typing import Any, Dict, List, Optional, Tuple

from app.core.exceptions import StrategyNotFoundError
from app.core.logging import get_logger
from app.domain.strategy_registry import get_strategy_registry
from app.infrastructure.repositories.base import BaseRepository
from app.schemas.trade import Trade, TradeSummary

logger = get_logger(__name__)

# Map engine exit reasons → frontend ExitReason enum values
EXIT_REASON_MAP: Dict[str, str] = {
    "Stop Loss": "stop_loss",
    "Gap + EMA Confirmation": "signal_reversal",
    "Confirmed Death Cross": "signal_reversal",
    "Target": "target",
    "Manual": "manual",
    "Time Exit": "time_exit",
}


class TradeService:
    def __init__(self, repository: BaseRepository) -> None:
        self._repo = repository
        self._registry = get_strategy_registry()

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
        if not self._registry.exists(strategy_id):
            raise StrategyNotFoundError(strategy_id)

        raw = self._repo.load_backtest_trades(strategy_id, user_id)
        trades = [self._map_trade(r, strategy_id, i) for i, r in enumerate(raw)]

        # Filters
        if status:
            trades = [t for t in trades if t.status == status]
        if symbol:
            trades = [t for t in trades if symbol.upper() in t.symbol.upper()]
        if exit_reason:
            trades = [t for t in trades if t.exitReason == exit_reason]
        if date_from:
            trades = [t for t in trades if t.entryDate >= date_from]
        if date_to:
            trades = [t for t in trades if t.entryDate <= date_to]

        # Sort
        reverse = sort_dir.lower() == "desc"
        field_map = {
            "entryDate": "entryDate",
            "pnlPercent": "pnlPercent",
            "holdingDays": "holdingDays",
            "symbol": "symbol",
        }
        sort_attr = field_map.get(sort_field, "entryDate")
        trades.sort(
            key=lambda t: (getattr(t, sort_attr) or ""),
            reverse=reverse,
        )

        total = len(trades)
        start = (page - 1) * page_size
        return trades[start : start + page_size], total

    def get_trade_summary(
        self, strategy_id: str, user_id: str = "default"
    ) -> TradeSummary:
        if not self._registry.exists(strategy_id):
            raise StrategyNotFoundError(strategy_id)

        raw = self._repo.load_backtest_trades(strategy_id, user_id)
        if not raw:
            return TradeSummary()

        returns = [float(r.get("Return %", 0) or 0) for r in raw]
        wins = [r for r in returns if r > 0]
        losses = [r for r in returns if r <= 0]
        holding_days = [int(r.get("Holding Days", 0) or 0) for r in raw]

        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0.0

        exit_breakdown: Dict[str, int] = {}
        for r in raw:
            reason = EXIT_REASON_MAP.get(r.get("Exit Reason", ""), "signal_reversal")
            exit_breakdown[reason] = exit_breakdown.get(reason, 0) + 1

        return TradeSummary(
            totalTrades=len(raw),
            openTrades=0,
            closedTrades=len(raw),
            winners=len(wins),
            losers=len(losses),
            winRate=round(len(wins) / len(raw) * 100, 2) if raw else 0,
            avgWin=round(sum(wins) / len(wins), 2) if wins else 0,
            avgLoss=round(sum(losses) / len(losses), 2) if losses else 0,
            profitFactor=round(profit_factor, 2),
            totalPnl=round(sum(returns), 2),
            largestWin=round(max(wins), 2) if wins else 0,
            largestLoss=round(min(losses), 2) if losses else 0,
            avgHoldingDays=round(
                sum(holding_days) / len(holding_days), 1
            ) if holding_days else 0,
            exitReasonBreakdown=exit_breakdown,
        )

    def export_csv(
        self, strategy_id: str, user_id: str = "default"
    ) -> str:
        """Return trades as CSV string."""
        if not self._registry.exists(strategy_id):
            raise StrategyNotFoundError(strategy_id)

        raw = self._repo.load_backtest_trades(strategy_id, user_id)
        trades = [self._map_trade(r, strategy_id, i) for i, r in enumerate(raw)]

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Symbol", "Entry Date", "Exit Date", "Entry Price", "Exit Price",
            "P&L %", "Holding Days", "Exit Reason", "MFE %", "MAE %",
        ])
        for t in trades:
            writer.writerow([
                t.symbol, t.entryDate, t.exitDate or "",
                t.entryPrice, t.exitPrice or "",
                t.pnlPercent or "", t.holdingDays or "",
                t.exitReason or "",
                t.mfe or "", t.mae or "",
            ])
        return output.getvalue()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _map_trade(
        self, raw: dict, strategy_id: str, index: int
    ) -> Trade:
        symbol = str(raw.get("Symbol", ""))
        entry_price = float(raw.get("Entry Price", 0) or 0)
        exit_price = float(raw.get("Exit Price", 0) or 0)
        return_pct = float(raw.get("Return %", 0) or 0)

        trade_id = hashlib.md5(
            f"{strategy_id}:{symbol}:{raw.get('Entry Date','')}:{index}".encode()
        ).hexdigest()[:16]

        exit_reason_raw = raw.get("Exit Reason", "")
        exit_reason = EXIT_REASON_MAP.get(exit_reason_raw, "signal_reversal")

        return Trade(
            id=trade_id,
            strategyId=strategy_id,
            symbol=symbol,
            companyName=symbol.replace(".NS", ""),
            exchange="NSE",
            direction="long",
            status="closed",
            entryDate=str(raw.get("Entry Date", ""))[:10],
            entryPrice=entry_price,
            quantity=0,
            entryValue=0,
            exitDate=str(raw.get("Exit Date", ""))[:10] if raw.get("Exit Date") else None,
            exitPrice=exit_price if exit_price > 0 else None,
            exitReason=exit_reason if exit_reason_raw else None,
            pnl=round(return_pct, 2),
            pnlPercent=round(return_pct, 2),
            holdingDays=int(raw.get("Holding Days", 0) or 0),
            stopLoss=round(entry_price * 0.85, 2),
            target=round(entry_price * 1.20, 2),
            riskRewardRatio=round(0.20 / 0.15, 2),
            mfe=float(raw.get("MFE %", 0) or 0) or None,
            mae=float(raw.get("MAE %", 0) or 0) or None,
            highestGap=float(raw.get("Highest Gap", 0) or 0) or None,
            exitGapPercent=float(raw.get("Exit Gap %", 0) or 0) or None,
        )
