"""
Data Preprocessing Pipeline for SITARA
Loads, cleans, and merges all crime datasets from the DATASET folder
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
import logging
from typing import Dict, List, Tuple
import re

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPreprocessor:
    """Preprocesses and combines Indian crime datasets"""
    
    def __init__(self, dataset_dir: Path):
        self.dataset_dir = dataset_dir
        self.processed_data = None
        
    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """Load all CSV files from DATASET folder"""
        datasets = {}
        csv_files = list(self.dataset_dir.glob("*.csv"))
        
        logger.info(f"Found {len(csv_files)} CSV files")
        
        for csv_file in csv_files:
            try:
                # Try different encodings
                for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
                    try:
                        df = pd.read_csv(csv_file, encoding=encoding, low_memory=False)
                        datasets[csv_file.stem] = df
                        logger.info(f"Loaded {csv_file.name}: {df.shape}")
                        break
                    except UnicodeDecodeError:
                        continue
            except Exception as e:
                logger.warning(f"Could not load {csv_file.name}: {e}")
                
        return datasets
    
    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names"""
        df.columns = (df.columns.str.strip().str.lower()
                      .str.replace(' ', '_')
                      .str.replace('/', '_')
                      .str.replace('[^a-z0-9_]', '', regex=True))
        return df
    
    def extract_district_level_data(self, datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Extract and merge district-level crime data"""
        
        district_dfs = []
        
        # Priority datasets for district-level data
        priority_patterns = [
            'district_wise_crimes_committed_ipc',
            'district_wise_crimes_committed_against_women',
            'district_wise_crimes_committed_against_sc',
            'district_wise_crimes_committed_against_st',
            'district_wise_crimes_committed_against_children'
        ]
        
        for pattern in priority_patterns:
            matching_keys = [k for k in datasets.keys() if pattern in k.lower()]
            
            for key in matching_keys:
                df = datasets[key].copy()
                df = self.clean_column_names(df)
                
                # Extract year from filename or column
                year_match = re.search(r'(\d{4})', key)
                if year_match:
                    df['year'] = int(year_match.group(1))
                elif 'year' in df.columns:
                    df['year'] = pd.to_numeric(df['year'], errors='coerce')
                
                # Identify key columns
                has_state = any(col in df.columns for col in ['state_ut', 'state'])
                has_district = 'district' in df.columns
                
                if has_state and has_district:
                    district_dfs.append(df)
                    logger.info(f"Added district data from {key}")
        
        if district_dfs:
            # Combine all district-level data
            combined_df = pd.concat(district_dfs, ignore_index=True, sort=False)
            logger.info(f"Combined district data shape: {combined_df.shape}")
            return combined_df
        else:
            logger.warning("No district-level data found")
            return pd.DataFrame()
    
    def aggregate_crime_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate crime statistics into meaningful features"""
        
        if df.empty:
            return df
        
        # Identify numeric crime columns (excluding year, state, district)
        exclude_cols = ['year', 'state_ut', 'district', 'state', 'ut']
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        crime_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        # Fill NaN with 0 for crime counts
        df[crime_cols] = df[crime_cols].fillna(0)
        
        # Create aggregated features
        if len(crime_cols) > 0:
            df['total_crimes'] = df[crime_cols].sum(axis=1)
            df['crime_intensity'] = df['total_crimes'] / (df['total_crimes'].max() + 1)
            
            # Identify violent crimes (common patterns)
            violent_patterns = ['murder', 'rape', 'kidnapping', 'assault', 'robbery', 'dacoity']
            violent_cols = [col for col in crime_cols if any(pattern in col.lower() for pattern in violent_patterns)]
            
            if violent_cols:
                df['violent_crimes'] = df[violent_cols].sum(axis=1)
                df['violent_crime_ratio'] = df['violent_crimes'] / (df['total_crimes'] + 1)
            
            # Women-specific crimes
            women_patterns = ['women', 'dowry', 'rape', 'molestation', 'sexual', 'harassment']
            women_cols = [col for col in crime_cols if any(pattern in col.lower() for pattern in women_patterns)]
            
            if women_cols:
                df['crimes_against_women'] = df[women_cols].sum(axis=1)
                df['women_crime_ratio'] = df['crimes_against_women'] / (df['total_crimes'] + 1)
        
        return df
    
    def create_risk_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create risk labels using weak supervision"""
        
        if 'crime_intensity' not in df.columns:
            logger.warning("crime_intensity not found, using default labeling")
            df['risk_label'] = 'low'
            df['risk_score'] = 0.2
            return df
        
        # Multi-factor risk scoring
        risk_score = df['crime_intensity'].copy()
        
        if 'violent_crime_ratio' in df.columns:
            risk_score += df['violent_crime_ratio'] * 0.3
        
        if 'women_crime_ratio' in df.columns:
            risk_score += df['women_crime_ratio'] * 0.4
        
        # Normalize to 0-1
        risk_score = (risk_score - risk_score.min()) / (risk_score.max() - risk_score.min() + 1e-10)
        
        df['risk_score'] = risk_score
        
        # Create categorical labels
        df['risk_label'] = pd.cut(
            risk_score,
            bins=[0, 0.33, 0.66, 1.0],
            labels=['low', 'medium', 'high'],
            include_lowest=True
        )
        
        logger.info(f"Risk label distribution:\n{df['risk_label'].value_counts()}")
        
        return df
    
    def create_state_district_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create clean state-district mapping with risk scores"""
        
        if df.empty:
            return pd.DataFrame()
        
        # Group by state and district
        group_cols = []
        if 'state_ut' in df.columns:
            group_cols.append('state_ut')
        elif 'state' in df.columns:
            group_cols.append('state')
        
        if 'district' in df.columns:
            group_cols.append('district')
        
        if not group_cols:
            logger.warning("No state/district columns found")
            return df
        
        # Aggregate by location
        agg_dict = {
            'total_crimes': 'sum',
            'violent_crimes': 'sum' if 'violent_crimes' in df.columns else 'count',
            'crimes_against_women': 'sum' if 'crimes_against_women' in df.columns else 'count',
            'risk_score': 'mean'
        }
        
        # Remove missing aggregations
        agg_dict = {k: v for k, v in agg_dict.items() if k in df.columns}
        
        location_df = df.groupby(group_cols).agg(agg_dict).reset_index()
        
        # Recreate risk labels on aggregated data
        if 'risk_score' in location_df.columns:
            location_df['risk_label'] = pd.cut(
                location_df['risk_score'],
                bins=[0, 0.33, 0.66, 1.0],
                labels=['low', 'medium', 'high'],
                include_lowest=True
            )
        
        logger.info(f"Created location mapping with {len(location_df)} locations")
        
        return location_df
    
    def process_all(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Main processing pipeline"""
        
        logger.info("="*60)
        logger.info("Starting Data Preprocessing Pipeline")
        logger.info("="*60)
        
        # Load all datasets
        datasets = self.load_all_datasets()
        
        if not datasets:
            raise ValueError("No datasets loaded!")
        
        # Extract district-level data
        district_data = self.extract_district_level_data(datasets)
        
        if district_data.empty:
            raise ValueError("Could not extract district-level data!")
        
        # Aggregate crime features
        district_data = self.aggregate_crime_features(district_data)
        
        # Create risk labels
        district_data = self.create_risk_labels(district_data)
        
        # Create location mapping
        location_mapping = self.create_state_district_mapping(district_data)
        
        logger.info("="*60)
        logger.info("Data Preprocessing Complete")
        logger.info(f"District data shape: {district_data.shape}")
        logger.info(f"Location mapping shape: {location_mapping.shape}")
        logger.info("="*60)
        
        self.processed_data = district_data
        
        return district_data, location_mapping


def main():
    """Test the preprocessing pipeline"""
    from config import DATASET_DIR, MODELS_DIR
    
    preprocessor = DataPreprocessor(DATASET_DIR)
    district_data, location_mapping = preprocessor.process_all()
    
    # Save processed data
    district_data.to_csv(MODELS_DIR / "processed_district_data.csv", index=False)
    location_mapping.to_csv(MODELS_DIR / "location_risk_mapping.csv", index=False)
    
    logger.info("Processed data saved to models directory")


if __name__ == "__main__":
    main()
