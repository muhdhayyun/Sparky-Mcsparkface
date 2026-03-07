from pathlib import Path

import pandas as pd

from energy_ml_pipeline.ingestion import prepare_raw_data
from energy_ml_pipeline.verify_prepared_data import verify_prepared_data


def test_verify_prepared_data_reports_matching_counts(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()

    first = pd.DataFrame(
        {
            "timestamp (dd/mm/yyyy hh:mm:ss)": ["27/02/2013 00:30:00", "27/02/2013 01:00:00"],
            " energy (Wh)": [77, 71],
        }
    )
    second = pd.DataFrame(
        {
            "timestamp (dd/mm/yyyy hh:mm:ss)": ["28/02/2013 00:30:00"],
            " energy (Wh)": [55],
        }
    )
    first.to_csv(raw_dir / "meter_a.csv", index=False)
    second.to_csv(raw_dir / "meter_b.csv", index=False)

    _, output_path = prepare_raw_data(raw_dir, processed_dir)
    results = verify_prepared_data(raw_dir, output_path)

    assert results["all_present"] is True
    assert results["all_counts_match"] is True
    assert results["raw_file_count"] == 2
    assert results["combined_source_file_count"] == 2
