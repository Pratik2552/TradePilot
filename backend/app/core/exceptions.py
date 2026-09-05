"""
TradePilot Backend — Custom Exception Hierarchy

All domain exceptions live here. FastAPI error handlers convert these
into standardized JSON responses. Services raise these; routes never
catch exceptions except to re-raise as HTTP errors.

Hierarchy:
    TradePilotError (base)
    ├── NotFoundError (404)
    │   ├── StrategyNotFoundError
    │   ├── TaskNotFoundError
    │   └── TradeNotFoundError
    ├── ConflictError (409)
    │   ├── ScanAlreadyRunningError
    │   └── BacktestAlreadyRunningError
    ├── ValidationError (422)
    │   └── InvalidStrategyConfigError
    ├── EngineError (500)
    │   ├── EngineNotReadyError (503)
    │   ├── ScannerError
    │   └── BacktestError
    └── RepositoryError (500)
"""

from __future__ import annotations


class TradePilotError(Exception):
    """Base exception for all TradePilot domain errors."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


# ==============================================================
# 404 — Not Found
# ==============================================================


class NotFoundError(TradePilotError):
    status_code = 404
    error_code = "NOT_FOUND"


class StrategyNotFoundError(NotFoundError):
    error_code = "STRATEGY_NOT_FOUND"

    def __init__(self, strategy_id: str) -> None:
        super().__init__(f"Strategy '{strategy_id}' not found.")
        self.strategy_id = strategy_id


class TaskNotFoundError(NotFoundError):
    error_code = "TASK_NOT_FOUND"

    def __init__(self, task_id: str) -> None:
        super().__init__(f"Task '{task_id}' not found.")


class TradeNotFoundError(NotFoundError):
    error_code = "TRADE_NOT_FOUND"

    def __init__(self, trade_id: str) -> None:
        super().__init__(f"Trade '{trade_id}' not found.")


# ==============================================================
# 409 — Conflict
# ==============================================================


class ConflictError(TradePilotError):
    status_code = 409
    error_code = "CONFLICT"


class ScanAlreadyRunningError(ConflictError):
    error_code = "SCAN_ALREADY_RUNNING"

    def __init__(self, strategy_id: str) -> None:
        super().__init__(
            f"A scan is already running for strategy '{strategy_id}'. "
            "Wait for it to complete before starting another."
        )


class BacktestAlreadyRunningError(ConflictError):
    error_code = "BACKTEST_ALREADY_RUNNING"

    def __init__(self, strategy_id: str) -> None:
        super().__init__(
            f"A backtest is already running for strategy '{strategy_id}'. "
            "Wait for it to complete before starting another."
        )


# ==============================================================
# 422 — Validation / Business Logic
# ==============================================================


class InvalidStrategyConfigError(TradePilotError):
    status_code = 422
    error_code = "INVALID_STRATEGY_CONFIG"


# ==============================================================
# 503 — Engine / Infrastructure
# ==============================================================


class EngineError(TradePilotError):
    status_code = 500
    error_code = "ENGINE_ERROR"


class EngineNotReadyError(EngineError):
    status_code = 503
    error_code = "ENGINE_NOT_READY"

    def __init__(self, reason: str = "No cached data available. Run a scan first.") -> None:
        super().__init__(reason)


class ScannerError(EngineError):
    error_code = "SCANNER_ERROR"


class BacktestError(EngineError):
    error_code = "BACKTEST_ERROR"


class RepositoryError(TradePilotError):
    status_code = 500
    error_code = "REPOSITORY_ERROR"
