"""
TradePilot — Background Task Runner (FastAPI BackgroundTasks Implementation)

Uses Python threads for background execution. No Redis or Celery required.
Task state is kept in memory — restarts clear state (acceptable for dev).

For production, swap to CeleryRunner by implementing BaseTaskRunner.
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any, Callable

from app.core.logging import get_logger
from app.infrastructure.task_runner.base import (
    BaseTaskRunner,
    TaskState,
    TaskStatus,
    create_task_id,
)

logger = get_logger(__name__)


class BackgroundTaskRunner(BaseTaskRunner):
    """
    In-process background task runner using Python threads.
    Thread-safe task registry with in-memory state.
    """

    def __init__(self) -> None:
        self._tasks: dict[str, TaskStatus] = {}
        self._lock = threading.Lock()

    def submit(
        self,
        task_type: str,
        strategy_id: str,
        fn: Callable[[], None],
        **kwargs: Any,
    ) -> TaskStatus:
        task_id = create_task_id()

        status = TaskStatus(
            task_id=task_id,
            task_type=task_type,
            strategy_id=strategy_id,
            state=TaskState.QUEUED,
            message=f"{task_type.capitalize()} queued.",
        )

        with self._lock:
            self._tasks[task_id] = status

        thread = threading.Thread(
            target=self._run,
            args=(task_id, fn),
            daemon=True,
            name=f"tradepilot-{task_type}-{strategy_id}",
        )
        thread.start()

        logger.info(
            f"Task submitted: [{task_id}] {task_type} for strategy '{strategy_id}'"
        )
        return status

    def _run(self, task_id: str, fn: Callable[[], None]) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return
            task.state = TaskState.RUNNING
            task.started_at = datetime.now(timezone.utc)
            task.message = "Running..."
            task.progress = 5

        try:
            fn()
            with self._lock:
                task = self._tasks[task_id]
                task.state = TaskState.COMPLETED
                task.progress = 100
                task.completed_at = datetime.now(timezone.utc)
                task.message = "Completed successfully."
            logger.info(f"Task completed: [{task_id}]")

        except Exception as exc:
            with self._lock:
                task = self._tasks[task_id]
                task.state = TaskState.FAILED
                task.error = str(exc)
                task.completed_at = datetime.now(timezone.utc)
                task.message = f"Failed: {exc}"
            logger.error(f"Task failed: [{task_id}] {exc}")

    def get_status(self, task_id: str) -> TaskStatus | None:
        return self._tasks.get(task_id)

    def is_running(self, task_type: str, strategy_id: str) -> bool:
        with self._lock:
            for task in self._tasks.values():
                if (
                    task.task_type == task_type
                    and task.strategy_id == strategy_id
                    and task.state in (TaskState.QUEUED, TaskState.RUNNING)
                ):
                    return True
        return False

    def list_tasks(
        self, strategy_id: str | None = None
    ) -> list[TaskStatus]:
        with self._lock:
            tasks = list(self._tasks.values())
        if strategy_id:
            tasks = [t for t in tasks if t.strategy_id == strategy_id]
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)


# ---- Singleton -----------------------------------------------------------

_task_runner: BackgroundTaskRunner | None = None


def get_task_runner() -> BackgroundTaskRunner:
    global _task_runner
    if _task_runner is None:
        _task_runner = BackgroundTaskRunner()
    return _task_runner
