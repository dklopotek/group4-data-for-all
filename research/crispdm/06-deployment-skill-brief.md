# Skill Brief: CRISP-DM Phase 6 — Deployment (Pipeline Handoff)

## name
`crispdm-phase-6-deployment`

## description
Walks a graduate student through CRISP-DM Phase 6 reframed for a **data-pipeline-only** project. The skill produces a **release bundle** (pinned code + data + documentation + provenance), a **FAIR-compliance checklist**, a **final report skeleton**, and a **monitoring and maintenance plan**. **This skill does NOT build a frontend, dashboard, API, or hosted service.** The deliverable is a citable, reproducible, well-documented data product handed off to a named user.

## triggers
Use this skill when:

- The student has completed CRISP-DM Phase 5 (Evaluation) and has a **go decision** memo on file.
- The pipeline produces a *data product* (dataset, composite index, network graph, derived layer) — not a trained model destined for serving.
- The student says "we're ready to publish," "we need to hand this off," "how do we release this," "we need a final report," or "what do we do at the end of CRISP-DM."
- The student asks about FAIR, datasheets, Zenodo, DOIs, lockfiles, reproducibility, or licensing for the project.
- The course explicitly says "no frontend" and the work needs to *land* somewhere.

Do **NOT** use this skill when:

- The user wants to build a dashboard, map UI, web app, or hosted API. Stop and remind them of the course constraint.
- Phase 5 is incomplete or returned a *no-go*. Phase 6 cannot begin without a documented go decision.
- The user is operationalizing a trained ML model — that's a different (industrial) reading of Phase 6 and requires different tooling (MLOps).

## inputs (required before running)

The skill blocks until these are present in the repo:

1. **Phase 5 go/no-go memo** — explicit decision document. If `no-go`, stop; route back to Phase 1.
2. **Pipeline notebooks/scripts** — version-controlled, ordered, runnable end-to-end.
3. **Data product** — the actual output artifact(s) (CSV/GeoPackage/GraphML/Parquet) sitting in `outputs/`.
4. **Phase 4 modeling/feature notes** — the design decisions need to be carried into the final report.
5. **Intended user named** — a real role at a real organization, even if hypothetical (e.g., "capital planning analyst at Ajuntament Espais Verds").
6. **Decision log** (any format) — every defensible design choice made earlier in the project.

If any of these are missing, the skill names what's missing and stops. Do not fake-run Phase 6 on a half-built pipeline.

## sequential steps

### Step 1. Confirm Phase 5 go decision and load inputs

- Read the Phase 5 memo. Confirm `decision: go`.
- Inventory the artifacts listed under *inputs*. List anything missing in a numbered checklist; if any required input is missing, stop and report.
- Identify the named intended user and write their name + role + decision context to `release/intended_user.md`.

### Step 2. Pin the environment

Create or verify:

- `pyproject.toml` (preferred) **or** `environment.yml`.
- A **lockfile**: `poetry.lock`, `conda-lock` output, or a `pip-tools` compiled `requirements.txt` with hashes. A `requirements.txt` with version ranges is **not** sufficient.
- A `Dockerfile` (or `apptainer.def`) that builds a working environment from the lockfile. Pin the base image to a specific tag (no `:latest`).
- A `.python-version` or equivalent that pins the interpreter.
- Verify the build runs (`docker build .` succeeds) and that a smoke notebook executes inside it.

### Step 3. Stamp versions on inputs and outputs

For every input dataset, record in `release/manifest.json`:

```json
{
  "name": "Ajuntament BCN tree inventory",
  "version_or_date": "snapshot 2026-04-15",
  "url_or_doi": "https://opendata-ajuntament.barcelona.cat/...",
  "license": "CC-BY-4.0",
  "sha256": "…",
  "bytes": …
}
```

For every output artifact, assign a **semantic version** (`MAJOR.MINOR.PATCH`) and embed it in the filename:

- `outputs/barrier_composite_v1.0.0.gpkg`
- `outputs/mycorrhizal_network_v1.0.0.graphml`
- `outputs/top15_priority_zones_v1.0.0.csv`

Record SHA-256 of each output in `release/manifest.json`.

### Step 4. Write a datasheet for each produced dataset

For every output, create `outputs/datasheet_<name>.md` following Gebru et al. (2021). Sections required:

- Motivation
- Composition (what's in it, what the rows/edges represent, what the fields mean)
- Collection process (which inputs, which transformations, which notebook cells)
- Preprocessing/cleaning/labeling
- Uses (intended uses, **out-of-scope uses**)
- Distribution (license, DOI, channel)
- Maintenance (named maintainer, update cadence, contact)

A README that says "here is the file" is **not** a datasheet.

### Step 5. Build the FAIR-compliance checklist

Walk through Wilkinson et al. (2016). For each item, record `pass | fail | n/a` in `release/fair_checklist.md`:

**Findable**
- [ ] F1 — DOI minted (Zenodo or domain repository)
- [ ] F2 — Metadata rich enough that a stranger can understand the dataset without contacting the author
- [ ] F3 — Metadata explicitly includes the DOI of the data
- [ ] F4 — Dataset indexed in a searchable resource (DataCite, GBIF, institutional catalog)

**Accessible**
- [ ] A1 — Retrievable by DOI using HTTPS
- [ ] A1.1 — Protocol is open/free
- [ ] A1.2 — Authentication/authorization documented if access is restricted
- [ ] A2 — Tombstone page guaranteed by host (Zenodo, Dryad, Figshare all support this)

**Interoperable**
- [ ] I1 — Uses a standard format (GeoPackage, Parquet, GraphML, CSV with documented schema)
- [ ] I2 — Field names map to a controlled vocabulary where one exists (Darwin Core, ISO 19115, OGC, INSPIRE)
- [ ] I3 — Qualified references to other datasets (DOIs in `manifest.json`, not bare URLs)

**Reusable**
- [ ] R1 — Every field documented in the datasheet
- [ ] R1.1 — Explicit license (CC-BY-4.0 / ODbL / CC0 — pick deliberately, not by default)
- [ ] R1.2 — Provenance recorded (`provenance.json` or Snakefile DAG)
- [ ] R1.3 — Domain-community standard observed (Darwin Core for biodiversity, OGC/ISO 19115 for geospatial, etc.)

Any `fail` blocks release. Any `n/a` requires a written justification.

### Step 6. Choose publication channels

For each released artifact, decide and record:

- **Citable archive** (always): Zenodo DOI via GitHub release integration (for code) and direct upload (for data).
- **Domain repository** (where applicable): GBIF for occurrence data, PANGAEA for earth science, ICPSR for social science.
- **Consumer-facing portal** (where applicable): city/regional open-data portal if the intended user is a public-sector consumer.
- **Institutional repository** (fallback): university dataverse for long-term preservation.

Record the choices and rationale in `release/publication_plan.md`.

### Step 7. Pick licenses deliberately

In `release/licenses.md`, record and justify:

- **Code license**: MIT / Apache-2.0 / GPL-3.0. Apache-2.0 if patent grant is wanted.
- **Data license**: CC-BY-4.0 (most common) / ODbL (databases, copyleft) / CC0 (public domain).
- **Documentation license**: CC-BY-4.0 default.

Add `LICENSE` (code), `LICENSE-DATA` (data), and `LICENSE-DOCS` (docs) to the repo root. A README without a license file is legally "all rights reserved."

### Step 8. Write the final report

Generate `release/final_report.md` (render to PDF via Quarto or Pandoc). Required sections:

1. Executive summary for non-technical decision-makers (≤ 1 page, plain language).
2. Background and intended use.
3. Data sources (with DOIs).
4. Methods (linked to specific notebook cells/scripts).
5. Results (the data product, with summary statistics and uncertainty).
6. Limitations and known biases (carried from the limitations register).
7. Code and data availability statement (DOIs explicit).
8. Funding statement.
9. Conflicts of interest.
10. AI / tool disclosure.
11. Author contributions in **CRediT** roles.
12. References.

### Step 9. Write the supporting documents

- `release/intended_use.md` — who, what decisions it informs, what it must NOT be used for, failure modes.
- `release/limitations.md` — known biases, edge cases, scope boundaries.
- `release/how_to_rerun.md` — one page; `docker build . && docker run … snakemake all`.
- `release/how_to_extend.md` — soft parts of the pipeline; how to swap inputs or modify scoring.
- `release/decision_log.md` — every defensible design choice and its rationale.
- `CITATION.cff` in the repo root.
- `CONTRIBUTORS.md` with CRediT roles signed by all contributors.

### Step 10. Write the monitoring and maintenance plan

In `release/monitoring_plan.md`, name:

- **Inputs monitored** (explicit list with check cadence).
- **Dependencies monitored** (lockfile rebuild test, link check).
- **Triggers for a new release** (upstream-source bumps, scientific revisions, user-reported failures).
- **Named maintainer** (or explicit "unmaintained — fork freely" statement).
- **Ownership transfer plan** (what happens if the maintainer leaves).
- **Deprecation policy** (when products are marked superseded; tombstone metadata preserved).
- **Re-run cadence** (annual / quarterly / on-demand).

### Step 11. Tag, archive, mint DOIs

- Tag the Git release: `v1.0.0`.
- Trigger Zenodo via GitHub integration → mint DOI for code.
- Upload data bundle to Zenodo → mint DOI for data.
- Update `final_report.md` with the minted DOIs.
- Update `CITATION.cff` with the code DOI.

### Step 12. Project retrospective

Add `release/retrospective.md` covering:

- What worked / what didn't / what next (three-column).
- Lessons-learned register (numbered, phase-tagged, severity-tagged).
- Reverse premortem: which risks materialized, which were avoided.
- Contribution accounting (CRediT roles signed by all contributors).
- End-of-cycle triggers identified: what would start a new CRISP-DM iteration?

## deliverables

A complete Phase 6 produces:

1. **Release bundle manifest** (`release/manifest.json`) — every input + every output with version, DOI, license, hash.
2. **FAIR compliance checklist** (`release/fair_checklist.md`) — all items passed or justified.
3. **Final report** (`release/final_report.md` + rendered PDF) — academic conventions, plain-language executive summary.
4. **Datasheets** for every produced dataset (`outputs/datasheet_*.md`).
5. **Monitoring and maintenance plan** (`release/monitoring_plan.md`) — named maintainer, refresh cadence, deprecation policy.
6. **Re-run + extend guides** (`release/how_to_rerun.md`, `release/how_to_extend.md`).
7. **Decision log** (`release/decision_log.md`).
8. **Intended-use statement** (`release/intended_use.md`).
9. **Licenses** (`LICENSE`, `LICENSE-DATA`, `LICENSE-DOCS`).
10. **Citation files** (`CITATION.cff`, `CONTRIBUTORS.md`).
11. **Retrospective** (`release/retrospective.md`).
12. **DOIs**: one for code, one for data, recorded in the final report.

## quality checks

### FAIR check
Every item in `release/fair_checklist.md` must be `pass` or `n/a` with justification. Run before declaring Phase 6 complete.

### Reproducibility check (the "stranger test")
Hand the release bundle to someone who has never seen the project. Ask them to follow `how_to_rerun.md`. If they cannot reproduce the published outputs without contacting the author, Phase 6 fails. Common failure points:

- Container won't build (un-pinned base image, missing system library).
- Notebooks have hidden state (cells run out of order).
- An input URL has rotted.
- A field in a datasheet is too vague to disambiguate values in the file.

### Citability check
Search the project's title and the dataset's title. Both must surface a landing page with a DOI within the first page of results from a major search engine within a week of release.

### Maintainability check
The repo has a named maintainer with a working contact. The `monitoring_plan.md` names a successor or explicitly says "unmaintained."

### Stranger-can-extend check
A second stranger reads `how_to_extend.md` and identifies, without help, the three soft parts of the pipeline (which input to swap, which scoring weight to change, which sub-pipeline to add to).

## anti-patterns (block release if observed)

- **`requirements.txt` with version ranges and no lockfile.** Use a lockfile.
- **Notebooks that depend on cells executed earlier in a different order.** Use "Restart and Run All."
- **Data in `outputs/` without a datasheet.** Every output gets a datasheet.
- **README without a license.** "All rights reserved" is not open.
- **Same license for code and data.** Code and data have different needs; choose deliberately.
- **Input cited by URL only, no DOI, no snapshot date.** Inputs vanish; record the snapshot.
- **"Maintainer: TBD."** Name a maintainer or declare the project unmaintained — both are acceptable; ambiguity is not.
- **A final report with no Code and Data Availability statement.** Add it.
- **An intended-use statement that says "for research."** Too vague. Name the decision the product is meant to inform.
- **Building a frontend "because the user needs a dashboard."** They don't. The course constraint is explicit: **no frontend**. The deliverable is the data product, the documentation, and the reproducibility infrastructure. If a user genuinely needs a UI, that is a *separate* downstream project with its own CRISP-DM cycle. **Do not slip a UI into Phase 6 of a pipeline-only project.**
- **Conflating data publication with software publication.** Code and data are separate artifacts with separate licenses and separate DOIs. Publish both.

## explicit guidance: this is NOT building a frontend

This skill enforces the course constraint that the deliverable is a **data product handoff**, not a user interface. Specifically:

- **No dashboards.** No Streamlit, no Dash, no Power BI, no Tableau, no Looker.
- **No web apps.** No Flask, no FastAPI, no Next.js, no static site beyond the rendered report.
- **No interactive maps "for the user."** Internal exploration notebooks are fine; a published Folium/Leaflet HTML is not the deliverable.
- **No "lite" production model.** No model serving, no scoring endpoint, no scheduled jobs in someone else's infrastructure.

What you **do** ship:

- The dataset (citable, FAIR, datasheeted).
- The pipeline (pinned, reproducible, containerized).
- The report (final report + methods + intended use + limitations).
- The plan (monitoring, maintenance, ownership, deprecation).

If the intended user later needs an interface, that is the start of a *new* project (Phase 1: Business Understanding, with the data product from this project as an input). The teacher's directive is: stay in your lane — be the architect of the data system, not the front-end engineer.

## release bundle checklist template

The skill enforces this checklist before declaring Phase 6 complete. Copy into `release/release_bundle_checklist.md` and tick each item.

```
RELEASE BUNDLE CHECKLIST — vMAJOR.MINOR.PATCH — YYYY-MM-DD

ENVIRONMENT
[ ] pyproject.toml or environment.yml present
[ ] Lockfile present (poetry.lock / conda-lock / pip-tools)
[ ] Dockerfile pins base image (no :latest) and builds clean
[ ] .python-version pins interpreter
[ ] Smoke notebook runs in the container

CODE
[ ] All notebooks executed top-to-bottom in clean kernel; outputs committed
[ ] All scripts have docstrings and a __main__ guard where applicable
[ ] Pipeline DAG defined (Snakefile / Nextflow / CWL / hand-documented)
[ ] CITATION.cff at repo root
[ ] LICENSE (code) at repo root
[ ] CONTRIBUTORS.md with CRediT roles
[ ] README points to release/final_report.md and the DOIs

DATA
[ ] manifest.json lists every input with DOI, snapshot date, SHA-256, license
[ ] manifest.json lists every output with version, SHA-256, license
[ ] LICENSE-DATA at repo root (or per-dataset license headers)
[ ] Every output has a datasheet in outputs/datasheet_*.md
[ ] Coordinate reference systems explicitly stated for any spatial output
[ ] Field-level data dictionary for every output

DOCUMENTATION
[ ] release/final_report.md (with rendered PDF)
[ ] release/intended_use.md (who, what decisions, what NOT to use)
[ ] release/limitations.md
[ ] release/how_to_rerun.md (one page)
[ ] release/how_to_extend.md
[ ] release/decision_log.md
[ ] release/retrospective.md
[ ] LICENSE-DOCS at repo root

FAIR
[ ] release/fair_checklist.md complete; every item pass or justified n/a

PUBLICATION
[ ] release/publication_plan.md identifies all channels
[ ] Zenodo DOI minted for code (via GitHub release)
[ ] Zenodo DOI minted for data
[ ] DOIs recorded in final_report.md and CITATION.cff
[ ] Domain repository listing (if applicable)
[ ] Open-data portal listing (if applicable)

MAINTENANCE
[ ] release/monitoring_plan.md names maintainer
[ ] release/monitoring_plan.md sets re-run cadence
[ ] release/monitoring_plan.md sets deprecation policy
[ ] release/monitoring_plan.md sets ownership transfer plan

QUALITY GATES
[ ] FAIR check passed
[ ] Reproducibility ("stranger test") passed
[ ] Citability check passed
[ ] Maintainability check passed
[ ] Stranger-can-extend check passed

NEGATIVE CHECKS (must all be false)
[ ] No frontend / dashboard / web app shipped
[ ] No live model-serving endpoint
[ ] No bare URLs as data citations (DOIs only)
[ ] No "TBD" in maintainer field
[ ] No notebook with out-of-order cells

SIGN-OFF
Maintainer: ____________________
Date: ____________________
Release tag: ____________________
```

## references

- Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C., & Wirth, R. (2000). *CRISP-DM 1.0: Step-by-step data mining guide*. SPSS Inc. / The CRISP-DM Consortium.
- Wilkinson, M. D., et al. (2016). The FAIR Guiding Principles for scientific data management and stewardship. *Scientific Data*, 3, 160018.
- Gebru, T., et al. (2021). Datasheets for datasets. *Communications of the ACM*, 64(12), 86–92.
- Mitchell, M., et al. (2019). Model cards for model reporting. *FAT* '19*, 220–229.
- Sculley, D., et al. (2015). Hidden technical debt in machine learning systems. *NeurIPS 2015*.
- Paleyes, A., Urma, R.-G., & Lawrence, N. D. (2022). Challenges in deploying machine learning: A survey of case studies. *ACM Computing Surveys*, 55(6).
- Studer, S., et al. (2021). Towards CRISP-ML(Q). *Machine Learning and Knowledge Extraction*, 3(2), 392–413.
- Peng, R. D. (2011). Reproducible research in computational science. *Science*, 334(6060), 1226–1227.
- Stodden, V., et al. (2016). Enhancing reproducibility for computational methods. *Science*, 354(6317), 1240–1241.
- Gentleman, R., & Temple Lang, D. (2007). Statistical analyses and reproducible research. *J. Comp. Graph. Stat.*, 16(1), 1–23.
- Boettiger, C. (2015). An introduction to Docker for reproducible research. *ACM SIGOPS OSR*, 49(1), 71–79.
- Brand, A., et al. (2015). Beyond authorship: Attribution, contribution, collaboration, and credit (CRediT). *Learned Publishing*, 28(2), 151–155.
- Klein, M., et al. (2014). Scholarly context not found: One in five articles suffers from reference rot. *PLOS ONE*, 9(12).
- Mons, B., et al. (2017). Cloudy, increasingly FAIR. *Information Services & Use*, 37(1), 49–56.
- ISO 19115-1:2014 — Geographic information — Metadata.
- W3C PROV-O.
- Darwin Core (TDWG); GBIF data publication guidelines.
- DataCite Metadata Schema 4.4; Citation File Format (CFF) v1.2.
- INSPIRE Directive 2007/2/EC.
