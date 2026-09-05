import pandas as pd

from strategy.exit import get_exit_signal

from config import (
    STOP_LOSS_PERCENT,
    MAX_DAILY_MOVE_PERCENT,
)

from backtester.trade import Trade


def simulate_trade(
    df: pd.DataFrame,
    symbol: str,
    entry_index: int,
    gap_threshold: float = 0.50,
):
    """
    Simulate one historical trade.

    ENTRY:
        Golden Cross confirmed on Day T close.
        Buy Day T+1 open.

    HARD STOP:
        If price touches stop intraday,
        exit at stop price.

        If stock gaps below stop,
        exit at actual opening price.

    NORMAL EXIT:
        Strategy exit confirmed at Day X close.
        Exit Day X+1 open.

    OPEN POSITION:
        If no exit has occurred by the end of
        available data, the trade remains OPEN.

        It is marked-to-market using the latest
        available closing price.
    """

    # ==================================================
    # ENTRY
    # ==================================================

    execution_index = (
        entry_index + 1
    )

    if (
        execution_index
        >= len(df)
    ):
        return None

    entry = df.iloc[
        execution_index
    ]

    entry_price = pd.to_numeric(
        entry["Open"],
        errors="coerce",
    )

    if (
        pd.isna(entry_price)
        or entry_price <= 0
    ):
        return None

    entry_price = float(
        entry_price
    )

    # ==================================================
    # STOP LOSS
    # ==================================================

    stop_price = (
        entry_price
        * (
            1
            + STOP_LOSS_PERCENT / 100
        )
    )

    # ==================================================
    # STATE
    # ==================================================

    highest_gap = 0.0

    highest_gap_date = (
        entry["Date"]
    )

    bearish_cross_seen = False
    bearish_cross_date = None

    gap_condition_met = False
    gap_condition_date = None

    death_cross_seen = False

    highest_price = entry_price
    lowest_price = entry_price

    latest_price = entry_price

    latest_date = (
        entry["Date"]
    )

    pending_exit_reason = None

    # ==================================================
    # WALK FORWARD
    # ==================================================

    for i in range(
        execution_index,
        len(df),
    ):

        row = df.iloc[i]

        if i == 0:
            continue

        prev = df.iloc[
            i - 1
        ]

        # ==================================================
        # PRICE DATA
        # ==================================================

        open_price = pd.to_numeric(
            row["Open"],
            errors="coerce",
        )

        high_price = pd.to_numeric(
            row["High"],
            errors="coerce",
        )

        low_price = pd.to_numeric(
            row["Low"],
            errors="coerce",
        )

        close_price = pd.to_numeric(
            row["Close"],
            errors="coerce",
        )

        prev_close = pd.to_numeric(
            prev["Close"],
            errors="coerce",
        )

        required_prices = [
            open_price,
            high_price,
            low_price,
            close_price,
            prev_close,
        ]

        if any(
            pd.isna(value)
            for value
            in required_prices
        ):
            return None

        open_price = float(
            open_price
        )

        high_price = float(
            high_price
        )

        low_price = float(
            low_price
        )

        close_price = float(
            close_price
        )

        prev_close = float(
            prev_close
        )

        if (
            open_price <= 0
            or high_price <= 0
            or low_price <= 0
            or close_price <= 0
            or prev_close <= 0
        ):
            return None

        latest_price = (
            close_price
        )

        latest_date = (
            row["Date"]
        )

        # ==================================================
        # DATA SANITY
        # ==================================================

        daily_return = (
            (
                close_price
                - prev_close
            )
            / prev_close
        ) * 100

        if (
            abs(daily_return)
            > MAX_DAILY_MOVE_PERCENT
        ):
            return None

        # ==================================================
        # HARD STOP
        #
        # CASE 1:
        # GAP BELOW STOP
        # ==================================================

        if open_price <= stop_price:

            exit_price = (
                open_price
            )

            realized_return = (
                (
                    exit_price
                    - entry_price
                )
                / entry_price
            ) * 100

            mfe = (
                (
                    highest_price
                    - entry_price
                )
                / entry_price
            ) * 100

            mae = realized_return

            return Trade(

                symbol=symbol,

                entry_date=
                    entry["Date"],

                exit_date=
                    row["Date"],

                entry_price=
                    entry_price,

                exit_price=
                    exit_price,

                highest_gap=
                    highest_gap,

                highest_gap_date=
                    highest_gap_date,

                bearish_cross_date=
                    bearish_cross_date,

                gap_condition_date=
                    gap_condition_date,

                exit_gap=None,

                exit_reason=
                    "Stop Loss",

                exit_timing=
                    "OPEN",

                mfe=mfe,

                mae=mae,

                status="CLOSED",
            )

        # ==================================================
        # CASE 2:
        # INTRADAY STOP
        # ==================================================

        if low_price <= stop_price:

            exit_price = (
                stop_price
            )

            mfe = (
                (
                    highest_price
                    - entry_price
                )
                / entry_price
            ) * 100

            mae = (
                STOP_LOSS_PERCENT
            )

            return Trade(

                symbol=symbol,

                entry_date=
                    entry["Date"],

                exit_date=
                    row["Date"],

                entry_price=
                    entry_price,

                exit_price=
                    exit_price,

                highest_gap=
                    highest_gap,

                highest_gap_date=
                    highest_gap_date,

                bearish_cross_date=
                    bearish_cross_date,

                gap_condition_date=
                    gap_condition_date,

                exit_gap=None,

                exit_reason=
                    "Stop Loss",

                exit_timing=
                    "INTRADAY",

                mfe=mfe,

                mae=mae,

                status="CLOSED",
            )

        # ==================================================
        # MFE / MAE
        # ==================================================

        highest_price = max(
            highest_price,
            high_price,
        )

        lowest_price = min(
            lowest_price,
            low_price,
        )

        mfe = (
            (
                highest_price
                - entry_price
            )
            / entry_price
        ) * 100

        mae = (
            (
                lowest_price
                - entry_price
            )
            / entry_price
        ) * 100

        current_return = (
            (
                close_price
                - entry_price
            )
            / entry_price
        ) * 100

        # ==================================================
        # EMA VALIDATION
        # ==================================================

        ema_values = [

            row["EMA9"],
            row["EMA21"],
            row["EMA50"],
            row["EMA200"],

            prev["EMA9"],
            prev["EMA21"],
            prev["EMA50"],
            prev["EMA200"],
        ]

        if any(
            pd.isna(value)
            for value
            in ema_values
        ):
            continue

        # ==================================================
        # EMA50 / EMA200 GAP
        # ==================================================

        gap = (
            row["EMA50"]
            - row["EMA200"]
        )

        if gap > highest_gap:

            highest_gap = gap

            highest_gap_date = (
                row["Date"]
            )

        if highest_gap <= 0:
            continue

        gap_ratio = (
            gap
            / highest_gap
        )

        # ==================================================
        # EMA9 / EMA21 BEARISH CROSS
        # ==================================================

        bearish_cross = (

            row["EMA9"]
            < row["EMA21"]

            and

            prev["EMA9"]
            >= prev["EMA21"]
        )

        if (
            bearish_cross
            and not bearish_cross_seen
        ):

            bearish_cross_seen = True

            bearish_cross_date = (
                row["Date"]
            )

        # ==================================================
        # GAP CONDITION
        # ==================================================

        if (
            gap_ratio
            <= gap_threshold

            and

            not gap_condition_met
        ):

            gap_condition_met = True

            gap_condition_date = (
                row["Date"]
            )

        # ==================================================
        # DEATH CROSS
        # ==================================================

        death_cross = (

            row["EMA50"]
            < row["EMA200"]

            and

            prev["EMA50"]
            >= prev["EMA200"]
        )

        if death_cross:
            death_cross_seen = True

        # ==================================================
        # EXIT SIGNAL
        # ==================================================

        exit_reason = get_exit_signal(

            state={

                "bearish_seen":
                    bearish_cross_seen,

                "gap_seen":
                    gap_condition_met,

                "death_seen":
                    death_cross_seen,
            },

            current_return=
                current_return,

            gap_ratio=
                gap_ratio,
        )

        if exit_reason is None:
            continue

        # ==================================================
        # NORMAL EXIT = NEXT DAY OPEN
        # ==================================================

        exit_execution_index = (
            i + 1
        )

        # ==================================================
        # EXIT SIGNAL EXISTS,
        # BUT NEXT CANDLE DOES NOT EXIST YET.
        #
        # KEEP POSITION OPEN.
        # ==================================================

        if (
            exit_execution_index
            >= len(df)
        ):

            pending_exit_reason = (
                exit_reason
            )

            return Trade(

                symbol=symbol,

                entry_date=
                    entry["Date"],

                exit_date=None,

                entry_price=
                    entry_price,

                exit_price=None,

                highest_gap=
                    highest_gap,

                highest_gap_date=
                    highest_gap_date,

                bearish_cross_date=
                    bearish_cross_date,

                gap_condition_date=
                    gap_condition_date,

                exit_gap=
                    gap_ratio,

                exit_reason=None,

                exit_timing=None,

                mfe=mfe,

                mae=mae,

                status="OPEN",

                current_price=
                    close_price,

                current_date=
                    row["Date"],

                pending_exit_reason=
                    pending_exit_reason,
            )

        # ==================================================
        # EXIT CAN ACTUALLY EXECUTE
        # ==================================================

        exit_row = df.iloc[
            exit_execution_index
        ]

        exit_price = pd.to_numeric(
            exit_row["Open"],
            errors="coerce",
        )

        if (
            pd.isna(exit_price)
            or exit_price <= 0
        ):
            return None

        exit_price = float(
            exit_price
        )

        return Trade(

            symbol=symbol,

            entry_date=
                entry["Date"],

            exit_date=
                exit_row["Date"],

            entry_price=
                entry_price,

            exit_price=
                exit_price,

            highest_gap=
                highest_gap,

            highest_gap_date=
                highest_gap_date,

            bearish_cross_date=
                bearish_cross_date,

            gap_condition_date=
                gap_condition_date,

            exit_gap=
                gap_ratio,

            exit_reason=
                exit_reason,

            exit_timing=
                "OPEN",

            mfe=mfe,

            mae=mae,

            status="CLOSED",
        )

    # ==================================================
    # END OF DATA
    #
    # OLD LOGIC:
    #
    # return None
    #
    # NEW LOGIC:
    #
    # KEEP POSITION OPEN
    # ==================================================

    mfe = (
        (
            highest_price
            - entry_price
        )
        / entry_price
    ) * 100

    mae = (
        (
            lowest_price
            - entry_price
        )
        / entry_price
    ) * 100

    return Trade(

        symbol=symbol,

        entry_date=
            entry["Date"],

        exit_date=None,

        entry_price=
            entry_price,

        exit_price=None,

        highest_gap=
            highest_gap,

        highest_gap_date=
            highest_gap_date,

        bearish_cross_date=
            bearish_cross_date,

        gap_condition_date=
            gap_condition_date,

        exit_gap=None,

        exit_reason=None,

        exit_timing=None,

        mfe=mfe,

        mae=mae,

        status="OPEN",

        current_price=
            latest_price,

        current_date=
            latest_date,

        pending_exit_reason=
            pending_exit_reason,
    )