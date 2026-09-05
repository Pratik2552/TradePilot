from pathlib import Path
from datetime import date
from io import StringIO

import pandas as pd
import requests


# ==========================================================
# Configuration
# ==========================================================

NSE_EQUITY_URL = (
    "https://nsearchives.nseindia.com/"
    "content/equities/EQUITY_L.csv"
)

BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = (
    BASE_DIR / "nse_symbols.csv"
)

SNAPSHOT_DIR = (
    BASE_DIR / "universe_snapshots"
)

SNAPSHOT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ==========================================================
# Download Current NSE Universe
# ==========================================================

def refresh_universe() -> pd.DataFrame:
    """
    Download the CURRENT NSE equity universe.

    IMPORTANT:
    This is NOT a historical point-in-time universe.

    Using this universe for historical backtests introduces
    survivorship bias because companies that were delisted,
    merged, failed, etc. may not appear here.
    """

    print(
        "Downloading current NSE stock universe..."
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/138.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(
        NSE_EQUITY_URL,
        headers=headers,
        timeout=20,
    )

    response.raise_for_status()

    df = pd.read_csv(
        StringIO(response.text)
    )

    if "SYMBOL" not in df.columns:
        raise ValueError(
            "NSE universe file does not contain SYMBOL column."
        )

    df = df[
        ["SYMBOL"]
    ].copy()

    df["SYMBOL"] = (
        df["SYMBOL"]
        .astype(str)
        .str.strip()
    )

    df = df[
        df["SYMBOL"] != ""
    ]

    df.drop_duplicates(
        subset=["SYMBOL"],
        inplace=True,
    )

    df["SYMBOL"] = (
        df["SYMBOL"] + ".NS"
    )

    df.sort_values(
        "SYMBOL",
        inplace=True,
    )

    df.reset_index(
        drop=True,
        inplace=True,
    )

    # ------------------------------------------------------
    # Main current-universe cache
    # ------------------------------------------------------

    df.to_csv(
        CSV_PATH,
        index=False,
    )

    # ------------------------------------------------------
    # Save dated point-in-time snapshot
    #
    # These snapshots will gradually allow future
    # point-in-time universe testing.
    # ------------------------------------------------------

    snapshot_path = (
        SNAPSHOT_DIR
        / f"{date.today().isoformat()}.csv"
    )

    df.to_csv(
        snapshot_path,
        index=False,
    )

    print(
        f"Saved {len(df)} current NSE symbols."
    )

    print(
        f"Universe snapshot: {snapshot_path.name}"
    )

    return df


# ==========================================================
# Load Current Universe
# ==========================================================

def load_symbols() -> list[str]:
    """
    Load CURRENT NSE-listed symbols.

    WARNING:
    Historical backtests using this list are
    survivorship-biased.
    """

    if not CSV_PATH.exists():
        refresh_universe()

    df = pd.read_csv(
        CSV_PATH
    )

    if "SYMBOL" not in df.columns:
        raise ValueError(
            "Invalid NSE universe cache."
        )

    return (
        df["SYMBOL"]
        .dropna()
        .astype(str)
        .tolist()
    )


# ==========================================================
# Universe Information
# ==========================================================

def get_universe_mode() -> str:
    """
    Describe the universe methodology used by the backtester.
    """

    return "CURRENT_NSE_UNIVERSE_SURVIVOR_BIASED"