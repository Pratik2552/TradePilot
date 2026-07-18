import pandas as pd


def rank_stock(df: pd.DataFrame) -> dict:
    """
    Calculate ranking metrics for a stock.
    """

    avg_volume = df["Volume"].tail(20).mean()
    current_volume = df.iloc[-1]["Volume"]

    volume_ratio = (
        current_volume / avg_volume
        if avg_volume > 0
        else 0
    )

    ema_distance = (
        (df.iloc[-1]["EMA50"] - df.iloc[-1]["EMA200"])
        / df.iloc[-1]["EMA200"]
    ) * 100

    return {
        "Current Volume": int(current_volume),
        "20D Avg Volume": int(avg_volume),
        "Volume Ratio": round(volume_ratio, 2),
        "EMA Distance %": round(ema_distance, 2),
    }