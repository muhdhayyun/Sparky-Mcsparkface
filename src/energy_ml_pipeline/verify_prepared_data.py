"""Verification entrypoint for the merged smart meter dataset."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from energy_ml_pipeline.config import PipelineConfig
from energy_ml_pipeline.preprocessing import clean_column_names
from energy_ml_pipeline.utils import get_logger


def verify_prepared_data(
    raw_dir: str | Path,
    combined_path: str | Path,
) -> dict[str, object]:
    """Verify that the combined dataset contains all expected raw file data."""
    raw_dir = Path(raw_dir)
    combined_path = Path(combined_path)

    if not combined_path.exists():
        raise FileNotFoundError(f"Combined dataset not found: {combined_path}")

    raw_files = sorted(raw_dir.glob("*.csv"))
    if not raw_files:
        raise FileNotFoundError(f"No raw CSV files found in {raw_dir}")

    combined_df = pd.read_csv(combined_path)
    expected_columns = {"timestamp", "energy_wh", "meter_id", "source_file", "unit"}
    missing_columns = expected_columns.difference(combined_df.columns)
    if missing_columns:
        raise ValueError(f"Combined dataset is missing columns: {sorted(missing_columns)}")

    raw_file_count = len(raw_files)
    combined_file_count = combined_df["source_file"].nunique()
    per_file_results: list[dict[str, object]] = []

    for raw_file in raw_files:
        raw_df = pd.read_csv(raw_file)
        raw_df = clean_column_names(raw_df)
        expected_row_count = len(raw_df)
        combined_subset = combined_df[combined_df["source_file"] == raw_file.name]
        combined_row_count = len(combined_subset)

        per_file_results.append(
            {
                "source_file": raw_file.name,
                "meter_id": raw_file.stem,
                "raw_rows": expected_row_count,
                "combined_rows": combined_row_count,
                "row_count_match": expected_row_count == combined_row_count,
                "present_in_combined": combined_row_count > 0,
            }
        )

    all_present = all(item["present_in_combined"] for item in per_file_results)
    all_counts_match = all(item["row_count_match"] for item in per_file_results)

    return {
        "raw_file_count": raw_file_count,
        "combined_source_file_count": int(combined_file_count),
        "all_present": all_present,
        "all_counts_match": all_counts_match,
        "total_combined_rows": int(len(combined_df)),
        "per_file_results": per_file_results,
    }


def main() -> None:
    """Run verification against the default raw and processed dataset paths."""
    logger = get_logger("energy_ml_pipeline.verify_prepared_data")
    config = PipelineConfig()
    combined_path = config.output_dir.parent / "data" / "processed" / "smart_meter_combined.csv"

    results = verify_prepared_data(
        raw_dir=config.dataset_path.parent,
        combined_path=combined_path,
    )

    logger.info("Raw files found: %s", results["raw_file_count"])
    logger.info("Files represented in combined dataset: %s", results["combined_source_file_count"])
    logger.info("All files present: %s", results["all_present"])
    logger.info("All row counts match: %s", results["all_counts_match"])

    for item in results["per_file_results"]:
        logger.info(
            "%s | present=%s | raw_rows=%s | combined_rows=%s",
            item["source_file"],
            item["present_in_combined"],
            item["raw_rows"],
            item["combined_rows"],
        )


if __name__ == "__main__":
    main()
