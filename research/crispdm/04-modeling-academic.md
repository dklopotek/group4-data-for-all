# CRISP-DM Phase 4 — Modeling, Reframed as the Analytical Core of a Data Pipeline

*Course: Graduate seminar on data-pipeline design. Audience: students who will be **architects** of analytical systems, not necessarily ML engineers. Domain anchor: AEC, urban, and environmental data — with a live test case in urban-ecology mycorrhizal network mapping for Barcelona.*

---

## 1. Reframing Phase 4 for pipeline projects

The CRISP-DM reference guide (Chapman et al., 2000) introduces Phase 4 — *Modeling* — with language that has aged poorly for the kind of work most environmental, urban, and infrastructure analysts now do. It speaks of "selecting modeling techniques", "calibrating parameters", and "assessing the model" in a vocabulary that maps cleanly onto classification, regression, and clustering. Two decades later, the most consequential analytical outputs in AEC, sustainability, and public-policy pipelines are *not* predictive ML models. They are **composite indices**, **scoring maps**, **spatial diagnostics**, **network connectivity products**, and **rule-based classifications** — analytical artefacts whose correctness is judged by robustness and defensibility rather than by held-out accuracy.

For this course we therefore read Phase 4 expansively. *Modeling*, in the pipeline sense, is the step where prepared data becomes the analytical product the project promised in Phase 1. It is the **analytical core** — the place where domain logic, normalization choices, weighting decisions, spatial assumptions, and graph constructions are encoded into a reproducible computation. The CRISP-DM tasks (Select Modeling Technique → Generate Test Design → Build Model → Assess Model) still structure the work; what changes is the catalogue of "techniques" we consider valid and the assessment criteria we apply to them.

This reframing matters because students who treat Phase 4 as synonymous with "train an ML model" tend to commit two errors. First, they reach for ML when their data, sample size, ground truth, and downstream use simply do not justify it (Rudin, 2019). Second, when they correctly choose a non-ML approach — a composite barrier index, for example — they then under-invest in the methodological rigour the analytical-core deserves, treating weights and normalization as cosmetic rather than load-bearing decisions (OECD/JRC, 2008). The chapter that follows tries to inoculate against both.

---

## 2. The canonical four tasks, restated

Chapman et al. (2000, pp. 47–53) define Phase 4 through four generic tasks with explicit outputs. We retain that scaffolding:

1. **Select Modeling Technique** — choose the technique family and document assumptions. *Output:* modeling technique record + modeling assumptions log.
2. **Generate Test Design** — describe the procedure for testing the model's quality and validity *before* building it. *Output:* test design document.
3. **Build Model** — run the technique on the prepared dataset(s); record parameter settings. *Output:* parameter settings, the model artefact itself, model descriptions.
4. **Assess Model** — evaluate the model technically against the test design and against domain expectations. *Output:* model assessment + revised parameter settings.

For a pipeline analytical core, "technique" includes composite indicators, spatial estimators, graph algorithms, decision rules, and simulations. "Test design" is rarely a train/test split — far more often it is a **sensitivity analysis plan**, a **scenario testing plan**, or a **ground-truth comparison protocol**. "Assessment" is rarely a confusion matrix — it is a **robustness statement**, an **interpretability statement**, and a **defensibility statement**.

---

## 3. Technique selection — a decision matrix for pipeline modelers

The single most consequential moment in Phase 4 is the choice of technique family. The wrong family cannot be rescued by careful execution. Below is a decision matrix anchored to the *question the pipeline is being asked to answer*. (Inspired by the question-first framing in OECD/JRC, 2008, ch. 1.)

| If the analytical question is...                                                                       | Technique family                                                              | Canonical references                                  | When NOT to use it                                                                                                                       |
| ------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| "Rank these units (cities, parcels, blocks, projects) on a multi-dimensional concept like *liveability* or *barrier severity*." | **Composite indicator**                                                       | OECD/JRC (2008); Nardo et al. (2005); Booysen (2002) | When indicators are highly redundant, or when units differ so much in context that aggregation hides more than it reveals.               |
| "Where are the statistically unusual clusters of values on a map?"                                     | **Spatial hotspot / autocorrelation analysis** (Local Moran's I, Getis-Ord Gi\*) | Anselin (1995); Getis & Ord (1992)                    | When the spatial unit is itself arbitrary (MAUP) or when there is no underlying spatial process you can articulate.                      |
| "What is the value of variable X at unobserved locations?"                                             | **Geostatistical interpolation** (kriging, IDW) or **regression-kriging**     | Cressie (1993); Hengl et al. (2007)                   | When observations are clustered and unrepresentative of the prediction surface.                                                          |
| "How connected is the system, and which links/nodes are critical?"                                     | **Network / graph analysis** (centrality, components, percolation)            | Newman (2003); Urban & Keitt (2001)                   | When you cannot defensibly justify what an edge *means* in domain terms.                                                                 |
| "Which class does this unit belong to under a known, expert-defined rule set?"                         | **Rule-based classification** (decision tables, expert systems)               | Russell & Norvig (2021, ch. 9)                        | When the rules are unstable, contested, or implicit — then you need consensus first, not a model.                                        |
| "What is the probable value/class of a new case, given many labelled past cases?"                      | **Statistical or ML model** (regression, tree ensemble, neural net)           | Hastie, Tibshirani & Friedman (2009)                  | When you lack a labelled ground truth of sufficient size, quality, and representativeness — the most common failure mode.                |
| "What would happen if we changed X?"                                                                   | **Simulation** (agent-based, system dynamics, diffusion)                      | Railsback & Grimm (2019)                              | When you cannot validate at least the behavioural primitives — simulations are arguments, not predictions, unless calibrated. |

Two heuristics flow from this matrix. **First**, the question should select the family — not the other way around. **Second**, several questions can co-exist in one pipeline (the Barcelona project below combines a composite indicator with a network model). When they do, treat them as *distinct* analytical cores, each requiring its own Phase 4 documentation.

---

## 4. Composite indicators in depth — the gold-standard methodology

For pipeline projects that produce a ranked map or scorecard, the **OECD/JRC Handbook on Constructing Composite Indicators** (OECD/JRC, 2008) is the canonical reference. It is detailed, opinionated, and treats every methodological step as a decision that must be defended. Students should not invent composite-index methodology; they should follow the handbook and document deviations.

The handbook lays out ten steps. The four that matter most analytically — and that students most often get wrong — are normalization, weighting, aggregation, and uncertainty/sensitivity analysis.

### 4.1 Normalization

Indicators arrive in different units, scales, and directions. Aggregation requires bringing them onto a common scale. The most-used methods (Nardo et al., 2005, sec. 4) are:

- **Min–max** rescaling to [0, 1]. Intuitive, but extremely sensitive to outliers and changes the inter-unit distances. Min and max selection must be justified (observed range? policy target? theoretical bound?).
- **Z-score (standardization)** to mean 0, variance 1. Less outlier-sensitive than min–max but produces unbounded values and assumes the comparison group is a meaningful reference.
- **Ranking** (each indicator replaced by ordinal rank). Loses information about magnitude differences but is robust to outliers and easy to communicate.
- **Distance to a reference** (target, leader, baseline year). Useful for benchmarking but requires a defensible reference.
- **Categorical scales** (e.g., quartile classes). Discards information but is robust and stakeholder-friendly.

The OECD/JRC handbook (2008, ch. 4) is unambiguous: normalization choice can flip rankings and is therefore a substantive analytical decision, not a preprocessing detail. Every project must document which method was chosen, why, and how rankings change under alternatives (this is the seed of the sensitivity analysis at step 4.4).

### 4.2 Weighting

Weights encode the (often value-laden) judgment of how much each indicator should contribute. The main schemes are:

- **Equal weighting.** The default; defensible only when (i) all indicators are theoretically of equal importance, *and* (ii) the indicator set is not redundant. The OECD/JRC handbook (2008, p. 31) warns that equal weighting is often used "for lack of a better alternative" and then defended as theoretical neutrality — which it is not.
- **Expert weighting via AHP** (Saaty, 1980, 2008). Pairwise comparisons of indicators with a consistency check. Mathematically principled and defensible; requires elicitation effort and a clearly identified panel.
- **Budget Allocation Process (BAP)**. Experts distribute a fixed budget of points across indicators. Simpler than AHP, also defensible (Nardo et al., 2005, sec. 6).
- **Statistical weighting (PCA / factor analysis).** Weights derived from variance structure of the data. Useful when indicators correlate and you want to avoid double-counting, but the weights then reflect *statistical* importance, not *substantive* importance — a frequent source of confusion.
- **Data envelopment analysis (DEA) / benefit-of-the-doubt.** Each unit is assigned its most favourable weighting. Defensible for benchmarking but unusual for shared rankings.

Booysen (2002) reviewed 30 years of composite-index practice in development studies and found that weighting was the single most-criticised methodological step, almost always because the weights were undocumented or unjustified. The corollary is procedural: every weight in the final index must have a paragraph behind it.

### 4.3 Aggregation

Aggregation combines weighted, normalized indicators into a single score:

- **Linear (additive) aggregation** (weighted sum). Fully compensatory — a strong score in one dimension offsets a weak score in another. Simple and the default, but often unrealistic (a slum with excellent transit is not "average").
- **Geometric aggregation** (weighted product). Partially compensatory — weak dimensions drag the score down more than strong ones lift it. The UNDP Human Development Index moved from linear to geometric for exactly this reason (UNDP, 2010).
- **Non-compensatory / multi-criteria methods** (e.g., MULTIMOORA, PROMETHEE, ELECTRE). No trade-off across dimensions; rankings depend on pairwise comparisons. Methodologically heavier; more appropriate when dimensions are considered incommensurable.

Aggregation choice should follow from the substantive theory of the concept. If the concept is genuinely substitutable across dimensions (e.g., "amenity richness"), linear is fine. If weak dimensions are *qualitatively* different from strong ones (a city cannot trade away its drinking-water safety for more parks), use geometric or non-compensatory.

### 4.4 Uncertainty and sensitivity analysis

Saltelli et al. (2008) and the OECD/JRC handbook (2008, ch. 5) treat uncertainty and sensitivity analysis as **non-optional**. Without it, a composite index cannot honestly be published.

- **Uncertainty analysis** propagates input uncertainty (normalization method, weighting scheme, aggregation function, missing-data imputation, indicator set) through to the output ranking, producing confidence intervals or rank ranges.
- **Sensitivity analysis** decomposes output variation by source — *which* methodological choice moved the ranking most? — typically via variance-based Sobol' indices (Saltelli et al., 2010).

In practice, the minimum viable sensitivity protocol is: run the index under all reasonable combinations of {normalization × weighting × aggregation × imputation}, plot rank distributions, and report which units are *robustly* in which tier and which units flip across specifications. Units that flip cannot be communicated as belonging to one tier — that is honest data-pipeline practice.

---

## 5. Spatial analytical techniques

Many pipeline analytical cores are spatial: maps of risk, of access, of barrier, of opportunity. The relevant technique families:

### 5.1 Zonal statistics and aggregation
Computing summaries (mean, sum, density) of a continuous surface within zones (parcels, blocks, neighbourhoods). The pipeline-design caveat is the **Modifiable Areal Unit Problem** (Openshaw, 1984): both the *scale* and the *zoning* of the units change results, sometimes dramatically. Phase 4 must document zonal-unit choice and ideally test results at two scales.

### 5.2 Hotspot detection
- **Local Moran's I** (Anselin, 1995) classifies each unit as part of high-high, low-low, high-low, or low-high clusters relative to neighbours.
- **Getis-Ord Gi\* statistic** (Getis & Ord, 1992) detects local concentrations of high or low values, returning a z-score that supports statistical inference.

Both are sensitive to (i) the **spatial weights matrix** (rook, queen, k-nearest, distance band — each gives different clusters), (ii) **multiple testing corrections** (false discovery rate; Caldas de Castro & Singer, 2006), and (iii) **edge effects** at the study area boundary. The pipeline-design discipline is to declare all three choices in the modeling document.

### 5.3 Spatial autocorrelation as diagnostic, not just result
Global Moran's I is also useful **diagnostically**: if a regression's residuals exhibit strong spatial autocorrelation, ordinary regression is biased and a spatial model (spatial lag, spatial error, or GWR) is warranted (Anselin, 1995).

### 5.4 Edge effects and boundary discipline
For any local statistic, units near the boundary have fewer neighbours and produce biased estimates. Phase 4 documentation should state how edge effects were treated (buffered study area, edge weighting, omission of edge units) and acknowledge residual bias.

---

## 6. Network analysis as a pipeline output

Graph-theoretic outputs — connectivity scores, centrality rankings, percolation thresholds — are increasingly common in environmental and urban pipelines. Newman (2003) is the standard introduction.

### 6.1 Graph construction is a modeling choice
The most consequential Phase 4 decisions in a network pipeline are not in the algorithms but in **how the graph is built**:

- **What is a node?** A habitat patch, an intersection, an organisation, a parcel? Different choices produce different graphs from the same underlying data.
- **What is an edge?** Physical adjacency, functional connection, probability of dispersal, observed flow? Edge semantics determine which metrics are meaningful.
- **What is the edge weight?** Inverse distance, resistance, capacity, similarity? Distance-decay parameters can be load-bearing.
- **What is the threshold for an edge to exist?** Many environmental network analyses construct edges from continuous resistance surfaces by thresholding. The result is famously sensitive to the threshold (Urban & Keitt, 2001).

### 6.2 Connectivity metrics
- **Component analysis** — which nodes belong to which connected sub-network.
- **Centrality** — degree, betweenness, eigenvector, current-flow betweenness (the last useful when "flow" rather than "shortest path" is the right metaphor; Newman, 2005).
- **Probability of connectivity / equivalent connected area** (Saura & Pascual-Hortal, 2007) — landscape-ecology metrics that translate well to any "what fraction of the system is connected?" question.
- **Percolation** — the threshold at which the largest component fragments (Stauffer & Aharony, 1994).

### 6.3 Sensitivity to construction
The honest network-analysis pipeline reports connectivity metrics across a range of edge-thresholds and distance-decay parameters, not at a single (often arbitrary) value. Otherwise the result is an artefact of the construction, not a finding about the system.

---

## 7. Test design — how to test a non-ML model

Chapman et al. (2000, p. 50) define test design as the **procedure for assessing model quality**, planned *before* the model is built. For ML, this is the train/validation/test split. For pipeline analytical cores, the equivalents are:

1. **Sensitivity analysis** (composite indices, network thresholds, weighting schemes). Plan in advance which parameters/choices will be varied, over what ranges, and how rank/score changes will be summarised (Saltelli et al., 2008).
2. **Scenario testing.** Define a small set of substantively meaningful alternative specifications (e.g., "all expert-weighted", "all equal-weighted", "PCA-weighted") and report the index/ranking under each.
3. **Alternative-specification comparison.** A specific form of scenario testing: rerun the analysis with a defensibly different choice at each methodological fork. Report which results are stable and which depend on the choice.
4. **Ground-truth comparison where possible.** Even non-ML analytical outputs can sometimes be partially validated — e.g., a composite "soil quality" index can be checked against held-out soil samples; a hotspot map of pedestrian injuries against intervention sites flagged by local police. Plan such comparisons in the test design.
5. **Expert / stakeholder face validation.** Document the protocol: which experts, what they were shown, what counts as agreement. A structured Delphi or focus group is more defensible than ad-hoc consultation.
6. **Internal consistency checks.** For composite indices: Cronbach's alpha on indicators within a sub-dimension (Nardo et al., 2005, ch. 5). For networks: stability of centrality ranks under edge resampling.
7. **Cross-data validation.** Re-run the model on a parallel dataset (different year, different city, different sensor source) and compare structural results — not exact values, but whether the same units cluster, lead, or break the system.

CRISP-ML(Q) (Studer et al., 2021) extends CRISP-DM to ML projects with explicit **quality assurance** tasks at every phase. Even when the pipeline output is not ML, the CRISP-ML(Q) discipline — risk identification, mitigation planning, and quality acceptance criteria written *before* the model is built — is directly applicable and recommended.

---

## 8. Model assessment — robustness, interpretability, defensibility

For pipeline analytical cores, "accuracy" is often the wrong frame. There is no held-out truth to be accurate against; there is only the question of whether the model is **defensible** to a critical reader. The relevant assessment criteria:

- **Robustness.** Do the substantive conclusions survive reasonable variation in methodological choices (normalization, weighting, aggregation, spatial weights, edge thresholds)? Quantify via sensitivity analysis (Saltelli et al., 2008).
- **Stability.** Do the results survive small perturbations of the input data (noise injection, jackknife on observations, alternative imputation)?
- **Interpretability.** Can a domain expert reconstruct, in words, *why* a particular unit got the score it did? If not, the analytical core is opaque — and Rudin (2019) is clear that for high-stakes decisions, **interpretable models should be preferred to post-hoc explanations of black boxes**.
- **Internal consistency.** Within-dimension indicators correlate as theory predicts; sub-indices correlate with the overall index appropriately.
- **Construct validity.** Does the model actually measure the concept it claims to measure? Tested via expert review, comparison to established proxies, and convergent/discriminant validity checks (Nardo et al., 2005, sec. 5).
- **Communicability.** Can the result be communicated without misleading? A unit whose rank moves across the top two quartiles under reasonable choices should not be communicated as "in the top quartile".
- **Defensibility.** Could you, in front of a critical Phase 5 audience, defend every choice? If not, document the gap.

These criteria, taken together, are stronger and more honest than "the model is 87 % accurate" — and they generalize to ML outputs too. CRISP-ML(Q) (Studer et al., 2021) makes such criteria explicit acceptance gates before deployment.

---

## 9. Documentation — model cards for analytical cores

Mitchell et al. (2019) introduced **model cards** for ML models: short, structured documents recording intended use, training data, evaluation, limitations, and ethical considerations. The concept generalizes beautifully to analytical-core artefacts in pipeline projects. A minimum analytical-core model card should include:

- **Purpose and intended use.** What decision is this model meant to inform? Who is the user?
- **Out-of-scope uses.** What this model should *not* be used for.
- **Input data.** Sources, vintages, known biases.
- **Modeling technique.** Family, specific method, key references.
- **Parameter and choice log.** Normalization, weights, aggregation, thresholds — each with a one-paragraph justification.
- **Test design and assessment results.** Sensitivity outputs, scenario comparisons, validity checks.
- **Robustness statement.** Which conclusions are robust; which are fragile.
- **Interpretability statement.** How a non-author can reconstruct any unit's score.
- **Known limitations and ethical considerations.** MAUP, edge effects, equity implications, missing populations.
- **Versioning.** Hash or version of inputs, code, parameters.
- **Authors and reviewers.**

Two companions to the model card make audit trivially possible:

- A **decision log**, in plain prose, recording the order in which methodological choices were made and the alternatives considered.
- A **weight justification table** (for composite indices) mapping every weight to a source (literature, expert panel, statistical procedure) with a one-line rationale.

Datasheets for Datasets (Gebru et al., 2021) are the upstream analogue at the data-source level and should already exist from Phase 3.

---

## 10. Anti-patterns

The following anti-patterns recur in student and even published work. Phase 4 reviews should flag them explicitly.

1. **Black-box composites.** A single number, no breakdown, no weights published. Booysen (2002) catalogued this as the modal failure of development indices; it persists.
2. **Equal weighting by default, with no justification.** Equal weighting is a substantive claim about indicator importance, not the absence of a claim. State it and defend it (OECD/JRC, 2008, p. 31).
3. **Hidden normalization choices.** Switching from min–max to z-score silently changes rankings. The choice must be documented and the alternative reported.
4. **No sensitivity analysis.** The single most-common Phase 4 failure. Without sensitivity analysis the composite or network is a position statement, not a result (Saltelli et al., 2008).
5. **Mistaking precision for accuracy.** Reporting a score to four decimal places does not make it more correct. Report only as many significant digits as your sensitivity analysis supports.
6. **Arbitrary edge thresholds in networks.** Picking a single distance or resistance threshold and not showing the rest of the curve (Urban & Keitt, 2001).
7. **ML where a rule would do.** A four-feature decision a domain expert can write down does not need a random forest. Rudin (2019) is the relevant warning shot.
8. **Spatial-weights neglect.** Reporting Moran's I or Gi\* with no statement of how the spatial weights were constructed (Anselin, 1995).
9. **Cherry-picked specifications.** Running many model variants and reporting only the one whose result was congenial. The fix is pre-registered test designs.
10. **No model card.** No reproducible artefact survives the project. The pipeline is therefore not actually a pipeline.

---

## 11. Worked example — Barcelona mycorrhizal pipeline

The seminar's live test case is a pipeline producing (a) a **barrier-severity composite index** for the soil ecosystem fungal network across Barcelona and (b) a **connectivity network model** identifying critical patches and broken links. Both are analytical cores in the sense of this chapter.

### 11.1 Composite barrier-severity index

- **Question.** Where are the most severe barriers to underground fungal-network continuity, ranked at the city-block scale?
- **Technique family.** Composite indicator (Section 4); the question is a multi-dimensional ranking, not a prediction.
- **Indicators** (illustrative; drawn from the project's Phase 3 documentation). Soil sealing percentage; depth-to-natural-soil; soil compaction proxy; vegetation continuity index; subsurface infrastructure density; historical land-use disturbance score.
- **Normalization.** Min–max to [0, 1], with min/max set to the 5th/95th percentile to avoid outlier dominance — per OECD/JRC (2008, ch. 4). Sensitivity tested against z-score and ranking.
- **Weighting.** AHP-derived weights from a structured panel of three urban-ecology experts (Saaty, 2008), with consistency ratio reported. Sensitivity tested against equal weighting and PCA-derived weights.
- **Aggregation.** Geometric mean to penalize blocks with even one extreme barrier dimension (a fully sealed block is not "average" because it has a few street trees). Sensitivity tested against linear aggregation.
- **Sensitivity analysis.** Variance-based Sobol' decomposition (Saltelli et al., 2010) across the {normalization × weights × aggregation} space. Output: per-block rank distribution and a **robust-tier classification** (top quintile across ≥ 80 % of specifications).
- **Assessment.** Robust top-tier blocks compared against an independent dataset of soil-sealing surveys for face validity; expert panel inspects top-20 and bottom-20 blocks.
- **Model card.** Records all of the above plus zonal-unit choice (block) and MAUP caveat (re-run at parcel and neighbourhood scales; structural pattern stable, exact rankings vary).

### 11.2 Connectivity network model

- **Question.** Treating each green/unsealed patch as a node and inferring potential fungal dispersal between patches, which patches are most critical to overall network connectivity, and which broken edges would most cheaply restore it?
- **Technique family.** Network analysis (Section 6); the question is structural.
- **Nodes.** Green/unsealed patches above 25 m² (sensitivity tested at 10 m² and 100 m²).
- **Edges.** Inferred from a resistance surface (sealing, traffic, hard surfaces), with edge probability following a negative exponential of effective distance — a standard landscape-genetics formulation (McRae, 2006). Edge included when probability > 0.05 (sensitivity tested at 0.01 and 0.10).
- **Metrics.** Probability of Connectivity (Saura & Pascual-Hortal, 2007) for overall connectivity; per-node delta-PC for criticality; per-non-edge delta-PC for restoration priority.
- **Sensitivity analysis.** Connectivity metrics reported across patch-size and edge-threshold grids; top-10 critical patches identified as those robustly in top-10 across ≥ 80 % of grid cells.
- **Assessment.** Construct-validity check against patches independently flagged by Barcelona urban-ecology partners; percolation curve reported alongside the headline metric.
- **Model card.** All of the above; explicit out-of-scope warning that the network is *potential* fungal connectivity inferred from physical proxies, not direct observation of fungal flow.

### 11.3 Why two analytical cores, not one fused score
A frequent temptation is to fuse the composite index and the network metrics into a single mega-score. Resist it. They answer different questions ("how bad is this block?" vs "how critical is this patch?"). Fusing them collapses information, makes weights even harder to justify, and produces an output no Phase 5 audience can sensibly interpret. Honest pipelines often produce **multiple, related analytical artefacts**, not a single number.

---

## 12. Handoff to Phase 5 — what artefacts must exist

Phase 5 (Evaluation) tests the model not just technically but against the business / mission objectives set in Phase 1 (Chapman et al., 2000, ch. 5). For that to be a real test rather than a paperwork exercise, the following artefacts must cross from Phase 4 to Phase 5:

1. **Model card(s)** for each analytical core, per Section 9.
2. **Sensitivity analysis log** — every {normalization × weighting × aggregation × threshold × imputation} run, with rank/score outputs and the summary robust-tier classification.
3. **Decision log** — prose record of the order and rationale of methodological choices.
4. **Weight justification table** (for composite indices).
5. **Construct-validity evidence** — expert panel notes; independent dataset comparisons; convergent/discriminant validity checks.
6. **Reproducible artefact** — code (versioned), inputs (hashed), parameters (in a config file, not hard-coded), and a script that produces the headline output and the sensitivity outputs in a single command.
7. **Out-of-scope statement** — explicit list of uses the model is *not* fit for.
8. **Open questions and known limitations** — including MAUP, edge effects, missing populations, contested weights, and any test that could not be performed.

If these eight artefacts exist, Phase 5 can be an honest evaluation. If they don't, Phase 5 will degenerate into either uncritical acceptance or undeserved dismissal of the analytical core — both of which are pipeline-design failures.

---

## References

- Anselin, L. (1995). Local indicators of spatial association — LISA. *Geographical Analysis*, 27(2), 93–115.
- Booysen, F. (2002). An overview and evaluation of composite indices of development. *Social Indicators Research*, 59(2), 115–151.
- Caldas de Castro, M., & Singer, B. H. (2006). Controlling the false discovery rate: A new application to account for multiple and dependent tests in local statistics of spatial association. *Geographical Analysis*, 38(2), 180–208.
- Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C., & Wirth, R. (2000). *CRISP-DM 1.0: Step-by-Step Data Mining Guide*. SPSS / The CRISP-DM consortium.
- Cressie, N. (1993). *Statistics for Spatial Data* (rev. ed.). Wiley.
- Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., & Crawford, K. (2021). Datasheets for datasets. *Communications of the ACM*, 64(12), 86–92.
- Getis, A., & Ord, J. K. (1992). The analysis of spatial association by use of distance statistics. *Geographical Analysis*, 24(3), 189–206.
- Hastie, T., Tibshirani, R., & Friedman, J. (2009). *The Elements of Statistical Learning* (2nd ed.). Springer.
- Hengl, T., Heuvelink, G. B. M., & Rossiter, D. G. (2007). About regression-kriging: From equations to case studies. *Computers & Geosciences*, 33(10), 1301–1315.
- McRae, B. H. (2006). Isolation by resistance. *Evolution*, 60(8), 1551–1561.
- Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., & Gebru, T. (2019). Model cards for model reporting. *Proceedings of the Conference on Fairness, Accountability, and Transparency*, 220–229.
- Nardo, M., Saisana, M., Saltelli, A., Tarantola, S., Hoffman, A., & Giovannini, E. (2005). *Tools for Composite Indicators Building*. Joint Research Centre, European Commission, EUR 21682 EN.
- Newman, M. E. J. (2003). The structure and function of complex networks. *SIAM Review*, 45(2), 167–256.
- Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. *Social Networks*, 27(1), 39–54.
- OECD & Joint Research Centre. (2008). *Handbook on Constructing Composite Indicators: Methodology and User Guide*. OECD Publishing.
- Openshaw, S. (1984). *The Modifiable Areal Unit Problem*. Concepts and Techniques in Modern Geography 38. Geo Books.
- Railsback, S. F., & Grimm, V. (2019). *Agent-Based and Individual-Based Modeling* (2nd ed.). Princeton University Press.
- Rudin, C. (2019). Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. *Nature Machine Intelligence*, 1(5), 206–215.
- Russell, S., & Norvig, P. (2021). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson.
- Saaty, T. L. (1980). *The Analytic Hierarchy Process*. McGraw-Hill.
- Saaty, T. L. (2008). Decision making with the analytic hierarchy process. *International Journal of Services Sciences*, 1(1), 83–98.
- Saltelli, A., Ratto, M., Andres, T., Campolongo, F., Cariboni, J., Gatelli, D., Saisana, M., & Tarantola, S. (2008). *Global Sensitivity Analysis: The Primer*. Wiley.
- Saltelli, A., Annoni, P., Azzini, I., Campolongo, F., Ratto, M., & Tarantola, S. (2010). Variance based sensitivity analysis of model output. *Computer Physics Communications*, 181(2), 259–270.
- Saura, S., & Pascual-Hortal, L. (2007). A new habitat availability index to integrate connectivity in landscape conservation planning. *Landscape and Urban Planning*, 83(2–3), 91–103.
- Stauffer, D., & Aharony, A. (1994). *Introduction to Percolation Theory* (2nd ed.). Taylor & Francis.
- Studer, S., Bui, T. B., Drescher, C., Hanuschkin, A., Winkler, L., Peters, S., & Müller, K.-R. (2021). Towards CRISP-ML(Q): A machine learning process model with quality assurance methodology. *Machine Learning and Knowledge Extraction*, 3(2), 392–413.
- UNDP. (2010). *Human Development Report 2010: The Real Wealth of Nations — Pathways to Human Development*. United Nations Development Programme.
- Urban, D., & Keitt, T. (2001). Landscape connectivity: A graph-theoretic perspective. *Ecology*, 82(5), 1205–1218.
