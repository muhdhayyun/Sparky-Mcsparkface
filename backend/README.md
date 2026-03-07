# Energy Backend API

Node.js/Express backend for processing CSV energy consumption data.

## Setup

```bash
cd backend
npm install
npm start
```

Server runs on http://localhost:3001

## API Endpoints

### GET /api/monthly-usage
Returns monthly energy consumption for 2014 comparing user vs all users average.

Response:
```json
[
  { "month": "Jan", "allUsersAvg": 120.4, "userUsage": 134.2 },
  ...
]
```

### GET /api/weekly-overview
Returns average weekday consumption (Mon-Fri) for the user.

Response:
```json
[
  { "day": "Mon", "avgUsage": 14.2, "target": 16 },
  ...
]
```

## Data Source
- CSV files: `/data/processed/*.csv`
- User file: `1623189_FD1_NK_EDMI_10_D.csv`
- Format: `timestamp (dd/mm/yyyy hh:mm:ss), energy (Wh)`
