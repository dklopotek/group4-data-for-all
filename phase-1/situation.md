# Situation Assessment

## Resources

### People

| Name | Role | Time Commitment |
|---|---|---|
| Rafik | Pipeline architect / lead | Part-time, ~4 weeks remaining |
| Dominika | Data layer contributor | Part-time, Session 3–4 |
| Juan | Data layer contributor | Part-time, Session 3–4 |
| [Fourth member] | TBD | Part-time |

### Data (primary sources, named)

| Source | Provider | Access |
|---|---|---|
| Ajuntament tree inventory (Arbrat Viari + Arbrat Zona) | Open Data BCN | CC-BY 4.0, bulk CSV download |
| FungalRoot v2.0 | Soudzilovskaia et al. (2022), *New Phytologist* | Published supplementary data + Zenodo mirror |
| GBIF fungal occurrences (Barcelona, 2015–2024) | GBIF Secretariat | REST API + bulk DwC-A download |
| Copernicus Urban Atlas 2018/2021 | Copernicus Land Monitoring Service | Free portal download |
| Landsat 8/9 LST (Collection 2, Level 2) | USGS EarthExplorer | Free bulk download |
| Sentinel-2 L2A (NDVI) | Copernicus Data Space Ecosystem | Free, CDSE API / STAC |
| OpenStreetMap (street network, building footprints) | OSM Foundation | Overpass API + Geofabrik |
| BCN administrative boundaries (district, barri) | Open Data BCN | CC-BY 4.0 |
| GlobalAMFungi (investigate) | Větrovský et al. (2023) | Web portal (pending manual access) |
| ERA5-Land (rejected — 9km too coarse) | ECMWF / Copernicus | N/A |

### Compute and Software

- Local laptop (Windows 11), Python 3.13
- Libraries: geopandas, shapely, rasterio, networkx, folium, matplotlib, scipy, requests
- No cloud compute, no commercial tools
- Jupyter notebooks for pipeline execution

### Budget

Zero euros. All data and tools are free and open-source.

## Requirements

### Schedule

- Session 3 (current): CRISP-DM data preparation retrofitting + personal data layers
- Session 4 (final): Modeling, evaluation, output packaging, submission

### Comprehensibility

Output must be comprehensible to urban planning analysts who work with GIS but are not mycologists or soil ecologists. The product card must be readable standalone.

### Legal and Ethical

- **Intended use:** Decision-support for municipal green-infrastructure capital allocation in Barcelona.
- **Intended user:** Ajuntament de Barcelona Espais Verds i Biodiversitat; Barcelona Regional planning analysts.
- **Prohibited uses:** (1) No use as a regulatory compliance tool (the map does not meet any regulatory standard). (2) No use for real-estate valuation or property-level decisions (resolution is 400m, not parcel-scale). (3) No use as a substitute for site-specific soil or fungal surveys.

### Security

No PII, no sensitive data. All inputs are public open data. Output is public (CC-BY 4.0).

### Deployment Environment

Git repository. Output is a static GeoJSON file + HTML map. No server, no database, no API.

## Assumptions

1. **Ajuntament tree inventory species taxonomy is consistent** — verified during Session 2 profiling (only 25 records / 0.01% are genus-only).
2. **Satellite data is cloud-free enough for summer composites** — partially verified; cloud occlusion risk documented.
3. **FungalRoot v2.0 species coverage includes all major BCN tree genera** — verified during Session 2 (Platanus, Celtis, Pinus, Quercus, etc. all covered).
4. **GBIF occurrence density in Barcelona is workable** — verified at 1,023 records (2015–2024).
5. **400m grid is the right decision unit for Superilla-scale planning** — confirmed by problem brief v2 analysis.
6. **AM-blindness does not invalidate the barrier-reduction approach** — the project maps barriers, not fungi; the confound is documented, not hidden.

## Constraints (Hard Limits)

### Explicitly IN scope

- Data pipeline design and implementation (Python notebooks)
- CRISP-DM process documentation
- Barrier-reduction priority map (GeoJSON output)
- Per-zone intervention-type recommendation
- Peri-urban reference patch as methodological anchor
- Product card with intended use and limitations

### Explicitly OUT of scope

1. **No frontend, no UI, no map application.** The teacher will not review any frontend work. Output is a GeoJSON file + static HTML map for verification only.
2. **No predictive model.** This is a data pipeline that computes barrier scores from observed data, not a model that predicts future states.
3. **No claim of belowground network state, connectivity, or fragmentation.** The project maps barriers, not the network itself.
4. **No claim that barrier reduction will produce mycorrhizal network recovery.** Timescales are 5–20+ years; the output identifies leverage, not outcome.
5. **No tree-species recommendations.** Only mycorrhizal-type expectation — planners select species within their existing protocols.
6. **No AM-fungal DNA-based validation.** No DNA metabarcoding data exists for Barcelona at usable density.
7. **No peri-urban quantitative claims.** The reference patch is N=1, qualitative anchor only.
8. **No real-time or streaming data.** Static snapshot for the current planning cycle.
