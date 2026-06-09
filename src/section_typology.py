"""Cycle-B Phase-4 Model #2 -- INTERVENTION TYPOLOGIES (unsupervised clustering).

Clusters the 1,068 sections into intervention archetypes on five decision-relevant layers
(mature-plane density, population density, income, sealed surface, NDVI). No target ->
no tautology possible. Compares k-means, Gaussian Mixture, and spatial contiguity-constrained
Ward (sklearn AgglomerativeClustering + queen-adjacency connectivity -- the SKATER regionalization
family, Assuncao et al. 2006, no extra deps). Reports silhouette/CH/DB, stability (ARI), and
named archetype profiles for planner segmentation.

Deterministic (seed 42), ASCII-only. Run:  python src/section_typology.py
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.sparse import csr_matrix
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import (silhouette_score, calinski_harabasz_score,
                             davies_bouldin_score, adjusted_rand_score)
from sklearn.preprocessing import StandardScaler

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
FEAT = ROOT / "data" / "processed" / "section_features.parquet"
OUTDIR = ROOT / "outputs" / "phase-6"
DESIGN = ROOT / "phase-6" / "modeling-ml-design.md"
LAYERS = ["mature_density", "pop_density", "income", "mean_sealed", "mean_ndvi"]
SIL_CRIT = 0.25


def queen_adjacency(gdf):
    """Sparse 0/1 contiguity matrix: sections sharing a boundary/point."""
    idx = gdf.sindex
    rows, cols = [], []
    geoms = gdf.geometry.values
    for i, g in enumerate(geoms):
        for j in idx.query(g, predicate="intersects"):
            if i != j:
                rows.append(i); cols.append(int(j))
    n = len(gdf)
    return csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n))


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    g = gpd.read_parquet(FEAT)
    Xz = StandardScaler().fit_transform(g[LAYERS].to_numpy(float))

    # scan k for k-means
    scan = []
    for k in range(3, 9):
        lab = KMeans(k, random_state=SEED, n_init=10).fit_predict(Xz)
        scan.append({"k": k,
                     "silhouette": round(float(silhouette_score(Xz, lab)), 4),
                     "calinski_harabasz": round(float(calinski_harabasz_score(Xz, lab)), 1),
                     "davies_bouldin": round(float(davies_bouldin_score(Xz, lab)), 4)})
    best_k = max(scan, key=lambda r: r["silhouette"])["k"]

    km = KMeans(best_k, random_state=SEED, n_init=10).fit_predict(Xz)
    gm = GaussianMixture(best_k, random_state=SEED, n_init=5).fit_predict(Xz)
    W = queen_adjacency(g)
    ward = AgglomerativeClustering(n_clusters=best_k, linkage="ward",
                                   connectivity=W).fit_predict(Xz)

    # stability: ARI across kmeans seeds, and kmeans vs GMM vs spatial-Ward
    km_alt = KMeans(best_k, random_state=7, n_init=10).fit_predict(Xz)
    stab = {
        "kmeans_seed42_vs_seed7": round(float(adjusted_rand_score(km, km_alt)), 4),
        "kmeans_vs_gmm": round(float(adjusted_rand_score(km, gm)), 4),
        "kmeans_vs_spatial_ward": round(float(adjusted_rand_score(km, ward)), 4),
    }

    # profiles + names (on the primary k-means labels, in raw units)
    g = g.copy(); g["cluster"] = km
    prof = g.groupby("cluster")[LAYERS].mean()
    sizes = g.groupby("cluster").size()
    med = g[LAYERS].median()
    archetypes = {}
    for c in prof.index:
        src = "high-source" if prof.loc[c, "mature_density"] >= med["mature_density"] else "low-source"
        pop = "high-pop" if prof.loc[c, "pop_density"] >= med["pop_density"] else "low-pop"
        inc = "lower-income" if prof.loc[c, "income"] < med["income"] else "higher-income"
        act = ("PRIORITY (cut early)" if src == "high-source" and pop == "high-pop"
               else "defer (park-like)" if src == "high-source" and pop == "low-pop"
               else "monitor" if src == "low-source" and pop == "high-pop"
               else "low-relevance")
        archetypes[int(c)] = {"name": f"{src} / {pop} / {inc}", "action": act,
                              "n_sections": int(sizes[c])}

    res = {"n": int(len(g)), "layers": LAYERS, "k_scan": scan, "chosen_k": best_k,
           "silhouette_criterion": SIL_CRIT,
           "chosen_silhouette": next(r["silhouette"] for r in scan if r["k"] == best_k),
           "stability_ARI": stab,
           "profiles_raw_means": prof.round(2).to_dict(orient="index"),
           "archetypes": archetypes}
    res["VERDICT"] = (
        f"usable segmentation: silhouette {res['chosen_silhouette']} >= {SIL_CRIT}, "
        f"{best_k} interpretable archetypes"
        if res["chosen_silhouette"] >= SIL_CRIT else
        f"WEAK structure: silhouette {res['chosen_silhouette']} < {SIL_CRIT} -- the city varies "
        f"continuously, archetypes are a convenience not a natural grouping (reported honestly)")

    # write per-section labels (data product) + results
    out = g[["key", "district_lbl", "cluster"] + LAYERS].copy()
    out["archetype"] = out["cluster"].map(lambda c: archetypes[int(c)]["name"])
    out["action"] = out["cluster"].map(lambda c: archetypes[int(c)]["action"])
    out.to_csv(OUTDIR / "section_typology.csv", index=False)
    (OUTDIR / "section_typology.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    _write_md(res); _append_design(res)
    print(json.dumps(res, indent=2))


def _write_md(res):
    scan = "\n".join(f"| {r['k']} | {r['silhouette']} | {r['calinski_harabasz']} | {r['davies_bouldin']} |"
                     for r in res["k_scan"])
    arch = "\n".join(f"| {c} | {a['name']} | {a['action']} | {a['n_sections']} |"
                     for c, a in res["archetypes"].items())
    md = f"""# Intervention Typologies (Cycle-B Phase-4 Model #2)

Unsupervised clustering of 1,068 sections on {res['layers']}. No target -> no tautology.

**VERDICT: {res['VERDICT']}**

## Choosing k (k-means)
| k | silhouette | Calinski-Harabasz | Davies-Bouldin |
|---|---|---|---|
{scan}
Chosen k = {res['chosen_k']} (criterion: silhouette >= {res['silhouette_criterion']}).

## Stability (Adjusted Rand Index)
{json.dumps(res['stability_ARI'], indent=2)}

## Archetypes (k-means labels; raw-unit profiles in the JSON)
| cluster | archetype (source / pop / income) | suggested action | sections |
|---|---|---|---|
{arch}

Per-section labels: `outputs/phase-6/section_typology.csv` (planner segmentation + map colouring).
Spatially-contiguous variant (Ward + queen adjacency) agreement with k-means: ARI
{res['stability_ARI']['kmeans_vs_spatial_ward']}.
"""
    (OUTDIR / "section_typology.md").write_text(md, encoding="utf-8")


def _append_design(res):
    if not DESIGN.exists():
        return
    txt = DESIGN.read_text(encoding="utf-8")
    anchor = "(typology + hotspot results appended below.)"
    block = (anchor + "\n\n### Model #2 -- typologies\n\n"
             f"**{res['VERDICT']}** Chosen k={res['chosen_k']}, silhouette "
             f"{res['chosen_silhouette']}. Stability ARI: seed {res['stability_ARI']['kmeans_seed42_vs_seed7']}, "
             f"vs GMM {res['stability_ARI']['kmeans_vs_gmm']}, vs spatial-Ward "
             f"{res['stability_ARI']['kmeans_vs_spatial_ward']}. "
             f"{len(res['archetypes'])} archetypes -> `outputs/phase-6/section_typology.md`. "
             "(hotspot results appended below.)")
    if anchor in txt:
        DESIGN.write_text(txt.replace(anchor, block), encoding="utf-8")


if __name__ == "__main__":
    main()
