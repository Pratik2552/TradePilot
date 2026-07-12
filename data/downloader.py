from pathlib import Path

import pandas as pd
import yfinance as yf


# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / "cache"

# Create cache folder automatically if it doesn't exist
CACHE_DIR.mkdir(exist_ok=True)


# -------------------------------------------------------------------
# Cache Helpers
# -------------------------------------------------------------------

def get_cache_path(symbol: str) -> Path:
    """
    Returns the cache file path for a symbol.
    """

    return CACHE_DIR / f"{symbol}.csv"


def cache_exists(symbol: str) -> bool:
    """
    Checks whether cached history exists.
    """

    return get_cache_path(symbol).exists()


# -------------------------------------------------------------------
# Download Functions
# -------------------------------------------------------------------

def download_full_history(
    symbol: str,
    start_date=None,
    end_date=None,
) -> pd.DataFrame:
    """
    Downloads the complete historical data from Yahoo Finance.
    """

    df = yf.download(
        symbol,
        start=start_date,
        end=end_date,
        auto_adjust=True,
        progress=False,
        multi_level_index=False,
    )

    df.reset_index(inplace=True)

    return df


# -------------------------------------------------------------------
# Public API
# -------------------------------------------------------------------

def get_stock_data(
    symbol: str,
    start_date=None,
    end_date=None,
) -> pd.DataFrame:
    """
    Main function used by the rest of the application.

    Currently:
        Downloads full history.

    Later:
        - Load cache
        - Update missing candles
        - Save cache
    """

    return download_full_history(
        symbol,
        start_date,
        end_date,
    )