import pandas as pd


def analyze_gap(
    df: pd.DataFrame,
    entry_date,
):
    """
    Calculates:

    - Highest EMA50-EMA200 gap since entry
    - Current EMA50-EMA200 gap
    - Gap percentage remaining
    """

    # Convert entry date
    entry_date = pd.to_datetime(entry_date)

    # Data after entry
    trade_df = df[df["Date"] >= entry_date].copy()

    if trade_df.empty:
        return None

    # EMA gap
    trade_df["Gap"] = trade_df["EMA50"] - trade_df["EMA200"]

    highest_gap = trade_df["Gap"].max()

    current_gap = trade_df.iloc[-1]["Gap"]

    if highest_gap <= 0:
        return None

    gap_percent = current_gap / highest_gap

    return {
        "Highest Gap": round(highest_gap, 2),
        "Current Gap": round(current_gap, 2),
        "Gap %": round(gap_percent * 100, 2),
    }