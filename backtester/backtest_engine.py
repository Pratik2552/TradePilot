from pathlib import Path

import pandas as pd

from portfolio.simulator import PortfolioSimulator

from data.universe import (
    refresh_universe,
    load_symbols,
)

from data.downloader import get_cached_stock_data

from indicators.ema import add_ema

from backtester.report import generate_trade_report
from backtester.metrics import calculate_metrics


def run_backtest():

    # ==================================================
    # Load stock universe
    # ==================================================

    refresh_universe()

    symbols = load_symbols()

    total_symbols = len(symbols)

    all_trades = []

    scanned = 0
    failed = 0

    # ==================================================
    # Generate candidate strategy trades
    # ==================================================

    for i, symbol in enumerate(
        symbols,
        start=1,
    ):

        print(
            f"[{i}/{total_symbols}] {symbol}"
        )

        try:

            df = get_cached_stock_data(
                symbol
            )

            if df.empty:
                continue

            # EMA200 needs sufficient history.
            if len(df) < 250:
                continue

            scanned += 1

            df = df.copy()

            # ------------------------------------------
            # Indicators
            # ------------------------------------------

            for period in (
                9,
                21,
                50,
                200,
            ):

                df = add_ema(
                    df,
                    period,
                )

            # ------------------------------------------
            # Candidate trades
            # ------------------------------------------

            symbol_trades = generate_trade_report(
                symbol=symbol,
                df=df,
            )

            if not symbol_trades.empty:

                all_trades.append(
                    symbol_trades
                )

        except Exception as e:

            failed += 1

            print(
                f"{symbol}: {e}"
            )

    # ==================================================
    # Merge candidate trades
    # ==================================================

    if all_trades:

        candidate_trades = pd.concat(
            all_trades,
            ignore_index=True,
        )

        # Deterministic same-day ordering.
        #
        # IMPORTANT:
        # Never rank using future information such as:
        # Return %, Exit Price, MFE, MAE, Exit Date, etc.
        candidate_trades.sort_values(
            by=[
                "Entry Date",
                "Symbol",
            ],
            kind="mergesort",
            inplace=True,
        )

        candidate_trades.reset_index(
            drop=True,
            inplace=True,
        )

    else:

        candidate_trades = pd.DataFrame()

    # ==================================================
    # Results directory
    # ==================================================

    results_dir = Path(
        "results"
    )

    results_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ==================================================
    # Save all strategy candidates
    # ==================================================

    candidate_trades.to_csv(
        results_dir
        / "backtest_trades.csv",
        index=False,
    )

    # ==================================================
    # Portfolio simulation
    # ==================================================

    simulator = PortfolioSimulator(
        trades=candidate_trades,
        initial_capital=100000,
        allocation=0.10,
        max_positions=10,
    )

    equity_curve = simulator.run()

    # ==================================================
    # Actual executed / rejected trades
    # ==================================================

    executed_trades = (
        simulator.get_executed_trades()
    )

    rejected_trades = (
        simulator.get_rejected_trades()
    )

    executed_trades.to_csv(
        results_dir
        / "executed_trades.csv",
        index=False,
    )

    rejected_trades.to_csv(
        results_dir
        / "rejected_trades.csv",
        index=False,
    )

    # ==================================================
    # Save equity curve
    # ==================================================

    equity_curve.to_csv(
        results_dir
        / "equity_curve.csv",
        index=False,
    )

    # ==================================================
    # Portfolio summary
    # ==================================================

    portfolio_summary = pd.DataFrame(
        [
            {
                "Initial Capital":
                    simulator.portfolio.initial_capital,

                "Final Equity":
                    simulator.portfolio.equity(),

                "Cash":
                    simulator.portfolio.cash,

                "Open Positions":
                    len(
                        simulator.portfolio.open_positions
                    ),

                "Candidate Trades":
                    len(candidate_trades),

                "Executed Trades":
                    len(executed_trades),

                "Rejected Trades":
                    len(rejected_trades),
            }
        ]
    )

    portfolio_summary.to_csv(
        results_dir
        / "portfolio_summary.csv",
        index=False,
    )

    # ==================================================
    # IMPORTANT:
    # Metrics must use EXECUTED trades
    # ==================================================

    metrics = calculate_metrics(
        executed_trades
    )

    pd.DataFrame(
        [metrics]
    ).to_csv(
        results_dir
        / "performance_summary.csv",
        index=False,
    )

    # ==================================================
    # Executed trade exit summary
    # ==================================================

    if (
        not executed_trades.empty
        and
        "Exit Reason"
        in executed_trades.columns
    ):

        exit_summary = (
            executed_trades[
                "Exit Reason"
            ]
            .value_counts()
            .rename_axis(
                "Exit Reason"
            )
            .reset_index(
                name="Trades"
            )
        )

        exit_summary.to_csv(
            results_dir
            / "exit_summary.csv",
            index=False,
        )

    # ==================================================
    # Candidate signal statistics
    #
    # Useful for research, but kept separate from
    # actual portfolio performance.
    # ==================================================

    candidate_metrics = (
        calculate_metrics(
            candidate_trades
        )
        if not candidate_trades.empty
        else calculate_metrics(
            pd.DataFrame()
        )
    )

    pd.DataFrame(
        [candidate_metrics]
    ).to_csv(
        results_dir
        / "candidate_performance_summary.csv",
        index=False,
    )

    # ==================================================
    # Console summary
    # ==================================================

    print(
        "\n===================================="
    )

    print(
        "BACKTEST COMPLETE"
    )

    print(
        "===================================="
    )

    print(
        f"Stocks Loaded      : {total_symbols}"
    )

    print(
        f"Stocks Scanned     : {scanned}"
    )

    print(
        f"Failed             : {failed}"
    )

    print(
        f"Candidate Trades   : {len(candidate_trades)}"
    )

    print(
        f"Executed Trades    : {len(executed_trades)}"
    )

    print(
        f"Rejected Trades    : {len(rejected_trades)}"
    )

    print(
        f"Final Equity       : "
        f"{simulator.portfolio.equity():,.2f}"
    )

    print(
        "===================================="
    )


if __name__ == "__main__":
    run_backtest()