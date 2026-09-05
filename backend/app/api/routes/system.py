"""System health and status routes."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import get_settings
from app.domain.strategy_registry import get_strategy_registry
from app.infrastructure.task_runner.background_runner import get_task_runner
from app.schemas.base import ApiResponse

router = APIRouter(tags=["System"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return ApiResponse.ok(
        data={"status": "ok", "version": get_settings().API_VERSION},
        message="TradePilot backend is running.",
    )


@router.get("/system/status")
async def system_status():
    """Engine status, registered strategies, running tasks."""
    registry = get_strategy_registry()
    runner = get_task_runner()
    settings = get_settings()

    running_tasks = [
        t.to_dict()
        for t in runner.list_tasks()
        if t.state.value in ("queued", "running")
    ]

    return ApiResponse.ok(
        data={
            "status": "operational",
            "version": settings.API_VERSION,
            "engineRoot": str(settings.engine_root_path),
            "resultsPath": str(settings.results_path),
            "registeredStrategies": registry.strategy_ids,
            "runningTasks": running_tasks,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
