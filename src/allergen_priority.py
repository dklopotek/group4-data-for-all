"""Pivot product — PRIORITY + pre-registered evaluation (phase-6/allergen-validation-design.md).

priority = source_std * exposure_std (two transparent layers, feasibility annotated).
Runs T1 (does exposure re-order vs naive density), T2 (redundancy), T3 (burden
capture vs density-only/random), T4 (sensitivity). Writes results + a
planner-readable priority table. Deterministic (seed 42), ASCII-only.

Run:  python src/allergen_priority.py
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.stats import spearmanr

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
LAYERS = ROOT / "data" / "processed" / "allergen_layers.parquet"
OUTDIR = ROOT / "outputs" / "phase-6"
DESIGN = ROOT / "phase-6" / "allergen-validation-design.md"


def minmax(x):
    x = np.asarray(x, float)
    lo, hi = np.nanmin(x), np.nanmax(x)
    return np.zeros_like(x) if hi - lo == 0 else (x - lo) / (hi - lo)


def topk(score, k):
    return set(np.argsort(-score)[:k])


def jaccard(a, b):
    return len(a & b) / len(a | b) if (a | b) else float("nan")


def burden_capture(priority, order_score, k, total):
    idx = np.argsort(-order_score)[:k]
    return float(priority[idx].sum() / total)


def random_capture(priority, k, total, draws=200):
    rng = np.random.default_rng(SEED)
    n = len(priority)
    vals = [priority[rng.choice(n, k, replace=False)].sum() / total for _ in range(draws)]
    return float(np.mean(vals))


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    g = gpd.read_parquet(LAYERS)
    src = g["source_std"].to_numpy(float)
    expo = g["exposure_std"].to_numpy(float)
    priority = src * expo
    g["priority"] = priority
    g["priority_std"] = minmax(priority)
    total = priority.sum()

    res = {"pollen_validation": "INFEASIBLE - source is literature-anchored proxy, "
                                "not measured-pollen-validated (see design Sec 0)"}

    # T1 -- does exposure re-order vs naive density (source-only)?
    sp = spearmanr(priority, src).statistic
    j15 = jaccard(topk(priority, 15), topk(src, 15))
    j50 = jaccard(topk(priority, 50), topk(src, 50))
    t1_reorder = bool(j15 < 0.70 and sp < 0.90)
    res["T1_reordering_vs_density"] = {
        "spearman_priority_vs_source": round(float(sp), 4),
        "jaccard_top15": round(j15, 4), "jaccard_top50": round(j50, 4),
        "exposure_materially_reorders": t1_reorder,
    }

    # T2 -- redundancy
    cps = float(np.corrcoef(priority, src)[0, 1])
    cpe = float(np.corrcoef(priority, expo)[0, 1])
    cse = float(np.corrcoef(src, expo)[0, 1])
    res["T2_redundancy"] = {
        "corr_priority_source": round(cps, 4), "corr_priority_exposure": round(cpe, 4),
        "corr_source_exposure": round(cse, 4),
        "both_layers_material": bool(abs(cps) >= 0.3 and abs(cpe) >= 0.3),
        "inputs_not_redundant": bool(abs(cse) < 0.8),
    }

    # T3 -- burden capture vs baselines
    cap = {}
    for k in (15, 50):
        cap[k] = {
            "priority": round(burden_capture(priority, priority, k, total), 4),
            "density_only": round(burden_capture(priority, src, k, total), 4),
            "random_mean": round(random_capture(priority, k, total), 4),
        }
        cap[k]["margin_priority_minus_density"] = round(
            cap[k]["priority"] - cap[k]["density_only"], 4)
    res["T3_burden_capture"] = cap

    # T4 -- sensitivity (T1 verdict must survive)
    def reorder_verdict(pri, order):
        return bool(jaccard(topk(pri, 15), topk(order, 15)) < 0.70
                    and spearmanr(pri, order).statistic < 0.90)
    dens = minmax(g["plane_density"].to_numpy(float))
    pri_a = dens * expo                                    # uniform maturity
    src_rank = pd.Series(src).rank().to_numpy()
    expo_rank = pd.Series(expo).rank().to_numpy()
    pri_b = minmax(src_rank) * minmax(expo_rank)           # rank-normalized
    pri_c = np.minimum(src, expo)                          # conjunctive (min)
    res["T4_sensitivity_reorder_holds"] = {
        "uniform_maturity": reorder_verdict(pri_a, dens),
        "rank_normalized": reorder_verdict(pri_b, minmax(src_rank)),
        "min_aggregation": reorder_verdict(pri_c, src),
    }

    res["VERDICT"] = ("exposure earns its place (materially re-orders + non-redundant)"
                      if t1_reorder and res["T2_redundancy"]["both_layers_material"]
                      else "exposure largely redundant with density (honest limitation)")

    # planner-readable priority table (top 30)
    cols = ["cell_id", "district", "plane_density", "maturity", "exposure_pop",
            "source_std", "exposure_std", "priority", "feasibility"]
    tbl = g.sort_values("priority", ascending=False)[cols].head(30).copy()
    tbl.insert(0, "rank", range(1, len(tbl) + 1))
    tbl.to_csv(OUTDIR / "priority_zones.csv", index=False)

    (OUTDIR / "allergen_priority_results.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    _write_md(res, g)
    _append_design(res)
    print(json.dumps(res, indent=2))


def _write_md(res, g):
    t1, t2, t3 = res["T1_reordering_vs_density"], res["T2_redundancy"], res["T3_burden_capture"]
    md = f"""# Allergen-Priority Results (Phase 6)

**Pollen validation:** {res['pollen_validation']}

**VERDICT: {res['VERDICT']}**

## T1 - does exposure re-order vs naive plane-density?
Spearman(priority, source) = {t1['spearman_priority_vs_source']}; top-15 Jaccard = {t1['jaccard_top15']}, top-50 Jaccard = {t1['jaccard_top50']}.
-> exposure materially re-orders: **{t1['exposure_materially_reorders']}** (criterion: J15<0.70 AND Spearman<0.90).

## T2 - redundancy (not one layer in a costume)
corr(priority, source) = {t2['corr_priority_source']}; corr(priority, exposure) = {t2['corr_priority_exposure']}; corr(source, exposure) = {t2['corr_source_exposure']}.
Both layers material: {t2['both_layers_material']}; inputs not redundant: {t2['inputs_not_redundant']}.

## T3 - allergen-exposure burden captured by top-k (priority's own objective; read the MARGIN)
| k | priority | density-only | random | margin (priority - density) |
|---|---|---|---|---|
| 15 | {t3[15]['priority']} | {t3[15]['density_only']} | {t3[15]['random_mean']} | {t3[15]['margin_priority_minus_density']} |
| 50 | {t3[50]['priority']} | {t3[50]['density_only']} | {t3[50]['random_mean']} | {t3[50]['margin_priority_minus_density']} |

## T4 - sensitivity (T1 re-order verdict must hold)
{json.dumps(res['T4_sensitivity_reorder_holds'], indent=2)}

## Top priority cells
See `outputs/phase-6/priority_zones.csv` (top 30: cell, district, planes, population, priority, feasibility).
"""
    (OUTDIR / "allergen_priority_results.md").write_text(md, encoding="utf-8")


def _append_design(res):
    if not DESIGN.exists():
        return
    marker = "_(pending - `src/allergen_priority.py`)_"
    txt = DESIGN.read_text(encoding="utf-8").replace(
        "_(pending — `src/allergen_priority.py`)_", marker)
    t1 = res["T1_reordering_vs_density"]
    block = (f"**VERDICT: {res['VERDICT']}.** T1: Spearman {t1['spearman_priority_vs_source']}, "
             f"top-15 Jaccard {t1['jaccard_top15']} -> re-orders={t1['exposure_materially_reorders']}. "
             f"T3 burden margin over density-only (top-15): "
             f"{res['T3_burden_capture'][15]['margin_priority_minus_density']}. "
             f"Full: `outputs/phase-6/allergen_priority_results.md`.")
    if marker in txt:
        DESIGN.write_text(txt.replace(marker, block), encoding="utf-8")


if __name__ == "__main__":
    main()
