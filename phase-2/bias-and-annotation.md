# Bias and Annotation-Quality Estimate

Per CRISP-DM Phase 2 companion Step G. Two parts: (1) bias findings lifted verbatim from data sheets and the data inventory, so this artifact is self-contained and reviewable; (2) label/annotation error-rate estimates for citizen-science and crowd-annotated sources. Closes **G6**.

**Date:** 2026-05-26

---

## Part 1 — Bias findings (verbatim from Phase 2 artifacts)

### 1.1 Ajuntament BCN Tree Inventory

*Source: `phase-2/data-sheets/ajuntament-trees.md` §8*

> **Spatial bias toward areas with municipally-managed greenery** — i.e. away from peripheral districts with high private-land vegetation, and away from informal/unrecorded plantings. Using this dataset alone to infer "biodiversity" of an area would systematically undercount private-realm contributions.

> **No tree-health information.** The dataset records presence and identification, not condition. A listed tree may be dead, removed since the snapshot, or in serious decline. The expected-mycorrhizal-type layer is genuinely an *expectation*, not a confirmation.

> **Species-level taxonomy may be inconsistent.** Genus-only entries (observed: 0.01%) trigger a defined fallback in the FungalRoot join.

> **FungalRoot lookup in engineered urban substrates.** Barcelona's street trees are frequently planted in structural soil cells (crushed aggregate + minimal soil), compacted backfill, or as container-grown transplants — conditions under which AM and EM colonisation may not establish for 3–10 years post-planting regardless of host species (Jumpponen & Egerton-Warburton 2010, *Mycorrhiza* 20:557–567). Trees with `data_plantacio` within the past 5 years are flagged `colonisation_uncertain=True` in the pipeline output.

> **Public-realm-only coverage.** Private gardens, courtyards, and manzana-interior plantings are absent. Sentinel-2 NDVI partly compensates by giving total vegetation signal regardless of management category.

*Source: `phase-2/data-inventory.md` — Ajuntament Trees rubric*

> Bias clarity score: **1/2** — Bias toward public-realm trees is documented but private-tree cover has not been quantified at 400m resolution for Barcelona. The magnitude of the private-realm gap is unknown for our decision unit.

### 1.2 GBIF Fungal Occurrences

*Source: `phase-2/data-sheets/gbif-fungi.md` §3 and §8*

> **Opportunistic sampling.** Citizen-science observations occur where humans go, during seasons when fruiting bodies are visible (autumn-heavy), and conditional on phone-camera-and-app technology adoption. This is emphatically *not* probabilistic sampling.

> **Geographic skew toward accessible / high-foot-traffic areas.**

> **Phenological skew toward fruiting-body season** (typically autumn in Mediterranean climate).

> **Taxonomic skew toward visible, identifiable groups** — ectomycorrhizal and saprotrophic fungi over-represented; arbuscular mycorrhizal fungi essentially absent (no visible fruiting body to photograph).

> **Observer skew** toward enthusiast taxa (boletes, *Amanita*, morels) over inconspicuous taxa.

> **AM-blindness** — the load-bearing limit. AM fungi do not produce visible fruiting bodies and are essentially absent from the citizen-science portion of GBIF. A *zero* fungal record at a location does not mean *no fungi* — it means *no visible fruiting body was observed by a citizen scientist*.

> **Socioeconomic equity concern.** Citizen-science participation is uneven across neighborhoods and may correlate with income, age, and access to outdoor green space. Using this dataset to allocate any kind of public investment without correcting for the skew would systematically disadvantage areas with lower observer participation.

*Source: `phase-2/data-inventory.md` — GBIF rubric*

> Bias clarity score: **1/2** — Major biases documented but not quantified for our area. Fruiting-body bias, geographic skew, seasonal bias, and taxonomic skew are all documented in the literature but numerical correction factors do not exist for our spatial/temporal window.

### 1.3 FungalRoot v2.0

*Source: `phase-2/data-inventory.md` — FungalRoot rubric*

> Bias clarity score: **2/2** — The database reports mycorrhizal *type* (AM/EM/ErM/NM/mixed), not colonisation intensity or viability. This limit is documented in the paper. No bias in type assignment methodology identified.

*Source: `phase-2/quality-cross-check.md` — DQ2 Objectivity*

> **deferred:** The database reports mycorrhizal *type*, not colonisation intensity or viability. This limit is documented in the paper.

**Additional note (added at companion close-out):** FungalRoot assignments are compiled from natural and semi-natural ecosystem literature. Colonisation type in engineered urban substrates may differ from the published assignment. This is not a bias in FungalRoot itself — it is a domain-shift issue when applying the lookup table to an urban context. Mitigation: the `colonisation_uncertain` flag (trees planted <5 years ago) and the categorical mismatch encoding (matched / mismatched / unconfirmable) rather than a pseudo-continuous score.

### 1.4 Copernicus Urban Atlas 2018

*Source: `phase-2/quality-cross-check.md` — DQ2 Objectivity*

> **assessed:** High. Standardised methodology applied uniformly across all European FUAs. The sealed-surface fraction is an objective remote-sensing product.

*No bias findings specific to our use case. The 2018 vintage is ageing but sealed-surface fraction changes slowly at city scale.*

### 1.5 Landsat 8/9 LST

*Source: `phase-2/quality-cross-check.md` — DQ2 Objectivity*

> **assessed:** High. Instrument-derived measurement with documented algorithms. Known urban canopy limitation: LST ≠ soil temperature. The satellite measures surface (rooftop, pavement, canopy-top) temperature, not ground-level air temperature. Urban heat island studies routinely use LST as a proxy; this is documented, not hidden.

### 1.6 Sentinel-2 L2A

*Source: `phase-2/quality-cross-check.md` — DQ2 Objectivity*

> **assessed:** High. Instrument-derived measurement. NDVI is a well-characterised vegetation index.

*No bias findings specific to our use case. NDVI saturation at high biomass (>0.8) is a known remote-sensing limit but not relevant for a Mediterranean urban environment where high-NDVI values are rare.*

---

## Part 2 — Annotation / label quality estimates

Per Northcutt et al. (2021), label noise destabilises downstream rankings even at ~3% error rates. This section records what the project knows, what it does not know, and what it plans to do about both for each crowd-annotated or citizen-science source.

### 2.1 GBIF / iNaturalist — fungal identification accuracy

**Source type:** Citizen-science (crowd-annotated). iNaturalist "research grade" requires ≥2/3 community identifications agreeing at species level. Non-research-grade records may still appear in GBIF depending on publisher configuration.

**Published audit:** No fungal-specific iNaturalist accuracy audit exists for our geography or taxa. General iNaturalist accuracy studies (e.g., Hochmair et al., 2020, *PLOS ONE*) report >95% research-grade accuracy for well-photographed macro-taxa (birds, plants, butterflies) but fungi are consistently among the lowest-accuracy taxa due to cryptic species complexes and dependence on microscopy/DNA for definitive identification.

**Our estimate:** `unknown` — no published error rate for fungal records in our geography.

**Observed quality signals in our data:**
- 98.3% HUMAN_OBSERVATION (citizen-science) vs 1.6% PRESERVED_SPECIMEN (vouchered)
- 0% MATERIAL_SAMPLE (DNA-based) — zero molecular records
- `taxonRank`: majority species-level, some genus-only (not yet tabulated for our subset)

**Mitigation:**
1. The project does NOT use GBIF as a barrier sub-score input. GBIF is used as observation-context only.
2. The peri-urban reference patch (Collserola) provides a qualitative sanity-check anchor — not a quantitative correction.
3. The "unconfirmable" category in the host–mismatch sub-score encodes the AM-blindness limit explicitly rather than faking a pseudo-quantitative score.
4. If DNA-based fungal records become available for Barcelona (e.g., from soil eDNA surveys), re-ingest and compare against citizen-science records. Until then, the gap is documented.

### 2.2 Ajuntament Trees — species identification

**Source type:** Professional (municipal contractor field surveys). Not crowd-annotated.

**Quality assessment:** Species identification is performed by trained operators with municipal oversight. 0.01% genus-only records (25 out of 189,090) suggests high identification confidence. However, no independent audit of species-ID accuracy exists — we rely on the Ajuntament's internal QA.

**Our estimate:** `unknown` but low-risk. The 381 species in the inventory are common Mediterranean urban trees; identification error rate is likely <1% for trained operators. Misidentification risk is highest for:
- Cultivars within a species complex (e.g., *Platanus × acerifolia* vs *Platanus orientalis*)
- Young trees before diagnostic features develop
- Palm species (*Phoenix*, *Washingtonia*)

**Mitigation:** The FungalRoot join at species level is robust to occasional misidentifications because AM/EM type is conserved at genus level for most taxa. A misidentified *Platanus* cultivar still maps to AM.

### 2.3 Sentinel-2 NDVI — cloud masking

**Source type:** Instrument-derived (ESA operational product). Not crowd-annotated.

**Quality signal:** Sen2Cor atmospheric correction + Scene Classification Layer (SCL). Cloud and cloud-shadow pixels (SCL classes 8, 9, 10) are masked before compositing.

**Our estimate:** `unknown` — cloud-mask coverage for our specific scene(s) has not been verified. Mediterranean summer cloud cover is low (<15% expected), but no quantitative check has been performed (deferred to Session 3 notebook 02).

**Mitigation:** Report scene count, cloud-cover fraction, and valid-pixel fraction per 400m cell in the output metadata. Cells with <50% valid NDVI pixels after cloud masking should be flagged and reported separately.

### 2.4 Landsat LST — emissivity and cloud screening

**Source type:** Instrument-derived (NASA/USGS operational product). Not crowd-annotated.

**Quality signal:** Landsat Collection 2 Level-2 ST band includes per-pixel quality assessment (QA_PIXEL band). Cloud, cloud-shadow, and water pixels are flagged.

**Our estimate:** `unknown` — QA band has not been inspected for our scene(s). Deferred to Session 3 notebook 02.

**Mitigation:** Same as Sentinel-2 — report valid-pixel fraction per 400m cell. Flag cells with <50% valid LST pixels.

---

## Summary: bias and annotation register

| Source | Bias severity | Annotation quality | Mitigation |
|--------|-------------|-------------------|------------|
| Ajuntament Trees | MODERATE (public-realm only) | Professional; error rate unknown but likely <1% | NDVI cross-check; documented caveat |
| GBIF Fungi | SEVERE (AM-blindness, geographic/taxonomic/seasonal skew) | Citizen-science; fungal ID accuracy unknown, likely lower than macro-fauna/flora | NOT used as barrier input; reference patch anchor; unconfirmable category |
| FungalRoot v2.0 | LOW (urban-substrate domain shift) | Peer-reviewed; type assignments stable at species level | colonisation_uncertain flag; categorical mismatch encoding |
| Urban Atlas 2018 | LOW | Instrument-derived; standardised methodology | Vintage tracking |
| Landsat LST | LOW | Instrument-derived; validated product | Valid-pixel fraction reporting |
| Sentinel-2 NDVI | LOW | Instrument-derived; validated product | Cloud-mask coverage reporting |

**The load-bearing gap:** GBIF's AM-blindness is the single largest bias in the project. It is structural (not correctable at our scope), documented in every artifact, and encoded in the output as the "unconfirmable" category rather than hidden behind a pseudo-quantitative score. This is the design choice that makes the v2 (barrier-reduction) brief answerable where the v1 (fragmentation) brief was not.

**Date:** 2026-05-26
**Estimated by:** Rafik (Phase 2 companion Step G)
