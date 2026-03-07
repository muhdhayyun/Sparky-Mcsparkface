# AI Service Setup Guide

## Overview
This AI service provides:
1. **Appliance energy consumption lookup** - Searches for typical energy usage of appliances
2. **Pinecone vector storage** - Stores appliance knowledge for RAG
3. **Personalized recommendations** - AI-generated energy-saving tips based on user's usage patterns

## Prerequisites

1. **OpenAI API Key** - Get from https://platform.openai.com/api-keys
2. **Pinecone API Key** - Get from https://app.pinecone.io/

## Setup Instructions

### 1. Install Python Dependencies

```bash
# Activate your virtual environment (from project root)
source .venv/bin/activate

# Navigate to AI service directory
cd ai_service

# Install AI service dependencies
pip install -r ai_requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `ai_service/` directory (you can copy from `.env.example`):

```bash
cp .env.example .env
```

Then edit `.env` and add your API keys:

```bash
OPENAI_API_KEY=sk-proj-your-actual-key-here
PINECONE_API_KEY=your-pinecone-key-here
TAVILY_API_KEY=tvly-your-key-here  # Optional: for web search
```

### 3. Run the AI Service API

```bash
# From ai_service/ directory
python ai_api.py
```

The AI service will start on `http://localhost:5000`

### 4. Run the Backend (Node.js)

In a separate terminal:

```bash
cd backend
npm start
```

Backend will run on `http://localhost:3001`

### 5. Run the Frontend

In another terminal:

```bash
cd frontend
npm run dev
```

Frontend will run on `http://localhost:8080`

## API Endpoints

### AI Service (Port 5000)

1. **POST /api/ai/appliance-consumption**
   - Get energy consumption data for an appliance
   - Stores knowledge in Pinecone
   ```json
   {
     "appliance_name": "Air Conditioner",
     "hours": 3,
     "date": "2026-03-08"
   }
   ```

2. **GET /api/ai/recommendations**
   - Get personalized energy-saving recommendations
   - Uses RAG from Pinecone + user's appliance history

3. **POST /api/ai/search-appliance**
   - Search for appliance energy data
   ```json
   {
     "appliance_name": "Washing Machine"
   }
   ```

4. **POST /api/ai/sync-knowledge**
   - Sync all database appliances to Pinecone
   - Run this once during initial setup

### Backend (Port 3001)

1. **POST /api/appliances** - Save appliance usage
2. **GET /api/appliances** - Get all appliance usage
3. **GET /api/monthly-usage** - Get monthly energy data
4. **GET /api/weekly-overview** - Get weekly overview

## Integration Flow

```
1. User fills form → Frontend (ApplianceUsageForm)
2. Form submits → Backend (:3001/api/appliances) → SQLite
3. Backend webhook/trigger → AI Service (:5000/api/ai/appliance-consumption)
4. AI Service:
   - Searches appliance consumption data
   - Stores in Pinecone for RAG
   - Returns consumption estimate
5. User requests recommendations → AI Service (:5000/api/ai/recommendations)
6. AI Service:
   - Fetches user appliances from database
   - Queries Pinecone for relevant knowledge (RAG)
   - Generates personalized recommendations via GPT-4
```

## Testing

### Test AI Service Standalone

```bash
# From ai_service/ directory
python ai_service.py
```

### Test via API

```bash
# Health check
curl http://localhost:5000/health

# Search appliance
curl -X POST http://localhost:5000/api/ai/search-appliance \
  -H "Content-Type: application/json" \
  -d '{"appliance_name": "Air Conditioner"}'

# Get recommendations (after adding some appliances)
curl http://localhost:5000/api/ai/recommendations
```

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │────────▶│   Backend    │────────▶│   SQLite    │
│   (React)   │         │   (Node.js)  │         │   Database  │
└─────────────┘         └──────────────┘         └─────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  AI Service  │
                        │   (Python)   │
                        └──────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
            ┌─────────────┐      ┌─────────────┐
            │   OpenAI    │      │  Pinecone   │
            │  (GPT-4)    │      │   (RAG)     │
            └─────────────┘      └─────────────┘
```

## Appliance Energy Database

The AI service includes a built-in knowledge base of common appliances:
- Air Conditioner: 3.5 kWh/hour
- Washing Machine: 0.5 kWh/hour
- Refrigerator: 0.15 kWh/hour
- Television: 0.1 kWh/hour
- Oven: 2.3 kWh/hour
- And more...

You can extend this or integrate with external APIs (Tavily, Serper, etc.) for web search.

## Troubleshooting

**"Module not found" errors:**
- Make sure you activated the virtual environment
- Run `pip install -r ai_requirements.txt`

**Pinecone connection errors:**
- Verify your `PINECONE_API_KEY` in `.env`
- Check your Pinecone account has available indexes

**OpenAI API errors:**
- Verify your `OPENAI_API_KEY` in `.env`
- Ensure you have API credits

**Database errors:**
- Make sure backend has created `appliances.db`
- Run `npm start` in backend folder first

## Next Steps

1. **Connect form to AI service** - Add webhook to call AI service when form is submitted
2. **Display recommendations** - Create a UI component to show AI recommendations
3. **Add more appliances** - Expand the appliance knowledge base
4. **Integrate web search** - Add Tavily/Serper API for real-time appliance data lookup
5. **Grid load integration** - Add real-time grid load data for smarter recommendations

## License

MIT
