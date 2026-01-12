# SITARA - Quick Start Guide

## 🚀 How to Run the Application

### ✅ What's Already Done

All files are created and ready:
- ✅ Backend API (FastAPI) - **Complete**
- ✅ Frontend UI (Next.js 14) - **Complete**  
- ✅ All Components - **Complete**
- ✅ Database Schema - **Complete**
- ✅ ML Scripts - **Complete**
- ⏳ Trained Model - **Need to train on powerful PC**

---

## 🎯 Option 1: Run WITHOUT Trained Model (See UI Only)

You can see the full UI even without the trained model!

### Step 1: Start Frontend

**Windows:**
```cmd
Double-click: START_FRONTEND.bat
```

**Or manually:**
```cmd
cd frontend
npm install
npm run dev
```

The app will open at: **http://localhost:3000**

### Step 2: Start Backend (Optional)

**Windows:**
```cmd
Double-click: START_BACKEND.bat
```

**Or manually:**
```cmd
cd backend
python main.py
```

API will run at: **http://localhost:8000**

**Note:** Backend will show warnings about missing model files - that's OK for now!

---

## 🎯 Option 2: Train Model First (Full Functionality)

### For Training on Powerful PC:

1. **Copy these to powerful PC:**
   ```
   DATASET/                           (all 78 CSV files)
   backend/standalone_preprocessing.py
   backend/standalone_training.py  
   backend/requirements.txt
   ```

2. **On powerful PC:**
   ```bash
   # Install dependencies
   pip install pandas numpy scikit-learn joblib
   
   # Create directory
   mkdir models
   
   # Run preprocessing (~10 seconds)
   python standalone_preprocessing.py
   
   # Run training (~10-30 minutes)
   python standalone_training.py
   ```

3. **Copy back these 3 files:**
   ```
   models/risk_model.joblib
   models/feature_scaler.joblib
   models/feature_names.json
   ```
   
   Place in: `N:\cognivia\backend\models\`

4. **Now run both servers** (see Option 1)

---

## 🌐 What You'll See

### Frontend (http://localhost:3000)

**Main Page:**
- ✨ Hero section with SITARA branding
- 📊 Statistics cards
- 🎨 Professional design (sky blue theme)
- ✅ "Explore Live Demo" button

**After Clicking "Explore":**
- 🗺️ **Interactive OpenStreetMap** - Click anywhere to assess risk
- 📊 **Risk Monitor Panel** - Shows current risk level
- 🤖 **Agent Status Panel** - Shows agent state (safe/caution/elevated/high)
- 🎯 **Real-time Updates** - Risk scores and recommendations

**Features Section:**
- 🔍 Continuous Observation
- 🧠 Intelligent Reasoning  
- 🛡️ Proportional Intervention
- 🗺️ Route Intelligence

**India-First Section:**
- Privacy guarantees
- India-specific design choices

### Backend (http://localhost:8000)

**API Endpoints:**
- `GET /` - API info
- `GET /health` - Health check
- `POST /api/assess-risk` - Risk assessment
- `POST /api/analyze-route` - Route analysis
- `GET /api/agent/state` - Agent status
- `GET /api/model/info` - Model metrics

**API Documentation:**
- http://localhost:8000/docs - Interactive Swagger UI

---

## 🐛 Troubleshooting

### Frontend Issues

**"Cannot find module 'next'"**
```cmd
cd frontend
npm install
```

**"Port 3000 already in use"**
```cmd
# Kill the process using port 3000
npx kill-port 3000
# Or use a different port
npm run dev -- -p 3001
```

### Backend Issues

**"Model not found" warning**
- This is normal if you haven't trained the model yet
- The API will still run, but risk predictions won't work
- UI will still display beautifully!

**"Module not found"**
```cmd
cd backend
pip install -r requirements.txt
```

**Database errors**
- Make sure PostgreSQL is running
- Password should be: `niklaus2212`
- Run migrations:
  ```cmd
  cd frontend
  npx prisma migrate dev
  ```

---

## 📱 Testing the UI

### Without Model:
1. Open http://localhost:3000
2. See beautiful landing page ✅
3. Click "Explore Live Demo" ✅
4. See map interface ✅
5. Clicking on map will show "Model not loaded" - that's OK!

### With Model:
1. Everything above ✅
2. Click on map → See actual risk assessment ✅
3. Agent state updates ✅
4. Risk monitor shows real predictions ✅
5. Route suggestions work ✅

---

## 🎨 UI Features to Show Off

1. **Professional Design**
   - Clean sky blue color scheme (not purple!)
   - Glass-morphism cards
   - Smooth animations

2. **Interactive Map**
   - Full India coverage
   - Click anywhere for risk assessment
   - Real-time updates

3. **Agent Visualization**
   - State machine visualization
   - Risk velocity tracking
   - Alert history

4. **Risk Monitor**
   - Live risk score (0-100%)
   - Risk level badge (low/medium/high)
   - Agent recommendations

---

## ✅ Quick Verification

**Frontend is working if you see:**
- ✨ SITARA logo and branding
- Professional hero section
- Features grid (4 cards)
- India-First section
- Footer with links

**Backend is working if:**
- http://localhost:8000 returns API info
- http://localhost:8000/docs shows Swagger UI
- http://localhost:8000/health returns {"status": "healthy"}

---

## 🎯 Next Steps

1. ✅ **See the UI** - Just run `START_FRONTEND.bat`
2. ⏳ **Train Model** - Use powerful PC (see above)
3. 🚀 **Full Demo** - Run both frontend + backend with trained model

---

## 📞 Need Help?

**Can't see the frontend?**
- Make sure you're in the correct directory
- Run `npm install` in frontend folder
- Check terminal for errors

**Everything looks blank?**
- Check browser console for errors (F12)
- Try clearing cache (Ctrl+Shift+R)
- Make sure dev server is running

**Want to customize?**
- Colors: `frontend/tailwind.config.ts`
- Content: `frontend/app/page.tsx`
- Components: `frontend/components/`

---

**You have a fully functional UI ready to demo right now!** 🎉

Just double-click `START_FRONTEND.bat` and open http://localhost:3000
