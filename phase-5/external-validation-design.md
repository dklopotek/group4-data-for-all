# Phase 5 — Pre-registered External Validation Test

**Date written:** 2026-06-04 (BEFORE building the target or running any model — pre-registration is binding)
**Author:** Rafik El Khoury (Group 4)
**Anchors:** Session 5 lecture (Evaluation — "test whether your data carries signal"); instructor review 2026-06-02 ("point it at a question whose answer you don't already know"); `outputs/reports/lit-review-mycorrhizal-prioritization.md` §8–§9 (recommendation #4).
**Rule (inherited from `phase-4/test-design.md`):** every test below MUST run on the build, and every result reported — including unfriendly ones. Silently dropping a pre-registered test is the cardinal sin. No edits to this design after the build except dated addenda.

---

## 0. Why this test exists

Phase 4 Core B validated whether 10 raw features can predict `composite_score_B` — but the composite is a deterministic function of those features, so the answer (R² ≈ 1 in-distribution) was arithmetic, not science. The instructor and the Phase 5 lit-review both establish that the headline composite is ~91% sealed surface, with the mycorrhizal sub-scores (`s4_mismatch`, `prpi`) contributing ~0.

This test asks the question Session 4 was supposed to ask, against a target the composite **never used**:

> **After accounting for the abiotic null (sealed surface + greenness), do the biotic/host layers add any real explanatory power for an EXTERNAL fungal outcome — observed GBIF fungal occurrence?**

The answer is genuinely unknown before running. That is the point.

## 1. External target (never used to build the composite)

Source: `data/gbif-fungi-all.json` — 1,024 GBIF fungal occurrence records, all geo-located (decimalLatitude/Longitude), 287 distinct species, with genus/order/year.

**Leakage check (pre-condition, must pass before modeling):** none of the target columns below may be inputs to `composite_score_A/B/C` or to sub-scores `s1–s4`. The grid already carries `gbif_records`; confirm it is NOT a composite input (it is not among the s1–s4 formulas nor the 10 Core-B features). If any target column is found to feed the composite, STOP and redesign.

Build per 400 m cell (spatial join of GBIF points → grid in EPSG:25831, point-in-cell):
- `gbif_richness` — count of **distinct** fungal species in the cell (primary target).
- `gbif_present` — 1 if ≥1 record, else 0 (secondary target).
- `gbif_effort` — raw record count in the cell (sampling-effort proxy / covariate, NOT a target).

Written to `data/processed/gbif_external_target.parquet` (cell_id keyed), joined to the grid for analysis. Raw grid is not mutated.

## 2. The threat this test must survive — and how (pre-registered)

GBIF urban records are opportunistic citizen-science. Most cells will have 0 records, and effort co-varies with greenness/accessibility. Without controls this test would just rediscover **selection bias** (lecture threat #2). Pre-registered controls:

- **Effort is a covariate in BOTH the null and the full model**, so the biotic increment is measured at fixed effort. `log_effort = log(1 + gbif_effort)`.
- **Primary analysis is on the observed subset** (cells with `gbif_effort ≥ 1`); report n and the share of cells dropped. Silent truncation is logged, not hidden.
- **Secondary analysis is presence/absence over ALL cells** (logistic, effort as offset/covariate), so the empty cells are not thrown away — they test a different, complementary question.
- **Spatial autocorrelation** is checked via Moran's I on the full-model residuals; if significant, it is reported and a spatial-block cross-validation is run as robustness.
- **MAUP**: the 400 m cell is fixed; a one-line caveat is carried (cell size/partition condition the result).

## 3. Models (nested, formative-safe)

Abiotic null (M0) vs biotic/host (M1). Same rows, same target, M1 ⊃ M0.

```
M0 (abiotic null):  gbif_richness ~ mean_sealed + mean_ndvi + log_effort
M1 (+ biotic/host): M0 + am_pct + em_pct + platanus_pct + s4_mismatch + prpi
                       + species_richness + total_trees
```

- Richness target: OLS on the observed subset (primary); negative-binomial on the full count as robustness (count, over-dispersed).
- Presence target: logistic regression over all cells, `log_effort` included.
- Standardize predictors; report VIF (the lit-review warns sealing/heat/density are collinear — high VIF is itself a reportable finding).
- No feature selection, no tuning beyond model family. The biotic block is tested as a **block**, not variable-by-variable, to avoid cherry-picking a lucky single predictor.

## 4. Pre-registered PASS criterion (decided BEFORE running)

The biotic/host block carries real, decision-relevant signal **iff**, on the primary richness model:

> **ΔAdjusted-R² (M1 − M0) ≥ 0.05** AND **partial-F test of the biotic block p < 0.05.**

For the presence model the parallel criterion is **ΔAUC ≥ 0.03** with a likelihood-ratio test **p < 0.05**.

- **PASS** → the project has earned a *qualified* biotic claim. Report which layers carry the signal and their signs; this rescues a (re-weighted) mycorrhizal framing.
- **FAIL** → the composite adds nothing beyond the abiotic null for real fungal occurrence. The **reframe is confirmed empirically** — the deliverable becomes an urban cooling/depaving prioritization, and the mycorrhizal claim is demoted to a stated, falsified-in-this-data hypothesis. This is a clean, publishable Session-5 result, not a defeat.

Both outcomes are reported in full. The verdict does not depend on which way it lands.

## 5. Robustness (must hold for the verdict to stand)

Re-run and confirm the PASS/FAIL verdict is stable under:
1. Negative-binomial on full counts (instead of OLS observed-subset).
2. Dropping `log_effort` (does effort alone drive any apparent biotic signal?).
3. EM/AM split vs combined host layers.
4. Spatial-block CV if Moran's I on residuals is significant.

If the verdict flips under any defensible alternative, it was never robust — report that, with aggressive caveats (lecture: "conclusions that only hold one way are coincidence").

## 6. Threats-to-validity ledger (ties to VAL-05)

| Threat | How ruled out / flagged |
|---|---|
| Selection bias (GBIF effort) | effort covariate + observed-subset + presence model + drop-effort robustness (§2, §5) |
| Confounding (effort ↔ greenness ↔ sealing) | effort and abiotic null both in M0; biotic increment is over-and-above both; VIF reported |
| Spurious correlation | block test (not per-variable fishing); single pre-registered criterion |
| Cherry-picking | criterion fixed in §4 before build; all results + both targets reported |

## 7. Reporting contract

After build, append a `## Results` section to THIS file:
- Target build summary (n cells with ≥1 record, total species, richness distribution).
- M0 vs M1 table: Adj-R², ΔAdj-R², partial-F p, AIC; presence AUC + LR p.
- Per-layer coefficients + signs (M1), with VIF.
- Robustness table (§5) and Moran's I.
- **Verdict line:** PASS or FAIL against §4, and what it means for defend/rebuild/reframe.

Negative results stay in the report.

---

## Results

**Verdict: FAIL.** Richness Delta Adj-R2 = -0.0195 (criterion >= 0.05), partial-F p = 0.98917 (criterion < 0.05). Observed cells 99/494. Robust under log-richness (p=0.57) and drop-effort (p=0.54); Moran's I on residuals n.s. (I=-0.047, p=0.21). Full table + interpretation: `outputs/phase-5/external_validation_results.md`.

### Dated addendum — 2026-06-04 (post-build, design flaw logged honestly)

The §3 **presence model is circular** and its result (AUC=1.0, both models) must be discounted: `gbif_present` was pre-registered as `effort >= 1` while `log_effort` was a covariate, so effort predicts presence by construction. This was not caught at pre-registration time. Per the contract, the design is NOT silently re-run; the flaw is recorded and the **richness model on the observed subset carries the verdict** (it is sound and effort-controlled). The §5 negative-binomial robustness was not run (statsmodels not installed on the build venv); the OLS log-richness variant was substituted and is reported. These deferrals/flaws do not change the FAIL verdict — every variant agrees the biotic block adds no signal.
