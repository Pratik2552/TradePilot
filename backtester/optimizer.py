import pandas as pd

from backtester.simulator import simulate_trade
from backtester.metrics import calculate_metrics
from strategy.golden_cross import find_golden_crosses


def optimize_strategy(
    df: pd.DataFrame,
    thresholds=None,
):
    """
    Test multiple EMA gap thresholds.
    """

    if thresholds is None:
        thresholds = [
            0.30,
            0.35,
            0.40,
            0.45,
            0.50,
            0.55,
            0.60,
            0.65,
            0.70,
        ]

    results = []

    golden_crosses = find_golden_crosses(df)

    for threshold in thresholds:

        trades = []

        for idx in golden_crosses.index:

            trade = simulate_trade(
                df=df,
                entry_index=idx,
                gap_threshold=threshold,
            )

            if trade is not None:
                trades.append(trade)

        trades_df = pd.DataFrame(trades)

        metrics = calculate_metrics(trades_df)

        metrics["Gap Threshold"] = threshold

        results.append(metrics)

    return pd.DataFrame(results)