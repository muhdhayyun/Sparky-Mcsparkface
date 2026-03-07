"""Forecasting entrypoint for the combined smart meter dataset."""

from __future__ import annotations

import pandas as pd

from energy_ml_pipeline.config import PipelineConfig
from energy_ml_pipeline.forecasting import run_forecasting_baseline, save_forecasting_outputs
from energy_ml_pipeline.utils import get_logger


def main() -> None:
    """Train and evaluate a baseline forecasting model on the combined dataset."""
    logger = get_logger("energy_ml_pipeline.run_forecasting")
    config = PipelineConfig(
        model_name="lightgbm",
        group_column="meter_id",
        usage_feature_column="energy_wh",
        target_column="energy_wh",
        timestamp_column="timestamp",
        use_time_series_split=True,
    )
    df = pd.read_csv(config.processed_dataset_path)
    results = run_forecasting_baseline(df, config)
    outputs = save_forecasting_outputs(
        results,
        output_dir=config.output_dir / "forecasting",
        model_path=config.model_dir / "forecasting_model.joblib",
    )

    logger.info("Forecasting complete with RMSE %.3f", results["metrics"]["rmse"])
    logger.info("Forecast predictions saved to %s", outputs["predictions"])


if __name__ == "__main__":
    main()
