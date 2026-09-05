"""Portfolio route — GET /strategies/{id}/portfolio"""

from fastapi import APIRouter, Depends
from app.core.dependencies import get_portfolio_service
from app.schemas.base import ApiResponse
from app.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/strategies", tags=["Portfolio"])


@router.get("/{strategy_id}/portfolio", summary="Get portfolio snapshot")
async def get_portfolio(
    strategy_id: str,
    service: PortfolioService = Depends(get_portfolio_service),
):
    """Current portfolio state — equity, cash, positions, allocations."""
    snapshot = service.get_portfolio_snapshot(strategy_id)
    return ApiResponse.ok(data=snapshot.model_dump())
