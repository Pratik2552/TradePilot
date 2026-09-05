from portfolio.position import Position


class Portfolio:

    def __init__(
        self,
        initial_capital=100000,
        allocation=0.10,
        max_positions=10,
    ):

        self.initial_capital = initial_capital

        self.cash = initial_capital

        self.allocation = allocation

        self.max_positions = max_positions

        self.open_positions = []

        self.closed_positions = []

    # --------------------------------------------------
    # Portfolio Value
    # --------------------------------------------------

    def equity(self):

        total = self.cash

        for position in self.open_positions:

            total += position.market_value()

        return total

    # --------------------------------------------------
    # Can Enter?
    # --------------------------------------------------

    def can_enter(self, symbol):

        if len(self.open_positions) >= self.max_positions:
            return False

        for position in self.open_positions:

            if position.symbol == symbol:
                return False

        return True

    # --------------------------------------------------
    # Open Position
    # --------------------------------------------------

    def open_position(

        self,

        symbol,

        entry_date,

        entry_price,

    ):

        if not self.can_enter(symbol):
            return None

        invest_amount = self.equity() * self.allocation

        invest_amount = min(
            invest_amount,
            self.cash,
        )

        if invest_amount <= 0:
            return None

        shares = invest_amount / entry_price

        self.cash -= invest_amount

        position = Position(

            symbol=symbol,

            entry_date=entry_date,

            exit_date=None,

            entry_price=entry_price,

            shares=shares,

            invested=invest_amount,

        )

        self.open_positions.append(position)

        return position

    # --------------------------------------------------
    # Close Position
    # --------------------------------------------------

    def close_position(

        self,

        position,

        exit_price,

        exit_date,

        reason,

    ):

        returned_cash = position.close(

            exit_price,

            exit_date,

            reason,

        )

        self.cash += returned_cash

        self.open_positions.remove(position)

        self.closed_positions.append(position)

    # --------------------------------------------------
    # Update Prices
    # --------------------------------------------------

    def update_price(

        self,

        symbol,

        price,

    ):

        for position in self.open_positions:

            if position.symbol == symbol:

                position.current_price = price

    # --------------------------------------------------
    # Exposure
    # --------------------------------------------------

    def exposure(self):

        invested = 0

        for position in self.open_positions:

            invested += position.market_value()

        if self.equity() == 0:
            return 0

        return invested / self.equity() * 100