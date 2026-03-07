"""Batch data preparation entrypoint for raw smart meter CSV files."""

from __future__ import annotations

from energy_ml_pipeline.config import PipelineConfig
from energy_ml_pipeline.ingestion import prepare_raw_data
from energy_ml_pipeline.utils import get_logger


def main() -> None:
    """Normalize raw CSV files into a single processed dataset."""
    logger = get_logger("energy_ml_pipeline.prepare_data")
    config = PipelineConfig()

    prepared_df, output_path = prepare_raw_data(
        input_dir=config.dataset_path.parent,
        output_dir=config.output_dir.parent / "data" / "processed",
    )
    logger.info("Prepared %s rows across %s columns", len(prepared_df), len(prepared_df.columns))
    logger.info("Saved processed dataset to %s", output_path)


if __name__ == "__main__":
    main()
