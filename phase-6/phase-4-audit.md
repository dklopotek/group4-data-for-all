# Phase 4 (Modeling) — Skill Audit: Composite-Indicator Discipline (Pivot)

**Date:** 2026-06-05
**Skill applied:** `crispdm-4-modeling` (Route 4A composite indicator; OECD/JRC 2008; mandatory sensitivity; Mitchell model card; anti-pattern catalogue).
**Precondition met:** Phase 3 data contract exists (`phase-6/allergen-data-contract.yaml`).
**Analytical core:** `priority = source_std × exposure_std` (v1); `× deprivation_std` (v3). Baselines: density-only, random.
**Altitude:** seminar scope, lecture > skill.

## Technique routing (decision tree)

Output per cell = **a ranking on a multi-dimensional concept** (allergen-exposure-relief priority) → **Route 4A composite indicator**. ML gate correctly **failed** (no labelled ground truth, no measured-pollen target, decision is a ranking not a prediction) → ML rejected, composite chosen. This is the lesson from Cycle A, which *also* should have been 4A but was dressed as 4C (a linear model validated against its own composite). Routing recorded.

## 8-artifact exit check

| # | Artifact | Status | Location |
|---|---|---|---|
| 1 | Model card (non-ML) | ✅ | `outputs/model-card-allergen-v1.md` |
| 2 | Sensitivity log (norm × weight × aggregation × threshold) | ✅ | §C + T4 + v3 sensitivity |
| 3 | Decision log | ✅ | `phase-6/phase-3-audit.md` §1 + `modeling.md` |
| 4 | Weight justification table | ❌→✅ | §A (filled) |
| 5 | Construct-validity evidence | ⚠️→✅ | §B (formalized) |
| 6 | Reproducible artefact (1 command, seed) | ✅ | data contract `rebuild:` |
| 7 | Out-of-scope statement | ✅ | model card NOT-list (6) |
| 8 | Open questions / limitations | ✅ | model card + §D |

## §A — Weight & aggregation justification (closes anti-pattern #2)

The skill flags "equal weighting by default with no justification." Here the defense is stronger than equal-weighting: **the product is not a chosen aggregation of indicators — it IS the objective.**

| Term | Exponent/weight | Source of weight | Rationale |
|---|---|---|---|
| source_std | 1 | definitional | exposure burden = pollen emitted × people exposed; this is the quantity the decision maximizes, not a weighted opinion about importance |
| exposure_std | 1 | definitional | same — burden is the product by definition (a unit of pollen over an empty cell relieves no one; a crowded cell with no planes has no plane-pollen to relieve) |
| deprivation_std (v3) | 1 | value choice (equity) | multiplies in only in the equity variant; declared as an objective change (efficiency→equity), co-reported with v1, planner chooses |

- **Normalization:** min-max to [0,1] (OECD/JRC ch.4 menu). NOT 5th/95th-winsorized — the max (485-plane Sant Martí cell) is a *real* cell, not a data error, so winsorizing would discard a true extreme. Outlier-sensitivity is **tested**, not assumed: T4 rank-normalized variant (immune to the single high cell) holds the re-order verdict. So the plain-min-max choice does not drive the conclusion.
- **Aggregation:** multiplicative (geometric family) — **partially/non-compensatory** (OECD/JRC ch.6). A cell low on either layer cannot be rescued by being high on the other. This is the exact decision semantics and the explicit fix for Cycle A's fully-compensatory weighted sum, where one high-variance component (sealed surface) silently dominated. Justified by the concept, not convenience.
- **No hidden effective weights:** each layer enters once at exponent 1 over standardized [0,1] inputs; there is no weight vector to mis-set. T2 confirms both layers materially move the ranking (corr 0.80 / 0.64) and inputs are not collinear (0.30).

## §B — Construct validity (closes artifact #5)

Split by what is definitional vs proxy — the honest distinction:

- **"Exposure burden" — high construct validity, by construction.** The index measures `source × exposure`, which *is* the exposure-relief objective. There is no latent concept being approximated here; the number is the thing.
- **"Plane pollen" (the SOURCE sub-layer) — LIMITED construct validity.** `plane_count × maturity` is a *proxy* for actual emitted pollen, literature-anchored (Gabarra et al. 2002: Platanus ≈ 46% of Barcelona's annual pollen; Maya-Manzano et al. 2017: emission scales with inflorescence count/maturity) but **not validated against measured pollen** (none open). This is the central declared limitation, carried from Phase 2.
- **Face validity (convergent check):** the re-ordering is inspectable and sensible — Nou Barris cell (251 planes, 13.4k residents) outranks Sant Martí (485 planes, 6.5k residents); density-only would invert them. A planner can reconstruct any cell's score in plain words (count × maturity × people).
- **Independent expert panel: NOT performed** (seminar scope) — declared as a limitation, not claimed.

## §C — Sensitivity log (consolidated; closes artifact #2)

Mandatory per skill — run across the consequential forks, verdict must survive:

| Fork | Variant | Result |
|---|---|---|
| Maturity weighting | uniform maturity (priority = density × exposure) | re-order verdict **holds** |
| Normalization | rank-normalized instead of min-max | **holds** |
| Aggregation | min(source,exposure) instead of product | **holds** |
| Threshold k | top-15 AND top-50 both reported | margin +4.6 / +9.3 pts |
| Equity weight (v3) | floored [0.5,1] deprivation | top-15 Jaccard 0.875 vs v1 |
| Equity weight (v3) | rank-based deprivation | top-15 Jaccard 0.5 vs v1 |

Source: `outputs/phase-6/allergen_priority_results.md` (T4), `equity_results.md`. The headline (exposure earns its place) is **robust** across all v1 forks. The equity tradeoff direction holds under both deprivation variants.

## §D — Precision honesty (closes anti-pattern #5)

Raw results are reported to 4 dp in the JSON for reproducibility, but the **defensible claims are coarse**: exposure re-orders (~70% of top-15 changes), margin over density is a few points, equity lifts the deprived-tercile share 40%→60% for ~0.5 pp. The verdict does not depend on any 3rd/4th-decimal digit. Report the conclusion in tier/direction terms; keep the decimals as audit trail, not as claimed precision.

## Quality gate

- [x] One-sentence analytical question matches output
- [x] Technique family (4A) justified vs rejected ML
- [x] All methodological choices logged with rationale (§A, phase-3-audit §1)
- [x] Test design pre-registered before build (`allergen-validation-design.md`, dated before results)
- [x] Sensitivity across ≥3 forks (norm, weight, aggregation) — §C
- [x] Robust-tier classification (not single point) — §C/§D
- [x] External/face validity check — §B
- [x] Reproducible: one command — data contract
- [x] Model card + sensitivity log + weight table written
- [x] Out-of-scope stated — model card
- [x] Equity considered (who's missing, who bears error cost) — v3 + model card ethics

**Phase 4 (pivot) passes the skill's 8-artifact gate and quality checklist.**
