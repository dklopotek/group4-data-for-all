# 05 · Evaluation Notebook — Scaffold

> Copy each cell into a new Jupyter notebook in your repo at
> `notebooks/05-evaluation.ipynb`. Adapt to your dataset and your track.
>
> Your final notebook must be runnable end-to-end from a clean kernel,
> and every number it prints must match `docs/evaluation-report.md`.
>
> The notebook is forked: cells **1–4** are shared, then go to the
> **Track A** cells (you built a model) or the **Track B** cells (you
> built on existing systems & data and drew conclusions). Cells at the
> end are shared again.

---

## Cell 1 — Markdown: title & purpose

```markdown
# Evaluation — [project name]

**Purpose:** judge what we built in Sessions 1–4 against the success
criteria from the Session 1 problem brief. Produce a defensible verdict —
deploy, iterate, or stop — with the evidence behind it.

**Track:** [A — model · or · B — conclusions from existing systems/data]

**Inputs:**
- `docs/problem-brief.md` — the success criteria we grade against
- Track A: `models/baseline.joblib`, `data/processed/<dataset>-test.parquet`
- Track B: the existing data / system outputs we drew conclusions from,
  and a held-out / out-of-sample slice we did NOT look at while concluding

**Outputs:**
- `docs/evaluation-report.md` — the verdict
- `docs/failure-gallery.md` (A) / `docs/validity-audit.md` (B)
- `docs/evaluation-log.md` — every test we ran
```

## Cell 2 — Imports & deterministic config

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

# Track A only — loaded in Cell A1.
# import joblib
# from sklearn.metrics import mean_absolute_error, r2_score
```

## Cell 3 — Markdown: the success criteria (from Session 1)

```markdown
## The bar we set in Session 1

Copy the success criteria verbatim from `docs/problem-brief.md`. If they
were vague, write the sharpest honest version now — and note that the
brief was vague (that's a finding for the report).

| # | Success criterion (from S1) | How it's measured |
|---|---|---|
| 1 | [e.g. "predict next-day PM2.5 within ±3 µg/m³ for the planner"] | [test MAE ≤ 3.0] |
| 2 | [e.g. "beat the city's current rule-of-thumb"] | [vs persistence / heuristic] |
| 3 | [e.g. "usable on Thursday before the weekly meeting"] | [runs in < 1 min, output legible] |
```

## Cell 4 — Task 1: results-vs-criteria table (BOTH TRACKS)

```python
# One row per S1 criterion. Fill `result` from the evidence below.
# verdict ∈ {"met", "partial", "missed"}.
criteria = pd.DataFrame([
    {"criterion": "criterion 1", "target": "...", "result": "...", "verdict": "..."},
    {"criterion": "criterion 2", "target": "...", "result": "...", "verdict": "..."},
    {"criterion": "criterion 3", "target": "...", "result": "...", "verdict": "..."},
])
print(criteria.to_markdown(index=False))
```

> **Discipline:** this table goes straight into the evaluation report,
> section 2. A criterion you can't fill is a criterion you can't claim.

---
---

# TRACK A — you built a model

> Skip this whole block if you're Track B.

## Cell A1 — Load the locked model + the sacred test set

```python
import joblib
from sklearn.metrics import mean_absolute_error, r2_score

model = joblib.load("../models/baseline.joblib")
test = pd.read_parquet("../data/processed/your-dataset-test.parquet")

TARGET = "temp_c"
FEATURE_COLS = ["hour_of_day", "month", "lat", "lon",
                "temp_anomaly_c_vs_station_median"]

X_test, y_test = test[FEATURE_COLS], test[TARGET]
y_pred = model.predict(X_test)
print(f"test rows: {len(test):,}")
```

> The test number was the headline in S4. Evaluation starts where that
> number ends — by asking where the average is hiding a failure.

## Cell A2 — Per-segment error analysis (where does it break?)

```python
# Replace `segment` with the factor from your model card section 3.
segment = test["station_id"]
err = y_test.values - y_pred

report = (pd.DataFrame({"err": err, "segment": segment})
          .groupby("segment")["err"]
          .agg(mae=lambda e: e.abs().mean(), bias="mean", n="size")
          .sort_values("mae", ascending=False))
print(report)   # the worst segment is your headline — not the overall MAE
```

> The worst rows here become the first entries in `failure-gallery.md`.

## Cell A3 — Stress tests (break it on purpose)

```python
def drop_a_sensor(X):       X = X.copy(); X["temp_anomaly_c_vs_station_median"] = np.nan; return X
def shift_distribution(X):  X = X.copy(); X["temp_c"] = X["temp_c"] + 5 if "temp_c" in X else X; return X
def inject_missing(X):      X = X.copy(); X.loc[X.sample(frac=0.2, random_state=RANDOM_SEED).index, "lat"] = np.nan; return X
def extreme_inputs(X):      X = X.copy(); X["month"] = 12; return X   # a season barely in training

TOL = 3.0  # the S1 error budget
for shift in [drop_a_sensor, shift_distribution, inject_missing, extreme_inputs]:
    try:
        mae = mean_absolute_error(y_test, model.predict(shift(X_test)))
        flag = "OK" if mae < TOL else "DEGRADED"
    except Exception as e:
        mae, flag = float("nan"), f"CRASHED · {type(e).__name__}"
    print(f"{shift.__name__:18s}  MAE {mae:.2f}  [{flag}]")
```

> A crash is also a finding — a model that errors on a missing sensor is
> not deployable. Log every row of this in `evaluation-log.md`.

## Cell A4 — Confidence / interval (carried from S4)

```python
trees = model.named_steps["model"].estimators_
all_preds = np.stack([t.predict(X_test) for t in trees])
y_lo, y_hi = np.percentile(all_preds, 5, axis=0), np.percentile(all_preds, 95, axis=0)
coverage = float(np.mean((y_test.values >= y_lo) & (y_test.values <= y_hi)))
print(f"90% interval coverage on test: {coverage:.2%}   (aim ≥ 85%)")
```

## Cell A5 — Compared to what (the baseline / status quo)

```python
# The honest framing: model vs the alternative the decision-maker uses today.
baseline_mae = mean_absolute_error(y_test, np.full_like(y_test, y_test.mean()))  # or persistence / heuristic
model_mae = mean_absolute_error(y_test, y_pred)
print(f"model MAE      {model_mae:.2f}")
print(f"baseline MAE   {baseline_mae:.2f}")
print(f"improvement    {(baseline_mae - model_mae) / baseline_mae:.1%}")
```

> Jump to **Cell S1 — verdict**.

---
---

# TRACK B — conclusions from existing systems & data

> Skip this whole block if you're Track A.

## Cell B1 — State the claim as one falsifiable sentence

```markdown
## The claim under evaluation

> [One sentence a reviewer could prove wrong. Example: "Manhattan census
> tracts with < 10% tree canopy run ≥ 3 °C hotter in summer surface
> temperature than tracts with > 30% canopy."]

- **The decision it serves:** [who acts, and how]
- **The exact evidence:** [which data, which comparison, which number]
```

## Cell B2 — Load the data and reproduce the headline number

```python
df = pd.read_parquet("../data/processed/your-analysis.parquet")  # or read your existing-system export

# Reproduce the exact comparison your conclusion rests on.
low_canopy  = df[df["canopy_pct"] < 10]["lst_c"]
high_canopy = df[df["canopy_pct"] > 30]["lst_c"]
headline = low_canopy.mean() - high_canopy.mean()
print(f"headline effect: {headline:+.2f} °C  (n_low={len(low_canopy)}, n_high={len(high_canopy)})")
```

## Cell B3 — Threats to validity (rule each one out, or admit it)

```python
# i · confounding — does a third variable drive both?
#     e.g. control for distance-to-water / building density and re-check.
controlled = (df.assign(bucket=pd.qcut(df["dist_to_water_m"], 4))
                .groupby("bucket", observed=True)
                .apply(lambda g: g[g.canopy_pct<10].lst_c.mean() - g[g.canopy_pct>30].lst_c.mean()))
print("effect within distance-to-water quartiles (confounding check):")
print(controlled)

# ii · selection bias — who/what is missing from this data? (write it in the audit)
# iii · spurious — was the question fixed before you saw the answer? (state it)
# iv · cherry-picking — report the cuts that did NOT support the claim too
```

## Cell B4 — Robustness / sensitivity (does it survive a different cut?)

```python
def effect_on(sub):
    return sub[sub.canopy_pct<10].lst_c.mean() - sub[sub.canopy_pct>30].lst_c.mean()

cuts = {
    "all":            df,
    "exclude_2020":   df[df.year != 2020],
    "daytime_only":   df[df.is_daytime],
    "alt_threshold":  df.assign(),   # e.g. <15% vs >25% — redefine the bands
}
for name, sub in cuts.items():
    e = effect_on(sub)
    print(f"{name:16s}  effect {e:+.2f} °C   [{'holds' if np.sign(e)==np.sign(headline) else 'FLIPS'}]")
```

> If the effect flips on a reasonable cut, it was never robust — that is
> the central finding of your `validity-audit.md`.

## Cell B5 — Out-of-sample check (the Track-B "test set")

```python
# The slice you did NOT look at while forming the conclusion.
# Does the finding hold there too?
holdout = pd.read_parquet("../data/processed/your-analysis-holdout.parquet")
print(f"out-of-sample effect: {effect_on(holdout):+.2f} °C  (n={len(holdout)})")
```

> Jump to **Cell S1 — verdict**.

---
---

# SHARED — review the process & reach the verdict

## Cell S1 — Markdown: the verdict

```markdown
## The verdict

- **Result vs criteria:** [met X of N · which ones partial/missed]
- **Where it fails:** [worst segment (A) / threat not fully ruled out (B)]
- **Compared to what:** [the alternative, and by how much]
- **Confidence:** [interval/spread (A) · robustness (B)] → [high / medium / low]
- **Recommendation:** [DEPLOY / ITERATE / STOP] — because [one sentence]
- **What we are NOT claiming:** [≥ 3 things]
```

## Cell S2 — Review the process (the honest error audit)

```markdown
## What would we redo if we started over Monday?

- **Weakest link:** the single decision the result is most fragile to.
- **The shortcut:** where we traded rigour for time, knowingly.
- **Untested assumption:** what we took on faith from an earlier session.
- **The thing we avoided looking at:** the slice we suspected was bad.
  (Go look at it now — before the pair-review does.)
```

---

## Reproducibility check (before committing)

1. `Restart kernel` in `05-evaluation.ipynb`.
2. `Run all` — every cell runs without error, top to bottom.
3. Open `docs/evaluation-report.md`. Every number in it appears,
   identical, in the notebook output. If not, the report is fiction —
   fix it before the verdict.
4. Re-read "what we are NOT claiming." Can you list three without
   checking?
5. Read the verdict sentence aloud. It's what you'll open your S7
   presentation with — practise it now.

If any step fails, the evaluation is not done.
