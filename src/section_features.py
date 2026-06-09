"""Cycle-B Phase-4 ML -- assemble the SECTION feature table (independent of plane counts).

Per census section (1,068): urban-form features area-weighted from the 400 m grid
(mean_sealed, mean_ndvi, mean_lst_celsius, income), geometry-derived (area, distance
to the city's metric centre, Polsby-Popper compactness), demographic (pop_density),
and the categorical district. Target (supervised model only) = mature-Platanus density.

NON-TAUTOLOGY CONTRACT (phase-6/modeling-ml-design.md sec 0): NO plane-derived column is
a feature. mature_count is used ONLY to build the target, never as a predictor.

Deterministic, ASCII-only. Run:  python src/section_features.py
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "outputs" / "phase-6" / "section_priority.parquet"
GRID = ROOT / "data" / "processed" / "scored_grid.parquet"
LAYERS = ROOT / "data" / "processed" / "allergen_layers.parquet"
OUT = ROOT / "data" / "processed" / "section_features.parquet"
CRS = "EPSG:25831"

# features the model may use (declared); target built separately from mature_count
FEATURES = ["mean_sealed", "mean_ndvi", "mean_lst_celsius", "income",
            "pop_density", "area_km2", "dist_to_centre_km", "compactness"]
FORBIDDEN = ("plane", "mature", "platanus", "source", "priority", "composite",
             "total_trees", "species_rich")  # leakage guard


def main():
    sec = gpd.read_parquet(SEC)
    if sec.crs is None:
        sec = sec.set_crs(CRS)
    sec = sec.to_crs(CRS)

    # cell urban-form features (+ income merged from allergen_layers by cell_id)
    grid = gpd.read_parquet(GRID)
    if grid.crs is None:
        grid = grid.set_crs(CRS)
    grid = grid.to_crs(CRS)[["cell_id", "mean_sealed", "mean_ndvi", "mean_lst_celsius", "geometry"]]
    lay = gpd.read_parquet(LAYERS)[["cell_id", "cell_income"]]
    grid = grid.merge(lay, on="cell_id", how="left").rename(columns={"cell_income": "income"})
    grid["cell_area"] = grid.geometry.area

    # area-weighted aggregation of cell features -> sections
    inter = gpd.overlay(sec[["key", "geometry"]], grid, how="intersection", keep_geom_type=True)
    inter["w"] = inter.geometry.area
    agg = {}
    for col in ["mean_sealed", "mean_ndvi", "mean_lst_celsius", "income"]:
        num = (inter[col] * inter["w"]).groupby(inter["key"]).sum()
        den = inter.loc[inter[col].notna(), "w"].groupby(inter["key"]).sum()
        agg[col] = (num / den)
    feat = pd.DataFrame(agg).reset_index()

    # geometry-derived + demographic, from the section itself
    sec = sec.copy()
    sec["area_km2"] = sec.geometry.area / 1e6
    cx, cy = sec.geometry.centroid.x, sec.geometry.centroid.y
    ctr_x, ctr_y = cx.mean(), cy.mean()                      # metric centre of the city
    sec["dist_to_centre_km"] = np.hypot(cx - ctr_x, cy - ctr_y) / 1000.0
    perim = sec.geometry.length
    sec["compactness"] = (4 * np.pi * sec.geometry.area / perim**2).clip(0, 1)
    sec["pop_density"] = sec["exposure_pop"] / sec["area_km2"].replace(0, np.nan)
    sec["mature_density"] = sec["mature_count"] / sec["area_km2"].replace(0, np.nan)  # TARGET

    df = sec[["key", "district_lbl", "area_km2", "dist_to_centre_km", "compactness",
              "pop_density", "mature_density", "mature_count", "priority", "geometry"]].merge(
        feat, on="key", how="left")

    # impute any feature gaps with median (declared), flag count
    nfill = 0
    for c in ["mean_sealed", "mean_ndvi", "mean_lst_celsius", "income", "pop_density", "compactness"]:
        m = df[c].isna().sum()
        if m:
            df[c] = df[c].fillna(df[c].median()); nfill += int(m)

    # leakage guard: no forbidden token among declared FEATURES
    bad = [f for f in FEATURES if any(t in f for t in FORBIDDEN)]
    assert not bad, f"LEAKAGE: forbidden feature(s) {bad}"

    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs=CRS)
    gdf.to_parquet(OUT, index=False)

    print("SECTION FEATURES built ->", OUT.name)
    print(f"  sections: {len(gdf)}   feature gaps imputed (median): {nfill}")
    print(f"  features (independent of plane counts): {FEATURES}")
    print(f"  target: mature_density (mature_count / area_km2)")
    print(gdf[["mean_sealed", "mean_ndvi", "mean_lst_celsius", "income",
               "pop_density", "dist_to_centre_km", "mature_density"]].describe().round(3).to_string())


if __name__ == "__main__":
    main()
