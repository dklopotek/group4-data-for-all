# Design — Platanus Pollen-Allergen Exposure Priority (project pivot)

**Date:** 2026-06-04
**Status:** approved (brainstorm → design)
**Supersedes the headline framing of:** "Mycorrhizal Barcelona" (mycorrhizal thesis falsified — see `docs/failure-and-pivot.md`)

## 1. Why we pivoted (one paragraph)

The original project ranked 400 m cells for mycorrhizal-fungal regeneration. Session-5 evaluation falsified that thesis on three independent lines: the headline composite is ~91% sealed surface; the biotic/host layers add no signal for external GBIF fungal occurrence beyond the abiotic null; and the literature finds the AM→EM host lever weak-to-unsupported. Rather than ship a fungus-labelled sealed-surface map, we pivot to a question the data *can* answer and that ties to a real Barcelona policy. Full account: `docs/failure-and-pivot.md`.

## 2. The new product

**Decision:** where to sequence Barcelona's plane-tree (*Platanus × acerifolia*) reduction — city policy targets cutting Platanus from ~27% to <12% of street trees by 2037 (Pla Director de l'Arbrat 2017–2037) — so that **each removal buys the most pollen-allergen-exposure relief for people**.

**Actor & unit:** Ajuntament Espais Verds / urban-health planners, acting at the **census-section / street-axis** scale (not a raw 400 m grid).

**Falsifiable headline claim:** *Plane-pollen allergen exposure is spatially concentrated, and a transparent source×exposure map identifies replacement priorities that reduce population allergen exposure more than the city's density-only or random sequencing.*

## 3. Architecture — three transparent layers (NO opaque composite)

The cardinal lesson from the failure: do not bundle weighted sub-scores into one number whose effective weights nobody checks. Keep layers separate, each independently inspectable, and validate the source layer externally.

1. **SOURCE — plane-pollen emission proxy per cell.** `source = plane_count × maturity`, where maturity derives from age class (older/larger planes emit more; use `trees_young_pct` inverted as a proxy, and trunk diameter if present). Built from the street-tree inventory only. Reported raw and standardized.
2. **EXPOSURE — receptor population per cell.** Residential population from Barcelona Open Data (census-section population), areal-joined to cells. Optional equity weight (share elderly/children) deferred to **v2**.
3. **FEASIBILITY — plantability gate, not a score.** `1 − mean_sealed` (or a binary plantable flag). Used to gate/annotate, not to inflate the ranking.

**Priority = SOURCE × EXPOSURE, feasibility-annotated.** A product of two transparent layers; we report each layer and the product, and we run the effective-weight / redundancy diagnostic on the result to confirm it is NOT just one layer in disguise.

## 4. External validation (pre-registered — the anti-tautology move)

The failure happened because the old index was validated against its own ingredients. This product is validated against **independent** data:

- **Primary:** the SOURCE layer is validated against measured **aerobiology Platanus-pollen data** (Catalonia/Barcelona pollen-monitoring network). Pre-register: does measured Platanus pollen rise with our source intensity in the catchment of monitoring stations? Pass bar fixed before running.
- **If pollen-station data is unavailable or too sparse:** fall back to literature-anchored pollen-emission factors for *Platanus*, and state the coarse-validation limitation explicitly (no silent claim).
- **Baselines the ranking must beat:** (a) plane-density-only sequencing, (b) random sequencing — on modeled population allergen-exposure reduction per tree removed.

Pre-registration goes in `phase-6/allergen-validation-design.md` BEFORE results, same discipline as the GBIF test.

## 5. Success criteria

- SOURCE map externally correlates with measured Platanus pollen at the pre-registered bar (or the fallback limitation is documented).
- Priority ranking beats density-only and random baselines on modeled exposure reduction.
- Redundancy diagnostic shows priority is genuinely two-layered (source AND exposure both move it), not a single layer relabelled.
- Every layer reported separately; a sensitivity pass and an explicit "what we are NOT claiming" section.
- The failure-and-pivot story is documented and front-and-centre.

## 6. CRISP-DM mapping (what gets run autonomously)

- **Business understanding:** this doc + `phase-6/business-understanding.md` (decision, actor, good-enough bar, cost of wrong).
- **Data understanding:** acquire + profile census population and pollen data; confirm leakage-free external target.
- **Data preparation:** build source/exposure/feasibility layers → a transparent priority table.
- **Modeling:** the source×exposure priority + baselines.
- **Evaluation:** pre-registered external validation + baseline comparison + redundancy/sensitivity.
- **Deployment:** NOT this session (no UI) — a planner-readable priority table + conclusion only.

## 7. Risks & assumptions (surfaced, not hidden)

- **Pollen-station data availability/resolution** — Barcelona/Catalonia has aerobiology monitoring, but stations are few → external validation will be spatially coarse. Verify availability first; fall back to emission factors with a stated limitation if needed.
- **Population data** — Barcelona Open Data publishes population by census section; low risk to fetch and join (areal interpolation to cells introduces MAUP — declared).
- **Maturity proxy** — inventory may lack trunk diameter; approximate with age class; document.
- **Exposure ≠ harm** — we model *exposure*, not clinical allergy outcomes; stated as a non-claim.

## 8. Scope

- **v1 (this build):** source × exposure priority, feasibility-gated, external source validation, baselines, sensitivity, documentation, failure record.
- **v2 (deferred):** equity weighting (elderly/children, social vulnerability); street-axis aggregation for the Eixos Verds; decision-facing UI.
