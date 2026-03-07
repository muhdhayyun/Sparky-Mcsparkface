import pandas as pd

from energy_ml_pipeline.forecasting import build_forecasting_dataset


def test_build_forecasting_dataset_creates_supervised_columns() -> None:
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=80, freq="30min").astype(str),
            "energy_wh": list(range(80)),
            "meter_id": ["meter_a"] * 80,
            "source_file": ["meter_a.csv"] * 80,
            "unit": ["Wh"] * 80,
        }
    )

    forecast_df = build_forecasting_dataset(df, horizon=1)

    assert {"lag_1", "lag_48", "rolling_mean_48", "target_next"}.issubset(forecast_df.columns)
    assert not forecast_df.empty
