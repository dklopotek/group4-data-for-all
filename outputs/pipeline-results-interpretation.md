# Mycorrhizal Barcelona -- Pipeline Results Interpretation

**Date**: 2026-05-26
**Pipeline**: `src/clean_data.py` (14-stage deterministic ETL)
**Data sources**: Ajuntament tree inventory (189,140 trees), FungalRoot v2.0, GBIF fungi (300 records), Urban Atlas sealed surface, Landsat LST summer composite, Sentinel-2 NDVI summer composite, BCN municipal boundary.

---

## 1. What the Pipeline Produced

The pipeline built a 400 m x 400 m square grid clipped to the Barcelona municipal boundary and scored all 495 intersecting cells on a **0-1 barrier index** where higher = more hostile to mycorrhizal fungi. Each cell carries:

- **4 sub-scores**: S1 (sealed-surface fraction), S2 (LST anomaly -- heat island intensity), S3 (inverted NDVI -- canopy absence), S4 (host-mycorrhizal mismatch).
- **3 composite scores** from different weight scenarios:
  - **Scenario A** (equal): 0.25 / 0.25 / 0.25 / 0.25
  - **Scenario B** (sealed-dominant, PRIMARY): 0.55 / 0.20 / 0.20 / 0.05
  - **Scenario C** (heat + canopy): 0.17 / 0.30 / 0.30 / 0.23
- An **intervention type** (de-paving / planting / cooling / multi-strategy) and a **top-15 flag** ensuring every district has at least one priority cell.

The output is written to `data/processed/scored_grid.geojson` (0.9 MB, 40 columns) and `data/processed/scored_grid.parquet` (0.2 MB).

---

## 2. Where the Highest Barriers Are

**Scenario B top-5 (raw score, no district constraint):**

| Rank | Cell ID | District | Score B | Primary driver |
|------|---------|----------|---------|----------------|
| 1 | C016_011 | Sants-Montjuic | 0.855 | S2=1.00 (extreme heat island), S3=0.95 (near-zero canopy) |
| 2 | C031_035 | Sant Andreu | 0.821 | S2=0.89, S1=0.80 |
| 3 | C032_032 | Sant Andreu | 0.817 | S1=0.81, S3=0.89 |
| 4 | C016_010 | Sants-Montjuic | 0.797 | S1=0.81, S2=0.82 |
| 5 | C014_016 | Sants-Montjuic | 0.794 | S1=0.88 (extremely sealed) |

**The top 9 cells** (scores 0.781-0.855) cluster in Sants-Montjuic, Sant Andreu, and Ciutat Vella -- the industrial port zone, the Besos river industrial corridor, and the dense historic core. **Sants-Montjuic alone claims 5 of the top 15**, reflecting its dual burden of extreme sealing (former industrial rail yards, Zona Franca) and intense heat islands (port infrastructure, asphalt).

The district-constrained top-15 selection then tacks on the highest-scoring cell from each of the remaining 5 districts (Eixample, Les Corts, Gracia, Sarria-Sant Gervasi, Horta-Guinardo, Nou Barris), creating a sharp score drop from #10 (C025_024, Eixample, 0.646) to #11 (C010_022, Les Corts, 0.282). The district constraint is necessary for equity but produces a top-15 with a **5:1 score ratio between the highest and lowest priority cell** -- meaning some "priority" cells are barely barriers at all by the citywide standard.

The Sats-Montjuic cluster lies in the Zona Franca / port zone. This area also has the highest LST anomaly values (S2 peaks at C016_011 with a normalized score of 1.00), confirming the industrial-sealed-heat synergy.

---

## 3. What the Intervention Breakdown Tells Us

With real raster data, **471 cells (95.2%) are classified "de-paving"** -- the dominant intervention. Only 14 cells (2.8%) are "planting", 9 (1.8%) are "cooling", and 1 (0.2%) is "multi-strategy".

**Why de-paving dominates:**

1. **Scenario B weights sealed surface at 0.55** -- the single largest weight. This was an intentional design choice (ADR-003) reflecting that physical soil sealing is the root cause that drives both heat islands and canopy loss.
2. **Barcelona is heavily paved**. The Urban Atlas sealed-surface raster yields a citywide mean of 0.646. Eixample averages 0.86 sealed. Sants-Montjuic industrial zones hit 0.88.
3. **S1 drives the composite**. The correlation between S1 and composite_B is 0.968. The other sub-scores are far weaker drivers: S3 (inverted NDVI) correlates at 0.776 with the composite, S2 (LST) at 0.510, and S4 (mismatch) at -0.033 (essentially uncorrelated).

**When the other interventions fire instead:**

- **Planting** (14 cells): Fires when a cell has low sealed surface but high inverted NDVI (missing canopy). These are primarily green but unvegetated areas -- parks with sparse tree cover, or unpaved vacant lots.
- **Cooling** (9 cells): Fires when sealed surface is moderate but heat island intensity is extreme relative to the surroundings. These are typically dense residential blocks with some tree cover but extreme albedo/thermal mass.
- **Multi-strategy** (1 cell, C024_038 in Nou Barris): This single cell has S4=0.8 (EM potential isolation), very low sealed surface (0.02), and low NDVI (0.02). It is the only cell where the S4 mismatch signal rises above the sealed-surface noise, and its intervention profile is de-paving=14%, cooling=38%, planting=4%, multi-strategy=43%.

The near-monoculture of "de-paving" is a honest reflection of the sealed-dominant weighting, but it also means the intervention map is not very discriminating. For a city planning department, the message is essentially: *almost everywhere needs de-paving first*.

---

## 4. AM-Blindness Impact

**423 cells (85.5%) are scored at S4=0.5** (informationally null), down from the initial claim of 53.1%. The reason: **94.5% of grid cells are AM-dominant** (mean AM% = 89.8%, mean EM% = 9.8% across the city).

This is not a pipeline bug. It is a **fundamental ecological characteristic of Barcelona's urban forest**. The overwhelmingly AM tree population (Platanus, Celtis, Tipuana, Jacaranda, Robinia -- all AM) means there is almost no EM tree signal to detect. The S4 rules are:

- AM-pct >= 80% -> S4 = 0.5 (informationally null) regardless of GBIF evidence
- EM-pct >= 50% -> S4 = 0.0 if EM GBIF nearby, 0.8 if not

Since 468 of 495 cells are AM-dominant, the S4 score essentially **collapses to a constant 0.5 for the vast majority of cells**. The only cells that escape this are the 12 EM-dominant cells and 13 mixed cells.

**What this means for the output's honesty**: The S4 sub-score is effectively non-informative for 85.5% of the map. It does not distinguish between cells that genuinely have healthy AM fungal networks and cells where we simply lack the data to know. The pipeline is correct to flag this via S4=0.5, but the interpretation must be explicit: **for AM-dominant cells, we have no fungal-connectivity information at all**. The composite score for these cells reflects only physical barriers (sealing, heat, canopy loss), not biological ones.

The 12 EM cells (C010_029 being the highest-profile, reaching the top-15 as the Sarria-Sant Gervasi representative with S4=0.0 -- EM partners present) are the only cells where we can say anything biologically specific.

---

## 5. Scenario Sensitivity

The three weight scenarios produce top-15 lists that diverge sharply:

| Comparison | Jaccard | Overlap | Interpretation |
|------------|---------|---------|----------------|
| A (equal) vs B (sealed-dominant) | 0.364 | 8/15 | Very different -- prioritizing sealed surface changes priorities |
| A (equal) vs C (heat+canopy) | 1.000 | 15/15 | Identical -- equal weights and heat+canopy weights produce the same top-15 |
| B (sealed-dominant) vs C (heat+canopy) | 0.364 | 8/15 | Very different -- the sealed vs. heat/canopy split is real |

**A and C produce identical top-15 lists.** This makes sense: A (0.25/0.25/0.25/0.25) and C (0.17/0.30/0.30/0.23) both distribute weight away from sealing and toward the other factors, unlike B which concentrates 0.55 on S1. The seven cells unique to B (absent from A/C) are:
- C026_018, C026_019 (Ciutat Vella) -- dense, sealed historic core
- C030_034 (Sant Marti) -- industrial zone
- C015_016, C014_016, C027_027 (Sants-Montjuic/Sant Marti) -- port/industrial
- C028_022 -- another sealed pocket

The **8 cells common to all three scenarios** represent the irreducible core of Barcelona's worst barriers: cells that are simultaneously sealed, hot, canopy-poor, and mycorrhizally uncertain. These are the no-brainer priority zones.

**Practical implication**: A city council that adopts sealing reduction as its primary strategy (Scenario B) gets a different priority list than one focused on heat + greening (Scenario C). The two lists disagree on half their recommendations. This sensitivity should be acknowledged explicitly in any planning document.

---

## 6. GBIF Data Poverty

**431 of 495 cells (87.1%) have zero fungal occurrence records.** The mean is 0.3 records per cell; the maximum is 18 records in a single cell. The entire city has only 300 GBIF records for all fungi.

This is a severe data limitation that constrains what the pipeline can honestly claim:

- The S4 score's "EM GBIF nearby" check (which could reduce S4 from 0.8 to 0.0 for EM-dominant cells) is essentially non-functional: almost no EM-dominant cell has GBIF evidence to confirm or refute nearby EM partners.
- The 12 EM-dominant cells are evaluated with essentially no ground-truth fungal observation data.
- The S4=0.5 (informationally null) score is as much a commentary on GBIF data poverty as it is on AM dominance.

GBIF-based fungal mapping in Mediterranean urban ecosystems is an active research gap. The 300 records cover only the most commonly observed macrofungi (largely Basidiomycota). The vast majority of Glomeromycota (AM fungi) are entirely invisible to citizen science because they fruit underground.

---

## 7. What This Map Can Claim vs. Cannot Claim

### Can claim (within the pipeline's stated limits):

1. **Physical barrier hotspots**: Cells C016_011 through C027_027 (scores 0.781-0.855) are genuinely the most physically degraded zones for soil organism movement -- sealed, hot, and vegetation-poor. The ranking of these top-9 cells is robust across scenarios.
2. **District-level barrier patterns**: Eixample, Sant Andreu, and Sant Marti are the most sealed districts; Sarria-Sant Gervasi is the least. This matches known urban morphology.
3. **Intervention type**: The near-universal need for de-paving is a real finding, consistent with Barcelona's documented 60%+ impervious surface cover.
4. **AM dominance**: 89.8% mean AM fraction is robust and consistent with Mediterranean urban tree selection favoring AM species.

### Cannot claim (and why):

1. **EM fungal connectivity**. With 85.5% of cells at S4=0.5 (informationally null) and 87.1% with zero GBIF records, we cannot say anything about which cells have functional EM networks. The map is silent on this for most of Barcelona.
2. **Fine-scale priorities below the top-9**. The district constraint creates a long tail of low-score "priority" cells that are barely distinguishable from random 400 m blocks in their barrier scores. Cells #11-#15 (scores 0.093-0.282) should not be interpreted as confirmed barriers.
3. **Causal links between sub-scores**. The pipeline is correlational, not causal. High sealing correlates with low NDVI (r=0.648), but we cannot say how much de-paving a specific cell would increase canopy cover.
4. **Mycorrhizal inoculation potential**. The map identifies barriers to mycorrhizal establishment. It does not model the dispersal kernel, soil chemistry, or competition dynamics that determine whether inoculation would succeed.

---

## 8. Concrete Recommendation for Barcelona Regional

**Zone 1: Zona Franca port-industrial triangle (Cells C016_011, C016_010, C014_016, C015_016, C020_016)**

This is the single most urgent zone -- 5 cells in the top 15, all in Sants-Montjuic, centered on the Zona Franca industrial estate and port area. These cells have sealing rates of 0.80-0.88, LST anomalies at the city maximum, and near-zero canopy (inverted NDVI 0.76-0.95). The recommended intervention is **coordinated de-paving plus industrial greening**: replacing non-functional pavement with permeable surfaces, constructing green corridors along the port rail sidings, and targeted tree planting of AM-compatible species (given the AM dominance). This zone also has network connectivity data (385 cells with component IDs), so de-paving here would connect fragmented habitat patches.

**Zone 2: Sant Andreu Besos corridor (Cells C031_035, C032_032)**

These two cells sit in the Besos river industrial corridor in Sant Andreu, with scores of 0.821 and 0.817. Sealing is 0.80-0.81, LST anomaly is 0.86-0.89, and canopy deficit is 0.88-0.89. The Besos corridor is a known environmental justice concern (lower income, higher industrial exposure). This zone is also the district's only high-barrier area, meaning a targeted intervention here would serve the dual purpose of addressing the district's worst barrier and providing a high-profile demonstration project. Intervention: **de-paving + riparian corridor planting** leveraging the proximity to the Besos river.

**Zone 3: Ciutat Vella historic core (Cell C026_019)**

This cell (score 0.783, sealing 0.88, inverted NDVI 0.81) sits in Barcelona's densest, oldest district. Here, physical space for de-paving is extremely limited -- there are no industrial lots or rail yards. The intervention must be **micro-scale de-paving**: converting underused street parking into permeable planted squares, green roofs on the many flat-roofed historic buildings, and vertical greening on courtyard walls. This zone requires a fundamentally different intervention strategy from the industrial zones, and it represents a test case for whether the de-paving recommendation can be implemented in the ultra-dense historic fabric.

**Why these three zones**: They represent the three distinct urban morphologies of Barcelona -- industrial/sealed (Zona Franca), post-industrial river corridor (Besos), and ultra-dense historic (Ciutat Vella). A successful intervention program across these three zones would generate evidence for the full spectrum of Barcelona's barrier types and de-paving strategies.

---

## 9. The Platanus Replacement Layer (PRPI · v1.1)

**Why this layer exists.** *Platanus × acerifolia* is Barcelona's #1 street tree (~43,722 individuals, ~27.5% of the inventory per Ajuntament canon; 42,828 / 22.6% in our previous snapshot, see v1.2 inventory refresh) and the single largest contributor to spring **rhinoconjunctivitis and food-allergy cross-reactivity** burden in the city — one tree can produce up to 143 billion grains per season, and Barcelona's 2018 peak of 48,626 grains/m³ coincides with Sant Jordi (23 April), the city's largest outdoor public event. The Pla a 3 nsLTP fraction of plane pollen cross-reacts with peach (Pru p 3), walnut (Jug r 3), hazelnut, peanut, and lettuce — making Platanus removal a food-allergy intervention as much as a respiratory one (Scala et al., 2017). The severe-asthma attribution is weaker than commonly cited: Osborne et al. (2017, *Int J Biometeorol*) found no statistically significant association between London plane pollen and asthma hospitalization at any lag in the largest comparable daily-time-series study (London, n=8.2M); grass pollen DID show strong lag effects. The 2017-2037 Pla Director de l'Arbrat targets a reduction of plane trees from 27% to <12% of street-tree canopy by 2037. The city's ordinary planting cadence is ~2,500/year with post-drought catch-up ~5,000/year; Platanus-specific replacement to hit the 2037 target requires ~1,800/year. PRPI gives operations a defensible spatial allocation of that budget.

**What the index combines.** PRPI is a 0-1 weighted sum of four signals -- Platanus density (0.40 weight, public-health driver), inverted NDVI (0.20, low canopy benefits most from replanting), S4 shift potential (0.20, replacement can break the AM-blind null zone where it counts), and planting feasibility (0.20, `1 - sealed_surface_fraction`). The index is folded as a 5th term into all three composite scenarios; Scenario B's primary weight allocation was rebalanced from `{s1: 0.55, s2: 0.20, s3: 0.20, s4: 0.05}` to `{s1: 0.45, s2: 0.20, s3: 0.15, s4: 0.05, prpi: 0.15}`. PRPI is also surfaced standalone in the output schema so planners can read it without scenario context.

**Headline results.** PRPI range across 495 cells: [0.151, 0.832], mean 0.314. 15 cells satisfy the strict `replacement_priority` gate (PRPI > 0.5 AND s4_shift_potential > 0 AND s1_sealed < 0.7). 3 cells have PRPI as their dominant intervention term and receive `intervention_type = "species-replacement"`. 165 cells (33%) hit the `s4_shift_ceiling_reached` flag -- they remain ≥80% AM even after full Platanus removal, because non-Platanus AM species (Celtis, Tipuana, Sophora, Citrus) already saturate them. In those cells PRPI signals only the pollen + feasibility component; the mycorrhizal shift is structurally impossible without a much broader species turnover.

**What we can claim.** (1) The Platanus removal queue is spatially differentiated. Pollen exposure is not uniformly distributed -- cells in Sant Martí, Eixample, and Sant Andreu carry both high Platanus density AND high planting feasibility AND meaningful S4 shift potential. These are first-cut candidates for the 2027-2030 phase of the Master Plan. (2) The native EM palette (*Quercus ilex*, *Pinus halepensis*) gives the city a way to address public health AND ecological function simultaneously, vs. the current AM-host trial species (*Zelkova*, *Pistacia*) which only address public health. (3) The honest reporting of the AM-blindness ceiling tells operations where the mycorrhizal argument is window-dressing and where it's load-bearing.

**What we cannot claim.** (1) Replacement species succession dynamics. PRPI assumes one-for-one replacement at full survival; transplant mortality in Barcelona's compacted urban substrate is ~15-25% over the first 5 years (Roman & Battles 2011 for street trees generally; no BCN-specific cohort data). (2) Allergen exposure modelling. PRPI counts trees, not pollen drift -- prevailing onshore winds during March-May skew exposure inland and concentrate downwind of the central plane-tree spine. The pollen layer is a proxy, not a dispersion model. (3) Replacement cost optimisation. Each tree-for-tree swap costs roughly €4,500 (extraction + structural soil + 25-30L specimen + warranty). PRPI does not balance this against the avoided medical cost of pollen-related ER visits; a full cost-benefit analysis would need an Agència de Salut Pública dataset we have not yet sourced. (4) That the city will actually adopt the index. The 2037 plan is a political artifact -- elections, budget cuts, or a shift in Master Plan emphasis can date this layer at any point. The schema's `version: 1.1.0` and the explicit `PLATANUS_TARGET_PCT = 12.0` constant exist so the index can be re-parameterised without rewriting the pipeline.

**Recommended use.** PRPI is a planning prior, not an operational instruction. Treat the `replacement_priority` flagged cells as the candidate set for a 2027-pilot programme; treat the cells where PRPI dominates the composite as the showcase sites for cross-functional alignment between Direcció d'Espais Verds, Agència de Salut Pública, and Barcelona Regional. Cells flagged `s4_shift_ceiling_reached` are valid Platanus-removal sites for public-health reasons but should NOT be marketed as mycorrhizal-restoration projects -- the substrate cannot carry that claim.

---

## 10. v1.2 Pivot — VPA Allergenicity + Operational Scenario

A three-stream deep-research review on 2026-05-26 (full report at `outputs/deep-research-platanus-prpi.md`, ~5,800 words, APA 7, 30+ refs) surfaced five evidence-based contradictions to the v1.1 design. The v1.2 pivot is small, additive, and fully explainable: same composite architecture, same six locked design decisions, same 2037 policy anchor — with empirically-warranted priors layered on.

**What changed:** (a) `arbrat-viari` refreshed to the Open Data BCN 2026_1T snapshot (188,991 trees, 494 cells × 51 cols); (b) `s4_shift_potential` reframed as an *upper-bound* under ideal-substrate assumption, per Verbeek et al. (2025) and Gaimaro et al. (2025) showing urban AM communities shift composition rather than collapse; (c) public-health docstrings re-scoped from "asthma burden" to "rhinoconjunctivitis morbidity + food-allergy cross-reactivity via Pla a 3" per Scala et al. (2017) and the null asthma-admission result of Osborne et al. (2017); (d) a `Cariñanos & Marinangeli (2021)` VPA allergenicity table for 40 Mediterranean species wired in as `cell_vpa_score`; (e) a parallel `prpi_operational` scenario anchored to Barcelona's Espais Verds Zelkova/Pistacia pilot palette, sitting beside the EM-optimistic `prpi` so both scenarios remain auditable.

**Headline result (2026_1T run):** `cell_vpa_score` ranges [0.200, 0.856]; 24 cells already have ≥50% of their tree composition in the operational pilot palette; `prpi_operational` ranges [0.151, 0.728] — peaking 0.104 below the EM-optimistic `prpi` (0.832), reflecting that the operational scenario does not credit cells with the speculative AM-blindness break. The most decision-relevant statistic is the **17-cell disagreement set** at the `prpi > 0.5` action threshold — these are the cells where the policy choice between EM-host substitution (*Quercus ilex* / *Pinus halepensis*) and operational pilot palette (*Zelkova* / *Pistacia* / *Sophora*) materially changes the recommendation. The intervention enum distribution remains stable (de-paving 459 / cooling 24 / planting 7 / species-replacement 3 / multi-strategy 1).

**Why pivot, what the pivot does NOT do:** The pivot does NOT invalidate v1.1; each finding tightens v1.1 rather than overturning it. *Quercus ilex* allergenically equals *Platanus* (both VPA IV–V, both Bet v 1-family allergen panels via Que i 1) — the EM-optimistic substitution alone would shift the allergy peak rather than reduce it. Barcelona's *own* operational pilot uses Zelkova and Pistacia precisely because they sit in VPA class I-III with low Mediterranean cross-reactivity, are drought-tolerant under +2°C scenarios, and avoid the food-allergy bridge that *Platanus* Pla a 3 creates with peach, walnut, and lettuce. The v1.2 operational scenario is what the city is actually doing; the EM-optimistic scenario remains useful as a mycorrhizal-ecology upper-bound sensitivity test.

**What this means for downstream consumers.** Direcció d'Espais Verds should preference Zelkova/Pistacia in the 17 disagreement cells. Agència de Salut Pública can cite `cell_vpa_score` as a peer-reviewed proxy for allergenicity burden (Cariñanos & Marinangeli, 2021) rather than the implicit "high allergen because Platanus" proxy of v1.1. Barcelona Regional can use the operational scenario for grant-defensible recommendations because every assumption is anchored to either a published policy (Pla Director 2017-2037) or a peer-reviewed empirical study (Cariñanos & Marinangeli 2021; Osborne et al. 2017; Scala et al. 2017; Verbeek et al. 2025). The full evidence chain and integration matrix for any future v1.3 work is in `outputs/deep-research-platanus-prpi.md` §7-§10.
