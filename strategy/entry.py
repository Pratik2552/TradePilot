import pandas as pd


def is_entry(df: pd.DataFrame, i: int) -> bool:
    """
    Returns True if a Golden Cross occurs
    on candle i.
    """

    if i == 0:
        return False

    return (

        df.iloc[i]["EMA50"] > df.iloc[i]["EMA200"]

        and

        df.iloc[i - 1]["EMA50"] <= df.iloc[i - 1]["EMA200"]

    )