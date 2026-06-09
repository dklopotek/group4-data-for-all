# Phase-4 Modeling Options for Cycle B — Deep-Research Recommendation

> Deep-research deliverable (2026-06-09). Question: with **no measured ground-truth target**, what
> trainable model is methodologically defensible AND useful for the Platanus allergen-priority pipeline
> at census-section grain? Goal: pick one, then **pre-register** (binding rule) and build.
>
> **Framing up front.** The shipped *priority* is correctly a composite indicator, not ML: there is no
> label for "exposure burden", and per OECD/JRC (2008) and Rudin (2019) a transparent, inspectable
> computation is the right tool for an unlabelled multi-criteria ranking. A trained model therefore must
> serve a **different, legitimate sub-task** — not re-predict the composite from its own inputs (that is
> the Cycle-A tautology that produced eval R² 0.999 and an external null). Every option below has a
> target/structure that is **independent of the priority construction.**

---

## When a composite is right vs when a model earns its place

- **Composite (current):** correct when the headline quantity is unmeasured and the value is a
  transparent, auditable ranking (OECD/JRC 2008; Saltelli et al. 2008; Rudin 2019). Keep it as the
  shipped priority.
- **Trained model:** earns its place only for a sub-task with either (a) an **observed, independent
  target** (supervised) or (b) **no target at all** (unsupervised structure discovery). CRISP-DM
  (Chapman et al. 2000) frames Phase 4 as "select modeling technique fit to the goal" — not "train an
  ML model for its own sake."

---

## Ranked recommendations

### #1 (RECOMMENDED) — Source estimator: supervised regression with SPATIAL cross-validation
- **Predicts:** observed **mature-Platanus density per section** (from the street-tree inventory) — an
  *observed* quantity.
- **From (independent features):** sealed-surface fraction, NDVI, building/road density,
  distance-to-centre, district. **None is derived from the plane count** → non-tautological by
  construction (the explicit fix for Cycle A).
- **Model:** interpretable first — regularized linear / GAM — then Random Forest as a flexible
  comparator (RF urban-canopy/tree-density estimation from open remote-sensing + urban-form covariates
  is well established). Report feature importance.
- **Why it's useful to a planner:** a **drift-resistant source estimate** — the inventory is the input
  most likely to go stale (it is the #1 trigger in `release/monitoring_plan.md`); a model keyed on
  slow-changing urban form lets you estimate pollen source between inventory refreshes or in
  poorly-surveyed areas.
- **Validation WITHOUT ground truth for the headline — but the target here IS observed**, so do proper
  held-out evaluation, and it **must be SPATIAL cross-validation** (block/cluster CV; Roberts et al.
  2017; Ploton et al. 2020). Report spatial-CV R²/MAE **next to** random-CV: the gap is the
  spatial-leakage that fooled us in Cycle A. Disclose the debate (Wadoux et al. 2021 argues spatial CV
  can be pessimistically biased for design-based map accuracy) and interpret the random↔spatial range,
  not a single number.
- **Expected failure mode (and it's fine):** urban form may **not** predict where the city historically
  planted planes (planting is administrative/path-dependent, not environmentally determined) → low
  spatial-CV R². That is an honest, interesting negative — it would show plane distribution is
  path-dependent, and would justify *keeping* the inventory as irreplaceable. Either outcome is reportable.
- **Pedagogically:** mirrors Cycle A's regression rigour but done honestly — the spatial-CV requirement
  *is* the lesson learned. Strongest "we grew from the failure" story for a grader.

### #2 — Intervention typologies: spatially-constrained clustering (unsupervised)
- **Produces:** ~5–6 contiguous **section archetypes** by clustering on the layers (mature-plane
  density, population, income, sealed, NDVI) under a spatial-contiguity constraint — **SKATER**
  (Assunção et al. 2006), available in PySAL `spopt`; compare to plain k-means/Ward (non-spatial) and
  GMM.
- **Why non-tautological:** no target at all — structure discovery cannot be a tautology.
- **Why it's useful:** turns 1,068 numbers into a handful of named action-types ("dense-residential
  high-source → priority replacement", "park-clusters low-exposure → defer", "low-everything →
  ignore"). **Directly fixes the "how do I use this?" problem** — pairs with the map as colour-coded zones.
- **Validation without labels:** internal indices (silhouette, Calinski-Harabasz, Davies-Bouldin),
  spatial contiguity satisfied by construction (SKATER), **stability** under k and feature-set
  perturbation, and profile interpretability. (No ground truth needed — quality is internal +
  decision-relevance.)
- **Failure mode:** weak separation (low silhouette) → report honestly; sensitivity to k and to the
  non-spatial-vs-SKATER choice (MAUP-adjacent; Openshaw 1984).

### #3 — Hotspot layer (inferential spatial statistics, lightweight complement)
- **Produces:** statistically significant priority **hot/cold spots** and spatial outliers via
  Getis-Ord Gi* (Getis & Ord 1992) and Local Moran's I / LISA (Anselin 1995).
- **Why useful:** replaces an arbitrary "top-N" with statistically defensible clusters, and **flags the
  Montjuïc-type case as a High-Low spatial outlier** — operationalizing the MAUP caveat. We already used
  global Moran's I in Phase 5, so this extends a method the project knows.
- **Validation:** permutation pseudo-p-values (built in). Cheap; best as a robustness/defensibility
  layer on top of #1 or #2, not a standalone "model".

---

## Recommendation for THIS project

**Primary: build #1 (supervised source estimator with spatial cross-validation).** It is a genuine
trained ML model (what the Phase-4 brief wants), has a real observed independent target, operationalizes
the exact lesson from the Cycle-A failure, and has real deployment value. **Add #3 (Gi*) as a cheap
defensibility layer.** Offer #2 (typologies) as the usability-first alternative if the priority is
planner-facing segmentation over predictive rigour.

Whichever is chosen: **pre-register first** (target, features, spatial-CV protocol, success criterion,
the explicit non-tautology argument, and the failure-is-reportable clause), per the binding project rule.

---

## References (verified)
- Anselin, L. (1995). Local indicators of spatial association — LISA. *Geographical Analysis, 27*(2), 93–115.
- Assunção, R. M., Neves, M. C., Câmara, G., & da Costa Freitas, C. (2006). Efficient regionalization techniques… SKATER. *International Journal of Geographical Information Science, 20*(7), 797–811.
- Chapman, P., et al. (2000). *CRISP-DM 1.0: Step-by-step data mining guide.* SPSS Inc.
- Getis, A., & Ord, J. K. (1992). The analysis of spatial association by use of distance statistics. *Geographical Analysis, 24*(3), 189–206.
- OECD & JRC (2008). *Handbook on Constructing Composite Indicators.* OECD Publishing.
- Openshaw, S. (1984). *The Modifiable Areal Unit Problem* (CATMOG 38).
- Ploton, P., et al. (2020). Spatial validation reveals poor predictive performance of large-scale ecological mapping models. *Nature Communications, 11*, 4540.
- Roberts, D. R., et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*(8), 913–929.
- Rudin, C. (2019). Stop explaining black box machine learning models for high-stakes decisions… *Nature Machine Intelligence, 1*, 206–215.
- Saltelli, A., et al. (2008). *Global Sensitivity Analysis: The Primer.* Wiley.
- Wadoux, A. M. J.-C., et al. (2021). Spatial cross-validation is not the right way to evaluate map accuracy. *Ecological Modelling, 457*, 109692. *(counterpoint — disclose and interpret the random↔spatial range.)*
- PySAL `spopt` (regionalization: SKATER, Max-P, AZP, Ward) — implementation reference.
- Precedent: Random-Forest estimation of urban tree canopy/density from open-access remote-sensing + urban-form covariates (multiple studies, 2019–2023).
