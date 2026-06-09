"""Cycle-B Phase-4 Model #1 -- SOURCE ESTIMATOR (supervised, spatial cross-validation).

Predicts OBSERVED mature-Platanus density per section from urban-form + demographic
features (none derived from plane counts -> non-tautological; phase-6/modeling-ml-design.md sec 0).

The point: report RANDOM-CV next to SPATIAL-CV. Spatial autocorrelation inflates random-CV
(Roberts et al. 2017; Ploton et al. 2020) -- the same inflation that produced Cycle A's false
0.999. The gap is the audit. Headline = the SPATIAL-CV number.

Pre-registered: useful drift proxy iff spatial-CV R2 >= 0.30; below = honest negative (urban form
does not predict historical plane placement). Deterministic (seed 42), ASCII-only.
Run:  python src/section_source_model.py
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold, GroupKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
FEAT = ROOT / "data" / "processed" / "section_features.parquet"
OUTDIR = ROOT / "outputs" / "phase-6"
DESIGN = ROOT / "phase-6" / "modeling-ml-design.md"

NUM = ["mean_sealed", "mean_ndvi", "mean_lst_celsius", "income",
       "pop_density", "area_km2", "dist_to_centre_km", "compactness"]
CAT = ["district_lbl"]
TARGET = "mature_density"
CRITERION = 0.30


def make_ohe():
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:                      # older sklearn
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def pipe(model):
    pre = ColumnTransformer([("num", StandardScaler(), NUM), ("cat", make_ohe(), CAT)])
    return Pipeline([("pre", pre), ("model", model)])


def cv_scores(est, X, y, splitter, groups=None):
    r2 = cross_val_score(est, X, y, cv=splitter, groups=groups, scoring="r2")
    mae = -cross_val_score(est, X, y, cv=splitter, groups=groups, scoring="neg_mean_absolute_error")
    return round(float(r2.mean()), 4), round(float(mae.mean()), 2)


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    g = gpd.read_parquet(FEAT)
    X = g[NUM + CAT].copy()
    y = g[TARGET].to_numpy(float)

    # spatial folds = k-means on section centroids (k=5, seed 42)
    cxy = np.c_[g.geometry.centroid.x.to_numpy(), g.geometry.centroid.y.to_numpy()]
    clusters = KMeans(n_clusters=5, random_state=SEED, n_init=10).fit_predict(cxy)

    rand = KFold(n_splits=5, shuffle=True, random_state=SEED)
    spat = GroupKFold(n_splits=5)

    models = {
        "Ridge": pipe(Ridge(alpha=1.0, random_state=SEED)),
        "RandomForest": pipe(RandomForestRegressor(n_estimators=400, random_state=SEED, n_jobs=-1)),
    }
    res = {"target": TARGET, "n": int(len(g)), "criterion_spatial_R2": CRITERION, "models": {}}
    for name, est in models.items():
        r2_rand, mae_rand = cv_scores(est, X, y, rand)
        r2_spat, mae_spat = cv_scores(est, X, y, spat, groups=clusters)
        res["models"][name] = {
            "random_cv": {"R2": r2_rand, "MAE": mae_rand},
            "spatial_cv": {"R2": r2_spat, "MAE": mae_spat},
            "leakage_gap_R2": round(r2_rand - r2_spat, 4),
        }

    # feature importance from a full-data RF fit (interpretation only)
    rf = pipe(RandomForestRegressor(n_estimators=400, random_state=SEED, n_jobs=-1)).fit(X, y)
    names = NUM + list(rf.named_steps["pre"].named_transformers_["cat"]
                       .get_feature_names_out(CAT))
    imp = rf.named_steps["model"].feature_importances_
    top = sorted(zip(names, imp), key=lambda t: -t[1])[:8]
    res["rf_top_features"] = [{"feature": n, "importance": round(float(i), 4)} for n, i in top]

    best_spatial = max(m["spatial_cv"]["R2"] for m in res["models"].values())
    res["best_spatial_R2"] = best_spatial
    res["VERDICT"] = (
        f"USEFUL drift proxy: best spatial-CV R2 {best_spatial} >= {CRITERION}"
        if best_spatial >= CRITERION else
        f"HONEST NEGATIVE: best spatial-CV R2 {best_spatial} < {CRITERION} -- urban form does not "
        f"predict historical plane placement (planting is path-dependent). Inventory irreplaceable.")

    (OUTDIR / "source_model_results.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    _write_md(res); _append_design(res)
    print(json.dumps(res, indent=2))


def _write_md(res):
    rows = "\n".join(
        f"| {n} | {m['random_cv']['R2']} | **{m['spatial_cv']['R2']}** | {m['random_cv']['MAE']} | "
        f"{m['spatial_cv']['MAE']} | {m['leakage_gap_R2']} |"
        for n, m in res["models"].items())
    feats = ", ".join(f"{f['feature']} ({f['importance']})" for f in res["rf_top_features"][:6])
    md = f"""# Source-Estimator Results (Cycle-B Phase-4 Model #1)

Predicts observed **mature-plane density** from urban-form/demographic features (no plane-derived
inputs). Headline = **spatial-CV R2** (random-CV shown only to expose spatial-autocorrelation leakage,
the Cycle-A 0.999 trap; Roberts 2017, Ploton 2020).

**VERDICT: {res['VERDICT']}**

| model | random-CV R2 | spatial-CV R2 | random MAE | spatial MAE | leakage gap (R2) |
|---|---|---|---|---|---|
{rows}

Criterion (pre-registered): useful drift proxy iff spatial-CV R2 >= {res['criterion_spatial_R2']}.

**Top RF features:** {feats}.

The random-vs-spatial gap is the audit: a large gap = the same leakage that inflated Cycle A. We report
the spatial number as the truth.
"""
    (OUTDIR / "source_model_results.md").write_text(md, encoding="utf-8")


def _append_design(res):
    if not DESIGN.exists():
        return
    txt = DESIGN.read_text(encoding="utf-8")
    marker = "_(pending -- `src/section_source_model.py`, `section_typology.py`, `section_hotspots.py`)_"
    block = ("### Model #1 -- source estimator\n\n"
             f"**{res['VERDICT']}**\n\n"
             + "\n".join(f"- {n}: random-CV R2 {m['random_cv']['R2']}, **spatial-CV R2 "
                         f"{m['spatial_cv']['R2']}** (gap {m['leakage_gap_R2']}), spatial MAE "
                         f"{m['spatial_cv']['MAE']}." for n, m in res["models"].items())
             + f"\n- Top RF features: "
             + ", ".join(f["feature"] for f in res["rf_top_features"][:5])
             + ".\n- Full: `outputs/phase-6/source_model_results.md`. "
             + "(typology + hotspot results appended below.)\n")
    if marker in txt:
        DESIGN.write_text(txt.replace(marker, block), encoding="utf-8")


if __name__ == "__main__":
    main()
