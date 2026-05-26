# Skill Brief — CRISP-DM Phase 4: Build the Analytical Core

> Pipeline-first companion to `04-modeling-academic.md`. This brief is structured as a re-usable skill the student can invoke to pick and execute the **analytical core** of a data pipeline. It is opinionated: when in doubt, do what the OECD/JRC composite-indicator handbook says.

---

## Name
`crispdm-04-modeling-core`

## Description
Guides a pipeline architect through CRISP-DM Phase 4 *Modeling* treated as the **analytical core of a data pipeline** — not as ML training. Helps the student (a) pick the right technique family from the question, (b) execute the four canonical CRISP-DM tasks (Select Technique, Generate Test Design, Build Model, Assess Model) for that family, and (c) produce the artefacts Phase 5 needs to evaluate the result honestly. Covers composite indicators, spatial diagnostics, network/graph analysis, rule-based classification, simulation, and (when justified) statistical/ML modeling. Anchored to OECD/JRC (2008), Saltelli et al. (2008), Anselin (1995), Newman (2003), Rudin (2019), and Mitchell et al. (2019).

## Triggers
Invoke this skill when the student:
- Has finished Phase 3 (Data Preparation) and is about to "build the model".
- Says any of: "I have my data, now what do I do with it?", "what model should I use?", "should I train an ML model?", "I want to build a scoring map / barrier index / connectivity score / hotspot map".
- Is producing a **ranking**, a **scoring map**, a **classification by rule**, a **network/graph metric**, a **hotspot map**, an **interpolation surface**, or a **simulation output** — not just a prediction from labelled examples.
- Has been told their composite index is "subjective" or "not scientific" and needs a defensible methodology.
- Needs to write the modeling section of a thesis, report, or course deliverable that will be reviewed for methodological rigour.

Do **not** invoke this skill when the student is doing Phase 2 (Data Understanding) or Phase 3 (Data Preparation) — these have their own discipline and should not be conflated with modeling choices.

---

## Required inputs

The skill refuses to proceed until the student can state:

1. **The analytical question** — one sentence, of the form: *"For each [unit of analysis], the pipeline outputs [a number / a class / a connection / a probability / a forecast] that represents [concept]."* The unit of analysis must be explicit (block, parcel, patch, person, sensor reading, edge).
2. **The decision the output will inform** — who acts on this result, and how? If no one, the model has no audience and Phase 4 is premature.
3. **The Phase 1 success criterion** — what would make this model a successful answer to the question? Stated in non-modeling language.
4. **The prepared dataset(s)** — file path, vintage, row count, key columns, known limitations, and the Phase 3 documentation (datasheet).
5. **The pipeline-vs-ML constraint** — confirmation that the project is a *data-pipeline* project, not an ML training project. (This changes the dominant test-design family from train/test splits to sensitivity analysis.)

If any of (1)–(5) is missing, stop and recover it before going further. Most Phase 4 failures are actually unresolved Phase 1 / Phase 3 problems.

---

## Decision tree — which technique family?

Walk the student through this decision tree. The terminal nodes route to the sequential steps below.

```
What is the pipeline's output for each unit?

├── A ranking on a multi-dimensional concept (e.g., barrier severity, liveability)
│   → COMPOSITE INDICATOR  (route: 4A — OECD/JRC, 2008)
│
├── A class label from explicit, expert-stated rules
│   → RULE-BASED CLASSIFICATION  (route: 4B)
│
├── A class label/value learned from many labelled past cases
│   → STATISTICAL / ML MODEL  (route: 4C — but first check the gate below)
│
├── A spatial pattern — clusters, hotspots, autocorrelation
│   → SPATIAL DIAGNOSTIC  (route: 4D — Anselin, 1995; Getis & Ord, 1992)
│
├── A value at unobserved locations
│   → GEOSTATISTICAL INTERPOLATION  (route: 4E)
│
├── A structural property of the system (connectivity, criticality, components)
│   → NETWORK / GRAPH ANALYSIS  (route: 4F — Newman, 2003)
│
└── A counterfactual ("what would happen if...?")
    → SIMULATION  (route: 4G)
```

**ML gate.** Before routing to 4C, confirm *all* of:
- A labelled ground truth exists, with enough samples and representativeness for the population of interest.
- The decision is genuinely a prediction (not a ranking dressed as a prediction).
- The downstream user accepts opaque outputs, or you can use an interpretable model class (Rudin, 2019).

If any of these fail, route back to 4A or 4B. Many "ML" problems are actually composite-index or rule-based problems in disguise.

---

## Sequential steps (all routes share Steps 1, 7, 8, 9, 10)

### Step 1 — Lock the analytical question and write the modeling assumptions log
- Write the question in the canonical form (Required Inputs §1).
- Open `modeling-assumptions.md` and list every assumption the model will make about the world (e.g., "block-level aggregation is meaningful for fungal connectivity"; "self-reported land-use is reliable"). Each assumption gets a one-line risk note.

### Step 2 — Choose the technique family
- Use the decision tree. Document the chosen family and *why the alternatives were rejected*.
- One paragraph in `model-card.md` under "Modeling technique".

### Step 3 — Route-specific build

**Route 4A — Composite indicator** (the most common pipeline route)
1. Identify the **indicator set**. Each indicator gets a definition, source, vintage, and direction (does higher = "more" of the concept?). Document any *reverse-coded* indicators explicitly.
2. **Normalize.** Default: min–max to [0, 1] with min/max set at the 5th/95th percentiles (winsorized) — robust against outliers. State the choice (OECD/JRC, 2008, ch. 4).
3. **Weight.** Default is *not* equal weighting — equal weighting is a claim that must be defended. Preferred: AHP-derived weights from a small expert panel (Saaty, 2008) with consistency ratio reported, or Budget Allocation. If neither is feasible, document equal weighting *and* run PCA-derived weights as a sensitivity check.
4. **Aggregate.** Choose linear (fully compensatory), geometric (partially compensatory — preferred when weak dimensions should drag), or non-compensatory (incommensurable dimensions). Justify against substantive theory.
5. **Compute** the index. Store the per-unit indicator values, normalized values, weights, and final score in a flat, joinable table. No hidden steps.

**Route 4B — Rule-based classification**
1. Externalize the rules. Each rule is `IF condition THEN class`, written in a decision-table file that domain experts can read and edit.
2. Confirm rule coverage: every unit must be classified by exactly one rule (or by an explicit "uncovered" class).
3. Test the rules on a held-out batch of expert-labelled units; report disagreements; refine.
4. Version the rule table.

**Route 4C — Statistical / ML model** (only after passing the ML gate)
1. Choose the most interpretable model class that meets the performance bar (Rudin, 2019). Start with logistic regression, GAMs, decision trees, or constrained models. Move to ensembles only if necessary.
2. Train/validation/test split that respects the data's structure (spatial blocks for spatial data; time-respecting splits for time-series).
3. Tune on validation only; touch test exactly once.
4. Document features, target, splits, hyperparameters, random seeds.

**Route 4D — Spatial diagnostic** (Anselin, 1995; Getis & Ord, 1992)
1. Choose the **spatial weights matrix** (rook, queen, k-nearest, distance band) and justify it.
2. Run **Local Moran's I** or **Getis-Ord Gi\***; apply false-discovery-rate correction (Caldas de Castro & Singer, 2006).
3. Acknowledge **edge effects** and the **MAUP** (Openshaw, 1984): rerun at a second spatial unit and compare.

**Route 4E — Geostatistical interpolation**
1. Inspect the sample design — clustered samples bias prediction surfaces.
2. Fit a variogram; choose kriging variant (ordinary, universal, regression-kriging if covariates available, per Hengl et al., 2007).
3. Cross-validate via leave-one-out; report root-mean-square error in source units, not just a number.
4. Produce both the prediction surface *and* the uncertainty surface — never one without the other.

**Route 4F — Network / graph analysis** (Newman, 2003)
1. Specify **what is a node**, **what is an edge**, **what is an edge weight**, **what is the existence threshold**. Each gets a paragraph.
2. Compute connectivity metrics — component analysis, Probability of Connectivity (Saura & Pascual-Hortal, 2007), centrality (degree, betweenness, current-flow betweenness per Newman, 2005).
3. Run sensitivity across edge thresholds and distance-decay parameters — at least three values each. Identify which nodes/edges are **robustly** critical across the grid.

**Route 4G — Simulation**
1. Specify the model's behavioural primitives (what each agent / state does at each timestep) and which of them you can validate against data.
2. Run an ensemble — at least 100 stochastic replicates — and report distributions, not single trajectories.
3. State explicitly that the simulation is an **argument**, not a prediction, unless calibrated against ground truth (Railsback & Grimm, 2019).

### Step 4 — Generate the test design (write *before* finishing the build)
Open `test-design.md` and pre-register:
- For routes 4A, 4D, 4F: the **sensitivity grid** — which choices vary, over what values, and how rank/score variation will be summarised (Saltelli et al., 2008).
- For routes 4B, 4C: the **validation protocol** — held-out cases, accuracy metric, accepted minimum.
- For routes 4E, 4G: the **cross-validation / ensemble protocol** and the **calibration source**.
- For *every* route: an **expert face-validation** protocol (which experts, what they see, what counts as agreement) and at least one **alternative-specification comparison** (a defensibly different choice at the most consequential fork).

### Step 5 — Build the model
Execute the route-specific build. Hard rules:
- All parameters in a config file. **No** magic numbers in code.
- Versioned inputs (hash) and versioned outputs (timestamp + git SHA).
- One script reproduces the full pipeline from raw inputs to final output (`make all` or equivalent).

### Step 6 — Run the test design
Execute every pre-registered test. Append results to `test-design.md` — never silently drop tests that failed to produce friendly results. Cherry-picking is the cardinal sin of Phase 4 (see anti-patterns below).

### Step 7 — Assess the model
For pipeline analytical cores the assessment criteria are:
- **Robustness** — do the substantive conclusions survive the sensitivity grid? Quantify (% of specifications in which top-tier units remain top-tier).
- **Stability** — small perturbations of the input don't move conclusions.
- **Interpretability** — a non-author can reconstruct any unit's score in plain language. If not, prefer a simpler model (Rudin, 2019).
- **Internal consistency** — within-dimension indicators correlate as theory predicts.
- **Construct validity** — comparison to external proxies, expert review.
- **Communicability** — units that flip across the sensitivity grid are reported as flipping, not as belonging to one tier.
- **Defensibility** — every choice has a paragraph behind it.

Write the assessment in `model-card.md`. State explicitly which conclusions are robust and which are fragile.

### Step 8 — Document — three artefacts, no exceptions

1. **`model-card.md`** — Mitchell et al. (2019)-style card adapted for analytical cores:
   - Purpose and intended use; out-of-scope uses.
   - Input data summary (and pointer to Phase 3 datasheet).
   - Modeling technique, family, references.
   - Parameter and choice log (every choice, one paragraph).
   - Test design and assessment results.
   - Robustness statement.
   - Interpretability statement.
   - Known limitations (MAUP, edge effects, missing populations, equity considerations).
   - Versioning (input hashes, code git SHA).
   - Authors and reviewers.

2. **`sensitivity-analysis-log.md`** — the full grid of {normalization × weighting × aggregation × threshold × imputation} runs, with rank/score outputs and a summary table of *robust-tier classifications*.

3. **`weight-justification-table.md`** (composite-indicator routes only) — every indicator weight mapped to source (literature, expert panel, statistical procedure) with a one-line rationale.

### Step 9 — Quality checks (the "before you call it done" gate)
Refuse to declare Phase 4 complete until every item is `yes`:
- [ ] One-sentence analytical question written and matches the actual output?
- [ ] Technique family justified against rejected alternatives?
- [ ] All methodological choices logged with paragraph-length rationale?
- [ ] Test design pre-registered *before* the final build?
- [ ] Sensitivity analysis run across at least three forks (normalization, weighting, aggregation — or their network-analysis equivalents)?
- [ ] Robust-tier / robust-rank classification produced — not a single point estimate?
- [ ] At least one external/expert validity check?
- [ ] Reproducible: one command regenerates everything?
- [ ] Model card, sensitivity log, weight-justification table written?
- [ ] Out-of-scope uses stated?
- [ ] Equity considerations (whose data is missing, who bears the cost of error) considered?

If any answer is `no`, Phase 4 is not done. Do not move to Phase 5.

### Step 10 — Handoff to Phase 5
Phase 5 (Evaluation) tests the model against the Phase 1 mission objectives. It needs the eight artefacts listed in `04-modeling-academic.md` §12:

1. Model card(s).
2. Sensitivity analysis log.
3. Decision log (prose, ordered, with alternatives considered).
4. Weight justification table (composite routes).
5. Construct-validity evidence.
6. Reproducible code + hashed inputs + config-file parameters + one-command run script.
7. Out-of-scope statement.
8. Open questions and known limitations.

Hand these over to the Phase 5 reviewer **before** the review meeting, not during it.

---

## Anti-patterns — fail the brief if you see these

1. **Black-box composite.** A single number with no breakdown. (Booysen, 2002.)
2. **Equal weighting by default with no justification.** Equal weighting is a claim, not a neutral. (OECD/JRC, 2008.)
3. **Hidden normalization.** Switching from min–max to z-score silently flipped a ranking. Both must be reported.
4. **No sensitivity analysis.** Cardinal sin. (Saltelli et al., 2008.)
5. **Mistaking precision for accuracy.** Four-decimal scores from a fragile composite.
6. **Single edge threshold in a network.** Report the curve. (Urban & Keitt, 2001.)
7. **ML where a rule would do.** Random forest for a problem an expert solves in their head. (Rudin, 2019.)
8. **Spatial weights unspecified.** Moran's I or Gi\* with no statement of weight construction. (Anselin, 1995.)
9. **Cherry-picked specification.** Many runs, one reported.
10. **No model card.** No surviving reproducible artefact = no pipeline.
11. **Composite + network fused into one mega-score.** They answer different questions; keep them separate.
12. **"Validated by face validity" with no protocol.** Document which experts, what they saw, what counted as agreement.

---

## Deliverables checklist (what leaves Phase 4)

- [ ] `model-card.md` (one per analytical core).
- [ ] `modeling-assumptions.md`.
- [ ] `test-design.md` (pre-registered + post-hoc results).
- [ ] `sensitivity-analysis-log.md`.
- [ ] `weight-justification-table.md` (composite routes).
- [ ] `decision-log.md` (prose, ordered).
- [ ] `reproducible-pipeline/` directory: code + config + hashed inputs + run script.
- [ ] `out-of-scope.md` — what this model must not be used for.
- [ ] Headline output artefact (the index table, the connectivity map, the hotspot layer).
- [ ] Sensitivity output artefact (the rank-distribution plot, the robust-tier classification, the percolation curve).

---

## Worked routing example — Barcelona mycorrhizal project

1. **Question.** For each city block, output a barrier-severity score (0–1) for underground fungal-network continuity.
2. **Decision tree.** Multi-dimensional ranking → Route **4A (composite indicator)**.
3. **Indicators.** Soil sealing %, depth-to-natural-soil, soil compaction proxy, vegetation continuity, subsurface-infrastructure density, historical land-use disturbance.
4. **Normalize.** Min–max to [0,1] at 5th/95th percentile. Sensitivity: z-score, ranking.
5. **Weight.** AHP from 3-expert panel (consistency ratio reported). Sensitivity: equal, PCA.
6. **Aggregate.** Geometric mean (a fully sealed block is not "average"). Sensitivity: linear.
7. **Test design (pre-registered).** Sensitivity grid over {3 normalization × 3 weighting × 2 aggregation}; robust top-quintile = top-quintile in ≥ 80 % of cells; expert face-validation on top-20 and bottom-20 blocks.
8. **Assess.** Reports robust top-quintile blocks; flags fragile blocks; documents MAUP via parcel-scale re-run.
9. **Model card.** Stores all of the above plus out-of-scope warning.
10. **Second analytical core (network).** Same skill re-invoked, routes to **4F (network analysis)** for the patch-connectivity question. Kept *separate* from the composite — they answer different questions.

If a student can produce all of the above for their own project, the analytical core is defensible. If they can't, they need to loop back to whichever step they skipped.

---

## References (core, mirrors `04-modeling-academic.md`)

- Anselin, L. (1995). Local indicators of spatial association — LISA. *Geographical Analysis*, 27(2), 93–115.
- Booysen, F. (2002). An overview and evaluation of composite indices of development. *Social Indicators Research*, 59(2), 115–151.
- Caldas de Castro, M., & Singer, B. H. (2006). Controlling the false discovery rate: A new application to account for multiple and dependent tests in local statistics of spatial association. *Geographical Analysis*, 38(2), 180–208.
- Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C., & Wirth, R. (2000). *CRISP-DM 1.0: Step-by-Step Data Mining Guide*. SPSS / The CRISP-DM consortium.
- Getis, A., & Ord, J. K. (1992). The analysis of spatial association by use of distance statistics. *Geographical Analysis*, 24(3), 189–206.
- Hengl, T., Heuvelink, G. B. M., & Rossiter, D. G. (2007). About regression-kriging: From equations to case studies. *Computers & Geosciences*, 33(10), 1301–1315.
- Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., & Gebru, T. (2019). Model cards for model reporting. *Proceedings of the Conference on Fairness, Accountability, and Transparency*, 220–229.
- Nardo, M., Saisana, M., Saltelli, A., Tarantola, S., Hoffman, A., & Giovannini, E. (2005). *Tools for Composite Indicators Building*. Joint Research Centre, EUR 21682 EN.
- Newman, M. E. J. (2003). The structure and function of complex networks. *SIAM Review*, 45(2), 167–256.
- Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. *Social Networks*, 27(1), 39–54.
- OECD & Joint Research Centre. (2008). *Handbook on Constructing Composite Indicators: Methodology and User Guide*. OECD Publishing.
- Openshaw, S. (1984). *The Modifiable Areal Unit Problem*. Geo Books.
- Railsback, S. F., & Grimm, V. (2019). *Agent-Based and Individual-Based Modeling* (2nd ed.). Princeton University Press.
- Rudin, C. (2019). Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. *Nature Machine Intelligence*, 1(5), 206–215.
- Saaty, T. L. (1980). *The Analytic Hierarchy Process*. McGraw-Hill.
- Saaty, T. L. (2008). Decision making with the analytic hierarchy process. *International Journal of Services Sciences*, 1(1), 83–98.
- Saltelli, A., Ratto, M., Andres, T., Campolongo, F., Cariboni, J., Gatelli, D., Saisana, M., & Tarantola, S. (2008). *Global Sensitivity Analysis: The Primer*. Wiley.
- Saura, S., & Pascual-Hortal, L. (2007). A new habitat availability index to integrate connectivity in landscape conservation planning. *Landscape and Urban Planning*, 83(2–3), 91–103.
- Studer, S., Bui, T. B., Drescher, C., Hanuschkin, A., Winkler, L., Peters, S., & Müller, K.-R. (2021). Towards CRISP-ML(Q): A machine learning process model with quality assurance methodology. *Machine Learning and Knowledge Extraction*, 3(2), 392–413.
- Urban, D., & Keitt, T. (2001). Landscape connectivity: A graph-theoretic perspective. *Ecology*, 82(5), 1205–1218.
