# Function Design Checklist

> Before you commit a function to `src/clean_data.py` (or any module), it
> passes this checklist. No exceptions.
>
> Save as a working reference; not a committed artifact.

---

## The minimum bar — every function

A function ready to commit answers all eight questions in writing,
inside the function itself or its docstring:

- [ ] **Does the function name say what it does as a verb?**
  `parse_timestamps`, `cap_outliers`, `compute_ndvi` — good. `process`,
  `do_thing`, `handler` — no. Verbs only.

- [ ] **Does the function do ONE thing?**
  If you're tempted to use "and" in the docstring summary, split.
  `clean_and_save` is two functions: `clean` and `save`.

- [ ] **Is it pure where possible?** No printing in helpers; no global state
  mutation. Side effects (file I/O, `print`) live at the boundaries
  (`main`, `load_*`, `save_*`).

- [ ] **Does it have type hints?**
  `pd.DataFrame -> pd.DataFrame` is a fine starting point. Even imperfect
  types document intent.

- [ ] **Does it have a docstring with `Args` and `Returns`?**
  Three lines minimum. The first line is a one-sentence summary; the rest
  describe inputs and outputs.

- [ ] **Does the docstring include an example?**
  At least one `>>>` line showing how to call it. This forces you to
  actually run it.

- [ ] **Does it have at least one assertion?**
  Either inside the function (input validation) or in the calling
  pipeline (`assert_clean_invariants`). Assertions are checkpoints.

- [ ] **Is it testable without a real dataset?**
  If you'd need 100 GB of raw data to test it, the function is doing too
  much. Refactor.

---

## The structure — copy this template

```python
def transform_name(
    df: pd.DataFrame,
    threshold: float = 0.5,
) -> pd.DataFrame:
    """One-sentence summary in the imperative.

    A short paragraph explaining the design decision: why this transform,
    what alternatives were considered, what's the cost.

    Args:
        df: Dataframe with columns [list required columns].
        threshold: What this parameter controls and its valid range.

    Returns:
        The transformed dataframe with [list added/changed columns].

    Raises:
        ValueError: If the input is missing required columns.

    Example:
        >>> df_clean = transform_name(df_raw, threshold=0.7)
        >>> df_clean["new_column"].notna().all()
        True
    """
    required = {"col_a", "col_b"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    out = df.copy()

    # ... transform logic, one or two operations max ...

    return out
```

---

## Anti-patterns to refuse

### The mega-function

```python
def clean(df):
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.dropna()
    df["temp_c"] = df["temp_c"].clip(-40, 55)
    df["hour"] = df["timestamp"].dt.hour
    df["is_anomaly"] = abs(df["temp_c"]) > 30
    df.to_parquet("out.parquet")
    return df
```

**Why it's wrong:**
- Six different responsibilities
- No type hints, no docstring, no example
- Side effect (write to parquet) hidden inside a "clean" function
- Untestable in isolation
- The function name lies — it does more than clean

**Refactor:** six separate functions chained with `.pipe()`.

### The mutating-input function

```python
def parse_timestamps(df):
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df
```

**Why it's wrong:** mutates the caller's dataframe. The caller's `df_raw`
is no longer raw after this runs.

**Fix:** start with `out = df.copy()`, transform `out`, return `out`.

### The flag-soup signature

```python
def clean(df, drop_nulls, cap_outliers, impute, add_features, write_out, verbose):
    ...
```

**Why it's wrong:** booleans are configuration in disguise. The function
is now seven functions in one, switched by flags.

**Fix:** seven functions, composed by the caller.

### The string-typed enum

```python
def impute(df, strategy):
    if strategy == "mean":
        ...
    elif strategy == "median":
        ...
    elif strategy == "mdian":  # typo — silent bug
        ...
```

**Why it's wrong:** typos in strings are silent bugs.

**Fix:** use `Literal["mean", "median"]` and let the type checker catch
typos. Or split into two functions.

---

## When to promote from notebook → module

Lift a notebook cell into a function when:

- [ ] You've stopped iterating on its logic.
- [ ] It's used more than once (DRY).
- [ ] Its inputs and outputs are clear.
- [ ] You want the type checker / tests to verify it.

Keep it in the notebook (for now) when:

- [ ] It's a one-off exploration ("what does this look like?").
- [ ] You're still changing it every two minutes.
- [ ] It's tied to interactive output (a chart, a `df.head()`).

The arrow only goes one direction: notebook → module. Once promoted,
the notebook **imports** the function instead of duplicating it.

---

## The LLM working loop applied to functions

When you ask an LLM to write a function for you:

1. **Specify** — input shape, output shape, edge cases, the assertion that
   would prove it correct. No "make a cleaning function." Yes "given a df
   with columns [...], parse the timestamp column to UTC, preserving the
   original string in `timestamp_raw`, and assert <1% parse failures."

2. **Direct** — paste the function template above and ask the LLM to fill
   in the body.

3. **Verify** — read the body LINE BY LINE. Ask the LLM to explain any
   line you don't fully understand. Check the docstring against what the
   code actually does. Run the example.

4. **Iterate** — if the function fails the checklist, ask for a refactor.
   Don't accept "it works" as a defense — works once is not works.

If the function passes the checklist, it goes in `src/`. If it doesn't,
it stays in the notebook until it does.
