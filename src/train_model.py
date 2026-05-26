"""
train_model.py — Phase 4 Core B regression driver.

Trains one linear regression and three baselines on the spatial split written
by ``src/split_data.py``, then writes:

    outputs/phase-4/metrics.csv             (one row per estimator x split)
    outputs/phase-4/per_district.csv        (test-set residuals by district)
    outputs/phase-4/predictions.parquet     (cell_id, split, y_true, y_pred*)
    outputs/phase-4/model_artifact.joblib   (fitted final model + imputer)

Constraints (Lecture 4)
-----------------------
- Exactly one model tuned (``fit_intercept in {True, False}``).
- No regularization sweep, no PolynomialFeatures.
- Test cluster touched exactly once at end.
- Every baseline + the model reported on train, eval, and test.

References
----------
- Lecture 4 (Session 4) lines 354-415
- phase-4/test-design.md §3-§8
- phase-4/analytical-question.md §5 (target + feature list, leakage check)
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline

from baselines import BaselineDomainHeuristic, BaselineMean, BaselineSpatialNearest

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------
TARGET = "composite_score_B"

FEATURE_COLS: list[str] = [
    "mean_sealed",
    "mean_ndvi",
    "lst_anomaly",
    "am_pct",
    "em_pct",
    "platanus_pct",
    "cell_vpa_score",
    "species_richness",
    "total_trees",
    "trees_young_pct",
]

# Columns needed by BaselineSpatialNearest beyond FEATURE_COLS
SPATIAL_AUX_COLS: list[str] = [
    "cell_bbox_minx",
    "cell_bbox_miny",
    "cell_bbox_maxx",
    "cell_bbox_maxy",
]

KEEP_COLS: list[str] = ["cell_id", "district", "split", TARGET] + FEATURE_COLS + SPATIAL_AUX_COLS

_HERE = Path(__file__).resolve().parent
PROJECT_ROOT = _HERE.parent
SPLITS_DIR = PROJECT_ROOT / "data" / "splits"
OUT_DIR = PROJECT_ROOT / "outputs" / "phase-4"


def load_split(name: str) -> pd.DataFrame:
    df = pd.read_parquet(SPLITS_DIR / f"{name}.parquet")
    keep = [c for c in KEEP_COLS if c in df.columns]
    return df[keep].copy()


def build_pipeline(fit_intercept: bool) -> Pipeline:
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("regressor", LinearRegression(fit_intercept=fit_intercept)),
        ]
    )


def score(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
    }


def evaluate_estimator(
    name: str,
    fitted: object,
    splits: dict[str, pd.DataFrame],
    needs_features: bool,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for split_name, df in splits.items():
        X = df[FEATURE_COLS + SPATIAL_AUX_COLS] if not needs_features else df[FEATURE_COLS]
        y_true = df[TARGET].to_numpy()
        y_pred = fitted.predict(X)
        s = score(y_true, y_pred)
        s.update({"estimator": name, "split": split_name, "n": int(len(df))})
        rows.append(s)
    return rows


def tune_model(
    train: pd.DataFrame, eval_: pd.DataFrame
) -> tuple[Pipeline, dict[str, object]]:
    """Tune the single allowed hyperparameter (``fit_intercept``) on eval."""
    results = []
    fitted_models: dict[bool, Pipeline] = {}
    for fi in (True, False):
        pipe = build_pipeline(fit_intercept=fi)
        pipe.fit(train[FEATURE_COLS], train[TARGET])
        fitted_models[fi] = pipe
        y_pred = pipe.predict(eval_[FEATURE_COLS])
        results.append({"fit_intercept": fi, **score(eval_[TARGET].to_numpy(), y_pred)})

    tune_df = pd.DataFrame(results).sort_values("mae")
    best = tune_df.iloc[0]
    chosen = bool(best["fit_intercept"])
    return fitted_models[chosen], {
        "tune_table": results,
        "chosen": {"fit_intercept": chosen, "eval_mae": float(best["mae"])},
    }


def per_district_residuals(test: pd.DataFrame, y_pred: np.ndarray) -> pd.DataFrame:
    df = test[["district", TARGET]].copy()
    df["y_pred"] = y_pred
    df["residual"] = df[TARGET] - df["y_pred"]
    grouped = df.groupby("district").agg(
        n=("residual", "size"),
        mean_resid=("residual", "mean"),
        abs_mean_resid=("residual", lambda x: float(np.abs(x).mean())),
        max_abs_resid=("residual", lambda x: float(np.abs(x).max())),
    )
    return grouped.reset_index().sort_values("abs_mean_resid", ascending=False)


def write_predictions(splits: dict[str, pd.DataFrame], preds: dict[str, dict[str, np.ndarray]]) -> None:
    frames = []
    for split_name, df in splits.items():
        out = df[["cell_id", "district", "split", TARGET]].copy().rename(columns={TARGET: "y_true"})
        for est_name, est_preds in preds.items():
            out[f"y_pred__{est_name}"] = est_preds[split_name]
        frames.append(out)
    pd.concat(frames, ignore_index=True).to_parquet(OUT_DIR / "predictions.parquet", index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[train_model] loading splits")
    train = load_split("train")
    eval_ = load_split("eval")
    test = load_split("test")
    splits = {"train": train, "eval": eval_, "test": test}
    print(f"  train n={len(train)}  eval n={len(eval_)}  test n={len(test)}")

    # ---- Baselines ------------------------------------------------------
    print("[train_model] fitting baselines on train only")
    baseline_estimators = {
        "BaselineMean": BaselineMean(),
        "BaselineSpatialNearest": BaselineSpatialNearest(),
        "BaselineDomainHeuristic": BaselineDomainHeuristic(),
    }
    for name, est in baseline_estimators.items():
        if name == "BaselineSpatialNearest":
            est.fit(train[SPATIAL_AUX_COLS], train[TARGET])
        else:
            est.fit(train[FEATURE_COLS], train[TARGET])

    # ---- Model: tune fit_intercept on eval ------------------------------
    print("[train_model] tuning LinearRegression(fit_intercept) on eval")
    model, tune_info = tune_model(train, eval_)
    print(f"  chosen fit_intercept = {tune_info['chosen']['fit_intercept']}  (eval MAE = {tune_info['chosen']['eval_mae']:.4f})")

    # ---- Metrics table --------------------------------------------------
    print("[train_model] computing train/eval/test metrics for every estimator")
    rows: list[dict[str, object]] = []
    for name, est in baseline_estimators.items():
        rows.extend(evaluate_estimator(name, est, splits, needs_features=False))
    rows.extend(evaluate_estimator("LinearRegression", model, splits, needs_features=True))

    metrics = pd.DataFrame(rows)[["estimator", "split", "n", "r2", "mae", "rmse"]]
    metrics.to_csv(OUT_DIR / "metrics.csv", index=False)
    print("\n  -- metrics (sorted, test only) --")
    print(metrics[metrics["split"] == "test"].sort_values("mae").to_string(index=False))

    # ---- Per-district residual table for test ---------------------------
    test_pred = model.predict(test[FEATURE_COLS])
    pd_df = per_district_residuals(test, test_pred)
    pd_df.to_csv(OUT_DIR / "per_district.csv", index=False)
    print(f"\n  per-district residuals -> {(OUT_DIR / 'per_district.csv').relative_to(PROJECT_ROOT)}")

    # ---- Predictions parquet --------------------------------------------
    all_preds: dict[str, dict[str, np.ndarray]] = {}
    for name, est in baseline_estimators.items():
        all_preds[name] = {
            sname: est.predict(df[SPATIAL_AUX_COLS] if name == "BaselineSpatialNearest" else df[FEATURE_COLS])
            for sname, df in splits.items()
        }
    all_preds["LinearRegression"] = {sname: model.predict(df[FEATURE_COLS]) for sname, df in splits.items()}
    write_predictions(splits, all_preds)

    # ---- Save fitted artifact ------------------------------------------
    joblib.dump(
        {
            "model": model,
            "features": FEATURE_COLS,
            "target": TARGET,
            "tune_info": tune_info,
            "version": "phase-4-v1",
        },
        OUT_DIR / "model_artifact.joblib",
    )

    print("\n[train_model] done")


if __name__ == "__main__":
    main()
