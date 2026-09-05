import pandas as pd


def find_golden_crosses(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return all confirmed Golden Cross candles.

    A Golden Cross occurs when:
        EMA50 > EMA200 today
        EMA50 <= EMA200 on the previous candle

    Uses only current and historical information.
    """

    required = {"EMA50", "EMA200"}

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required EMA columns: {sorted(missing)}"
        )

    golden_cross = (
        (df["EMA50"] > df["EMA200"])
        &
        (df["EMA50"].shift(1) <= df["EMA200"].shift(1))
    )

    return df.loc[golden_cross].copy()


def find_recent_golden_cross(
    df: pd.DataFrame,
    lookback_days: int,
):
    """
    Return the most recent Golden Cross if it occurred
    within the last `lookback_days` candles.

    Used by the daily scanner.
    """

    if df.empty:
        return None

    golden_cross = (
        (df["EMA50"] > df["EMA200"])
        &
        (df["EMA50"].shift(1) <= df["EMA200"].shift(1))
    )

    cross_positions = [
        i
        for i, is_cross in enumerate(golden_cross.to_numpy())
        if is_cross
    ]

    if not cross_positions:
        return None

    latest_position = cross_positions[-1]

    candles_since = (
        len(df) - 1 - latest_position
    )

    if candles_since <= lookback_days:
        return df.iloc[latest_position].copy()

    return None