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

        self.trades = trades.copy()

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
            ]
        )

        self.trades[
            "Exit Date"
        ] = pd.to_datetime(
            self.trades[
                "Exit Date"
            ]
        )

        # Deterministic ordering.
        #
        # Never rank using:
        # Return %, Exit Price, MFE, MAE, etc.
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
    # RECORD REJECTION
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
            exit_price=exit_price,
            exit_date=current_date,
            reason=position.exit_reason,
        )

        record = (
            position.source_trade.copy()
        )

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
            ].unique()
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
            # 1. VALUE EXISTING POSITIONS AT MARKET OPEN
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
                        float(open_price)
                    )

            # ==================================================
            # 2. CLOSE POSITIONS THAT EXIT AT TODAY'S OPEN
            # ==================================================

            still_open = []

            for position in open_trades:

                should_close = (
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
            # 3. OPEN TODAY'S NEW POSITIONS AT OPEN
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
                    trade["Symbol"]
                )

                # ------------------------------------------
                # Duplicate symbol check
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
                # Max positions
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
                # Entry price
                # ------------------------------------------

                entry_price = (
                    pd.to_numeric(
                        trade[
                            "Entry Price"
                        ],
                        errors="coerce",
                    )
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

                # ------------------------------------------
                # Open position
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

                # ------------------------------------------
                # Store strategy exit information
                # ------------------------------------------

                position.target_exit = (
                    trade[
                        "Exit Date"
                    ]
                )

                position.target_exit_price = (
                    float(
                        trade[
                            "Exit Price"
                        ]
                    )
                )

                position.exit_reason = (
                    trade[
                        "Exit Reason"
                    ]
                )

                # Old trade files may not have this column.
                position.exit_timing = (
                    trade.get(
                        "Exit Timing",
                        "OPEN",
                    )
                )

                position.source_trade = (
                    trade.to_dict()
                )

                position.current_price = (
                    float(entry_price)
                )

                open_trades.append(
                    position
                )

            # ==================================================
            # 4. PROCESS INTRADAY STOP-LOSS EXITS
            # ==================================================
            #
            # This happens AFTER morning entries.
            #
            # An intraday stop cannot free a slot/cash
            # for an order that was already supposed
            # to execute at today's market open.
            # ==================================================

            still_open = []

            for position in open_trades:

                should_close = (
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
            # 5. MARK REMAINING POSITIONS AT CLOSE
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
                        float(close_price)
                    )

            # ==================================================
            # 6. RECORD DAILY EQUITY
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
    # EXECUTED TRADES
    # ==================================================

    def get_executed_trades(
        self,
    ):

        return pd.DataFrame(
            self.executed_trades
        )

    # ==================================================
    # REJECTED TRADES
    # ==================================================

    def get_rejected_trades(
        self,
    ):

        return pd.DataFrame(
            self.rejected_trades
        )