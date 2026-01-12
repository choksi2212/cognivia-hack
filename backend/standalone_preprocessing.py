"""
STANDALONE DATA PREPROCESSING SCRIPT FOR SITARA
Run this script first to process all crime datasets

Usage:
    python standalone_preprocessing.py

Output:
    - models/processed_district_data.csv
    - models/location_risk_mapping.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
import logging
import re
import sys

warnings.filterwarnings('ignore')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('preprocessing.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
DATASET_DIR = Path("../DATASET")  # Adjust this path as needed
OUTPUT_DIR = Path("./models")
OUTPUT_DIR.mkdir(exist_ok=True)


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names"""
    df.columns = (df.columns.str.strip().str.lower()
                  .str.replace(' ', '_')
                  .str.replace('/', '_')
                  .str.replace('[^a-z0-9_]', '', regex=True))
    return df


def load_all_datasets(dataset_dir: Path):
    """Load all CSV files from DATASET folder"""
    datasets = {}
    csv_files = list(dataset_dir.glob("*.csv"))
    
    logger.info(f"Found {len(csv_files)} CSV files")
    
    for csv_file in csv_files:
        try:
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


def extract_district_level_data(datasets: dict):
    """Extract and merge district-level crime data"""
    
    district_dfs = []
    
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
            df = clean_column_names(df)
            
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
        combined_df = pd.concat(district_dfs, ignore_index=True, sort=False)
        logger.info(f"Combined district data shape: {combined_df.shape}")
        return combined_df
    else:
        raise ValueError("No district-level data found!")


def aggregate_crime_features(df: pd.DataFrame):
    """Aggregate crime statistics into meaningful features"""
    
    exclude_cols = ['year', 'state_ut', 'district', 'state', 'ut']
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    crime_cols = [col for col in numeric_cols if col not in exclude_cols]
    
    # Fill NaN with 0 for crime counts
    df[crime_cols] = df[crime_cols].fillna(0)
    
    # Create aggregated features
    if len(crime_cols) > 0:
        df['total_crimes'] = df[crime_cols].sum(axis=1)
        df['crime_intensity'] = df['total_crimes'] / (df['total_crimes'].max() + 1)
        
        # Violent crimes
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


def create_risk_labels(df: pd.DataFrame):
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


def create_state_district_mapping(df: pd.DataFrame):
    """Create clean state-district mapping with risk scores"""
    
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


def main():
    """Main preprocessing pipeline"""
    
    logger.info("="*80)
    logger.info("SITARA DATA PREPROCESSING - STANDALONE")
    logger.info("="*80)
    
    if not DATASET_DIR.exists():
        logger.error(f"Dataset directory not found: {DATASET_DIR}")
        logger.info("Please update DATASET_DIR path in the script")
        return 1
    
    try:
        # Step 1: Load all datasets
        logger.info("\n[1/5] Loading datasets...")
        datasets = load_all_datasets(DATASET_DIR)
        
        if not datasets:
            raise ValueError("No datasets loaded!")
        
        # Step 2: Extract district-level data
        logger.info("\n[2/5] Extracting district-level data...")
        district_data = extract_district_level_data(datasets)
        
        # Step 3: Aggregate crime features
        logger.info("\n[3/5] Aggregating crime features...")
        district_data = aggregate_crime_features(district_data)
        
        # Step 4: Create risk labels
        logger.info("\n[4/5] Creating risk labels...")
        district_data = create_risk_labels(district_data)
        
        # Step 5: Create location mapping
        logger.info("\n[5/5] Creating location mapping...")
        location_mapping = create_state_district_mapping(district_data)
        
        # Save processed data
        district_data_path = OUTPUT_DIR / "processed_district_data.csv"
        location_mapping_path = OUTPUT_DIR / "location_risk_mapping.csv"
        
        district_data.to_csv(district_data_path, index=False)
        location_mapping.to_csv(location_mapping_path, index=False)
        
        logger.info("="*80)
        logger.info("PREPROCESSING COMPLETE!")
        logger.info("="*80)
        logger.info(f"✓ District data saved: {district_data_path}")
        logger.info(f"  Shape: {district_data.shape}")
        logger.info(f"✓ Location mapping saved: {location_mapping_path}")
        logger.info(f"  Shape: {location_mapping.shape}")
        logger.info("="*80)
        logger.info("\nNext step: Run standalone_training.py")
        logger.info("="*80)
        
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ Preprocessing failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
