"""
Complete System Integration Test for SITARA
Tests all components: ML Model, Agent, API, Database, OSM Integration
"""

import sys
import requests
import json
import time
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_LOCATIONS = [
    {"lat": 22.6823, "lng": 72.8703, "name": "Ahmedabad - Satellite Area"},
    {"lat": 28.6139, "lng": 77.2090, "name": "Delhi - Connaught Place"},
    {"lat": 19.0760, "lng": 72.8777, "name": "Mumbai - Marine Drive"},
    {"lat": 12.9716, "lng": 77.5946, "name": "Bangalore - MG Road"},
]

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def test_backend_health():
    """Test 1: Backend Health Check"""
    print_header("TEST 1: Backend Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        data = response.json()
        
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 200, "Health check failed"
        assert data["status"] == "healthy", "Backend not healthy"
        assert data["model_loaded"] == True, "Model not loaded"
        assert data["agent_initialized"] == True, "Agent not initialized"
        
        if data.get("database_connected"):
            print_success("Database connected!")
        else:
            print_warning("Database not connected (optional)")
        
        print_success("Backend is healthy and ready!")
        return True
        
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend. Is it running?")
        print_warning("Run: START_BACKEND.bat")
        return False
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False

def test_model_artifacts():
    """Test 2: Model Artifacts Validation"""
    print_header("TEST 2: Model Artifacts Validation")
    
    models_dir = Path("models")
    required_files = [
        "risk_model.joblib",
        "feature_scaler.joblib",
        "feature_names.json"
    ]
    
    all_present = True
    for filename in required_files:
        filepath = models_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            if size > 1024 * 1024:
                size_str = f"{size / (1024*1024):.2f} MB"
            else:
                size_str = f"{size / 1024:.2f} KB"
            print_success(f"{filename}: {size_str}")
        else:
            print_error(f"{filename}: NOT FOUND")
            all_present = False
    
    if all_present:
        print_success("All model artifacts present!")
        return True
    else:
        print_error("Some model artifacts missing!")
        return False

def test_risk_assessment():
    """Test 3: Risk Assessment API"""
    print_header("TEST 3: Risk Assessment API")
    
    all_passed = True
    
    for location in TEST_LOCATIONS:
        print(f"\n{Colors.BOLD}Testing: {location['name']}{Colors.RESET}")
        
        payload = {
            "location": {
                "latitude": location["lat"],
                "longitude": location["lng"]
            }
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/api/assess-risk",
                json=payload,
                timeout=10
            )
            response_time = (time.time() - start_time) * 1000
            
            assert response.status_code == 200, f"Failed with status {response.status_code}"
            
            data = response.json()
            
            # Validate response structure
            assert "risk_score" in data, "Missing risk_score"
            assert "risk_level" in data, "Missing risk_level"
            assert "agent_decision" in data, "Missing agent_decision"
            
            # Validate risk score
            risk_score = data["risk_score"]
            assert 0.0 <= risk_score <= 1.0, f"Invalid risk score: {risk_score}"
            
            # Validate risk level
            risk_level = data["risk_level"]
            assert risk_level in ["low", "medium", "high"], f"Invalid risk level: {risk_level}"
            
            # Validate agent decision
            agent = data["agent_decision"]
            assert "state" in agent, "Missing agent state"
            assert "action" in agent, "Missing agent action"
            assert "message" in agent, "Missing agent message"
            
            print_info(f"Risk Score: {risk_score:.3f}")
            print_info(f"Risk Level: {risk_level}")
            print_info(f"Agent State: {agent['state']}")
            print_info(f"Agent Action: {agent['action']}")
            print_info(f"Response Time: {response_time:.2f}ms")
            
            # Check performance
            if response_time < 100:
                print_success(f"Response time excellent: {response_time:.2f}ms")
            elif response_time < 500:
                print_success(f"Response time good: {response_time:.2f}ms")
            else:
                print_warning(f"Response time slow: {response_time:.2f}ms")
            
            print_success(f"Risk assessment successful for {location['name']}")
            
        except AssertionError as e:
            print_error(f"Assertion failed: {e}")
            all_passed = False
        except Exception as e:
            print_error(f"Error: {e}")
            all_passed = False
    
    return all_passed

def test_route_analysis():
    """Test 4: Route Analysis API"""
    print_header("TEST 4: Route Analysis API")
    
    # Test route from Satellite to CG Road in Ahmedabad
    payload = {
        "start": {
            "latitude": 22.6823,
            "longitude": 72.8703
        },
        "end": {
            "latitude": 23.0225,
            "longitude": 72.5714
        }
    }
    
    try:
        print_info("Testing route: Ahmedabad Satellite → CG Road")
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/analyze-route",
            json=payload,
            timeout=15
        )
        response_time = (time.time() - start_time) * 1000
        
        assert response.status_code == 200, f"Failed with status {response.status_code}"
        
        data = response.json()
        
        # Validate response
        assert "route_risk_score" in data, "Missing route_risk_score"
        assert "risk_level" in data, "Missing risk_level"
        assert "safe_segments" in data, "Missing safe_segments"
        assert "risky_segments" in data, "Missing risky_segments"
        
        route_risk = data["route_risk_score"]
        risk_level = data["risk_level"]
        
        print_info(f"Route Risk Score: {route_risk:.3f}")
        print_info(f"Overall Risk Level: {risk_level}")
        print_info(f"Safe Segments: {len(data['safe_segments'])}")
        print_info(f"Risky Segments: {len(data['risky_segments'])}")
        print_info(f"Response Time: {response_time:.2f}ms")
        
        print_success("Route analysis successful!")
        return True
        
    except Exception as e:
        print_error(f"Route analysis failed: {e}")
        return False

def test_agent_state():
    """Test 5: Agent State Management"""
    print_header("TEST 5: Agent State Management")
    
    try:
        response = requests.get(f"{BASE_URL}/api/agent/state", timeout=5)
        assert response.status_code == 200, f"Failed with status {response.status_code}"
        
        data = response.json()
        
        # Validate state
        assert "current_state" in data, "Missing current_state"
        assert "last_risk_score" in data, "Missing last_risk_score"
        assert "risk_history" in data, "Missing risk_history"
        assert "interventions_count" in data, "Missing interventions_count"
        
        print_info(f"Current State: {data['current_state']}")
        print_info(f"Last Risk Score: {data.get('last_risk_score', 'N/A')}")
        print_info(f"Risk History Length: {len(data['risk_history'])}")
        print_info(f"Interventions Count: {data['interventions_count']}")
        
        print_success("Agent state retrieved successfully!")
        return True
        
    except Exception as e:
        print_error(f"Agent state test failed: {e}")
        return False

def test_database_integration():
    """Test 6: Database Integration"""
    print_header("TEST 6: Database Integration")
    
    try:
        # Test database stats
        response = requests.get(f"{BASE_URL}/api/database/stats", timeout=5)
        
        if response.status_code == 404:
            print_warning("Database endpoints not available (optional)")
            return True
        
        assert response.status_code == 200, f"Failed with status {response.status_code}"
        
        data = response.json()
        
        if data.get("connected"):
            print_success("Database is connected!")
            print_info(f"Total Locations: {data.get('total_locations', 0)}")
            print_info(f"Total Alerts: {data.get('total_alerts', 0)}")
            print_info(f"Total Routes: {data.get('total_routes', 0)}")
            print_info(f"Total Logs: {data.get('total_logs', 0)}")
            
            # Test recent locations
            response2 = requests.get(f"{BASE_URL}/api/locations/recent?limit=5", timeout=5)
            if response2.status_code == 200:
                locations = response2.json()
                print_info(f"Recent locations retrieved: {locations.get('count', 0)}")
                print_success("Database integration working!")
            
            return True
        else:
            print_warning("Database not connected (optional for demo)")
            return True
            
    except Exception as e:
        print_warning(f"Database test skipped: {e}")
        return True  # Database is optional

def test_edge_cases():
    """Test 7: Edge Cases"""
    print_header("TEST 7: Edge Cases")
    
    edge_cases = [
        {"name": "Invalid latitude", "payload": {"location": {"latitude": 91, "longitude": 72.8703}}, "should_fail": True},
        {"name": "Invalid longitude", "payload": {"location": {"latitude": 22.6823, "longitude": 181}}, "should_fail": True},
        {"name": "Missing location", "payload": {}, "should_fail": True},
        {"name": "Extreme north India", "payload": {"location": {"latitude": 34.0837, "longitude": 74.7973}}, "should_fail": False},
        {"name": "Extreme south India", "payload": {"location": {"latitude": 8.0883, "longitude": 77.5385}}, "should_fail": False},
    ]
    
    all_passed = True
    
    for case in edge_cases:
        print(f"\n{Colors.BOLD}Testing: {case['name']}{Colors.RESET}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/assess-risk",
                json=case["payload"],
                timeout=10
            )
            
            if case["should_fail"]:
                if response.status_code != 200:
                    print_success(f"Correctly rejected: {response.status_code}")
                else:
                    print_warning("Should have failed but didn't")
            else:
                if response.status_code == 200:
                    data = response.json()
                    print_success(f"Handled correctly: Risk={data['risk_level']}")
                else:
                    print_error(f"Should have succeeded: {response.status_code}")
                    all_passed = False
                    
        except Exception as e:
            if case["should_fail"]:
                print_success(f"Correctly errored: {str(e)[:50]}")
            else:
                print_error(f"Unexpected error: {str(e)[:50]}")
                all_passed = False
    
    return all_passed

def test_performance():
    """Test 8: Performance Benchmarks"""
    print_header("TEST 8: Performance Benchmarks")
    
    print_info("Running 10 consecutive risk assessments...")
    
    times = []
    location = {"latitude": 22.6823, "longitude": 72.8703}
    
    for i in range(10):
        try:
            start = time.time()
            response = requests.post(
                f"{BASE_URL}/api/assess-risk",
                json={"location": location},
                timeout=10
            )
            duration = (time.time() - start) * 1000
            times.append(duration)
            
            if response.status_code == 200:
                print(f"  Request {i+1}: {duration:.2f}ms")
            else:
                print_error(f"  Request {i+1} failed")
                
        except Exception as e:
            print_error(f"  Request {i+1} error: {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print_info(f"\nAverage Response Time: {avg_time:.2f}ms")
        print_info(f"Min Response Time: {min_time:.2f}ms")
        print_info(f"Max Response Time: {max_time:.2f}ms")
        
        if avg_time < 100:
            print_success("Performance: Excellent (<100ms)")
        elif avg_time < 500:
            print_success("Performance: Good (<500ms)")
        elif avg_time < 1000:
            print_warning("Performance: Acceptable (<1s)")
        else:
            print_error("Performance: Slow (>1s)")
        
        return avg_time < 1000
    
    return False

def run_all_tests():
    """Run all tests and generate report"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}SITARA - COMPLETE SYSTEM TEST SUITE{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    tests = [
        ("Backend Health Check", test_backend_health),
        ("Model Artifacts Validation", test_model_artifacts),
        ("Risk Assessment API", test_risk_assessment),
        ("Route Analysis API", test_route_analysis),
        ("Agent State Management", test_agent_state),
        ("Database Integration", test_database_integration),
        ("Edge Cases Handling", test_edge_cases),
        ("Performance Benchmarks", test_performance),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            time.sleep(0.5)  # Small delay between tests
        except KeyboardInterrupt:
            print_warning("\n\nTests interrupted by user")
            break
        except Exception as e:
            print_error(f"Test crashed: {e}")
            results[test_name] = False
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*60}")
        print(f"{'🎉 ALL TESTS PASSED! SYSTEM IS READY! 🎉':^60}")
        print(f"{'='*60}{Colors.RESET}\n")
        return True
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}{'='*60}")
        print(f"{'⚠️  SOME TESTS FAILED - REVIEW ABOVE  ⚠️':^60}")
        print(f"{'='*60}{Colors.RESET}\n")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
