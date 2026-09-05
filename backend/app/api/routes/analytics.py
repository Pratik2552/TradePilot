"""Analytics route — GET /strategies/{id}/analytics"""

from fastapi import APIRouter, Depends
from app.core.dependencies import get_analytics_service
from app.schemas.base import ApiResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/strategies", tags=["Analytics"])


@router.get("/{strategy_id}/analytics", summary="Get full analytics snapshot")
async def get_analytics(
    strategy_id: str,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Computes and returns full analytics:
    Sharpe, Sortino, Calmar, drawdown periods, monthly returns,
    equity curve with drawdown %, return distribution, holding distribution.
    """
    snapshot = service.get_analytics(strategy_id)
    return ApiResponse.ok(data=snapshot.model_dump())
