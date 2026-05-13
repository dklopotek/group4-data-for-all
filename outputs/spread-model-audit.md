# Spread-Model Audit — `network_spread.html`

**Auditor:** Independent Model QA
**Date:** 2026-05-10
**Scope:** The "2030 mycorrhizal network spread" layer of
`outputs/network_spread.html` and the chain claim -> implementation across
`notebooks/04-connectivity.ipynb` (cells `cell-spread-fn`,
`cell-run-spread`) and `notebooks/05-visualisation.ipynb` (cell
`d8e9f0a1`).
**Question:** Is the "2030 projected spread under top-3 bridge
interventions" scientifically defensible, or aspirational decoration?

---

## Verdict at the top

**REWRITE the claim, not the code. The visual layer is a 500 m static
halo and has nothing to do with the simulation in notebook 04. Relabel
honestly, or DELETE the layer.**

The map markets a "2030 projection." What it shows is `island_hull.buffer(500m)`
— a fixed disc, identical for every island regardless of fungal type,
seasonal time-step, source patch, intervention, or sealed-surface
barrier. Calling this a "projected spread" is a category error: it is
not a projection, it is an illustration. The underlying simulation
exists in notebook 04 but (a) is never read by the map, and (b) is
itself a heavily-degraded model of hyphal spread that produces zero
growth on the current inputs.

---

## Finding 1 — The visualisation does NOT display the simulation output

**Severity: CRITICAL**

`notebooks/05-visualisation.ipynb` cell `d8e9f0a1` (the cell that builds
and saves `m2` / `network_spread.html`) constructs the green "2030
projected spread" layer as follows:

```python
top_islands_spread     = network_islands.nlargest(20, "node_count").copy()
islands_hulls_spread   = top_islands_spread.copy()
islands_hulls_spread["geometry"] = (
    islands_hulls_spread.geometry.convex_hull.simplify(tolerance=10)
)

_islands_metric        = islands_hulls_spread.to_crs("EPSG:25831")
_islands_metric["geometry"] = _islands_metric.geometry.buffer(500)  # metres
projected_hulls_top    = _islands_metric.to_crs("EPSG:4326")
```

The "2030 projection" is `island_centroid_hull.buffer(500m)`. That is
it. No simulation output is loaded; `spread_baseline`,
`spread_intervention`, and `simulate_spread` from notebook 04 are not
referenced anywhere in cell `d8e9f0a1`. The map is built from
`data/network_islands.geojson` (centroid Points -> convex hull -> 500 m
metric buffer).

**Evidence:**
- `fix-network-spread.md:90-106` confirms the post-fix output: 20
  features, each spanning ~0.012 deg lon x ~0.009 deg lat -- a 500 m
  disc, identical for every island regardless of `node_count`, fungal
  type, district, or intervention status.
- The same cell builds a "Baseline" purple layer from
  `islands_hulls_spread` (no buffer) and the "Spread" green layer from
  the same object buffered 500 m. The intervention zone outlines are
  separately drawn but the green spread halo itself does not change
  with intervention — it is the same 500 m halo whether top-3 zones
  are de-paved or not.
- Visually: 20 identical halos -> 20 identical halos. Two scenarios
  cannot differ when the function used to generate them ignores its
  scenario input.

**Impact:** Every claim the map makes about *projection*, *2030*,
*intervention effect*, or *spread* is unsupported by the rendered
geometry. The map is internally inconsistent with its own legend, which
says "2030 projected spread (top-3 bridge interventions)".

---

## Finding 2 — The simulation in notebook 04 does not model hyphal growth as documented

**Severity: MAJOR (independent of Finding 1)**

`notebooks/04-connectivity.ipynb` cell `cell-spread-fn` was patched
(BUG-8 fix) to be frontier-based. The current implementation:

```python
non_barrier = trees_gdf[trees_gdf["sealed_pct"] < seal_threshold]
kd = cKDTree(non_barrier[["x_etrs89","y_etrs89"]].values)
reached = {tid for tid in source_nodes if tid in id_to_idx}

for season in range(1, n_seasons + 1):
    frontier_coords = nb_coords[[id_to_idx[t] for t in reached]]
    neighbour_idx_lists = kd.query_ball_point(frontier_coords,
                                              r=spread_m_per_season)
    new_reached = {nb_ids[j] for lst in neighbour_idx_lists for j in lst
                   if nb_ids[j] not in reached}
    reached |= new_reached
```

What this is: a tree-to-tree BFS where any tree within `2 m` of any
already-reached tree joins the frontier next season.

What it is **not**, against the brief's claim of "hyphal growth from
Collserola / Ciutadella / Montjuic":

| Claim in label / docstring                          | Reality in code                                              | Severity |
|----------------------------------------------------- |------------------------------------------------------------- |--------- |
| Models hyphal extension at 1-5 m/season (AM) and faster for EM | Single constant `spread_m_per_season = 2.0` m; same for AM and EM | MAJOR |
| Differentiated AM vs EM growth rates                 | No `myco_type` differentiation anywhere in `simulate_spread`. Source trees are merged into one undifferentiated `source_nodes` set | MAJOR |
| Propagation through soil                             | Tree-to-tree only. There is no medium model. Two trees 3 m apart through unbroken soil are *unreachable* in one season; two trees 1.9 m apart across a road are *reachable* (the 2 m hop ignores sealed surface entirely between source and target) | MAJOR |
| Cost-distance via sealed surface                     | Only the *target tree's* `sealed_pct >= 0.7` is checked. The path between trees is not | MAJOR |
| Sealing barriers obstruct spread                     | Only at endpoints. A tree on a tiny non-sealed verge surrounded by sealed cells is reachable from any neighbour 2 m away | MAJOR |
| 5 seasons of accumulated growth                      | Implemented correctly — frontier accumulates BFS-style. This part works as written | OK |
| Source-sink propagation from Collserola, Ciutadella, Montjuic | Source patches are bbox-defined point sets; once selected they enter `reached` and are indistinguishable from any other reached tree | MINOR (acceptable abstraction) |

**Empirically (from `cell-run-spread` output):**

```
[baseline]           Season 0: 180   Season 1: 180   Season 3: 180   Season 5: 180
[top-3 intervention] Season 0: 180   Season 1: 180   Season 3: 180   Season 5: 180
Spread gain from top-3 bridge interventions:
  Season 1: gain=+0 trees   Season 3: +0   Season 5: +0
```

180 trees reached and zero growth across 5 seasons. Of 2 464 source
trees identified by the patch bboxes, only 180 survive the
`sealed_pct < 0.7` filter — and none of those 180 has a neighbour
within 2 m through non-sealed soil. The BFS halts at season 0.

This is mechanically consistent with the model: with AM_DISTANCE_M = 15 m
for graph edges but `spread_m_per_season = 2.0 m`, the simulation
literally cannot traverse the graph it was supposed to traverse. The
spread radius (2 m) is 7.5x smaller than the AM edge radius (15 m) and
17.5x smaller than the EM edge radius (35 m). The graph `G` is built
but `simulate_spread` does not use it — it builds its own KDTree from
`trees_gdf` and ignores `G` entirely.

**Impact:** Even if cell `d8e9f0a1` were rewritten to consume the
simulation output, it would draw 180 unchanging dots that do not
respond to interventions. The 2 m / season constant is small enough,
and the survival filter aggressive enough, that no measurable spread
occurs.

---

## Finding 3 — The spread function never reads the NetworkX graph

**Severity: MAJOR**

`simulate_spread(trees_gdf, source_nodes, G, n_seasons, ...)` accepts
`G` as a parameter but the function body never touches it. The graph
encoding (a) AM vs EM edge rules at 15 m / 35 m, (b) the 25 508
connected components, (c) which trees are co-network-resident — is
discarded. The simulation runs against a flat KDTree of tree
coordinates with a sealing filter.

This means a tree can join `reached` in two distinct ways the docstring
does not acknowledge:

1. via a real fungal edge (same myco_type, < 15/35 m, both non-barrier),
2. via spatial proximity alone (any myco_type, < 2 m, target
   non-barrier).

Path (2) is ecologically nonsensical: an AM tree 1.9 m from an EM tree
acquires no AM hyphal network and vice versa. The function permits
AM-via-EM and EM-via-AM crossover with no flag.

**Impact:** The "spread" of an AM-dominated source patch into an
EM-dominated forest fringe will appear in the count, even though no
hyphal network would actually form. Conversely, the strict 2 m hop
under-represents real hyphal spread because the graph already encodes
the empirically-grounded 15/35 m thresholds.

---

## Finding 4 — The 500 m buffer is not a calibrated dispersal distance

**Severity: MAJOR**

The choice of 500 m for the visualisation buffer is, per the comments
in cell `d8e9f0a1` and cell `c7d8e9f0`:

> "Projected spread: 500 m buffer from island centroids after top-3
> intervention. This is a simplified 2030-projection heuristic --
> distance is illustrative, not a calibrated dispersal model."

Honest comment in code; not reflected in the layer label on the
rendered map. Five hundred metres of mycorrhizal spread in (5? 10? --
the year is "2030" without a start year) is not supported by any cited
literature in the notebook. For reference:

| Process                                | Realistic rate                                          |
|--------------------------------------- |-------------------------------------------------------- |
| AM hyphal extension                    | 1-5 m / season (Friese & Allen 1991; Jakobsen et al. 1992) |
| EM mycelium frontal expansion          | 0.3-2 m / year (Anderson & Cairney 2007)                  |
| AM spore dispersal (wind, fauna)       | tens of metres / decade typical                          |
| EM spore dispersal (basidiocarps)      | km-scale via wind, but establishment rate is the bottleneck |
| New host colonisation across sealed surface | physically blocked unless de-paving occurs           |

A 500 m halo, applied uniformly to all 20 islands regardless of fungal
type, in a 4-year horizon (2026 -> 2030), implies ~125 m / year of
hyphal advance. That is 25-400x faster than any cited rate, with no
attempt to differentiate AM (slower) from EM (slower still) or to
account for sealed-surface obstruction.

**Impact:** If a planner reads the map literally — "if we de-pave these
three cells, the fungal network reaches these green halos by 2030" —
the implied gain is overstated by approximately two orders of magnitude.

---

## Finding 5 — Top-3 intervention zones do not bound the green halos on the map

**Severity: MAJOR**

The green halos in the map are drawn around **all 20 of the largest
existing islands**, not around the trees that would gain connectivity
under the top-3 intervention. Per cell `d8e9f0a1`:

```python
_islands_metric = islands_hulls_spread.to_crs("EPSG:25831")
                  # ^ this is top_islands_spread, i.e. the top 20
                  #   existing islands by node_count — independent of
                  #   the top-3 bridge interventions
_islands_metric["geometry"] = _islands_metric.geometry.buffer(500)
```

The layer's name claims "top-3 bridge interventions" but the geometry
is a function only of `network_islands.geojson` (existing islands), not
of `bridge_scores.csv` (the top-3 zones). The top-3 zones are drawn as
**separate orange/cyan outlines** on the map for context, but they do
not shape the green halos at all.

Cross-checking with `model-qa-audit.md:218`: the bridge analysis itself
currently returns `bridge_score = 0` for all 15 top zones (because of
the upstream sealing bug). So "top-3 bridge interventions" today means
"the three cells that happened to come first in a tie at score = 0,"
i.e., arbitrary. The map's claim of intervention-driven spread layers
two unfounded assertions on top of each other.

**Impact:** A user clicking the "Baseline" vs "2030 projected spread"
layers sees the same 20 polygons; one set is unbuffered, the other is
buffered by a constant 500 m. There is no relationship between the
green geometry and the orange/cyan intervention zones drawn beside it.

---

## Finding 6 — The legend is internally honest, the layer name is not

**Severity: MINOR**

Cell `d8e9f0a1` emits this in the in-map legend:

```html
<span style='color:#999; font-size:10px;'>
  Buffer = 500 m heuristic. Not calibrated.
</span>
```

That is the right disclaimer. The same cell also names the toggle
layer:

```python
spread_layer = folium.FeatureGroup(
    name="2030 projected spread (top-3 bridge interventions)", show=True
)
```

The legend says "heuristic, not calibrated." The toggle label says
"projected." Both cannot be true. A planner toggling the layer sees the
authoritative-sounding label; the qualifier is buried below in 10pt
grey.

---

## What scientific claim can the output ACTUALLY support?

The strongest defensible claim is approximately:

> "Approximate 500-metre connectivity neighbourhood around each of the
> 20 largest existing fungal islands. The buffer distance is an
> illustrative constant, not a calibrated hyphal-spread or
> seed-dispersal estimate. The map does not reflect any specific time
> horizon, fungal type, source patch, or intervention; it is the same
> halo whether or not interventions are applied."

The weak-but-honest version:

> "Illustrative connectivity neighbourhood (500 m), for orientation
> only. Not a model output."

The current label ("2030 projected spread under top-3 bridge
interventions") is **stronger than the geometry supports by three
margins simultaneously**: time (no time-step in the geometry), fungal
biology (no AM/EM differentiation), and intervention (the layer is
invariant under the intervention).

---

## Minimum work to make the spread layer scientifically defensible

To support even a weak "where the network might be by 2030 if we
de-pave" claim, all of the following are needed:

1. **AM vs EM differentiation.** Two layers (or one combined layer
   coloured by myco_type) with empirically-grounded rates:
   - AM: 1-3 m / season
   - EM: 0.5-1.5 m / year
   Each cited to FungalRoot / Smith & Read / Anderson & Cairney.

2. **Time-stepped expansion via the existing graph `G`.** Walk BFS
   from source nodes through real edges (AM edges <= 15 m, EM edges
   <= 35 m, both endpoints `sealed_pct < seal_threshold`). One BFS
   ring per season, with `seasons = 4 * 2 = 8` (4 years, 2 seasons /
   year for AM; equivalent or fewer for EM).

3. **Cost-distance via sealed surface, not point-filter.** Spread must
   be obstructed *along the path*, not just at the endpoints. Easiest
   defensible approximation: rasterise sealed_pct at 5 m, compute
   cost-weighted distances from source trees, and call any cell with
   accumulated cost >= threshold "unreachable." This eliminates the
   "1.9 m hop across a road" pathology.

4. **Baseline vs intervention comparison that the geometry actually
   reflects.** Run the BFS twice — once with the unmodified
   sealed_pct, once with top-3 cells set to 0 — and render the
   *difference* as the intervention-gain layer. The current map
   renders only the union of existing islands buffered uniformly; no
   difference signal exists.

5. **A `seal_threshold` calibrated to the corrected raster.** Per
   `model-qa-audit.md:218`, 0.7 puts the median Barcelona cell above
   the barrier line. A 90th-percentile cutoff (~0.86) or a literature-
   sourced ecological threshold is needed.

6. **A model card.** AM/EM rates with citations, the bbox for source
   patches, the season-length assumption, the sealed-surface cost
   function, the validation strategy (or its absence), and the
   uncertainty band.

This is one to two days of work for someone who already understands
the graph and the raster. It is not a trivial relabel.

---

## Methodological honesty: relabel suggestions

If the spread layer SHIPS without rewriting:

**Required minimum** — replace the toggle name and add a tooltip:

| Current                                                | Honest replacement                                           |
|------------------------------------------------------- |------------------------------------------------------------- |
| `"2030 projected spread (top-3 bridge interventions)"` | `"Illustrative 500 m connectivity halo (heuristic — not a model output)"` |
| Map title "Network Spread Projection"                  | `"Existing fungal islands with 500 m connectivity halos (illustrative)"`  |
| Legend "2030 projected spread"                         | `"500 m halo (illustrative, not calibrated)"`                             |

Add a tooltip on each green polygon:

> "500 m heuristic buffer around the convex hull of this island.
> Not a hyphal-spread projection. Not differentiated by fungal type.
> Identical under all intervention scenarios in the current pipeline."

**Stronger relabel (recommended)** — DELETE the green spread layer and
keep only the existing-islands layer plus the top-3 intervention-zone
outlines. The honest version of this product is "current network
islands + candidate interventions," not "2030 projection."

---

## Findings summary

| #  | Finding                                                                                              | Severity  | Domain          |
|--- |----------------------------------------------------------------------------------------------------- |---------- |-----------------|
| 1  | The visualisation `network_spread.html` does not display the simulation; it renders `buffer(500m)`   | CRITICAL  | Implementation  |
| 2  | `simulate_spread` does not model hyphal growth (no AM/EM differentiation, 2 m vs 15-35 m graph edges, no medium) | MAJOR     | Model            |
| 3  | `simulate_spread` accepts `G` but never uses it; bypasses the graph entirely                         | MAJOR     | Model            |
| 4  | The 500 m buffer is uncalibrated; implies ~125 m/year hyphal advance, 25-400x literature rates       | MAJOR     | Calibration      |
| 5  | Top-3 intervention zones do not bound or shape the green halo geometry on the map                    | MAJOR     | Internal consistency |
| 6  | Layer label "2030 projected spread" contradicts the in-map legend disclaimer "Not calibrated"        | MINOR     | Communication    |
| 7  | Simulation halts at season 0 (180 trees, no growth) on current inputs; intervention gain = 0         | INFO      | Diagnostic       |
| 8  | `seal_threshold = 0.7` filters out 93% of source-patch trees; only 180 of 2 464 survive              | INFO      | Diagnostic (inherited from model-qa-audit.md:218) |

---

## SHIP / REWRITE / DELETE — the spread layer specifically

**REWRITE** for the layer.

The map and the simulation are both salvageable as separate honest
products but neither is a "2030 projection" today:

- **The map's green halo (cell `d8e9f0a1`):** keep it only if it is
  relabelled "Illustrative 500 m connectivity neighbourhood
  (heuristic)". Drop the "2030", drop the "projection", drop the "top-3
  intervention" framing. The geometry simply does not encode any of
  those concepts. If a true 2030 projection is needed, it must be
  produced by a rewritten simulation (Findings 2-3) and re-saved into
  this map.

- **The notebook 04 simulation (cells `cell-spread-fn`,
  `cell-run-spread`):** REWRITE to traverse `G`, differentiate AM/EM,
  use literature-sourced rates, and emit a usable GeoJSON of season-N
  reached trees that the visualisation cell consumes directly. Until
  then the simulation should not be cited in any output.

Fallback option, if rewrite is out of scope for this session:
**DELETE** the green spread layer from `network_spread.html` and
republish the file as `outputs/network_islands.html` with the
existing-islands layer and the top-3 candidate intervention zone
outlines only. That is an honest, useful map. The current file is
neither.

---

**QA Analyst:** Independent Model QA Specialist
**QA Date:** 2026-05-10
**Re-audit trigger:** when (a) `simulate_spread` is rewritten to traverse
`G` with AM/EM rate differentiation and the spread filter is calibrated,
or (b) the layer is relabelled per Finding 6 and the green halo is
documented as illustrative rather than projected.
