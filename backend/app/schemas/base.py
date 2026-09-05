"""
TradePilot — Base Pydantic Schemas

Matches the frontend TypeScript interfaces exactly:
    ApiResponse<T>     → success, data, message, timestamp
    PaginatedResponse<T> → data, total, page, pageSize, totalPages, hasMore
    ApiError           → code, message, statusCode, details
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API envelope. Matches frontend ApiResponse<T>."""
    success: bool = True
    data: T
    message: str = "OK"
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @classmethod
    def ok(cls, data: Any, message: str = "OK") -> "ApiResponse":
        return cls(success=True, data=data, message=message)


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list wrapper. Matches frontend PaginatedResponse<T>."""
    data: List[T]
    total: int
    page: int
    pageSize: int
    totalPages: int
    hasMore: bool

    @classmethod
    def build(
        cls,
        items: list,
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse":
        total_pages = max(1, (total + page_size - 1) // page_size)
        return cls(
            data=items,
            total=total,
            page=page,
            pageSize=page_size,
            totalPages=total_pages,
            hasMore=(page * page_size) < total,
        )
