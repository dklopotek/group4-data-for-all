# Skill brief — CRISP-DM Phase 3: Data Preparation

> **Name:** `crispdm-phase-3-data-preparation`
> **Use:** when the student has finished Phase 2 (Data Understanding) and is about to start cutting, cleaning, deriving, joining, and writing files in service of a modeling step they have not yet built.
> **Stance:** opinionated and prescriptive. This is the heaviest phase in the course because the teacher will grade *how each processing decision was made*. Do not give the student a buffet — give them a chosen path with logged alternatives.

---

## description

A 5-step walkthrough of the canonical CRISP-DM Phase 3 (Chapman et al., 2000): **Select → Clean → Construct → Integrate → Format**. Each step has actions, Socratic prompts, a decision-log template, and an exit check. The skill enforces a pipeline-architect mindset: every transformation is versioned, justified, reversible-by-default, and exits with a contract.

## triggers

Invoke this skill when the user says any of:

- "I'm starting data preparation"
- "I've finished understanding the data, now what"
- "How do I clean this"
- "Should I drop this column / impute these missing values / merge these layers"
- "I need to build the modeling-ready dataset"
- "We have raw layers, we need one priority map"
- Or whenever the user is in the gap between *understanding raw data* and *running an analysis*.

Do **not** invoke this skill for:
- Pure exploration ("show me what's in this file") → that's Phase 2.
- Model selection or training → that's Phase 4.
- UI work → out of scope for this course.

## inputs the skill expects from the user

Before starting, confirm or solicit:

1. **The Phase-1 business question** restated in one sentence ("we want to produce X for Y, so that Z").
2. **The Phase-2 data inventory**: list of sources, each with format, CRS (if spatial), resolution, time range, license, known issues, vetting score from the `earn-the-data` skill if it was used.
3. **The target output spec**: what does the *next* phase (modeling) need? A single table? A raster stack? A spatial join? At what scale?
4. **The compute environment**: pandas-in-a-notebook, dbt + Parquet, PostGIS, Dagster + DuckDB, etc. The skill is tool-agnostic but the user must declare the tool.
5. **The repo and the data-product naming convention**: where do artifacts live, how are they versioned.

If any of these is missing, **stop and ask**. Phase 3 without a target spec is a notebook accident.

---

## Sub-step 3.1 — SELECT DATA

### actions

1. **Inventory every source** as a row in the selection log. One source = one row. If you have one big "all_data.csv" file, decompose it conceptually into its logical sources.
2. **Per source, decide IN or OUT** against a written inclusion criterion. Common criteria: relevance to the Phase-1 question, license compatibility, spatial/temporal coverage, vetting score from `earn-the-data`, redundancy with another retained source.
3. **Per retained source, decide which columns are IN/OUT.** Drop columns are justified individually.
4. **Per retained source, define row-level filters** (temporal cut, spatial cut, quality cut). Each filter has a rationale and a row-count impact.
5. **Implement filters as `WHERE` clauses or function arguments** that emit *two* outputs: the kept rows and the rejected rows. **Never delete; always partition.** Rejected rows go to a `rejected/` partition with a `reason_code` column.
6. **Sampling**, if needed: declare the sampling method (random, stratified, spatial-stratified, temporal-windowed) and seed. Justify against statistical-bias concerns. For spatial data, the default should be spatial-stratified, not simple random.

### Socratic prompts

- "What is the cost if you keep this row and it turns out to be junk?"
- "What is the cost if you drop this row and it turned out to matter?"
- "If a reviewer asks 'why is the dataset 12,847 rows and not 15,000?', can you point to one log entry per missing 2,153 rows?"
- "Is this filter reversible? If we relax it next week, can we re-run without re-downloading?"
- "Did you sample? If yes, why is your sample unbiased for the question?"

### decision-log template (selection)

| dec_id | source | scope | keep? | rationale | rows in | rows out | filter spec | reviewer | date |
|---|---|---|---|---|---|---|---|---|---|
| SEL-001 | OpenData BCN tree inventory | full file | YES | core layer for host-tree density | 198,243 | 0 | — | — | YYYY-MM-DD |
| SEL-002 | OpenData BCN tree inventory | species column | YES | needed for mycorrhizal-host filter | — | — | normalize against GBIF backbone | — | YYYY-MM-DD |
| SEL-003 | OpenData BCN tree inventory | rows where `planting_date < 1990` | NO | data quality before 1990 is unreliable per source metadata | 198,243 | 31,402 | `planting_date >= '1990-01-01'` | — | YYYY-MM-DD |
| SEL-004 | OSM impervious surfaces | rows outside Barcelona muni boundary | NO | out of scope per Phase-1 | — | — | `ST_Within(geom, muni)` | — | YYYY-MM-DD |

### exit check for 3.1

- Every retained source has a written inclusion rationale.
- Every dropped column has a written exclusion rationale.
- The total row count in the kept partition + the rejected partition equals the raw row count. **No rows are unaccounted for.**
- Filters are executable code, not described in prose.
- If you sampled, the seed is recorded.

---

## Sub-step 3.2 — CLEAN DATA

### actions

1. **Profile** each retained source: row count, column dtypes, null counts per column, unique counts, min/max/mean/median per numeric column, sample of unique values per categorical column, geometry validity rate per spatial layer, CRS per spatial layer.
2. **Classify each quality issue** along Rahm & Do's (2000) axes: schema vs. instance, single-source vs. multi-source. Multi-source issues defer to Step 3.4.
3. **For missing values**, classify the mechanism (MCAR / MAR / MNAR per Rubin, 1976; Little & Rubin, 2019). The classification is a *judgment about the world*, not about the data — it requires domain knowledge.
4. **For outliers**, detect (≥3σ, ≥1.5×IQR, isolation forest, domain-specific bounds) but **never silently remove**. Flag first; decide treatment in a logged step.
5. **For duplicates**, distinguish exact (hash) from near (entity-resolution problem — defer to 3.4 if it requires cross-source matching).
6. **For type/encoding**: enforce types at ingest. Use a schema validator (Pandera, Great Expectations, dbt tests). Set Unicode normalization to NFC. Set date locale explicitly.
7. **For geospatial**: run `ST_IsValid` or `geom.is_valid` on every layer; repair with `make_valid` (not `buffer(0)` — that lies for non-simple polygons); reproject to the project's canonical CRS at ingest; never re-project repeatedly.
8. **Emit a Data Cleaning Report** (Markdown + JSON sidecar) per source.

### Socratic prompts

- "Is this missingness because the value didn't exist, wasn't measured, or was deleted? Each implies a different fix."
- "If you impute with the mean, you're betting MCAR. Is that bet defensible?"
- "Why is this an outlier — sensor error, real rare event, or a different unit? The treatment depends on the answer."
- "If you re-run this cleaning step tomorrow, will it produce bit-identical output? If not, where is the non-determinism?"
- "Did you check geometries for validity *before* the join, or did the join silently drop them?"

### decision-log template (cleaning)

| dec_id | dataset | issue | decision | rationale | rows affected | reversible? | reviewer | date |
|---|---|---|---|---|---|---|---|---|
| CLN-001 | tree_inventory | 12% missing `species` | flag + drop | listwise deletion under assumed MAR conditional on `district` | 23,789 | YES (rejected partition) | — | YYYY-MM-DD |
| CLN-002 | tree_inventory | 0.4% `diameter_cm` > 300 | flag + cap at 300 | physically implausible for street trees; cap rather than drop | 793 | YES (original retained in `raw_diameter_cm`) | — | YYYY-MM-DD |
| CLN-003 | OSM impervious | 1.2% invalid geometries (self-intersections) | repair with `ST_MakeValid` | OGC SF compliance; required for downstream `ST_Intersects` | 2,408 | YES (`raw_geom` retained) | — | YYYY-MM-DD |
| CLN-004 | soil raster | NoData over urban areas (~35%) | leave as NoData; do not interpolate | NoData carries information about urban impermeability; imputing would smuggle a model into the data | 0 | YES | — | YYYY-MM-DD |
| CLN-005 | tree_inventory | mixed date formats `DD/MM/YYYY` and `YYYY-MM-DD` | normalize to ISO 8601 | unambiguous; international standard | all | YES | — | YYYY-MM-DD |
| CLN-006 | all spatial layers | mixed CRSs (4326, 25831, 3857) | reproject all to EPSG:25831 at ingest | canonical project CRS per ADR-001 | all | YES (sources unchanged) | — | YYYY-MM-DD |

### exit check for 3.2

- Every issue identified during profiling has a log entry.
- For each missing-value treatment, the assumed mechanism is named.
- No row was modified in place; every modification has a new column or a new artifact.
- All spatial layers are valid (`is_valid` rate = 100%) and in the canonical CRS.
- The cleaning code is deterministic given the same inputs and seed.

---

## Sub-step 3.3 — CONSTRUCT DATA

### actions

1. **List the constructions** required by the modeling step: derived attributes, aggregations, normalizations, composite indices. Each one is a named feature.
2. **For each derived attribute**, write the formula. The formula is code; the documentation cites the source of the formula.
3. **For aggregations** (especially zonal statistics in spatial work), produce *multiple* summaries (mean, median, sum, count, percentile) where the choice is not pre-determined by theory. Let the modeling phase pick.
4. **For normalization/standardization**, use a `Pipeline` object whose `fit` happens on training data only and whose `transform` is applied identically to test/inference data. **Fit-on-full-data is the leakage anti-pattern** — see Kapoor & Narayanan (2023).
5. **For composite indices**, follow the OECD/JRC handbook (Nardo et al., 2008): theoretical framework → normalization → weighting → aggregation → **sensitivity analysis on weights**. The sensitivity analysis is not optional. Emit a rank-stability metric using Sobol or Morris (Saltelli et al., 2008).
6. **Version every construction** in the pipeline. A new weight set = a new artifact version, not an overwrite.

### Socratic prompts

- "If you weight the inputs differently, does the answer change? By how much? If a 10% perturbation flips the top-10 rankings, your index is fragile."
- "Where did this formula come from? Cite a paper, a standard, or a documented domain rule. 'It seemed reasonable' is not a rationale."
- "What's the unit of this derived attribute? If you can't say, you don't have a derived attribute, you have a number."
- "Is this feature using information that wouldn't be available at inference time? If yes, you have a leakage bug."

### decision-log template (construction)

| dec_id | feature | formula | inputs | unit | alternatives considered | sensitivity result | reviewer | date |
|---|---|---|---|---|---|---|---|---|
| CON-001 | `host_density_50m` | count of mycorrhizal-host trees per 50 m cell | tree_inventory.species ∈ FungalRoot list | count | basal-area-weighted variant | rank correlation ρ=0.91 between count and basal-area variants | — | YYYY-MM-DD |
| CON-002 | `imperv_frac_50m` | fraction of cell area covered by impervious polygons | OSM impervious surfaces | dimensionless [0,1] | — | — | — | YYYY-MM-DD |
| CON-003 | `soil_suitability_50m` | weighted sum of normalized pH, OC, texture | LUCAS soil raster | dimensionless [0,1] | unweighted mean | weights ADR-003; Sobol S1 [0.31, 0.42, 0.27] | — | YYYY-MM-DD |
| CON-004 | `barrier_priority_v1` | composite of CON-001..003 | CON-001..003 | dimensionless [0,1] | — | rank-stability 0.84 under ±10% weight perturbation | — | YYYY-MM-DD |

### exit check for 3.3

- Every derived feature has a formula, an input lineage, and a unit.
- Composite indices have a weighting ADR and a sensitivity-analysis log.
- No fit-then-leak pattern: all scalers/encoders are saved as serialized pipeline objects.
- Feature names are `snake_case`, descriptive, and unit-suffixed where applicable.

---

## Sub-step 3.4 — INTEGRATE DATA

### actions

1. **For each planned join, declare the cardinality**: 1:1, 1:N, or N:N. If N:N, **stop and re-design** — N:N is almost always a bug.
2. **Pre-join, snapshot row counts**. Post-join, assert the expected row count. A test that fails this assertion is a release blocker.
3. **For spatial joins**, declare the predicate explicitly (`intersects`, `contains`, `within`, `nearest`) and the boundary convention (open vs. closed). Test on a known edge case.
4. **For fuzzy / entity-resolution joins**, use a Fellegi–Sunter-based tool (e.g., Splink — Linacre, Kennedy & Tilling, 2022). Declare the threshold; produce a precision/recall estimate on a labeled validation sample.
5. **Reconcile units, locales, time zones, and CRSs at ingest**, not at the join. Joining on misaligned units silently produces wrong answers.
6. **Apply the 2× resolution rule**: integration output is no finer than 2× the coarsest input resolution. If your finest input is 1 m and your coarsest is 30 m, integrate at 60 m, not 1 m. Document this as an ADR.
7. **Declare a conflict-resolution policy** *before* the join. Trust hierarchy, recency, voting, or flag-and-defer. Conflicts go to a `conflicts/` audit table.

### Socratic prompts

- "If your join doubles the row count, was that expected? If not, where's the duplicate key?"
- "What happens to a feature that falls exactly on the boundary of two zones? Two assignments? Zero? One arbitrary one? Did you test this?"
- "Your finest raster is 1 m. Your coarsest is 30 m. Why is your output 1 m? Is it really 1 m, or is it 30 m pretending to be 1 m?"
- "When two sources disagree, who wins? Is that a documented policy or an accident?"

### decision-log template (integration)

| dec_id | join | type | predicate / key | cardinality (expected → actual) | conflict policy | rows in | rows out | reviewer | date |
|---|---|---|---|---|---|---|---|---|---|
| INT-001 | trees ⋈ districts | spatial | `ST_Within` (closed) | 1:1 → 1:1 | — | 174,454 | 174,454 | — | YYYY-MM-DD |
| INT-002 | host_density ⋈ soil_suitability | raster align | resample to 50 m EPSG:25831 | grid:grid | — | — | — | — | YYYY-MM-DD |
| INT-003 | trees ⋈ OSM tree points | fuzzy spatial | within 5 m AND species match | 1:1 → 1:1.07 (7% multi-match) | municipal wins; OSM logged to `conflicts/` | 174,454 | 174,454 (12,213 conflicts) | — | YYYY-MM-DD |

### exit check for 3.4

- All joins have asserted cardinalities.
- All conflicts have a logged resolution.
- Integration output resolution is no finer than 2× the coarsest input.
- CRSs, units, time zones are uniform across the integrated artifact.
- No silent row inflation or deflation.

---

## Sub-step 3.5 — FORMAT DATA

### actions

1. **Choose the target format** based on access pattern, not familiarity:
   - Tabular analytical → **Parquet** (or **GeoParquet** for vector geospatial).
   - Multi-dim arrays → **Zarr** (or NetCDF if downstream tools demand it).
   - Desktop-GIS round-tripping → **GeoPackage**, never Shapefile.
   - Human-readable export → CSV, with explicit encoding (UTF-8) and locale.
   - Streaming → Avro / Arrow IPC.
2. **Enforce naming conventions**: `snake_case`, no spaces, no special characters, unit-suffixed where applicable, source-prefixed where ambiguous. Pin a `glossary.md` in the repo.
3. **Embed metadata in the file**, not in a sidecar. Parquet footer, GeoPackage SQLite metadata tables, GeoParquet metadata block, NetCDF/Zarr CF attributes.
4. **Reshape to tidy form** (Wickham, 2014): each variable a column, each observation a row, each observational unit a table. Wide-to-long pivots happen here, not in modeling.
5. **Ship a datasheet** (Gebru et al., 2021) or **data card** (Pushkarna, Zaldivar & Kjartansson, 2022) with every published artifact: motivation, composition, collection, preprocessing, uses, distribution, maintenance.
6. **Mint a persistent identifier** for archived outputs (Zenodo DOI for course deliverables; internal UUID for pipeline-internal artifacts) and meet FAIR (Wilkinson et al., 2016).

### Socratic prompts

- "If someone three years from now finds this file on a hard drive with no other context, can they tell what's in it, what the CRS is, what the units are, and how it was made?"
- "Why CSV? If the answer is 'it's easy to open in Excel', that's not an engineering rationale."
- "Is your column name self-documenting? `pop` is not; `census_pop_2020_count` is."
- "Does your file declare its schema, or does it rely on the reader to guess?"

### decision-log template (format)

| dec_id | artifact | format | rationale | metadata embedded? | datasheet? | identifier | reviewer | date |
|---|---|---|---|---|---|---|---|---|
| FMT-001 | barrier_priority_v1_50m | GeoParquet | cloud-native, columnar, queryable from DuckDB / Sedona / GeoPandas | YES (CRS in geo metadata; schema in footer) | YES (`datasheet.md`) | Zenodo DOI | — | YYYY-MM-DD |
| FMT-002 | barrier_priority_v1_50m_gpkg | GeoPackage | desktop-GIS round-trip for collaborators on QGIS | YES (gpkg_metadata table) | shared with FMT-001 | — | — | YYYY-MM-DD |
| FMT-003 | decision_log.csv | CSV (UTF-8) | human-readable; reviewed in PRs | header row | self-describing | repo path | — | YYYY-MM-DD |

### exit check for 3.5

- Format is justified, not defaulted.
- Names follow the convention; glossary is in the repo.
- Metadata travels with the file.
- Datasheet exists and answers the seven Gebru et al. categories.
- Artifact has a stable identifier.

---

## deliverables (the Phase-3 output bundle)

A complete Phase-3 deliverable contains, at minimum:

1. **The modeling-ready artifact** (Parquet / GeoParquet / Zarr / GeoPackage), in the project's canonical CRS and at the integration-appropriate resolution.
2. **The rejected/conflicts audit tables**, in the same format as the artifact.
3. **The decision log** (`decisions.csv` or `decisions.md`) with all SEL / CLN / CON / INT / FMT entries.
4. **ADRs** for the load-bearing choices (canonical CRS, integration resolution, composite-index weights, conflict policy).
5. **Sensitivity-analysis log** for every choice that is a hyperparameter (cleaning thresholds, weights, join tolerances).
6. **The datasheet** per Gebru et al. (2021) — motivation, composition, collection, preprocessing, uses, distribution, maintenance.
7. **The data contract** with the modeling phase (schema, freshness, quality SLOs, lineage pointer).
8. **The pipeline code** itself: a DAG in Airflow / Dagster / Prefect, or a `dbt project + Makefile`, runnable with one command from raw inputs.
9. **A test suite**: schema tests, row-count assertions, geometry-validity assertions, join-cardinality assertions.
10. **A README** that explains how to rebuild the artifact from raw inputs.

If any of items 1–7 is missing, the Phase-3 deliverable is incomplete regardless of how good the artifact is.

---

## quality checks (run before declaring Phase 3 done)

- [ ] **Reproducibility**: rebuild from raw inputs with one command. Output is bit-identical (or, where non-determinism is intentional, identical up to the declared seed).
- [ ] **Lineage**: for any value in the final artifact, can you point to the inputs and transformations that produced it in one query?
- [ ] **Row accounting**: raw row count = kept + rejected + conflict-deferred. No rows are unaccounted for.
- [ ] **Schema validation**: schema-on-write is enforced; the artifact passes its own contract.
- [ ] **Geometry validity**: 100% of geometries are valid; CRS is uniform and explicit.
- [ ] **Unit consistency**: every numeric column has a declared unit and the values are in that unit.
- [ ] **No leakage**: scalers/encoders fit on train only; features do not use future-only information.
- [ ] **Sensitivity declared**: weight choices and threshold choices have a sensitivity-analysis log.
- [ ] **Datasheet shipped**: all seven Gebru et al. categories answered.
- [ ] **Decision log complete**: every transformation has a log entry.
- [ ] **Anti-pattern audit**: none of the twelve anti-patterns in §10 of the academic deep-dive is present.

---

## anti-patterns (call these out and stop the user)

1. **Silent row drop.** `df = df.dropna()` with no log entry. → Stop. Always log + partition to `rejected/`.
2. **In-place overwrite of raw data.** → Stop. Raw is immutable; cleaned outputs are new artifacts.
3. **`fillna(mean)` without naming the mechanism.** → Stop. State MCAR/MAR/MNAR; if MCAR, justify; if MAR, use proper multiple imputation.
4. **CRS implicit / mixed.** → Stop. Declare and validate at ingest; reproject everything to the canonical CRS.
5. **Joining at the finest resolution available.** → Stop. Apply the 2× rule.
6. **N:N join without an association table.** → Stop. Re-design.
7. **Fit-on-full-data scalers.** → Stop. Refactor as a Pipeline; fit on train only.
8. **Shapefile as the canonical output.** → Stop. Use GeoPackage / GeoParquet.
9. **Composite index with one set of weights and no sensitivity analysis.** → Stop. Run a Sobol or Morris perturbation.
10. **Conflict resolution that is "whichever loaded last".** → Stop. Declare a policy.
11. **`pd.read_csv` ingest into a `pd.to_csv` egress with no schema enforcement.** → Stop. Use Parquet with a schema.
12. **No data contract for Phase 4.** → Stop. Phase 3 is not done.

---

## handoff to Phase 4

The handoff is a **data contract** the modeling phase commits against:

```yaml
artifact: barrier_priority_v1_50m.parquet
schema:
  cell_id:        {type: int64,   nullable: false, unique: true}
  geometry:       {type: geometry, crs: EPSG:25831, validity: 100%}
  host_density:   {type: float64, unit: count, range: [0, 200], nullable: false}
  imperv_frac:    {type: float64, unit: dimensionless, range: [0, 1], nullable: false}
  soil_suit:      {type: float64, unit: dimensionless, range: [0, 1], nullable: false}
  priority_score: {type: float64, unit: dimensionless, range: [0, 1], nullable: false}
freshness:
  produced_at: 2026-MM-DD
  valid_until: 2027-MM-DD
quality_slos:
  missingness_max_pct: 0
  geometry_validity_pct: 100
  duplicate_cell_id_count: 0
lineage:
  pipeline: dagster://group4/barrier_priority
  decision_log: research/crispdm/decisions.csv
sensitivity:
  composite_weights: see ADR-003; rank-stability 0.84
rebuild:
  command: "make rebuild"
```

If Phase 4 starts before this contract exists, the project loses the ability to attribute modeling failures to data versus model. Hold the line.

---

## references (verified for the brief)

- Chapman, P. et al. (2000). *CRISP-DM 1.0: Step-by-step data mining guide*. SPSS Inc.
- Chu, X., Ilyas, I. F., Krishnan, S., & Wang, J. (2016). Data Cleaning: Overview and Emerging Challenges. *SIGMOD*.
- Fellegi, I. P., & Sunter, A. B. (1969). A theory for record linkage. *JASA*.
- Gebru, T. et al. (2021). Datasheets for datasets. *Communications of the ACM*, 64(12).
- Ilyas, I. F., & Chu, X. (2019). *Data Cleaning*. ACM Books.
- Kandel, S., Paepcke, A., Hellerstein, J., & Heer, J. (2011). Wrangler. *CHI*.
- Kapoor, S., & Narayanan, A. (2023). Leakage and the reproducibility crisis in ML-based science. *Patterns*.
- Krishnan, S. et al. (2016). ActiveClean. *VLDB*.
- Linacre, R., Kennedy, P., & Tilling, K. (2022). Splink. *JOSS*.
- Little, R. J. A., & Rubin, D. B. (2019). *Statistical Analysis with Missing Data* (3rd ed.).
- Martínez-Plumed, F. et al. (2021). CRISP-DM Twenty Years Later. *IEEE TKDE*.
- Nardo, M. et al. (2008). *OECD Handbook on Constructing Composite Indicators*.
- Nygard, M. (2011). *Documenting Architecture Decisions*.
- Polyzotis, N., Roy, S., Whang, S. E., & Zinkevich, M. (2018). Data Lifecycle Challenges in Production ML. *SIGMOD Record*.
- Press, G. (2016). Cleaning Big Data. *Forbes*.
- Pushkarna, M., Zaldivar, A., & Kjartansson, O. (2022). Data Cards. *FAccT*.
- Rahm, E., & Do, H. H. (2000). Data Cleaning: Problems and Current Approaches. *IEEE Data Eng. Bulletin*.
- Rubin, D. B. (1976). Inference and missing data. *Biometrika*.
- Saltelli, A. et al. (2008). *Global Sensitivity Analysis: The Primer*.
- Schröer, C., Kruse, F., & Gómez, J. M. (2021). A Systematic Literature Review on Applying CRISP-DM. *Procedia CS*.
- Sculley, D. et al. (2015). Hidden Technical Debt in ML Systems. *NeurIPS*.
- Van Buuren, S. (2018). *Flexible Imputation of Missing Data* (2nd ed.).
- Wickham, H. (2014). Tidy Data. *Journal of Statistical Software*.
- Wilkinson, M. D. et al. (2016). FAIR Guiding Principles. *Scientific Data*.
