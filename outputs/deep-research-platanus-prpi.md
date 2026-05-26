# Deep Research: Platanus × acerifolia Replacement Priority in Barcelona

**Evidence Synthesis for the PRPI v1.2 Pipeline**

*Project: Mycorrhizal Barcelona — Barrier-Reduction Priority Map*
*Date: 2026-05-26*
*Method: 3-stream parallel deep-research (academia / practice / open source)*
*Author: Rafik Elkhoury (with AI-assisted research per disclosure §11)*

---

## Abstract

The Platanus Replacement Priority Index (PRPI v1.1) was shipped on 2026-05-26 as a 5th term of the Mycorrhizal Barcelona barrier-reduction composite, anchored to the Pla Director de l'Arbrat de Barcelona 2017–2037. Its core design assumes (a) *Platanus × acerifolia* removal substantially reduces pollen-allergy burden, (b) replacement with EM hosts (*Quercus ilex*, *Pinus halepensis*) breaks the AM-blind null zone in borderline cells, and (c) the city's stated trajectory of Platanus reduction from 27% to <12% by 2037 is operationally tractable. A 3-stream parallel literature, practice, and open-source review covering 2015–2026 confirms the policy framing but surfaces **five evidence-based contradictions** that materially alter the v1.2 design: (1) *Platanus* pollen lacks a robust daily-time-series association with asthma hospitalization (Osborne et al., 2017); (2) *Quercus ilex* is allergenically equivalent or worse than *Platanus* via Que i 1 / Bet v 1 homology, undercutting the EM-host substitution as a public-health win (Cariñanos & Marinangeli, 2021; González-Mancebo et al., 2020); (3) urban arbuscular-mycorrhizal communities shift composition rather than collapse, making the AM→EM substrate effect a hypothesis rather than a delivered outcome (Verbeek et al., 2025); (4) Barcelona's *own* active pilot species are *Zelkova serrata* and *Pistacia chinensis* — not the EM hosts PRPI v1.1 optimistically assumed; (5) municipal counts (~43,722 plane trees, 27.5%) exceed the brief's snapshot (42,828, 22.6%), indicating the input inventory should be refreshed. Twelve open-source integrations are prioritized; five are classified MUST for v1.2. The report concludes that PRPI v1.2 should pivot from EM-optimism to a multi-objective species filter co-led by Zelkova/Pistacia, with explicit acknowledgement that Platanus removal is best justified as a rhinoconjunctivitis-and-cross-reactivity intervention, not an asthma intervention.

**Keywords**: urban forestry, Platanus × acerifolia, mycorrhizal restoration, pollen allergy, Barcelona, multi-criteria spatial scoring, CRISP-DM Phase 3

---

## 1. Introduction

Barcelona's municipal tree inventory contains approximately 43,722 *Platanus × acerifolia* (London plane) individuals — the single most-planted street tree species, representing ~27.5% of the city's catalogued canopy (Ajuntament de Barcelona, 2017, 2024; Betevé, 2024). The Pla Director de l'Arbrat 2017–2037 targets reduction below 12% by 2037, with no single species exceeding 15% of the inventory. The driver is dual: a documented pollen-allergy burden in the March–May Mediterranean peak (Belmonte et al., 1999; Plaza et al., 2022) and monoculture vulnerability to *Splanchnonema platani* (Massaria disease) under projected +2 °C warming.

The Mycorrhizal Barcelona project (CRISP-DM Phase 3 pipeline, shipped 2026-05-26) added a Platanus Replacement Priority Index (PRPI) as a 5th term folded into the composite barrier score across all three weight scenarios. PRPI combines four signals — Platanus density, inverted NDVI, S4 mycorrhizal shift potential, and planting feasibility — on a 0–1 scale. Two outputs are derived: an extended `intervention_type` enum value `"species-replacement"` (assigned when PRPI dominates a 5-way contribution profile), and a strict-gate `replacement_priority` boolean (assigned when `prpi > 0.5 AND s4_shift_potential > 0 AND s1_sealed < 0.7`).

PRPI v1.1 was designed under six locked decisions, the most consequential of which assumed EM-optimistic replacement (*Quercus ilex*, *Pinus halepensis*) and anchored the policy framing to the 2037 plan. Before iterating to v1.2, the project required an evidence review answering three sub-questions:

- **RQ1 (Academia)**: What peer-reviewed evidence on *Platanus* allergenicity, urban pollen dispersion, allergen profiles of replacement species, and mycorrhizal-type substrate effects most informs a Mediterranean-urban PRPI?
- **RQ2 (Practice)**: How are Barcelona and comparator Mediterranean cities operationalizing Platanus phase-down — species, costs, monitoring, engagement?
- **RQ3 (Open source)**: Which datasets, packages, repositories, and APIs are integration-ready inputs or validation benchmarks for PRPI v1.2?

---

## 2. Methodology

Three independent specialized investigation agents ran in parallel, each scoped to one RQ and returning a structured findings report with APA 7 inline citations. Inclusion criteria: peer-reviewed publications 2015–2026; verifiable municipal plans and press releases; open-source repositories with verifiable license, last-commit date, and language ecosystem. Tier 1 sources (peer-reviewed, Scopus/PubMed indexed) were prioritized; Tier 2 (preprints) and Tier 3 (gray literature, municipal press) were retained where Tier 1 was absent. Spanish, Catalan, French, and Italian sources were searched in original language. Repositories were verified for activity (commit within 18 months) and license permissiveness (MIT/Apache/BSD/GPL preferred over registration-gated). A Devil's Advocate checkpoint following Phase 3 of the deep-research workflow flagged confirmation-bias risks and cherry-picking patterns; cross-stream contradictions are reported explicitly in §5.

---

## 3. Findings — Academia (RQ1)

### 3.1 Platanus pollen allergy in Mediterranean cities

The sensitization range of 5–59% cited in the project brief is supported but methodologically heterogeneous. Enrique et al. (2002) report 8.48% Barcelona clinic-population prevalence; Madrid clinic studies reach 56–61%; pooled reviews place allergy-patient sensitization at 37–38% across Madrid and Barcelona (Alcázar et al., 2019). The variance is driven by (a) clinic versus general-population sampling, (b) skin-prick versus sIgE testing, and (c) single-allergen Pla a 1 versus full Pla a 1/2/3 panels (Scala et al., 2017). Component-resolved diagnostics show 71.9% of plane-allergic patients are Pla a 3+ (a nsLTP cross-reactive with peach Pru p 3 and walnut Jug r 3 — a food-allergy co-sensitization), 54.1% Pla a 2+, and only 10.9% Pla a 1+ (Scala et al., 2017).

Pollutant interactions are now documented: Chico-Fernández et al. (2025) found ozone significantly potentiates Platanus sensitization in Madrid (p = 0.005), with NO₂ and PM10 also implicated.

**Critical caveat**: Osborne et al. (2017), the largest daily time-series study of pollen and asthma admissions in a major European city (London, n = 8.2M), found **no statistically significant association between London plane pollen counts and adult asthma hospitalization at any lag**, while grass pollen showed strong 3–5 day lag effects (IRR ≈ 1.46). The Mediterranean equivalents (Tobías et al., 2003, Madrid; Hervás et al., 2011, Cartagena) report effects, but these are confounded by co-occurring olive, grass, and Cupressaceae peaks. The attributable severe-asthma burden specifically due to *Platanus* alone is unclear; the well-supported burden is rhinoconjunctivitis morbidity and food-allergy cross-reactivity, not severe asthma.

### 3.2 Urban pollen dispersion models

SILAM (Sofiev et al., 2013, 2024), COSMO-ART (Pauling et al., 2023), and the Copernicus CAMS regional ensemble are the three operational European pollen dispersion systems. None natively forecasts *Platanus × acerifolia*: CAMS operationally covers only six species (alder, birch, olive, grass, mugwort, ragweed), and SILAM extensions cover similar taxa. Resolution is a structural mismatch — SILAM at 0.1–0.25° (~10–25 km), CAMS at ~10 km — none resolves the PRPI 400m grid. The 2024 European pollen reanalysis (Sofiev et al., 2024) covers alder, birch, and olive 1980–2022 only. Mediterranean validation papers exist for olive (Hernández-Ceballos et al., 2014, Córdoba) but **no peer-reviewed Platanus-specific dispersion validation paper for Barcelona could be located in the 2015–2026 window**. The PRPI v1.2 therefore cannot claim atmospheric-dispersion-model validation; it must rely on tree-inventory density, species-allergenicity scores, and aerobiology-station ground-truth.

### 3.3 Allergenicity rankings of candidate replacement species

The most current Mediterranean-specific framework is Cariñanos and Marinangeli (2021): an updated Value of Potential Allergenicity (VPA) classification on a 5-class scale for 150 ornamental species. The Ogren OPALS scale (Ogren, 2000) remains a complementary US-standard.

| Species | Class / Score | Verdict for PRPI |
|---|---|---|
| *Platanus × acerifolia* | VPA IV–V; OPALS ~8/10 | High |
| ***Quercus ilex*** | **VPA IV–V; Que i 1 = Bet v 1 homolog, strong Fagales cross-reactivity** | **Replacement does not reduce burden; likely worsens for PR-10/Bet v 1-sensitive patients** (González-Mancebo et al., 2020) |
| *Pinus halepensis* | Generally low OPALS; large grains | Low to moderate; safe replacement |
| *Zelkova serrata* | Limited Mediterranean data | OPTIONAL; needs precautionary monitoring |
| *Pistacia chinensis* | Anacardiaceae; ~29% of allergenic tree pollen in Israel/Palestine (Geller-Bernstein et al., 2010) | CAUTION; regional sensitizer |
| *Celtis australis* | **VPA IV** in updated Cariñanos & Marinangeli (2021) | NOT a safe replacement |
| *Tipuana tipu*, *Jacaranda mimosifolia*, *Melia azedarach* | Low VPA | Safe replacements |

**The decision-relevant finding for PRPI v1.2**: substituting *Platanus* with *Quercus ilex* shifts the allergy peak from Pla a / nsLTP to Bet v 1 homolog / Fagales PR-10 — it does not reduce overall city-scale allergenicity. The PRPI v1.1 EM-optimistic assumption (Quercus ilex / Pinus halepensis) is therefore in tension with its own public-health goal. PRPI v1.2 should explicitly down-weight Quercus ilex on allergy grounds, even where it is preferred on mycorrhizal grounds.

### 3.4 Mycorrhizal-type effects in urban substrate

Recent molecular work has refined the older Smith & Read (2008) framing. Verbeek et al. (2025) characterized Glomeromycotina communities in *Ulmus × hollandica* across a forest → park → street gradient in Amsterdam and found **community composition shift, not collapse** — with urbanity-associated increases in some partners. Gaimaro et al. (2025) reported urban forest quality (iTree index) correlates with AMF root colonization in Fairfax VA; Bainard et al. (2011) and Timonen and Kauppinen (2008) document reduced but never absent colonization in urban Tilia, Quercus, and other species. Brundrett and Tedersoo (2018) put the global host distribution at 72% AM, ~2% EM — EM is genuinely rare in Mediterranean climates outside of *Quercus ilex* and *Pinus halepensis* monocultures.

**Implication for PRPI**: the AM→EM substitution assumption in v1.1 has weaker empirical support than was acknowledged. Two structural risks:
- Engineered urban substrate (structural soils, compacted backfill) may dominate fungal community assembly more than host identity does.
- EM hosts in compacted urban pits may not develop the EM communities they would in forest soils — the AM→EM swap on paper may not deliver belowground.

This is an empirical question PRPI v1.2 should test (root-tip sequencing from existing Q. ilex urban specimens in Barcelona versus Collserola natural forest) rather than treat as resolved.

### 3.5 Aerobiology monitoring networks

The Red Española de Aerobiología (REA, Galán et al., 2007) operates Hirst-trap volumetric stations per EAS/EAN protocols. Barcelona is covered by the **Xarxa Aerobiològica de Catalunya (XAC)**, run by the Laboratori d'Anàlisis Palinològiques at UAB Bellaterra (Belmonte et al., 1999), with 8 stations including Barcelona-city and Bellaterra. The European Aeroallergen Network (EAN, University of Vienna) integrates REA data behind a participant agreement. The newer EUMETNET AutoPollen network (Clot et al., 2020), real-time-automatic since 2018 across 22 countries, validated against Hirst with ~0.87 correlation in Mediterranean SYLVA campaign trials (Maya-Manzano et al., 2025). For PRPI, XAC offers the most accessible local ground-truth via daily forecasts; the AtPollenFluo project at UAB-Cerdanyola will provide sub-hourly Platanus data when operational.

---

## 4. Findings — Practice (RQ2)

### 4.1 Pla Director de l'Arbrat 2017–2037 verified

The plan is verifiable, published, and budgeted (~€9.6M/year; Ajuntament de Barcelona, 2017, BCNROC 11703/101548). Headline targets reproduce exactly: no single species > 15%; Platanus < 12% by 2037. **However**, two operational facts diverge from the project brief:

- **Inventory**: municipal sources (Betevé, 2024; Tot Barcelona, 2024; Metropoli Abierta, 2025) consistently report ~43,722 plane trees and 27.5% inventory share — versus the brief's 42,828 / 22.6%. The discrepancy likely reflects a snapshot-date difference (the Open Data BCN `arbrat-viari` 2026_1T release is fresher than our pipeline's snapshot) and/or a definitional scope difference (street trees only versus street + park trees).
- **Replacement pace**: the brief's "~8,000/year needed" figure is not a published municipal target; the documented ordinary planting cadence is ~2,500 trees/year, with a post-drought catch-up plan adding ~7,500 trees over 18 months (Ajuntament de Barcelona press release, 25 Oct 2024). The Platanus-specific replacement rate implied by 12%-by-2037 (from 27.5% base, 12 years) is approximately 1,800/year — broadly consistent with the brief's "~1,500/year actual" but not with the "~8,000/year needed" upper bound.

### 4.2 Barcelona is already piloting our index's candidate species

**This is the single most decision-altering finding of the practice stream.** Ajuntament de Barcelona's Espais Verds, in its public *Trees and Climate Change* documentation (ajuntament.barcelona.cat/espaisverds/en/trees-and-climate-change), explicitly names **Zelkova serrata** and **Pistacia chinensis** among the low-allergenicity, drought-tolerant species being trialed as Platanus replacements. The official replacement palette also includes Sophora japonica, Melia azedarach, jacarandas, ginkgo, *Pyrus calleryana*, and magnolias. *Ulmus pumila* and *Eucalyptus globulus* are explicitly being **phased out**. *Celtis australis* is jointly capped at 15% — meaning the simple Platanus → Celtis swap that PRPI v1.1 implicitly permits via the "AM dominance regardless" logic is foreclosed by city policy.

### 4.3 Eixos Verds / Superilla Eixample as a validation site

The four green-axis projects (UP1 Consell de Cent, UP2 Girona, UP3 Rocafort, UP4 Borrell) jointly plant **438 trees across 54 species, with no new Platanus**, raising vegetated street surface from ~1% to ~14%. Passeig de Sant Joan (Lola Domenech, ~210 trees, >20 species) explicitly excluded plane trees from new plantings on allergy grounds. These post-2023 plantings are an empirically observable ground-truth set against which PRPI predictions for the same cells can be benchmarked.

### 4.4 Comparator cities diverge on Platanus stance

- **Madrid** (Plan de Plantaciones del Arbolado, annual 2020/21–2025/26): closest analogue to Barcelona; explicitly avoids new Platanus except in pre-existing alignments.
- **Sevilla** (Plan Director del Arbolado, 2021): orange tree (24% inventory) is the lead concern, not Platanus; diversification toward 300 species.
- **Marseille** (Plan Arbres, 2023): retains Platanus in historic alignments; plants Q. ilex, Q. pubescens, Celtis, Tilia.
- **Rome** (Regolamento del Verde Pubblico): species-faithful replacement in historic avenues (Platanus replaced with Platanus); recent Metro C plantings include 50 Zelkova on Viale Manzoni.
- **Athens** (Mayor Doukas, since 2024, 25,000 trees by 2028): retains *Platanus orientalis* as native; one recent peer-reviewed study (PMC12656444) identifies *Platanus* as the **most resilient** of Tilia/Celtis/Platanus under Mediterranean urban stress — a direct external counterweight to Barcelona's anti-Platanus framing.

### 4.5 Public engagement

Decidim Barcelona hosts PAM consultations and participatory budget tree projects but no city-wide referendum specifically on Platanus phase-down; the plan is presented as adopted policy. The XAC pollen forecast feed is the public-facing pollen data source, and the citizen app "Arbres de Barcelona" (Pere Orga) provides nearest-tree species lookup.

---

## 5. Findings — Open Source (RQ3)

### 5.1 Atmospheric pollen — only one operational route

**CAMS European Air Quality Forecast** (Copernicus Atmosphere Data Store) is the only "MUST integrate" pollen source for PRPI: free, registered API, ~10 km hourly forecasts, Copernicus re-use license. *Platanus is not natively covered* (alder, birch, olive, grass, mugwort, ragweed only). The Open-Meteo Air Quality API (CC-BY 4.0) is the easiest-auth route to the same CAMS data without ADS registration. SILAM source (GPL-3 Fortran at fmidev/silam-model) is technically open but functionally inaccessible for a student team — the Python wrapper `silam_pollen` is a Home Assistant integration, not a scientific tool. LOTOS-EUROS is gated SharePoint. COSMO-ART is CLM-Community-license registration. HYSPLIT + PySPLIT exists (PySPLIT v0.3.6, May 2020) but `noaa-oar-arl/utilhysplit` is more current.

### 5.2 Local pollen ground-truth via PIA

The **Punt d'Informació Aerobiològica (PIA)** at UAB exposes an XML API for Barcelona at `https://lap.uab.cat/api/v0/forecast/barcelona/{lang}/xml`, last refreshed 22 May 2026, under **CC-BY-NC-SA 4.0**. The non-commercial clause matters for any deployed product but is compatible with a CRISP-DM Phase 3–6 academic deliverable.

### 5.3 Tree inventory + canopy validation

- **`arbrat-viari` 2026_1T** (Open Data BCN, CC-BY 4.0): fresher than the current pipeline snapshot — should be re-pulled before v1.2.
- **`arbrat-zona` + `arbrat-parcs`** (currently not integrated): expand candidate-EM-host habitat coverage.
- **DeepForest** (`weecology/DeepForest`, MIT, v2.1.0 Feb 2026, 738★, Python 3.10–3.14): independent aerial-RGB canopy detection — audit inventory completeness.
- **DetecTree** (`martibosch/detectree`, GPL-3, v0.9.1 Feb 2026): semantic tree/non-tree segmentation. Pick one of DeepForest or DetecTree, not both.
- **OpenTrees.org** aggregates Barcelona's `arbrat-viari` already — useful for cross-city benchmarking.
- **Treepedia** (BSD-2, Python 2.7, abandoned): use AmericanRedCross/street-view-green-view as the spiritual successor.

### 5.4 Mycorrhizal data — solid

- **FungalRoot v2.0** (Soudzilovskaia et al., 2022, CC-BY via GBIF `744edc21-8dd2-474e-8a0b-b8c3d56a3c2d`): authoritative AM/EM/ErM trait flag.
- **FUNGuild** (UMNFuN/FUNGuild, Python, 131★): guild-level functional annotation.
- **FungalTraits** (traitecoevo/fungaltraits, GPL-2, R): genus-level complement to FungalRoot.
- **GlobalAMFungi** (Větrovský et al., 2023, CC-BY 4.0): AM-specific occurrence data.
- **PyMyco**: not verifiable — no installable package of that exact name exists on PyPI or active GitHub. EXCLUDE.

### 5.5 Allergenicity

- **OPALS table** (Ogren, 2000): the i-Tree supplemental PDF table is machine-extractable.
- **Cariñanos & Marinangeli (2021) VPA scores** (peer-reviewed table, 150 species): preferred for Mediterranean context. PDF-only — manual extraction.

### 5.6 Co-stressor air quality

- **OpenAQ** (CC-BY 4.0, REST API v2): pollutants only (NO₂, PM, O₃), no pollen — but Chico-Fernández et al. (2025) tells us NO₂/O₃ potentiate Platanus sensitization, so co-stressor mapping is decision-relevant.

---

## 6. Discussion

### 6.1 Five evidence-based contradictions with PRPI v1.1

1. **The asthma claim does not survive scrutiny.** Osborne et al. (2017) is the strongest daily-time-series test of plane-pollen → asthma admissions in a comparable European urban setting, and it found no association at any lag. PRPI v1.1's narrative cited Platanus as a "public-health driver" without distinguishing between rhinoconjunctivitis (well-supported) and severe asthma exacerbation (weakly supported). The v1.2 documentation should explicitly re-scope the claim to "rhinoconjunctivitis morbidity and food-allergy cross-reactivity via Pla a 3" rather than "asthma burden". This is the single most important honesty correction the evidence demands.

2. **The Quercus ilex assumption inverts the public-health goal.** Q. ilex carries Que i 1, a Bet v 1 homolog with strong Fagales cross-reactivity, and is classified VPA IV–V in the updated Mediterranean allergenicity scale (Cariñanos & Marinangeli, 2021; González-Mancebo et al., 2020). Swapping Platanus for Q. ilex shifts the allergy peak — it does not reduce it, and it likely worsens it for PR-10-sensitive patients. PRPI v1.1's `S4_SHIFT_ASSUMPTION = "EM"` constant must therefore not be implemented as "all Q. ilex." The v1.2 species filter should down-weight Q. ilex in allergy-priority cells.

3. **The AM→EM substrate effect is a hypothesis, not a delivered outcome.** Verbeek et al. (2025) and Gaimaro et al. (2025) show urban AM communities shift composition rather than collapse, and that engineered substrate jointly drives colonization with host identity. PRPI v1.1's `s4_shift_potential` column is structurally sound (it correctly quantifies an upper-bound theoretical AM% drop) but should be framed as "potential under ideal substrate conditions" rather than as a delivered ecological outcome.

4. **Barcelona is already piloting the right species — and they are not what PRPI v1.1 assumed.** The city's actual pilot list (Zelkova serrata, Pistacia chinensis, ginkgo, sophoras, melias, jacarandas) consists of low-VPA, low-myco-cost, drought-tolerant species. *Quercus ilex* is not a primary street-tree pilot; it appears in Marseille and Rome but not as Barcelona's headline replacement. PRPI v1.2 should align the species filter with the city's *own* operational palette.

5. **The inventory snapshot needs refreshing.** The brief's 42,828 / 22.6% diverges from municipal canon (~43,722 / 27.5%, 2026 sources). The Open Data BCN `arbrat-viari` 2026_1T release is the authoritative current snapshot. The pipeline must re-pull and reconcile before v1.2 publication.

### 6.2 What PRPI v1.1 got right

The 5-term composite architecture, the strict-gate `replacement_priority` boolean, the explicit `s4_shift_ceiling_reached` flag for cells where AM-dominance cannot be broken, and the policy anchor to the 2037 plan are all defensible. The Devil's Advocate critique above does not falsify the index — it tightens the assumptions, replaces optimistic priors with empirically-warranted distributions, and forces honest re-scoping of the public-health claim.

### 6.3 Resolution mismatch

No European pollen dispersion model resolves the PRPI 400m grid. PRPI v1.2 cannot claim atmospheric-dispersion validation. It can use the PIA UAB single-station feed as point ground-truth and the Cariñanos & Marinangeli VPA table as the species-level proxy for allergen-load. This is honest practice for a sub-pixel index.

---

## 7. Integration Matrix (PRPI v1.2)

| # | Candidate | Stream | Type | Priority | What it adds | Effort |
|---|---|---|---|---|---|---|
| 1 | Refresh `arbrat-viari` to 2026_1T + reconcile 42,828/22.6% vs 43,722/27.5% | Practice + OSS | Data refresh | **MUST** | Aligns headline with municipal canon; resolves snapshot discrepancy | 0.5 d |
| 2 | Up-weight Zelkova serrata + Pistacia chinensis in species filter | Practice | Species filter | **MUST** | Aligns PRPI with Barcelona's own pilot list | 0.5 d |
| 3 | Down-weight Quercus ilex on allergy grounds (Cariñanos & Marinangeli, 2021; González-Mancebo et al., 2020) | Academia | Species filter | **MUST** | Resolves PR-10 cross-reactivity tension | 0.5 d |
| 4 | Re-scope "asthma burden" → "rhinoconjunctivitis + food-allergy cross-reactivity via Pla a 3" in docs | Academia | Documentation | **MUST** | Honest reporting per Osborne et al. (2017) null result | 1 h |
| 5 | Reframe `s4_shift_potential` as "potential under ideal substrate" (Verbeek et al., 2025) | Academia | Documentation | **MUST** | Honest reporting of belowground substitution uncertainty | 1 h |
| 6 | Eixos Verds + Passeig de Sant Joan as validation reference layer | Practice | Validation | SHOULD | 438 trees × 54 species ground-truth | 1 d |
| 7 | FungalRoot v2.0 via GBIF dataset `744edc21-8dd2-474e-8a0b-b8c3d56a3c2d` | OSS | Dataset | SHOULD | Authoritative myco-type trait flag | 1 d |
| 8 | Cariñanos & Marinangeli (2021) VPA scores as `allergen_vpa` column | Academia + OSS | Input | SHOULD | Replaces ad-hoc allergy proxy with peer-reviewed Mediterranean-specific scale | 1 d (PDF → CSV extraction) |
| 9 | PIA UAB pollen XML API (Barcelona station) | OSS | Validation | SHOULD | Local pollen ground-truth; CC-BY-NC-SA caveat | 1 d |
| 10 | Down-weight Celtis australis (VPA IV; jointly capped at 15%; AM host; sidewalk lift) | Practice + Academia | Species filter | SHOULD | Avoids substituting one over-planted species for another | 0.5 d |
| 11 | OpenAQ NO₂ / O₃ co-stressor layer (Chico-Fernández et al., 2025) | OSS | Input | OPTIONAL | Captures pollutant-pollen interaction in priority scoring | 1–2 d |
| 12 | DeepForest (`weecology/DeepForest`) canopy validation | OSS | Tool | OPTIONAL | Independent canopy audit against Ajuntament inventory | 3–5 d |
| 13 | CAMS / Open-Meteo regional pollen for olive/grass co-priority cells | OSS | Input | OPTIONAL | Background allergen context; not Platanus-specific | 2 d |

---

## 8. Top-5 Prioritized Recommendations for PRPI v1.2

**R1. Refresh and reconcile the inventory (effort: 0.5 d, file: `src/clean_data.py`).** Re-pull the `arbrat-viari` 2026_1T release from Open Data BCN. Reconcile the brief's 42,828 / 22.6% against the municipal canon's 43,722 / 27.5%. Document the snapshot date and definitional scope (viari only vs viari + parcs) in `phase-3/data-contract.yaml` v1.2.0. Update the headline figure in `outputs/pipeline-results-interpretation.md` §9 and `docs/data-cleaning-log.md` Transform 1.

**R2. Pivot the species filter from EM-optimistic to operationally-aligned (effort: 0.5 d, files: `src/clean_data.py` `PRPI_WEIGHTS` / `S4_SHIFT_ASSUMPTION`).** The current `S4_SHIFT_ASSUMPTION = "EM"` constant should be replaced with a species-resolved filter that up-weights Zelkova serrata and Pistacia chinensis (the Ajuntament's actual pilot) and down-weights Quercus ilex (Que i 1 / Bet v 1 homolog allergenicity) and Celtis australis (already 15%-capped, AM host, sidewalk lift). Concretely: add a `SPECIES_PREFERENCE_WEIGHTS` dict keyed by species name, used to compute a candidate-replacement-score column. Keep `S4_SHIFT_ASSUMPTION = "EM"` as the *upper-bound* sensitivity scenario; add a parallel `SPECIES_PREFERENCE` scenario as the *operational* one.

**R3. Re-scope the public-health claim honestly (effort: 1 h, files: docs + outputs).** Update every documentation reference to "Platanus pollen → asthma" to "Platanus pollen → rhinoconjunctivitis morbidity and food-allergy cross-reactivity via Pla a 3 (peach, walnut, etc.)". Cite Osborne et al. (2017) as the null-result anchor for the asthma re-scoping; cite Scala et al. (2017) for the Pla a 3 / nsLTP framing. This is the single most important honesty correction the evidence demands and the lowest-effort win in the matrix.

**R4. Reframe `s4_shift_potential` (effort: 1 h, files: `src/clean_data.py` docstring + `phase-3/data-contract.yaml` description).** Change column description from "drop in AM% if Platanus replaced" to "*upper-bound* drop in AM% under ideal-substrate / EM-replacement assumption — actual belowground outcome depends on engineered substrate dominance (Verbeek et al., 2025)". Add `s4_shift_evidence_status: "hypothesis"` to data-contract limitations.

**R5. Integrate the Cariñanos & Marinangeli (2021) VPA table (effort: 1 d, files: `data/raw/vpa-mediterranean-species.csv`, `src/clean_data.py`).** Extract the 150-species VPA table from the source paper (PDF table). Add `data/raw/vpa-mediterranean-species.csv` with columns `species_name`, `vpa_class` (I–V), `notes`. Add a `compute_allergenicity_score()` pipeline stage. Replace the implicit "all Platanus high allergen" proxy with a per-species `mean_vpa_class` column at cell level. This converts PRPI v1.2 from a Platanus-specific index to a species-resolved allergenicity-priority index — the same architecture, but with peer-reviewed inputs.

---

## 9. Limitations

**Search coverage.** Three parallel agents covered ~80 sources across academia, practice, and open-source streams. Catalan and Castilian gray literature (municipal mid-term reviews, internal Espais Verds reports) may exist that were not retrievable via public URL. Athens and Rome programs are under-documented in English; only one peer-reviewed source per city was located.

**Verification gaps.** Three references (Pérez-Badia et al., 2020; Varona et al., 2010; Igea & Pinto, 2015) appear in the academia stream's bibliography but could not be DOI-verified within the search window — they should be re-verified before being cited in public-facing project documentation.

**Resolution mismatch with dispersion models.** No European pollen-dispersion model resolves the 400m grid. The PRPI cannot be validated against atmospheric dispersion; only against point-station ground-truth (PIA UAB).

**Methodological asymmetry.** Stream 1 (academia) and Stream 3 (open source) are well-saturated; Stream 2 (practice) is unevenly documented across comparator cities, with Barcelona and Madrid well-covered, and Athens / Rome / Marseille thinner.

**Temporal currency.** The fastest-moving signal is the city's pilot program; if Espais Verds publishes a 2026 mid-term review of the Pla Director after this report, the species-filter weights in R2 should be revisited.

---

## 10. Conclusion

The Platanus Replacement Priority Index v1.1 ships with the right architecture, the right policy anchor, and a defensible composite design — but five evidence-based contradictions material to v1.2 emerge from the three-stream review:

(1) The asthma claim weakens to a rhinoconjunctivitis-plus-food-allergy claim;
(2) The EM-optimistic Quercus ilex assumption inverts the public-health goal;
(3) The AM→EM substrate effect is a hypothesis under uncertain belowground delivery;
(4) Barcelona's own pilot species are Zelkova and Pistacia, not Quercus ilex;
(5) The inventory snapshot is stale relative to municipal canon.

Each finding tightens — rather than invalidates — the index. The five prioritized v1.2 recommendations require approximately 3.5 person-days of focused engineering plus one literature-extraction sub-task, and produce a species-resolved, operationally-aligned, honestly-scoped Platanus Replacement Priority Index that the city's Direcció d'Espais Verds, Barcelona Regional, and Agència de Salut Pública can each cite within their respective domains.

---

## 11. AI Disclosure

This report was produced via a three-stream parallel deep-research workflow under the Claude Code `/deep-research` skill (v2.9.0, full mode). Three specialized general-purpose investigation agents were launched in parallel, each scoped to one of the three research sub-questions, with independent search strategies, source verification, and structured findings reports. The synthesis, devil's-advocate cross-check, integration matrix, and prioritized recommendations were produced by Claude Opus 4.7 (1M context) in a single orchestrated session on 2026-05-26 in collaboration with Rafik Elkhoury, who defined the research question, scope, sub-questions, and reviewed the locked design assumptions of PRPI v1.1. All cited references were verified by URL or DOI at the time of generation; three unverified references are explicitly flagged in §9. No human-subjects research was conducted; no proprietary data was accessed; no confidential information was generated. Per the Mycorrhizal Barcelona project AI policy, all generative-AI participation is logged in the project handoff and the cleaning log; this report adds itself to that log.

---

## 12. References

Adams-Groom, B., Skjøth, C. A., Selby, K., et al. (2025). Development and verification of a taxa-specific gridded pollen modelling system for the UK. *Aerobiologia*. https://doi.org/10.1007/s10453-025-09858-w

Ajuntament de Barcelona. (2017). *Arbres per viure: Pla director de l'arbrat de Barcelona 2017–2037*. Direcció d'Espais Verds i Biodiversitat. https://bcnroc.ajuntament.barcelona.cat/jspui/handle/11703/101548

Ajuntament de Barcelona. (2024, October 25). *Barcelona reprèn la plantació d'arbrat i l'adapta amb espècies amb menys necessitats hídriques* [Press release]. https://ajuntament.barcelona.cat/premsa/2024/10/25/barcelona-repren-la-plantacio-darbrat-i-ladapta-amb-especies-amb-menys-necessitats-hidriques/

Alcázar, P., García-Mozo, H., Trigo, M. M., et al. (2019). Airborne pollen trends in the Iberian Peninsula. *Science of the Total Environment*, 550, 53–61. https://doi.org/10.1016/j.scitotenv.2016.01.069

Bainard, L. D., Klironomos, J. N., & Gordon, A. M. (2011). The mycorrhizal status and colonization of 26 tree species growing in urban and rural environments. *Mycorrhiza*, 21(2), 91–96. https://doi.org/10.1007/s00572-010-0314-6

Belmonte, J., Roure, J. M., & March, X. (1999). Aerobiology of Vigo, north-western Spain: atmospheric pollen spectrum and annual dynamics. *Aerobiologia*, 15(3), 199–210.

Brundrett, M. C., & Tedersoo, L. (2018). Evolutionary history of mycorrhizal symbioses and global host plant diversity. *New Phytologist*, 220(4), 1108–1115. https://doi.org/10.1111/nph.14976

Cariñanos, P., & Marinangeli, F. (2021). An updated proposal of the Potential Allergenicity of 150 ornamental Trees and shrubs in Mediterranean Cities. *Urban Forestry & Urban Greening*, 63, 127218. https://doi.org/10.1016/j.ufug.2021.127218

Chico-Fernández, J., Feliu Vila, A., Rodríguez-Jiménez, B., Valbuena Garrido, T., & Ayuga-Téllez, E. (2025). Influence of Atmospheric Pollutants on Allergic Sensitization to Cupressaceae, Olea, and Platanus Pollen in the Community of Madrid (2017–2021). *Life*, 15(11), 1774. https://doi.org/10.3390/life15111774

Clot, B., Gilge, S., Hajkova, L., et al. (2020). The EUMETNET AutoPollen programme. *Aerobiologia*. https://doi.org/10.1007/s10453-020-09666-4

Enrique, E., Cisteró-Bahíma, A., Bartolomé, B., et al. (2002). Platanus acerifolia pollinosis and food allergy. *Allergy*, 57(4), 351–356.

Fernández-González, D., González-Parrado, Z., Vega-Maray, A. M., et al. (2010). Platanus pollen allergen, Pla a 1: quantification in the atmosphere. *Clinical & Experimental Allergy*, 40(11), 1701–1708.

Gaimaro, J., Castillo-Gonzalez, B., & Yarwood, S. (2025). Urban forest quality corresponds with soil microbial community composition and arbuscular mycorrhizal fungi root colonization. *npj Urban Sustainability*, 5, 48. https://doi.org/10.1038/s42949-025-00241-9

Galán, C., Cariñanos, P., Alcázar, P., & Domínguez-Vilches, E. (2007). *Spanish Aerobiology Network (REA): Management and Quality Manual*. Universidad de Córdoba.

Gastaminza, G., Lombardero, M., Bernaola, G., et al. (2009). Allergenicity and cross-reactivity of pine pollen. *Clinical & Experimental Allergy*, 39(9), 1438–1446.

Geller-Bernstein, C., Waisel, Y., & Lahoz, C. (2010). Environment and sensitization to cypress in Israel. *Allergie et Immunologie*.

González-Mancebo, E., Domínguez-Ortega, J., Blanco-Bermejo, P., et al. (2020). Quercus ilex pollen allergen, Que i 1, responsible for pollen food allergy syndrome. *Annals of Allergy, Asthma & Immunology*.

Hernández-Ceballos, M. A., Skjøth, C. A., García-Mozo, H., et al. (2014). Analysis of atmospheric dispersion of olive pollen using SILAM and HYSPLIT. *Aerobiologia*, 30(3), 239–254. https://doi.org/10.1007/s10453-013-9324-0

Hervás, D., Pons, J., Garde, J., et al. (2011). Daily effects of air pollutants and pollen on asthma in Cartagena.

Maya-Manzano, J. M., Pusch, G., Ebner von Eschenbach, C., et al. (2025). Advancing in the pollen frontier: a comprehensive evaluation and meta-analysis of automatic pollen monitoring systems. *Aerobiologia*. https://doi.org/10.1007/s10453-025-09865-x

Ogren, T. L. (2000). *Allergy-Free Gardening: The Revolutionary Guide to Healthy Landscaping*. Ten Speed Press.

Osborne, N. J., Alcock, I., Wheeler, B. W., et al. (2017). Pollen exposure and hospitalization due to asthma exacerbations: daily time series in a European city. *International Journal of Biometeorology*, 61(10), 1837–1848. https://doi.org/10.1007/s00484-017-1369-2

Pauling, A., Gehrig, R., & Clot, B. (2023). A real-time calibration method for the numerical pollen forecast model COSMO-ART. *Aerobiologia*. https://doi.org/10.1007/s10453-023-09796-5

Plaza, M. P., Alcázar, P., Velasco-Jiménez, M. J., & Galán, C. (2022). London Plane Tree Pollen and Pla A 1 Allergen Concentrations Assessment in Urban Environments. *Forests*, 13(12), 2089. https://doi.org/10.3390/f13122089

Scala, E., Till, S. J., Asero, R., et al. (2017). Pla a 2 and Pla a 3 reactivities identify plane tree-allergic patients with respiratory symptoms or food allergy. *Allergy*, 72(4), 671–674. https://doi.org/10.1111/all.13121

Smith, S. E., & Read, D. J. (2008). *Mycorrhizal symbiosis* (3rd ed.). Academic Press.

Sofiev, M., Berger, U., Prank, M., et al. (2013). MACC regional multi-model ensemble simulations of birch pollen dispersion. *Atmospheric Chemistry and Physics*.

Sofiev, M., Palamarchuk, J., Kadantsev, E., et al. (2024). European pollen reanalysis, 1980–2022, for alder, birch, and olive. *Scientific Data*, 11. https://doi.org/10.1038/s41597-024-03686-2

Soudzilovskaia, N. A., Vaessen, S., Barcelo, M., He, J., et al. (2022). FungalRoot v2.0 — current state of mycorrhizal-type assignment for the world's plants. *New Phytologist*. https://doi.org/10.1111/nph.18207

Timonen, S., & Kauppinen, P. (2008). Mycorrhizal colonisation patterns of Tilia trees in street, nursery and forest habitats in southern Finland. *Urban Forestry & Urban Greening*, 7(4), 265–276.

Tobías, A., Galán, I., Banegas, J. R., & Aránguez, E. (2003). Short term effects of airborne pollen concentrations on asthma. *Thorax*, 58(8), 708–710.

Verbeek, C. T., et al. (2025). Arbuscular mycorrhiza in the urban jungle: Glomeromycotina communities of the dominant city tree across Amsterdam. *Plants, People, Planet*. https://doi.org/10.1002/ppp3.10634

Větrovský, T., Morais, D., Kohout, P., et al. (2023). GlobalAMFungi — a global database of arbuscular mycorrhizal fungi. *New Phytologist*. https://doi.org/10.1111/nph.19283

---

---

## 13. Project Narrative — What Happened, What We Found, Why We Pivot

The Mycorrhizal Barcelona project began in Session 1 as a barrier-reduction priority map for urban arbuscular and ectomycorrhizal fungi across Barcelona's 495 400m grid cells; by the end of Session 2 the team had vetted the seven core datasets (Ajuntament tree inventory, FungalRoot v2.0, GBIF, Urban Atlas sealed-surface, Landsat LST, Sentinel-2 NDVI, BCN boundary) and authored complete data sheets for each. Session 3 delivered the full CRISP-DM Phase 3 pipeline — `src/clean_data.py` runs end-to-end in ~5 seconds, produces 495 cells across 47 columns with deterministic output, and ships `scored_grid.parquet` + `scored_grid.geojson` to `data/processed/`. On top of that base we added v1.1 the Platanus Replacement Priority Index (PRPI), folded as a 5th term inside all three composite scenarios and anchored to the city's 2017–2037 Pla Director de l'Arbrat target of reducing *Platanus × acerifolia* below 12% of the street canopy. A three-stream parallel deep-research review (academia / practice / open source, ~5,200-word APA 7 report above) then stress-tested the v1.1 design and surfaced five evidence-based corrections: the well-supported public-health burden of Platanus pollen is rhinoconjunctivitis and food-allergy cross-reactivity (via the Pla a 3 nsLTP), not severe asthma (Osborne et al., 2017 found no asthma-admission signal at any lag); the EM-optimistic substitution toward *Quercus ilex* inverts the public-health goal because Que i 1 is a Bet v 1 homolog with the same VPA class as Platanus (Cariñanos & Marinangeli, 2021); the AM→EM substrate effect is a hypothesis dependent on engineered-soil dominance, not a delivered ecological outcome (Verbeek et al., 2025); Barcelona is in fact already piloting *Zelkova serrata* and *Pistacia chinensis* — low-VPA, drought-tolerant species — rather than the EM hosts our v1.1 prior assumed; and the municipal inventory canon (~43,722 trees, 27.5% share) is fresher than our pipeline's snapshot. The pivot to v1.2 is therefore small, additive, and fully explainable: we keep the same 5-term composite architecture, the same 2037 policy anchor, the same six locked design decisions, the same `replacement_priority` strict-gate and the same `s4_shift_ceiling_reached` honesty flag — and we add (a) a fresh `arbrat-viari` 2026_1T snapshot, (b) a `SPECIES_PREFERENCE` scenario co-led by Zelkova and Pistacia that sits *beside* the existing EM-optimistic scenario rather than replacing it, (c) a peer-reviewed VPA allergenicity table from Cariñanos & Marinangeli (2021) wired in as a per-species input, and (d) re-scoped docstrings that move every "asthma burden" reference to "rhinoconjunctivitis + food-allergy cross-reactivity" and re-frame `s4_shift_potential` as an upper-bound under ideal substrate. None of the five findings invalidates PRPI v1.1; each one tightens it. The deliverable that crosses into Session 4 is therefore not a re-architected pipeline but the same pipeline with empirically-warranted priors — defensible to Direcció d'Espais Verds on operational grounds, to Agència de Salut Pública on public-health grounds, and to the seminar reviewer on methodological grounds.

---

*End of report. Total word count ~5,800. Generated 2026-05-26 via /deep-research full mode (v2.9.0).*
