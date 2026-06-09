"""Phase 6 (Deployment) -- PRIORITY at census-section grain (~1,068 units).

Recomputes the allergen priority at the NATIVE grain of the demand signal (census
section), removing the 400 m areal-interpolation step entirely. Source is computed
directly from the street-tree inventory (mature Platanus count per section); exposure
is section population joined natively (no interpolation). Re-runs the pre-registered
tests T1-T4 (phase-6/section-street-design.md) at section grain, plus deployment
checks C1 (grain sanity + rollup agreement).

priority = minmax(source_raw) * minmax(exposure_pop),  source_raw = mature Platanus count.

Reuses minmax/topk/jaccard/burden_capture/random_capture from allergen_priority.
Deterministic (seed 42), ASCII-only console. Run:  python src/section_priority.py
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.stats import spearmanr

from allergen_priority import minmax, topk, jaccard, burden_capture, random_capture

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
TREES = ROOT / "data" / "arbrat-viari.csv"
POP = ROOT / "data" / "raw" / "2026_pad_mdbas.csv"
BND = ROOT / "data" / "raw" / "Unitats_Administratives_BCN_geojson" / "0301100100_UNITATS_ADM_POLIGONS.json"
CELLS = ROOT / "data" / "processed" / "allergen_layers.parquet"
OUTDIR = ROOT / "outputs" / "phase-6"
DESIGN = ROOT / "phase-6" / "section-street-design.md"
CRS = "EPSG:25831"

MATURE = {"EXEMPLAR", "PRIMERA"}            # A1 (primary assumption; T4-tested)
MATURE_BROAD = {"EXEMPLAR", "PRIMERA", "SEGONA"}

# Barcelona's 10 districts (code -> name); section key starts with the 2-digit code.
DISTRICTS = {
    "01": "Ciutat Vella", "02": "Eixample", "03": "Sants-Montjuic",
    "04": "Les Corts", "05": "Sarria-Sant Gervasi", "06": "Gracia",
    "07": "Horta-Guinardo", "08": "Nou Barris", "09": "Sant Andreu",
    "10": "Sant Marti",
}


def load_platanus():
    df = pd.read_csv(TREES, dtype=str, low_memory=False)
    plat = df[df["cat_nom_cientific"].str.startswith("Platanus", na=False)].copy()
    plat["x"] = pd.to_numeric(plat["x_etrs89"], errors="coerce")
    plat["y"] = pd.to_numeric(plat["y_etrs89"], errors="coerce")
    plat = plat.dropna(subset=["x", "y"])
    gdf = gpd.GeoDataFrame(
        plat, geometry=gpd.points_from_xy(plat["x"], plat["y"]), crs=CRS)
    return gdf


def load_sections():
    bnd = gpd.read_file(BND)
    bnd = bnd[bnd["TIPUS_UA"] == "SEC_CENS"].copy()
    bnd["key"] = (bnd["DISTRICTE"].astype(str).str.zfill(2)
                  + bnd["SEC_CENS"].astype(str).str.zfill(3))
    bnd = bnd.to_crs(CRS)
    # human-readable district label from the 2-digit district code (section spans one district)
    bnd["district_lbl"] = bnd["key"].str[:2].map(DISTRICTS).fillna(bnd["key"].str[:2])
    return bnd[["key", "district_lbl", "geometry"]]


def load_pop():
    pop = pd.read_csv(POP, dtype=str)
    pop["key"] = (pop["Codi_Districte"].str.zfill(2)
                  + pop["Seccio_Censal"].astype(str).str[-3:])
    pop["exposure_pop"] = pop["Valor"].astype(float)
    return pop[["key", "exposure_pop"]]


def reorder_verdict(pri, order):
    return bool(jaccard(topk(pri, 15), topk(order, 15)) < 0.70
                and spearmanr(pri, order).statistic < 0.90)


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    trees = load_platanus()
    sec = load_sections()
    pop = load_pop()

    # --- spatial join trees -> sections ---
    joined = gpd.sjoin(trees, sec[["key", "geometry"]], how="left", predicate="within")
    unmatched = int(joined["key"].isna().sum())
    joined = joined.dropna(subset=["key"])
    joined["is_mature"] = joined["categoria_arbrat"].isin(MATURE)
    joined["is_mature_broad"] = joined["categoria_arbrat"].isin(MATURE_BROAD)

    agg = joined.groupby("key").agg(
        plane_count=("codi", "size"),
        mature_count=("is_mature", "sum"),
        mature_broad=("is_mature_broad", "sum"),
    ).reset_index()

    # --- assemble section table (left join keeps ALL sections, incl. zero-plane) ---
    df = sec.merge(agg, on="key", how="left").merge(pop, on="key", how="left")
    for c in ("plane_count", "mature_count", "mature_broad"):
        df[c] = df[c].fillna(0).astype(int)
    pop_missing = int(df["exposure_pop"].isna().sum())
    df["exposure_pop"] = df["exposure_pop"].fillna(0.0)

    src = df["mature_count"].to_numpy(float)            # A1: source = mature plane count
    expo = df["exposure_pop"].to_numpy(float)
    df["source_std"] = minmax(src)
    df["exposure_std"] = minmax(expo)
    priority = df["source_std"].to_numpy() * df["exposure_std"].to_numpy()
    df["priority"] = priority
    df["priority_std"] = minmax(priority)
    total = priority.sum()

    res = {
        "grain": "census_section",
        "n_sections": int(len(df)),
        "sections_with_planes": int((df["plane_count"] > 0).sum()),
        "platanus_joined": int(joined.shape[0]),
        "platanus_unmatched_to_section": unmatched,
        "city_population_joined": round(float(df["exposure_pop"].sum()), 0),
        "sections_without_population": pop_missing,
        "mature_set_A1": sorted(MATURE),
        "source_definition": "source_raw = mature Platanus count per section (A1)",
    }

    # --- T1: does exposure re-order vs naive plane-density (source-only)? ---
    sp = spearmanr(priority, src).statistic
    j15 = jaccard(topk(priority, 15), topk(src, 15))
    j50 = jaccard(topk(priority, 50), topk(src, 50))
    t1 = bool(j15 < 0.70 and sp < 0.90)
    res["T1_reordering_vs_density"] = {
        "spearman_priority_vs_source": round(float(sp), 4),
        "jaccard_top15": round(j15, 4), "jaccard_top50": round(j50, 4),
        "exposure_materially_reorders": t1,
    }

    # --- T2: redundancy ---
    cps = float(np.corrcoef(priority, src)[0, 1])
    cpe = float(np.corrcoef(priority, expo)[0, 1])
    cse = float(np.corrcoef(src, expo)[0, 1])
    res["T2_redundancy"] = {
        "corr_priority_source": round(cps, 4), "corr_priority_exposure": round(cpe, 4),
        "corr_source_exposure": round(cse, 4),
        "both_layers_material": bool(abs(cps) >= 0.3 and abs(cpe) >= 0.3),
        "inputs_not_redundant": bool(abs(cse) < 0.8),
    }

    # --- T3: burden capture vs baselines ---
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

    # --- T4: sensitivity (T1 verdict must survive >=2 of 3 arms) ---
    src_broad = df["mature_broad"].to_numpy(float)
    pri_broad = minmax(src_broad) * df["exposure_std"].to_numpy()
    src_all = df["plane_count"].to_numpy(float)
    pri_unif = minmax(src_all) * df["exposure_std"].to_numpy()
    src_rank = pd.Series(src).rank().to_numpy()
    expo_rank = pd.Series(expo).rank().to_numpy()
    pri_rank = minmax(src_rank) * minmax(expo_rank)
    arms = {
        "broad_mature": reorder_verdict(pri_broad, minmax(src_broad)),
        "uniform_maturity": reorder_verdict(pri_unif, minmax(src_all)),
        "rank_normalized": reorder_verdict(pri_rank, minmax(src_rank)),
    }
    res["T4_sensitivity_reorder_holds"] = arms
    res["T4_holds_majority"] = bool(sum(arms.values()) >= 2)

    # --- C1: grain sanity + rollup agreement vs old 400 m cell product ---
    cells = gpd.read_parquet(CELLS)
    if cells.crs is None:
        cells = cells.set_crs(CRS)
    cells = cells.to_crs(CRS)
    cells["cell_priority"] = (cells["source_std"].to_numpy(float)
                              * cells["exposure_std"].to_numpy(float))
    inter = gpd.overlay(sec[["key", "geometry"]], cells[["cell_priority", "geometry"]],
                        how="intersection", keep_geom_type=True)
    inter["a"] = inter.geometry.area
    inter["w"] = inter["cell_priority"] * inter["a"]
    roll = inter.groupby("key").agg(w=("w", "sum"), a=("a", "sum")).reset_index()
    roll["cell_pri_rollup"] = roll["w"] / roll["a"]
    cmp = df[["key", "priority"]].merge(roll[["key", "cell_pri_rollup"]], on="key", how="inner")
    rollup_sp = float(spearmanr(cmp["priority"], cmp["cell_pri_rollup"]).statistic)
    res["C1_grain"] = {
        "n_sections_expected_~1068": int(len(df)),
        "rollup_spearman_vs_cell_product": round(rollup_sp, 4),
        "rollup_interpretation": ("high-but-<1: finer signal, consistent (not noise/contradiction)"
                                  if 0.5 <= rollup_sp < 1.0 else "REVIEW"),
        "n_sections_compared": int(len(cmp)),
    }

    res["VERDICT"] = (
        "section-grain product deployable: exposure re-orders + non-redundant at native grain"
        if t1 and res["T2_redundancy"]["both_layers_material"]
        else "section-grain exposure largely redundant (honest limitation)")

    # --- write artifacts ---
    keep = ["key", "district_lbl", "plane_count", "mature_count", "exposure_pop",
            "source_std", "exposure_std", "priority", "priority_std", "geometry"]
    out = df[keep].copy()
    out.to_parquet(OUTDIR / "section_priority.parquet", index=False)

    tbl = out.drop(columns="geometry").sort_values("priority", ascending=False).copy()
    tbl.insert(0, "rank", range(1, len(tbl) + 1))
    tbl.head(50).to_csv(OUTDIR / "section_priority.csv", index=False)

    (OUTDIR / "section_priority.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    _write_md(res)
    _append_design(res)
    print(json.dumps(res, indent=2))

    # hard assertions (C1)
    assert 900 <= len(df) <= 1100, f"section count {len(df)} off expected ~1068"
    assert abs(df["exposure_pop"].sum() - 1_730_000) < 80_000, "city pop far from 1.73M"
    print("\nC1 assertions PASSED")


def _write_md(res):
    t1, t2, t3, c1 = (res["T1_reordering_vs_density"], res["T2_redundancy"],
                      res["T3_burden_capture"], res["C1_grain"])
    md = f"""# Section-Grain Priority Results (Phase 6 -- Deployment)

Recomputed at **census-section grain** ({res['n_sections']} sections, native demand grain --
NO areal interpolation). Source = mature Platanus count per section (assumption A1:
mature = {res['mature_set_A1']}). {res['platanus_joined']} Platanus joined to sections
({res['platanus_unmatched_to_section']} unmatched).

**VERDICT: {res['VERDICT']}**

## C1 -- grain sanity + agreement with the 400 m cell product
- sections: {c1['n_sections_expected_~1068']} (expected ~1068); city pop joined:
  {res['city_population_joined']:,.0f} ({res['sections_without_population']} sections missing pop).
- Spearman(section priority, rolled-up cell priority) = **{c1['rollup_spearman_vs_cell_product']}**
  over {c1['n_sections_compared']} sections -> {c1['rollup_interpretation']}.

## T1 -- does exposure re-order vs naive plane-density?
Spearman(priority, source) = {t1['spearman_priority_vs_source']}; top-15 Jaccard =
{t1['jaccard_top15']}, top-50 Jaccard = {t1['jaccard_top50']}.
-> exposure materially re-orders: **{t1['exposure_materially_reorders']}** (criterion: J15<0.70 AND Spearman<0.90).

## T2 -- redundancy (two material layers, not one in a costume)
corr(priority,source) = {t2['corr_priority_source']}; corr(priority,exposure) = {t2['corr_priority_exposure']};
corr(source,exposure) = {t2['corr_source_exposure']}.
Both layers material: {t2['both_layers_material']}; inputs not redundant: {t2['inputs_not_redundant']}.

## T3 -- allergen-exposure burden captured by top-k (read the MARGIN)
| k | priority | density-only | random | margin (priority - density) |
|---|---|---|---|---|
| 15 | {t3[15]['priority']} | {t3[15]['density_only']} | {t3[15]['random_mean']} | {t3[15]['margin_priority_minus_density']} |
| 50 | {t3[50]['priority']} | {t3[50]['density_only']} | {t3[50]['random_mean']} | {t3[50]['margin_priority_minus_density']} |

## T4 -- sensitivity (T1 re-order verdict must hold in >=2 of 3 arms)
{json.dumps(res['T4_sensitivity_reorder_holds'], indent=2)}
-> holds in majority: **{res['T4_holds_majority']}**.

## Top priority sections
See `outputs/phase-6/section_priority.csv` (top 50: key, district, planes, mature, population, priority).
Street-level action lists for the top sections: `outputs/phase-6/street_removal_actions.csv`.
"""
    (OUTDIR / "section_priority.md").write_text(md, encoding="utf-8")


def _append_design(res):
    if not DESIGN.exists():
        return
    marker = "_(pending -- `src/section_priority.py` + `src/street_actions.py`)_"
    alt = "_(pending — `src/section_priority.py` + `src/street_actions.py`)_"
    txt = DESIGN.read_text(encoding="utf-8")
    t1 = res["T1_reordering_vs_density"]
    c1 = res["C1_grain"]
    block = (
        f"### section_priority.py (run {res['n_sections']} sections)\n\n"
        f"**VERDICT: {res['VERDICT']}.**\n\n"
        f"- **C1:** {res['n_sections']} sections; pop {res['city_population_joined']:,.0f}; "
        f"rollup Spearman vs cell product {c1['rollup_spearman_vs_cell_product']} "
        f"({c1['rollup_interpretation']}).\n"
        f"- **T1:** Spearman {t1['spearman_priority_vs_source']}, top-15 Jaccard "
        f"{t1['jaccard_top15']} -> re-orders = {t1['exposure_materially_reorders']}.\n"
        f"- **T2:** corr(source,exposure) {res['T2_redundancy']['corr_source_exposure']} -> "
        f"both material = {res['T2_redundancy']['both_layers_material']}.\n"
        f"- **T3:** top-15 burden margin over density-only "
        f"{res['T3_burden_capture'][15]['margin_priority_minus_density']}.\n"
        f"- **T4:** {res['T4_sensitivity_reorder_holds']} -> majority = {res['T4_holds_majority']}.\n\n"
        f"Full: `outputs/phase-6/section_priority.md`. (street results appended by street_actions.py)\n"
    )
    for m in (marker, alt):
        if m in txt:
            DESIGN.write_text(txt.replace(m, block), encoding="utf-8")
            return


if __name__ == "__main__":
    main()
