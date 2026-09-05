"""
TradePilot — Portfolio Service

Computes portfolio snapshot from equity curve and position data.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from app.core.exceptions import StrategyNotFoundError
from app.core.logging import get_logger
from app.domain.strategy_registry import get_strategy_registry
from app.infrastructure.repositories.base import BaseRepository
from app.schemas.portfolio import PortfolioSnapshot, Position, SectorAllocation

logger = get_logger(__name__)


class PortfolioService:
    def __init__(self, repository: BaseRepository) -> None:
        self._repo = repository
        self._registry = get_strategy_registry()

    def get_portfolio_snapshot(
        self, strategy_id: str, user_id: str = "default"
    ) -> PortfolioSnapshot:
        if not self._registry.exists(strategy_id):
            raise StrategyNotFoundError(strategy_id)

        portfolio_summary = self._repo.load_portfolio_summary(strategy_id, user_id)
        equity_curve = self._repo.load_equity_curve(strategy_id, user_id)

        initial_capital = float(
            portfolio_summary.get("Initial Capital", 100_000) or 100_000
        )
        final_equity = float(
            portfolio_summary.get("Final Equity", initial_capital) or initial_capital
        )
        cash = float(portfolio_summary.get("Cash", final_equity) or final_equity)
        invested = max(0.0, final_equity - cash)

        unrealized_pnl = 0.0
        unrealized_pct = 0.0

        # Get last equity point for day change
        day_change = 0.0
        day_change_pct = 0.0
        snapshot_date = datetime.now(timezone.utc).isoformat()[:10]

        if len(equity_curve) >= 2:
            last = equity_curve[-1]
            prev = equity_curve[-2]
            last_val = float(last.get("Portfolio", final_equity) or final_equity)
            prev_val = float(prev.get("Portfolio", last_val) or last_val)
            day_change = round(last_val - prev_val, 2)
            day_change_pct = (
                round((last_val - prev_val) / prev_val * 100, 2)
                if prev_val > 0 else 0
            )
            snapshot_date = str(last.get("Date", snapshot_date))[:10]

        return PortfolioSnapshot(
            snapshotDate=snapshot_date,
            totalValue=round(final_equity, 2),
            cash=round(cash, 2),
            invested=round(invested, 2),
            unrealizedPnl=round(unrealized_pnl, 2),
            unrealizedPnlPercent=round(unrealized_pct, 2),
            dayChange=day_change,
            dayChangePercent=day_change_pct,
            openPositions=0,
            sectorAllocations=[],
            positions=[],
        )
