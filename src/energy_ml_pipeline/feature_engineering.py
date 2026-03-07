"""Feature engineering utilities and domain-specific placeholders."""

from __future__ import annotations

import pandas as pd


def add_rolling_features(
    df: pd.DataFrame,
    value_column: str,
    group_column: str | None = None,
    windows: tuple[int, ...] = (3, 6, 24),
) -> pd.DataFrame:
    """Add rolling average features for grouped or global time-series data."""
    if value_column not in df.columns:
        return df

    engineered = df.copy()
    if group_column and group_column in engineered.columns:
        grouped = engineered.groupby(group_column)[value_column]
        for window in windows:
            engineered[f"{value_column}_rolling_mean_{window}"] = grouped.transform(
                lambda series: series.rolling(window=window, min_periods=1).mean()
            )
    else:
        for window in windows:
            engineered[f"{value_column}_rolling_mean_{window}"] = (
                engineered[value_column].rolling(window=window, min_periods=1).mean()
            )
    return engineered


def add_lag_features(
    df: pd.DataFrame,
    value_column: str,
    group_column: str | None = None,
    lags: tuple[int, ...] = (1, 2, 24),
) -> pd.DataFrame:
    """Add lag features to capture temporal dependencies."""
    if value_column not in df.columns:
        return df

    engineered = df.copy()
    if group_column and group_column in engineered.columns:
        grouped = engineered.groupby(group_column)[value_column]
        for lag in lags:
            engineered[f"{value_column}_lag_{lag}"] = grouped.shift(lag)
    else:
        for lag in lags:
            engineered[f"{value_column}_lag_{lag}"] = engineered[value_column].shift(lag)
    return engineered


def add_interaction_features(df: pd.DataFrame, numeric_columns: list[str]) -> pd.DataFrame:
    """Add a minimal set of pairwise interaction placeholders."""
    engineered = df.copy()
    if len(numeric_columns) < 2:
        return engineered

    first, second = numeric_columns[:2]
    engineered[f"{first}_x_{second}"] = engineered[first] * engineered[second]
    return engineered


def add_energy_specific_features(
    df: pd.DataFrame, timestamp_column: str | None = None, usage_column: str | None = None
) -> pd.DataFrame:
    """Add smart-meter features such as peak-hour and off-peak indicators."""
    engineered = df.copy()
    if timestamp_column and timestamp_column in engineered.columns:
        ts = pd.to_datetime(engineered[timestamp_column], errors="coerce")
        hour = ts.dt.hour
        engineered["is_peak_hour"] = hour.isin([7, 8, 9, 18, 19, 20]).astype("Int64")
        engineered["is_off_peak_hour"] = hour.isin([0, 1, 2, 3, 4, 5]).astype("Int64")

    if usage_column and usage_column in engineered.columns:
        median_usage = engineered[usage_column].median()
        engineered["high_usage_flag"] = (engineered[usage_column] > median_usage).astype("Int64")

    return engineered


def run_feature_engineering(
    df: pd.DataFrame,
    usage_column: str | None = None,
    timestamp_column: str | None = None,
    group_column: str | None = None,
    numeric_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Apply a sequence of generic and domain-aware feature engineering steps."""
    numeric_columns = numeric_columns or []
    engineered = df.copy()
    if usage_column and usage_column in engineered.columns:
        engineered = add_rolling_features(engineered, value_column=usage_column, group_column=group_column)
        engineered = add_lag_features(engineered, value_column=usage_column, group_column=group_column)
    engineered = add_interaction_features(engineered, numeric_columns=numeric_columns)
    engineered = add_energy_specific_features(
        engineered,
        timestamp_column=timestamp_column,
        usage_column=usage_column,
    )
    return engineered
