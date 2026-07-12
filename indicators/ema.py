import pandas as pd


def add_ema(df: pd.DataFrame, period: int) -> pd.DataFrame:
    """
    Adds an EMA column to the dataframe.
    """

    column_name = f"EMA{period}"

    df[column_name] = (
        df["Close"]
        .ewm(span=period, adjust=False)
        .mean()
    )

    return df