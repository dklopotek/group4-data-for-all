# Session 3 Templates — Data Preparation (CRISP-DM Phase 3)

Drop these into your team repo at the start of Session 3. By 4 PM today,
every file should be filled in and committed.

> **The frame for today:** cleaning is not janitor work. Every transformation
> is a design decision with downstream consequences. Document them as
> rigorously as you'd document a wall section.

---

## Where to put them in your repo

```
your-repo/
├── docs/
│   ├── problem-brief.md                (S1)
│   ├── problem-brief-v2.md             (S2)
│   ├── data-source-inventory.md        (S2)
│   ├── datasheets/<slug>.md            (S2 — UPDATE section 4 today)
│   ├── data-quality-audit.md           (S2)
│   ├── data-to-decision-map.md         (S2)
│   ├── system-sketch-v0.md             (S2)
│   ├── output-sketch-v0.md             (S2)
│   ├── data-cleaning-log.md            (NEW — every transform justified)
│   └── pipeline-architecture-v1.md     (NEW — system sketch evolved)
├── notebooks/
│   ├── 01-data-profiling.ipynb         (S2 — RE-RUN on cleaned data today)
│   └── 02-data-cleaning.ipynb          (NEW — exploratory cleaning)
├── src/
│   └── clean_data.py                   (NEW — promoted module)
├── data/
│   ├── raw/                            (gitignored — don't commit large files)
│   └── processed/
│       └── <dataset>-clean.parquet     (NEW — deterministic output)
└── requirements.txt                    (UPDATE — pin actual versions used)
```

---

## The 9 artifacts you owe by 4 PM

| # | File | Why it exists |
|---|---|---|
| 1 | `notebooks/02-data-cleaning.ipynb` | Exploratory cleaning — the messy work, raw → clean, with thinking visible |
| 2 | `src/clean_data.py` | The **promoted module** — repeated logic lifted out of the notebook into named functions |
| 3 | `data/processed/<dataset>-clean.parquet` | The **deterministic output** — the contract artifact downstream sessions consume |
| 4 | `docs/data-cleaning-log.md` | Every transformation with a one-line justification (the design diary) |
| 5 | `datasheets/<slug>.md` | Section 4 "Preprocessing & cleaning" filled with what *you* did |
| 6 | `notebooks/01-data-profiling.ipynb` | **Re-run on cleaned data** — confirms fixes landed; shows raw vs cleaned |
| 7 | ≥1 documented function | Docstring + types + ≥1 assertion (defensive programming) |
| 8 | `requirements.txt` | Pinned versions actually used (not `pandas` — `pandas==2.2.3`) |
| 9 | `docs/pipeline-architecture-v1.md` | System sketch evolved with **real boxes** now that cleaning is real |

---

## The frame — cleaning is design

You'd never accept a wall section that said "concrete, somehow." You'd
demand: which mix, what depth, why this and not the alternative. Same
applies to data.

For every transformation in your pipeline, you should be able to answer:

1. **What did this transform change?**
2. **Why this transform and not the alternative?**
3. **What downstream effect does it have?**
4. **What does it preserve from raw — i.e. is it reversible?**

If you can't answer all four, the transform is undocumented. The cleaning
log is where you answer them.

---

## The phase 3 spine — five tasks

1. **Select** — which rows, which columns, which time window. Every filter has a reason; every reason gets logged.
2. **Clean** — handle missing values, outliers, type errors, datetime parsing. Reversibility matters: keep raw, derive cleaned.
3. **Construct** — derive new columns (NDVI, heat index, hour-of-day, season). Naming carries derivation.
4. **Integrate** — join heterogeneous sources. Keys, conflicts, cardinality. Always print the row count after a join.
5. **Format** — final schema, units in column names, parquet over CSV for non-trivial data.

Cross-cutting moves applied to all five tasks:
- **Notebook → module** — promote repeated logic into named, documented, typed functions.
- **Reversibility** — keep raw column, derive cleaned. Don't overwrite.
- **Assertions** — at least one `assert df['col'].between(min, max).all()` per cleaning function.
- **Reproducibility** — pipeline runs from scratch in a single command, deterministic output.
- **The LLM working loop** — specify, direct, **verify (read every line)**, iterate.

---

## What Session 3 does NOT do

To protect the phase boundary in both directions:

- ❌ Train any model (Phase 4 / Session 4)
- ❌ Compute model metrics (Phase 4 / Session 4)
- ❌ Synthetic data generation (Phase 5 / Session 5)
- ❌ Stress-test or build a failure gallery (Phase 6 / Session 6)
- ❌ Build the final dashboard / UI (Phase 7 / Session 7)

Cleaning ends when raw → clean is reproducible from one command and the
result has been re-profiled. Not before.

---

## The pre-commit ritual (every team, by 3:55 PM)

1. **Restart kernel** in `02-data-cleaning.ipynb`.
2. **Run all** — confirm no errors.
3. **Run** `python src/clean_data.py` — confirm the parquet output regenerates identically.
4. **Confirm** `data/processed/<dataset>-clean.parquet` matches what the notebook produced.
5. **Re-run** `01-data-profiling.ipynb` on the cleaned output — confirm anomalies are now resolved (or explicitly documented).
6. `git log --oneline` — show the commits since 1:00 PM.
7. Push.

If any of those six steps fail, that's the fix-list before next Tuesday.

---

## Reading order — fill the templates in this order

1. **`02-data-cleaning-scaffold.md`** — copy structure into your notebook, start cleaning your dataset
2. **`function-design-checklist.md`** — read before promoting any code into `src/clean_data.py`
3. **`clean-data-module.md`** — copy as the skeleton of `src/clean_data.py`
4. **`data-cleaning-log.md`** — log every transform as you make it (don't batch this at the end)
5. **`reproducibility-checklist.md`** — work through before committing
6. **`pipeline-architecture-v1.md`** — fill once your cleaning is stable
