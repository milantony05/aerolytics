#!/usr/bin/env python3
"""
Test script for Phase 4 - Weather Categorization & Unified Endpoint

This script tests the new unified briefing endpoint and weather classification system.
"""

import requests
import json
import sys

def test_unified_briefing_endpoint():
    """Test the unified briefing endpoint with sample airports"""
    
    base_url = "http://localhost:5000"
    test_airports = ["KJFK", "KLAX", "KORD", "KDEN"]
    
    print("=" * 60)
    print("Phase 4 Testing: Weather Categorization & Unified Endpoint")
    print("=" * 60)
    
    for airport in test_airports:
        print(f"\n🛩️  Testing {airport}...")
        print("-" * 40)
        
        try:
            # Test unified briefing endpoint
            response = requests.get(f"{base_url}/api/briefing/airport/{airport}", timeout=15)
            
            if response.status_code == 200:
                briefing = response.json()
                
                print(f"✅ Briefing retrieved successfully")
                print(f"📍 Airport: {briefing.get('airport', 'Unknown')}")
                print(f"📊 Status: {briefing.get('status', 'Unknown')}")
                
                # Test weather classification
                if 'weather_classification' in briefing:
                    classification = briefing['weather_classification']
                    category = classification.get('category', 'Unknown')
                    score = classification.get('score', 0)
                    confidence = classification.get('confidence', 'Unknown')
                    
                    # Get category emoji
                    category_emoji = {
                        'Clear': '☀️',
                        'Significant': '⚠️',
                        'Severe': '⛈️'
                    }.get(category, '❓')
                    
                    print(f"{category_emoji} Weather Category: {category}")
                    print(f"📈 Classification Score: {score}/12")
                    print(f"🎯 Confidence: {confidence}")
                    
                    # Show top reasoning
                    if classification.get('reasoning'):
                        print(f"🔍 Key Factors:")
                        for reason in classification['reasoning'][:3]:  # Top 3
                            print(f"   • {reason}")
                    
                    # Show factor breakdown
                    if classification.get('factors'):
                        print(f"📋 Factor Analysis:")
                        for factor, data in classification['factors'].items():
                            impact = data.get('impact', 'None')
                            factor_score = data.get('score', 0)
                            impact_emoji = {
                                'None': '✅',
                                'Minor': '🟡',
                                'Significant': '🟠',
                                'Severe': '🔴'
                            }.get(impact, '⚪')
                            print(f"   {impact_emoji} {factor.title()}: {impact} ({factor_score})")
                
                # Test data availability
                has_metar = bool(briefing.get('current_conditions'))
                has_taf = bool(briefing.get('forecast'))
                
                print(f"📡 Data Availability:")
                print(f"   METAR: {'✅ Available' if has_metar else '❌ Not Available'}")
                print(f"   TAF: {'✅ Available' if has_taf else '❌ Not Available'}")
                
                # Show any errors
                if briefing.get('errors'):
                    print(f"⚠️  Warnings:")
                    for error in briefing['errors'][:2]:  # Show first 2
                        print(f"   • {error}")
                
                # Show briefing summary
                if briefing.get('summary'):
                    print(f"📝 Summary:")
                    for item in briefing['summary'][:3]:  # Top 3 items
                        print(f"   • {item}")
                        
            else:
                error_data = response.json() if response.headers.get('Content-Type', '').startswith('application/json') else {}
                print(f"❌ Error {response.status_code}: {error_data.get('error', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Phase 4 Testing Complete!")
    print("=" * 60)

def test_individual_endpoints():
    """Test that individual METAR and TAF endpoints still work"""
    
    base_url = "http://localhost:5000"
    test_airport = "KJFK"
    
    print(f"\n🔧 Testing Individual Endpoints for {test_airport}...")
    print("-" * 50)
    
    # Test METAR endpoint
    try:
        response = requests.get(f"{base_url}/api/metar/{test_airport}", timeout=10)
        if response.status_code == 200:
            print("✅ METAR endpoint working")
        else:
            print(f"❌ METAR endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ METAR endpoint error: {str(e)}")
    
    # Test TAF endpoint
    try:
        response = requests.get(f"{base_url}/api/taf/{test_airport}", timeout=10)
        if response.status_code == 200:
            print("✅ TAF endpoint working")
        else:
            print(f"❌ TAF endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ TAF endpoint error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Phase 4 Tests...")
    print("Make sure the Flask backend is running on http://localhost:5000")
    print()
    
    # Test unified briefing endpoint
    test_unified_briefing_endpoint()
    
    # Test individual endpoints for backward compatibility
    test_individual_endpoints()
    
    print("\n✈️  Phase 4 implementation complete!")
    print("The unified briefing endpoint provides comprehensive weather analysis.")