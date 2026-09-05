"""
TradePilot — Dependency Injection

All injectable dependencies are defined here.
Routes declare deps with `Depends(...)` — no direct instantiation.
Swapping implementations requires changing only this file.
"""

from __future__ import annotations

from app.infrastructure.repositories.csv_repository import CSVRepository
from app.infrastructure.task_runner.background_runner import get_task_runner
from app.services.analytics_service import AnalyticsService
from app.services.backtest_service import BacktestService
from app.services.portfolio_service import PortfolioService
from app.services.scanner_service import ScannerService
from app.services.strategy_service import StrategyService
from app.services.trade_service import TradeService


def get_repository() -> CSVRepository:
    """Today: CSV. Tomorrow: swap to PostgreSQLRepository here."""
    return CSVRepository()


def get_strategy_service() -> StrategyService:
    return StrategyService(repository=get_repository())


def get_scanner_service() -> ScannerService:
    return ScannerService(
        repository=get_repository(),
        task_runner=get_task_runner(),
    )


def get_trade_service() -> TradeService:
    return TradeService(repository=get_repository())


def get_portfolio_service() -> PortfolioService:
    return PortfolioService(repository=get_repository())


def get_analytics_service() -> AnalyticsService:
    return AnalyticsService(repository=get_repository())


def get_backtest_service() -> BacktestService:
    return BacktestService(
        repository=get_repository(),
        task_runner=get_task_runner(),
    )
