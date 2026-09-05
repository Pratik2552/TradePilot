"""
TradePilot — Scanner Service

Orchestrates the scanner workflow:
1. Validate strategy exists
2. Check if scan already running
3. Submit scan as background task
4. Enrich repository results for API responses

No engine code here. Engine is called via the strategy's scanner_adapter.
"""

from __future__ import annotations

import hashlib
import importlib
from datetime import datetime, timezone
from typing import Any, List, Optional

from app.core.exceptions import (
    ScanAlreadyRunningError,
    StrategyNotFoundError,
)
from app.core.logging import get_logger
from app.domain.strategy_registry import get_strategy_registry
from app.infrastructure.repositories.base import BaseRepository
from app.infrastructure.task_runner.background_runner import BackgroundTaskRunner
from app.infrastructure.task_runner.base import TaskStatus
from app.schemas.scanner import ScanResult, ScannerSummary, WatchlistItem

logger = get_logger(__name__)

# Sector color palette (cycles through for display)
SECTOR_COLORS = [
    "#6366f1", "#8b5cf6", "#ec4899", "#f59e0b",
    "#10b981", "#3b82f6", "#ef4444", "#14b8a6",
]


class ScannerService:
    """Scanner orchestration — strategy-agnostic core."""

    def __init__(
        self,
        repository: BaseRepository,
        task_runner: BackgroundTaskRunner,
    ) -> None:
        self._repo = repository
        self._tasks = task_runner
        self._registry = get_strategy_registry()

    def get_scan_results(
        self,
        strategy_id: str,
        user_id: str = "default",
        page: int = 1,
        page_size: int = 50,
        search: Optional[str] = None,
        signal_strength: Optional[List[str]] = None,
        is_watchlisted: Optional[bool] = None,
    ) -> tuple[List[ScanResult], int]:
        """Return paginated, filtered scan results."""
        if not self._registry.exists(strategy_id):
            raise StrategyNotFoundError(strategy_id)

        raw = self._repo.load_fresh_crossovers(strategy_id, user_id)
        watchlist = set(self._repo.load_watchlist(strategy_id, user_id))

        results = [self._enrich(r, strategy_id, watchlist) for r in raw]

        # Apply filters
        if search:
            q = search.lower()
            results = [
                r for r in results
                if q in r.symbol.lower() or q in r.companyName.lower()
            ]

        if signal_strength:
            results = [r for r in results if r.signalStrength in signal_strength]

        if is_watchlisted is not None:
            results = [r for r in results if r.isWatchlisted == is_watchlisted]

        total = len(results)
        start = (page - 1) * page_size
        return results[start : start + page_size], total

    def get_scanner_summary(
        self, strategy_id: str, user_id: str = "default"
    ) -> ScannerSummary:
        if not self._registry.exists(strategy_id):
            raise StrategyNotFoundError(strategy_id)

        raw = self._repo.load_fresh_crossovers(strategy_id, user_id)
        watchlist = self._repo.load_watchlist(strategy_id, user_id)
        last_scan = self._get_last_scan_time(strategy_id)

        return ScannerSummary(
            totalResults=len(raw),
            freshCrossovers=len(raw),
            existingSignals=0,
            addedToWatchlist=len(watchlist),
            lastScanAt=last_scan,
            scannedSymbols=len(raw),
        )

    def run_scan(
        self,
        strategy_id: str,
        config_overrides: dict[str, Any] | None = None,
        user_id: str = "default",
    ) -> TaskStatus:
        """Submit a background scan. Raises if one is already running."""
        if not self._registry.exists(strategy_id):
            raise StrategyNotFoundError(strategy_id)

        if self._tasks.is_running("scan", strategy_id):
            raise ScanAlreadyRunningError(strategy_id)

        # Resolve config
        from app.infrastructure.repositories.csv_repository import CSVRepository
        raw_config = self._repo.load_strategy_config(strategy_id, user_id) or {}
        if config_overrides:
            raw_config.update(config_overrides)

        # Load the strategy's scanner adapter dynamically
        adapter_fn = self._load_scanner_adapter(strategy_id)

        def _task() -> None:
            adapter_fn(raw_config)

        return self._tasks.submit(
            task_type="scan",
            strategy_id=strategy_id,
            fn=_task,
        )

    def get_task_status(self, task_id: str) -> TaskStatus | None:
        return self._tasks.get_status(task_id)

    def get_watchlist(
        self, strategy_id: str, user_id: str = "default"
    ) -> List[WatchlistItem]:
        if not self._registry.exists(strategy_id):
            raise StrategyNotFoundError(strategy_id)

        symbols = self._repo.load_watchlist(strategy_id, user_id)
        raw = self._repo.load_fresh_crossovers(strategy_id, user_id)
        price_map = {r.get("Symbol", ""): r.get("Close", 0) for r in raw}
        now = datetime.now(timezone.utc).isoformat()

        return [
            WatchlistItem(
                symbol=sym,
                addedAt=now,
                currentPrice=float(price_map.get(sym, 0)),
            )
            for sym in symbols
        ]

    def toggle_watchlist(
        self, strategy_id: str, symbol: str, user_id: str = "default"
    ) -> bool:
        if not self._registry.exists(strategy_id):
            raise StrategyNotFoundError(strategy_id)
        return self._repo.toggle_watchlist(strategy_id, symbol, user_id)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _enrich(
        self, raw: dict, strategy_id: str, watchlist: set
    ) -> ScanResult:
        symbol = raw.get("Symbol", "")
        close = float(raw.get("Close", 0) or 0)
        volume_ratio = float(raw.get("Volume Ratio", 0) or 0)

        # Derive signal strength from volume ratio
        if volume_ratio >= 2.0:
            strength = "strong"
        elif volume_ratio >= 1.2:
            strength = "moderate"
        else:
            strength = "weak"

        # Derive suggested risk levels
        stop_loss = round(close * 0.85, 2)   # 15% stop loss
        target = round(close * 1.20, 2)      # 20% target
        rr = round((target - close) / (close - stop_loss), 2) if close > stop_loss else 0

        row_id = hashlib.md5(f"{strategy_id}:{symbol}".encode()).hexdigest()[:12]

        return ScanResult(
            id=row_id,
            strategyId=strategy_id,
            symbol=symbol,
            companyName=symbol.replace(".NS", ""),
            exchange="NSE",
            crossoverType="golden",
            scanStatus="fresh",
            signalStrength=strength,
            scannedAt=raw.get("Date", ""),
            currentPrice=close,
            volume=float(raw.get("Current Volume", 0) or 0),
            avgVolume=float(raw.get("20D Avg Volume", 0) or 0),
            volumeRatio=volume_ratio,
            ema50=float(raw.get("EMA50", 0) or 0),
            ema200=float(raw.get("EMA200", 0) or 0),
            ema50ema200Gap=float(raw.get("EMA Distance %", 0) or 0),
            crossoverDate=raw.get("Date"),
            suggestedEntry=close,
            suggestedStopLoss=stop_loss,
            suggestedTarget=target,
            riskRewardRatio=rr,
            tradingViewUrl=raw.get("TradingView"),
            screenerUrl=raw.get("Screener"),
            isWatchlisted=symbol in watchlist,
        )

    def _get_last_scan_time(self, strategy_id: str) -> str:
        try:
            from app.core.config import get_settings
            f = get_settings().results_path / "fresh_crossovers.csv"
            if f.exists():
                mtime = f.stat().st_mtime
                return datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
        except Exception:
            pass
        return ""

    def _load_scanner_adapter(self, strategy_id: str):
        """
        Dynamically load the scanner adapter for a strategy plugin.
        Convention: app.strategies.{id_underscore}.scanner_adapter.run_scanner
        """
        module_name = strategy_id.replace("-", "_")
        try:
            module = importlib.import_module(
                f"app.strategies.{module_name}.scanner_adapter"
            )
            return module.run_scanner
        except (ImportError, AttributeError) as exc:
            logger.error(
                f"ScannerService: no scanner adapter for '{strategy_id}': {exc}"
            )
            raise StrategyNotFoundError(strategy_id)
