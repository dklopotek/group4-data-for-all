"""Pivot product — Layer 2 (EXPOSURE): residential population per grid cell.

Areal-weighted interpolation of Barcelona census-section population
(Padro 2026, 1.73M residents) onto the analysis grid. Each cell receives a
share of each overlapping section's population proportional to the overlap area
(section pop is a count, not a density -> areal weighting is required; MAUP is
declared in the model card).

Joins into data/processed/allergen_layers.parquet. Deterministic, ASCII-only.
Run:  python src/exposure_layer.py
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]
POP = ROOT / "data" / "raw" / "2026_pad_mdbas.csv"
BND = ROOT / "data" / "raw" / "Unitats_Administratives_BCN_geojson" / "0301100100_UNITATS_ADM_POLIGONS.json"
LAYERS = ROOT / "data" / "processed" / "allergen_layers.parquet"
CRS = "EPSG:25831"


def minmax(x):
    lo, hi = np.nanmin(x), np.nanmax(x)
    return np.zeros_like(x) if hi - lo == 0 else (x - lo) / (hi - lo)


def main():
    # population by census section -> 5-digit key (district zfill2 + 3-digit section)
    pop = pd.read_csv(POP, dtype=str)
    sec = pop["Seccio_Censal"].str.slice(start=0)  # e.g. '1001','10141'
    dist = pop["Codi_Districte"].str.zfill(2)
    section3 = [s[len(d.lstrip("0") or "0"):] if False else s[-3:] for s, d in zip(pop["Seccio_Censal"], pop["Codi_Districte"])]
    pop["key"] = dist + pd.Series(section3, index=pop.index)
    pop["pop"] = pop["Valor"].astype(int)
    pop = pop[["key", "pop"]]

    # census-section polygons
    bnd = gpd.read_file(BND)
    bnd = bnd[bnd["TIPUS_UA"] == "SEC_CENS"].copy()
    bnd["key"] = bnd["DISTRICTE"].astype(str).str.zfill(2) + bnd["SEC_CENS"].astype(str).str.zfill(3)
    bnd = bnd.to_crs(CRS)
    sec_gdf = bnd[["key", "geometry"]].merge(pop, on="key", how="left")
    miss = int(sec_gdf["pop"].isna().sum())
    assert miss == 0, f"{miss} sections without population (join failed)"
    sec_gdf["sec_area"] = sec_gdf.geometry.area

    # grid cells
    layers = gpd.read_parquet(LAYERS)
    if layers.crs is None:
        layers = layers.set_crs(CRS)
    grid = layers[["cell_id", "geometry"]].to_crs(CRS)

    # areal-weighted allocation
    inter = gpd.overlay(grid, sec_gdf, how="intersection", keep_geom_type=True)
    inter["w"] = inter.geometry.area / inter["sec_area"]
    inter["pop_alloc"] = inter["pop"] * inter["w"]
    expo = inter.groupby("cell_id")["pop_alloc"].sum().reset_index()
    expo.columns = ["cell_id", "exposure_pop"]

    out = layers.merge(expo, on="cell_id", how="left")
    out["exposure_pop"] = out["exposure_pop"].fillna(0.0)
    out["exposure_std"] = minmax(out["exposure_pop"].to_numpy(float))
    out.to_parquet(LAYERS, index=False)

    total_alloc = out["exposure_pop"].sum()
    print("EXPOSURE layer built ->", LAYERS.name)
    print(f"  sections joined: {len(sec_gdf)}  city pop: {sec_gdf['pop'].sum()}")
    print(f"  allocated to grid: {total_alloc:,.0f} ({100*total_alloc/sec_gdf['pop'].sum():.1f}% of city)")
    print(f"  cells with residents: {int((out['exposure_pop']>0).sum())}/{len(out)}")
    print(f"  exposure_pop: median {out['exposure_pop'].median():,.0f} max {out['exposure_pop'].max():,.0f}")


if __name__ == "__main__":
    main()
