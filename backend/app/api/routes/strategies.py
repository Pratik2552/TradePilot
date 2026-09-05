"""
Strategy routes.

GET  /strategies           → list all strategies
GET  /strategies/{id}      → full strategy detail
PATCH /strategies/{id}/config → update config
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.dependencies import get_strategy_service
from app.schemas.base import ApiResponse
from app.schemas.strategy import UpdateStrategyConfigRequest
from app.services.strategy_service import StrategyService

router = APIRouter(prefix="/strategies", tags=["Strategies"])


@router.get("", summary="List all strategies")
async def list_strategies(
    service: StrategyService = Depends(get_strategy_service),
):
    """
    Returns all registered strategy plugins with summary stats.
    Frontend uses this to populate the strategies list page.
    """
    items = service.list_strategies()
    return ApiResponse.ok(data=[i.model_dump() for i in items])


@router.get("/{strategy_id}", summary="Get strategy detail")
async def get_strategy(
    strategy_id: str,
    service: StrategyService = Depends(get_strategy_service),
):
    """
    Returns full strategy detail including config, stats, and manifest.
    Frontend uses this for the strategy overview page.
    """
    strategy = service.get_strategy(strategy_id)
    return ApiResponse.ok(data=strategy.model_dump())


@router.patch("/{strategy_id}/config", summary="Update strategy configuration")
async def update_strategy_config(
    strategy_id: str,
    body: UpdateStrategyConfigRequest,
    service: StrategyService = Depends(get_strategy_service),
):
    """Update strategy configuration overrides. Merges with defaults."""
    strategy = service.update_config(strategy_id, body)
    return ApiResponse.ok(
        data=strategy.model_dump(),
        message="Strategy configuration updated.",
    )
