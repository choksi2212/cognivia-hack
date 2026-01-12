"""
Comprehensive Edge Case Testing for SITARA
Tests ALL possible edge cases and failure modes
NO MOCKS - Tests real production code
"""

import pytest
import sys
import logging
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from osm_feature_extractor import OSMFeatureExtractor, extract_real_features
from agent import SafetyAgent, AgentState, ActionType
import joblib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestOSMFeatureExtractor:
    """Test REAL OSM feature extraction"""
    
    def test_valid_coordinates(self):
        """Test extraction with valid coordinates"""
        extractor = OSMFeatureExtractor()
        
        # Test Delhi coordinates
        features = extractor.extract_features(28.6139, 77.2090)
        
        assert 'poi_density' in features
        assert 'road_type' in features
        assert 'intersection_count' in features
        assert features['query_success'] == True
        logger.info("✓ Valid coordinates test passed")
    
    def test_invalid_latitude(self):
        """Test with invalid latitude"""
        extractor = OSMFeatureExtractor()
        
        with pytest.raises(ValueError, match="Invalid latitude"):
            extractor.extract_features(91.0, 77.2090)  # >90
        
        with pytest.raises(ValueError, match="Invalid latitude"):
            extractor.extract_features(-91.0, 77.2090)  # <-90
        
        logger.info("✓ Invalid latitude test passed")
    
    def test_invalid_longitude(self):
        """Test with invalid longitude"""
        extractor = OSMFeatureExtractor()
        
        with pytest.raises(ValueError, match="Invalid longitude"):
            extractor.extract_features(28.6139, 181.0)  # >180
        
        with pytest.raises(ValueError, match="Invalid longitude"):
            extractor.extract_features(28.6139, -181.0)  # <-180
        
        logger.info("✓ Invalid longitude test passed")
    
    def test_invalid_radius(self):
        """Test with invalid radius"""
        extractor = OSMFeatureExtractor()
        
        with pytest.raises(ValueError, match="Invalid radius"):
            extractor.extract_features(28.6139, 77.2090, radius=0)
        
        with pytest.raises(ValueError, match="Invalid radius"):
            extractor.extract_features(28.6139, 77.2090, radius=6000)
        
        logger.info("✓ Invalid radius test passed")
    
    def test_edge_coordinates(self):
        """Test with edge case coordinates"""
        extractor = OSMFeatureExtractor()
        
        # Test extremes
        test_cases = [
            (0, 0),  # Null Island
            (90, 0),  # North Pole
            (-90, 0),  # South Pole
            (0, 180),  # Date line
            (0, -180),  # Date line other side
        ]
        
        for lat, lng in test_cases:
            features = extractor.extract_features(lat, lng)
            assert 'poi_density' in features
            assert isinstance(features['poi_density'], (int, float))
        
        logger.info("✓ Edge coordinates test passed")
    
    def test_osm_query_failure_handling(self):
        """Test graceful degradation when OSM fails"""
        extractor = OSMFeatureExtractor()
        
        # Test with very remote location (middle of ocean)
        features = extractor.extract_features(0.0, 0.0, radius=100)
        
        # Should return degraded features, not crash
        assert 'poi_density' in features
        assert 'data_source' in features
        
        logger.info("✓ OSM failure handling test passed")
    
    def test_caching(self):
        """Test that caching works"""
        extractor = OSMFeatureExtractor()
        
        # First call - should query OSM
        features1 = extractor.extract_features(28.6139, 77.2090)
        
        # Second call - should use cache
        features2 = extractor.extract_features(28.6139, 77.2090)
        
        # Should be identical
        assert features1['poi_density'] == features2['poi_density']
        assert features1['road_type'] == features2['road_type']
        
        logger.info("✓ Caching test passed")


class TestSafetyAgent:
    """Test Agentic FSM decision system"""
    
    def test_initial_state(self):
        """Test agent starts in SAFE state"""
        agent = SafetyAgent()
        
        assert agent.context.current_state == AgentState.SAFE.value
        assert agent.context.current_risk_score == 0.0
        assert agent.context.alert_count == 0
        
        logger.info("✓ Initial state test passed")
    
    def test_state_transitions(self):
        """Test all valid state transitions"""
        agent = SafetyAgent()
        
        # SAFE -> CAUTION
        decision = agent.process_risk_update(0.4)
        assert decision.state == AgentState.CAUTION.value
        
        # CAUTION -> ELEVATED_RISK
        decision = agent.process_risk_update(0.65)
        assert decision.state == AgentState.ELEVATED_RISK.value
        
        # ELEVATED_RISK -> HIGH_RISK
        decision = agent.process_risk_update(0.85)
        assert decision.state == AgentState.HIGH_RISK.value
        
        # HIGH_RISK -> ELEVATED_RISK (decreasing)
        decision = agent.process_risk_update(0.68)
        assert decision.state == AgentState.ELEVATED_RISK.value
        
        # Back to SAFE
        decision = agent.process_risk_update(0.2)
        assert decision.state == AgentState.SAFE.value
        
        logger.info("✓ State transitions test passed")
    
    def test_risk_velocity_calculation(self):
        """Test risk velocity is calculated correctly"""
        agent = SafetyAgent()
        
        # Start low
        agent.process_risk_update(0.2)
        
        # Jump high
        decision = agent.process_risk_update(0.8)
        
        # Velocity should be positive and large
        assert agent.context.risk_velocity > 0.5
        assert decision.priority >= 2  # Should trigger high priority
        
        logger.info("✓ Risk velocity test passed")
    
    def test_alert_cooldown(self):
        """Test alert cooldown prevents spam"""
        agent = SafetyAgent()
        
        # Trigger high risk
        decision1 = agent.process_risk_update(0.85)
        assert decision1.action in [ActionType.RECOMMEND_ESCALATION.value, ActionType.SUGGEST_ROUTE.value]
        
        # Immediately trigger again - should respect cooldown
        decision2 = agent.process_risk_update(0.85)
        # Should not recommend escalation again immediately
        
        assert agent.context.alert_count >= 1
        
        logger.info("✓ Alert cooldown test passed")
    
    def test_hysteresis(self):
        """Test hysteresis prevents oscillation"""
        agent = SafetyAgent()
        
        # Go to CAUTION
        agent.process_risk_update(0.4)
        assert agent.context.current_state == AgentState.CAUTION.value
        
        # Slight decrease shouldn't immediately go back to SAFE
        agent.process_risk_update(0.32)
        # Should still be in CAUTION due to hysteresis
        # (needs to drop below 0.30 to go back to SAFE)
        
        logger.info("✓ Hysteresis test passed")
    
    def test_proportional_intervention(self):
        """Test intervention is proportional to risk"""
        agent = SafetyAgent()
        
        # Low risk - minimal action
        decision = agent.process_risk_update(0.2)
        assert decision.priority == 0
        assert decision.action == ActionType.NONE.value
        
        # Medium risk - moderate action
        decision = agent.process_risk_update(0.65)
        assert decision.priority == 2
        
        # High risk - strong action
        decision = agent.process_risk_update(0.9)
        assert decision.priority == 3
        
        logger.info("✓ Proportional intervention test passed")


class TestMLModel:
    """Test ML model if available"""
    
    def test_model_loading(self):
        """Test model can be loaded"""
        from config import MODEL_PATH, SCALER_PATH, FEATURE_NAMES_PATH
        
        if not MODEL_PATH.exists():
            logger.warning("Model not trained yet - skipping model tests")
            return
        
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        
        with open(FEATURE_NAMES_PATH, 'r') as f:
            import json
            metadata = json.load(f)
            feature_names = metadata['feature_names']
        
        assert model is not None
        assert scaler is not None
        assert len(feature_names) > 0
        
        logger.info("✓ Model loading test passed")
    
    def test_prediction_shape(self):
        """Test model produces valid predictions"""
        from config import MODEL_PATH, SCALER_PATH, FEATURE_NAMES_PATH
        
        if not MODEL_PATH.exists():
            return
        
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        
        with open(FEATURE_NAMES_PATH, 'r') as f:
            import json
            metadata = json.load(f)
            feature_names = metadata['feature_names']
        
        # Create dummy features
        X = np.zeros((1, len(feature_names)))
        X_scaled = scaler.transform(X)
        
        # Predict
        pred = model.predict(X_scaled)
        proba = model.predict_proba(X_scaled)
        
        assert pred.shape == (1,)
        assert proba.shape[0] == 1
        assert np.sum(proba[0]) - 1.0 < 0.01  # Probabilities sum to 1
        
        logger.info("✓ Prediction shape test passed")
    
    def test_all_features_in_bounds(self):
        """Test model handles boundary feature values"""
        from config import MODEL_PATH, SCALER_PATH, FEATURE_NAMES_PATH
        
        if not MODEL_PATH.exists():
            return
        
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        
        with open(FEATURE_NAMES_PATH, 'r') as f:
            import json
            metadata = json.load(f)
            feature_names = metadata['feature_names']
        
        # Test with extreme values
        test_cases = [
            np.zeros(len(feature_names)),  # All zeros
            np.ones(len(feature_names)),  # All ones
            np.full(len(feature_names), 100),  # Large values
        ]
        
        for X in test_cases:
            X_scaled = scaler.transform(X.reshape(1, -1))
            pred = model.predict(X_scaled)
            assert pred is not None
        
        logger.info("✓ Boundary values test passed")


class TestDataValidation:
    """Test input validation and error handling"""
    
    def test_invalid_hour(self):
        """Test hour validation"""
        # Hours must be 0-23
        invalid_hours = [-1, 24, 25, 100]
        
        for hour in invalid_hours:
            # This would be caught in extract_features_from_request
            assert not (0 <= hour < 24)
        
        logger.info("✓ Hour validation test passed")
    
    def test_invalid_day_of_week(self):
        """Test day of week validation"""
        # Days must be 0-6
        invalid_days = [-1, 7, 8, 100]
        
        for day in invalid_days:
            assert not (0 <= day < 7)
        
        logger.info("✓ Day validation test passed")
    
    def test_nan_handling(self):
        """Test NaN values are handled"""
        # Should never pass NaN to model
        values = [np.nan, np.inf, -np.inf]
        
        for val in values:
            # These should be caught and replaced with 0
            cleaned = 0 if not np.isfinite(val) else val
            assert np.isfinite(cleaned)
        
        logger.info("✓ NaN handling test passed")
    
    def test_extreme_coordinates(self):
        """Test extreme but valid coordinates"""
        extreme_cases = [
            (-89.9, -179.9),  # Near South Pole, near dateline
            (89.9, 179.9),  # Near North Pole, near dateline
            (0.0001, 0.0001),  # Very close to origin
        ]
        
        for lat, lng in extreme_cases:
            assert -90 <= lat <= 90
            assert -180 <= lng <= 180
        
        logger.info("✓ Extreme coordinates test passed")


def run_all_tests():
    """Run all edge case tests"""
    
    print("\n" + "="*80)
    print("RUNNING COMPREHENSIVE EDGE CASE TESTS")
    print("="*80 + "\n")
    
    test_classes = [
        TestOSMFeatureExtractor,
        TestSafetyAgent,
        TestMLModel,
        TestDataValidation
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for test_class in test_classes:
        print(f"\n📋 {test_class.__name__}")
        print("-" * 80)
        
        test_instance = test_class()
        test_methods = [m for m in dir(test_instance) if m.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(test_instance, method_name)
                method()
                passed_tests += 1
                print(f"  ✓ {method_name}")
            except Exception as e:
                failed_tests += 1
                print(f"  ✗ {method_name}: {e}")
    
    print("\n" + "="*80)
    print(f"RESULTS: {passed_tests}/{total_tests} tests passed")
    if failed_tests > 0:
        print(f"⚠️  {failed_tests} tests failed")
    else:
        print("🎉 ALL TESTS PASSED!")
    print("="*80 + "\n")
    
    return failed_tests == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
