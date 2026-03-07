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

---

# Sparky-Mcsparkface Energy Dashboard

Production-ready energy dashboard with ML pipeline and AI-powered chatbot assistant for analyzing smart meter energy consumption data.

## 🌟 Features

- **📊 Real-time Energy Dashboard**: Interactive visualization of energy consumption patterns
- **🤖 AI Energy Assistant**: RAG-powered chatbot for personalized energy advice
- **📈 Smart Meter Analytics**: Analyze consumption patterns and trends
- **💡 Energy Saving Recommendations**: AI-driven suggestions based on your usage
- **📱 Responsive Interface**: Works on desktop and mobile devices

## 🏗️ Architecture

This project consists of three main components:

1. **Frontend** (React + TypeScript): Dashboard UI and chat interface
2. **Backend** (Node.js): API for serving energy consumption data
3. **Chatbot** (Python + FastAPI): RAG-powered AI assistant

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

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+
- OpenAI API key
- Pinecone API key

### Installation

1. **Clone and install dependencies:**

```bash
# Install root dependencies
npm install

# Install frontend dependencies
cd frontend && npm install && cd ..

# Install backend dependencies
cd backend && npm install && cd ..
```

2. **Set up the AI Chatbot:**

```bash
cd chatbot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your API keys:
# - OPENAI_API_KEY
# - PINECONE_API_KEY
```

3. **Ingest knowledge base (first time only):**

```bash
python -c "from rag_engine import ingest_directory; chunks, files = ingest_directory('knowledge_base'); print(f'Ingested {len(files)} files')"
cd ..
```

4. **Start all services:**

```bash
# From project root
npm run dev

# This starts:
# - Frontend: http://localhost:5173
# - Backend: http://localhost:3001
# - Chatbot: http://localhost:8000
```

### Using the Dashboard

1. Open http://localhost:5173 in your browser
2. View your energy consumption data and analytics
3. Click the chat icon (💬) in the bottom-right to talk to the AI assistant
4. Ask questions like:
   - "How can I reduce my energy bill?"
   - "What are peak hours?"
   - "Tell me about smart meters"

## 📚 Documentation

- **[Chatbot Setup Guide](chatbot/README.md)** - Detailed chatbot configuration and API docs
- **[Energy ML Pipeline](#energy-ml-pipeline)** - Data processing and ML workflows

## Quick Start (ML Pipeline)

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
