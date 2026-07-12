from pathlib import Path
import pandas as pd

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

    df = pd.read_csv(NSE_EQUITY_URL)

    # Keep only the SYMBOL column
    df = df[["SYMBOL"]].copy()

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    # Convert to Yahoo Finance format
    df["SYMBOL"] = df["SYMBOL"].astype(str) + ".NS"

    # Sort alphabetically
    df.sort_values("SYMBOL", inplace=True)

    # Reset index
    df.reset_index(drop=True, inplace=True)

    # Save locally
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