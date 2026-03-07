"""Dataset loading utilities."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_dataset(path: str | Path, **kwargs: object) -> pd.DataFrame:
    """Load a dataset from disk based on the file extension."""
    dataset_path = Path(path)
    suffix = dataset_path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(dataset_path, **kwargs)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(dataset_path, **kwargs)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(dataset_path, **kwargs)

    raise ValueError(f"Unsupported dataset format: {suffix}")
