"""Reporting entrypoint for the prepared smart meter dataset."""

from __future__ import annotations

import pandas as pd

from energy_ml_pipeline.config import PipelineConfig
from energy_ml_pipeline.reporting import generate_meter_report, save_reporting_outputs
from energy_ml_pipeline.utils import get_logger


def main() -> None:
    """Generate user-facing reporting artifacts from the combined dataset."""
    logger = get_logger("energy_ml_pipeline.run_reporting")
    config = PipelineConfig()
    df = pd.read_csv(config.processed_dataset_path)
    report = generate_meter_report(df)
    outputs = save_reporting_outputs(report, config.output_dir / "reports")

    logger.info("Reporting complete for %s meters", report["overview"]["meter_count"])
    logger.info("Top meter report saved to %s", outputs["top_meters"])


if __name__ == "__main__":
    main()
