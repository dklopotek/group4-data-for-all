# Data Quality Audit — Ajuntament Barcelona Tree Inventory

> Honest assessment of fitness for our brief based on profiling
> (`notebooks/01-data-profiling.ipynb`, executed against the Open Data
> BCN snapshot downloaded 2026-05-01). Numbers below are real, not
> placeholders.

---

## Dataset under audit

- **Dataset:** Ajuntament BCN tree inventory (Arbrat Viari + Arbrat Zona, combined)
- **Profiling notebook:** `notebooks/01-data-profiling.ipynb`
- **Snapshot vintage:** Primary current resource on Open Data BCN, last published 2024-11-12 (with 2026-Q1 quarterly archive available; we use the primary current as our working reference)
- **Records:** 145,478 street trees + 43,612 park trees = **189,090 combined**
- **Unique species:** 381
- **Spatial coverage:** lat 41.345 → 41.468 N, lon 2.089 → 2.225 E (within Barcelona municipal boundary)
- **Audit performed by:** [name]
- **Date:** 2026-05-01

---

## Gaps

### Temporal gaps

The published file represents inventory state at snapshot time. There is
no per-event timeline of plantings or removals.

- **Planting date is missing for ~81% of records** (153,176 of 189,090).
  This means we cannot reconstruct planting cohorts, cannot estimate tree
  age at population scale, and cannot do reliable change-detection from
  this dataset alone. Implication: all temporal claims must be made by
  comparing two snapshots, not by reading planting dates.
- For the ~19% of records with parseable dates, the range spans 0013-04-22
  to 2026-09-30 — both extremes are anomalies (typo at the lower end,
  forward-dated planned plantings at the upper end; counts in anomaly
  table below).

### Spatial gaps

- **No coordinate is outside the Barcelona municipal bounding box** —
  data is geographically clean.
- **All 10 districts have substantial counts** (Sant Martí 36,119 →
  Ciutat Vella 6,773). Ciutat Vella's lower count reflects the dense
  historical fabric and is not a data gap. **No district is silently
  excluded** — satisfies seminar success-criterion 2.
- **6 records have a missing or invalid district code**, which we will
  drop or hand-correct in Session 3.
- Private gardens, courtyards, and manzana-interior plantings are
  out-of-scope for this dataset (it is a public-realm inventory). This
  was anticipated in the datasheet's Section 8 and remains true.

### Field-level gaps

| Field | % missing | Pattern of missingness | Implication |
|---|---|---|---|
| `catalogacio` | 99.51% | Effectively absent — only ~900 of 189k records carry a value | Drop from analysis. Field is not load-bearing for our barrier model. |
| `tipus_aigua` (water-source type) | 94.03% | Mostly empty, populated only for some recently-installed park irrigation | Not used in our pipeline. Document as "available for the irrigation-aware subset only." |
| `data_plantacio` (planting date) | 81.01% | Heritage-tree records pre-dating systematic recording lack planting dates | Snapshot-state analysis only; no temporal cohort analysis. |
| `espai_verd` | 60.40% | Park-name field; absent for street trees outside named green spaces | Use as a categorical filter, not a join key. |
| `cat_nom_catala` | 2.17% | Catalan common name | Cosmetic only — not used in pipeline. |
| `cat_nom_castella` | 1.96% | Castilian common name | Cosmetic only. |
| `tipus_reg` (irrigation type) | 0.03% | Almost complete | Usable. Categories: `GOTEIG`, `GOTEIG AVARIAT`, `ASPERSIÓ`, `SENSE INFORMAR`, etc. |
| `categoria_arbrat` | 0.02% | Almost complete | Usable. Categories: `EXEMPLAR`, `PRIMERA`, `SEGONA`, `TERCERA`. |
| `nom_barri` / `codi_barri` | 0.01% | Almost complete | Usable as a within-district aggregation level. |

---

## Anomalies found during profiling

| # | Anomaly | Count | Diagnosis | Action taken |
|---|---|---|---|---|
| 1 | Coordinates outside BCN bounding box | 0 | None — geographic cleanliness is high | None needed |
| 2 | Missing or invalid district code | 6 | Likely data-entry oversight; small enough to inspect manually | Flag for Session 3 cleanup; drop from district-aggregated analyses |
| 3 | Duplicate `codi` within snapshot | 0 | None — unique IDs are clean | None needed |
| 4 | `cat_especie_id <= 0` | 0 | None — species ID space is clean | None needed |
| 5 | Planting date in the future | 28 | Likely planned plantings entered into inventory pre-actually-planted (consistent with quarterly publication and ongoing rollout) | Treat dates > today as null in temporal analyses |
| 6 | Planting date pre-1900 | 8 | Almost certainly typos (e.g. `0013-04-22` is plausibly `2013-04-22` with a missing digit) | Treat dates < 1900-01-01 as null in temporal analyses |
| 7 | Genus-only species names | 25 | All `Washingtonia sp` — a genuine identification gap for a single genus | Drop these from FungalRoot species-level join; document as 0.01% dropout |

---

## Bias check

- **Selection bias:** Inventory covers *municipally-managed* public-realm
  trees only. Private gardens, courtyards, and manzana-interior plantings
  are absent. Direction: undercounts neighborhoods with high private-land
  vegetation. Mitigation: Sentinel-2 NDVI as an auxiliary "all vegetation"
  signal to flag where private-realm contributions matter.

- **Measurement bias:** Field surveys done by trained operators, GPS
  positioning ~submeter to a few meters in dense urban canyons due to
  signal multipath. Position precision is fine for 400m grid aggregation;
  identification precision (species-level) is verified high — only 25
  records (0.01%) are genus-only, all *Washingtonia sp*.

- **Coverage bias:** No district is silently empty; coverage is even
  enough that the per-district sub-claim is defensible. Sant Martí,
  Sants-Montjuïc, Eixample, and Sant Andreu carry 50%+ of the inventory
  by count, reflecting district size and street-network density rather
  than inventory bias.

- **Temporal drift / non-stationarity:** The Eixos Verds and Superilla
  rollouts during 2015–2024 actively change the public-realm tree
  population. Our snapshot is a single point in time; we acknowledge
  this and analyse snapshot state, not change. If we want to make any
  claim about "where new plantings have happened," we'd need to compare
  two snapshots.

- **Label bias:** N/A — this dataset has no labels in the ML sense.

---

## Fitness for OUR brief

Each sub-question from `problem-brief.md`:

- **Sub-question 1:** *Per zone, what mycorrhizal type does the host
  tree composition lead us to expect (AM / EM / mixed)?*
  - **Answer:** **YES — fully supported.**
  - **Why:** Species-level taxonomy is consistent (only 0.01% genus-only).
    All ~381 unique species can be joined against FungalRoot v2.0 at
    species level; the 25 *Washingtonia sp* records would either fall
    back to genus-level lookup or be dropped (they are 0.01% of the
    population). Top species composition empirically confirms AM-host
    dominance (top 6 species are all AM hosts) with a meaningful EM
    subset (*Pinus pinea* 4,287 + *Pinus halepensis* 2,549 +
    *Quercus ilex* 2,307 = ~9k EM-host trees).

- **Sub-question 2:** *Per zone, what is the sealed-surface fraction?*
  - **Answer:** Yes — but answered by Urban Atlas, not by this dataset.
  - **Why:** Tree inventory does not contain sealed-surface information;
    Urban Atlas (auxiliary, 14/14 score) provides it at 10m. This audit
    confirms tree-inventory coverage is dense enough that sealed-surface
    can be intersected at 400m grid resolution without coverage holes.

- **Sub-question 5:** *Per zone, is there host–mycorrhizal mismatch?*
  - **Answer:** **YES — fully supported.**
  - **Why:** With 381 unique species, the host-composition layer is
    rich enough to detect zones where (a) host trees expect a specific
    mycorrhizal type and (b) the spatial vicinity has no recent
    citizen-science fungal confirmation. The sub-question presumes
    GBIF integration (covered by the GBIF datasheet and audit-time
    spot-check below).

- **Sub-question 6:** *Combined zone ranking + intervention type.*
  - **Answer:** YES — supported.
  - **Why:** Per-tree precision allows stable per-400m-cell aggregation;
    no per-cell zero-tree dropouts at the 400m scale (the smallest
    district by tree count is Ciutat Vella at 6,773 trees / ~4 km², or
    ~600 trees / 400m cell). The minimum density gives a defensible
    sample at every cell.

---

## GBIF spot-check (supplemental)

Run during this audit, answers the v2 brief's open question on GBIF
record availability:

- **GBIF Kingdom Fungi, Barcelona bbox (2.052–2.230 E, 41.310–41.475 N),
  eventDate 2015-01-01 to 2024-12-31, hasCoordinate=true: **1,023
  records.**
  - HUMAN_OBSERVATION (citizen science): 1,006 (98.3%)
  - PRESERVED_SPECIMEN (museum): 16 (1.6%)
  - MATERIAL_SAMPLE (DNA-based): 0 (0.0%)
- **Verdict on the v1 brief's open question** ("above 500 or below 100"):
  comfortably *above* 500. Sample size is workable — but the basis-of-record
  breakdown confirms the citizen-science dominance and the absence of any
  DNA-based ground truth. AM-blindness limit stands.

## GlobalAMFungi spot-check (supplemental)

Attempted via the public web portal (`globalamfungi.com`) and the
*New Phytologist* paper page; both blocked by JS-only rendering and
publisher paywall respectively. **Iberian-sample density was not
verifiable from this profiling session.** Treat as INVESTIGATE pending
manual portal access. The v2 brief retains GlobalAMFungi as a
provisional INVESTIGATE source.

---

## Decisions

- **What we WILL use this dataset for:**
  - Per-zone host-species composition input to the expected-mycorrhizal-type
    layer (sub-question 1) and the host-mycorrhizal-mismatch sub-score
    (sub-question 5)
  - Per-district / per-barri summary statistics for sanity checks
  - Spatial framework for 400m grid aggregation

- **What we will NOT use this dataset for:**
  1. **Tree-health, vitality, or stress claims.** No condition data exists.
  2. **Temporal cohort analysis or per-period change detection** without
     external comparison snapshots — planting-date completeness is too
     low.
  3. **Claims about private-realm or non-public-managed greenery.**

- **What additional source(s) we'd need to fill the gaps:**
  - Sentinel-2 NDVI (already adopted) for total-vegetation cross-check and
    private-realm context
  - Comparison against an earlier snapshot if change-detection becomes
    necessary in Session 3+
  - GlobalAMFungi (pending manual verification) for any AM-fungal
    DNA-confirmed reference

---

## Implications for the brief

- The v1 brief's open question "Does Ajuntament tree data carry
  consistent species-level taxonomy, or is genus the realistic join key
  against FungalRoot?" is **resolved YES — species-level taxonomy is
  consistent.** Update `problem-brief-v2.md` to reflect.

- The v1 brief's open question "Actual GBIF fungal record count for the
  Barcelona municipal boundary, 2015–2024 — above 500, or below 100?"
  is **resolved at ~1,023 records (above 500)**. The AM-blindness
  concern is empirically confirmed via basisOfRecord breakdown
  (98% citizen-sci, 0% DNA).

- The GlobalAMFungi check is pending manual portal verification.

---

## Per-team-member contributions

*Each team member must write at least one paragraph in this file.*

### [Name 1]

### [Name 2]

### [Name 3]

### [Name 4]
