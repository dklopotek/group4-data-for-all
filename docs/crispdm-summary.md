# CRISP-DM Summary — Group 4, Barcelona

**What this document is.** The single map of the whole project across all six CRISP-DM phases. The project ran **two CRISP-DM cycles**: a first cycle that built a mycorrhizal-regeneration priority map and **falsified its own thesis at the Evaluation phase**, and a second cycle that pivoted to a Platanus pollen-allergen exposure priority. The failure is not hidden in a footnote — it is the **hinge** between the two cycles and the central methodological result of the project. CRISP-DM is explicitly iterative; this document shows the iteration actually happening.

> Read this first, then follow the pointers. The honest failure record is `docs/failure-and-pivot.md`; the shipped product is documented in `phase-6/` and `outputs/phase-6/`.

---

## The story in one paragraph

We set out to rank Barcelona's 400 m grid cells for where intervention would best support soil **mycorrhizal-fungal** regeneration (Cycle A, the "Mycorrhizal Barcelona" thesis). We built a rigorous pipeline through Phases 1–4 — pre-registered tests, spatial-cluster split, a linear model at test R² = 0.877 that beat every baseline. Then Phase 5 (Evaluation) **falsified the thesis on three independent lines**: the headline composite is ~91% sealed surface (the ecological components carry near-zero effective weight); a pre-registered external test against independent GBIF fungal occurrences returned partial-F p = 0.99 (the biotic layers add nothing); and a 44-source literature review found the AM→EM host lever weak-to-unsupported. We did not relabel and ship. We **stopped the mycorrhizal claim and pivoted** to a question the data *can* answer and that ties to a real city policy: where to sequence Barcelona's plane-tree (*Platanus × acerifolia*) reduction so each removal relieves the most pollen-allergen exposure for people (Cycle B). Cycle B ran its own clean Phases 1–5 and is documented and evaluated here. **Phase 6 (Deployment) is intentionally deferred** — we do it with the class next week.

---

## The two cycles

```
CYCLE A — Mycorrhizal Barcelona                CYCLE B — Platanus allergen priority
P1 Business understanding   ─┐                  P1 Business understanding  (phase-6/business-understanding.md)
P2 Data understanding        │                  P2 Data understanding      (phase-6/data-understanding.md)
P3 Data preparation          │ rigorous build   P3 Data preparation        (phase-6/data-preparation.md)
P4 Modeling                  │                  P4 Modeling                (phase-6/modeling.md)
P5 Evaluation  == FALSIFIED ─┘ ===== HINGE ===> P5 Evaluation  == SHIP v1 + v3 (phase-6/evaluation-report.md)
                                                P6 Deployment  == DEFERRED to next week (with the class)
```

The arrow is the whole point. A falsified hypothesis, reported honestly, **is a result** — and the Evaluation phase doing its job (killing a flattering-but-empty number) is what triggered the second, defensible cycle.

---

## Phase-by-phase map

| CRISP-DM phase | Cycle A — Mycorrhizal (built, then falsified) | Cycle B — Allergen priority (shipped v1 + v3) |
|---|---|---|
| **1. Business understanding** | Rank 400 m cells for mycorrhizal-network regeneration; user = capital-planning analyst, Espais Verds. `phase-1/` | Sequence the already-decided plane-reduction (27%→<12% by 2037) so each removal buys the most allergen-exposure relief. `phase-6/business-understanding.md` |
| **2. Data understanding** | 189k–230k-tree inventory → mycorrhizal composition, richness, satellite features; GBIF fungal occurrences as external probe. `phase-2/` | Reuse the tree inventory; add census-section population, boundaries, income; **negative finding: no open machine-readable Platanus pollen series exists**. `phase-6/data-understanding.md` |
| **3. Data preparation** | Deterministic ETL → 494-cell scored grid; five-component composite, three weighting scenarios. `phase-3/`, `src/clean_data.py` | Three transparent layers (SOURCE, EXPOSURE, FEASIBILITY) + DEPRIVATION; areal-weighted interpolation; raw immutable. `phase-6/data-preparation.md` |
| **4. Modeling** | `composite_score_B` + linear model; pre-registered test design; spatial split; test R² 0.877. `phase-4/`, `src/train_model.py` | Composite **indicator**, not a learned model: `priority = source × exposure`, feasibility-annotated; baselines density-only + random. `phase-6/modeling.md` |
| **5. Evaluation** | **FALSIFIED** — 91% sealed surface (internal redundancy); external GBIF partial-F p=0.99 (FAIL); 44-source lit-review. `phase-5/`, `outputs/phase-5/`, `outputs/reports/lit-review-*.md` | **SHIP** — exposure earns its place (T1 re-orders, T2 non-redundant, T3 +4.6pt margin, T4 robust); equity variant v3 a near-free win. `phase-6/evaluation-report.md`, `outputs/phase-6/` |
| **6. Deployment** | Dropped with the thesis (the "rank by predicted score" use case was just the composite, worse). | **Deferred to next week, with the class.** Out of scope this session per the lecture (no decision-facing UI yet). |

---

## The hinge — why Cycle A's Phase 5 produced Cycle B

Cycle A's Evaluation phase asked the question Phase 4 should have asked — *does the thesis hold against data it was never built from?* — and the answer was no. The root causes (full account in `docs/failure-and-pivot.md`):

1. **Validated a tautology.** Phase 4 tested whether raw features predict a composite built from those features. R² ≈ 1 in-distribution was arithmetic, not evidence.
2. **Signal weighted into irrelevance.** Nominal weights ≠ effective weights; one dominant, high-variance component (sealed surface) decided the ranking regardless of declared weights.
3. **Mechanism was assumption, not measurement.** Mycorrhizal types came from a genus-level trait-table fallback, and the AM→EM "improvement" direction was contradicted by the best urban evidence.
4. **The data could not carry the claim.** Coarse opportunistic GBIF occurrence at 400 m, no measured local soil-fungal outcome.

The four lessons became design constraints on Cycle B: never validate an index against its own ingredients; check effective weights; relabel a proxy as the proxy it is; a falsified hypothesis honestly reported beats a meaningless flattering number. Cycle B is the structural opposite of the failure — two layers that **both** demonstrably move the ranking, tested against an external question whose answer was unknown, with its un-validatable element (no measured pollen) disclosed rather than dressed up.

---

## Where the project stands

- **Cycle A:** complete and closed. Thesis falsified, documented in full, carried forward only as a *stated, here-falsified hypothesis* (future work with measured soil data).
- **Cycle B:** Phases 1–5 complete. Shipped at **v1 (efficiency)** and **v3 (equity variant)**; model card `outputs/model-card-allergen-v1.md`. Two rejected layers (age-prevalence, sex) documented as honest negatives.
- **Phase 6 (Deployment):** not started — by design. Done next week with the class.

## Artifact index

- **Failure record (required reading):** `docs/failure-and-pivot.md`
- **Cycle B Phase 1:** `phase-6/business-understanding.md` · skill audit `phase-6/phase-1-audit.md`
- **Cycle B Phase 2:** `phase-6/data-understanding.md` · skill audit `phase-6/phase-2-audit.md`
- **Cycle B Phase 3:** `phase-6/data-preparation.md` · skill audit `phase-6/phase-3-audit.md` · data contract `phase-6/allergen-data-contract.yaml`
- **Cycle B Phase 4:** `phase-6/modeling.md` · skill audit `phase-6/phase-4-audit.md`
- **Cycle B Phase 5 design (pre-registered):** `phase-6/allergen-validation-design.md`
- **Cycle B Phase 5 verdict (readable):** `phase-6/evaluation-report.md` · skill audit + Go/Iterate/Kill memo `phase-6/phase-5-audit.md`
- **Skill provenance:** each Phase-N audit applies the `crispdm-N` skill to the pivot docs; gaps filled, conflicts flagged (esp. Phase-5 deploy gate).
- **Results + tables:** `outputs/phase-6/*.md|json|csv`
- **Model card:** `outputs/model-card-allergen-v1.md`
- **Cycle A evaluation:** `outputs/phase-5/external_validation_results.md`, `outputs/reports/lit-review-mycorrhizal-prioritization.md`
- **Pipeline (Cycle B):** `src/allergen_source.py`, `src/exposure_layer.py`, `src/allergen_priority.py`, `src/equity_layer.py`, `src/atrisk_layer.py`, `src/sex_atrisk.py`
