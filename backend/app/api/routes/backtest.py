"""
Backtest routes.

POST /strategies/{id}/backtest/run         → trigger background backtest
GET  /strategies/{id}/backtest/run/{task}  → poll backtest task
"""

from fastapi import APIRouter, Depends
from app.core.dependencies import get_backtest_service
from app.core.exceptions import TaskNotFoundError
from app.schemas.base import ApiResponse
from app.services.backtest_service import BacktestService

router = APIRouter(prefix="/strategies", tags=["Backtest"])


@router.post("/{strategy_id}/backtest/run", summary="Trigger backtest")
async def run_backtest(
    strategy_id: str,
    service: BacktestService = Depends(get_backtest_service),
):
    """
    Trigger a background backtest. Returns immediately with task_id.
    Note: backtest uses cached data — run a scan first to populate cache.
    """
    task = service.run_backtest(strategy_id)
    return ApiResponse.ok(
        data=task.to_dict(),
        message="Backtest started in background.",
    )


@router.get("/{strategy_id}/backtest/run/{task_id}", summary="Poll backtest task")
async def get_backtest_task_status(
    strategy_id: str,
    task_id: str,
    service: BacktestService = Depends(get_backtest_service),
):
    """Poll the status of a running or completed backtest task."""
    task = service.get_task_status(task_id)
    if task is None:
        raise TaskNotFoundError(task_id)
    return ApiResponse.ok(data=task.to_dict())
