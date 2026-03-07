"""Central configuration objects for the machine learning pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"


@dataclass(slots=True)
class PipelineConfig:
    """Runtime configuration for the end-to-end training pipeline."""

    dataset_path: Path = RAW_DATA_DIR / "smart_meter_data.csv"
    target_column: str = "target"
    timestamp_column: str | None = "timestamp"
    group_column: str | None = None
    usage_feature_column: str | None = None
    categorical_columns: list[str] = field(default_factory=list)
    numeric_columns: list[str] = field(default_factory=list)
    feature_columns: list[str] | None = None
    model_name: str = "lightgbm"
    task_type: str = "regression"
    test_size: float = 0.2
    validation_size: float | None = 0.1
    random_seed: int = 42
    use_time_series_split: bool = False
    time_series_splits: int = 5
    output_dir: Path = OUTPUTS_DIR
    model_dir: Path = MODELS_DIR
    model_filename: str = "trained_model.joblib"
    eda_sample_size: int = 10000
    model_params: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "lightgbm": {
                "n_estimators": 300,
                "learning_rate": 0.05,
                "num_leaves": 31,
                "subsample": 0.9,
                "colsample_bytree": 0.9,
                "random_state": 42,
            },
            "random_forest": {
                "n_estimators": 300,
                "max_depth": None,
                "min_samples_split": 2,
                "min_samples_leaf": 1,
                "random_state": 42,
                "n_jobs": -1,
            },
            "linear_regression": {},
        }
    )

    def ensure_directories(self) -> None:
        """Create output directories required by the pipeline."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.model_dir.mkdir(parents=True, exist_ok=True)
