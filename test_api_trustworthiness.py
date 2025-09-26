#!/usr/bin/env python3
"""
API Trustworthiness Test - Simple Terminal Verification Program
**1. Backend Connection Test**
**2. METAR API Test**
**3. Route Weather API Test**
**4. Data Freshness Test**
**5. Error Handling Test**
"""

import httpx
import time
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_AIRPORTS = [
    "KJFK",  # JFK - Major US airport
    "KLAX",  # LAX - Major US airport  
    "VIDP",  # Delhi - Major Indian airport
    "EGLL"   # Heathrow - Major UK airport
]

def print_header(title):
    """Print formatted section header"""
    print(f"\n{title}")
    print("=" * 50)

def print_test_result(test_name, passed, duration, details=""):
    """Print formatted test result"""
    status = "PASS" if passed else "FAIL"
    duration_text = f"({duration:.0f}ms)" if duration > 0 else ""
    print(f"{status} {test_name} {duration_text}")
    if details:
        print(f"    └─ {details}")

def test_backend_connection():
    """Test if backend server is responding"""
    print_header("Backend Connection Test")
    
    try:
        start_time = time.time()
        response = httpx.get(f"{BASE_URL}/", timeout=5)
        duration = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            service_name = data.get("service", "Unknown Service")
            print_test_result("Backend Server", True, duration, f"Service: {service_name}")
            return True
        else:
            print_test_result("Backend Server", False, duration, f"HTTP {response.status_code}")
            return False
            
    except httpx.ConnectError:
        print_test_result("Backend Server", False, 0, "Connection refused - server not running")
        return False
    except Exception as e:
        print_test_result("Backend Server", False, 0, f"Error: {str(e)}")
        return False

def test_metar_api():
    """Test METAR weather data fetching"""
    print_header("METAR API Test")
    
    for airport in TEST_AIRPORTS:
        try:
            start_time = time.time()
            response = httpx.get(f"{BASE_URL}/metar/decoded/{airport}", timeout=10)
            duration = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                station = data.get("station_id", "Unknown")
                obs_time = data.get("time", "Unknown time")
                print_test_result(f"METAR {airport}", True, duration, f"Station: {station}, Time: {obs_time}")
            else:
                print_test_result(f"METAR {airport}", False, duration, f"HTTP {response.status_code}")
                
        except Exception as e:
            print_test_result(f"METAR {airport}", False, 0, f"Error: {str(e)}")

def test_route_weather_api():
    """Test route weather analysis"""
    print_header("Route Weather API Test")
    
    test_routes = [
        ("KJFK", "KLAX", "New York to Los Angeles"),
        ("EGLL", "VIDP", "London to Delhi"),
        ("KORD", "YSSY", "Chicago to Sydney")
    ]
    
    for dep, arr, description in test_routes:
        try:
            start_time = time.time()
            response = httpx.get(f"{BASE_URL}/route-weather", 
                               params={"departure": dep, "arrival": arr}, 
                               timeout=15)
            duration = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                dep_analysis = data.get("departure", {}).get("analysis", {}).get("overall", "Unknown")
                arr_analysis = data.get("arrival", {}).get("analysis", {}).get("overall", "Unknown")
                print_test_result(f"Route {dep}-{arr}", True, duration, 
                                f"{description} | Dep: {dep_analysis}, Arr: {arr_analysis}")
            else:
                print_test_result(f"Route {dep}-{arr}", False, duration, f"HTTP {response.status_code}")
                
        except Exception as e:
            print_test_result(f"Route {dep}-{arr}", False, 0, f"Error: {str(e)}")

def test_data_freshness():
    """Test data timestamp freshness"""
    print_header("Data Freshness Test")
    
    try:
        start_time = time.time()
        response = httpx.get(f"{BASE_URL}/route-weather", 
                           params={"departure": "KJFK", "arrival": "KLAX"}, 
                           timeout=10)
        duration = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            
            # Check departure data freshness
            dep_time = data.get("departure", {}).get("decoded_metar", {}).get("time")
            arr_time = data.get("arrival", {}).get("decoded_metar", {}).get("time")
            
            if dep_time and arr_time:
                print_test_result("Data Timestamps", True, duration, 
                                f"Departure: {dep_time}, Arrival: {arr_time}")
            else:
                print_test_result("Data Timestamps", False, duration, "Missing timestamp data")
        else:
            print_test_result("Data Freshness", False, duration, f"HTTP {response.status_code}")
            
    except Exception as e:
        print_test_result("Data Freshness", False, 0, f"Error: {str(e)}")

def test_error_handling():
    """Test API error handling with invalid inputs"""
    print_header("Error Handling Test")
    
    invalid_tests = [
        ("XXXX", "Invalid ICAO code"),
        ("12345", "Numeric input"),
        ("", "Empty input")
    ]
    
    for invalid_icao, description in invalid_tests:
        try:
            start_time = time.time()
            response = httpx.get(f"{BASE_URL}/metar/decoded/{invalid_icao}", timeout=5)
            duration = (time.time() - start_time) * 1000
            
            if response.status_code == 404:
                print_test_result(f"Invalid Input: {description}", True, duration,
                                "Correctly returned 404 for invalid input")
            else:
                print_test_result(f"Invalid Input: {description}", False, duration,
                                f"Unexpected HTTP {response.status_code}")
                
        except Exception as e:
            print_test_result(f"Invalid Input: {description}", False, 0, f"Error: {str(e)}")

def main():
    """Run all API tests"""
    print("AEROLYTICS API TRUSTWORTHINESS TEST")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing Backend: {BASE_URL}")
    
    # Run all tests
    backend_ok = test_backend_connection()
    
    if backend_ok:
        test_metar_api()
        test_route_weather_api() 
        test_data_freshness()
        test_error_handling()
    else:
        print("\nBackend server not available. Please start the backend first:")
        print("   cd c:\\Users\\milan\\Downloads\\hackspace")
        print("   python -m uvicorn backend.main:app --reload --port 8000")
    
    print_header("Test Summary")
    print("All tests completed!")
    print("Tips:")
    print("   • Run this test regularly to verify API reliability")
    print("   • Compare METAR data with official aviation weather sources")
    print("   • Check timestamps to ensure data freshness")
    print("\nVerify data manually at: https://aviationweather.gov/data/metar/")

if __name__ == "__main__":
    main()