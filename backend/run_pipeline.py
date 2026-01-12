"""
Complete ML Pipeline Runner for SITARA
Runs data preprocessing, feature engineering, and model training
"""

import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run complete ML pipeline"""
    
    logger.info("="*80)
    logger.info(" SITARA ML PIPELINE")
    logger.info(" Agentic Situational Risk Intelligence Platform")
    logger.info("="*80)
    
    try:
        # Step 1: Data Preprocessing
        logger.info("\n" + "="*80)
        logger.info("STEP 1: DATA PREPROCESSING")
        logger.info("="*80)
        
        from data_preprocessing import DataPreprocessor
        from config import DATASET_DIR, MODELS_DIR
        
        preprocessor = DataPreprocessor(DATASET_DIR)
        district_data, location_mapping = preprocessor.process_all()
        
        # Save processed data
        district_data.to_csv(MODELS_DIR / "processed_district_data.csv", index=False)
        location_mapping.to_csv(MODELS_DIR / "location_risk_mapping.csv", index=False)
        
        logger.info("✓ Data preprocessing complete")
        
        # Step 2: Feature Engineering
        logger.info("\n" + "="*80)
        logger.info("STEP 2: FEATURE ENGINEERING")
        logger.info("="*80)
        
        from feature_engineering import FeatureEngineer
        
        engineer = FeatureEngineer()
        training_data, feature_cols = engineer.prepare_training_data(
            district_data,
            location_mapping
        )
        
        # Save training data
        training_data.to_csv(MODELS_DIR / "training_data.csv", index=False)
        
        logger.info("✓ Feature engineering complete")
        logger.info(f"  Training samples: {len(training_data)}")
        logger.info(f"  Features: {len(feature_cols)}")
        
        # Step 3: Model Training
        logger.info("\n" + "="*80)
        logger.info("STEP 3: MODEL TRAINING")
        logger.info("="*80)
        
        from train_model import RiskModelTrainer
        
        trainer = RiskModelTrainer(random_state=42)
        
        # Prepare data
        X_train, X_test, y_train, y_test = trainer.prepare_data(training_data, feature_cols)
        
        # Train model with optimization
        logger.info("Training Random Forest with hyperparameter optimization...")
        trainer.train_random_forest(X_train, y_train, optimize=True)
        
        # Evaluate
        metrics = trainer.evaluate_model(X_train, X_test, y_train, y_test)
        
        # Save model
        trainer.save_model(
            MODELS_DIR / "risk_model.joblib",
            MODELS_DIR / "feature_scaler.joblib",
            MODELS_DIR / "feature_names.json"
        )
        
        logger.info("✓ Model training complete")
        
        # Final Summary
        logger.info("\n" + "="*80)
        logger.info("PIPELINE COMPLETE")
        logger.info("="*80)
        logger.info(f"✓ Training Accuracy: {metrics['train_accuracy']*100:.2f}%")
        logger.info(f"✓ Test Accuracy: {metrics['test_accuracy']*100:.2f}%")
        logger.info(f"✓ Precision: {metrics['precision']:.4f}")
        logger.info(f"✓ Recall: {metrics['recall']:.4f}")
        logger.info(f"✓ F1 Score: {metrics['f1_score']:.4f}")
        
        if metrics['test_accuracy'] >= 0.98:
            logger.info("\n🎉 TARGET ACCURACY OF >98% ACHIEVED! 🎉")
        else:
            logger.info(f"\n⚠️  Accuracy: {metrics['test_accuracy']*100:.2f}% (Target: 98%+)")
        
        logger.info("\nModel saved to: backend/models/")
        logger.info("Ready to start FastAPI server!")
        logger.info("="*80)
        
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ Pipeline failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
