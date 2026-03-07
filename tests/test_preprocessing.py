import pandas as pd

from energy_ml_pipeline.preprocessing import clean_column_names, extract_datetime_features


def test_clean_column_names_normalizes_headers() -> None:
    frame = pd.DataFrame({"Meter ID ": [1], "Reading Value(kWh)": [2.4]})
    cleaned = clean_column_names(frame)
    assert list(cleaned.columns) == ["meter_id", "reading_value_kwh"]


def test_extract_datetime_features_adds_columns() -> None:
    frame = pd.DataFrame({"timestamp": ["2025-01-01 08:15:00"]})
    enriched = extract_datetime_features(frame, "timestamp")
    assert {"timestamp_hour", "timestamp_day", "timestamp_month", "timestamp_weekday"}.issubset(
        enriched.columns
    )
