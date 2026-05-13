"""
fix-04-connectivity.py
======================
Corrected replacement cells for notebooks/04-connectivity.ipynb.

All bridge_score values are 0 because of three compounding bugs described
below. This file contains drop-in replacements for the affected cells.
Paste each block into the corresponding notebook cell and re-run from
that cell downward.

ROOT CAUSE CHAIN
----------------
Bug 1 (primary) — sealed_pct is 0.003 everywhere
    scored_grid.geojson stores sealed_pct = 0.003 for all 495 cells.
    This is a stub/fallback value written by notebook 03 when the Urban
    Atlas raster could not be loaded.  With no cell ever reaching the
    SEAL_THRESHOLD of 0.7, the graph is built WITHOUT any barriers: every
    tree within 15 m (AM) or 35 m (EM) of another same-type tree gets an
    edge.  All nearby trees are already connected into one component, so
    there are no disconnected islands that an intervention could bridge.

Bug 2 (consequence) — bridge_score_for_zone always returns 0 immediately
    The function's first guard is:
        blocked = trees_gdf[
            (trees_gdf["cell_id"] == zone_cell_id) &
            (trees_gdf["sealed_pct"] >= SEAL_THRESHOLD)   # ← ALWAYS FALSE
        ]
        if len(blocked) == 0:
            return 0                                       # ← ALWAYS HITS HERE
    Because sealed_pct never reaches 0.7, blocked is always an empty
    DataFrame and the function returns 0 before doing any work.

Bug 3 (secondary, in the function body) — double-counting & wrong sentinel
    Even if sealed_pct were correct, the original function would
    overcount.  Blocked trees are excluded from G, so
        b_comp = node_to_comp.get(b_id, -1)
    always returns -1.  Their neighbours return -2 (different default).
    The condition `b_comp != n_comp` is therefore always True, so every
    reachable neighbour gets counted as a new connection regardless of
    whether the two trees are in the same or different components.
    The correct metric is unique new (comp_A, comp_B) pairs, not a raw
    edge count.

THE FIX
-------
The Urban Atlas raster is the real source of sealed_pct.  Until notebook 03
is re-run with the raster available, the best available proxy is s2_lst
(the normalised LST anomaly score already in scored_grid.geojson).
High LST → more impervious surface → higher effective sealing.

Cell replacements below:
  [A] Updated imports / configuration  — adds S2_SEAL_PROXY flag
  [B] Grid-join cell                   — substitutes s2_lst for sealed_pct
  [C] bridge_score_for_zone function   — fixes the three bugs above
  [D] compute-bridges cell             — no logic change, works correctly
                                         once [B] and [C] are in place

IMPORTANT: after pasting [B] you must re-run ALL cells from §3 onward
(grid join → graph construction → components → bridge analysis → save).
The graph needs to be rebuilt with the corrected sealed_pct values.
"""

# =============================================================================
# [A] ADD TO cell-imports  (append after the existing SEAL_THRESHOLD line)
# =============================================================================

# Replace the single SEAL_THRESHOLD definition with these three lines:

SEAL_THRESHOLD = 0.7    # cells above this are barriers (fraction impervious)

# When scored_grid.geojson lacks real sealed_pct (Urban Atlas raster absent),
# fall back to s2_lst (normalised LST score: 0 = cool/vegetated, 1 = hot/paved).
# Set to True to activate the proxy; False to use the raw sealed_pct column.
USE_S2_LST_PROXY = True   # flip to False once notebook 03 re-generates real sealed_pct

print("Configuration set — USE_S2_LST_PROXY =", USE_S2_LST_PROXY)


# =============================================================================
# [B] REPLACEMENT for cell-grid-join  (the full cell, paste verbatim)
# =============================================================================

def load_grid_with_sealing() -> "gpd.GeoDataFrame":  # type: ignore[name-defined]
    """
    Load scored_grid.geojson (preferred) or grid_trees.geojson.
    Both contain sealed_pct.  If neither exists, synthesise.
    """
    for path in [SCORED_GRID_PATH, GRID_TREES_PATH]:
        if path.exists():
            g = gpd.read_file(path)
            print(f"Grid loaded from: {path.name}  ({len(g):,} cells)")
            return g

    print("WARNING: No grid file found — synthesising sealed_pct grid.")
    from shapely.geometry import box
    x0, y0, x1, y1 = 419_000, 4_575_000, 436_000, 4_593_000
    cell_size = 400
    xs = np.arange(x0, x1, cell_size)
    ys = np.arange(y0, y1, cell_size)
    xx, yy = np.meshgrid(xs, ys)
    cells = [box(x, y, x + cell_size, y + cell_size)
             for x, y in zip(xx.ravel(), yy.ravel())]
    n = len(cells)
    rng = np.random.default_rng(42)
    g = gpd.GeoDataFrame(
        {
            "cell_id":    [f"CELL_{i:04d}" for i in range(n)],
            "sealed_pct": rng.beta(2, 5, size=n),
            "s2_lst":     rng.beta(2, 5, size=n),
            "composite_B":rng.uniform(0, 1, size=n),
            "top15_scenario_B": False,
        },
        geometry=cells,
        crs="EPSG:25831",
    )
    top_idx = rng.choice(n, size=15, replace=False)
    g.loc[top_idx, "top15_scenario_B"] = True
    return g


grid = load_grid_with_sealing()
if grid.crs is None or grid.crs.to_epsg() != 25831:
    grid = grid.to_crs(epsg=25831)

# ── FIX: substitute s2_lst for sealed_pct when the raster proxy flag is set ──
#
# WHY: scored_grid.geojson was written with sealed_pct = 0.003 (constant stub)
# because notebook 03 could not load the Urban Atlas raster.  A value of 0.003
# means NO cell ever exceeds the 0.7 barrier threshold, so graph construction
# creates no barriers and the bridge analysis always returns 0.
#
# s2_lst is the normalised land-surface-temperature anomaly score (0–1).
# Hot pixels correspond to impervious, sun-baked surfaces — a reasonable proxy
# for pavement fraction until the real raster is available.
#
# Replace this block entirely once notebook 03 produces real sealed_pct values.
if USE_S2_LST_PROXY and "s2_lst" in grid.columns:
    n_stub = (grid["sealed_pct"] < 0.01).sum()
    if n_stub > len(grid) * 0.9:   # >90 % of values are stub → use proxy
        print(f"INFO: sealed_pct appears to be a stub value ({n_stub}/{len(grid)} cells < 0.01).")
        print("      Substituting s2_lst as sealed_pct proxy (USE_S2_LST_PROXY=True).")
        grid["sealed_pct"] = grid["s2_lst"]
    else:
        print("INFO: sealed_pct looks real — not substituting s2_lst proxy.")
else:
    if USE_S2_LST_PROXY:
        print("WARNING: USE_S2_LST_PROXY=True but s2_lst column absent — keeping raw sealed_pct.")

# Build GeoDataFrame of trees in UTM31N
trees = trees_known.copy()
trees_gdf = gpd.GeoDataFrame(
    trees,
    geometry=gpd.points_from_xy(trees["x_etrs89"], trees["y_etrs89"]),
    crs="EPSG:25831",
)
trees_gdf["tree_id"] = trees_gdf["codi"].astype(str)

# Spatial join: attach grid cell attributes to each tree
grid_sub = grid[["geometry", "cell_id", "sealed_pct"]].copy()
trees_gdf = gpd.sjoin(trees_gdf, grid_sub, how="left", predicate="within")
trees_gdf["sealed_pct"] = trees_gdf["sealed_pct"].fillna(0.5)
trees_gdf["cell_id"]    = trees_gdf["cell_id"].fillna("UNKNOWN")
trees_gdf = trees_gdf.drop(columns=["index_right"], errors="ignore")

n_barrier = (trees_gdf["sealed_pct"] >= SEAL_THRESHOLD).sum()
print(f"\nTrees joined to grid: {len(trees_gdf):,}")
print(f"Sealed_pct stats — mean: {trees_gdf['sealed_pct'].mean():.3f}, "
      f"max: {trees_gdf['sealed_pct'].max():.3f}")
print(f"Trees in barrier cells (sealed_pct >= {SEAL_THRESHOLD}): {n_barrier:,}")
if n_barrier == 0:
    print("WARNING: No barrier trees found.  Bridge analysis will return 0 for all zones.")
    print("         Check that sealed_pct has variation (not a constant stub).")


# =============================================================================
# [C] REPLACEMENT for cell-bridge-fn  (the full cell, paste verbatim)
# =============================================================================

def bridge_score_for_zone(
    zone_cell_id: str,
    trees_gdf: "gpd.GeoDataFrame",  # type: ignore[name-defined]
    node_to_comp: dict,
    G: "nx.Graph",                  # type: ignore[name-defined]
) -> int:
    """
    Compute how many additional inter-component connections would be enabled
    by removing the sealing barrier in the given grid cell.

    A 'blocked' tree is one in a cell with sealed_pct >= SEAL_THRESHOLD.
    Removing the barrier means such a tree becomes eligible to form edges
    with non-blocked trees within the standard distance threshold.

    For each newly-enabled edge that spans two DIFFERENT connected components
    the pair (comp_A, comp_B) is recorded.  The bridge score is the count of
    DISTINCT component pairs newly joined — not the raw edge count.

    Returns
    -------
    int : number of distinct inter-component pairs newly connected
    """
    # ── Bug 1 fix: trees 'blocked' are those in the CURRENT zone with
    # sealed_pct >= threshold.  Previously this was always empty because
    # sealed_pct = 0.003 everywhere.  With a real (or proxy) sealed_pct,
    # this set is non-empty for high-sealing cells.
    blocked = trees_gdf[
        (trees_gdf["cell_id"] == zone_cell_id) &
        (trees_gdf["sealed_pct"] >= SEAL_THRESHOLD)
    ].copy()

    if len(blocked) == 0:
        return 0

    # All non-barrier graph trees (potential neighbours once barrier removed)
    all_graph_trees = trees_gdf[
        (trees_gdf["tree_id"].isin(G.nodes())) &
        (trees_gdf["sealed_pct"] < SEAL_THRESHOLD)
    ].copy()

    if len(all_graph_trees) == 0:
        return 0

    all_coords = all_graph_trees[["x_etrs89", "y_etrs89"]].values
    all_ids    = all_graph_trees["tree_id"].values
    all_myco   = all_graph_trees["myco_type"].values

    kd = cKDTree(all_coords)

    # ── Bug 3 fix: count distinct (comp_A, comp_B) pairs, not raw edges.
    # Blocked trees were excluded from G so they have no component; we treat
    # them as potential connectors between existing components.  Two blocked
    # trees that both connect to the same target component should only be
    # counted once per unique pair of components they bridge.
    new_component_pairs: set = set()

    for bi in range(len(blocked)):
        b_row  = blocked.iloc[bi]
        b_id   = b_row["tree_id"]
        b_myco = b_row["myco_type"]

        dist_thresh = AM_DISTANCE_M if b_myco == "AM" else EM_DISTANCE_M
        bx = float(b_row["x_etrs89"])
        by = float(b_row["y_etrs89"])

        nbr_idx = kd.query_ball_point([bx, by], r=dist_thresh)
        reached_comps: set = set()

        for j in nbr_idx:
            if all_ids[j] == b_id:
                continue
            if all_myco[j] != b_myco:          # no AM–EM edges
                continue
            n_comp = node_to_comp.get(all_ids[j], None)
            if n_comp is not None:
                reached_comps.add(n_comp)

        # Each blocked tree bridging k components adds C(k,2) new pairs
        comps_list = sorted(reached_comps)
        for a in range(len(comps_list)):
            for b in range(a + 1, len(comps_list)):
                new_component_pairs.add((comps_list[a], comps_list[b]))

    return len(new_component_pairs)


print("Bridge score function defined (fixed).")


# =============================================================================
# [D] REPLACEMENT for cell-compute-bridges  (the full cell, paste verbatim)
# =============================================================================
# No logic changes in this cell — it works correctly once the upstream fixes
# ([B] real sealed_pct and [C] fixed function) are in place.
# The only addition is a diagnostic check to help catch the stub-value problem
# early in future runs.

# Sanity-check: warn if barrier trees are still zero
n_barrier_total = (trees_gdf["sealed_pct"] >= SEAL_THRESHOLD).sum()
if n_barrier_total == 0:
    raise RuntimeError(
        "No barrier trees found (sealed_pct never >= SEAL_THRESHOLD).\n"
        "This means bridge_score will be 0 for every zone.\n"
        "Fix: ensure notebook 03 writes real sealed_pct values, or set\n"
        "USE_S2_LST_PROXY = True in cell-imports and re-run from §3."
    )

# Identify top-15 zone cell_ids from scored_grid
if "top15_scenario_B" in grid.columns and "cell_id" in grid.columns:
    top15_cells = grid[grid["top15_scenario_B"] == True]["cell_id"].tolist()
else:
    top15_cells = grid["cell_id"].sample(15, random_state=42).tolist()
    print("WARNING: top15_scenario_B column not found — using random 15 cells.")

print(f"Computing bridge scores for {len(top15_cells)} priority zones…")
bridge_records = []

for i, cid in enumerate(top15_cells):
    score = bridge_score_for_zone(cid, trees_gdf, node_to_comp, G)
    bridge_records.append({"cell_id": cid, "bridge_score": score})
    if (i + 1) % 5 == 0 or (i + 1) == len(top15_cells):
        print(f"  Processed {i+1}/{len(top15_cells)} zones…")

bridge_df = pd.DataFrame(bridge_records).sort_values("bridge_score", ascending=False)
bridge_df["leverage_rank"] = range(1, len(bridge_df) + 1)

if "composite_B" in grid.columns:
    merge_cols = ["cell_id", "composite_B"]
    for col in ["nom_districte", "intervention_type"]:
        if col in grid.columns:
            merge_cols.append(col)
    bridge_df = bridge_df.merge(
        grid[merge_cols].drop_duplicates("cell_id"),
        on="cell_id", how="left",
    )

print("\nNetwork leverage ranking (top-15 zones by bridge score):")
print(bridge_df.to_string(index=False))

n_nonzero = (bridge_df["bridge_score"] > 0).sum()
print(f"\nZones with bridge_score > 0: {n_nonzero}/{len(bridge_df)}")
if n_nonzero == 0:
    print("STILL ZERO: sealed_pct proxy may not have sufficient variation,")
    print("or the priority zones do not overlap with high-sealing barrier cells.")
    print("Consider broadening the bridge analysis to all high-sealing cells")
    print("(not only the top-15 composite-score cells).")
