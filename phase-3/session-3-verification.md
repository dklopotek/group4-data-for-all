# Session 3 Deliverable Verification Report

**Date:** 2026-05-26
**Verifier:** Claude Code Review Agent
**Scope:** CRISP-DM Phase 3 (Data Preparation) — Mycorrhizal Barcelona

---

## Summary

| # | Deliverable | Status | Issues |
|---|------------|--------|--------|
| 1 | `notebooks/02-data-cleaning.ipynb` | PASS | Non-deterministic (pd.Timestamp.now()), references wrong log path |
| 2 | `src/clean_data.py` | PASS | Non-deterministic (pd.Timestamp.now()), some helpers lack assertions |
| 3 | `data/processed/*.parquet` | EXISTS | clean_data.py writes GeoJSON + Parquet; notebook writes trees_cleaned.parquet |
| 4 | `docs/data-cleaning-log.md` | PASS | 14 transforms logged, all sections present; references different notebooks |
| 5 | `docs/datasheets/ajuntament-trees.md` — Section 4 | FAIL | Placeholder text not replaced with Session 3 cleaning steps |
| 6 | `docs/datasheets/gbif-fungi.md` — Section 4 | FAIL | Not updated with Session 3 cleaning steps |
| 7 | `notebooks/01-data-profiling.ipynb` | EXISTS | File exists, content not re-verified for cleaned-data run |
| 8 | `docs/pipeline-architecture-v1.md` | PASS | Stale reference to "No src/ directory yet" (line 31); function name mismatch |
| 9 | `requirements.txt` | FAIL | Uses `>=` not `==`; missing pandas, numpy |
| 10 | >=1 documented function with assertion | PASS | Most functions have type hints + docstrings + assertions |

---

## Detailed Findings

### 1. `notebooks/02-data-cleaning.ipynb`

**CHECKLIST:**

| Check | Status | Detail |
|-------|--------|--------|
| Title + purpose (Cell 1) | PASS | Markdown cell with inputs/outputs/framing |
| Imports + RANDOM_SEED=42 (Cell 2) | PASS | deterministic seed set, pathlib paths |
| Load raw + df = df_raw.copy() (Cell 3) | PASS | concat 2 CSVs, never mutates raw |
| Task 1 — Select (Cells 4-5) | PASS | 14 of 43 cols retained, all 189K rows kept |
| Task 2 — Clean (Cells 6-10) | PASS | Datetime parse, type coercion, 4-strategy missing, cap-and-flag outliers |
| Task 3 — Construct (Cells 11-12) | PASS | Species normalization, temporal features |
| Task 4 — Integrate (Cells 13-14) | PASS | FungalRoot join with TOP20_MYCO override |
| Task 5 — Format (Cells 15-16b) | PASS | REQUIRED_COLS assertion, parquet output |
| Task 6 — Verify (Cells 17-21) | PASS | 3 visualizations, summary table |
| Task 7 — Bridge to module (Cell 22) | PASS | Deferred items, residual concerns documented |
| Reproducibility check (Cell 23) | PASS | Checklist present |

**ISSUES:**

- **NON-DETERMINISTIC** — Cell 7 (`now = pd.Timestamp.now()`) and Cell 12 (`YOUNG_CUTOFF = now - pd.DateOffset(years=5)`) compute a dynamic young-tree threshold that changes daily. Violates reproducibility checklist item 1.
- References `phase-3/data-cleaning-report.md` rather than `docs/data-cleaning-log.md` as the cleaning audit artifact.
- Output file is at `data/trees_cleaned.parquet` not `data/processed/trees_cleaned.parquet` — does not use the `processed/` subdirectory.

---

### 2. `src/clean_data.py`

**CHECKLIST:**

| Check | Status | Detail |
|-------|--------|--------|
| Type hints | PASS | Most functions have pd.DataFrame/gpd.GeoDataFrame -> same |
| Docstrings (Args/Returns/Example) | PASS | Most functions have all three |
| df.copy() at start of transforms | PASS | Nearly all start with `out = df.copy()` |
| One function = one transform | PASS | Good separation of concerns |
| Assertions per function | PARTIAL | `zonal_mean_from_raster`, `_modal`, `_species_list_json`, `_young_pct`, `finalize_columns` lack assertions |
| Constants at top | PASS | RNG_SEED, YOUNG_YEARS, SCENARIOS, etc. |
| `if __name__ == "__main__"` guard | PASS | Present |
| pathlib paths, relative to project root | PASS | `PROJECT_ROOT` derived from `__file__` |
| `assert_clean_invariants()` | PASS | 12 invariant checks on final output |
| RNG_SEED=42, deterministic | PARTIAL | Uses `np.random.default_rng(RNG_SEED)` good, but `pd.Timestamp.now()` line 125 is non-deterministic |

**ISSUES:**

- **NON-DETERMINISTIC** — `TODAY = pd.Timestamp.now()` on line 125. Used in `flag_colonisation_uncertainty` to determine 5-year young-tree cutoff. Changes daily. Fix: hardcode a reference date or pass it as a parameter defaulting to a fixed date.
- Helper functions without assertions: `zonal_mean_from_raster`, `_modal`, `_species_list_json`, `_young_pct`, `finalize_columns`.
- `_normalise_myco` (line ~166) has fragile string-matching — `"AM-"` in `v_upper` catches "AM-..." types but could also catch unexpected labels. Consider exact enum matching instead.
- Some docstrings use `Parameters` section header but the course template examples use singular `Parameter`.

---

### 3. `docs/data-cleaning-log.md`

**CHECKLIST:**

| Check | Status | Detail |
|-------|--------|--------|
| Dataset metadata | PASS | Dataset name, paths, maintainer, date |
| Pipeline summary | PASS | Row counts, retention %, columns added/dropped |
| One row per transform | PASS | 14 transforms |
| Each row: What/Why/Downstream/Reversibility/Assertion | PASS | All five fields populated for every transform |
| "What we did NOT clean" section | PASS | 6 items with rationale |
| Cumulative effect paragraph | PASS | Raw vs cleaned summary |
| Sign-off checklist | PASS | 6 items |

**ISSUES:**

- References `notebooks/02-grid-trees.ipynb` and `notebooks/03-scoring.ipynb` as the cleaning notebooks — but these are NOT the same as the scaffold-generated `notebooks/02-data-cleaning.ipynb`. The log describes a different pipeline structure than the one produced in the scaffold notebook.
- The log says output is `data/scored_grid.geojson` (no `processed/` prefix) but clean_data.py writes to `data/processed/scored_grid.geojson`.
- Some assertion blocks reference `data-cleaning-report` issue codes (A3, G1, F1, etc.) without defining them in the log — assumes reader has the earlier report open.

---

### 4. `docs/pipeline-architecture-v1.md`

**CHECKLIST:**

| Check | Status | Detail |
|-------|--------|--------|
| What changed since v0 | PASS | Lines 9-35 |
| Mermaid diagram | PASS | Lines 41-108 |
| 12 components + 4 connectivity components | PASS | C1-C12, N1-N4 |
| Component tables (File/Input/Output/Failure/Tests/Log) | PASS | All have full tables |
| Schema table | PASS | 40 columns documented |
| Open seams | PASS | 6 items |
| ADRs | PASS | 5 ADRs |

**ISSUES:**

- **STALE** — Line 31: "No `src/` directory yet -- all implementation lives in notebooks" and lists refactoring as Session 4 goal. `src/clean_data.py` now exists. This line is misleading.
- Function name mismatch: Box C12 is called `classify_interventions` (with plural 's') but the actual function in `clean_data.py` is `classify_intervention` (singular). The `classify_interventions` name appears in the table at line 26 as well.
- Component tables list function locations as notebooks (e.g., "notebooks/02-grid-trees.ipynb") rather than `src/clean_data.py` — these were not updated after the module was built.

---

### 5. `requirements.txt`

**ISSUES:**
- Uses `>=` not `==` — violates the pinned-dependencies reproducibility requirement. e.g., `geopandas>=1.1.3` should be `geopandas==1.1.3` after verifying which version actually works.
- Missing: `pandas`, `numpy` — both are standard dependencies used in clean_data.py. The comment says they are "intentionally unpinned because already installed at correct versions" but this breaks pip install from scratch.
- Missing: `rasterio` is imported with try/except in clean_data.py but not listed in requirements.txt.

---

### 6. Datasheet Section 4

- **ajuntament-trees.md** — Section 4 begins at line 144. Contains original Session 2 placeholder text (preprocessing done by dataset creators). NOT updated with actual Session 3 cleaning steps (species normalization, FungalRoot join, planting date parsing, etc.).
- **gbif-fungi.md** — Section 4 begins at line 158. Contains original Session 2 description (GBIF query filters). NOT updated with Session 3 cleaning-specific processing.

---

## Cross-Artifact Consistency

| Check | Status | Detail |
|-------|--------|--------|
| column names: clean_data.py finalize vs data-contract.yaml | PASS | 39 columns match after rename map |
| intervention_type enum: clean_data.py vs data-contract.yaml | FAIL | clean_data.py: "species-selection"; contract: "multi-strategy" |
| intervention_profile format: code vs contract docs | FAIL | Code stores JSON dict; contract documents human-readable "52% de-paving ..." |
| function names: clean_data.py vs pipeline-architecture.md | FAIL | `classify_intervention` (code) vs `classify_interventions` (arch doc) |
| notebook references: cleaning-log vs actual notebooks | FAIL | Log references `02-grid-trees.ipynb`, notebook is `02-data-cleaning.ipynb` |
| clean_data.py location claim: pipeline-arch vs reality | FAIL | Arch doc says "No src/ directory yet" but src/clean_data.py exists |
| notebook imports from src.clean_data | N/A | Notebook 02-data-cleaning.ipynb does NOT import from clean_data.py — it is a standalone exploration. clean_data.py is the production pipeline built separately. |

---

## Pre-Commit Ritual Readiness

| Step | Status | Notes |
|------|--------|-------|
| Restart kernel in 02-data-cleaning.ipynb | UNTESTED | Must be done manually |
| Run All — no errors | UNTESTED | |
| `python src/clean_data.py` regenerates parquet | UNTESTED | Requires input files (raster data) to be present |
| Parquet matches notebook output | UNTESTED | clean_data.py outputs scored grid; notebook outputs cleaned tree table (different artifacts) |
| Re-run 01-data-profiling.ipynb on cleaned data | UNTESTED | Profiling notebook content not checked |
| `git log --oneline` shows Session 3 commits | UNTESTED | See git status below |
| Push | UNTESTED | |

---

## Recommended Fixes Before Commit

### Blocker (Must Fix Before Merge):

1. **Fix non-deterministic `pd.Timestamp.now()` in both clean_data.py (line 125) and notebook (cells 7, 12).** Replace with a fixed reference date (e.g., `2026-05-26` or the last snapshot date). The young-tree 5-year cutoff must be reproducible across runs.

2. **Update datasheet Section 4 for both ajuntament-trees.md and gbif-fungi.md** with actual Session 3 cleaning operations performed (species normalization, FungalRoot join strategy, planting date handling, missingness classification, etc.).

3. **Pin requirements.txt** — change all `>=` to `==` with verified working versions. Add `pandas`, `numpy`, and `rasterio` to the dependency list.

4. **Resolve `intervention_type` enum mismatch.** Align clean_data.py's `"species-selection"` with data-contract.yaml's `"multi-strategy"` — change one to match the other. The assert in `assert_clean_invariants` (line 1508) will need updating too.

### Should Fix Before Commit:

5. **Update pipeline-architecture-v1.md line 31** — remove "No src/ directory yet" claim now that `src/clean_data.py` exists. Update component tables to point to `src/clean_data.py` function names.

6. **Align function name** — change `classify_intervention` (singular) to `classify_interventions` (plural) in clean_data.py to match the architecture doc, or vice versa.

7. **Align cross-artifact references** — the cleaning-log.md, notebook.md, and architecture doc should reference consistent notebook names. The cleaning-log was written for `02-grid-trees.ipynb` / `03-scoring.ipynb` but the scaffold notebook is `02-data-cleaning.ipynb`.

### Nits:

8. Add assertions to the 5 helper functions missing them: `zonal_mean_from_raster`, `_modal`, `_species_list_json`, `_young_pct`, `finalize_columns`.

9. Fix `_normalise_myco` string matching — use exact enum comparison instead of `"AM-" in v_upper` substring matching to avoid false positives.

10. Update notebook output path to use `data/processed/trees_cleaned.parquet` for consistency with the processed/ convention.

---

## Current Git State

```
M session-3/task-ownership.yaml
?? HANDOFF.md
?? "MaAI01 25-26 - T03S13_Data -- DOCUMENTS/"
?? Seek_Deep_CHINA.md
?? phase-1/
?? phase-2/
?? phase-3/
?? research/
?? session_3
```

Session 3 files are in untracked directories (phase-3/, session_3/). The modified file `session-3/task-ownership.yaml` was already tracked. None of the Session 3 deliverables (src/, docs/, notebooks/) appear in git status because they are not yet staged. All 4 deliverable files exist on disk but need `git add` before they can be committed.
