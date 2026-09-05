"""
TradePilot — Task Runner Abstraction

Long-running tasks (scanner, backtest, optimizer) must not block HTTP requests.
Today: FastAPI BackgroundTasks (in-process threads).
Tomorrow: swap to CeleryRunner or RQRunner without changing any service code.

TaskStatus model tracks task lifecycle:
    queued → running → completed | failed
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable


class TaskState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskStatus:
    task_id: str
    task_type: str           # "scan", "backtest", "optimize"
    strategy_id: str
    state: TaskState = TaskState.QUEUED
    progress: int = 0        # 0–100
    message: str = ""
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "taskId": self.task_id,
            "taskType": self.task_type,
            "strategyId": self.strategy_id,
            "state": self.state.value,
            "progress": self.progress,
            "message": self.message,
            "result": self.result,
            "error": self.error,
            "createdAt": self.created_at.isoformat(),
            "startedAt": self.started_at.isoformat() if self.started_at else None,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
        }


class BaseTaskRunner(ABC):
    """Abstract task runner. Subclass to use Celery, RQ, etc."""

    @abstractmethod
    def submit(
        self,
        task_type: str,
        strategy_id: str,
        fn: Callable[[], None],
        **kwargs: Any,
    ) -> TaskStatus:
        """Submit a task for background execution. Returns immediately with TaskStatus."""

    @abstractmethod
    def get_status(self, task_id: str) -> TaskStatus | None:
        """Return current task status, or None if not found."""

    @abstractmethod
    def is_running(self, task_type: str, strategy_id: str) -> bool:
        """Check if a task of this type is currently running for this strategy."""


def create_task_id() -> str:
    return str(uuid.uuid4())
