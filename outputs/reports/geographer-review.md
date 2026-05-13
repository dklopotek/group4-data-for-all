# Geographer's Review — Mycorrhizal Barcelona Spatial Findings

**Reviewer:** Geographer (physical and human geography)
**Date:** 2026-05-10
**Branch:** session-2/data-understanding-rafik
**Scope:** Spatial interpretation of the post-fix `scored_grid.geojson`, `network_islands.geojson`, `bridge_scores.csv`, and `priority_zones.csv` against Barcelona's actual physical and urban geography.

> Important provenance note before any planner reads this: `priority_zones.csv` reflects the pre-sealed-raster-fix run (labels "cooling" / "planting"). `scored_grid.geojson` reflects the post-fix state predicted by the QA audit, where the top-15 collapses to a single intervention class ("de-paving"). The two artefacts disagree about which 15 cells matter. This review interprets the post-fix `scored_grid.geojson` because it is the live state of the data; the CSV is a stale snapshot.

---

## 1. Where the top-15 actually lands in Barcelona

Mapped against Barcelona's terrain and urban fabric, the post-fix top-15 is not scattered — it traces a **specific geographic corridor**: the Llobregat-side industrial-port flats (La Marina del Port, La Marina del Prat Vermell, Sants–Badal), the Ciutat Vella medieval core (Sant Pere–Santa Caterina–La Ribera, Barri Gòtic), the Besòs-side floodplain (El Bon Pastor, Baró de Viver, La Verneda i la Pau, Camp de l'Arpa del Clot, Parc i Llacuna del Poblenou), with one Horta–Guinardó cell (El Guinardó, on the lower slope of the Collserola foothill).

Cluster geometry: the 15 centroids fit a 7.6 km × 10.4 km bounding box and have a mean pairwise distance of 5.3 km — i.e. the top-15 is a **tri-cluster** (Marina-port, Ciutat Vella–Sant Martí seafront, Sant Andreu–Besòs-bank) rather than a scattered set. This matches urban-ecology theory cleanly: the highest barrier scores accumulate where (a) historic industrial fill or alluvial substrate was sealed early and heavily, (b) the Mediterranean sea-breeze regime doesn't reach inland (Bon Pastor sits in a thermal pocket between the Collserola wall and the Besòs urbanisation), and (c) the Eixample grid's interior — which would be the textbook "central place" — is conspicuously **not** the worst.

What is missing tells the same story. **Eixample contributes a single top-15 cell** (C025_020, Dreta de l'Eixample), and **Gràcia, Les Corts, Nou Barris are absent or near-absent** from the post-fix list. The Cerdà grid scores high on sealing but its tree-lined chamfered corners and recent Superilla interventions (Consell de Cent, Sant Antoni, Poblenou superblock) pull NDVI up just enough to keep it off the worst-15. That is a defensible geographic result: Eixample looks sealed from above but has more linear canopy than the Marina del Port or Bon Pastor flats.

**Sarrià–Sant Gervasi** and **upper Horta-Guinardó** are absent from the top-15 and dominate the **bottom-15** (6 of 15 lowest-barrier cells are in Vallvidrera-Tibidabo-Les Planes — the Collserola interface). Theoretically expected. The Collserola escarpment is the city's ecological refugium; cells there have low sealing, negative LST anomaly (–4 to –7 °C below city median), and NDVI 3–5× the urban mean.

So the geographic pattern is: **flat alluvial / fill, low-elevation, far from Collserola = high barrier**; **Collserola interface = low barrier**; **Eixample = mid-range, pulled up by recent green-axis investment**. That is urban-ecology theory expressed in Barcelona's specific topography. The data passes the geographic-coherence sniff test.

---

## 2. The "spread" projection — why a uniform 500 m buffer is not defensible

The current implementation buffers every island convex hull by exactly 500 m. Three independent failures make this geographically meaningless:

**(a) Most "islands" are single trees.** 24,982 of 25,508 islands (98%) have node_count = 1. The "convex hull" of a single point is the point itself; a 500 m buffer around a point is a disc with no relationship to fungal-network spread. We are projecting a 78.5 ha "fungal future" around individual street trees.

**(b) The buffer ignores fungal biology.** AM hyphal extension is on the order of 2 m / growing season; EM extension perhaps 5 m / season. A 500 m buffer over a ~5-year planning horizon implies 100 m/yr, which is two orders of magnitude beyond any documented hyphal-front rate. Even sporocarp dispersal (the relevant medium-distance vector for EM fungi) rarely exceeds tens of metres per generation in urban settings. A uniform 500 m buffer represents nothing real.

**(c) The buffer is isotropic in a city that is not.** Barcelona's belowground spread is constrained by sealed surface, buried infrastructure, the Cerdà grid's continuous foundations, and the Collserola rock interface. Spread "north" from a Bon Pastor patch into the Besòs canalised channel is geographically impossible; spread "west" from the same patch toward the Sant Andreu rail corridor is structurally blocked. A directionally uniform buffer treats compacted Cerdà street profiles and unsealed Collserola lower slopes as identical media.

**When would a uniform buffer ever be defensible?** Only as an explicitly-labelled "decision-distance" buffer — i.e. "within X metres of an existing patch, an intervention can reasonably claim mycorrhizal proximity benefit," not "the network will reach here by 2030." With that re-labelling, 500 m is too large; 50–100 m would be the defensible decision distance for AM at typical urban hyphal-front rates.

**A proper geographic spread model** would be a **cost-distance / friction-surface model** (Knaapen 1992; Adriaensen et al. 2003): every grid cell gets a permeability weight (sealed_pct directly, weighted by soil compaction proxy, with infrastructure corridors as hard barriers), and spread is computed as a least-cost path from each source patch up to a biologically-credible cumulative cost (≈ 50 m AM, ≈ 150 m EM over 5 years). Anisotropy enters via the prevailing direction of unsealed strips (the Eixos Verds on Consell de Cent, Pi i Margall, Cristóbal de Moura). For larger patches (the Ciutadella and Montjuïc anchors, Collserola edge), **network-percolation** is the right model: treat each patch as a graph node, connect nodes within a distance threshold weighted by intervening permeability, and ask "which intervention edge most increases the giant-component size?" That is what the bridge_score was meant to measure, and it can only be meaningful on a cost-distance graph, not the current straight-line knn graph.

---

## 3. The within-city reference reframe

The pivot from peri-urban Collserola to a within-city lowest-barrier anchor is **geographically tighter** than the original brief allowed. Two reasons:

First, the original Collserola anchor compares urban Barcelona to a fundamentally different geomorphological unit (sandstone-conglomerate hills, Mediterranean pine-oak woodland, no impervious cover, no urban heat island). The comparison is asymmetric: Collserola will *always* look better. It says "the city is worse than the forest," which is not actionable.

Second, the within-city gradient is real and well-resolved. Comparing post-fix bottom-15 to top-15: composite_B ranges from 0.09 (Torre Baró, Nou Barris) to 0.86 (La Marina del Port). The best within-city cells are at the Collserola interface — Vallvidrera, Tibidabo, Sant Genís dels Agudells, Canyelles, upper Sarrià. Mean NDVI in the bottom-15 is +0.32 (forest-like) versus +0.04 in the top-15 (near-zero canopy). LST anomaly is –5.3 °C versus +2.9 °C. Sealed fraction is 0.12 versus 0.85.

The gradient story is therefore **physical-geographic, not just urban**: as you move from the Llobregat / Besòs delta plain (alluvial sands, sealed early for industry, no relief to shed heat) upslope into the Collserola conglomerate (broken topography, persistent woodland canopy, cold-air drainage from Tibidabo at night), barrier scores fall by 0.75 composite-units. This is a 9 km horizontal traverse with a ~300 m elevation gain. The within-city reference is a **bioclimatic transect**, not a single point — that is a stronger geographic frame than the original peri-urban anchor.

One caveat: Vallvidrera–Tibidabo–Les Planes are administratively in Sarrià–Sant Gervasi but geomorphologically in Collserola. Calling them "within-city" is technically correct (inside the municipal boundary) but blurs the very distinction the reframe was supposed to fix. The reference should be specifically: "lowest-barrier cells inside the dense urban footprint" — i.e. exclude cells with sealed_pct < 0.15 from the reference set, which removes the Collserola-interface cells and leaves a more honest within-city baseline (probably Ciutadella, Turó Park, Parc del Guinardó interior).

---

## 4. Intervention typology — single label vs. compound profile

The single-label output is **geographically incoherent**. Urban-ecology interventions compound by definition: de-paving without planting produces a heat-absorbing bare-soil patch; planting without de-paving produces stressed trees in compacted soil; cooling without canopy is structural shading; species-selection without soil-aware planting is a labelling exercise.

The current pipeline returns "de-paving" for all 15 top zones because of an argmax-of-weighted-subscore rule where sealed (weight 0.55) structurally outranks NDVI (0.20), LST (0.20), and mismatch (0.05). This is documented in the QA audit (Finding 7). Geographically, the worst cells are simultaneously **highly sealed, hot, and canopy-poor** — La Marina del Port has sealed=0.80, LST anomaly +7.9 °C, NDVI –0.006 (effectively bare). A planner reading "de-paving" alone loses the information that this cell also needs aggressive cooling and re-planting; treating it as a de-paving project will produce an unshaded scar.

The output should be a **profile vector**, not a category — e.g. `{de-paving: HIGH, cooling: HIGH, planting: HIGH, species-selection: LOW}` per cell, ordered by per-subscore z-score against the city distribution. A category label is only honest where one subscore exceeds the others by a defensible margin (e.g. ≥ 1 standard-deviation gap). For the current top-15, every cell would have at least two HIGH labels.

This also aligns the output with Ajuntament budget reality: Eixos Verds, Superilles, planting programme, and cooling strategy are not mutually exclusive budget lines — a single block in Marina del Prat Vermell would draw on multiple programmes simultaneously, and the priority map should communicate that.

---

## 5. What the output tells a planner — strong, weak, and the peer-review attack surface

**Strongest defensible claim:** Barrier concentration in Barcelona is spatially structured, not random, and the structure is geographically interpretable — high-barrier cells cluster on alluvial / fill substrate on the Llobregat (Marina) and Besòs (Bon Pastor) margins and in the medieval core, while low-barrier cells cluster on the Collserola interface. Within reasonable weight perturbations the worst tri-cluster stays the same. A planner can defend "the Marina district, the Besòs left-bank, and inner Ciutat Vella are the three highest-leverage barrier-reduction corridors in the municipality" against any reasonable challenge.

**Weakest claim, highest risk of misreading:** The "intervention_type" column. A planner who reads "de-paving" for all 15 zones will (a) think they have a one-dimensional problem, (b) ignore the compound canopy / heat / mismatch context, and (c) potentially commission de-paving projects that produce bare-earth heat sinks. The label is technically what the argmax says; it is **geographically wrong** as a decision aid.

**Where a peer reviewer pushes back hardest:** The network spread layer. A reviewer with any soil-ecology or landscape-ecology training will look at a uniform 500 m buffer around 25,508 mostly-single-tree "islands" and reject the figure outright. The cell-distance arithmetic alone (98% of islands are single trees; 500 m / 5 years = 100 m/yr hyphal extension) is enough to mark the spread layer as "not a model, an illustration." Coupled with the AM-connectivity-computed-only-for-Sant-Martí finding (audit point 11), the spread map mis-states its own geographic coverage. **Recommendation:** demote the spread layer to "qualitative buffer of intervention proximity" with explicit unit-and-scale labelling, or remove it from any planner-facing artefact until a friction-surface model replaces it. The priority map and the within-city gradient narrative are defensible. The spread projection, as currently rendered, is not.
