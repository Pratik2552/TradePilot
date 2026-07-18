from pathlib import Path
import pandas as pd
import requests
from io import StringIO

# URL of the latest NSE Equity Securities CSV
NSE_EQUITY_URL = (
    "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
)

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "nse_symbols.csv"


def refresh_universe() -> pd.DataFrame:
    """
    Downloads the latest NSE equity list and saves it locally.
    """

    print("Downloading latest NSE stock universe...")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0.0.0 Safari/537.36"
        )
    }
    print("Step 1 - Sending request...")


    response = requests.get(
        NSE_EQUITY_URL,
        headers=headers,
        timeout=20,
    )
    print("Step 2 - Request completed.")

    response.raise_for_status()

    print("Step 3 - Status OK.")

    df = pd.read_csv(StringIO(response.text))

    df = df[["SYMBOL"]].copy()

    df.drop_duplicates(inplace=True)

    df["SYMBOL"] = df["SYMBOL"].astype(str) + ".NS"

    df.sort_values("SYMBOL", inplace=True)

    df.reset_index(drop=True, inplace=True)

    df.to_csv(CSV_PATH, index=False)

    print(f"Saved {len(df)} symbols.")

    return df


def load_symbols() -> list[str]:
    """
    Loads NSE symbols from the local CSV.
    """

    if not CSV_PATH.exists():
        refresh_universe()

    df = pd.read_csv(CSV_PATH)

    return df["SYMBOL"].tolist()