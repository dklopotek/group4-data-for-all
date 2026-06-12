# Brief Revisit (Step 10) — does the question still hold after the data hunt?

**Research question:** sequence Barcelona's plane-tree removals to relieve the most pollen-allergen
*exposure*, as a co-benefit of the city's biodiversity programme, at census-section grain.

**Answer: YES, unchanged in scope — and now better-defended.** The hunt did not find data that forces
a narrower question; it found one layer that *enriches* it and three honest negatives that *sharpen its
stated limits*. None of the four gaps was closeable in a way that changes what we can claim, except NO2,
which adds an optional interpretive dimension without touching the core proxy.

## Per gap

- **Per-tree size / Katz allometry — question unaffected; limitation now precise.** No continuous DBH/canopy exists in any Barcelona open dataset (verified; the "trunk perimeter" claim was false). We cannot run allometric per-tree emission. We *can*, as a declared assumption, weight the ordinal size classes (EXEMPLAR/PRIMERA/SEGONA/TERCERA) by literature-anchored size midpoints and run it as a **sensitivity arm** — but with no official class→size mapping, that midpoint is our own assumption, carried explicitly, not earned from the source. The headline (mature-count = size-ordered proxy) stands, now with a named ceiling.

- **Pollarding — question unaffected; the #1 limitation is now named and bounded.** Per-tree pruning dates exist in Parcs i Jardins' internal `fitxa` but are not open; the only public figure is an **average ~5-year, condition-based** street-tree cycle. So we cannot correct the dominant confounder per tree. Two honest moves: (a) declare it as the largest uncorrected error (literature agrees it is "frequently unknown to aerobiological studies"); (b) optionally express it as a **uniform ~5-yr uncertainty band**, never a per-tree correction. The real fix is a data request to Parcs i Jardins — out of scope this session.

- **NO2 allergenicity — question ENRICHED.** CALIOPE-Urban gives an open, 25 m, peer-reviewed NO2 surface **already aggregated to our 1,068 sections**. This lets us add an **allergenicity-context layer**: it does not change grain counts, it flags where the same grain is likely more allergenic. It is the one genuinely wire-able new dataset. Recommended: profile (per the plan) then wire as an optional lens + Vera knowledge. Caveats: modeled (validate vs XVPCA), NO2-only/annual, licence to confirm with BSC.

- **Measured pollen (XAC) — question unaffected; the gap is confirmed, not closed.** A 30-year Barcelona Platanus series exists but is request-only (CC-BY-NC) and, decisively, is **one trap with a ~15–30 km catchment** — it can calibrate our model's *timing/magnitude* but is **physically incapable of validating the spatial map**. This confirms our standing statement ("no spatial pollen exists for Barcelona") is literally true. The published annual indices (e.g. 25,790 in 1997) are citable now as a coarse temporal anchor.

## Net effect on the product

1. **One real upgrade:** add the CALIOPE-Urban NO2 allergenicity-context layer at section grain (honest, optional, validated against XVPCA).
2. **Three sharpened limitations** (size/allometry, pollarding, measured-pollen) — each now literature-anchored and primary-source-verified, which strengthens the Phase-5 limitations register rather than weakening the product.
3. **No over-claim is unlocked:** we still never claim measured pollen or health. The core remains a modeled exposure proxy; NO2 modulates *interpretation*, not measurement.

**Recommendation:** wire CALIOPE-Urban (after profiling); fold all four findings into the limitations register, the model card, and Vera's grounded knowledge so she explains them honestly. Treat XAC and the per-tree pollarding `fitxa` as named, out-of-scope data requests for a future milestone.
