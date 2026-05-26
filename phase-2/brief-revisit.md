# Brief Revisit — Phase 2 Data Understanding Close-Out

Per earn-the-data Step 10: after data profiling and quality audit, re-ask whether the original question can still be answered with the available data.

## Original question (v1)

> "Where is Barcelona's mycorrhizal fungal network most fragmented, and which urban-form features best predict fragmentation severity?"

## Can it be answered with available data?

**No.** Three findings from Phase 2 made the v1 question unanswerable:

1. **AM-blindness.** AM fungi — partners of ~85% of Barcelona's street trees — produce no visible aboveground fruiting bodies and are invisible to citizen science. GBIF records are 98.3% citizen-science observations, 0% DNA-based. The "observed fungi" layer is structurally incomplete.
2. **No belowground data.** No DNA metabarcoding reference exists for Barcelona at usable density. GlobalAMFungi has sparse/zero Iberian coverage.
3. **"Fragmentation" implies network state.** We cannot measure, map, or predict mycorrhizal network connectivity belowground.

## Revised question (v2, adopted)

> "Which 400m zones in Barcelona face the highest combined barrier load (sealed surface, heat anomaly, low canopy, host-mycorrhizal mismatch), and what intervention type — de-paving, planting, species-selection, or combined — offers the highest leverage per zone, within existing Ajuntament budget lines?"

## Why v2 is answerable

Each of the four barrier sub-scores maps to a dataset that passed the 10/14 rubric threshold:

| Barrier | Data Source | Rubric Score | Resolution |
|---------|------------|-------------|------------|
| Sealed surface | Copernicus Urban Atlas | 14/14 | 10m |
| Heat anomaly | Landsat 8/9 LST | 14/14 | 100m (resampled 30m) |
| Low canopy (NDVI) | Sentinel-2 L2A | 14/14 | 10m |
| Host–mismatch | Ajuntament Trees + FungalRoot + GBIF | 13/14 + 12/14 + 12/14 | Per-tree point |

All four are ≥2× finer than the 400m decision unit.

## Surviving questions (7 sub-questions)

1. Per zone, what mycorrhizal type does host tree composition lead us to expect? → **Answerable** (species-level join against FungalRoot)
2. Per zone, what is the sealed-surface fraction? → **Answerable** (Urban Atlas 10m)
3. Per zone, what is the land-surface temperature anomaly vs. BCN mean? → **Answerable** (Landsat LST)
4. Per zone, what is the mean NDVI? → **Answerable** (Sentinel-2)
5. Per zone, is there host–mycorrhizal mismatch? → **Answerable** with documented AM-blindness caveat
6. Per zone, what is the composite barrier index and recommended intervention type? → **Answerable** (weighted composite of 1–5)
7. How do the top 15 zones compare to the Collserola reference patch? → **Answerable** (qualitative anchor, same data layers)

## What the data still cannot answer

- **Belowground network state.** No data source. Not claimed.
- **Recovery trajectory.** Would require 5–20+ year longitudinal DNA data. Not claimed.
- **AM-fungal community composition.** No DNA reference in Iberia. Documented as gap.
- **Soil moisture at 400m.** ERA5-Land rejected (9km, fatal resolution axis). NDVI+LST used as joint surface proxies.
- **Tree health/vitality.** Not in tree inventory. Not claimed.

## Cancellation criterion re-check

> "If more than two of four barrier sub-scores cannot be computed at 400m for ≥50% of cells, rescope or cancel."

**Status after Phase 2:** All four sub-scores have adopted data sources at ≥2× finer than 400m resolution. Sealed surface and NDVI are near-certain. LST is highly likely (Mediterranean summer cloud cover is low). Host–mismatch is the one at risk (AM-blindness), but it IS computable — the "unconfirmable" flag IS the computed value. The cancellation criterion has NOT been triggered. Proceed to Phase 3.

## Sign-off

The revised question (v2, barrier-reduction priority map) is answerable with the adopted data. All 7 sub-questions have at least one adopted data source. The cancellation criterion has been re-checked and has not fired.

**Date:** 2026-05-26
**Revisited by:** Rafik (Phase 2 companion close-out)
