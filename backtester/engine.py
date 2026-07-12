from config import START_DATE, END_DATE
from data.universe import refresh_universe, load_symbols
from data.downloader import get_stock_data
from indicators.ema import add_ema
from strategy.golden_cross import find_golden_crosses


def run_backtest():
    """
    Main backtesting engine.
    """

    # Refresh the NSE stock universe
    refresh_universe()

    # Load all available NSE symbols
    symbols = load_symbols()

    print(f"\nLoaded {len(symbols)} NSE stocks.\n")

    # -------------------------------------------------------
    # TEMPORARY
    # Scan only the first stock while we're developing.
    # Later simply remove this line.
    # -------------------------------------------------------
    symbols = symbols[:1]

    for symbol in symbols:

        print("\n" + "=" * 60)
        print(f"Scanning {symbol}")
        print("=" * 60)

        # Download historical data
        df = get_stock_data(
            symbol=symbol,
            start_date=START_DATE,
            end_date=END_DATE,
        )

        print(f"Downloaded {len(df)} candles.")

        # Calculate EMAs
        for period in [9, 21, 50, 200]:
            df = add_ema(df, period)

        # Detect Golden Crosses
        golden_crosses = find_golden_crosses(df)

        print(f"\nGolden Crosses Found: {len(golden_crosses)}")

        if golden_crosses.empty:
            print("No Golden Crosses Found.")
        else:
            print(
                golden_crosses[
                    ["Date", "Close", "EMA50", "EMA200"]
                ]
            )

    print("\nBacktest Completed.")