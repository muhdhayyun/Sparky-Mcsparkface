const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');
const sqlite3 = require('sqlite3').verbose();

const app = express();
const PORT = 3001;

// Initialize SQLite database
const DB_PATH = path.join(__dirname, 'appliances.db');
const db = new sqlite3.Database(DB_PATH);

// Create appliance_usage table
db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS appliance_usage (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      date TEXT NOT NULL,
      hours INTEGER NOT NULL,
      appliance_name TEXT NOT NULL,
      energy_kwh REAL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
  console.log('✓ Database initialized');
});

app.use(cors());
app.use(express.json());

const DATA_DIR = path.join(__dirname, '../data/processed');
const USER_FILE = '1623189_FD1_NK_EDMI_10_D.csv';

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
          const timestampKey = Object.keys(row)[0]; // Handle "timestamp (dd/mm/yyyy hh:mm:ss)"
          const energyKey = Object.keys(row)[1]; // Handle " energy (Wh)"
          
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
    const files = fs.readdirSync(DATA_DIR).filter(f => f.endsWith('.csv'));
    
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const allFilesMonthlyData = {}; // { filename: { 0: totalWh, 1: totalWh, ... } }
    const userMonthlyData = {}; // { 0: totalWh, 1: totalWh, ... }
    
    // Initialize monthly totals
    for (let i = 0; i < 12; i++) {
      userMonthlyData[i] = 0;
    }
    
    // Process each file
    for (const file of files) {
      try {
        const filePath = path.join(DATA_DIR, file);
        const rows = await readCsvFile(filePath);
        
        const monthlyTotals = {};
        for (let i = 0; i < 12; i++) {
          monthlyTotals[i] = 0;
        }
        
        // Filter 2014 data and sum by month
        rows.forEach(({ timestamp, energyWh }) => {
          if (timestamp.getFullYear() === 2014) {
            const month = timestamp.getMonth();
            monthlyTotals[month] += energyWh;
          }
        });
        
        allFilesMonthlyData[file] = monthlyTotals;
        
        // Track user file separately
        if (file === USER_FILE) {
          for (let i = 0; i < 12; i++) {
            userMonthlyData[i] = monthlyTotals[i];
          }
        }
      } catch (err) {
        console.warn(`Warning: Could not process ${file}:`, err.message);
      }
    }
    
    // Calculate average across all files
    const result = [];
    for (let month = 0; month < 12; month++) {
      let sum = 0;
      let count = 0;
      
      Object.values(allFilesMonthlyData).forEach(monthlyTotals => {
        sum += monthlyTotals[month];
        count++;
      });
      
      const allUsersAvg = count > 0 ? (sum / count) / 1000 : 0; // Convert to kWh
      const userUsage = userMonthlyData[month] / 1000; // Convert to kWh
      
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
    const filePath = path.join(DATA_DIR, USER_FILE);
    const rows = await readCsvFile(filePath);
    
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const weekdayData = {}; // { 'Mon': { '2014-01-06': totalWh, '2014-01-13': totalWh, ... }, ... }
    
    // Initialize for Mon-Fri
    ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'].forEach(day => {
      weekdayData[day] = {};
    });
    
    // Group by weekday and date
    rows.forEach(({ timestamp, energyWh }) => {
      const dayOfWeek = dayNames[timestamp.getDay()];
      
      // Only process Mon-Fri
      if (['Mon', 'Tue', 'Wed', 'Thu', 'Fri'].includes(dayOfWeek)) {
        const dateKey = timestamp.toISOString().split('T')[0]; // YYYY-MM-DD
        
        if (!weekdayData[dayOfWeek][dateKey]) {
          weekdayData[dayOfWeek][dateKey] = 0;
        }
        weekdayData[dayOfWeek][dateKey] += energyWh;
      }
    });
    
    // Calculate average daily usage for each weekday
    const result = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'].map(day => {
      const dailyTotals = Object.values(weekdayData[day]);
      const avgWh = dailyTotals.length > 0
        ? dailyTotals.reduce((sum, val) => sum + val, 0) / dailyTotals.length
        : 0;
      
      return {
        day,
        avgUsage: parseFloat((avgWh / 1000).toFixed(1)), // Convert to kWh
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
  const { date, hours, applianceName } = req.body;
  
  if (!date || !hours || !applianceName) {
    return res.status(400).json({ error: 'Missing required fields' });
  }
  
  const stmt = db.prepare('INSERT INTO appliance_usage (date, hours, appliance_name) VALUES (?, ?, ?)');
  stmt.run(date, parseInt(hours), applianceName, function(err) {
    if (err) {
      console.error('Error saving appliance:', err);
      return res.status(500).json({ error: 'Failed to save appliance data' });
    }
    res.json({ 
      success: true, 
      id: this.lastID,
      message: 'Appliance usage saved successfully'
    });
  });
  stmt.finalize();
});

// Endpoint 4: GET /api/appliances - Get all appliance usage
app.get('/api/appliances', (req, res) => {
  db.all('SELECT * FROM appliance_usage ORDER BY date DESC, created_at DESC', (err, rows) => {
    if (err) {
      console.error('Error fetching appliances:', err);
      return res.status(500).json({ error: 'Failed to fetch appliance data' });
    }
    res.json(rows);
  });
});

app.listen(PORT, () => {
  console.log(`Backend server running on http://localhost:${PORT}`);
});
