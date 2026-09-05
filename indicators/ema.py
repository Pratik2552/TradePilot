import pandas as pd


def add_ema(df: pd.DataFrame, period: int) -> pd.DataFrame:
    """
    Add a causal EMA column.

    The EMA is not considered valid until at least `period`
    candles are available.

    No future data is used.
    """

    if "Close" not in df.columns:
        raise ValueError("DataFrame must contain a 'Close' column.")

    column_name = f"EMA{period}"

    df[column_name] = (
        pd.to_numeric(df["Close"], errors="coerce")
        .ewm(
            span=period,
            adjust=False,
            min_periods=period,
        )
        .mean()
    )

    return df