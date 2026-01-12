"""
FastAPI Backend for SITARA
Agentic Situational Risk Intelligence Platform
"""

import joblib
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import numpy as np
import pandas as pd

from agent import SafetyAgent, AgentDecision
from config import MODEL_PATH, SCALER_PATH, FEATURE_NAMES_PATH, AGENT_STATE_PATH

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SITARA API",
    description="Agentic Situational Risk Intelligence Platform for Women's Safety",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and agent
model = None
scaler = None
feature_names = []
agent = None


# Pydantic models
class LocationInput(BaseModel):
    """Location and context input"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timestamp: Optional[str] = None
    speed: Optional[float] = 0.0
    heading: Optional[float] = None


class ContextFeatures(BaseModel):
    """Additional context features"""
    hour: Optional[int] = Field(None, ge=0, lt=24)
    day_of_week: Optional[int] = Field(None, ge=0, lt=7)
    road_type: Optional[str] = "residential"
    poi_density: Optional[float] = 5.0
    police_station_distance: Optional[float] = 1000.0
    hospital_distance: Optional[float] = 1000.0
    intersection_count: Optional[int] = 3
    dead_end_nearby: Optional[int] = 0
    lighting_score: Optional[float] = 0.6
    crowd_density: Optional[float] = 10.0


class RiskAssessmentRequest(BaseModel):
    """Request for risk assessment"""
    location: LocationInput
    context: Optional[ContextFeatures] = None


class RiskAssessmentResponse(BaseModel):
    """Risk assessment response"""
    risk_score: float
    risk_level: str
    agent_decision: Dict
    timestamp: str
    location: Dict


class RoutePoint(BaseModel):
    """Point in a route"""
    latitude: float
    longitude: float
    risk_score: Optional[float] = None


class RouteRequest(BaseModel):
    """Request for route safety analysis"""
    start: LocationInput
    end: LocationInput
    waypoints: Optional[List[RoutePoint]] = None


class RouteResponse(BaseModel):
    """Route analysis response"""
    route_risk_score: float
    risk_level: str
    safe_segments: List[Dict]
    risky_segments: List[Dict]
    alternative_routes: Optional[List[Dict]] = None


class AgentStateResponse(BaseModel):
    """Agent state summary"""
    current_state: str
    risk_score: float
    risk_velocity: float
    alert_count: int
    location_history_count: int


# Startup and shutdown events
@app.on_event("startup")
async def load_models():
    """Load ML model and initialize agent on startup"""
    global model, scaler, feature_names, agent
    
    try:
        # Load ML model
        if MODEL_PATH.exists():
            model = joblib.load(MODEL_PATH)
            logger.info(f"Model loaded from {MODEL_PATH}")
        else:
            logger.warning("Model not found. Please train the model first.")
        
        # Load scaler
        if SCALER_PATH.exists():
            scaler = joblib.load(SCALER_PATH)
            logger.info(f"Scaler loaded from {SCALER_PATH}")
        
        # Load feature names
        if FEATURE_NAMES_PATH.exists():
            with open(FEATURE_NAMES_PATH, 'r') as f:
                metadata = json.load(f)
                feature_names = metadata.get('feature_names', [])
                logger.info(f"Loaded {len(feature_names)} feature names")
        
        # Initialize agent
        agent = SafetyAgent(state_file=AGENT_STATE_PATH)
        logger.info("Safety agent initialized")
        
        logger.info("="*60)
        logger.info("SITARA Backend Ready")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"Error loading models: {e}")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("Shutting down SITARA backend")


# Helper functions
def extract_features_from_request(request: RiskAssessmentRequest) -> Dict:
    """Extract features from request matching training feature names"""
    
    # Get timestamp
    if request.location.timestamp:
        try:
            dt = datetime.fromisoformat(request.location.timestamp)
        except:
            dt = datetime.now()
    else:
        dt = datetime.now()
    
    # Base temporal features
    features = {
        'hour': request.context.hour if request.context and request.context.hour is not None else dt.hour,
        'day_of_week': request.context.day_of_week if request.context and request.context.day_of_week is not None else dt.weekday(),
    }
    
    # Time-based derived features
    hour = features['hour']
    features['is_night'] = int((hour >= 21) or (hour < 6))
    features['is_evening'] = int((hour >= 17) and (hour < 21))
    features['is_late_night'] = int((hour >= 0) and (hour < 6))
    features['is_weekend'] = int(features['day_of_week'] in [5, 6])
    
    # Time of day encoding
    if 6 <= hour < 12:
        time_encoded = 0
    elif 12 <= hour < 17:
        time_encoded = 1
    elif 17 <= hour < 21:
        time_encoded = 2
    elif 21 <= hour < 24:
        time_encoded = 3
    else:
        time_encoded = 4
    features['time_of_day_encoded'] = time_encoded
    
    # Spatial features (use context if provided, else defaults)
    if request.context:
        features['poi_density'] = request.context.poi_density
        features['police_station_distance'] = request.context.police_station_distance
        features['hospital_distance'] = request.context.hospital_distance
        features['intersection_count'] = request.context.intersection_count
        features['dead_end_nearby'] = request.context.dead_end_nearby
        features['lighting_score'] = request.context.lighting_score
        features['crowd_density'] = request.context.crowd_density
    else:
        # Reasonable defaults
        features['poi_density'] = 5.0
        features['police_station_distance'] = 1000.0
        features['hospital_distance'] = 1000.0
        features['intersection_count'] = 3
        features['dead_end_nearby'] = 0
        features['lighting_score'] = 0.6
        features['crowd_density'] = 10.0
    
    # Calculate isolation score
    features['isolation_score'] = (
        (1 / (features['poi_density'] + 1)) *
        (1 / (features['intersection_count'] + 1)) *
        (features['dead_end_nearby'] + 0.5)
    )
    
    # Interaction features
    features['night_isolation'] = features['is_night'] * features['isolation_score']
    features['evening_alley'] = features['is_evening'] * 0  # Would need road_type
    features['night_low_poi'] = features['is_night'] * int(features['poi_density'] < 3)
    features['night_far_police'] = features['is_night'] * int(features['police_station_distance'] > 1000)
    
    # Road type encoding (if provided)
    if request.context and request.context.road_type:
        road_type = request.context.road_type
        features['road_type_footpath'] = int(road_type == 'footpath')
        features['road_type_highway'] = int(road_type == 'highway')
        features['road_type_main_road'] = int(road_type == 'main_road')
        features['road_type_residential'] = int(road_type == 'residential')
    else:
        # Default to residential
        features['road_type_footpath'] = 0
        features['road_type_highway'] = 0
        features['road_type_main_road'] = 0
        features['road_type_residential'] = 1
    
    return features


def predict_risk(features: Dict) -> tuple[float, str]:
    """Predict risk score and level"""
    
    if model is None or scaler is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Create feature vector matching training features
    feature_vector = []
    for fname in feature_names:
        feature_vector.append(features.get(fname, 0))
    
    # Convert to numpy array
    X = np.array(feature_vector).reshape(1, -1)
    
    # Scale features
    X_scaled = scaler.transform(X)
    
    # Get prediction probabilities
    probs = model.predict_proba(X_scaled)[0]
    
    # Get class predictions
    classes = model.classes_
    
    # Calculate weighted risk score
    class_weights = {'low': 0.2, 'medium': 0.5, 'high': 0.9}
    risk_score = sum(probs[i] * class_weights.get(classes[i], 0.5) for i in range(len(classes)))
    
    # Determine risk level
    if risk_score < 0.33:
        risk_level = 'low'
    elif risk_score < 0.66:
        risk_level = 'medium'
    else:
        risk_level = 'high'
    
    return risk_score, risk_level


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "SITARA API",
        "description": "Agentic Situational Risk Intelligence Platform",
        "version": "1.0.0",
        "status": "online",
        "model_loaded": model is not None
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "agent_initialized": agent is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/assess-risk", response_model=RiskAssessmentResponse)
async def assess_risk(request: RiskAssessmentRequest):
    """
    Assess risk for a given location and context
    Returns ML risk score + agentic decision
    """
    
    try:
        # Extract features
        features = extract_features_from_request(request)
        
        # Predict risk
        risk_score, risk_level = predict_risk(features)
        
        # Get agent decision
        location_data = {
            'latitude': request.location.latitude,
            'longitude': request.location.longitude
        }
        
        decision = agent.process_risk_update(risk_score, location=location_data)
        
        response = RiskAssessmentResponse(
            risk_score=risk_score,
            risk_level=risk_level,
            agent_decision=decision.to_dict(),
            timestamp=datetime.now().isoformat(),
            location=location_data
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in risk assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-route", response_model=RouteResponse)
async def analyze_route(request: RouteRequest):
    """
    Analyze safety of a route
    Returns cumulative risk and segment-level analysis
    """
    
    try:
        # If no waypoints, create simple direct route
        if not request.waypoints:
            # In production, would use OSM routing here
            waypoints = [
                RoutePoint(latitude=request.start.latitude, longitude=request.start.longitude),
                RoutePoint(latitude=request.end.latitude, longitude=request.end.longitude)
            ]
        else:
            waypoints = request.waypoints
        
        # Assess risk for each waypoint
        segment_risks = []
        safe_segments = []
        risky_segments = []
        
        for i, point in enumerate(waypoints):
            # Create assessment request
            assessment_req = RiskAssessmentRequest(
                location=LocationInput(
                    latitude=point.latitude,
                    longitude=point.longitude
                )
            )
            
            features = extract_features_from_request(assessment_req)
            risk_score, risk_level = predict_risk(features)
            
            segment = {
                'index': i,
                'latitude': point.latitude,
                'longitude': point.longitude,
                'risk_score': risk_score,
                'risk_level': risk_level
            }
            
            segment_risks.append(risk_score)
            
            if risk_level == 'low':
                safe_segments.append(segment)
            else:
                risky_segments.append(segment)
        
        # Calculate overall route risk
        route_risk_score = np.mean(segment_risks)
        
        if route_risk_score < 0.33:
            route_risk_level = 'low'
        elif route_risk_score < 0.66:
            route_risk_level = 'medium'
        else:
            route_risk_level = 'high'
        
        response = RouteResponse(
            route_risk_score=route_risk_score,
            risk_level=route_risk_level,
            safe_segments=safe_segments,
            risky_segments=risky_segments
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in route analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agent/state", response_model=AgentStateResponse)
async def get_agent_state():
    """Get current agent state"""
    
    try:
        state_summary = agent.get_state_summary()
        return AgentStateResponse(**state_summary)
        
    except Exception as e:
        logger.error(f"Error getting agent state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agent/reset")
async def reset_agent():
    """Reset agent to initial state"""
    
    try:
        agent.reset_context()
        return {"status": "success", "message": "Agent reset to initial state"}
        
    except Exception as e:
        logger.error(f"Error resetting agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/model/info")
async def model_info():
    """Get model information and metrics"""
    
    try:
        if not FEATURE_NAMES_PATH.exists():
            raise HTTPException(status_code=404, detail="Model metadata not found")
        
        with open(FEATURE_NAMES_PATH, 'r') as f:
            metadata = json.load(f)
        
        return {
            "model_type": metadata.get("model_type"),
            "n_features": metadata.get("n_features"),
            "classes": metadata.get("classes"),
            "metrics": metadata.get("metrics"),
            "feature_count": len(metadata.get("feature_names", []))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
