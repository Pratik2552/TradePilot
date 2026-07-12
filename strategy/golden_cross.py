import pandas as pd


def find_golden_crosses(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns all rows where EMA50 crosses above EMA200.
    """

    golden_cross = (
        (df["EMA50"] > df["EMA200"]) &
        (df["EMA50"].shift(1) <= df["EMA200"].shift(1))
    )

    return df[golden_cross].copy()