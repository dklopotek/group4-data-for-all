# Section + Street Deployment Design — PRE-REGISTRATION

> **Binding pre-registration** (CLAUDE.md cardinal rule). Written *before* `src/section_priority.py`
> and `src/street_actions.py` are built. Mirrors the discipline of `phase-4/test-design.md` and
> `phase-6/allergen-validation-design.md`: every test declared here MUST run and MUST be reported —
> including unfriendly results. Results are appended to this file under `## Results` (dated addenda only).
>
> **Phase:** CRISP-DM Phase 6 (Deployment) — the *deployable artifact* the Phase-5 evaluation report
> flagged as the open gate ("a planner cannot act on a 400 m square"). NOT a re-derivation of Phases 1–3.
> Uses only data already on disk (`data/arbrat-viari.csv`, `data/raw/2026_pad_mdbas.csv`, section
> polygons) — no new ingestion.

---

## 0. Why this artifact exists (the deployment gap)

The shipped Phase-6 product (`outputs/phase-6/allergen_priority_results.md`) ranks **494 cells of a
400 m grid**. Two problems block a planner from acting on it:

1. **The grid is arbitrary (MAUP).** A 400 m square is not an administrative or operational unit.
   The standard attack on any composite-indicator map is that the ranking is an artifact of the
   aggregation geometry.
2. **The demand signal was interpolated.** `src/exposure_layer.py` areal-weights census-section
   population onto the 400 m grid — *false precision*, since population is natively a census-section
   count, not a gridded density.

**The deployment move:** recompute priority at **census-section grain** (~1,068 units — *finer* than
the 494 cells AND the native grain of the demand data, so the areal-interpolation step is removed
entirely), then within the top sections emit a **per-street Platanus action list**.

**The line not to cross:** section-level priority is a defensible claim; **street-level priority is
not** (ecological fallacy — ranking individual streets by section-level exposure is invented
precision). Street output is an **allocation / feasibility layer**, never a priority claim. The street
file carries action/inventory fields only — no priority or score column at street grain. This is the
honesty gate, grep-verified post-build.

---

## 1. Two locked decisions (recommend; veto if disagree)

**D1 — Priority grain = census section (~1,068).** NOT barri/neighbourhood: barri is only 73 units,
*coarser* than today's 494 cells, so it would lose resolution. Barri is carried as a human-readable
label only. Census section is the native grain of the population demand signal → no interpolation.

**D2 — Quota = inventory + suggested policy allocation.** Always list mature planes per street
(inventory — fully backed by `arbrat-viari.csv`). Annotate a *suggested* removal count by allocating
the city's standing policy target proportionally to section priority. Labelled feasibility allocation,
explicitly NOT a priority claim.

---

## 2. Method (declared before build)

### 2.1 Source layer (pollen source strength), section grain
- Load `data/arbrat-viari.csv`; filter `cat_nom_cientific` starting `"Platanus"` → points in EPSG:25831
  (from `x_etrs89`, `y_etrs89`).
- Spatial-join trees → census-section polygons (`TIPUS_UA == SEC_CENS`), section key =
  `DISTRICTE.zfill(2) + SEC_CENS.zfill(3)` (the `exposure_layer.py:43` pattern).
- `plane_count` = Platanus per section; `mature_count` = Platanus whose `categoria_arbrat` is in the
  **mature set** (see assumption A1).
- **`source_raw = mature_count`** — the section analogue of the cell model's
  `source_raw = plane_density * maturity` (`src/allergen_source.py:37`), computed natively instead of
  via a young-fraction field.

### 2.2 Exposure layer (demand), section grain — NATIVE, no interpolation
- Population per section from `2026_pad_mdbas.csv` `Valor`, joined on the section key. This is the
  whole point: the demand signal is used at its native grain.

### 2.3 Priority
- `priority = minmax(source_raw) * minmax(exposure_pop)` — identical functional form to the shipped
  cell product (`src/allergen_priority.py:57`). Reuse `minmax`, `topk`, `jaccard`, `burden_capture`
  from `src/allergen_priority.py` (import, do not re-implement).

### 2.4 Street allocation (feasibility layer, top-K sections)
- For each top-K priority section, take its Platanus; derive street from `adreca` by stripping the
  house-number suffix (split on last comma) and normalising whitespace/case.
- Group by street → `n_planes`, `n_mature`, example tree `codi`s.
- `suggested_remove` per street = section quota × (street mature share), capped at `n_mature`.

---

## 3. Assumptions (declared, sensitivity-tested)

- **A1 — Mature set = {`EXEMPLAR`, `PRIMERA`}.** These are the large/specimen size classes (higher
  canopy → higher pollen yield). `SEGONA`/`TERCERA` are smaller classes. This is an **assumption**,
  tested as a T4 arm (broaden to include `SEGONA`; and a uniform-maturity arm where every plane counts
  equally). 1 Platanus row has a null category → counted as non-mature (reported).
- **A2 — City removal target (sourced, corrected 2026-06-09).** Pla Director de l'Arbrat 2017–2037
  (ElNacional / Beteve, May 2026): Barcelona has **43,722 Platanus = 27.45% of *total urban trees***
  (street + parks/forest), to be cut to **12% by 2037 → a ~56.3% reduction** of the plane stock
  (~24,500 city-wide). Two caveats make us drive the worklist off the **rate**, not a fixed count:
  (i) our `arbrat-viari.csv` is **street trees only** (40,444 planes), a subset of the 43,722; and
  (ii) the **city's stated primary rationale is biodiversity / monoculture disease-risk and climate
  resilience — *not* allergy** (allergy is politically salient but explicitly contextual; the Sant
  Jordi 2026 nuisance was the *fruit*, not spring pollen). So the street target =
  `(1 − 12/27.45) × street_plane_count ≈ 0.563 × 40,433 ≈ 22,757`, computed in code. It scales the
  *suggested* allocation only — a **policy input, not a finding**, swappable (`how_to_extend`). Framing:
  this product optimizes allergen-exposure relief as a **co-benefit** of a removal programme the city
  runs for other reasons.
- **A3 — Address = street identity.** `adreca` minus the house number identifies a street. Free-text;
  unmatched/garbled addresses are accepted and the street-match coverage % is reported, not hidden.

---

## 4. Pre-registered tests (re-run at section grain) — all MUST report

The shipped product passed T1–T4 at cell grain. The headline claim is that the product is deployable
at the *finer, native* grain. We re-run the same four tests so a grade can compare like-for-like.

| ID | Test | What it could break | Pre-registered pass criterion |
|----|------|---------------------|-------------------------------|
| **T1** | Does exposure re-order vs naive plane-density (source-only)? | If not, the product is just the city's existing "most planes first" rule. | top-15 Jaccard < 0.70 **AND** Spearman(priority, source) < 0.90 |
| **T2** | Redundancy — two material layers or one in a costume? | The exact Cycle-A failure mode (one variable masquerading as a composite). | \|corr(priority,source)\| ≥ 0.30 AND \|corr(priority,exposure)\| ≥ 0.30 AND \|corr(source,exposure)\| < 0.80 |
| **T3** | Burden captured by top-k vs density-only / random | Re-ordering must buy more exposure relief, not just move cells. | top-15 priority capture > density-only capture (positive margin) |
| **T4** | Sensitivity — does T1 survive perturbation? | Headline must not depend on arbitrary maturity/normalisation/aggregation choices. | T1 verdict holds under ≥2 of 3 arms (broad-mature, uniform-maturity, rank-normalised) |

**Plus two deployment-specific checks (declared here, reported in Results):**
- **C1 — grain sanity:** section count ≈ 1,068; population joined ≈ 1.73 M (matches `exposure_layer.py`
  city total); Spearman(section priority, old cell priority rolled up to section) **high but < 1**
  (finer signal, not noise or contradiction). Report the value either way.
- **C2 — honesty gate:** the street output file contains **no** priority/score column; only
  action/inventory/allocation fields. Grep-verified. Per-street `suggested_remove ≤ n_mature`
  everywhere; per-section street plane counts sum to the section `plane_count`.

---

## 5. Outputs
- `outputs/phase-6/section_priority.{parquet,csv,md,json}` (same writer convention as
  `allergen_priority.py`). The `.md` carries the T1–T4 + C1 verdicts.
- `outputs/phase-6/street_removal_actions.csv` (the deployable action list) +
  `street_removal_points.geojson` (tree points, for internal QA mapping only — not a published UI).
- Section choropleth `outputs/phase-6/maps/priority_section.html` is an **internal QA artifact**, not
  the deliverable (crispdm-6 skill: no published frontend).

---

## 6. Verification (run before declaring done)
- `python src/section_priority.py` → C1 asserts (section count, population total); T1–T4 verdicts
  printed (ASCII only — cp1252 console).
- `python src/street_actions.py` → spot-check one top section: per-street planes sum to section total;
  `suggested_remove ≤ n_mature` everywhere; coverage % printed.
- Honesty gate: confirm no priority/score column at street grain.

---

## Results

### section_priority.py (run 1068 sections)

**VERDICT: section-grain exposure largely redundant (honest limitation).**

- **C1:** 1068 sections; pop 1,729,963; rollup Spearman vs cell product 0.4669 (REVIEW).
- **T1:** Spearman 0.9701, top-15 Jaccard 0.5789 -> re-orders = False.
- **T2:** corr(source,exposure) 0.0866 -> both material = True.
- **T3:** top-15 burden margin over density-only 0.049.
- **T4:** {'broad_mature': False, 'uniform_maturity': False, 'rank_normalized': True} -> majority = False.

Full: `outputs/phase-6/section_priority.md`. (street results below)
### street_actions.py

- **C2 honesty gate PASSED:** street file carries no priority/score column; `suggested_remove <= n_mature` everywhere.
- Street-match coverage from free-text `adreca`: **100.0%**.
- Spot-check #1 section 03024 (Sants-Montjuic): per-street planes sum = 1840 = section plane_count 1840 (consistent).
- 401 street rows across the top-60 sections; total suggested removal 4636 planes (illustrative, A2 policy anchor).
- Output: `outputs/phase-6/street_removal_actions.csv` (worklist) + `street_removal_points.geojson` (QA map).


