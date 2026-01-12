"""
Feature Engineering Module for SITARA
Combines spatial (OSM), temporal, and crime data features
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging
from datetime import datetime, time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Creates features for risk prediction model"""
    
    def __init__(self):
        self.feature_names = []
    
    def create_temporal_features(self, df: pd.DataFrame, datetime_col: str = None) -> pd.DataFrame:
        """Create time-based features"""
        
        if datetime_col and datetime_col in df.columns:
            df['datetime'] = pd.to_datetime(df[datetime_col])
        else:
            # Create synthetic temporal features for training
            df['hour'] = np.random.randint(0, 24, len(df))
            df['day_of_week'] = np.random.randint(0, 7, len(df))
        
        if 'hour' not in df.columns and 'datetime' in df.columns:
            df['hour'] = df['datetime'].dt.hour
            df['day_of_week'] = df['datetime'].dt.dayofweek
        
        # Time of day categories
        def categorize_time(hour):
            if 6 <= hour < 12:
                return 'morning'
            elif 12 <= hour < 17:
                return 'afternoon'
            elif 17 <= hour < 21:
                return 'evening'
            elif 21 <= hour < 24:
                return 'night'
            else:
                return 'late_night'
        
        if 'hour' in df.columns:
            df['time_of_day'] = df['hour'].apply(categorize_time)
            
            # Binary features
            df['is_night'] = (df['hour'] >= 21) | (df['hour'] < 6)
            df['is_evening'] = (df['hour'] >= 17) & (df['hour'] < 21)
            df['is_late_night'] = (df['hour'] >= 0) & (df['hour'] < 6)
            df['is_weekend'] = df['day_of_week'].isin([5, 6])
        
        return df
    
    def create_spatial_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create synthetic spatial features (OSM-like)"""
        
        n = len(df)
        
        # Road type distribution (simulated)
        road_types = ['highway', 'main_road', 'residential', 'alley', 'footpath']
        df['road_type'] = np.random.choice(road_types, n, p=[0.1, 0.2, 0.4, 0.2, 0.1])
        
        # POI density (points of interest per 500m radius)
        df['poi_density'] = np.random.exponential(scale=5, size=n)
        df['police_station_distance'] = np.random.exponential(scale=2000, size=n)  # meters
        df['hospital_distance'] = np.random.exponential(scale=1500, size=n)
        
        # Connectivity features
        df['intersection_count'] = np.random.poisson(lam=3, size=n)
        df['dead_end_nearby'] = np.random.choice([0, 1], n, p=[0.8, 0.2])
        
        # Lighting proxy (higher in main roads)
        road_type_lighting = {
            'highway': 0.9,
            'main_road': 0.8,
            'residential': 0.6,
            'alley': 0.3,
            'footpath': 0.2
        }
        df['lighting_score'] = df['road_type'].map(road_type_lighting)
        
        # Crowd density (synthetic)
        df['crowd_density'] = np.random.exponential(scale=20, size=n)
        
        # Isolation score (inverse of connectivity and POI density)
        df['isolation_score'] = (
            (1 / (df['poi_density'] + 1)) * 
            (1 / (df['intersection_count'] + 1)) * 
            (df['dead_end_nearby'] + 0.5)
        )
        df['isolation_score'] = (df['isolation_score'] - df['isolation_score'].min()) / \
                                 (df['isolation_score'].max() - df['isolation_score'].min())
        
        return df
    
    def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create interaction features between spatial and temporal"""
        
        # Night + isolation = higher risk
        if 'is_night' in df.columns and 'isolation_score' in df.columns:
            df['night_isolation'] = df['is_night'].astype(int) * df['isolation_score']
        
        # Evening + alley = moderate risk
        if 'is_evening' in df.columns and 'road_type' in df.columns:
            df['evening_alley'] = (df['is_evening'].astype(int) * 
                                   (df['road_type'] == 'alley').astype(int))
        
        # Low POI + night
        if 'poi_density' in df.columns and 'is_night' in df.columns:
            df['night_low_poi'] = df['is_night'].astype(int) * (df['poi_density'] < 3).astype(int)
        
        # Distance to police + night
        if 'police_station_distance' in df.columns and 'is_night' in df.columns:
            df['night_far_police'] = df['is_night'].astype(int) * (df['police_station_distance'] > 1000).astype(int)
        
        return df
    
    def encode_categorical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """One-hot encode categorical features"""
        
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Remove label columns
        exclude = ['risk_label', 'state_ut', 'district', 'state', 'time_of_day']
        categorical_cols = [col for col in categorical_cols if col not in exclude]
        
        if categorical_cols:
            df = pd.get_dummies(df, columns=categorical_cols, prefix=categorical_cols, drop_first=True)
        
        # Encode time_of_day if present
        if 'time_of_day' in df.columns:
            time_mapping = {
                'morning': 0,
                'afternoon': 1,
                'evening': 2,
                'night': 3,
                'late_night': 4
            }
            df['time_of_day_encoded'] = df['time_of_day'].map(time_mapping)
        
        return df
    
    def prepare_training_data(self, district_data: pd.DataFrame, 
                             location_mapping: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Prepare complete training dataset
        
        Combines:
        - Crime statistics (location-based risk)
        - Temporal features (time patterns)
        - Spatial features (OSM-like)
        - Interaction features
        """
        
        logger.info("Starting feature engineering pipeline...")
        
        # Create synthetic spatial samples
        # For each location in mapping, create multiple time-based samples
        samples_per_location = 50  # Creates diverse training examples
        
        expanded_samples = []
        
        for idx, row in location_mapping.iterrows():
            for _ in range(samples_per_location):
                sample = row.to_dict()
                expanded_samples.append(sample)
        
        df = pd.DataFrame(expanded_samples)
        logger.info(f"Created {len(df)} training samples from {len(location_mapping)} locations")
        
        # Add temporal features
        df = self.create_temporal_features(df)
        
        # Add spatial features
        df = self.create_spatial_features(df)
        
        # Add interaction features
        df = self.create_interaction_features(df)
        
        # Encode categorical features
        df = self.encode_categorical_features(df)
        
        # Identify feature columns (exclude metadata and labels)
        exclude_cols = [
            'state_ut', 'district', 'state', 'risk_label', 'risk_score',
            'datetime', 'time_of_day', 'year'
        ]
        
        all_cols = df.columns.tolist()
        feature_cols = [col for col in all_cols if col not in exclude_cols]
        
        # Ensure all features are numeric
        for col in feature_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Fill any remaining NaNs
        df[feature_cols] = df[feature_cols].fillna(0)
        
        # Ensure risk_label exists
        if 'risk_label' not in df.columns:
            # Create from risk_score
            if 'risk_score' in df.columns:
                df['risk_label'] = pd.cut(
                    df['risk_score'],
                    bins=[0, 0.33, 0.66, 1.0],
                    labels=['low', 'medium', 'high'],
                    include_lowest=True
                )
            else:
                raise ValueError("No risk labels or scores found!")
        
        self.feature_names = feature_cols
        
        logger.info(f"Feature engineering complete: {len(feature_cols)} features")
        logger.info(f"Features: {feature_cols[:10]}... (showing first 10)")
        
        return df, feature_cols


def main():
    """Test feature engineering"""
    from config import MODELS_DIR
    
    # Load preprocessed data
    location_mapping = pd.read_csv(MODELS_DIR / "location_risk_mapping.csv")
    
    engineer = FeatureEngineer()
    training_data, feature_cols = engineer.prepare_training_data(
        pd.DataFrame(),  # Not using district_data directly
        location_mapping
    )
    
    # Save training data
    training_data.to_csv(MODELS_DIR / "training_data.csv", index=False)
    
    logger.info(f"Training data saved: {training_data.shape}")
    logger.info(f"Risk label distribution:\n{training_data['risk_label'].value_counts()}")


if __name__ == "__main__":
    main()
