import pandas as pd


class Trade:

    def __init__(
        self,
        symbol,
        entry_date,
        exit_date,
        entry_price,
        exit_price,
        highest_gap,
        highest_gap_date,
        bearish_cross_date,
        gap_condition_date,
        exit_gap,
        exit_reason,
        mfe,
        mae,
    ):

        if entry_price <= 0:
            raise ValueError(
                f"Invalid entry price for {symbol}: {entry_price}"
            )

        self.symbol = symbol

        self.entry_date = entry_date
        self.exit_date = exit_date

        self.entry_price = entry_price
        self.exit_price = exit_price

        self.highest_gap = highest_gap
        self.highest_gap_date = highest_gap_date

        self.bearish_cross_date = bearish_cross_date
        self.gap_condition_date = gap_condition_date

        self.exit_gap = exit_gap
        self.exit_reason = exit_reason

        self.mfe = mfe
        self.mae = mae

        self.return_pct = (
            (exit_price - entry_price)
            / entry_price
        ) * 100

        self.holding_days = (
            exit_date - entry_date
        ).days

    def to_dict(self):

        return {

            "Symbol": self.symbol,

            "Entry Date": self.entry_date,
            "Exit Date": self.exit_date,

            "Entry Price": round(self.entry_price, 2),
            "Exit Price": round(self.exit_price, 2),

            "Return %": round(self.return_pct, 2),

            "Holding Days": self.holding_days,

            "Highest Gap": round(self.highest_gap, 4),
            "Highest Gap Date": self.highest_gap_date,

            "Bearish Cross Date": self.bearish_cross_date,
            "Gap Condition Date": self.gap_condition_date,

            "Exit Gap %": (
                round(self.exit_gap * 100, 2)
                if self.exit_gap is not None
                else None
            ),

            "Exit Reason": self.exit_reason,

            "MFE %": round(self.mfe, 2),
            "MAE %": round(self.mae, 2),

        }