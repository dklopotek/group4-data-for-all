# Evaluation Report — Mycorrhizal Barcelona → Platanus Pollen-Allergen Priority

> CRISP-DM Phase 5 (Evaluation). One report, **both tracks** — because this project is a
> Track-A team whose evaluation *killed* the model (Cycle A), after which we pivoted to a
> Track-B analytical product (Cycle B). The kill is not an accident in the story; it is the
> story. Evidence notebook: `notebooks/05-evaluation.ipynb` (restart-run reproduces every
> number below). Skill-disciplined Go/Iterate/Kill memo: `phase-6/phase-5-audit.md`.

- **Track:** A (model) **→** B (conclusions from existing data). Dual, in sequence.
- **Maintainer:** Group 4 (Rafik El Khoury)
- **Last updated:** 2026-06-09
- **Verdict (one line):** **STOP** the mycorrhizal model (falsified on independent data, high
  confidence) → **SHIP ~75%** the allergen priority product (analytically), **deploy-pending**
  a stakeholder Monday-test deferred to Phase 6.

---

## 1 · The question & the success criteria (from Session 1)

The project pivoted, so there are two briefs and two bars.

**Cycle A — the original ecological claim** (`docs/problem-brief.md`).
- **The decision it served:** Barcelona Regional / Espais Verds planners ranking ~400 m zones
  for barrier-reduction capital (de-paving, cooling, planting, species selection), with the
  project's underlying motivation being **belowground mycorrhizal recovery** via AM→EM host
  replacement.
- **The load-bearing scientific criterion:** the host-mycorrhizal layer must carry real signal
  about belowground fungal outcomes. Criteria 1–7 in the brief are reproducibility / district
  coverage / ≤15-zone shortlist / planner-can-state-limits / green-axis sanity-check /
  peri-urban anchor / budget-line mapping — engineering gates. **None of them matters if the
  ecological signal is not real.**
- **The cost of being wrong:** capital routed to "fungal recovery" zones that are really just
  paved zones, sold under an ecological banner the data cannot support.

**Cycle B — the pivot** (`phase-6/phase-1-audit.md §B`), six pre-registered **numeric**
criteria, written before the build:

- **The decision it serves:** Espais Verds sequences the already-decided plane-tree reduction
  (Pla Director de l'Arbrat 2017–2037, 27%→<12%) so each removal relieves the most
  pollen-allergen exposure for residents.
- **The cost of being wrong:** mis-sequencing wastes budget and delays relief for the
  most-exposed (moderate — removal proceeds under policy regardless; the product only orders it).

| # | Success criterion (Cycle B, S1) | How it's measured | The bar |
|---|---|---|---|
| 1 | Exposure re-orders vs naive plane-density | top-15 Jaccard & Spearman(priority, source) | J15 < 0.70 **and** ρ < 0.90 |
| 2 | Both layers material; inputs not collinear | corr(priority,·); corr(source,exposure) | each ≥ 0.3; cross < 0.8 |
| 3 | Beat density-only on burden captured | Σ priority over top-k, vs density-only | margin > 0 at top-15 |
| 4 | Verdict survives perturbation | T1 under 3 perturbations | all hold |
| 5 | Equity precondition (deprivation decorrelated) | corr(deprivation, source/exposure) | \|r\| < 0.7 from both |
| 6 | Failure-and-pivot documented | file check | exists on disk |

---

## 2 · Result vs criteria

**Cycle B (the shipped product) — 6 of 6 build criteria met; 1 further criterion un-evaluable.**

| # | Criterion | Target | Result | Verdict | Evidence |
|---|---|---|---|---|---|
| 1 | Exposure re-orders vs density | J15<0.70 & ρ<0.90 | J15 **0.30**, ρ **0.89** | **met** | NB Cell B1 / T1 |
| 2 | Both layers material, not collinear | ≥0.3 / ≥0.3 / <0.8 | **0.80 / 0.64 / 0.30** | **met** | NB Cell B2 / T2 |
| 3 | Beat density-only on burden (top-15) | margin > 0 | priority 0.180 vs density 0.134 → **+0.046** | **met** | NB Cell B3 / T3 |
| 4 | Verdict survives perturbation | 3/3 hold | **3/3** (uniform maturity, rank-norm, min-agg) | **met** | NB Cell B3 / T4 |
| 5 | Equity precondition (decorrelation) | \|r\|<0.7 both | **−0.008 / 0.17** | **met** | NB Cell B4 / V3-1 |
| 6 | Failure-and-pivot documented | on disk | `docs/failure-and-pivot.md` | **met** | file |
| 7 | SOURCE validated vs measured pollen | any open series | **no open data exists** | **unmet — un-evaluable** | design §0 |

**Summary:** the allergen product meets every criterion it *can* be tested against; the seventh
(measured-pollen validation) is un-evaluable by absence of data — itself a reported Phase-5
outcome, not an escape hatch.

**Cycle A (the model) — passed Phase 4, failed Phase 5.**

| Claim | Target | Result | Verdict | Evidence |
|---|---|---|---|---|
| Model beats baselines on held-out cluster | beat all 3 on test R² & MAE | R² **0.877** vs −0.29; MAE **0.0106** vs 0.130 | **met (Phase 4)** | NB Cell A1 |
| Biotic/host layer carries real ecological signal | ΔAdj-R² ≥ 0.05 & partial-F p<0.05 on external GBIF | Δ **−0.0195**, p **0.989** | **FAILED** | NB Cell A4 |

The model is technically excellent and ecologically empty. Winning the Phase-4 contest and
still failing Phase 5 is the entire lesson.

---

## 3 · Compared to what

- **Cycle A — model vs baselines / vs the null.** On the test cluster the linear model
  (R² 0.877) beats spatial-nearest (−0.29), mean (−0.62) and the domain heuristic (−0.62) — a
  decisive Phase-4 win. But against the **external null** (abiotic-only model of independent
  GBIF richness) the biotic block adds nothing: ΔAdj-R² −0.0195, partial-F **p = 0.989**. "We'd
  have hoped the host layer adds signal; it adds none." This *overturns* the prior.
- **Cycle B — product vs the city's implicit rule.** The city's implicit rule is "remove where
  planes are densest." Accounting for people changes **~70% of the top-15** (top-15 Jaccard
  0.30) and captures **+0.046 more modeled exposure burden at top-15** (+0.094 at top-50) than
  density-only — and far above random (0.030). *Worked example:* a **Nou Barris** cell with
  **251 planes and 13,436 residents** (priority 0.490, rank 1) outranks a **Sant Martí** cell
  with **485 planes but 6,501 residents** (0.463, rank 2). Density-only would invert them.
- **Effort vs value.** Cycle A: high engineering effort, zero ecological value — correctly
  stopped. Cycle B: near-zero marginal cost (same data, two transparent layers), real decision
  value — worth shipping with its caveat.

---

## 4 · Where it fails

**Track A — `docs/failure-gallery.md` (summary).** Five+ documented failures of the model:

| Failing slice / case | Metric there | Diagnosis | One-off or systematic |
|---|---|---|---|
| External GBIF target (the kill) | ΔAdj-R² −0.0195, p 0.989 | host/biotic block adds no signal about real fungal richness | **systematic** (whole claim) |
| Drop `mean_sealed` (stress) | MAE 0.0106 → **0.1205 (11×)** | the model is a sealed-surface re-skin; one feature carries it | systematic |
| Drop any biotic/tree feature | MAE **unchanged** (Δ≈0) | ecological features carry ≈0 weight — they don't do anything | systematic |
| Sarrià outlier cell | residual **0.334** (32× the test MAE) | one wealthy-NW cell the linear fit cannot place | spectacular (one cell) |
| Eval→test generalization | MAE **6×** (0.0017→0.0106) | calibration depends on the geographic distribution used to normalize | systematic |

**Track B — `docs/validity-audit.md` (summary).**

| Threat | Present? | Ruled out by | Residual risk |
|---|---|---|---|
| Confounding (sealed surface drives source *and* exposure) | partial | T2: corr(source,exposure)=0.30, near-independent | residential≠daytime exposure (L2) |
| Selection bias (who's missing) | yes | declared: non-residents/commuters, 0.9% clipped at municipal edge | mobility data would close |
| Spurious correlation | no | question pre-registered before result; T1/T2 binding | — |
| Cherry-picking | no | rejected layers (age, sex, bike) **reported**, not hidden | — |

---

## 5 · Confidence

- **Cycle A (STOP) — high confidence.** The kill is triangulated, not a single test:
  external null (partial-F p **0.989**), robust to log-richness (p 0.57) and drop-effort
  (p 0.54), residuals not spatially autocorrelated (Moran's I −0.047, p 0.21); internal
  diagnostic shows the composite ≈ sealed surface (convergent r(pred,sealed) **0.94**); and a
  44-source literature review finds the lever weak-to-unsupported. The model itself is *stable*
  (noise-injection test-R² 0.876, Δ −0.0008; alt-seeds 0.877/0.877/0.877) — stability is not the
  problem; validity is.
- **Cycle B (SHIP) — ~75% analytical confidence.** All four pre-registered tests pass and
  survive 3/3 perturbations; the bound is the one un-closable limitation — the SOURCE layer is a
  literature-anchored emission proxy, **not** validated against measured pollen (none exists
  open). The product claims *exposure*, not clinical outcome, so the proxy gap is disclosed, not
  dressed up.
- **Conditions:** trustworthy at 400 m, city-wide, as a *sequencing* aid; not trustworthy below
  400 m, for within-cell siting, or as health evidence.

---

## 6 · What we are NOT claiming

1. **NOT** validated against measured pollen — the source layer is a literature-anchored
   emission proxy (Gabarra et al. 2002: *Platanus* ≈ 46% of Barcelona's annual pollen). Central
   limitation, stated plainly.
2. **NOT** a health/allergy *outcome* predictor — it ranks *exposure potential*, not diagnosed
   allergy or clinical impact.
3. **NOT** a decision on *whether* to remove plane trees — city policy already decides that;
   this only sequences it.
4. **NOT** valid below 400 m nor for within-cell siting — grid + areal population both carry the
   Modifiable Areal Unit Problem.
5. **NOT** a claim that the AM→EM mycorrhizal mechanism holds — it is here **falsified** in this
   data, at this resolution, with these proxies.
6. **NOT** equity-adjusted in v1 (all residents weighted equally); equity is the explicit,
   co-reported v3 variant.

---

## 7 · Recommendation — deploy / iterate / stop

- **Cycle A verdict: STOP.** The ecological signal is not in the data and the data we have
  cannot put it there. Documented reason: claim falsified on independent data
  (`outputs/phase-5/external_validation_results.md`). We did not relabel a sealed-surface map as
  a fungal one.
- **Cycle B verdict: SHIP (~75%), DEPLOY-PENDING.**
  - **Because:** six of six build criteria met with file-backed, reproducible evidence; survives
    every sensitivity perturbation; honest about its one un-closable limitation; beats the city's
    current implicit rule on the city's own objective.
  - **Confidence:** ~75% analytical; deployment gated, not granted.
  - **The two open gates (Phase 6, by design):** (1) a real Espais Verds analyst's Monday-test —
    *would they act on this output, in front of colleagues, without further work?*; (2) an
    independent second-operator reproduction on a clean machine. Both are deployment-readiness
    checks, **not** analytical defects (`phase-6/phase-5-audit.md §3, §8`).
  - **What S6 should show:** the two maps (efficiency v1 + equity v3) and the trade-off number,
    aggregated to the section/axis procurement unit. **What S6 must hide / refuse:** any
    measured-pollen or clinical reading of the map; any sub-400 m siting claim — the NOT-list
    must travel with every output.

---

## Sign-off

- **Evaluated by:** Group 4 (Rafik El Khoury). Built with Claude Code (Opus 4.8).
- **Reviewed by another team:** pending (cross-team hostile review, Session-5 block 03) — feedback
  to land in `docs/evaluation-log.md`.
- **Reproducible:** a fresh clone + restart-run of `notebooks/05-evaluation.ipynb` on the
  `hermes-agent` kernel reproduces every number in this report — **yes** (verified 2026-06-09).

---

## Appendix · How this report is used downstream

- **Session 6 (deployment):** this report is the spec for the decision-facing output — the
  verdict is the headline; section 6 (NOT-list) is what the UI must refuse to show; the two open
  gates in section 7 are the Phase-6 agenda.
- **Session 7 (presentation):** open with the verdict sentence (top of this file). Two core
  slides: section 2 (result vs criteria, both cycles) and section 4 (where it fails — the kill).
