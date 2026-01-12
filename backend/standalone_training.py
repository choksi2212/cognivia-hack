"""
STANDALONE MODEL TRAINING SCRIPT FOR SITARA
Run this script after standalone_preprocessing.py

Usage:
    python standalone_training.py

Input Required:
    - models/location_risk_mapping.csv (from preprocessing)

Output:
    - models/risk_model.joblib
    - models/feature_scaler.joblib
    - models/feature_names.json
    - models/training_data.csv
"""

import pandas as pd
import numpy as np
import joblib
import json
import logging
import sys
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    f1_score, precision_score, recall_score
)
import warnings

warnings.filterwarnings('ignore')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
MODELS_DIR = Path("./models")
MODELS_DIR.mkdir(exist_ok=True)


def create_temporal_features(df: pd.DataFrame):
    """Create time-based features"""
    
    df['hour'] = np.random.randint(0, 24, len(df))
    df['day_of_week'] = np.random.randint(0, 7, len(df))
    
    # Time-based derived features
    df['is_night'] = (df['hour'] >= 21) | (df['hour'] < 6)
    df['is_evening'] = (df['hour'] >= 17) & (df['hour'] < 21)
    df['is_late_night'] = (df['hour'] >= 0) & (df['hour'] < 6)
    df['is_weekend'] = df['day_of_week'].isin([5, 6])
    
    # Time of day encoding
    def time_encode(hour):
        if 6 <= hour < 12:
            return 0  # morning
        elif 12 <= hour < 17:
            return 1  # afternoon
        elif 17 <= hour < 21:
            return 2  # evening
        elif 21 <= hour < 24:
            return 3  # night
        else:
            return 4  # late_night
    
    df['time_of_day_encoded'] = df['hour'].apply(time_encode)
    
    return df


def create_spatial_features(df: pd.DataFrame):
    """Create synthetic spatial features (OSM-like)"""
    
    n = len(df)
    
    # Road type distribution
    road_types = ['highway', 'main_road', 'residential', 'alley', 'footpath']
    df['road_type'] = np.random.choice(road_types, n, p=[0.1, 0.2, 0.4, 0.2, 0.1])
    
    # POI density
    df['poi_density'] = np.random.exponential(scale=5, size=n)
    df['police_station_distance'] = np.random.exponential(scale=2000, size=n)
    df['hospital_distance'] = np.random.exponential(scale=1500, size=n)
    
    # Connectivity features
    df['intersection_count'] = np.random.poisson(lam=3, size=n)
    df['dead_end_nearby'] = np.random.choice([0, 1], n, p=[0.8, 0.2])
    
    # Lighting
    road_type_lighting = {
        'highway': 0.9,
        'main_road': 0.8,
        'residential': 0.6,
        'alley': 0.3,
        'footpath': 0.2
    }
    df['lighting_score'] = df['road_type'].map(road_type_lighting)
    
    # Crowd density
    df['crowd_density'] = np.random.exponential(scale=20, size=n)
    
    # Isolation score
    df['isolation_score'] = (
        (1 / (df['poi_density'] + 1)) * 
        (1 / (df['intersection_count'] + 1)) * 
        (df['dead_end_nearby'] + 0.5)
    )
    df['isolation_score'] = (df['isolation_score'] - df['isolation_score'].min()) / \
                             (df['isolation_score'].max() - df['isolation_score'].min())
    
    return df


def create_interaction_features(df: pd.DataFrame):
    """Create interaction features"""
    
    df['night_isolation'] = df['is_night'].astype(int) * df['isolation_score']
    df['evening_alley'] = (df['is_evening'].astype(int) * 
                           (df['road_type'] == 'alley').astype(int))
    df['night_low_poi'] = df['is_night'].astype(int) * (df['poi_density'] < 3).astype(int)
    df['night_far_police'] = df['is_night'].astype(int) * (df['police_station_distance'] > 1000).astype(int)
    
    return df


def encode_categorical_features(df: pd.DataFrame):
    """One-hot encode categorical features"""
    
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    exclude = ['risk_label', 'state_ut', 'district', 'state', 'time_of_day']
    categorical_cols = [col for col in categorical_cols if col not in exclude]
    
    if categorical_cols:
        df = pd.get_dummies(df, columns=categorical_cols, prefix=categorical_cols, drop_first=True)
    
    return df


def prepare_training_data(location_mapping: pd.DataFrame):
    """Prepare complete training dataset"""
    
    logger.info("Starting feature engineering...")
    
    # Create multiple samples per location
    samples_per_location = 50
    
    expanded_samples = []
    for idx, row in location_mapping.iterrows():
        for _ in range(samples_per_location):
            expanded_samples.append(row.to_dict())
    
    df = pd.DataFrame(expanded_samples)
    logger.info(f"Created {len(df)} training samples from {len(location_mapping)} locations")
    
    # Add temporal features
    df = create_temporal_features(df)
    
    # Add spatial features
    df = create_spatial_features(df)
    
    # Add interaction features
    df = create_interaction_features(df)
    
    # Encode categorical features
    df = encode_categorical_features(df)
    
    # Identify feature columns
    exclude_cols = [
        'state_ut', 'district', 'state', 'risk_label', 'risk_score',
        'datetime', 'time_of_day', 'year'
    ]
    
    all_cols = df.columns.tolist()
    feature_cols = [col for col in all_cols if col not in exclude_cols]
    
    # Ensure all features are numeric
    for col in feature_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Fill NaNs
    df[feature_cols] = df[feature_cols].fillna(0)
    
    logger.info(f"Feature engineering complete: {len(feature_cols)} features")
    
    return df, feature_cols


def train_random_forest(X_train, y_train, optimize=True):
    """Train Random Forest with hyperparameter optimization"""
    
    logger.info("="*80)
    logger.info("Training Random Forest Classifier")
    logger.info("="*80)
    
    if optimize:
        # Simplified grid for faster training
        param_grid = {
            'n_estimators': [200, 500],
            'max_depth': [20, 30],
            'min_samples_split': [2, 5],
            'min_samples_leaf': [1, 2],
            'max_features': ['sqrt'],
            'class_weight': ['balanced']
        }
        
        base_rf = RandomForestClassifier(random_state=42, n_jobs=-1)
        
        logger.info("Running GridSearchCV...")
        logger.info(f"Parameter combinations: {np.prod([len(v) for v in param_grid.values()])}")
        
        grid_search = GridSearchCV(
            base_rf,
            param_grid,
            cv=3,  # Reduced from 5 for speed
            scoring='accuracy',
            n_jobs=-1,
            verbose=2
        )
        
        grid_search.fit(X_train, y_train)
        
        logger.info(f"Best parameters: {grid_search.best_params_}")
        logger.info(f"Best CV accuracy: {grid_search.best_score_:.4f}")
        
        model = grid_search.best_estimator_
    
    else:
        model = RandomForestClassifier(
            n_estimators=500,
            max_depth=30,
            min_samples_split=2,
            min_samples_leaf=1,
            max_features='sqrt',
            class_weight='balanced',
            random_state=42,
            n_jobs=-1,
            verbose=1
        )
        
        logger.info("Training with optimized parameters...")
        model.fit(X_train, y_train)
    
    logger.info("Training complete!")
    
    return model


def evaluate_model(model, X_train, X_test, y_train, y_test, label_encoder):
    """Comprehensive model evaluation"""
    
    logger.info("="*80)
    logger.info("Model Evaluation")
    logger.info("="*80)
    
    # Predictions
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    # Metrics
    train_accuracy = accuracy_score(y_train, y_train_pred)
    test_accuracy = accuracy_score(y_test, y_test_pred)
    test_precision = precision_score(y_test, y_test_pred, average='weighted')
    test_recall = recall_score(y_test, y_test_pred, average='weighted')
    test_f1 = f1_score(y_test, y_test_pred, average='weighted')
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
    
    metrics = {
        'train_accuracy': float(train_accuracy),
        'test_accuracy': float(test_accuracy),
        'precision': float(test_precision),
        'recall': float(test_recall),
        'f1_score': float(test_f1),
        'cv_mean': float(cv_scores.mean()),
        'cv_std': float(cv_scores.std())
    }
    
    # Print results
    logger.info(f"Training Accuracy: {train_accuracy:.4f} ({train_accuracy*100:.2f}%)")
    logger.info(f"Test Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
    logger.info(f"Precision: {test_precision:.4f}")
    logger.info(f"Recall: {test_recall:.4f}")
    logger.info(f"F1 Score: {test_f1:.4f}")
    logger.info(f"CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    
    # Classification report
    logger.info("\nClassification Report:")
    print(classification_report(y_test, y_test_pred, target_names=label_encoder.classes_))
    
    # Confusion matrix
    logger.info("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_test_pred)
    print(cm)
    
    # Check target accuracy
    if test_accuracy >= 0.98:
        logger.info("\n🎉 TARGET ACCURACY OF >98% ACHIEVED! 🎉")
    else:
        logger.info(f"\n⚠️  Accuracy {test_accuracy*100:.2f}% (Target: 98%+)")
    
    return metrics


def main():
    """Main training pipeline"""
    
    logger.info("="*80)
    logger.info("SITARA MODEL TRAINING - STANDALONE")
    logger.info("="*80)
    
    # Check for preprocessed data
    location_mapping_path = MODELS_DIR / "location_risk_mapping.csv"
    
    if not location_mapping_path.exists():
        logger.error(f"Location mapping not found: {location_mapping_path}")
        logger.info("Please run standalone_preprocessing.py first")
        return 1
    
    try:
        # Load preprocessed data
        logger.info(f"\n[1/6] Loading preprocessed data...")
        location_mapping = pd.read_csv(location_mapping_path)
        logger.info(f"Loaded {len(location_mapping)} locations")
        
        # Feature engineering
        logger.info(f"\n[2/6] Feature engineering...")
        training_data, feature_cols = prepare_training_data(location_mapping)
        
        # Save training data
        training_data.to_csv(MODELS_DIR / "training_data.csv", index=False)
        logger.info(f"Training data saved: {training_data.shape}")
        
        # Prepare for training
        logger.info(f"\n[3/6] Preparing training/test sets...")
        X = training_data[feature_cols].copy()
        y = training_data['risk_label'].copy()
        
        # Handle NaNs and infinites
        X = X.fillna(0)
        X = X.replace([np.inf, -np.inf], 0)
        
        # Encode labels
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)
        
        logger.info(f"Classes: {label_encoder.classes_}")
        logger.info(f"Training samples: {len(X)}")
        logger.info(f"Features: {len(feature_cols)}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        logger.info(f"Train set: {X_train_scaled.shape}")
        logger.info(f"Test set: {X_test_scaled.shape}")
        
        # Train model
        logger.info(f"\n[4/6] Training Random Forest...")
        model = train_random_forest(X_train_scaled, y_train, optimize=True)
        
        # Evaluate
        logger.info(f"\n[5/6] Evaluating model...")
        metrics = evaluate_model(model, X_train_scaled, X_test_scaled, 
                                y_train, y_test, label_encoder)
        
        # Save model
        logger.info(f"\n[6/6] Saving model artifacts...")
        
        joblib.dump(model, MODELS_DIR / "risk_model.joblib")
        logger.info(f"✓ Model saved")
        
        joblib.dump(scaler, MODELS_DIR / "feature_scaler.joblib")
        logger.info(f"✓ Scaler saved")
        
        metadata = {
            'feature_names': feature_cols,
            'classes': label_encoder.classes_.tolist(),
            'metrics': metrics,
            'n_features': len(feature_cols),
            'model_type': 'RandomForestClassifier'
        }
        
        with open(MODELS_DIR / "feature_names.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"✓ Metadata saved")
        
        # Final summary
        logger.info("="*80)
        logger.info("TRAINING COMPLETE!")
        logger.info("="*80)
        logger.info(f"✓ Test Accuracy: {metrics['test_accuracy']*100:.2f}%")
        logger.info(f"✓ Precision: {metrics['precision']:.4f}")
        logger.info(f"✓ Recall: {metrics['recall']:.4f}")
        logger.info(f"✓ F1 Score: {metrics['f1_score']:.4f}")
        logger.info("="*80)
        logger.info("\nModel artifacts saved in models/ directory")
        logger.info("Ready to deploy!")
        logger.info("="*80)
        
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ Training failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
