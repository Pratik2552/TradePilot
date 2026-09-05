"""
Golden Cross Strategy Plugin — Scanner Adapter

Wraps the existing backtester/engine.py run_backtest() function
(which in scanner mode finds fresh golden crossovers).

This is NOT a rewrite. It is a thin adapter that:
1. Sets up the correct working directory
2. Calls the engine's existing scan function
3. Returns structured results
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def run_scanner(config: dict[str, Any]) -> dict[str, Any]:
    """
    Run the Golden Cross scanner.

    Args:
        config: Strategy config (lookback, etc.)

    Returns:
        dict with keys: fresh_crossovers (list), entered_positions (list)
    """
    settings = get_settings()
    engine_root = settings.engine_root_path
    original_cwd = os.getcwd()

    # Ensure engine root is on sys.path
    engine_str = str(engine_root)
    if engine_str not in sys.path:
        sys.path.insert(0, engine_str)

    try:
        # Change working directory so the engine's relative paths resolve correctly
        os.chdir(engine_root)
        logger.info(f"GoldenCross Scanner: CWD set to {engine_root}")

        # Import engine modules (after CWD change)
        from data.universe import refresh_universe, load_symbols
        from data.downloader import get_stock_data
        from indicators.ema import add_ema
        from strategy.golden_cross import find_recent_golden_cross
        from strategy.gap_tracker import analyze_gap
        from strategy.ranking import rank_stock

        import pandas as pd

        lookback = int(config.get("golden_cross_lookback", 3))

        # Refresh NSE universe
        refresh_universe()
        symbols = load_symbols()
        logger.info(f"GoldenCross Scanner: scanning {len(symbols)} symbols")

        # Load entered positions
        entered_file = engine_root / "data" / "entered_positions.csv"
        if entered_file.exists():
            entered_positions = pd.read_csv(entered_file)
        else:
            entered_positions = pd.DataFrame()

        fresh_crossovers = []
        entered_status = []
        total = len(symbols)

        for i, symbol in enumerate(symbols, start=1):
            if i % 200 == 0:
                logger.info(f"GoldenCross Scanner: [{i}/{total}] {symbol}")

            try:
                df = get_stock_data(symbol)
                if len(df) < 250:
                    continue

                for period in [9, 21, 50, 200]:
                    df = add_ema(df, period)

                # Fresh Golden Cross
                recent_gc = find_recent_golden_cross(df, lookback)
                if recent_gc is not None:
                    ranking = rank_stock(df)
                    clean_symbol = symbol.replace(".NS", "")
                    fresh_crossovers.append({
                        "Symbol": symbol,
                        "Date": str(recent_gc["Date"])[:10],
                        "Close": round(float(recent_gc["Close"]), 2),
                        "Current Volume": ranking["Current Volume"],
                        "20D Avg Volume": ranking["20D Avg Volume"],
                        "Volume Ratio": ranking["Volume Ratio"],
                        "EMA Distance %": ranking["EMA Distance %"],
                        "EMA50": round(float(recent_gc["EMA50"]), 2),
                        "EMA200": round(float(recent_gc["EMA200"]), 2),
                        "TradingView": f"https://www.tradingview.com/chart/?symbol=NSE:{clean_symbol}",
                        "Screener": f"https://www.screener.in/company/{clean_symbol}/",
                    })

                # Entered position tracking
                if not entered_positions.empty:
                    trade = entered_positions[entered_positions["Symbol"] == symbol]
                    if not trade.empty:
                        gap = analyze_gap(df, trade.iloc[0]["Entry Date"])
                        if gap is not None:
                            entered_status.append({
                                "Symbol": symbol,
                                "Highest Gap": gap["Highest Gap"],
                                "Current Gap": gap["Current Gap"],
                                "Gap %": gap["Gap %"],
                            })

            except Exception as exc:
                logger.debug(f"GoldenCross Scanner: {symbol} skipped — {exc}")

        # Persist results
        results_dir = engine_root / "results"
        results_dir.mkdir(exist_ok=True)

        fresh_df = pd.DataFrame(fresh_crossovers)
        if not fresh_df.empty:
            fresh_df = fresh_df.sort_values("Volume Ratio", ascending=False)
        fresh_df.to_csv(results_dir / "fresh_crossovers.csv", index=False)

        pd.DataFrame(entered_status).to_csv(
            results_dir / "entered_positions_status.csv", index=False
        )

        logger.info(
            f"GoldenCross Scanner: completed. "
            f"Fresh crossovers: {len(fresh_crossovers)}, "
            f"Entered stocks: {len(entered_status)}"
        )

        return {
            "fresh_crossovers": fresh_crossovers,
            "entered_positions": entered_status,
        }

    finally:
        os.chdir(original_cwd)
