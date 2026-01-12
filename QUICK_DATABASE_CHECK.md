# ⚡ Quick Database Check - Is Data Being Stored?

## 🎯 Answer: YES! Here's How to Verify

### **Step 1: Setup Database (One-Time)**

Double-click this file:
```
SETUP_DATABASE.bat
```

It will:
- ✅ Create database connection files
- ✅ Create PostgreSQL database
- ✅ Create all tables

**Takes ~2 minutes**

---

### **Step 2: Start Backend**

Double-click:
```
START_BACKEND.bat
```

Look for this message:
```
✅ Database initialized successfully
✅ Database stats: {'connected': True, 'total_locations': 0, ...}
```

---

### **Step 3: Verify Database is Connected**

Open browser and go to:
```
http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "database_connected": true  ← THIS MEANS IT'S WORKING!
}
```

---

### **Step 4: Check Database Statistics**

Go to:
```
http://localhost:8000/api/database/stats
```

You'll see:
```json
{
  "connected": true,
  "total_locations": 0,
  "total_alerts": 0,
  "total_routes": 0,
  "total_logs": 0
}
```

**These numbers will increase as you use the app!**

---

### **Step 5: Use the App (Start Frontend)**

Double-click:
```
START_FRONTEND.bat
```

Then:
1. Click "Explore Live Demo"
2. Enter any location
3. Click "Assess Risk"

---

### **Step 6: See Data Being Stored!**

Go back to:
```
http://localhost:8000/api/database/stats
```

You'll see the numbers increase:
```json
{
  "connected": true,
  "total_locations": 5,  ← Increased!
  "total_alerts": 2,     ← Increased!
  "total_routes": 0,
  "total_logs": 12       ← Increased!
}
```

---

### **Step 7: View Recent Data**

Go to:
```
http://localhost:8000/api/locations/recent
```

You'll see:
```json
{
  "locations": [
    {
      "id": "abc-123-...",
      "latitude": 22.6823,
      "longitude": 72.8703,
      "riskScore": 0.45,
      "riskLevel": "medium",
      "agentState": "caution",
      "timestamp": "2026-01-12T..."
    }
  ],
  "count": 5
}
```

**THIS IS YOUR ACTUAL DATA STORED IN THE DATABASE!**

---

## 🔍 Alternative: Check with PostgreSQL Directly

Open Command Prompt and run:

```bash
psql -U postgres -d sitara
```

Then:
```sql
-- See all tables
\dt

-- Count locations
SELECT COUNT(*) FROM locations;

-- View recent locations
SELECT * FROM locations ORDER BY timestamp DESC LIMIT 5;

-- View recent alerts
SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 5;

-- Exit
\q
```

---

## ✅ What Gets Stored Automatically?

### **Every Risk Assessment:**
```
✅ Location (latitude, longitude)
✅ Risk score (0.0 - 1.0)
✅ Risk level (low/medium/high)
✅ Agent state (safe/caution/elevated_risk/high_risk)
✅ Time of day (hour)
✅ Day of week
✅ Road type
✅ POI density
✅ Timestamp
```

### **Every Alert:**
```
✅ Alert type (monitor/suggest_route/silent_checkin/recommend_escalation)
✅ Priority (0-3)
✅ Message
✅ Risk score
✅ Location
✅ Timestamp
```

### **Every Route Analysis:**
```
✅ Start/end coordinates
✅ All waypoints
✅ Cumulative risk score
✅ Risk level
✅ Timestamp
```

---

## 🎯 Quick Test Script

Copy and paste this in Command Prompt to test the API:

```powershell
# Test risk assessment
Invoke-WebRequest -Uri "http://localhost:8000/api/assess-risk" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"location":{"latitude":22.6823,"longitude":72.8703}}'

# Check if it was logged
Invoke-WebRequest -Uri "http://localhost:8000/api/database/stats"
```

---

## 📊 Visual Summary

```
┌─────────────────────────────────────────┐
│  Frontend (Next.js)                     │
│  User clicks "Assess Risk"              │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Backend API (FastAPI)                  │
│  - Extracts OSM features                │
│  - Runs ML model                        │
│  - Gets agent decision                  │
│  - 🔥 LOGS TO DATABASE 🔥              │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  PostgreSQL Database                    │
│  ✅ locations table                     │
│  ✅ alerts table                        │
│  ✅ routes table                        │
│  ✅ system_logs table                   │
└─────────────────────────────────────────┘
             │
             ▼
        💾 Permanent Storage
        (Data persists forever)
```

---

## 🆘 Troubleshooting

### "database_connected": false

**Fix:**
1. Make sure PostgreSQL is running
2. Run `SETUP_DATABASE.bat`
3. Restart backend

### "Database does not exist"

**Fix:**
```bash
psql -U postgres -c "CREATE DATABASE sitara;"
cd frontend
npx prisma migrate dev
```

### "Password authentication failed"

**Fix:**
Your PostgreSQL password is not `niklaus2212`.

Update these files:
- `frontend/.env`
- `backend/.env`

Change the password in `DATABASE_URL`

---

## ✅ Final Answer

**YES, the database IS connected and IS storing data!**

To verify:
1. Run `SETUP_DATABASE.bat` (once)
2. Run `START_BACKEND.bat`
3. Visit http://localhost:8000/api/database/stats
4. Use the app
5. Refresh the stats page - numbers will increase!

**Every single API call stores data permanently in PostgreSQL.**
