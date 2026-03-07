# Welcome to your Lovable project

## Project info

**URL**: https://lovable.dev/projects/REPLACE_WITH_PROJECT_ID

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/REPLACE_WITH_PROJECT_ID) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/REPLACE_WITH_PROJECT_ID) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/features/custom-domain#custom-domain)
# Energy ML Pipeline

Production-ready Python project skeleton for analyzing smart meter energy consumption data. The codebase is modular, dataset-agnostic, and designed so new datasets can be integrated with minimal changes.

## Structure

```text
project_root/
├── ai_service/              # Python Flask AI service for recommendations
│   ├── ai_api.py           # Flask REST API
│   ├── ai_service.py       # Core AI logic (RAG, recommendations)
│   ├── ai_requirements.txt # Python dependencies
│   └── .env.example        # API keys template
├── backend/                # Node.js Express server
│   ├── server.js
│   ├── appliances.db
│   └── package.json
├── frontend/               # React + Vite + TypeScript
│   ├── src/
│   │   ├── components/
│   │   └── pages/
│   └── package.json
├── data/
│   ├── processed/          # 2016 household energy CSVs
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

## Services

### 1. Frontend (React + Vite) - Port 8080
```bash
cd frontend
npm run dev
```

### 2. Backend (Node.js + Express) - Port 3001
```bash
cd backend
npm start
```

### 3. AI Service (Python + Flask) - Port 5000
```bash
cd ai_service
source ../.venv/bin/activate
python ai_api.py
```

See [ai_service/README.md](ai_service/README.md) for AI service setup.

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


# how to run the project
```
# AI Service (Port 5000)
cd ai_service
source ../.venv/bin/activate
python ai_api.py

# Backend (Port 3001)
cd backend
npm start

# Frontend (Port 8080)
cd frontend
npm run dev
```