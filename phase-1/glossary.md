# Terminology Glossary

Bilingual glossary: sponsor/planning domain terms and data-team technical terms, cross-referenced.

## Planning Domain → Technical

| Term | Meaning | Cross-reference |
|---|---|---|
| **Superilla (Superblock)** | Barcelona's urban-block aggregation programme. Combines 9 city blocks (~400m × 400m) into a pedestrian-priority zone with reduced car access. The primary delivery mechanism for green-infrastructure capital. | Equivalent to our **decision unit** (400m grid) |
| **Eixos Verds (Green Axes)** | Green corridors connecting Superilles, with dedicated planting, de-paving, and sustainable drainage budgets. | One of the four **intervention budget lines** |
| **Barri (Neighborhood)** | Barcelona's 73 administrative neighborhoods. Aggregation level for within-district analysis. | `nom_barri` / `codi_barri` fields in tree inventory |
| **Districte (District)** | Barcelona's 10 administrative districts. All 10 have substantial tree counts. | `district` field in tree inventory |
| **Arbrat Viari** | Street tree inventory (~145,000 records). | Primary dataset |
| **Arbrat Zona** | Park tree inventory (~44,000 records). | Primary dataset |
| **Espais Verds i Biodiversitat** | Ajuntament department responsible for green spaces and biodiversity. | **Intended user** |
| **Barcelona Regional** | Municipal urban-development agency (absorbed former Agència d'Ecologia Urbana de Barcelona in 2020). | **Intended user** |
| **Pla Clima** | Barcelona's 2030 climate action plan. Provides the policy context for urban cooling interventions. | Context document |

## Technical → Planning Domain

| Term | Meaning | Cross-reference |
|---|---|---|
| **Barrier-reduction priority map** | The project's output: a ranked GeoJSON of 400m grid cells scored on four measurable barriers (sealed surface, heat, low canopy, host–mycorrhizal mismatch), with a per-zone intervention-type recommendation. | NOT a mycorrhizal network map, NOT a recovery prediction, NOT a belowground state assessment |
| **Composite barrier index** | Weighted combination of four normalized sub-scores (0–1). Higher = more barriers = higher intervention priority. | Each sub-score maps to a specific budget line |
| **Sub-score** | One of four per-zone barrier measurements: sealed surface %, heat anomaly °C, NDVI, host–mycorrhizal mismatch flag. | Each maps 1:1 to an intervention type |
| **Decision unit** | The 400m × 400m grid cell at which claims are made. | Maps to Superilla scale |
| **Peri-urban reference patch** | A 1km² zone in Collserola Natural Park used as a low-barrier qualitative baseline. NOT a target zone, NOT used for quantitative comparison. | Methodological anchor only; N=1 |
| **CRS (Coordinate Reference System)** | EPSG:4326 (WGS84 lat/lon) for output; EPSG:25831 (ETRS89 / UTM zone 31N) for raster processing. | All spatial layers reprojected at ingest |
| **AM (Arbuscular Mycorrhizal)** | Fungal type that penetrates root cells. Partners with ~85% of BCN's street trees (*Platanus*, *Celtis*, *Tipuana*, etc.). Invisible to citizen science (no aboveground fruiting bodies). | The **AM-blindness** confound |
| **EM (Ectomycorrhizal)** | Fungal type that forms a sheath around root tips. Partners with *Pinus*, *Quercus*, *Tilia* (~9,000 BCN trees). Produces mushrooms — visible to citizen science. | The subset for which GBIF observations are useful |
| **FungalRoot v2.0** | Global empirical database mapping plant species to mycorrhizal type. | Join table: tree species → expected mycorrhizal type |
| **GBIF** | Global Biodiversity Information Facility. Aggregates occurrence records (specimens, observations) from ~2,000 publishers. | Source for observed-fungi layer |
| **NDVI** | Normalized Difference Vegetation Index. Proxy for canopy density/health. Unitless, range −1 to 1. | Sentinel-2 10m |
| **LST** | Land Surface Temperature. Measured in °C from Landsat thermal band. | Landsat 8/9 100m, resampled to 30m |
| **Urban Atlas** | Copernicus land-cover/land-use product at 10m resolution. Source for sealed-surface fraction. | 2018/2021 vintage |

## Contested Terms (Different Meanings in Different Contexts)

| Term | Planning Meaning | Technical/Data Meaning | Resolution |
|---|---|---|---|
| **"Priority"** | Political or budgetary priority (which zone gets funding first) | Statistical priority (highest composite barrier score) | We use the statistical meaning. The product card explicitly states that political priority may differ. |
| **"Connectivity"** | Ecological connectivity (wildlife corridors, green infrastructure network) | Graph connectivity (network edges between nodes) | We do NOT map ecological connectivity. The v1 "fragmentation" framing was rejected. If "connectivity" appears, it refers to the network-graph analysis in notebook 04, which is used to identify isolated tree clusters — NOT to claim belowground fungal network connectivity. |
| **"Recovery"** | Policy goal: ecological restoration of urban soils | Ecological process: fungal community re-establishment (5–20+ year timescale) | We do NOT claim or measure recovery. The output identifies *barrier reduction leverage* — conditions that would need to change for recovery to become possible. |
| **"Grid"** | City grid (Eixample street layout) | Analysis grid (400m × 400m vector grid) | We use the analysis meaning. Clarify in all documentation that "grid cell" = analysis unit, not a city block. |
