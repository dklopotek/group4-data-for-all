"""Build per-cell Platanus maturity from categoria_arbrat (Open Data BCN).

categoria_arbrat is an arborist-assigned size class, 99.98% complete in the
street-tree inventory -- far better coverage than planting dates (81% missing).

Size-class -> emission weight mapping (larger tree = more pollen surface area):
  PRIMERA  -> 0.25  (young / small)
  SEGONA   -> 0.50  (medium)
  TERCERA  -> 0.75  (large)
  EXEMPLAR -> 1.00  (notable specimen -- maximum)

Per-cell maturity = weighted mean across all Platanus trees in that cell.
Fallback: trees with missing/unknown categoria get weight 0.60 (midpoint).

Writes: data/processed/categoria_maturity.parquet
        columns: cell_id, cat_maturity, n_plat_with_cat, n_plat_total

Run:  python src/categoria_maturity.py
      (downloads arbrat-viari.csv on first run if not present, ~43 MB)
"""
from __future__ import annotations
import ssl
import urllib.request
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

ROOT = Path(__file__).resolve().parents[1]
VIARI_URL = (
    "https://opendata-ajuntament.barcelona.cat/data/dataset/"
    "27b3f8a7-e536-4eea-b025-ce094817b2bd/resource/"
    "23124fd5-521f-40f8-85b8-efb1e71c2ec8/download"
)
VIARI_CSV = ROOT / "data" / "arbrat-viari.csv"
GRID = ROOT / "data" / "processed" / "scored_grid.parquet"
OUT = ROOT / "data" / "processed" / "categoria_maturity.parquet"
CRS = "EPSG:25831"

WEIGHT = {"PRIMERA": 0.25, "SEGONA": 0.50, "TERCERA": 0.75, "EXEMPLAR": 1.00}
FALLBACK_WEIGHT = 0.60


def download_viari() -> None:
    print("  downloading arbrat-viari.csv (~43 MB) ...", end=" ", flush=True)
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(VIARI_URL, headers={"User-Agent": "MycorrhizalBcn/1.0"})
    with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
        data = resp.read()
    VIARI_CSV.write_bytes(data)
    print(f"done ({len(data) // 1_000_000} MB)")


def main() -> None:
    if not VIARI_CSV.exists():
        download_viari()
    else:
        print(f"  using cached {VIARI_CSV.name} ({VIARI_CSV.stat().st_size // 1_000_000} MB)")

    print("  loading tree inventory ...", end=" ", flush=True)
    inv = pd.read_csv(VIARI_CSV, encoding="utf-8", low_memory=False,
                      usecols=["cat_nom_cientific", "categoria_arbrat",
                                "x_etrs89", "y_etrs89"])
    print(f"{len(inv):,} rows")

    plat = inv[inv["cat_nom_cientific"].str.contains("Platanus", na=False)].copy()
    print(f"  Platanus trees: {len(plat):,}")
    print(f"  categoria_arbrat coverage: "
          f"{plat['categoria_arbrat'].notna().mean() * 100:.1f}%")
    print(f"  value counts:")
    for k, v in plat["categoria_arbrat"].value_counts().items():
        print(f"    {k:10s}  {v:,}  (weight={WEIGHT.get(k, FALLBACK_WEIGHT)})")

    plat["emission_weight"] = (
        plat["categoria_arbrat"].map(WEIGHT).fillna(FALLBACK_WEIGHT)
    )

    # build GeoDataFrame in EPSG:25831 (same CRS as grid)
    plat = plat.dropna(subset=["x_etrs89", "y_etrs89"])
    gdf = gpd.GeoDataFrame(
        plat,
        geometry=gpd.points_from_xy(plat["x_etrs89"], plat["y_etrs89"]),
        crs=CRS,
    )

    grid = gpd.read_parquet(GRID)[["cell_id", "geometry"]]
    if grid.crs is None:
        grid = grid.set_crs(CRS)
    else:
        grid = grid.to_crs(CRS)

    print("  spatial join trees -> grid cells ...", end=" ", flush=True)
    joined = gpd.sjoin(gdf, grid, how="inner", predicate="within")
    print(f"{len(joined):,} matched")

    agg = (
        joined.groupby("cell_id")
        .agg(
            cat_maturity=("emission_weight", "mean"),
            n_plat_with_cat=("categoria_arbrat", lambda s: s.notna().sum()),
            n_plat_total=("emission_weight", "count"),
        )
        .reset_index()
    )
    agg["cat_maturity"] = agg["cat_maturity"].round(4)

    agg.to_parquet(OUT, index=False)

    # summary
    print(f"\n  cells with Platanus: {len(agg)}")
    print(f"  cat_maturity: min={agg['cat_maturity'].min():.3f} "
          f"median={agg['cat_maturity'].median():.3f} "
          f"max={agg['cat_maturity'].max():.3f}")
    print(f"\n  -> {OUT.relative_to(ROOT)}")
    print("\n  Compare to old maturity proxy (1 - trees_young_pct/100):")
    print("  The old proxy relied on planting dates (81% missing).")
    print("  This proxy uses arborist size classes (99.98% complete).")


if __name__ == "__main__":
    main()
