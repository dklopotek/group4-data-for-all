# Reality-Check Audit — Mycorrhizal Barcelona Data Pipeline

**Date:** 2026-05-10
**Auditor:** TestingRealityChecker (Integration Agent)
**Branch:** session-2/data-understanding-rafik

---

## Files Inspected

| File | Rows / Features | Outcome |
|------|----------------|---------|
| `data/scored_grid.geojson` | 495 features | Audited |
| `data/network_islands.geojson` | 2,165 features | Audited |
| `data/bridge_scores.csv` | 15 rows | Audited |
| `outputs/priority_zones.csv` | 0 rows (before fix) / 15 rows (after) | FIXED |
| `notebooks/05-visualisation.ipynb` | 30 cells | 4 bugs found and fixed |

---

## Issues Found and Status

### ISSUE 1: priority_zones.csv completely empty (0 rows) — ROOT CAUSE
**Status: FIXED**

**Evidence:** `outputs/priority_zones.csv` contained only a header row with 14 columns, 0 data rows. File size was 194 B.

**Root cause:** Cell 5 (`e1f2a3b4`) of notebook 05 called `_ensure_col()` to add `district`, `barri`, `composite_score_A/B/C`, and `top15_flag` as new columns with default values (`"unknown"`, `0.0`, `0`). Because `scored_grid.geojson` does not contain these exact column names, the defaults silently shadowed the real data:

| Column expected by notebook | Actual column in scored_grid.geojson |
|-----------------------------|--------------------------------------|
| `district` | `nom_districte` |
| `barri` | `barri_name` |
| `composite_score_A/B/C` | `composite_A/B/C` |
| `top15_flag` | `top15_scenario_B` |
| `expected_myco_type` | `dominant_myco_type` |
| `lst_anomaly` | `lst_anomaly_celsius` |

Because `top15_flag` was created with default `0`, the filter `scored_grid["top15_flag"] == 1` returned 0 rows, producing an empty `top15` DataFrame that cascaded through every downstream output.

**Fix applied:** Cell 5 now opens with an explicit `rename_map` that renames the real column names to the canonical names expected by the rest of the notebook, before `_ensure_col` runs. The `_ensure_col` calls then add defaults only for genuinely absent columns.

**Verification:** `outputs/priority_zones.csv` now contains 15 rows with real district, barri, composite score, and intervention type values. File size is 1,572 B.

---

### ISSUE 2: Sensitivity comparison chart drew from empty lists — FIXED
**Status: FIXED**

**Evidence:** `SCENARIO_COLS` in Cell 2 (`e5f6a7b8`) was set to:
```python
SCENARIO_COLS = {"A": "composite_score_A", "B": "composite_score_B", "C": "composite_score_C"}
```
But `scored_grid.geojson` stores these columns as `composite_A`, `composite_B`, `composite_C`. The `_top15_for_scenario()` function checked `if score_col not in gdf.columns: return []`, so all three lists were empty. The sensitivity comparison chart rendered with blank rows for all 15 ranks.

**Fix applied:** `SCENARIO_COLS` corrected to `{"A": "composite_A", "B": "composite_B", "C": "composite_C"}`. After the column rename in Cell 5 these become `composite_score_A/B/C`, which is what `SCENARIO_COLS` now references. Both are consistent.

**Verification:** After fix, `_top15_for_scenario()` returns 15 cell IDs per scenario. Sensitivity chart now renders 15 real zones per column.

---

### ISSUE 3: All top-15 zones rendered in grey (#888888) on the priority map — FIXED
**Status: FIXED**

**Evidence:** `INTERVENTION_COLOURS` in Cell 2 used Title-case keys:
```python
INTERVENTION_COLOURS = {"De-paving": ..., "Cooling": ..., "Planting": ..., "Species-selection": ...}
```
But `scored_grid.geojson` stores `intervention_type` as lowercase (`"cooling"`, `"planting"`, `"species-selection"`). The `_intervention_colour()` function returned `"#888888"` (grey fallback) for every real zone on the map and in the sensitivity chart.

**Fix applied:** Both lowercase and Title-case keys added to `INTERVENTION_COLOURS`. The lowercase keys (`"cooling"`, `"planting"`, `"species-selection"`) ensure real data resolves to correct colours. Title-case keys remain for synthetic scaffold compatibility.

**Verification:** Colour lookup for all 2 intervention types present in the real top-15 (`cooling`, `planting`) now resolves to `#C0392B` and `#27AE60` respectively, not grey.

---

### ISSUE 4: bridge_score = 0 for all 15 priority zones — DATA PROBLEM, NOT FIXED IN CODE
**Status: NEEDS MANUAL STEP**

**Evidence:** `data/bridge_scores.csv` contains a `bridge_score` column with dtype `int64`, and all 15 values are `0`. This is not a column-name bug — the column exists and is numeric. The zeros were written by notebook 04 (`04-connectivity.ipynb`), which apparently computed bridge centrality but either the computation produced zeros or the output was not saved correctly.

**Impact:** `bridge_score` appears as `0.0` in `priority_zones.csv`. The network spread map layer (top-3 bridge zones) falls back to `top15.head(3)` because `nlargest(3, "bridge_score")` on all-zero values returns the first 3 rows, which is technically correct but not meaningful.

**Required action:** Re-run `notebooks/04-connectivity.ipynb` and verify that the bridge centrality computation produces non-zero values. The `bridge_score` column in `bridge_scores.csv` should reflect actual betweenness centrality of each zone in the network graph. This is a notebook 04 data-generation issue, not a notebook 05 bug.

---

### ISSUE 5: Previously reported "intervention_type = unknown for all 15 zones" — NOT CONFIRMED
**Status: NOT A BUG (false report)**

**Evidence:** `scored_grid.geojson` has `intervention_type` with three distinct real values:
- `planting`: 320 cells
- `cooling`: 174 cells
- `species-selection`: 1 cell

Among the top-15 (Scenario B), values are `cooling` (5 zones) and `planting` (10 zones). No `unknown` values exist anywhere in the file. This issue was likely observed when notebook 05 was generating output from an empty `top15` DataFrame (Issue 1), causing the `intervention_type.value_counts()` to return an empty Series.

---

### ISSUE 6: bridge_score stored as object dtype — NOT CONFIRMED IN GEOJSON
**Status: NOT PRESENT**

**Evidence:** In `data/scored_grid.geojson`, `bridge_score` is `None` for all 495 features (it is not populated in the grid, only in `bridge_scores.csv`). In `bridge_scores.csv`, `bridge_score` dtype is `int64` — not object. The originally reported `object` dtype does not appear in the current files. The `pd.to_numeric` cast in the network spread cell is retained as a defensive guard and causes no harm.

---

## Summary Table

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | `priority_zones.csv` empty — column name mismatch in Cell 5 | Critical | FIXED |
| 2 | Sensitivity chart empty — wrong SCENARIO_COLS column names | High | FIXED |
| 3 | All map zones rendered grey — INTERVENTION_COLOURS case mismatch | High | FIXED |
| 4 | bridge_score = 0 for all zones — notebook 04 data problem | Medium | NEEDS MANUAL STEP |
| 5 | "intervention_type = unknown" report | False alarm | NOT A BUG |
| 6 | bridge_score as object dtype report | Not present | NOT CONFIRMED |

---

## Output File Status After Fixes

| File | Size before | Size after | Status |
|------|-------------|------------|--------|
| `outputs/priority_zones.csv` | 194 B (0 rows) | 1,572 B (15 rows) | FIXED |
| `outputs/priority_zones.html` | 3,244 B (empty table) | 21,612 B (15 rows) | FIXED |
| `outputs/priority_map.html` | 1.0 MB (0 zones) | 1.1 MB (15 zones) | FIXED |
| `outputs/sensitivity_comparison.png` | 131,715 B (blank rows) | 62,418 B (real data) | FIXED |
| `outputs/limitations.md` | 7,803 B | 7,803 B | Unchanged, OK |
| `outputs/network_spread.html` | 7.2 MB | 7.2 MB | Unchanged, OK |

---

## Remaining Open Item

Notebook 04 must be investigated for why `bridge_score` is zero for all 15 priority zones. Until that is resolved, the network spread map's "top-3 bridge interventions" layer is functionally a top-3 by rank rather than by true network leverage, and the `bridge_score` column in `priority_zones.csv` is not meaningful.
