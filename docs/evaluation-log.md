# Evaluation Log — Mycorrhizal Barcelona → Allergen Priority

> Every test run during evaluation, **including the ones that made the result look worse** —
> that is the point of a log: proof we went looking for problems, not for confirmation. A clean
> log with no negative findings means we didn't test hard enough. Each entry: what it tested (and
> why it could break the result), what it showed, what we concluded (held / weakened / killed),
> and what it changed in the verdict. All numbers reproduce in `notebooks/05-evaluation.ipynb`.

- **Track:** A (model, Cycle A) → B (conclusions, Cycle B)
- **Maintainer:** Group 4 (Rafik El Khoury)
- **Last updated:** 2026-06-09

---

## Cycle A — the mycorrhizal model

> **Test 1:** Baseline contest on the frozen test cluster
> - **Tested / why it could break:** does the model beat dumb/spatial/expert baselines on
>   held-out geography, or is the headline R² just bulk-average fitting?
> - **Showed:** test R² **0.877** vs best baseline −0.29; test MAE **0.0106** vs 0.130.
> - **Concluded:** **held** — model passes the pre-registered Phase-4 bar.
> - **Changed in verdict:** earned Cycle A the right to be evaluated in Phase 5 (a passing model
>   is the *precondition* for the kill being interesting).

> **Test 2:** Per-district residuals (OOD probe)
> - **Tested / why:** does error hide in a district? Aggregate MAE can mask a biased slice.
> - **Showed:** Sarrià mean|resid| 0.0174 (n=51), Les Corts 0.0011 (n=37); all districts < 0.10
>   gate; but one Sarrià cell residual **0.334** (32× the test MAE).
> - **Concluded:** **held at district level, weakened at cell level** — one spectacular outlier.
> - **Changed:** set the trustworthy-resolution floor (don't split cells < 0.03 apart);
>   model-card fragility note.

> **Test 3:** Drop-feature stress (all 10 features)
> - **Tested / why:** which feature actually carries the model? A production feature can go missing.
> - **Showed:** dropping `mean_sealed` → MAE **0.1205 (11×)**; dropping the 4 ecological/tree
>   features (`total_trees`, `trees_young_pct`, `species_richness`, `cell_vpa_score`) → **Δ ≈ 0**.
> - **Concluded:** **weakened the ecological story badly** — the model is a sealed-surface re-skin;
>   the ecological inputs are inert.
> - **Changed:** strong prior that the composite ≈ sealed surface → motivated the external test.

> **Test 4 (THE KILL):** External GBIF richness — does the biotic/host block add signal?
> - **Tested / why:** the only test that matters — against data the pipeline never saw, does the
>   ecological claim survive? Pre-registered pass: ΔAdj-R² ≥ 0.05 AND partial-F p < 0.05.
> - **Showed:** M0 abiotic Adj-R² 0.6972 → M1 + biotic 0.6777; **Δ −0.0195**, partial-F **p 0.989**.
> - **Concluded:** **KILLED** the mycorrhizal claim. The host/biotic layer adds no signal about
>   real fungal occurrence.
> - **Changed:** Cycle A verdict → **STOP**; triggered the pivot.

> **Test 5:** Presence logistic (secondary)
> - **Tested / why:** a parallel presence test (logistic, 5-fold CV).
> - **Showed:** CV-AUC **1.0** for both M0 and M1; LR p 0.99996.
> - **Concluded:** **uninformative / circular** — `gbif_present` ≡ `effort ≥ 1` and effort is a
>   covariate, so AUC=1.0 is mechanical.
> - **Changed:** explicitly **discounted** (dated addendum); the richness test carries the verdict.
>   (Catching "right for the wrong reason" is a passed check.)

> **Test 6:** Kill robustness — log-richness & drop-effort
> - **Tested / why:** does the null depend on the outcome transform or on the effort covariate?
> - **Showed:** log-richness partial-F p **0.57**; drop-effort partial-F p **0.54**.
> - **Concluded:** **kill holds** under both variants.
> - **Changed:** raised confidence in STOP from "one test" to "robust".

> **Test 7:** Moran's I on M1 residuals
> - **Tested / why:** is the null an artifact of unmodelled spatial autocorrelation?
> - **Showed:** I = **−0.047**, p = 0.21 (not significant).
> - **Concluded:** **held** — the FAIL is not a spatial-autocorrelation artifact.
> - **Changed:** closed the obvious "but spatial structure" objection.

> **Test 8:** VIF collinearity of the biotic block
> - **Tested / why:** are the "five components" five independent signals?
> - **Showed:** VIF `platanus_pct` 699, `prpi` 628, `am_pct`/`em_pct` ∞.
> - **Concluded:** **weakened the composite's premise** — the components are not independent; M1
>   coefficients are individually uninterpretable (but the block partial-F is still valid).
> - **Changed:** reinforced that the composite carries one signal (sealed), not five.

> **Test 9:** 24-spec sensitivity grid (composite rank-stability)
> - **Tested / why:** does the Phase-3 composite ranking depend on normalization/weighting/aggregation?
> - **Showed:** cells tagged ROBUST **321** / MODERATE 97 / FRAGILE **76** (of 494).
> - **Concluded:** **held moderately** — most cells stable, a non-trivial 76 fragile.
> - **Changed:** model-card robustness statement; fragile cells flagged.

> **Test 10:** Cronbach's α across the 4 sub-scores
> - **Tested / why:** internal consistency of the composite's sub-scores.
> - **Showed:** α = **0.599** (below the 0.7 convention).
> - **Concluded:** **weakened** — the sub-scores are not measuring one coherent construct.
> - **Changed:** further evidence the composite is a bundle, not a unified index.

> **Test 11:** Model stability — jackknife / noise / alt-seed / alt-cut
> - **Tested / why:** is the *model* itself stable (separate from whether it's valid)?
> - **Showed:** noise-injection test-R² **0.8761** (Δ −0.0008); alt-seeds 0.877/0.877/0.877;
>   alt-cut (drop largest district) 0.878.
> - **Concluded:** **held** — the model is stable. (Stability ≠ validity: a stable re-skin of a
>   confound is still invalid.)
> - **Changed:** prevented us from blaming the kill on instability — the problem is validity.

> **Test 12:** Construct validity (convergent / discriminant / face)
> - **Tested / why:** does the prediction converge on sealed and stay clear of richness; does the
>   top-15 match Phase-3's flagged cells?
> - **Showed:** convergent r(pred, sealed) **0.94**; discriminant r(pred, richness) 0.25; Jaccard
>   top-15 pred vs flag 0.36 (< 0.5).
> - **Concluded:** **confirmed** the model is essentially a sealed-surface measure.
> - **Changed:** sealed the interpretation behind STOP.

---

## Cycle B — the allergen priority product

> **Test 13 (T1):** Does exposure re-order vs naive plane-density?
> - **Tested / why:** if exposure doesn't re-order, the product is just the city's existing rule.
> - **Showed:** Spearman 0.89, top-15 Jaccard **0.30** (~70% of top-15 change).
> - **Concluded:** **held** — exposure materially re-orders.
> - **Changed:** criterion 1 → met.

> **Test 14 (T2):** Redundancy — two layers or one in a costume?
> - **Tested / why:** the exact Cycle-A failure mode (one variable masquerading as a composite).
> - **Showed:** corr(priority,source) 0.80, corr(priority,exposure) 0.64, corr(source,exposure) **0.30**.
> - **Concluded:** **held** — both layers material, inputs near-independent.
> - **Changed:** criterion 2 → met; structurally distinguishes Cycle B from Cycle A.

> **Test 15 (T3):** Burden captured vs density-only / random
> - **Tested / why:** does the re-ordering actually buy more exposure relief, or just move cells?
> - **Showed:** top-15 priority 0.180 vs density 0.134 vs random 0.030 → **margin +0.046**
>   (top-50 +0.094).
> - **Concluded:** **held** — beats the city's rule on its own objective.
> - **Changed:** criterion 3 → met.

> **Test 16 (T4):** Sensitivity — does T1 survive perturbation?
> - **Tested / why:** does the headline depend on arbitrary normalization/aggregation choices?
> - **Showed:** holds under uniform maturity, rank-normalization, min-aggregation — **3/3**.
> - **Concluded:** **held**.
> - **Changed:** criterion 4 → met.

> **Test 17 (V3-1):** Equity precondition — is deprivation decorrelated?
> - **Tested / why:** an equity weight is only worth adding if it carries new info.
> - **Showed:** corr(deprivation, source) **−0.008**, corr(deprivation, exposure) 0.17.
> - **Concluded:** **held** — genuine new information.
> - **Changed:** criterion 5 → met; justified building v3.

> **Test 18 (V3-3):** Equity–efficiency trade-off
> - **Tested / why:** quantify the cost of the equity tilt — don't sell it as free.
> - **Showed:** deprived-tercile share top-15 **40% → 60%** at a cost of **~0.5 pp** relief
>   (0.180 → 0.175).
> - **Concluded:** **quantified** — a near-free equity win, but a *value choice* not a correctness one.
> - **Changed:** both v1 and v3 shipped; planner chooses the objective.

> **Test 19:** At-risk (age-prevalence) layer — built then rejected
> - **Tested / why:** does weighting population by age-band allergy prevalence re-order?
> - **Showed:** Spearman(at_risk, population) **0.999**; top-15 Jaccard vs v1 0.875.
> - **Concluded:** **rejected** — redundant with population (age structure ~flat in space).
> - **Changed:** kept v1; reported as an honest negative (anti-cherry-picking).

> **Test 20:** Sex weighting — answered, not mapped
> - **Tested / why:** women receive 1.62× the antihistamines of men — does sex add a spatial layer?
> - **Showed:** the ratio is real city-wide but ~constant across neighbourhoods.
> - **Concluded:** **rejected** as a spatial layer — no mappable signal.
> - **Changed:** documented the epidemiology; no map change.

> **Test 21:** Bike-exposure layer — killed at design
> - **Tested / why:** cyclists are a high-ventilation receptor — worth a layer?
> - **Showed:** ~2–3% travel-mode receptor, no cyclist-volume data, no validation path.
> - **Concluded:** **rejected at design** (karpathy critique) before spending build effort.
> - **Changed:** scope discipline; documented.

> **Test 22:** Pollen validation — the un-closable one
> - **Tested / why:** can the SOURCE layer be validated against measured pollen?
> - **Showed:** **no open machine-readable Barcelona Platanus-pollen series exists.**
> - **Concluded:** **INFEASIBLE** — cancellation clause invoked, honest downgrade to a
>   literature-anchored proxy.
> - **Changed:** criterion 7 → un-evaluable; bounds Cycle-B confidence at ~75%; NOT-list #1.

---

## Cross-team review feedback (Session-5 block 03)

> _Reserved for the hostile-reviewer team's three bullets (per the Session-5 peer-review prompt)._

---

> **Discipline check:** every number in `docs/evaluation-report.md` has a backing entry above.
> 22 tests logged across both cycles; **3 killed/rejected a claim, 5 weakened one** — the log is
> not all-positive, by design.
