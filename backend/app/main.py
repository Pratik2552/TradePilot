"""
TradePilot Backend — FastAPI Application Factory

Architecture:
    Frontend → FastAPI → Application Services → Domain → Repositories → Engine

No business logic here. This file only wires up:
    - CORS
    - Exception handlers
    - Router registration
    - Lifespan events (startup logging)
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.core.config import get_settings
from app.core.error_handlers import register_error_handlers
from app.core.logging import get_logger
from app.domain.strategy_registry import get_strategy_registry

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown."""
    settings = get_settings()
    registry = get_strategy_registry()

    logger.info("=" * 60)
    logger.info(f"TradePilot Backend v{settings.API_VERSION}")
    logger.info(f"Engine Root   : {settings.engine_root_path}")
    logger.info(f"Results Path  : {settings.results_path}")
    logger.info(
        f"Strategies    : {registry.strategy_ids}"
    )
    logger.info(f"CORS Origins  : {settings.cors_origins}")
    logger.info("=" * 60)

    yield

    logger.info("TradePilot Backend shutting down.")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ---- CORS -------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- Exception Handlers ----------------------------------------
    register_error_handlers(app)

    # ---- Routes -----------------------------------------------------
    app.include_router(router)

    return app


app = create_app()
