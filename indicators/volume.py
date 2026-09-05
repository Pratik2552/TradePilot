import numpy as np
import pandas as pd


def add_volume_metrics(
    df: pd.DataFrame,
    lookback: int = 20,
) -> pd.DataFrame:
    """
    Add point-in-time volume and liquidity metrics.

    IMPORTANT:
    The current candle is NOT included in the historical average.

    Adds:
        AvgVolume20
        RelativeVolume20
        ADTV20

    Example:
        RelativeVolume20 =
            current candle volume /
            average volume of previous 20 candles

        ADTV20 =
            average of (Close * Volume)
            over previous 20 candles
    """

    if lookback <= 0:
        raise ValueError("lookback must be greater than 0")

    required_columns = {"Close", "Volume"}

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    out = df.copy()

    close = pd.to_numeric(
        out["Close"],
        errors="coerce",
    )

    volume = pd.to_numeric(
        out["Volume"],
        errors="coerce",
    )

    avg_volume_column = f"AvgVolume{lookback}"
    relative_volume_column = f"RelativeVolume{lookback}"
    adtv_column = f"ADTV{lookback}"

    # ------------------------------------------------------
    # IMPORTANT:
    # shift(1) ensures current candle does not affect its own
    # historical benchmark.
    # ------------------------------------------------------

    previous_volume = volume.shift(1)

    previous_traded_value = (
        close * volume
    ).shift(1)

    # Previous N candle average volume
    out[avg_volume_column] = (
        previous_volume
        .rolling(
            window=lookback,
            min_periods=lookback,
        )
        .mean()
    )

    # Current volume / previous N average volume
    out[relative_volume_column] = (
        volume / out[avg_volume_column]
    )

    out[relative_volume_column] = (
        out[relative_volume_column]
        .replace(
            [np.inf, -np.inf],
            np.nan,
        )
    )

    # Average Daily Traded Value
    out[adtv_column] = (
        previous_traded_value
        .rolling(
            window=lookback,
            min_periods=lookback,
        )
        .mean()
    )

    return out