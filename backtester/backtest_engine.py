from pathlib import Path

import pandas as pd

from portfolio.simulator import (
    PortfolioSimulator,
)

from data.universe import (
    refresh_universe,
    load_symbols,
)

from data.downloader import (
    get_cached_stock_data,
)

from indicators.ema import (
    add_ema,
)

from indicators.volume import (
    add_volume_metrics,
)

from filters.volume_filter import (
    filter_candidate_trades,
)

from backtester.report import (
    generate_trade_report,
)

from backtester.metrics import (
    calculate_metrics,
)

from config import (
    ENABLE_VOLUME_FILTER,
    VOLUME_LOOKBACK,
    MIN_RELATIVE_VOLUME,
    MIN_ADTV,
)


def run_backtest():

    # ==================================================
    # UNIVERSE
    # ==================================================

    refresh_universe()

    symbols = load_symbols()

    total_symbols = len(
        symbols
    )

    # ----------------------------------------------
    # RAW Golden Cross trades
    # before volume filtering
    # ----------------------------------------------

    all_raw_trades = []

    # ----------------------------------------------
    # Trades passing filters
    # ----------------------------------------------

    all_trades = []

    # ----------------------------------------------
    # Filter rejections
    # ----------------------------------------------

    filter_rejections = []

    scanned = 0
    failed = 0

    # ==================================================
    # GENERATE STRATEGY TRADES
    # ==================================================

    for i, symbol in enumerate(
        symbols,
        start=1,
    ):

        print(
            f"[{i}/{total_symbols}] "
            f"{symbol}"
        )

        try:

            # ==========================================
            # DATA
            # ==========================================

            df = (
                get_cached_stock_data(
                    symbol
                )
            )

            if df.empty:
                continue

            # EMA200 requires enough history
            if len(df) < 250:
                continue

            scanned += 1

            df = df.copy()

            # ==========================================
            # EMA INDICATORS
            # ==========================================

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

            # ==========================================
            # VOLUME INDICATORS
            # ==========================================

            df = add_volume_metrics(

                df,

                lookback=
                    VOLUME_LOOKBACK,
            )

            # ==========================================
            # GOLDEN CROSS TRADES
            # ==========================================

            symbol_trades = (
                generate_trade_report(

                    symbol=symbol,

                    df=df,
                )
            )

            if symbol_trades.empty:
                continue

            # ==========================================
            # RAW CANDIDATES
            # ==========================================

            all_raw_trades.append(
                symbol_trades.copy()
            )

            # ==========================================
            # VOLUME / LIQUIDITY FILTER
            # ==========================================

            if ENABLE_VOLUME_FILTER:

                (
                    passed_trades,
                    rejected_by_filter,
                ) = filter_candidate_trades(

                    trades=
                        symbol_trades,

                    price_data=
                        df,

                    lookback=
                        VOLUME_LOOKBACK,

                    min_relative_volume=
                        MIN_RELATIVE_VOLUME,

                    min_adtv=
                        MIN_ADTV,
                )

                if (
                    not rejected_by_filter.empty
                ):

                    filter_rejections.append(
                        rejected_by_filter
                    )

                symbol_trades = (
                    passed_trades
                )

            # ==========================================
            # PASSED TRADES
            # ==========================================

            if (
                not symbol_trades.empty
            ):

                all_trades.append(
                    symbol_trades
                )

        except Exception as e:

            failed += 1

            print(
                f"{symbol}: {e}"
            )

    # ==================================================
    # RAW CANDIDATES
    # ==================================================

    if all_raw_trades:

        raw_candidate_trades = pd.concat(

            all_raw_trades,

            ignore_index=True,
        )

        raw_candidate_trades.sort_values(

            by=[
                "Entry Date",
                "Symbol",
            ],

            kind="mergesort",

            inplace=True,
        )

        raw_candidate_trades.reset_index(
            drop=True,
            inplace=True,
        )

    else:

        raw_candidate_trades = (
            pd.DataFrame()
        )

    # ==================================================
    # FILTERED CANDIDATES
    # ==================================================

    if all_trades:

        candidate_trades = pd.concat(

            all_trades,

            ignore_index=True,
        )

        # ----------------------------------------------
        # IMPORTANT:
        #
        # Do not sort/rank using future information:
        #
        # Return %
        # Exit Price
        # MFE
        # MAE
        # Exit Date
        # ----------------------------------------------

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

        candidate_trades = (
            pd.DataFrame()
        )

    # ==================================================
    # FILTER REJECTIONS
    # ==================================================

    if filter_rejections:

        filter_rejected_trades = pd.concat(

            filter_rejections,

            ignore_index=True,
        )

        if (
            "Entry Date"
            in filter_rejected_trades.columns
        ):

            filter_rejected_trades.sort_values(

                by=[
                    "Entry Date",
                    "Symbol",
                ],

                kind="mergesort",

                inplace=True,
            )

            filter_rejected_trades.reset_index(
                drop=True,
                inplace=True,
            )

    else:

        filter_rejected_trades = (
            pd.DataFrame()
        )

    # ==================================================
    # RESULTS DIRECTORY
    # ==================================================

    results_dir = Path(
        "results"
    )

    results_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ==================================================
    # SAVE RAW CANDIDATES
    # ==================================================

    raw_candidate_trades.to_csv(

        results_dir
        / "raw_candidate_trades.csv",

        index=False,
    )

    # ==================================================
    # SAVE FILTERED CANDIDATES
    # ==================================================

    candidate_trades.to_csv(

        results_dir
        / "backtest_trades.csv",

        index=False,
    )

    # ==================================================
    # SAVE FILTER REJECTIONS
    # ==================================================

    filter_rejected_trades.to_csv(

        results_dir
        / "filter_rejected_trades.csv",

        index=False,
    )

    # ==================================================
    # PORTFOLIO
    # ==================================================

    simulator = PortfolioSimulator(

        trades=
            candidate_trades,

        initial_capital=
            100000,

        allocation=
            0.10,

        max_positions=
            10,
    )

    equity_curve = (
        simulator.run()
    )

    # ==================================================
    # CLOSED TRADES
    # ==================================================

    executed_trades = (
        simulator
        .get_executed_trades()
    )

    # ==================================================
    # OPEN TRADES
    # ==================================================

    open_trades = (
        simulator
        .get_open_trades()
    )

    # ==================================================
    # PORTFOLIO REJECTIONS
    # ==================================================

    rejected_trades = (
        simulator
        .get_rejected_trades()
    )

    # ==================================================
    # SAVE EXECUTED
    # ==================================================

    executed_trades.to_csv(

        results_dir
        / "executed_trades.csv",

        index=False,
    )

    # ==================================================
    # SAVE OPEN POSITIONS
    # ==================================================

    open_trades.to_csv(

        results_dir
        / "open_trades.csv",

        index=False,
    )

    # ==================================================
    # SAVE PORTFOLIO REJECTIONS
    # ==================================================

    rejected_trades.to_csv(

        results_dir
        / "rejected_trades.csv",

        index=False,
    )

    # ==================================================
    # EQUITY CURVE
    # ==================================================

    equity_curve.to_csv(

        results_dir
        / "equity_curve.csv",

        index=False,
    )

    # ==================================================
    # PORTFOLIO SUMMARY
    # ==================================================

    portfolio_summary = pd.DataFrame(

        [
            {

                "Initial Capital":
                    simulator
                    .portfolio
                    .initial_capital,

                "Final Equity":
                    simulator
                    .portfolio
                    .equity(),

                "Cash":
                    simulator
                    .portfolio
                    .cash,

                "Market Value Open Positions":
                    (
                        simulator
                        .portfolio
                        .equity()
                        -
                        simulator
                        .portfolio
                        .cash
                    ),

                "Open Positions":
                    len(
                        simulator
                        .portfolio
                        .open_positions
                    ),

                "Raw Candidate Trades":
                    len(
                        raw_candidate_trades
                    ),

                "Filter Rejected Trades":
                    len(
                        filter_rejected_trades
                    ),

                "Passed Filter":
                    len(
                        candidate_trades
                    ),

                "Closed Executed Trades":
                    len(
                        executed_trades
                    ),

                "Open Executed Trades":
                    len(
                        open_trades
                    ),

                "Portfolio Rejected Trades":
                    len(
                        rejected_trades
                    ),
            }
        ]
    )

    portfolio_summary.to_csv(

        results_dir
        / "portfolio_summary.csv",

        index=False,
    )

    # ==================================================
    # PERFORMANCE METRICS
    #
    # ONLY CLOSED / REALIZED TRADES
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
    # EXIT SUMMARY
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
    # CLOSED FILTERED CANDIDATES
    #
    # OPEN trades must NOT affect:
    #
    # win rate
    # average realized return
    # median realized return
    # etc.
    # ==================================================

    if (
        not candidate_trades.empty
        and
        "Status"
        in candidate_trades.columns
    ):

        closed_candidate_trades = (

            candidate_trades[

                candidate_trades[
                    "Status"
                ]
                == "CLOSED"
            ]
            .copy()
        )

    else:

        closed_candidate_trades = (
            candidate_trades.copy()
        )

    candidate_metrics = (

        calculate_metrics(
            closed_candidate_trades
        )

        if (
            not closed_candidate_trades.empty
        )

        else

        calculate_metrics(
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
    # CLOSED RAW CANDIDATES
    # ==================================================

    if (
        not raw_candidate_trades.empty
        and
        "Status"
        in raw_candidate_trades.columns
    ):

        closed_raw_candidate_trades = (

            raw_candidate_trades[

                raw_candidate_trades[
                    "Status"
                ]
                == "CLOSED"
            ]
            .copy()
        )

    else:

        closed_raw_candidate_trades = (
            raw_candidate_trades.copy()
        )

    raw_candidate_metrics = (

        calculate_metrics(
            closed_raw_candidate_trades
        )

        if (
            not closed_raw_candidate_trades.empty
        )

        else

        calculate_metrics(
            pd.DataFrame()
        )
    )

    pd.DataFrame(
        [raw_candidate_metrics]
    ).to_csv(

        results_dir
        / "raw_candidate_performance_summary.csv",

        index=False,
    )

    # ==================================================
    # FILTER REJECTION SUMMARY
    # ==================================================

    if (
        not filter_rejected_trades.empty
        and
        "Filter Rejection Reasons"
        in filter_rejected_trades.columns
    ):

        rejection_summary = (

            filter_rejected_trades[
                "Filter Rejection Reasons"
            ]

            .value_counts()

            .rename_axis(
                "Reason"
            )

            .reset_index(
                name="Trades"
            )
        )

        rejection_summary.to_csv(

            results_dir
            / "filter_rejection_summary.csv",

            index=False,
        )

    # ==================================================
    # OPEN POSITION SUMMARY
    # ==================================================

    if not open_trades.empty:

        open_summary = pd.DataFrame(

            [
                {

                    "Open Positions":
                        len(
                            open_trades
                        ),

                    "Total Invested":
                        (
                            open_trades[
                                "Invested"
                            ].sum()
                            if
                            "Invested"
                            in open_trades.columns
                            else 0
                        ),

                    "Current Market Value":
                        (
                            open_trades[
                                "Market Value"
                            ].sum()
                            if
                            "Market Value"
                            in open_trades.columns
                            else 0
                        ),

                    "Unrealized P&L":
                        (
                            open_trades[
                                "Unrealized P&L"
                            ].sum()
                            if
                            "Unrealized P&L"
                            in open_trades.columns
                            else 0
                        ),
                }
            ]
        )

    else:

        open_summary = pd.DataFrame(

            [
                {

                    "Open Positions": 0,

                    "Total Invested": 0,

                    "Current Market Value": 0,

                    "Unrealized P&L": 0,
                }
            ]
        )

    open_summary.to_csv(

        results_dir
        / "open_positions_summary.csv",

        index=False,
    )

    # ==================================================
    # CONSOLE
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
        f"Stocks Loaded        : "
        f"{total_symbols}"
    )

    print(
        f"Stocks Scanned       : "
        f"{scanned}"
    )

    print(
        f"Failed               : "
        f"{failed}"
    )

    print(
        "------------------------------------"
    )

    print(
        f"Raw Candidates       : "
        f"{len(raw_candidate_trades)}"
    )

    print(
        f"Filter Rejected      : "
        f"{len(filter_rejected_trades)}"
    )

    print(
        f"Passed Filter        : "
        f"{len(candidate_trades)}"
    )

    print(
        "------------------------------------"
    )

    print(
        f"Closed Trades        : "
        f"{len(executed_trades)}"
    )

    print(
        f"Open Positions       : "
        f"{len(open_trades)}"
    )

    print(
        f"Portfolio Rejected   : "
        f"{len(rejected_trades)}"
    )

    print(
        "------------------------------------"
    )

    print(
        f"Cash                 : "
        f"₹{simulator.portfolio.cash:,.2f}"
    )

    print(
        f"Final Equity         : "
        f"₹{simulator.portfolio.equity():,.2f}"
    )

    print(
        "===================================="
    )

    print(
        "\nVOLUME FILTER"
    )

    print(
        "------------------------------------"
    )

    print(
        f"Enabled              : "
        f"{ENABLE_VOLUME_FILTER}"
    )

    print(
        f"Lookback             : "
        f"{VOLUME_LOOKBACK} days"
    )

    print(
        f"Minimum Relative Vol : "
        f"{MIN_RELATIVE_VOLUME:.2f}x"
    )

    print(
        f"Minimum ADTV         : "
        f"₹{MIN_ADTV:,.0f}"
    )

    print(
        "===================================="
    )


if __name__ == "__main__":
    run_backtest()