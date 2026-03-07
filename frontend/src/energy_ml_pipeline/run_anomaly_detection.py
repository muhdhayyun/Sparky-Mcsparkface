"""Anomaly detection entrypoint for the combined smart meter dataset."""

from __future__ import annotations

import pandas as pd

from energy_ml_pipeline.anomaly_detection import detect_anomalies, save_anomaly_outputs
from energy_ml_pipeline.config import PipelineConfig
from energy_ml_pipeline.utils import get_logger


def main() -> None:
    """Run anomaly detection against the processed combined dataset."""
    logger = get_logger("energy_ml_pipeline.run_anomaly_detection")
    config = PipelineConfig()
    df = pd.read_csv(config.processed_dataset_path)
    anomalies, summary = detect_anomalies(
        df,
        contamination=config.anomaly_contamination,
        random_state=config.random_seed,
    )
    outputs = save_anomaly_outputs(anomalies, summary, config.output_dir / "anomalies")

    logger.info("Detected %s anomalies", summary["anomaly_count"])
    logger.info("Anomaly file saved to %s", outputs["anomalies"])


if __name__ == "__main__":
    main()
