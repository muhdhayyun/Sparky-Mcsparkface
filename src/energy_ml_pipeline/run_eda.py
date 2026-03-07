"""EDA entrypoint for the prepared smart meter dataset."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from energy_ml_pipeline.eda import run_basic_eda
from energy_ml_pipeline.utils import get_logger, save_json


def build_meter_level_summary(df: pd.DataFrame) -> dict[str, object]:
    """Create meter-level summary statistics for the combined dataset."""
    summary: dict[str, object] = {
        "meter_count": int(df["meter_id"].nunique()) if "meter_id" in df.columns else 0,
        "date_range": {
            "start": str(df["timestamp"].min()) if "timestamp" in df.columns else None,
            "end": str(df["timestamp"].max()) if "timestamp" in df.columns else None,
        },
    }

    if {"meter_id", "energy_wh"}.issubset(df.columns):
        per_meter = (
            df.groupby("meter_id")["energy_wh"]
            .agg(["count", "mean", "min", "max", "sum"])
            .sort_values("sum", ascending=False)
        )
        summary["per_meter_summary"] = per_meter.to_dict(orient="index")

    return summary


def run_combined_dataset_eda(
    combined_path: str | Path,
    output_dir: str | Path,
) -> dict[str, object]:
    """Run EDA for the prepared combined smart meter dataset."""
    combined_path = Path(combined_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(combined_path)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    basic_eda = run_basic_eda(
        df=df,
        output_dir=output_dir,
        timestamp_column="timestamp" if "timestamp" in df.columns else None,
        target_column="energy_wh" if "energy_wh" in df.columns else None,
    )
    meter_summary = build_meter_level_summary(df)

    results = {
        "dataset_path": str(combined_path),
        "basic_eda": basic_eda,
        "meter_summary": meter_summary,
    }
    save_json(results, output_dir / "eda_summary.json")
    return results


def main() -> None:
    """Run EDA for `data/processed/smart_meter_combined.csv`."""
    logger = get_logger("energy_ml_pipeline.run_eda")
    project_root = Path(__file__).resolve().parents[2]
    combined_path = project_root / "data" / "processed" / "smart_meter_combined.csv"
    output_dir = project_root / "outputs" / "eda"

    results = run_combined_dataset_eda(combined_path=combined_path, output_dir=output_dir)
    logger.info("EDA complete for %s", results["dataset_path"])
    logger.info("EDA artifacts saved to %s", output_dir)


if __name__ == "__main__":
    main()
