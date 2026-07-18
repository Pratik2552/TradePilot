from pathlib import Path

import pandas as pd

from config import MIN_STOCK_PRICE

from strategy.golden_cross import find_golden_crosses
from backtester.simulator import simulate_trade


def generate_trade_report(
    symbol: str,
    df: pd.DataFrame,
    gap_threshold: float = 0.50,
):

    valid_trades = []
    invalid_trades = []

    golden_crosses = find_golden_crosses(df)

    for idx in golden_crosses.index:

        entry_price = float(df.loc[idx, "Close"])

        # --------------------------------------------------
        # Skip Penny Stocks
        # --------------------------------------------------

        if entry_price < MIN_STOCK_PRICE:
            continue

        trade = simulate_trade(
            df=df,
            symbol=symbol,
            entry_index=idx,
            gap_threshold=gap_threshold,
        )

        if trade is None:
            continue

        trade = trade.to_dict()

        # --------------------------------------------------
        # Validate Trade
        # --------------------------------------------------

        reason = None

        if trade["Entry Price"] <= 0:
            reason = "Entry Price <= 0"

        elif trade["Exit Price"] <= 0:
            reason = "Exit Price <= 0"

    

        elif trade["Holding Days"] <= 0:
            reason = "Invalid Holding Days"

        if reason is None:

            valid_trades.append(trade)

        else:

            trade["Reason"] = reason
            invalid_trades.append(trade)

    # --------------------------------------------------
    # Save Invalid Trades
    # --------------------------------------------------

    if invalid_trades:

        invalid_df = pd.DataFrame(invalid_trades)

        invalid_file = Path("results/invalid_trades.csv")

        if invalid_file.exists():

            existing = pd.read_csv(invalid_file)

            invalid_df = pd.concat(
                [existing, invalid_df],
                ignore_index=True,
            ).drop_duplicates()

        invalid_df.to_csv(
            invalid_file,
            index=False,
        )

    return pd.DataFrame(valid_trades)