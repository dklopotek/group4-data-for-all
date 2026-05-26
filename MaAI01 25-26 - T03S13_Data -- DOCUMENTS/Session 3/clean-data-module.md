# `src/clean_data.py` — Module Template

> Copy this file as the skeleton of `src/clean_data.py` in your repo.
> This is the **promoted** version of your `02-data-cleaning.ipynb` —
> the same logic, lifted out of the notebook into named, typed,
> documented, testable functions.
>
> **Why this matters for arch students:** designing buildings, you don't
> hand a contractor a sketch and say "you'll figure it out." You hand them
> drawings. This module is the drawings version of your cleaning pipeline.
> Future-you, your teammates, and Session 4 all read it.

---

## The full template

Save the block below as `src/clean_data.py`:

```python
"""
clean_data.py — deterministic cleaning pipeline for [dataset name].

Reads raw data from `data/raw/`, applies the cleaning logic settled on in
`notebooks/02-data-cleaning.ipynb`, and writes the cleaned parquet to
`data/processed/`.

Run from project root:
    python src/clean_data.py

Or import individual functions:
    from src.clean_data import clean_temperature_dataset

Cleaning decisions are documented in `docs/data-cleaning-log.md`.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# Paths — relative to project root.
RAW_PATH = Path("data/raw/your-dataset.csv")
OUT_PATH = Path("data/processed/your-dataset-clean.parquet")

# Cleaning constants — every magic number lives here, not inline.
TIME_WINDOW_START = "2023-06-01"
TIME_WINDOW_END = "2023-09-30"
TEMP_PLAUSIBLE_RANGE_C = (-40.0, 55.0)
OUTLIER_QUANTILES = (0.001, 0.999)
MAX_PARSE_FAIL_FRACTION = 0.01

FINAL_COLUMNS = [
    "timestamp",
    "station_id",
    "lat",
    "lon",
    "temp_c",
    "temp_c_imputed_flag",
    "temp_c_clipped_flag",
    "hour_of_day",
    "month",
    "is_summer",
    "temp_anomaly_c_vs_station_median",
]


def select_window(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """Select rows within [start, end] (inclusive) on the timestamp column.

    Args:
        df: Raw dataframe with a 'timestamp' column (string or datetime).
        start: ISO date string (e.g. '2023-06-01').
        end: ISO date string.

    Returns:
        Filtered dataframe. Logs the row count change.

    Example:
        >>> df_summer = select_window(df, '2023-06-01', '2023-09-30')
    """
    before = len(df)
    out = df[df["timestamp"].between(start, end)].copy()
    print(f"select_window: {before:,} → {len(out):,} rows")
    return out


def parse_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Parse timestamp column to UTC datetime, preserving the raw string.

    Adds:
        timestamp_raw — original string preserved for traceability.
        timestamp     — parsed UTC datetime.

    Asserts that fewer than MAX_PARSE_FAIL_FRACTION of timestamps fail.
    """
    out = df.copy()
    out["timestamp_raw"] = out["timestamp"]
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True, errors="coerce")

    n_failed = out["timestamp"].isna().sum()
    if n_failed > len(out) * MAX_PARSE_FAIL_FRACTION:
        raise ValueError(
            f"Too many timestamp parse failures: {n_failed} / {len(out)} "
            f"(>{MAX_PARSE_FAIL_FRACTION:.1%})"
        )
    return out


def impute_temperature_by_station(df: pd.DataFrame) -> pd.DataFrame:
    """Impute missing temperatures with the station's median; flag imputed rows.

    Adds:
        temp_c_imputed_flag — bool, True where the value was imputed.
    """
    out = df.copy()
    out["temp_c_imputed_flag"] = out["temp_c"].isna()
    out["temp_c"] = out.groupby("station_id")["temp_c"].transform(
        lambda s: s.fillna(s.median())
    )
    n = out["temp_c_imputed_flag"].sum()
    print(f"impute_temperature_by_station: imputed {n:,} values")
    return out


def cap_temperature_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Cap temperature at OUTLIER_QUANTILES; preserve raw and flag clipped rows.

    Adds:
        temp_c_raw           — original value preserved (reversibility).
        temp_c_clipped_flag  — bool, True where the value was clipped.
    """
    out = df.copy()
    q_lo, q_hi = out["temp_c"].quantile(list(OUTLIER_QUANTILES))
    out["temp_c_raw"] = out["temp_c"]
    out["temp_c"] = out["temp_c"].clip(lower=q_lo, upper=q_hi)
    out["temp_c_clipped_flag"] = out["temp_c"] != out["temp_c_raw"]
    print(f"cap_temperature_outliers: clipped at [{q_lo:.2f}, {q_hi:.2f}], "
          f"{out['temp_c_clipped_flag'].sum():,} rows")
    return out


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add hour_of_day, month, is_summer derived from the timestamp."""
    out = df.copy()
    out["hour_of_day"] = out["timestamp"].dt.hour
    out["month"] = out["timestamp"].dt.month
    out["is_summer"] = out["month"].between(6, 8)
    return out


def add_temperature_anomaly(df: pd.DataFrame) -> pd.DataFrame:
    """Add temp_anomaly_c_vs_station_median: temp_c minus per-station median."""
    out = df.copy()
    station_median = out.groupby("station_id")["temp_c"].transform("median")
    out["temp_anomaly_c_vs_station_median"] = out["temp_c"] - station_median
    return out


def assert_clean_invariants(df: pd.DataFrame) -> None:
    """Assert every property the downstream pipeline depends on.

    Run this AT THE END of every clean. Failures here mean the cleaning
    invariants have drifted — fix the cleaning before proceeding.
    """
    assert df["timestamp"].notna().all(), "timestamp has nulls after cleaning"
    assert df["temp_c"].between(*TEMP_PLAUSIBLE_RANGE_C).all(), \
        "temp_c outside plausible range"
    assert df["lat"].between(-90, 90).all(), "lat out of range"
    assert df["lon"].between(-180, 180).all(), "lon out of range"
    assert set(FINAL_COLUMNS).issubset(df.columns), \
        f"missing columns: {set(FINAL_COLUMNS) - set(df.columns)}"


def clean_temperature_dataset(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Full cleaning pipeline: raw dataframe → cleaned dataframe.

    Composition order matters — DON'T reorder without re-validating.

    Args:
        df_raw: As-loaded raw dataframe.

    Returns:
        Cleaned dataframe with FINAL_COLUMNS.
    """
    df = (
        df_raw
        .pipe(parse_timestamps)
        .pipe(select_window, TIME_WINDOW_START, TIME_WINDOW_END)
        .pipe(impute_temperature_by_station)
        .pipe(cap_temperature_outliers)
        .pipe(add_temporal_features)
        .pipe(add_temperature_anomaly)
    )
    df = df[FINAL_COLUMNS].copy()
    assert_clean_invariants(df)
    return df


def main() -> None:
    """Run the cleaning pipeline from the command line."""
    print(f"Loading {RAW_PATH}…")
    df_raw = pd.read_csv(RAW_PATH)
    print(f"Raw shape: {df_raw.shape}")

    df_clean = clean_temperature_dataset(df_raw)
    print(f"Cleaned shape: {df_clean.shape}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_parquet(OUT_PATH, index=False)
    print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
```

---

## Why this structure

### One function = one transform
Every function takes a dataframe in, returns a dataframe out. No
side-effects (except `print`). This makes the pipeline composable with
`.pipe(fn)` and unit-testable with `pytest` later.

### Constants at the top
Every magic number is a named constant. If you need to change the time
window, you change `TIME_WINDOW_START` once — not three buried spots.

### Type hints + docstrings
`pd.DataFrame -> pd.DataFrame` is rough but honest. The docstring tells
you what columns are added or removed. Reading this module without
running it should be enough to know what each function does.

### `assert_clean_invariants` at the end
This is the most important function in the file. It encodes every
property your pipeline depends on. If a future you or teammate breaks
something silently, the assert breaks loudly. Defensive programming —
the architectural equivalent of a structural redundancy.

### `if __name__ == "__main__"` guard
Lets the module be both imported (from the notebook) AND run from the
command line (`python src/clean_data.py`). No code duplication.

---

## What to actually adapt

When you copy this template, you'll need to change:

| You change | Why |
|---|---|
| Imports | If you need rasterio, geopandas, xarray for spatial data |
| Constants at top | Time window, plausible ranges, quantiles for YOUR data |
| `FINAL_COLUMNS` | Your output schema |
| Function names + bodies | Your transforms (these are example transforms) |
| `clean_temperature_dataset` | Rename to `clean_<your_dataset>` and change the pipe chain |
| `assert_clean_invariants` | The properties YOUR cleaning must preserve |
| `RAW_PATH` and `OUT_PATH` | Your file paths |

The structure stays. The contents become yours.
