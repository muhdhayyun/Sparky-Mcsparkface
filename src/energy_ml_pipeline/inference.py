"""Inference helpers for loading models and generating predictions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd


def save_model(model: Any, output_path: str | Path) -> Path:
    """Persist a trained model pipeline to disk."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
    return output_path


def load_model(model_path: str | Path) -> Any:
    """Load a persisted model pipeline from disk."""
    return joblib.load(model_path)


def predict(model: Any, features: pd.DataFrame) -> pd.Series:
    """Run inference and return predictions as a pandas series."""
    predictions = model.predict(features)
    return pd.Series(predictions, index=features.index, name="prediction")
