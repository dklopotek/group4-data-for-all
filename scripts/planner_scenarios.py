"""Run the planner tool's logic across MANY options -> grounded scenario results.

Replays the budget-planner greedy fill under different objectives, skip-park settings, and
budgets, so a planner (or an evaluating agent) can compare real outcomes -- no invented numbers.

Objectives (section ordering):
  efficiency   = priority desc            (the tool default: source x exposure)
  equity       = priority x deprivation   (relief tilted to low-income sections)
  quick_wins   = mature_count desc        (fewest sections to hit the budget)
  density_naive= plane_count desc         (the city's implicit 'most planes first' rule = baseline)

For each (objective x skip_park x budget): sections used, streets, exposure burden captured,
deprived-tercile share, districts touched, top sections. Deterministic. ASCII-only.
Run:  python scripts/planner_scenarios.py
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]
SECP = ROOT / "outputs" / "phase-6" / "section_priority.parquet"
FEAT = ROOT / "data" / "processed" / "section_features.parquet"
TYPO = ROOT / "outputs" / "phase-6" / "section_typology.csv"
ACTIONS = ROOT / "outputs" / "phase-6" / "street_removal_actions.csv"
OUTJSON = ROOT / "outputs" / "phase-6" / "planner_scenarios.json"
OUTMD = ROOT / "outputs" / "phase-6" / "planner_scenarios.md"

BUDGETS = [100, 300, 500, 1000, 2000, 5000]


def minmax(x):
    x = np.asarray(x, float); lo, hi = np.nanmin(x), np.nanmax(x)
    return np.zeros_like(x) if hi - lo == 0 else (x - lo) / (hi - lo)


def load():
    g = gpd.read_parquet(SECP)[["key", "district_lbl", "plane_count", "mature_count",
                                "exposure_pop", "priority"]].copy()
    g["key"] = g["key"].astype(str)
    f = gpd.read_parquet(FEAT)[["key", "income"]].copy(); f["key"] = f["key"].astype(str)
    t = pd.read_csv(TYPO, dtype={"key": str})[["key", "action"]]
    g = g.merge(f, on="key", how="left").merge(t, on="key", how="left")
    g["depriv"] = minmax(-g["income"].to_numpy(float))           # poorest = 1
    g["inc_tercile"] = pd.qcut(g["income"], 3, labels=["low", "mid", "high"])
    # street counts per section (for feasibility reporting)
    sc = {}
    if ACTIONS.exists():
        a = pd.read_csv(ACTIONS, dtype={"section_key": str})
        sc = a.groupby("section_key").size().to_dict()
    g["n_streets_listed"] = g["key"].map(lambda k: int(sc.get(k, 0)))
    return g


def order(g, objective):
    if objective == "efficiency":
        s = g["priority"]
    elif objective == "equity":
        s = g["priority"] * g["depriv"]
    elif objective == "quick_wins":
        s = g["mature_count"].astype(float)
    elif objective == "density_naive":
        s = g["plane_count"].astype(float)
    return g.assign(_score=s).sort_values("_score", ascending=False)


def run_one(g, objective, skip_park, budget, total_priority):
    df = order(g, objective)
    if skip_park:
        df = df[df["action"] != "defer (park-like)"]
    cum = 0; picked = []
    for r in df.itertuples():
        if r.mature_count <= 0:
            continue
        picked.append(r); cum += r.mature_count
        if cum >= budget:
            break
    sel = pd.DataFrame([{"key": p.key, "district": p.district_lbl, "mature": p.mature_count,
                         "priority": p.priority, "inc_tercile": p.inc_tercile,
                         "n_streets": p.n_streets_listed} for p in picked])
    if sel.empty:
        return None
    burden = float(sel["priority"].sum() / total_priority)
    deprived_share = float((sel["inc_tercile"] == "low").mean())
    return {
        "objective": objective, "skip_park": skip_park, "budget": budget,
        "sections_used": int(len(sel)),
        "mature_removed": int(sel["mature"].sum()),
        "exposure_burden_captured_pct": round(100 * burden, 2),
        "deprived_tercile_share_pct": round(100 * deprived_share, 1),
        "districts_touched": int(sel["district"].nunique()),
        "streets_listed": int(sel["n_streets"].sum()),
        "top5": sel.head(5)[["district", "mature"]].to_dict("records"),
    }


def main():
    g = load()
    total_priority = float(g["priority"].sum())
    rows = []
    for obj in ("efficiency", "equity", "quick_wins", "density_naive"):
        for skip in (False, True):
            for b in BUDGETS:
                r = run_one(g, obj, skip, b, total_priority)
                if r:
                    rows.append(r)
    res = {"city_total_priority": round(total_priority, 4),
           "n_sections": int(len(g)), "scenarios": rows,
           "note": "exposure_burden_captured_pct = share of the city's total source*exposure "
                   "burden in the chosen sections; the headline 'relief' proxy. deprived share = "
                   "fraction of chosen sections in the bottom income tercile."}
    OUTJSON.write_text(json.dumps(res, indent=2), encoding="utf-8")
    _md(res); _print_highlights(res)


def _md(res):
    hdr = ("| objective | skip-park | budget | sections | mature | burden % | deprived % | districts |\n"
           "|---|---|---|---|---|---|---|---|\n")
    body = "\n".join(
        f"| {r['objective']} | {r['skip_park']} | {r['budget']} | {r['sections_used']} | "
        f"{r['mature_removed']} | {r['exposure_burden_captured_pct']} | "
        f"{r['deprived_tercile_share_pct']} | {r['districts_touched']} |"
        for r in res["scenarios"])
    OUTMD.write_text(f"# Planner Scenario Results ({res['n_sections']} sections)\n\n"
                     f"{res['note']}\n\n{hdr}{body}\n", encoding="utf-8")


def _print_highlights(res):
    print(f"SCENARIOS run: {len(res['scenarios'])}  ->  {OUTJSON.name}, {OUTMD.name}")
    print("\nKey comparison at budget=1000, skip-park=True:")
    for r in res["scenarios"]:
        if r["budget"] == 1000 and r["skip_park"]:
            print(f"  {r['objective']:14} sections={r['sections_used']:3}  "
                  f"burden={r['exposure_burden_captured_pct']:5}%  "
                  f"deprived={r['deprived_tercile_share_pct']:5}%  "
                  f"districts={r['districts_touched']}")


if __name__ == "__main__":
    main()
