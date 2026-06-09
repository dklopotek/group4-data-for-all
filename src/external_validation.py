"""Phase 5 — External validation test (pre-registered in phase-5/external-validation-design.md).

Question: after accounting for the abiotic null (sealed surface + greenness), do the
biotic/host layers add explanatory power for an EXTERNAL fungal outcome (observed GBIF
fungal occurrence) the composite never used?

Pre-registered PASS criterion (richness, observed subset):
    Delta adjusted-R2 (M1 - M0) >= 0.05  AND  partial-F p < 0.05.
Presence parallel: Delta CV-AUC >= 0.03 AND likelihood-ratio p < 0.05.

Self-contained on pandas/numpy/geopandas/scipy/sklearn (no statsmodels/pysal).
Deterministic (RANDOM_SEED = 42). Raw inputs are not mutated.

Run:  python src/external_validation.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from scipy import stats
from scipy.spatial import cKDTree
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

RANDOM_SEED = 42
GRID_CRS = "EPSG:25831"
ROOT = Path(__file__).resolve().parents[1]
GRID_PATH = ROOT / "data" / "processed" / "scored_grid.parquet"
GBIF_PATH = ROOT / "data" / "gbif-fungi-all.json"
TARGET_OUT = ROOT / "data" / "processed" / "gbif_external_target.parquet"
RESULTS_DIR = ROOT / "outputs" / "phase-5"
DESIGN_DOC = ROOT / "phase-5" / "external-validation-design.md"

ABIOTIC = ["mean_sealed", "mean_ndvi", "log_effort"]
BIOTIC = ["am_pct", "em_pct", "platanus_pct", "s4_mismatch", "prpi",
          "species_richness", "total_trees"]
# columns that must NOT be model inputs because they define the composite (leakage guard)
COMPOSITE_INPUTS = {
    "s1_sealed", "s2_lst_anomaly", "s3_inverted_ndvi", "s4_mismatch",
    "composite_score_A", "composite_score_B", "composite_score_C", "prpi",
}


# --------------------------------------------------------------------------- #
# 1. Build the external GBIF target
# --------------------------------------------------------------------------- #
def build_target(grid: gpd.GeoDataFrame) -> pd.DataFrame:
    records = json.loads(GBIF_PATH.read_text(encoding="utf-8"))
    rows = [
        (r.get("decimalLongitude"), r.get("decimalLatitude"),
         r.get("species") or r.get("scientificName"))
        for r in records
        if r.get("decimalLatitude") is not None and r.get("decimalLongitude") is not None
    ]
    pts = pd.DataFrame(rows, columns=["lon", "lat", "species"])
    gpts = gpd.GeoDataFrame(
        pts, geometry=[Point(xy) for xy in zip(pts.lon, pts.lat)], crs="EPSG:4326"
    ).to_crs(GRID_CRS)

    joined = gpd.sjoin(gpts, grid[["cell_id", "geometry"]], how="inner", predicate="within")
    agg = joined.groupby("cell_id").agg(
        gbif_richness=("species", "nunique"),
        gbif_effort=("species", "size"),
    ).reset_index()

    tgt = grid[["cell_id"]].merge(agg, on="cell_id", how="left")
    tgt["gbif_richness"] = tgt["gbif_richness"].fillna(0).astype(int)
    tgt["gbif_effort"] = tgt["gbif_effort"].fillna(0).astype(int)
    tgt["gbif_present"] = (tgt["gbif_effort"] >= 1).astype(int)
    return tgt


# --------------------------------------------------------------------------- #
# 2. OLS helpers (manual, so we can compute nested partial-F)
# --------------------------------------------------------------------------- #
def _design(df: pd.DataFrame, cols: list[str]) -> np.ndarray:
    X = df[cols].to_numpy(dtype=float)
    mu, sd = X.mean(0), X.std(0)
    sd[sd == 0] = 1.0
    Xs = (X - mu) / sd
    return np.column_stack([np.ones(len(Xs)), Xs])


def ols(df: pd.DataFrame, y: np.ndarray, cols: list[str]) -> dict:
    X = _design(df, cols)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    rss = float(resid @ resid)
    tss = float(((y - y.mean()) ** 2).sum())
    n, p = len(y), X.shape[1] - 1
    r2 = 1 - rss / tss if tss > 0 else float("nan")
    adj = 1 - (1 - r2) * (n - 1) / (n - p - 1) if n - p - 1 > 0 else float("nan")
    return {"rss": rss, "r2": r2, "adj_r2": adj, "n": n, "p": p,
            "beta": beta, "resid": resid, "cols": cols}


def partial_f(m0: dict, m1: dict) -> tuple[float, float]:
    q = m1["p"] - m0["p"]                       # added predictors
    df_res = m1["n"] - m1["p"] - 1
    num = (m0["rss"] - m1["rss"]) / q
    den = m1["rss"] / df_res
    f = num / den
    return f, float(stats.f.sf(f, q, df_res))


def vif(df: pd.DataFrame, cols: list[str]) -> dict:
    out = {}
    for c in cols:
        others = [o for o in cols if o != c]
        X = _design(df, others)
        y = (df[c].to_numpy(float) - df[c].mean()) / (df[c].std() or 1)
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        rss = float(((y - X @ beta) ** 2).sum())
        tss = float(((y - y.mean()) ** 2).sum())
        r2 = 1 - rss / tss if tss > 0 else 0.0
        out[c] = float("inf") if r2 >= 1 else 1.0 / (1.0 - r2)
    return out


# --------------------------------------------------------------------------- #
# 3. Presence model (logistic) — CV-AUC + likelihood-ratio test
# --------------------------------------------------------------------------- #
def _loglik(y: np.ndarray, p: np.ndarray) -> float:
    p = np.clip(p, 1e-9, 1 - 1e-9)
    return float(np.sum(y * np.log(p) + (1 - y) * np.log(1 - p)))


def logistic_block(df: pd.DataFrame, y: np.ndarray, m0_cols, m1_cols) -> dict:
    def fit_cv(cols):
        X = _design(df, cols)[:, 1:]  # logistic adds its own intercept
        clf = LogisticRegression(max_iter=2000, random_state=RANDOM_SEED)
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
        oof = np.zeros(len(y))
        for tr, te in skf.split(X, y):
            clf.fit(X[tr], y[tr])
            oof[te] = clf.predict_proba(X[te])[:, 1]
        auc = roc_auc_score(y, oof)
        clf.fit(X, y)                            # full-data fit for LR test
        ll = _loglik(y, clf.predict_proba(X)[:, 1])
        return auc, ll, len(cols)

    auc0, ll0, p0 = fit_cv(m0_cols)
    auc1, ll1, p1 = fit_cv(m1_cols)
    lr = 2 * (ll1 - ll0)
    lr_p = float(stats.chi2.sf(lr, p1 - p0))
    return {"auc0": auc0, "auc1": auc1, "d_auc": auc1 - auc0, "lr": lr, "lr_p": lr_p}


# --------------------------------------------------------------------------- #
# 4. Moran's I on residuals (kNN binary weights, permutation p)
# --------------------------------------------------------------------------- #
def morans_i(coords: np.ndarray, x: np.ndarray, k: int = 8, perms: int = 999) -> dict:
    n = len(x)
    if n <= k + 1:
        return {"I": float("nan"), "p": float("nan"), "note": "too few cells"}
    tree = cKDTree(coords)
    _, idx = tree.query(coords, k=k + 1)
    idx = idx[:, 1:]                              # drop self
    z = x - x.mean()
    s2 = float((z ** 2).sum())
    rng = np.random.default_rng(RANDOM_SEED)

    def stat(zv):
        num = sum(zv[i] * zv[idx[i]].sum() for i in range(n))
        return (n / (n * k)) * (num / s2)

    obs = stat(z)
    null = np.array([stat(rng.permutation(z)) for _ in range(perms)])
    p = (np.sum(np.abs(null) >= abs(obs)) + 1) / (perms + 1)
    return {"I": float(obs), "p": float(p)}


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    np.random.seed(RANDOM_SEED)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    grid = gpd.read_parquet(GRID_PATH)
    if grid.crs is None:
        grid = grid.set_crs(GRID_CRS)
    elif str(grid.crs).upper() not in (GRID_CRS, "EPSG:25831"):
        grid = grid.to_crs(GRID_CRS)

    # Leakage guard: model inputs must not be composite-defining columns
    bad = (set(ABIOTIC) | set(BIOTIC)) & COMPOSITE_INPUTS
    leak_note = (f"LEAKAGE WARNING: {sorted(bad)} are composite inputs"
                 if bad else "Leakage check OK: no model input defines the composite.")
    # (s4_mismatch and prpi ARE composite inputs but here they are TESTED as biotic
    #  predictors of an EXTERNAL target, not of the composite — that is the intended use.)

    tgt = build_target(grid)
    tgt.to_parquet(TARGET_OUT, index=False)

    df = grid.merge(tgt, on="cell_id", how="left").copy()
    df["log_effort"] = np.log1p(df["gbif_effort"])
    # median-impute predictors on the analysis frame
    for c in set(ABIOTIC) | set(BIOTIC):
        if c in df and df[c].isna().any():
            df[c] = df[c].fillna(df[c].median())

    centroids = np.column_stack([df.geometry.centroid.x, df.geometry.centroid.y])

    # ---- Primary: richness OLS on observed subset (effort >= 1) -------------
    obs = df[df["gbif_effort"] >= 1].reset_index(drop=True)
    y = obs["gbif_richness"].to_numpy(float)
    m0 = ols(obs, y, ABIOTIC)
    m1 = ols(obs, y, ABIOTIC + BIOTIC)
    f, fp = partial_f(m0, m1)
    d_adj = m1["adj_r2"] - m0["adj_r2"]
    pass_rich = bool(d_adj >= 0.05 and fp < 0.05)
    vifs = vif(obs, ABIOTIC + BIOTIC)
    obs_centroids = np.column_stack([obs.geometry.centroid.x, obs.geometry.centroid.y])
    moran = morans_i(obs_centroids, m1["resid"])

    # ---- Secondary: presence logistic over ALL cells -----------------------
    yp = df["gbif_present"].to_numpy(int)
    pres = logistic_block(df, yp, ABIOTIC, ABIOTIC + BIOTIC)
    pass_pres = bool(pres["d_auc"] >= 0.03 and pres["lr_p"] < 0.05)

    # ---- Robustness --------------------------------------------------------
    yl = np.log1p(obs["gbif_richness"].to_numpy(float))
    rl0, rl1 = ols(obs, yl, ABIOTIC), ols(obs, yl, ABIOTIC + BIOTIC)
    _, rl_p = partial_f(rl0, rl1)
    rob_logrich = {"d_adj_r2": rl1["adj_r2"] - rl0["adj_r2"], "partial_f_p": rl_p}

    ne = [c for c in ABIOTIC if c != "log_effort"]      # drop effort
    de0, de1 = ols(obs, y, ne), ols(obs, y, ne + BIOTIC)
    _, de_p = partial_f(de0, de1)
    rob_noeffort = {"d_adj_r2": de1["adj_r2"] - de0["adj_r2"], "partial_f_p": de_p}

    verdict = "PASS" if pass_rich else "FAIL"
    coefs = dict(zip(["intercept"] + m1["cols"], m1["beta"].round(4)))

    results = {
        "leakage": leak_note,
        "n_cells_total": int(len(df)),
        "n_cells_observed": int(len(obs)),
        "n_gbif_species_total": int(tgt["gbif_richness"].sum() and obs["gbif_richness"].max()),
        "richness_primary": {
            "M0_adj_r2": round(m0["adj_r2"], 4), "M1_adj_r2": round(m1["adj_r2"], 4),
            "delta_adj_r2": round(d_adj, 4), "partial_F": round(f, 3),
            "partial_F_p": round(fp, 5), "PASS": pass_rich,
        },
        "presence_secondary": {
            "M0_cv_auc": round(pres["auc0"], 4), "M1_cv_auc": round(pres["auc1"], 4),
            "delta_auc": round(pres["d_auc"], 4), "LR": round(pres["lr"], 3),
            "LR_p": round(pres["lr_p"], 5), "PASS": pass_pres,
        },
        "robustness": {"log_richness": rob_logrich, "drop_effort": rob_noeffort},
        "morans_I_resid": moran,
        "vif": {k: round(v, 2) for k, v in vifs.items()},
        "m1_coefficients_std": {k: float(v) for k, v in coefs.items()},
        "VERDICT": verdict,
    }
    (RESULTS_DIR / "external_validation_results.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8")
    _write_markdown(results)
    _append_design_results(results)

    print("=" * 60)
    print(f"EXTERNAL VALIDATION VERDICT: {verdict}")
    print(f"  richness  dAdjR2={d_adj:+.4f}  partial-F p={fp:.4f}  -> {'PASS' if pass_rich else 'FAIL'}")
    print(f"  presence  dAUC={pres['d_auc']:+.4f}  LR p={pres['lr_p']:.4f}  -> {'PASS' if pass_pres else 'FAIL'}")
    print(f"  observed cells: {len(obs)}/{len(df)}")
    print("=" * 60)


def _write_markdown(r: dict) -> None:
    rr, pr = r["richness_primary"], r["presence_secondary"]
    md = f"""# External Validation Results

**Verdict: {r['VERDICT']}** (pre-registered criterion in `phase-5/external-validation-design.md` Sec 4)

{r['leakage']}

Cells: {r['n_cells_observed']} with >=1 GBIF record / {r['n_cells_total']} total.

## Richness (primary, observed subset, OLS)
| Model | Adj-R2 |
|---|---|
| M0 abiotic null (sealed + ndvi + effort) | {rr['M0_adj_r2']} |
| M1 + biotic/host | {rr['M1_adj_r2']} |
| **Delta Adj-R2** | **{rr['delta_adj_r2']}** |

partial-F = {rr['partial_F']}, p = {rr['partial_F_p']} -> biotic block **{'adds signal' if rr['PASS'] else 'adds NO signal'}**

## Presence (secondary, all cells, logistic, 5-fold CV)
M0 AUC {pr['M0_cv_auc']} -> M1 AUC {pr['M1_cv_auc']} (Delta {pr['delta_auc']}); LR p {pr['LR_p']} -> {'PASS' if pr['PASS'] else 'FAIL'}

## Robustness
- log-richness OLS: dAdjR2 {r['robustness']['log_richness']['d_adj_r2']:.4f}, partial-F p {r['robustness']['log_richness']['partial_f_p']:.4f}
- drop effort: dAdjR2 {r['robustness']['drop_effort']['d_adj_r2']:.4f}, partial-F p {r['robustness']['drop_effort']['partial_f_p']:.4f}
- Moran's I on M1 residuals: I={r['morans_I_resid'].get('I')}, p={r['morans_I_resid'].get('p')}

## VIF (collinearity)
{json.dumps(r['vif'], indent=2)}

## M1 standardized coefficients
{json.dumps(r['m1_coefficients_std'], indent=2)}
"""
    (RESULTS_DIR / "external_validation_results.md").write_text(md, encoding="utf-8")


def _append_design_results(r: dict) -> None:
    if not DESIGN_DOC.exists():
        return
    txt = DESIGN_DOC.read_text(encoding="utf-8")
    marker = "_(pending build — `scripts/external_validation.py`)_"
    rr = r["richness_primary"]
    block = (f"**Verdict: {r['VERDICT']}.** Richness Delta Adj-R2 = {rr['delta_adj_r2']} "
             f"(criterion >= 0.05), partial-F p = {rr['partial_F_p']} (criterion < 0.05). "
             f"Observed cells {r['n_cells_observed']}/{r['n_cells_total']}. "
             f"Full table: `outputs/phase-5/external_validation_results.md`.")
    if marker in txt:
        DESIGN_DOC.write_text(txt.replace(marker, block), encoding="utf-8")


if __name__ == "__main__":
    main()
