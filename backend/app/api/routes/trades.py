"""
Trades routes.

GET  /strategies/{id}/trades         → paginated filtered trades
GET  /strategies/{id}/trades/summary → aggregated trade stats
GET  /strategies/{id}/trades/export  → download as CSV
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.core.dependencies import get_trade_service
from app.schemas.base import ApiResponse, PaginatedResponse
from app.services.trade_service import TradeService

router = APIRouter(prefix="/strategies", tags=["Trades"])


@router.get("/{strategy_id}/trades", summary="Get paginated trades")
async def get_trades(
    strategy_id: str,
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=200),
    status: Optional[str] = Query(default=None),
    symbol: Optional[str] = Query(default=None),
    exitReason: Optional[str] = Query(default=None),
    dateFrom: Optional[str] = Query(default=None),
    dateTo: Optional[str] = Query(default=None),
    sort: str = Query(default="entryDate"),
    dir: str = Query(default="desc"),
    service: TradeService = Depends(get_trade_service),
):
    """Paginated trade history with filtering and sorting."""
    trades, total = service.get_trades(
        strategy_id=strategy_id,
        page=page,
        page_size=pageSize,
        status=status,
        symbol=symbol,
        exit_reason=exitReason,
        date_from=dateFrom,
        date_to=dateTo,
        sort_field=sort,
        sort_dir=dir,
    )
    paginated = PaginatedResponse.build(
        items=[t.model_dump() for t in trades],
        total=total,
        page=page,
        page_size=pageSize,
    )
    return ApiResponse.ok(data=paginated.model_dump())


@router.get("/{strategy_id}/trades/summary", summary="Get trade statistics")
async def get_trade_summary(
    strategy_id: str,
    service: TradeService = Depends(get_trade_service),
):
    """Aggregated performance statistics for all trades."""
    summary = service.get_trade_summary(strategy_id)
    return ApiResponse.ok(data=summary.model_dump())


@router.get("/{strategy_id}/trades/export", summary="Export trades as CSV")
async def export_trades(
    strategy_id: str,
    service: TradeService = Depends(get_trade_service),
):
    """Download all trades as a CSV file."""
    csv_content = service.export_csv(strategy_id)

    def _iter():
        yield csv_content.encode("utf-8")

    return StreamingResponse(
        _iter(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={strategy_id}-trades.csv"
        },
    )
