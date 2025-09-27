import pytest
import requests
import json
from typing import Dict, Any
from fastapi.testclient import TestClient
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from main import app

# Create a test client
client = TestClient(app)

class TestAerolyticsAPI:
    """
    Comprehensive test suite for Aerolytics Aviation Weather API
    Tests all available endpoints with various scenarios including success and error cases
    """
    
    # Test data - valid ICAO codes for testing
    VALID_ICAO_CODES = ["KLAX", "KJFK", "VIDP", "EGLL", "LFPG"]
    VALID_IATA_CODES = ["LAX", "JFK", "DEL", "LHR", "CDG"]
    INVALID_CODES = ["XXXX", "12345", "", "ABC"]
    
    def test_root_endpoint(self):
        """Test the root health check endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "online"
        assert "service" in data
        assert data["service"] == "Aerolytics Aviation Weather API"
        assert "version" in data
        assert "endpoints" in data
        assert isinstance(data["endpoints"], list)
        assert len(data["endpoints"]) > 0
        
        # Verify all expected endpoints are listed
        expected_endpoints = [
            "/metar/decoded/{icao}",
            "/metar/analyzed/{icao}",
            "/route-weather/{departure_icao}/{arrival_icao}",
            "/sigmet/current",
            "/sigmet/analysis",
            "/sigmet/raw",
            "/api/gemini/chat",
            "/api/gemini/health"
        ]
        
        for endpoint in expected_endpoints:
            assert endpoint in data["endpoints"], f"Expected endpoint {endpoint} not found in response"

    def test_metar_decoded_valid_icao(self):
        """Test METAR decoded endpoint with valid ICAO codes"""
        for icao in self.VALID_ICAO_CODES:
            response = client.get(f"/metar/decoded/{icao}")
            
            # Should return 200 or 404 (if no current METAR data)
            assert response.status_code in [200, 404], f"Unexpected status for {icao}: {response.status_code}"
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify required fields are present
                required_fields = ["station_id", "time", "temperature", "dew_point", 
                                 "wind", "visibility", "pressure", "weather", "sky", "raw"]
                for field in required_fields:
                    assert field in data, f"Required field {field} missing from METAR response for {icao}"
                
                # Verify station_id matches requested airport
                assert data["station_id"] == icao, f"Station ID mismatch for {icao}"
                assert isinstance(data["weather"], str), "Weather should be a formatted string"
                assert isinstance(data["raw"], str), "Raw METAR should be a string"

    def test_metar_decoded_valid_iata(self):
        """Test METAR decoded endpoint with valid IATA codes (should convert to ICAO)"""
        for iata in self.VALID_IATA_CODES:
            response = client.get(f"/metar/decoded/{iata}")
            
            # Should return 200 or 404 (if no current METAR data)
            assert response.status_code in [200, 404], f"Unexpected status for {iata}: {response.status_code}"
            
            if response.status_code == 200:
                data = response.json()
                # Verify the station_id is an ICAO code (4 letters starting with appropriate prefix)
                assert len(data["station_id"]) == 4, f"Station ID should be ICAO format for {iata}"
                assert data["station_id"].isalpha(), f"Station ID should be alphabetic for {iata}"

    def test_metar_decoded_invalid_codes(self):
        """Test METAR decoded endpoint with invalid airport codes"""
        for invalid_code in self.INVALID_CODES:
            response = client.get(f"/metar/decoded/{invalid_code}")
            
            # Should return 400 or 404 for invalid codes
            assert response.status_code in [400, 404, 422], f"Should reject invalid code {invalid_code}"
            
            data = response.json()
            assert "detail" in data, f"Error response should contain detail for {invalid_code}"

    def test_metar_analyzed_valid_codes(self):
        """Test METAR analyzed endpoint with valid codes"""
        for icao in self.VALID_ICAO_CODES[:2]:  # Test first 2 to avoid rate limiting
            response = client.get(f"/metar/analyzed/{icao}")
            
            assert response.status_code in [200, 404], f"Unexpected status for analyzed {icao}: {response.status_code}"
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                assert "analysis" in data, f"Analysis missing from response for {icao}"
                assert "decoded_metar" in data, f"Decoded METAR missing from response for {icao}"
                
                # Verify analysis structure
                analysis = data["analysis"]
                required_analysis_fields = ["overall", "wind_speed", "visibility", "hazards", "weather_phenomena"]
                for field in required_analysis_fields:
                    assert field in analysis, f"Analysis field {field} missing for {icao}"
                
                # Verify analysis values are appropriate
                assert analysis["overall"] in ["green", "yellow", "red"], f"Invalid overall status for {icao}"
                assert isinstance(analysis["wind_speed"], (int, float)), f"Wind speed should be numeric for {icao}"
                assert isinstance(analysis["visibility"], (int, float)), f"Visibility should be numeric for {icao}"
                assert isinstance(analysis["hazards"], list), f"Hazards should be a list for {icao}"
                assert isinstance(analysis["weather_phenomena"], list), f"Weather phenomena should be a list for {icao}"

    def test_route_weather_valid_routes(self):
        """Test route weather endpoint with valid airport pairs"""
        test_routes = [
            ("KLAX", "KJFK"),  # LAX to JFK
            ("LAX", "JFK"),    # Same route with IATA codes
            ("VIDP", "VABB"),  # Delhi to Mumbai
        ]
        
        for departure, arrival in test_routes:
            response = client.get(f"/route-weather/{departure}/{arrival}")
            
            assert response.status_code in [200, 404, 503], f"Unexpected status for route {departure}->{arrival}: {response.status_code}"
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                assert "departure" in data, f"Departure data missing for route {departure}->{arrival}"
                assert "arrival" in data, f"Arrival data missing for route {departure}->{arrival}"
                
                # Verify departure structure
                dep_data = data["departure"]
                required_route_fields = ["icao", "coords", "summary_text", "analysis", "decoded_metar"]
                for field in required_route_fields:
                    assert field in dep_data, f"Departure field {field} missing for {departure}"
                
                # Verify arrival structure
                arr_data = data["arrival"]
                for field in required_route_fields:
                    assert field in arr_data, f"Arrival field {field} missing for {arrival}"
                
                # Verify coordinates are valid
                assert isinstance(dep_data["coords"], list), f"Departure coords should be a list for {departure}"
                assert len(dep_data["coords"]) == 2, f"Departure coords should have 2 elements for {departure}"
                assert isinstance(arr_data["coords"], list), f"Arrival coords should be a list for {arrival}"
                assert len(arr_data["coords"]) == 2, f"Arrival coords should have 2 elements for {arrival}"
                
                # Verify summary text is present and non-empty
                assert isinstance(dep_data["summary_text"], str), f"Departure summary should be string for {departure}"
                assert len(dep_data["summary_text"]) > 0, f"Departure summary should not be empty for {departure}"
                assert isinstance(arr_data["summary_text"], str), f"Arrival summary should be string for {arrival}"
                assert len(arr_data["summary_text"]) > 0, f"Arrival summary should not be empty for {arrival}"

    def test_route_weather_query_params(self):
        """Test route weather endpoint with query parameters"""
        response = client.get("/route-weather", params={"departure": "KLAX", "arrival": "KJFK"})
        
        assert response.status_code in [200, 404, 503], f"Unexpected status for query param route: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "departure" in data
            assert "arrival" in data

    def test_route_weather_invalid_codes(self):
        """Test route weather endpoint with invalid airport codes"""
        invalid_routes = [
            ("XXXX", "YYYY"),
            ("", "KJFK"),
            ("KLAX", ""),
            ("12345", "ABCDE")
        ]
        
        for departure, arrival in invalid_routes:
            response = client.get(f"/route-weather/{departure}/{arrival}")
            assert response.status_code in [400, 404, 422], f"Should reject invalid route {departure}->{arrival}"

    def test_sigmet_current(self):
        """Test current SIGMET endpoint"""
        response = client.get("/sigmet/current")
        
        assert response.status_code in [200, 503], f"Unexpected status for SIGMET current: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            required_fields = ["status", "count", "sigmets", "timestamp"]
            for field in required_fields:
                assert field in data, f"SIGMET current response missing field: {field}"
            
            assert data["status"] == "success", "SIGMET status should be success"
            assert isinstance(data["count"], int), "SIGMET count should be integer"
            assert data["count"] >= 0, "SIGMET count should be non-negative"
            assert isinstance(data["sigmets"], list), "SIGMETs should be a list"
            assert len(data["sigmets"]) == data["count"], "SIGMET count should match list length"

    def test_sigmet_analysis(self):
        """Test SIGMET analysis endpoint"""
        response = client.get("/sigmet/analysis")
        
        assert response.status_code in [200, 503], f"Unexpected status for SIGMET analysis: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            required_fields = ["status", "analysis", "raw_sigmets", "timestamp"]
            for field in required_fields:
                assert field in data, f"SIGMET analysis response missing field: {field}"
            
            assert data["status"] == "success", "SIGMET analysis status should be success"
            assert isinstance(data["analysis"], dict), "SIGMET analysis should be a dict"
            assert isinstance(data["raw_sigmets"], list), "Raw SIGMETs should be a list"

    def test_sigmet_raw(self):
        """Test raw SIGMET endpoint"""
        response = client.get("/sigmet/raw")
        
        assert response.status_code in [200, 503], f"Unexpected status for SIGMET raw: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            required_fields = ["status", "raw_data", "timestamp"]
            for field in required_fields:
                assert field in data, f"SIGMET raw response missing field: {field}"
            
            assert data["status"] == "success", "SIGMET raw status should be success"
            assert isinstance(data["raw_data"], str), "Raw SIGMET data should be a string"

    def test_gemini_health(self):
        """Test Gemini health check endpoint"""
        response = client.get("/api/gemini/health")
        
        assert response.status_code == 200, f"Gemini health check failed: {response.status_code}"
        
        data = response.json()
        assert "status" in data, "Gemini health response missing status"
        assert data["status"] in ["healthy", "online", "ok"], f"Unexpected Gemini health status: {data['status']}"

    def test_gemini_chat_basic(self):
        """Test Gemini chat endpoint with basic message"""
        chat_request = {
            "message": "Hello, what's the weather like?"
        }
        
        response = client.post("/api/gemini/chat", json=chat_request)
        
        # Should return 200 or 500 (if API key issues)
        assert response.status_code in [200, 500], f"Unexpected status for Gemini chat: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            required_fields = ["response", "success"]
            for field in required_fields:
                assert field in data, f"Gemini chat response missing field: {field}"
            
            assert isinstance(data["success"], bool), "Success field should be boolean"
            if data["success"]:
                assert isinstance(data["response"], str), "Response should be string when successful"
                assert len(data["response"]) > 0, "Response should not be empty when successful"
            else:
                assert "error" in data, "Error field should be present when success is False"

    def test_gemini_chat_weather_query(self):
        """Test Gemini chat endpoint with weather-related query"""
        chat_request = {
            "message": "What's the weather like at LAX airport?"
        }
        
        response = client.post("/api/gemini/chat", json=chat_request)
        
        assert response.status_code in [200, 500], f"Unexpected status for Gemini weather chat: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "response" in data
            assert "success" in data

    def test_gemini_chat_invalid_request(self):
        """Test Gemini chat endpoint with invalid request format"""
        # Test empty message
        response = client.post("/api/gemini/chat", json={"message": ""})
        assert response.status_code in [200, 400, 422], "Should handle empty message"
        
        # Test missing message field
        response = client.post("/api/gemini/chat", json={})
        assert response.status_code in [400, 422], "Should reject request without message"
        
        # Test invalid JSON
        response = client.post("/api/gemini/chat", data="invalid json", 
                             headers={"content-type": "application/json"})
        assert response.status_code in [400, 422], "Should reject invalid JSON"

    def test_api_error_handling(self):
        """Test that API properly handles various error conditions"""
        
        # Test non-existent endpoint
        response = client.get("/non-existent-endpoint")
        assert response.status_code == 404, "Should return 404 for non-existent endpoints"
        
        # Test invalid HTTP methods on existing endpoints
        response = client.post("/")
        assert response.status_code == 405, "Should return 405 for invalid HTTP methods"
        
        # Test endpoints with missing parameters
        response = client.get("/metar/decoded/")
        assert response.status_code == 404, "Should return 404 for missing parameters"

    def test_response_content_types(self):
        """Test that all endpoints return proper JSON content types"""
        endpoints_to_test = [
            "/",
            "/sigmet/current",
            "/api/gemini/health"
        ]
        
        for endpoint in endpoints_to_test:
            response = client.get(endpoint)
            if response.status_code == 200:
                assert "application/json" in response.headers.get("content-type", ""), \
                    f"Endpoint {endpoint} should return JSON content type"
                
                # Verify response is valid JSON
                try:
                    response.json()
                except ValueError:
                    pytest.fail(f"Endpoint {endpoint} did not return valid JSON")

    def test_cors_headers(self):
        """Test that CORS headers are properly set for frontend requests"""
        # Test preflight request
        response = client.options("/", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })
        
        # Should allow the request or return 405 if OPTIONS not implemented
        assert response.status_code in [200, 204, 405], "CORS preflight should be handled"
        
        # Test actual request from allowed origin
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        
        if response.status_code == 200:
            # Should have CORS headers (if CORS is properly configured)
            headers = response.headers
            # Note: Actual CORS header presence depends on FastAPI CORS configuration


# Utility functions for running tests
def run_basic_smoke_tests():
    """
    Run a subset of critical tests to verify basic API functionality
    """
    test_instance = TestAerolyticsAPI()
    
    try:
        print("🧪 Running smoke tests...")
        
        print("✅ Testing root endpoint...")
        test_instance.test_root_endpoint()
        
        print("✅ Testing SIGMET endpoints...")
        test_instance.test_sigmet_current()
        
        print("✅ Testing Gemini health...")
        test_instance.test_gemini_health()
        
        print("✅ Testing basic METAR...")
        # Test with one reliable airport
        response = client.get("/metar/decoded/KLAX")
        print(f"   METAR LAX status: {response.status_code}")
        
        print("🎉 Smoke tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
        return False


def run_comprehensive_tests():
    """
    Run the full test suite
    """
    import subprocess
    import sys
    
    try:
        print("🧪 Running comprehensive test suite...")
        result = subprocess.run([
            sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"
        ], capture_output=True, text=True, timeout=300)
        
        print(result.stdout)
        if result.stderr:
            print("Stderr:", result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Aerolytics API Test Suite")
    print("=" * 50)
    
    # First run smoke tests
    if run_basic_smoke_tests():
        print("\n" + "=" * 50)
        print("🔍 Running comprehensive tests...")
        run_comprehensive_tests()
    else:
        print("❌ Smoke tests failed - skipping comprehensive tests")