from dataclasses import dataclass


@dataclass
class Position:

    symbol: str

    entry_date: object
    exit_date: object | None

    entry_price: float

    shares: float

    invested: float

    exit_price: float | None = None

    closed: bool = False

    exit_reason: str | None = None

    current_price: float | None = None

    def market_value(self):

        if self.current_price is None:
            return self.invested

        return self.shares * self.current_price

    def pnl(self):

        return self.market_value() - self.invested

    def return_percent(self):

        return (
            self.pnl()
            / self.invested
        ) * 100

    def close(
        self,
        exit_price,
        exit_date,
        reason,
    ):

        self.exit_price = exit_price

        self.exit_date = exit_date

        self.current_price = exit_price

        self.closed = True

        self.exit_reason = reason

        return self.market_value()