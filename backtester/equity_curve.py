from pathlib import Path

import pandas as pd


def generate_equity_curve(
    equity_curve: pd.DataFrame,
    output_path: str = "results/equity_curve.csv",
) -> pd.DataFrame:
    """
    Validate and save an equity curve produced by PortfolioSimulator.

    IMPORTANT:
    This function does NOT calculate portfolio returns from trade-level
    Return % values.

    Portfolio accounting must be performed by PortfolioSimulator, which
    correctly handles:
        - cash
        - position sizing
        - maximum positions
        - overlapping trades
        - mark-to-market values
        - realized gains/losses

    This function only validates and saves the resulting daily curve.
    """

    if equity_curve is None or equity_curve.empty:
        return pd.DataFrame()

    required_columns = {
        "Date",
        "Cash",
        "Invested",
        "Portfolio",
        "Open Positions",
    }

    missing_columns = required_columns - set(equity_curve.columns)

    if missing_columns:
        raise ValueError(
            f"Equity curve missing required columns: "
            f"{sorted(missing_columns)}"
        )

    result = equity_curve.copy()

    result["Date"] = pd.to_datetime(result["Date"])

    result.sort_values(
        "Date",
        inplace=True,
    )

    result.drop_duplicates(
        subset=["Date"],
        keep="last",
        inplace=True,
    )

    result.reset_index(
        drop=True,
        inplace=True,
    )

    output = Path(output_path)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        output,
        index=False,
    )

    return result