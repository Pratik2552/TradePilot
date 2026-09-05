import pandas as pd


def calculate_metrics(trades: pd.DataFrame) -> dict:
    """
    Calculate trade-level metrics.

    IMPORTANT:
    For portfolio performance, this function must receive ONLY
    trades that were actually executed by PortfolioSimulator.

    Do not pass the full candidate/signal trade list when portfolio
    constraints such as max positions can reject trades.
    """

    empty_metrics = {
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

    if trades is None or trades.empty:
        return empty_metrics

    required_columns = {
        "Return %",
        "Holding Days",
    }

    missing = required_columns - set(trades.columns)

    if missing:
        raise ValueError(
            f"Missing required metric columns: {sorted(missing)}"
        )

    trades = trades.copy()

    trades["Return %"] = pd.to_numeric(
        trades["Return %"],
        errors="coerce",
    )

    trades["Holding Days"] = pd.to_numeric(
        trades["Holding Days"],
        errors="coerce",
    )

    trades.dropna(
        subset=["Return %"],
        inplace=True,
    )

    if trades.empty:
        return empty_metrics

    wins = trades[trades["Return %"] > 0]

    losses = trades[trades["Return %"] < 0]

    gross_profit = wins["Return %"].sum()

    gross_loss = abs(
        losses["Return %"].sum()
    )

    if gross_loss > 0:
        profit_factor = gross_profit / gross_loss
    elif gross_profit > 0:
        profit_factor = float("inf")
    else:
        profit_factor = 0

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