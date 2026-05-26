# Data Cleaning Log — [primary dataset]

> Every transformation in your cleaning pipeline gets one row in this log.
> Filled in **as you make each decision**, not at the end.
>
> Save as `docs/data-cleaning-log.md` in your repo.
>
> **Why this exists:** in Session 4 you'll write a model card. The model
> card cites this log. In Session 6 you'll build a failure gallery. The
> failure gallery cites this log. In Session 7 a planner will read the
> output and ask "but how do you know?" — this log is your answer.

---

## Dataset under cleaning

- **Dataset:** 
- **Raw path:** `data/raw/...`
- **Clean output:** `data/processed/<dataset>-clean.parquet`
- **Cleaning module:** `src/clean_data.py`
- **Cleaning notebook:** `notebooks/02-data-cleaning.ipynb`
- **Maintainer:** [name]
- **Last updated:** [YYYY-MM-DD]

---

## Pipeline summary

- **Raw rows:** [N]
- **Cleaned rows:** [M]
- **Retention:** [M/N as %]
- **Columns added:** [count]
- **Columns dropped:** [count]
- **Wall-clock time on standard laptop:** [seconds]

---

## The transforms — every one logged

For each transform, fill in all five columns. If you can't fill a column,
you don't yet understand the transform. Stop and read the code.

### Format per row

> **Transform:** [name from `src/clean_data.py`]
> - **What it changed:** [rows / cells / columns affected, with counts]
> - **Why this and not the alternative:** [reasoning — what was the choice space, what did you pick, why]
> - **Downstream effect:** [what does this mean for the model in S4 / failure gallery in S6 / output in S7]
> - **Reversibility:** [yes — raw column preserved as `<col>_raw` / no — raw is lost, here's why that's OK]
> - **Assertion that proves it worked:** [code snippet or description]

---

### Example — one filled row to model after

> **Transform:** `parse_timestamps`
> - **What it changed:** Parsed 487,213 string timestamps to UTC datetime. 142 strings (0.029%) failed parsing — fewer than the 1% MAX_PARSE_FAIL_FRACTION threshold so the run continues. Original strings preserved in `timestamp_raw`.
> - **Why this and not the alternative:** Considered (a) `errors='ignore'` — rejected because it silently keeps strings; (b) drop NaT rows immediately — rejected because the failure pattern is itself diagnostic; (c) `errors='coerce'` and inspect — chosen because we want to surface the parse failures for the cleaning log.
> - **Downstream effect:** All temporal joins, resampling, and feature engineering depend on `timestamp` being timezone-aware UTC datetime. Models in S4 will trust this column.
> - **Reversibility:** Yes — `timestamp_raw` preserves the original string for any future debugging.
> - **Assertion that proves it worked:** `assert df['timestamp'].notna().all()` after later cleaning steps drop the parse failures.

---

### Your transforms

> **Transform 1:** [...]
> - **What it changed:** 
> - **Why this and not the alternative:** 
> - **Downstream effect:** 
> - **Reversibility:** 
> - **Assertion that proves it worked:** 

> **Transform 2:** [...]
> - **What it changed:** 
> - **Why this and not the alternative:** 
> - **Downstream effect:** 
> - **Reversibility:** 
> - **Assertion that proves it worked:** 

> **Transform 3:** [...]
> - **What it changed:** 
> - **Why this and not the alternative:** 
> - **Downstream effect:** 
> - **Reversibility:** 
> - **Assertion that proves it worked:** 

*(continue for every transform in your pipeline — typically 5–10)*

---

## What we did NOT clean — and why

Sometimes the right call is to leave bad data in the dataset and document
its badness. List those here.

| Issue | Why we left it | What downstream needs to know |
|---|---|---|
| | | |
| | | |

---

## Cumulative effect — raw vs cleaned (one paragraph)

After all transforms, the dataset has changed in the following ways
(write this paragraph after the pipeline is stable):

> Of [N] raw rows, [M] survived ([M/N as %]). The cleaning preserved
> [list the design properties — geographic coverage, temporal density,
> station representation, etc.] but reduced [list the trade-offs — e.g.
> outlier extremes capped, ~3% of rows imputed]. The cleaned dataset is
> suitable for [list the modeling tasks it supports]. It is **not** suitable
> for [list the tasks it can't support — e.g. anomaly detection at the
> raw extremes, since those have been clipped].

---

## Sign-off

The pipeline runs from raw to clean reproducibly:

- [ ] `python src/clean_data.py` produces `data/processed/<dataset>-clean.parquet`
- [ ] Re-running on the same input produces an identical parquet (deterministic)
- [ ] `01-data-profiling.ipynb` re-run on the cleaned data shows anomalies resolved
- [ ] All assertions in `assert_clean_invariants` pass
- [ ] This log has one entry per transform

**Cleaned by:** [team]
**Reviewed by another team:** [name of reviewer team] on [date]
**Reviewer notes:** [link to peer-review section or a few bullets]
