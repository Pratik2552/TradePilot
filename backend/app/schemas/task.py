"""Task status schema."""
from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel


class TaskStatusSchema(BaseModel):
    taskId: str
    taskType: str
    strategyId: str
    state: str
    progress: int = 0
    message: str = ""
    result: Optional[dict] = None
    error: Optional[str] = None
    createdAt: str
    startedAt: Optional[str] = None
    completedAt: Optional[str] = None
