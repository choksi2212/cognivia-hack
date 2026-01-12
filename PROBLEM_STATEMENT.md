# SITARA - Problem Statement

## Target Industry
**Public Safety Technology / Women's Safety Solutions**

Specifically addressing the gap in preventive, context-aware safety systems for women in Indian urban environments.

---

## User Group
**Primary Users:** Women aged 18-45 navigating urban and semi-urban areas in India

**Characteristics:**
- Navigate through dense, poorly-lit localities and narrow gullies
- Use public transit with rapid crowd density changes
- Move through mixed land-use zones (residential, industrial, markets)
- Require discreet, dignity-preserving safety assistance
- Need early warning rather than reactive panic responses

---

## Solution Scenario

### User Flow in Proposed Solution

**1. Passive Monitoring (Continuous)**
- User opens web app or enables background tracking
- GPS captures real-time location (latitude, longitude)
- System automatically detects time of day, day of week

**2. Environmental Analysis (Real-Time)**
- System queries OpenStreetMap for spatial context:
  - Road type (highway, residential, alley, dead-end)
  - POI density (shops, hospitals, police stations)
  - Distance to safety facilities
  - Intersection count, lighting proxies
- Merges with historical crime data for the district

**3. Risk Assessment (ML Model)**
- Random Forest classifier processes 26 engineered features
- Outputs risk score (0.0 - 1.0) and risk level (low/medium/high)
- Prediction happens in <30ms for real-time responsiveness

**4. Agentic Decision Layer (Intelligent Intervention)**
- Agent observes risk score and calculates risk velocity
- Maintains state: SAFE → CAUTION → ELEVATED_RISK → HIGH_RISK
- Decides intervention based on:
  - Current risk level
  - Risk trend (increasing/decreasing)
  - Time since last alert
  - User movement patterns

**5. Proportional Actions (User-Controlled)**

| Risk State | Agent Action | User Experience |
|------------|-------------|-----------------|
| **SAFE** | Monitor silently | No interruption |
| **CAUTION** | Silent monitoring | Subtle visual indicator |
| **ELEVATED_RISK** | Suggest safer route | Route alternatives displayed |
| **HIGH_RISK** | Recommend escalation | Prompt for check-in/emergency contact |

**6. Route Intelligence (Proactive)**
- User enters destination
- System generates 3+ alternative routes
- Calculates cumulative risk for each route
- Recommends lowest-risk path with visual overlay
- Updates recommendations as conditions change

**7. Data Logging (Analytics & Learning)**
- All assessments logged to PostgreSQL
- Alerts tracked with timestamps
- Routes analyzed for pattern recognition
- System learns from aggregated data (future enhancement)

---

## Proposed Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERACTION                         │
│  (Web App: Requests location assessment or route analysis)     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js 14)                       │
│  • Captures GPS coordinates via browser Geolocation API         │
│  • Sends POST request to backend API                            │
│  • Displays risk level, agent decision, route recommendations   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND API (FastAPI)                        │
│                                                                 │
│  Step 1: Feature Extraction                                     │
│  ├─ Query OpenStreetMap API (via osmnx)                        │
│  ├─ Extract spatial features (road type, POI density, etc.)    │
│  ├─ Generate temporal features (hour, day_of_week)             │
│  └─ Normalize and scale features                               │
│                                                                 │
│  Step 2: Risk Prediction                                        │
│  ├─ Load trained Random Forest model (joblib)                  │
│  ├─ Predict risk score & level                                 │
│  └─ Return confidence scores                                    │
│                                                                 │
│  Step 3: Agentic Decision                                       │
│  ├─ Safety Agent processes risk score                          │
│  ├─ Calculates risk velocity (rate of change)                  │
│  ├─ Updates FSM state (SAFE/CAUTION/ELEVATED/HIGH)            │
│  └─ Determines intervention action                             │
│                                                                 │
│  Step 4: Database Logging                                       │
│  ├─ Log location + risk score to PostgreSQL                    │
│  ├─ Log alert if action triggered                              │
│  └─ Log route analysis for analytics                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DATA SOURCES (External)                       │
│                                                                 │
│  • OpenStreetMap API                                            │
│    └─ Real-time queries for spatial context                    │
│                                                                 │
│  • Historical Crime Datasets (Pre-processed)                    │
│    ├─ 78 Indian district-level crime CSVs                      │
│    ├─ Kaggle Indian Crimes Dataset                             │
│    └─ Used for weak supervision during training                │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  DATABASE (PostgreSQL)                          │
│                                                                 │
│  Tables:                                                        │
│  • locations (lat, lng, risk_score, risk_level, timestamp)     │
│  • alerts (type, priority, message, acknowledged)              │
│  • routes (start, end, waypoints, cumulative_risk)             │
│  • system_logs (event_type, metadata)                          │
│                                                                 │
│  Purpose: Persistence, analytics, pattern recognition          │
└─────────────────────────────────────────────────────────────────┘
```

### Data Capture Points

1. **User Location:** Browser Geolocation API (GPS)
2. **Spatial Context:** OpenStreetMap API (real-time query)
3. **Temporal Context:** System timestamp → hour, day_of_week
4. **Historical Risk:** Pre-processed crime datasets (district-level)
5. **ML Prediction:** Random Forest model inference
6. **Agent State:** Finite State Machine logic
7. **Persistent Storage:** PostgreSQL writes

---

## Nature of Output

### Primary: **Progressive Web App (PWA)**

**Technology Stack:**
- **Frontend:** Next.js 14 with React, TypeScript, Tailwind CSS
- **UI Components:** Framer Motion animations, Leaflet maps, Three.js 3D hero
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL with SQLAlchemy ORM
- **ML Pipeline:** scikit-learn, pandas, numpy
- **Geospatial:** osmnx, geopandas, shapely

**Delivery Method:**
- **Web Application** accessible via modern browsers
- Responsive design (mobile, tablet, desktop)
- Installable as PWA for offline capability
- No app store approval required (faster iteration)

**User Interface Elements:**
1. **Interactive Map:** Real-time risk visualization with Leaflet
2. **Risk Monitor:** Live risk score and level display
3. **Agent Status:** Current state and intervention recommendations
4. **Route Planner:** Multiple route options with risk comparison
5. **3D Hero Experience:** Immersive onboarding (Three.js)

**Why Web-First:**
- ✅ Faster development and deployment
- ✅ Cross-platform (works on any device)
- ✅ No app store delays
- ✅ Easy A/B testing and updates
- ✅ Can become native app later (React Native wrapper)

**Future Expansion:**
- Native mobile apps (iOS/Android)
- API integration with ride-sharing platforms
- Browser extension for desktop users
- Voice-activated assistant integration

---

## Cost Model
**₹0 Infrastructure** using:
- Free tiers: Vercel (frontend), Render/Railway (backend)
- Open-source: PostgreSQL, Next.js, FastAPI
- Free APIs: OpenStreetMap, public crime datasets
