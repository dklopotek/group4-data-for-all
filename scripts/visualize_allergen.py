"""Visualize the Platanus allergen-priority layers as interactive browser maps.

Loads data/processed/allergen_layers.parquet, recomputes priority v1 (efficiency)
and v3 (equity), prints a top-cells summary to the console, and writes
self-contained interactive HTML maps you open in any browser (no Jupyter kernel).

Run:  python scripts/visualize_allergen.py
Then open the printed .html paths.
ASCII-only console (Windows cp1252 safe). Deterministic.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]
LAYERS = ROOT / "data" / "processed" / "allergen_layers.parquet"
OUTDIR = ROOT / "outputs" / "phase-6" / "maps"


def minmax(x):
    x = np.asarray(x, float)
    lo, hi = np.nanmin(x), np.nanmax(x)
    return np.zeros_like(x) if hi - lo == 0 else (x - lo) / (hi - lo)


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    g = gpd.read_parquet(LAYERS)
    if g.crs is None:
        g = g.set_crs("EPSG:25831")

    # recompute the two priorities (same formulas as the pipeline)
    g["priority_v1"] = minmax(g["source_std"].to_numpy(float)
                              * g["exposure_std"].to_numpy(float))
    if "deprivation_std" in g.columns:
        g["priority_v3"] = minmax(g["source_std"].to_numpy(float)
                                  * g["exposure_std"].to_numpy(float)
                                  * g["deprivation_std"].to_numpy(float))
    else:
        g["priority_v3"] = np.nan

    # round display columns
    show = ["cell_id", "district", "plane_density", "exposure_pop",
            "source_std", "exposure_std", "feasibility",
            "deprivation_std", "priority_v1", "priority_v3"]
    show = [c for c in show if c in g.columns]
    for c in ("source_std", "exposure_std", "feasibility", "deprivation_std",
              "priority_v1", "priority_v3"):
        if c in g.columns:
            g[c] = g[c].round(3)
    if "exposure_pop" in g.columns:
        g["exposure_pop"] = g["exposure_pop"].round(0)

    # console summary -- the quick check
    print("=" * 64)
    print("ALLERGEN PRIORITY -- top 15 cells by v1 (efficiency)")
    print("=" * 64)
    top = g.sort_values("priority_v1", ascending=False).head(15)
    print(top[["cell_id", "district", "plane_density", "exposure_pop",
               "priority_v1", "priority_v3"]].to_string(index=False))
    print(f"\ncells: {len(g)}   total planes: {int(g['plane_density'].sum())}")
    print(f"priority_v1 range: {g['priority_v1'].min():.3f} .. {g['priority_v1'].max():.3f}")

    # interactive maps -- one HTML per objective + a combined toggle map
    def write_map(col, fname, cmap):
        m = g.explore(column=col, cmap=cmap, scheme="quantiles", k=6,
                      legend=True, tooltip=show, name=col,
                      style_kwds={"weight": 0.3, "fillOpacity": 0.7},
                      tiles="CartoDB positron")
        out = OUTDIR / fname
        m.save(str(out))
        return out

    p1 = write_map("priority_v1", "priority_v1_efficiency.html", "YlOrRd")
    out_paths = [p1]
    if g["priority_v3"].notna().any():
        p3 = write_map("priority_v3", "priority_v3_equity.html", "PuRd")
        out_paths.append(p3)

    # combined: v1 as base, v3 as a toggleable layer
    import folium
    m = g.explore(column="priority_v1", cmap="YlOrRd", scheme="quantiles", k=6,
                  legend=True, tooltip=show, name="v1 efficiency",
                  style_kwds={"weight": 0.3, "fillOpacity": 0.7},
                  tiles="CartoDB positron")
    if g["priority_v3"].notna().any():
        g.explore(m=m, column="priority_v3", cmap="PuRd", scheme="quantiles", k=6,
                  legend=False, tooltip=show, name="v3 equity", show=False,
                  style_kwds={"weight": 0.3, "fillOpacity": 0.7})
    folium.LayerControl(collapsed=False).add_to(m)
    combined = OUTDIR / "priority_combined.html"
    m.save(str(combined))
    out_paths.append(combined)

    # DIFFERENCE map -- where equity (v3) moves priority vs efficiency (v1).
    # delta > 0 (blue): v3 rewards this cell more -> poorer, equity pushes UP.
    # delta < 0 (red):  v3 demotes this cell      -> richer, equity pulls DOWN.
    if g["priority_v3"].notna().any():
        g["equity_shift"] = (g["priority_v3"] - g["priority_v1"]).round(3)
        # top-15 membership change
        t15_v1 = set(g.sort_values("priority_v1", ascending=False).head(15)["cell_id"])
        t15_v3 = set(g.sort_values("priority_v3", ascending=False).head(15)["cell_id"])
        def membership(cid):
            if cid in t15_v1 and cid in t15_v3:
                return "top15 both"
            if cid in t15_v3:
                return "ENTERS top15 (equity)"
            if cid in t15_v1:
                return "LEAVES top15 (equity)"
            return "-"
        g["top15_change"] = g["cell_id"].map(membership)

        dshow = ["cell_id", "district", "cell_income", "deprivation_std",
                 "priority_v1", "priority_v3", "equity_shift", "top15_change"]
        dshow = [c for c in dshow if c in g.columns]
        vmax = float(np.nanmax(np.abs(g["equity_shift"])))
        dm = g.explore(column="equity_shift", cmap="RdBu", vmin=-vmax, vmax=vmax,
                       legend=True, tooltip=dshow, name="equity shift (v3 - v1)",
                       style_kwds={"weight": 0.3, "fillOpacity": 0.75},
                       tiles="CartoDB positron")
        diffmap = OUTDIR / "priority_equity_shift.html"
        dm.save(str(diffmap))
        out_paths.append(diffmap)

        enters = sorted(t15_v3 - t15_v1)
        leaves = sorted(t15_v1 - t15_v3)
        print("\n--- EQUITY EFFECT on the top-15 ---")
        print(f"ENTERS top-15 under equity (v3): {enters}")
        print(f"LEAVES top-15 under equity (v3): {leaves}")
        print(f"unchanged: {15 - len(enters)} of 15")

    print("\nINTERACTIVE MAPS written (open in browser):")
    for p in out_paths:
        print("  ", p)
    print("\nWhich map to open:")
    print("  priority_combined.html      -- v1 vs v3, toggle top-right")
    print("  priority_equity_shift.html  -- THE difference: blue=equity rewards (poorer),")
    print("                                 red=equity demotes (richer). This shows the shift.")


if __name__ == "__main__":
    main()
