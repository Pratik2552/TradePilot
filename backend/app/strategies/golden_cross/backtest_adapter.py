"""
Golden Cross Strategy Plugin — Backtest Adapter

Wraps the existing backtester/backtest_engine.py run_backtest() function.
This is NOT a rewrite — it's a thin wrapper that manages CWD + imports.
"""

from __future__ import annotations

import os
import sys
from typing import Any

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def run_backtest(config: dict[str, Any]) -> dict[str, Any]:
    """
    Run the Golden Cross historical backtest.

    Args:
        config: Strategy config (initial_capital, allocation, max_positions, etc.)

    Returns:
        dict with summary of backtest results
    """
    settings = get_settings()
    engine_root = settings.engine_root_path
    original_cwd = os.getcwd()

    # Ensure engine root is on sys.path
    engine_str = str(engine_root)
    if engine_str not in sys.path:
        sys.path.insert(0, engine_str)

    try:
        os.chdir(engine_root)
        logger.info(f"GoldenCross Backtest: CWD set to {engine_root}")

        # Import after CWD set
        from backtester.backtest_engine import run_backtest as _engine_backtest

        # The existing engine reads config from config.py
        # We patch the config module with user values before running
        import config as engine_config
        original_values = {}

        param_map = {
            "stop_loss_percent": "STOP_LOSS_PERCENT",
            "golden_cross_lookback": "GOLDEN_CROSS_LOOKBACK",
            "gap_threshold": "GAP_THRESHOLD",
        }

        for config_key, engine_key in param_map.items():
            if config_key in config:
                original_values[engine_key] = getattr(engine_config, engine_key, None)
                setattr(engine_config, engine_key, config[config_key])

        try:
            _engine_backtest()
        finally:
            # Restore original config values
            for engine_key, original_val in original_values.items():
                setattr(engine_config, engine_key, original_val)

        logger.info("GoldenCross Backtest: completed successfully.")
        return {"status": "completed"}

    except Exception as exc:
        logger.error(f"GoldenCross Backtest: failed — {exc}")
        raise

    finally:
        os.chdir(original_cwd)
