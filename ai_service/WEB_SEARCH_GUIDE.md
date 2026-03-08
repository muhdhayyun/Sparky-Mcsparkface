# Web Search Options for Appliance Data Lookup

The AI service now searches online for appliance energy consumption data instead of relying on a hardcoded database.

## Default: Tavily API (Recommended)

**Tavily** is designed for AI applications and provides clean, structured search results.

### Setup:
1. Sign up at https://tavily.com
2. Get your API key
3. Add to `.env`:
   ```bash
   TAVILY_API_KEY=tvly-your-actual-key-here
   ```

### Pricing:
- Free tier: 1,000 requests/month
- Pro: $100/month for 50,000 requests

## Alternative 1: Serper API (Google Search)

If you prefer Google search results, use Serper.

### Implementation:
```python
# In ai_service.py, replace the Tavily section with:

response = requests.get(
    "https://google.serper.dev/search",
    headers={
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json"
    },
    json={
        "q": f"{appliance_name} average energy consumption kwh per hour"
    }
)

if response.status_code == 200:
    results = response.json()
    # Extract organic results
    context = ""
    for result in results.get("organic", [])[:3]:
        context += f"{result.get('snippet', '')}\n\n"
```

### Setup:
1. Sign up at https://serper.dev
2. Add to `.env`:
   ```bash
   SERPER_API_KEY=your-serper-key
   ```

### Pricing:
- Free tier: 2,500 requests
- Pay as you go: $50 for 50,000 requests

## Alternative 2: SerpAPI

Another Google search option with more features.

### Implementation:
```python
import serpapi

params = {
    "engine": "google",
    "q": f"{appliance_name} energy consumption kwh",
    "api_key": os.getenv("SERPAPI_KEY")
}

search = serpapi.search(params)
results = search.get("organic_results", [])
```

### Setup:
1. Sign up at https://serpapi.com
2. Install: `pip install google-search-results`
3. Add to `.env`:
   ```bash
   SERPAPI_KEY=your-serpapi-key
   ```

### Pricing:
- Free tier: 100 searches/month
- Starter: $50/month for 5,000 searches

## Alternative 3: Brave Search API

Privacy-focused search with a generous free tier.

### Implementation:
```python
response = requests.get(
    "https://api.search.brave.com/res/v1/web/search",
    headers={
        "Accept": "application/json",
        "X-Subscription-Token": os.getenv("BRAVE_API_KEY")
    },
    params={
        "q": f"{appliance_name} energy consumption kwh per hour"
    }
)

if response.status_code == 200:
    results = response.json()
    # Extract web results
    for result in results.get("web", {}).get("results", [])[:3]:
        context += f"{result.get('description', '')}\n\n"
```

### Setup:
1. Sign up at https://brave.com/search/api/
2. Add to `.env`:
   ```bash
   BRAVE_API_KEY=your-brave-key
   ```

### Pricing:
- Free tier: 2,000 queries/month
- Pro: $3 per 1,000 queries

## Fallback: GPT Knowledge (No API Key Needed)

If no search API key is provided, the system automatically falls back to using GPT's built-in knowledge about appliances.

**Pros:**
- No additional API keys needed
- No extra cost beyond OpenAI
- Still reasonably accurate for common appliances

**Cons:**
- Limited to GPT's training data (not current)
- May not have data on newer/specialized appliances

## Recommendation

**For production:**
1. **Primary**: Tavily API (best for AI applications)
2. **Fallback**: GPT knowledge (automatic, no setup needed)

**For cost-conscious:**
- Use GPT fallback only (free beyond OpenAI costs)
- Or use Brave Search (generous free tier)

**For highest accuracy:**
- Tavily or Serper (Google results)

## Current Implementation Flow

```
1. User adds appliance → Form submission
2. AI Service calls search_appliance_consumption()
3. If TAVILY_API_KEY exists:
   - Search web via Tavily
   - GPT extracts kWh data from results
4. Else:
   - Use GPT's knowledge directly
5. Store result in Pinecone for future RAG
6. Return consumption estimate
```

## Testing

Test the search functionality:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the AI service test
python ai_service.py

# Or test via API
curl -X POST http://localhost:5000/api/ai/search-appliance \
  -H "Content-Type: application/json" \
  -d '{"appliance_name": "Electric Kettle"}'
```

## Switching Search Providers

To switch from Tavily to another provider:

1. Update the `search_appliance_consumption_online()` method in `ai_service.py`
2. Replace the Tavily API call with your chosen provider
3. Update `.env` with the new API key
4. Restart the AI service

All search methods should return the same format:
```json
{
  "appliance": "Air Conditioner",
  "kwh_per_hour": 3.5,
  "source": "Energy Star",
  "found": true
}
```

This ensures compatibility regardless of the search provider used.
