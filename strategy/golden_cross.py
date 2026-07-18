import pandas as pd


def find_golden_crosses(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns every Golden Cross in the dataframe.
    Used by the historical backtester.
    """

    golden_cross = (

        (df["EMA50"] > df["EMA200"])

        &

        (df["EMA50"].shift(1) <= df["EMA200"].shift(1))

    )

    return df[golden_cross].copy()


def find_recent_golden_cross(
    df: pd.DataFrame,
    lookback_days: int,
):
    """
    Returns the most recent Golden Cross if it occurred
    within the last `lookback_days` candles.

    Used by the daily scanner.
    """

    golden_crosses = find_golden_crosses(df)

    if golden_crosses.empty:
        return None

    latest_gc = golden_crosses.iloc[-1]

    latest_index = latest_gc.name
    last_index = df.index[-1]

    candles_since = last_index - latest_index

    if candles_since <= lookback_days:
        return latest_gc

    return None