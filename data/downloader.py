from pathlib import Path
from datetime import timedelta

import pandas as pd
import yfinance as yf


# ==========================================================
# Configuration
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / "cache"

CACHE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# Re-download complete history after this many days.
# Important because corporate actions can change historical
# adjusted prices.
FULL_REFRESH_DAYS = 30


# ==========================================================
# Cache Helpers
# ==========================================================

def get_cache_path(symbol: str) -> Path:
    return CACHE_DIR / f"{symbol}.csv"


def cache_exists(symbol: str) -> bool:
    return get_cache_path(symbol).exists()


def _clean_data(df: pd.DataFrame) -> pd.DataFrame:

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    if "Date" not in df.columns:
        return pd.DataFrame()

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
    )

    required_columns = [
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing OHLC columns: {missing}"
        )

    # Convert prices safely
    for column in [
        "Open",
        "High",
        "Low",
        "Close",
    ]:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df.dropna(
        subset=[
            "Date",
            "Open",
            "High",
            "Low",
            "Close",
        ],
        inplace=True,
    )

    # Invalid price rows must never enter backtest
    df = df[
        (df["Open"] > 0)
        &
        (df["High"] > 0)
        &
        (df["Low"] > 0)
        &
        (df["Close"] > 0)
    ]

    df.drop_duplicates(
        subset=["Date"],
        keep="last",
        inplace=True,
    )

    df.sort_values(
        "Date",
        inplace=True,
    )

    df.reset_index(
        drop=True,
        inplace=True,
    )

    return df


def save_cache(
    symbol: str,
    df: pd.DataFrame,
):

    df = _clean_data(df)

    if df.empty:
        return

    df.to_csv(
        get_cache_path(symbol),
        index=False,
    )


def load_cache(
    symbol: str,
) -> pd.DataFrame:

    path = get_cache_path(symbol)

    if not path.exists():
        return pd.DataFrame()

    try:

        df = pd.read_csv(
            path,
            parse_dates=["Date"],
        )

        return _clean_data(df)

    except Exception as exc:

        print(
            f"{symbol}: Invalid cache ({exc})"
        )

        return pd.DataFrame()


# ==========================================================
# Download Full Adjusted History
# ==========================================================

def download_full_history(
    symbol: str,
) -> pd.DataFrame:

    print(
        f"Downloading full adjusted history: {symbol}"
    )

    df = yf.download(
        tickers=symbol,
        period="max",
        interval="1d",

        # IMPORTANT:
        # All OHLC values are adjusted consistently.
        auto_adjust=True,

        progress=False,
        multi_level_index=False,
    )

    if df.empty:
        return pd.DataFrame()

    df.reset_index(
        inplace=True,
    )

    return _clean_data(df)


# ==========================================================
# Download Recent Missing Candles
# ==========================================================

def download_missing_history(
    symbol: str,
    last_date,
) -> pd.DataFrame:

    last_date = pd.to_datetime(
        last_date
    ).normalize()

    start_date = (
        last_date
        + timedelta(days=1)
    )

    today = pd.Timestamp.today().normalize()

    if start_date > today:
        return pd.DataFrame()

    print(
        f"Updating {symbol} from "
        f"{start_date.strftime('%Y-%m-%d')}"
    )

    df = yf.download(
        tickers=symbol,

        start=start_date.strftime(
            "%Y-%m-%d"
        ),

        end=(
            today
            + timedelta(days=1)
        ).strftime(
            "%Y-%m-%d"
        ),

        interval="1d",

        # MUST match full-history mode
        auto_adjust=True,

        progress=False,
        multi_level_index=False,
    )

    if df.empty:
        return pd.DataFrame()

    df.reset_index(
        inplace=True,
    )

    return _clean_data(df)


# ==========================================================
# Determine Whether Full Cache Refresh Is Needed
# ==========================================================

def full_refresh_required(
    symbol: str,
) -> bool:

    path = get_cache_path(symbol)

    if not path.exists():
        return True

    modified = pd.Timestamp(
        path.stat().st_mtime,
        unit="s",
    )

    age = (
        pd.Timestamp.now()
        - modified
    )

    return (
        age
        >= timedelta(
            days=FULL_REFRESH_DAYS
        )
    )


# ==========================================================
# Update / Get Stock Data
# ==========================================================

def get_stock_data(
    symbol: str,
    force_full_refresh: bool = False,
):

    # ------------------------------------------------------
    # Full historical refresh
    # ------------------------------------------------------

    if (
        force_full_refresh
        or
        not cache_exists(symbol)
        or
        full_refresh_required(symbol)
    ):

        df = download_full_history(
            symbol
        )

        if not df.empty:

            save_cache(
                symbol,
                df,
            )

        return df

    # ------------------------------------------------------
    # Load existing cache
    # ------------------------------------------------------

    cache = load_cache(
        symbol
    )

    if cache.empty:

        df = download_full_history(
            symbol
        )

        if not df.empty:

            save_cache(
                symbol,
                df,
            )

        return df

    # ------------------------------------------------------
    # Append recent missing candles
    # ------------------------------------------------------

    last_date = (
        cache["Date"]
        .max()
        .normalize()
    )

    missing = download_missing_history(
        symbol,
        last_date,
    )

    if missing.empty:

        return cache

    updated = pd.concat(
        [
            cache,
            missing,
        ],
        ignore_index=True,
    )

    updated = _clean_data(
        updated
    )

    save_cache(
        symbol,
        updated,
    )

    return updated


# ==========================================================
# Read Cache Only
# ==========================================================

def get_cached_stock_data(
    symbol: str,
):

    if not cache_exists(symbol):
        return pd.DataFrame()

    return load_cache(
        symbol
    )