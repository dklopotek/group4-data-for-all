# Profiling Plan — before wiring CALIOPE-Urban NO2

Run these 8 checks on the downloaded dataset (Zenodo 16737066) BEFORE joining it to the planner.
The plan is produced here; the verification is run by us on the real file.

1. **Shape & dtypes** — open both products: the 25 m grid (Shapefile/GeoTIFF) and the **census-tract CSV** (preferred). Confirm row count of the tract table ≈ 1,068; confirm the NO2 column is numeric µg/m³.
2. **Missing values** — count tracts with no NO2 value; check whether any of our 1,068 sections are unmatched (edge/Collserola sections). Decide: drop, flag, or nearest-fill — never silent.
3. **Numeric summaries** — NO2 min/max/mean/median per year; sanity-check against known Barcelona annual means (XVPCA city background ~30–45 µg/m³ range historically); flag implausible outliers.
4. **Categorical / key consistency** — inspect the tract identifier field. Is it INE `CUSEC`, or the Ajuntament district+section code we use? Build and test a crosswalk to our `key` (2-digit district + 3-digit section). Confirm a 1:1 match rate; report the %.
5. **Spatial coverage** — bounding box vs Barcelona municipality; confirm full coverage of inhabited sections; note the 250 m buffer spillover into Hospitalet/Badalona (drop those).
6. **Temporal coverage** — confirm years 2019–2024 present; choose the reference year (most recent stable, e.g. 2023/2024) or a multi-year mean; record the choice.
7. **Cross-field consistency / validation** — extract modeled NO2 at the 9 XVPCA station coordinates and compare to their measured annual means (from the XVPCA open dataset). Report the residuals; if systematically off, treat the layer as relative not absolute.
8. **Bridging** — confirm the join key links cleanly to `section_priority.parquet`/`section_enrich.parquet` on `key`; verify a handful of known sections (e.g. an Eixample high-traffic section should read high NO2; a Collserola-edge section low).

Stop-gate: if step 4 (key crosswalk) or step 7 (XVPCA validation) fails, do NOT wire it as a weight — wire it as a clearly-labelled context-only layer, or not at all.
