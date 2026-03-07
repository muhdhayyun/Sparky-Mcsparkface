import pandas as pd

from energy_ml_pipeline.reporting import generate_meter_report


def test_generate_meter_report_returns_expected_sections() -> None:
    df = pd.DataFrame(
        {
            "timestamp": ["2025-01-01 00:00:00", "2025-01-01 00:30:00"],
            "energy_wh": [100, 120],
            "meter_id": ["meter_a", "meter_a"],
            "source_file": ["meter_a.csv", "meter_a.csv"],
            "unit": ["Wh", "Wh"],
        }
    )

    report = generate_meter_report(df)

    assert report["overview"]["meter_count"] == 1
    assert not report["top_meters"].empty
