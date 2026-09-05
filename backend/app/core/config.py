"""
TradePilot Backend — Application Settings

Uses pydantic-settings to load from .env file and environment variables.
All configuration is centralized here. Nothing else reads os.environ directly.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Server -----------------------------------------------------------
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    LOG_LEVEL: str = "info"

    # ---- CORS -------------------------------------------------------------
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://10.43.176.25:3000"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    # ---- Paths ------------------------------------------------------------
    ENGINE_ROOT: str = ""
    RESULTS_DIR: str = "results"
    DATA_CACHE_DIR: str = "data/cache"

    @property
    def engine_root_path(self) -> Path:
        """
        Absolute path to the Python engine root.
        If ENGINE_ROOT is empty, auto-detect: backend/ is a child of the project root.
        Path traversal: config.py -> core/ -> app/ -> backend/ -> PROJECT_ROOT
        """
        if self.ENGINE_ROOT:
            return Path(self.ENGINE_ROOT).resolve()
        # config.py is at: PROJECT_ROOT/backend/app/core/config.py
        # So parent.parent.parent.parent = PROJECT_ROOT
        return Path(__file__).resolve().parent.parent.parent.parent

    @property
    def results_path(self) -> Path:
        root = self.engine_root_path
        p = Path(self.RESULTS_DIR)
        return p if p.is_absolute() else root / p

    @property
    def data_cache_path(self) -> Path:
        root = self.engine_root_path
        p = Path(self.DATA_CACHE_DIR)
        return p if p.is_absolute() else root / p

    @property
    def strategies_config_path(self) -> Path:
        """Where strategy-level config JSON files live."""
        path = self.results_path / "strategies"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def watchlist_path(self) -> Path:
        return self.results_path / "watchlist.json"

    # ---- Default Engine Config --------------------------------------------
    DEFAULT_INITIAL_CAPITAL: float = 100_000.0
    DEFAULT_ALLOCATION: float = 0.10
    DEFAULT_MAX_POSITIONS: int = 10
    DEFAULT_STOP_LOSS_PERCENT: float = -15.0
    DEFAULT_GOLDEN_CROSS_LOOKBACK: int = 3
    DEFAULT_GAP_THRESHOLD: float = 0.50

    # ---- API --------------------------------------------------------------
    API_TITLE: str = "TradePilot Research Platform"
    API_DESCRIPTION: str = (
        "Production-grade quantitative trading research platform. "
        "Strategy-agnostic, pluggable, multi-exchange ready."
    )
    API_VERSION: str = "1.0.0"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings singleton. Import and call this everywhere."""
    return Settings()
