import pandas as pd


def calculate_metrics(trades: pd.DataFrame) -> dict:
    """
    Calculate performance metrics from completed trades.
    """

    if trades.empty:

        return {
            "Total Trades": 0,
            "Winning Trades": 0,
            "Losing Trades": 0,
            "Win Rate (%)": 0,
            "Average Return (%)": 0,
            "Median Return (%)": 0,
            "Max Return (%)": 0,
            "Max Loss (%)": 0,
            "Profit Factor": 0,
            "Average Holding Days": 0,
        }

    wins = trades[trades["Return %"] > 0]
    losses = trades[trades["Return %"] <= 0]

    gross_profit = wins["Return %"].sum()

    gross_loss = abs(losses["Return %"].sum())

    profit_factor = (
        gross_profit / gross_loss
        if gross_loss > 0
        else float("inf")
    )

    return {

        "Total Trades": len(trades),

        "Winning Trades": len(wins),

        "Losing Trades": len(losses),

        "Win Rate (%)": round(
            len(wins) / len(trades) * 100,
            2,
        ),

        "Average Return (%)": round(
            trades["Return %"].mean(),
            2,
        ),

        "Median Return (%)": round(
            trades["Return %"].median(),
            2,
        ),

        "Max Return (%)": round(
            trades["Return %"].max(),
            2,
        ),

        "Max Loss (%)": round(
            trades["Return %"].min(),
            2,
        ),

        "Profit Factor": round(
            profit_factor,
            2,
        ),

        "Average Holding Days": round(
            trades["Holding Days"].mean(),
            2,
        ),

    }