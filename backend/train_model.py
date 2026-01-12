"""
ML Model Training Pipeline for SITARA
Trains Random Forest Classifier for risk estimation with >98% accuracy
"""

import pandas as pd
import numpy as np
import joblib
import json
import logging
from pathlib import Path
from typing import Tuple, Dict
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    roc_auc_score, f1_score, precision_score, recall_score
)
import warnings

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskModelTrainer:
    """Trains and evaluates risk prediction model"""
    
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = []
        self.metrics = {}
        
    def prepare_data(self, df: pd.DataFrame, feature_cols: list, 
                     target_col: str = 'risk_label') -> Tuple:
        """Prepare training and test sets"""
        
        logger.info("Preparing training data...")
        
        # Ensure all feature columns exist and are numeric
        X = df[feature_cols].copy()
        y = df[target_col].copy()
        
        # Handle any remaining NaNs
        X = X.fillna(0)
        
        # Remove infinite values
        X = X.replace([np.inf, -np.inf], 0)
        
        # Encode labels
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        
        logger.info(f"Classes: {self.label_encoder.classes_}")
        logger.info(f"Training samples: {len(X)}")
        logger.info(f"Features: {len(feature_cols)}")
        
        # Split data (80-20 split)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=self.random_state,
            stratify=y_encoded
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.feature_names = feature_cols
        
        logger.info(f"Train set: {X_train_scaled.shape}")
        logger.info(f"Test set: {X_test_scaled.shape}")
        
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def train_random_forest(self, X_train: np.ndarray, y_train: np.ndarray,
                           optimize: bool = True) -> RandomForestClassifier:
        """
        Train Random Forest Classifier with hyperparameter optimization
        Target: >98% accuracy
        """
        
        logger.info("="*60)
        logger.info("Training Random Forest Classifier")
        logger.info("="*60)
        
        if optimize:
            # Hyperparameter grid for optimization
            param_grid = {
                'n_estimators': [200, 300, 500],
                'max_depth': [20, 30, None],
                'min_samples_split': [2, 5],
                'min_samples_leaf': [1, 2],
                'max_features': ['sqrt', 'log2'],
                'class_weight': ['balanced', None]
            }
            
            # Base model
            base_rf = RandomForestClassifier(
                random_state=self.random_state,
                n_jobs=-1,
                warm_start=False
            )
            
            logger.info("Running GridSearchCV for hyperparameter optimization...")
            logger.info("This may take a few minutes...")
            
            grid_search = GridSearchCV(
                base_rf,
                param_grid,
                cv=5,
                scoring='accuracy',
                n_jobs=-1,
                verbose=1
            )
            
            grid_search.fit(X_train, y_train)
            
            logger.info(f"Best parameters: {grid_search.best_params_}")
            logger.info(f"Best CV accuracy: {grid_search.best_score_:.4f}")
            
            self.model = grid_search.best_estimator_
        
        else:
            # Train with strong default parameters
            self.model = RandomForestClassifier(
                n_estimators=500,
                max_depth=30,
                min_samples_split=2,
                min_samples_leaf=1,
                max_features='sqrt',
                class_weight='balanced',
                random_state=self.random_state,
                n_jobs=-1,
                verbose=1
            )
            
            logger.info("Training with default optimized parameters...")
            self.model.fit(X_train, y_train)
        
        logger.info("Training complete!")
        
        return self.model
    
    def evaluate_model(self, X_train: np.ndarray, X_test: np.ndarray,
                       y_train: np.ndarray, y_test: np.ndarray) -> Dict:
        """Comprehensive model evaluation"""
        
        logger.info("="*60)
        logger.info("Model Evaluation")
        logger.info("="*60)
        
        # Training predictions
        y_train_pred = self.model.predict(X_train)
        train_accuracy = accuracy_score(y_train, y_train_pred)
        
        # Test predictions
        y_test_pred = self.model.predict(X_test)
        test_accuracy = accuracy_score(y_test, y_test_pred)
        
        # Detailed metrics
        test_precision = precision_score(y_test, y_test_pred, average='weighted')
        test_recall = recall_score(y_test, y_test_pred, average='weighted')
        test_f1 = f1_score(y_test, y_test_pred, average='weighted')
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=5, scoring='accuracy')
        
        metrics = {
            'train_accuracy': train_accuracy,
            'test_accuracy': test_accuracy,
            'precision': test_precision,
            'recall': test_recall,
            'f1_score': test_f1,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }
        
        self.metrics = metrics
        
        # Print results
        logger.info(f"Training Accuracy: {train_accuracy:.4f} ({train_accuracy*100:.2f}%)")
        logger.info(f"Test Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
        logger.info(f"Precision: {test_precision:.4f}")
        logger.info(f"Recall: {test_recall:.4f}")
        logger.info(f"F1 Score: {test_f1:.4f}")
        logger.info(f"CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        # Classification report
        logger.info("\nClassification Report:")
        print(classification_report(
            y_test, y_test_pred,
            target_names=self.label_encoder.classes_
        ))
        
        # Confusion matrix
        logger.info("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_test_pred)
        print(cm)
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("\nTop 10 Most Important Features:")
        print(feature_importance.head(10))
        
        # Check if target accuracy achieved
        if test_accuracy >= 0.98:
            logger.info("🎉 Target accuracy of >98% ACHIEVED!")
        else:
            logger.warning(f"⚠️ Accuracy {test_accuracy*100:.2f}% - Target is 98%+")
            logger.info("Consider: more data, feature engineering, or hyperparameter tuning")
        
        return metrics
    
    def save_model(self, model_path: Path, scaler_path: Path, 
                   feature_names_path: Path):
        """Save trained model and preprocessing objects"""
        
        # Save model
        joblib.dump(self.model, model_path)
        logger.info(f"Model saved to {model_path}")
        
        # Save scaler
        joblib.dump(self.scaler, scaler_path)
        logger.info(f"Scaler saved to {scaler_path}")
        
        # Save feature names and metadata
        metadata = {
            'feature_names': self.feature_names,
            'classes': self.label_encoder.classes_.tolist(),
            'metrics': {k: float(v) for k, v in self.metrics.items()},
            'n_features': len(self.feature_names),
            'model_type': 'RandomForestClassifier'
        }
        
        with open(feature_names_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Metadata saved to {feature_names_path}")
        logger.info("All model artifacts saved successfully!")


def main():
    """Main training pipeline"""
    from config import MODELS_DIR
    
    logger.info("="*60)
    logger.info("SITARA ML Model Training Pipeline")
    logger.info("="*60)
    
    # Load training data
    training_data_path = MODELS_DIR / "training_data.csv"
    
    if not training_data_path.exists():
        logger.error("Training data not found! Run data_preprocessing.py and feature_engineering.py first")
        return
    
    df = pd.read_csv(training_data_path)
    logger.info(f"Loaded training data: {df.shape}")
    
    # Identify feature columns
    exclude_cols = [
        'state_ut', 'district', 'state', 'risk_label', 'risk_score',
        'datetime', 'time_of_day', 'year'
    ]
    
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    logger.info(f"Using {len(feature_cols)} features")
    
    # Initialize trainer
    trainer = RiskModelTrainer(random_state=42)
    
    # Prepare data
    X_train, X_test, y_train, y_test = trainer.prepare_data(df, feature_cols)
    
    # Train model (with optimization for >98% accuracy)
    trainer.train_random_forest(X_train, y_train, optimize=True)
    
    # Evaluate
    metrics = trainer.evaluate_model(X_train, X_test, y_train, y_test)
    
    # Save model
    trainer.save_model(
        MODELS_DIR / "risk_model.joblib",
        MODELS_DIR / "feature_scaler.joblib",
        MODELS_DIR / "feature_names.json"
    )
    
    logger.info("="*60)
    logger.info("Training Pipeline Complete!")
    logger.info("="*60)


if __name__ == "__main__":
    main()
