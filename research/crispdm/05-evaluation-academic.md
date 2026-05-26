# CRISP-DM Phase 5 — Evaluation
## A Pipeline-Architect's Reading of the Most Misunderstood Phase

*Research brief for graduate seminar on data-pipeline design (Group 4 / Data-for-All)*
*Domain anchor: AEC, urban-ecology, environmental data pipelines*

---

## 1. The Phase 4 / Phase 5 Distinction — Why It Matters

The single most common error in industrial and academic uses of CRISP-DM is to collapse Phase 4 ("Modeling") and Phase 5 ("Evaluation") into one undifferentiated "did the model work?" stage. The original CRISP-DM 1.0 reference guide is unusually explicit that these are different activities with different audiences, different success criteria, and different artifacts (Chapman et al., 2000).

Phase 4 ends with a generic task called **Assess Model**, in which "the data mining engineer interprets the models according to his domain knowledge, the data mining success criteria and the desired test design… he judges the success of the application of modeling and discovery techniques *more technically*" (Chapman et al., 2000, p. 28). The outputs are a *model assessment* and *revised parameter settings*. The audience is the engineer themselves. The success criteria are the *data-mining* success criteria written at the end of Phase 1 — things like AUC ≥ 0.8, RMSE ≤ X, runtime under N minutes.

Phase 5 — Evaluation — starts where that technical judgement ends. Its first task is **Evaluate Results**: "*Previous evaluation steps dealt with factors such as the accuracy and generality of the model. This step assesses the degree to which the model meets the business objectives and seeks to determine if there is some business reason why this model is deficient*" (Chapman et al., 2000, p. 30, emphasis added). The audience is the *business* — in a pipeline project that means the urban planner, the scientist, the policymaker, the operations team that will (or will not) act on the output. The success criteria are the *business* success criteria written at the start of Phase 1. The outputs are very different: an "Assessment of data mining results *with respect to business success criteria*", a list of "Approved models", a Review of Process, a List of Possible Actions, and a Decision (Chapman et al., 2000, pp. 30–31).

This distinction is load-bearing for pipeline projects, which often have no "model" in the supervised-learning sense at all. A Barcelona urban-ecology pipeline that composites NDVI rasters, soil maps, OSM street-tree records, and DEM-derived connectivity into a "barrier-reduction priority map" passes through no train/test split — there is nothing to "assess" in Phase-4 terms. But it absolutely requires Phase 5: *does this map answer the question an urban planner actually asked, at the resolution they can act on, with caveats they can defend?* In pipelines, the entire centre of gravity of the CRISP-DM evaluation activity shifts into Phase 5. Practitioners who skip it — and the empirical literature shows most do (Sambasivan et al., 2021; Heger et al., 2022) — ship pipelines that produce technically valid outputs nobody can act on, or worse, that produce outputs that look authoritative but encode invisible failure modes (Sculley et al., 2015).

Throughout the rest of this brief we will use the term **assessment** strictly for Phase-4 technical judgement of an artifact, and **evaluation** strictly for Phase-5 socio-technical judgement of whether the whole pipeline does what the original commissioning party needed it to do.

## 2. Canonical Phase 5 — Three Generic Tasks

Chapman et al. (2000, pp. 30–31) define Phase 5 as exactly three generic tasks:

| Task | Outputs |
|---|---|
| **5.1 Evaluate Results** | Assessment of data mining results with respect to business success criteria; Approved models |
| **5.2 Review Process** | Review of process (what was missed, what should be repeated, QA issues) |
| **5.3 Determine Next Steps** | List of possible actions (with reasons for and against); Decision (how to proceed, with rationale) |

These three tasks correspond, roughly, to the three questions a pipeline architect must answer before any release: *Does it do what was asked? Was it built defensibly? What do we do now?* The remainder of this brief treats each task in pipeline-relevant depth, then layers on the modern apparatus that CRISP-DM 1.0 pre-dates: model-card-style documentation (Mitchell et al., 2019), internal algorithmic audit (Raji et al., 2020), fairness checklists (Madaio et al., 2020), data-cascade post-mortems (Sambasivan et al., 2021), reproducibility checks (Pineau et al., 2021), and fit-for-purpose environmental-modelling criteria (Hamilton et al., 2022; Refsgaard & Henriksen, 2004).

## 3. Evaluate Results — Closing the Loop to Phase 1

The phrase "evaluate against business success criteria" is meaningful only if those criteria exist, are unambiguous, and were written down before modelling began. The CRISP-ML(Q) extension makes this explicit by adding a Quality Assurance step at the end of every phase, in which results must be tied back to documented criteria from the originating phase (Studer et al., 2021). When the criteria do not exist, or were written so loosely they cannot be falsified ("provide useful insight to planners"), Phase 5 collapses into theatre — every output is acceptable because nothing was ever inadmissible.

### 3.1 The closing-the-loop discipline

A defensible Evaluate Results task answers, for every Phase-1 success criterion, a literal yes / no / partial, with evidence. For a pipeline like the Barcelona mycorrhizal project the criteria might be: *(i) produces a 25-m raster covering the municipal boundary; (ii) integrates at least three independent ecological signals; (iii) outputs are reproducible from raw inputs in under one working day on commodity hardware; (iv) every prioritised cell can be traced back to the source observations that drove it; (v) Barcelona City Council ecology staff can identify, in a 30-minute walkthrough, the top-10 priority cells they would actually visit.* Each of these is checkable; each makes a clear evaluation question; each can fail. The pipeline architect's job in Phase 5 is to run those checks, document the result, and not soften the language.

### 3.2 Failure modes when the loop does not close

The empirical literature on data-science failures is consistent about what happens when Phase 5 is skipped or replaced with Phase-4 metrics:

- **Data cascades.** Sambasivan et al. (2021) interviewed 53 high-stakes AI practitioners and found 92% had experienced one or more "data cascades" — compounding downstream failures rooted in unvalidated upstream data choices — and 45.3% had experienced two or more in the same project. These cascades become visible only when evaluation is anchored to the use context; technical metrics rarely surface them.
- **Hidden technical debt.** Sculley et al. (2015) documented that real-world ML systems accrue debt through "boundary erosion, entanglement, hidden feedback loops, undeclared consumers, data dependencies, configuration issues, [and] changes in the external world", none of which are visible in held-out validation. Phase-5 evaluation is the only structured point at which these can be surfaced before release.
- **Goodhart drift.** When teams substitute proxy metrics (Phase-4 success criteria) for the real business goal (Phase-1 success criteria), the proxy becomes the target and the goal silently drifts. Phase 5 is the institutional mechanism CRISP-DM provides for catching this.
- **Documentation debt.** Heger et al. (2022), interviewing 14 ML practitioners at a large IT company, found that data documentation is widely seen as a low-status afterthought, leaving downstream evaluators without the information they need to judge fitness for purpose. Closing the Phase-5 loop forces documentation to exist.

## 4. Stakeholder Review Methods

Because Phase 5 is socio-technical, it cannot be done by the pipeline team alone. The literature on participatory environmental modelling (Voinov & Bousquet, 2010; Voinov et al., 2018) is unanimous that *stakeholders are involved most frequently in goal-setting, data collection and checking, and evaluation of model results* — but that the evaluation step is the most frequently neglected of the three. For pipeline projects, four review formats are well-supported in the literature:

1. **Structured walkthrough.** The pipeline team presents the pipeline end-to-end to the decision-maker(s), one stage at a time, asking at each stage: *would you trust this input? do you understand this transformation? do you accept this assumption?* This is the format Raji et al. (2020) embed inside the SMACTR audit framework as the "internal review" component.
2. **Decision-rehearsal session.** The decision-maker is given the pipeline's output (the map, the ranked list, the alert) and asked to *make and justify a real decision from it in real time*, in front of the team. Observers note where the user hesitated, asked for missing context, or felt forced to invent caveats. This is the operational form of Mitchell et al.'s (2019) "intended use" check.
3. **Red-team review.** A separate group is tasked with arguing the pipeline is wrong, unsafe, or inappropriate for release. The technique pre-dates AI red-teaming and traces in modern practice to adversarial testing of safety-critical software; current CISA and industry guidance treats it as a recurring governance mechanism, not a one-time event (CISA, 2024).
4. **The "would you use this on Monday?" test.** Drawn from the participatory-modelling tradition (Voinov & Bousquet, 2010), this asks the decision-maker, after the walkthrough, whether they would actually act on the output the next working day. A "no", or any hedged answer, is a Phase-5 failure even when every Phase-4 metric is green.

Madaio et al. (2020) — winners of the CHI 2020 Best Paper Award for *Co-Designing Checklists to Understand Organizational Challenges and Opportunities around Fairness in AI* — show that checklists succeed only when co-designed with the practitioners who will use them. The same principle applies to pipeline evaluation: a Phase-5 review designed without the decision-maker in the room produces compliance, not insight.

## 5. Fitness-for-Purpose Checklists

Fitness for purpose is the dominant evaluation frame in environmental modelling, where "validation" in the strict falsificationist sense is rarely possible (Refsgaard & Henriksen, 2004). Hamilton et al. (2022), in *Fit-for-purpose environmental modeling: Targeting the intersection of usability, reliability and feasibility*, formalise it as the simultaneous satisfaction of three conditions:

- **Usability** — does the output address the end-user's actual question, at the spatial/temporal/categorical resolution they can act on?
- **Reliability** — has the pipeline reached an adequate level of certainty or trust for the decision at hand? "Adequate" is set by the decision, not by the model.
- **Feasibility** — was the pipeline producible within the practical constraints of the project, and is it producible again under the same constraints?

A fitness-for-purpose checklist for a pipeline project should answer, item by item:

- Does the output answer the *original* question, or a question the pipeline made convenient?
- Is the spatial/temporal/categorical resolution matched to the decision unit? (A 1-km raster cannot inform a parcel-scale planning decision.)
- Is the stated confidence honest? Are uncertainty intervals computed from real propagation, or from model goodness-of-fit only?
- Is timeliness adequate? A pipeline that produces a "real-time" alert with a 48-hour lag is unfit for an alert use case but may be fit for a quarterly-planning use case.
- Are the data licences, ethical clearances, and re-use rights compatible with the intended use?
- Is the pipeline re-runnable by a second team on different hardware without contact with the original authors? (Pineau et al., 2021.)

## 6. Ethical and Bias Review at the Pipeline Level

Mitchell et al. (2019) introduced *Model Cards* to force documentation of intended use, out-of-scope use, evaluation across demographic and intersectional subgroups, and ethical considerations. Raji et al. (2020) extended this into SMACTR (Scoping, Mapping, Artifact Collection, Testing, Reflection), an end-to-end internal audit framework. Madaio et al. (2020) showed that fairness checklists succeed only when contextualised to the team's domain and workflow. Together these three works define the modern apparatus of pipeline-level ethical review.

A pipeline-level ethical review at Phase 5 must ask, in plain language:

- **Who benefits from the pipeline's output?** Name specific people or institutions.
- **Who is missed?** Whose phenomena, geographies, or populations are systematically under-represented in the inputs? Sambasivan et al. (2021) document that this is the single most common source of high-stakes failure.
- **What is the failure-cost asymmetry?** What happens if the pipeline is wrong in direction A (false positive) vs direction B (false negative)? Are these costs borne by the same people? For an urban-ecology priority map, a false positive ("plant trees here") wastes municipal budget; a false negative ("don't plant here") may permanently lock a corridor closed. The asymmetry should be named, not averaged away.
- **What is the pipeline's behaviour at the edges?** Where geographic, temporal, or categorical coverage thins, what does the pipeline output, and how is that signalled to the user?
- **Is there a route by which the affected community can contest or correct an output?**

For environmental pipelines, the bias question is rarely demographic in the classical fairness-ML sense — it is usually *sampling bias*: dense observations near universities, sparse observations in peripheral neighbourhoods; iNaturalist records biased to scenic areas; soil samples concentrated in agricultural land; LiDAR coverage clipped to municipal boundaries. Phase 5 is where these biases must be made visible to the decision-maker, in language the decision-maker can use, before the map becomes "the map".

## 7. Review Process — The Meta-Review

Chapman et al. (2000, p. 31) define this task narrowly: "*it is now appropriate to do a more thorough review of the data mining engagement in order to determine if there is any important factor or task that has somehow been overlooked. This review also covers quality assurance issues, e.g., did we correctly build the model? Did we only use attributes that we are allowed to use and that are available for future analyses?*" The output is a *Review of Process* that "summarize[s] the process review and highlight[s] activities that have been missed and/or should be repeated."

In a pipeline project, this meta-review should run a structured pass through every prior phase and produce a written register of:

1. **Shortcuts taken.** Filters applied without sensitivity analysis; default parameters left untouched; one CRS assumed for all inputs; missing values dropped instead of imputed; rasters resampled with the default method.
2. **Assumptions not validated.** "We assumed parks are connected to streets" — was it checked? "We assumed iNaturalist records are presence-only" — was the assumption documented?
3. **Inputs whose provenance is thin.** Datasets whose licence, vintage, accuracy, or sampling protocol could not be confirmed at primary source. (See *earn-the-data* discipline.)
4. **Steps that should be re-run before deployment.** Re-runs to catch silent failure (hash inputs, re-run, diff outputs); re-runs on a held-out spatial region; re-runs by an independent operator.

A pre-mortem (Kahneman, 2011; Kepner-Tregoe, 2017) is a useful structuring device: ask the team *"imagine this pipeline has been live for six months and a journalist or auditor has just shown the council a serious failure. Write the post-mortem now."* The failures that surface in a pre-mortem are precisely the items the Review-Process register must capture.

## 8. Decision Artifacts

Phase 5 produces a small, dense bundle of artifacts that together constitute the institutional memory of the project. They should exist as files in the repository, not as slide decks. At minimum:

- **Evaluation Report.** One document, structured by Phase-1 business success criteria, recording for each: criterion (verbatim), evidence of attainment, gaps, residual risk.
- **Limitations Register.** A line-item list of every known limitation: data gap, edge case, untested assumption, dependency, computational constraint, statistical caveat. Each line names the limitation, its severity, and its trigger (the condition under which it becomes a real failure).
- **Intended-Use Statement.** Adapted from Mitchell et al. (2019): primary intended uses, primary intended users, out-of-scope uses, prohibited uses. For pipelines, "prohibited uses" matters as much as "intended uses" — many environmental pipelines should explicitly forbid parcel-scale enforcement decisions.
- **Conditions for Deployment.** A list of conditions that must hold for release (e.g., "deployment only after a second team re-runs the pipeline end-to-end on a different machine and outputs hash-match").
- **Conditions for Non-Use.** A list of contexts in which the pipeline must *not* be used (e.g., "must not be used as sole evidence in planning appeals; must not be used outside the Barcelona municipal boundary; must not be used after 2027 without re-running the land-cover layer").
- **Go / No-Go Memo.** A one-page decision artifact recording the recommendation, the recommender, the dissenting opinions, and the rationale. This is the *Decision* output named by Chapman et al. (2000, p. 31).

## 9. Determine Next Steps — Ship, Iterate, or Kill

Chapman et al. (2000, p. 31) describe Determine Next Steps as: *"the project decides how to proceed at this stage. The project needs to decide whether to finish this project and move on to deployment if appropriate or whether to initiate further iterations or set up new data mining projects. This task includes analyses of remaining resources and budget that influences the decisions."* In modern pipeline work this is a three-way choice — ship, iterate, kill — and each branch needs its own discipline.

### 9.1 Ship
Move to Phase 6 (Deployment). Required preconditions: all Phase-1 business criteria marked attained or explicitly accepted as partial; Evaluation Report, Limitations Register, Intended-Use Statement, Conditions for Deployment, Conditions for Non-Use, and Go/No-Go Memo all signed.

### 9.2 Iterate
Loop back to an earlier phase. The Review Process register dictates which phase. Iteration is legitimate; iteration without a written hypothesis for what will change is sunk-cost defence.

### 9.3 Kill
The hardest of the three. The literature on go/no-go decisions stresses sunk-cost-guards: the time and money already spent are unrecoverable and must be excluded from the forward-looking decision (Kahneman, 2011; project-management practice literature). For a pipeline project, the kill decision is warranted when:
- The Phase-1 business question turned out to be the wrong question (revealed by stakeholder walkthrough).
- The data needed to answer it does not exist at usable quality and cannot be produced within the resource window.
- The decision-maker has no decision to make — the output, even if perfect, would not change action.
- A simpler instrument (a one-page checklist, a thresholded indicator) would do the same job.

A useful operational distinction is between **"done"** and **"deployed"**. A project is *done* when its Phase-5 artifacts exist and stand up to external review, even if the decision is no-go. A project is *deployed* only when the conditions for deployment in the Phase-5 memo are satisfied and operational ownership exists. Many pipeline projects are *done* without ever being *deployed*, and that is a legitimate Phase-5 outcome.

## 10. Documentation: Templates That Force Honesty

### 10.1 Evaluation Report template
1. Project name; pipeline version (commit hash); evaluation date; evaluators present (names, roles).
2. Verbatim Phase-1 business question and success criteria.
3. For each criterion: status (met / partial / unmet), evidence, residual risk.
4. Stakeholder walkthrough summary: decision-maker present, decisions rehearsed, hesitations recorded.
5. Fitness-for-purpose checklist (Section 5) — line item answers.
6. Ethical and bias review (Section 6) — line item answers.
7. Process-review findings (Section 7).
8. Recommendation: ship / iterate / kill, with rationale.

### 10.2 Limitations Register template
| ID | Limitation | Source phase | Severity (L/M/H) | Trigger condition | Mitigation | Owner |

### 10.3 Intended-Use Statement (after Mitchell et al., 2019)
- Pipeline name and version
- Primary intended uses (use cases)
- Primary intended users (named institutions or roles)
- Out-of-scope uses (named)
- Prohibited uses (named)
- Performance characteristics across coverage tiers (where reliability degrades)
- Date of next required re-evaluation

## 11. Anti-Patterns in Phase 5

The empirical literature lets us name the anti-patterns precisely.

1. **The Phase-4-as-Phase-5 conflation.** Reporting AUC, RMSE, or accuracy and calling it evaluation. Chapman et al. (2000) explicitly mark these as Phase-4 Assess Model outputs. They are necessary but not sufficient. In pipeline projects with no held-out test set at all, this anti-pattern presents as evaluation-by-visual-inspection ("the map looks plausible") with no link to a Phase-1 criterion.
2. **Confirmation bias.** Phase 5 is run by the team that built the pipeline; they have strong incentives to find the pipeline acceptable. Kahneman (2011) and the debiasing literature treat this as the default human pattern, not an unusual failing. The pre-mortem and the red-team review are the two best-supported antidotes.
3. **No decision-maker in the room.** The single most diagnostic Phase-5 failure: the team evaluates the pipeline against criteria the team invented, presents the result to itself, and signs off. Madaio et al. (2020) show that fairness review without affected stakeholders produces compliance, not improvement; the same holds for Phase-5 evaluation generally.
4. **Evaluating in isolation from the intended-use context.** Evaluating a pipeline at the desk is not the same as evaluating it at the planning office on a Monday morning. Voinov et al. (2018) document that pipeline outputs which test well in the lab routinely fail the "would-you-use-this" test in situ.
5. **The vanishing limitations register.** Limitations are surfaced during evaluation, mentioned in the meeting, and lost. The fix is to require, as a Phase-5 deliverable, a versioned, line-item limitations file in the repository.
6. **Skipping Review Process.** The CRISP-DM 1.0 guide is explicit that Review Process is a separate task with its own output. Treating evaluation as one undifferentiated activity loses the QA function that this task is designed to provide.
7. **Treating "no" as failure.** A clean no-go decision, accompanied by a defensible evaluation, is a successful Phase 5. Treating it as failure incentivises teams to ship anyway.

## 12. Worked Example — Barcelona Mycorrhizal Pipeline

Consider the live test case: a city-scale composite that integrates NDVI/EVI, soil-pH and texture rasters, an OSM street-tree layer, DEM-derived connectivity, and (optionally) iNaturalist sporocarp records, into a 25-m raster of "barrier-reduction priority" for urban mycorrhizal networks across Barcelona. The intended user is the city ecology team; the intended decision is *"where should we prioritise the next round of tree-planting, depaving, or soil-amendment interventions to maintain mycorrhizal connectivity?"* No supervised model exists — outputs are weighted overlays plus a connectivity / centrality analysis on a derived graph.

**Phase-1 criteria (assumed for the worked example):**
- (i) 25-m raster covering municipal boundary;
- (ii) integrates ≥3 independent ecological signals with documented weights;
- (iii) reproducible from raw inputs in <1 working day on commodity hardware;
- (iv) every priority cell traceable to its source observations;
- (v) ecology staff can identify, in a 30-minute walkthrough, the top-10 priority cells they would actually visit on Monday.

**Phase-5 Evaluate Results:**
- (i)–(iii) are file/runtime checks — yes / no, with evidence.
- (iv) is a provenance check — pick five random cells, walk back through the pipeline, confirm the contributing data points.
- (v) is the decision-rehearsal session — record where the ecology team hesitated, asked for missing data, or invented caveats.

**Phase-5 fitness-for-purpose check:**
- Usability — is 25 m the right resolution? Council interventions happen at the parcel / street-segment scale; 25 m may be too coarse for some streets and too fine for some parks. Note explicitly.
- Reliability — uncertainty from raster resampling, weight choice, and observation density should be propagated to the output. If the pipeline cannot produce per-cell uncertainty, the limitation is named in the register.
- Feasibility — re-run by a second team on a clean machine; if it does not reproduce, the pipeline is not fit-for-purpose regardless of output quality.

**Phase-5 bias / ethics check:**
- Who benefits? The council and residents of intervention neighbourhoods.
- Who is missed? Neighbourhoods with thin iNaturalist coverage (typically lower-income, peripheral) will have lower modelled "evidence weight" and risk being de-prioritised — exactly the inverse of equity intent. This is the single most important Phase-5 finding for this pipeline and must be named explicitly to the decision-maker before release.
- Failure-cost asymmetry — false positive: minor budget loss; false negative: a corridor is paved over before being identified, which is irreversible. The pipeline should be tuned (and the decision framed) accordingly.

**Phase-5 process review:**
- CRS assumptions (ETRS89 / UTM 31N for everything?) checked at every join.
- Land-cover vintage matched to NDVI vintage (otherwise temporal mismatch).
- Weight choices documented with sensitivity-analysis output.
- A second analyst re-runs the pipeline end-to-end from raw inputs; outputs hash-match or differences are explained.

**Determine Next Steps:**
- Ship if (i)–(v) attained, bias caveat acknowledged in writing by council, second-team reproduction succeeds.
- Iterate if (v) fails (planners cannot use the map) — loop back to Phase 1 to renegotiate the decision the pipeline is meant to inform.
- Kill if the council confirms it would make the same intervention decisions without the pipeline — the pipeline has no decision to inform.

## 13. Handoff to Phase 6 — Deployment

CRISP-DM treats Deployment as a separate phase with its own planning, monitoring, and maintenance tasks (Chapman et al., 2000, pp. 32–34); CRISP-ML(Q) elaborates the maintenance side substantially (Studer et al., 2021). The handoff from Phase 5 to Phase 6 should consist of, at minimum:

- The Evaluation Report (Section 10.1).
- The Limitations Register (10.2).
- The Intended-Use Statement (10.3).
- The Conditions for Deployment list.
- The Conditions for Non-Use list.
- The Go/No-Go Memo, signed.
- A reproducibility bundle: pinned environment, raw-input manifest with hashes, run script, expected-output hashes (Pineau et al., 2021).
- A documented owner for monitoring (who is responsible for re-evaluation, on what schedule).

Without these artifacts, Phase 6 inherits the technical debt described by Sculley et al. (2015) — the maintenance cost will be paid in production, by people who were not in the room when the assumptions were made. With them, Phase 6 begins on a defensible footing.

---

## References

CISA. (2024). *AI red teaming: Applying software TEVV for AI evaluations.* US Cybersecurity and Infrastructure Security Agency. https://www.cisa.gov/news-events/news/ai-red-teaming-applying-software-tevv-ai-evaluations

Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C., & Wirth, R. (2000). *CRISP-DM 1.0: Step-by-step data mining guide.* SPSS / The CRISP-DM Consortium. https://www.kde.cs.uni-kassel.de/lehre/ws2012-13/kdd/files/CRISPWP-0800.pdf

Hamilton, S. H., Fu, B., Guillaume, J. H. A., Badham, J., Elsawah, S., Gober, P., Hunt, R. J., Iwanaga, T., Jakeman, A. J., Ames, D. P., Curtis, A., Hill, M. C., Pierce, S. A., & Zare, F. (2022). A framework for characterising and evaluating the effectiveness of environmental modelling. *Environmental Modelling & Software, 148,* 105278 (and related fit-for-purpose articulation). https://www.sciencedirect.com/science/article/abs/pii/S1364815221003200

Heger, A., Marquis, L. B., Vorvoreanu, M., Wallach, H. M., & Vaughan, J. W. (2022). Understanding machine learning practitioners' data documentation perceptions, needs, challenges, and desiderata. *Proceedings of the ACM on Human-Computer Interaction, 6*(CSCW2). https://dl.acm.org/doi/10.1145/3555760

Kahneman, D. (2011). *Thinking, fast and slow.* Farrar, Straus and Giroux. (Pre-mortem technique and confirmation-bias debiasing.)

Madaio, M. A., Stark, L., Wortman Vaughan, J., & Wallach, H. (2020). Co-designing checklists to understand organizational challenges and opportunities around fairness in AI. In *Proceedings of the 2020 CHI Conference on Human Factors in Computing Systems* (pp. 1–14). ACM. https://doi.org/10.1145/3313831.3376445

Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., & Gebru, T. (2019). Model cards for model reporting. In *Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT\* '19)* (pp. 220–229). ACM. https://doi.org/10.1145/3287560.3287596

Pineau, J., Vincent-Lamarre, P., Sinha, K., Larivière, V., Beygelzimer, A., d'Alché-Buc, F., Fox, E., & Larochelle, H. (2021). Improving reproducibility in machine learning research: A report from the NeurIPS 2019 reproducibility program. *Journal of Machine Learning Research, 22,* 1–20. https://www.jmlr.org/papers/v22/20-303.html

Raji, I. D., Smart, A., White, R. N., Mitchell, M., Gebru, T., Hutchinson, B., Smith-Loud, J., Theron, D., & Barnes, P. (2020). Closing the AI accountability gap: Defining an end-to-end framework for internal algorithmic auditing. In *Proceedings of the 2020 Conference on Fairness, Accountability, and Transparency (FAT\* '20)* (pp. 33–44). ACM. https://doi.org/10.1145/3351095.3372873

Refsgaard, J. C., & Henriksen, H. J. (2004). Modelling guidelines — terminology and guiding principles. *Advances in Water Resources, 27*(1), 71–82.

Sambasivan, N., Kapania, S., Highfill, H., Akrong, D., Paritosh, P., & Aroyo, L. (2021). "Everyone wants to do the model work, not the data work": Data cascades in high-stakes AI. In *Proceedings of the 2021 CHI Conference on Human Factors in Computing Systems* (pp. 1–15). ACM. https://doi.org/10.1145/3411764.3445518

Sculley, D., Holt, G., Golovin, D., Davydov, E., Phillips, T., Ebner, D., Chaudhary, V., Young, M., Crespo, J.-F., & Dennison, D. (2015). Hidden technical debt in machine learning systems. In *Advances in Neural Information Processing Systems 28 (NIPS 2015)* (pp. 2503–2511). https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems

Studer, S., Bui, T. B., Drescher, C., Hanuschkin, A., Winkler, L., Peters, S., & Müller, K.-R. (2021). Towards CRISP-ML(Q): A machine learning process model with quality assurance methodology. *Machine Learning and Knowledge Extraction, 3*(2), 392–413. https://doi.org/10.3390/make3020020

Voinov, A., & Bousquet, F. (2010). Modelling with stakeholders. *Environmental Modelling & Software, 25*(11), 1268–1281.

Voinov, A., Jenni, K., Gray, S., Kolagani, N., Glynn, P. D., Bommel, P., Prell, C., Zellner, M., Paolisso, M., Jordan, R., Sterling, E., Schmitt Olabisi, L., Giabbanelli, P. J., Sun, Z., Le Page, C., Elsawah, S., BenDor, T. K., Hubacek, K., Laursen, B. K., … Smajgl, A. (2018). Tools and methods in participatory modeling: Selecting the right tool for the job. *Environmental Modelling & Software, 109,* 232–255. https://doi.org/10.1016/j.envsoft.2018.08.028
