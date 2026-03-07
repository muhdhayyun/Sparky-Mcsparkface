"""Main entrypoint for the end-to-end machine learning pipeline."""

from __future__ import annotations

from energy_ml_pipeline.config import PipelineConfig
from energy_ml_pipeline.data_loader import load_dataset
from energy_ml_pipeline.eda import run_basic_eda
from energy_ml_pipeline.evaluation import evaluate_regression_model
from energy_ml_pipeline.feature_engineering import run_feature_engineering
from energy_ml_pipeline.inference import save_model
from energy_ml_pipeline.preprocessing import (
    build_preprocessing_pipeline,
    clean_column_names,
    extract_datetime_features,
    handle_missing_values,
    infer_feature_types,
)
from energy_ml_pipeline.splitting import (
    split_time_series_holdout,
    split_train_test,
    split_train_validation_test,
)
from energy_ml_pipeline.training import build_training_pipeline, get_model, train_model
from energy_ml_pipeline.utils import get_logger, save_json


def run_pipeline(config: PipelineConfig) -> dict[str, object]:
    """Execute the full ML workflow from loading data to persisting artifacts."""
    logger = get_logger()
    config.ensure_directories()

    logger.info("Loading dataset from %s", config.dataset_path)
    df = load_dataset(config.dataset_path)
    df = clean_column_names(df)

    if config.target_column not in df.columns:
        raise ValueError(f"Target column '{config.target_column}' not found in dataset.")

    logger.info("Running automated EDA")
    eda_summary = run_basic_eda(
        df=df,
        output_dir=config.output_dir / "eda",
        timestamp_column=config.timestamp_column,
        target_column=config.target_column,
    )
    save_json(eda_summary, config.output_dir / "eda" / "eda_summary.json")

    logger.info("Applying preprocessing and feature engineering")
    df = extract_datetime_features(df, config.timestamp_column)
    df = handle_missing_values(df)

    if config.use_time_series_split and config.timestamp_column and config.timestamp_column in df.columns:
        df = df.sort_values(config.timestamp_column).reset_index(drop=True)

    categorical_columns, numeric_columns = infer_feature_types(
        df=df,
        target_column=config.target_column,
        timestamp_column=config.timestamp_column,
    )
    df = run_feature_engineering(
        df=df,
        usage_column=config.usage_feature_column,
        timestamp_column=config.timestamp_column,
        group_column=config.group_column,
        numeric_columns=numeric_columns,
    )

    categorical_columns, numeric_columns = infer_feature_types(
        df=df,
        target_column=config.target_column,
        timestamp_column=config.timestamp_column,
    )
    feature_columns = config.feature_columns or [*numeric_columns, *categorical_columns]

    X = df[feature_columns].copy()
    y = df[config.target_column].copy()

    logger.info("Splitting dataset")
    if config.use_time_series_split and config.timestamp_column and config.timestamp_column in df.columns:
        split_data = split_time_series_holdout(
            X=X,
            y=y,
            test_size=config.test_size,
            validation_size=config.validation_size,
        )
    elif config.validation_size:
        split_data = split_train_validation_test(
            X=X,
            y=y,
            test_size=config.test_size,
            validation_size=config.validation_size,
            random_seed=config.random_seed,
        )
    else:
        split_data = split_train_test(
            X=X,
            y=y,
            test_size=config.test_size,
            random_seed=config.random_seed,
        )

    logger.info("Training %s model", config.model_name)
    preprocessor = build_preprocessing_pipeline(
        numeric_columns=[column for column in numeric_columns if column in feature_columns],
        categorical_columns=[column for column in categorical_columns if column in feature_columns],
    )
    model = get_model(config.model_name, config.model_params)
    training_pipeline = build_training_pipeline(preprocessor=preprocessor, model=model)
    trained_pipeline = train_model(training_pipeline, split_data.X_train, split_data.y_train)

    logger.info("Evaluating model")
    evaluation_results = evaluate_regression_model(
        pipeline=trained_pipeline,
        X_test=split_data.X_test,
        y_test=split_data.y_test,
        output_dir=config.output_dir / "evaluation",
    )
    save_json(evaluation_results, config.output_dir / "evaluation" / "metrics.json")

    model_path = save_model(trained_pipeline, config.model_dir / config.model_filename)
    logger.info("Saved trained model to %s", model_path)

    return {
        "eda_summary": eda_summary,
        "evaluation_results": evaluation_results,
        "model_path": model_path,
    }


if __name__ == "__main__":
    run_pipeline(PipelineConfig())
