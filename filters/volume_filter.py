from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class VolumeFilterResult:
    """
    Result returned after checking one trade against
    the volume/liquidity filtration rules.
    """

    passed: bool

    signal_date: pd.Timestamp | None

    current_volume: float | None

    average_volume: float | None

    relative_volume: float | None

    adtv: float | None

    reasons: tuple[str, ...]


def _normalise_timestamp(
    value,
) -> pd.Timestamp | None:
    """
    Convert dates into timezone-free normalized timestamps.
    """

    try:
        timestamp = pd.Timestamp(value)

    except (TypeError, ValueError):
        return None

    if pd.isna(timestamp):
        return None

    if timestamp.tzinfo is not None:

        timestamp = timestamp.tz_localize(
            None
        )

    return timestamp.normalize()


def _date_series(
    df: pd.DataFrame,
) -> pd.Series:
    """
    Return normalized dates regardless of whether
    Date is a column or dataframe index.
    """

    if "Date" in df.columns:

        values = pd.to_datetime(
            df["Date"],
            errors="coerce",
        )

        series = pd.Series(
            values,
            index=df.index,
        )

    else:

        values = pd.to_datetime(
            df.index,
            errors="coerce",
        )

        series = pd.Series(
            values,
            index=df.index,
        )

    try:

        series = series.dt.tz_localize(
            None
        )

    except (
        TypeError,
        AttributeError,
    ):

        pass

    return series.dt.normalize()


def _first_existing_column(
    columns: Iterable[str],
    candidates: Iterable[str],
) -> str | None:
    """
    Find the first candidate column that exists.
    """

    existing = set(columns)

    for column_name in candidates:

        if column_name in existing:
            return column_name

    return None


def evaluate_volume_filter(
    price_data: pd.DataFrame,
    signal_date,
    *,
    lookback: int = 20,
    min_relative_volume: float = 1.5,
    min_adtv: float = 2_00_00_000,
) -> VolumeFilterResult:
    """
    Evaluate ONE historical trade.

    Rules:

    1. Current signal candle volume must be >=
       min_relative_volume * previous lookback average.

    2. Previous lookback average daily traded value
       must be >= min_adtv.

    This function does NOT use future candles.
    """

    target_date = _normalise_timestamp(
        signal_date
    )

    if target_date is None:

        return VolumeFilterResult(

            passed=False,

            signal_date=None,

            current_volume=None,

            average_volume=None,

            relative_volume=None,

            adtv=None,

            reasons=(
                "INVALID_SIGNAL_DATE",
            ),
        )

    average_column = (
        f"AvgVolume{lookback}"
    )

    relative_column = (
        f"RelativeVolume{lookback}"
    )

    adtv_column = (
        f"ADTV{lookback}"
    )

    required_columns = {

        "Volume",

        average_column,

        relative_column,

        adtv_column,
    }

    missing_columns = (
        required_columns
        - set(price_data.columns)
    )

    if missing_columns:

        raise ValueError(

            "Volume metrics have not been "
            "calculated. Missing columns: "
            f"{sorted(missing_columns)}"
        )

    dates = _date_series(
        price_data
    )

    matching_rows = price_data.loc[
        dates == target_date
    ]

    if matching_rows.empty:

        return VolumeFilterResult(

            passed=False,

            signal_date=target_date,

            current_volume=None,

            average_volume=None,

            relative_volume=None,

            adtv=None,

            reasons=(
                "SIGNAL_DATE_NOT_FOUND",
            ),
        )

    row = matching_rows.iloc[-1]

    current_volume = pd.to_numeric(
        row["Volume"],
        errors="coerce",
    )

    average_volume = pd.to_numeric(
        row[average_column],
        errors="coerce",
    )

    relative_volume = pd.to_numeric(
        row[relative_column],
        errors="coerce",
    )

    adtv = pd.to_numeric(
        row[adtv_column],
        errors="coerce",
    )

    rejection_reasons = []

    # ------------------------------------------------------
    # Not enough candles available
    # ------------------------------------------------------

    if (
        pd.isna(average_volume)
        or pd.isna(relative_volume)
        or pd.isna(adtv)
    ):

        rejection_reasons.append(
            "INSUFFICIENT_VOLUME_HISTORY"
        )

    else:

        # --------------------------------------------------
        # Relative Volume Rule
        # --------------------------------------------------

        if (
            float(relative_volume)
            < min_relative_volume
        ):

            rejection_reasons.append(
                "LOW_RELATIVE_VOLUME"
            )

        # --------------------------------------------------
        # Liquidity / ADTV Rule
        # --------------------------------------------------

        if float(adtv) < min_adtv:

            rejection_reasons.append(
                "LOW_ADTV"
            )

    return VolumeFilterResult(

        passed=(
            len(rejection_reasons)
            == 0
        ),

        signal_date=target_date,

        current_volume=(
            None
            if pd.isna(current_volume)
            else float(current_volume)
        ),

        average_volume=(
            None
            if pd.isna(average_volume)
            else float(average_volume)
        ),

        relative_volume=(
            None
            if pd.isna(relative_volume)
            else float(relative_volume)
        ),

        adtv=(
            None
            if pd.isna(adtv)
            else float(adtv)
        ),

        reasons=tuple(
            rejection_reasons
        ),
    )


def filter_candidate_trades(
    trades: pd.DataFrame,
    price_data: pd.DataFrame,
    *,
    lookback: int = 20,
    min_relative_volume: float = 1.5,
    min_adtv: float = 2_00_00_000,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:
    """
    Apply volume filtration to every candidate trade.

    Returns:

        passed_trades,
        rejected_trades
    """

    if trades.empty:

        return (
            trades.copy(),
            trades.copy(),
        )

    # ------------------------------------------------------
    # TradePilot currently primarily uses Entry Date.
    # Other possible names are supported for future use.
    # ------------------------------------------------------

    date_column = _first_existing_column(

        trades.columns,

        (
            "Golden Cross Date",
            "Cross Date",
            "Signal Date",
            "Entry Date",
        ),
    )

    if date_column is None:

        raise ValueError(

            "Could not determine signal date. "
            "Expected one of these columns: "
            "Golden Cross Date, Cross Date, "
            "Signal Date, Entry Date"
        )

    passed_rows = []

    rejected_rows = []

    # ------------------------------------------------------
    # Check each Golden Cross trade
    # ------------------------------------------------------

    for _, trade in trades.iterrows():

        result = evaluate_volume_filter(

            price_data,

            trade[date_column],

            lookback=lookback,

            min_relative_volume=(
                min_relative_volume
            ),

            min_adtv=min_adtv,
        )

        trade_data = trade.to_dict()

        trade_data.update(

            {

                "Volume Signal Date":
                    result.signal_date,

                "Current Volume":
                    result.current_volume,

                f"{lookback}D Avg Volume":
                    result.average_volume,

                "Relative Volume":
                    result.relative_volume,

                f"ADTV {lookback}D":
                    result.adtv,

                "Volume Filter Passed":
                    result.passed,

                "Filter Rejection Reasons":
                    "|".join(
                        result.reasons
                    ),
            }
        )

        if result.passed:

            passed_rows.append(
                trade_data
            )

        else:

            rejected_rows.append(
                trade_data
            )

    # ------------------------------------------------------
    # Convert results back into DataFrames
    # ------------------------------------------------------

    passed_df = pd.DataFrame(
        passed_rows
    )

    rejected_df = pd.DataFrame(
        rejected_rows
    )

    return (
        passed_df,
        rejected_df,
    )