"""Phase 5 — ROB/VAL evidence pack (pre-registered in phase-4/test-design.md SS4-6).

Implements:
  ROB-01..04  24-spec sensitivity grid + rank-stability tags + figure
  ROB-03      Cronbach's alpha across the 4 sub-scores
  ROB-05..08  linear-model stability: jackknife, noise, 3-seed splits, alt-cut
  VAL-01..04  construct validity: convergent / discriminant / Jaccard / OOD

Self-contained on pandas/numpy/geopandas/scipy/sklearn/matplotlib. Deterministic
(seed 42). ASCII-only console (Windows cp1252). Raw data not mutated.
Run:  python src/phase5_robustness.py
"""
from __future__ import annotations

import json
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.impute import SimpleImputer
from sklearn.metrics import r2_score

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
GRID = ROOT / "data" / "processed" / "scored_grid.parquet"
CLUST = ROOT / "data" / "splits" / "cluster_assignments.parquet"
PREDS = ROOT / "outputs" / "phase-4" / "predictions.parquet"
OUT = ROOT / "outputs" / "phase-4"
FIG = ROOT / "outputs" / "sensitivity-rank-stability.png"
DESIGN = ROOT / "phase-4" / "test-design.md"

COMPONENTS = ["s1_sealed", "s2_lst_anomaly", "s3_inverted_ndvi", "s4_mismatch", "prpi"]
SUBSCORES4 = ["s1_sealed", "s2_lst_anomaly", "s3_inverted_ndvi", "s4_mismatch"]
WEIGHTS = {
    "A": [0.20, 0.20, 0.20, 0.20, 0.20],
    "B": [0.45, 0.20, 0.15, 0.05, 0.15],
    "C": [0.15, 0.25, 0.25, 0.20, 0.15],
}
FEATURES = ["mean_sealed", "mean_ndvi", "lst_anomaly", "am_pct", "em_pct",
            "platanus_pct", "cell_vpa_score", "species_richness",
            "total_trees", "trees_young_pct"]
TARGET = "composite_score_B"


def minmax(x):
    lo, hi = np.nanmin(x), np.nanmax(x)
    return np.full_like(x, 0.5) if hi - lo == 0 else (x - lo) / (hi - lo)


def normalize(df, mode):
    M = df[COMPONENTS].to_numpy(float)
    out = np.empty_like(M)
    for j in range(M.shape[1]):
        col = M[:, j]
        if mode == "minmax":
            out[:, j] = minmax(col)
        elif mode == "winsor":
            lo, hi = np.nanpercentile(col, 5), np.nanpercentile(col, 95)
            out[:, j] = minmax(np.clip(col, lo, hi))
        elif mode == "zscore":
            sd = np.nanstd(col)
            z = (col - np.nanmean(col)) / (sd if sd else 1.0)
            out[:, j] = minmax(z)
    return out


def weights_for(scheme, Mn):
    if scheme in WEIGHTS:
        return np.array(WEIGHTS[scheme])
    # PCA: abs loadings of first PC, normalized to sum 1
    X = Mn - Mn.mean(0)
    _, _, vt = np.linalg.svd(X, full_matrices=False)
    w = np.abs(vt[0])
    return w / w.sum()


def aggregate(Mn, w, mode):
    if mode == "linear":
        return Mn @ w
    eps = 1e-6
    return np.exp((w * np.log(Mn + eps)).sum(1))  # geometric weighted product


def tiers(score):
    hi, lo = np.nanpercentile(score, 90), np.nanpercentile(score, 10)
    t = np.where(score >= hi, "top", np.where(score <= lo, "bottom", "mid"))
    return t


def cronbach(df):
    M = df[SUBSCORES4].to_numpy(float)
    k = M.shape[1]
    item_var = M.var(0, ddof=1).sum()
    total_var = M.sum(1).var(ddof=1)
    return float(k / (k - 1) * (1 - item_var / total_var))


def fit_lr(tr, te):
    imp = SimpleImputer(strategy="median").fit(tr[FEATURES])
    Xtr, Xte = imp.transform(tr[FEATURES]), imp.transform(te[FEATURES])
    lr = LinearRegression(fit_intercept=False).fit(Xtr, tr[TARGET])
    return lr, imp, r2_score(te[TARGET], lr.predict(Xte))


def main():
    np.random.seed(SEED)
    OUT.mkdir(parents=True, exist_ok=True)
    g = gpd.read_parquet(GRID)
    res = {}

    # ---- correctness gate -------------------------------------------------
    default = (np.array(WEIGHTS["B"]) * g[COMPONENTS].to_numpy(float)).sum(1).clip(0, 1)
    gate = float(np.corrcoef(default, g[TARGET])[0, 1])
    assert gate > 0.999, f"recipe mismatch: corr={gate:.5f}"
    res["correctness_gate_corr"] = round(gate, 6)

    # ---- ROB-01..04 sensitivity grid -------------------------------------
    norms = {"minmax": None, "winsor": None, "zscore": None}
    for m in norms:
        norms[m] = normalize(g, m)
    specs, tier_cols = [], {}
    for nmode, wsch, agg in product(["minmax", "winsor", "zscore"],
                                    ["A", "B", "C", "PCA"], ["linear", "geom"]):
        Mn = norms[nmode]
        w = weights_for(wsch, Mn)
        score = aggregate(Mn, w, agg)
        name = f"{nmode}|{wsch}|{agg}"
        specs.append(name)
        tier_cols[name] = tiers(score)
    default_name = "minmax|B|linear"
    grid_df = pd.DataFrame({"cell_id": g["cell_id"].values})
    for s in specs:
        grid_df[s] = tier_cols[s]
    dflt = tier_cols[default_name]
    stab = np.sum([tier_cols[s] == dflt for s in specs], axis=0)
    grid_df["rank_stability"] = stab
    grid_df["robustness_tag"] = np.where(stab >= 22, "ROBUST",
                                  np.where(stab < 18, "FRAGILE", "MODERATE"))
    grid_df.to_csv(OUT / "sensitivity-grid.csv", index=False)
    counts = grid_df["robustness_tag"].value_counts().to_dict()
    res["sensitivity"] = {"n_specs": len(specs), "tag_counts": counts,
                          "default_spec": default_name}

    plt.figure(figsize=(7, 4))
    plt.hist(stab, bins=range(0, 26), color="#4C72B0", edgecolor="white")
    plt.xlabel("rank-stability (specs agreeing with default tier, /24)")
    plt.ylabel("cells")
    plt.title("Sensitivity: per-cell rank-stability across 24 specs")
    plt.tight_layout(); plt.savefig(FIG, dpi=120); plt.close()

    # ---- ROB-03 Cronbach --------------------------------------------------
    res["cronbach_alpha_4subscores"] = round(cronbach(g), 4)

    # ---- ROB-05..08 stability --------------------------------------------
    ca = pd.read_parquet(CLUST)
    gg = g.merge(ca[["cell_id", "cluster_id", "split"]], on="cell_id", how="left")
    train_clusters = sorted(gg.loc[gg.split == "train", "cluster_id"].unique())
    tr_all = gg[gg.split == "train"].copy()
    te = gg[gg.split == "test"].copy()
    base_lr, base_imp, base_r2 = fit_lr(tr_all, te)

    # jackknife: drop each train cluster
    jk = {}
    for c in train_clusters:
        sub = tr_all[tr_all.cluster_id != c]
        lr, _, _ = fit_lr(sub, te)
        jk[int(c)] = lr.coef_
    jk_arr = np.array(list(jk.values()))
    jack = {FEATURES[i]: {"mean": round(float(jk_arr[:, i].mean()), 4),
                          "std": round(float(jk_arr[:, i].std()), 4)}
            for i in range(len(FEATURES))}

    # noise: N(0, 0.02 * train-sd per feature)
    sd = tr_all[FEATURES].std().to_numpy()
    trn = tr_all.copy()
    rng = np.random.default_rng(SEED)
    trn[FEATURES] = tr_all[FEATURES].to_numpy() + rng.normal(0, 0.02 * sd, (len(tr_all), len(FEATURES)))
    _, _, noise_r2 = fit_lr(trn, te)

    # 3 alternative kmeans seeds
    coords = np.column_stack([gg.geometry.centroid.x, gg.geometry.centroid.y])
    seed_r2 = {}
    for s in (1, 7, 123):
        km = KMeans(n_clusters=5, random_state=s, n_init=10).fit(coords)
        lab = km.labels_
        order = pd.Series(lab).value_counts().index.tolist()  # desc size
        split_map = {order[0]: "train", order[1]: "train", order[2]: "train",
                     order[3]: "eval", order[4]: "test"}
        sp = np.array([split_map[l] for l in lab])
        tr_s = gg[sp == "train"]; te_s = gg[sp == "test"]
        _, _, r2s = fit_lr(tr_s, te_s)
        seed_r2[s] = round(float(r2s), 4)

    # alt-cut: drop the largest district from training
    big_dist = tr_all["district"].value_counts().index[0]
    _, _, altcut_r2 = fit_lr(tr_all[tr_all.district != big_dist], te)

    res["stability"] = {
        "baseline_test_r2": round(float(base_r2), 4),
        "jackknife_coef": jack,
        "noise_sigma0.02_test_r2": round(float(noise_r2), 4),
        "noise_delta": round(float(noise_r2 - base_r2), 4),
        "alt_seed_test_r2": seed_r2,
        "alt_cut_drop_%s_test_r2" % big_dist: round(float(altcut_r2), 4),
    }
    (OUT / "stability.json").write_text(json.dumps(res["stability"], indent=2), encoding="utf-8")

    # ---- VAL-01..04 construct validity -----------------------------------
    pr = pd.read_parquet(PREDS)
    ycol = "y_pred__LinearRegression"
    pv = pr.merge(g[["cell_id", "mean_sealed", "species_richness", "top15_flag"]],
                  on="cell_id", how="left")
    conv = float(np.corrcoef(pv[ycol], pv["mean_sealed"])[0, 1])
    disc = float(np.corrcoef(pv[ycol], pv["species_richness"])[0, 1])
    top15_pred = set(pv.sort_values(ycol, ascending=False).head(15)["cell_id"])
    top15_flag = set(pv.loc[pv["top15_flag"] == 1, "cell_id"])
    jac = len(top15_pred & top15_flag) / len(top15_pred | top15_flag) if (top15_pred | top15_flag) else float("nan")
    test = pr[pr.split == "test"].copy()
    test["resid"] = test["y_true"] - test[ycol]
    ood = test.groupby("district")["resid"].apply(lambda s: round(float(s.abs().mean()), 4)).to_dict()
    res["construct_validity"] = {
        "convergent_r_pred_vs_sealed": round(conv, 4),
        "discriminant_r_pred_vs_richness": round(disc, 4),
        "jaccard_top15_pred_vs_flag": round(jac, 4),
        "jaccard_below_0.5": bool(jac < 0.5),
        "ood_mean_abs_resid_by_district": ood,
        "ood_districts_over_0.10": [d for d, v in ood.items() if v > 0.10],
    }
    (OUT / "construct-validity.json").write_text(
        json.dumps(res["construct_validity"], indent=2), encoding="utf-8")

    _append_design(res)
    print(json.dumps(res, indent=2))


def _append_design(res):
    if not DESIGN.exists():
        return
    s, sv, cv = res["sensitivity"], res["stability"], res["construct_validity"]
    block = f"""

## Results (ROB/VAL, appended 2026-06-04)

**Correctness gate:** default spec reproduces `composite_score_B` at corr = {res['correctness_gate_corr']}.

**ROB-01..04 sensitivity grid (24 specs):** cells tagged {s['tag_counts']} (ROBUST >=22/24, FRAGILE <18/24). Artifact `outputs/phase-4/sensitivity-grid.csv`, figure `outputs/sensitivity-rank-stability.png`.

**ROB-03 Cronbach's alpha (4 sub-scores):** {res['cronbach_alpha_4subscores']}.

**ROB-05 jackknife:** per-feature coef mean +/- std across 3 train-cluster refits (full table `outputs/phase-4/stability.json`). **ROB-06 noise (sigma 0.02 of train SD):** test-R2 {sv['noise_sigma0.02_test_r2']} (delta {sv['noise_delta']}). **ROB-07 alt seeds:** test-R2 {sv['alt_seed_test_r2']}. **ROB-08 alt-cut:** {[k for k in sv if k.startswith('alt_cut')][0]} = {sv[[k for k in sv if k.startswith('alt_cut')][0]]} vs baseline {sv['baseline_test_r2']}.

**VAL-01 convergent** r(pred, sealed) = {cv['convergent_r_pred_vs_sealed']}. **VAL-02 discriminant** r(pred, richness) = {cv['discriminant_r_pred_vs_richness']}. **VAL-03 Jaccard** top-15 pred vs flag = {cv['jaccard_top15_pred_vs_flag']} (below 0.5: {cv['jaccard_below_0.5']}). **VAL-04 OOD** districts with mean|resid|>0.10: {cv['ood_districts_over_0.10']}.
"""
    DESIGN.write_text(DESIGN.read_text(encoding="utf-8") + block, encoding="utf-8")


if __name__ == "__main__":
    main()
