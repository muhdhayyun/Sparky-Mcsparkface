"""Evaluation metrics and visualization helpers for regression models."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def compute_regression_metrics(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, float]:
    """Compute standard regression metrics."""
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)),
    }


def plot_predicted_vs_actual(
    y_true: pd.Series, y_pred: np.ndarray, output_path: str | Path
) -> Path:
    """Save a predicted-versus-actual scatter plot."""
    output_path = Path(output_path)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(y_true, y_pred, alpha=0.6)
    min_value = min(float(np.min(y_true)), float(np.min(y_pred)))
    max_value = max(float(np.max(y_true)), float(np.max(y_pred)))
    ax.plot([min_value, max_value], [min_value, max_value], linestyle="--", color="red")
    ax.set_xlabel("Actual")
    ax.set_ylabel("Predicted")
    ax.set_title("Predicted vs Actual")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_residuals(y_true: pd.Series, y_pred: np.ndarray, output_path: str | Path) -> Path:
    """Save a residual plot."""
    output_path = Path(output_path)
    residuals = y_true - y_pred
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.scatter(y_pred, residuals, alpha=0.6)
    ax.axhline(0, linestyle="--", color="red")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Residual")
    ax.set_title("Residual Plot")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_feature_importance(
    pipeline: Any,
    feature_names: list[str],
    output_path: str | Path,
    top_n: int = 20,
) -> Path | None:
    """Save feature importance plot if the fitted model exposes importances."""
    model = getattr(pipeline, "named_steps", {}).get("model")
    importances = getattr(model, "feature_importances_", None)
    if importances is None:
        return None

    output_path = Path(output_path)
    importance_df = (
        pd.DataFrame({"feature": feature_names, "importance": importances})
        .sort_values("importance", ascending=False)
        .head(top_n)
    )

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(importance_df["feature"], importance_df["importance"])
    ax.set_title("Feature Importance")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def evaluate_regression_model(
    pipeline: Any,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    output_dir: str | Path,
) -> dict[str, Any]:
    """Evaluate a trained regression model and save visual artifacts."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    predictions = pipeline.predict(X_test)
    metrics = compute_regression_metrics(y_test, predictions)
    pred_actual_path = plot_predicted_vs_actual(y_test, predictions, output_dir / "predicted_vs_actual.png")
    residual_path = plot_residuals(y_test, predictions, output_dir / "residuals.png")

    feature_importance_path = None
    preprocessor = getattr(pipeline, "named_steps", {}).get("preprocessor")
    if preprocessor is not None and hasattr(preprocessor, "get_feature_names_out"):
        feature_names = list(preprocessor.get_feature_names_out())
        feature_importance_path = plot_feature_importance(
            pipeline,
            feature_names=feature_names,
            output_path=output_dir / "feature_importance.png",
        )

    return {
        "metrics": metrics,
        "predicted_vs_actual_path": pred_actual_path,
        "residual_path": residual_path,
        "feature_importance_path": feature_importance_path,
    }
