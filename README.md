# Hackomania Energy App

This project is a local three-service app for household energy analysis, appliance tracking, and smart recommendations.

## Architecture

- `frontend/` = React + Vite UI
- `backend/` = Node/Express API and SQLite owner
- `ai_service/` = Python/Flask recommendations service
- `data/processed/` = processed household CSV datasets used as the demo user pool

Current behavior:

- The `Simple Login` dropdown is a temporary user switcher.
- Each demo user is mapped to one processed CSV dataset.
- Appliance usage is stored in SQLite and scoped by the selected user.
- Smart recommendations use:
  - selected user appliance usage from the backend
  - selected dataset energy profile
  - the full processed dataset pool for baseline and peak-hour analysis

## How The App Works

1. Frontend loads available demo users from the AI service.
2. Selecting a user changes the active dataset context across the page.
3. The backend serves:
   - monthly usage for the selected dataset
   - weekly overview for the selected dataset
   - appliance usage for the selected user
   - appliance context summary for the AI service
4. The AI service:
   - fetches appliance context from the backend
   - compares the selected dataset against the dataset pool
   - calculates peak demand hours from processed CSVs
   - generates smart recommendations
5. Appliance usage added in the form is stored only for the currently selected user.

## Run The Project

Use three terminals.

### 1. Frontend

```powershell
cd C:\Users\muhdh\Desktop\Apps\School\Y2S2\Hackomania\frontend
npm run dev
```

### 2. Backend

```powershell
cd C:\Users\muhdh\Desktop\Apps\School\Y2S2\Hackomania\backend
npm start
```

Runs on `http://localhost:3001`

### 3. AI Service

```powershell
cd C:\Users\muhdh\Desktop\Apps\School\Y2S2\Hackomania\ai_service
python ai_api.py
```

Runs on `http://localhost:5001`

Notes:

- Pinecone is optional at runtime. If unavailable, the AI service still runs.
- Tavily is optional. If it fails, appliance lookup falls back.
- The backend creates `backend/appliances.db` automatically on startup.

## Main User Flow

1. Start all three services.
2. Open the frontend in the browser.
3. Use `Simple Login` to choose a demo user.
4. Check:
   - monthly usage chart
   - weekly overview
   - smart recommendations
5. Add appliance usage for that selected user.
6. Switch users and verify appliance usage and recommendations are isolated per user.

## Important Endpoints

### Backend

- `GET /api/monthly-usage?dataset=<dataset_id>`
- `GET /api/weekly-overview?dataset=<dataset_id>`
- `POST /api/appliances`
- `GET /api/appliances?user_id=<dataset_id>`
- `GET /api/context-summary?user_id=<dataset_id>`

### AI Service

- `GET /health`
- `GET /api/ai/datasets`
- `GET /api/ai/recommendations?dataset=<dataset_id>`
- `POST /api/ai/appliance-consumption`

## Key Files

- `frontend/src/pages/Index.tsx`
- `frontend/src/components/UsageChart.tsx`
- `frontend/src/components/WeeklyOverview.tsx`
- `frontend/src/components/Recommendations.tsx`
- `frontend/src/components/ApplianceUsageForm.tsx`
- `frontend/src/components/ApplianceUsageDashboard.tsx`
- `backend/server.js`
- `ai_service/ai_api.py`
- `ai_service/ai_service.py`

## Current Constraints

- The login system is temporary and dataset-backed, not real authentication.
- Appliance lookup may use fallback estimates if Tavily is unavailable.
- Recommendation rendering still depends on parsing formatted text from the AI response.

## Useful Checks

```powershell
curl http://localhost:3001/api/appliances
curl "http://localhost:3001/api/monthly-usage?dataset=1130211_FD1_L1_EDMI_1_D"
curl "http://localhost:3001/api/weekly-overview?dataset=1130211_FD1_L1_EDMI_1_D"
curl http://localhost:5001/health
curl http://localhost:5001/api/ai/datasets
curl "http://localhost:5001/api/ai/recommendations?dataset=1130211_FD1_L1_EDMI_1_D"
```
