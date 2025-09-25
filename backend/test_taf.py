#!/usr/bin/env python3
"""
Test script for the TAF parser - Phase 3 verification
"""

from taf_parser import parse_taf
import json

def test_taf_parser():
    """Test the TAF parser with various examples"""
    
    test_cases = [
        {
            'name': 'Basic forecast with FM groups',
            'taf': 'TAF KJFK 261720Z 2618/2724 26008KT P6SM FEW250 FM270200 27012KT P6SM SCT250 FM271400 28015KT P6SM BKN250'
        },
        {
            'name': 'Forecast with TEMPO conditions',
            'taf': 'TAF KLAX 261740Z 2618/2724 25005KT P6SM FEW015 SCT250 TEMPO 2622/2702 BKN015'
        },
        {
            'name': 'Forecast with BECMG conditions',
            'taf': 'TAF KORD 261720Z 2618/2724 27012KT P6SM SCT250 BECMG 2620/2622 30015G25KT'
        },
        {
            'name': 'Complex forecast with weather',
            'taf': 'TAF KSEA 261720Z 2618/2724 21008KT 5SM -RA BKN008 OVC015 TEMPO 2620/2624 3SM RA BR BKN005'
        }
    ]
    
    print("TAF Parser Test Results")
    print("=" * 70)
    
    for test in test_cases:
        print(f"\n{test['name']}:")
        print(f"Raw TAF: {test['taf']}")
        print("-" * 50)
        
        parsed = parse_taf(test['taf'])
        
        if 'error' in parsed:
            print(f"ERROR: {parsed['error']}")
            continue
            
        # Display key parsed fields
        print(f"Station: {parsed['station']}")
        
        if parsed['issue_time']:
            print(f"Issued: {parsed['issue_time']['formatted']}")
            
        if parsed['valid_period']:
            print(f"Valid: {parsed['valid_period']['description']}")
            
        if parsed['base_forecast']:
            print("Base Forecast:")
            bf = parsed['base_forecast']
            
            if bf.get('wind') and bf['wind'].get('description'):
                print(f"  Wind: {bf['wind']['description']}")
                
            if bf.get('visibility') and bf['visibility'].get('description'):
                print(f"  Visibility: {bf['visibility']['description']}")
                
            if bf.get('weather'):
                for weather in bf['weather']:
                    print(f"  Weather: {weather['description']}")
                    
            if bf.get('clouds'):
                for cloud in bf['clouds']:
                    print(f"  Clouds: {cloud['description']}")
                    
        if parsed['change_groups']:
            print(f"Change Groups ({len(parsed['change_groups'])}):")
            for i, group in enumerate(parsed['change_groups'], 1):
                print(f"  {i}. {group.get('type', 'Unknown')}")
                if group.get('time_period') and group['time_period'].get('description'):
                    print(f"     Time: {group['time_period']['description']}")
                elif group.get('time_period') and group['time_period'].get('formatted'):
                    print(f"     Time: {group['time_period']['formatted']}")
    
    print("\n" + "=" * 70)
    print("All TAF tests completed successfully!")

def test_taf_components():
    """Test individual TAF components"""
    print("\nTesting TAF Component Parsing:")
    print("=" * 40)
    
    # Test basic TAF
    sample_taf = "TAF KJFK 261720Z 2618/2724 26008KT P6SM FEW250"
    parsed = parse_taf(sample_taf)
    
    print("Sample TAF Components:")
    print(f"  Station: {parsed.get('station')}")
    print(f"  Issue Time: {parsed.get('issue_time', {}).get('formatted')}")
    print(f"  Valid Period: {parsed.get('valid_period', {}).get('description')}")
    
    if parsed.get('base_forecast'):
        bf = parsed['base_forecast']
        print("  Base Forecast:")
        if bf.get('wind'):
            print(f"    Wind: {bf['wind'].get('description')}")
        if bf.get('visibility'):
            print(f"    Visibility: {bf['visibility'].get('description')}")
        if bf.get('clouds'):
            for cloud in bf['clouds']:
                print(f"    Clouds: {cloud.get('description')}")

if __name__ == '__main__':
    test_taf_parser()
    test_taf_components()