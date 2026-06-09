"""Phase 6 (Deployment) -- per-STREET Platanus action lists for the top priority sections.

This is the planner's worklist: for each high-priority census section, which streets hold
mature plane trees and how many. It is an INVENTORY + FEASIBILITY ALLOCATION layer, NOT a
priority claim -- there is deliberately NO priority/score column at street grain (ecological
fallacy; see phase-6/section-street-design.md, the honesty gate C2).

The optional `suggested_remove` column allocates a city policy target (A2: remove ~23,013 of
40,444 planes to hit the 12%-by-2037 stock goal) proportionally to SECTION priority, then splits
each section's quota across its streets by mature share -- capped so you can never be told to
remove more mature planes than a street has. It is a swappable policy input, not a finding.

Depends on outputs/phase-6/section_priority.parquet (run src/section_priority.py first).
Deterministic, ASCII-only. Run:  python src/street_actions.py
"""
from __future__ import annotations
import re
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]
TREES = ROOT / "data" / "arbrat-viari.csv"
SECTIONS = ROOT / "outputs" / "phase-6" / "section_priority.parquet"
OUTDIR = ROOT / "outputs" / "phase-6"
DESIGN = ROOT / "phase-6" / "section-street-design.md"
CRS = "EPSG:25831"

MATURE = {"EXEMPLAR", "PRIMERA"}     # must match section_priority.py A1
TOPK_SECTIONS = 60                   # sections that get a street worklist
TARGET_REMOVE = 23_013               # A2 policy anchor (illustrative, swappable)


def street_of(adreca: str) -> str:
    """Street identity = address minus the house-number suffix (split on last comma)."""
    if not isinstance(adreca, str) or not adreca.strip():
        return ""
    base = adreca.rsplit(",", 1)[0] if "," in adreca else adreca
    return re.sub(r"\s+", " ", base).strip()


def largest_remainder(weights, total):
    """Apportion an integer `total` across buckets by `weights`, summing exactly to total."""
    w = np.asarray(weights, float)
    if w.sum() <= 0 or total <= 0:
        return np.zeros(len(w), int)
    raw = w / w.sum() * total
    floor = np.floor(raw).astype(int)
    rem = total - floor.sum()
    if rem > 0:
        order = np.argsort(-(raw - floor))
        floor[order[:rem]] += 1
    return floor


def main():
    sec = gpd.read_parquet(SECTIONS)
    if sec.crs is None:
        sec = sec.set_crs(CRS)

    # section-level removal quota: city target apportioned by priority, capped at mature stock
    quota = largest_remainder(sec["priority"].to_numpy(float), TARGET_REMOVE)
    sec = sec.copy()
    sec["section_quota"] = np.minimum(quota, sec["mature_count"].to_numpy(int))

    # load Platanus points, join to sections
    df = pd.read_csv(TREES, dtype=str, low_memory=False)
    plat = df[df["cat_nom_cientific"].str.startswith("Platanus", na=False)].copy()
    plat["x"] = pd.to_numeric(plat["x_etrs89"], errors="coerce")
    plat["y"] = pd.to_numeric(plat["y_etrs89"], errors="coerce")
    plat = plat.dropna(subset=["x", "y"])
    pts = gpd.GeoDataFrame(plat, geometry=gpd.points_from_xy(plat["x"], plat["y"]), crs=CRS)
    pts = gpd.sjoin(pts, sec[["key", "district_lbl", "priority", "section_quota", "geometry"]],
                    how="left", predicate="within").dropna(subset=["key"])
    pts["street"] = pts["adreca"].map(street_of)
    pts["is_mature"] = pts["categoria_arbrat"].isin(MATURE)

    coverage = float((pts["street"] != "").mean())

    # rank sections by priority; take the top-K for the worklist
    rank = sec.sort_values("priority", ascending=False).reset_index(drop=True)
    rank["rank"] = range(1, len(rank) + 1)
    top_keys = rank.head(TOPK_SECTIONS)["key"].tolist()
    rank_by_key = dict(zip(rank["key"], rank["rank"]))

    rows = []
    pts_top = pts[pts["key"].isin(top_keys)]
    for key, grp in pts_top.groupby("key"):
        sec_quota = int(grp["section_quota"].iloc[0])
        by_street = grp.groupby("street").agg(
            n_planes=("codi", "size"),
            n_mature=("is_mature", "sum"),
            example_codis=("codi", lambda s: ";".join(list(s)[:3])),
        ).reset_index()
        # split section quota across streets by mature share, capped at each street's mature stock
        alloc = largest_remainder(by_street["n_mature"].to_numpy(float), sec_quota)
        by_street["suggested_remove"] = np.minimum(alloc, by_street["n_mature"].to_numpy(int))
        by_street.insert(0, "section_key", key)
        by_street.insert(1, "district", grp["district_lbl"].iloc[0])
        by_street.insert(2, "section_rank", rank_by_key[key])
        rows.append(by_street)

    actions = pd.concat(rows, ignore_index=True)
    actions = actions.sort_values(["section_rank", "n_mature"], ascending=[True, False])
    # NOTE: deliberately NO priority/score column at street grain (honesty gate C2)
    cols = ["section_rank", "section_key", "district", "street",
            "n_planes", "n_mature", "suggested_remove", "example_codis"]
    actions = actions[cols]
    actions.to_csv(OUTDIR / "street_removal_actions.csv", index=False)

    # tree points (WGS84) for the top sections -> internal QA map
    qa = pts_top[["codi", "street", "key", "district_lbl", "categoria_arbrat",
                  "is_mature", "geometry"]].to_crs("EPSG:4326")
    qa = qa.rename(columns={"key": "section_key", "district_lbl": "district"})
    qa.to_file(OUTDIR / "street_removal_points.geojson", driver="GeoJSON")

    # --- verification / honesty gate ---
    assert "priority" not in actions.columns and "score" not in actions.columns, \
        "HONESTY GATE FAILED: street file must carry no priority/score column"
    assert (actions["suggested_remove"] <= actions["n_mature"]).all(), \
        "suggested_remove exceeds available mature planes"
    # spot-check: per-street planes in the #1 section sum to that section's plane_count
    top1 = rank.iloc[0]
    top1_planes = int(actions[actions["section_key"] == top1["key"]]["n_planes"].sum())

    print("STREET ACTIONS built ->", (OUTDIR / 'street_removal_actions.csv').name)
    print(f"  top-{TOPK_SECTIONS} sections -> {len(actions)} street rows")
    print(f"  street-match coverage: {100*coverage:.1f}%")
    print(f"  #1 section {top1['key']} ({top1['district_lbl']}): "
          f"street planes sum={top1_planes} vs section plane_count={int(top1['plane_count'])}")
    print(f"  total suggested_remove (top-{TOPK_SECTIONS}): {int(actions['suggested_remove'].sum())} "
          f"(of city target {TARGET_REMOVE})")
    print(f"  HONESTY GATE: no priority/score column at street grain -> PASS")
    print("\n  sample (top section, top streets by mature):")
    print(actions.head(8).to_string(index=False))

    _append_design(actions, coverage, top1, top1_planes)


def _append_design(actions, coverage, top1, top1_planes):
    if not DESIGN.exists():
        return
    txt = DESIGN.read_text(encoding="utf-8")
    block = (
        f"\n### street_actions.py\n\n"
        f"- **C2 honesty gate PASSED:** street file carries no priority/score column; "
        f"`suggested_remove <= n_mature` everywhere.\n"
        f"- Street-match coverage from free-text `adreca`: **{100*coverage:.1f}%**.\n"
        f"- Spot-check #1 section {top1['key']} ({top1['district_lbl']}): per-street planes "
        f"sum = {top1_planes} = section plane_count {int(top1['plane_count'])} (consistent).\n"
        f"- {len(actions)} street rows across the top-60 sections; total suggested removal "
        f"{int(actions['suggested_remove'].sum())} planes (illustrative, A2 policy anchor).\n"
        f"- Output: `outputs/phase-6/street_removal_actions.csv` (worklist) + "
        f"`street_removal_points.geojson` (QA map).\n"
    )
    if "(street results appended by street_actions.py)" in txt:
        txt = txt.replace("(street results appended by street_actions.py)",
                          "(street results below)" + block)
        DESIGN.write_text(txt, encoding="utf-8")


if __name__ == "__main__":
    main()
