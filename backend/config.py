"""Configuration module for SITARA backend"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR.parent / "DATASET"
MODELS_DIR = BASE_DIR / "models"
CACHE_DIR = BASE_DIR / "cache"

# Ensure directories exist
MODELS_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:niklaus2212@localhost:5432/sitara"
)

# Model configuration
MODEL_PATH = MODELS_DIR / "risk_model.joblib"
SCALER_PATH = MODELS_DIR / "feature_scaler.joblib"
FEATURE_NAMES_PATH = MODELS_DIR / "feature_names.json"

# Agent configuration
AGENT_STATE_PATH = MODELS_DIR / "agent_state.json"

# Risk thresholds
RISK_THRESHOLDS = {
    "low": 0.3,
    "medium": 0.6,
    "high": 0.8
}

# Agent state machine
AGENT_STATES = {
    "SAFE": 0,
    "CAUTION": 1,
    "ELEVATED_RISK": 2,
    "HIGH_RISK": 3
}

# Feature engineering parameters
GRID_SIZE = 500  # meters
TIME_WINDOWS = ["morning", "afternoon", "evening", "night", "late_night"]

# OSM configuration
OSM_CACHE_PATH = CACHE_DIR / "osm"
OSM_CACHE_PATH.mkdir(exist_ok=True)
