const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');
const sqlite3 = require('sqlite3').verbose();

const app = express();
const PORT = 3001;
const DEFAULT_USER_ID = 'shared-demo-user';

function normalizeUserId(value) {
  return typeof value === 'string' && value.trim() ? value.trim() : DEFAULT_USER_ID;
}

// Initialize SQLite database
const DB_PATH = path.join(__dirname, 'appliances.db');
const db = new sqlite3.Database(DB_PATH);

// Create appliance_usage table
db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS appliance_usage (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT NOT NULL DEFAULT '${DEFAULT_USER_ID}',
      date TEXT NOT NULL,
      hours INTEGER NOT NULL,
      appliance_name TEXT NOT NULL,
      energy_kwh REAL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
  db.run(`
    ALTER TABLE appliance_usage
    ADD COLUMN user_id TEXT NOT NULL DEFAULT '${DEFAULT_USER_ID}'
  `, (err) => {
    if (err && !err.message.includes('duplicate column name')) {
      console.error('Error ensuring appliance_usage.user_id column:', err);
    }
  });
  db.run(`
    UPDATE appliance_usage
    SET user_id = '${DEFAULT_USER_ID}'
    WHERE user_id IS NULL OR TRIM(user_id) = ''
  `);
  console.log('Database initialized');
});

app.use(cors());
app.use(express.json());

const DATA_DIR = path.join(__dirname, '../data/processed');
const USER_FILE = '1623189_FD1_NK_EDMI_10_D.csv';

function resolveDatasetFile(datasetId) {
  const normalized = typeof datasetId === 'string' && datasetId.trim()
    ? datasetId.trim().replace(/\.csv$/i, '')
    : USER_FILE.replace(/\.csv$/i, '');
  const candidate = path.join(DATA_DIR, `${normalized}.csv`);
  return fs.existsSync(candidate) ? candidate : path.join(DATA_DIR, USER_FILE);
}

// Helper: Parse DD/MM/YYYY HH:mm:ss timestamp
function parseTimestamp(timestampStr) {
  const [datePart, timePart] = timestampStr.trim().split(' ');
  const [day, month, year] = datePart.split('/');
  const [hour, minute, second] = timePart.split(':');
  return new Date(
    parseInt(year),
    parseInt(month) - 1,
    parseInt(day),
    parseInt(hour),
    parseInt(minute),
    parseInt(second)
  );
}

// Helper: Read and parse a single CSV file
async function readCsvFile(filePath) {
  return new Promise((resolve, reject) => {
    const rows = [];
    fs.createReadStream(filePath)
      .pipe(csv())
      .on('data', (row) => {
        try {
          const timestampKey = Object.keys(row)[0];
          const energyKey = Object.keys(row)[1];

          const timestamp = parseTimestamp(row[timestampKey]);
          const energyWh = parseFloat(row[energyKey]);

          if (!isNaN(energyWh) && timestamp instanceof Date && !isNaN(timestamp)) {
            rows.push({ timestamp, energyWh });
          }
        } catch (err) {
          // Skip malformed rows
        }
      })
      .on('end', () => resolve(rows))
      .on('error', (err) => reject(err));
  });
}

// Endpoint 1: GET /api/monthly-usage
app.get('/api/monthly-usage', async (req, res) => {
  try {
    const selectedDatasetPath = resolveDatasetFile(req.query.dataset);
    const selectedDatasetFile = path.basename(selectedDatasetPath);
    const files = fs.readdirSync(DATA_DIR).filter((f) => f.endsWith('.csv'));

    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const allFilesMonthlyData = {};
    const userMonthlyData = {};
    const baselineMonthlyTotals = {};
    const baselineMonthlyCounts = {};

    for (let i = 0; i < 12; i++) {
      userMonthlyData[i] = 0;
      baselineMonthlyTotals[i] = 0;
      baselineMonthlyCounts[i] = 0;
    }

    for (const file of files) {
      try {
        const filePath = path.join(DATA_DIR, file);
        const rows = await readCsvFile(filePath);

        const monthlyTotals = {};
        for (let i = 0; i < 12; i++) {
          monthlyTotals[i] = 0;
        }

        rows.forEach(({ timestamp, energyWh }) => {
          if (timestamp.getFullYear() === 2014) {
            const month = timestamp.getMonth();
            monthlyTotals[month] += energyWh;
          }
        });

        allFilesMonthlyData[file] = monthlyTotals;

        for (let i = 0; i < 12; i++) {
          baselineMonthlyTotals[i] += monthlyTotals[i];
          baselineMonthlyCounts[i] += 1;
        }

        if (file === selectedDatasetFile) {
          for (let i = 0; i < 12; i++) {
            userMonthlyData[i] = monthlyTotals[i];
          }
        }
      } catch (err) {
        console.warn(`Warning: Could not process ${file}:`, err.message);
      }
    }

    const result = [];
    for (let month = 0; month < 12; month++) {
      const allUsersAvg = baselineMonthlyCounts[month] > 0
        ? (baselineMonthlyTotals[month] / baselineMonthlyCounts[month]) / 1000
        : 0;
      const userUsage = userMonthlyData[month] / 1000;

      result.push({
        month: monthNames[month],
        allUsersAvg: parseFloat(allUsersAvg.toFixed(1)),
        userUsage: parseFloat(userUsage.toFixed(1))
      });
    }

    res.json(result);
  } catch (err) {
    console.error('Error in /api/monthly-usage:', err);
    res.status(500).json({ error: 'Failed to process monthly usage data' });
  }
});

// Endpoint 2: GET /api/weekly-overview
app.get('/api/weekly-overview', async (req, res) => {
  try {
    const filePath = resolveDatasetFile(req.query.dataset);
    const rows = await readCsvFile(filePath);

    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const weekdayData = {};

    ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'].forEach((day) => {
      weekdayData[day] = {};
    });

    rows.forEach(({ timestamp, energyWh }) => {
      const dayOfWeek = dayNames[timestamp.getDay()];

      if (['Mon', 'Tue', 'Wed', 'Thu', 'Fri'].includes(dayOfWeek)) {
        const dateKey = timestamp.toISOString().split('T')[0];

        if (!weekdayData[dayOfWeek][dateKey]) {
          weekdayData[dayOfWeek][dateKey] = 0;
        }
        weekdayData[dayOfWeek][dateKey] += energyWh;
      }
    });

    const result = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'].map((day) => {
      const dailyTotals = Object.values(weekdayData[day]);
      const avgWh = dailyTotals.length > 0
        ? dailyTotals.reduce((sum, val) => sum + val, 0) / dailyTotals.length
        : 0;

      return {
        day,
        avgUsage: parseFloat((avgWh / 1000).toFixed(1)),
        target: 16
      };
    });

    res.json(result);
  } catch (err) {
    console.error('Error in /api/weekly-overview:', err);
    res.status(500).json({ error: 'Failed to process weekly overview data' });
  }
});

// Endpoint 3: POST /api/appliances - Save appliance usage
app.post('/api/appliances', (req, res) => {
  const { date, hours, applianceName, userId } = req.body;

  if (!date || !hours || !applianceName) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  const normalizedUserId = normalizeUserId(userId);
  const stmt = db.prepare('INSERT INTO appliance_usage (user_id, date, hours, appliance_name) VALUES (?, ?, ?, ?)');
  stmt.run(normalizedUserId, date, parseInt(hours), applianceName, function(err) {
    if (err) {
      console.error('Error saving appliance:', err);
      return res.status(500).json({ error: 'Failed to save appliance data' });
    }
    res.json({
      success: true,
      id: this.lastID,
      user_id: normalizedUserId,
      message: 'Appliance usage saved successfully'
    });
  });
  stmt.finalize();
});

// Endpoint 4: GET /api/appliances - Get appliance usage for one user
app.get('/api/appliances', (req, res) => {
  const userId = normalizeUserId(req.query.user_id);
  db.all('SELECT * FROM appliance_usage WHERE user_id = ? ORDER BY date DESC, created_at DESC', [userId], (err, rows) => {
    if (err) {
      console.error('Error fetching appliances:', err);
      return res.status(500).json({ error: 'Failed to fetch appliance data' });
    }
    res.json(rows);
  });
});

// Endpoint 5: GET /api/context-summary - Structured appliance context for AI service
app.get('/api/context-summary', (req, res) => {
  const userId = normalizeUserId(req.query.user_id);
  db.all('SELECT * FROM appliance_usage WHERE user_id = ? ORDER BY date DESC, created_at DESC', [userId], (err, rows) => {
    if (err) {
      console.error('Error building context summary:', err);
      return res.status(500).json({ error: 'Failed to build appliance context summary' });
    }

    const applianceCounts = new Map();
    const applianceHours = new Map();
    const weekdayBuckets = {
      weekday: 0,
      weekend: 0,
    };

    for (const row of rows) {
      const applianceName = row.appliance_name;
      const hours = Number(row.hours) || 0;

      applianceCounts.set(applianceName, (applianceCounts.get(applianceName) || 0) + 1);
      applianceHours.set(applianceName, (applianceHours.get(applianceName) || 0) + hours);

      const usageDate = new Date(`${row.date}T00:00:00`);
      const weekday = usageDate.getDay();

      if (!Number.isNaN(weekday)) {
        if (weekday === 0 || weekday === 6) {
          weekdayBuckets.weekend += 1;
        } else {
          weekdayBuckets.weekday += 1;
        }
      }
    }

    const sortedAppliances = [...applianceCounts.entries()].sort((a, b) => b[1] - a[1]);
    const highConsumptionAppliances = [...applianceHours.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([applianceName]) => applianceName);

    const mostCommonUsageWindow = Object.entries(weekdayBuckets).sort((a, b) => b[1] - a[1])[0]?.[0] || null;

    res.json({
      user_id: userId,
      appliances: rows,
      summary: {
        total_appliances: rows.length,
        unique_appliances: applianceCounts.size,
        most_common_appliance: sortedAppliances[0]?.[0] || null,
        most_common_usage_window: mostCommonUsageWindow,
        high_consumption_appliances: highConsumptionAppliances,
      }
    });
  });
});

app.listen(PORT, () => {
  console.log(`Backend server running on http://localhost:${PORT}`);
});
