from pathlib import Path

import pandas as pd

from energy_ml_pipeline.run_eda import run_combined_dataset_eda


def test_run_combined_dataset_eda_creates_summary_file(tmp_path: Path) -> None:
    combined_path = tmp_path / "smart_meter_combined.csv"
    output_dir = tmp_path / "eda"

    pd.DataFrame(
        {
            "timestamp": ["2025-01-01 00:00:00", "2025-01-01 00:30:00"],
            "energy_wh": [100, 120],
            "meter_id": ["meter_a", "meter_a"],
            "source_file": ["meter_a.csv", "meter_a.csv"],
            "unit": ["Wh", "Wh"],
        }
    ).to_csv(combined_path, index=False)

    results = run_combined_dataset_eda(combined_path, output_dir)

    assert results["meter_summary"]["meter_count"] == 1
    assert (output_dir / "eda_summary.json").exists()
