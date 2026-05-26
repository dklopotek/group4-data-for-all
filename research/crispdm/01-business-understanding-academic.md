# CRISP-DM Phase 1 — Business Understanding for Data-Pipeline Projects

*A scholarly synthesis with operational guidance for architects of data products (not predictive models)*

---

## 1. What Phase 1 Is — Canonical Definition

The Cross-Industry Standard Process for Data Mining (CRISP-DM) defines **Business Understanding** as the first of six iterative phases in a data-mining lifecycle (Chapman et al. 2000; Wirth & Hipp 2000). Its purpose is brutally simple and frequently misunderstood: *establish what the project is for, in business terms, before any data is touched.* The CRISP-DM 1.0 reference model decomposes this phase into four generic tasks, each with prescribed outputs (Chapman et al. 2000):

1. **Determine Business Objectives** — produce three artifacts: (a) *Background* (the situation at the start of the project), (b) *Business Objectives* (what the customer actually wants in their own words), and (c) *Business Success Criteria* (the measurable conditions under which the project will be judged a success).
2. **Assess Situation** — produce five artifacts: *Inventory of Resources* (personnel, data, computing, software); *Requirements, Assumptions, and Constraints* (schedule, legal, security, data-comprehensibility, deployment); *Risks and Contingencies*; *Terminology* (a glossary covering both business and data-mining language); and *Costs and Benefits* (a cost-benefit analysis at the project level).
3. **Determine Data Mining Goals** — produce *Data Mining Goals* (the business objective restated in technical terms) and *Data Mining Success Criteria* (the technical thresholds — accuracy, lift, coverage — by which the analytical output will be judged).
4. **Produce Project Plan** — produce a *Project Plan* (phases, durations, dependencies, decision points) and an *Initial Assessment of Tools and Techniques*.

Wirth and Hipp (2000) emphasised that CRISP-DM is a *reference model* (what to produce) paired with a *user guide* (how to produce it), and that the model is deliberately industry-, tool-, and application-neutral. The 1.0 step-by-step guide (Chapman et al. 2000) remains the authoritative source for this terminology; later vendor adaptations (e.g., IBM SPSS) preserve the four tasks and twelve outputs verbatim (IBM 2021).

The phase exists because the cost of correcting a misframed problem grows monotonically with each downstream phase. Saltz (2021) and Schröer et al. (2021) both report that the modal failure pattern in surveyed CRISP-DM applications is not technical but definitional: the team produced what was asked for and discovered, at evaluation, that what was asked for was not what was needed.

## 2. Historical Evolution

CRISP-DM was conceived in 1996 by a consortium of Daimler-Chrysler, NCR, SPSS, and OHRA Insurance, and developed under the European Union's ESPRIT funding programme as the first attempt to produce a non-proprietary, cross-industry process for what was then called "knowledge discovery in databases" (Chapman et al. 2000; Wikipedia 2025). Version 1.0 was published in 1999 (presented at the 4th CRISP-DM SIG Workshop, Brussels, March 1999) and has not received an official revision; a CRISP-DM 2.0 Special Interest Group existed between 2006 and 2008 but produced no published successor, and the original crisp-dm.org domain is now defunct (Wikipedia 2025; Data Science PM 2024).

Despite this stagnation at the consortium level, repeated KDnuggets polls (2002, 2004, 2007, 2014) and a 2020 Data Science PM survey of 109 practitioners confirm CRISP-DM remains the *de facto* standard process model, with nearly half of responding teams citing it as their primary framework (Data Science PM 2020). Martínez-Plumed et al. (2021) describe it as "still the de facto standard" twenty years on, while simultaneously arguing that it is no longer sufficient for modern data science work.

Several derivative and competing frameworks have emerged:

- **KDD (Knowledge Discovery in Databases)** — Fayyad, Piatetsky-Shapiro, and Smyth (1996) — an earlier, more research-oriented nine-step process. KDD lacks an explicit business understanding phase analogous to CRISP-DM's; selection of the target dataset is its starting point (Azevedo & Santos 2008).
- **SEMMA (Sample, Explore, Modify, Model, Assess)** — SAS Institute — a tool-bound workflow that SAS itself describes as "a logical organization of the functional toolset of SAS Enterprise Miner," not a methodology. SEMMA explicitly omits a business-understanding phase, beginning with data sampling (Azevedo & Santos 2008; Data Science PM 2024).
- **TDSP (Team Data Science Process)** — Microsoft, 2016 — derived directly from CRISP-DM with five stages including Business Understanding, but adding role definitions, an infrastructure / DevOps layer, and explicit Customer Acceptance gates (Data Science PM 2024).
- **Domino Data Lab lifecycle** — Domino (2017) — extends CRISP-DM at both ends, adding an ideation phase and an explicit deployment-and-monitoring phase, organised around three principles: "expect and embrace iteration," "prevent iterations from delaying the goal," and "enable compounding collaboration" (Domino 2017).
- **CRISP-ML(Q)** — Studer et al. (2021) — the most academically rigorous successor. It collapses CRISP-DM's first two phases into a single "Business and Data Understanding" stage on the grounds that "data availability oftentimes affects the project feasibility," and overlays explicit *quality assurance* requirements on every phase: each task carries documented quality objectives, risk-mitigation actions, and verification criteria.
- **bizML** — Siegel (2024), Harvard Business Review — a six-step business-led framing intended specifically to make ML projects legible to non-technical sponsors.

These derivatives share a common diagnosis of CRISP-DM's original Phase 1: it tells you *what* to produce (the four tasks, twelve outputs) but is thin on *how* to elicit, quantify, and verify those outputs. That gap is what the literature surveyed below targets.

## 3. What the Literature Says Goes Wrong in Phase 1

The empirical record is consistent and unflattering. Gartner estimated in 2017 that 85% of big-data projects fail (Heudecker, in Data Science PM 2024); VentureBeat (2019) reported that 87% of data-science projects never reach production; NewVantage Partners' multi-year executive survey concluded that cultural and organisational issues — not technical ones — represent the single largest impediment to deployment (NewVantage Partners, in Data Science PM 2024). Becker (2017) attributes 62% of failures specifically to project-management and organisational causes rather than technology. These are not failures of model accuracy; they are failures of business understanding.

Taylor (2017), drawing on Decision Management Solutions' consulting experience, names the four Phase-1 failure modes most often observed in practice:

1. **Lack of clarity** — teams skip drilling into the business problem and "make do with the business goals," producing technically sound analyses that do not move any decision;
2. **Mindless rework** — without a clear definition of done, teams pursue new data or new models rather than revisiting the original problem statement with stakeholders;
3. **Blind hand-off to IT** — analytics teams treat deployment as someone else's concern, producing artifacts that cannot be integrated;
4. **Failure to iterate** — without a clear business performance metric, teams lose the basis on which to maintain and tune the system after release.

Saltz and Shamshurin (2016) reach a complementary conclusion from a literature review of big-data team processes: CRISP-DM's task-focused approach "fails to address how a team should prioritize tasks, and in general, collaborate and communicate," and "suffers from the same weaknesses of Waterfall." Their later work (Saltz 2021) extends this critique, arguing that Phase 1 in particular needs explicit roles, decision rights, and acceptance criteria that the 1.0 guide does not provide.

Schröer, Kruse, and Gómez (2021), in a systematic literature review of 24 CRISP-DM application papers across IEEE, ScienceDirect, and ACM, found that the most commonly under-specified phase in published case studies is Business Understanding — many papers describe data and modelling work in detail while glossing over how objectives were elicited, who the stakeholder was, and what the success criteria were. The reviewers note that this opacity makes such projects effectively impossible to reproduce or transfer.

Martínez-Plumed et al. (2021), in their twenty-year retrospective, argue that the original Phase 1 was built for *goal-directed, process-driven* projects (e.g., reduce churn from 12% to 9%) and is poorly suited to exploratory or data-product projects where the goal must itself be co-discovered with the data. They propose the language of "data science trajectories" — multiple paths through the model, only some of which begin with a hard business objective. The implication for Phase 1 is that even exploratory projects need a *decision context* and an *intended use* — what they call a "trajectory anchor" — even when no single optimisation target exists.

Hoerl, Kuonen, and Redman (2022), in MIT Sloan Management Review, formalise the most common Phase-1 anti-pattern: "Too often, teams skip right to analyzing the data before agreeing on the problem to be solved." They invoke the canonical Einstein paraphrase — that one should spend 59 minutes defining a problem and one minute solving it — and recommend root-cause questioning, explicit stakeholder consensus, and the avoidance of "fishing expeditions" through data without a framed question.

Studer et al. (2021) operationalise these critiques in CRISP-ML(Q) by requiring, at Phase 1, that the team document not only objectives and success criteria but also: (a) the feasibility constraints imposed by available data, (b) the application's risk class and corresponding quality-assurance regime, and (c) the conditions under which the project should be cancelled rather than proceed. The cancellation criterion is novel and important: most Phase-1 templates assume the project will go forward.

The consensus across this literature is unambiguous: Phase 1 fails not because practitioners do not know it exists, but because they pass through it perfunctorily, producing the *artifacts* without the *understanding* the artifacts are supposed to capture.

## 4. What "Good" Phase 1 Looks Like — Concrete Artifacts

Synthesising the original CRISP-DM 1.0 outputs (Chapman et al. 2000), IBM's expanded operational guidance (IBM 2021), the CRISP-ML(Q) quality additions (Studer et al. 2021), and the Domino lifecycle's product-orientation additions (Domino 2017), a defensible Phase 1 produces the following twelve artifacts. Each is binary — either it exists and is signed off, or the team is not yet out of Phase 1.

1. **Project background brief (1 page)** — context, antecedents, why now. Names the decision and the decision-maker (not "the user" — the named role).
2. **Decision statement (1 sentence)** — *"This data product will help [decision-maker role] decide [decision] at [cadence] by [mechanism]."* This is the single most load-bearing artifact in Phase 1; if the team cannot fill in all four slots, they have not yet begun.
3. **Business objectives** — what the sponsoring organisation will do differently if the project succeeds. Stated as observable changes in behaviour, not as KPIs.
4. **Business success criteria** — measurable conditions under which the project will be judged a success, SMART-formatted (Specific, Measurable, Achievable, Relevant, Time-bound). Each criterion is a number with a deadline.
5. **Inventory of resources** — people (named, with roles and time commitments), data (with named primary sources, not generic categories), compute, software, budget.
6. **Requirements, assumptions, constraints** — schedule, comprehensibility (does the output need to be explainable to non-technical decision-makers?), legal and ethical (intended use, intended user, prohibited uses), security, deployment environment.
7. **Risk register** — at least the top five risks, each with likelihood, impact, owner, and contingency. Per CRISP-ML(Q), this must include risks that would trigger cancellation, not only risks to mitigate.
8. **Terminology glossary** — bilingual: the sponsor's domain vocabulary and the data-team's technical vocabulary, with cross-references. Reduces the surface area for the "two teams speaking past each other" failure mode.
9. **Cost-benefit analysis** — even a back-of-envelope version; the discipline forces explicit value claims that can be challenged.
10. **Data-mining / data-product goals** — the business objective restated in technical terms. For a pipeline project (no model), this is the *output specification*: what dataset, map, dashboard, or report will exist, at what resolution, covering what extent, refreshed at what cadence.
11. **Data-mining / data-product success criteria** — the technical thresholds — completeness, freshness, accuracy versus a reference, coverage gaps tolerated — at which the output is considered acceptable.
12. **Project plan + initial tool assessment** — a phased plan with decision gates, plus an initial position on tooling. CRISP-ML(Q) requires this plan to name explicit quality gates, not only milestones.

A useful test: any artifact in this list that exists only as a vague paragraph in a doc is not done. Each should be specific enough that a stranger could pick up the project and act on it.

## 5. Domain-Specific Nuances for Pipeline / Data-Product Projects

CRISP-DM's original framing assumes a *predictive model* is the deliverable. A growing fraction of contemporary work — including the test case for this skill — produces *data products*: curated datasets, decision-support maps, dashboards, or analytical reports that humans use to make decisions, without any model in the loop (Domino 2017; Studer et al. 2021). The Phase 1 framing must adapt in several specific ways.

**Success is consumption, not accuracy.** A predictive model has a loss function; a data product has a *decision it must support*. The success criterion is therefore not "MAE < 0.5" but "the named decision-maker can answer the named decision-question from the artifact, without going back to the team for clarification." This shifts the Phase 1 success criterion into the realm of usability and decision-relevance, not statistical performance.

**The output specification replaces the model specification.** Where CRISP-DM Task 3 (Determine Data Mining Goals) would specify "binary classifier, F1 ≥ 0.85," a pipeline project specifies the *output schema*: fields, types, units, coordinate reference system, spatial / temporal resolution, refresh cadence, file format, distribution mechanism. This is the most concrete and verifiable Phase 1 artifact for pipeline work.

**Intended use and intended user become first-class artifacts.** Gebru et al. (2021), in *Datasheets for Datasets*, argue that every published dataset should be accompanied by an explicit statement of recommended uses, prohibited uses, and known limitations — the analogue of an electronics datasheet. For a data product, these are not afterthoughts; they belong in Phase 1, because they constrain every subsequent design decision. A map intended for public communication and a map intended for internal budget allocation are different products even when their data layers are identical.

**FAIR is a Phase-1 commitment, not a Phase-6 afterthought.** Wilkinson et al. (2016) formalised the Findable-Accessible-Interoperable-Reusable principles for scientific data. For pipeline projects whose output is itself a dataset (e.g., a published priority map), the FAIR posture must be decided in Phase 1: will the output be published, under what licence, with what metadata schema, at what persistent identifier? Retrofitting FAIRness onto a finished pipeline is far more expensive than designing for it.

**Decision-back framing, not data-forward.** Hoerl, Kuonen, and Redman (2022) and Taylor (2017) both argue for working *backwards from the decision*: what action will be taken, what information that action requires, what data could produce that information, where that data lives. Pipeline projects are particularly vulnerable to the inverse pattern — starting from "interesting data we have" and inventing decisions it might support. The decision-back discipline is therefore stricter for pipeline work than for model work, where the loss function imposes its own backwards pressure.

**No model means no model card — but the equivalent is required.** ML model cards (Mitchell et al. 2019) document a model's intended use, performance characteristics, and limitations. For a pipeline data product, the equivalent is a *product card* — a short document published with the artifact that names its intended use, its known limitations, the questions it can answer, and the questions it cannot. Phase 1 should produce a draft of this card; the data product is not done until the card is signed off.

## 6. Stakeholder Elicitation Techniques

Producing the twelve artifacts above requires structured conversations with people who often cannot articulate what they need. The literature offers several established techniques; the strongest Phase 1 work uses two or three in combination.

**The Heilmeier Catechism** (Heilmeier, in DARPA n.d.) is a set of eight questions originally devised for DARPA programme proposals and now used by NASA, NSF, and corporate innovation teams (Stanford H4D 2024). The questions: *What are you trying to do? Articulate your objectives using absolutely no jargon. How is it done today, and what are the limits of current practice? What is new in your approach and why do you think it will be successful? Who cares? If you are successful, what difference will it make? What are the risks? How much will it cost? How long will it take? What are the mid-term and final 'exams' to check for success?* The catechism is well-suited to data-pipeline projects because it forces the sponsor to articulate the decision, the gap, and the success test in plain language — and because question 4 ("who cares, what difference") flushes out solutionism that question 1 alone does not.

**Jobs-to-be-Done (JTBD)** (Ulwick, in Strategyn 2024; ProductPlan 2024) reframes elicitation around what the user is trying to accomplish rather than what features they want. For pipeline projects, the relevant translation is: the planner is not buying a map; they are "hiring" the map to make a defensible budget allocation under time pressure. JTBD is particularly useful for surfacing the *social and emotional* dimensions of the job — the planner's need to defend the choice to a councillor, not only to identify the optimal site. These dimensions almost never appear in a written requirements document but heavily constrain what the data product must look like.

**The 4Ws problem-scoping canvas** (Toolify 2024; Medium 2026) — Who is affected, What is the specific problem, Where does it occur, Why is it important — is a lighter-weight alternative to the Heilmeier catechism, useful for early framing sessions before the team has enough material to answer the harder Heilmeier questions.

**Five Whys** (BABOK Guide, in IIBA 2024; ITONICS 2024) drives surface complaints down to underlying causes. The technique is well-established in lean and project management, but its specific value in Phase 1 of a data project is to distinguish *symptom* from *decision*: a stakeholder who asks for "a dashboard showing canopy cover by neighbourhood" may, under five-whys interrogation, reveal that the actual decision is which streets to prioritise for de-paving next budget cycle — a very different artifact.

**Decision-back framing** (Taylor 2017; Hoerl, Kuonen, & Redman 2022) is less a technique than a discipline: refuse to discuss data or methods until the team can complete the sentence *"This system exists to help [role] decide [decision]; the decision is currently made by [mechanism]; better information would change the decision by [delta]."* If the sentence cannot be completed, Phase 1 is not done.

**Problem framing canvas** (Design Sprint Academy, in DSA 2024) is a workshop artifact that captures the current state of the problem from multiple frames simultaneously (business/customer, inward/outward, past/future). It is more useful for ambiguous problem spaces (e.g., "we want to do something with urban biodiversity data") than for already-scoped problems.

The empirical pattern across these techniques is that they work best in *workshops*, not interviews, and that the workshop output is itself a Phase 1 artifact — not just the document that follows from it. The discipline is to schedule and run the workshop, not only to take notes about needing to.

## 7. Quantification Methods — From Fuzzy Goals to Measurable Criteria

Translating a stakeholder's natural-language goal into a measurable success criterion is the single most error-prone step in Phase 1. The CRISP-DM 1.0 guide (Chapman et al. 2000) names the artifact ("Business Success Criteria") but provides only the example *"reduce churn to 5%"*. The literature has since converged on a small set of techniques.

**SMART criteria** (Doran 1981, popularised in management literature) — every success criterion must be Specific, Measurable, Achievable, Relevant, and Time-bound. The Achievable test is the one most often skipped in data projects; it requires a defensible argument that the threshold *can* be hit with available data and resources, not only that it would be desirable.

**Translation table** — a two-column document, business goal on the left, data-mining / data-product success criterion on the right, with an arrow and a rationale paragraph in between. Example: *"reduce churn"* → *"identify 80% of customers who will churn in the next 30 days at a precision of ≥ 60%, refreshed weekly"* → rationale: *"the retention team can act on roughly 200 contacts per week; precision below 60% wastes their capacity."* The rationale paragraph is the load-bearing element; without it, the threshold is arbitrary.

**Counterfactual quantification** — for data-product projects where there is no obvious accuracy metric, the question becomes: *what would the decision-maker do differently if the product met spec vs. failed spec?* If the answer is "nothing," the success criterion is wrong. This technique is borrowed from causal inference and decision theory and has been popularised in the data-product literature (Domino 2017).

**Cancellation thresholds** (CRISP-ML(Q); Studer et al. 2021) — for each Phase 1 success criterion, define the conditions under which the project should be stopped rather than continued. This is rare in CRISP-DM practice and almost universally absent from informal Phase 1 work, but it is the cleanest safeguard against sunk-cost continuation.

**Pre-mortem** (Klein 2007) — the team imagines that the project has failed and works backwards to enumerate the reasons. The output is a forced ranking of risks that is then folded into the risk register. Pre-mortems are particularly effective at surfacing risks that the team is *avoiding* discussing.

The empirical finding from Studer et al. (2021) and Schröer et al. (2021) is that projects with documented, numerical success criteria at Phase 1 are markedly more likely to reach a defensible Evaluation phase. Projects whose success criteria are qualitative ("useful," "actionable," "insightful") effectively cannot fail at Evaluation — and therefore effectively cannot succeed either, because no result distinguishes a success from a failure.

## 8. Anti-Patterns and Pitfalls

The literature reports a consistent set of anti-patterns; the strongest Phase 1 work treats each as a red flag that should block progression.

**Solutionism.** Starting from a chosen technology ("we want to use LLMs / GIS / GNNs to do something") rather than from a decision (Mishra 2022; Stefanovskyi 2023). The diagnostic question: *what decision will this support?* If the answer references the technology rather than the user, the framing is upside down.

**Premature data hunting.** Beginning with data acquisition before the problem is framed (Hoerl, Kuonen, & Redman 2022). The diagnostic: if Phase 2 (Data Understanding) has begun before Phase 1's twelve artifacts exist, Phase 1 is not done. The earn-the-data skill explicitly refuses to begin without these artifacts.

**Missing decision-maker.** No named individual or role who will use the output to make a specific decision (Taylor 2017). The product is being built for "stakeholders" or "users" in the abstract. Diagnostic: ask who will be unhappy if the project is cancelled. If the answer is the project team itself, the missing-decision-maker pattern is present.

**Undefined or non-numerical success.** Success criteria expressed as adjectives rather than numbers ("better," "more accurate," "useful"). Diagnostic: each criterion should be a quantity with a deadline. If it is not, it cannot fail evaluation and therefore cannot succeed.

**Scope creep enabled by ambiguity.** Vague Phase 1 documents allow stakeholders to expand the work by re-interpreting them. Diagnostic: the project plan names what is *out* of scope, not only what is in. CRISP-DM 1.0 (Chapman et al. 2000) explicitly recommends naming explicit exclusions in the constraints artifact.

**Vanity metrics.** Optimising for a number that looks impressive in isolation but does not move any decision (Xebia 2024; Mishra 2022). For pipeline projects this often appears as "number of data sources integrated" or "number of features engineered" rather than "decisions changed by the output."

**Hand-off mentality.** Treating the technical team and the business team as sequential handoff stages rather than co-authors of Phase 1 (Taylor 2017; Saltz 2021). Diagnostic: were the twelve artifacts produced *with* the sponsor, or *for* the sponsor? Only the former counts.

**Skipping the cancellation criterion.** Assuming the project will go forward whatever Phase 1 finds (Studer et al. 2021). Diagnostic: Phase 1 has not produced a defensible answer to *"under what findings would we cancel this project?"*

**Vocabulary collisions.** The sponsor and the data team use the same word to mean different things ("zone," "block," "intervention"). This always produces a hidden disagreement that surfaces at Evaluation. The terminology glossary (Chapman et al. 2000, Task 2 output) is the explicit defence; the anti-pattern is the absence of one.

The literature is consistent that these are not exotic failure modes but the modal failure modes. The Phase 1 discipline exists precisely to catch them before they become Phase 6 disasters.

## 9. Worked Example — Barcelona Mycorrhizal Pipeline (Anchor Case)

To anchor the abstract framework, here is the twelve-artifact Phase 1 applied to the live project this skill was developed alongside. It is included as an illustration, not as a substantive contribution.

The project produces a **barrier-reduction priority map** for urban mycorrhizal fungi in Barcelona — a ranked shortlist of city blocks at the Superilla (~400 m) scale where targeted de-paving, canopy expansion, or sealed-surface reduction would maximise mycorrhizal network connectivity (project memory 2026). The team applied Phase 1 (loosely at first, then formally) and produced the following:

- **Decision statement.** "This data product will help a capital planning analyst at Ajuntament de Barcelona's Espais Verds i Biodiversitat division decide which Eixos Verds / Superilla budget allocations to prioritise, at the annual budget cycle cadence, by providing a top-15 shortlist of blocks with intervention-type recommendations tied to existing budget lines."
- **Business objective.** Shift discretionary urban-greening spend toward blocks where biophysical conditions for mycorrhizal recovery are present but currently constrained, rather than blocks where the constraints are insurmountable or already absent.
- **Business success criteria.** (i) The shortlist is used in at least one budget-cycle decision in the next fiscal year. (ii) For each shortlist entry, the recommended intervention type maps to an existing Ajuntament budget line. (iii) The planner can defend the ranking to the councillor without contacting the team.
- **Inventory of resources.** Seven adopted data sources (Ajuntament tree inventory, Copernicus Urban Atlas, Sentinel-2 L2A, Landsat 8/9 thermal, FungalRoot v2.0, GBIF, OSM); a four-person student team; the seminar's compute; no cash budget.
- **Constraints.** No frontend deliverable (teacher constraint); the planner is the sole intended user; deployment is a published report, not a service.
- **Top risks.** (i) Data resolution insufficient for block-scale claims (mitigation: 2× rule applied at Phase 2); (ii) the host-mismatch sub-score is informationally null for ~95% of the city (status: confirmed; mitigation: drop sub-score weight to 5%, redistribute); (iii) no discretionary budget line exists for any recommended intervention (status: open; mitigation: produce the budget-line crosswalk in session 3).
- **Glossary.** "Block" = Superilla cell (~400 m), not Manzana (city block) or census tract. "Intervention" = a budget-funded physical change (de-pave, plant, irrigate), not a policy change. "Mycorrhizal" = both arbuscular and ectomycorrhizal unless otherwise specified.
- **Data-product output specification.** A ranked GeoJSON of the top-15 Superilla cells, each with composite score, sub-scores, recommended intervention type, mapped budget line, and a 1-sentence rationale; refreshed annually; CC-BY licence; published with a product card naming intended use and limitations.
- **Data-product success criteria.** Coverage: all Superilla cells inside the municipal boundary. Completeness: ≥ 95% of cells have non-null sub-scores for the three retained barrier dimensions. Freshness: input data ≤ 18 months old at publication. Defensibility: each shortlist entry's ranking is reproducible from the published code.
- **Cancellation criterion.** If the budget-line crosswalk reveals that no intervention type has any discretionary pathway in the current budget cycle, the project is reframed as an institutional-blockage finding rather than a planning tool, and a different deliverable is produced.

The exercise made visible a finding the team had been avoiding: the host-mismatch sub-score (sub-score 4) is informationally null for most of the city, and the composite is therefore best understood as a three-variable urban stress index, not a four-variable mycorrhizal-specific index (deep research finding 2026). That finding propagated into a redesign of the scoring weights *before* Phase 3 began — the value of Phase 1 done seriously.

## 10. Handoff Contract to Phase 2 (Data Understanding)

The `earn-the-data` skill encodes the Phase 2 discipline for this seminar (decision unit → six-category hunt → primary-source verification → 2× resolution rule → 5-dimension rubric → 8-section data sheets → coordinate / unit pitfalls → named biases → profiling plan → brief revisit). It is explicit that Phase 2 cannot begin without the decision unit being stated.

The handoff contract from this Phase 1 skill to `earn-the-data` is therefore:

| Required artifact from Phase 1 | Used by Phase 2 to … |
|---|---|
| Decision statement (1 sentence) | Frame the brief revisit at Step 10 |
| Decision unit (smallest spatial / temporal / spectral unit at which claims must hold) | Apply the 2× resolution rule at Step 4 |
| Output specification (schema, resolution, extent, cadence) | Score Coverage and Resolution on the rubric at Step 5 |
| Intended use and intended user | Fill the Uses section of the data sheets at Step 6 |
| Constraints (legal, licensing, deployment) | Score Licensing on the rubric at Step 5 |
| Risk register | Cross-reference candidate-dataset risks against project risks |
| Cancellation criterion | Trigger an explicit no-go finding at Step 10 if data cannot support the decision |
| Terminology glossary | Disambiguate dataset field semantics |
| Product card draft | Seed the Limitations sections of the data sheets at Step 6 |

The Phase 1 skill must therefore produce, at minimum, **the decision statement, the decision unit, the output specification, the intended use / intended user, and the cancellation criterion** before invoking `earn-the-data`. The remaining seven artifacts strengthen Phase 2 but are not strictly load-bearing for it.

This is the contract the operational skill brief (`01-business-understanding-skill-brief.md`) encodes.

---

## References

Azevedo, A., & Santos, M. F. (2008). KDD, SEMMA and CRISP-DM: A parallel overview. *Proceedings of the IADIS European Conference on Data Mining*, 182–185.

Becker, D. (2017). Cited in *Data Science PM* (2024). *Why Big Data Science & Data Analytics Projects Fail*. https://www.datascience-pm.com/project-failures/

Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C., & Wirth, R. (2000). *CRISP-DM 1.0: Step-by-step data mining guide*. SPSS Inc. / The CRISP-DM consortium. (Mirror available via IBM SPSS Modeler documentation.)

Data Science PM. (2020). *CRISP-DM is still the most popular framework for executing data science projects*. https://www.datascience-pm.com/crisp-dm-still-most-popular/

Data Science PM. (2024). *What is CRISP-DM?* https://www.datascience-pm.com/crisp-dm-2/

DARPA. (n.d.). *The Heilmeier Catechism*. U.S. Defense Advanced Research Projects Agency. https://www.darpa.mil/about/heilmeier-catechism

Domino Data Lab. (2017). *Domino data science lifecycle*. Summarised in Data Science PM (2024). https://www.datascience-pm.com/domino-data-science-life-cycle/

Doran, G. T. (1981). There's a S.M.A.R.T. way to write management's goals and objectives. *Management Review*, 70(11), 35–36.

Fayyad, U., Piatetsky-Shapiro, G., & Smyth, P. (1996). From data mining to knowledge discovery in databases. *AI Magazine*, 17(3), 37–54.

Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., & Crawford, K. (2021). Datasheets for datasets. *Communications of the ACM*, 64(12), 86–92. https://doi.org/10.1145/3458723

Hoerl, R., Kuonen, D., & Redman, T. C. (2022, April 14). Framing data science problems the right way from the start. *MIT Sloan Management Review*. https://sloanreview.mit.edu/article/framing-data-science-problems-the-right-way-from-the-start/

IBM. (2021). *IBM SPSS Modeler CRISP-DM Guide* (Version 18.3). IBM Corporation. https://www.ibm.com/docs/it/SS3RA7_18.3.0/pdf/ModelerCRISPDM.pdf

International Institute of Business Analysis. (2024). *BABOK Guide v3 — 10.40 Root Cause Analysis*. https://www.iiba.org/knowledgehub/business-analysis-body-of-knowledge-babok-guide/10-techniques/10-40-root-cause-analysis/

Klein, G. (2007). Performing a project premortem. *Harvard Business Review*, 85(9), 18–19.

Martínez-Plumed, F., Contreras-Ochando, L., Ferri, C., Hernández-Orallo, J., Kull, M., Lachiche, N., Ramírez-Quintana, M. J., & Flach, P. (2021). CRISP-DM twenty years later: From data mining processes to data science trajectories. *IEEE Transactions on Knowledge and Data Engineering*, 33(8), 3048–3061. https://doi.org/10.1109/TKDE.2019.2962680

Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., & Gebru, T. (2019). Model cards for model reporting. *Proceedings of the Conference on Fairness, Accountability, and Transparency*, 220–229.

Saltz, J. S. (2021). CRISP-DM for data science: Strengths, weaknesses and potential next steps. *Proceedings of the IEEE International Conference on Big Data*. https://www.researchgate.net/publication/357821509

Saltz, J. S., & Shamshurin, I. (2016). Big data team process methodologies: A literature review and the identification of key factors for a project's success. *Proceedings of the IEEE International Conference on Big Data*, 2872–2879.

Schröer, C., Kruse, F., & Gómez, J. M. (2021). A systematic literature review on applying CRISP-DM process model. *Procedia Computer Science*, 181, 526–534. https://doi.org/10.1016/j.procs.2021.01.199

Siegel, E. (2024). Why machine learning isn't enough. *Harvard Business Review*. (bizML framework.)

Stefanovskyi, A. (2023). The most important phase of CRISP-DM you need to get right: Business Understanding. *Medium*. https://medium.com/@stefanovskyi/business-understanding-crisp-dm-1111bfbc7b8d

Studer, S., Bui, T. B., Drescher, C., Hanuschkin, A., Winkler, L., Peters, S., & Müller, K.-R. (2021). Towards CRISP-ML(Q): A machine learning process model with quality assurance methodology. *Machine Learning and Knowledge Extraction*, 3(2), 392–413. https://doi.org/10.3390/make3020020

Taylor, J. (2017, January 18). Four problems in using CRISP-DM and how to fix them. *KDnuggets*. https://www.kdnuggets.com/2017/01/four-problems-crisp-dm-fix.html

Ulwick, A. (2024). *Jobs-to-be-Done: The original framework*. Strategyn. https://strategyn.com/jobs-to-be-done/

Wikipedia. (2025). Cross-industry standard process for data mining. https://en.wikipedia.org/wiki/Cross-industry_standard_process_for_data_mining

Wilkinson, M. D., Dumontier, M., Aalbersberg, I. J., Appleton, G., Axton, M., Baak, A., Blomberg, N., Boiten, J.-W., da Silva Santos, L. B., Bourne, P. E., et al. (2016). The FAIR Guiding Principles for scientific data management and stewardship. *Scientific Data*, 3, 160018. https://doi.org/10.1038/sdata.2016.18

Wirth, R., & Hipp, J. (2000). CRISP-DM: Towards a standard process model for data mining. *Proceedings of the 4th International Conference on the Practical Applications of Knowledge Discovery and Data Mining*, 29–40.
