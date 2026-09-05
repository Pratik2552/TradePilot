"""
TradePilot — Backtest Service

Orchestrates the backtest workflow as a background task.
"""

from __future__ import annotations

import importlib
from typing import Any

from app.core.exceptions import BacktestAlreadyRunningError, StrategyNotFoundError
from app.core.logging import get_logger
from app.domain.strategy_registry import get_strategy_registry
from app.infrastructure.repositories.base import BaseRepository
from app.infrastructure.task_runner.background_runner import BackgroundTaskRunner
from app.infrastructure.task_runner.base import TaskStatus

logger = get_logger(__name__)


class BacktestService:
    def __init__(
        self,
        repository: BaseRepository,
        task_runner: BackgroundTaskRunner,
    ) -> None:
        self._repo = repository
        self._tasks = task_runner
        self._registry = get_strategy_registry()

    def run_backtest(
        self,
        strategy_id: str,
        config_overrides: dict[str, Any] | None = None,
        user_id: str = "default",
    ) -> TaskStatus:
        if not self._registry.exists(strategy_id):
            raise StrategyNotFoundError(strategy_id)

        if self._tasks.is_running("backtest", strategy_id):
            raise BacktestAlreadyRunningError(strategy_id)

        raw_config = self._repo.load_strategy_config(strategy_id, user_id) or {}
        if config_overrides:
            raw_config.update(config_overrides)

        adapter_fn = self._load_backtest_adapter(strategy_id)

        def _task() -> None:
            adapter_fn(raw_config)

        return self._tasks.submit(
            task_type="backtest",
            strategy_id=strategy_id,
            fn=_task,
        )

    def get_task_status(self, task_id: str) -> TaskStatus | None:
        return self._tasks.get_status(task_id)

    def _load_backtest_adapter(self, strategy_id: str):
        module_name = strategy_id.replace("-", "_")
        try:
            module = importlib.import_module(
                f"app.strategies.{module_name}.backtest_adapter"
            )
            return module.run_backtest
        except (ImportError, AttributeError) as exc:
            logger.error(f"BacktestService: no adapter for '{strategy_id}': {exc}")
            raise StrategyNotFoundError(strategy_id)
