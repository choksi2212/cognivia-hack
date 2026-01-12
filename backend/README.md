# SITARA Backend

Agentic Situational Risk Intelligence Platform - Backend API

## 🚀 Quick Start

### Option 1: Train on Powerful PC (Recommended)

1. Copy to powerful PC:
   - `DATASET/` folder
   - `standalone_preprocessing.py`
   - `standalone_training.py`
   - `requirements.txt`

2. Run preprocessing:
   ```bash
   python standalone_preprocessing.py
   ```

3. Run training:
   ```bash
   python standalone_training.py
   ```

4. Copy `models/` folder back to this directory

See `TRAINING_INSTRUCTIONS.md` for detailed guide.

### Option 2: Use Pre-trained Model

If you have pre-trained model files:
1. Place them in `backend/models/`:
   - `risk_model.joblib`
   - `feature_scaler.joblib`
   - `feature_names.json`

### Option 3: Train Locally

```bash
pip install -r requirements.txt
python run_pipeline.py
```

**Warning:** This requires significant CPU and may take 30+ minutes.

## 📦 Installation

```bash
cd backend
pip install -r requirements.txt
```

## 🏃 Running the Server

```bash
python main.py
```

Server will start at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## 📁 Directory Structure

```
backend/
├── main.py                          # FastAPI application
├── agent.py                         # Agentic FSM decision layer
├── config.py                        # Configuration
├── data_preprocessing.py            # Data preprocessing module
├── feature_engineering.py           # Feature engineering
├── train_model.py                   # Model training
├── run_pipeline.py                  # Full pipeline runner
├── standalone_preprocessing.py      # Standalone preprocessing
├── standalone_training.py           # Standalone training
├── requirements.txt                 # Python dependencies
├── models/                          # Trained models (generated)
│   ├── risk_model.joblib
│   ├── feature_scaler.joblib
│   ├── feature_names.json
│   └── agent_state.json
└── cache/                           # OSM cache (generated)
```

## 🔑 API Endpoints

### Health Check
```bash
GET /health
```

### Risk Assessment
```bash
POST /api/assess-risk
{
  "location": {
    "latitude": 28.6139,
    "longitude": 77.2090
  },
  "context": {
    "hour": 20,
    "day_of_week": 5
  }
}
```

### Route Analysis
```bash
POST /api/analyze-route
{
  "start": {"latitude": 28.6, "longitude": 77.2},
  "end": {"latitude": 28.7, "longitude": 77.3}
}
```

### Agent State
```bash
GET /api/agent/state
```

### Model Info
```bash
GET /api/model/info
```

## 🧠 ML Model

- **Algorithm:** Random Forest Classifier
- **Target Accuracy:** >98%
- **Features:** 26 (spatial + temporal + interaction)
- **Classes:** low, medium, high risk

## 🤖 Agentic AI

The agent uses a Finite State Machine with 4 states:
1. **SAFE** - No action needed
2. **CAUTION** - Silent monitoring
3. **ELEVATED_RISK** - Route suggestions
4. **HIGH_RISK** - Escalation options

## 📊 Data Sources

- District-level crime data (78 CSV files)
- OpenStreetMap for spatial context
- Synthetic temporal features

## 🔧 Configuration

Edit `config.py` or set environment variables:

```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/sitara
MODEL_PATH=./models/risk_model.joblib
```

## 🐛 Troubleshooting

### Model not loaded
- Check if `models/risk_model.joblib` exists
- Run training scripts first

### Import errors
- Install all requirements: `pip install -r requirements.txt`

### Database connection
- Ensure PostgreSQL is running
- Check DATABASE_URL in config

## 📝 Logs

All scripts generate log files:
- `preprocessing.log`
- `training.log`

## 🧪 Testing

Test individual modules:

```bash
# Test preprocessing
python data_preprocessing.py

# Test agent
python agent.py

# Test feature engineering
python feature_engineering.py
```

## 🚀 Production Deployment

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📄 License

MIT License - See main README.md
