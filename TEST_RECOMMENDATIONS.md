# Testing Smart Recommendations

## Current Status

✅ **AI Service Running** on port 5001  
✅ **Backend Running** on port 3001  
✅ **Frontend Running** on port 8080  
✅ **Database Connected** - 2 appliances stored  
✅ **Peak Hours Calculated** - 18:00-22:00 (from 29 household CSVs)  
⚠️  **OpenAI Quota Exceeded** - Using offline fallback recommendations

## Issues Fixed

1. ✅ **Database Path** - Changed from `../../backend/` to `../backend/`
2. ✅ **Port Conflict** - Moved from 5000 (macOS AirPlay) to 5001
3. ✅ **Missing pandas** - Added to requirements
4. ✅ **Pinecone Package** - Updated from `pinecone-client` to `pinecone`
5. ✅ **Fallback Mechanism** - Recommendations work without OpenAI

## How to Test

### 1. Add an Appliance

1. Go to `http://localhost:8080`
2. Fill out the form:
   - Date: Today's date
   - Hours: 3
   - Appliance Name: "Air Conditioner"
3. Click "Add Appliance"
4. Watch the "Smart Recommendations" section

### 2. Verify Update

The recommendations should:
- Show actual peak hours: **18:00-19:00, 19:00-20:00, 20:00-21:00, 21:00-22:00**
- Display appliance-specific tips
- Update the appliance count
- Change recommendations based on what you added

### 3. Check Browser Console

Open Developer Tools (F12) → Console tab:
- Should see: "Appliance usage saved successfully"
- No red errors about CORS or 404

## API Endpoints to Test

```bash
# Check AI service health
curl http://localhost:5001/health

# Get current recommendations
curl http://localhost:5001/api/ai/recommendations

# Check backend data
curl http://localhost:3001/api/appliances
```

## Troubleshooting

### Recommendations Not Updating?

1. **Check the event is firing**: Open browser console, add appliance, look for logs
2. **Manual refresh**: Click the "Refresh Recommendations" button
3. **Hard refresh**: Press Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

### OpenAI Quota Issue

The system is using fallback recommendations (offline mode). To restore full AI features:

1. Add credits to your OpenAI account: https://platform.openai.com/account/billing
2. Or use a different API key in `/ai_service/.env`

The fallback provides:
- ✅ Peak hours from real data
- ✅ Appliance-specific recommendations
- ✅ Energy savings estimates
- ❌ No RAG from Pinecone
- ❌ No GPT-generated natural language

## Database Contents

Check what's stored:

```bash
cd /Users/sophia/Documents/GitHub/Sparky-Mcsparkface
sqlite3 backend/appliances.db "SELECT * FROM appliance_usage;"
```

## Next Steps

1. Test adding different appliances (Washing Machine, Oven, etc.)
2. Verify recommendations change for each appliance type
3. Check peak hours are displayed correctly
4. Test the progress ring (mark recommendations as complete)
