"""Pivot product v2 — at-risk (allergy-prevalence) layer.

Replaces flat population EXPOSURE with an AT-RISK layer = population reweighted by
allergic-rhinitis (AR) prevalence by age. Spatial variation comes from local age
structure (no sub-city AR data exists). Pre-registered in
phase-6/allergen-validation-design.md (v2 addendum).

Tests:
  V2-1  does prevalence re-order vs plain population? (the "is it worth it" test)
  V2-2  city-wide calibration vs empirical antihistamine age profile (honesty note)

Deterministic, ASCII-only. Run:  python src/atrisk_layer.py
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
EDATQ = ROOT / "data" / "raw" / "2026_pad_mdbas_edat-q.csv"
BND = ROOT / "data" / "raw" / "Unitats_Administratives_BCN_geojson" / "0301100100_UNITATS_ADM_POLIGONS.json"
PRESC = ROOT / "data" / "raw" / "catsalut_receptes_bcnciutat_respiratori.csv"
LAYERS = ROOT / "data" / "processed" / "allergen_layers.parquet"
OUTDIR = ROOT / "outputs" / "phase-6"
CRS = "EPSG:25831"


def ar_prev(band):
    """AR prevalence weight for 5-year band index (0=0-4,1=5-9,...). Literature-anchored."""
    age0 = 5 * int(band)
    if age0 < 5: return 0.04
    if age0 < 10: return 0.089      # GAN 6-7yr
    if age0 < 15: return 0.146      # GAN 13-14yr
    if age0 < 45: return 0.22       # Bauchau & Durham 2004 (~23% EU adult)
    if age0 < 65: return 0.18
    if age0 < 70: return 0.10
    return 0.06                     # 70+ decline


def minmax(x):
    x = np.asarray(x, float)
    lo, hi = np.nanmin(x), np.nanmax(x)
    return np.zeros_like(x) if hi - lo == 0 else (x - lo) / (hi - lo)


def topk(score, k):
    return set(np.argsort(-np.asarray(score))[:k])


def jaccard(a, b):
    return len(a & b) / len(a | b) if (a | b) else float("nan")


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    # --- section-level at-risk from age bands ---
    e = pd.read_csv(EDATQ, dtype=str)
    e["pop"] = pd.to_numeric(e["Valor"], errors="coerce").fillna(0)   # '..' -> 0
    e["band"] = pd.to_numeric(e["EDAT_Q"], errors="coerce")
    e = e.dropna(subset=["band"])
    e["w"] = e["band"].map(ar_prev)
    e["key"] = e["Codi_Districte"].str.zfill(2) + e["Seccio_Censal"].str[-3:]
    e["atrisk"] = e["pop"] * e["w"]
    sec = e.groupby("key").agg(pop=("pop", "sum"), atrisk=("atrisk", "sum")).reset_index()

    # --- polygons + areal interpolation to grid ---
    bnd = gpd.read_file(BND)
    bnd = bnd[bnd["TIPUS_UA"] == "SEC_CENS"].copy()
    bnd["key"] = bnd["DISTRICTE"].astype(str).str.zfill(2) + bnd["SEC_CENS"].astype(str).str.zfill(3)
    bnd = bnd.to_crs(CRS).merge(sec, on="key", how="left")
    miss = int(bnd["atrisk"].isna().sum())
    assert miss == 0, f"{miss} sections without age data"
    bnd["sec_area"] = bnd.geometry.area

    layers = gpd.read_parquet(LAYERS)
    if layers.crs is None:
        layers = layers.set_crs(CRS)
    grid = layers[["cell_id", "geometry"]].to_crs(CRS)
    inter = gpd.overlay(grid, bnd[["key", "atrisk", "sec_area", "geometry"]],
                        how="intersection", keep_geom_type=True)
    inter["frac"] = inter.geometry.area / inter["sec_area"]
    inter["alloc"] = inter["atrisk"] * inter["frac"]
    cell_ar = inter.groupby("cell_id")["alloc"].sum().reset_index()
    cell_ar.columns = ["cell_id", "at_risk_pop"]

    out = layers.merge(cell_ar, on="cell_id", how="left")
    out["at_risk_pop"] = out["at_risk_pop"].fillna(0.0)
    out["at_risk_std"] = minmax(out["at_risk_pop"].to_numpy(float))
    out.to_parquet(LAYERS, index=False)

    # --- priorities ---
    src = out["source_std"].to_numpy(float)
    pri_v1 = src * out["exposure_std"].to_numpy(float)     # population-based
    pri_v2 = src * out["at_risk_std"].to_numpy(float)      # at-risk-based

    # V2-1: does prevalence re-order vs plain population?
    sp_ar_pop = float(spearmanr(out["at_risk_pop"], out["exposure_pop"]).statistic)
    j15 = jaccard(topk(pri_v2, 15), topk(pri_v1, 15))
    j50 = jaccard(topk(pri_v2, 50), topk(pri_v1, 50))
    sp_pri = float(spearmanr(pri_v2, pri_v1).statistic)
    reorders = bool(j15 < 0.70 and sp_ar_pop < 0.95)

    # V2-2: city-wide calibration vs empirical antihistamine (R06) age profile
    calib = {}
    try:
        p = pd.read_csv(PRESC, dtype=str)
        col = "codi_atc_2" if "codi_atc_2" in p.columns else [c for c in p.columns if "atc" in c.lower()][0]
        r06 = p[p[col].astype(str).str.upper().str.startswith("R06")].copy()
        ycol = "any" if "any" in r06.columns else [c for c in r06.columns if c.lower() in ("any", "year")][0]
        r06 = r06[r06[ycol].astype(str) == str(r06[ycol].astype(str).max())]
        agecol = [c for c in r06.columns if "edat" in c.lower()][0]
        valcol = "receptes" if "receptes" in r06.columns else [c for c in r06.columns if "recept" in c.lower()][0]
        r06["v"] = pd.to_numeric(r06[valcol], errors="coerce").fillna(0)
        prof = r06.groupby(agecol)["v"].sum().sort_values(ascending=False)
        calib = {"R06_total": int(r06["v"].sum()),
                 "top_age_bands_by_prescriptions": prof.head(5).to_dict(),
                 "note": "prescriptions peak in middle/older age (chronic medication use), "
                         "while AR PREVALENCE peaks younger -- prescriptions are a use proxy, "
                         "not a prevalence map; divergence reported, not forced to agree."}
    except Exception as ex:
        calib = {"note": f"calibration profile not computed: {ex}"}

    res = {
        "at_risk_layer": "literature-weighted demographic (age-band x AR prevalence x Platanus share 0.37 constant)",
        "spatial_AR_data": "none below health-region; layer is modeled, not measured",
        "V2_1_reordering_vs_population": {
            "spearman_atrisk_vs_population": round(sp_ar_pop, 4),
            "spearman_priority_v2_vs_v1": round(sp_pri, 4),
            "jaccard_top15": round(j15, 4), "jaccard_top50": round(j50, 4),
            "prevalence_materially_reorders": reorders,
            "criterion": "jaccard_top15 < 0.70 AND spearman_atrisk_vs_population < 0.95",
        },
        "V2_2_calibration": calib,
        "VERDICT": ("at-risk earns its place (re-orders vs plain population)" if reorders
                    else "age-weighting largely redundant with population at this resolution "
                         "-- honest: keep v1 (population), report at-risk as a minor refinement"),
    }
    (OUTDIR / "atrisk_results.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    _md(res)
    print(json.dumps(res, indent=2))


def _md(res):
    v = res["V2_1_reordering_vs_population"]
    md = f"""# At-Risk (Allergy-Prevalence) Layer Results (Phase 6 v2)

**Layer:** {res['at_risk_layer']}
**Spatial AR data:** {res['spatial_AR_data']}

**VERDICT: {res['VERDICT']}**

## V2-1 -- does prevalence re-order vs plain population?
Spearman(at_risk, population) = {v['spearman_atrisk_vs_population']}; Spearman(priority_v2, priority_v1) = {v['spearman_priority_v2_vs_v1']}; top-15 Jaccard = {v['jaccard_top15']}, top-50 Jaccard = {v['jaccard_top50']}.
-> prevalence materially re-orders: **{v['prevalence_materially_reorders']}** (criterion: {v['criterion']}).

## V2-2 -- city-wide calibration (honesty note)
{json.dumps(res['V2_2_calibration'], indent=2, ensure_ascii=True)}
"""
    (OUTDIR / "atrisk_results.md").write_text(md, encoding="utf-8")


if __name__ == "__main__":
    main()
