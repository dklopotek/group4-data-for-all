"""
split_data.py — deterministic spatial cluster splitter for Phase 4 modeling.

Loads ``data/processed/scored_grid.parquet`` and writes:

    data/splits/cluster_assignments.parquet  (cell_id, cluster_id, split)
    data/splits/train.parquet
    data/splits/eval.parquet
    data/splits/test.parquet

Splitting strategy
------------------
K-means on cell centroid (x, y) in EPSG:25831, k = 5.

    cluster 0, 1, 2 -> TRAIN  (~60% of cells)
    cluster 3       -> EVAL   (~20% of cells)
    cluster 4       -> TEST   (~20% of cells, FROZEN — do not inspect)

Cluster-to-split mapping is locked by sorting clusters by descending size so
that the assignment is deterministic across re-runs.

References
----------
- Lecture 4 (Session 4) lines 291-301: spatial cluster split, k=5 example.
- crispdm-4-modeling skill §6: pre-registered test design.
- phase-4/test-design.md §1: split design contract.

Run from project root::

    python src/split_data.py
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd
from sklearn.cluster import KMeans

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------
RANDOM_SEED = 42
N_CLUSTERS = 5
TRAIN_CLUSTERS = 3  # first 3 (by size desc) -> train
# Remaining: 1 eval, 1 test

_HERE = Path(__file__).resolve().parent
PROJECT_ROOT = _HERE.parent
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "scored_grid.parquet"
SPLITS_DIR = PROJECT_ROOT / "data" / "splits"


def load_grid() -> gpd.GeoDataFrame:
    gdf = gpd.read_parquet(INPUT_PATH)
    assert gdf.crs is not None and gdf.crs.to_string() == "EPSG:25831", (
        f"Expected EPSG:25831 input CRS, got {gdf.crs}"
    )
    assert "cell_id" in gdf.columns, "Input missing cell_id"
    assert "composite_score_B" in gdf.columns, "Input missing target column"
    return gdf


def assign_clusters(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    centroids = gdf.geometry.centroid
    xy = pd.DataFrame(
        {"x": centroids.x.values, "y": centroids.y.values}, index=gdf.index
    )
    km = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_SEED, n_init=10)
    raw_labels = km.fit_predict(xy.values)

    # Re-label so cluster_id is sorted by descending size (deterministic).
    sizes = pd.Series(raw_labels).value_counts().sort_values(ascending=False)
    remap = {old: new for new, old in enumerate(sizes.index)}
    cluster_ids = pd.Series(raw_labels, index=gdf.index).map(remap)

    df = pd.DataFrame(
        {
            "cell_id": gdf["cell_id"].values,
            "x": xy["x"].values,
            "y": xy["y"].values,
            "cluster_id": cluster_ids.values,
        }
    )
    return df


def assign_splits(cluster_df: pd.DataFrame) -> pd.DataFrame:
    def to_split(cid: int) -> str:
        if cid < TRAIN_CLUSTERS:
            return "train"
        if cid == TRAIN_CLUSTERS:
            return "eval"
        return "test"

    cluster_df = cluster_df.copy()
    cluster_df["split"] = cluster_df["cluster_id"].map(to_split)
    return cluster_df


def write_splits(gdf: gpd.GeoDataFrame, cluster_df: pd.DataFrame) -> None:
    SPLITS_DIR.mkdir(parents=True, exist_ok=True)

    cluster_df[["cell_id", "cluster_id", "split"]].to_parquet(
        SPLITS_DIR / "cluster_assignments.parquet", index=False
    )

    joined = gdf.merge(cluster_df[["cell_id", "cluster_id", "split"]], on="cell_id")

    for split in ("train", "eval", "test"):
        subset = joined[joined["split"] == split]
        subset.to_parquet(SPLITS_DIR / f"{split}.parquet", index=False)
        print(f"  {split:5s}  n={len(subset):3d}  clusters={sorted(subset['cluster_id'].unique().tolist())}")


def main() -> None:
    print(f"[split_data] loading {INPUT_PATH.relative_to(PROJECT_ROOT)}")
    gdf = load_grid()
    print(f"[split_data] loaded {len(gdf)} cells")

    print(f"[split_data] k-means clustering on centroid (x, y), k={N_CLUSTERS}, seed={RANDOM_SEED}")
    cluster_df = assign_clusters(gdf)

    cluster_df = assign_splits(cluster_df)

    print(f"[split_data] writing splits to {SPLITS_DIR.relative_to(PROJECT_ROOT)}")
    write_splits(gdf, cluster_df)

    print("[split_data] done")


if __name__ == "__main__":
    main()
