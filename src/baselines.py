"""
baselines.py — three pre-registered baselines for Phase 4 (Core B regression).

Each baseline implements the minimal sklearn estimator interface (``fit`` /
``predict``) so it is interchangeable with ``LinearRegression`` in the
training driver. Targets are predictions of ``composite_score_B`` in [0, 1].

Baselines
---------
BaselineMean
    Predicts the train-set mean of the target for every test row. Lecture 4
    "dumb baseline" (mean/mode). The floor — any real model must beat this
    to claim it captures signal beyond bulk average.

BaselineSpatialNearest
    For each test row, predicts the target of the nearest train row by
    Euclidean distance on (x, y) centroid in EPSG:25831. Lecture 4 "spatial
    nearest" baseline. Captures pure-geography signal.

BaselineDomainHeuristic
    Rule: if mean_sealed > SEALED_HIGH_THRESHOLD then predict the 90th
    percentile of the train target; else predict the train mean. Lecture 4
    "domain heuristic" baseline. Encodes what an Espais Verds analyst
    already knows: more sealed surface implies more barrier severity.

References
----------
- Lecture 4 lines 313-328 (baselining)
- phase-4/test-design.md §2 (baseline contract)
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------
SEALED_HIGH_THRESHOLD = 0.7
HIGH_TIER_PERCENTILE = 90.0


@dataclass
class BaselineMean:
    """Predict the train mean of the target for every input row."""

    train_mean_: float = field(default=np.nan, init=False)

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "BaselineMean":
        self.train_mean_ = float(np.asarray(y).mean())
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return np.full(len(X), self.train_mean_, dtype=float)


@dataclass
class BaselineSpatialNearest:
    """Predict the target of the nearest train cell by Euclidean (x, y) distance.

    Expects ``X`` to contain ``cell_bbox_minx`` / ``cell_bbox_miny`` /
    ``cell_bbox_maxx`` / ``cell_bbox_maxy`` from the scored grid; uses the
    bbox midpoint as the centroid.
    """

    train_tree_: cKDTree | None = field(default=None, init=False)
    train_y_: np.ndarray | None = field(default=None, init=False)

    @staticmethod
    def _centroids(X: pd.DataFrame) -> np.ndarray:
        x = (X["cell_bbox_minx"].to_numpy() + X["cell_bbox_maxx"].to_numpy()) / 2.0
        y = (X["cell_bbox_miny"].to_numpy() + X["cell_bbox_maxy"].to_numpy()) / 2.0
        return np.column_stack([x, y])

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "BaselineSpatialNearest":
        pts = self._centroids(X)
        self.train_tree_ = cKDTree(pts)
        self.train_y_ = np.asarray(y, dtype=float)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        assert self.train_tree_ is not None and self.train_y_ is not None, (
            "BaselineSpatialNearest.predict called before fit"
        )
        pts = self._centroids(X)
        _, idx = self.train_tree_.query(pts, k=1)
        return self.train_y_[idx]


@dataclass
class BaselineDomainHeuristic:
    """Sealed-surface rule baseline.

    If ``mean_sealed > SEALED_HIGH_THRESHOLD`` -> predict the
    ``HIGH_TIER_PERCENTILE``th percentile of the train target.
    Otherwise -> predict the train mean.
    """

    high_tier_value_: float = field(default=np.nan, init=False)
    low_tier_value_: float = field(default=np.nan, init=False)

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "BaselineDomainHeuristic":
        y_arr = np.asarray(y, dtype=float)
        self.high_tier_value_ = float(np.percentile(y_arr, HIGH_TIER_PERCENTILE))
        self.low_tier_value_ = float(y_arr.mean())
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        sealed = X["mean_sealed"].to_numpy()
        return np.where(sealed > SEALED_HIGH_THRESHOLD, self.high_tier_value_, self.low_tier_value_)


def all_baselines() -> dict[str, object]:
    """Construct the three pre-registered baselines as a name -> estimator dict."""
    return {
        "BaselineMean": BaselineMean(),
        "BaselineSpatialNearest": BaselineSpatialNearest(),
        "BaselineDomainHeuristic": BaselineDomainHeuristic(),
    }
