import pandas as pd

from energy_ml_pipeline.anomaly_detection import detect_anomalies


def test_detect_anomalies_returns_summary_keys() -> None:
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=50, freq="30min").astype(str),
            "energy_wh": [100] * 49 + [5000],
            "meter_id": ["meter_a"] * 50,
            "source_file": ["meter_a.csv"] * 50,
            "unit": ["Wh"] * 50,
        }
    )

    anomalies, summary = detect_anomalies(df, contamination=0.05)

    assert "anomaly_count" in summary
    assert "meters_with_anomalies" in summary
    assert isinstance(anomalies, pd.DataFrame)
