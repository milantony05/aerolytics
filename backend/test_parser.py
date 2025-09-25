#!/usr/bin/env python3
"""
Test script for the METAR parser - Phase 2 verification
"""

from metar_parser import parse_metar
import json

def test_parser():
    """Test the METAR parser with various examples"""
    
    test_cases = [
        {
            'name': 'Clear conditions',
            'metar': 'METAR KJFK 261951Z 26008KT 10SM FEW250 24/18 A2995 RMK AO2'
        },
        {
            'name': 'Weather phenomena',
            'metar': 'METAR KORD 261951Z 27012G18KT 5SM -RA BKN008 OVC015 18/16 A2985'
        },
        {
            'name': 'Low visibility', 
            'metar': 'METAR KSFO 261956Z 28008KT 1/4SM FG VV002 15/15 A3001'
        }
    ]
    
    print("METAR Parser Test Results")
    print("=" * 60)
    
    for test in test_cases:
        print(f"\n{test['name']}:")
        print(f"Raw METAR: {test['metar']}")
        print("-" * 40)
        
        parsed = parse_metar(test['metar'])
        
        if 'error' in parsed:
            print(f"❌ ERROR: {parsed['error']}")
            continue
            
        # Display key parsed fields
        print(f"✅ Station: {parsed['station']}")
        
        if parsed['observation_time']:
            print(f"✅ Time: {parsed['observation_time']['formatted']}")
            
        if parsed['wind'] and 'description' in parsed['wind']:
            print(f"✅ Wind: {parsed['wind']['description']}")
            
        if parsed['visibility'] and 'description' in parsed['visibility']:
            print(f"✅ Visibility: {parsed['visibility']['description']}")
            
        if parsed['weather']:
            for weather in parsed['weather']:
                print(f"✅ Weather: {weather['description']}")
                
        if parsed['clouds']:
            for cloud in parsed['clouds']:
                print(f"✅ Clouds: {cloud['description']}")
                
        if parsed['temperature'] and 'description' in parsed['temperature']:
            print(f"✅ Temperature: {parsed['temperature']['description']}")
            
        if parsed['pressure'] and 'description' in parsed['pressure']:
            print(f"✅ Pressure: {parsed['pressure']['description']}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")

if __name__ == '__main__':
    test_parser()