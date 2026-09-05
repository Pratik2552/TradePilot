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
        exit_timing="OPEN",
    ):

        entry_price = float(entry_price)
        exit_price = float(exit_price)

        if entry_price <= 0:
            raise ValueError(
                f"Invalid entry price for {symbol}: {entry_price}"
            )

        if exit_price <= 0:
            raise ValueError(
                f"Invalid exit price for {symbol}: {exit_price}"
            )

        # Same-day stop-loss exits are valid.
        if exit_date < entry_date:
            raise ValueError(
                f"Exit date cannot be before entry date for {symbol}"
            )

        if exit_timing not in {
            "OPEN",
            "INTRADAY",
        }:
            raise ValueError(
                f"Invalid exit timing: {exit_timing}"
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
        self.exit_timing = exit_timing

        self.mfe = mfe
        self.mae = mae

        # ------------------------------------------
        # Return
        # ------------------------------------------

        self.return_pct = (
            (self.exit_price - self.entry_price)
            / self.entry_price
        ) * 100

        # Calendar days
        self.holding_days = (
            self.exit_date - self.entry_date
        ).days

    def to_dict(self):

        return {
            "Symbol": self.symbol,

            "Entry Date": self.entry_date,
            "Exit Date": self.exit_date,

            "Entry Price": round(
                self.entry_price,
                2,
            ),

            "Exit Price": round(
                self.exit_price,
                2,
            ),

            "Return %": round(
                self.return_pct,
                2,
            ),

            "Holding Days":
                self.holding_days,

            "Highest Gap": round(
                self.highest_gap,
                4,
            ),

            "Highest Gap Date":
                self.highest_gap_date,

            "Bearish Cross Date":
                self.bearish_cross_date,

            "Gap Condition Date":
                self.gap_condition_date,

            "Exit Gap %": (
                round(
                    self.exit_gap * 100,
                    2,
                )
                if self.exit_gap is not None
                else None
            ),

            "Exit Reason":
                self.exit_reason,

            "Exit Timing":
                self.exit_timing,

            "MFE %": round(
                self.mfe,
                2,
            ),

            "MAE %": round(
                self.mae,
                2,
            ),
        }