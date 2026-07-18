from strategy.golden_cross import find_recent_golden_cross
from strategy.ranking import rank_stock
from strategy.gap_tracker import analyze_gap

from data.downloader import get_stock_data
from indicators.ema import add_ema


def scan_stock(symbol, entered_positions, lookback):

    try:

        df = get_stock_data(symbol)

        if len(df) < 250:
            return None, None

        for period in [9, 21, 50, 200]:
            df = add_ema(df, period)

        fresh = None
        entered = None

        # -------------------------
        # Fresh Golden Cross
        # -------------------------

        gc = find_recent_golden_cross(
            df,
            lookback,
        )

        if gc is not None:

            rank = rank_stock(df)

            fresh = {

                "Symbol": symbol,
                "Date": gc["Date"],
                "Close": round(float(gc["Close"]), 2),

                "Current Volume": rank["Current Volume"],
                "20D Avg Volume": rank["20D Avg Volume"],
                "Volume Ratio": rank["Volume Ratio"],
                "EMA Distance %": rank["EMA Distance %"],

                "EMA50": round(float(gc["EMA50"]), 2),
                "EMA200": round(float(gc["EMA200"]), 2),

                "TradingView":
                    f"https://www.tradingview.com/chart/?symbol=NSE:{symbol.replace('.NS','')}",

                "Screener":
                    f"https://www.screener.in/company/{symbol.replace('.NS','')}/"

            }

        # -------------------------
        # Entered Position
        # -------------------------

        if not entered_positions.empty:

            trade = entered_positions[
                entered_positions["Symbol"] == symbol
            ]

            if not trade.empty:

                gap = analyze_gap(
                    df,
                    trade.iloc[0]["Entry Date"],
                )

                if gap is not None:

                    entered = {

                        "Symbol": symbol,

                        "Highest Gap": gap["Highest Gap"],
                        "Current Gap": gap["Current Gap"],
                        "Gap %": gap["Gap %"],

                    }

        return fresh, entered

    except Exception as e:

        print(symbol, e)

        return None, None