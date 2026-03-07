from energy_ml_pipeline.config import PipelineConfig


def test_default_config_has_supported_model_name() -> None:
    config = PipelineConfig()
    assert config.model_name in {"lightgbm", "random_forest", "linear_regression"}
