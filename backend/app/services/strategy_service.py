"""
TradePilot — Strategy Service

Manages strategy discovery, config, and computed stats.
Uses the strategy registry for manifest data and the repository
for persisted configuration overrides.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List

from app.core.config import get_settings
from app.core.exceptions import StrategyNotFoundError
from app.core.logging import get_logger
from app.domain.strategy_registry import get_strategy_registry
from app.infrastructure.repositories.base import BaseRepository
from app.schemas.strategy import (
    Strategy,
    StrategyConfig,
    StrategyListItem,
    StrategyListItemStats,
    StrategyStats,
    UpdateStrategyConfigRequest,
)

logger = get_logger(__name__)


class StrategyService:
    """
    Manages the strategy catalog and per-strategy configuration.
    No business logic in routes — everything routes to here.
    """

    def __init__(self, repository: BaseRepository) -> None:
        self._repo = repository
        self._registry = get_strategy_registry()
        self._settings = get_settings()

    def list_strategies(self, user_id: str = "default") -> List[StrategyListItem]:
        """Return all registered strategies with their summary stats."""
        manifests = self._registry.list_manifests()
        items = []

        for manifest in manifests:
            perf = self._repo.load_performance_summary(manifest.id, user_id)
            portfolio = self._repo.load_portfolio_summary(manifest.id, user_id)
            equity_curve = self._repo.load_equity_curve(manifest.id, user_id)

            total_return = self._compute_total_return(portfolio, equity_curve)
            win_rate = float(perf.get("Win Rate (%)", 0) or 0)
            portfolio_value = float(portfolio.get("Final Equity", 0) or 0)
            closed_trades = int(portfolio.get("Closed Trades", 0) or 0)

            last_scan = self._get_last_scan_time(manifest.id)

            items.append(
                StrategyListItem(
                    id=manifest.id,
                    name=manifest.name,
                    description=manifest.description,
                    status="active" if manifest.supported_features.scanner else "inactive",
                    stocks=len(self._repo.load_fresh_crossovers(manifest.id, user_id)),
                    lastScan=last_scan,
                    tags=manifest.tags,
                    stats=StrategyListItemStats(
                        portfolioValue=portfolio_value,
                        totalReturn=total_return,
                        winRate=win_rate,
                        openPositions=0,
                    ),
                )
            )

        return items

    def get_strategy(self, strategy_id: str, user_id: str = "default") -> Strategy:
        """Return full strategy detail with config and computed stats."""
        manifest = self._registry.get_manifest(strategy_id)
        if manifest is None:
            raise StrategyNotFoundError(strategy_id)

        config = self._get_effective_config(strategy_id, user_id, manifest)
        stats = self._compute_stats(strategy_id, user_id)
        last_scan = self._get_last_scan_time(strategy_id)

        return Strategy(
            id=manifest.id,
            name=manifest.name,
            description=manifest.description,
            longDescription=manifest.long_description or None,
            status="active",
            category=manifest.category,
            stocks=stats.closedTrades,
            lastScan=last_scan,
            createdAt="2024-01-15T08:00:00.000Z",
            config=config,
            stats=stats,
            tags=manifest.tags,
        )

    def update_config(
        self,
        strategy_id: str,
        update: UpdateStrategyConfigRequest,
        user_id: str = "default",
    ) -> Strategy:
        """Merge config update into persisted config, return updated strategy."""
        manifest = self._registry.get_manifest(strategy_id)
        if manifest is None:
            raise StrategyNotFoundError(strategy_id)

        current_raw = self._repo.load_strategy_config(strategy_id, user_id) or {}
        patch = update.model_dump(exclude_none=True)
        current_raw.update(patch)

        self._repo.save_strategy_config(strategy_id, current_raw, user_id)
        logger.info(f"StrategyService: config updated for '{strategy_id}'")

        return self.get_strategy(strategy_id, user_id)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_effective_config(
        self, strategy_id: str, user_id: str, manifest: Any
    ) -> StrategyConfig:
        """Merge manifest defaults + persisted overrides → effective config."""
        defaults = manifest.get_default_config()
        overrides = self._repo.load_strategy_config(strategy_id, user_id) or {}

        s = self._settings
        merged = {
            "initialCapital": overrides.get(
                "initialCapital", defaults.get("initial_capital", s.DEFAULT_INITIAL_CAPITAL)
            ),
            "allocation": overrides.get(
                "allocation", defaults.get("allocation", s.DEFAULT_ALLOCATION)
            ),
            "maxPositions": overrides.get(
                "maxPositions", defaults.get("max_positions", s.DEFAULT_MAX_POSITIONS)
            ),
            "stopLossPercent": abs(overrides.get(
                "stopLossPercent",
                defaults.get("stop_loss_percent", abs(s.DEFAULT_STOP_LOSS_PERCENT)),
            )),
            "goldenCrossLookback": overrides.get(
                "goldenCrossLookback",
                defaults.get("golden_cross_lookback", s.DEFAULT_GOLDEN_CROSS_LOOKBACK),
            ),
            "gapThreshold": overrides.get(
                "gapThreshold", defaults.get("gap_threshold", s.DEFAULT_GAP_THRESHOLD)
            ),
            "emaPeriodFast": 50,
            "emaPeriodSlow": 200,
            "riskPerTrade": overrides.get("riskPerTrade", 2.0),
            "takeProfitPercent": overrides.get("takeProfitPercent", 20.0),
            "scanTimeframe": "1D",
            "universe": manifest.universe,
        }
        return StrategyConfig(**merged)

    def _compute_stats(self, strategy_id: str, user_id: str) -> StrategyStats:
        """Compute strategy-level stats from repository data."""
        perf = self._repo.load_performance_summary(strategy_id, user_id)
        portfolio = self._repo.load_portfolio_summary(strategy_id, user_id)
        equity_curve = self._repo.load_equity_curve(strategy_id, user_id)

        initial_capital = float(portfolio.get("Initial Capital", self._settings.DEFAULT_INITIAL_CAPITAL) or self._settings.DEFAULT_INITIAL_CAPITAL)
        final_equity = float(portfolio.get("Final Equity", initial_capital) or initial_capital)
        cash = float(portfolio.get("Cash", final_equity) or final_equity)
        closed_trades = int(portfolio.get("Closed Trades", 0) or 0)

        total_return = ((final_equity - initial_capital) / initial_capital * 100) if initial_capital > 0 else 0
        invested = max(0.0, final_equity - cash)

        # Compute CAGR and Sharpe from equity curve if available
        cagr, sharpe, max_dd = 0.0, 0.0, 0.0
        if equity_curve:
            try:
                import pandas as pd
                import numpy as np
                ec = pd.DataFrame(equity_curve)
                ec["Date"] = pd.to_datetime(ec["Date"])
                ec = ec.sort_values("Date")
                port_vals = ec["Portfolio"].astype(float)

                if len(port_vals) > 1:
                    years = (ec["Date"].iloc[-1] - ec["Date"].iloc[0]).days / 365.25
                    if years > 0:
                        cagr = ((port_vals.iloc[-1] / port_vals.iloc[0]) ** (1 / years) - 1) * 100

                    daily_r = port_vals.pct_change().dropna()
                    if daily_r.std() > 0:
                        sharpe = (daily_r.mean() / daily_r.std()) * np.sqrt(252)

                    running_max = port_vals.cummax()
                    drawdown = (port_vals - running_max) / running_max * 100
                    max_dd = float(drawdown.min())
            except Exception as exc:
                logger.warning(f"Could not compute equity stats: {exc}")

        return StrategyStats(
            portfolioValue=round(final_equity, 2),
            capitalDeployed=round(invested, 2),
            openPositions=0,
            closedTrades=closed_trades,
            winRate=round(float(perf.get("Win Rate (%)", 0) or 0), 2),
            profitFactor=round(float(perf.get("Profit Factor", 0) or 0), 2),
            averageReturn=round(float(perf.get("Average Return (%)", 0) or 0), 2),
            averageHoldingDays=round(float(perf.get("Average Holding Days", 0) or 0), 1),
            totalReturn=round(total_return, 2),
            cagr=round(cagr, 2),
            sharpeRatio=round(sharpe, 2),
            maxDrawdown=round(max_dd, 2),
        )

    def _compute_total_return(
        self, portfolio: dict, equity_curve: list
    ) -> float:
        initial = float(portfolio.get("Initial Capital", 0) or 0)
        final = float(portfolio.get("Final Equity", 0) or 0)
        if initial > 0:
            return round((final - initial) / initial * 100, 2)
        return 0.0

    def _get_last_scan_time(self, strategy_id: str) -> str:
        """Return ISO timestamp of last scan result file modification."""
        try:
            crossover_file = self._settings.results_path / "fresh_crossovers.csv"
            if crossover_file.exists():
                mtime = crossover_file.stat().st_mtime
                return datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
        except Exception:
            pass
        return ""
