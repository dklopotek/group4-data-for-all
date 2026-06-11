"""Phase 6 (Deployment) -- section ENRICHMENT for the planner app's flagship augmentation.

Computes three NEW per-section layers from data already on disk (no new ingestion --
frozen-data rule; this is a presentation derivation over Phase-1..4 outputs):

  1. CROSS-GRAIN CORROBORATION  (the flagship "trust verdict")
     Re-rank sections by the 400 m people-weighted product (area-weighted rollup of
     cell source_std*exposure_std), compare to the section-grain priority rank, and
     stamp each section:
       CORROBORATED -- high at BOTH grains (act first)
       ARTIFACT     -- high at section grain only; 400 m people-weighting demotes it
                       (the Montjuic park trap -- big mature-plane cluster, few residents)
       UNDERRATED   -- low at section grain, high at 400 m (dense-residential, buried by
                       the "count the planes" ranking -- the upside of people-weighting)
       minor        -- not high at either grain
     HONESTY: this tests whether two aggregations of the SAME exposure proxy agree on
     WHERE to act. It does NOT validate the pollen proxy itself. It is a MAUP-robustness
     / internal-consistency check, not ground truth.

  2. MONOCULTURE / BIODIVERSITY co-benefit  (the city's ACTUAL removal driver)
     share = section Platanus count / section total street trees (ALL 286 species).
     The Pla Director removes planes for monoculture-risk, not allergy; high-share
     sections are where diversification matters most. co_benefit = priority_std *
     monoculture_std surfaces sections that serve the city mandate AND the health co-benefit.

  3. THERMAL do-no-harm guardrail  (don't cook the block)
     heat_risk = minmax(mean_lst_celsius) * (1 - minmax(mean_ndvi)); flag = top quartile.
     Removing canopy where it is already hot and bare worsens the urban heat island --
     flagged sections need immediate replacement, no gaps.

Writes outputs/phase-6/section_enrich.parquet (key + new columns) consumed by
scripts/build_app_data.py, plus section_enrich.json (summary + Montjuic verification).
Deterministic, ASCII-only console. Run:  python src/section_enrich.py
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.stats import spearmanr

from allergen_priority import minmax

ROOT = Path(__file__).resolve().parents[1]
TREES = ROOT / "data" / "arbrat-viari.csv"
BND = ROOT / "data" / "raw" / "Unitats_Administratives_BCN_geojson" / "0301100100_UNITATS_ADM_POLIGONS.json"
SECP = ROOT / "outputs" / "phase-6" / "section_priority.parquet"
CELLS = ROOT / "data" / "processed" / "allergen_layers.parquet"
FEAT = ROOT / "data" / "processed" / "section_features.parquet"
OUTDIR = ROOT / "outputs" / "phase-6"
CRS = "EPSG:25831"

HIGH_Q = 2.0 / 3.0          # "high" = top tercile in a grain (rank-percentile >= this)
HEAT_Q = 0.75               # thermal flag = top quartile heat-risk


def load_sections():
    bnd = gpd.read_file(BND)
    bnd = bnd[bnd["TIPUS_UA"] == "SEC_CENS"].copy()
    bnd["key"] = (bnd["DISTRICTE"].astype(str).str.zfill(2)
                  + bnd["SEC_CENS"].astype(str).str.zfill(3))
    return bnd.to_crs(CRS)[["key", "geometry"]]


def all_tree_counts(sec):
    """Per section: total street trees (all 286 species), Platanus share, AND Shannon
    species diversity. Shannon H = -sum(p_i ln p_i), normalised by ln(n_species) so a
    balanced mix -> 1, a monoculture -> 0 (method inspired by the CoolSpend project's
    rules_engine.species_diversity_score; computed here on THIS project's own inventory)."""
    df = pd.read_csv(TREES, dtype=str, low_memory=False)
    df["x"] = pd.to_numeric(df["x_etrs89"], errors="coerce")
    df["y"] = pd.to_numeric(df["y_etrs89"], errors="coerce")
    df = df.dropna(subset=["x", "y"])
    df["sp"] = df["cat_nom_cientific"].fillna("unknown")
    df["is_plat"] = df["sp"].str.startswith("Platanus", na=False)
    g = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["x"], df["y"]), crs=CRS)
    j = gpd.sjoin(g, sec, how="left", predicate="within").dropna(subset=["key"])

    agg = j.groupby("key").agg(total_trees=("is_plat", "size"),
                               plat_trees=("is_plat", "sum")).reset_index()
    agg["monoculture"] = np.where(agg["total_trees"] > 0,
                                  agg["plat_trees"] / agg["total_trees"], 0.0)

    # --- Shannon diversity per section (richer ecological signal) ---
    sc = j.groupby(["key", "sp"]).size().rename("c").reset_index()
    tot = sc.groupby("key")["c"].transform("sum")
    sc["p"] = sc["c"] / tot
    sc["plogp"] = -sc["p"] * np.log(sc["p"])
    H = sc.groupby("key")["plogp"].sum().rename("shannon")
    nsp = sc.groupby("key")["sp"].nunique().rename("n_species")
    div = pd.concat([H, nsp], axis=1).reset_index()
    div["shannon_norm"] = np.where(div["n_species"] > 1,
                                   div["shannon"] / np.log(div["n_species"].clip(lower=2)), 0.0)
    agg = agg.merge(div, on="key", how="left")
    for c in ("shannon", "shannon_norm"):
        agg[c] = agg[c].fillna(0.0)
    agg["n_species"] = agg["n_species"].fillna(0).astype(int)
    return agg[["key", "total_trees", "plat_trees", "monoculture",
                "n_species", "shannon", "shannon_norm"]]


def cell_rollup(sec, df):
    """Area-weighted rollup of the 400 m people-weighted product onto sections."""
    cells = gpd.read_parquet(CELLS)
    if cells.crs is None:
        cells = cells.set_crs(CRS)
    cells = cells.to_crs(CRS)
    cells["cpri"] = (cells["source_std"].to_numpy(float)
                     * cells["exposure_std"].to_numpy(float))
    inter = gpd.overlay(sec[["key", "geometry"]], cells[["cpri", "geometry"]],
                        how="intersection", keep_geom_type=True)
    inter["a"] = inter.geometry.area
    inter["w"] = inter["cpri"] * inter["a"]
    roll = inter.groupby("key").agg(w=("w", "sum"), a=("a", "sum")).reset_index()
    roll["pri_400m"] = np.where(roll["a"] > 0, roll["w"] / roll["a"], 0.0)
    return roll[["key", "pri_400m"]]


def pctile_rank(x):
    """Rank-percentile in [0,1]; 1 = highest value (ties -> average rank)."""
    s = pd.Series(np.asarray(x, float))
    return (s.rank(method="average") - 1) / (len(s) - 1) if len(s) > 1 else s * 0


def classify(sec_pct, p400_pct):
    sec_hi = sec_pct >= HIGH_Q
    p4_hi = p400_pct >= HIGH_Q
    out = np.full(len(sec_pct), "minor", dtype=object)
    out[sec_hi & p4_hi] = "CORROBORATED"
    out[sec_hi & ~p4_hi] = "ARTIFACT"
    out[~sec_hi & p4_hi] = "UNDERRATED"
    return out


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    sec_geom = load_sections()

    sp = gpd.read_parquet(SECP)
    if sp.crs is None:
        sp = sp.set_crs(CRS)
    sp["key"] = sp["key"].astype(str)

    # --- 1. corroboration: 400 m rollup rank vs section rank ---
    roll = cell_rollup(sec_geom, sp)
    df = sp.merge(roll, on="key", how="left")
    df["pri_400m"] = df["pri_400m"].fillna(0.0)
    df["sec_pct"] = pctile_rank(df["priority"].to_numpy(float))
    df["p400_pct"] = pctile_rank(df["pri_400m"].to_numpy(float))
    df["corrob"] = classify(df["sec_pct"].to_numpy(), df["p400_pct"].to_numpy())
    # rank_400m (1 = best by the 400 m people-weighted product)
    df["rank_400m"] = df["pri_400m"].rank(ascending=False, method="min").astype(int)
    grain_sp = float(spearmanr(df["priority"], df["pri_400m"]).statistic)

    # --- 2. monoculture / co-benefit ---
    trees = all_tree_counts(sec_geom)
    df = df.merge(trees, on="key", how="left")
    for c in ("total_trees", "plat_trees"):
        df[c] = df[c].fillna(0).astype(int)
    df["monoculture"] = df["monoculture"].fillna(0.0)
    df["mono_std"] = minmax(df["monoculture"].to_numpy(float))
    df["co_benefit"] = df["priority_std"].to_numpy(float) * df["mono_std"].to_numpy(float)

    # --- 3. thermal guardrail ---
    feat = gpd.read_parquet(FEAT)[["key", "mean_lst_celsius", "mean_ndvi"]].copy()
    feat["key"] = feat["key"].astype(str)
    df = df.merge(feat, on="key", how="left")
    lst = df["mean_lst_celsius"].to_numpy(float)
    ndvi = df["mean_ndvi"].to_numpy(float)
    df["heat_risk"] = minmax(np.nan_to_num(lst)) * (1.0 - minmax(np.nan_to_num(ndvi)))
    thr = float(np.nanquantile(df["heat_risk"], HEAT_Q))
    df["heat_flag"] = (df["heat_risk"] >= thr).astype(int)

    # --- write enrich parquet (no geometry; build_app_data merges on key) ---
    keep = ["key", "pri_400m", "rank_400m", "sec_pct", "p400_pct", "corrob",
            "total_trees", "plat_trees", "monoculture", "mono_std", "co_benefit",
            "n_species", "shannon", "shannon_norm",
            "mean_lst_celsius", "heat_risk", "heat_flag"]
    out = df[keep].copy()
    out.to_parquet(OUTDIR / "section_enrich.parquet", index=False)

    # --- summary + Montjuic verification (the flagship's correctness gate) ---
    counts = df["corrob"].value_counts().to_dict()
    top = df.sort_values("priority", ascending=False).iloc[0]
    montjuic = {
        "section_key": str(top["key"]),
        "section_rank_by_priority": 1,
        "rank_400m": int(top["rank_400m"]),
        "mature_planes": int(top.get("mature_count", 0)) if "mature_count" in df.columns else None,
        "residents": int(top.get("exposure_pop", 0)) if "exposure_pop" in df.columns else None,
        "corrob_class": str(top["corrob"]),
        "EXPECT": "ARTIFACT (high source, low people-weighting)",
    }
    # most UNDERRATED section (low at section grain, highest 400m percentile)
    und = df[df["corrob"] == "UNDERRATED"].sort_values("p400_pct", ascending=False)
    underrated_example = None
    if len(und):
        u = und.iloc[0]
        underrated_example = {"key": str(u["key"]), "section_pctile": round(float(u["sec_pct"]), 3),
                              "p400_pctile": round(float(u["p400_pct"]), 3)}

    res = {
        "grain_spearman_section_vs_400m": round(grain_sp, 4),
        "interpretation": ("the two grains disagree materially (MAUP) -- corroboration is "
                           "informative" if grain_sp < 0.8 else "grains largely agree"),
        "corrob_counts": {k: int(counts.get(k, 0)) for k in
                          ("CORROBORATED", "ARTIFACT", "UNDERRATED", "minor")},
        "montjuic_check": montjuic,
        "underrated_example": underrated_example,
        "monoculture": {
            "city_share_check": round(float(df["plat_trees"].sum() / max(df["total_trees"].sum(), 1)), 4),
            "sections_over_50pct_planes": int((df["monoculture"] > 0.5).sum()),
            "median_shannon_diversity": round(float(df["shannon"].median()), 3),
            "median_species_per_section": int(df["n_species"].median()),
            "note": "share = section Platanus / section total trees; Shannon H = -sum(p ln p) over "
                    "all 286 species (diversity context, method inspired by CoolSpend).",
        },
        "thermal": {
            "heat_flag_threshold_top_quartile": round(thr, 4),
            "n_flagged": int(df["heat_flag"].sum()),
            "note": "heat_risk = minmax(LST) * (1 - minmax(NDVI)); flagged = removal worsens heat island.",
        },
        "honesty": ("Corroboration compares two aggregations of the SAME unvalidated pollen "
                    "proxy. Agreement raises confidence in the spatial ALLOCATION; it does NOT "
                    "validate the proxy. Monoculture is real inventory; co_benefit is a ranking "
                    "lens, not a claim. Thermal is a guardrail, not a priority."),
    }
    (OUTDIR / "section_enrich.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(json.dumps(res, indent=2))

    # correctness gate: the #1 section MUST be an ARTIFACT, else the trust badge would lie
    assert montjuic["corrob_class"] == "ARTIFACT", (
        f"Top-priority section classified {montjuic['corrob_class']}, expected ARTIFACT -- "
        "corroboration logic is wrong, do NOT ship.")
    assert grain_sp < 0.9, f"grain spearman {grain_sp} too high -- corroboration adds little"
    print("\nGATE PASSED: top section = ARTIFACT; grains disagree (Spearman "
          f"{grain_sp}). Corroboration is informative and honest.")


if __name__ == "__main__":
    main()
