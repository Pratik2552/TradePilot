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
    Returns the cache file path for a stock.
    """
    return CACHE_DIR / f"{symbol}.csv"


def cache_exists(symbol: str) -> bool:
    """
    Checks whether cached history exists.
    """
    return get_cache_path(symbol).exists()


def save_cache(symbol: str, df: pd.DataFrame):
    """
    Saves dataframe to cache.
    """
    df.to_csv(
        get_cache_path(symbol),
        index=False,
    )


def load_cache(symbol: str) -> pd.DataFrame:
    """
    Loads dataframe from cache.
    """
    return pd.read_csv(
        get_cache_path(symbol),
        parse_dates=["Date"],
    )


# -------------------------------------------------------------------
# Download Functions
# -------------------------------------------------------------------

def download_full_history(symbol: str) -> pd.DataFrame:
    """
    Downloads the complete daily history from Yahoo Finance.
    """

    print(f"Downloading {symbol}...")

    df = yf.download(
        tickers=symbol,
        period="max",
        interval="1d",
        auto_adjust=False,
        progress=False,
        multi_level_index=False,
    )

    df.reset_index(inplace=True)

    print(f"Downloaded {len(df)} candles.")

    return df


# -------------------------------------------------------------------
# Public API
# -------------------------------------------------------------------

def get_stock_data(symbol: str) -> pd.DataFrame:
    """
    Returns historical data for a stock.

    Current behaviour:
    - If cache exists → Load from cache.
    - Otherwise → Download full history and save it.

    Later we'll add:
    - Download only missing candles.
    """

    if cache_exists(symbol):

        print(f"Loading {symbol} from cache...")

        return load_cache(symbol)

    df = download_full_history(symbol)

    save_cache(symbol, df)

    return df