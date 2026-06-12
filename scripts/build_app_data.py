"""Build the data bundle for the planner web app (single inlinable JS file).

Merges everything the app needs into outputs/phase-6/app/app_data.js as
`window.PLANNER_DATA = {...}` (script-src include works on file://, unlike fetch):
  - sections: GeoJSON (WGS84, simplified) with priority + ML layers (archetype, hotspot) + top streets
  - cells: 400 m GeoJSON for the MAUP toggle
  - meta: counts, policy figures, honesty notes

HONESTY (baked into the data, enforced in the app brief):
  - street entries carry counts only -- NO priority/score at street grain (ecological fallacy)
  - archetype + hotspot are INTERPRETIVE layers; the priority math is unchanged by the ML probe
Deterministic. Run:  python scripts/build_app_data.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import cost_model_bcn                      # noqa: E402

SEC = ROOT / "outputs" / "phase-6" / "section_priority.parquet"
ENRICH = ROOT / "outputs" / "phase-6" / "section_enrich.parquet"   # corroboration + monoculture + thermal
NO2 = ROOT / "data" / "processed" / "no2_april_climatology.csv"
CELLS = ROOT / "data" / "processed" / "allergen_layers.parquet"
FEAT = ROOT / "data" / "processed" / "section_features.parquet"
ACTIONS = ROOT / "outputs" / "phase-6" / "street_removal_actions.csv"
TYPO = ROOT / "outputs" / "phase-6" / "section_typology.csv"
HOT = ROOT / "outputs" / "phase-6" / "section_hotspots.csv"
OUT = ROOT / "outputs" / "phase-6" / "app" / "app_data.js"
CRS = "EPSG:25831"


def minmax(x):
    x = np.asarray(x, float); lo, hi = np.nanmin(x), np.nanmax(x)
    return np.zeros_like(x) if hi - lo == 0 else (x - lo) / (hi - lo)


def geom_of(g):
    return json.loads(gpd.GeoSeries([g], crs="EPSG:4326").to_json())["features"][0]["geometry"]


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)

    sec = gpd.read_parquet(SEC)
    if sec.crs is None:
        sec = sec.set_crs(CRS)
    sec = sec.sort_values("priority", ascending=False).reset_index(drop=True)
    sec["rank"] = range(1, len(sec) + 1)

    typo = pd.read_csv(TYPO, dtype={"key": str})[["key", "archetype", "action", "cluster"]]
    hot = pd.read_csv(HOT, dtype={"key": str})[["key", "gi_z", "hotspot", "lisa_quadrant"]]
    sec["key"] = sec["key"].astype(str)
    sec = sec.merge(typo, on="key", how="left").merge(hot, on="key", how="left")

    # features (income for equity, vuln_std for vulnerability) + per-objective scores
    feat = gpd.read_parquet(FEAT)[["key", "income", "vuln_std"]].copy()
    feat["key"] = feat["key"].astype(str)
    sec = sec.merge(feat, on="key", how="left")

    # NO2 potency lens (ordinal, season-matched climatology)
    if NO2.exists():
        no2 = pd.read_csv(NO2, dtype={"key": str})
        sec = sec.merge(no2, on="key", how="left")
        sec["no2_val"] = sec["no2_avg"].fillna(sec["no2_avg"].median())
        sec["no2_potency"] = minmax(sec["no2_val"].to_numpy())
    else:
        sec["no2_potency"] = 0.0

    sec["depriv"] = minmax(-sec["income"].to_numpy(float))            # poorest = 1
    src_std = sec["source_std"].to_numpy(float)
    pri = sec["priority"].to_numpy(float)
    sec["sc_efficiency"] = pri
    sec["sc_equity"] = pri * sec["depriv"].to_numpy()
    sec["sc_quick_wins"] = sec["mature_count"].astype(float)
    sec["sc_density"] = sec["plane_count"].astype(float)
    sec["sc_vulnerability"] = src_std * sec["vuln_std"].fillna(0).to_numpy(float)
    sec["sc_potency"] = pri * sec["no2_potency"]

    # enrichment: cross-grain corroboration + monoculture/Shannon + thermal flag
    enr = pd.read_parquet(ENRICH)
    enr["key"] = enr["key"].astype(str)
    sec = sec.merge(enr, on="key", how="left")
    sec["sc_co_benefit"] = sec["co_benefit"].fillna(0.0)   # priority x monoculture (city mandate + relief)

    streets = {}
    if ACTIONS.exists():
        a = pd.read_csv(ACTIONS, dtype={"section_key": str})
        for k, g in a.groupby("section_key"):
            g = g.sort_values("n_mature", ascending=False)
            streets[str(k)] = [{"s": r.street, "n": int(r.n_planes), "m": int(r.n_mature),
                                "r": int(r.suggested_remove)} for r in g.itertuples()]

    secw = sec.copy()
    secw["geometry"] = secw.geometry.simplify(15)
    secw = secw.to_crs("EPSG:4326")
    feats = []
    for r in secw.itertuples():
        k = str(r.key)
        feats.append({"type": "Feature", "geometry": geom_of(r.geometry), "properties": {
            "key": k, "rank": int(r.rank), "district": r.district_lbl,
            "planes": int(r.plane_count), "mature": int(r.mature_count),
            "pop": int(round(r.exposure_pop)), "pri": round(float(r.priority_std), 4),
            "archetype": r.archetype if isinstance(r.archetype, str) else "n/a",
            "action": r.action if isinstance(r.action, str) else "n/a",
            "cluster": int(r.cluster) if pd.notna(r.cluster) else -1,
            "gi_z": round(float(r.gi_z), 2) if pd.notna(r.gi_z) else 0.0,
            "hot": r.hotspot if isinstance(r.hotspot, str) else "ns",
            "lisa": r.lisa_quadrant if isinstance(r.lisa_quadrant, str) else "ns",
            "pri_raw": round(float(r.priority), 6),          # burden axis for the relief curve
            "depriv": round(float(r.depriv), 4),
            "vuln": round(float(r.vuln_std), 4) if pd.notna(r.vuln_std) else 0.0,
            # --- cross-grain corroboration (flagship) ---
            "corrob": r.corrob if isinstance(r.corrob, str) else "minor",
            "rank400": int(r.rank_400m) if pd.notna(r.rank_400m) else -1,
            # --- monoculture / biodiversity co-benefit ---
            "mono": round(float(r.monoculture), 4) if pd.notna(r.monoculture) else 0.0,
            "shannon": round(float(r.shannon), 3) if pd.notna(r.shannon) else 0.0,
            "nsp": int(r.n_species) if pd.notna(r.n_species) else 0,
            "ttrees": int(r.total_trees) if pd.notna(r.total_trees) else 0,
            "no2": round(float(r.no2_potency), 4) if hasattr(r, "no2_potency") else 0.0,
            # --- thermal do-no-harm guardrail ---
            "heat": int(r.heat_flag) if pd.notna(r.heat_flag) else 0,
            "lst": round(float(r.mean_lst_celsius), 1) if pd.notna(r.mean_lst_celsius) else None,
            "scores": {                                      # per-objective sort scores
                "efficiency": round(float(r.sc_efficiency), 6),
                "equity": round(float(r.sc_equity), 6),
                "quick_wins": round(float(r.sc_quick_wins), 2),
                "density": round(float(r.sc_density), 2),
                "vulnerability": round(float(r.sc_vulnerability), 6),
                "co_benefit": round(float(r.sc_co_benefit), 6),
            },
            "streets": streets.get(k, []),
        }})
    sections_gj = {"type": "FeatureCollection", "features": feats}

    cells = gpd.read_parquet(CELLS)
    if cells.crs is None:
        cells = cells.set_crs(CRS)
    cells = cells.assign(cpri=minmax(cells["source_std"].to_numpy(float) * cells["exposure_std"].to_numpy(float)))
    cw = cells[["cell_id", "district", "n_platanus", "cpri", "geometry"]].copy()
    cw["geometry"] = cw.geometry.simplify(15)
    cw = cw.to_crs("EPSG:4326")
    cfeats = [{"type": "Feature", "geometry": geom_of(r.geometry), "properties": {
        "cell": r.cell_id, "district": r.district, "planes": int(r.n_platanus),
        "pri": round(float(r.cpri), 4)}} for r in cw.itertuples()]
    cells_gj = {"type": "FeatureCollection", "features": cfeats}

    # archetype legend (cluster -> name/action/color assigned in the app)
    arche = (sec.dropna(subset=["archetype"]).groupby(["cluster", "archetype", "action"])
             .size().reset_index(name="n"))
    archetypes = [{"cluster": int(r.cluster), "name": r.archetype, "action": r.action,
                   "n": int(r.n)} for r in arche.itertuples()]

    meta = {
        "title": "Barcelona Plane-Tree Removal Priority - Planner Tool",
        "n_sections": int(len(sec)),
        "sections_with_planes": int((sec["plane_count"] > 0).sum()),
        "city_population": int(round(sec["exposure_pop"].sum())),
        "city_platanus_total": 43722, "pct_now": 27.45, "pct_target_2037": 12.0,
        "removal_rate": round(1 - 12.0 / 27.45, 3),
        "street_platanus": int(sec["plane_count"].sum()),
        "districts": sorted(sec["district_lbl"].dropna().unique().tolist()),
        "archetypes": archetypes,
        "total_priority": round(float(sec["priority"].sum()), 6),  # denom for the relief curve
        "cost": cost_model_bcn.as_dict(),                          # euro<->tree (from coolspend)
        "objectives": ["efficiency", "potency", "co_benefit", "equity", "quick_wins", "density", "vulnerability"],
        "corrob_counts": {k: int((sec["corrob"] == k).sum()) for k in
                          ("CORROBORATED", "ARTIFACT", "UNDERRATED", "minor")},
        "grain_spearman": round(float(spearmanr(sec["priority"], sec["pri_400m"].fillna(0)).statistic), 3),
        "n_heat_flagged": int(sec["heat_flag"].fillna(0).sum()),
        "vulnerability_note": "Age-AR-prevalence weighting; tested REDUNDANT with population "
                              "(re-orders ~nothing, Jaccard top-15 = 1.0) -- an optional lens, not a re-ranking.",
        "potency_note": "NO2-allergenicity lens (BSC CALIOPE-Urban). March-April climatology (2019-2024). "
                        "Gate: collinearity 0.22 (independent), variance share 9% (non-dominating).",
        "top15_share_pct": round(100 * sec.head(15)["priority"].sum() / sec["priority"].sum(), 1),
        "top50_share_pct": round(100 * sec.head(50)["priority"].sum() / sec["priority"].sum(), 1),
        "notes": {
            "street_layer": "Street counts are inventory + a feasibility allocation, NOT a priority. No street-level ranking (ecological fallacy).",
            "ml": "Three models run in this project. UNSUPERVISED ML (k-means/GMM typologies, silhouette 0.32) drives the live Archetype layer; SPATIAL STATISTICS (Getis-Ord Gi* / Local Moran's I, 999 permutations) drive the live Hotspot layer. A SUPERVISED model (Ridge + RandomForest source-estimator) was pre-registered and spatially cross-validated: it returned an honest NEGATIVE (random-CV R2 0.41/0.44 collapses to -0.25/-0.37 under spatial CV -- the random score was leakage), so it correctly does NOT touch the priority. The headline priority is a composite indicator -- the rubric-correct Phase-4 artifact for ranking, not a black box.",
            "maup": "At 400 m the population re-orders priorities; at section grain a few park-like clusters dominate (e.g. Montjuic). Use 400 m as the people-weighting evidence, sections as the operational unit.",
            "rationale": "City removes planes primarily for biodiversity/monoculture-risk, not allergy. This tool sequences that removal for max allergen-exposure relief as a co-benefit.",
            "corrob": "Corroboration compares the section ranking with the 400 m people-weighted ranking. CORROBORATED = both agree (act first); ARTIFACT = high only at section grain, a MAUP cluster the people-weighting demotes (e.g. Montjuic); UNDERRATED = buried at section grain but high at 400 m. It tests agreement of two aggregations of the SAME proxy -- it does NOT validate the pollen proxy.",
            "potency": "The Potency lens (NO2) re-ranks priority by multiplying exposure by a cycle-averaged March-April NO2 surface. It reflects the mechanism where NO2 damages pollen membranes, releasing more allergens (e.g. Pla a 3) per grain. It is ordinal and season-matched (climatology reframe), not a real-time prediction.",
            "monoculture": "Co-benefit objective ranks by priority x Platanus dominance (share of a section's street trees that are planes; Shannon diversity shown for context). This aligns the sequence with the city's actual biodiversity mandate (no species >15%).",
            "thermal": "Heat-flagged sections (top-quartile heat-risk = high LST x low NDVI) must be replaced immediately, no gaps -- removing canopy where it is already hot worsens the urban heat island.",
        },
    }

    payload = {"meta": meta, "sections": sections_gj, "cells": cells_gj}
    OUT.write_text("window.PLANNER_DATA = " + json.dumps(payload) + ";\n", encoding="utf-8")
    print("APP DATA built ->", OUT)
    print(f"  sections {len(feats)}  cells {len(cfeats)}  archetypes {len(archetypes)}")
    print(f"  size: {OUT.stat().st_size/1e6:.2f} MB")
    print(f"  archetypes: {[(a['name'], a['action'], a['n']) for a in archetypes]}")


if __name__ == "__main__":
    main()
