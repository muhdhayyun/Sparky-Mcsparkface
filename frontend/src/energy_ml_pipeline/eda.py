"""Reusable exploratory data analysis utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


sns.set_theme(style="whitegrid")


def summarize_dataset(df: pd.DataFrame) -> dict[str, Any]:
    """Return a generic summary for any dataframe."""
    return {
        "shape": df.shape,
        "column_types": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isna().sum().sort_values(ascending=False).to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "descriptive_statistics": df.describe(include="all", datetime_is_numeric=True).transpose(),
    }


def compute_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Compute a correlation matrix for numeric columns."""
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty:
        return pd.DataFrame()
    return numeric_df.corr(numeric_only=True)


def plot_correlation_matrix(df: pd.DataFrame, output_path: str | Path) -> Path | None:
    """Save a correlation heatmap when numeric columns exist."""
    corr = compute_correlation_matrix(df)
    if corr.empty:
        return None

    output_path = Path(output_path)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, cmap="coolwarm", center=0, ax=ax)
    ax.set_title("Correlation Matrix")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_distributions(
    df: pd.DataFrame, output_dir: str | Path, max_columns: int = 8
) -> list[Path]:
    """Save distribution plots for numeric columns."""
    output_dir = Path(output_dir)
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()[:max_columns]
    saved_paths: list[Path] = []

    for column in numeric_columns:
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.histplot(df[column].dropna(), kde=True, ax=ax)
        ax.set_title(f"Distribution: {column}")
        ax.set_xlabel(column)
        output_path = output_dir / f"distribution_{column}.png"
        fig.tight_layout()
        fig.savefig(output_path, dpi=150)
        plt.close(fig)
        saved_paths.append(output_path)

    return saved_paths


def plot_time_series(
    df: pd.DataFrame,
    timestamp_column: str,
    value_column: str | None,
    output_path: str | Path,
) -> Path | None:
    """Save a time-series plot if a timestamp column exists."""
    if timestamp_column not in df.columns:
        return None

    plot_df = df.copy()
    plot_df[timestamp_column] = pd.to_datetime(plot_df[timestamp_column], errors="coerce")
    plot_df = plot_df.dropna(subset=[timestamp_column]).sort_values(timestamp_column)
    if plot_df.empty:
        return None

    if value_column and value_column in plot_df.columns:
        value_series = plot_df[value_column]
        title = f"Time Series: {value_column}"
        y_label = value_column
    else:
        value_series = pd.Series(range(len(plot_df)), index=plot_df.index)
        title = "Observation Count Over Time"
        y_label = "row_index"

    output_path = Path(output_path)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(plot_df[timestamp_column], value_series)
    ax.set_title(title)
    ax.set_xlabel(timestamp_column)
    ax.set_ylabel(y_label)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def run_basic_eda(
    df: pd.DataFrame,
    output_dir: str | Path,
    timestamp_column: str | None = None,
    target_column: str | None = None,
) -> dict[str, Any]:
    """Execute standard automated EDA and save generated artifacts."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = summarize_dataset(df)
    correlation_path = plot_correlation_matrix(df, output_dir / "correlation_matrix.png")
    distribution_paths = plot_distributions(df, output_dir)
    time_series_path = None

    if timestamp_column:
        time_series_path = plot_time_series(
            df=df,
            timestamp_column=timestamp_column,
            value_column=target_column,
            output_path=output_dir / "time_series.png",
        )

    summary["correlation_path"] = correlation_path
    summary["distribution_paths"] = distribution_paths
    summary["time_series_path"] = time_series_path
    return summary
