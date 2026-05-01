# Data → Decision Map

> The bridge from `problem-brief.md` to the data inventory. For each
> sub-question in the brief, which dataset answers it, and at what
> confidence?
>
> Confidence reflects what the data realistically lets us claim, given
> the gaps documented in `data-quality-audit.md` and the AM-blindness
> limit documented in `datasheets/gbif-fungi.md`.

---

## The map

| Brief sub-question | Primary data source | Secondary source | Confidence | Notes |
|---|---|---|---|---|
| **Sub-Q 1:** Per zone, expected mycorrhizal type (AM/EM/mixed)? | Ajuntament tree inventory | FungalRoot v2.0 | **HIGH** | Species-level join is feasible (only 25 records / 0.01% are genus-only). 381 unique species. Reproducible via FungalRoot's published lookup. |
| **Sub-Q 2:** Per zone, sealed-surface fraction? | Copernicus Urban Atlas 2018/2021 | OSM building footprints | **HIGH** | 10m raster, full BCN FUA coverage, well-documented methodology. 100× finer than 400m decision unit. |
| **Sub-Q 3:** Per zone, heat anomaly relative to city baseline? | Landsat 8/9 thermal LST | Sentinel-3 SLSTR (fallback) | **HIGH** | 100m native, ~8-day combined revisit since 2021. Cloud occlusion is the only operational risk. |
| **Sub-Q 4:** Per zone, canopy / NDVI? | Sentinel-2 L2A | Landsat 8/9 (fallback) | **HIGH** | 10m visible/NIR, 5-day revisit. Cloud-cover documented per scene. |
| **Sub-Q 5:** Per zone, host–mycorrhizal mismatch (host present, partner not confirmed)? | Ajuntament tree inventory + FungalRoot + GBIF | (none) | **MEDIUM** | Host-side is HIGH; "partner confirmation" via GBIF is suppressed by AM-blindness — for AM-host-dominant zones (the majority of BCN), this sub-score is necessarily a *categorical* "expected-but-unconfirmable" flag, not a quantitative gap. EM-host subset (~9k trees) supports a quantitative version. The peri-urban reference patch is the methodological anchor. |
| **Sub-Q 6:** Combined barrier composite + top intervention recommendation per zone? | (composite of sub-Qs 1–5) | (none) | **MEDIUM** | Composite is HIGH for sub-Qs 2/3/4 inputs and MEDIUM for sub-Q 5. Output is per-zone rank + intervention-type label. The intervention-type recommendation is a heuristic mapping (highest individual sub-score → corresponding intervention), defensible but not optimal. |
| **Sub-Q 7:** Peri-urban reference patch barrier index vs urban core median? | GBIF + Urban Atlas + Landsat LST + Sentinel-2 (applied to a Collserola or Garraf 1km² patch) | Diputació de Barcelona forest inventory (auxiliary host data) | **MEDIUM** | All inputs available; the reference patch is methodologically valid but explicitly N=1 — used qualitatively as a baseline anchor, not as a statistical comparator. |

### Confidence scale

- **HIGH** — adopted dataset(s) directly answer the question at appropriate
  resolution and coverage. Defensible in front of a reviewer.
- **MEDIUM** — adopted dataset(s) answer the question with caveats
  (resolution mismatch, gap, proxy required). Defensible with explicit
  documentation in the audit + brief.
- **LOW** — partial answer only; will require synthesis, modeling
  assumptions, or proxies. Mark as a known limitation.
- **NONE** — no data backing exists.

---

## Coverage check

- **Sub-questions with HIGH confidence:**
  - Sub-Q 1 (expected mycorrhizal type)
  - Sub-Q 2 (sealed-surface fraction)
  - Sub-Q 3 (heat anomaly)
  - Sub-Q 4 (canopy / NDVI)

- **Sub-questions with MEDIUM confidence:**
  - Sub-Q 5 (host–mycorrhizal mismatch) — AM-blindness imposes a structural
    confound; mitigated by categorical-flag handling for AM-host zones and
    by the peri-urban reference patch
  - Sub-Q 6 (combined composite + intervention recommendation) — inherits
    sub-Q 5's MEDIUM; intervention-type heuristic is defensible but simple
  - Sub-Q 7 (peri-urban reference patch) — valid as qualitative anchor;
    explicitly N=1

- **Sub-questions with LOW confidence:**
  - None. Any sub-question that would have scored LOW was either reframed
    out of scope (the v1 "fragmentation" claim) or backed by a proxy that
    elevates confidence to MEDIUM.

- **Sub-questions with NO data backing:**
  - None.

---

## What this means for the brief

No sub-question has NONE or LOW confidence — but two MEDIUM-confidence
sub-questions (5, 6) carry a known structural limit (AM-blindness) that
the brief documents explicitly.

- [x] **Find a new source** — already done at inventory time. The Shape-C
      framing was specifically chosen so that the inputs we *do* have
      (Urban Atlas, Sentinel-2, Landsat, tree inventory, FungalRoot) are
      load-bearing, not the inputs we don't (DNA metabarcoding, soil
      moisture at 400m, tree health).

- [x] **Revise the brief** — committed in `problem-brief-v2.md`:
      Shape-C reframe specifically protects against the gaps we cannot
      close.

- [x] **Accept MEDIUM confidence as documented limitations** — captured in:
      - `problem-brief.md` Risks section
      - `problem-brief.md` Out-of-scope section ("output identifies
        leverage, not outcome")
      - `data-quality-audit.md` bias check + sub-question fitness
      - `datasheets/gbif-fungi.md` Section 8 (AM-blindness verdict)
      - The host-mismatch sub-score's categorical-flag handling for
        AM-host zones (will be referenced in the model card / output
        documentation in Session 7)

---

## Sign-off

**Team:** [names]
**Last updated:** 2026-05-01
