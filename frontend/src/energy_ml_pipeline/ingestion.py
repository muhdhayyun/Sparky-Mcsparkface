"""Raw dataset ingestion and normalization utilities."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from energy_ml_pipeline.preprocessing import clean_column_names


TIMESTAMP_CANDIDATES = (
    "timestamp",
    "datetime",
    "date_time",
    "reading_time",
    "timestamp_dd_mm_yyyy_hh_mm_ss",
)

ENERGY_CANDIDATES = (
    "energy_wh",
    "energy",
    "reading",
    "usage",
    "consumption",
    "kwh",
    "wh",
)


def _find_first_matching_column(columns: list[str], candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def _normalize_meter_frame(file_path: Path) -> pd.DataFrame:
    """Read and standardize a raw meter file into a shared schema."""
    df = pd.read_csv(file_path)
    df = clean_column_names(df)

    timestamp_column = _find_first_matching_column(df.columns.tolist(), TIMESTAMP_CANDIDATES)
    energy_column = _find_first_matching_column(df.columns.tolist(), ENERGY_CANDIDATES)

    if timestamp_column is None:
        raise ValueError(f"Could not find a timestamp column in {file_path.name}")
    if energy_column is None:
        raise ValueError(f"Could not find an energy column in {file_path.name}")

    standardized = df.rename(
        columns={
            timestamp_column: "timestamp",
            energy_column: "energy_wh",
        }
    ).copy()

    standardized["timestamp"] = pd.to_datetime(
        standardized["timestamp"],
        errors="coerce",
        dayfirst=True,
    )
    standardized["energy_wh"] = pd.to_numeric(standardized["energy_wh"], errors="coerce")
    standardized["meter_id"] = file_path.stem
    standardized["source_file"] = file_path.name
    standardized["unit"] = "Wh"

    standardized = standardized.dropna(subset=["timestamp", "energy_wh"]).sort_values("timestamp")
    standardized = standardized.reset_index(drop=True)
    return standardized


def prepare_raw_data(
    input_dir: str | Path,
    output_dir: str | Path,
    output_filename: str = "smart_meter_combined.csv",
) -> tuple[pd.DataFrame, Path]:
    """Prepare all raw CSV files in a directory and save a merged processed dataset."""
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(input_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {input_dir}")

    prepared_frames = [_normalize_meter_frame(file_path) for file_path in csv_files]
    combined = pd.concat(prepared_frames, ignore_index=True)
    combined = combined.sort_values(["meter_id", "timestamp"]).reset_index(drop=True)

    output_path = output_dir / output_filename
    combined.to_csv(output_path, index=False)
    return combined, output_path
