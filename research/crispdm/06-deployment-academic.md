# CRISP-DM Phase 6: Deployment — Reframed for Data-Pipeline Handoff

*A graduate-seminar research note on what "Deployment" means when the deliverable is a reproducible pipeline and a documented data product, not a user-facing system.*

---

## 1. Reframing Phase 6 for Pipeline-Only Projects

The classical Cross-Industry Standard Process for Data Mining (CRISP-DM) defines Phase 6 — *Deployment* — as "the organization of the knowledge gained in a form that the customer can use" (Chapman et al., 2000, p. 14). In the canonical reference guide, Chapman et al. enumerate four generic tasks: *Plan Deployment*, *Plan Monitoring and Maintenance*, *Produce Final Report*, and *Review Project*. The literature has long acknowledged that "deployment" in CRISP-DM is the most under-specified phase because it depends entirely on what the deliverable is (Martínez-Plumed et al., 2021).

For most industrial readings of CRISP-DM, deployment is assumed to mean *operationalizing a model* — pushing a scoring function to a production API, embedding it in a business workflow, or instrumenting a dashboard. Sculley et al. (2015) and Paleyes et al. (2022) write almost exclusively from this stance: deployment is the moment a model meets a live system, and the bulk of cost is in maintaining that system.

This framing does not fit the project at hand. In a graduate seminar on data-pipeline design, the explicit course constraint is **no frontend, no API, no production model**. The student is being trained as the *architect of a data system*, not as a deployment engineer. The deliverable is:

1. A **reproducible pipeline** (notebooks, scripts, lockfiles, container specifications, data manifests).
2. A **documented data product** — typically a derived dataset, a composite index, or a network graph — with a datasheet, methods document, and intended-use statement.
3. A **handoff package** that an intended user (e.g., an urban-planning office, a city ecologist, a research collaborator) can read, re-run, audit, extend, and cite.

Under this reading, Phase 6 becomes: **release, publish, document for handoff, and plan maintenance** — not "build a dashboard." This document develops that reframing in depth and grounds it in the open-science, FAIR-data, and reproducibility literatures.

## 2. The Canonical Four Tasks

Chapman et al. (2000) define Phase 6 around four generic tasks. The reframing below preserves their structure but reinterprets their outputs.

| Canonical task | Industrial reading | Pipeline-handoff reading |
|---|---|---|
| Plan Deployment | Plan model rollout to production | Plan **release packaging and publication** of pipeline + data product |
| Plan Monitoring and Maintenance | Plan drift detection and re-training | Plan **upstream-source monitoring**, dependency refresh, ownership transfer |
| Produce Final Report | Executive deck for sponsor | Produce **final report + datasheet + methods document + intended-use statement** |
| Review Project | Internal retrospective | **Open retrospective** with lessons-learned register, what-to-do-differently note, contribution accounting |

The phase is, in other words, less about *running* anything and more about *closing the loop*: making the work usable, citable, auditable, and re-runnable by someone other than its author.

## 3. Plan Deployment for Data Products

In a pipeline-only project, "Plan Deployment" means deciding **what gets released, in what form, on what channel, with what version**.

### 3.1 Release packaging

A minimum-viable release bundle for a data pipeline contains:

- **Code**: notebooks, scripts, package code (with module structure).
- **Environment specification**: lockfile (`poetry.lock`, `conda-lock`, `pip-tools` compiled `requirements.txt`) and a container recipe (Dockerfile or Apptainer/Singularity definition).
- **Data manifests**: a list of every input dataset with version, accession URL, license, retrieval date, and hash; plus a list of every output dataset.
- **Documentation**: README, datasheet for each produced dataset (Gebru et al., 2021), methods document, intended-use statement, limitations register, "how to re-run" guide.
- **Provenance metadata**: a machine-readable record of inputs → transformations → outputs (PROV-O is the W3C standard).
- **License files**: separate licenses for code (e.g., MIT, Apache-2.0) and data (e.g., CC-BY-4.0, ODbL).

### 3.2 Versioning

Data products need versioning just as code does. A pragmatic convention is **semantic versioning for data**: MAJOR.MINOR.PATCH where MAJOR breaks consumers (schema change), MINOR adds non-breaking content (more rows, new optional fields), and PATCH fixes errors (corrected values, fixed typos). Klímek et al. (2019) and the Data Versioning Working Group of the Research Data Alliance have proposed similar conventions.

Equally important is **input versioning**: pinning the exact version of every upstream dataset. If the input is a snapshot (e.g., GBIF download), the snapshot DOI must be recorded; if it is a live API, the retrieval timestamp and query parameters must be recorded.

### 3.3 Publishing channels

Publication channels for data products include:

- **General-purpose archives**: Zenodo, Figshare, Dryad, Open Science Framework. These mint DOIs and provide long-term preservation. Zenodo is the de facto standard for citable code releases via its GitHub integration (Sicilia et al., 2017).
- **Domain repositories**: GBIF (biodiversity occurrences), PANGAEA (earth and environmental science), ICPSR (social science), EBI (life sciences). Domain repositories enforce stricter metadata standards.
- **Geospatial portals**: the OGC stack (WMS, WFS, OGC API Features) and ISO 19115/19139 metadata are the standards for spatial data. INSPIRE (the EU Infrastructure for Spatial Information) defines interoperability requirements for member-state spatial data (European Commission, 2007).
- **Institutional repositories**: university dataverses, library-managed CRIS systems. These tend to have the longest preservation guarantees.
- **Open-data portals**: city-level (e.g., Open Data BCN), regional, or national. These are appropriate when the audience is the public sector that will *consume* the data.

The choice depends on (a) who the intended user is, (b) what metadata standard the user expects, and (c) what citation/credit infrastructure exists. For a city-planning office, an open-data portal listing plus a Zenodo DOI for archival is usually the right combination.

## 4. FAIR Principles in Depth

The FAIR Guiding Principles — Findable, Accessible, Interoperable, Reusable — were articulated by Wilkinson et al. (2016) and have become the dominant framework for data-product release planning. FAIR is **not synonymous with open**; a dataset can be FAIR and access-restricted (e.g., behind authentication for privacy reasons), as long as access conditions are clearly stated. The four pillars, with operational checklists:

### 4.1 Findable

- **F1**: (Meta)data assigned a globally unique and persistent identifier (DOI, ARK, Handle).
- **F2**: Data described with rich metadata.
- **F3**: Metadata clearly and explicitly include the identifier of the data they describe.
- **F4**: (Meta)data registered or indexed in a searchable resource (e.g., DataCite, GBIF, an institutional catalog).

*Practical check*: can a stranger Google a phrase from the project and reach a landing page with a DOI?

### 4.2 Accessible

- **A1**: (Meta)data retrievable by their identifier using a standardized communications protocol.
- **A1.1**: The protocol is open, free, and universally implementable.
- **A1.2**: The protocol allows authentication and authorization where necessary.
- **A2**: Metadata are accessible *even when the data are no longer available* (tombstone pages).

*Practical check*: if the dataset is removed in five years, will a future reader still be able to find a description of what once existed and why it was withdrawn?

### 4.3 Interoperable

- **I1**: (Meta)data use a formal, accessible, shared, and broadly applicable language for knowledge representation.
- **I2**: (Meta)data use vocabularies that follow FAIR principles (controlled vocabularies, ontologies).
- **I3**: (Meta)data include qualified references to other (meta)data.

*Practical check*: do the column names map to a standard schema (Darwin Core for biodiversity, GeoJSON / OGC for spatial, ISO 19115 for geospatial metadata)? Are CRSs (coordinate reference systems) explicitly stated?

### 4.4 Reusable

- **R1**: Meta(data) richly described with a plurality of accurate and relevant attributes.
- **R1.1**: (Meta)data released with a clear and accessible data usage license.
- **R1.2**: (Meta)data associated with detailed provenance.
- **R1.3**: (Meta)data meet domain-relevant community standards.

*Practical check*: can a third party download the dataset, understand what each field means without contacting the author, and legally re-use it?

Mons et al. (2017) make the often-missed point that FAIR is primarily about **machines** being able to find and use data; the human-facing pieces (README, datasheet) are necessary but not sufficient.

## 5. Reproducibility Infrastructure

Reproducibility is the spine of Phase 6 in a pipeline-only project. The literature distinguishes (Peng, 2011; Stodden et al., 2016; National Academies, 2019) between:

- **Methods reproducibility**: the same code on the same data produces the same result.
- **Results reproducibility**: an independent re-implementation produces equivalent results.
- **Inferential reproducibility**: an independent analysis of the same data supports the same conclusions.

CRISP-DM Phase 6 has direct purchase on the first; the second and third require Phase 6 *artifacts* to be sufficient for someone else to do that work.

### 5.1 Environment pinning

- **Lockfiles**: `poetry.lock`, `conda-lock`, `pip-tools` compiled `requirements.txt`. A lockfile records the exact transitive dependency graph; a `requirements.txt` with version ranges does not (Gentleman & Temple Lang, 2007 noted this in pre-lockfile form; the principle predates the tooling).
- **Containers**: Docker is the dominant choice for general reproducibility; Apptainer (formerly Singularity) is preferred in HPC contexts because it does not require a root daemon. Boettiger (2015) makes the canonical case for containers in scientific computing.
- **Binder / MyBinder**: turns a Git repository with a `requirements.txt` (or `environment.yml`) and a notebook into a one-click executable environment in the browser. Useful for *demonstration*, not for *preservation* — MyBinder builds are ephemeral.

### 5.2 Data versioning

Code-versioning tools (Git) handle text well but balk at large binary artifacts. Tools that address this:

- **DVC** (Data Version Control): stores hashes in Git, content in object storage; integrates with the pipeline definition (a DAG of stages).
- **lakeFS**: Git-like semantics over object storage; supports branching, merging, and rollback on data lakes.
- **Pachyderm**: data-centric pipeline orchestration with versioned commits.
- **Git LFS**: simple, widely supported; suitable for moderately-sized artifacts.

For pure release purposes, a content hash (SHA-256) recorded in the manifest is often sufficient. Versioning tools become important when the pipeline is *iterated* over time.

### 5.3 Executable reports

- **Jupyter Book** and **Quarto** turn a collection of notebooks and Markdown into a navigable, executable scientific report. Both support cross-references, citation rendering, equation typesetting, and execution caching.
- **Executable papers** (Lasser, 2020) refer to the broader practice of bundling narrative, code, data, and execution environment into a single distributable artifact. Software-Heritage-archived Git snapshots paired with Zenodo DOIs are a robust pattern.

### 5.4 Provenance

The W3C **PROV-O** ontology represents entities, activities, and agents in a DAG. Workflow systems like **Snakemake**, **Nextflow**, and **Common Workflow Language (CWL)** emit provenance records automatically. Even for a small pipeline, a hand-maintained `provenance.json` or a Snakefile that names every input → transformation → output edge raises the floor of reproducibility dramatically.

## 6. Documentation for Handoff

A pipeline release without documentation is a pile of files. The minimum documentation set:

### 6.1 Final report

Structure (adapted from academic conventions and IMRaD):

1. **Executive summary** for non-technical decision-makers (1 page, plain-language: what was done, what it shows, what the limits are, what the user should do next).
2. **Background and intended use**.
3. **Data sources**, with provenance and licensing.
4. **Methods**: enough detail that an independent analyst could re-do the work from scratch. Where the methods reference a notebook or script, that path is given.
5. **Results**: what the pipeline produced (the data product, the index, the network), with summary statistics and uncertainty.
6. **Limitations and known biases**.
7. **Code and data availability statement** (DOIs, repository URLs).
8. **Funding statement** and **conflicts of interest** (academic convention; even seminar projects should declare).
9. **References**.

### 6.2 Datasheets

Gebru et al. (2021) introduced *Datasheets for Datasets*: a structured questionnaire covering motivation, composition, collection process, preprocessing, uses, distribution, and maintenance. For each produced dataset (not just the inputs), a datasheet must exist. The point is not the format; it is that *every produced dataset has its own provenance document*.

### 6.3 Model cards (when applicable)

Mitchell et al. (2019) introduced *Model Cards* for ML models. In a pipeline-only project without a trained model, the *data product* (e.g., a composite index, a network graph) often functions like a model: it has intended uses, evaluation context, and known biases. A "product card" — a one-page document with sections for intended use, out-of-scope use, performance characteristics, ethical considerations, and limitations — is a useful analogue.

### 6.4 Intended-use statement

A short document stating: *who* the data product is for, *what decisions* it is designed to inform, *what decisions* it must not be used for, *what level of statistical confidence* it carries, and *what the failure modes* are. The intended-use statement is the first line of defense against well-meaning misuse.

### 6.5 Re-run and extend guides

- **How to re-run**: step-by-step instructions for reproducing the published outputs from the published inputs. Should fit on one page.
- **How to extend**: where to plug in new data sources, how to modify the scoring scheme, how to scale to a different city. Identifies the "soft" parts of the pipeline.

## 7. Plan Monitoring and Maintenance for Data Products

Monitoring in CRISP-ML(Q) (Studer et al., 2021) extends CRISP-DM with explicit quality assurance per phase and adds a dedicated monitoring phase. For a data product, the things that decay over time are different from a model:

- **Upstream source drift**: the data source changes its schema, its sampling protocol, or its access conditions (e.g., GBIF schema changes, Copernicus product version bumps, a city open-data portal restructures URLs).
- **Dependency rot**: Python packages release breaking changes; transitive dependencies become unavailable. Sculley et al. (2015) describe this as "unstable data dependencies" and identify it as a major source of hidden technical debt.
- **Link rot**: URLs cited as inputs or referenced in the report 404. Studies (e.g., Klein et al., 2014) consistently find ~20-50% link rot in scientific outputs after 5 years.
- **License changes**: an upstream source switches from CC-BY to a more restrictive license; the downstream product may become non-redistributable.
- **Scientific drift**: the science underlying a sub-score is revised by new literature; the intended-use statement may need updating.

A monitoring plan answers, for each of these:

- **What is monitored**: explicit list of input sources, dependencies, and links.
- **How often**: scheduled refresh cadence (quarterly, annually, on-demand).
- **By whom**: a *named maintainer* (or a "this is unmaintained — fork freely" statement).
- **Triggers for a re-run**: e.g., "if Urban Atlas releases a new edition, re-run pipeline P2 and re-publish v1.1."
- **Deprecation policy**: when the product will be marked superseded or withdrawn; how the tombstone metadata will be preserved.
- **Ownership transfer**: contingency if the original author leaves the institution.

Treating data products as having *life cycles* — published, current, superseded, withdrawn — is the maintenance analogue of model retraining.

## 8. Produce Final Report — Academic Conventions

For a seminar deliverable, the final report doubles as the assessable artifact. Beyond the structural elements in §6.1, academic conventions worth observing:

- **Code and data availability**: an explicit section, near the end, listing DOIs and URLs for code and data. Many journals now require this; the seminar should adopt the same norm.
- **Author contributions**: the CRediT taxonomy (Brand et al., 2015) defines 14 contributor roles (conceptualization, methodology, software, validation, formal analysis, investigation, resources, data curation, writing — original draft, writing — review & editing, visualization, supervision, project administration, funding acquisition). Group projects should list contributors against these roles.
- **Funding**: even where the only funding is "this is a course project," stating so is good practice.
- **Conflicts of interest**: declare partnerships, data-provider relationships, or stakeholder roles that could shape the analysis.
- **AI / tool disclosure**: increasingly expected; state which AI tools were used and for what (writing assistance, code generation, literature search).
- **Plain-language executive summary**: written for the *user*, not for the seminar grader.

## 9. Review Project — Retrospective Methodology

The final canonical task is the project retrospective. Useful structures:

- **What worked / what didn't / what next**: classic three-column retrospective.
- **Premortem in reverse**: "imagine the project had failed — why?" then enumerate which of those risks actually materialized and which were avoided.
- **Lessons-learned register**: a numbered list of lessons, each tagged with phase (Business Understanding, Data Understanding, etc.) and severity, suitable to carry forward to the next CRISP-DM cycle.
- **Contribution accounting**: who did what, written as CRediT roles, signed by all contributors.
- **Decision log**: every defensible design decision made during the project, with the alternatives considered and the reason for the choice. The decision log is one of the most valuable artifacts to hand to a successor.

A *contribution-tracked* retrospective is also the most honest form of credit assignment in group work.

## 10. Open-Science Angle

### 10.1 Licensing

Licensing choices are not arbitrary; they constrain who can use the work and how:

- **Code**: MIT and Apache-2.0 are maximally permissive; GPL is copyleft (derivative works must also be GPL). Apache-2.0 includes an explicit patent grant; MIT does not.
- **Data**: CC-BY-4.0 requires attribution; CC0 is public domain; ODbL (Open Database License) is copyleft for databases; CC-BY-SA enforces share-alike. For databases specifically, the Creative Commons FAQ recommends CC-BY-4.0 over the older "database" CC licenses.
- **Documentation**: CC-BY-4.0 is the default.

Mixed licensing (different licenses for code, data, and documentation) is normal and expected.

### 10.2 Preprint vs publication

For research outputs, posting a preprint (arXiv, bioRxiv, EarthArXiv, EngArXiv) is now standard practice and is compatible with subsequent peer-reviewed publication in most venues. Preprints are the academic equivalent of a "release candidate" for a paper.

### 10.3 Code repositories

GitHub / GitLab are not archival. The standard pattern: develop on GitHub, **archive a release on Zenodo via the GitHub-Zenodo integration**, which mints a DOI for each tagged release. The Software Heritage initiative provides a complementary "best-effort" archive of public source code.

### 10.4 Credit assignment

Use the **CRediT** taxonomy in the final report. For software specifically, the **Citation File Format (CFF)** standard (`CITATION.cff` in the repo root) lets GitHub and Zenodo auto-generate citation metadata. For datasets, the DataCite metadata schema supports rich contributor roles.

## 11. Anti-Patterns

The following are common, harmful, and largely preventable:

- **Pipeline-rot from un-pinned dependencies**: `pip install pandas` in a notebook from 2024 will not install the same pandas in 2027. Use a lockfile.
- **Irreproducible cells**: notebooks run out of order, hidden state, manual edits to outputs. Use "Restart and Run All" as the only acceptable execution mode before release; consider `nbqa`, `papermill`, or `treon` for CI.
- **"Works on my machine"**: no container, no lockfile, no explicit Python version. Cannot be reproduced.
- **Missing data versioning**: "I downloaded this from GBIF" with no date, no query, no DOI. Whatever was downloaded is unrecoverable.
- **No maintainer named**: the README does not say who to contact; the issue tracker is closed; the email bounces. The project is *born dead*.
- **Dead links to inputs**: data dictionary points to a 404. Always cite the *DOI of a snapshot*, not the URL of the live source.
- **No intended-use statement**: users repurpose the data product for decisions it was never validated for. (This is the *Cambridge Analytica* pattern in miniature: data collected for one purpose used for another.)
- **Conflating data publication with software publication**: releasing the notebook does not release the data; releasing the data does not release the code. They are separate artifacts with separate licenses and separate DOIs.
- **README without a license**: legally, "all rights reserved" is the default, which means the work is *not* open even if the author intended it to be.

## 12. Worked Example: Handoff Package for an Urban-Ecology Pipeline

To anchor the abstractions, consider a city-scale spatial composite + mycorrhizal network pipeline handed off to an urban-planning office (the Barcelona Eixos Verds use case). The release bundle contains:

- **Code (Zenodo DOI, MIT license)**:
  - `notebooks/` (numbered 01 — ingest, 02 — clean, 03 — construct features, 04 — integrate, 05 — compose, 06 — network, 07 — rank).
  - `src/` reusable modules.
  - `Snakefile` defining the DAG.
  - `pyproject.toml` + `poetry.lock`.
  - `Dockerfile` pinning Python 3.11 and GDAL 3.x.

- **Data (Zenodo DOI, CC-BY-4.0)**:
  - `outputs/barrier_composite_v1.0.0.gpkg` (the 400 m-grid composite).
  - `outputs/mycorrhizal_network_v1.0.0.graphml` (the tree-to-tree graph).
  - `outputs/top15_priority_zones_v1.0.0.csv`.
  - `outputs/datasheet_composite.md` and `outputs/datasheet_network.md` (Gebru et al. format).
  - `manifest.json` listing every input with DOI, retrieval date, SHA-256.

- **Documentation (CC-BY-4.0)**:
  - `final_report.pdf` (rendered from Quarto, IMRaD).
  - `methods.md` (linking to specific notebook cells).
  - `intended_use.md` (who, what decisions, what NOT to use it for).
  - `limitations.md` (host-mismatch sub-score null over ~95% of city; LST confounded with irrigation; etc.).
  - `how_to_rerun.md` (one-page; `docker build && snakemake all`).
  - `how_to_extend.md` (how to swap city, how to add a sub-score).
  - `decision_log.md` (every defensible design choice and its rationale).
  - `CITATION.cff`.
  - `CONTRIBUTORS.md` with CRediT roles.

- **Publication channels**:
  - Zenodo DOI for code release (citable as software).
  - Zenodo DOI for data release (citable as dataset).
  - Listing on Open Data BCN (consumer-facing).
  - Mention of the network graph on GBIF/OBIS only if it qualifies as a derived occurrence dataset (it does not in this case).

- **Monitoring plan**:
  - Annual re-run when Urban Atlas releases a new edition.
  - Quarterly link-check on input DOIs (automated via CI).
  - Named maintainer (with handoff plan if they leave the institution).
  - Deprecation policy: superseded versions remain available with a tombstone notice; major schema breaks bump MAJOR version.

This bundle would let the Eixos Verds analyst (a) cite the work in a budget memo, (b) re-run the pipeline next year on updated inputs, (c) understand exactly what the index does and does not measure, and (d) extend the methodology to neighboring municipalities — without the original author present.

## 13. End-of-Cycle: What Triggers a New CRISP-DM Iteration

CRISP-DM is explicitly iterative (Chapman et al., 2000, p. 13). Triggers for a new cycle from Phase 6:

1. **A new business question** raised by the user upon receiving the product ("Can we do this for nighttime cooling too?").
2. **Upstream-source change** invalidating an input (Urban Atlas 2024 supersedes 2021).
3. **A scientific update** to the underlying method (a new paper revises hyphal growth rates).
4. **A user-reported failure mode** (the index ranks an obvious false positive at the top, suggesting a missing variable).
5. **A scheduled refresh** (annual update for budget-cycle alignment).
6. **A discovered bias** that requires methodological change (the host-mismatch sub-score case in the worked example).

Each of these returns the project to Phase 1 (*Business Understanding*) with a revised problem statement, then proceeds through the cycle with the previous deliverables as inputs. Phase 6 is the closing *and* opening hinge of the loop.

---

## References

Boettiger, C. (2015). An introduction to Docker for reproducible research. *ACM SIGOPS Operating Systems Review*, 49(1), 71–79. https://doi.org/10.1145/2723872.2723882

Brand, A., Allen, L., Altman, M., Hlava, M., & Scott, J. (2015). Beyond authorship: Attribution, contribution, collaboration, and credit. *Learned Publishing*, 28(2), 151–155. https://doi.org/10.1087/20150211

Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C., & Wirth, R. (2000). *CRISP-DM 1.0: Step-by-step data mining guide*. SPSS Inc. / The CRISP-DM Consortium.

European Commission. (2007). Directive 2007/2/EC of the European Parliament and of the Council of 14 March 2007 establishing an Infrastructure for Spatial Information in the European Community (INSPIRE). *Official Journal of the European Union*, L 108, 1–14.

Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., & Crawford, K. (2021). Datasheets for datasets. *Communications of the ACM*, 64(12), 86–92. https://doi.org/10.1145/3458723

Gentleman, R., & Temple Lang, D. (2007). Statistical analyses and reproducible research. *Journal of Computational and Graphical Statistics*, 16(1), 1–23. https://doi.org/10.1198/106186007X178663

Klein, M., Van de Sompel, H., Sanderson, R., Shankar, H., Balakireva, L., Zhou, K., & Tobin, R. (2014). Scholarly context not found: One in five articles suffers from reference rot. *PLOS ONE*, 9(12), e115253. https://doi.org/10.1371/journal.pone.0115253

Klímek, J., Škoda, P., & Nečaský, M. (2019). Survey of tools for linked data consumption. *Semantic Web*, 10(4), 665–720. https://doi.org/10.3233/SW-180316

Lasser, J. (2020). Creating an executable paper is a journey through Open Science. *Communications Physics*, 3, 143. https://doi.org/10.1038/s42005-020-00403-4

Martínez-Plumed, F., Contreras-Ochando, L., Ferri, C., Hernández-Orallo, J., Kull, M., Lachiche, N., Ramírez-Quintana, M. J., & Flach, P. (2021). CRISP-DM twenty years later: From data mining processes to data science trajectories. *IEEE Transactions on Knowledge and Data Engineering*, 33(8), 3048–3061. https://doi.org/10.1109/TKDE.2019.2962680

Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., & Gebru, T. (2019). Model cards for model reporting. In *Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT* '19)* (pp. 220–229). ACM. https://doi.org/10.1145/3287560.3287596

Mons, B., Neylon, C., Velterop, J., Dumontier, M., da Silva Santos, L. O. B., & Wilkinson, M. D. (2017). Cloudy, increasingly FAIR: Revisiting the FAIR Data guiding principles for the European Open Science Cloud. *Information Services & Use*, 37(1), 49–56. https://doi.org/10.3233/ISU-170824

National Academies of Sciences, Engineering, and Medicine. (2019). *Reproducibility and replicability in science*. The National Academies Press. https://doi.org/10.17226/25303

Paleyes, A., Urma, R.-G., & Lawrence, N. D. (2022). Challenges in deploying machine learning: A survey of case studies. *ACM Computing Surveys*, 55(6), Article 114. https://doi.org/10.1145/3533378

Peng, R. D. (2011). Reproducible research in computational science. *Science*, 334(6060), 1226–1227. https://doi.org/10.1126/science.1213847

Sculley, D., Holt, G., Golovin, D., Davydov, E., Phillips, T., Ebner, D., Chaudhary, V., Young, M., Crespo, J.-F., & Dennison, D. (2015). Hidden technical debt in machine learning systems. In *Advances in Neural Information Processing Systems 28 (NIPS 2015)* (pp. 2503–2511).

Sicilia, M.-A., García-Barriocanal, E., & Sánchez-Alonso, S. (2017). Community curation in open dataset repositories: Insights from Zenodo. *Procedia Computer Science*, 106, 54–60. https://doi.org/10.1016/j.procs.2017.03.009

Stodden, V., McNutt, M., Bailey, D. H., Deelman, E., Gil, Y., Hanson, B., Heroux, M. A., Ioannidis, J. P. A., & Taufer, M. (2016). Enhancing reproducibility for computational methods. *Science*, 354(6317), 1240–1241. https://doi.org/10.1126/science.aah6168

Studer, S., Bui, T. B., Drescher, C., Hanuschkin, A., Winkler, L., Peters, S., & Müller, K.-R. (2021). Towards CRISP-ML(Q): A machine learning process model with quality assurance methodology. *Machine Learning and Knowledge Extraction*, 3(2), 392–413. https://doi.org/10.3390/make3020020

Wilkinson, M. D., Dumontier, M., Aalbersberg, I. J., Appleton, G., Axton, M., Baak, A., Blomberg, N., Boiten, J.-W., da Silva Santos, L. B., Bourne, P. E., Bouwman, J., Brookes, A. J., Clark, T., Crosas, M., Dillo, I., Dumon, O., Edmunds, S., Evelo, C. T., Finkers, R., … Mons, B. (2016). The FAIR Guiding Principles for scientific data management and stewardship. *Scientific Data*, 3, 160018. https://doi.org/10.1038/sdata.2016.18

### Standards referenced

- ISO 19115-1:2014 — Geographic information — Metadata — Part 1: Fundamentals.
- OGC API — Features, Web Map Service (WMS), Web Feature Service (WFS).
- W3C PROV-O — The PROV Ontology.
- Darwin Core (TDWG) — biodiversity data exchange standard.
- GBIF — Global Biodiversity Information Facility data publication guidelines.
- DataCite Metadata Schema 4.4.
- Citation File Format (CFF) v1.2.
