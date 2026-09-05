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
        exit_timing="OPEN",
        status=None,
        current_price=None,
        current_date=None,
        pending_exit_reason=None,
    ):

        # ==================================================
        # ENTRY
        # ==================================================

        entry_price = float(entry_price)

        if entry_price <= 0:
            raise ValueError(
                f"Invalid entry price for {symbol}: "
                f"{entry_price}"
            )

        self.symbol = symbol

        self.entry_date = pd.Timestamp(
            entry_date
        )

        self.entry_price = entry_price

        # ==================================================
        # DETERMINE STATUS
        # ==================================================

        if status is None:

            if (
                exit_date is None
                or exit_price is None
                or pd.isna(exit_date)
                or pd.isna(exit_price)
            ):
                status = "OPEN"

            else:
                status = "CLOSED"

        status = str(status).upper()

        if status not in {
            "OPEN",
            "CLOSED",
        }:
            raise ValueError(
                f"Invalid trade status: {status}"
            )

        self.status = status

        # ==================================================
        # COMMON STRATEGY INFORMATION
        # ==================================================

        self.highest_gap = highest_gap
        self.highest_gap_date = highest_gap_date

        self.bearish_cross_date = bearish_cross_date
        self.gap_condition_date = gap_condition_date

        self.exit_gap = exit_gap

        self.exit_reason = exit_reason

        self.pending_exit_reason = (
            pending_exit_reason
        )

        self.mfe = (
            float(mfe)
            if (
                mfe is not None
                and not pd.isna(mfe)
            )
            else None
        )

        self.mae = (
            float(mae)
            if (
                mae is not None
                and not pd.isna(mae)
            )
            else None
        )

        # ==================================================
        # CLOSED TRADE
        # ==================================================

        if self.status == "CLOSED":

            if (
                exit_date is None
                or pd.isna(exit_date)
            ):
                raise ValueError(
                    f"Closed trade missing exit date: "
                    f"{symbol}"
                )

            if (
                exit_price is None
                or pd.isna(exit_price)
            ):
                raise ValueError(
                    f"Closed trade missing exit price: "
                    f"{symbol}"
                )

            exit_price = float(
                exit_price
            )

            if exit_price <= 0:
                raise ValueError(
                    f"Invalid exit price for "
                    f"{symbol}: {exit_price}"
                )

            exit_date = pd.Timestamp(
                exit_date
            )

            if (
                exit_date
                < self.entry_date
            ):
                raise ValueError(
                    "Exit date cannot be before "
                    f"entry date for {symbol}"
                )

            if exit_timing not in {
                "OPEN",
                "INTRADAY",
            }:
                raise ValueError(
                    f"Invalid exit timing: "
                    f"{exit_timing}"
                )

            self.exit_date = exit_date
            self.exit_price = exit_price
            self.exit_timing = exit_timing

            self.current_price = None
            self.current_date = None

            # ------------------------------------------
            # REALIZED RETURN
            # ------------------------------------------

            self.return_pct = (
                (
                    self.exit_price
                    - self.entry_price
                )
                / self.entry_price
            ) * 100

            self.unrealized_return_pct = None

            self.holding_days = (
                self.exit_date
                - self.entry_date
            ).days

        # ==================================================
        # OPEN TRADE
        # ==================================================

        else:

            self.exit_date = None
            self.exit_price = None
            self.exit_timing = None

            # ------------------------------------------
            # CURRENT PRICE
            # ------------------------------------------

            if (
                current_price is None
                or pd.isna(current_price)
            ):
                current_price = (
                    self.entry_price
                )

            current_price = float(
                current_price
            )

            if current_price <= 0:
                current_price = (
                    self.entry_price
                )

            self.current_price = (
                current_price
            )

            # ------------------------------------------
            # CURRENT DATE
            # ------------------------------------------

            if (
                current_date is None
                or pd.isna(current_date)
            ):
                current_date = (
                    self.entry_date
                )

            self.current_date = pd.Timestamp(
                current_date
            )

            if (
                self.current_date
                < self.entry_date
            ):
                self.current_date = (
                    self.entry_date
                )

            # ------------------------------------------
            # OPEN TRADE HAS NO REALIZED RETURN
            # ------------------------------------------

            self.return_pct = None

            self.unrealized_return_pct = (
                (
                    self.current_price
                    - self.entry_price
                )
                / self.entry_price
            ) * 100

            self.holding_days = (
                self.current_date
                - self.entry_date
            ).days

    # ==================================================
    # DICTIONARY
    # ==================================================

    def to_dict(self):

        return {

            "Symbol":
                self.symbol,

            "Status":
                self.status,

            "Entry Date":
                self.entry_date,

            "Exit Date":
                self.exit_date,

            "Entry Price":
                round(
                    self.entry_price,
                    2,
                ),

            "Exit Price":
                (
                    round(
                        self.exit_price,
                        2,
                    )
                    if self.exit_price
                    is not None
                    else None
                ),

            "Return %":
                (
                    round(
                        self.return_pct,
                        2,
                    )
                    if self.return_pct
                    is not None
                    else None
                ),

            "Current Date":
                self.current_date,

            "Current Price":
                (
                    round(
                        self.current_price,
                        2,
                    )
                    if self.current_price
                    is not None
                    else None
                ),

            "Unrealized Return %":
                (
                    round(
                        self.unrealized_return_pct,
                        2,
                    )
                    if (
                        self.unrealized_return_pct
                        is not None
                    )
                    else None
                ),

            "Holding Days":
                self.holding_days,

            "Highest Gap":
                (
                    round(
                        self.highest_gap,
                        4,
                    )
                    if self.highest_gap
                    is not None
                    else None
                ),

            "Highest Gap Date":
                self.highest_gap_date,

            "Bearish Cross Date":
                self.bearish_cross_date,

            "Gap Condition Date":
                self.gap_condition_date,

            "Exit Gap %":
                (
                    round(
                        self.exit_gap * 100,
                        2,
                    )
                    if self.exit_gap
                    is not None
                    else None
                ),

            "Exit Reason":
                self.exit_reason,

            "Pending Exit Reason":
                self.pending_exit_reason,

            "Exit Timing":
                self.exit_timing,

            "MFE %":
                (
                    round(
                        self.mfe,
                        2,
                    )
                    if self.mfe
                    is not None
                    else None
                ),

            "MAE %":
                (
                    round(
                        self.mae,
                        2,
                    )
                    if self.mae
                    is not None
                    else None
                ),
        }