# Dataset Datasheet — Ajuntament de Barcelona Tree Inventory (Arbrat Viari + park-tree inventory)

> Primary dataset for the Mycorrhizal Barcelona project (Session 2,
> CRISP-DM Phase 2). Based on Gebru et al. 2021, "Datasheets for Datasets."

---

## 0. Quick reference

- **Dataset name:** Arbrat viari de la ciutat de Barcelona (street-tree inventory) + Arbrat de parcs i jardins (park-tree inventory) — combined as one logical dataset for our use
- **Version / vintage:** Quarterly snapshots; we use the snapshot closest to 2024-Q4 as the working reference, with the 2015-Q1 snapshot held aside for comparison if temporal-drift analysis is needed
- **Source URL:** `https://opendata-ajuntament.barcelona.cat/data/en/dataset/arbrat-viari` (street trees) and `https://opendata-ajuntament.barcelona.cat/data/en/dataset/arbrat-parcs` (park trees)
- **License:** CC-BY 4.0 per Open Data BCN portal terms (attribution required, redistribution and modification permitted)
- **Spatial coverage:** Full Barcelona municipal boundary (10 districts, ~73 barris)
- **Temporal coverage:** Quarterly snapshots from approximately 2015 onwards; some historical fields (planting date) extend earlier per tree
- **Native resolution (spatial / temporal):** Per-tree point coordinates at ~meter precision; temporal granularity is the publication quarter (the dataset reflects state at snapshot time, not continuous tree-by-tree change events)
- **Format:** CSV / GeoJSON / Shapefile / KML, downloadable per snapshot; CKAN API for programmatic access
- **Size:** Combined ~150,000–185,000 records depending on snapshot (street ~150k, parks ~30k); per snapshot ~30–60 MB CSV
- **Datasheet last updated:** 2026-05-01 by [name]

---

## 1. Motivation

- **Why was the dataset created?**
  Operational management of Barcelona's public arboreal asset — tree-care
  scheduling (pruning, treatment, replacement), public information
  (street-tree finder), urban planning support, and citizen reporting. The
  dataset is *not* an ecological survey; it is a municipal asset register
  with ecological *uses* downstream.

- **Who created the dataset (individuals, organizations)?**
  Ajuntament de Barcelona — Servei d'Arbrat (tree service), within the
  Direcció d'Espais Verds i Biodiversitat. Fieldwork is performed by
  municipal contractors with technical staff oversight.

- **Who funded the creation of the dataset?**
  Ajuntament municipal budget. The Open Data BCN portal that publishes the
  dataset is funded by the Ajuntament's Direcció de Serveis d'Innovació
  Digital.

- **For what tasks was the dataset originally intended?**
  Tree maintenance routing, tree-replacement scheduling, public-facing
  street-tree finder, citizen reporting of tree issues, and basic urban
  greenery statistics. Use for scientific analysis (urban ecology, canopy
  cover, biodiversity-host modelling) is downstream and the dataset was
  not specifically designed for it.

---

## 2. Composition

- **What does an instance represent?**
  A single tree at a single snapshot in time, with its location, species
  identification, and a small set of management metadata.

- **How many instances are there in total?**
  ~150,000 street trees + ~30,000 park trees per recent snapshot. Counts
  vary across snapshots due to plantings, removals, and re-surveys.

- **What features / fields does each instance have?**

| Field | Type | Description | Required? |
|---|---|---|---|
| `codi` / `id` | string / int | Unique tree identifier within snapshot | Yes |
| `latitud`, `longitud` | float | WGS-84 coordinates | Yes |
| `coord_x`, `coord_y` | float | ETRS89 / UTM 31N coordinates (alternate) | Yes |
| `nom_cientific` | string | Scientific species name (genus + epithet); may default to genus only for some records | Mostly |
| `nom_castella`, `nom_catala` | string | Common names | Mostly |
| `categoria_arbrat` | string | Tree category (street / park / other) | Yes |
| `tipus_element` | string | Type tag (live tree / removed / replacement / etc.) — varies by snapshot | Yes |
| `tronc_perimetre`, `tronc_diametre` | float / category | Trunk size measurement or category | Variable |
| `data_plantacio` | date | Planting date, when known | Variable, often missing |
| `adreca` / `address` | string | Nearest street address (street trees) | Yes for street, no for park |
| `parc_nom` | string | Park name (park trees) | Yes for park, no for street |
| `districte`, `barri` | string | Administrative district + neighborhood | Yes |

- **Are there labels or targets associated with each instance?**
  No. This is a record set, not a labelled training dataset. For our
  project, the *target* is derived (expected mycorrhizal type, computed
  from `nom_cientific` × FungalRoot lookup).

- **Is any information missing from instances?**
  - **Planting date:** missing for a substantial fraction (heritage trees
    pre-dating systematic recording).
  - **Species (vs genus only):** flagged as a v1-brief open question.
    Some records carry genus-only identification (e.g. *Platanus sp.*
    rather than *Platanus × hispanica*). Need to quantify in profiling.
  - **Health / vitality:** **not in the dataset.** This is the single
    biggest limit for our project. We can know a tree is *listed* but not
    whether it is healthy, dying, or merely retained as a stump.
  - **Root-system extent:** not recorded.

- **Are there relationships between individual instances?**
  Spatial clustering by street or park. Trees on the same street may share
  planting context (a single planting cohort) but this isn't explicitly
  encoded; we'd infer it from `data_plantacio` similarity.

- **Are there recommended data splits (train/val/test)?**
  N/A. Not an ML training dataset.

---

## 3. Collection process

- **How was the data acquired?**
  Direct field surveys by municipal contractors and Ajuntament Servei
  d'Arbrat staff, supplemented by maintenance records (when a tree is
  pruned, the visit confirms its existence and condition). Coordinates are
  recorded via field GPS; species identification is by trained operators.

- **What instruments / sensors / software were used?**
  Field GPS units (~submeter to a few meters precision in dense urban
  canyons due to multipath), tree-management database software (internal
  to the Servei). No remote-sensing instruments are used in the inventory
  itself.

- **Who was involved in the data collection process?**
  Ajuntament technical staff and contracted survey teams. Citizen reports
  of new or removed trees may feed corrections.

- **Over what time period was the data collected?**
  Continuous since the inventory's establishment; quarterly snapshots are
  published to Open Data BCN. The earliest snapshot we'd use is 2015-Q1.

- **What was the sampling strategy?**
  Deterministic — *every* municipally-managed tree on public streets and
  in public parks is recorded. This is *not* a sample; it is intended as
  a complete census of public-realm trees.

- **Is the sample representative of the larger population it claims to
  describe?**
  Of *publicly-managed* trees, yes — close to a complete census.
  Of *all trees in Barcelona*, no — private gardens, courtyards, and
  manzana-interior plantings are not included. For the Eixos Verds /
  Superilla decision context this is acceptable: the planning decision
  applies to public-realm interventions.

- **Were any ethical review processes conducted?**
  Not required (no personal data; tree records).

---

## 4. Preprocessing & cleaning

- **What preprocessing was done by the dataset creators?**
  Coordinate normalisation to WGS-84 + ETRS89, deduplication within
  snapshot, address standardisation against the BCN street register.
  Species name normalisation is best-effort and somewhat inconsistent
  across snapshots (this is what triggers the species-vs-genus open
  question).

- **Is the raw data also available?**
  No raw fieldwork sheets are published. The published snapshot is the
  cleaned record.

- **What preprocessing did WE do before adopting the dataset?**
  *(To be filled in during the profiling notebook — Cell 3.)* Planned:
  (i) merge street + park snapshots into one logical dataset; (ii)
  reproject to a single CRS (ETRS89 / UTM 31N for distance calculations);
  (iii) join `nom_cientific` against FungalRoot v2.0 — at species level
  where possible, falling back to genus-level lookup with a documented
  fallback flag; (iv) aggregate per 400m grid cell for the priority-map
  pipeline; (v) tag each tree with district + barri (already in source).

- **Where is the preprocessing software / code available?**
  `notebooks/01-data-profiling.ipynb` (this repo).

---

## 5. Uses

- **What tasks has the dataset been used for?**
  Operational tree management; published BCN canopy/biodiversity reports;
  peer-reviewed studies on urban-tree species composition and diversity
  (e.g. Padullés Cubino et al. work on European urban trees, Catalan
  groups on Barcelona-specific canopy studies).

- **Is there a repository linking to papers / systems that use this
  dataset?**
  Not formally. The Open Data BCN portal lists some downstream uses;
  literature search at adoption time identifies further uses.

- **What other tasks could this dataset be used for?**
  Urban canopy modelling, climate-cooling estimation (with caveats),
  biodiversity-host inference (this project), species-distribution
  studies, carbon-stock approximation.

- **What tasks should this dataset NOT be used for?**

  1. **Inferring tree health, vitality, or stress.** The dataset records
     presence and identification, not condition. A listed tree may be
     dead, removed since the snapshot, or in serious decline.
  2. **Modelling private-property tree cover or neighborhood-scale
     biodiversity beyond the public realm.** Private gardens,
     courtyards, and manzana-interior plantings are absent.
  3. **Per-day or per-event temporal analysis of tree change.** The
     quarterly snapshot cadence cannot resolve sub-quarter events; use
     it for state at snapshot time, not for change tracking.

- **Are there any considerations about discrimination, bias, or harm
  that could result from use of this dataset?**
  Spatial bias toward areas with *municipally-managed* greenery — i.e.
  away from peripheral districts with high private-land vegetation, and
  away from informal/unrecorded plantings. Using this dataset alone to
  infer "biodiversity" of an area would systematically undercount
  private-realm contributions.

---

## 6. Distribution & licensing

- **Under what license is the dataset distributed?**
  Creative Commons Attribution 4.0 International (CC-BY 4.0) per the Open
  Data BCN portal default.

- **Are there any restrictions on use, redistribution, attribution, or
  modification?**
  Attribution required. Modification and redistribution permitted. No
  share-alike requirement.

- **What's the required attribution string?**
  > "© Ajuntament de Barcelona, Open Data BCN, CC-BY 4.0. Arbrat viari /
  > Arbrat de parcs (snapshot YYYY-Qn)."

- **Are there fees for access?**
  No.

- **Are there export controls or regulatory restrictions?**
  No. Public data.

---

## 7. Maintenance

- **Who supports / hosts / maintains the dataset?**
  Ajuntament de Barcelona — Direcció de Serveis d'Innovació Digital
  (publication / portal) + Servei d'Arbrat (data content). Open Data BCN
  staff for portal-level issues.

- **How can the maintainer be contacted?**
  Open Data BCN contact form on the portal; municipal Servei d'Arbrat for
  data-content questions (contact via Ajuntament citizen channel
  `010` / contact form).

- **Is there an erratum?**
  No public erratum; corrections appear in the next quarterly snapshot.

- **Will the dataset be updated?**
  Yes — quarterly publication cadence.

- **How often is the dataset updated?**
  Quarterly snapshots published to Open Data BCN.

- **Are older versions of the dataset still available?**
  Older snapshots remain accessible on the portal. Each is independently
  downloadable.

---

## 8. Limitations relative to OUR project

*The most important section for the seminar. How does this dataset's
character intersect with our problem brief?*

- **Resolution mismatch with our decision unit?**
  None. Per-tree point coordinates are far finer than the 400m Superilla
  grid. Aggregation upward is straightforward.

- **Geographic gaps that matter for us?**
  Private gardens and manzana-interior plantings are absent. For the
  Eixos Verds / Superilla decision context (public-realm interventions),
  this is acceptable. For any sub-claim about "neighborhood total
  greenery" we'd need to caveat that we describe the *public-managed*
  realm only. Sentinel-2 NDVI partly compensates by giving total
  vegetation signal regardless of management category.

- **Temporal gaps that matter for us?**
  Quarterly cadence is fine for a snapshot analysis. The Eixos Verds /
  Superilla rollout introduces real change during 2015–2024 — which is
  honest but means we should pick a single recent snapshot as the
  reference, not average across the window.

- **Biases that could distort our conclusions?**
  - Species-level taxonomy may be inconsistent (genus-only entries) —
    triggers a defined fallback in our FungalRoot join.
  - No tree-health information; our project must avoid claims that a
    listed tree is functioning ecologically. The
    *expected-mycorrhizal-type* layer is genuinely an *expectation*,
    not a confirmation.
  - Public-realm-only coverage as noted above.

- **What additional sources would compensate for these limits?**
  - Sentinel-2 NDVI sanity-checks the inventory against actual vegetation
    (catches recent removals or unrecorded plantings).
  - Urban Atlas land-use class differentiates dense-urban-no-green from
    private-garden zones.
  - Tree-health remains a true gap — no remote sensing reliably gives it
    at species precision.

- **Verdict for our project:**
  **PRIMARY** — load-bearing input for the host-side mycorrhizal-type
  expectation layer (sub-question 1) and the host-mycorrhizal-mismatch
  sub-score (sub-question 5). Without this dataset the project does not
  exist.
