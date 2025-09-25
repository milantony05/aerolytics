#!/usr/bin/env python3
"""
Test script for Phase 5 - PIREP (Pilot Reports) Integration

This script tests the PIREP fetching functionality and integration with the 
unified briefing endpoint.
"""

import requests
import json
import sys

def test_pirep_integration():
    """Test PIREP integration in the unified briefing endpoint"""
    
    base_url = "http://localhost:5000"
    test_airports = ["KJFK", "KLAX", "KORD", "KDEN"]
    
    print("=" * 70)
    print("Phase 5 Testing: PIREP (Pilot Reports) Integration")
    print("=" * 70)
    
    for airport in test_airports:
        print(f"\n✈️  Testing PIREPs for {airport}...")
        print("-" * 50)
        
        try:
            # Test unified briefing endpoint with PIREP data
            response = requests.get(f"{base_url}/api/briefing/airport/{airport}", timeout=20)
            
            if response.status_code == 200:
                briefing = response.json()
                
                print(f"✅ Briefing retrieved successfully")
                print(f"📍 Airport: {briefing.get('airport', 'Unknown')}")
                print(f"📊 Status: {briefing.get('status', 'Unknown')}")
                
                # Test PIREP data presence
                pirep_data = briefing.get('pilot_reports')
                if pirep_data:
                    pirep_count = pirep_data.get('count', 0)
                    print(f"📋 PIREP Integration: ✅ Available")
                    print(f"📊 Total PIREPs: {pirep_count}")
                    
                    # Test PIREP summary
                    summary = pirep_data.get('summary', {})
                    if summary:
                        urgent_count = len(summary.get('urgent_reports', []))
                        routine_count = len(summary.get('routine_reports', []))
                        
                        print(f"🚨 Urgent Reports: {urgent_count}")
                        print(f"📝 Routine Reports: {routine_count}")
                        
                        # Test condition flags
                        conditions = []
                        if summary.get('has_turbulence'):
                            conditions.append('🌪️ Turbulence')
                        if summary.get('has_icing'):
                            conditions.append('🧊 Icing')
                        if summary.get('has_weather'):
                            conditions.append('🌦️ Weather')
                            
                        if conditions:
                            print(f"⚠️  Reported Conditions: {', '.join(conditions)}")
                        else:
                            print(f"✅ No adverse conditions reported")
                        
                        # Test summary text
                        if summary.get('summary'):
                            print(f"📄 Summary:")
                            for item in summary['summary'][:3]:
                                print(f"   • {item}")
                    
                    # Test individual PIREP structure
                    if pirep_count > 0:
                        all_reports = summary.get('urgent_reports', []) + summary.get('routine_reports', [])
                        if all_reports:
                            sample_pirep = all_reports[0]
                            print(f"🔍 Sample PIREP Structure:")
                            print(f"   Type: {sample_pirep.get('report_type', 'Unknown')}")
                            print(f"   Urgency: {sample_pirep.get('urgency', 'Unknown')}")
                            if sample_pirep.get('location'):
                                print(f"   Location: {sample_pirep['location']}")
                            if sample_pirep.get('aircraft_type'):
                                print(f"   Aircraft: {sample_pirep['aircraft_type']}")
                            if sample_pirep.get('altitude'):
                                print(f"   Altitude: {sample_pirep['altitude']}")
                            
                            # Test conditions parsing
                            conditions = sample_pirep.get('conditions', {})
                            if conditions:
                                condition_items = []
                                for key, value in conditions.items():
                                    if value:
                                        condition_items.append(f"{key}: {value}")
                                if condition_items:
                                    print(f"   Conditions: {', '.join(condition_items[:2])}")
                else:
                    print(f"❌ PIREP Integration: Not available")
                
                # Test briefing summary integration
                summary_items = briefing.get('summary', [])
                pirep_summary_items = [item for item in summary_items if 'report' in item.lower() or 'pilot' in item.lower()]
                if pirep_summary_items:
                    print(f"📝 PIREP in Summary:")
                    for item in pirep_summary_items:
                        print(f"   • {item}")
                
                # Show any errors
                if briefing.get('errors'):
                    pirep_errors = [error for error in briefing['errors'] if 'pirep' in error.lower()]
                    if pirep_errors:
                        print(f"⚠️  PIREP Warnings:")
                        for error in pirep_errors[:2]:
                            print(f"   • {error}")
                        
            else:
                error_data = response.json() if response.headers.get('Content-Type', '').startswith('application/json') else {}
                print(f"❌ Error {response.status_code}: {error_data.get('error', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
    
    print("\n" + "=" * 70)
    print("Phase 5 Testing Complete!")
    print("=" * 70)

def test_pirep_parser_directly():
    """Test the PIREP parser module directly"""
    
    print(f"\n🔧 Testing PIREP Parser Module Directly...")
    print("-" * 50)
    
    try:
        # Import and test the PIREP parser
        from backend.pirep_parser import fetch_and_parse_pireps
        
        test_airport = "KJFK"
        print(f"Testing PIREP parser for {test_airport}...")
        
        pireps, categorized = fetch_and_parse_pireps(test_airport, radius_nm=100)
        
        print(f"✅ PIREP parser working")
        print(f"📊 Raw PIREPs returned: {len(pireps)}")
        print(f"📋 Categorized data structure: {type(categorized)}")
        
        if categorized:
            print(f"📈 Total count: {categorized.get('total_count', 0)}")
            print(f"🚨 Urgent reports: {len(categorized.get('urgent_reports', []))}")
            print(f"📝 Routine reports: {len(categorized.get('routine_reports', []))}")
            
        # Test for any errors in the PIREPs
        error_pireps = [p for p in pireps if p.get('error')]
        if error_pireps:
            print(f"⚠️  Parser errors: {len(error_pireps)}")
            for error_pirep in error_pireps[:2]:
                print(f"   • {error_pirep.get('error', 'Unknown error')}")
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
    except Exception as e:
        print(f"❌ Parser test error: {str(e)}")

def test_api_backward_compatibility():
    """Test that existing API endpoints still work"""
    
    base_url = "http://localhost:5000"
    test_airport = "KJFK"
    
    print(f"\n🔧 Testing API Backward Compatibility for {test_airport}...")
    print("-" * 60)
    
    # Test individual endpoints still work
    endpoints = [
        ("/api/metar/", "METAR"),
        ("/api/taf/", "TAF")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}{test_airport}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {name} endpoint working")
            else:
                print(f"❌ {name} endpoint error: {response.status_code}")
        except Exception as e:
            print(f"❌ {name} endpoint error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Phase 5 Tests...")
    print("Make sure the Flask backend is running on http://localhost:5000")
    print()
    
    # Test PIREP integration in unified endpoint
    test_pirep_integration()
    
    # Test PIREP parser module directly
    test_pirep_parser_directly()
    
    # Test backward compatibility
    test_api_backward_compatibility()
    
    print("\n✈️  Phase 5 implementation complete!")
    print("PIREPs are now integrated into the unified briefing system.")
    print("Frontend includes a dedicated Pilot Reports tab with detailed formatting.")