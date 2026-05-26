# 02 · Data Cleaning Notebook — Scaffold

> Copy each cell into a new Jupyter notebook in your repo at
> `notebooks/02-data-cleaning.ipynb`. Adapt to your dataset.
>
> Your final notebook must be runnable end-to-end from a clean kernel.
> The cleaning logic you settle on here gets **promoted** into
> `src/clean_data.py` once it's stable.

---

## Cell 1 — Markdown: title & purpose

```markdown
# Data Cleaning — [primary dataset name]

**Purpose:** apply the design decisions from Session 2's data-quality-audit
to produce a clean, reproducible dataset ready for Phase 4 (modeling).

**Input:** `data/raw/<your-dataset>.csv` (or wherever raw lives)
**Output:** `data/processed/<dataset>-clean.parquet`
**Cleaning log:** `docs/data-cleaning-log.md` (every transform justified)

This notebook is the **exploratory** layer. The stable logic gets promoted
to `src/clean_data.py`.
```

## Cell 2 — Imports & deterministic config

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

RAW_PATH = Path("../data/raw/your-dataset.csv")
OUT_PATH = Path("../data/processed/your-dataset-clean.parquet")
RANDOM_SEED = 42

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

pd.set_option("display.max_columns", 50)
pd.set_option("display.precision", 4)
np.random.seed(RANDOM_SEED)
```

## Cell 3 — Load raw + initial shape check

```python
df_raw = pd.read_csv(RAW_PATH)
print(f"Raw shape: {df_raw.shape}")
df = df_raw.copy()  # never mutate raw
df.head()
```

> **Discipline:** never mutate `df_raw`. Always work on `df`. Lets you
> sanity-check at any point with `df_raw.head()` against `df.head()`.

---

## Task 1 — Select

### Cell 4 — Markdown: selection plan

```markdown
## Task 1: Select

Decide which rows, columns, and time window we keep. Every filter has a
reason. Every reason goes in `data-cleaning-log.md`.

- **Rows kept:** [criterion]
- **Columns kept:** [list]
- **Time window:** [start → end]
- **Spatial extent:** [bounding box / district / etc.]
```

### Cell 5 — Apply selection

```python
COLS_KEEP = ["timestamp", "lat", "lon", "temp_c", "station_id"]
df = df[COLS_KEEP].copy()

before = len(df)
df = df[df["timestamp"].between("2023-06-01", "2023-09-30")]
print(f"Time-window filter: {before:,} → {len(df):,} rows")

print(f"After selection: {df.shape}")
```

---

## Task 2 — Clean

### Cell 6 — Markdown: cleaning plan

```markdown
## Task 2: Clean

For each issue surfaced by `data-quality-audit.md`:
- **Strategy:** drop / impute / flag / model
- **Reversibility:** keep raw column? Derive new?
- **Assertion:** what must be true after cleaning?
```

### Cell 7 — Datetime parsing (every dataset has this issue)

```python
df["timestamp_raw"] = df["timestamp"]
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")

n_failed = df["timestamp"].isna().sum()
print(f"Datetime parse failures: {n_failed:,}")
assert n_failed < len(df) * 0.01, f"Too many parse failures: {n_failed}"
```

> **Why `errors='coerce'`:** turns un-parseable strings into NaT, lets us
> count and decide. Don't use `errors='ignore'` — it silently keeps strings.

### Cell 8 — Type coercion with assertion

```python
df["temp_c"] = pd.to_numeric(df["temp_c"], errors="coerce")

assert df["temp_c"].between(-40, 55).all() | df["temp_c"].isna(), \
    "Temperature outside plausible range — check raw data"
```

### Cell 9 — Missing values: the four-strategy decision

```python
miss = df.isna().mean().sort_values(ascending=False)
print("Missing fractions:")
print(miss[miss > 0])
```

```python
df = df.dropna(subset=["timestamp", "lat", "lon"])

df["temp_c_imputed_flag"] = df["temp_c"].isna()
df["temp_c"] = df.groupby("station_id")["temp_c"].transform(
    lambda s: s.fillna(s.median())
)

print(f"Rows after dropping core nulls: {len(df):,}")
print(f"Imputed temperature values: {df['temp_c_imputed_flag'].sum():,}")
```

> **Discipline:** when you impute, **flag the imputed rows**. The flag is
> the trace. Models trained without knowing which values are real vs
> imputed will overconfide.

### Cell 10 — Outliers: cap, don't drop (usually)

```python
q_lo, q_hi = df["temp_c"].quantile([0.001, 0.999])
df["temp_c_raw"] = df["temp_c"]
df["temp_c"] = df["temp_c"].clip(lower=q_lo, upper=q_hi)
df["temp_c_clipped_flag"] = df["temp_c"] != df["temp_c_raw"]

print(f"Capped at [{q_lo:.2f}, {q_hi:.2f}]")
print(f"Rows clipped: {df['temp_c_clipped_flag'].sum():,}")
```

> **Why cap and flag, not drop:** a sensor reading 87°C is wrong but it's
> evidence of *something* — maybe a sensor failure pattern. Dropping loses
> the signal. Capping + flagging keeps it.

---

## Task 3 — Construct

### Cell 11 — Derived columns (with derivation in the name)

```python
df["hour_of_day"] = df["timestamp"].dt.hour
df["month"] = df["timestamp"].dt.month
df["is_summer"] = df["month"].between(6, 8)

df["temp_anomaly_c_vs_station_median"] = (
    df["temp_c"] - df.groupby("station_id")["temp_c"].transform("median")
)
```

> **Naming rule:** derived columns should make their derivation legible.
> `temp_anomaly_c_vs_station_median` is verbose but unambiguous.
> `temp_anomaly` is not.

---

## Task 4 — Integrate (only if you have multiple sources)

### Cell 12 — Joining heterogeneous sources

```python
df_aux = pd.read_csv("../data/raw/aux-source.csv")
df_aux["timestamp"] = pd.to_datetime(df_aux["timestamp"], utc=True)

before = len(df)
df = df.merge(df_aux, on=["timestamp", "station_id"], how="left", validate="m:1")
print(f"After join: {before:,} → {len(df):,} rows")

assert len(df) == before, "Cardinality changed unexpectedly — check the join"
```

> **The cartesian-join trap:** ALWAYS print row count before and after a
> join. ALWAYS use `validate=` to assert the relationship type.
> A silent 1:m join is the most common silent bug in data prep.

---

## Task 5 — Format

### Cell 13 — Final schema check

```python
FINAL_COLS = [
    "timestamp", "station_id", "lat", "lon",
    "temp_c", "temp_c_imputed_flag", "temp_c_clipped_flag",
    "hour_of_day", "month", "is_summer",
    "temp_anomaly_c_vs_station_median",
]

assert set(FINAL_COLS).issubset(df.columns), \
    f"Missing columns: {set(FINAL_COLS) - set(df.columns)}"

df_out = df[FINAL_COLS].copy()
print(f"Final schema: {df_out.shape}")
df_out.dtypes
```

### Cell 14 — Write parquet output

```python
df_out.to_parquet(OUT_PATH, index=False)
print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size / 1024:.1f} KB)")
```

> **Why parquet:** preserves dtypes (CSV makes everything strings), 5–10×
> smaller than CSV, faster to read. Use CSV only if a non-technical
> reviewer needs to open the file in Excel.

---

## Task 6 — Verify (the back-half discipline)

### Cell 15 — Visualization 1: raw vs cleaned distribution

```python
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(df["temp_c_raw"].dropna(), bins=60, alpha=0.5, label="raw")
ax.hist(df["temp_c"].dropna(), bins=60, alpha=0.7, label="cleaned")
ax.set_xlabel("temperature (°C)")
ax.set_ylabel("count")
ax.legend()
ax.set_title("Raw vs cleaned — distribution shift after cleaning")
plt.tight_layout()
plt.show()
```

### Cell 16 — Visualization 2: coverage over time

```python
fig, ax = plt.subplots(figsize=(12, 4))
df.groupby(df["timestamp"].dt.date).size().plot(ax=ax)
ax.set_title("Records per day after cleaning")
ax.set_ylabel("count")
plt.tight_layout()
plt.show()
```

### Cell 17 — Markdown: what changed

```markdown
## What did cleaning change?

1. **[Transform name]** — [N] rows affected. Why: [reason]. Downstream impact: [effect].
2. **[Transform name]** — [N] rows. Why: [reason]. Downstream impact: [effect].
3. **[Transform name]** — [N] rows. Why: [reason]. Downstream impact: [effect].

**Total rows raw → cleaned:** [N1] → [N2] ([%] retained)
**Total cells changed:** [estimate]

**Implications for the model card (S4):**
- This dataset must NOT be used for: [...]
- Confidence intervals will need to account for: [...]
```

---

## Task 7 — Bridge to the module

### Cell 18 — Markdown: what gets promoted

```markdown
## What gets promoted to `src/clean_data.py`?

Anything that:
- Is repeated logic (same shape twice in this notebook)
- Has a clear input → output contract
- Is stable (you've stopped iterating on it)

This notebook stays as the **exploration**. The module becomes the
**production** path. After promotion, this notebook should call
`from src.clean_data import clean_temperature_dataset` instead of
duplicating the logic.
```

---

## Reproducibility check (do before committing)

1. `Restart kernel` in `02-data-cleaning.ipynb`.
2. `Run all` — every cell should run without error.
3. From terminal: `python src/clean_data.py` — confirm parquet regenerates.
4. Confirm the parquet from the script matches the notebook's output:
   ```python
   import pandas as pd
   pd.testing.assert_frame_equal(
       pd.read_parquet("data/processed/your-dataset-clean.parquet"),
       df_out
   )
   ```
5. Re-run `01-data-profiling.ipynb` on the cleaned data — confirm anomalies resolved.

If any of these fail, the cleaning is not done. Fix before committing.
