"""
TradePilot — API Router

Aggregates all domain routers. No API prefix — matches frontend API_CONTRACT.md exactly.
"""

from fastapi import APIRouter

from app.api.routes import (
    analytics,
    backtest,
    portfolio,
    scanner,
    strategies,
    system,
    trades,
)

router = APIRouter()

# System
router.include_router(system.router)

# Domain
router.include_router(strategies.router)
router.include_router(scanner.router)
router.include_router(trades.router)
router.include_router(portfolio.router)
router.include_router(analytics.router)
router.include_router(backtest.router)
