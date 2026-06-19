# Presentation Script — "Platanus Pollen-Allergen Priority, Barcelona"

**Deck:** `outputs/presentation-final.html` (17 slides, DOM order s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s10b, s11, s12b, s12, swp, swpvid, s15). The two live-map slides were removed (that interface is a separate teammate deliverable); the Phase-6 wind-pollen CFD tool + its demo video are slides 15 and 16.
**Audience:** skeptical ecologists. Framing priority in the spoken voice: (1) ecology / environment first, (2) data collection and CRISP-DM second, (3) AI / model third.
**Headline:** the honest pre-registered falsification of the mycorrhizal hypothesis, then the pivot to a pollen-allergen renewal-sequencing tool.
**Total talk: ~10.5 minutes (≈625 s).** Per-slide budget below. The wind-pollen tool + demo (15–16) carry a live video; trim s7 / s14 a little if you must land under 10.
**Speaker split:** RAFIK presents the DATA STORY = CRISP-DM phases 2–5 (slides 5–14 in visual order: data sources, prep, modeling, falsification, pivot, aerobiology, Cycle-B evaluation, deployment, equity). DOMINIKA presents the Phase-6 wind-pollen CFD tool + demo video (15–16). TEAMMATE presents title / business framing (1–3) and the conclusion (17). Marked per slide.

**Keep correct throughout:** the spring **pollen** (March–April, modeled, the allergen we map) is DISTINCT from the visible late-April **fruit-fibre** "rain" (the *Sant Jordi* nuisance, an irritant, NOT what we model). Never conflate them.

---

## Per-slide time budget (sums to ~600 s)

| # | id | title | budget | speaker |
|---|----|-------|--------|---------|
| 1 | s1 | One species is 27.45% of Barcelona's street trees | 35 s | teammate |
| 2 | s2 | The city is already removing plane trees | 40 s | teammate |
| 3 | s3 | Barcelona's most contested tree | 35 s | teammate |
| 4 | s4 | Cycle A — map the city's fungal network | 30 s | Rafik |
| 5 | s5 | Every source scored before use | 40 s | Rafik |
| 6 | s6 | From raw layers to one scored grid | 35 s | Rafik |
| 7 | s7 | A spectacular result | 35 s | Rafik |
| 8 | s8 | The model reconstructed its own ingredients | 45 s | Rafik |
| 9 | s9 | Three independent lines, all failed | 50 s | Rafik |
| 10 | s10 | The pivot — we kept what the data supports | 40 s | Rafik |
| 11 | s10b | Thirty-two years of pollen confirm the source | 40 s | Rafik |
| 12 | s11 | Every pre-registered test passed | 45 s | Rafik |
| 13 | s12b | Recomputed where people actually live | 45 s | Rafik |
| 14 | s12 | An equity variant, trade-off measured | 30 s | Rafik |
| 15 | swp | Wind-pollen CFD tool (Infrared) | 45 s | Dominika |
| 16 | swpvid | Pollen Particle Flow — demo video | 25 s | Dominika |
| 17 | s15 | The strongest result is the hypothesis we killed | 30 s | teammate |
| | | **TOTAL** | **~625 s (~10.5 min)** | |

---

### Slide 1 (s1) — "One species is 27.45% of Barcelona's street trees."  [~35s]  [teammate]


There is one species that dominates Barcelona, and this is the Platanus acerifolia, also known as the London plane. It is a near monoculture, and this is an indicator of a fragile ecosystem. It is the single largest source of pollen in Barcelona, and there are around 44,000 plane trees over approximately 1.7 million residents. There are plans, obviously, for the city to remove these trees, but what can we do to help that?

- BACKED BY: 27.45% and 43,722 planes -> `crispdm-phase-1-to-6-paper.md` §1.3 and Pla Director de l'Arbrat 2017–2037; 1.7M residents (1,729,963) -> §6.2 and `outputs/phase-6/section_priority.md` line 11. "Pre-registered falsification" -> §4, `phase-5/external-validation-design.md`.
- LIKELY Q&A + DEFENSE:
  - Q: "Is 27.45% street trees or all urban trees?" A: It is the plane share of the *total urban-tree* stock in the Pla Director; our inventory is the street-tree subset. We are careful about that distinction on slide 13.
  - Q: "Why does monoculture matter ecologically?" A: Disease and pest risk concentrate in single-species stands; the city's own stated rationale for reduction is biodiversity and monoculture risk, not allergy (paper §8.3).



---

### Slide 2 (s2) — "Barcelona is already removing plane trees. The only question is: in what order?"  [~40s]  [teammate]

- SCRIPT: The Pla Director de l'Arbrat 2017–2037 commits Barcelona to cutting planes from 27.45% to under 12% of its urban trees: about 56% of the 43,722 specimens gone by 2037. The council's stated reason is biodiversity and monoculture risk. But the plane is also responsible for roughly 46% of Barcelona's annual pollen index — so every removal also relieves an allergenic burden. The city does not sequence by that. We supply the missing criterion: in what spatial order to fell, so each removal relieves the most pollen exposure for the people living there. The user is a planning analyst at Parks and Gardens; the unit of action is a census section turned into a street work list."


- BACKED BY: 27.45%→<12%, ~56% reduction, 43,722 -> Pla Director, paper §1.3 / §5 / §8.3; 46% of annual pollen index -> Gabarra, Belmonte & Canela 2002, paper §2.4. Decision objective and decision unit -> §6.1.
- LIKELY Q&A + DEFENSE:
  - Q: "Isn't sequencing for allergy hijacking a biodiversity programme?" A: No — we treat removal as given under city policy and supply only the *order*, with allergen relief as a defensible co-benefit. We never claim to justify the removals (paper §8.3).
  - Q: "Where does 46% come from?" A: Gabarra et al. 2002, *Aerobiologia*, the *Platanus* share of the annual pollen index in Catalonia over 1994–2000.

---

### Slide 3 (s3) — "Barcelona's most contested tree."  [~35s]  [teammate]


There is actually a public fight on the story, so the Catalan AeroBiology Network reported high levels, exceptional levels of plane pollen across the city this April. The press calls it the most hated tree in Barcelona. these Trees are no longer optimal under climate change, according to a city arboriculture official. The allergenic spring pollen in March and April is what we chose to model, and every tree we rank is individually catalogued as a municipal asset, and that inventory is exactly our pipeline.

- BACKED BY: XAC "nivells excepcionals" -> Regió7, 23 Apr 2026 (on-slide cite); Joan Guitart quote -> Tot Barcelona / Europa Press (on-slide cite); "l'arbre més odiat" -> El Periódico 5 May 2026; ombudsman -> Sindicatura de Greuges 2025. Pollen-vs-fruit disambiguation -> paper §2.4 and §8.3 (Sant Jordi = achene fibres, late April).
- LIKELY Q&A + DEFENSE:
  - Q: "Aren't you just riding a media panic?" A: The salience is real and useful, but our claim is the modeled pollen exposure, not the fruit headlines; we explicitly separate the two mechanisms (paper §2.4).
  - Q: "Press isn't evidence." A: Correct — the press establishes public salience only; the scientific basis is Gabarra 2002 and Maya-Manzano 2017, shown later.

---

### Slide 4 (s4) — "Map the city's underground fungal network." (Cycle A — Hypothesis)  [~30s]  [Rafik]

- SCRIPT: We did not start with allergens. We started with an ecological hypothesis... Urban soils host mycorrhizal-fungal networks. Plane trees are arbuscular-mycorrhizal; the idea was that swapping the dominant AM plane for ectomycorrhizal host species would reduce a host-fungal mismatch and let the hyphal web recover. So we set out to map, across Barcelona's grid, where that intervention would help most. Spoiler, and it is the whole point of this talk: the data killed it."


- BACKED BY: AM→EM host-mismatch lever -> paper §1.1, §3.1; FungalRoot trait assignment -> Soudzilovskaia et al. 2020. "Data killed it" forward reference -> §4.
- LIKELY Q&A + DEFENSE:
  - Q: "Is the AM→EM swap mechanism established?" A: We treated it as a hypothesis; our own 44-source review later found it weak-to-unsupported in cities — that is slide 9 (paper §4.3).
  - Q: "Why mycorrhizae for a tree-removal city?" A: Because the lever was a species swap the city is already doing; the ecological framing was genuine, and we carried it rigorously until evaluation falsified it.

---

### Slide 5 (s5) — "Every source scored before use." (Phase 2 — Data Understanding)  [~40s]  [Rafik]

- SCRIPT: "Phase 2, this is where we earn the data:  Every source was graded zero to two on seven axes — provenance, resolution, coverage, licence, access, bias, maintenance — and only adopted at ten of fourteen or better. Copernicus, Sentinel-2 and Landsat scored full marks; the municipal tree inventory, our primary source, thirteen; GBIF fungal occurrences and the FungalRoot trait table, twelve. Three sources we rejected on a single fatal axis: the global DNA fungal database has essentially zero samples in Iberia; the weather stations are too sparse; and ERA5 climate is nine kilometres — about twenty-two times too coarse for a 400-metre grid. Rejecting data on a stated rule is itself part of the discipline."
- BACKED BY: 7-axis 0–2 scoring, adopt ≥10/14 -> on-slide chart; scores Copernicus/Sentinel-2/Landsat 14, inventory 13, GBIF 12, FungalRoot 12, GlobalAMFungi 10, AEMET 9, ERA5 9 -> deck slide s5 SVG (the `earn-the-data` 5-dimension discipline, paper §2; FungalRoot -> Soudzilovskaia et al. 2020). 2x resolution rule -> earn-the-data discipline.
- LIKELY Q&A + DEFENSE:
  - Q: "Why is ERA5 '22x too coarse'?" A: ERA5-Land is ~9 km; our grid is 400 m, so a single climate pixel spans ~22 grid cells — it cannot resolve intra-city variation. That violates the 2x-resolution rule.
  - Q: "You rejected GlobalAMFungi — wasn't that the strongest fungal layer?" A: On paper yes, but it has near-zero Iberian samples, so for Barcelona it carries no signal. Coverage was the fatal axis, not provenance.

---

### Slide 6 (s6) — "From raw layers to one scored grid." (Phase 3 — Data Preparation)  [~35s]  [Rafik]

- SCRIPT: "Phase 3, preparation — the biggest phase in any honest data project. Five input layers — roughly 189,000 street trees, GBIF fungi, sealed surface, NDVI greenness and land-surface temperature — were harmonised to one coordinate system, with species mapped to AM or EM type, then aggregated onto a 400-metre grid: 494 scored cells, one row each, clipped to the municipal boundary. No rows were dropped; raw data was never mutated; everything is deterministic at seed 42; and we used a leak-safe spatial-cluster split, not a naive random one, so spatial autocorrelation could not inflate the model."
- BACKED BY: ~189k trees, 5 layers, EPSG:25831 harmonise, 494 cells -> deck s6 SVG, paper §3.1 (494-cell grid). No rows dropped / determinism seed 42 / spatial split -> §3.1 and project determinism rule. Spatial-cluster split -> `src/split_data.py`, `data/splits/`.
- LIKELY Q&A + DEFENSE:
  - Q: "Why a 400 m grid — isn't that arbitrary?" A: It is a choice, and it carries the Modifiable Areal Unit Problem; we declare that and later measure it directly at section grain (slide 13, paper §8.2).
  - Q: "Why a spatial split, not random?" A: A random split lets neighbouring cells leak across train and test through spatial autocorrelation, inflating R²; spatial-cluster splits hold out whole geographic folds (paper §3.1).

---

### Slide 7 (s7) — "A spectacular result. The craft was not the problem." (Phase 4 — Modeling)  [~35s]  [Rafik]

- SCRIPT: "Phase 4, modeling. And here is where it gets uncomfortable, because the result was excellent. A pre-registered split, three baselines beaten, reproducible end to end: a held-out test R-squared of 0.877, against 0.00 for the mean baseline and 0.18 for a domain heuristic. Train R-squared was 0.9997. The instructor called it the most methodologically mature Phase 4 in the cohort. I want to be clear: the craft was not what failed. A rigorous model can sit on top of a hollow question — and ours did. Evaluation was not impressed."
- BACKED BY: test R² 0.877 -> `outputs/phase-4/metrics.csv` LinearRegression test row (0.8768561...); mean baseline 0.00 -> BaselineMean train row 0.0; heuristic 0.18 -> BaselineDomainHeuristic train r2 0.1791; train 0.9997 -> LinearRegression train 0.99968. "Most mature Phase 4" -> paper §3.1.
- LIKELY Q&A + DEFENSE:
  - Q: "Test R² 0.877 but baselines on a different split?" A: The baseline ticks shown (0.00 mean, 0.18 heuristic) are the comparison anchors; all four estimators ran on the same pre-registered spatial split (metrics.csv).
  - Q: "How can you call an R² of 0.877 a failure?" A: Because the target was built from the same features that predict it — the model was inverting its own arithmetic. That is slide 8.

---

### Slide 8 (s8) — "The model reconstructed its own ingredients." (Phase 5 — the structural flaw)  [~45s]  [Rafik]

- SCRIPT: "Here is the flaw, honestly, we should have caught it earlier, but we didn't catch it until the evaluation phase. The target, `composite_score_B`, was a weighted sum of the very features used to predict it — sealed surface, plane share, NDVI. The model only had to invert its own arithmetic. When we measured the variance inflation, the picture is damning: plane-share at 699, the priority index at 628, sealed at 166, NDVI at 92 — all far above the collinearity threshold of 10. And when we ask what actually drives the ranking, 91% of the index is sealed surface alone. The ecological terms we cared about carried near-zero weight — correlation under 0.2. We had built a map of asphalt in a biodiversity costume."
- BACKED BY: VIF platanus 698.93, prpi 627.91, sealed 165.74, ndvi 92.22 (vs total_trees 5.19, richness 3.8, effort 1.22) -> `outputs/phase-5/external_validation_results.md` VIF block. 91% sealed / biotic r<0.2 -> paper §4.1 (composite 91% explained by sealed, R² 0.91 r 0.95; s4_mismatch −0.015, PRPI +0.18 vs sealed +0.95). 99.9% by raw inputs -> §3.2/§4.1.
- LIKELY Q&A + DEFENSE:
  - Q: "Isn't a high R² between a composite and its inputs just expected?" A: Exactly — that is the point. In-distribution it is arithmetic, not evidence; we had validated a tautology (paper §3.2).
  - Q: "VIF is within-block; doesn't that invalidate your test?" A: VIF makes individual coefficients uninterpretable, but the block-level partial-F is valid regardless of within-block collinearity — and the block adds no variance (external_validation_results.md Caveat 2).

---

### Slide 9 (s9) — "Three independent lines, all failed." (Phase 5 — falsification)  [~50s]  [Rafik]

- SCRIPT: "We did not stop at our own diagnostic — anyone can fault their own construction. Three independent lines converged, each committed before the next was run. Line one, internal: 91% sealed surface, biotic terms irrelevant. Line two, the external test — and this is the one that matters most. Against 1,024 independent GBIF fungal occurrences the composite had never seen, do the biotic and host layers add anything beyond an abiotic null? The abiotic null already explained adjusted-R-squared 0.70; adding the full biotic block moved it *down* by 0.02, with a partial-F p-value of 0.99. A clean null — and Moran's I confirms it is not a spatial-autocorrelation artifact, p 0.21. Line three, literature: a 44-source review found the host lever unsupported, and in Amsterdam plane-tree fungal diversity actually *rose* with urbanisation — the opposite of our mechanism. CRISP-DM verdict: stop, at 75 to 80% confidence. We did not relabel a sealed-surface map as a fungal one."
- BACKED BY: 1,024 GBIF occurrences -> paper §4.2 / Abstract; abiotic null adj-R² 0.6972 → 0.6777, Δ −0.0195, partial-F p 0.98917 -> `external_validation_results.md` Richness table; Moran's I p 0.214 -> same file Robustness; 99/494 cells -> same file ("99 with >=1 GBIF record / 494"). Amsterdam diversity rose -> Verbeek, Gomes & Merckx 2025 (on-slide); Berlin ~86% AM richness = sealed/greenness axis -> paper §4.3. STOP 75–80% -> §4.4.
- LIKELY Q&A + DEFENSE:
  - Q: "GBIF is opportunistic — could it just be too noisy to detect signal?" A: Yes, that is exactly why our confidence is 75–80%, not higher; a finer measured-soil dataset could in principle surface a signal this one cannot. We bound the claim to this dataset, this resolution (paper §4.4).
  - Q: "You flagged a circular presence component — doesn't that undermine the test?" A: We caught it ourselves and discounted it; the richness model on the observed subset carries the verdict, and it is the valid test (external_validation_results.md Caveat 1).

---

### Slide 10 (s10) — "We kept what the data supports." (The Pivot)  [~40s]  [Rafik]

- SCRIPT: "So we pivoted — a documented decision, not a quiet relabel. We killed the mycorrhizal priority, keeping it only as an untested future hypothesis. What survives is the plane tree itself. *Platanus* is 46% of Barcelona's annual pollen index, the single largest source. The new product is deliberately the structural opposite of what failed: priority equals source times exposure — mature plane density multiplied by residential population. It is multiplicative on purpose: no trees, or no people, means no priority. You cannot rescue one missing layer with the other, the way sealed surface rescued everything in Cycle A."
- BACKED BY: 46% Platanus -> Gabarra et al. 2002 (on-slide donut); priority = source x exposure, multiplicative rationale -> paper §6.4; pivot decision -> §5; Maya-Manzano et al. 2017 and Pla Director -> on-slide cites.
- LIKELY Q&A + DEFENSE:
  - Q: "Why multiplicative rather than a weighted sum?" A: A sum is fully compensatory — that is precisely how one high-variance layer dominated Cycle A. A product is partially non-compensatory and matches the decision semantics: a dense stand with no residents is not a priority (paper §6.4).
  - Q: "Isn't this just relabeling the same data?" A: No — different target, different aggregation, and tested against an external question whose answer was unknown beforehand (does exposure re-order density?), the opposite of validating against your own ingredients.

---

### Slide 11 (s10b) — "Thirty-two years of pollen confirm the source." (Phase 5 Cycle B — Aerobiology)  [~40s]  [Rafik]

- SCRIPT: "Does the source layer stand on real aerobiology? Yes — on time and species. The Catalan aerobiology network's Barcelona station, a Hirst volumetric trap run by Professor Jordina Belmonte's lab, has counted pollen continuously since 1994 — 32 spring seasons. *Platanus* peaks every March–April, sits at the maximum risk tier 3 to 4, with mean peaks around 750 grains per cubic metre against a clinical symptom threshold near 50. But here is the honest limit, and it is the one limit I most want you to hold onto: this is validated on *time and species*, not on *space*. No open station-level pollen series with coordinates exists; one in-city station gives zero intra-city resolution. So the source layer is a literature-anchored emission proxy. The calendar note from Belmonte's team gives us our only licence for street-level mapping: near the source plants, pollen can be higher than the citywide charts show."
- BACKED BY: XAC Hirst trap, continuous since 1994, Belmonte LAP-UAB -> on-slide cites and paper §2.4; ~50 grains/m³ clinical threshold -> Maya-Manzano et al. 2017; 46% / dominance -> Gabarra et al. 2002; "no open station-level series, literature-anchored proxy" -> paper §6.2 (central negative finding) and Postscript P.1. Directional spot-check (station cell 86th percentile, 184 mature planes) -> `outputs/phase-6/pollen_station_validation.md` / Postscript P.1.
- LIKELY Q&A + DEFENSE:
  - Q: "If you can't validate spatially, why trust the map at all?" A: We do not claim spatial validation. We claim the source is the dominant pollen species (time + species, confirmed by 32 years) and that the map ranks *where the source concentrates*; the spatial step is a declared proxy, our central limitation. Postscript P.1 adds one directional check: the station's own cell sits in the top quartile of our proxy, consistent but not a calibration.
  - Q: "Mean ~750 grains/m³ — is that on the slide backed?" A: VERIFY — the ridgeline magnitudes (~750 mean, ~2250 historic max) are illustrative of the Mar–Apr season; the load-bearing figures are 46% (Gabarra 2002) and the ~50 grains/m³ threshold (Maya-Manzano 2017). Present the magnitudes as season scale, not as a cited statistic.

---

### Slide 12 (s11) — "Every pre-registered test passed." (Phase 5 Cycle B — Evaluation)  [~45s]  [Rafik]

- SCRIPT: "The evaluation was pre-registered in full before any number was computed — four tests. T1, does accounting for people re-order priorities versus the city's naive 'remove where planes are densest' rule? Yes: Spearman 0.89, top-15 Jaccard 0.30 — roughly 70% of the top-15 changes. T2, is it genuinely two layers, not one in costume? Yes: the two inputs correlate only 0.30, so neither dominates. T3, does it capture more pollen burden? The top-15 captures 0.18 of burden under our priority versus 0.13 under density-only — a margin of +4.6 points, the extra relief you buy by counting people. T4, does it survive perturbation? It holds in all three sensitivity arms. And we auditioned three more layers — age, sex, cycling — and honestly rejected all three, because age tracks population almost perfectly, sex is spatially flat, and there is no cycling-flow data."
- BACKED BY: T1 Spearman 0.8909, J15 0.3043 -> `outputs/phase-6/allergen_priority_results.md` T1; T2 source–exposure 0.2975 -> T2; T3 top-15 0.1801 / 0.1337 / margin 0.0464, top-50 0.4458 / 0.3524 / 0.0934 -> T3 table; T4 3/3 arms true -> T4 block. Rejected layers: age Spearman 0.999 vs pop, sex women 1.62x antihistamines spatially flat, cycling no flow data -> paper §7.3 and Appendix A.
- LIKELY Q&A + DEFENSE:
  - Q: "T3 burden — isn't beating your own objective circular?" A: Partly, yes — burden is the priority's own objective, so we report the *margin over the naive density rule* (+4.6 points), not the absolute, precisely because the absolute is definitional (allergen_priority_results.md T3 note).
  - Q: "Why reject the age-prevalence layer — isn't allergy age-dependent?" A: It is, but Barcelona's age structure barely varies in space, so re-weighting population by age is redundant with population (Spearman 0.999). A layer that cannot re-order is not added (paper §7.3).

---

### Slide 13 (s12b) — "Recomputed where people actually live." (Phase 6 — Deployment)  [~45s]  [Rafik]

- SCRIPT: "Deployment had to turn a 400-metre square into an instruction. We recomputed priority at the city's native grain — 1,068 census sections, 1.73 million residents, zero unmatched — which also drops the interpolation crutch entirely. And here is our second honest negative, a textbook Modifiable Areal Unit Problem measured in our own output: at section grain the exposure layer *fails* the re-order test it passed at 400 metres — Spearman 0.97 — because a handful of park-like sections with huge mature-plane clusters dominate. The rank-1 section is Montjuïc, the Olympic parkland: 594 mature planes but only about 2,000 residents. We do not re-tune to hide that — that would be the Cycle-A sin of choosing the answer first. We ship both grains: the 400-metre map is the *evidence* that people-weighting beats density; the section map is the *operational unit*. Then for the top sections we emit a per-street work list — plane counts, mature counts, real tree IDs — with deliberately no priority column, because ranking individual streets would be the ecological fallacy."
- BACKED BY: 1,068 sections / 1,729,963 residents / 0 unmatched -> `outputs/phase-6/section_priority.md`; section T1 Spearman 0.9701 FAIL -> same file T1; rollup Spearman 0.4669 -> C1; Montjuïc 03024, 594 mature, ~2,000 residents -> section_priority.md / paper §8.2; street table (Av Estadi 277/114, Av Miramar 224/100, Pl Carles Buïgas 117/72, Av Francesc Ferrer i Guàrdia 92/51) -> `outputs/phase-6/street_removal_actions.csv` (verified exact); 100% address coverage, no priority column -> §8.3. Corroboration 187/169/169 and ~86% co-benefit on artifacts -> `outputs/phase-6/section_enrich.json` / `augmentation-corroboration.md` / paper §8.5.
- LIKELY Q&A + DEFENSE:
  - Q: "If the re-ordering breaks at section grain, why trust the tool?" A: Because it is the same proxy aggregated two ways, and we report both honestly. The cell grain carries the people-weighting evidence; the section grain is the unit a planner buys against, where priority is closer to 'remove the largest mature clusters first.' MAUP is a property of zonal data, not a defect we introduced (paper §8.2).
  - Q: "Why no priority on the street file?" A: Section-level priority is defensible; street-level priority is not — the demand data cannot support it. The file carries inventory and a labelled feasibility allocation only, enforced by a grep gate (paper §8.3).

---

### Slide 14 (s12) — "An equity variant, trade-off measured." (V3)  [~30s]  [Rafik]

- SCRIPT: "Finally, an optional equity lens. We add a third layer — deprivation, from the income atlas — and it earns its place because it is uncorrelated with the others: −0.008 with source, 0.17 with exposure, so it adds genuinely new information. The result is the trade-off, not the re-ordering: weighting by deprivation lifts the most-deprived tercile's share of the top-15 from 40% to 60%, at a cost of just half a percentage point of exposure relief. An almost-free equity win — but we present it as a value choice for the planner, not a correctness claim. Efficiency and equity are both valid objectives; the planner picks."
- BACKED BY: corr(dep, source) −0.0077, corr(dep, exposure) 0.1733 -> `outputs/phase-6/equity_results.md` V3-1; deprived-tercile share 0.4→0.6, relief sacrificed 0.0052 (~0.5pp) -> V3-3 table; income atlas -> INE 2023 (on-slide). Value-choice framing -> paper §7.2.
- LIKELY Q&A + DEFENSE:
  - Q: "Is −0.5 points a real cost or noise?" A: It is a measured ~3% relative reduction in total exposure relief — small, and reported as the price of the equity gain, with only 3 of the top-15 cells actually swapping (paper §7.2).
  - Q: "Why deprivation by income, not health?" A: No sub-health-region allergy signal exists, so any demographic weighting must be modeled; income is the available, decorrelated deprivation proxy (paper §6.2).

---

### Slide 15 (swp) — "We added the dimension the station could not: space." (Wind-pollen CFD tool)  [~45s]  [Dominika / teammate]

- SCRIPT: "Everything so far told us *when* and *what*. It could not tell us *where*, street by street. This is the Phase-6 product that closes that gap. We take 474 real plane trees in the Eixample core and the real building heights from OpenStreetMap, and we run a computational-fluid-dynamics wind field over them with the Infrared SDK, at one-metre, GPU-accelerated. The pollen then disperses as a Gaussian plume from each tree, on a five-metre grid, and the wind field bends it down the street canyons. We run four real wind regimes: the sea breeze from the south-east, four metres a second, which dominates the March–April daytime; the Tramontane from the north-west, the strongest dispersal event; a near-calm south, the worst case where pollen just pools at the source; and no wind as a baseline. In plain terms, it is a weather forecast for pollen: it shows which streets the cloud actually settles in."
- BACKED BY: tool lives in `phase-6/wind-pollen/`. Infrared CFD wind -> `wind_runner.py` (WindModelRequest, 1.5 m pedestrian height, scenarios from `config_barcelona.json`). Gaussian plume + grid -> `pollen_dispersion.py` (5 m grid, 600 m max radius). Physics (grain 32 µm, release 18 m, settling 0.003 m/s, Mar–Apr) + scenarios (sea breeze SE 4 m/s, Tramontane NW 6 m/s, calm S 2 m/s) -> `config_barcelona.json`. 474 Platanus trees + OSM buildings -> `platanus_trees.geojson`, `buildings.geojson`. Viewers -> `viewer.html`, `block_viewer.html` (deck.gl). Eixample = top priority cells -> ties to the section_priority top rows.
- LIKELY Q&A + DEFENSE:
  - Q: "Is the wind field real or decorative?" A: Real CFD from the Infrared SDK over actual OSM building geometry; the same engine family used in the IAAC x Infrared work. We also keep a `--mock` synthetic mode for running without an API key, clearly flagged.
  - Q: "Does this finally validate the pollen spatially?" A: No, and we are careful: it is a physically-grounded *simulation* of dispersion, not measured-pollen validation. It adds a defensible spatial mechanism on top of the literature-anchored source; the station limit from the previous slide still stands.

---

### Slide 16 (swpvid) — "Pollen Particle Flow." (Live tool demo video)  [~25s]  [Dominika / teammate]  [VIDEO plays]

- SCRIPT: "And this is it running. [VIDEO.] Each green crown is a plane tree, the blue blocks are real building heights, and the drifting grains are pollen carried by the CFD wind. Watch what happens when we switch the wind regime — sea breeze, Tramontane, calm: the plume reshapes, and you can see exactly which streets load up and which clear. This is the street-scale picture a planner needs to sequence renewal where the exposure is worst, block by block."
- BACKED BY: `outputs/img/wind-pollen-tool.mp4` (a 14 s loop of `phase-6/wind-pollen/block_viewer.html`, real recording). Full 58 s walkthrough kept at `outputs/img/wind-pollen-tool-full.mp4`. On-screen readout in the clip ("Calm S · 2 m/s input · real CFD (Infrared SDK) · 474 Platanus trees") is generated by the viewer, not annotated by us.
- LIKELY Q&A + DEFENSE:
  - Q: "Is this a canned animation?" A: No — it is a screen recording of the interactive deck.gl viewer; the scenario buttons re-run the dispersion against a different stored CFD wind field live.

---

### Slide 17 (s15) — "The strongest result is the hypothesis we killed." (Conclusion)  [~30s]  [teammate]

- SCRIPT: "So where does this leave us? Our strongest result is not only the tool — it is the hypothesis we killed. A pre-registered falsification, reported without smoothing, is the clearest possible proof that the Evaluation phase did its job. We did not relabel a sealed-surface map as a fungal one; we shipped the honest question instead. Five contributions, no new algorithm: failure-as-outcome, anti-tautology discipline, nominal versus effective weights, an honesty gate for layers, and honest downgrade when validation data is missing. What next: pilot it inside the 2026–27 renewal plan in one district — say Sant Martí — sequencing the felling the city already commits to and pairing it with the Eixos Verds replanting. Plane pollen sensitises about 37% of the pollen-allergic, so across roughly 24,500 committed renewals the co-benefit is measurable from day one. Thank you."
- BACKED BY: five contributions -> paper §1.4; pivot/honest-question -> §11; ~37% Platanus sensitization -> Puiggròs 2015 (on-slide) and paper §2.4 / `atrisk_results.json` (0.37 constant); ~24,500 renewals -> ~56.3% of 43,722, paper §8.3; Pla Director / Eixos Verds -> §8.3 / §5.
- LIKELY Q&A + DEFENSE:
  - Q: "Is the project actually deployable, or just a seminar exercise?" A: It is analytically ship-ready — passes every pre-registered test, survives sensitivity, honest about its one un-closable limit — but deployment-pending on two organizational gates: a real Espais Verds analyst's sign-off and an independent reproduction (paper §7.4 / §8.4).
  - Q: "37% sensitization — where from?" A: Puiggròs 2015, the *Platanus* sensitization share among the pollen-allergic in Barcelona, used in the demographic exploration (paper §2.4).

---

## TRANSITIONS (one handoff line each, so the talk is one story)

- 1 -> 2: "That commitment to thin the planes is not ours to make — the city already made it. So the only open question is order."
- 2 -> 3: "And this is not a quiet planning matter — it is already a public fight."
- 3 -> 4: "[Handoff to Rafik] That is the city's decision. Now the data story behind how we got there — and it does not start with pollen."
- 4 -> 5: "Before any model, we had to earn the data."
- 5 -> 6: "With the sources vetted, we turned them into one analytical surface."
- 6 -> 7: "On that grid we trained the model — and the number was spectacular."
- 7 -> 8: "Spectacular, and hollow. Here is why."
- 8 -> 9: "But a flaw in our own construction proves nothing on its own — so we tested it three independent ways."
- 9 -> 10: "We had a choice: dress up the failure, or pivot honestly. We pivoted."
- 10 -> 11: "If the new source layer is pollen, it had better rest on real aerobiology."
- 11 -> 12: "With the source defensible, we put the whole product through a pre-registered evaluation."
- 12 -> 13: "Passing the tests is not enough — a planner cannot act on a 400-metre square."
- 13 -> 14: "That is efficiency. The planner can also choose equity."
- 14 -> 15: "[Handoff to teammate] Let me show you the live product."
- 15 -> 16: "And the same tool makes the equity trade-off visible."
- 16 -> 17: "Which brings us back to the one thing this whole project is really about."

---

## TOP 10 Q&A (hardest cross-cutting questions)

1. **"Why did you trust a literature-anchored pollen proxy with no measured validation?"**
   We do not over-trust it — it is our declared central limitation (Limitation #1). The proxy is defensible on established facts: *Platanus* is ~46% of the annual pollen index (Gabarra 2002) and dominant March–April, confirmed by 32 years of the XAC Hirst trap on *time and species*. What is missing is *spatial* validation, because no open station-level coordinate series exists. We wrote a cancellation criterion in Phase 1 that fired, downgrading the source to an emission proxy. The directional spot-check (station cell at the 86th percentile of our proxy) is consistent but explicitly not a calibration. -> paper §6.2, Postscript P.1, `pollen_station_validation.md`.

2. **"Isn't your priority map just a population map?"**
   No — and we pre-registered the test for exactly that (T2). Source and exposure correlate only 0.30 at cell grain; both layers are material; the product does not collapse onto either. That is the structural opposite of Cycle A, where the index *did* collapse onto one variable (sealed surface). -> `allergen_priority_results.md` T2, paper §7.1.

3. **"Isn't it just a plane-density map, then?"**
   At 400-metre cell grain, no: exposure re-orders ~70% of the top-15 versus density-only (T1, Spearman 0.89, Jaccard 0.30). At section grain, honestly, it gets *closer* to density because of MAUP — we measured and reported that rather than hiding it. -> `allergen_priority_results.md` T1, `section_priority.md` T1, paper §8.2.

4. **"Why a multiplicative index instead of a weighted sum?"**
   A weighted sum is fully compensatory — a high score on one layer offsets a low score on another, which is precisely how a single high-variance component (sealed surface) seized control of the Cycle-A ranking despite the declared weights. A product is partially non-compensatory: a cell low on either layer cannot be rescued, matching the decision semantics. There are no hidden weights to mis-set. -> paper §6.4, §9.3.

5. **"What is MAUP and why does it matter here?"**
   The Modifiable Areal Unit Problem (Openshaw 1984): results from zonal data depend on the chosen partition and scale, and can flip under a different one. It matters because our exposure re-ordering result holds at 400-metre cells but breaks at census-section grain (rollup Spearman 0.47) — the same method gives different answers at different zoom. We treat that as a load-bearing finding and ship both grains with the caveat. -> paper §2.3, §8.2, Limitation #5.

6. **"Why kill a model that scored R² 0.877?"**
   Because the 0.877 was nearly arithmetic, not evidence: the target was a weighted sum of the same features used to predict it (99.9% reconstructable from raw inputs; 91% sealed surface alone). The model inverted its own ingredients. The external test against 1,024 GBIF occurrences the composite never saw returned a flat null (partial-F p = 0.99). A meaningful-looking number that means nothing is worse than an honest failure. -> `metrics.csv`, `external_validation_results.md`, paper §3.2, §4.

7. **"Did you ever try a real machine-learning model on the pivoted product?"**
   Yes, pre-registered, with the binding rule that no model may predict a quantity built from its own inputs. A supervised source-estimator looked usable under random CV (R² ~0.41–0.44) but went *negative* under spatial cross-validation (−0.25 to −0.37) — urban form does not predict where Barcelona historically planted planes; planting is path-dependent and administrative. That negative is a finding we keep: it confirms the inventory is irreplaceable, and it shows spatial CV catching the exact inflation that fooled Cycle A, this time before we believed it. -> paper §6.5, Appendix A ML#1.

8. **"How is the pollen you model different from the Sant Jordi 'rain' in the news?"**
   Two distinct mechanisms in different weeks. Allergenic *pollen* is March–April — that is what our source layer proxies. The visible late-April fruit-fibre (achene) 'rain' is the *Sant Jordi* irritant that drove the 2026 headlines. Removing a mature plane reduces both, but we claim only the pollen exposure and never conflate them. -> paper §2.4, §8.3.

9. **"You claim equity is 'almost free' — prove the trade-off is real."**
   Deprivation is decorrelated from both existing layers (−0.008 with source, 0.17 with exposure), so it adds genuine information rather than re-skinning one. Re-weighting lifts the most-deprived tercile's top-15 share from 40% to 60% while sacrificing 0.0052 of burden — about 0.5 percentage points, ~3% relative — with only 3 of 15 cells swapping. We report both numbers as the decision, not a correctness claim. -> `equity_results.md` V3-1/V3-3, paper §7.2.

10. **"What would actually make this deployable, and what is missing?"**
    Analytically it is ship-ready: it passes every pre-registered test, survives sensitivity, and is honest about its one un-closable limit. Two organizational gates remain open by design and a seminar cannot manufacture them: a real Espais Verds analyst's on-the-record sign-off (the Monday test) and an independent reproduction on a clean machine. Those are deployment-readiness checks, not analytical defects. -> paper §7.4, §8.4.

---

## NUMBERS CHEAT-SHEET (statistic -> source file)

| Statistic (as on deck) | Value | Source |
|---|---|---|
| Plane share of urban trees | 27.45% | Pla Director 2017–2037; paper §1.3 |
| Plane trees today | 43,722 | Pla Director; paper §1.3 / §8.3 |
| Reduction by 2037 | to <12% (~56.3%, ~24,500) | Pla Director; paper §8.3 |
| Platanus share of annual pollen index | ~46% | Gabarra et al. 2002; paper §2.4 |
| Clinical symptom threshold | ~50 grains/m³ | Maya-Manzano et al. 2017; paper §2.4 |
| Platanus sensitization among pollen-allergic | ~37% | Puiggròs 2015; `atrisk_results.json` (0.37) |
| Residents | 1,729,963 | `section_priority.md`; paper §6.2 |
| Census sections | 1,068 | `section_priority.md`; paper §6.2 |
| Data adopt threshold | ≥10 / 14 (7 axes x 0–2) | deck s5; earn-the-data discipline |
| Scored grid cells (400 m) | 494 | paper §3.1; deck s6 |
| Cycle A test R² (held-out) | 0.877 (0.8768561) | `outputs/phase-4/metrics.csv` LinearRegression test |
| Cycle A train R² | 0.9997 (0.99968) | `metrics.csv` LinearRegression train |
| Baseline mean R² | 0.00 | `metrics.csv` BaselineMean train |
| Domain heuristic R² | 0.18 (0.1791) | `metrics.csv` BaselineDomainHeuristic train |
| Composite explained by sealed alone | 91% (R² 0.91, r 0.95) | paper §4.1 |
| Composite reconstructable from raw inputs | 99.9% | paper §3.2 / §4.1 |
| VIF platanus % | 699 (698.93) | `external_validation_results.md` VIF |
| VIF PRPI | 628 (627.91) | `external_validation_results.md` VIF |
| VIF sealed | 166 (165.74) | `external_validation_results.md` VIF |
| VIF NDVI | 92 (92.22) | `external_validation_results.md` VIF |
| External null adj-R² | 0.697 -> 0.678 (Δ −0.0195) | `external_validation_results.md` Richness |
| External partial-F p | 0.99 (0.98917) | `external_validation_results.md` |
| Moran's I on residuals p | 0.21 (0.214) | `external_validation_results.md` Robustness |
| GBIF cells / occurrences | 99 / 494 cells; 1,024 occurrences | `external_validation_results.md`; paper §4.2 |
| Falsification verdict / confidence | STOP, 75–80% | paper §4.4 |
| Cycle B T1 Spearman / Jaccard15 | 0.89 / 0.30 (0.8909 / 0.3043) | `allergen_priority_results.md` T1 |
| Cycle B T2 source–exposure corr | 0.30 (0.2975) | `allergen_priority_results.md` T2 |
| Cycle B T3 top-15 burden | 0.18 / 0.13 / 0.03 (margin +4.6 pp) | `allergen_priority_results.md` T3 |
| Cycle B T3 top-50 burden | 0.45 / 0.35 / 0.10 (margin +9.3 pp) | `allergen_priority_results.md` T3 |
| Cycle B T4 sensitivity arms | 3 / 3 hold | `allergen_priority_results.md` T4 |
| Rejected age layer | Spearman 0.999 vs population | paper §7.3 / Appendix A |
| Rejected sex layer | women 1.62x antihistamines, flat | paper §7.3 / Appendix A |
| Equity decorrelation | −0.008 (source), 0.17 (exposure) | `equity_results.md` V3-1 |
| Equity deprived-tercile share | 40% -> 60% (top-15) | `equity_results.md` V3-3 |
| Equity relief cost | −0.5 pp (0.0052) | `equity_results.md` V3-3 |
| Section grain T1 Spearman | 0.97 (0.9701) — FAILS | `section_priority.md` T1 |
| Section vs cell rollup Spearman | 0.47 (0.4669) | `section_priority.md` C1 |
| Section grain T2 source–exposure | 0.09 (0.0866) — holds | `section_priority.md` T2 |
| Rank-1 section (Montjuïc 03024) | 594 mature planes, ~2,000 residents | `section_priority.md`; paper §8.2 |
| Cross-grain badges | 187 corroborated / 169 artifact / 169 underrated | `section_enrich.json` |
| Co-benefit objective on artifacts | ~86% | paper §8.5; `planner.html` |
| Street worklist coverage | 100% address-match, no priority column | `street_removal_actions.csv`; paper §8.3 |
| Montjuïc top streets (planes / mature) | Av Estadi 277/114, Av Miramar 224/100, Pl Carles Buïgas 117/72, Av F. Ferrer i Guàrdia 92/51 | `street_removal_actions.csv` (verified exact) |

---

## VERIFY flags (slide claims not cleanly traceable to a numeric artifact)

1. **Slide 11 (s10b) pollen magnitudes "mean peak ~750 P/m³" and "historic max ~2250 P/m³".** These appear only on the deck SVG as season-scale illustration; I did not find them as cited values in the repo artifacts (the load-bearing, citeable figures are 46% from Gabarra 2002 and the ~50 grains/m³ threshold from Maya-Manzano 2017). Present them as the *scale* of the Mar–Apr season, not as a precise cited statistic. (The XAC tier "3–4 / maximum" and "continuous since 1994" are consistent with paper §2.4 and Postscript P.1.)
2. **Slide 9 (s9) "Berlin null: ~86% of AM richness = sealed/greenness axis".** The paper §4.3 references "a comparable European city" for the sealed/greenness axis but the body does not name Berlin with the 86% figure; it lives in `outputs/reports/lit-review-mycorrhizal-prioritization.md` (the 44-source review, Appendix B). If pressed for the exact source, cite the lit-review artifact, not the main paper. (Note: 86% here is a *different* 86% from the Phase-6 "co-benefit leans ~86% on artifacts" on slide 13 — do not conflate them.)
3. **Slide 11 top-50 grouped bar (s11) "priority .45 / density .35 / random .10".** Matches `allergen_priority_results.md` T3 top-50 (0.4458 / 0.3524 / 0.1015) — backed; flagged only because the on-slide checklist headlines the top-15 margin (+4.6 pp) while the bar chart shows both top-15 and top-50. Both are correct; just be clear which k you are pointing at.
4. **Slide 1 "Pre-registered falsification" pill vs Slide 2 phase strip showing all 6 phases "done/pivot".** Consistent with the paper (full six-phase cycle closed; deployment gates organizational). No numeric issue — noted so the presenter is not caught claiming live deployment; the honest status is "analytically ship-ready, deployment-pending" (paper §7.4).

(No invented support was used anywhere. Every on-slide statistic above is traced to a file; the four VERIFY items are the only places where a slide figure is illustrative or lives in a secondary artifact rather than the main results files.)
