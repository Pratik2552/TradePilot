"""
Scanner routes.

GET  /strategies/{id}/scanner          → paginated scan results
GET  /strategies/{id}/scanner/summary  → summary stats
POST /strategies/{id}/scanner/run      → trigger background scan
GET  /strategies/{id}/scanner/run/{task_id} → poll task status
GET  /strategies/{id}/scanner/watchlist     → watchlist items
POST /strategies/{id}/watchlist/{symbol}    → toggle watchlist
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_scanner_service
from app.core.exceptions import TaskNotFoundError
from app.schemas.base import ApiResponse, PaginatedResponse
from app.schemas.scanner import RunScanRequest
from app.services.scanner_service import ScannerService

router = APIRouter(prefix="/strategies", tags=["Scanner"])


@router.get("/{strategy_id}/scanner", summary="Get scan results")
async def get_scan_results(
    strategy_id: str,
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=50, ge=1, le=200),
    search: Optional[str] = Query(default=None),
    signalStrength: Optional[List[str]] = Query(default=None),
    isWatchlisted: Optional[bool] = Query(default=None),
    service: ScannerService = Depends(get_scanner_service),
):
    """Paginated and filtered scanner results."""
    results, total = service.get_scan_results(
        strategy_id=strategy_id,
        page=page,
        page_size=pageSize,
        search=search,
        signal_strength=signalStrength,
        is_watchlisted=isWatchlisted,
    )
    paginated = PaginatedResponse.build(
        items=[r.model_dump() for r in results],
        total=total,
        page=page,
        page_size=pageSize,
    )
    return ApiResponse.ok(data=paginated.model_dump())


@router.get("/{strategy_id}/scanner/summary", summary="Get scanner summary")
async def get_scanner_summary(
    strategy_id: str,
    service: ScannerService = Depends(get_scanner_service),
):
    """Summary stats for the latest scan run."""
    summary = service.get_scanner_summary(strategy_id)
    return ApiResponse.ok(data=summary.model_dump())


@router.post("/{strategy_id}/scanner/run", summary="Trigger scanner")
async def run_scanner(
    strategy_id: str,
    body: Optional[RunScanRequest] = None,
    service: ScannerService = Depends(get_scanner_service),
):
    """
    Trigger a background scan. Returns immediately with task_id.
    Poll GET /scanner/run/{task_id} for progress.
    """
    config_overrides = {}
    if body and body.goldenCrossLookback is not None:
        config_overrides["golden_cross_lookback"] = body.goldenCrossLookback

    task = service.run_scan(strategy_id, config_overrides)
    return ApiResponse.ok(
        data=task.to_dict(),
        message="Scanner started in background.",
    )


@router.get("/{strategy_id}/scanner/run/{task_id}", summary="Poll scan task")
async def get_scan_task_status(
    strategy_id: str,
    task_id: str,
    service: ScannerService = Depends(get_scanner_service),
):
    """Poll the status of a running or completed scan task."""
    task = service.get_task_status(task_id)
    if task is None:
        raise TaskNotFoundError(task_id)
    return ApiResponse.ok(data=task.to_dict())


@router.get("/{strategy_id}/scanner/watchlist", summary="Get watchlist")
async def get_watchlist(
    strategy_id: str,
    service: ScannerService = Depends(get_scanner_service),
):
    """Return watchlisted symbols for this strategy."""
    items = service.get_watchlist(strategy_id)
    return ApiResponse.ok(data=[i.model_dump() for i in items])


@router.post("/{strategy_id}/watchlist/{symbol}", summary="Toggle watchlist")
async def toggle_watchlist(
    strategy_id: str,
    symbol: str,
    service: ScannerService = Depends(get_scanner_service),
):
    """Add or remove a symbol from the watchlist. Returns new state."""
    is_watchlisted = service.toggle_watchlist(strategy_id, symbol.upper())
    return ApiResponse.ok(
        data={"isWatchlisted": is_watchlisted, "symbol": symbol.upper()},
        message=f"{'Added to' if is_watchlisted else 'Removed from'} watchlist.",
    )
