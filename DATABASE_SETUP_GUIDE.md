# 📊 SITARA Database Setup Guide

## Overview
SITARA uses **PostgreSQL** with **SQLAlchemy** (backend) and **Prisma** (frontend) to store:
- 📍 Location assessments
- 🚨 Risk alerts
- 🛣️ Route analyses
- 📝 System logs
- 👤 User data (future)

---

## ✅ Step-by-Step Setup

### **1. Run the Automated Setup Script**

Simply double-click or run:

```bash
SETUP_DATABASE.bat
```

This script will:
- ✅ Create `.env` files for frontend and backend
- ✅ Create the PostgreSQL database `sitara`
- ✅ Run Prisma migrations to create all tables
- ✅ Initialize the database schema

---

## 🔧 Manual Setup (if needed)

### **Step 1: Create Database**

Open Command Prompt or PowerShell and run:

```bash
psql -U postgres
```

Then in the PostgreSQL prompt:

```sql
CREATE DATABASE sitara;
\q
```

### **Step 2: Create .env Files**

**Frontend** (`frontend/.env`):
```env
DATABASE_URL="postgresql://postgres:niklaus2212@localhost:5432/sitara?schema=public"
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend** (`backend/.env`):
```env
DATABASE_URL="postgresql://postgres:niklaus2212@localhost:5432/sitara?schema=public"
MODEL_PATH=models/risk_model.joblib
SCALER_PATH=models/feature_scaler.joblib
FEATURE_NAMES_PATH=models/feature_names.json
```

### **Step 3: Run Prisma Migrations**

```bash
cd frontend
npx prisma migrate dev --name init
npx prisma generate
```

### **Step 4: Verify Database**

```bash
psql -U postgres -d sitara -c "\dt"
```

You should see:
- `users`
- `locations`
- `alerts`
- `routes`
- `trusted_contacts`
- `system_logs`

---

## 📊 Database Schema

### **Users Table**
```sql
id            UUID PRIMARY KEY
email         TEXT UNIQUE
name          TEXT
phoneNumber   TEXT UNIQUE
createdAt     TIMESTAMP
updatedAt     TIMESTAMP
```

### **Locations Table** (Main Risk Tracking)
```sql
id            UUID PRIMARY KEY
userId        UUID FOREIGN KEY
latitude      FLOAT
longitude     FLOAT
timestamp     TIMESTAMP
riskScore     FLOAT
riskLevel     TEXT (low/medium/high)
agentState    TEXT (safe/caution/elevated_risk/high_risk)
hour          INT
dayOfWeek     INT
roadType      TEXT
poiDensity    FLOAT
```

### **Alerts Table**
```sql
id            UUID PRIMARY KEY
userId        UUID FOREIGN KEY
type          TEXT (monitor/suggest_route/silent_checkin/recommend_escalation)
priority      INT (0-3)
message       TEXT
riskScore     FLOAT
latitude      FLOAT
longitude     FLOAT
timestamp     TIMESTAMP
acknowledged  BOOLEAN
```

### **Routes Table**
```sql
id            UUID PRIMARY KEY
startLat      FLOAT
startLng      FLOAT
endLat        FLOAT
endLng        FLOAT
waypoints     JSONB (array of waypoints)
riskScore     FLOAT
riskLevel     TEXT
timestamp     TIMESTAMP
```

### **System Logs Table**
```sql
id            UUID PRIMARY KEY
eventType     TEXT
metadata      JSONB
timestamp     TIMESTAMP
```

---

## 🔌 Backend Integration

The backend (`backend/db.py`) provides these functions:

### **Logging Functions**
```python
db.log_location(lat, lng, risk_score, risk_level, agent_state, features)
db.log_alert(user_id, alert_type, priority, message, risk_score, lat, lng)
db.log_route(start_lat, start_lng, end_lat, end_lng, risk_score, risk_level, waypoints)
db.log_system_event(event_type, metadata)
```

### **Query Functions**
```python
db.get_recent_locations(user_id="anonymous", limit=10)
db.get_statistics()  # Returns total counts and connection status
```

---

## 🌐 API Endpoints

### **Health Check (with DB status)**
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "agent_initialized": true,
  "database_connected": true,
  "timestamp": "2026-01-12T..."
}
```

### **Database Statistics**
```http
GET /api/database/stats
```

Response:
```json
{
  "connected": true,
  "total_locations": 42,
  "total_alerts": 7,
  "total_routes": 15,
  "total_logs": 128
}
```

### **Recent Locations**
```http
GET /api/locations/recent?user_id=anonymous&limit=10
```

Response:
```json
{
  "locations": [
    {
      "id": "uuid",
      "latitude": 22.6823,
      "longitude": 72.8703,
      "riskScore": 0.45,
      "riskLevel": "medium",
      "agentState": "caution",
      "timestamp": "2026-01-12T..."
    }
  ],
  "count": 10
}
```

---

## 🔍 Verify Data is Being Stored

### **Option 1: Check via API**
After running the backend, visit:
- http://localhost:8000/api/database/stats
- http://localhost:8000/api/locations/recent

### **Option 2: Check via PostgreSQL**

```bash
psql -U postgres -d sitara
```

Then:
```sql
-- Count records
SELECT COUNT(*) FROM locations;
SELECT COUNT(*) FROM alerts;
SELECT COUNT(*) FROM routes;

-- View recent locations
SELECT * FROM locations ORDER BY timestamp DESC LIMIT 10;

-- View recent alerts
SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 10;
```

---

## 🎯 What Gets Logged Automatically

When you use the API:

1. **Risk Assessment** (`/api/assess-risk`):
   - ✅ Logs location, risk score, risk level, agent state to `locations` table
   - ✅ Logs alert to `alerts` table if action is needed (non-monitor)

2. **Route Analysis** (`/api/analyze-route`):
   - ✅ Logs entire route with waypoints to `routes` table

3. **System Events**:
   - ✅ Backend startup/shutdown events
   - ✅ Model loading events
   - ✅ Error events

---

## 🚀 Testing the Database

### **1. Start Backend**
```bash
START_BACKEND.bat
```

### **2. Test Risk Assessment**
```bash
curl -X POST http://localhost:8000/api/assess-risk \
  -H "Content-Type: application/json" \
  -d '{
    "location": {
      "latitude": 22.6823,
      "longitude": 72.8703
    }
  }'
```

### **3. Check if Data Was Logged**
```bash
curl http://localhost:8000/api/database/stats
```

You should see `total_locations` increase!

---

## 🔒 Privacy & Security

### **Current Setup (Development)**
- Password stored in `.env` file (not committed to Git)
- Local database only

### **Production Recommendations**
1. Use environment variables from hosting platform
2. Enable SSL for PostgreSQL connections
3. Implement user authentication
4. Add data retention policies
5. Enable row-level security
6. Regular backups

---

## 📝 Database Maintenance

### **View All Tables**
```sql
\dt
```

### **Clear All Data (Reset)**
```sql
TRUNCATE TABLE locations, alerts, routes, system_logs CASCADE;
```

### **Drop and Recreate Database**
```sql
DROP DATABASE sitara;
CREATE DATABASE sitara;
```

Then re-run:
```bash
cd frontend
npx prisma migrate dev
```

---

## ✅ Checklist

After setup, verify:
- [ ] PostgreSQL is running
- [ ] Database `sitara` exists
- [ ] `.env` files created in both `frontend/` and `backend/`
- [ ] Prisma migrations completed
- [ ] Backend starts without database errors
- [ ] `/health` endpoint shows `"database_connected": true`
- [ ] `/api/database/stats` returns statistics
- [ ] Risk assessments are being logged

---

## 🆘 Troubleshooting

### **Error: "database 'sitara' does not exist"**
Run: `psql -U postgres -c "CREATE DATABASE sitara;"`

### **Error: "password authentication failed"**
Update password in `.env` files to match your PostgreSQL password

### **Error: "relation 'locations' does not exist"**
Run Prisma migrations: `cd frontend && npx prisma migrate dev`

### **Database connection slow**
Check if PostgreSQL service is running:
```bash
# Windows
sc query postgresql-x64-16
```

---

**Your database is now fully integrated! 🎉**

All risk assessments, routes, and alerts are being automatically logged to PostgreSQL.
