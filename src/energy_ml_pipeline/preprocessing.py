"""Preprocessing helpers for dataset cleaning and transformation."""

from __future__ import annotations

import re
from typing import Iterable

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize dataframe column names into snake_case."""
    cleaned = df.copy()
    cleaned.columns = [
        re.sub(r"[^0-9a-zA-Z]+", "_", column.strip()).strip("_").lower() for column in cleaned.columns
    ]
    return cleaned


def infer_feature_types(
    df: pd.DataFrame, target_column: str, timestamp_column: str | None = None
) -> tuple[list[str], list[str]]:
    """Infer categorical and numeric feature columns from a dataframe."""
    excluded = {target_column}
    if timestamp_column:
        excluded.add(timestamp_column)

    feature_df = df.drop(columns=[col for col in excluded if col in df.columns])
    categorical_columns = feature_df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    numeric_columns = feature_df.select_dtypes(include=["number"]).columns.tolist()
    return categorical_columns, numeric_columns


def extract_datetime_features(df: pd.DataFrame, timestamp_column: str | None) -> pd.DataFrame:
    """Create hour/day/month/weekday features from a timestamp column."""
    if not timestamp_column or timestamp_column not in df.columns:
        return df

    enriched = df.copy()
    enriched[timestamp_column] = pd.to_datetime(enriched[timestamp_column], errors="coerce")
    enriched[f"{timestamp_column}_hour"] = enriched[timestamp_column].dt.hour
    enriched[f"{timestamp_column}_day"] = enriched[timestamp_column].dt.day
    enriched[f"{timestamp_column}_month"] = enriched[timestamp_column].dt.month
    enriched[f"{timestamp_column}_weekday"] = enriched[timestamp_column].dt.weekday
    return enriched


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Apply simple default missing-value handling at dataframe level."""
    processed = df.copy()
    for column in processed.select_dtypes(include=["number"]).columns:
        processed[column] = processed[column].fillna(processed[column].median())
    for column in processed.select_dtypes(include=["object", "category", "bool"]).columns:
        processed[column] = processed[column].fillna("unknown")
    return processed


def build_preprocessing_pipeline(
    numeric_columns: Iterable[str], categorical_columns: Iterable[str]
) -> ColumnTransformer:
    """Build a scikit-learn preprocessing transformer."""
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, list(numeric_columns)),
            ("categorical", categorical_pipeline, list(categorical_columns)),
        ],
        remainder="drop",
    )
