# Reproducibility Checklist

> Before you commit and call cleaning "done", run through this checklist.
> If any item fails, the cleaning is not done.
>
> Use as a working reference; not a committed artifact.

---

## The bar

**Reproducibility means:** a teammate clones your repo on a new machine,
follows your README, and produces the same `data-clean.parquet` you
produced — byte-for-byte (or row-for-row at minimum).

If that's not true, the cleaning isn't done. It's a sketch of cleaning.

---

## The five disciplines

### 1. Determinism

- [ ] Random seed is set in `src/clean_data.py` and used everywhere
      randomness enters the pipeline (`np.random.seed`, `random.seed`,
      `df.sample(random_state=...)`).
- [ ] Sort order is deterministic. After any `groupby`, `sort_values` by
      a stable key. Don't rely on insertion order.
- [ ] No `datetime.now()` or `time.time()` in cleaning logic — these
      poison reproducibility.
- [ ] No reads from environment variables that change between machines
      (no `os.environ["USER"]` etc.).

### 2. Pinned dependencies

- [ ] `requirements.txt` pins exact versions: `pandas==2.2.3`, not `pandas`.
- [ ] Generate by running `pip freeze > requirements.txt` AFTER your
      pipeline runs cleanly.
- [ ] Note your Python version in `README.md` (e.g. "Python 3.11.x").

### 3. Path discipline

- [ ] All paths are constants at the top of `src/clean_data.py` —
      `RAW_PATH`, `OUT_PATH`. Never inline `"data/raw/whatever.csv"`
      mid-function.
- [ ] All paths use `pathlib.Path`, not `os.path.join` strings.
- [ ] All paths are relative to the project root, not absolute.
      `data/raw/x.csv` — yes. `/Users/me/Documents/.../x.csv` — no.

### 4. The "runs from scratch" test

Open a terminal in your project root and run, in order:

```bash
# 1. Fresh virtual env
python -m venv .venv
source .venv/bin/activate

# 2. Install deps from your requirements.txt
pip install -r requirements.txt

# 3. Confirm raw data is present (or downloadable)
ls data/raw/

# 4. Run the pipeline
python src/clean_data.py

# 5. Confirm the output exists
ls -lh data/processed/

# 6. Bonus — confirm the output matches an earlier run (if you saved one)
# diff <(parquet-tools head data/processed/x-clean.parquet) earlier.txt
```

- [ ] Steps 1–5 complete without error.
- [ ] Step 5 takes less than [N] minutes (you decide N — write it in README).
- [ ] If you ran the pipeline yesterday, today's output is identical.

### 5. Documentation as artifact

- [ ] `README.md` has a "How to reproduce" section with the exact commands
      above.
- [ ] The cleaning log (`docs/data-cleaning-log.md`) has one entry per
      transform.
- [ ] The pipeline architecture (`docs/pipeline-architecture-v1.md`) shows
      every implemented box with a file path.
- [ ] The datasheet's preprocessing section (`datasheets/<slug>.md`
      section 4) is filled with what YOU did, not what the dataset
      creators did.

---

## The pre-commit ritual

Right before you push:

1. **Restart kernel** in `02-data-cleaning.ipynb`.
2. **Run all** — every cell runs, no errors.
3. **Run** `python src/clean_data.py` from terminal — no errors.
4. **Confirm** that the output of step 2 (notebook) and step 3 (script)
   produce the same parquet.
5. **Re-run** `01-data-profiling.ipynb` on the cleaned data — anomalies
   are resolved or explicitly documented.
6. **Inspect** `git status` — only the files you intended to change are
   changed.
7. **Commit** with a message that says what changed and why
   (`"add datetime parsing — preserve raw in timestamp_raw"`, not
   `"updates"`).

---

## What to NOT commit

- [ ] Raw data files larger than 5 MB go in `.gitignore`.
- [ ] Cleaned outputs (`data/processed/*.parquet`) — your call: commit
      if <10 MB and useful as a "freeze point", otherwise gitignore.
- [ ] Virtual env directory (`.venv/`).
- [ ] `__pycache__/`, `.ipynb_checkpoints/`.
- [ ] Anything with credentials or API keys.

If a teammate clones the repo and can't get their copy of the raw data,
your README needs a "Get the data" section explaining how to fetch or
generate it.

---

## When the checklist fails

Any failure is a real failure. Don't push. Common causes and fixes:

| Failure | Cause | Fix |
|---|---|---|
| Different output two runs in a row | Random ordering somewhere | Add `random_state=` everywhere; sort after groupby |
| "Module not found" on a teammate's machine | Missing pin | `pip freeze > requirements.txt` and recommit |
| Notebook runs but script crashes | Notebook has hidden state | Restart kernel + run all reveals the truth |
| Parquet has different row count two runs in a row | `dropna` order matters or non-deterministic join | Sort before drop; use `validate=` on merges |
| Path errors on different machine | Absolute path in code | Convert to `pathlib.Path` relative to project root |
