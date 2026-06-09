# Conclusions Brief — Platanus Pollen-Allergen Priority (Cycle B) · TRACK B

> Track B's equivalent of a model card — a structured certificate that travels with the result
> so no one has to take our word for it. Structure mirrors Mitchell et al. (2019), adapted for a
> findings-based deliverable. Companion: `docs/validity-audit.md`, `outputs/model-card-allergen-v1.md`.

- **Analysis:** Barcelona plane-tree (*Platanus*) pollen-allergen exposure priority
- **Version:** v1.0 · 2026-06-09
- **Produced by:** Group 4 (Rafik El Khoury). Built with Claude Code (Opus 4.8).
- **Notebook:** `notebooks/05-evaluation.ipynb` · **Validity audit:** `docs/validity-audit.md`
- **Code:** `src/allergen_source.py`, `src/exposure_layer.py`, `src/allergen_priority.py`,
  `src/equity_layer.py` (deterministic, seed 42)

---

## 1 · The decision this serves

- **User:** capital-planning analyst at Ajuntament Espais Verds / Barcelona Regional (GIS-literate
  planner, not a mycologist or aerobiologist).
- **Decision:** in what **spatial order** to execute the already-decided plane-tree reduction
  (Pla Director de l'Arbrat 2017–2037, *Platanus* from ~27% to <12% of the street stock) so each
  removal relieves the most pollen-allergen exposure for residents.
- **Cadence / horizon:** a one-shot sequencing aid for a multi-year program; refresh on each
  inventory/population update or if measured pollen or mobility data appears.

---

## 2 · The data & systems it rests on

- **Sources (all existing, open or held):** Barcelona street-tree inventory (`arbrat`, ~230k
  trees → 494-cell 400 m grid); Padró Municipal 2026 residential population by census section
  (1,068 sections, 1.71M residents allocated, 99.1% of the city); INE Atlas gross income per
  person 2023 (deprivation); literature emission factors (Gabarra et al. 2002: *Platanus* ≈ 46%
  of Barcelona's annual pollen).
- **What we computed vs what was given:** we derived two transparent layers —
  source_std = `minmax(plane_count × maturity)` and exposure_std = `minmax(areal-weighted
  population)` — and their product. We did **not** train a predictor; this is a deterministic
  composite indicator (OECD/JRC 2008 family).
- **Coverage & gaps:** every district covered; residential receptors only (commuters/workers
  absent); 0.9% of population clipped at the municipal boundary; nothing below 400 m.
- **The out-of-sample slice:** *none exists* for the source layer — there is no open measured
  Barcelona Platanus-pollen series. This absence is the central limitation (see §4 #1), not a
  gap we can fill by holding data back.

---

## 3 · The claims

> **Claim 1:** Ranking cells by (mature-plane pollen source × residential exposure) materially
> re-orders the city's "remove where densest" rule and captures more modeled exposure relief per
> removal.
> - **Evidence:** Spearman(priority, source) = 0.89, top-15 Jaccard = **0.30** (≈70% of the
>   top-15 change). Modeled exposure-relief burden captured by the top-15 = **0.180** vs
>   density-only **0.134** vs random 0.030 → **margin +0.046** (top-50: +0.094).
>   `05-evaluation.ipynb` Cells B1, B3. Worked example: a Nou Barris cell (251 planes, 13,436
>   residents) outranks a Sant Martí cell (485 planes, 6,501 residents).
> - **Robustness:** holds under all three pre-registered perturbations (uniform maturity,
>   rank-normalization, min-aggregation) — 3/3.
> - **Threats ruled out:** confounding (corr(source, exposure)=0.30, near-independent — not one
>   variable in a costume); spurious (pre-registered thresholds, deterministic indicator);
>   cherry-picking (rejected layers reported, §3 Claim 3).
> - **Confidence & caveats:** ~75% for the *exposure re-ordering*; the source layer is an
>   un-validated emission proxy (see §4 #1). Limited to 400 m, city-wide, as a sequencing aid.

> **Claim 2:** An equity (deprivation) re-weight redirects priority toward the most-deprived
> income tercile at a small, **measured** efficiency cost.
> - **Evidence:** deprivation is decorrelated from both layers (corr −0.008 / 0.17 → genuine new
>   info). The v3 equity map lifts the most-deprived-tercile share of the top-15 from **40% → 60%**
>   while sacrificing **~0.5 pp** of total exposure relief (burden captured 0.180 → 0.175).
>   `05-evaluation.ipynb` Cell B4 / `outputs/phase-6/equity_results.md`.
> - **Robustness:** top-15 set Jaccard-stable 0.875 under a floored weight; 0.5 under a rank-based
>   weight (the tilt strength is a value dial).
> - **Threats ruled out:** confounding (income decorrelated from plane density by construction);
>   cherry-picking (both v1 and v3 reported; the trade-off number shown, not just the win).
> - **Confidence & caveats:** high for the *trade-off magnitude*; this is a **value choice**, not
>   a correctness choice — v1 (max total relief) and v3 (relieve the worst-off first) are both
>   valid; the planner chooses the objective.

> **Claim 3 (an honest negative — reported as a finding):** demographic refinements do not add
> mappable signal at this resolution.
> - **Evidence:** age-prevalence at-risk layer is redundant with plain population
>   (Spearman(at_risk, population) = **0.999**, top-15 Jaccard vs v1 = 0.875 → cannot re-order);
>   sex weighting — women receive **1.62×** the per-capita antihistamines of men, but the sex
>   ratio is ~constant across neighbourhoods, so it adds no spatial signal; bike-exposure was
>   rejected at design (no cyclist-volume data, no validation path). `05-evaluation.ipynb` Cell B4.
> - **Robustness:** the redundancy is structural (Barcelona's age/sex structure barely varies in
>   space), so it does not depend on a threshold.
> - **Threats ruled out:** this *is* the anti-cherry-picking evidence — we built/specified these,
>   they failed to help, and we report them.
> - **Confidence & caveats:** high that they don't re-order *spatially*; the epidemiology (women
>   more affected as adults) is real but answers a different question than the map.

---

## 4 · What we are NOT claiming

1. **Not claiming** the map is validated against measured pollen — it is a literature-anchored
   emission proxy (no open measured series exists). Central limitation.
2. **Not claiming** any health/allergy *outcome* — it ranks *exposure potential*, not diagnosed
   allergy or clinical impact.
3. **Not claiming** a decision on *whether* to remove planes — policy decides that; we sequence it.
4. **Not claiming** validity below 400 m or for within-cell siting (MAUP on grid + areal population).
5. **Not claiming** v1 is equity-adjusted (all residents equal); equity is the explicit v3 variant.
6. **Not claiming** the mycorrhizal mechanism that Cycle A rested on — it is *falsified* in this data.

---

## 5 · Ethical considerations & caveats

- **Whose neighbourhoods are represented?** Residents of high-priority cells (high plane density ×
  dense population) — Sant Martí, Eixample, Nou Barris feature prominently; the v3 variant
  explicitly elevates the most-deprived tercile.
- **Who is missing, and could the gap misdirect resources?** Commuters/workers (not in the
  residential layer); the 0.9% clipped at the edge; anyone below 400 m. A commuter-dominated axis
  could rank high on residents who are not its daytime receptors — declared as limitation L2.
- **Correlational, not causal** — a ranked priority list is a starting point for sequencing, not
  proof that a removal changes any measured outcome.
- **Snapshot** — tree inventory `2026_1T`, population Padró 2026, income 2023; re-run on refresh.

---

## Sign-off

- **Brief written by:** Group 4 (Rafik El Khoury)
- **Reviewed by another team:** pending (Session-5 cross-team review)
- **Reviewer feedback:** to land in `docs/evaluation-log.md`
- **Last updated:** 2026-06-09

---

## Appendix · How this brief is used downstream

- **Session 6 (deployment):** Claims 1–2 become the decision-facing output (two maps + the
  trade-off); §4 is what the output must caveat and refuse to over-read.
- **Session 7 (presentation):** open with Claim 1 + its confidence; §4 keeps you honest under
  questions.
