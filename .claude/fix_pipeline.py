"""
Atomic fix script for the Mycorrhizal Barcelona pipeline.
Applies the 12 bug fixes identified by the Model QA + Code Reviewer audits.
Run from repo root:
    python .claude/fix_pipeline.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NB_DIR = REPO / "notebooks"


def load_nb(name):
    return json.loads((NB_DIR / name).read_text(encoding="utf-8"))


def save_nb(name, nb):
    (NB_DIR / name).write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")


def cell_src(cell):
    s = cell.get("source", "")
    return "".join(s) if isinstance(s, list) else s


def set_cell_src(cell, new_src):
    cell["source"] = new_src.splitlines(keepends=True)


def find_cell_by_id(nb, cell_id):
    for c in nb["cells"]:
        if c.get("id") == cell_id:
            return c
    raise KeyError(cell_id)


# ════════════════════════════════════════════════════════════════════════════
# FILE 1: notebooks/02-grid-trees.ipynb
# BUG-1 (CRITICAL) + BUG-2 (MAJOR)
# ════════════════════════════════════════════════════════════════════════════
nb02 = load_nb("02-grid-trees.ipynb")
p5 = find_cell_by_id(nb02, "o5p6q7r8")
old = cell_src(p5)
new = '''# ── Hardcoded stub for top-20 species (~90% of inventory) ─────────────────
TOP20_MYCO = {
    "Platanus × acerifolia"          : "AM",
    "Celtis australis"               : "AM",
    "Tipuana tipu"                   : "AM",
    "Styphnolobium japonicum"         : "AM",
    "Melia azedarach"                : "AM",
    "Brachychiton populneus"          : "AM",
    "Jacaranda mimosifolia"           : "AM",
    "Pinus pinea"                    : "EM",
    "Ligustrum lucidum"               : "AM",
    "Pyrus calleryana \'Chanticleer\'" : "AM",
    "Ulmus pumila"                   : "AM",
    "Cercis siliquastrum"             : "AM",
    "Prunus cerasifera \'Pissardii\'" : "AM",
    "Cupressus sempervirens"          : "NM",
    "Citrus × aurantium"             : "AM",
    "Robinia pseudoacacia"            : "NM",
    "Pinus halepensis"               : "EM",
    "Quercus ilex"                   : "EM",
    "Magnolia grandiflora"            : "AM",
    "Grevillea robusta"               : "AM",
}

FUNGALROOT_PATH = DATA_DIR / "fungalroot.csv"


def _normalise_myco(v):
    """Normalise a raw FungalRoot mycorrhizal-type string to {AM, EM, NM}."""
    if not isinstance(v, str):
        return "NM"
    v = v.strip()
    v_upper = v.upper()
    if v_upper.startswith("ECM") or "ECM" in v_upper:
        return "EM"
    if v_upper == "AM":
        return "AM"
    if "AM" in v_upper and "ECM" not in v_upper:
        return "AM"
    if "NON-MYCORRHIZAL" in v_upper.replace("-", "-") or v_upper == "NM":
        return "NM"
    if v_upper in ("OM", "ERM"):
        return "NM"  # treated as non-AM/EM for our purposes
    return "NM"


if FUNGALROOT_PATH.exists():
    fr = pd.read_csv(FUNGALROOT_PATH, encoding="utf-8")
    # Normalise column names — accept both naming conventions
    fr.columns = [c.strip().lower().replace(" ", "_") for c in fr.columns]
    name_col = next(
        (c for c in fr.columns if "species" in c or "name" in c), fr.columns[0]
    )
    type_col = next(
        (c for c in fr.columns if "myco" in c or "type" in c), fr.columns[1]
    )
    fr = fr.rename(columns={name_col: "species_name", type_col: "myco_type"})
    fr["myco_type"] = fr["myco_type"].str.upper().str.strip()
    # BUG-1 fix: collapse compound FungalRoot strings ("EcM, AM undetermined",
    # "EcM, no AM colonization", "EcM,AM", …) into the canonical {AM, EM, NM}
    # vocabulary expected by the per-cell aggregator.
    fr["myco_type"] = fr["myco_type"].apply(_normalise_myco)
    myco_map = dict(zip(fr["species_name"], fr["myco_type"]))
    print(f"Loaded FungalRoot CSV: {len(myco_map):,} species mappings")
    # BUG-2 fix: curated 20-species stub OVERRIDES the CSV value for safety.
    for sp, mt in TOP20_MYCO.items():
        myco_map[sp] = mt
else:
    myco_map = TOP20_MYCO.copy()
    print("FungalRoot CSV not found — using hardcoded top-20 stub.")
    print("(Place data/fungalroot.csv to use the full database.)")

# ── Map myco_type onto every joined tree row ───────────────────────────────
joined["myco_type"] = joined["cat_nom_cientific"].map(myco_map).fillna("NM")

coverage = (joined["myco_type"] != "NM").sum() / len(joined) * 100
print(f"\\nMyco type assigned ({coverage:.1f}% of tree-rows):")
print(joined["myco_type"].value_counts().to_string())'''
set_cell_src(p5, new)
save_nb("02-grid-trees.ipynb", nb02)
print("[02-grid-trees.ipynb] BUG-1, BUG-2 applied to cell o5p6q7r8")


# ════════════════════════════════════════════════════════════════════════════
# FILE 2: notebooks/03-scoring.ipynb
# BUG-3, BUG-4, BUG-5, BUG-6
# ════════════════════════════════════════════════════════════════════════════
nb03 = load_nb("03-scoring.ipynb")

# ── BUG-3: cell-s1 — sealed_pct already 0–1 in the GeoTIFF ──────────────────
s1 = find_cell_by_id(nb03, "cell-s1")
old = cell_src(s1)
assert "scale=1/100" in old, "BUG-3 marker not found in cell-s1"
new = old.replace(
    "    sealed_raw = zonal_mean_from_raster(SEALED_RASTER_PATH, grid, band=1, scale=1/100)",
    "    # BUG-3 fix: process_urban_atlas.py writes sealed_surface.tif on a 0–1 scale\n"
    "    # already (verified min=0.024, max=0.894). Do NOT divide by 100 again.\n"
    "    sealed_raw = zonal_mean_from_raster(SEALED_RASTER_PATH, grid, band=1, scale=1.0)",
)
# Update the upstream comment that justified the /100
new = new.replace(
    "    # Urban Atlas stores values as 0–100 % imperviousness → divide by 100\n",
    "    # Urban Atlas raster is already on a 0–1 scale (process_urban_atlas.py).\n",
)
set_cell_src(s1, new)
print("[03-scoring.ipynb] BUG-3 applied to cell-s1")

# ── BUG-4: cell-s4 — am_pct/em_pct stored 0–100, not 0–1 ────────────────────
s4 = find_cell_by_id(nb03, "cell-s4")
old = cell_src(s4)
new = old
# Function-internal thresholds
new = new.replace("em_dom = em_pct >= 0.5",
                   "em_dom = em_pct >= 50  # BUG-4 fix: am_pct/em_pct stored on 0-100 scale")
new = new.replace("    am_dom = am_pct >= 0.8",
                   "    am_dom = am_pct >= 80  # BUG-4 fix: 0-100 scale")
# Reporting block after the function call
new = new.replace('print(f"\\nAM-dominant cells (score=0.5): {(grid[\'am_pct\'] >= 0.8).sum():,}")',
                   'print(f"\\nAM-dominant cells (score=0.5): {(grid[\'am_pct\'] >= 80).sum():,}")')
new = new.replace('print(f"EM-dominant cells:             {(grid[\'em_pct\'] >= 0.5).sum():,}")',
                   'print(f"EM-dominant cells:             {(grid[\'em_pct\'] >= 50).sum():,}")')
new = new.replace('f"{((grid[\'am_pct\'] < 0.8) & (grid[\'em_pct\'] < 0.5)).sum():,}"',
                   'f"{((grid[\'am_pct\'] < 80) & (grid[\'em_pct\'] < 50)).sum():,}"')
assert new != old, "BUG-4 replacements did not change cell-s4"
set_cell_src(s4, new)
print("[03-scoring.ipynb] BUG-4 applied to cell-s4")

# ── BUG-5: cell-colonisation — trees_young_pct on 0–100 scale ───────────────
col_cell = find_cell_by_id(nb03, "cell-colonisation")
old = cell_src(col_cell)
new = old.replace(
    "grid[\"top15_scenario_B\"] & (grid[\"trees_young_pct\"] >= 0.3)",
    "grid[\"top15_scenario_B\"] & (grid[\"trees_young_pct\"] >= 30)  # BUG-5 fix: 0-100 scale",
)
assert new != old, "BUG-5 replacement did not change cell-colonisation"
set_cell_src(col_cell, new)
print("[03-scoring.ipynb] BUG-5 applied to cell-colonisation")

# ── BUG-6: cell-top15 — list-based district fill instead of selected[-1] ────
top15 = find_cell_by_id(nb03, "cell-top15")
old = cell_src(top15)
new = '''def select_top15_with_district_constraint(
    gdf: gpd.GeoDataFrame,
    composite_col: str,
    district_col: str = "nom_districte",
    k: int = 15,
) -> pd.Index:
    """
    Select top-k cells ranked by composite_col.
    Ensure every district that has any cells in the full grid has at least
    one representative in the returned set.

    BUG-6 fix: previous version overwrote selected[-1] for every missing
    district, so only the LAST missing district got a representative. The
    new logic adds one cell per missing district, displacing the lowest-
    ranked currently-selected cell whose district has > 1 representative.

    Returns: pandas Index of selected cell index labels.
    """
    scored = gdf.sort_values(composite_col, ascending=False)
    selected = scored.head(k).copy()
    selected_districts = set(selected[district_col].dropna().unique())
    all_districts = set(scored[district_col].dropna().unique())
    missing = sorted(all_districts - selected_districts)

    for d in missing:
        candidate = scored[scored[district_col] == d].nlargest(1, composite_col)
        if candidate.empty:
            continue
        # Find the lowest-ranked currently-selected cell whose district has
        # more than one representative — that\'s the safe one to drop.
        selected_sorted = selected.sort_values(composite_col)
        drop_idx = None
        for idx in selected_sorted.index:
            cell_d = selected.loc[idx, district_col]
            if (selected[district_col] == cell_d).sum() > 1:
                drop_idx = idx
                break
        if drop_idx is not None:
            selected = selected.drop(drop_idx)
        # If no over-represented district exists we simply grow the set —
        # the constraint is "at least one per district", so growing is fine.
        selected = pd.concat([selected, candidate])
    selected = selected.sort_values(composite_col, ascending=False)
    return selected.index

if "district_name" in grid.columns and "nom_districte" not in grid.columns:
      grid = grid.rename(columns={"district_name": "nom_districte"})
top15_indices = {}
for label in ["A", "B", "C"]:
    idx = select_top15_with_district_constraint(
        grid, f"composite_{label}", district_col="nom_districte", k=15
    )
    top15_indices[label] = idx
    col = f"top15_scenario_{label}"
    grid[col] = False
    grid.loc[idx, col] = True
    n_districts = grid.loc[idx, "nom_districte"].nunique()
    print(f"Scenario {label}: {len(idx)} cells selected, {n_districts} districts represented")

print("\\nTop-15 district coverage (Scenario B — primary):")
print(
    grid[grid["top15_scenario_B"]][["nom_districte", "composite_B", "rank_B"]]
    .sort_values("rank_B")
    .to_string(index=False)
)'''
set_cell_src(top15, new)
print("[03-scoring.ipynb] BUG-6 applied to cell-top15")

save_nb("03-scoring.ipynb", nb03)


# ════════════════════════════════════════════════════════════════════════════
# FILE 3: notebooks/04-connectivity.ipynb
# BUG-7, BUG-8
# ════════════════════════════════════════════════════════════════════════════
nb04 = load_nb("04-connectivity.ipynb")

# ── BUG-7: bridge score — count distinct component pairs, not raw edges ─────
bridge_fn = find_cell_by_id(nb04, "cell-bridge-fn")
old = cell_src(bridge_fn)
new = '''def bridge_score_for_zone(
    zone_cell_id: str,
    trees_gdf: gpd.GeoDataFrame,
    node_to_comp: dict,
    G: nx.Graph,
) -> int:
    """
    Compute how many DISTINCT component pairs would be linked by removing
    the sealing barrier in the given zone cell.

    BUG-7 fix: previously this counted every potential new edge to a
    different-component neighbour, which double-counts and inflates the
    score whenever a blocked tree (component -1) reaches several neighbours
    in the same other component. We now collect the set of component IDs
    each blocked tree reaches and tally distinct unordered component pairs.

    Returns
    -------
    int : number of distinct (component_a, component_b) pairs that would
          become connected.
    """
    # Trees currently blocked in this zone\'s cell
    blocked = trees_gdf[
        (trees_gdf["cell_id"] == zone_cell_id) &
        (trees_gdf["sealed_pct"] >= SEAL_THRESHOLD)
    ].copy()

    if len(blocked) == 0:
        return 0

    # All trees within edge-distance radius of blocked trees
    blocked_coords = blocked[["x_etrs89", "y_etrs89"]].values

    # Build a local tree index for all trees in the graph
    all_graph_trees = trees_gdf[trees_gdf["tree_id"].isin(G.nodes())].copy()
    if len(all_graph_trees) == 0:
        return 0

    all_coords = all_graph_trees[["x_etrs89", "y_etrs89"]].values
    all_ids    = all_graph_trees["tree_id"].values
    all_sealed = all_graph_trees["sealed_pct"].values
    all_myco   = all_graph_trees["myco_type"].values

    kd = cKDTree(all_coords)

    new_component_pairs = set()
    for bi, (bx, by) in enumerate(blocked_coords):
        b_tree = blocked.iloc[bi]
        b_myco = b_tree["myco_type"]

        dist_thresh = AM_DISTANCE_M if b_myco == "AM" else EM_DISTANCE_M
        nbr_idx = kd.query_ball_point([bx, by], r=dist_thresh)

        reached_comps = set()
        for j in nbr_idx:
            if all_myco[j] != b_myco:           # no AM–EM edges
                continue
            if all_sealed[j] >= SEAL_THRESHOLD:  # neighbour also sealed
                continue
            n_id = all_ids[j]
            n_comp = node_to_comp.get(n_id, None)
            if n_comp is not None:
                reached_comps.add(n_comp)

        # Pair up every distinct component the blocked tree could bridge.
        comps_sorted = sorted(reached_comps)
        for a in range(len(comps_sorted)):
            for b in range(a + 1, len(comps_sorted)):
                new_component_pairs.add((comps_sorted[a], comps_sorted[b]))

    return len(new_component_pairs)


print("Bridge score function defined.")'''
set_cell_src(bridge_fn, new)
print("[04-connectivity.ipynb] BUG-7 applied to cell-bridge-fn")

# ── BUG-8: simulate_spread — frontier-based BFS-like expansion ──────────────
spread_fn = find_cell_by_id(nb04, "cell-spread-fn")
old = cell_src(spread_fn)
new = '''def simulate_spread(
    trees_gdf: gpd.GeoDataFrame,
    source_nodes: set,
    G: nx.Graph,
    n_seasons: int = 5,
    spread_m_per_season: float = 2.0,
    seal_threshold: float = SEAL_THRESHOLD,
    label: str = "baseline",
) -> dict:
    """
    Simulate seasonal spread of fungal networks from source patches.

    BUG-8 fix: the previous implementation issued a single radius query
    from each source node and grew the radius linearly with season — that
    is not propagation, it is a static buffer.  The 2 m/season "growth"
    was documented but never implemented because nothing was passed from
    season N to season N+1.

    The new implementation is frontier-based: each season, we extend the
    front by `spread_m_per_season` metres around every CURRENTLY-reached
    tree, filter by the sealing barrier, and accumulate newly-reached
    trees into the reached set. Over 5 seasons this produces genuine
    propagation rather than a series of independent radii.

    Returns dict keyed `season_0`..`season_n`, each a set of reached tree_ids.
    """
    # Build coordinate arrays for all non-barrier trees (the universe we
    # can ever reach). Trees in barrier cells are filtered out up-front.
    non_barrier = trees_gdf[trees_gdf["sealed_pct"] < seal_threshold].copy()
    if len(non_barrier) == 0:
        print(f"[{label}] No non-barrier trees — spread trivially 0.")
        return {f"season_{s}": set() for s in range(n_seasons + 1)}

    nb_coords = non_barrier[["x_etrs89", "y_etrs89"]].values
    nb_ids    = non_barrier["tree_id"].values
    id_to_idx = {tid: i for i, tid in enumerate(nb_ids)}

    kd = cKDTree(nb_coords)

    # Season 0: source trees that are themselves in non-barrier cells.
    reached = {tid for tid in source_nodes if tid in id_to_idx}
    history = {0: set(reached)}

    if not reached:
        print(f"[{label}] No source trees in non-barrier cells — spread trivially 0.")
        return {f"season_{s}": history.get(s, set()) for s in range(n_seasons + 1)}

    for season in range(1, n_seasons + 1):
        # Frontier = every reached tree (BFS-like expansion from the front).
        frontier_idx = [id_to_idx[tid] for tid in reached]
        frontier_coords = nb_coords[frontier_idx]

        radius = spread_m_per_season   # NB: per-season growth, not cumulative
        neighbour_idx_lists = kd.query_ball_point(frontier_coords, r=radius)

        new_reached = set()
        for nbr_list in neighbour_idx_lists:
            for j in nbr_list:
                tid = nb_ids[j]
                if tid in reached:
                    continue
                new_reached.add(tid)
        if not new_reached:
            # No further growth possible — record same set for remaining seasons
            for s in range(season, n_seasons + 1):
                history[s] = set(reached)
            break
        reached |= new_reached
        history[season] = set(reached)

    # Ensure we always emit n_seasons+1 keys even if growth halted early.
    for s in range(n_seasons + 1):
        history.setdefault(s, set(reached))

    print(f"[{label}] Spread result:")
    for s in [0, 1, 3, 5]:
        if s <= n_seasons:
            print(f"  Season {s}: {len(history[s]):,} trees reachable")
    return {f"season_{s}": history[s] for s in range(n_seasons + 1)}


print("Spread simulation function defined.")'''
set_cell_src(spread_fn, new)
print("[04-connectivity.ipynb] BUG-8 applied to cell-spread-fn")

save_nb("04-connectivity.ipynb", nb04)


# ════════════════════════════════════════════════════════════════════════════
# FILE 4: notebooks/05-visualisation.ipynb
# BUG-9, BUG-10, BUG-11
# ════════════════════════════════════════════════════════════════════════════
nb05 = load_nb("05-visualisation.ipynb")

# ── BUG-9: scenario labels in chart cell b0c1d2e3 + caption strings ─────────
chart_cell = find_cell_by_id(nb05, "b0c1d2e3")
old = cell_src(chart_cell)
new = old.replace(
    '    ("Scenario A\\n(Equal weights)",      ids_A_p),\n'
    '    ("Scenario B\\n(LST-heavy)",          ids_B_p),\n'
    '    ("Scenario C\\n(Sealed-heavy)",       ids_C_p),',
    '    # BUG-9 fix: scenario labels now match the implemented weights\n'
    '    # in 03-scoring.ipynb (A=equal, B=sealed-dominant, C=heat+canopy).\n'
    '    ("Scenario A\\n(Equal weights)",                  ids_A_p),\n'
    '    ("Scenario B\\n(Sealed-dominant, recommended)",   ids_B_p),\n'
    '    ("Scenario C\\n(Heat + canopy weighted)",         ids_C_p),',
)
assert new != old, "BUG-9 chart label replacement did not match"
set_cell_src(chart_cell, new)
print("[05-visualisation.ipynb] BUG-9 applied to cell b0c1d2e3 (chart labels)")

# Also fix the per-zone HTML caption that reads "Scenario B: LST-heavy weighting"
html_cell = find_cell_by_id(nb05, "e3f4a5b6")
old = cell_src(html_cell)
assert "LST-heavy weighting" in old, "BUG-9 HTML caption marker missing"
new = old.replace(
    "Top 15 zones ranked by composite barrier score (Scenario B: LST-heavy weighting).",
    "Top 15 zones ranked by composite barrier score "
    "(Scenario B: Sealed-dominant weighting, recommended).",
)
set_cell_src(html_cell, new)
print("[05-visualisation.ipynb] BUG-9 applied to cell e3f4a5b6 (HTML caption)")

# ── BUG-10: data label based on variance, not file presence ─────────────────
synth_cell = find_cell_by_id(nb05, "c9d0e1f2")
old = cell_src(synth_cell)
assert 'DATA_LABEL = "SYNTHETIC PLACEHOLDER" if IS_SYNTHETIC else "REAL DATA"' in old, (
    "BUG-10 marker missing in cell c9d0e1f2"
)
new = old.replace(
    'DATA_LABEL = "SYNTHETIC PLACEHOLDER" if IS_SYNTHETIC else "REAL DATA"\n'
    'print(f"\\nData status: {DATA_LABEL}")\n'
    'print(f"scored_grid rows: {len(scored_grid):,}")',
    '# BUG-10 fix: real-data label now also reflects sub-score VARIANCE.\n'
    '# A file can be present but contain near-uniform values (e.g. when the\n'
    '# raster scale was wrong upstream), which is still unreliable output.\n'
    'def _data_label(gdf, is_synth):\n'
    '    if is_synth:\n'
    '        return "SYNTHETIC PLACEHOLDER"\n'
    '    low_var_subs = []\n'
    '    for sub in ["s1_sealed", "s2_lst", "s3_ndvi"]:\n'
    '        if sub in gdf.columns and gdf[sub].std() < 0.05:\n'
    '            low_var_subs.append(sub)\n'
    '    if low_var_subs:\n'
    '        return ("DATA-WARNING: low variance in sub-scores "\n'
    '                f"({\', \'.join(low_var_subs)}) — output may be unreliable")\n'
    '    return "REAL DATA"\n'
    '\n'
    'DATA_LABEL = _data_label(scored_grid, IS_SYNTHETIC)\n'
    'print(f"\\nData status: {DATA_LABEL}")\n'
    'print(f"scored_grid rows: {len(scored_grid):,}")',
)
assert new != old, "BUG-10 replacement did not change cell c9d0e1f2"
set_cell_src(synth_cell, new)
print("[05-visualisation.ipynb] BUG-10 applied to cell c9d0e1f2")

# ── BUG-11: limitations footer section 5 — describe the actual flag ─────────
lim_cell = find_cell_by_id(nb05, "a5b6c7d8")
old = cell_src(lim_cell)
old_para = (
    "In such contexts the expected mycorrhizal type is a biological potential, not a\n"
    "reflection of current colonisation status. The `colonisation_uncertain` flag in\n"
    "the tabular report identifies zones where this caveat is likely to apply based on\n"
    "sealed-surface fraction > 85% and/or LST anomaly > 4°C."
)
new_para = (
    "In such contexts the expected mycorrhizal type is a biological potential, not a\n"
    "reflection of current colonisation status. The `colonisation_uncertain` flag in\n"
    "the tabular report is True for cells where ≥30% of trees were planted within the\n"
    "past 5 years. These cells may have lower-than-expected mycorrhizal colonisation\n"
    "regardless of host species (FungalRoot lookup assumes colonisation-competent\n"
    "substrate, which is not guaranteed in recently-engineered urban substrates)."
)
assert old_para in old, "BUG-11 paragraph not found in cell a5b6c7d8"
new = old.replace(old_para, new_para)
set_cell_src(lim_cell, new)
print("[05-visualisation.ipynb] BUG-11 applied to cell a5b6c7d8")

save_nb("05-visualisation.ipynb", nb05)


# ════════════════════════════════════════════════════════════════════════════
# FILE 5: data/process_urban_atlas.py — BUG-12
# ════════════════════════════════════════════════════════════════════════════
pua_path = REPO / "data" / "process_urban_atlas.py"
text = pua_path.read_text(encoding="utf-8")
assert "12230: 0.70" in text, "BUG-12 marker missing"
text = text.replace("12230: 0.70,", "12230: 0.50,")  # Railways: align with UA Imperviousness Density bands
pua_path.write_text(text, encoding="utf-8")
print("[data/process_urban_atlas.py] BUG-12 applied (railways 0.70 -> 0.50)")


# ════════════════════════════════════════════════════════════════════════════
# FILE 6: docs/system-sketch-v0.md — BUG-13 (doc only)
# ════════════════════════════════════════════════════════════════════════════
doc_path = REPO / "docs" / "system-sketch-v0.md"
text = doc_path.read_text(encoding="utf-8")
old_line = (
    "    - **Scenario B — Sealed-dominant (recommended primary):** "
    "sealed 0.50 / LST 0.17 / NDVI 0.17 / host-mismatch 0.05"
)
new_line = (
    "    - **Scenario B — Sealed-dominant (recommended primary):** "
    "sealed 0.55 / LST 0.20 / NDVI 0.20 / host-mismatch 0.05"
)
assert old_line in text, "BUG-13 doc line not found"
text = text.replace(old_line, new_line)
doc_path.write_text(text, encoding="utf-8")
print("[docs/system-sketch-v0.md] BUG-13 applied (Scenario B weights documented to match implementation)")

print("\nAll 13 fixes applied successfully.")
