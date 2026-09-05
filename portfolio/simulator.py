import pandas as pd

from portfolio.portfolio import Portfolio

from data.downloader import (
    get_cached_stock_data,
)


class PortfolioSimulator:

    def __init__(
        self,
        trades,
        initial_capital=100000,
        allocation=0.10,
        max_positions=10,
    ):

        self.trades = (
            trades.copy()
        )

        self.portfolio = Portfolio(
            initial_capital,
            allocation,
            max_positions,
        )

        self.daily_equity = []

        self.executed_trades = []

        self.rejected_trades = []

    # ==================================================
    # PREPARE
    # ==================================================

    def prepare(self):

        if (
            self.trades is None
            or self.trades.empty
        ):
            return

        self.trades[
            "Entry Date"
        ] = pd.to_datetime(

            self.trades[
                "Entry Date"
            ],

            errors="coerce",
        )

        if (
            "Exit Date"
            in self.trades.columns
        ):

            self.trades[
                "Exit Date"
            ] = pd.to_datetime(

                self.trades[
                    "Exit Date"
                ],

                errors="coerce",
            )

        # ==================================================
        # BACKWARD COMPATIBILITY
        # ==================================================

        if (
            "Status"
            not in self.trades.columns
        ):

            self.trades[
                "Status"
            ] = "CLOSED"

        # ==================================================
        # DETERMINISTIC ORDER
        # ==================================================

        self.trades.sort_values(

            [
                "Entry Date",
                "Symbol",
            ],

            kind="mergesort",

            inplace=True,
        )

        self.trades.reset_index(
            drop=True,
            inplace=True,
        )

    # ==================================================
    # REJECT
    # ==================================================

    def _reject(
        self,
        trade,
        reason,
    ):

        rejected = (
            trade.to_dict()
        )

        rejected[
            "Rejection Reason"
        ] = reason

        self.rejected_trades.append(
            rejected
        )

    # ==================================================
    # CLOSE POSITION
    # ==================================================

    def _close_position(
        self,
        position,
        current_date,
    ):

        exit_price = float(
            position.target_exit_price
        )

        returned_cash = (
            position.shares
            * exit_price
        )

        realized_pnl = (
            returned_cash
            - position.invested
        )

        realized_return = (
            realized_pnl
            / position.invested
            * 100
        )

        self.portfolio.close_position(

            position,

            exit_price=
                exit_price,

            exit_date=
                current_date,

            reason=
                position.exit_reason,
        )

        record = (
            position.source_trade.copy()
        )

        record[
            "Status"
        ] = "CLOSED"

        record[
            "Entry Date"
        ] = position.entry_date

        record[
            "Exit Date"
        ] = current_date

        record[
            "Entry Price"
        ] = position.entry_price

        record[
            "Exit Price"
        ] = exit_price

        record[
            "Return %"
        ] = realized_return

        record[
            "Current Date"
        ] = None

        record[
            "Current Price"
        ] = None

        record[
            "Unrealized Return %"
        ] = None

        record[
            "Invested"
        ] = position.invested

        record[
            "Shares"
        ] = position.shares

        record[
            "Realized P&L"
        ] = realized_pnl

        record[
            "Returned Cash"
        ] = returned_cash

        record[
            "Exit Timing"
        ] = position.exit_timing

        self.executed_trades.append(
            record
        )

    # ==================================================
    # RUN
    # ==================================================

    def run(self):

        self.prepare()

        if (
            self.trades is None
            or self.trades.empty
        ):

            return pd.DataFrame(

                columns=[
                    "Date",
                    "Cash",
                    "Invested",
                    "Portfolio",
                    "Open Positions",
                ]
            )

        symbols = (
            self.trades[
                "Symbol"
            ]
            .dropna()
            .unique()
        )

        history = {}

        calendar = set()

        # ==================================================
        # LOAD HISTORY
        # ==================================================

        for symbol in symbols:

            df = get_cached_stock_data(
                symbol
            )

            if df.empty:
                continue

            df = df.copy()

            df[
                "Date"
            ] = pd.to_datetime(
                df["Date"]
            )

            df.drop_duplicates(

                subset=[
                    "Date"
                ],

                keep="last",

                inplace=True,
            )

            df.set_index(
                "Date",
                inplace=True,
            )

            df.sort_index(
                inplace=True,
            )

            history[
                symbol
            ] = df

            calendar.update(
                df.index
            )

        calendar = sorted(
            calendar
        )

        open_trades = []

        # ==================================================
        # DAILY SIMULATION
        # ==================================================

        for current_date in calendar:

            # ==================================================
            # 1. VALUE EXISTING POSITIONS AT OPEN
            # ==================================================

            for position in open_trades:

                df = history.get(
                    position.symbol
                )

                if df is None:
                    continue

                if (
                    current_date
                    not in df.index
                ):
                    continue

                open_price = df.loc[
                    current_date,
                    "Open",
                ]

                if (
                    pd.notna(open_price)
                    and open_price > 0
                ):

                    position.current_price = (
                        float(
                            open_price
                        )
                    )

                    position.current_date = (
                        current_date
                    )

            # ==================================================
            # 2. CLOSE TODAY'S OPEN EXITS
            # ==================================================

            still_open = []

            for position in open_trades:

                should_close = (

                    position.target_exit
                    is not None

                    and

                    not pd.isna(
                        position.target_exit
                    )

                    and

                    current_date
                    == position.target_exit

                    and

                    position.exit_timing
                    == "OPEN"
                )

                if should_close:

                    self._close_position(
                        position,
                        current_date,
                    )

                else:

                    still_open.append(
                        position
                    )

            open_trades = (
                still_open
            )

            # ==================================================
            # 3. TODAY'S ENTRIES
            # ==================================================

            todays_entries = (

                self.trades[

                    self.trades[
                        "Entry Date"
                    ]
                    == current_date
                ]
            )

            for _, trade in (
                todays_entries.iterrows()
            ):

                symbol = (
                    trade[
                        "Symbol"
                    ]
                )

                # ------------------------------------------
                # STATUS
                # ------------------------------------------

                raw_status = (
                    trade.get(
                        "Status",
                        None,
                    )
                )

                if (
                    raw_status is None
                    or pd.isna(raw_status)
                ):

                    if (
                        pd.notna(
                            trade.get(
                                "Exit Date"
                            )
                        )
                    ):
                        trade_status = (
                            "CLOSED"
                        )

                    else:
                        trade_status = (
                            "OPEN"
                        )

                else:

                    trade_status = str(
                        raw_status
                    ).upper()

                # ------------------------------------------
                # DUPLICATE SYMBOL
                # ------------------------------------------

                duplicate_symbol = any(

                    position.symbol
                    == symbol

                    for position
                    in self.portfolio.open_positions
                )

                if duplicate_symbol:

                    self._reject(
                        trade,
                        "Symbol Already Open",
                    )

                    continue

                # ------------------------------------------
                # MAX POSITIONS
                # ------------------------------------------

                if (
                    len(
                        self.portfolio.open_positions
                    )
                    >=
                    self.portfolio.max_positions
                ):

                    self._reject(
                        trade,
                        "Max Positions Reached",
                    )

                    continue

                # ------------------------------------------
                # ENTRY PRICE
                # ------------------------------------------

                entry_price = pd.to_numeric(

                    trade[
                        "Entry Price"
                    ],

                    errors="coerce",
                )

                if (
                    pd.isna(entry_price)
                    or entry_price <= 0
                ):

                    self._reject(
                        trade,
                        "Invalid Entry Price",
                    )

                    continue

                # ==================================================
                # VALIDATE CLOSED TRADE BEFORE OPENING
                # ==================================================

                exit_date = None
                exit_price = None

                if (
                    trade_status
                    == "CLOSED"
                ):

                    exit_date = (
                        trade.get(
                            "Exit Date"
                        )
                    )

                    exit_price = pd.to_numeric(

                        trade.get(
                            "Exit Price"
                        ),

                        errors="coerce",
                    )

                    if (
                        exit_date is None
                        or pd.isna(exit_date)
                        or pd.isna(exit_price)
                        or exit_price <= 0
                    ):

                        self._reject(
                            trade,
                            "Invalid Historical Exit",
                        )

                        continue

                # ------------------------------------------
                # OPEN PORTFOLIO POSITION
                # ------------------------------------------

                position = (
                    self.portfolio.open_position(

                        symbol=symbol,

                        entry_date=
                            trade[
                                "Entry Date"
                            ],

                        entry_price=
                            float(
                                entry_price
                            ),
                    )
                )

                if position is None:

                    self._reject(
                        trade,
                        "Portfolio Rejected Entry",
                    )

                    continue

                # ==================================================
                # CLOSED HISTORICAL TRADE
                # ==================================================

                if (
                    trade_status
                    == "CLOSED"
                ):

                    position.target_exit = (
                        exit_date
                    )

                    position.target_exit_price = (
                        float(
                            exit_price
                        )
                    )

                    position.exit_reason = (
                        trade.get(
                            "Exit Reason"
                        )
                    )

                    position.exit_timing = (
                        trade.get(
                            "Exit Timing",
                            "OPEN",
                        )
                    )

                # ==================================================
                # OPEN POSITION
                # ==================================================

                else:

                    position.target_exit = None

                    position.target_exit_price = (
                        None
                    )

                    position.exit_reason = None

                    position.exit_timing = None

                position.source_trade = (
                    trade.to_dict()
                )

                position.current_price = (
                    float(
                        entry_price
                    )
                )

                position.current_date = (
                    trade[
                        "Entry Date"
                    ]
                )

                open_trades.append(
                    position
                )

            # ==================================================
            # 4. INTRADAY STOP EXITS
            # ==================================================

            still_open = []

            for position in open_trades:

                should_close = (

                    position.target_exit
                    is not None

                    and

                    not pd.isna(
                        position.target_exit
                    )

                    and

                    current_date
                    == position.target_exit

                    and

                    position.exit_timing
                    == "INTRADAY"
                )

                if should_close:

                    self._close_position(
                        position,
                        current_date,
                    )

                else:

                    still_open.append(
                        position
                    )

            open_trades = (
                still_open
            )

            # ==================================================
            # 5. MARK OPEN POSITIONS AT CLOSE
            # ==================================================

            for position in open_trades:

                df = history.get(
                    position.symbol
                )

                if df is None:
                    continue

                if (
                    current_date
                    not in df.index
                ):
                    continue

                close_price = df.loc[
                    current_date,
                    "Close",
                ]

                if (
                    pd.notna(close_price)
                    and close_price > 0
                ):

                    position.current_price = (
                        float(
                            close_price
                        )
                    )

                    position.current_date = (
                        current_date
                    )

            # ==================================================
            # 6. DAILY EQUITY
            # ==================================================

            invested = sum(

                position.market_value()

                for position
                in self.portfolio.open_positions
            )

            self.daily_equity.append(

                {

                    "Date":
                        current_date,

                    "Cash":
                        self.portfolio.cash,

                    "Invested":
                        invested,

                    "Portfolio":
                        self.portfolio.equity(),

                    "Open Positions":
                        len(
                            self.portfolio.open_positions
                        ),
                }
            )

        return pd.DataFrame(
            self.daily_equity
        )

    # ==================================================
    # CLOSED EXECUTED TRADES
    # ==================================================

    def get_executed_trades(
        self,
    ):

        return pd.DataFrame(
            self.executed_trades
        )

    # ==================================================
    # OPEN POSITIONS
    # ==================================================

    def get_open_trades(
        self,
    ):

        records = []

        for position in (
            self.portfolio.open_positions
        ):

            record = (
                position.source_trade.copy()
            )

            current_price = float(
                position.current_price
            )

            market_value = (
                position.shares
                * current_price
            )

            unrealized_pnl = (
                market_value
                - position.invested
            )

            unrealized_return = (
                unrealized_pnl
                / position.invested
                * 100
            )

            record[
                "Status"
            ] = "OPEN"

            record[
                "Exit Date"
            ] = None

            record[
                "Exit Price"
            ] = None

            record[
                "Return %"
            ] = None

            record[
                "Current Date"
            ] = getattr(
                position,
                "current_date",
                None,
            )

            record[
                "Current Price"
            ] = current_price

            record[
                "Unrealized Return %"
            ] = unrealized_return

            record[
                "Invested"
            ] = position.invested

            record[
                "Shares"
            ] = position.shares

            record[
                "Market Value"
            ] = market_value

            record[
                "Unrealized P&L"
            ] = unrealized_pnl

            records.append(
                record
            )

        return pd.DataFrame(
            records
        )

    # ==================================================
    # REJECTED
    # ==================================================

    def get_rejected_trades(
        self,
    ):

        return pd.DataFrame(
            self.rejected_trades
        )