# Sparky Energy Assistant - AI Chatbot Integration

This directory contains the RAG (Retrieval-Augmented Generation) powered AI chatbot that serves as an energy assistant for the Sparky-Mcsparkface dashboard.

## What is This?

The Energy Assistant is an AI-powered chatbot that helps users:
- Understand their energy consumption patterns
- Get personalized energy-saving recommendations
- Learn about smart meters and energy monitoring
- Ask questions about renewable energy and sustainability
- Receive tips based on your actual usage data

## Architecture

The chatbot uses:
- **Pinecone**: Vector database for storing knowledge
- **OpenAI**: For embeddings (text-embedding-3-small) and chat (gpt-4o-mini)
- **FastAPI**: REST API server exposing chatbot endpoints
- **React Component**: Frontend chat interface integrated into the dashboard

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))
- Pinecone API key ([get one here](https://www.pinecone.io/))

### Step 1: Create Virtual Environment

```bash
cd chatbot
python -m venv .venv

# Activate (macOS/Linux):
source .venv/bin/activate

# Activate (Windows):
.venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file in the `chatbot/` directory:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-...your_key_here...

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_INDEX=energy-assistant

# Model Configuration (can keep defaults)
EMBED_MODEL=text-embedding-3-small
EMBED_DIMENSIONS=1024
CHAT_MODEL=gpt-4o-mini
```

### Step 4: Initialize the Knowledge Base

First time only - load the knowledge base documents:

```bash
python -c "
from rag_engine import ingest_directory
chunks, files = ingest_directory('knowledge_base')
print(f'Ingested {len(files)} files with {chunks} chunks')
"
```

This will ingest:
- Energy saving tips
- Smart meter usage guide
- Any additional documents you add to the `knowledge_base/` folder

### Step 5: Start the Chatbot API

```bash
python api.py
```

The API will start on `http://localhost:8000`

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 6: Test the Chatbot

Visit http://localhost:8000 in your browser - you should see:
```json
{
  "status": "ok",
  "message": "Sparky Energy Assistant API is running",
  "version": "1.0.0"
}
```

Test the chat endpoint:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How can I save energy at home?"}'
```

## Running the Full Application

From the project root directory:

```bash
# Start everything at once:
npm run dev

# This starts:
# - Frontend (React) on port 5173
# - Backend (Node.js) on port 3001
# - Chatbot (Python) on port 8000
```

Or run individually:
```bash
# Terminal 1: Frontend
cd frontend && npm run dev

# Terminal 2: Backend
cd backend && npm start

# Terminal 3: Chatbot
cd chatbot && source .venv/bin/activate && python api.py
```

## Using the Chat Interface

1. Open the dashboard at `http://localhost:5173`
2. Click the **message icon** (💬) in the bottom-right corner
3. Type your energy-related questions
4. Get AI-powered responses based on your knowledge base

### Example Questions to Try:

- "How can I reduce my energy bill?"
- "What are the best times to use electricity?"
- "Tell me about smart meters"
- "How do LED bulbs save energy?"
- "What should I do during peak hours?"
- "How can I monitor my appliance usage?"

## API Endpoints

### `GET /`
Health check - returns API status

### `GET /health`
Detailed health check with database stats

### `POST /chat`
Main chat endpoint
```json
Request:
{
  "message": "How can I save energy?",
  "user_context": "optional context about user"
}

Response:
{
  "response": "AI-generated response...",
  "contexts": ["relevant context 1", "relevant context 2"]
}
```

### `POST /ingest`
Ingest new knowledge documents
```json
Request:
{
  "directory": "/path/to/documents"
}
OR
{
  "file_path": "/path/to/file.txt"
}

Response:
{
  "status": "success",
  "chunks_added": 25,
  "files_processed": ["file1.txt", "file2.pdf"]
}
```

### `GET /stats`
Get database statistics

### `DELETE /database`
Clear all data from database (use with caution!)

## Adding Custom Knowledge

To teach the chatbot new information:

1. Add `.txt` or `.pdf` files to `knowledge_base/` directory
2. Run the ingestion:
```bash
python -c "
from rag_engine import ingest_directory
chunks, files = ingest_directory('knowledge_base')
print(f'Added {chunks} chunks from {len(files)} files')
"
```

Or use the API:
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory": "knowledge_base"}'
```

### Tips for Adding Content:

- Use clear, concise text
- Break into logical sections with headings
- Focus on energy-related topics
- Include practical tips and examples
- Avoid very technical jargon unless necessary

## Customizing the Chatbot

### Change the System Prompt

Edit `rag_engine.py`, function `chat_with_rag()`, around line 95:

```python
system_context = """You are an AI energy assistant for Sparky-Mcsparkface...
[customize this message]
"""
```

### Adjust Retrieval Settings

In `chat_with_rag()`, change `top_k` parameter:
```python
contexts = retrieve_from_pinecone(user_message, top_k=5)  # default: 3
```

More contexts = more comprehensive but possibly less focused responses

### Change Models

Edit `.env`:
```env
# Use a more powerful chat model:
CHAT_MODEL=gpt-4o

# Use a different embedding model:
EMBED_MODEL=text-embedding-3-large
EMBED_DIMENSIONS=3072  # Must match model dimensions!
```

Note: If you change embedding dimensions, you must recreate the Pinecone index.

## Troubleshooting

### "Failed to get response from assistant"

**Problem**: Frontend can't connect to chatbot API

**Solutions**:
1. Make sure chatbot API is running on port 8000
2. Check terminal for error messages
3. Verify `.env` file has correct API keys
4. Test API directly: `curl http://localhost:8000`

### "Missing environment variable"

**Problem**: `.env` file not configured

**Solution**: Copy `.env.example` to `.env` and add your API keys

### "Index not found" or Pinecone errors

**Problem**: Pinecone index doesn't exist or credentials wrong

**Solutions**:
1. Verify `PINECONE_API_KEY` in `.env`
2. Check index name matches your Pinecone dashboard
3. The code will auto-create index on first run if it doesn't exist

### Chatbot gives generic responses

**Problem**: Knowledge base not ingested

**Solution**: Run the ingestion script to load your documents into Pinecone

### High API costs

**Solutions**:
1. Use cheaper models: `gpt-4o-mini` instead of `gpt-4o`
2. Reduce `top_k` in retrieval (fewer contexts = fewer tokens)
3. Monitor usage in OpenAI dashboard
4. Consider caching common responses

## Cost Estimates

Based on typical usage (approximate):

**OpenAI**:
- Embeddings: $0.00002 per 1K tokens (very cheap)
- GPT-4o-mini: $0.15 per 1M input tokens, $0.60 per 1M output tokens
- Average chat: ~500 input + 200 output tokens = $0.00020 per chat

**Pinecone**:
- Free tier: Up to 100K vectors (plenty for most use cases)
- Paid: $70/month for 1M vectors (if you exceed free tier)

**Typical monthly cost for moderate use**: $5-15

## Architecture Details

```
┌─────────────┐
│   React     │ (Frontend - Port 5173)
│  Dashboard  │
└──────┬──────┘
       │ HTTP POST /chat
       ↓
┌─────────────┐
│   FastAPI   │ (Chatbot API - Port 8000)
│  rag_engine │
└──────┬──────┘
       │
       ├──→ OpenAI (Embeddings + Chat)
       │
       └──→ Pinecone (Vector Database)
```

The chatbot:
1. Receives user question via REST API
2. Converts question to embedding vector
3. Searches Pinecone for similar content
4. Retrieves top-k relevant text chunks
5. Sends question + context to OpenAI
6. Returns AI-generated response

## Files Overview

- `rag_engine.py` - Core RAG functionality (embeddings, storage, retrieval, chat)
- `api.py` - FastAPI server exposing REST endpoints
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variable template
- `knowledge_base/` - Document storage for ingestion
- `README.md` - This file

## Security Notes

⚠️ **Important**:
- Never commit `.env` file to git (it's in `.gitignore`)
- Keep API keys secure
- The chatbot runs on localhost by default (not exposed to internet)
- For production deployment, add authentication and rate limiting

## Next Steps

Want to enhance the chatbot? Consider:

1. **Add user usage data integration**: Connect to the Node.js backend to get actual user energy data
2. **Personalized recommendations**: Use user's consumption patterns for tailored advice
3. **Conversation history**: Store chat history in a database
4. **Multi-language support**: Add translation capabilities
5. **Voice interface**: Add speech-to-text input
6. **Scheduled tips**: Send proactive energy-saving notifications
7. **Integration with smart home**: Control devices via chat commands

## Support

For issues:
1. Check this README troubleshooting section
2. Verify all dependencies are installed
3. Test each component independently
4. Check console logs for error messages

## License

Part of the Sparky-Mcsparkface energy dashboard project.
