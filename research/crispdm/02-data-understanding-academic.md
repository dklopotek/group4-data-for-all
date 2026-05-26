# CRISP-DM Phase 2 — Data Understanding: An Academic Synthesis for Pipeline Architects

**Author context.** This document is one of a series of phase-by-phase academic syntheses written to support graduate seminar work in computational urban ecology (project: Mycorrhizal Barcelona). It treats CRISP-DM not as a checklist but as a contestable model whose silences must be filled by the post-2018 dataset-documentation literature. The audience is the pipeline *architect* — the person responsible for justifying why a downstream analysis can be trusted — not a model-builder or UI designer.

---

## 1. Canonical Phase 2: the four generic tasks and their outputs

In the reference model published by the original CRISP-DM consortium, Phase 2 (Data Understanding) is described as a four-task generic block immediately following Business Understanding and immediately preceding Data Preparation (Chapman et al., 2000). The four generic tasks, with their canonical output documents, are:

1. **Collect Initial Data** — output: *Initial Data Collection Report.* The task is to acquire (or access in place) the data listed in the project resources, log every source, every access method, every problem encountered, and every resolution adopted. The deliverable is a document, not a dataset.
2. **Describe Data** — output: *Data Description Report.* Examine the gross properties of the data: format, quantity (rows, columns, size on disk), identities of fields, and any identifier conventions. The report must surface whether the acquired data even meet the project's stated requirements.
3. **Explore Data** — output: *Data Exploration Report.* Probe deeper: distributions of key attributes, relationships among small numbers of attributes, simple aggregations, and the properties of significant sub-populations. The report should explicitly state findings, hypotheses generated, and impacts on the rest of the project plan.
4. **Verify Data Quality** — output: *Data Quality Report.* List, for each data source, the quality problems discovered (missingness, errors, coding inconsistencies, metadata conflicts) and, where possible, *solutions* the project will adopt — solutions that will be operationalized in Phase 3 (Data Preparation).

The reference model deliberately frames these tasks as **iterative and recursive with Business Understanding**: discoveries in Phase 2 routinely force a return to Phase 1 to re-scope the question (Chapman et al., 2000, §2.3). This iteration is not a failure mode; it is the model's central epistemological commitment.

CRISP-DM has remained the most-cited generic process model for data work for a quarter-century (Schröer et al., 2021), and was extended in 2021 to CRISP-ML(Q) — a quality-assured variant that decomposes each phase into requirements, constraints, tasks, risks and quality-assurance methods (Studer et al., 2021). For the architect, the most important update in CRISP-ML(Q) is the explicit naming of *data quality* as a phase-level constraint and the introduction of risk categories (e.g. concept drift, label noise, bias) that must be mitigated within Phase 2 rather than discovered downstream.

## 2. Why Phase 2 is the most-skipped phase in practice

The empirical literature is now unambiguous: data work is systematically undervalued in ML and data-driven projects, with measurable downstream cost. The canonical reference is Sambasivan et al.'s CHI 2021 paper, whose title is itself the finding: "*Everyone wants to do the model work, not the data work*". In interviews with 53 high-stakes AI practitioners across India, East and West Africa and the United States, **92 % reported experiencing "data cascades"** — compounding events in which undervalued data work in early phases triggered failures (sometimes catastrophic) in deployment, evaluation, or maintenance (Sambasivan et al., 2021).

Five mechanisms recurred:
- *physical-world brittleness* (sensors, label drift),
- *inadequate domain expertise* in data collection,
- *conflicting reward systems* that incentivize model-publishing over data documentation,
- *poor cross-organizational documentation*, and
- *clashes between brittle ML practices and messy live data*.

These cascades were "opaque and protracted" — i.e. they did not manifest as obvious bugs but as quiet degradation of the science (Sambasivan et al., 2021, p. 1). Heger et al. (2022) corroborated this from the documentation side: ML practitioners regard data documentation as low-status work, perform it inconsistently, and frequently lack the tooling, training and organizational mandate to do it well. Polyzotis et al. (2018), surveying production ML at Google, similarly identified *data understanding, data validation and data preparation* as the three under-served lifecycle stages where production failures concentrate.

The implication for the architect is direct: any pipeline whose Phase 2 deliverable is *only* a Jupyter notebook with a few `.head()` and `.describe()` calls is statistically over-represented in the failure literature. The artifacts of Phase 2 must be **documents**, written for human readers, defensible at the primary source, and re-readable months later when someone challenges a claim.

## 3. Initial data collection — what "initial" means

The "Collect Initial Data" task is widely misread as "download everything that looks relevant." The reference model is more disciplined: collect what is needed to *characterize* the candidate data sources well enough to make a defensible go/no-go choice (Chapman et al., 2000). Three sub-decisions structure this task.

**Sampling strategy at ingest.** When candidate sources are large (e.g., a full Sentinel-2 tile stack, a multi-year GBIF download, a national cadastral dump), the architect must decide whether to ingest a stratified sample (representative across the relevant axes), a temporal slice, a spatial slice matching the project's area of interest, or a metadata-only manifest. The choice is consequential: a too-large initial download wastes storage and discourages exploration; a too-small one biases the data-quality assessment toward whatever sub-population happened to be in the sample. Polyzotis et al. (2018) argue that *schema-level* sampling — pulling only enough to confirm field names, types, and value ranges — is often sufficient for Phase 2, with full ingestion deferred to Phase 3.

**Exploratory ingestion patterns.** The literature on data engineering has converged on a "**land then describe**" pattern: write raw immutable bytes to a quarantine zone, register provenance metadata (source URL, retrieval timestamp, hash, license, retrieval agent), and only then run description and exploration jobs. This is the technical implementation of the reference model's insistence that initial data collection produces a *report*, not just a folder of files.

**The cost asymmetry.** Collecting too much is recoverable (delete, narrow); collecting too little is often irrecoverable, especially when the data are observational and time-stamped (sensor archives that lapse, satellite revisits that pass, ephemeral citizen-science records). For environmental projects, conservative over-collection of the *time dimension* is usually the right default, while spatial and spectral dimensions can be more aggressively scoped.

## 4. Data description — schema, typing, cardinality, and the rise of dataset documentation frameworks

The "Describe Data" task expects, at minimum: counts (rows, columns, size on disk), field-by-field type inference, identifier-and-key inventory, and confirmation that the data meet the project's stated requirements (Chapman et al., 2000). In modern practice this is operationalized by tools that *infer a schema* (TensorFlow Data Validation, Great Expectations, Pandera, frictionless data) and then expect a human to ratify it (Breck et al., 2019). Schema inference is "best-effort" — TFDV's documentation is explicit that the auto-generated schema must be reviewed before downstream code depends on it.

Beyond mechanical description, the post-2018 literature has produced **four widely cited dataset documentation frameworks**. The architect should know all four, when each fits, and where they overlap.

**Datasheets for Datasets (Gebru et al., 2021).** Inspired by electronics-industry datasheets, this framework proposes that every dataset ship with a structured document organized around seven sections — *Motivation, Composition, Collection Process, Preprocessing/Cleaning/Labeling, Uses, Distribution, Maintenance* — articulated through 57 questions. The framework's central contribution is the *Uses* section, which forces dataset creators to enumerate intended uses and, crucially, *uses to avoid*. Datasheets are now standard practice in major repositories (Hugging Face Hub, OpenML, Papers With Code).

**Data Statements for NLP (Bender & Friedman, 2018).** A more linguistically and demographically focused framework, written for natural-language datasets. The contribution is its insistence on documenting *speaker* and *annotator* demographics, curation rationale, language variety, and text characteristics — categories that make bias auditing tractable. The two authors' subsequent work (Bender & Friedman, 2018, TACL 6:587-604) made data statements a standard expectation in ACL-venue submissions.

**Dataset Nutrition Labels (Holland et al., 2018).** A visual, modular, at-a-glance framework. The label combines qualitative and statistical "modules" — provenance, variable descriptions, statistics, pair-plots, ground-truth correlations, probabilistic models — into a one-page report intended for *consumers*. The framework's distinctive contribution is its insistence that the label be machine-generated from the dataset itself wherever possible, with human-authored sections only where automation cannot reach (motivation, intended use).

**Data Cards (Pushkarna et al., 2022).** Developed at Google, Data Cards extend Datasheets with explicit *audience targeting* (researchers, decision-makers, end-users, reviewers), structured around the OFTEn framework (Observations, Findings, Theories, Explanations). Data Cards introduce *transparency artifacts* and *purposeful* design that prioritize the questions readers actually ask. They are now embedded in Google's internal ML release processes.

A complementary contribution from the same period is **Hutchinson et al. (2021)** — *Towards Accountability for Machine Learning Datasets* — which argues that dataset development should adopt the auditability practices of software engineering: versioning, change logs, test suites, requirements traceability, and post-release maintenance. Hutchinson et al. essentially recast Datasheets as one artifact in a much larger *dataset lifecycle governance* model.

The four frameworks have considerable overlap (motivation, composition, collection, intended uses recur in every one). They differ in **emphasis**: Datasheets on motivation and uses; Data Statements on demographic representativeness; Nutrition Labels on at-a-glance machine-readable summaries; Data Cards on audience-purposeful disclosure. For an AEC/environmental pipeline, the practical recommendation in the recent literature (Heger et al., 2022; Pushkarna et al., 2022) is to **pick one framework and adapt it**, rather than try to satisfy all four. The 2024 *Croissant* metadata format (Akhtar et al., 2024) is an attempt to provide a machine-readable lingua franca across frameworks; it is already supported by Hugging Face, Kaggle, Google Dataset Search and OpenML and represents the most credible standardization effort in the field.

## 5. Data exploration — EDA for pipeline design, not just modeling

Exploration as taught in the EDA tradition (Tukey, 1977) emphasizes graphical, distribution-aware, robust techniques for *understanding* a dataset before fitting a model. For pipeline architects, several EDA techniques map specifically to pipeline-relevant questions:

- **Coverage maps for spatial data.** Plot point density or per-cell counts across the area of interest. Holes are findings: they may be artifacts of sensor placement, sampling bias, administrative boundaries, or data licensing. iNaturalist's well-documented under-sampling outside English-speaking countries is the canonical example.
- **Gap-and-overlap analysis.** For temporal data, plot record counts per unit time as a histogram or strip plot. Gaps reveal sensor outages, retroactive censorship, or pipeline-side bugs. Overlaps (the same observation recorded by multiple ingest paths) reveal de-duplication needs.
- **Joinability checks.** For every pair of datasets that will be joined downstream, audit the join key's cardinality, type, completeness and coding stability. The cost of discovering a join failure in Phase 5 is orders of magnitude higher than discovering it in Phase 2.
- **Time-coverage histograms.** When datasets span multiple years, year-by-year record counts often reveal regime changes (a new data-collection protocol, a sensor replacement, an institutional handover). These regime changes constitute hidden subpopulations that will confound any longitudinal claim.
- **Cardinality and value-frequency profiles.** For categorical fields, the top-N values and the long tail both matter: the long tail is where typos, deprecated codes, and free-text contamination live.
- **Pair-plots restricted to candidate predictors.** Even when the project is not building a model, pair-plots reveal redundancy (two fields measuring the same thing) and incompatibility (two fields claiming the same name but measuring different things).

Polyzotis et al. (2018) and Breck et al. (2019) extend this by arguing that exploration should produce *executable artifacts*: schemas with statistical guardrails (min/max, allowed-value sets, missingness budgets) that can be re-run on every fresh ingest to detect drift. For long-lived pipelines this is non-optional; for one-shot research pipelines it is still good hygiene.

## 6. Data quality verification — frameworks and dimensions

The most cited academic framework for data quality dimensions is Wang & Strong (1996), who consolidated 118 attributes elicited from data consumers into 15 dimensions, organized as four categories:

- **Intrinsic** — accuracy, objectivity, believability, reputation;
- **Contextual** — relevancy, value-added, timeliness, completeness, appropriate amount;
- **Representational** — interpretability, ease of understanding, consistency, concise representation;
- **Accessibility** — accessibility, access security.

The framework's enduring contribution is the insight that *quality is consumer-defined and context-dependent*: a dataset that is "high quality" for one project may be unfit for another, and the difference is not a property of the data alone.

The international standards body has codified a similar but more concise model in **ISO/IEC 25012** (Software product Quality Requirements and Evaluation — Data Quality Model), which defines fifteen characteristics partitioned into *inherent* (accuracy, completeness, consistency, credibility, currentness) and *system-dependent* (availability, portability, recoverability, accessibility, compliance, confidentiality, efficiency, precision, traceability, understandability) categories. The ISO/IEC 25024 companion standard provides measurement procedures. **ISO 8000** addresses data-quality management at the enterprise level (provenance, master data, transactional data).

For ML-era pipelines, two further considerations supplement these classical frameworks:

- **Label-noise as a first-class quality dimension.** Northcutt et al. (2021) audited the test sets of ten of the most-cited ML benchmarks and found an average of 3.3 % label errors, with ImageNet's validation set above 6 %. Even MNIST contained validated errors. Their finding — that model rankings are unstable under correctly relabeled test sets — is direct evidence that downstream "model accuracy" inherits upstream label quality. For environmental projects this generalizes: a citizen-science species identification that is 80 % accurate is a different artifact than one that is 99 % accurate, and the difference shapes every claim downstream.
- **Provenance and lineage.** The FAIR principles (Wilkinson et al., 2016) — Findable, Accessible, Interoperable, Reusable — make explicit that *re-usability* depends on provenance metadata (R1 — "data are richly described with a plurality of accurate and relevant attributes") and lineage (R1.2 — "data are associated with detailed provenance"). For an AEC pipeline integrating municipal, satellite, biodiversity and sensor data, FAIR compliance is the minimum bar that makes the pipeline auditable.

In practice, the architect builds the Phase 2 Data Quality Report around a small number of these dimensions chosen for project relevance (typically: completeness, currentness, accuracy/credibility, consistency across joins, and bias) and explicitly *defers* the others to a "known unknowns" register.

## 7. Geospatial-specific nuances

CRISP-DM is domain-agnostic, and its silence on spatial data is one of its real weaknesses for AEC and environmental work. The architect must explicitly add the following considerations to Phase 2:

**Resolution matching.** Spatial datasets have native resolution (raster cell size, vector minimum mapping unit, point sampling density). Joining two layers at different resolutions without explicit handling produces silent failures (aggregation choices that change the answer). The "2× rule" used by the earn-the-data skill — data resolution at least twice as fine as the decision unit — is a conservative reformulation of the Nyquist intuition and is broadly supported in the spatial-analysis literature.

**CRS verification.** Every spatial dataset carries (or should carry) a coordinate reference system. Joining datasets in different CRSs without reprojection produces shifts of metres to kilometres. Reprojection is itself lossy: raster reprojection requires resampling, which alters cell-level values and is not exactly reversible (Lovelace et al., *Geocomputation with R*). The architect must record the CRS of every layer at ingest and the reprojection target chosen for analysis, ideally in the data sheet's Pre-processing section.

**The Modifiable Areal Unit Problem (MAUP).** Identified by Gehlke and Biehl (1934) and formalized by Openshaw and Taylor (1979), the MAUP is the well-documented statistical artifact whereby *the same underlying point process produces different correlations, regressions and rates when aggregated to different areal units* (the *scale effect*) or to different boundaries at the same scale (the *zone effect*). For any project that aggregates point observations into administrative or grid cells — and most urban-ecology projects do — MAUP must be acknowledged in Phase 2, not after results are in.

**Edge effects.** Spatial processes that are partially observed near the boundary of a study area (e.g., a buffer that extends beyond the city limit, a species range that crosses a national border) introduce edge effects that bias any local statistic. The architect should explicitly buffer the study area or mark edge observations.

**Unit and time-zone hygiene.** ERA5 temperatures are in Kelvin; many municipal sensors report local time; satellite passes are UTC; coordinate-pair conventions vary (lat,lon vs lon,lat). These are silent-failure categories — analyses that run without errors but produce nonsense.

## 8. Benchmarking the earn-the-data discipline against the literature

The "earn-the-data" skill in this repository encodes a ten-step discipline for dataset discovery and vetting that originated in master's-level urban-ecology research. The discipline reads as follows (paraphrased):

1. Identify the *decision unit* (smallest spatial, temporal, spectral scale of claims).
2. *Hunt* across six categories (remote-sensing optical, remote-sensing thermal/radar, climate reanalysis, in-situ sensors, biodiversity, built environment).
3. *Verify at primary source* — never trust secondhand summaries.
4. Apply the *2× resolution rule*.
5. Score survivors on a *five-dimension rubric* (Provenance, Resolution, Coverage, Licensing, Bias).
6. Draft an *8-section data sheet* per recommended dataset (Gebru et al.'s seven plus a Limitations section).
7. Flag *coordinate-system and unit pitfalls*.
8. Name *sampling biases* as first-class findings.
9. Generate a *profiling plan* (eight EDA checks: shape, missingness, numeric summaries, categorical summaries, spatial coverage, temporal coverage, cross-field consistency, bridging keys).
10. *Revisit the brief* — does the original research question still hold?

Mapped against the canonical CRISP-DM Phase 2 tasks (Chapman et al., 2000), the coverage is as follows:

| earn-the-data step | CRISP-DM Phase 2 task | Literature alignment | Coverage |
|---|---|---|---|
| 1. Decision unit | Bridges Phase 1↔2 (sets requirements that drive collection) | Chapman §2.1; Polyzotis 2018 | **Strong** |
| 2. Hunt across six categories | Collect Initial Data (Outline data requirements) | Chapman §3.2 | **Strong (domain-specialized)** |
| 3. Verify at primary source | Collect Initial Data (Acquire data) + Verify Data Quality (provenance) | Wilkinson 2016 (FAIR); Hutchinson 2021 | **Strong** |
| 4. 2× resolution rule | Collect Initial Data (requirement check) + Verify (fitness for purpose) | Spatial analysis canon (Openshaw 1979) | **Strong; novel framing** |
| 5. Five-dimension rubric | Verify Data Quality | Wang & Strong 1996 (broader); ISO 25012 (broader) | **Partial — narrower than Wang & Strong** |
| 6. 8-section data sheet | Describe Data (formal documentation) | Gebru 2021; Pushkarna 2022; Bender & Friedman 2018 | **Strong** |
| 7. CRS/unit pitfalls | Verify Data Quality (consistency, accuracy) | Geospatial canon | **Strong; domain-specialized** |
| 8. Name biases | Verify Data Quality (bias as quality dimension) | Sambasivan 2021; Bender & Friedman 2018 | **Strong** |
| 9. Profiling plan | Explore Data | Tukey 1977; Breck 2019 (TFDV) | **Strong** |
| 10. Revisit the brief | Iterates back to Business Understanding | Chapman §2.3 | **Strong; explicit step that CRISP-DM only implies** |

**Identified gaps** (places where earn-the-data is silent or thinner than the literature recommends):

- **G1. Initial Data Collection *Report* artifact.** earn-the-data produces inventory, data sheets, profiling plan and brief-revisit, but does not require the *narrative ingestion log* Chapman et al. (2000) specify under "Initial Data Collection Report" — capturing access method, retrieval timestamps, retrieval agent, errors encountered, fallbacks adopted. This is what enables exact re-execution.
- **G2. Data Description Report as a formal artifact.** The earn-the-data 8-section data sheet covers *what the data are* but does not require a separate report on *what was actually ingested* (row counts, file hashes, size on disk, schema as inferred at ingest). For pipeline reproducibility this is the artifact future-you needs.
- **G3. Quality dimensions narrower than Wang & Strong.** The 5-dimension rubric (Provenance, Resolution, Coverage, Licensing, Bias) is *selection*-oriented — appropriate for go/no-go decisions — but does not cover Wang & Strong's full set (e.g., timeliness, interpretability, consistency across versions, believability, accessibility-security). The architect of an evidence-defensible pipeline should explicitly map the 5-dimension rubric onto the dimensions left out, even if only to acknowledge that they were considered.
- **G4. Schema-as-code (executable validation).** Breck et al. (2019) and Polyzotis et al. (2018) make a strong case that the Phase 2 schema should be **executable** (TFDV, Great Expectations, Pandera) so that re-runs detect drift. earn-the-data's profiling plan is human-runnable; a schema-as-code artifact would close the loop.
- **G5. MAUP and edge-effects.** Resolution and CRS are addressed; MAUP and edge-effect aggregation artifacts are not explicitly named in the rubric. For aggregated spatial analyses these are first-class confounders.
- **G6. Label-noise / annotation-quality.** earn-the-data is implicit on annotation-quality (which falls under "Bias" in the rubric). Northcutt et al. (2021) demonstrate that label noise is a measurable, separable concern — distinct from sampling bias — and worth its own line in the rubric for citizen-science and crowd-annotated sources (iNaturalist, GBIF research-grade flags).
- **G7. Machine-readable metadata artifact.** earn-the-data produces Markdown documents. The 2024 Croissant standard (Akhtar et al., 2024) enables a machine-readable JSON-LD sidecar that downstream tooling can ingest. For a project that may publish its pipeline (the stated goal here), an export step into Croissant or DCAT would be valuable.
- **G8. Dataset versioning / change-log.** Hutchinson et al. (2021) argue that datasets need software-engineering-grade versioning and change logs. earn-the-data captures version-at-retrieval; it does not require ongoing change-tracking. For a long-lived pipeline that re-ingests, this is a gap.

**Where earn-the-data exceeds canonical CRISP-DM.** Three steps go *beyond* the 2000 reference model in ways the post-2018 literature endorses:

- Decision unit (Step 1) makes explicit a Phase 1↔2 dependency the original model only implies.
- 2× resolution rule (Step 4) operationalizes a fitness-for-purpose check that Chapman et al. (2000) leave abstract.
- Brief-revisit (Step 10) institutionalizes the iteration that the reference model says should happen but does not require as a deliverable.

These three are genuine contributions, not redundancies, and they are why earn-the-data is the right backbone for Phase 2 rather than a generic CRISP-DM checklist.

## 9. Recommended companion checklist for the gaps

Rather than rewrite earn-the-data, the literature supports a thin companion artifact that runs *after* the ten steps and adds:

1. **Ingestion Log.** For each retrieved source: retrieval timestamp (UTC), exact URL or API call, agent (script name, version), file hash (SHA-256), file size, observed encoding, errors encountered, fallbacks adopted. (Closes G1.)
2. **Ingested-Data Description.** Per source: row count, column list with inferred dtypes, observed value ranges per numeric field, observed cardinality per categorical field, file format and on-disk size. (Closes G2.)
3. **Wang & Strong / ISO 25012 cross-check.** A one-page mapping that records, for each recommended dataset, whether each of the 15 Wang & Strong dimensions (or ISO 25012 characteristics) was assessed, deferred, or judged not-applicable. (Closes G3.)
4. **Executable schema.** A `schema.yaml` or `expectations.json` per source, suitable for re-running on fresh ingests to detect drift. (Closes G4.)
5. **MAUP / edge-effect declaration.** For any analysis that aggregates point observations to areal units, an explicit statement of: aggregation unit chosen, sensitivity to alternative units tested, edge-buffer policy. (Closes G5.)
6. **Annotation-quality estimate.** For crowd-annotated or citizen-science sources, an estimate (or honest unknown) of label-error rate, with reference to any audit or cross-validation. (Closes G6.)
7. **Croissant sidecar.** A machine-readable `croissant.jsonld` export of the data sheet for each recommended dataset. (Closes G7.)
8. **Versioning policy.** A short statement of how this project will track dataset version changes between Phase 2 and project end. (Closes G8.)

These eight items are short, additive, and do not require re-doing the ten-step discipline — they ride on top of it.

## 10. Handoff to Phase 3 (Data Preparation)

Phase 3 expects, at minimum: a definitive dataset inventory, a documented set of quality issues with mitigation strategies, and an operational schema. The artifacts the architect should hand off from Phase 2 — combining earn-the-data outputs with the companion checklist above — are:

- `decision-unit.md` — the spatial/temporal/spectral unit at which claims must hold (from earn-the-data Step 1).
- `data-inventory.md` — every candidate considered with rubric scores and inclusion/exclusion reasoning (earn-the-data Step 5).
- `data-sheets/<source>.md` — one 8-section data sheet per recommended dataset (earn-the-data Step 6).
- `ingestion-log.md` — chronological log of all retrievals (companion item 1).
- `ingested-data-description.md` — per-source row/column/type/size manifest (companion item 2).
- `quality-cross-check.md` — Wang & Strong / ISO 25012 dimensions assessed (companion item 3).
- `schemas/<source>.yaml` — executable schemas (companion item 4).
- `geospatial-declarations.md` — CRS, MAUP, edge-effect statements (earn-the-data Step 7 + companion item 5).
- `bias-and-annotation.md` — sampling biases and annotation-quality estimates (earn-the-data Step 8 + companion item 6).
- `profiling-plan.md` — the 8-cell EDA checklist per dataset (earn-the-data Step 9).
- `croissant/<source>.jsonld` — machine-readable metadata (companion item 7).
- `versioning-policy.md` — change-tracking statement (companion item 8).
- `brief-revisit.md` — does the research question still hold (earn-the-data Step 10).

If any of these are missing, Phase 3 should not start. The reason is not bureaucratic: it is that each missing artifact is a known failure mode in the empirical literature on data cascades (Sambasivan et al., 2021), production ML data validation (Breck et al., 2019; Polyzotis et al., 2018), or dataset accountability (Hutchinson et al., 2021).

---

## References

Akhtar, M., Benjelloun, O., Conforti, C., Gijsbers, P., Goswami, S., Hettinger, J., et al. (2024). *Croissant: A Metadata Format for ML-Ready Datasets.* Advances in Neural Information Processing Systems 37 (Datasets and Benchmarks Track). https://arxiv.org/abs/2403.19546

Bender, E. M., & Friedman, B. (2018). Data statements for natural language processing: Toward mitigating system bias and enabling better science. *Transactions of the Association for Computational Linguistics, 6,* 587-604. https://aclanthology.org/Q18-1041/

Breck, E., Polyzotis, N., Roy, S., Whang, S. E., & Zinkevich, M. (2019). Data validation for machine learning. *Proceedings of the 2nd SysML Conference.* https://mlsys.org/Conferences/2019/doc/2019/167.pdf

Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C., & Wirth, R. (2000). *CRISP-DM 1.0: Step-by-step data mining guide.* CRISP-DM Consortium. (Reference model and user guide, esp. §2 and §3.2-3.5.)

Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., & Crawford, K. (2021). Datasheets for datasets. *Communications of the ACM, 64*(12), 86-92. https://doi.org/10.1145/3458723

Gehlke, C. E., & Biehl, K. (1934). Certain effects of grouping upon the size of the correlation coefficient in census tract material. *Journal of the American Statistical Association, 29*(185A), 169-170.

Heger, A. K., Marquis, L. B., Vorvoreanu, M., Wallach, H., & Wortman Vaughan, J. (2022). Understanding machine learning practitioners' data documentation perceptions, needs, challenges, and desiderata. *Proceedings of the ACM on Human-Computer Interaction, 6*(CSCW2), Article 340. https://doi.org/10.1145/3555760

Holland, S., Hosny, A., Newman, S., Joseph, J., & Chmielinski, K. (2018). *The Dataset Nutrition Label: A framework to drive higher data quality standards.* arXiv:1805.03677. https://arxiv.org/abs/1805.03677

Hutchinson, B., Smart, A., Hanna, A., Denton, E., Greer, C., Kjartansson, O., Barnes, P., & Mitchell, M. (2021). Towards accountability for machine learning datasets: Practices from software engineering and infrastructure. *Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency (FAccT '21),* 560-575. https://doi.org/10.1145/3442188.3445918

ISO/IEC 25012:2008. *Software engineering — Software product Quality Requirements and Evaluation (SQuaRE) — Data quality model.* International Organization for Standardization. https://www.iso.org/standard/35736.html

Northcutt, C. G., Athalye, A., & Mueller, J. (2021). Pervasive label errors in test sets destabilize machine learning benchmarks. *Proceedings of the 35th Conference on Neural Information Processing Systems (NeurIPS 2021), Datasets and Benchmarks Track.* https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/hash/f2217062e9a397a1dca429e7d70bc6ca-Abstract-round1.html

Openshaw, S., & Taylor, P. J. (1979). A million or so correlation coefficients: Three experiments on the modifiable areal unit problem. In N. Wrigley (Ed.), *Statistical applications in the spatial sciences* (pp. 127-144). Pion.

Polyzotis, N., Roy, S., Whang, S. E., & Zinkevich, M. (2018). Data lifecycle challenges in production machine learning: A survey. *SIGMOD Record, 47*(2), 17-28. https://doi.org/10.1145/3299887.3299891

Pushkarna, M., Zaldivar, A., & Kjartansson, O. (2022). Data Cards: Purposeful and transparent dataset documentation for responsible AI. *Proceedings of the 2022 ACM Conference on Fairness, Accountability, and Transparency (FAccT '22),* 1776-1826. https://doi.org/10.1145/3531146.3533231

Sambasivan, N., Kapania, S., Highfill, H., Akrong, D., Paritosh, P., & Aroyo, L. M. (2021). "Everyone wants to do the model work, not the data work": Data cascades in high-stakes AI. *Proceedings of the 2021 CHI Conference on Human Factors in Computing Systems (CHI '21),* Article 39. https://doi.org/10.1145/3411764.3445518

Schröer, C., Kruse, F., & Gómez, J. M. (2021). A systematic literature review on applying CRISP-DM process model. *Procedia Computer Science, 181,* 526-534. https://doi.org/10.1016/j.procs.2021.01.199

Studer, S., Bui, T. B., Drescher, C., Hanuschkin, A., Winkler, L., Peters, S., & Müller, K.-R. (2021). Towards CRISP-ML(Q): A machine learning process model with quality assurance methodology. *Machine Learning and Knowledge Extraction, 3*(2), 392-413. https://doi.org/10.3390/make3020020

Tukey, J. W. (1977). *Exploratory data analysis.* Addison-Wesley.

Wang, R. Y., & Strong, D. M. (1996). Beyond accuracy: What data quality means to data consumers. *Journal of Management Information Systems, 12*(4), 5-33. https://doi.org/10.1080/07421222.1996.11518099

Wilkinson, M. D., Dumontier, M., Aalbersberg, I. J., Appleton, G., Axton, M., Baak, A., et al. (2016). The FAIR Guiding Principles for scientific data management and stewardship. *Scientific Data, 3,* 160018. https://doi.org/10.1038/sdata.2016.18
