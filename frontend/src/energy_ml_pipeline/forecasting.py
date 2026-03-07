"""Baseline forecasting utilities for smart meter energy consumption."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from energy_ml_pipeline.config import PipelineConfig
from energy_ml_pipeline.evaluation import compute_regression_metrics
from energy_ml_pipeline.preprocessing import build_preprocessing_pipeline
from energy_ml_pipeline.training import build_training_pipeline, get_model, train_model
from energy_ml_pipeline.utils import save_json


def build_forecasting_dataset(df: pd.DataFrame, horizon: int = 1) -> pd.DataFrame:
    """Create a supervised learning table for next-interval forecasting."""
    forecast_df = df.copy()
    forecast_df["timestamp"] = pd.to_datetime(forecast_df["timestamp"], errors="coerce")
    forecast_df = forecast_df.dropna(subset=["timestamp", "energy_wh"]).sort_values(["meter_id", "timestamp"])

    grouped = forecast_df.groupby("meter_id")["energy_wh"]
    forecast_df["lag_1"] = grouped.shift(1)
    forecast_df["lag_2"] = grouped.shift(2)
    forecast_df["lag_48"] = grouped.shift(48)
    forecast_df["rolling_mean_6"] = grouped.transform(lambda series: series.shift(1).rolling(6, min_periods=1).mean())
    forecast_df["rolling_mean_48"] = grouped.transform(lambda series: series.shift(1).rolling(48, min_periods=1).mean())

    forecast_df["hour"] = forecast_df["timestamp"].dt.hour
    forecast_df["day"] = forecast_df["timestamp"].dt.day
    forecast_df["month"] = forecast_df["timestamp"].dt.month
    forecast_df["weekday"] = forecast_df["timestamp"].dt.weekday

    forecast_df["target_next"] = grouped.shift(-horizon)
    forecast_df = forecast_df.dropna(
        subset=["lag_1", "lag_2", "lag_48", "rolling_mean_6", "rolling_mean_48", "target_next"]
    ).reset_index(drop=True)
    return forecast_df


def run_forecasting_baseline(
    df: pd.DataFrame,
    config: PipelineConfig,
) -> dict[str, Any]:
    """Train and evaluate a chronological next-interval forecasting baseline."""
    forecast_df = build_forecasting_dataset(df, horizon=config.forecast_horizon)
    feature_columns = [
        "meter_id",
        "hour",
        "day",
        "month",
        "weekday",
        "lag_1",
        "lag_2",
        "lag_48",
        "rolling_mean_6",
        "rolling_mean_48",
    ]

    X = forecast_df[feature_columns].copy()
    y = forecast_df["target_next"].copy()

    split_index = int(len(forecast_df) * (1 - config.test_size))
    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]
    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]
    test_metadata = forecast_df.iloc[split_index:][["timestamp", "meter_id", "energy_wh", "target_next"]].copy()

    preprocessor = build_preprocessing_pipeline(
        numeric_columns=["hour", "day", "month", "weekday", "lag_1", "lag_2", "lag_48", "rolling_mean_6", "rolling_mean_48"],
        categorical_columns=["meter_id"],
    )
    model = get_model(config.model_name, config.model_params)
    pipeline = build_training_pipeline(preprocessor, model)
    trained_pipeline = train_model(pipeline, X_train, y_train)

    predictions = trained_pipeline.predict(X_test)
    metrics = compute_regression_metrics(y_test, predictions)

    prediction_frame = test_metadata.copy()
    prediction_frame["predicted_next_energy_wh"] = predictions
    prediction_frame["absolute_error"] = (prediction_frame["target_next"] - prediction_frame["predicted_next_energy_wh"]).abs()

    return {
        "metrics": metrics,
        "prediction_frame": prediction_frame,
        "trained_pipeline": trained_pipeline,
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
    }


def save_forecasting_outputs(results: dict[str, Any], output_dir: str | Path, model_path: str | Path) -> dict[str, Path]:
    """Persist baseline forecasting artifacts to disk."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)

    predictions_path = output_dir / "forecast_predictions.csv"
    results["prediction_frame"].to_csv(predictions_path, index=False)

    metrics_payload = {
        "metrics": results["metrics"],
        "train_rows": results["train_rows"],
        "test_rows": results["test_rows"],
    }
    metrics_path = save_json(metrics_payload, output_dir / "forecast_metrics.json")
    joblib.dump(results["trained_pipeline"], model_path)

    return {
        "predictions": predictions_path,
        "metrics": metrics_path,
        "model": model_path,
    }
