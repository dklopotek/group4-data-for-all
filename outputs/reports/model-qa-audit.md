# Model QA Audit — Mycorrhizal Barcelona Scoring Pipeline

**Auditor:** Independent Model QA (audit-grade review)
**Date:** 2026-05-10
**Scope:** Composite scoring (notebook 03) and connectivity / bridge analysis (notebook 04), with the newly-fixed `data/urban-atlas/sealed_surface.tif` (sealed_pct now 0.024–0.894, mean 0.57 across 1,050 raster pixels covering the 495-cell grid).
**Question asked of this audit:** Will re-running notebooks 03–05 against the fixed raster produce defensible results? Or are there latent bugs that will silently propagate into the final priority map?

---

## Verdict at the top

**FIX-FIRST.** Do **not** re-run the pipeline yet. There are **four blocking implementation defects** independent of the sealed raster — each one will produce numerically different but still wrong outputs after a re-run. Two of these defects exist *because* the team only saw the symptoms when sealed_pct was constant; they will surface as new pathologies the moment sealed_pct varies.

Concretely: the existing code, run today against the new raster, produces a top-15 list where 471/495 cells (95%) collapse onto `intervention_type = "de-paving"` (the saved file currently shows 320/495 = "planting" because sealed is broken; that distribution flips entirely after the fix). Districts shrink from 5 represented to 5 represented, but the constraint logic is internally broken (Section 4 below). And the documented Scenario B weights drift from (0.50/0.17/0.17/0.05 → docs) to (0.55/0.20/0.20/0.05 → code) — a silent change that has never been signed off.

The four blockers:

1. **`s1_sealed` scale bug persists in code** — notebook 03 cell `cell-s1` still applies `scale=1/100`, which will turn the new 0.024–0.894 raster back into 0.00024–0.0089. Same bug, fixed raster.
2. **`s4_mismatch` scale bug** — the AM-dominant rule compares `am_pct >= 0.8` against data on a 0–100 scale. 489/495 cells (instead of 314) get classified as AM-blind. The downstream `am_blindness_flag` column says 314.
3. **District-constraint loop is broken** — the loop displaces `selected[-1]` on every iteration, overwriting itself, so only the *last* missing district ever gets a representative. Success Criterion #2 (every district has ≥1 cell) is silently violated.
4. **Documented weights ≠ implemented weights** — `docs/system-sketch-v0.md` line 187 specifies Scenario B = 0.50 / 0.17 / 0.17 / 0.05 (last edit 2026-05-10). `notebooks/03-scoring.ipynb` cell `cell-composite` uses 0.55 / 0.20 / 0.20 / 0.05. No commit message or comment explains the drift.

These are mechanical bugs, not interpretive disagreements. Fix them, then re-run.

The remaining issues (Sections below) are MAJOR-but-not-blocking calibration concerns that the team should *understand and acknowledge* before publishing top-15, but they don't require code changes before re-run. The single CRITICAL ranking issue — that LST and NDVI use min-max normalisation centred on 0.5 instead of being anomaly-centred — produces a defensible-but-different ranking; reasonable people will argue both ways.

---

## Dimension 1 — Documentation vs. Reality

**Verdict: MAJOR**

| Drift | Documented (docs/system-sketch-v0.md) | Implemented (notebooks/03-scoring.ipynb) | Severity |
|---|---|---|---|
| Scenario B weights | line 187: `sealed 0.50 / LST 0.17 / NDVI 0.17 / host-mismatch 0.05` | cell `cell-composite`: `sealed 0.55 / LST 0.20 / NDVI 0.20 / mismatch 0.05` | MAJOR — silent drift, no changelog entry |
| LST processing | line 161: "subtract city-wide median" → anomaly | cell `cell-s2`: subtracts city-wide median ✓ then min-max normalises [city_min, city_max] | MAJOR — the second step is undocumented and changes the semantics |
| AM-blindness application | seam 1 (line 255–261): "report categorical 'expected-but-unconfirmable' flag for AM cells; reserve quantitative confirmation gap for EM cells" | `compute_mismatch_score` applies a numeric 0.5 to AM-dominant cells (compare-vs-0.8 on a 0–100 column → fires on 489 cells); never produces the documented categorical flag in the output table | MAJOR |
| `dominant_myco_type` field | system-sketch P3 says "AM-dominant ≥80%, mixed, EM-dominant, no host" | scored_grid.geojson contains only `AM` (482) and `NM` (13). No "mixed", no "EM-dominant", no "no host". `em_pct` is identically 0 in `grid_trees.geojson` (data-audit Section 1) | MAJOR — system-sketch P3 is documented but not actually computed |
| Sub-question 5 / EM-mismatch sub-score | Both docs explicitly call out a quantitative confirmation-gap for EM cells using GBIF radius query | `em_gbif_nearby` is identically 0 across all 495 cells (no spatial join was ever done); the s4 logic that uses it is dead code | MAJOR |
| Reference patch (Source H, Sub-Q 7) | docs require Collserola/Garraf reference patch with same sub-scores, listed in Success Criterion #6 | No `data/reference_patch*.geojson`; no notebook cell computes it | MAJOR — Success Criterion #6 not met |
| Top-15 district constraint | Success Criterion #2: every district ≥ 1 representative | Function `select_top15_with_district_constraint` displaces `selected[-1]` repeatedly (overwrites itself); after corrected scoring, top-15 spans only 5 of 10 districts | CRITICAL behavioural |

**The documentation isn't a thin spec.** Both `docs/problem-brief.md` and `docs/system-sketch-v0.md` are detailed enough that the divergences above are obvious. Either the docs are out of date (and need the changes recorded with rationale) or the implementation is out of date (and needs to catch up). Today, neither is true — they have silently diverged.

**Specific evidence:**
- `notebooks/03-scoring.ipynb` cell `cell-composite`, line `"B": {"sealed": 0.55, "lst": 0.2, "ndvi": 0.2, "mismatch": 0.05}` vs `docs/system-sketch-v0.md:187`
- `data/scored_grid.geojson` `dominant_myco_type.value_counts()` = `{AM: 482, NM: 13}` — no `mixed` or `EM-dominant` ever produced
- `data/grid_trees.geojson` `em_pct.std()` = 0.0 (universally zero, see `outputs/data-audit.md` Section 1)
- `data/scored_grid.geojson` `em_gbif_nearby.value_counts()` = `{0: 495}` (universally zero)

---

## Dimension 2 — Calibration / Sanity

**Verdict: CRITICAL** (because of two specific issues; the others are MAJOR)

### 2a. Sub-score scale check

| Sub-score | Range observed (current scored_grid) | Range expected (after sealed fix) | Commensurability |
|---|---|---|---|
| `s1_sealed` | 0.0002 – 0.0089 (broken) | 0.024 – 0.894 (predicted from raster) | OK if scale bug fixed |
| `s2_lst` | 0.000 – 1.000, mean 0.524 | unchanged | OK on [0,1] |
| `s3_ndvi` | 0.000 – 1.000, mean 0.590 | unchanged | OK on [0,1] |
| `s4_mismatch` | 0.5 (489 cells) / 0.6 (6 cells) | 0.5 (314) / 0.6 (181) after s4 scale fix | Range 0.0–0.8 in code; observed 0.5–0.6 only |

### 2b. Weights sum to 1 — verified

The `assert abs(total_w - 1.0) < 1e-6` in cell `cell-composite` passes for all three scenarios as currently written: 0.55+0.20+0.20+0.05 = 1.00, 0.25×4 = 1.00, 0.17+0.30+0.30+0.23 = 1.00. **OK.**

### 2c. AM-blindness flag — fires correctly at the source, BUT s4 logic uses wrong threshold

The `am_blindness_flag` in `data/grid_trees.geojson` is computed correctly: 314 cells flagged, all with `am_pct >= 80` on a 0–100 scale. `outputs/data-audit.md:53` confirmed flag fires when AM dominates (mean am_pct = 90.1 in flagged cells).

But `notebook 03 cell-s4` re-derives AM-dominance with `am_dom = am_pct >= 0.8` against the *same 0–100 column*. Result: 489 of 495 cells get `s4_mismatch = 0.5` instead of the intended 314.

```python
# notebook 03, cell-s4:
am_dom = am_pct >= 0.8       # BUG: am_pct is on 0-100 scale
score[am_dom] = 0.5          # fires on 489 cells (should be 314)
```

**CRITICAL.** The `am_blindness_flag` in `grid_trees.geojson` and the `s4_mismatch` derivation in `scored_grid.geojson` are inconsistent with each other. A planner reading the per-cell record will see `am_blindness_flag = False` but `s4_mismatch = 0.5` (i.e., the categorical flag and the score disagree).

### 2d. NDVI / LST normalisation produces median-centred sub-scores

This is the calibration issue I think the team has not noticed.

The min-max normalisation `(x - city_min) / (city_max - city_min)` produces:
- `s2_lst.median()` = 0.533
- `s3_ndvi.median()` = 0.624

i.e., a typical cell has heat-anomaly sub-score 0.53 — interpreted by the composite as "53% of the way to a thermal barrier." A cell at the city median LST ought to score *near zero* on a barrier scale, not 0.5. Same for NDVI: a cell with median canopy ought to score low, not 0.6.

The consequence: every cell in Barcelona has a *floor* composite score around `0.55*sealed + 0.20*0.5 + 0.20*0.5 + 0.05*0.5 = 0.55*sealed + 0.225`, before any "actually a barrier" signal arrives. Composites cluster in 0.18–0.81 instead of the expected 0–1 spread.

**MAJOR.** Two defensible alternatives:
1. Use one-sided normalisation: `s2_lst = max(0, lst_anomaly) / lst_anomaly.max()` — cells cooler than median score 0.
2. Document the change explicitly and rename the metric ("relative thermal exposure rank" not "thermal barrier").

### 2e. Composite distribution after fix — predicted

I simulated a corrected re-run (sealed fix only, no other changes):

| Composite | Range | Mean | Std |
|---|---|---|---|
| A (equal) | 0.180 – 0.812 | 0.566 | 0.108 |
| B (sealed-dominant, 0.55/0.20/0.20/0.05) | 0.078 – 0.855 | 0.603 | 0.163 |
| C (heat+canopy) | 0.173 – 0.835 | 0.560 | 0.104 |

The distribution is reasonable in width (std 0.10–0.16) and not pathologically skewed. **OK conditional on fixing s1 scale.**

---

## Dimension 3 — Interpretability

**Verdict: MAJOR**

### 3a. Sub-score commensurability — partially OK

All four sub-scores nominally land on [0, 1] and are interpreted as "barrier" (0 = no barrier, 1 = maximum barrier). That part is fine.

But:
- `s1_sealed` is a *physical fraction* (0 = no impervious, 1 = fully impervious). Interpretable.
- `s2_lst` is a *relative rank* in [city_min, city_max]. The rank changes if the bbox changes. The same cell scored against a different bbox produces a different number. Not directly interpretable as "the cell is X% of a thermal barrier."
- `s3_ndvi` same as s2 — relative rank, not absolute barrier.
- `s4_mismatch` has only 2 distinct values in the current output (0.5 and 0.6) and no documented natural-language interpretation for "0.5 = informationally null but you weight it like a half barrier."

### 3b. Per-cell record readability

A planner reading a single row of `scored_grid.geojson` sees 36 columns. Some are unhelpful:
- `sensitivity_warning` is the same 80-character string in every row (`outputs/data-audit.md:132`).
- `jaccard_AB`, `jaccard_AC`, `jaccard_BC` are scalars broadcast to 495 rows (`data-audit.md:110`).
- `cell_x0`, `cell_y0` are integer corner coordinates duplicating geometry.

A planner asking "why does C016_011 rank #1?" cannot get a clean answer from the record alone:
- composite_B = 0.419 (after fix: 0.855)
- s1_sealed = 0.008 (after fix: 0.802) — "fully sealed surface"
- s2_lst = 1.000 — "hottest cell in city"
- s3_ndvi = 0.946 — "near-zero canopy"
- s4_mismatch = 0.500 — meaning **what** to a non-ecologist?

The record needs a one-line plain-English rationale derived from the dominant sub-score(s). Without it, the output is a number, not an explanation.

**MAJOR.** Add a `top_drivers` text column (e.g. `"hottest LST in city; near-zero canopy; AM-blind (no fungal signal expected)"`) before publishing.

### 3c. Intervention-type assignment after fix — collapses to one category

With corrected `s1_new` and Scenario B weights:

| Intervention type | Cell count (corrected) |
|---|---|
| de-paving (sealed) | 471 |
| planting (ndvi) | 14 |
| cooling (lst) | 10 |
| species-selection (mismatch) | **0** |

After the sealed fix, *every cell where s1_new > ~0.36* gets `intervention_type = "de-paving"`. That's 471 / 495 cells. The four-way recommendation collapses into a one-way recommendation across 95% of the city. **The species-selection branch is structurally unreachable** (max weighted s4 = 0.05 × 0.8 = 0.04 < every other sub-score's possible weighted maximum of 0.20 or 0.55).

This contradicts the stated intent of `output-sketch-v0.md` (a four-class intervention recommendation system) and undermines the project's articulation of *why* the four sub-scores are scored separately rather than collapsed earlier.

**MAJOR.** Either (a) accept that `intervention_type` is effectively a binary "de-paving / not-de-paving" recommendation and re-document accordingly, or (b) replace the argmax-of-weighted with argmax-of-unweighted-sub-score so each sub-score competes on its own scale.

---

## Dimension 4 — Robustness

**Verdict: CRITICAL** (one critical issue, two majors)

### 4a. Top-15 stability under weight perturbation (after sealed fix)

I simulated five weight scenarios against the fixed raster. Top-15 set Jaccard similarity:

| Comparison | Jaccard |
|---|---|
| base (0.55/0.20/0.20/0.05) vs +10% sealed | 0.765 |
| base vs −10% sealed | 0.875 |
| base vs equal weights | **0.429** |
| base vs heat+canopy (0.17/0.30/0.30/0.23) | **0.364** |
| equal vs heat+canopy | 0.875 |

**The current "weight-robust → recommend Scenario B as primary" claim is an artefact of the sealed bug.** With sealed_pct constant, the only variation in composites came from LST and NDVI, and LST and NDVI weights moved together across scenarios, producing high Jaccard. Once sealed varies, the Jaccard B-vs-C drops to 0.36 — well below the documented 0.5 threshold (`docs/system-sketch-v0.md:190`). The pipeline should switch to "rankings are weight-sensitive — present all 3 scenarios" automatically, but only if the sensitivity check is run on the *corrected* output. **CRITICAL.**

The pipeline currently writes the resulting "weight-robust" string into 495 rows (`sensitivity_warning` column). After the fix, that string will silently flip to "weight-sensitive" — but if the team doesn't notice, the output will continue to display the cached/old text.

### 4b. Edge cases

| Edge case | Current behavior | Robustness |
|---|---|---|
| Cells with 0 trees | None present (all 495 cells have ≥1 tree, min=1) | OK |
| Cells with all-NM trees | 10 cells with `nm_pct > 50` (some 100% NM) — currently get `s4_mismatch = 0.5` (because the broken `am_pct >= 0.8` test fires for 4 of them). After s4 fix: `s4 = 0.6` (mixed default). NM hosts don't *need* mycorrhiza; a "mismatch barrier" of 0.6 is ecologically incoherent | MAJOR — NM cells should arguably be excluded from the s4 sub-score, not assigned a mid-range mismatch barrier |
| Cells outside GBIF bbox | `em_gbif_nearby = 0` for *all* 495 cells regardless of bbox — the join was never done, so this column is structurally a constant. The "outside bbox" failure mode is masked by the "join never ran" failure mode | CRITICAL (but inherited from data pipeline, not scoring) |
| Cells outside Urban Atlas raster | After fix: 0 NaN cells (raster covers full grid bounds 423600–435600, 4577200–4591200) | OK |
| Cells outside LST raster | LST raster has 6,929 NaN pixels of 309,848 (~2%). Notebook fills NaN with 0.0 anomaly → forces `s2_lst = 0` for affected cells | MINOR — defensible default but should be flagged |
| Cells outside NDVI raster | NDVI raster has 58,714 NaN pixels of 2,784,936 (~2%). Notebook fills NaN with 0.3 → mid-range `s3_ndvi` | MINOR |
| Single-tree cells | 1 cell with `tree_count = 1`. AM percentages at 100% for those, `dominant_myco_type` becomes whatever that single tree is. Statistical noise treated as signal | MINOR — flag low-tree-count cells |
| Districts not represented in top-15 | Constraint loop is broken (Section 4c) — bypasses Success Criterion #2 silently | CRITICAL |

### 4c. The district-constraint bug

```python
# notebooks/03-scoring.ipynb, cell-top15:
for district in sorted(all_districts - selected_districts):
    district_cells = ranked[ranked[district_col] == district].index
    district_cells = [i for i in district_cells if i not in selected]
    if not district_cells:
        continue
    # Displace the current 15th-ranked cell  <-- always replaces selected[-1]
    selected[-1] = district_cells[0]
    selected_districts = set(gdf.loc[selected, district_col].tolist())
```

`selected[-1]` is overwritten on every loop iteration. If 5 districts are missing, the first 4 missing ones each *temporarily* claim the 15th slot, then are overwritten by the next missing district. The final `selected` ends up with one (unpredictable) added district plus the original top-14.

Empirically: with the corrected sealed pipeline, `select_top15_with_district_constraint` returns 15 cells covering only 5 of 10 districts (the original top-14 spans 4 districts; one extra slot adds the 5th). Five districts (LES CORTS, GRÀCIA, EIXAMPLE, NOU BARRIS, HORTA-GUINARDÓ) get zero representation. **Success Criterion #2 of the brief is silently violated.** The current saved output also fails this check (4 districts represented).

### 4d. Bridge analysis depends on `sealed_pct >= 0.7`

`notebooks/04-connectivity.ipynb` defines `SEAL_THRESHOLD = 0.7` and treats trees in cells with `sealed_pct >= 0.7` as graph-disconnected. With the broken sealed_pct (max 0.009), no tree is ever blocked → bridge_score = 0 for all 15 zones (`data/bridge_scores.csv`). After the fix: 272 of 495 cells (55%) cross the 0.7 threshold, holding 125,841 trees (66% of the inventory). The bridge analysis will produce real numbers — **but they will be very large**, because half the city's trees are now "blocked" and a single de-pave intervention will reconnect thousands.

**MAJOR.** The 0.7 threshold was chosen *before* the team had real sealed_pct values. With the fixed raster showing a mean of 0.57 and 75th percentile of 0.84, the 0.7 threshold puts the median cell *above* the barrier line. This will inflate bridge scores. Recommend: re-derive the threshold from the corrected raster (e.g., 90th percentile of sealed_pct, or a fixed ecological cutoff with citation).

### 4e. AM connectivity is computed for one district only

`notebooks/04-connectivity.ipynb` cell `cell-build-graph` builds the AM graph for a single "demonstration district" (Sant Martí, the highest-AM-count district). All 1,248 AM-dominant islands in `network_islands.geojson` are in Sant Martí. The other 9 districts have no AM connectivity computation at all.

This is *documented* in the notebook ("NOTE: AM graph built for demonstration district only…") but not in `docs/system-sketch-v0.md` and not in the data audit. A planner reading `network_islands.geojson` will see 1,248 AM islands and assume city-wide coverage. The geographical bias is invisible from the file alone.

**MAJOR.** Either compute the AM graph for all districts (the bottleneck is `cKDTree.query_pairs`, which is O(n log n), so 134k AM trees should run in tens of seconds) or add an explicit `district_coverage` field to the islands file documenting per-myco-type which districts were processed.

---

## SHIP / FIX-FIRST verdict

**FIX-FIRST.** Run this checklist *before* re-executing notebooks 03, 04, 05:

### Blocker fixes (must do, ~1 hour of work)

1. **`notebooks/03-scoring.ipynb` cell `cell-s1`:** remove `scale=1/100` from the `zonal_mean_from_raster` call. The new raster is already in [0,1].
2. **`notebooks/03-scoring.ipynb` cell `cell-s4`:** change `am_dom = am_pct >= 0.8` to `am_dom = am_pct >= 80` and `em_dom = em_pct >= 0.5` to `em_dom = em_pct >= 50`. Match the 0–100 scale of the column.
3. **`notebooks/03-scoring.ipynb` cell `cell-top15`:** rewrite the district-constraint loop to actually preserve added districts across iterations (e.g., maintain a separate `must_include` list and rebuild the final selection).
4. **`docs/system-sketch-v0.md` line 187:** decide whether the canonical Scenario B weight is 0.50/0.17/0.17/0.05 (docs) or 0.55/0.20/0.20/0.05 (code). Update one or the other and add a one-line changelog entry. No silent drift.

### Strongly-recommended fixes (do before publishing top-15, ~2 hours)

5. **`notebooks/03-scoring.ipynb` cell `cell-s2`/`cell-s3`:** decide whether you want anomaly-centred sub-scores (median cell scores ≈ 0) or city-rank sub-scores (median cell scores ≈ 0.5) and document the choice with rationale. Today the code does the second; the documentation suggests the first.
6. **Add a `top_drivers` text column** to `scored_grid.geojson` with a one-sentence plain-English rationale per cell.
7. **Re-derive `SEAL_THRESHOLD`** in notebook 04 from the corrected raster distribution (e.g., 90th percentile = ~0.86 from `np.percentile(sealed, 90)`).
8. **Address the `em_gbif_nearby = 0` everywhere** issue — either implement the spatial join or remove the dead-code branch from `compute_mismatch_score` and document that the EM-confirmation logic is deferred.
9. **Compute AM connectivity for all districts**, or add an explicit `district_coverage` flag and update the system sketch.

### Acknowledge-and-move-on (don't block re-run)

10. The intervention-type argmax will collapse to "de-paving" for ~95% of cells after fix. Decide whether to keep the four-way label or simplify. Don't pretend it's a four-way recommendation.
11. Sub-question 5's quantitative confirmation gap (EM cells × GBIF) is structurally not implemented because `em_pct = 0` everywhere in `grid_trees.geojson`. The brief's seam #1 said this would be addressed "in the model card" — make sure the model card actually documents it.
12. Sub-question 7's reference patch is not implemented. Either implement it or update Success Criterion #6 explicitly to "deferred to Session 4."

### After re-run, verify

- `composite_B` distribution: expect mean ≈ 0.60, std ≈ 0.16, min ≈ 0.08, max ≈ 0.86 (from this audit's simulation).
- Top-15 list is stable across small weight perturbations (Jaccard > 0.7) but **not** across scenario boundaries (Jaccard A-vs-B and B-vs-C will be ≈ 0.4). Update the `sensitivity_warning` text to reflect this.
- Bridge scores are no longer all-zero. If they're all > 1000, revisit `SEAL_THRESHOLD`.
- Top-15 spans ≥ 10 districts (Success Criterion #2). If not, the constraint logic is still broken.
- `s4_mismatch` distribution shows 314 cells at 0.5, ~175 at 0.6, ~6 at 0.0 or 0.8 (depending on `em_gbif_nearby` fix).
- `am_blindness_flag` and `s4_mismatch = 0.5` agree on the same 314 cells.

---

## Findings table

| # | Finding | Severity | Domain | File / Location |
|---|---|---|---|---|
| 1 | `scale=1/100` in s1 zonal stats applies to a raster already in [0,1] | CRITICAL | Implementation | `notebooks/03-scoring.ipynb` cell `cell-s1` |
| 2 | s4 `am_pct >= 0.8` test against 0–100 scale data fires on 489/495 cells instead of 314 | CRITICAL | Implementation | `notebooks/03-scoring.ipynb` cell `cell-s4` |
| 3 | District-constraint loop overwrites `selected[-1]` repeatedly; only one missing district added | CRITICAL | Implementation | `notebooks/03-scoring.ipynb` cell `cell-top15` |
| 4 | Documented Scenario B weights (0.50/0.17/0.17/0.05) ≠ implemented (0.55/0.20/0.20/0.05) | MAJOR | Doc-vs-code drift | `docs/system-sketch-v0.md:187` vs `notebooks/03-scoring.ipynb` cell `cell-composite` |
| 5 | After sealed fix, scenarios A/B/C are weight-sensitive (Jaccard B-C = 0.36) but `sensitivity_warning` will still claim weight-robust unless re-run | MAJOR | Calibration | `notebooks/03-scoring.ipynb` cell `cell-sensitivity` |
| 6 | LST and NDVI sub-scores are min-max ranks; median cell scores 0.5 (interpreted as half-barrier) | MAJOR | Calibration / Interpretability | `notebooks/03-scoring.ipynb` cells `cell-s2`, `cell-s3` |
| 7 | Intervention-type argmax collapses to "de-paving" for ~95% of cells after sealed fix; "species-selection" branch is structurally unreachable | MAJOR | Interpretability | `notebooks/03-scoring.ipynb` cell `cell-intervention` |
| 8 | `em_gbif_nearby = 0` for all 495 cells — spatial join never executed | MAJOR | Implementation | upstream of `data/scored_grid.geojson` |
| 9 | `dominant_myco_type` only ever = AM or NM in output; "mixed" and "EM-dominant" never produced | MAJOR | Doc-vs-code drift | `data/scored_grid.geojson`, vs `docs/system-sketch-v0.md:139` |
| 10 | Reference patch (Source H, Success Criterion #6) not implemented | MAJOR | Coverage | no `data/reference_patch*` file |
| 11 | AM connectivity graph computed for Sant Martí only; 9 districts uncovered | MAJOR | Coverage / Interpretability | `notebooks/04-connectivity.ipynb` cell `cell-build-graph` |
| 12 | `SEAL_THRESHOLD = 0.7` was set without seeing real sealed_pct distribution; after fix, 272 / 495 cells cross threshold | MAJOR | Calibration | `notebooks/04-connectivity.ipynb` cell `cell-imports` |
| 13 | `am_blindness_flag` (314 cells, correct) and `s4_mismatch = 0.5` (489 cells, wrong) disagree on which cells are AM-blind | MAJOR | Internal consistency | `data/scored_grid.geojson` |
| 14 | NM-dominant cells (10 cells) get `s4_mismatch ≈ 0.6` (mixed default) — ecologically incoherent for non-mycorrhizal hosts | MINOR | Edge case | `notebooks/03-scoring.ipynb` cell `cell-s4` |
| 15 | `sensitivity_warning`, `jaccard_AB/AC/BC` stored as per-row constants in 495 rows | MINOR | Schema smell | `data/scored_grid.geojson` |
| 16 | District names with Catalan accents corrupted in CSV/GeoJSON outputs (already documented) | MINOR | Encoding | `outputs/data-audit.md:208` |
| 17 | LST/NDVI raster NaN cells (~2%) silently filled with constants 0.0 / 0.3 | MINOR | Robustness | `notebooks/03-scoring.ipynb` cells `cell-s2`, `cell-s3` |
| 18 | `cell_x0`, `cell_y0` columns duplicate geometry information | INFO | Schema smell | `data/scored_grid.geojson` |

---

## What this audit can and cannot say

**Can say:** With high confidence, re-running the pipeline today against the fixed raster produces a different but still-defective result. Five mechanical bugs are independent of the raster fix and will not be caught by visual inspection of the output map (the symptoms are subtle: rankings shift, but the file structure looks fine).

**Cannot say:** Whether the *conceptual model* (4 sub-scores → weighted composite → top-15 + intervention-type) is the right framing for the planning decision. That's a separate review, and `outputs/limitations.md` is the right place to interrogate it. This audit is scoped to: does the implementation match what was documented, and does the documented implementation produce internally consistent, robust outputs.

The brief is honest about the project's epistemic limits (AM-blindness, no observed mycorrhizal community, leverage-not-outcome). The implementation should be honest about its mechanical limits too. Today it isn't.

---

**QA Analyst:** Independent Model QA Specialist
**QA Date:** 2026-05-10
**Next scheduled review:** After bug-fix checklist (items 1–4) is complete and notebooks 03, 04, 05 are re-run.
