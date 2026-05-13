"""
process_urban_atlas.py
======================
Converts the Urban Atlas 2018 LCU vector file into a per-400m-cell
sealed-surface fraction, saved as data/urban-atlas/sealed_per_cell.csv.

Run AFTER notebooks/02-grid-trees.ipynb has produced data/grid_trees.geojson:
    python data/process_urban_atlas.py

Output: data/urban-atlas/sealed_per_cell.csv
Columns: cell_id, sealed_pct (0.0–1.0)

The scoring notebook (03-scoring.ipynb) reads this CSV automatically.
"""

from pathlib import Path
import geopandas as gpd
import pandas as pd
import numpy as np

DATA_DIR   = Path(__file__).parent
UA_DIR     = DATA_DIR / "urban-atlas"
GRID_PATH  = DATA_DIR / "grid_trees.geojson"
OUT_PATH   = UA_DIR / "sealed_per_cell.csv"

# ── Sealed-surface fraction by Urban Atlas LCU class ─────────────────────
# Source: Copernicus Urban Atlas Technical Specifications + literature
# (Hermosilla et al. 2021; Kabisch et al. 2016; class definitions)
SEALED_FRACTION = {
    11100: 0.90,   # Continuous Urban Fabric (>80%)
    11210: 0.65,   # Discontinuous dense (50–80%)
    11220: 0.40,   # Discontinuous medium (30–50%)
    11230: 0.20,   # Discontinuous low density (10–30%)
    11240: 0.05,   # Discontinuous very low (<10%)
    11300: 0.50,   # Isolated structures
    12100: 0.80,   # Industrial / commercial / public
    12210: 0.92,   # Fast transit roads
    12220: 0.85,   # Other roads
    12230: 0.50,   # Railways
    12300: 0.85,   # Port areas
    13100: 0.50,   # Mineral extraction / dump
    13300: 0.40,   # Construction sites
    13400: 0.15,   # Land without current use
    14100: 0.05,   # Green urban areas
    14200: 0.30,   # Sports and leisure
    21000: 0.02,   # Arable land
    22000: 0.02,   # Permanent crops
    23000: 0.02,   # Pastures
    31000: 0.01,   # Forests
    32000: 0.01,   # Herbaceous vegetation
    33000: 0.01,   # Open spaces (beaches, bare rock)
    40000: 0.01,   # Wetlands
    50000: 0.00,   # Water
}


def main():
    # ── Load grid ─────────────────────────────────────────────────────────
    if not GRID_PATH.exists():
        print("ERROR: data/grid_trees.geojson not found.")
        print("Run notebook 02-grid-trees.ipynb first.")
        return

    print("Loading grid cells …")
    grid = gpd.read_file(GRID_PATH)
    print(f"  {len(grid):,} cells  CRS: {grid.crs}")

    # ── Load Urban Atlas ──────────────────────────────────────────────────
    fgb_files = list(UA_DIR.glob("*.fgb"))
    if not fgb_files:
        print("ERROR: No .fgb file found in data/urban-atlas/")
        return
    fgb = fgb_files[0]
    print(f"Loading Urban Atlas: {fgb.name} …")
    ua = gpd.read_file(fgb)
    print(f"  {len(ua):,} polygons  CRS: {ua.crs}")

    # ── Reproject both to UTM31N for area calculations ────────────────────
    TARGET_CRS = "EPSG:25831"
    if str(grid.crs) != TARGET_CRS:
        grid = grid.to_crs(TARGET_CRS)
    ua = ua.to_crs(TARGET_CRS)

    # Add sealed fraction column — convert code to int first (FGB stores as string)
    ua["_code_int"] = pd.to_numeric(ua["code_2018"], errors="coerce").fillna(0).astype(int)
    ua["sealed_frac"] = ua["_code_int"].map(SEALED_FRACTION).fillna(0.30)
    matched = ua["sealed_frac"].ne(0.30).sum()
    print(f"  LCU codes matched: {matched:,} / {len(ua):,} polygons")

    # ── Compute area-weighted sealed fraction per grid cell ───────────────
    print("Intersecting grid with Urban Atlas polygons …")
    print("  (this takes 1–3 minutes for ~200k polygons)")

    # Clip UA to grid extent first (speeds up intersection)
    grid_union = grid.geometry.unary_union
    ua_clip = ua[ua.geometry.intersects(grid_union)].copy()
    print(f"  UA polygons within grid extent: {len(ua_clip):,}")

    # Overlay: split UA polygons by grid cells
    overlay = gpd.overlay(grid[["cell_id", "geometry"]], ua_clip[["sealed_frac", "geometry"]],
                          how="intersection", keep_geom_type=False)
    overlay["area_m2"] = overlay.geometry.area

    # Area-weighted mean sealed fraction per cell
    grouped = overlay.groupby("cell_id").apply(
        lambda df: np.average(df["sealed_frac"], weights=df["area_m2"])
    ).reset_index()
    grouped.columns = ["cell_id", "sealed_pct"]

    # Cells with no Urban Atlas coverage get a reasonable default (urban context)
    all_ids = pd.DataFrame({"cell_id": grid["cell_id"]})
    result = all_ids.merge(grouped, on="cell_id", how="left")
    result["sealed_pct"] = result["sealed_pct"].fillna(0.50)
    result["sealed_pct"] = result["sealed_pct"].clip(0.0, 1.0)

    OUT_PATH.parent.mkdir(exist_ok=True)
    result.to_csv(OUT_PATH, index=False)

    print(f"\n✓ Saved: {OUT_PATH}")
    print(f"  Cells processed: {len(result):,}")
    print(f"  Sealed fraction: mean={result['sealed_pct'].mean():.2f}  "
          f"min={result['sealed_pct'].min():.2f}  max={result['sealed_pct'].max():.2f}")

    # ── Also write a raster TIF so notebook 03 finds sealed_surface.tif ──────
    # Join sealed_pct back onto grid geometry and rasterize to 400m pixels
    print("\nRasterising to sealed_surface.tif …")
    try:
        import rasterio
        from rasterio.transform import from_bounds
        from rasterio.features import rasterize as rio_rasterize

        grid_result = grid.merge(result, on="cell_id", how="left")
        grid_result["sealed_pct"] = grid_result["sealed_pct"].fillna(0.5).astype("float32")

        bounds = grid_result.total_bounds          # minx, miny, maxx, maxy in UTM31N
        cell_size = 400
        width  = max(1, int(round((bounds[2] - bounds[0]) / cell_size)))
        height = max(1, int(round((bounds[3] - bounds[1]) / cell_size)))
        transform = from_bounds(bounds[0], bounds[1], bounds[2], bounds[3], width, height)

        shapes = (
            (geom, val)
            for geom, val in zip(grid_result.geometry, grid_result["sealed_pct"])
            if geom is not None
        )
        raster = rio_rasterize(shapes, out_shape=(height, width),
                               transform=transform, fill=0.5, dtype="float32")

        tif_path = UA_DIR / "sealed_surface.tif"
        with rasterio.open(
            tif_path, "w", driver="GTiff", height=height, width=width,
            count=1, dtype="float32", crs="EPSG:25831",
            transform=transform, nodata=-9999,
        ) as dst:
            dst.write(raster, 1)
        print(f"✓ Saved: {tif_path}  ({tif_path.stat().st_size // 1024} KB)")
    except Exception as e:
        print(f"  Warning: rasterisation failed ({e}) — notebook will use the CSV fallback.")

    print(f"\nThe scoring notebook (03-scoring.ipynb) will now use real Urban Atlas data.")


if __name__ == "__main__":
    main()
