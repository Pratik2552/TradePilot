from pathlib import Path

import pandas as pd

from strategy.golden_cross import (
    find_golden_crosses,
)

from backtester.simulator import (
    simulate_trade,
)

from config import (
    MIN_STOCK_PRICE,
    BACKTEST_YEARS,
)


def generate_trade_report(
    symbol: str,
    df: pd.DataFrame,
    gap_threshold: float = 0.50,
):
    """
    Generate historical candidate trades.

    Golden Cross:
        Confirmed Day T close.

    Entry:
        Day T+1 open.

    CLOSED:
        Trade exited using actual strategy logic.

    OPEN:
        Trade remains active at end of available data.

    Prevents overlapping trades for the same stock.
    """

    valid_trades = []
    invalid_trades = []

    if (
        df is None
        or df.empty
    ):
        return pd.DataFrame()

    df = (
        df.copy()
        .reset_index(
            drop=True
        )
    )

    # ==================================================
    # DATES
    # ==================================================

    df["Date"] = pd.to_datetime(
        df["Date"]
    )

    # ==================================================
    # GOLDEN CROSSES
    # ==================================================

    golden_crosses = (
        find_golden_crosses(
            df
        )
    )

    # ==================================================
    # LIMIT TO BACKTEST YEARS
    # ==================================================

    latest_date = (
        df["Date"].max()
    )

    backtest_start = (
        latest_date
        - pd.DateOffset(
            years=BACKTEST_YEARS
        )
    )

    golden_crosses = golden_crosses[
        pd.to_datetime(
            golden_crosses["Date"]
        )
        >= backtest_start
    ].copy()

    if golden_crosses.empty:
        return pd.DataFrame()

    # ==================================================
    # PREVENT OVERLAPPING TRADES
    # ==================================================

    last_exit_position = -1

    for signal_position in (
        golden_crosses.index
    ):

        if (
            signal_position
            <= last_exit_position
        ):
            continue

        # ==================================================
        # ENTRY NEXT DAY OPEN
        # ==================================================

        execution_position = (
            signal_position + 1
        )

        if (
            execution_position
            >= len(df)
        ):
            continue

        execution_row = df.iloc[
            execution_position
        ]

        entry_price = pd.to_numeric(
            execution_row["Open"],
            errors="coerce",
        )

        if pd.isna(
            entry_price
        ):
            continue

        entry_price = float(
            entry_price
        )

        if (
            entry_price <= 0
            or entry_price
            < MIN_STOCK_PRICE
        ):
            continue

        # ==================================================
        # SIMULATE
        # ==================================================

        trade = simulate_trade(

            df=df,

            symbol=symbol,

            entry_index=
                signal_position,

            gap_threshold=
                gap_threshold,
        )

        if trade is None:
            continue

        trade_dict = (
            trade.to_dict()
        )

        # ==================================================
        # SAVE ACTUAL GOLDEN CROSS DATE
        #
        # This is also used by the volume filter.
        # ==================================================

        trade_dict[
            "Golden Cross Date"
        ] = df.iloc[
            signal_position
        ]["Date"]

        status = str(
            trade_dict.get(
                "Status",
                "CLOSED",
            )
        ).upper()

        # ==================================================
        # OVERLAP CONTROL
        # ==================================================

        if status == "CLOSED":

            exit_matches = df.index[
                df["Date"]
                == trade.exit_date
            ]

            if (
                len(exit_matches)
                > 0
            ):

                last_exit_position = int(
                    exit_matches[0]
                )

        else:

            # Trade remains open until end
            # of available dataset.
            #
            # Therefore another position in the
            # same symbol cannot be opened.
            last_exit_position = (
                len(df) - 1
            )

        # ==================================================
        # VALIDATION
        # ==================================================

        reason = None

        if (
            trade_dict[
                "Entry Price"
            ]
            <= 0
        ):

            reason = (
                "Entry Price <= 0"
            )

        # ==================================================
        # CLOSED VALIDATION
        # ==================================================

        elif status == "CLOSED":

            exit_price = (
                trade_dict.get(
                    "Exit Price"
                )
            )

            exit_date = (
                trade_dict.get(
                    "Exit Date"
                )
            )

            if (
                exit_price is None
                or pd.isna(exit_price)
                or exit_price <= 0
            ):

                reason = (
                    "Invalid Exit Price"
                )

            elif (
                exit_date is None
                or pd.isna(exit_date)
            ):

                reason = (
                    "Missing Exit Date"
                )

            elif (
                trade_dict[
                    "Holding Days"
                ]
                < 0
            ):

                reason = (
                    "Invalid Holding Days"
                )

            elif (
                pd.to_datetime(
                    exit_date
                )
                <
                pd.to_datetime(
                    trade_dict[
                        "Entry Date"
                    ]
                )
            ):

                reason = (
                    "Exit Date < Entry Date"
                )

        # ==================================================
        # OPEN VALIDATION
        # ==================================================

        else:

            current_price = (
                trade_dict.get(
                    "Current Price"
                )
            )

            current_date = (
                trade_dict.get(
                    "Current Date"
                )
            )

            if (
                current_price is None
                or pd.isna(
                    current_price
                )
                or current_price <= 0
            ):

                reason = (
                    "Invalid Current Price"
                )

            elif (
                current_date is None
                or pd.isna(
                    current_date
                )
            ):

                reason = (
                    "Missing Current Date"
                )

            elif (
                pd.to_datetime(
                    current_date
                )
                <
                pd.to_datetime(
                    trade_dict[
                        "Entry Date"
                    ]
                )
            ):

                reason = (
                    "Current Date < Entry Date"
                )

        # ==================================================
        # STORE
        # ==================================================

        if reason is None:

            valid_trades.append(
                trade_dict
            )

        else:

            trade_dict[
                "Reason"
            ] = reason

            invalid_trades.append(
                trade_dict
            )

    # ==================================================
    # INVALID TRADE LOG
    # ==================================================

    if invalid_trades:

        results_dir = Path(
            "results"
        )

        results_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        invalid_file = (
            results_dir
            / "invalid_trades.csv"
        )

        invalid_df = pd.DataFrame(
            invalid_trades
        )

        if invalid_file.exists():

            existing = pd.read_csv(
                invalid_file
            )

            invalid_df = (
                pd.concat(
                    [
                        existing,
                        invalid_df,
                    ],
                    ignore_index=True,
                )
                .drop_duplicates()
            )

        invalid_df.to_csv(
            invalid_file,
            index=False,
        )

    return pd.DataFrame(
        valid_trades
    )