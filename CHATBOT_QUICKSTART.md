# Sparky-Mcsparkface Chatbot - Quick Start Guide

## What You Just Got

Your Sparky-Mcsparkface energy dashboard now has an **AI-powered chatbot assistant** that can:
- Answer questions about energy consumption
- Provide personalized energy-saving tips
- Explain smart meter data
- Help users understand their usage patterns

## File Structure

```
Sparky-Mcsparkface/
├── chatbot/                          # 🆕 NEW - AI Chatbot Backend
│   ├── api.py                       # FastAPI server (port 8000)
│   ├── rag_engine.py                # RAG logic (Pinecone + OpenAI)
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment template
│   ├── README.md                    # Detailed documentation
│   └── knowledge_base/              # Energy tips & guides
│       ├── energy_saving_tips.txt
│       └── smart_meters_guide.txt
├── frontend/
│   └── src/
│       ├── components/
│       │   └── EnergyAssistant.tsx  # 🆕 NEW - Chat UI component
│       └── pages/
│           └── Index.tsx            # 🔄 UPDATED - Added chatbot
├── backend/
│   └── server.js                    # (unchanged)
└── package.json                     # 🔄 UPDATED - Added chatbot script
```

## Setup (5 minutes)

### 1. Get API Keys

**OpenAI**: https://platform.openai.com/api-keys
- Create account → API keys → Create new key
- Copy the key (starts with `sk-proj-...`)

**Pinecone**: https://www.pinecone.io/
- Sign up → Create project → Get API key
- Copy the key

### 2. Configure Chatbot

```bash
cd chatbot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# OR: .venv\Scripts\activate  # Windows

# Install packages
pip install -r requirements.txt

# Create .env file
cp .env.example .env
nano .env  # or use any text editor
```

**Edit .env and paste your keys:**
```env
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
PINECONE_API_KEY=YOUR_PINECONE_KEY_HERE
PINECONE_INDEX=energy-assistant
```

Save and close.

### 3. Load Knowledge Base

```bash
# Still in chatbot/ directory with .venv activated
python -c "from rag_engine import ingest_directory; chunks, files = ingest_directory('knowledge_base'); print(f'✅ Loaded {len(files)} files with {chunks} chunks')"
```

You should see: `✅ Loaded 2 files with X chunks`

### 4. Start Everything

```bash
# Go back to project root
cd ..

# Start all services at once
npm run dev
```

This starts:
- ✅ Frontend: http://localhost:5173
- ✅ Backend: http://localhost:3001
- ✅ Chatbot: http://localhost:8000

### 5. Test It!

1. Open http://localhost:5173
2. Look for the **chat icon (💬)** in bottom-right corner
3. Click it and ask: "How can I save energy?"
4. You should get an AI response!

## Common Issues & Fixes

### ❌ "Failed to get response from assistant"

**Problem**: Chatbot API not running

**Fix**:
```bash
cd chatbot
source .venv/bin/activate
python api.py
```

Check that you see: `Uvicorn running on http://0.0.0.0:8000`

### ❌ "Missing environment variable: OPENAI_API_KEY"

**Problem**: `.env` file not set up

**Fix**: Follow step 2 above - create `.env` and add keys

### ❌ "Index not found" or Pinecone errors

**Problem**: First-time setup or wrong API key

**Fix**:
1. Verify `PINECONE_API_KEY` in `.env`
2. Wait 1-2 minutes after first run (index creation takes time)
3. Retry knowledge base ingestion

### ❌ Chat window appears but responses are slow

**Normal!** First response can take 3-5 seconds. Subsequent responses are faster.

## Testing the Chatbot

Try these questions:
- "How can I reduce my electricity bill?"
- "What are peak hours for energy usage?"
- "Tell me about smart meters"
- "Why should I use LED bulbs?"
- "How do I read my energy dashboard?"

## What's Next?

### Add Your Own Knowledge

Drop any `.txt` or `.pdf` files into `chatbot/knowledge_base/`, then run:
```bash
cd chatbot
source .venv/bin/activate
python -c "from rag_engine import ingest_directory; ingest_directory('knowledge_base')"
```

### Customize the Assistant

Edit `chatbot/rag_engine.py` around line 95 to change how the chatbot behaves:
```python
system_context = """You are an AI energy assistant...
[change this to customize personality and behavior]
"""
```

### View Detailed Docs

See `chatbot/README.md` for:
- API endpoint documentation
- Advanced configuration
- Cost optimization tips
- Architecture details

## Running Components Separately

Instead of `npm run dev`, you can run each part individually:

```bash
# Terminal 1: Frontend
cd frontend
npm run dev

# Terminal 2: Backend  
cd backend
npm start

# Terminal 3: Chatbot
cd chatbot
source .venv/bin/activate
python api.py
```

## Cost Estimate

Using the chatbot costs (via OpenAI):
- ~$0.0002 per chat message
- Monthly: $5-15 for moderate use (50-100 messages/day)
- Pinecone free tier covers up to 100K knowledge chunks (plenty!)

## Support

**Issue**: Chatbot not working?
1. Check all 3 services are running (Frontend, Backend, Chatbot)
2. Verify `.env` file has valid API keys
3. Check browser console (F12) for errors
4. Check terminal running `python api.py` for errors

**Still stuck?** Check `chatbot/README.md` troubleshooting section.

## Success Checklist

- ✅ Installed Python dependencies
- ✅ Created `.env` with API keys
- ✅ Ingested knowledge base
- ✅ Started chatbot API (port 8000)
- ✅ Started frontend (port 5173)
- ✅ Chat icon appears in dashboard
- ✅ Chat responses work

🎉 **You're all set!** Your energy dashboard now has an AI assistant.
