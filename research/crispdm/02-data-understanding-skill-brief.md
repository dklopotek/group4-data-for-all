# Skill Brief — `phase-2-companion`

A thin companion skill that runs *after* `earn-the-data` to close the eight gaps between earn-the-data's ten-step discipline and the canonical CRISP-DM Phase 2 (Data Understanding) plus the post-2018 dataset-documentation literature.

---

## Decision: companion, not wrapper, not replacement

The gap analysis in `02-data-understanding-academic.md` identified eight specific gaps where earn-the-data is silent or thinner than the academic literature recommends (G1–G8 — ingestion log, ingested-data description, full Wang & Strong / ISO 25012 dimension cross-check, executable schema, MAUP/edge declarations, label-noise estimate, Croissant sidecar, versioning policy). None of these gaps invalidates earn-the-data: in fact, on three counts (decision unit, 2× resolution rule, brief-revisit) earn-the-data *exceeds* the canonical reference model.

The right architecture is therefore a **thin companion skill** that:
- assumes earn-the-data has already run and produced its four canonical artifacts (`data-inventory.md`, `data-sheets/<source>.md`, `profiling-plan.md`, `brief-revisit.md`),
- adds the eight gap-closing artifacts in the same `phase-2/` directory,
- explicitly does **not** re-do the rubric scoring, decision-unit identification, primary-source verification, or brief-revisit (those are earn-the-data's job and re-doing them would dilute the discipline).

A wrapper that *swallowed* earn-the-data would couple the two skills too tightly. A replacement would discard earn-the-data's domain specialization. A companion preserves the single-responsibility shape of both skills and lets the architect invoke them as a two-step pipeline.

---

## Skill front-matter (proposed)

```yaml
---
name: phase-2-companion
description: Use immediately after earn-the-data to harden Phase 2 (Data Understanding) outputs against the canonical CRISP-DM reference model (Chapman et al. 2000) and the post-2018 dataset-documentation literature (Gebru, Bender & Friedman, Holland, Pushkarna, Hutchinson, Sambasivan, Polyzotis, Wang & Strong, ISO/IEC 25012, FAIR, Croissant). Adds eight gap-closing artifacts that earn-the-data does not produce: ingestion log, ingested-data description, Wang & Strong / ISO 25012 cross-check, executable schemas, MAUP and edge-effect declarations, label-noise estimates, Croissant JSON-LD sidecars, and a versioning policy. Triggers on phrases like "harden Phase 2", "finalize data understanding", "prep for Phase 3", "before data preparation", "ready the data inventory", or whenever a `phase-2/` directory already exists with earn-the-data outputs but lacks the reproducibility artifacts a downstream architect (or reviewer) would need. Do not invoke before earn-the-data — this skill expects its outputs as inputs.
---
```

---

## Triggers

Invoke when **any** of the following hold:
- the user says "harden Phase 2", "finalize data understanding", "prep for Phase 3", "make Phase 2 reproducible", or equivalent;
- a `phase-2/` directory exists in the project but is missing one or more of: `ingestion-log.md`, `schemas/*.yaml`, `croissant/*.jsonld`, `versioning-policy.md`;
- the project is about to start Phase 3 (Data Preparation) and there is no audit trail back to the raw retrievals;
- a reviewer or teacher has asked "where did this data come from, exactly, and how do I re-run this?".

Do **not** invoke:
- before earn-the-data has run (this skill expects its outputs as inputs and will fail loudly if they are missing);
- as a substitute for the rubric or brief-revisit (those are earn-the-data's domain).

---

## Inputs (preconditions)

These must exist in the project's `phase-2/` directory before the skill runs:
1. `decision-unit.md` (or equivalent stated decision unit in `data-inventory.md`'s preamble).
2. `data-inventory.md` with rubric scores for each candidate.
3. `data-sheets/<source>.md` — one 8-section data sheet per recommended source.
4. `profiling-plan.md` with the 8-cell EDA checklist.
5. `brief-revisit.md` with the Step-10 conclusion.

If any are missing, halt and instruct the user to run earn-the-data first.

Additionally, the skill needs read-access to:
- the raw retrieved files (so file hashes, sizes, row/column counts are observed, not asserted),
- the ingestion script(s) or notebook(s) used (so the agent name and version go into the log).

---

## Sequential steps

The skill runs as a single pass over the recommended datasets identified by earn-the-data. Do not parallelize across datasets unless re-runs of profile code are independently safe.

### Step A — Verify earn-the-data outputs exist
List required inputs, fail loudly with a remediation instruction if any are missing. This is the only halt condition.

### Step B — Build the Ingestion Log (`ingestion-log.md`)
For each retrieval performed during Phase 2:
- retrieval timestamp in ISO 8601 UTC,
- exact URL or API call (with parameters),
- agent (script filename, version or git SHA, runtime version),
- destination path on disk,
- file hash (SHA-256 of bytes-as-downloaded, before any decoding),
- file size in bytes,
- observed encoding / content-type,
- HTTP status or API status code,
- any errors encountered and the fallback adopted.

If retrievals were ad-hoc (e.g., manual clicks on a portal), reconstruct what can be reconstructed and flag the rest as `unreproducible: yes` with a remediation note.

Closes gap G1 (Chapman et al., 2000 — Initial Data Collection Report).

### Step C — Build the Ingested-Data Description (`ingested-data-description.md`)
For each recommended source, *observed* (not asserted) values:
- row count (or feature count for spatial data),
- column list with inferred dtype,
- observed min/max for numeric columns,
- observed cardinality and top-10 values for categorical columns,
- file format and on-disk size,
- detected encoding,
- the date of observation.

Distinguish this from the data sheet: the data sheet describes *what the data are in general*; this report describes *what was actually ingested for this project*. Closes gap G2.

### Step D — Wang & Strong / ISO 25012 cross-check (`quality-cross-check.md`)
One row per recommended source × dimension. For each of the 15 Wang & Strong dimensions (or the 15 ISO/IEC 25012 characteristics — choose one and use it consistently), record:
- *assessed* (with one-sentence summary of the assessment),
- *deferred* (with reason — typically scope, time, or unavailable evidence),
- *not applicable* (with reason).

The 5-dimension earn-the-data rubric (Provenance, Resolution, Coverage, Licensing, Bias) maps onto a subset of these; the cross-check makes explicit which Wang & Strong dimensions are *not* covered by the rubric so the architect can defend that scope. Closes gap G3.

### Step E — Generate executable schemas (`schemas/<source>.yaml`)
For each recommended source, emit a schema file in one of:
- TensorFlow Data Validation `Schema` protobuf,
- Great Expectations `ExpectationSuite`,
- Pandera `DataFrameSchema`,
- frictionless `Table Schema`.

Pick the one already in use in the project; default to Pandera for tabular Python projects and frictionless for general-purpose pipelines. The schema must encode:
- field name and dtype,
- nullability and missingness budget,
- allowed-value set for low-cardinality categoricals,
- min/max for numerics (drawn from the data sheet, not from the ingested data — schemas are *expectations*, not observations),
- key/index constraints,
- CRS expectation for spatial layers.

Closes gap G4 (Breck et al., 2019; Polyzotis et al., 2018).

### Step F — Geospatial declarations (`geospatial-declarations.md`)
For any spatial dataset, declare:
- native CRS at source (EPSG code),
- chosen analysis CRS (EPSG code) and reprojection method,
- areal unit chosen for aggregation,
- justification for the chosen areal unit and a brief MAUP sensitivity note (was an alternative unit tested? if not, why not?),
- edge-buffer policy (how observations near the study-area boundary are handled).

Closes gap G5 (Openshaw & Taylor, 1979 — MAUP).

### Step G — Bias and annotation-quality estimate (`bias-and-annotation.md`)
Two parts.

*Part 1.* Lift the bias findings already named in earn-the-data Step 8 into this artifact verbatim (so the artifact is self-contained and reviewable without flipping between files).

*Part 2.* For each crowd-annotated or citizen-science source (iNaturalist, GBIF, OpenStreetMap, Purple Air, etc.), estimate label/annotation error rate:
- cite any published audit if one exists,
- otherwise mark as `unknown` and recommend an independent cross-validation source.

Northcutt et al. (2021) showed label noise destabilizes downstream rankings even at ~3% rates; this artifact records what the project knows, doesn't know, and plans to do about it. Closes gap G6.

### Step H — Croissant sidecar (`croissant/<source>.jsonld`)
For each recommended source, emit a machine-readable Croissant JSON-LD document (Akhtar et al., 2024) populated from the data sheet's Motivation, Composition, Collection, Distribution and Maintenance sections. Use the MLCommons Croissant editor or the `mlcroissant` Python library.

Even if the project never publishes, having Croissant sidecars makes the artifacts ingestible by Hugging Face, Kaggle, Google Dataset Search and OpenML, and is the standardization bet most likely to outlive any single proprietary format. Closes gap G7.

### Step I — Versioning policy (`versioning-policy.md`)
Short statement covering:
- how dataset versions are pinned (URL with version tag, snapshot hash, archived copy),
- where snapshots live (DVC remote, Zenodo deposit, S3 bucket),
- the policy for re-ingest cadence (one-shot, monthly, on-demand),
- the policy for breaking change detection (re-run the executable schema and diff),
- the policy for retiring a dataset (when and how).

Closes gap G8 (Hutchinson et al., 2021).

### Step J — Phase 3 handoff manifest (`phase-3-handoff.md`)
One page listing every artifact in `phase-2/` (earn-the-data outputs + companion outputs) with a one-line description and the test "Phase 3 can begin if and only if this artifact exists and is non-empty." This is the gate.

---

## Deliverables (writes all to `phase-2/`)

1. `ingestion-log.md` *(new)*
2. `ingested-data-description.md` *(new)*
3. `quality-cross-check.md` *(new)*
4. `schemas/<source>.yaml` (one per recommended source) *(new)*
5. `geospatial-declarations.md` *(new)*
6. `bias-and-annotation.md` *(new)*
7. `croissant/<source>.jsonld` (one per recommended source) *(new)*
8. `versioning-policy.md` *(new)*
9. `phase-3-handoff.md` *(new — the gate)*

The four earn-the-data artifacts are not modified.

---

## Quality checks (the skill's own self-audit)

Before declaring done, the skill must confirm:
- **Q1.** Every recommended source in `data-inventory.md` appears in `ingestion-log.md`, `ingested-data-description.md`, `schemas/`, and `croissant/`. No silent skips.
- **Q2.** Every SHA-256 in the ingestion log is computable from a file currently on disk (or marked `unreproducible: yes` with a remediation note).
- **Q3.** Every schema validates against at least one row from the ingested file. (Schemas that don't parse the data they purport to describe are worse than no schema.)
- **Q4.** Every spatial dataset in `data-sheets/` appears in `geospatial-declarations.md` with both native CRS and analysis CRS declared.
- **Q5.** Every crowd-annotated source has an annotation-quality estimate or an explicit `unknown` with a planned mitigation.
- **Q6.** `phase-3-handoff.md` lists every artifact and the gate condition.

If any check fails, surface the failure inline and stop — do not produce a final "ready for Phase 3" summary that papers over a failure.

---

## Anti-patterns (what this skill must NOT do)

- **Re-doing the rubric.** The 5-dimension rubric is earn-the-data's domain. If the architect wants a *different* rubric (e.g., full Wang & Strong), produce the cross-check (Step D), do not re-score.
- **Re-doing the brief-revisit.** Step 10 of earn-the-data is the most important single output of Phase 2; this skill must not silently overwrite it.
- **Producing schemas from observed data without expert review.** TFDV's documentation is explicit (Breck et al., 2019): inferred schemas are a *starting point*, not a finished artifact. Schemas in this skill are seeded from the data sheet (expert-authored), not auto-inferred from ingested bytes.
- **Treating absence of evidence as evidence of absence.** If a quality dimension cannot be assessed (e.g., timeliness of a one-shot historical dataset), the cross-check records *deferred* with a reason. It does not score the dimension 0/3 or omit it silently.
- **Producing Croissant sidecars that disagree with the data sheets.** The Markdown data sheets are the source of truth; the JSON-LD is a downstream serialization. If the two disagree, the data sheet wins.
- **Running before earn-the-data.** This is the only hard precondition. Halting is correct behavior.

---

## Handoff to Phase 3 (Data Preparation)

Phase 3 starts when `phase-3-handoff.md` exists, every artifact it lists exists and is non-empty, and the user signs off. The Phase 3 skill (when it exists) should consume:
- `schemas/<source>.yaml` as the validation entry point for any prepared data,
- `geospatial-declarations.md` as the binding declaration of analysis CRS and aggregation unit,
- `versioning-policy.md` as the rule for whether a re-ingest is required before preparation begins,
- `brief-revisit.md` as the binding scope statement (any Phase 3 work outside the brief-revisit's surviving question must be flagged and re-discussed with the user).

Phase 3 must not silently *narrow* the brief-revisit (silently choosing a subset of recommended datasets); narrowings must be explicit and recorded.

---

## References (the literature this skill operationalizes)

- Akhtar, M., et al. (2024). *Croissant: A Metadata Format for ML-Ready Datasets.* NeurIPS 2024 Datasets and Benchmarks Track. https://arxiv.org/abs/2403.19546
- Bender, E. M., & Friedman, B. (2018). Data statements for natural language processing. *TACL, 6,* 587-604.
- Breck, E., Polyzotis, N., Roy, S., Whang, S. E., & Zinkevich, M. (2019). Data validation for machine learning. *SysML 2019.*
- Chapman, P., Clinton, J., Kerber, R., et al. (2000). *CRISP-DM 1.0: Step-by-step data mining guide.* CRISP-DM Consortium.
- Gebru, T., Morgenstern, J., Vecchione, B., et al. (2021). Datasheets for datasets. *Communications of the ACM, 64*(12), 86-92.
- Heger, A. K., Marquis, L. B., Vorvoreanu, M., Wallach, H., & Wortman Vaughan, J. (2022). Understanding ML practitioners' data documentation perceptions, needs, challenges, and desiderata. *PACM HCI 6(CSCW2).*
- Holland, S., Hosny, A., Newman, S., Joseph, J., & Chmielinski, K. (2018). *The Dataset Nutrition Label.* arXiv:1805.03677.
- Hutchinson, B., Smart, A., Hanna, A., et al. (2021). Towards accountability for machine learning datasets. *FAccT '21,* 560-575.
- ISO/IEC 25012:2008. *SQuaRE — Data quality model.*
- Northcutt, C. G., Athalye, A., & Mueller, J. (2021). Pervasive label errors in test sets destabilize ML benchmarks. *NeurIPS 2021 Datasets and Benchmarks Track.*
- Openshaw, S., & Taylor, P. J. (1979). A million or so correlation coefficients: Three experiments on the modifiable areal unit problem. In Wrigley (Ed.), *Statistical applications in the spatial sciences.* Pion.
- Polyzotis, N., Roy, S., Whang, S. E., & Zinkevich, M. (2018). Data lifecycle challenges in production machine learning. *SIGMOD Record, 47*(2), 17-28.
- Pushkarna, M., Zaldivar, A., & Kjartansson, O. (2022). Data Cards: Purposeful and transparent dataset documentation for responsible AI. *FAccT '22,* 1776-1826.
- Sambasivan, N., Kapania, S., Highfill, H., Akrong, D., Paritosh, P., & Aroyo, L. M. (2021). "Everyone wants to do the model work, not the data work": Data cascades in high-stakes AI. *CHI '21,* Article 39.
- Studer, S., Bui, T. B., Drescher, C., et al. (2021). Towards CRISP-ML(Q). *MAKE, 3*(2), 392-413.
- Tukey, J. W. (1977). *Exploratory data analysis.* Addison-Wesley.
- Wang, R. Y., & Strong, D. M. (1996). Beyond accuracy: What data quality means to data consumers. *JMIS, 12*(4), 5-33.
- Wilkinson, M. D., et al. (2016). The FAIR Guiding Principles. *Scientific Data, 3,* 160018.

---

## Relationship to earn-the-data (explicit)

| Concern | earn-the-data covers | phase-2-companion covers |
|---|---|---|
| Decision unit | YES (Step 1) | reads it |
| Six-category candidate hunt | YES (Step 2) | reads inventory |
| Primary-source verification | YES (Step 3) | reads inventory |
| 2× resolution rule | YES (Step 4) | reads inventory |
| 5-dimension rubric (Provenance, Resolution, Coverage, Licensing, Bias) | YES (Step 5) | reads scores |
| 8-section data sheets | YES (Step 6) | reads data sheets, exports to Croissant |
| CRS / unit pitfalls | YES (Step 7, narrative) | extends to MAUP + edge effects + binding declaration |
| Sampling biases | YES (Step 8, narrative) | extends to annotation-quality estimate |
| Profiling plan (human-runnable EDA) | YES (Step 9) | converts to executable schemas |
| Brief-revisit | YES (Step 10) | reads, never overwrites |
| Ingestion log (timestamps, hashes, agent) | NO | YES (Step B) |
| Ingested-data description (observed, not asserted) | NO | YES (Step C) |
| Wang & Strong / ISO 25012 dimension cross-check | NO | YES (Step D) |
| Executable schema (TFDV / Pandera / GE / frictionless) | NO | YES (Step E) |
| MAUP and edge-effect declaration | NO (implicit only) | YES (Step F) |
| Annotation/label-noise estimate | NO (subsumed under bias) | YES (Step G, separated) |
| Croissant JSON-LD sidecar | NO | YES (Step H) |
| Versioning policy | NO | YES (Step I) |
| Phase 3 handoff gate | NO | YES (Step J) |

The two skills together cover Phase 2 to the standard the academic literature now expects. Used separately, each is incomplete.
