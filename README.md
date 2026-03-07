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
```

2. Update `src/energy_ml_pipeline/config.py` with your dataset path and target column.

3. Run the pipeline:

```bash
python -m energy_ml_pipeline.main
```
