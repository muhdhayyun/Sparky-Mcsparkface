from pathlib import Path

import pandas as pd

from energy_ml_pipeline.ingestion import prepare_raw_data


def test_prepare_raw_data_standardizes_schema(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()

    sample = pd.DataFrame(
        {
            "timestamp (dd/mm/yyyy hh:mm:ss)": ["27/02/2013 00:30:00", "27/02/2013 01:00:00"],
            " energy (Wh)": [77, 71],
        }
    )
    sample.to_csv(raw_dir / "meter_a.csv", index=False)

    combined, output_path = prepare_raw_data(raw_dir, processed_dir)

    assert output_path.exists()
    assert list(combined.columns) == ["timestamp", "energy_wh", "meter_id", "source_file", "unit"]
    assert combined.loc[0, "meter_id"] == "meter_a"
