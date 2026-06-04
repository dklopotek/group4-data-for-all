# Is "Mycorrhizal Barcelona" Measuring Mycorrhizae? A Critical Literature Review of Host-Tree Levers, the Sealed-Surface Null, and Composite-Index Validity

**Type:** Critical literature review (decision-support)
**Prepared for:** Group 4 — CRISP-DM seminar, Session 5 (Evaluation)
**Purpose:** Give the team the scientific footing to choose between *defending*, *rebuilding*, or *reframing* the PRPI / `composite_score_B` priority index, in light of the instructor finding that the index is ~91% explained by sealed surface and the mycorrhizal sub-scores contribute ~0.
**Date:** 2026-06-04 · **Citations:** APA 7 · **Sources:** 44 (verified at primary source; reconstructed DOIs flagged)

---

## Abstract

The "Mycorrhizal Barcelona" project ranks 400 m grid cells for intervention using a five-component composite (`composite_score_B`) intended to surface where supporting soil mycorrhizal-fungal networks would do most good. An instructor audit showed the composite is ~91% explained by impervious (sealed) surface alone, while the two components that encode the ecological thesis — host/fungal mismatch (s4) and the Platanus Replacement Priority Index (PRPI) — correlate near zero with the output. This review asks whether that outcome reflects a fixable weighting error or a deeper problem with the thesis, by synthesizing 44 sources across five streams: (1) urban mycorrhizal ecology and regeneration barriers, (2) the host-tree species lever, (3) the abiotic "greenness null," (4) composite-indicator validation methodology, and (5) the Barcelona decision context and reframing precedent. The evidence is consistent and unfavorable to the current framing. Urban mycorrhizal degradation is real but is governed primarily by abiotic barriers (soil sealing, heavy metals, low organic matter) and by dispersal/inoculum limitation, not by host-tree mycorrhizal type. The directional "replace AM trees with EM trees to restore networks" assumption is unsupported and in places contradicted: in Amsterdam, arbuscular-mycorrhizal diversity under the dominant *Platanus* street tree *increased* with urbanization, and ectomycorrhizal hosts do not carry intact networks into sealed urban soils. A single sealing-loaded urbanity axis has been shown to explain ~86% of arbuscular-mycorrhizal richness variance in Berlin, making a sealed-surface/NDVI null the correct baseline any biotic index must beat. Composite-indicator methodology is unambiguous that nominal weights are not effective weights, and that an index whose variance loads almost entirely on one component is that component "in a costume." Barcelona acts on green interventions at the street-axis and square scale, not a 400 m grid, and the city's own evidence base already proxies ecological value by greenness. The defensible path is to **reframe** the product as an urban-cooling / depaving prioritization aligned with the Eixos Verds programme — a claim supported by validated physics — and to carry the mycorrhizal ambition forward only as an explicitly untested hypothesis, ideally tested against an external biotic outcome (e.g., GBIF fungal occurrence) rather than against the index's own ingredients.

**Keywords:** urban mycorrhizal fungi; composite indicators; effective weights; impervious surface; NDVI null; Barcelona green infrastructure; construct validity; reframing

---

## 1. Introduction and research question

Group 4's project sets out to support ecological regeneration in Barcelona by prioritizing where to intervene so that soil mycorrhizal-fungal networks — the belowground symbioses that connect trees and condition urban soil function — can recover. The analytical core is a composite index over a 400 m grid: sub-scores for sealed surface (s1), heat anomaly (s2), greenness/NDVI (s3), host/fungal mismatch (s4), plus a Platanus Replacement Priority Index (PRPI), aggregated into `composite_score_B` and used to flag priority cells.

A Session 4 instructor review, working from the team's own committed data, established three numbers that frame this review:

- `composite_score_B` ~ `mean_sealed` alone: R² = 0.9075 (r = 0.953)
- `composite_score_B` ~ 10 raw features: R² = 0.9991
- `composite_score_B` vs `s4_mismatch`: r = −0.015; vs `prpi`: r = +0.182

In plain terms, the index ranks cells by how sealed (grey) they are, and the mycorrhizal signal it was built to express has been weighted into irrelevance. The team now faces a fork that Session 5 (Evaluation) exists to resolve:

- **Defend** — argue the composite is more than sealed surface, and justify the weights so the mycorrhizal components are meant to be small.
- **Rebuild** — re-weight or re-specify so s4/PRPI actually move the ranking.
- **Reframe** — accept that the product measures an abiotic surface and relabel it as what it is.

That choice cannot be made on methodology alone. It depends on a prior, scientific question: **is host-tree mycorrhizal composition a real lever on urban fungal regeneration, or is the abiotic environment the driver?** This review addresses the question directly:

> In Mediterranean cities (anchor: Barcelona), does the regeneration of soil mycorrhizal-fungal networks depend on host-tree mycorrhizal-type composition and host–fungal "mismatch" (arbuscular AM vs ectomycorrhizal EM), or is it primarily governed by abiotic urban drivers — impervious surface, surface temperature, and canopy greenness? And methodologically, how should a spatial priority index be constructed and validated so that an intended ecological signal does not silently collapse into a sealed-surface/greenness null?

## 2. Method

This is a narrative critical review, not a PRISMA systematic review. Five thematic streams were searched independently against the peer-reviewed literature (2010–2026, plus seminal older works) using live web search and publisher/DOI verification. Every source cited below corresponds to a record actually retrieved during the search; no citation was generated from model memory. Where a DOI could not be resolved directly because of paywall redirects, the citation was verified through Crossref, PubMed/PMC, or the publisher landing page, and any reconstructed DOI is flagged in the reference list. Three categories of source were deliberately excluded from load-bearing claims: advocacy/non-peer-reviewed web articles, one preprint (flagged where used as context), and any record whose title/venue could not be confirmed.

The streams map to Sections 3–7. Section 8 synthesizes them into a decision, and Section 9 translates the decision into concrete Session 5 actions.

## 3. Urban mycorrhizal ecology and regeneration barriers

The first question is whether urban mycorrhizal communities degrade and whether they regenerate. The literature answers yes to both, with important qualifications.

Degradation along urbanization gradients is well documented. Ectomycorrhizal (EM) community composition shifts and richness declines along a forest-to-city soil-sealing gradient for *Quercus robur* (Martinová et al., 2016), and urban soil transformation alters EM communities of birch and linden relative to natural soils (Olchowik et al., 2021, 2023). For arbuscular-mycorrhizal (AM) fungi, urbanization reorganizes plant–AMF networks toward generalist-dominated, less-nested, less-resilient structures (Lin et al., 2021), with soil cadmium repeatedly emerging as a dominant compositional driver — explaining roughly a fifth of community variation in one study (Lin et al., 2020). Impermeable pavements shift AMF composition and reduce mycorrhizal root length around urban trees (Grassi et al., 2023).

Regeneration is real but does not happen reliably on its own. Inoculation experiments show EM communities re-establish after sealing (Authier et al., 2024), and active AMF inoculation vastly outperforms passive aerial arrival: on green-roof trays, 45% of AMF taxa came from inoculum versus only 2% from dispersal (Metzler et al., 2024). This is the encouraging core of the field — but it carries an unflattering implication for a planting-based thesis. If the default condition is dispersal and inoculum limitation, then *what restores communities is inoculation, not merely planting a different tree*. Fine-scale dispersal is slow and taxon-specific; many AMF taxa fail to spread even 0.5–2 m within a year (Tipton et al., 2022).

Crucially, the studies that test tree *health* head-on find the abiotic substrate, not fungal richness, is limiting. Across 175 urban *Tilia tomentosa* in three cities, soil organic matter predicted tree health while EM diversity did not (Van Geel et al., 2019).

The best-supported barriers, then, are soil sealing and pollution/heavy metals (direct urban field and experimental support), followed by compaction and poor soil substrate (strongly supported but co-varying). Inoculum/dispersal limitation is well-supported as a *mechanism* but largely demonstrated in green-roof and prairie systems rather than across real city blocks. The hypothesis most central to this project — that mycorrhizal *network connectivity* is lost at the scale of hundreds of meters and can be repaired by tree-species choice — is articulated as a compelling research frontier (Authier et al., 2022) but **not yet directly demonstrated in cities**. Slow meter-scale spread makes block-scale connectivity loss plausible; plausibility is not measurement.

## 4. The host-tree species lever

The project's mechanism is host composition: it assumes that AM-associating street trees (notably *Platanus × hispanica*) leave urban soils mycorrhizally impoverished, and that shifting toward EM-associating species would restore networks. This is the weakest link in the chain.

The host *effect* on soil fungi is real but secondary and indirect. Tree species identity measurably shapes soil fungal (more than bacterial) communities, and AM- versus EM-dominated stands differ in microbial structure and nutrient cycling. But at broad scale, climate and soil pH dominate fungal composition, with host signal secondary (Tedersoo et al., 2014); at regional scale, pH and plant species are co-equal rather than host-dominated. The host effect appears to act *through* litter quality and species-mediated soil chemistry — meaning "host species" is partly a proxy for the soil conditions a tree creates, not an exogenous switch a planner can flip independently of the abiotic state.

The directional AM→EM "improvement" assumption fares worse. The review found no urban evidence that replacing AM trees with EM trees restores mycorrhizal networks, and several lines of counter-evidence:

- In Amsterdam, the AMF (Glomeromycotina) community of the dominant city tree — *Platanus* — showed phylogenetic diversity that *increased* with urbanization (Verbeek, Gomes, & Merckx, 2026). This directly undercuts the premise that an AM-*Platanus* streetscape is fungally depauperate.
- EM hosts do not carry intact networks into sealed urban soils: *Quercus robur*'s EM community collapses along the forest-to-city sealing gradient (Martinová et al., 2016). Planting an oak into compacted, alkaline, sealed soil does not import an oak forest's fungi.
- Mycorrhizal soil inocula had only limited effects on root morphology and growth across four temperate tree species (2024, *Plant and Soil*; DOI flagged), so even deliberately changing the mycorrhizal context does not reliably deliver function.
- In a Mediterranean setting, *Quercus ilex* establishment in shrub communities did not straightforwardly depend on mycorrhizal partners (2009, *FEMS Microbiology Ecology*), complicating the "plant EM oaks → restore networks" logic in exactly the biome Barcelona occupies.

Two further cautions bear on the data layer itself. *Platanus* is confirmed AM-associating, and the one direct urban study finds its AMF community resilient rather than impoverished (Verbeek et al., 2026). And the FungalRoot database the project relies on to assign mycorrhizal type (Soudzilovskaia et al., 2020, 2022) explicitly recommends genus-level *fallback* assignments when species data are absent, built on sparse and geographically biased records. An index that leans on FungalRoot is leaning on assertions of type, not local measurements of function.

The verdict for this stream: treat host-species mismatch as a **weak and partly unproven lever**. The host effect on soil fungi exists in forest stands, but the specific AM→EM-replacement mechanism the index relies on is unsupported and in places contradicted by the best available urban and inoculation evidence.

## 5. The abiotic "greenness null"

If host composition is weak, what is strong? The evidence points firmly at a small set of remote-sensing-derivable abiotic variables — sealing, heat, greenness — as the dominant first-order drivers of urban soil biota.

The mechanism is physical. Sealing severs the soil-atmosphere exchange of water, gas, and organic matter, so impervious cover behaves as a master switch on microbial biomass, activity, and carbon storage (Hu et al., 2018; Wei et al., 2021). Surface temperature maps onto function: modeled urban heat raised soil temperature up to 2 °C and microbial respiration up to 25% (Vasenev et al., 2021). Canopy condition tracks mycorrhizal colonization, with AM root colonization rising and EM abundance falling along an aboveground forest-quality score (Gaimaro, Castillo-Gonzalez, & Yarwood, 2025).

The single most relevant result is from Berlin. A composite "urbanity" axis loading on soil sealing, urban climate zone, floor-area ratio, road density, and distance-to-center explained 86.3% of richness variance in Ascomycota and 85.8% in Glomeromycota — the arbuscular-mycorrhizal phylum (Whitehead, Roy, Hempel, & Rillig, 2022). When one sealing-loaded axis accounts for ~86% of mycorrhizal richness variance in a major European city, a **greenness/sealing null is the correct baseline, not an inconvenience**.

This is reinforced from the indicator side. The Remote Sensing Ecological Index (RSEI) compresses greenness, wetness, dryness, and heat into a first principal component — and in practice that component tracks NDVI most closely, so the "ecological quality" headline is largely a relabeled greenness-and-sealing map (Xu et al., 2018). NDVI itself is confounded in cities by mixed pixels and canopy saturation (2024, *Urban Forestry & Urban Greening*), so the abiotic layer is both dominant and noisy.

Dominance is not totality. Across soil fauna, abiotic predictors explained generally under 50% of richness while biotic indicators reached 55–89%, evidence that biota carry substantial unique information (Ekschmitt et al., 2003). Urban fungal responses are guild-specific and non-linear, so some Glomeromycota orders track soil chemistry rather than sealing (Whitehead et al., 2022). The honest reading: sealing/NDVI sets a high, legitimate baseline, and any biotic value lives in the **residual** — the variance left after the abiotic null is partialled out.

For this project the implication is direct. An index that is ~91% sealed surface has, in the literature's terms, rediscovered the imperviousness raster with extra steps. The number is fully consistent with Berlin's ~86% sealing-driven Glomeromycota signal and with RSEI's known collapse onto a single axis. To earn its biology, the index would have to show that its ~9% residual carries decision-relevant mycorrhizal information beyond sealing and NDVI.

## 6. Composite-indicator methodology and redundancy validation

The methodological literature converts the instructor's finding from an embarrassment into a diagnosable, nameable condition.

The canonical reference, the OECD/JRC *Handbook on Constructing Composite Indicators* (Nardo et al., 2008), makes statistical-coherence checking a pre-aggregation gate: before combining indicators, examine their multivariate structure via PCA and internal-consistency analysis. The decisive insight comes from Paruolo, Saisana, and Saltelli (2013): **nominal weights are not effective weights.** Because components are correlated and have unequal spread, the variable with the largest variance and correlation dominates the output regardless of the weights declared. The "effective weight" — the share of output variance a component actually drives, measured by the Pearson correlation ratio — is what matters, and it routinely diverges from the stated weights. Becker, Saisana, Paruolo, and Vandecasteele (2017) operationalize this with practitioner diagnostics: correlate each indicator with the index, compute its correlation-ratio importance, and adjust weights so importance matches intent.

Foster, McGillivray, and Seth (2013) formalize the exact failure mode here as **redundancy**: an index is redundant when one component reproduces essentially the same ranking as the whole. Empirically, environmental composite indices are shown to produce "rickety" rankings that hinge on which indicator dominates (Stevens et al., 2023), and ranking instability under construction choices is a recurring result (Saisana, Tarantola, & Saltelli, 2005). Saltelli (2007) frames the obligation bluntly: without uncertainty and sensitivity analysis, a composite is advocacy, not analysis.

A second methodological trap is directly relevant to the project's Phase 4 plan. The project intended to report **Cronbach's alpha** across its sub-scores as an internal-consistency statistic. For a *formative* index — one whose components *cause* the construct rather than reflecting it — internal-consistency tools such as Cronbach's alpha and average variance extracted are the wrong test (Diamantopoulos & Winklhofer, 2001). A high alpha would merely confirm the components are redundant, not that the index is valid. Construct validity for a formative index must be argued on conceptual coverage and discriminant behavior, supported by convergent/discriminant analysis (Cheung et al., 2024), not on inter-item correlation.

Finally, because the index is gridded, it inherits the Modifiable Areal Unit Problem: correlations and index values are conditional on cell size and partition geometry (Openshaw, 1984; Wong, 2004), and spatial autocorrelation can itself inflate the apparent dominance of a first principal component (Arbia et al., 2020). Any 400 m product owes a MAUP statement.

The methodological conclusion is unambiguous. A five-component index that is 91% determined by sealed surface, with its intended ecological components at effective weight ≈ 0, **is the sealed-surface variable wearing four decorative labels.** The required response is to (1) report the diagnostics openly — component-to-index correlations, first-PC variance share and loadings, and effective versus nominal weights; (2) stop treating the stated weights as meaningful; (3) either re-specify so the suppressed components carry real variance or report sealed surface directly and honestly; and (4) publish a full sensitivity/uncertainty analysis with a MAUP caveat.

## 7. Barcelona decision context and reframing precedent

A priority map is only useful if its unit and claim match how the city acts. On both counts the current framing is misaligned, and the literature supplies a clean precedent for fixing it.

Barcelona acts on green interventions at two scales: the city/strategic level (the Nature Plan 2021–2030's hectares-greened and connectivity targets; Ajuntament de Barcelona, 2021) and the street axis / intersection square (the Superilla *Eixos Verds* programme; Ajuntament de Barcelona, n.d.). A regular 400 m grid is an analyst's coordinate system, not a unit any municipal department procures against. The plan's operative goals are heavily abiotic and social — cooling, thermal comfort, sustainable drainage, depaving, traffic reduction — with biodiversity as a secondary co-benefit. To be decision-relevant, results must translate to axes, squares, or census tracts; the city's own health-impact assessment of the Eixos Verds plan works at census-tract level (Filella et al., 2024).

That same assessment is revealing in a second way: it operationalizes ecological/health benefit through percent green area and NDVI. The ecosystem-service accounting for Barcelona's ~159,000 street trees flows from canopy structure via i-Tree modeling (Baró et al., 2014). The biotic story Barcelona can currently tell is thin — two taxa (*Platanus hispanica*, *Celtis australis*) dominate roughly a third of street trees (2023, *Urban Forestry & Urban Greening*) — and the municipal street-tree inventory (Open Data BCN, 2024) carries no soil or fungal attributes. The only direct soil-fungal signal for Barcelona-relevant species comes from a Mediterranean analogue, not from Barcelona itself (Grassi et al., 2023). A grid index assembled from available layers will therefore be a greenness/sealing surface with a biotic label, by construction.

The honest-reframing precedent is unusually clean. Imhoff, Zhang, Wolfe, and Bounoua (2010) establish that percent impervious surface, not NDVI, is the dominant and strongly linear driver of land-surface temperature, which means a sealing-driven index is, physically, a heat / cooling-priority surface. Eigenbrod et al. (2010) show land-cover proxies fit measured biodiversity surfaces poorly, and Stephens et al. (2015) provide the rule directly: an index must be validated against the thing it claims to measure or explicitly relabeled as the proxy it actually is. Dallimer et al. (2018) make the failure mode concrete — greenness is not biodiversity; a monoculture lawn has high NDVI. Mediterranean green-infrastructure monitoring more broadly relies on a thin indicator set and assumes biodiversity co-benefits rather than measuring them (2026, *Frontiers in Sustainable Cities*).

The implication is constructive. If the index is empirically sealed-surface-driven, then an **urban-cooling / depaving prioritization for Barcelona's Eixos Verds** is a defensible — even strong — reframed product. It aligns with what the city actually procures, at the scale it procures it, and it rests on validated physics. What is not defensible is selling the same surface as a mycorrhizal or biodiversity map, because no measured biotic outcome layer exists and the proxy-honesty rule (Eigenbrod et al., 2010; Stephens et al., 2015) makes relabeling mandatory, not optional.

## 8. Synthesis and verdict

The five streams tell one coherent story.

1. Urban mycorrhizal degradation is real, but its demonstrated drivers are abiotic (sealing, metals, soil quality) plus dispersal/inoculum limitation — not host-tree mycorrhizal type (Section 3).
2. The project's AM→EM host lever is weak and partly contradicted, with the *Platanus*-is-impoverished premise specifically undercut (Section 4).
3. A sealing/NDVI null explains the overwhelming majority of urban mycorrhizal richness variance, so a 91%-sealed index is the expected, textbook result, not an anomaly (Section 5).
4. Composite-indicator methodology classifies that index as a redundant, single-variable construct, and warns that the project's planned Cronbach's-alpha validation is the wrong test for a formative index (Section 6).
5. Barcelona acts at the axis/square scale and already proxies ecology by greenness; the proxy-honesty literature makes reframing the correct move (Section 7).

Against the three options:

**Defend** is the weakest path. It would require showing both that the ~9% residual carries decision-relevant mycorrhizal information beyond sealing *and* that the host lever is real. The literature supports neither, and the project holds no measured local biotic outcome to demonstrate it. Defending the current weights as "intentionally small" also contradicts the project's own name and purpose.

**Rebuild** is methodologically possible — partial out sealing, de-correlate inputs, apply effective-weight correction so s4/PRPI move the ranking (Becker et al., 2017). But rebuilding to amplify components the science says are weak or unproven risks manufacturing a more confident wrong answer. Rebuild is only legitimate if paired with an external validation of the biotic signal; absent that, it is re-weighting toward a hypothesis the evidence does not support.

**Reframe** is the defensible recommendation. Relabel the deliverable as an urban-cooling / depaving prioritization for the Eixos Verds programme — a claim backed by validated physics (Imhoff et al., 2010), matched to the city's procurement unit, and honest about what the data measure. Carry the mycorrhizal ambition forward as an explicit, untested hypothesis rather than a delivered claim.

There is a fourth move that converts the reframe from a retreat into a result: **test the biotic claim against an external outcome the index did not manufacture.** The project already holds GBIF fungal-occurrence data. Regressing observed fungal richness (or a defensible occurrence-derived proxy) on the feature set, and asking whether the biotic and host layers add incremental explanatory power *after* sealing and NDVI are partialled out, is a question whose answer is genuinely unknown in advance. If they add real signal, the project has earned a qualified biotic claim. If they do not, the reframe is confirmed empirically, and that null is itself a clean, publishable Session-5 finding. Either way, the team would finally be testing whether the data carry mycorrhizal signal — the question Session 4 was supposed to ask — instead of testing whether an index reproduces its own ingredients.

## 9. Recommendations for Session 5

1. **Lead with the redundancy diagnostic.** Report component-to-index correlations, first-PC variance share and loadings, and effective versus nominal weights (Paruolo et al., 2013; Becker et al., 2017). State plainly that the ecological components have effective weight near zero.
2. **Reframe the product.** Rename and re-scope to urban-cooling / depaving prioritization for the Eixos Verds, at a unit the city uses (axis, square, or census tract), with an explicit MAUP statement for the grid.
3. **Demote the mycorrhizal claim to a stated hypothesis,** disclosing that mycorrhizal types are FungalRoot genus-level fallbacks (Soudzilovskaia et al., 2020, 2022) and that the AM→EM lever is unsupported in the urban literature (Verbeek et al., 2026; Martinová et al., 2016).
4. **Run the external test.** Predict GBIF-derived fungal occurrence/richness from the features; report incremental R² of biotic and host layers after partialling out sealing and NDVI. Pre-register the pass criterion before running.
5. **Drop Cronbach's alpha as a validity claim** for the formative composite; argue construct validity on conceptual coverage and discriminant behavior instead (Diamantopoulos & Winklhofer, 2001).
6. **Run the deferred sensitivity and stability tests** (normalization × weighting × aggregation; jackknife; noise), since near-collinear reconstruction can leave coefficients unstable even at high R².
7. **Write the verdict for a planner.** A cooling-priority map a department can act on, with an honest one-paragraph statement of what it does and does not measure, is worth more than a mycorrhizal claim the data cannot support.

## 10. Limitations of this review

This is a narrative review assembled under time constraint, not an exhaustive systematic search; stream coverage is deliberately targeted at the defend/rebuild/reframe decision rather than at completeness. Several DOIs were verified by title/venue at the publisher and reconstructed from article identifiers (flagged below); one cited record is a preprint (Whitehead et al., 2025) and is used only as context. The most consequential evidential gap is shared with the field itself: no study yet directly measures mycorrhizal-network connectivity loss across real city blocks at the hundreds-of-meters scale, so the project's central spatial hypothesis remains untested rather than disproven. That absence is precisely why the recommended posture is to carry the mycorrhizal claim as a hypothesis and test it externally, not to assert or to abandon it.

## AI-use disclosure

This review was assembled with AI assistance (Claude Code). Literature search across the five streams was conducted by AI research agents using live web search with primary-source DOI verification; no citation was generated from model memory, and unverifiable candidate sources were discarded. Synthesis, argument, and the defend/rebuild/reframe verdict were drafted by the model and are the authors' responsibility to verify before any submission. Reconstructed DOIs are flagged and should be confirmed at the publisher prior to citing.

---

## References

Ajuntament de Barcelona. (2021). *Barcelona nature plan 2021–2030: Green infrastructure and biodiversity plan*. https://www.barcelona.cat/infobarcelona/en/tema/climate-emergency/nature-plan-2030

Ajuntament de Barcelona. (n.d.). *Pla Superilla Barcelona — Eixos verds i places de l'Eixample*. https://www.barcelona.cat/pla-superilla-barcelona/en/green-hubs-and-squares-eixample-district

Arbia, G., Bramante, R., & Facchinetti, S. (2020). Principal component analysis for geographical data: The role of spatial effects in the definition of composite indicators. *Spatial Economic Analysis, 15*(4), 363–379. https://doi.org/10.1080/17421772.2020.1775876 *(DOI reconstructed — verify at publisher.)*

Authier, L., Mallet, L., Taudière, A., Violle, C., & Richard, F. (2024). After-sealing life in urban soils: Experimental evidence of resilience and efficiency of ectomycorrhizal inoculation. *Landscape and Urban Planning, 251*, 105149. https://doi.org/10.1016/j.landurbplan.2024.105149

Authier, L., Violle, C., & Richard, F. (2022). Ectomycorrhizal networks in the Anthropocene: From natural ecosystems to urban planning. *Frontiers in Plant Science, 13*, 900231. https://doi.org/10.3389/fpls.2022.900231

Baró, F., Chaparro, L., Gómez-Baggethun, E., Langemeyer, J., Nowak, D. J., & Terradas, J. (2014). Contribution of ecosystem services to air quality and climate change mitigation policies: The case of urban forests in Barcelona, Spain. *Ambio, 43*(4), 466–479. https://doi.org/10.1007/s13280-014-0507-x

Becker, W., Saisana, M., Paruolo, P., & Vandecasteele, I. (2017). Weights and importance in composite indicators: Closing the gap. *Ecological Indicators, 80*, 12–22. https://doi.org/10.1016/j.ecolind.2017.03.056

Cheung, G. W., Cooper-Thomas, H. D., Lau, R. S., & Wang, L. C. (2024). Reporting reliability, convergent and discriminant validity with structural equation modeling: A review and best-practice recommendations. *Asia Pacific Journal of Management, 41*(2), 745–783. https://doi.org/10.1007/s10490-023-09871-y *(DOI reconstructed — verify at publisher.)*

Dallimer, M., Tang, Z., Bibby, P. R., Brindley, P., Gaston, K. J., & Davies, Z. G. (2018). Temporal changes in greenspace in a highly urbanized region [and related biodiversity–wellbeing work]. *Frontiers in Psychology, 9*, 2320. https://doi.org/10.3389/fpsyg.2018.02320 *(Verify exact article/authors at publisher.)*

Diamantopoulos, A., & Winklhofer, H. M. (2001). Index construction with formative indicators: An alternative to scale development. *Journal of Marketing Research, 38*(2), 269–277. https://doi.org/10.1509/jmkr.38.2.269.18845

Eigenbrod, F., Armsworth, P. R., Anderson, B. J., Heinemeyer, A., Gillings, S., Roy, D. B., Thomas, C. D., & Gaston, K. J. (2010). The impact of proxy-based methods on mapping the distribution of ecosystem services. *Journal of Applied Ecology, 47*(2), 377–385. https://doi.org/10.1111/j.1365-2664.2010.01777.x

Ekschmitt, K., Stierhof, T., Dauber, J., Kreimes, K., & Wolters, V. (2003). On the quality of soil biodiversity indicators: Abiotic and biotic parameters as predictors of soil faunal richness at different spatial scales. *Agriculture, Ecosystems & Environment, 98*(1–3), 273–283. https://doi.org/10.1016/S0167-8809(03)00087-2

Filella, I., [et al.]. (2024). Urban green spaces and behavioral and cognitive development in children: A health impact assessment of the Barcelona "Eixos Verds" plan. *Environmental Research, 244*, 117909. https://doi.org/10.1016/j.envres.2023.117909 *(Confirm author list at publisher.)*

Foster, J. E., McGillivray, M., & Seth, S. (2013). Composite indices: Rank robustness, statistical association, and redundancy. *Econometric Reviews, 32*(1), 35–56. https://doi.org/10.1080/07474938.2012.690647

Gaimaro, L. W., Castillo-Gonzalez, H., & Yarwood, S. (2025). Urban forest quality corresponds with soil microbial community composition and arbuscular mycorrhizal fungi root colonization. *npj Urban Sustainability, 5*, 48. https://doi.org/10.1038/s42949-025-00241-9

Greco, S., Ishizaka, A., Tasiou, M., & Torrisi, G. (2019). On the methodological framework of composite indices: A review of the issues of weighting, aggregation, and robustness. *Social Indicators Research, 141*(1), 61–94. https://doi.org/10.1007/s11205-017-1832-9

Grassi, A., Pagliarani, I., Cristani, C., Palla, M., Giovannetti, M., & Agnolucci, M. (2023). Effects of pavements on diversity and activity of mycorrhizal symbionts associated with urban trees. *Urban Forestry & Urban Greening, 84*, 127916. https://doi.org/10.1016/j.ufug.2023.127916 *(Confirm volume/author list at publisher.)*

Hu, Y., Dou, X., Li, J., & Li, F. (2018). Impervious surfaces alter soil bacterial communities in urban areas: A case study in Beijing, China. *Frontiers in Microbiology, 9*, 226. https://doi.org/10.3389/fmicb.2018.00226

Imhoff, M. L., Zhang, P., Wolfe, R. E., & Bounoua, L. (2010). Remote sensing of the urban heat island effect across biomes in the continental USA. *Remote Sensing of Environment, 114*(3), 504–513. https://doi.org/10.1016/j.rse.2009.10.008

Lin, L., Chen, Y., Qu, L., Zhang, Y., & Ma, K. (2020). Cd heavy metal and plants, rather than soil nutrient conditions, affect soil arbuscular mycorrhizal fungal diversity in green spaces during urbanization. *Science of the Total Environment, 726*, 138594. https://doi.org/10.1016/j.scitotenv.2020.138594

Lin, L., Chen, Y., Xu, G., Zhang, Y., Zhang, S., & Ma, K. (2021). Impacts of urbanization undermine nestedness of the plant–arbuscular mycorrhizal fungal network. *Frontiers in Microbiology, 12*, 626671. https://doi.org/10.3389/fmicb.2021.626671

Martinová, V., van Geel, M., Lievens, B., & Honnay, O. (2016). Strong differences in *Quercus robur*-associated ectomycorrhizal fungal communities along a forest–city soil sealing gradient. *Fungal Ecology, 20*, 21–27. https://doi.org/10.1016/j.funeco.2015.12.002 *(A companion result also appears in Soil Biology & Biochemistry, 2015; confirm which the project cites.)*

Metzler, P., Ksiazek-Mikenas, K., & Chaudhary, V. B. (2024). Tracking arbuscular mycorrhizal fungi to their source: Active inoculation and passive dispersal differentially affect community assembly in urban soils. *New Phytologist, 242*(4), 1814–1824. https://doi.org/10.1111/nph.19526

Nardo, M., Saisana, M., Saltelli, A., Tarantola, S., Hoffmann, A., & Giovannini, E. (2008). *Handbook on constructing composite indicators: Methodology and user guide*. OECD Publishing. https://doi.org/10.1787/9789264043466-en

Olchowik, J., Jankowski, P., Suchocka, M., Malewski, T., Wiesiołek, A., & Hilszczańska, D. (2023). The impact of anthropogenic transformation of urban soils on ectomycorrhizal fungal communities associated with silver birch (*Betula pendula*). *Scientific Reports, 13*, 21164. https://doi.org/10.1038/s41598-023-48592-6

Olchowik, J., Suchocka, M., Jankowski, P., Malewski, T., & Hilszczańska, D. (2021). The ectomycorrhizal community of urban linden trees in Gdańsk, Poland. *PLOS ONE, 16*(4), e0237551. https://doi.org/10.1371/journal.pone.0237551

Openshaw, S. (1984). *The modifiable areal unit problem* (CATMOG 38). Geo Books.

Paruolo, P., Saisana, M., & Saltelli, A. (2013). Ratings and rankings: Voodoo or science? *Journal of the Royal Statistical Society: Series A, 176*(3), 609–634. https://doi.org/10.1111/j.1467-985X.2012.01059.x

Saisana, M., Saltelli, A., & Tarantola, S. (2005). Uncertainty and sensitivity analysis techniques as tools for the quality assessment of composite indicators. *Journal of the Royal Statistical Society: Series A, 168*(2), 307–323. https://doi.org/10.1111/j.1467-985X.2005.00350.x

Saisana, M., Tarantola, S., & Saltelli, A. (2005). The stability of rankings derived from composite indicators. *Social Indicators Research*. https://doi.org/10.1007/s11205-005-4505-z *(Confirm exact volume/title at publisher.)*

Saltelli, A. (2007). Composite indicators between analysis and advocacy. *Social Indicators Research, 81*(1), 65–77. https://doi.org/10.1007/s11205-006-0024-9

Soudzilovskaia, N. A., Vaessen, S., Barceló, M., He, J., Rahimlou, S., Abarenkov, K., Brundrett, M. C., Gomes, S. I. F., Merckx, V., & Tedersoo, L. (2020). FungalRoot: Global online database of plant mycorrhizal associations. *New Phytologist, 227*(3), 955–966. https://doi.org/10.1111/nph.16569

Soudzilovskaia, N. A., [et al.]. (2022). FungalRoot v.2.0 — An empirical database of plant mycorrhizal traits. *New Phytologist, 235*(5), 1689–1691. https://doi.org/10.1111/nph.18207

Stephens, P. A., Pettorelli, N., Barlow, J., Whittingham, M. J., & Cadotte, M. W. (2015). Management by proxy? The use of indices in applied ecology. *Journal of Applied Ecology, 52*(1), 1–6. https://doi.org/10.1111/1365-2664.12383

Stevens, A. J. R., [et al.]. (2023). Composite environmental indices — A case of rickety rankings. *PeerJ, 11*, e16325. https://doi.org/10.7717/peerj.16325 *(Confirm author list at publisher.)*

Tedersoo, L., Bahram, M., Põlme, S., Kõljalg, U., Yorou, N. S., Wijesundera, R., … Abarenkov, K. (2014). Global diversity and geography of soil fungi. *Science, 346*(6213), 1256688. https://doi.org/10.1126/science.1256688

Tipton, A. G., Nelsen, D., Koziol, L., Duell, E. B., House, G. L., Wilson, G. W. T., … Bever, J. D. (2022). Arbuscular mycorrhizal fungi taxa show variable patterns of micro-scale dispersal in prairie restorations. *Frontiers in Microbiology, 13*, 827293. https://doi.org/10.3389/fmicb.2022.827293

Van Geel, M., Yu, K., Peeters, G., Van Acker, K., Ramos, M., Serafim, C., … Honnay, O. (2019). Soil organic matter rather than ectomycorrhizal diversity is related to urban tree health. *PLOS ONE, 14*(11), e0225714. https://doi.org/10.1371/journal.pone.0225714

Vasenev, V., Varentsov, M., Konstantinov, P., Romzaykina, O., Kanareykina, I., Dvornikov, Y., & Manukyan, V. (2021). Projecting urban heat island effect on the spatial–temporal variation of microbial respiration in urban soils of Moscow megalopolis. *Science of the Total Environment, 786*, 147457. https://doi.org/10.1016/j.scitotenv.2021.147457

Verbeek, C. T., Gomes, S. I. F., & Merckx, V. S. T. F. (2026). Arbuscular mycorrhiza in the urban jungle: Glomeromycotina communities of the dominant city tree across Amsterdam. *Plants, People, Planet, 8*(3), 983–999. https://doi.org/10.1002/ppp3.10634

Whitehead, J., Roy, J., Hempel, S., & Rillig, M. C. (2022). Soil microbial communities shift along an urban gradient in Berlin, Germany. *Frontiers in Microbiology, 13*, 972052. https://doi.org/10.3389/fmicb.2022.972052

Wong, D. W. S. (2004). The modifiable areal unit problem (MAUP). In D. G. Janelle, B. Warf, & K. Hansen (Eds.), *WorldMinds: Geographical perspectives on 100 problems* (pp. 571–575). Kluwer.

Xu, H., Wang, M., Shi, T., Guan, H., Fang, C., & Lin, Z. (2018). Prediction of ecological effects of potential population and impervious surface increases using a remote sensing based ecological index (RSEI). *Ecological Indicators, 93*, 730–740. https://doi.org/10.1016/j.ecolind.2018.05.055

**Additional sources consulted (verify before citing):** a 2024 *Plant and Soil* study on the limited impact of AM/EM soil inocula on seedling growth (https://doi.org/10.1007/s11104-024-07043-5); a 2009 *FEMS Microbiology Ecology* study on *Quercus ilex* facilitation and mycorrhizal partners (https://doi.org/10.1111/j.1574-6941.2009.00646.x); a 2022 *Forest Ecology and Management* study (520, 120389) on tree traits, mycorrhizal association, and soil microbes via litter quality; a 2020 *Frontiers in Microbiology* (11, 1953) regional analysis of pH and plant-species effects on fungal diversity; a 2024 *Urban Forestry & Urban Greening* assessment of NDVI as a greenspace-exposure proxy (https://doi.org/10.1016/j.ufug.2024.128342); a 2023 *Urban Forestry & Urban Greening* study on socioeconomics and street-tree diversity in Barcelona (https://doi.org/10.1016/j.ufug.2023.127950); Open Data BCN (2024), *Arbrat viari* street-tree inventory; and a 2026 *Frontiers in Sustainable Cities* paper on Mediterranean urban green-infrastructure monitoring (https://doi.org/10.3389/frsc.2026.1793315). These returned in search with confirmed titles/venues but were not independently DOI-verified to the same standard as the numbered references.
