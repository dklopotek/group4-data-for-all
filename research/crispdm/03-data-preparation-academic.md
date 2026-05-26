# CRISP-DM Phase 3 — Data Preparation: An Academic Deep-Dive

**Audience:** Graduate seminar on data-pipeline design (architect track, no UI).
**Status:** Research synthesis with verified citations.
**Domain framing:** Generic, with deliberate spatial/geospatial emphasis (live test case: Barcelona urban-ecology mycorrhizal pipeline).
**Length target:** 4,000–6,000 words.

---

## 1. Canonical Phase 3: the five generic tasks, exactly as the standard defines them

The Cross-Industry Standard Process for Data Mining (CRISP-DM) 1.0, authored by Chapman, Clinton, Kerber, Khabaza, Reinartz, Shearer and Wirth (2000) and published as a SPSS / NCR / DaimlerChrysler consortium document, decomposes the data-mining lifecycle into six phases: Business Understanding, Data Understanding, Data Preparation, Modeling, Evaluation and Deployment (Chapman et al., 2000). Phase 3 — Data Preparation — is described in the standard as covering *"all activities to construct the final dataset (data that will be fed into the modeling tool(s)) from the initial raw data"* (Chapman et al., 2000, p. 27). Critically, the standard specifies that *"data preparation tasks are likely to be performed multiple times, and not in any prescribed order"*, which is the first clue that Phase 3 is iterative-by-design rather than a single waterfall stage.

The five **generic tasks** of Phase 3, with their canonical outputs as enumerated in the CRISP-DM 1.0 user guide, are:

| # | Generic task | Canonical outputs (per Chapman et al., 2000) |
|---|---|---|
| 3.1 | **Select Data** | Rationale for inclusion/exclusion of attributes and records |
| 3.2 | **Clean Data** | Data cleaning report (issues identified, how each was resolved, residual quality concerns) |
| 3.3 | **Construct Data** | Derived attributes; generated records |
| 3.4 | **Integrate Data** | Merged data |
| 3.5 | **Format Data** | Reformatted data (no semantic change, only syntactic re-presentation for the modeling tool) |

These five generic tasks are *the* deliverable contract of Phase 3. Schröer, Kruse and Gómez (2021), in their systematic literature review of 24 CRISP-DM applications across IEEE/ScienceDirect/ACM, confirm that the Data Preparation phase is still treated in modern empirical work as the same five-task structure, even when other CRISP-DM phases get reinterpreted for ML-Ops or agile contexts. Martínez-Plumed et al. (2021), revisiting CRISP-DM after twenty years across 7 real cases and 51 use cases, retain the same five Phase-3 tasks while arguing that the *path* between them needs to become a flexible "trajectory" rather than a sequence.

A pipeline-architect reading of the standard is: **Phase 3 produces a versioned, documented, reproducible artifact (the modeling-ready dataset) plus a decision log that justifies every transformation between raw input and that artifact**. Everything else in this deep-dive is in service of that contract.

---

## 2. The "80% of project time" claim — verify before you cite it

The folklore that data scientists spend 80% of their time on data preparation deserves scrutiny because it is the single most cited empirical claim about Phase 3.

- The CRISP-DM 1.0 guide itself states only that *"data preparation… is the most time-intensive phase"* (Chapman et al., 2000, p. 28), without a specific percentage.
- Press (2016), reporting on a CrowdFlower survey of 80 data scientists in *Forbes*, found that respondents spent 60% of their time cleaning and organizing data and a further 19% collecting data sets — for a combined 79% on data preparation. This is the most common origin point for the "80%" claim.
- Dasu and Johnson (2003), in *Exploratory Data Mining and Data Cleaning*, reported industry estimates of 50–80%, anchoring the upper bound earlier than the *Forbes* citation.
- Anaconda's 2020 *State of Data Science* survey, reported by Woodie (2020) in *BigDATAwire*, found 45% of time on data preparation, down from earlier surveys but still the single largest line item.
- Dodds (2020), in a careful re-reading of the underlying surveys, cautions that the 80% figure is often quoted without distinguishing *cleaning* from *loading* and *exploring*, and that the precise number depends heavily on tooling maturity.

For the seminar deliverable, the defensible framing is: **"empirically, the data preparation phase consistently consumes 40–80% of total project effort across surveys from 2003 to 2020, with the precise figure depending on tooling, domain, and how 'preparation' is operationalized"**. The implication is not the number itself, but that *if the most expensive phase is the one with the least design rigor, the project will lose its money there*.

---

## 3. Task 3.1 — Select Data

### 3.1.1 What the standard requires

Per Chapman et al. (2000, p. 28), Select Data covers *"deciding on the data to be used for analysis"*. Selection criteria include relevance to the data-mining goal, data quality, and technical constraints (e.g., volume, data types). The required output is *"the rationale for inclusion/exclusion"* — i.e., the decision must be **documented**, not merely made.

### 3.1.2 Inclusion / exclusion criteria as first-class artifacts

A common anti-pattern is to filter rows or drop columns silently in a notebook cell that nobody re-reads. The pipeline-architect response is to treat inclusion/exclusion as a **specification**, not an implementation detail. A defensible Select Data step has:

1. **Column-level inclusion rationale**: every retained attribute is justified against the project's analytical question. Every dropped attribute has a reason logged (irrelevant, redundant, low quality, restricted licensing, ethical risk, etc.).
2. **Row-level inclusion rules**: temporal cuts ("only records after 2015 because the sensor was recalibrated"), spatial cuts ("only within the municipal boundary"), and quality cuts ("only records where the QC flag is 'good'") are codified as filters in the pipeline, each with a rationale.
3. **Reversibility**: filtered rows are not deleted — they are *partitioned out* into a `rejected/` table with a `reason_code`. This is critical for downstream audit and for sensitivity analysis ("what if we relax the 2015 cut to 2013?").

### 3.1.3 Sampling strategies

When the raw data is too large to use in full, sampling is itself a design decision with statistical consequences. Cochran (1977), the canonical reference, distinguishes **simple random**, **stratified**, **cluster**, and **systematic** sampling. For pipeline work the most consequential variants are:

- **Stratified sampling**: required when subgroups are unequally represented and the model must perform across all of them (e.g., rare habitat types in an ecological dataset).
- **Temporal sampling**: when streaming data is downsampled. Requires explicit choice between random-within-window, last-in-window, or aggregated-window.
- **Spatial sampling**: a known trap. Naïve random sampling of spatial points yields biased estimates because of spatial autocorrelation (Tobler's First Law of Geography: nearby things are more related than distant things). Stratified spatial sampling, grid-based sampling, or sample-with-distance-constraints are the defensible alternatives. See Wang, Stein, Gao and Ge (2012) for a survey.

### 3.1.4 The cost of premature filtering

Krishnan, Wang, Wu, Franklin and Goldberg (2016), in their ActiveClean work, demonstrate that aggressively dropping records before model training produces *systematically biased* models even when the dropped records are themselves "dirty". The mechanism is selection bias: rows missing not at random (see §4.2 below) carry information about the missingness mechanism that is destroyed when they are filtered. The architectural rule: **prefer flagging over filtering**. Add a `quality_flag` column; defer the drop decision until modeling, where it can be A/B-tested.

### 3.1.5 Geospatial selection gotchas

Spatial pipelines have selection failure modes that don't exist in tabular work:

- **Bounding-box selection that crosses the antimeridian** (longitude ±180°) silently drops half the world. Use polygon intersection, not bounding boxes, for international datasets.
- **Selection by administrative boundary at the wrong epoch**: municipal boundaries change. Joining 2024 census tracts to 2010 administrative geometries silently drops records on the boundary.
- **Selection from a tiled source without overlap** misses features that straddle tile edges. Always buffer tile reads by at least one feature radius.

---

## 4. Task 3.2 — Clean Data

Clean Data is described in CRISP-DM as *"raising the data quality to the level required by the selected analysis techniques"* (Chapman et al., 2000, p. 28). The standard's required output is a **Data Cleaning Report** that documents what changes were made and why. The literature on data cleaning is enormous; we synthesize the most decision-relevant strands here.

### 4.1 The taxonomy of dirty data

Rahm and Do (2000), in the foundational *Data Cleaning: Problems and Current Approaches*, distinguish two axes of dirty-data problems:

- **Single-source vs. multi-source**: single-source problems live within one dataset (missing values, outliers, typos); multi-source problems emerge when integrating across datasets (schema conflicts, entity-resolution failures, unit mismatches). Multi-source cleaning is properly the concern of Task 3.4 (Integrate), but Rahm and Do's taxonomy explains why cleaning and integration are deeply coupled.
- **Schema-level vs. instance-level**: schema-level problems are structural (a column should be `DECIMAL(10,2)` but is `VARCHAR`); instance-level problems are about individual values (a date written as `"31/02/2021"`).

Chu, Ilyas, Krishnan and Wang (2016), in their SIGMOD tutorial *Data Cleaning: Overview and Emerging Challenges*, extend this with a modern taxonomy of *qualitative* (rule- and constraint-based) versus *quantitative* (statistical and outlier-based) cleaning, and survey the machine-learning techniques that now augment both. Ilyas and Chu (2019), in the book-length treatment *Data Cleaning*, formalize the four sub-problems of any cleaning task: **error detection**, **error repair**, **value imputation**, and **deduplication**.

### 4.2 Missing data: a decision tree, not a default

Rubin's (1976) taxonomy, expanded in Little and Rubin's (2019) third edition of *Statistical Analysis with Missing Data*, classifies missingness into three mechanisms:

- **MCAR (Missing Completely At Random)**: missingness is independent of both observed and unobserved values. Example: a sensor battery died at random. **Safe to drop**, will not bias estimates (only inflate variance).
- **MAR (Missing At Random)**: missingness depends on observed variables but not on the missing value itself. Example: older sensors miss more readings, and we know the sensor age. **Multiple imputation is appropriate** if the imputation model conditions on the observed predictors of missingness.
- **MNAR (Missing Not At Random)**: missingness depends on the unobserved value itself. Example: pollution sensors fail more often at high concentrations. **No purely statistical fix; requires substantive modeling of the missingness mechanism**, often with sensitivity analyses bracketing the bias.

The architectural implication is that **the imputation choice must be justified against an assumed mechanism**, and the assumption must be logged. A pipeline that silently calls `df.fillna(df.mean())` has implicitly assumed MCAR — and is wrong about half the time in practice (Little and Rubin, 2019). Van Buuren's (2018) *Flexible Imputation of Missing Data* gives the canonical multiple-imputation recipe.

For pipeline-engineering purposes the imputation decision tree is:

1. **Diagnose**: tabulate missingness per column; cross-tabulate against other observed columns; check for monotone patterns.
2. **Classify**: which mechanism is most plausible? (Often only MAR vs. MNAR can be distinguished by domain knowledge, not by data alone.)
3. **Choose**:
   - MCAR + < 5% missing → listwise deletion is defensible.
   - MAR → multiple imputation (e.g., MICE; Van Buuren, 2018) or model-based (e.g., k-NN, regression).
   - MNAR → flag + sensitivity analysis; do not single-impute.
4. **Document**: log mechanism assumption, method chosen, rows affected, downstream sensitivity.

### 4.3 Outliers: statistical vs. domain-driven

There is no value-free definition of an outlier. The statistical definitions (e.g., points beyond ±3σ, or beyond 1.5×IQR per Tukey, 1977) are useful for *detection*, but the decision of whether to remove, cap, transform or retain is a **domain decision**. Aggarwal's (2017) textbook *Outlier Analysis* makes this point explicit and surveys detection methods (distance-based, density-based, model-based, ensemble). The pipeline rule: **detection is automated; treatment is logged**. Never let an outlier-removal threshold be a hidden hyperparameter.

### 4.4 Duplicate resolution

Duplicates can be **exact** (byte-identical rows from a re-ingestion) or **near** (the same real-world entity recorded twice with small variations). Exact duplicates are removed trivially after computing a hash. Near-duplicates require entity resolution (see §6.3). The trap is that "deduplication" is often run before integration, when many apparent duplicates are actually correct records from different sources that should be linked, not collapsed.

### 4.5 Type coercion and encoding

Type coercion errors are the silent killer of pipelines:

- Dates parsed as US-format (`MM/DD/YYYY`) when the source is European (`DD/MM/YYYY`) produce silently-shifted records that pass schema validation.
- Integer columns coerced to floats lose precision on large IDs.
- Unicode normalization (NFC vs. NFD) makes "café" not equal "café" depending on the input encoding. Use NFC consistently (see Davis and Whistler, 2024, in the Unicode TR15 standard).
- Number locale: `1,234.56` (US) vs. `1.234,56` (European) silently inverts.

Schema-on-write validation (e.g., Pandera, Great Expectations, dbt tests) is the architectural response: **fail loudly at ingest, never at query time**.

### 4.6 Geospatial cleaning — failure modes the textbook leaves out

Spatial data brings cleaning failure modes that have no analog in tabular work:

- **Invalid geometries**: self-intersecting polygons, polygons with rings in the wrong winding order, sliver polygons from upstream digitization. The OGC Simple Features standard (Herring, 2011) defines validity; tools like Shapely's `make_valid` or PostGIS's `ST_MakeValid` repair them. The classical `buffer(0)` trick (Ramsey, 2008) works for many cases but fails for non-simple polygons.
- **CRS mismatch**: combining a layer in WGS84 (EPSG:4326) with a layer in a UTM zone without reprojection produces silent misalignment; both layers will load and overlay visually, but distances and areas computed across them are nonsense. **Always declare and validate CRS at ingest.**
- **Topology errors**: gaps and overlaps between polygons that should tile. Tools: ArcGIS topology rules, JTS/GEOS validation, PostGIS `ST_IsValid`, the R `cleangeo` package.
- **Precision drift on reprojection**: repeatedly reprojecting between CRSs accumulates floating-point error. The architectural fix: store data in one canonical CRS, reproject only on output.
- **Geometry-attribute decoupling**: shapefile attribute encoding defaults vary by tool, leading to mojibake in attribute tables that look fine in the geometry but corrupt the joins downstream.

### 4.7 Tooling: Wrangler, OpenRefine, dbt tests

Kandel, Paepcke, Hellerstein and Heer (2011), in *Wrangler: Interactive Visual Specification of Data Transformation Scripts*, demonstrated that interactive, suggestion-driven cleaning was significantly faster than scripting-from-scratch — and, critically, **produced reusable scripts as artifacts**, addressing the reproducibility problem. The lineage from Wrangler runs through Trifacta and into modern tools (OpenRefine, AWS Glue DataBrew, dbt tests, Great Expectations). The architect's question is not "which tool" but "does the tool produce a versioned, replayable transformation script?". If it does not, it is a one-shot exploration tool, not a pipeline tool.

---

## 5. Task 3.3 — Construct Data

Construct Data covers *"constructive data preparation operations such as the production of derived attributes, entire new records, or transformed values for existing attributes"* (Chapman et al., 2000, p. 29). In modern parlance, this is **feature engineering**.

### 5.1 Derived attributes

Derived attributes are deterministic functions of existing attributes (e.g., `BMI = weight / height²`, or `distance_to_nearest_park` from a spatial join). The pipeline rule: **every derived attribute has a documented formula, an input lineage, and a unit**. The formula belongs in the pipeline code; the documentation belongs in the data dictionary; the lineage belongs in the orchestrator (Airflow, Dagster — see §8).

Kuhn and Johnson (2019), in *Feature Engineering and Selection*, provide a systematic treatment: encoding categoricals, handling skewness, interaction terms, basis expansions, and target encodings. They emphasize the leakage trap: features computed using information that would not be available at inference time produce overoptimistic offline performance and silent production failures.

### 5.2 Aggregation and zonal statistics

In spatial pipelines, the canonical construction is the **zonal statistic**: summarize a raster over the geometry of a vector zone (mean elevation per neighborhood, sum of impervious area per parcel, max NDVI per polygon). The choice of summary statistic (mean, median, sum, count, percentile) is a modeling decision, not a mechanical one, because it commits to a representation of the phenomenon. Architecturally, compute *multiple* summaries at construction time and defer the choice to modeling.

### 5.3 Normalization, standardization, transformation

- **Min-max normalization** ((x − min) / (max − min)) bounds values to [0,1] and preserves the shape of the distribution. Bad with outliers.
- **Z-score standardization** ((x − μ) / σ) centers and scales; assumes roughly symmetric distribution.
- **Robust scaling** (subtract median, divide by IQR) is the outlier-tolerant alternative.
- **Log / Box-Cox / Yeo-Johnson** transformations address skew.

The trap: fitting the normalizer on the entire dataset before train/test split leaks test-set statistics into training. The architecturally correct pattern is **fit-on-train, transform-on-train-and-test**, captured as a pipeline object (e.g., scikit-learn `Pipeline` / `ColumnTransformer`) so that the same scaler used in training is also serialized and used in inference. This is one of the leakage patterns Kapoor and Narayanan (2023) document as endemic in ML-based science.

### 5.4 Composite indices and weighting schemes

When the analytical product is itself an index (a barrier-reduction priority score, a sustainability rank, a vulnerability index), the construction step **is** the analysis. The OECD/JRC *Handbook on Constructing Composite Indicators* (Nardo, Saisana, Saltelli, Tarantola, Hoffman and Giovannini, 2008) lays out a ten-step methodology: theoretical framework → data selection → imputation → multivariate analysis → normalization → weighting → aggregation → uncertainty/sensitivity analysis → linking to other variables → visualization. The last three are routinely skipped and are also where defensibility lives.

Specifically, **sensitivity analysis on weighting choices is mandatory**, not optional. Saltelli, Andres, Campolongo, Cariboni, Gatelli, Saisana and Tarantola (2008), in *Global Sensitivity Analysis: The Primer*, give the methods (Sobol indices, Morris screening) for quantifying how much the final ranking depends on the analyst's weighting choice. The architectural fix: at construction time, emit not one composite index but a *distribution* of composite indices under perturbed weights, and report rank stability.

### 5.5 Sensitivity analysis on construction choices

Every construction decision is a hidden hyperparameter. The defensible pipeline emits not only the chosen construction but also a small grid of alternatives, and exposes downstream rank/score stability as a quality metric. This is the spirit of Saltelli's "multimodeling" principle and of Steegen, Tuerlinckx, Gelman and Vanpaemel's (2016) *multiverse analysis*, which advocates running the analysis under all defensible combinations of forking-paths choices and reporting the distribution of outcomes.

---

## 6. Task 3.4 — Integrate Data

Integrate Data covers *"methods whereby information is combined from multiple tables or records to create new records or values"* (Chapman et al., 2000, p. 29). This is the most error-rich generic task; almost every famous pipeline disaster lives here.

### 6.1 Join strategies

Joins are characterized by cardinality and key type:

- **1:1 joins** (e.g., a record per parcel joined to a record per parcel by parcel ID) are safest. Validate that the join key is unique on both sides; assert post-join row count equals pre-join row count.
- **1:N joins** (one parcel to many sensor readings) expand the dataset. Decide whether the downstream model wants the long form or an aggregation back to parcel level.
- **N:N joins** are almost always a bug. They produce a Cartesian explosion and double-count. If you genuinely need an N:N relationship, materialize it as an association table.
- **Fuzzy joins** (string similarity, geographic proximity) require an explicit threshold and a tie-breaking rule. The threshold is a hyperparameter; sensitivity should be tested.
- **Spatial joins** combine geometries by topological relationship (intersects, contains, within, nearest). The trap: a polygon-in-polygon "contains" join with an open boundary will exclude points exactly on the boundary; closed boundary will include them; many tools default differently. Test edge cases explicitly.

### 6.2 Schema alignment

Before any join, the analyst must reconcile:

- **Naming differences** (`pop_2020` vs. `population_2020`): trivial but pervasive.
- **Type differences** (string `"01234"` zip code vs. integer `1234`).
- **Cardinality differences** (one row per parcel-year vs. one row per parcel).
- **Granularity differences** (per-block vs. per-tract — see §6.6).

### 6.3 Entity resolution and record linkage

When records refer to the same real-world entity but lack a shared identifier, entity resolution is required. The foundational framework is **Fellegi and Sunter (1969)**, *A Theory for Record Linkage*, which formalizes linkage as a probabilistic classification problem: for each candidate record pair, compute agreement and disagreement vectors across fields, weight them by per-field match/non-match probabilities, and decide based on a likelihood ratio. Despite half a century of ML development, the Fellegi–Sunter model is the foundation of most modern probabilistic-matching systems, including the open-source Splink library (Linacre, Kennedy and Tilling, 2022).

Christen's (2012) *Data Matching: Concepts and Techniques for Record Linkage, Entity Resolution, and Duplicate Detection* is the modern textbook treatment. Binette and Steorts (2022), in *(Almost) all of entity resolution*, give the current research overview.

### 6.4 Unit and locale harmonization

Pipeline disasters with unit mismatches are common enough to have a famous example: the 1999 NASA Mars Climate Orbiter was lost because one team used metric units and another used imperial. For data pipelines the architectural fix is to **store units in the schema** (e.g., as column metadata, or as a column suffix convention `temperature_C`, `area_m2`) and to convert at ingest, never at consumption.

### 6.5 Temporal alignment

When integrating time series from multiple sources, the analyst must reconcile:

- **Sampling rates** (hourly vs. daily). Downsampling requires choosing an aggregation; upsampling requires choosing an interpolation.
- **Time zones**. Always store in UTC; convert to local only at presentation. Log the source time zone in the data dictionary.
- **Calendar conventions** (week start, fiscal year, daylight saving).
- **Reporting lag**. If source A is real-time and source B has a 30-day reporting lag, joining "as of today" silently mixes epochs.

### 6.6 CRS harmonization and resolution matching (the 2× rule)

For raster + raster or raster + vector integration, two constraints govern:

- **CRS harmonization**: reproject all layers to a single canonical CRS before integration. For city-scale work, the locally-appropriate UTM zone or the national grid (e.g., ETRS89 / ETRS-LAEA for Europe; EPSG:25831 for Catalonia) is usually correct; WGS84 is only correct for display.
- **The 2× resolution rule**: when integrating layers at different resolutions, the output cannot validly claim to be at the finer resolution. The defensible rule is to integrate at no finer than 2× the coarsest input resolution (i.e., if the coarsest layer is 100 m, integration outputs are valid only at ≥200 m cells). This is folkloric in the GIS community and codified in environmental-modeling practice; it derives from sampling theory's Nyquist–Shannon bound applied to spatial sampling (Atkinson and Curran, 1997). Skipping this rule produces visually-plausible but methodologically false fine-grained outputs — one of the major findings of the project's own deep-research integrity review.

### 6.7 Conflict resolution policies

When two sources disagree on the same fact, the pipeline needs a **conflict resolution policy**, declared in advance:

- **Trust hierarchy**: source A overrides source B (e.g., the official cadastre overrides OpenStreetMap).
- **Recency**: most recent record wins.
- **Voting / consensus**: across N sources, the modal value wins.
- **Flag and defer**: produce a record with `conflict=True` and let the modeler decide.

The architectural rule: **never resolve conflicts silently**. The conflict-resolution rule lives in the pipeline code; the conflicts themselves live in a `conflicts/` audit table.

---

## 7. Task 3.5 — Format Data

Format Data covers *"primarily syntactic modifications made to the data that do not change its meaning"* — reorderings, retypings, file-format conversions to suit the modeling tool (Chapman et al., 2000, p. 29). In the 2000 standard this was a minor task; in modern pipeline practice it is consequential because **format choice determines reproducibility, performance, and interoperability**.

### 7.1 Target format selection

Format choice is governed by access pattern, volume, schema stability, and downstream tooling:

- **CSV** is universal but lossy (no types, no schema, ambiguous encoding). Acceptable for archival of small reference tables; *not* acceptable as a pipeline-internal format.
- **JSON / JSON Lines** is good for semi-structured nested data; verbose at scale.
- **Apache Parquet** is the modern default for tabular analytical workloads: columnar, typed, compressed, schema-embedded, and supported by every major engine (Spark, DuckDB, Arrow, Polars, pandas) (Vohra, 2016).
- **Apache Avro** is row-oriented and the default for streaming/Kafka workloads; better than Parquet for record-at-a-time writes.
- **HDF5 / NetCDF** are the scientific-data formats for multidimensional arrays.
- **Zarr** is the cloud-native successor to HDF5/NetCDF, optimized for chunked parallel reads from object storage (Miles et al., 2020).
- **GeoPackage** (OGC standard) is the modern replacement for the Shapefile for vector geospatial data. It supports multiple layers, proper types, long field names, and Unicode — all areas where Shapefile is broken.
- **GeoParquet** (OGC standard, v1.1) extends Parquet with geometry types and CRS metadata for cloud-native vector workflows. As of Parquet 2.11 (released March 2025), geometry and geography types are native in the Parquet specification itself.

The architect's rule of thumb: **Parquet/GeoParquet for analytical tabular**, **Zarr for analytical arrays**, **GeoPackage for vector that must round-trip through desktop GIS**, **CSV only for human-readable exports**.

### 7.2 Columnar vs. row

Columnar storage (Parquet, ORC, Arrow) wins when the access pattern is "select a few columns from many rows" — the analytical default. Row-oriented storage (Avro, classic RDBMSes' row-store mode) wins when the access pattern is "read or write entire records one at a time" — the OLTP default. Pipeline outputs are almost always analytical; pipeline ingests are often row-oriented streams. The transformation between them is itself a Phase-3 task.

### 7.3 Naming conventions and metadata

Names are interfaces. A column called `pop` is a future bug. The defensible convention:

- `snake_case`, no spaces, no special characters.
- Unit suffix: `area_m2`, `temperature_c`, `population_count`.
- Source prefix when ambiguous: `census_pop_2020`, `osm_pop_2020`.
- Geometry column: `geom` or `geometry`, never both in the same project.

Metadata should be **embedded in the file**, not in a sidecar that can be lost:

- Parquet/GeoParquet: schema and column statistics are in the file footer; geometry CRS is in the GeoParquet metadata block.
- GeoPackage: stores CRS, extents, and table metadata in SQLite tables.
- NetCDF/Zarr: CF Conventions (Eaton et al., 2024) define a controlled vocabulary for attribute metadata.

### 7.4 FAIR compliance

Wilkinson et al. (2016), in *The FAIR Guiding Principles for Scientific Data Management and Stewardship* (*Scientific Data*), established the FAIR principles: **Findable, Accessible, Interoperable, Reusable**. Phase-3 outputs are FAIR-compliant when:

- **Findable**: assigned a persistent identifier (DOI for archived outputs; URN/UUID for internal pipeline artifacts) and rich metadata.
- **Accessible**: retrievable by their identifier via a standard protocol (HTTPS, S3).
- **Interoperable**: use standard formats and vocabularies.
- **Reusable**: licensed, provenance-documented, and accompanied by usage guidance.

For seminar deliverables this is operationalized as: every Phase-3 artifact ships with a **datasheet** (Gebru et al., 2021) or **data card** (Pushkarna, Zaldivar and Kjartansson, 2022) covering motivation, composition, collection process, preprocessing, uses, distribution and maintenance.

### 7.5 Tidy data principles

Wickham (2014), *Tidy Data* (*Journal of Statistical Software*), articulates three rules for the canonical tabular layout: each variable is a column; each observation is a row; each type of observational unit is a table. Tidy data is not always the storage-optimal layout, but it is almost always the *modeling-ready* layout, which is what Phase 3 must produce. Most format-stage work is reshaping (pivot, melt, normalize/denormalize) toward tidy form.

---

## 8. The modern pipeline-engineering view

CRISP-DM was written in 2000 for desktop tools and small datasets. The five Phase-3 tasks survive intact, but the **engineering substrate** has changed completely.

### 8.1 Idempotency

A pipeline step is **idempotent** if running it twice on the same input produces the same output. Without idempotency, retries are unsafe and reproducibility is lost. Practical rules: writes overwrite or append-with-upsert, never append-blindly; sources of randomness (sampling, imputation) take an explicit seed; timestamps are passed in, not generated inside the step.

### 8.2 Lineage and provenance

**Data lineage** is the record of which inputs produced which outputs through which transformations. Polyzotis, Roy, Whang and Zinkevich (2018), in *Data Lifecycle Challenges in Production Machine Learning* (*SIGMOD Record*), argue that lineage is the missing infrastructure that turns ad-hoc ML projects into reliable production systems. Modern tools (OpenLineage, Dagster's asset graph, dbt's compiled DAG, MLflow tracking, Pachyderm) capture lineage automatically. The pipeline-architect rule: **if you can't answer 'where did this value come from?' in one query, your lineage is broken**.

### 8.3 DAG orchestration

The transformation graph is a directed acyclic graph (DAG) of steps. The current canonical orchestrators are:

- **Apache Airflow**: the incumbent. Task-centric, large ecosystem (80+ providers), mature, verbose.
- **Dagster**: asset-centric (models data products, not just tasks), strong lineage and observability story, smaller ecosystem.
- **Prefect**: Python-function-decorator UX, dynamic graphs, hybrid execution.

For seminar pipelines, Dagster's asset model is the most pedagogically aligned because it forces students to think in terms of *data products* (the assets) rather than *scripts that happen to run* (the tasks).

### 8.4 Declarative transforms

**dbt** (Data Build Tool) is the de facto standard for in-warehouse transformations. The user writes SQL `SELECT` statements; dbt compiles them into a DAG, runs them in order, materializes results as tables/views, and emits a documentation site and lineage graph as artifacts. The pedagogical value of dbt is that it forces transformations to be **declarative and version-controlled**, with **tests as code** (uniqueness, not-null, referential integrity, custom assertions).

**Apache Beam** (Akidau et al., 2015, *The Dataflow Model*) is the equivalent abstraction for general-purpose batch + streaming compute: a unified programming model that runs on Spark, Flink, or Google Cloud Dataflow. Beam's contribution is treating batch as a special case of streaming, with watermarks and windowing as first-class primitives.

### 8.5 Data contracts

A **data contract** is an explicit, versioned agreement between a producer and a consumer of data: schema, semantics, freshness SLO, quality SLOs. In pipeline architecture, every Phase-3 output should ship with a contract that downstream Phase-4 (modeling) can rely on. Schema registries (Confluent, AWS Glue) and dbt model contracts operationalize this.

### 8.6 Schema-on-read vs. schema-on-write

- **Schema-on-write** (RDBMS, dbt + Parquet): the schema is enforced at the moment data is stored. Errors fail loudly at ingest. Better for trusted pipeline artifacts.
- **Schema-on-read** (raw data lake, JSON blobs): the schema is applied at query time. Errors fail at consumption. Better for exploratory ingestion of unknown sources.

The architectural pattern: **schema-on-read at the bronze layer, schema-on-write at silver and gold** (medallion architecture; Databricks community 2019, now industry-standard). Phase-3 outputs are gold-layer artifacts and must enforce schema on write.

---

## 9. Documenting decisions

Phase 3 is a chain of *design decisions*, not a chain of *executions*. The teacher's brief — "show how data is being processed and **why each processing decision was made**" — names this directly. The output is therefore not only the cleaned dataset; it is **a decision log**.

### 9.1 The decision-log artifact

The minimum schema for a Phase-3 decision log:

| Field | Description |
|---|---|
| `decision_id` | Stable identifier (e.g., `CLN-007`) |
| `task` | Select / Clean / Construct / Integrate / Format |
| `dataset` | Which dataset the decision applies to |
| `issue` | What was the problem |
| `decision` | What was done |
| `rationale` | Why this choice (with citation if applicable) |
| `alternatives_considered` | What else was on the table |
| `rows_affected` | Quantified impact |
| `reversible` | Yes / No / Partially |
| `reviewer` | Who signed off |
| `date` | When |

### 9.2 ADRs for data choices

Architecture Decision Records (Nygard, 2011) are the equivalent practice in software engineering. The same template (Context / Decision / Status / Consequences) applies cleanly to data choices: ADR-001 *"We will use ETRS89 / UTM31N (EPSG:25831) as the canonical CRS for the Barcelona pipeline because…"*.

### 9.3 Sensitivity-analysis logs

Where a Phase-3 decision is a hyperparameter (a threshold, a weight, a join tolerance), the log entry should reference the **sensitivity analysis** that justifies the chosen value, not merely assert it. This is the Saltelli et al. (2008) discipline applied to data preparation.

---

## 10. Anti-patterns

In order of severity for graduate-seminar pipelines:

1. **Silent dropping of rows** without a logged reason and without a `rejected/` partition. The reviewer cannot reconstruct what was lost.
2. **Irreversible cleaning** that overwrites the source. Always write cleaned outputs to a new artifact; never destroy the source.
3. **Double-counting via bad joins**. Any join that increases the row count without an explicit 1:N expectation is a bug until proven otherwise.
4. **Scale-mixing across resolutions**. Joining a 30 m raster to a 1 m vector and publishing the result as 1 m is the cardinal sin of spatial pipelines.
5. **Hidden coupling between cleaning and downstream model**. The cleaning rule that "removes outliers >3σ" leaks the test-set distribution into training if fit on the full data.
6. **CRS confusion**: a layer in WGS84 overlaid on a layer in a UTM zone "looks fine" in QGIS because of on-the-fly reprojection, but the integration is silently wrong.
7. **`fillna(mean)` without justifying the MCAR assumption**.
8. **Storing units in column names but not converting at ingest** — `temp_c` and `temp_f` co-existing in different rows of the same column.
9. **Shapefile as the canonical output format** (truncated field names, no Unicode, no CRS in the geometry, multiple sidecar files that can drift).
10. **Imputing before splitting** — leakage of test-set statistics into training.
11. **No data contract** between Phase 3 output and Phase 4 input.
12. **Hand-written `pandas` script with no DAG orchestrator** — passes for an exploration, fails as a pipeline.

---

## 11. Worked example — the five tasks applied to a city-scale spatial pipeline (Barcelona mycorrhizal)

The live test case is a city-scale pipeline that produces a barrier-reduction priority map for urban mycorrhizal fungi in Barcelona. Phase 3 instantiates as follows:

**3.1 Select.** Inputs include the Barcelona municipal tree inventory (Open Data BCN), CORINE land-cover, OSM impervious-surface polygons, soil-property rasters (LUCAS or ESDAC), and a research-derived list of mycorrhizal-host tree species. Selection rules: keep only species with confirmed mycorrhizal associations per the global FungalRoot database (Soudzilovskaia et al., 2020); keep only land-cover classes plausibly hosting fungal connectivity; clip to the Barcelona administrative boundary (current epoch). Rationale logged per source. Rejected records written to `rejected/` with reason codes (`not_mycorrhizal_host`, `outside_boundary`, etc.).

**3.2 Clean.** Tree inventory: type-coerce planting dates, normalize species names to a controlled taxonomy (GBIF backbone), flag duplicates by `(species, coords)` within 1 m. Geometry validation on all vector layers with `ST_MakeValid`. CRS validation: cast all to ETRS89 / UTM31N (EPSG:25831). Missing soil-property cells: classify mechanism (likely MAR — missingness correlates with land cover) and use predictive k-NN imputation with a sensitivity analysis comparing to no-imputation. Outlier handling: flag, do not drop. Cleaning report emitted as Markdown + JSON.

**3.3 Construct.** Derived attributes: per-cell mycorrhizal-host density (count and basal area), per-cell impervious fraction (zonal mean over the OSM layer), per-cell soil suitability (composite of pH, organic carbon, texture). Composite priority index from these inputs with explicit weights, documented as ADR-003, with Sobol sensitivity analysis on the weights producing a rank-stability score.

**3.4 Integrate.** All inputs are reprojected to EPSG:25831 and resampled to a common 50 m grid (the coarsest input is the soil raster at ~25 m; the 2× rule sets 50 m as the integration scale; finer downstream products would be methodologically unsupported). Vector layers are rasterized to the same grid. Conflict policy: where two sources disagree on tree presence, the municipal inventory wins; OSM is a fallback. Conflicts logged to `conflicts/`.

**3.5 Format.** Final artifact written as **GeoParquet** for analytical use (cloud-native, queryable from DuckDB/Sedona), with a parallel **GeoPackage** export for desktop-GIS round-tripping. Naming: `barrier_priority_v1_50m.parquet`, columns suffixed with units. Metadata: GeoParquet metadata block carries CRS; a sidecar `datasheet.md` (per Gebru et al., 2021) carries motivation, composition, collection, preprocessing, uses, distribution, maintenance. DOI minted on Zenodo at publication.

The full Phase-3 output is the GeoParquet artifact + the GeoPackage mirror + the datasheet + the decision log + the sensitivity-analysis log. Together they constitute the **data product** that Phase 4 (modeling) consumes.

---

## 12. Handoff to Phase 4

Phase 4 (Modeling) cannot begin until the Phase-3 output meets a **data contract** with the modeling step. The contract must specify:

1. **Schema**: column names, types, units, allowed values, geometry CRS.
2. **Freshness**: when was this produced, what is its valid-from / valid-until.
3. **Quality SLOs**: maximum missingness per column, geometry validity rate, duplicate rate.
4. **Lineage pointer**: the DAG and decision-log references that produced this artifact.
5. **Sensitivity**: known instability of derived attributes under construction-choice perturbation.
6. **Reproducibility**: a one-command rebuild from raw inputs (a `make rebuild` or `dagster materialize`).

If any of these is missing, the project is not ready for Phase 4. The defensible architecture treats this contract as a CI gate: a pull request cannot mark a Phase-3 artifact as "ready for modeling" until the contract checks pass.

---

## References

Aggarwal, C. C. (2017). *Outlier Analysis* (2nd ed.). Springer.

Akidau, T., Bradshaw, R., Chambers, C., Chernyak, S., Fernández-Moctezuma, R. J., Lax, R., McVeety, S., Mills, D., Perry, F., Schmidt, E., & Whittle, S. (2015). The Dataflow Model: A practical approach to balancing correctness, latency, and cost in massive-scale, unbounded, out-of-order data processing. *Proceedings of the VLDB Endowment*, 8(12), 1792–1803.

Atkinson, P. M., & Curran, P. J. (1997). Choosing an appropriate spatial resolution for remote sensing investigations. *Photogrammetric Engineering and Remote Sensing*, 63(12), 1345–1351.

Binette, O., & Steorts, R. C. (2022). (Almost) all of entity resolution. *Science Advances*, 8(12), eabi8021.

Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C., & Wirth, R. (2000). *CRISP-DM 1.0: Step-by-step data mining guide*. SPSS Inc.

Christen, P. (2012). *Data Matching: Concepts and Techniques for Record Linkage, Entity Resolution, and Duplicate Detection*. Springer.

Chu, X., Ilyas, I. F., Krishnan, S., & Wang, J. (2016). Data Cleaning: Overview and Emerging Challenges. *Proceedings of the 2016 ACM SIGMOD International Conference on Management of Data*, 2201–2206.

Cochran, W. G. (1977). *Sampling Techniques* (3rd ed.). Wiley.

Dasu, T., & Johnson, T. (2003). *Exploratory Data Mining and Data Cleaning*. Wiley.

Dodds, L. (2020). Do data scientists spend 80% of their time cleaning data? Turns out, no? *Lost Boy*. https://blog.ldodds.com/2020/01/31/

Eaton, B., Gregory, J., Drach, B., Taylor, K., Hankin, S., et al. (2024). *NetCDF Climate and Forecast (CF) Metadata Conventions*, v1.11.

Fellegi, I. P., & Sunter, A. B. (1969). A theory for record linkage. *Journal of the American Statistical Association*, 64(328), 1183–1210.

Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., & Crawford, K. (2021). Datasheets for datasets. *Communications of the ACM*, 64(12), 86–92.

Herring, J. R. (Ed.). (2011). *OpenGIS Implementation Standard for Geographic Information — Simple Feature Access — Part 1: Common Architecture*. Open Geospatial Consortium.

Ilyas, I. F., & Chu, X. (2019). *Data Cleaning*. ACM Books / Morgan & Claypool.

Kandel, S., Paepcke, A., Hellerstein, J., & Heer, J. (2011). Wrangler: Interactive Visual Specification of Data Transformation Scripts. *Proceedings of the SIGCHI Conference on Human Factors in Computing Systems*, 3363–3372.

Kapoor, S., & Narayanan, A. (2023). Leakage and the reproducibility crisis in machine-learning-based science. *Patterns*, 4(9), 100804.

Krishnan, S., Wang, J., Wu, E., Franklin, M. J., & Goldberg, K. (2016). ActiveClean: Interactive Data Cleaning For Statistical Modeling. *Proceedings of the VLDB Endowment*, 9(12), 948–959.

Kuhn, M., & Johnson, K. (2019). *Feature Engineering and Selection: A Practical Approach for Predictive Models*. Chapman & Hall/CRC.

Linacre, R., Kennedy, P., & Tilling, K. (2022). Splink: Free software for probabilistic record linkage at scale. *Journal of Open Source Software*, 7(80), 4324.

Little, R. J. A., & Rubin, D. B. (2019). *Statistical Analysis with Missing Data* (3rd ed.). Wiley.

Martínez-Plumed, F., Contreras-Ochando, L., Ferri, C., Hernández-Orallo, J., Kull, M., Lachiche, N., Ramírez-Quintana, M. J., & Flach, P. (2021). CRISP-DM Twenty Years Later: From Data Mining Processes to Data Science Trajectories. *IEEE Transactions on Knowledge and Data Engineering*, 33(8), 3048–3061.

Miles, A., Kirkham, J., Durant, M., Bourbeau, J., Onalan, T., Hamman, J., et al. (2020). *Zarr: A Format for the Storage of Chunked, Compressed, N-dimensional Arrays*. Zenodo.

Nardo, M., Saisana, M., Saltelli, A., Tarantola, S., Hoffman, A., & Giovannini, E. (2008). *Handbook on Constructing Composite Indicators: Methodology and User Guide*. OECD / JRC.

Nygard, M. (2011). *Documenting Architecture Decisions*. CognitiveConnect.

Polyzotis, N., Roy, S., Whang, S. E., & Zinkevich, M. (2018). Data Lifecycle Challenges in Production Machine Learning: A Survey. *ACM SIGMOD Record*, 47(2), 17–28.

Press, G. (2016, March 23). Cleaning Big Data: Most time-consuming, least enjoyable data science task, survey says. *Forbes*.

Pushkarna, M., Zaldivar, A., & Kjartansson, O. (2022). Data Cards: Purposeful and Transparent Dataset Documentation for Responsible AI. *Proceedings of the 2022 ACM Conference on Fairness, Accountability, and Transparency*, 1776–1826.

Rahm, E., & Do, H. H. (2000). Data Cleaning: Problems and Current Approaches. *IEEE Data Engineering Bulletin*, 23(4), 3–13.

Ramsey, P. (2008, August). PostGIS in Action. *OSGeo Journal*.

Rubin, D. B. (1976). Inference and missing data. *Biometrika*, 63(3), 581–592.

Saltelli, A., Ratto, M., Andres, T., Campolongo, F., Cariboni, J., Gatelli, D., Saisana, M., & Tarantola, S. (2008). *Global Sensitivity Analysis: The Primer*. Wiley.

Schröer, C., Kruse, F., & Gómez, J. M. (2021). A Systematic Literature Review on Applying CRISP-DM Process Model. *Procedia Computer Science*, 181, 526–534.

Sculley, D., Holt, G., Golovin, D., Davydov, E., Phillips, T., Ebner, D., Chaudhary, V., Young, M., Crespo, J.-F., & Dennison, D. (2015). Hidden Technical Debt in Machine Learning Systems. *Advances in Neural Information Processing Systems*, 28, 2503–2511.

Soudzilovskaia, N. A., Vaessen, S., Barcelo, M., He, J., Rahimlou, S., Abarenkov, K., et al. (2020). FungalRoot: global online database of plant mycorrhizal associations. *New Phytologist*, 227(3), 955–966.

Steegen, S., Tuerlinckx, F., Gelman, A., & Vanpaemel, W. (2016). Increasing transparency through a multiverse analysis. *Perspectives on Psychological Science*, 11(5), 702–712.

Tukey, J. W. (1977). *Exploratory Data Analysis*. Addison-Wesley.

Van Buuren, S. (2018). *Flexible Imputation of Missing Data* (2nd ed.). Chapman & Hall/CRC.

Vohra, D. (2016). Apache Parquet. In *Practical Hadoop Ecosystem* (pp. 325–335). Apress.

Wang, J.-F., Stein, A., Gao, B.-B., & Ge, Y. (2012). A review of spatial sampling. *Spatial Statistics*, 2, 1–14.

Wickham, H. (2014). Tidy Data. *Journal of Statistical Software*, 59(10), 1–23.

Wilkinson, M. D., Dumontier, M., Aalbersberg, I. J., Appleton, G., Axton, M., Baak, A., et al. (2016). The FAIR Guiding Principles for scientific data management and stewardship. *Scientific Data*, 3, 160018.

Woodie, A. (2020, July 6). Data Prep Still Dominates Data Scientists' Time, Survey Finds. *BigDATAwire*.
