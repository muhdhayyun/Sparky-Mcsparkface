# AI Service

Python Flask service for appliance energy analysis and personalized recommendations.

## Features

- 🔍 **Online Appliance Lookup** - Searches web for real appliance consumption data (via Tavily API)
- 🧠 **Vector Storage** - Stores appliance knowledge in Pinecone for RAG
- 💡 **Smart Recommendations** - AI-generated energy-saving tips based on user's actual usage
- ⚡ **Peak Hour Analysis** - Calculates actual peak grid hours from household CSV data

## Quick Start

```bash
# 1. Install dependencies
pip install -r ai_requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env and add your API keys

# 3. Run the service
python ai_api.py
```

The service will start on `http://localhost:5000`

## Documentation

- [Setup Guide](AI_SERVICE_README.md) - Complete setup instructions
- [Web Search Guide](WEB_SEARCH_GUIDE.md) - Configure Tavily/Serper/Brave Search

## API Endpoints

- `POST /api/ai/appliance-consumption` - Lookup appliance energy data
- `GET /api/ai/recommendations` - Get personalized recommendations
- `POST /api/ai/search-appliance` - Search appliance consumption
- `POST /api/ai/sync-knowledge` - Sync database to Pinecone

## Tech Stack

- **Flask** - REST API
- **OpenAI** - GPT-4o-mini, text-embedding-3-small
- **Pinecone** - Vector database for RAG
- **Tavily** - Web search API (optional)
- **Pandas** - CSV data analysis
