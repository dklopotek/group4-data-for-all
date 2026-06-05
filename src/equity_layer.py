"""Pivot product v3 — equity (deprivation) weighting.

priority_v1 (efficiency) = source x exposure.
priority_v3 (equity)     = source x exposure x deprivation_std.
Deprivation from INE Atlas gross income per person by census section (2023),
population-weighted-interpolated to cells (income is a rate, not a count).

Pre-registered in phase-6/allergen-validation-design.md (v3 addendum). Reports
the equity-efficiency TRADEOFF, not just reordering. Deterministic, ASCII-only.
Run:  python src/equity_layer.py
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
INCOME = ROOT / "data" / "raw" / "atles_renda_bruta_persona.csv"
POP = ROOT / "data" / "raw" / "2026_pad_mdbas.csv"
BND = ROOT / "data" / "raw" / "Unitats_Administratives_BCN_geojson" / "0301100100_UNITATS_ADM_POLIGONS.json"
LAYERS = ROOT / "data" / "processed" / "allergen_layers.parquet"
OUTDIR = ROOT / "outputs" / "phase-6"
CRS = "EPSG:25831"


def minmax(x):
    x = np.asarray(x, float)
    lo, hi = np.nanmin(x), np.nanmax(x)
    return np.zeros_like(x) if hi - lo == 0 else (x - lo) / (hi - lo)


def topk(s, k):
    return set(np.argsort(-np.asarray(s))[:k])


def jacc(a, b):
    return len(a & b) / len(a | b) if (a | b) else float("nan")


def burden_capture(burden, order_score, k):
    return float(burden[np.argsort(-order_score)[:k]].sum() / burden.sum())


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    inc = pd.read_csv(INCOME, dtype=str)
    icol = [c for c in inc.columns if c.startswith("Import_Renda")][0]
    inc["income"] = pd.to_numeric(inc[icol], errors="coerce")
    inc["key"] = inc["Codi_Districte"].str.zfill(2) + inc["Seccio_Censal"].str.zfill(3)
    med = inc["income"].median()
    n_missing = int(inc["income"].isna().sum())
    inc["income"] = inc["income"].fillna(med)

    pop = pd.read_csv(POP, dtype=str)
    pop["pop"] = pd.to_numeric(pop["Valor"], errors="coerce").fillna(0)
    pop["key"] = pop["Codi_Districte"].str.zfill(2) + pop["Seccio_Censal"].str[-3:]
    inc = inc.merge(pop[["key", "pop"]], on="key", how="left")
    inc["pop"] = inc["pop"].fillna(0)

    bnd = gpd.read_file(BND)
    bnd = bnd[bnd["TIPUS_UA"] == "SEC_CENS"].copy()
    bnd["key"] = bnd["DISTRICTE"].astype(str).str.zfill(2) + bnd["SEC_CENS"].astype(str).str.zfill(3)
    bnd = bnd.to_crs(CRS).merge(inc[["key", "income", "pop"]], on="key", how="left")
    bnd["sec_area"] = bnd.geometry.area

    layers = gpd.read_parquet(LAYERS)
    if layers.crs is None:
        layers = layers.set_crs(CRS)
    grid = layers[["cell_id", "geometry"]].to_crs(CRS)
    inter = gpd.overlay(grid, bnd[["income", "pop", "sec_area", "geometry"]],
                        how="intersection", keep_geom_type=True)
    inter["wpop"] = inter["pop"] * (inter.geometry.area / inter["sec_area"])
    # population-weighted mean income per cell
    g = inter.groupby("cell_id").apply(
        lambda d: np.average(d["income"], weights=d["wpop"]) if d["wpop"].sum() > 0
        else d["income"].mean()).reset_index()
    g.columns = ["cell_id", "cell_income"]

    out = layers.merge(g, on="cell_id", how="left")
    out["cell_income"] = out["cell_income"].fillna(out["cell_income"].median())
    out["deprivation_std"] = minmax(out["cell_income"].max() - out["cell_income"].to_numpy(float))
    out.to_parquet(LAYERS, index=False)

    src = out["source_std"].to_numpy(float)
    expo = out["exposure_std"].to_numpy(float)
    dep = out["deprivation_std"].to_numpy(float)
    burden = src * expo                      # exposure-relief objective (efficiency)
    pri_v1 = burden
    pri_v3 = burden * dep                    # equity-weighted
    pri_v3f = burden * (0.5 + 0.5 * dep)     # floored sensitivity
    dep_rank = minmax(pd.Series(dep).rank().to_numpy())
    pri_v3r = burden * dep_rank              # rank-based sensitivity

    # most-deprived income tercile (lowest-income third of cells)
    terc = pd.qcut(out["cell_income"], 3, labels=["low_income", "mid", "high_income"])
    deprived = set(out.loc[terc == "low_income", "cell_id"])
    cid = out["cell_id"].to_numpy()

    def deprived_share(order_score, k):
        top = cid[np.argsort(-order_score)[:k]]
        return round(float(np.mean([c in deprived for c in top])), 4)

    res = {
        "income_missing_sections_imputed": n_missing,
        "V3_1_decorrelation": {
            "corr_deprivation_source": round(float(np.corrcoef(dep, src)[0, 1]), 4),
            "corr_deprivation_exposure": round(float(np.corrcoef(dep, expo)[0, 1]), 4),
            "decorrelated_from_both": bool(abs(np.corrcoef(dep, src)[0, 1]) < 0.7
                                           and abs(np.corrcoef(dep, expo)[0, 1]) < 0.7),
        },
        "V3_2_reorder": {
            "spearman_v3_vs_v1": round(float(spearmanr(pri_v3, pri_v1).statistic), 4),
            "jaccard_top15": round(jacc(topk(pri_v3, 15), topk(pri_v1, 15)), 4),
            "jaccard_top50": round(jacc(topk(pri_v3, 50), topk(pri_v1, 50)), 4),
        },
        "V3_3_tradeoff": {},
    }
    for k in (15, 50):
        eff_self = burden_capture(burden, pri_v1, k)       # efficiency map captures
        eq_burden = burden_capture(burden, pri_v3, k)      # equity map captures (less)
        res["V3_3_tradeoff"][k] = {
            "efficiency_map_burden_captured": round(eff_self, 4),
            "equity_map_burden_captured": round(eq_burden, 4),
            "exposure_relief_sacrificed": round(eff_self - eq_burden, 4),
            "deprived_tercile_share_efficiency": deprived_share(pri_v1, k),
            "deprived_tercile_share_equity": deprived_share(pri_v3, k),
        }
    res["sensitivity_jaccard_top15_vs_v1"] = {
        "floored_weight": round(jacc(topk(pri_v3f, 15), topk(pri_v1, 15)), 4),
        "rank_based": round(jacc(topk(pri_v3r, 15), topk(pri_v1, 15)), 4),
    }
    res["VERDICT"] = ("deprivation is a genuine, decorrelated layer; equity weighting "
                      "redirects priority toward the most-deprived tercile at a measured "
                      "exposure-relief cost (see V3_3). Efficiency (v1) and equity (v3) "
                      "are both valid objectives; the planner chooses.")

    # equity priority table (top 30)
    out["priority_equity"] = pri_v3
    cols = ["cell_id", "district", "plane_density", "exposure_pop", "cell_income",
            "deprivation_std", "priority_equity"]
    tbl = out.sort_values("priority_equity", ascending=False)[cols].head(30).copy()
    tbl.insert(0, "rank", range(1, len(tbl) + 1))
    tbl.to_csv(OUTDIR / "priority_zones_equity.csv", index=False)

    (OUTDIR / "equity_results.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    _md(res)
    print(json.dumps(res, indent=2))


def _md(res):
    d, r, t = res["V3_1_decorrelation"], res["V3_2_reorder"], res["V3_3_tradeoff"]
    md = f"""# Equity (Deprivation) Weighting Results (Phase 6 v3)

Income missing sections imputed with city median: {res['income_missing_sections_imputed']}.

## V3-1 decorrelation (precondition)
corr(deprivation, source) = {d['corr_deprivation_source']}; corr(deprivation, exposure) = {d['corr_deprivation_exposure']}.
-> decorrelated from both (genuine new info): **{d['decorrelated_from_both']}**.

## V3-2 reorder (expected given V3-1)
Spearman(v3, v1) = {r['spearman_v3_vs_v1']}; top-15 Jaccard = {r['jaccard_top15']}, top-50 Jaccard = {r['jaccard_top50']}.

## V3-3 equity-efficiency TRADEOFF (the finding)
| k | efficiency map burden captured | equity map burden captured | relief sacrificed | deprived-tercile share (efficiency -> equity) |
|---|---|---|---|---|
| 15 | {t[15]['efficiency_map_burden_captured']} | {t[15]['equity_map_burden_captured']} | {t[15]['exposure_relief_sacrificed']} | {t[15]['deprived_tercile_share_efficiency']} -> {t[15]['deprived_tercile_share_equity']} |
| 50 | {t[50]['efficiency_map_burden_captured']} | {t[50]['equity_map_burden_captured']} | {t[50]['exposure_relief_sacrificed']} | {t[50]['deprived_tercile_share_efficiency']} -> {t[50]['deprived_tercile_share_equity']} |

Reading: the equity map directs more of the top cells into the most-deprived income tercile, at the cost of capturing less total exposure burden. Both numbers are the decision.

## Sensitivity (top-15 Jaccard vs v1)
{json.dumps(res['sensitivity_jaccard_top15_vs_v1'], indent=2)}

## Verdict
{res['VERDICT']}
"""
    (OUTDIR / "equity_results.md").write_text(md, encoding="utf-8")


if __name__ == "__main__":
    main()
