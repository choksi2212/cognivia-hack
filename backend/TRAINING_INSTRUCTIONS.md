# SITARA Model Training Instructions

## For Running on a Powerful PC

This guide helps you train the SITARA ML model on a more powerful computer.

## 📦 What You Need to Copy

Copy these items to your powerful PC:

```
DATASET/                              (entire folder with all 78 CSV files)
backend/standalone_preprocessing.py   (preprocessing script)
backend/standalone_training.py        (training script)
backend/requirements.txt              (Python dependencies)
```

## 🔧 Setup on Powerful PC

### Step 1: Install Python Dependencies

```bash
pip install pandas numpy scikit-learn joblib
```

Or use the full requirements.txt:

```bash
pip install -r requirements.txt
```

### Step 2: Create Directory Structure

```bash
mkdir models
```

Your directory should look like:
```
your-project/
├── DATASET/                    (78 CSV files)
├── models/                     (empty, will be populated)
├── standalone_preprocessing.py
├── standalone_training.py
└── requirements.txt
```

### Step 3: Update Paths (if needed)

Open `standalone_preprocessing.py` and verify:

```python
DATASET_DIR = Path("../DATASET")  # Adjust if your DATASET folder is elsewhere
```

## 🚀 Running the Scripts

### Step 1: Data Preprocessing

```bash
python standalone_preprocessing.py
```

**Expected Output:**
- `models/processed_district_data.csv` (~50,000 rows)
- `models/location_risk_mapping.csv` (~1,800 locations)
- `preprocessing.log` (detailed logs)

**Time:** ~5-10 seconds

### Step 2: Model Training

```bash
python standalone_training.py
```

**Expected Output:**
- `models/risk_model.joblib` (trained Random Forest model)
- `models/feature_scaler.joblib` (feature scaler)
- `models/feature_names.json` (metadata)
- `models/training_data.csv` (full training dataset)
- `training.log` (detailed logs)

**Time:** 
- Without GridSearch: ~2-5 minutes
- With GridSearch (default): ~10-30 minutes (depending on CPU cores)

**Target Accuracy:** >98%

## 📊 What Happens During Training

### Preprocessing Phase
1. Loads 78 CSV files from DATASET
2. Extracts district-level crime data
3. Aggregates crime statistics
4. Creates risk labels (low/medium/high)
5. Generates location mapping

### Training Phase
1. Feature engineering (26 features)
2. Creates 88,000+ training samples
3. Train/test split (80/20)
4. Hyperparameter optimization with GridSearchCV
5. Model evaluation
6. Saves all artifacts

## 🎯 Expected Results

```
Training Accuracy: 99.5%+
Test Accuracy: 98.0%+
Precision: 0.98+
Recall: 0.98+
F1 Score: 0.98+
```

## 🔄 Copy Back to Original PC

After training completes, copy these files back to your original PC:

```
models/risk_model.joblib
models/feature_scaler.joblib
models/feature_names.json
```

Place them in: `N:/cognivia/backend/models/`

## ⚡ Performance Tips

### For Faster Training:

Edit `standalone_training.py` line ~200:

```python
# Change from:
model = train_random_forest(X_train_scaled, y_train, optimize=True)

# To:
model = train_random_forest(X_train_scaled, y_train, optimize=False)
```

This skips GridSearchCV and uses optimized defaults (~2-5 minutes vs 10-30 minutes).

### For More Cores:

The scripts automatically use all CPU cores (`n_jobs=-1`). Ensure:
- No other heavy processes running
- Good cooling (training is CPU intensive)

## 🐛 Troubleshooting

### Issue: "Location mapping not found"
- Run `standalone_preprocessing.py` first
- Check if `models/location_risk_mapping.csv` exists

### Issue: Out of Memory
- Reduce `samples_per_location` in `standalone_training.py` (line ~105)
- Change from 50 to 25 or 20

### Issue: Training too slow
- Set `optimize=False` for faster training
- Reduce GridSearch parameters

### Issue: Accuracy below 98%
- This is normal for first run
- The model uses weak supervision
- Check logs for class imbalance
- Can still be deployed (>95% is good)

## 📝 Log Files

Both scripts create detailed logs:
- `preprocessing.log` - preprocessing details
- `training.log` - training metrics and progress

Check these if anything goes wrong.

## ✅ Validation

After training, verify these files exist:

```bash
ls -lh models/
```

Should show:
```
risk_model.joblib          (~50-100 MB)
feature_scaler.joblib      (~1 KB)
feature_names.json         (~2 KB)
processed_district_data.csv (~10-20 MB)
location_risk_mapping.csv  (~200 KB)
training_data.csv          (~50-100 MB)
```

## 🎉 Next Steps

Once trained:
1. Copy model files back to original PC
2. Start FastAPI backend: `python main.py`
3. Start Next.js frontend: `npm run dev`
4. Access at http://localhost:3000

---

**Need Help?**
Check the log files for detailed error messages.
