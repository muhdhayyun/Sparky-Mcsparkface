"""Anomaly detection utilities for smart meter data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.ensemble import IsolationForest

from energy_ml_pipeline.utils import save_json


def build_anomaly_features(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare numeric anomaly-detection features from the combined dataset."""
    anomaly_df = df.copy()
    anomaly_df["timestamp"] = pd.to_datetime(anomaly_df["timestamp"], errors="coerce")
    anomaly_df = anomaly_df.dropna(subset=["timestamp", "energy_wh"])
    anomaly_df["hour"] = anomaly_df["timestamp"].dt.hour
    anomaly_df["weekday"] = anomaly_df["timestamp"].dt.weekday
    anomaly_df["month"] = anomaly_df["timestamp"].dt.month
    return anomaly_df


def detect_anomalies(
    df: pd.DataFrame,
    contamination: float = 0.01,
    random_state: int = 42,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Flag unusual smart-meter readings with Isolation Forest."""
    anomaly_df = build_anomaly_features(df)
    feature_frame = anomaly_df[["energy_wh", "hour", "weekday", "month"]]

    model = IsolationForest(contamination=contamination, random_state=random_state)
    predictions = model.fit_predict(feature_frame)
    anomaly_scores = model.decision_function(feature_frame)

    anomaly_df["anomaly_flag"] = predictions == -1
    anomaly_df["anomaly_score"] = anomaly_scores
    flagged = anomaly_df[anomaly_df["anomaly_flag"]].copy()
    flagged = flagged.sort_values("anomaly_score")

    summary = {
        "row_count": int(len(anomaly_df)),
        "anomaly_count": int(len(flagged)),
        "anomaly_ratio": float(len(flagged) / len(anomaly_df)) if len(anomaly_df) else 0.0,
        "meters_with_anomalies": int(flagged["meter_id"].nunique()) if not flagged.empty else 0,
    }
    return flagged, summary


def save_anomaly_outputs(
    anomalies: pd.DataFrame,
    summary: dict[str, Any],
    output_dir: str | Path,
) -> dict[str, Path]:
    """Save anomaly results and summary to disk."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    anomaly_path = output_dir / "anomalies.csv"
    anomalies.to_csv(anomaly_path, index=False)
    summary_path = save_json(summary, output_dir / "anomaly_summary.json")
    return {"anomalies": anomaly_path, "summary": summary_path}
