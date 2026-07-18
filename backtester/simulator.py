import pandas as pd

from config import (
    STOP_LOSS_PERCENT,
    DEATH_CROSS_CONFIRMATION,
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
    Simulate one trade.

    Exit Reasons:
    1. Stop Loss
    2. Gap + EMA Confirmation
    3. Confirmed Death Cross

    Returns:
        Trade | None
    """

    entry = df.iloc[entry_index]

    entry_price = entry["Close"]

    highest_gap = 0.0
    highest_gap_date = entry["Date"]

    bearish_cross_seen = False
    bearish_cross_date = None

    gap_condition_met = False
    gap_condition_date = None

    death_cross_seen = False

    highest_price = entry_price
    lowest_price = entry_price

    for i in range(entry_index + 1, len(df)):

        row = df.iloc[i]
        prev = df.iloc[i - 1]

        # --------------------------------------------------
        # Reject corrupted historical data
        # --------------------------------------------------

        if prev["Close"] <= 0:
            return None

        daily_return = (
            (row["Close"] - prev["Close"])
            / prev["Close"]
        ) * 100

        if abs(daily_return) > MAX_DAILY_MOVE_PERCENT:
            return None

        # --------------------------------------------------
        # Track MFE / MAE
        # --------------------------------------------------

        highest_price = max(highest_price, row["High"])
        lowest_price = min(lowest_price, row["Low"])

        mfe = (
            (highest_price - entry_price)
            / entry_price
        ) * 100

        mae = (
            (lowest_price - entry_price)
            / entry_price
        ) * 100

        current_return = (
            (row["Close"] - entry_price)
            / entry_price
        ) * 100

        # --------------------------------------------------
        # Kill Switch
        # --------------------------------------------------

        if current_return <= STOP_LOSS_PERCENT:

            return Trade(
                symbol=symbol,

                entry_date=entry["Date"],
                exit_date=row["Date"],

                entry_price=entry_price,
                exit_price=row["Close"],

                highest_gap=highest_gap,
                highest_gap_date=highest_gap_date,

                bearish_cross_date=bearish_cross_date,
                gap_condition_date=gap_condition_date,

                exit_gap=None,
                exit_reason="Stop Loss",

                mfe=mfe,
                mae=mae,
            )

        # --------------------------------------------------
        # EMA50 - EMA200 Gap
        # --------------------------------------------------

        gap = row["EMA50"] - row["EMA200"]

        if gap > highest_gap:
            highest_gap = gap
            highest_gap_date = row["Date"]

        if highest_gap <= 0:
            continue

        gap_ratio = gap / highest_gap

        # --------------------------------------------------
        # Bearish EMA9 / EMA21 Cross
        # --------------------------------------------------

        bearish_cross = (

            row["EMA9"] < row["EMA21"]

            and

            prev["EMA9"] >= prev["EMA21"]

        )

        if bearish_cross and not bearish_cross_seen:

            bearish_cross_seen = True
            bearish_cross_date = row["Date"]

        # --------------------------------------------------
        # Gap Threshold
        # --------------------------------------------------

        if (
            gap_ratio <= gap_threshold
            and
            not gap_condition_met
        ):

            gap_condition_met = True
            gap_condition_date = row["Date"]

        # --------------------------------------------------
        # Death Cross
        # --------------------------------------------------

        death_cross = (

            row["EMA50"] < row["EMA200"]

            and

            prev["EMA50"] >= prev["EMA200"]

        )

        if death_cross:
            death_cross_seen = True

        # --------------------------------------------------
        # Normal Exit
        # --------------------------------------------------

        if bearish_cross_seen and gap_condition_met:

            return Trade(
                symbol=symbol,

                entry_date=entry["Date"],
                exit_date=row["Date"],

                entry_price=entry_price,
                exit_price=row["Close"],

                highest_gap=highest_gap,
                highest_gap_date=highest_gap_date,

                bearish_cross_date=bearish_cross_date,
                gap_condition_date=gap_condition_date,

                exit_gap=gap_ratio,
                exit_reason="Gap + EMA Confirmation",

                mfe=mfe,
                mae=mae,
            )

        # --------------------------------------------------
        # Confirmed Death Cross
        # --------------------------------------------------

        if (
            death_cross_seen
            and
            gap_ratio <= DEATH_CROSS_CONFIRMATION
        ):

            return Trade(
                symbol=symbol,

                entry_date=entry["Date"],
                exit_date=row["Date"],

                entry_price=entry_price,
                exit_price=row["Close"],

                highest_gap=highest_gap,
                highest_gap_date=highest_gap_date,

                bearish_cross_date=bearish_cross_date,
                gap_condition_date=gap_condition_date,

                exit_gap=gap_ratio,
                exit_reason="Confirmed Death Cross",

                mfe=mfe,
                mae=mae,
            )

    return None