from pathlib import Path

import pandas as pd

from data.universe import refresh_universe, load_symbols
from data.downloader import get_stock_data

from indicators.ema import add_ema

from backtester.report import generate_trade_report
from backtester.metrics import calculate_metrics


def run_backtest():

    # --------------------------------------------------
    # Load Universe
    # --------------------------------------------------

    refresh_universe()

    symbols = load_symbols()

    # TEMP
    # symbols = symbols[:50]

    total_symbols = len(symbols)

    all_trades = []

    scanned = 0
    failed = 0

    # --------------------------------------------------
    # Scan Stocks
    # --------------------------------------------------

    for i, symbol in enumerate(symbols, start=1):

        print(f"[{i}/{total_symbols}] {symbol}")

        try:

            df = get_stock_data(symbol)

            if len(df) < 250:
                continue

            scanned += 1

            for period in (9, 21, 50, 200):
                df = add_ema(df, period)

            trades = generate_trade_report(
                symbol=symbol,
                df=df,
            )

            if not trades.empty:
                all_trades.append(trades)

        except Exception as e:

            failed += 1
            print(f"{symbol}: {e}")

    # --------------------------------------------------
    # Merge Trades
    # --------------------------------------------------

    if all_trades:

        trades = pd.concat(
            all_trades,
            ignore_index=True,
        )

        trades.sort_values(
            by=[
                "Entry Date",
                "Symbol",
            ],
            inplace=True,
        )

        trades.reset_index(
            drop=True,
            inplace=True,
        )

    else:

        trades = pd.DataFrame()

    # --------------------------------------------------
    # Results Folder
    # --------------------------------------------------

    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    # --------------------------------------------------
    # Save Trades
    # --------------------------------------------------

    trades.to_csv(
        results_dir / "backtest_trades.csv",
        index=False,
    )

    # --------------------------------------------------
    # Performance Summary
    # --------------------------------------------------

    metrics = calculate_metrics(trades)

    metrics_df = pd.DataFrame([metrics])

    metrics_df.to_csv(
        results_dir / "performance_summary.csv",
        index=False,
    )

    # --------------------------------------------------
    # Exit Reason Summary
    # --------------------------------------------------

    if not trades.empty:

        exit_summary = (
            trades["Exit Reason"]
            .value_counts()
            .rename_axis("Exit Reason")
            .reset_index(name="Trades")
        )

        exit_summary.to_csv(
            results_dir / "exit_summary.csv",
            index=False,
        )

    # --------------------------------------------------
    # Console Summary
    # --------------------------------------------------

    print("\n====================================")
    print("BACKTEST COMPLETE")
    print("====================================")

    print(f"Stocks Loaded     : {total_symbols}")
    print(f"Stocks Scanned    : {scanned}")
    print(f"Failed Downloads  : {failed}")
    print(f"Completed Trades  : {len(trades)}")

    if not trades.empty:

        print("\nExit Reasons")

        print(
            trades["Exit Reason"]
            .value_counts()
            .to_string()
        )

    print("\nResults saved to:")
    print(results_dir.resolve())