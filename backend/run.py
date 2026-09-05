"""
TradePilot Backend — Uvicorn Entry Point

Run with:
    python run.py
Or directly:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""

import uvicorn
from app.core.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
