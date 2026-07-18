from pathlib import Path

import pandas as pd

from config import GOLDEN_CROSS_LOOKBACK
from data.universe import refresh_universe, load_symbols
from data.downloader import get_stock_data
from indicators.ema import add_ema
from strategy.golden_cross import find_recent_golden_cross
from strategy.gap_tracker import analyze_gap
from strategy.ranking import rank_stock


def run_backtest():

    # ----------------------------------------------------------
    # Refresh NSE Universe
    # ----------------------------------------------------------

    refresh_universe()

    symbols = load_symbols()

    print(f"\nLoaded {len(symbols)} NSE stocks.\n")

    # ----------------------------------------------------------
    # Entered Positions
    # ----------------------------------------------------------

    entered_file = Path("data/entered_positions.csv")
    entered_positions = pd.read_csv(entered_file)

    # ----------------------------------------------------------
    # Results
    # ----------------------------------------------------------

    fresh_crossovers = []
    entered_status = []

    total = len(symbols)

    # ----------------------------------------------------------
    # Scan
    # ----------------------------------------------------------

    for i, symbol in enumerate(symbols, start=1):

        print(f"[{i}/{total}] {symbol}")

        try:

            df = get_stock_data(symbol)

            if len(df) < 250:
                continue

            for period in [9, 21, 50, 200]:
                df = add_ema(df, period)

            # -------------------------
            # Fresh Golden Cross
            # -------------------------

            recent_gc = find_recent_golden_cross(
                df,
                GOLDEN_CROSS_LOOKBACK,
            )

            if recent_gc is not None:

                ranking = rank_stock(df)

                fresh_crossovers.append({

                    "Symbol": symbol,
                    "Date": recent_gc["Date"],
                    "Close": round(float(recent_gc["Close"]), 2),

                    "Current Volume": ranking["Current Volume"],
                    "20D Avg Volume": ranking["20D Avg Volume"],
                    "Volume Ratio": ranking["Volume Ratio"],
                    "EMA Distance %": ranking["EMA Distance %"],

                    "EMA50": round(float(recent_gc["EMA50"]), 2),
                    "EMA200": round(float(recent_gc["EMA200"]), 2),

                    "TradingView":
                        f"https://www.tradingview.com/chart/?symbol=NSE:{symbol.replace('.NS','')}",

                    "Screener":
                        f"https://www.screener.in/company/{symbol.replace('.NS','')}/"

                })

            # -------------------------
            # Entered Positions
            # -------------------------

            if entered_positions.empty:
                continue

            trade = entered_positions[
                entered_positions["Symbol"] == symbol
            ]

            if trade.empty:
                continue

            gap = analyze_gap(
                df,
                trade.iloc[0]["Entry Date"],
            )

            if gap is None:
                continue

            entered_status.append({

                "Symbol": symbol,

                "Highest Gap": gap["Highest Gap"],
                "Current Gap": gap["Current Gap"],
                "Gap %": gap["Gap %"],

            })

        except Exception as e:

            print(f"{symbol} : {e}")

    # ----------------------------------------------------------
    # Save
    # ----------------------------------------------------------

    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    fresh_df = pd.DataFrame(fresh_crossovers)

    if not fresh_df.empty:
        fresh_df = fresh_df.sort_values(
            by="Volume Ratio",
            ascending=False,
        )

    fresh_df.to_csv(
        results_dir / "fresh_crossovers.csv",
        index=False,
    )

    pd.DataFrame(
        entered_status
    ).to_csv(
        results_dir / "entered_positions_status.csv",
        index=False,
    )

    print("\n====================================")
    print("SCAN COMPLETED")
    print("====================================")
    print(f"Fresh Crossovers : {len(fresh_df)}")
    print(f"Entered Stocks   : {len(entered_status)}")