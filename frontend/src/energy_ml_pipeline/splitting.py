"""Reusable dataset splitting utilities."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.model_selection import TimeSeriesSplit, train_test_split


@dataclass(slots=True)
class SplitData:
    """Container for split datasets."""

    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    X_val: pd.DataFrame | None = None
    y_val: pd.Series | None = None


def split_train_test(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float,
    random_seed: int,
) -> SplitData:
    """Create a standard shuffled train/test split."""
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_seed,
    )
    return SplitData(X_train=X_train, X_test=X_test, y_train=y_train, y_test=y_test)


def split_train_validation_test(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float,
    validation_size: float,
    random_seed: int,
) -> SplitData:
    """Create train/validation/test datasets from a single dataframe."""
    initial_split = split_train_test(X, y, test_size=test_size, random_seed=random_seed)
    relative_validation_size = validation_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        initial_split.X_train,
        initial_split.y_train,
        test_size=relative_validation_size,
        random_state=random_seed,
    )
    return SplitData(
        X_train=X_train,
        X_val=X_val,
        X_test=initial_split.X_test,
        y_train=y_train,
        y_val=y_val,
        y_test=initial_split.y_test,
    )


def build_time_series_split(n_splits: int) -> TimeSeriesSplit:
    """Build a time-aware cross-validation splitter."""
    return TimeSeriesSplit(n_splits=n_splits)


def split_time_series_holdout(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float,
    validation_size: float | None = None,
) -> SplitData:
    """Create chronological holdout splits for timestamp-ordered datasets."""
    n_rows = len(X)
    test_count = max(1, int(n_rows * test_size))
    test_start = n_rows - test_count

    X_train_full = X.iloc[:test_start]
    y_train_full = y.iloc[:test_start]
    X_test = X.iloc[test_start:]
    y_test = y.iloc[test_start:]

    if validation_size:
        validation_count = max(1, int(n_rows * validation_size))
        validation_start = max(1, len(X_train_full) - validation_count)
        X_train = X_train_full.iloc[:validation_start]
        y_train = y_train_full.iloc[:validation_start]
        X_val = X_train_full.iloc[validation_start:]
        y_val = y_train_full.iloc[validation_start:]
        return SplitData(
            X_train=X_train,
            X_val=X_val,
            X_test=X_test,
            y_train=y_train,
            y_val=y_val,
            y_test=y_test,
        )

    return SplitData(X_train=X_train_full, X_test=X_test, y_train=y_train_full, y_test=y_test)
