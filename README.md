# Energy ML Pipeline

Production-ready Python project skeleton for analyzing smart meter energy consumption data. The codebase is modular, dataset-agnostic, and designed so new datasets can be integrated with minimal changes.

## Structure

```text
project_root/
├── data/
│   ├── processed/
│   └── raw/
├── models/
├── notebooks/
├── outputs/
├── src/
│   └── energy_ml_pipeline/
│       ├── config.py
│       ├── data_loader.py
│       ├── eda.py
│       ├── evaluation.py
│       ├── feature_engineering.py
│       ├── inference.py
│       ├── main.py
│       ├── preprocessing.py
│       ├── splitting.py
│       ├── training.py
│       └── utils.py
└── tests/
```

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
pip install -e .
```

2. Update `src/energy_ml_pipeline/config.py` with your dataset path and target column.

3. Run the pipeline:

```bash
python -m energy_ml_pipeline.main
```

## Prepare Multiple Raw Datasets

When you receive multiple smart meter CSV files, normalize them first:

```bash
python -m energy_ml_pipeline.prepare_data
```

This reads all `.csv` files in `data/raw/` and writes one merged file to `data/processed/smart_meter_combined.csv` with a standard schema:

- `timestamp`
- `energy_wh`
- `meter_id`
- `source_file`
- `unit`

To verify that the merged file contains all raw files and matching row counts:

```bash
python -m energy_ml_pipeline.verify_prepared_data
```

To run EDA on the merged dataset:

```bash
python -m energy_ml_pipeline.run_eda
```

This writes charts and `eda_summary.json` to `outputs/eda/`.

## Post-EDA Workflows

Generate reporting summaries from the combined dataset:

```bash
python -m energy_ml_pipeline.run_reporting
```

Detect anomalous readings:

```bash     
python -m energy_ml_pipeline.run_anomaly_detection
```

Train a baseline next-interval forecasting model:

```bash
python -m energy_ml_pipeline.run_forecasting
```
