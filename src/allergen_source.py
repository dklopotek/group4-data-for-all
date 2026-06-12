"""Pivot product — Layer 1 (SOURCE) + Layer 3 (FEASIBILITY).

Builds the transparent per-cell plane-pollen SOURCE proxy and the FEASIBILITY
gate from the street-tree inventory only (no external data). Layer 2 (EXPOSURE,
population) and external pollen validation are added once external data lands.

SOURCE = n_platanus * maturity, where maturity = 1 - trees_young_pct/100
(older/larger planes emit more pollen). Reported raw and min-max standardized.
plane_density (n_platanus) is retained as the density-only baseline.

Deterministic, ASCII-only. Raw data not mutated.
Run:  python src/allergen_source.py
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]
GRID = ROOT / "data" / "processed" / "scored_grid.parquet"
CAT_MAT = ROOT / "data" / "processed" / "categoria_maturity.parquet"
OUT = ROOT / "data" / "processed" / "allergen_layers.parquet"


def minmax(x):
    lo, hi = np.nanmin(x), np.nanmax(x)
    return np.zeros_like(x) if hi - lo == 0 else (x - lo) / (hi - lo)


def main():
    g = gpd.read_parquet(GRID)
    df = g[["cell_id", "district", "n_platanus", "platanus_pct", "total_trees",
            "trees_young_pct", "mean_sealed", "geometry"]].copy()

    # Maturity: prefer categoria_arbrat weights (arborist size class, 100% coverage
    # on Platanus) over planting-date proxy (81% missing in the inventory).
    if CAT_MAT.exists():
        import pandas as pd
        cat = pd.read_parquet(CAT_MAT)[["cell_id", "cat_maturity"]]
        df = df.merge(cat, on="cell_id", how="left")
        # fall back to planting-date proxy for cells not in the categoria file
        young_fallback = df["trees_young_pct"].fillna(df["trees_young_pct"].median()) / 100.0
        df["maturity"] = df["cat_maturity"].fillna((1.0 - young_fallback).clip(0, 1))
        maturity_source = "categoria_arbrat (arborist size class)"
    else:
        young = df["trees_young_pct"].fillna(df["trees_young_pct"].median()) / 100.0
        df["maturity"] = (1.0 - young).clip(0, 1)
        maturity_source = "planting-date proxy (fallback -- run categoria_maturity.py)"
    df["plane_density"] = df["n_platanus"].fillna(0)
    df["source_raw"] = df["plane_density"] * df["maturity"]
    df["source_std"] = minmax(df["source_raw"].to_numpy(float))
    df["feasibility"] = (1.0 - df["mean_sealed"].fillna(df["mean_sealed"].median())).clip(0, 1)

    df.to_parquet(OUT, index=False)

    n_plane_cells = int((df["plane_density"] > 0).sum())
    print("SOURCE/FEASIBILITY layers built ->", OUT.name)
    print(f"  maturity source: {maturity_source}")
    print(f"  cells: {len(df)}  with planes: {n_plane_cells}")
    print(f"  total plane trees: {int(df['plane_density'].sum())}")
    print(f"  source_raw: min {df['source_raw'].min():.1f} "
          f"median {df['source_raw'].median():.1f} max {df['source_raw'].max():.1f}")
    print(f"  top-5 source cells (cell_id, planes, maturity, source_raw):")
    for _, r in df.nlargest(5, "source_raw").iterrows():
        print(f"    {r['cell_id']}  planes={int(r['plane_density'])}  "
              f"mat={r['maturity']:.2f}  src={r['source_raw']:.1f}  {r['district']}")


if __name__ == "__main__":
    main()
