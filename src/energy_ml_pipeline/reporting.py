"""Reporting utilities for smart meter insights."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from energy_ml_pipeline.utils import save_json


def build_reporting_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add calendar fields used by downstream reporting summaries."""
    report_df = df.copy()
    report_df["timestamp"] = pd.to_datetime(report_df["timestamp"], errors="coerce")
    report_df = report_df.dropna(subset=["timestamp"])
    report_df["date"] = report_df["timestamp"].dt.date
    report_df["hour"] = report_df["timestamp"].dt.hour
    report_df["weekday"] = report_df["timestamp"].dt.day_name()
    report_df["month"] = report_df["timestamp"].dt.to_period("M").astype(str)
    return report_df


def generate_meter_report(df: pd.DataFrame) -> dict[str, Any]:
    """Generate product-facing reporting summaries from the combined dataset."""
    report_df = build_reporting_features(df)

    per_meter_summary = (
        report_df.groupby("meter_id")["energy_wh"]
        .agg(total_energy_wh="sum", average_energy_wh="mean", min_energy_wh="min", max_energy_wh="max", readings="count")
        .sort_values("total_energy_wh", ascending=False)
    )
    daily_usage = (
        report_df.groupby(["meter_id", "date"], as_index=False)["energy_wh"].sum().rename(columns={"energy_wh": "daily_energy_wh"})
    )
    peak_hour_usage = (
        report_df.groupby("hour", as_index=False)["energy_wh"].mean().rename(columns={"energy_wh": "average_energy_wh"})
    )
    weekday_usage = (
        report_df.groupby("weekday", as_index=False)["energy_wh"].mean().rename(columns={"energy_wh": "average_energy_wh"})
    )
    top_meters = per_meter_summary.head(10).reset_index()

    return {
        "overview": {
            "meter_count": int(report_df["meter_id"].nunique()),
            "row_count": int(len(report_df)),
            "date_range": {
                "start": str(report_df["timestamp"].min()),
                "end": str(report_df["timestamp"].max()),
            },
        },
        "per_meter_summary": per_meter_summary.reset_index(),
        "daily_usage": daily_usage,
        "peak_hour_usage": peak_hour_usage.sort_values("average_energy_wh", ascending=False),
        "weekday_usage": weekday_usage,
        "top_meters": top_meters,
    }


def save_reporting_outputs(report: dict[str, Any], output_dir: str | Path) -> dict[str, Path]:
    """Persist report tables and metadata to disk."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    paths: dict[str, Path] = {}
    for key in ("per_meter_summary", "daily_usage", "peak_hour_usage", "weekday_usage", "top_meters"):
        output_path = output_dir / f"{key}.csv"
        report[key].to_csv(output_path, index=False)
        paths[key] = output_path

    summary_payload = {
        "overview": report["overview"],
        "generated_files": {key: str(path) for key, path in paths.items()},
    }
    paths["summary"] = save_json(summary_payload, output_dir / "report_summary.json")
    return paths
