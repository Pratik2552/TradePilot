import pandas as pd


def build_equity_curve(

    trades: pd.DataFrame,

    initial_capital: float = 100000,

):

    """
    Builds the account equity curve by
    compounding every completed trade.
    """

    equity = initial_capital

    history = []

    trades = trades.sort_values(
        by="Exit Date"
    )

    for _, trade in trades.iterrows():

        equity *= (
            1 +
            trade["Return %"] / 100
        )

        history.append({

            "Date": trade["Exit Date"],

            "Symbol": trade["Symbol"],

            "Return %": trade["Return %"],

            "Equity": round(equity, 2),

        })

    return pd.DataFrame(history)