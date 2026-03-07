"""Model factory and training pipeline utilities."""

from __future__ import annotations

from typing import Any

from lightgbm import LGBMRegressor
from sklearn.base import RegressorMixin
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline


def get_model(model_name: str, model_params: dict[str, dict[str, Any]]) -> RegressorMixin:
    """Instantiate a supported regression model by name."""
    if model_name == "lightgbm":
        return LGBMRegressor(**model_params.get("lightgbm", {}))
    if model_name == "random_forest":
        return RandomForestRegressor(**model_params.get("random_forest", {}))
    if model_name == "linear_regression":
        return LinearRegression(**model_params.get("linear_regression", {}))
    raise ValueError(f"Unsupported model name: {model_name}")


def build_training_pipeline(preprocessor: Any, model: RegressorMixin) -> Pipeline:
    """Combine preprocessing and model training in one pipeline."""
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


def train_model(pipeline: Pipeline, X_train: Any, y_train: Any) -> Pipeline:
    """Fit the model pipeline and return the trained estimator."""
    pipeline.fit(X_train, y_train)
    return pipeline
