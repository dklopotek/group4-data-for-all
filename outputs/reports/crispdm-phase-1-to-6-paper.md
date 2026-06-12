# CRISP-DM Phase 1 → 6: From a Falsified Mycorrhizal Thesis to a Defensible — and Deployed — Platanus Pollen-Allergen Exposure Priority for Barcelona

**A methodological case study in honest data-product evaluation and deployment**

**Group 4** — MaAI01 25-26, CRISP-DM seminar
**Status:** Sessions 1–6 complete (Business Understanding through Deployment). Full CRISP-DM cycle closed; stakeholder sign-off and independent reproduction remain open organizational gates.
**Version:** 2.0 · 2026-06-09
**Canonical context document.** This paper is the authoritative narrative of the project to date; all phase artifacts referenced here live in the project repository (see Appendix B).

---

## Abstract

Most student data-science projects report a result that flatters the system they built. This one does not. We set out to build a spatial priority map telling Barcelona's urban-greening planners where intervention would best support the recovery of soil mycorrhizal-fungal networks, using the replacement of plane trees (*Platanus × acerifolia*) with ectomycorrhizal host species as the operative lever. We carried that thesis through four CRISP-DM phases to a linear model that reproduced end-to-end at a held-out R² of 0.877 and was judged the most methodologically mature Phase 4 in the cohort. Then the Evaluation phase did its job and falsified the thesis on three independent lines of evidence: the headline composite was 91% explained by sealed-surface fraction alone, with the ecological components carrying near-zero effective weight; a pre-registered external test against 1,024 independent fungal occurrences found that the biotic and host layers added no signal beyond an abiotic null (partial-F *p* = 0.99); and a 44-source literature review found the host-mismatch lever weak-to-unsupported, with direct counter-evidence from comparable cities. Rather than relabel a sealed-surface map as a fungal one, we stopped the mycorrhizal claim and pivoted to a question the same data could answer and that maps onto a standing city policy: where to sequence Barcelona's committed plane-tree reduction so that each removal relieves the most pollen-allergen exposure for residents. The pivoted product ran its own full CRISP-DM cycle. It is a deliberately transparent two-layer composite indicator — pollen-source intensity multiplied by residential exposure — that re-orders priorities relative to the city's implicit "remove where planes are densest" rule (Spearman 0.89, top-15 Jaccard 0.30), is demonstrably non-redundant (both layers materially move the ranking), captures more modeled exposure burden per removal than the naive rule (+4.6 points in the top 15), and survives every pre-registered sensitivity perturbation. An equity variant that re-weights by neighborhood deprivation lifts the most-deprived-tercile share of top priorities from 40% to 60% at a measured cost of roughly 0.5 percentage points of exposure relief. Three candidate layers (age-prevalence, sex, cycling exposure) were auditioned and honestly rejected for adding no mappable, non-redundant signal. We argue the project's strongest output is not the tool but the falsification: a documented, pre-registered hypothesis death is the clearest demonstration of the CRISP-DM iteration loop the course teaches, and the discipline that produced it — never validate an index against its own ingredients, distinguish nominal from effective weights, make a layer earn its place, and downgrade honestly when validation data is absent — now governs the shipped product. Deployment (Phase 6) carried the product to an actionable form — a per-street plane-removal worklist aggregated to the city's native census-section grain — and surfaced one further honest negative: at that finer grain the exposure layer's re-ordering power washes out (a few park-like sections with huge mature-plane clusters dominate), a textbook Modifiable Areal Unit Problem we measured in our own output rather than hid. We ship both grains with the caveat explicit. The full six-phase cycle is closed; the only remaining gates — a real decision-maker's sign-off and an independent reproduction — are organizational, not analytical.

**Keywords:** CRISP-DM; composite indicators; data-product evaluation; pre-registration; falsification; urban aerobiology; *Platanus*; spatial prioritization; equity weighting; environmental data science

---

## Resumen (Español)

La mayoría de los proyectos estudiantiles de ciencia de datos presentan un resultado que favorece al sistema construido. Este no. Nuestro objetivo inicial era un mapa de prioridad espacial para indicar a los planificadores del verde urbano de Barcelona dónde intervenir para favorecer la recuperación de las redes micorrícicas del suelo, usando como palanca la sustitución de plátanos de sombra (*Platanus × acerifolia*) por especies hospedadoras ectomicorrícicas. Llevamos esa tesis a través de cuatro fases CRISP-DM hasta un modelo lineal con R² de validación de 0,877. Entonces la fase de Evaluación falsó la tesis en tres líneas independientes: el indicador compuesto estaba explicado en un 91% por la superficie sellada; una prueba externa preregistrada contra 1.024 ocurrencias fúngicas independientes no halló señal biótica alguna (*p* = 0,99); y una revisión de 44 fuentes encontró la palanca débil o no respaldada. En lugar de reetiquetar un mapa de superficie sellada como uno fúngico, detuvimos la afirmación micorrícica y pivotamos hacia una pregunta que los mismos datos sí podían responder y que se alinea con una política municipal vigente: en qué orden secuenciar la reducción ya comprometida de plátanos para que cada tala alivie la mayor exposición posible al polen alergénico de los residentes. El producto pivotado es un indicador compuesto transparente de dos capas (intensidad de fuente de polen × exposición residencial) que reordena las prioridades frente a la regla ingenua de la ciudad (Spearman 0,89; Jaccard top-15 de 0,30), no es redundante, captura más carga de exposición por tala (+4,6 puntos en el top-15) y sobrevive a todas las perturbaciones de sensibilidad preregistradas. Sostenemos que la mayor aportación del proyecto no es la herramienta sino la falsación: una muerte de hipótesis documentada y preregistrada es la demostración más clara del bucle iterativo de CRISP-DM. La evaluación analítica está completa; la preparación para el despliegue es la tarea de la Sesión 6.

**Palabras clave:** CRISP-DM; indicadores compuestos; evaluación; preregistro; falsación; aerobiología urbana; *Platanus*; priorización espacial; equidad

---

## 1. Introduction

### 1.1 The problem we were asked to solve

Barcelona, like many dense Mediterranean cities, manages a large public street-tree stock as a capital asset. Decisions about that stock — which species to plant, which to remove, in what order, on a finite annual budget — are made by planners at the municipal greening administration (Espais Verds) and its planning partners. The seminar's premise was to build a data product that makes one such decision better, following the CRISP-DM reference process (Chapman et al., 2000) end-to-end across six sessions, from Business Understanding to Deployment.

Our original decision target was ecological. Urban soils host mycorrhizal-fungal networks — symbioses between fungi and tree roots that condition soil and connect trees belowground. We proposed to rank Barcelona's territory for where intervention would most support the recovery of those networks, and we encoded a specific mechanism: street trees differ in mycorrhizal type (arbuscular, AM, versus ectomycorrhizal, EM), and replacing the dominant AM-associating plane tree with EM hosts would, we hypothesized, reduce a host–fungal "mismatch" and aid network recovery.

This paper is the record of what happened to that hypothesis, and of what we built instead. It is written for two audiences who will read it differently: colleagues who need the technical detail to extend or reproduce the work, and the seminar instructor for whom it is the project's defense. We have written it to satisfy both without softening the parts that are unflattering, because the unflattering part is the point.

### 1.2 The twist: we falsified our own thesis

At Session 5 (Evaluation), the mycorrhizal thesis failed. It failed not because of a coding error or a missing dataset but because the claim was not in the data and the data we had could not put it there. We document the three independent lines of evidence in Section 4. The short version: our headline index turned out to rank cells by how much sealed (paved) surface they contained, the ecological signal we cared about had been weighted into irrelevance, and an external test against data the index had never seen returned a flat null.

The decision at that point was a genuine fork. We could have relabeled the index — it produced a plausible-looking map, the script ran, the instructor had praised the engineering — and shipped it. Instead we stopped the ecological claim and iterated to a different question. This is not a defeat dressed up as a lesson. The CRISP-DM literature is explicit that the process is iterative and that evaluation exists precisely to catch a technically successful model that fails to serve the business objective (Chapman et al., 2000; Martínez-Plumed et al., 2021; Studer et al., 2021). A pre-registered hypothesis that is honestly falsified is a result, and arguably a stronger one than a flattering number that means nothing.

### 1.3 What we built instead

The pivot kept what the data and the literature genuinely support and dropped what they do not. Plane trees stay central — not because of a contested fungal mechanism, but because *Platanus* is the single largest contributor to Barcelona's airborne pollen, responsible for roughly 46% of the annual pollen index, with a sharp spring season (Gabarra et al., 2002). Barcelona already has a standing policy — the *Pla Director de l'Arbrat 2017–2037* — to cut plane trees from 27.45% to under 12% of the **total urban-tree** stock (43,722 planes today; a ~56% reduction). Its stated primary rationale is biodiversity and monoculture disease-risk, not allergy; but the reduction will happen anyway, tree by tree, over years. The new decision is not *whether* to remove planes but *in what spatial order*, so that each removal buys the most pollen-allergen-exposure relief for the people who live there — an allergen co-benefit layered on a programme the city runs for other reasons.

The resulting product is a transparent composite indicator: a pollen-source layer (how many mature plane trees a cell holds) multiplied by an exposure layer (how many residents live there), reported alongside a feasibility annotation and an optional equity re-weighting. It is deliberately the structural opposite of the failed predecessor, and Section 6 explains why that structure is a direct response to the failure's root causes.

### 1.4 Contributions

This paper makes five methodological contributions, none of them a new algorithm:

1. **Failure-as-result.** We present a fully documented, pre-registered falsification of a project's central hypothesis as its primary scientific output, and as the clearest available demonstration of the CRISP-DM iteration loop.
2. **The anti-tautology discipline.** We show concretely how validating a composite index against its own ingredients manufactures a meaningless success, and how an external pre-registered test exposes it.
3. **Nominal versus effective weights.** We give a worked case in which declared (nominal) weights bear no relation to the weights that actually drive the ranking, because one high-variance component dominates a compensatory aggregation.
4. **The layer-audition honesty gate.** We propose and apply a simple rule for whether a candidate layer earns inclusion: it must both re-order the output and add non-redundant information. We audition five layers against it and report three rejections.
5. **Honest downgrade under missing validation data.** When the data needed to validate a layer does not exist, we downgrade the claim and label the proxy as a proxy, rather than inventing validation.

The remainder of the paper is organized around the two CRISP-DM cycles. Section 2 sets background. Sections 3–4 cover the mycorrhizal cycle and its falsification. Section 5 covers the pivot decision. Sections 6–7 cover the allergen cycle and its evaluation. Section 8 covers deployment (Phase 6) and its grain-dependence finding. Sections 9–11 discuss, bound, and conclude the work.

---

## 2. Background and Related Work

### 2.1 CRISP-DM as the governing process

The Cross-Industry Standard Process for Data Mining (Chapman et al., 2000) structures a data project into six phases — Business Understanding, Data Understanding, Data Preparation, Modeling, Evaluation, and Deployment — with explicit, expected iteration between them. Two decades of practice have surfaced both its durability and its weak points: the most common failure mode in surveyed applications is not technical but definitional, projects that build what was asked rather than what was needed (Martínez-Plumed et al., 2021). The quality-oriented extension CRISP-ML(Q) adds explicit quality-assurance tasks at every phase and, importantly for this project, requires a *cancellation criterion* — a written condition under which the project would be stopped — as a Phase 1 artifact (Studer et al., 2021). We treat that requirement as binding, and Section 5 shows the cancellation criterion actually firing.

A point the reference guide makes that is easy to miss: Phase 4 (Modeling) and Phase 5 (Evaluation) are different activities with different audiences. Phase 4 asks, technically, *did the model work?* Phase 5 asks, against the business objective, *does this output answer the decision-maker's actual question in a form they can act on?* (Chapman et al., 2000, pp. 28, 30). Conflating the two is the founding sin of careless CRISP-DM practice, and it is exactly the sin our mycorrhizal cycle committed in Phase 4 and our evaluation caught in Phase 5.

### 2.2 Composite indicators and their validation

Both of our analytical cores are composite indicators, not machine-learned models. The gold-standard methodology is the OECD/JRC *Handbook on Constructing Composite Indicators* (OECD & JRC, 2008; see also Nardo et al., 2005), which lays out a ten-step process whose last steps — uncertainty and sensitivity analysis — are the ones most often skipped and the ones where defensibility lives. Saisana, Saltelli, and Tarantola (2005) demonstrate that the normalization, weighting, and aggregation choices in a composite are not preprocessing details but substantive analytical decisions that can flip rankings; Saltelli et al. (2008) provide the variance-based methods for testing robustness to them. A recurring and underappreciated hazard, central to our failure, is the gap between *nominal* weights (the numbers the analyst declares) and *effective* weights (the influence each component actually exerts on the ranking), which diverge sharply when one component has much higher variance than the others in a compensatory (additive) aggregation.

For reporting, we adopt the model-card template (Mitchell et al., 2019) adapted for a non-machine-learned analytical product, and the datasheet conventions for the underlying data (Gebru et al., 2021). Rudin's (2019) argument for interpretable models in high-stakes settings underpins our choice to keep the product a transparent, inspectable computation rather than a learned black box.

### 2.3 The spatial dimension and its traps

Both cycles aggregate to a 400 m analysis grid, which raises the Modifiable Areal Unit Problem: results are conditional on the chosen zoning and scale, and can change under a different partition (Openshaw, 1984). We declare this rather than hide it. Population and income, reported at irregular census sections, are interpolated to the grid by area- and population-weighting respectively, because a count and a rate require different interpolation logic. Leakage of test-set information into training — endemic in ML-based science (Kapoor & Narayanan, 2023) — is a non-issue for the pivoted product because it is an indicator computed once over the complete fixed population of cells, with no held-out inference; we make that argument explicitly in Section 6 so a reader does not mis-flag the standardization step.

### 2.4 Urban aerobiology of *Platanus* in Barcelona

The pivot rests on an established fact base. *Platanus* pollen dominates Barcelona's aeroallergen load: Gabarra et al. (2002) report it at roughly 46% of the annual pollen index over 1994–2000, concentrated between mid-March and April, with peak daily concentrations in the thousands of grains per cubic metre. Maya-Manzano et al. (2017) quantify per-inflorescence emission on the order of millions of grains and locate a clinical symptom threshold around 50 grains m⁻³ in sensitized individuals, and frame urban planning as a legitimate prevention tool. European adult allergic-rhinitis prevalence is on the order of 23% (Bauchau & Durham, 2004), and a Barcelona sensitization figure of about 37% to *Platanus* among the pollen-allergic is used in the project's demographic exploration (sourced in the repository's data provenance record). Critically for our honesty constraint, no openly downloadable, machine-readable, station-level *Platanus* pollen time series with coordinates exists for Barcelona; the regional aerobiology network publishes only a current 0–4 forecast level. This absence determines the boundary of what the product can claim, as Section 6.2 details. One disambiguation, because the public debate conflates them: the plane tree produces two distinct seasonal nuisances — allergenic **pollen** in March–April (what our source layer proxies) and, later, the dry **fruit** that disaggregates into fine achene fibres (the highly visible *Sant Jordi*, late-April, irritant that drove the 2026 headlines). Removing a mature plane reduces both, but they are different mechanisms in different weeks; our exposure claim is about pollen, and we do not conflate it with the fruit-fibre episodes.

---

## 3. Cycle A — Mycorrhizal Barcelona (Phases 1–4)

### 3.1 The thesis and the build

The first cycle framed the decision as: where, on Barcelona's 400 m grid, would intervention best support mycorrhizal-network recovery, for a capital-planning analyst allocating greening budget. We operationalized "support recovery" through a five-component composite, `composite_score_B`, combining a host-mismatch sub-score (`s4_mismatch`), a Platanus Replacement Priority Index (`prpi`), and abiotic and structural terms, under three weighting scenarios with a top-15 priority flag.

The engineering was genuinely careful. A deterministic ETL turned a street-tree inventory of roughly 189,000–230,000 trees into a 494-cell scored grid carrying mycorrhizal composition (assigned by genus via the FungalRoot trait database; Soudzilovskaia et al., 2020), species richness, and satellite-derived features. We pre-registered a Phase-4 test design *before* building, used a spatial-cluster train/evaluation/test split to avoid the spatial-autocorrelation leakage that naive random splits cause, fitted three baselines and one tuned hyperparameter, and trained a linear model that reached a held-out R² of 0.877, beat every baseline, and reproduced end-to-end. The instructor's review called it the most methodologically mature Phase 4 in the cohort. We stress this because **the craft is not what failed.** A rigorous Phase 4 can sit on top of a hollow Phase 5 question, and ours did.

### 3.2 The latent flaw

The flaw was structural and present from Phase 3, though invisible until Phase 5. The model's headline number, the test-set R², measured how well raw features predicted a composite *built from those same features*. In-distribution, that relationship is close to arithmetic rather than empirical; the only non-trivial quantity, the held-out gap, turned out to measure how stable our normalization constants were across space, not anything about Barcelona's fungi. We had, without realizing it, validated a tautology.

---

## 4. The Evaluation that Falsified the Thesis (Cycle A, Phase 5)

Three independent lines of evidence converged on one conclusion. Each was documented and committed before the next was run.

### 4.1 Internal redundancy: a sealed-surface map in costume

We interrogated our own committed data. `composite_score_B` is 91% explained by impervious (sealed) surface fraction *alone* (R² 0.91, *r* 0.95), and 99.9% by a linear combination of its own raw inputs. The two components carrying the ecological thesis contributed almost nothing to the ranking: the correlation of the final score with the host/fungal mismatch component was −0.015, and with the Platanus Replacement Priority Index +0.18, against +0.95 for sealed surface. A planner ranking cells by our headline would have been ranking them, in effect, by how grey each cell is. This is the nominal-versus-effective-weight hazard (Section 2.2) made concrete: our declared weights distributed importance across five components, but one high-variance component decided the order regardless.

### 4.2 External falsification: the pre-registered null

The internal finding could be dismissed as an artifact of our own construction, so we asked the question Phase 4 should have asked. Against an external fungal outcome the composite had never used — 1,024 geo-located fungal occurrences from GBIF — do the biotic and host layers add any signal beyond an abiotic null (sealing, greenness, and sampling effort)? The design and code were committed *before* the result. The verdict was a clean FAIL: the biotic/host block added nothing, with a richness change in adjusted R² of −0.02 and a partial-F *p* of 0.99, robust under every alternative specification we tried. We disclosed our own design flaws in that test, including a circular presence component we caught and discounted ourselves.

### 4.3 Literature: the lever was never well-supported

A 44-source critical review found the AM→EM host lever weak-to-unsupported in cities; identified a sealed-surface and greenness axis that explains the large majority of arbuscular-mycorrhizal richness variance in a comparable European city; and surfaced direct counter-evidence to our premise, including a finding that plane-tree fungal diversity *increased* with urbanization in Amsterdam — the opposite of what our mechanism assumed.

### 4.4 Root causes

Four causes, stated plainly so future projects can avoid them:

- **We validated a tautology.** An index tested against its own ingredients returns arithmetic, not evidence.
- **The signal was weighted into irrelevance.** Nominal weights are not effective weights; one dominant high-variance component decides a compensatory ranking.
- **The mechanism was assumption, not measurement.** Mycorrhizal types came from a genus-level trait-table fallback, not local soil sampling, and the improvement direction was never demonstrated and is contradicted by the best urban evidence.
- **The data could not carry the claim.** Opportunistic occurrence data at 400 m is a coarse probe, and we had no measured local soil-fungal outcome.

The decision, in the Phase-5 vocabulary of deploy / iterate / stop, was to **stop the mycorrhizal claim and iterate to a new question**, at roughly 75–80% confidence — bounded by the coarseness of the external data, since a finer fungal dataset could in principle surface a signal this one cannot. The fungal ambition was not deleted; it was retained as a stated, here-falsified hypothesis for a future project with measured soil data.

---

## 5. The Pivot: Rationale and Decision

The pivot was a deliberate, documented decision, not a quiet relabeling. We chose a new question against three criteria: it had to be decision-relevant (tied to an action someone actually takes), it had to keep what was real in the original work, and the data had to be able to carry it.

The *Pla Director de l'Arbrat 2017–2037* provided the decision. The city is already committed to reducing plane trees from 27.45% to under 12% of the **total urban-tree** stock (43,722 specimens, a ~56% cut), under a rule that no single species exceed 15% of the stock. The Ajuntament frames this primarily as biodiversity and monoculture-risk management, not allergy; we take the *removal* as given and supply only the *sequencing*, for which allergen-exposure relief is a defensible co-benefit objective. That sequencing is a real, budget-constrained, multi-year choice with a public-health upside. *Platanus* allergenicity is the property of plane trees that the data and the literature genuinely support (Gabarra et al., 2002; Maya-Manzano et al., 2017), in contrast to the contested fungal mechanism. And the inputs the new question needs — plane locations and maturity, residential population, deprivation — are all real and available, whereas the inputs the old question needed were not.

The cost of being wrong in the new framing is moderate and asymmetric: mis-sequencing wastes budget and delays relief for the most-exposed, but causes no direct harm, since removal proceeds under policy regardless. Over-claiming a health benefit we could not support would damage credibility, which is precisely the lesson from the failure. The product therefore claims *exposure*, not clinical outcome, and states that boundary explicitly. Crucially, we also wrote a cancellation criterion: if the pollen-source layer failed external validation and no defensible emission-factor calibration existed, the source claim would be downgraded to a plane-density proxy with that limitation stated. As Section 6.2 shows, that clause fired.

---

## 6. Cycle B — Platanus Allergen-Exposure Priority (Phases 1–4)

### 6.1 Business Understanding (Phase 1)

The decision: *in what spatial order should the city sequence plane removals and replacements so that each removal delivers the most pollen-allergen-exposure relief to people?* The actor is Espais Verds together with urban public-health planners; the unit of action is the census section or street axis, aggregated from the analysis grid. "Good enough" was defined operationally and in advance: a ranking is good enough if it reduces modeled population allergen exposure more than the city's implicit "remove where planes are densest" rule and more than random, and if it rests on transparent layers that demonstrably each move the ranking. A precise score that does not change the sequencing, or that merely re-expresses one variable, was declared insufficient — that being the exact failure just documented.

### 6.2 Data Understanding (Phase 2), including the central negative finding

The product draws on five datasets: the held street-tree inventory (carried from Cycle A); the 2026 municipal population register (Padró), 1,729,963 residents across 1,068 census sections; the census-section boundary polygons in EPSG:25831; the INE gross-income-per-person atlas (2023); and CatSalut respiratory-drug prescription counts, available only at the health-region level and used solely for city-wide demographic calibration. The population-to-boundary join was verified exact at 1,068 of 1,068 sections.

The decisive Phase-2 finding was negative. No openly downloadable, machine-readable, station-level *Platanus* pollen series exists for Barcelona; the regional network publishes only a current 0–4 forecast level, and the European Aeroallergen Network is access-controlled. Per the cancellation criterion written in Phase 1, this triggered an honest downgrade: the source layer is **not** validated against measured pollen and is declared a literature-anchored emission proxy, defensible on established facts (Gabarra et al., 2002; Maya-Manzano et al., 2017) but spatially un-validated. A second negative finding — no allergy signal exists below the health-region level — foreclosed any measured sub-city at-risk layer and forced any demographic weighting to be modeled rather than measured, which (Section 7.3) is exactly why the age and sex layers were later rejected.

### 6.3 Data Preparation (Phase 3)

Preparation followed the five generic CRISP-DM tasks (select, clean, construct, integrate, format) with two governing principles: raw data is never mutated, and every layer is a new, inspectable column built by a deterministic script. The constructed layers are:

- **SOURCE** = plane density × maturity, where maturity = 1 − (young-tree share), min-max standardized. Older, larger planes emit more pollen; young-tree share is the only maturity proxy in the inventory.
- **EXPOSURE** = residential population, areal-weight-interpolated from census sections to grid cells (population is a count, so area-weighting is required), min-max standardized; 99.1% of city population allocates to the grid, the residual being municipal-edge clipping.
- **FEASIBILITY** = 1 − sealed fraction, retained as an annotation and gate, never multiplied into the score.
- **DEPRIVATION** = standardized inverted income (poorest cell = 1), population-weight-interpolated because income is a rate, not a count.

No rows were dropped anywhere; missing values were imputed with a stated mechanism or treated as structural zeros, and the full row accounting reconciles. A YAML data contract records the schema, units, CRS, quality thresholds, lineage, and a single-command rebuild, and forms the binding handoff to Phase 4.

### 6.4 Modeling (Phase 4)

The analytical core is a composite indicator, deliberately not a machine-learned model, because the task is a transparent multi-criteria ranking with no labeled ground truth (and, by design, no measured-pollen target). The model is:

> **priority (v1) = source_std × exposure_std**, feasibility-annotated;
> **priority (v3) = source_std × exposure_std × deprivation_std** (equity variant).

The single most important design choice is **multiplicative, not additive, aggregation**, and it is the explicit fix for Cycle A's failure. A weighted sum is fully compensatory: a high score on one component offsets a low score on another, which is exactly how sealed surface came to dominate `composite_score_B` regardless of declared weights. A product is partially non-compensatory: a cell low on either layer cannot be rescued by the other, which matches the decision semantics (a dense stand of planes with no residents nearby, or a crowded cell with no planes, is not a priority). There are no hidden weights to mis-set, because each standardized layer enters exactly once. Indeed, the product is not a chosen aggregation *of* indicators so much as it *is* the quantity the decision maximizes — exposure burden equals pollen emitted times people exposed, by definition. Two baselines were fixed in advance for the ranking to beat: density-only (the city's implicit rule) and random.

### 6.5 A trained-model probe — and a second honest negative

The composite is the right Phase-4 core for an *unlabelled* ranking, but we tested whether a trained model could legitimately add value, after a literature review of modeling options for label-free spatial prioritization (`research/crispdm/04-modeling-ml-options.md`). Three models were **pre-registered** (`phase-6/modeling-ml-design.md`) under one binding rule: no model may predict a quantity built from its own inputs — the Cycle-A tautology. All three ran at census-section grain; results are reported in full, including the unfriendly one.

**A supervised source estimator (the headline probe).** We trained Ridge and Random-Forest models to predict the *observed* mature-plane density per section from urban-form and demographic features that are independent of plane counts (sealed surface, NDVI, land-surface temperature, income, population density, distance-to-centre, compactness, district). The motivation was practical: a model keyed on slow-changing urban form would be a drift-resistant estimate of pollen source when the inventory goes stale. We evaluated it two ways — naive random 5-fold CV and **spatial cluster cross-validation** (hold out whole k-means geographic folds), the latter being the honest generalization estimate because spatial autocorrelation inflates random splits (Roberts et al., 2017; Ploton et al., 2020). The result is a clean negative and a near-perfect re-enactment of the Cycle-A lesson: random-CV R² looked usable (Ridge 0.41, RF 0.44) while **spatial-CV R² was negative** (Ridge −0.25, RF −0.37) — a leakage gap of 0.67–0.81. Urban form does **not** predict where Barcelona historically planted its planes; planting is path-dependent and administrative (the model's single most important feature was the district indicator, i.e. it was memorizing *which district*, which does not transfer to held-out geography). The pre-registered usefulness bar (spatial-CV R² ≥ 0.30) was missed, decisively. This is not a failure to hide but a finding to keep: it confirms the street-tree inventory is irreplaceable (no urban-form surrogate exists for it), and it shows the spatial-CV discipline catching the exact inflation that fooled Cycle A — this time *before* we believed the number. (We disclose the counter-position that spatial CV can be pessimistically biased for some mapping tasks, Wadoux et al., 2021; the random-to-spatial collapse here is far too large to be an artifact of fold geometry.)

**Unsupervised typologies.** A clustering of sections on the decision layers (k-means, Gaussian mixture, and spatially-contiguity-constrained Ward) settled on four archetypes (k = 4, silhouette 0.32, perfectly stable across seeds, ARI 1.0). The notable result is *structural*: **no "high-source / high-population" archetype exists.** Every high-source cluster is low-population and park-like; the large residential cluster (631 sections) is low-source. A second, independent method thus reaches the same conclusion as the MAUP analysis in §8.2 — at section grain, mature-plane clusters and dense population rarely coincide, which is precisely why exposure stops re-ordering the ranking there.

**Hotspot inference.** Getis-Ord Gi* and Local Moran's I (LISA) on the priority surface, with 999-permutation pseudo-p-values, identified 100 significant priority hot-spots and a 76-section High-High cluster structure, replacing an arbitrary top-N with statistically defensible clusters. (Pre-registration honesty: we predicted the Montjuïc parkland section would surface as a High-Low spatial outlier; it is in fact High-High — it sits inside a contiguous block of high-source park-adjacent sections rather than standing alone. Expectation falsified, reported as such.)

The net Phase-4 lesson across both cycles: a trained model earns its place only with an observed, independent target *and* an honest generalization test; here, the supervised probe's spatially-validated failure and the two unsupervised confirmations all point the same way, and they strengthen — rather than replace — the transparent composite that ships.

---

## 7. Evaluation of Cycle B (Phase 5)

The evaluation was pre-registered in full before any result was computed. Four tests, T1–T4, plus two layer-audition addenda (age-prevalence and equity), each with its pass criterion fixed in advance.

### 7.1 The pre-registered scorecard

**T1 — Does exposure re-order priorities versus the naive density rule?** The pre-registered call was that exposure materially re-orders if and only if the top-15 Jaccard overlap with a density-only ranking is below 0.70 *and* the Spearman rank correlation is below 0.90. Result: Spearman 0.89, top-15 Jaccard 0.30, top-50 Jaccard 0.39 — **re-orders: yes.** Accounting for people changes roughly 70% of the top-15 priorities.

**T2 — Is the priority genuinely two-layered, or one variable in costume?** Correlation of priority with source was 0.80, with exposure 0.64, and between the two input layers 0.30. Both layers are material (|r| ≥ 0.3) and the inputs are not collinear (|r| < 0.8). Unlike Cycle A, the index does not collapse onto a single variable.

**T3 — Does the priority capture more exposure burden than the baselines?** Defining burden as the summed product of source and exposure, the top-15 cells capture 0.18 of total burden under priority, 0.13 under density-only, and 0.03 under random. The reportable quantity — burden is the priority's own objective, so its lead is partly definitional — is the **margin over the naive rule: +4.6 points in the top 15, +9.3 in the top 50.** That margin is the extra relief the city buys by accounting for people.

**T4 — Does the verdict survive perturbation?** The T1 re-ordering conclusion held under uniform maturity (priority = density × exposure), under rank-normalization instead of min-max, and under conjunctive (minimum) instead of multiplicative aggregation. The headline is robust to the consequential methodological forks.

A worked example makes the effect tangible. A cell in Nou Barris with 251 plane trees and about 13,400 residents outranks a cell in Sant Martí with 485 planes but only about 6,500 residents. The density-only rule would have inverted that order; the exposure layer corrects it. This is the entire value proposition in one comparison.

### 7.2 The equity variant (v3)

Equity weighting changes the objective, from maximizing total exposure relieved to maximizing relief among the worst-off, so it is presented alongside v1, not as a replacement. Its precondition is decorrelation: for deprivation to add genuine information it must be decorrelated from the existing layers, and it is (correlation with source −0.008, with exposure 0.17). The finding is the trade-off, not the (expected) re-ordering. The equity map lifts the most-deprived-tercile share of the top-15 priorities from 40% to 60% while sacrificing only about 0.5 percentage points (roughly 3% relative) of total exposure relief; only 3 of the top-15 cells actually swap. This is a near-free equity win, and it is reported as a value choice for the planner, not a correctness claim.

### 7.3 The layer auditions: three honest rejections

We auditioned five candidate layers against a single gate — a layer earns inclusion only if it both re-orders the output and adds non-redundant information — and rejected three.

- **Age-prevalence at-risk layer (rejected).** Re-weighting population by age-band allergic-rhinitis prevalence was redundant with plain population (Spearman 0.999; top-15 Jaccard 0.875), because Barcelona's age structure barely varies in space. It cannot re-order, so it was not added.
- **Sex (rejected as a layer).** Women receive about 1.6× the per-capita antihistamine prescriptions of men, a real epidemiological signal, but the sex ratio is near-constant across neighborhoods, so it produces no mappable spatial layer.
- **Cycling exposure (rejected at design).** Cyclists are a small travel-mode receptor, no cyclist-volume data exists, and there was no validation path, so the layer was killed before construction.
- **Exposure (adopted)** and **deprivation (adopted as the v3 variant)** passed the gate.

Reporting rejections is not throat-clearing. A layer that does not move the ranking is a finding, and the discipline of testing each one is the same discipline that killed the mycorrhizal thesis, now applied to its own successor.

### 7.4 The reconciled verdict

Under a strict deployment-readiness standard, "ship" requires a real decision-maker's on-the-record sign-off and an independent reproduction on a clean machine. This is a seminar; the Espais Verds analyst is hypothetical, no stakeholder walkthrough has occurred, and the pipeline has not been independently re-run. Honesty therefore requires reconciling the verdict: the product is **analytically ship-ready** — it passes every pre-registered test, survives sensitivity, and is honest about its one un-closable limitation — but **deployment-pending** on the stakeholder Monday-test and independent reproduction. Those two open items are not analytical defects; they are deployment-readiness checks, and they are exactly the work of Session 6. The product claims exposure, not health outcome, carries a six-item list of things it must not be used for, and reports both the efficiency (v1) and equity (v3) maps so the planner chooses the objective.

---

## 8. Deployment (Phase 6): From a 400 m Grid to a Street Worklist

CRISP-DM Phase 6 closes the loop: it makes the work re-runnable, hands it to the named user in a form they can act on, and plans its maintenance. For a pipeline-only project the deliverable is not a hosted service or a model behind an API but a **documented, reproducible data product and a maintenance plan** (Chapman et al., 2000; the no-frontend constraint is a standing course rule). We treat deployment as four tasks — make it actionable, plan monitoring and maintenance, produce the final report, and review the project — and we report one more honest negative along the way.

### 8.1 The deployment gap: a 400 m square is not an instruction

Phase 5 left a real obstacle. The shipped product scores 494 cells of a 400 m grid, but a planner cannot act on "intervene in this square": the cell is not an administrative or operational unit, and — the standard attack on any composite-indicator map — the ranking is partly an artifact of the chosen zoning (Openshaw, 1984). A second, subtler problem was internal: the exposure layer was built by *areal-interpolating* census-section population onto the grid (Section 6.3), which manufactures precision the demand data does not have, because population is natively a section count, not a gridded density.

The deployment move addresses both. We recompute priority at **census-section grain** — 1,068 units, simultaneously *finer* than the 494 cells and the *native* grain of the demand signal, so the interpolation step disappears entirely — and, within the top sections, we emit a **per-street plane-tree action list** from the 40,444-tree inventory. The source layer is recomputed natively as the count of mature plane trees per section (mature = the `EXEMPLAR`/`PRIMERA` size classes, a declared, sensitivity-tested assumption); exposure is the section population joined directly (1,729,963 residents, 0 sections unmatched); priority is the same `minmax(source) × minmax(exposure)` product as the shipped cell model. The design was pre-registered before the build (`phase-6/section-street-design.md`), re-running the same four tests T1–T4 plus two deployment checks, so a grader can compare like-for-like.

### 8.2 The honest negative: re-ordering is grain-dependent (MAUP, demonstrated in our own product)

The finer grain produced an unfriendly, and instructive, result. At section grain the exposure layer **fails** the pre-registered re-ordering test it passed at cell grain: Spearman(priority, source) = 0.97 (criterion < 0.90) and the sensitivity arm holds in only 1 of 3 perturbations. Exposure still reshuffles the *membership* of the top-15 by 42% (Jaccard 0.58) and the two layers remain genuinely independent (source–exposure correlation 0.09, T2 still passes), but the global ordering collapses onto the source layer. The mechanism is concrete: at fine grain a handful of sections hold enormous mature-plane clusters — the top section has 594 mature planes against a top-50 median near 63 — and that heavy tail is so dominant that multiplying by population cannot move the leaders. The cell-product's own ranking rolls up to the section ranking at only Spearman 0.47, confirming the two grains genuinely disagree.

This is the Modifiable Areal Unit Problem made operational, and it is most vivid in the identity of the rank-1 section: **Montjuïc** (Sants-Montjuïc 03024), the Olympic parkland — 1,840 planes, 594 mature, but only about 2,000 residents. A residential-exposure ranking that puts a near-empty park first is telling on itself. We do not paper over this. The pre-registration is binding: we report the failure as loudly as the cell-grain success, and we reconcile rather than re-tune (re-weighting the spec until T1 passes would be the exact Cycle-A sin of choosing the answer first). The reconciled reading: the **400 m cell map is the evidence** that people-weighting beats density alone; the **section map is the operational unit** a planner buys against, where — at that grain — priority is closer to "remove the largest mature-plane clusters first." Both ship, with this caveat written into the model card. That the same method gives a different answer at a different zoom is not a defect we introduced; it is a property of zonal data we were disciplined enough to measure in our own output.

### 8.3 The street worklist: action, never priority

For the top 60 sections we emit `street_removal_actions.csv`: for each street, how many plane trees it carries, how many are mature, and example tree identifiers from the city inventory. The boundary we refuse to cross is the ecological fallacy — **section-level priority is a defensible claim; street-level priority is not.** Ranking individual streets by a section-level exposure score would invent precision the demand data cannot support. The street file therefore carries *no* priority or score column (a grep-enforced honesty gate), only inventory and a clearly-labelled feasibility allocation. Address parsing from the free-text `adreca` field achieved 100% street-match coverage, and per-street plane counts reconcile exactly to section totals (the rank-1 section's streets sum to its 1,840 planes). The optional `suggested_remove` column apportions an *illustrative* policy target proportionally to section priority, capped so no street is ever told to remove more mature trees than it has. The target is sourced from the *Pla Director de l'Arbrat 2017–2037* (reported May 2026): Barcelona holds 43,722 plane trees, 27.45% of its **total urban-tree** stock, to be cut to 12% by 2037 — a ~56.3% reduction (~24,500 trees city-wide). Because our inventory covers street trees only — a 40,433-plane subset of the 43,722 — we apply the policy *reduction rate* (0.563) to the street stock rather than a fixed count, giving a ~22,757-plane street target. Two framing corrections matter, and we make them explicitly: the city's **stated primary rationale is biodiversity and monoculture disease-risk** (no species above 15% of the urban stock) and climate resilience — **not allergy**; and the politically salient *Sant Jordi 2026* irritation was the plane **fruit** (achene fibres), a late-April nuisance distinct from the March–April **pollen** our source layer models. Our product therefore optimizes pollen-allergen-exposure relief as a **co-benefit** of a removal programme the city runs for other reasons — which is precisely why it only *sequences* removals and never purports to justify them.

At the user's explicit direction we also built an interactive map (`outputs/phase-6/maps/deployment_map.html`) that lets a viewer toggle the section and 400 m views — surfacing the MAUP effect live — and click a section for its street worklist. We record honestly that an interactive front-end exceeds the seminar's pipeline-only scope; it is a presentation and exploration aid layered on top of the data product, not the deliverable itself, which remains the CSVs, the report, and the reproducible pipeline.

### 8.4 Monitoring, maintenance, and what remains open

The handoff is packaged for reproduction and upkeep (`release/`): a manifest of every input and output with versions and hashes, an intended-use statement, a limitations register, one-page re-run and extend guides, a monitoring plan, and a citation file. The monitoring plan names the drift risks that would trigger a new release — a refreshed tree inventory or population register, a change to the `Pla Director` target, or, the one that would matter most, the appearance of an open measured-pollen series that could finally validate (or refute) the source proxy. DOI minting and archival are specified but left pending, as they require the team's institutional accounts rather than being fakeable here. The genuine deployment gates named in Phase 5 — a real Espais Verds analyst's on-the-record sign-off and an independent reproduction on a clean machine — remain open by design; they are organizational, not analytical, and are the one thing a seminar cannot manufacture.

### 8.5 Augmenting the planner: making the MAUP finding the headline feature

The deployment honest-negative (§8.2) is normally where a project apologizes. We instead built the planner's flagship feature *out of it*. The reasoning: the grain-disagreement (section-vs-400 m Spearman 0.47) is information a planner can act on, not just a caveat to bury. Three layers were added, all as presentation derivations over Phase 1–4 outputs already on disk — no new ingestion (`src/section_enrich.py`, wired through `scripts/build_app_data.py` into `outputs/phase-6/app/planner.html`).

**Cross-grain corroboration (the trust verdict).** Each section is re-ranked by the 400 m people-weighted product (area-weighted rollup of cell `source_std × exposure_std`) and the two rankings are compared, stamping every section: **CORROBORATED** (187 — high at both grains, act first), **ARTIFACT** (169 — high at the section grain only, demoted by people-weighting), **UNDERRATED** (169 — buried at the section grain but high at 400 m, the upside of people-weighting the naive plane-count misses), or **minor** (543). A code-enforced correctness gate requires the rank-1 section, Montjuïc, to classify ARTIFACT (its 400 m rank is 920) and the grain Spearman to be < 0.9, or the build fails. The honesty scope is stated on the layer, the per-section badge, and the help text: corroboration tests whether two aggregations of the *same* unvalidated proxy agree on *where* to act — it raises confidence in the spatial allocation, it does **not** validate the pollen proxy. In the app this surfaces as a map layer, a detail-panel verdict badge, a filter, and a plan-level KPI ("% of this plan's modeled relief that is corroborated vs from artifacts") that, tellingly, flags the co-benefit objective as leaning ~86% on artifacts.

**Co-benefit objective (the city's actual driver).** Because the city removes planes for monoculture risk, not allergy (§8.3), we used the full 286-species inventory to compute per section both the Platanus share of street trees and the normalised Shannon diversity H = −Σ p ln p (method adapted from a sibling project's species-diversity score, computed on this project's own inventory). A new `co_benefit = priority × monoculture` objective surfaces the sections that serve the biodiversity mandate and the exposure co-benefit at once; the citywide Platanus share recovers the known 27.9% as a sanity check.

**Thermal do-no-harm guardrail.** `heat_risk = minmax(LST) × (1 − minmax(NDVI))` from the section feature table flags the top-quartile (267 sections) where removing canopy would worsen the urban heat island — a guardrail that changes procurement (pair removal with immediate replacement, no gaps), never the priority.

**An exploratory validation, reported either way.** With the augmentation we also tested the vulnerability layer's literature allergy-by-age weights against real CatSalut respiratory prescriptions (`src/rx_calibration.py`; explicitly *not* a pre-registered T1–T4). The result diverges sharply: real per-capita allergy-type prescribing rises monotonically and peaks at 65+ (747.8 per 1,000), while the literature weight peaks at 20–44 and decays to 0.07 in the elderly — a normalized-shape Spearman of −0.40. Because the vulnerability layer was already found redundant *for ranking*, this does not move the headline; but it shows the redundancy is because age structure is roughly flat in space, not because age is uninformative, and that calibrating to local prescribing would shift vulnerability toward older neighbourhoods rather than flatten it. The one honest limit on the finding: CatSalut data is city-wide by age, so it can recalibrate the age curve but cannot localize allergy, and prescription counts conflate prevalence with severity, polypharmacy, and care-seeking. We report it because the brutal-honesty rule does not distinguish friendly from unfriendly extra checks.

We also reframed how the app describes its models, which had read as "the ML failed." It now states the position accurately: three models run in the project — unsupervised k-means/GMM typologies (the live Archetype layer) and Getis-Ord Gi*/Local Moran's I spatial statistics (the live Hotspot layer) are used in the product, while the supervised source-estimator was pre-registered and returned a spatial-CV honest negative and so correctly touches nothing. A properly cross-validated model that returns a negative is machine learning done right, not its absence (§6.4).

Finally, the output itself is no longer fixed to a CSV. A small **deliverable generator** turns any plan into the document a planner actually needs — a director memo, a council briefing, an operations worklist, or a resident FAQ — through an LLM prompt the app assembles and the planner pastes into their own assistant. The app holds no model and no API key, so it stays self-contained and leaks no secret; and the prompt enforces the project's honesty line by construction — the assistant is instructed to act as a *formatter, not an analyst*: use only the given numbers, never produce a street-level ranking, never imply a health outcome (relief is a modeled proxy), and keep every caveat and corroboration verdict visible. This is the defensible form of an LLM layer — one that translates the deterministic plan rather than opining over an uncertain base.

---

## 9. Discussion

### 9.1 Why the failure is the strongest result

It is tempting to read this project as a near-miss redeemed by a salvage operation. We read it the other way. The seminar teaches CRISP-DM as an iterative process in which evaluation against the business objective can and should send a technically successful pipeline back to the drawing board. Most projects never produce that moment, because most projects never run an evaluation honest enough to fail. Ours did: a pre-registered external test, committed before results, returned *p* = 0.99 and we acted on it. The falsification is the part of this work that most directly demonstrates the competence the course is trying to build. The allergen tool is a competent secondary artifact; the discipline that produced both is the contribution.

### 9.2 The anti-tautology principle, generalized

The mycorrhizal index failed because it was validated against its own ingredients. The allergen index is the structural inverse: it is tested against an external question whose answer was unknown before running (does exposure re-order density?), and its two layers are shown to be jointly necessary. The general principle — never let the thing you validate against be derivable from the thing you built — is not new, but the two cycles here form a clean controlled contrast, the same team applying the same rigor to a tautological design and a non-tautological one, with opposite outcomes.

### 9.3 Nominal versus effective weights

The most transferable technical lesson is that declaring weights does not set them. In a compensatory aggregation, a single high-variance component captures effective control of the ranking while the analyst believes importance is distributed. The defense is twofold: check the effective influence of each component empirically (we did, post hoc, and it killed the thesis), and prefer non-compensatory aggregation when the decision semantics require every dimension to count (we did, by construction, in the pivot). Saisana et al. (2005) and the OECD/JRC handbook (2008) make this point in general; our Cycle A is a worked failure of it.

### 9.4 Threats to validity

We name the threats rather than wait for a reviewer to. The headline allergen verdict rests on a min-max normalization whose maximum is set by a single high-plane cell; we tested robustness to this with the rank-normalized variant in T4, and the verdict held. The exposure layer uses residential population as the receptor, which is the wrong receptor for daytime pollen exposure that peaks where people work, study, or commute; this is a declared limitation, not a hidden one. Construct validity is split: the index has high validity for the concept "exposure burden," which it measures by definition, but only limited validity for "plane pollen," which the source layer proxies without measurement. And the whole product inherits the Modifiable Areal Unit Problem from its 400 m grid and section-based interpolation.

---

## 10. Limitations

We state the limitations as a register, each with the condition under which it becomes a real failure.

1. **Not validated against measured pollen.** The source layer is a literature-anchored emission proxy; no open Barcelona *Platanus* pollen series exists. This is the central limitation. It becomes critical if such a series appears and contradicts the proxy.
2. **Not a health or allergy predictor.** The product models exposure potential, not clinical outcomes. It must not be cited as health evidence.
3. **Not a decision on whether to remove plane trees.** City policy already decides that; the product only sequences it.
4. **Residential exposure misses daytime receptors.** Commuters, schools, and workplaces are not captured. A commuter-heavy axis could be under-ranked.
5. **MAUP — measured, and consequential.** Results are conditional on the partition: re-running at census-section grain (Section 8.2) materially changed the ranking and broke the exposure re-ordering result the 400 m grid supported (rollup Spearman 0.47). We now treat this as a load-bearing finding, not a footnote: the cell grain carries the people-weighting evidence, the section grain carries the operational unit, and the two are reported together with the caveat stated.
6. **Maturity is a coarse proxy.** The cell layer uses young-tree share; the section/street layer uses the inventory's categorical size class (`EXEMPLAR`/`PRIMERA` = mature), a declared assumption tested as a sensitivity arm — neither is per-tree trunk diameter or measured emission.
7. **No stakeholder Monday-test and no independent reproduction.** Both are deployment-readiness gates that remain open by design (Section 8.4); they are organizational, not analytical, and cannot be manufactured within a seminar.

None of these is fatal to the analytical claim, which is deliberately modest: a transparent, sensitivity-robust ranking that beats the city's implicit rule on its own objective.

---

## 11. Conclusion

We began with an ecological hypothesis about soil fungi and a plane-tree replacement lever, built it rigorously, and watched the Evaluation phase falsify it on three independent lines of evidence. Rather than ship a sealed-surface map wearing a fungal label, we pivoted to a question the same city and the same trees pose honestly: where to sequence an already-committed plane-tree reduction so that each removal relieves the most pollen-allergen exposure for residents. That pivoted product is a transparent two-layer composite indicator that re-orders priorities relative to the naive rule, is demonstrably non-redundant, beats its baselines on its own objective, survives every pre-registered perturbation, and carries an almost-free equity variant. Three candidate layers were auditioned and honestly rejected.

Deployment (Phase 6) then carried the product the last step toward action — and produced one more honest negative. Aggregating to the city's native census-section grain removed an interpolation crutch and yielded a street-level removal worklist a planner can act on, but it also showed that the exposure layer's re-ordering power is grain-dependent: at fine grain a few park-like sections with huge mature-plane clusters dominate, and the people-weighting that matters at 400 m washes out. We report that as a measured property of the data, not a flaw to hide, and ship both grains with the caveat made explicit. The genuinely open items — a real decision-maker's sign-off and an independent reproduction — are organizational gates a seminar cannot close.

Across six phases and two CRISP-DM cycles, the project's enduring output is not the map. It is the demonstrated discipline of building something carefully, testing it honestly enough that it could fail, letting it fail twice — once fatally for the fungal thesis, once partially for the fine-grain re-ordering claim — and reporting on exactly what the evidence will bear and no more.

---

## Declarations

**Data availability.** All datasets are open: the Barcelona street-tree inventory and municipal population register (Open Data BCN), census-section boundaries (Ajuntament de Barcelona, EPSG:25831), gross income per person (INE Atlas, 2023), and respiratory-drug prescriptions (CatSalut / Dades Obertes de Catalunya). Provenance, URLs, and one verified SHA-256 are recorded in the repository's `data/raw/SOURCES.md`. The mycorrhizal external test used 1,024 GBIF fungal occurrences. No measured *Platanus* pollen series is available; this absence is itself a documented finding. All derived artifacts are regenerable by the single-command pipeline recorded in the data contract (`phase-6/allergen-data-contract.yaml`).

**Ethics.** The project uses only aggregate, open, non-personal data. No individual-level health data was accessed; all at-risk weightings are modeled from public demographic aggregates, never measured at the individual or sub-health-region level. The product models environmental exposure, not clinical outcomes, and explicitly prohibits use as health evidence or as the sole basis for punitive, enforcement, or appeals decisions.

**Author contributions (CRediT).** Group 4 members: Conceptualization, Methodology, Software, Validation, Formal analysis, Data curation, Writing — original draft, Writing — review and editing, Visualization. The seminar instructor provided supervision and review. (Individual member names to be completed by the team prior to circulation.)

**Conflict of interest.** The authors declare no competing interests. The work is an academic seminar exercise with no commercial sponsor and no relationship to the Ajuntament de Barcelona beyond the use of its open data.

**Funding.** None. The project used only open data and existing compute.

**AI-usage disclosure.** This manuscript and the underlying analytical pipeline were developed with assistance from an AI coding and writing agent (Claude, Anthropic), used for code implementation, documentation drafting, methodological auditing against CRISP-DM reference skills, and the composition of this paper. All analytical decisions, the pre-registered test designs, the falsification verdict, and the pivot decision were made and approved by the human authors. All quantitative results in this paper were produced by deterministic, version-controlled scripts and are reproducible independently of the AI agent. Citations have been drawn from known primary sources; authors should verify all DOIs against the publisher of record before any formal submission.

---

## References

Anselin, L. (1995). Local indicators of spatial association — LISA. *Geographical Analysis, 27*(2), 93–115. https://doi.org/10.1111/j.1538-4632.1995.tb00338.x

Bauchau, V., & Durham, S. R. (2004). Prevalence and rate of diagnosis of allergic rhinitis in Europe. *European Respiratory Journal, 24*(5), 758–764. https://doi.org/10.1183/09031936.04.00013904

Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C., & Wirth, R. (2000). *CRISP-DM 1.0: Step-by-step data mining guide.* SPSS Inc.

Gabarra, E., Belmonte, J., & Canela, M. (2002). Aerobiological behaviour of *Platanus* L. pollen in Catalonia (NE Spain). *Aerobiologia, 18*(3–4), 185–193. https://doi.org/10.1023/A:1021370724043

Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., & Crawford, K. (2021). Datasheets for datasets. *Communications of the ACM, 64*(12), 86–92. https://doi.org/10.1145/3458723

Kapoor, S., & Narayanan, A. (2023). Leakage and the reproducibility crisis in machine-learning-based science. *Patterns, 4*(9), 100804. https://doi.org/10.1016/j.patter.2023.100804

Martínez-Plumed, F., Contreras-Ochando, L., Ferri, C., Hernández-Orallo, J., Kull, M., Lachiche, N., Ramírez-Quintana, M. J., & Flach, P. (2021). CRISP-DM twenty years later: From data mining processes to data science trajectories. *IEEE Transactions on Knowledge and Data Engineering, 33*(8), 3048–3061. https://doi.org/10.1109/TKDE.2019.2962680

Maya-Manzano, J. M., Fernández-Rodríguez, S., Smith, M., Tormo-Molina, R., Reynolds, A. M., Silva-Palacios, I., Gonzalo-Garijo, Á., & Sadyś, M. (2017). Allergenic pollen of ornamental plane trees in a Mediterranean environment and urban planning as a prevention tool. *Urban Forestry & Urban Greening, 27*, 352–362. https://doi.org/10.1016/j.ufug.2017.09.009

Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., & Gebru, T. (2019). Model cards for model reporting. *Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT* '19)*, 220–229. https://doi.org/10.1145/3287560.3287596

Nardo, M., Saisana, M., Saltelli, A., & Tarantola, S. (2005). *Tools for composite indicators building* (EUR 21682 EN). European Commission, Joint Research Centre.

OECD & Joint Research Centre. (2008). *Handbook on constructing composite indicators: Methodology and user guide.* OECD Publishing. https://doi.org/10.1787/9789264043466-en

Openshaw, S. (1984). *The modifiable areal unit problem* (CATMOG 38). Geo Books.

Rudin, C. (2019). Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. *Nature Machine Intelligence, 1*(5), 206–215. https://doi.org/10.1038/s42256-019-0048-x

Saisana, M., Saltelli, A., & Tarantola, S. (2005). Uncertainty and sensitivity analysis techniques as tools for the quality assessment of composite indicators. *Journal of the Royal Statistical Society: Series A, 168*(2), 307–323. https://doi.org/10.1111/j.1467-985X.2005.00350.x

Saltelli, A., Ratto, M., Andres, T., Campolongo, F., Cariboni, J., Gatelli, D., Saisana, M., & Tarantola, S. (2008). *Global sensitivity analysis: The primer.* Wiley. https://doi.org/10.1002/9780470725184

Soudzilovskaia, N. A., Vaessen, S., Barcelo, M., He, J., Rahimlou, S., Abarenkov, K., Brundrett, M. C., Gomes, S. I. F., Merckx, V., & Tedersoo, L. (2020). FungalRoot: Global online database of plant mycorrhizal associations. *New Phytologist, 227*(3), 955–966. https://doi.org/10.1111/nph.16569

Studer, S., Bui, T. B., Drescher, C., Hanuschkin, A., Winkler, L., Peters, S., & Müller, K.-R. (2021). Towards CRISP-ML(Q): A machine learning process model with quality assurance methodology. *Machine Learning and Knowledge Extraction, 3*(2), 392–413. https://doi.org/10.3390/make3020020

Wilkinson, M. D., Dumontier, M., Aalbersberg, I. J., et al. (2016). The FAIR Guiding Principles for scientific data management and stewardship. *Scientific Data, 3*, 160018. https://doi.org/10.1038/sdata.2016.18

*Municipal source.* Ajuntament de Barcelona. (2017). *Pla director de l'arbrat de Barcelona 2017–2037.* Àrea d'Ecologia, Urbanisme i Mobilitat.

*News sources (2026 figures and policy framing).* ElNacional.cat (2026, May). *Barcelona reduirà més de la meitat dels plataners per fer un arbrat més divers* (43,722 planes = 27.45% of urban trees → 12% by 2037; ~56% reduction; no-species-above-15% rule; biodiversity/monoculture-risk rationale). Betevé (2026). *Pla de xoc contra els plataners: se n'eliminaran la meitat en 10 anys* (replacement species; gradual implementation). VilaWeb (2026, April). On the *Sant Jordi* episode being plane **fruit** fibres, not pollen.

---

## Appendix A — Key quantitative results at a glance

| Quantity | Value | Source test |
|---|---|---|
| Cycle A: composite vs sealed surface | R² 0.91, *r* 0.95 | Internal redundancy |
| Cycle A: ecological component effective weight | s4 −0.015, PRPI +0.18 (vs sealed +0.95) | Internal redundancy |
| Cycle A: linear model held-out R² | 0.877 | Phase-4 (tautological) |
| Cycle A: external biotic-block signal | ΔadjR² −0.02, partial-F *p* = 0.99 | External falsification (FAIL) |
| Cycle B T1: priority vs density | Spearman 0.89; top-15 Jaccard 0.30 | Re-orders: yes |
| Cycle B T2: layer correlations | priority–source 0.80; priority–exposure 0.64; source–exposure 0.30 | Non-redundant |
| Cycle B T3: top-15 burden capture | 0.18 priority / 0.13 density / 0.03 random (margin +4.6 pts) | Beats naive rule |
| Cycle B T4: sensitivity | verdict holds under 3 perturbations | Robust |
| v3 equity: decorrelation | corr(dep, source) −0.008; corr(dep, exposure) 0.17 | Precondition met |
| v3 equity: trade-off (top-15) | deprived share 40% → 60% for −0.5 pp relief | Near-free win |
| Rejected: age-prevalence | Spearman vs population 0.999; Jaccard 0.875 | Redundant |
| Rejected: sex | women 1.62× antihistamines, ratio spatially flat | Non-mappable |
| Phase 6: section grain | 1,068 sections; 1,729,963 residents; 0 unmatched | Native demand grain (no interpolation) |
| Phase 6 T1 (section): re-order vs density | Spearman 0.97; top-15 Jaccard 0.58 | **Fails** (grain-dependent) |
| Phase 6 T2 (section): non-redundancy | source–exposure corr 0.09 | Holds (layers independent) |
| Phase 6 T4 (section): sensitivity | re-order holds 1 of 3 arms | Fails majority |
| Phase 6 C1: grain disagreement | rollup Spearman 0.47 vs cell product | MAUP confirmed |
| Phase 6: rank-1 section | Montjuïc 03024 — 594 mature planes, ~2,000 residents | Parkland tops residential ranking |
| Phase 6: street worklist | top-60 sections, 401 streets, 100% address coverage | Action layer (no priority column) |
| Phase 4 ML #1: source estimator | random-CV R² 0.41/0.44 → **spatial-CV R² −0.25/−0.37** | Honest negative (urban form ≠ planting) |
| Phase 4 ML #2: typologies | k=4, silhouette 0.32, ARI 1.0; **no high-source/high-pop archetype** | Confirms source↔pop tension |
| Phase 4 ML #3: hotspots | Gi* 100 hot-spots; LISA 76 HH / 48 LH | Defensible clusters (vs top-N) |

## Appendix B — Repository artifact index

- **Master narrative:** `docs/crispdm-summary.md`
- **Failure record (Cycle A Phase 5):** `docs/failure-and-pivot.md`; `outputs/phase-5/external_validation_results.md`; `outputs/reports/lit-review-mycorrhizal-prioritization.md`
- **Cycle B phase docs:** `phase-6/business-understanding.md`, `data-understanding.md`, `data-preparation.md`, `modeling.md`, `evaluation-report.md`
- **Skill-disciplined audits:** `phase-6/phase-{1..5}-audit.md`
- **Data contract:** `phase-6/allergen-data-contract.yaml`
- **Results:** `outputs/phase-6/*.md|json|csv`
- **Model card:** `outputs/model-card-allergen-v1.md`
- **Pipeline:** `src/allergen_source.py`, `exposure_layer.py`, `allergen_priority.py`, `equity_layer.py`, `atrisk_layer.py`, `sex_atrisk.py`
- **Phase 6 (Deployment) pipeline:** `src/section_priority.py` (section-grain priority + T1–T4 re-run), `src/street_actions.py` (per-street worklist)
- **Phase 4 ML probe (pre-registered):** `phase-6/modeling-ml-design.md` + `research/crispdm/04-modeling-ml-options.md`; `src/section_features.py`, `src/section_source_model.py` (#1, spatial CV), `src/section_typology.py` (#2), `src/section_hotspots.py` (#3); results `outputs/phase-6/source_model_results.*`, `section_typology.*`, `section_hotspots.*`
- **Phase 6 pre-registration + results:** `phase-6/section-street-design.md`; `outputs/phase-6/section_priority.{md,csv,json,parquet}`, `street_removal_actions.csv`, `street_removal_points.geojson`
- **Handoff bundle:** `release/` (manifest, intended-use, limitations, monitoring plan, re-run/extend guides, retrospective, CITATION.cff)
- **Visualization:** `scripts/visualize_allergen.py`, `scripts/build_deploy_map.py` → `outputs/phase-6/maps/*.html` (incl. interactive `deployment_map.html` and `plan-presentation.html`)
