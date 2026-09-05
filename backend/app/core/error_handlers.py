"""
TradePilot Backend — Global Exception Handlers

Registered on the FastAPI app in main.py.
Every TradePilotError subclass produces a standardized JSON error response
matching the frontend ApiError interface exactly.
"""

from __future__ import annotations

import traceback
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.exceptions import TradePilotError
from app.core.logging import get_logger

logger = get_logger(__name__)


def _error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: dict | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "data": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": {
                "code": error_code,
                "message": message,
                "statusCode": status_code,
                "details": details or {},
            },
        },
    )


def register_error_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI application."""

    @app.exception_handler(TradePilotError)
    async def tradepilot_error_handler(
        request: Request, exc: TradePilotError
    ) -> JSONResponse:
        logger.warning(
            "Domain error",
            extra={
                "error_code": exc.error_code,
                "status_code": exc.status_code,
                "message": exc.message,
                "path": str(request.url),
            },
        )
        return _error_response(
            status_code=exc.status_code,
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = {}
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            details.setdefault(field, []).append(error["msg"])

        logger.warning(
            "Request validation failed",
            extra={"path": str(request.url), "details": details},
        )
        return _error_response(
            status_code=422,
            error_code="VALIDATION_ERROR",
            message="Request validation failed.",
            details=details,
        )

    @app.exception_handler(ValidationError)
    async def pydantic_error_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        return _error_response(
            status_code=422,
            error_code="VALIDATION_ERROR",
            message="Data validation failed.",
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(
            "Unhandled exception",
            extra={
                "path": str(request.url),
                "exception": type(exc).__name__,
                "traceback": traceback.format_exc(),
            },
        )
        return _error_response(
            status_code=500,
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred. Please try again later.",
        )
