from flask import Flask, jsonify
from flask_cors import CORS
import requests
from metar_parser import parse_metar
from taf_parser import parse_taf
from weather_classifier import classify_weather
from pirep_parser import fetch_and_parse_pireps

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# AviationWeather.gov API base URLs
AVIATION_WEATHER_METAR_URL = "https://aviationweather.gov/api/data/metar"
AVIATION_WEATHER_TAF_URL = "https://aviationweather.gov/api/data/taf"

@app.route('/api/metar/<string:airport>', methods=['GET'])
def get_metar(airport):
    """
    Fetch raw METAR data for a specific airport from AviationWeather.gov
    
    Args:
        airport (str): 4-letter ICAO airport code (e.g., KJFK, KLAX)
    
    Returns:
        JSON response with raw METAR string or error message
    """
    try:
        # Convert airport code to uppercase
        airport_code = airport.upper()
        
        # Construct API URL with parameters
        params = {
            'ids': airport_code,
            'format': 'raw',
            'taf': 'false',
            'hours': '3'  # Get METAR from last 3 hours
        }
        
        # Make request to AviationWeather.gov API
        response = requests.get(AVIATION_WEATHER_METAR_URL, params=params, timeout=10)
        response.raise_for_status()
        
        # Get the raw METAR text
        metar_text = response.text.strip()
        
        if not metar_text or metar_text == "No METAR available":
            return jsonify({
                'error': f'No METAR data available for airport {airport_code}',
                'airport': airport_code
            }), 404
        
        # Parse the raw METAR data
        parsed_metar = parse_metar(metar_text)
        
        return jsonify({
            'airport': airport_code,
            'raw_metar': metar_text,
            'parsed_metar': parsed_metar,
            'status': 'success'
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': f'Failed to fetch METAR data: {str(e)}',
            'airport': airport.upper()
        }), 500
    except Exception as e:
        return jsonify({
            'error': f'Unexpected error: {str(e)}',
            'airport': airport.upper()
        }), 500

@app.route('/api/taf/<string:airport>', methods=['GET'])
def get_taf(airport):
    """
    Fetch raw TAF data for a specific airport from AviationWeather.gov
    
    Args:
        airport (str): 4-letter ICAO airport code (e.g., KJFK, KLAX)
    
    Returns:
        JSON response with raw TAF string and parsed data or error message
    """
    try:
        # Convert airport code to uppercase
        airport_code = airport.upper()
        
        # Construct API URL with parameters
        params = {
            'ids': airport_code,
            'format': 'raw',
            'hours': '30'  # Get TAF for next 30 hours
        }
        
        # Make request to AviationWeather.gov API
        response = requests.get(AVIATION_WEATHER_TAF_URL, params=params, timeout=10)
        response.raise_for_status()
        
        # Get the raw TAF text
        taf_text = response.text.strip()
        
        if not taf_text or taf_text == "No TAF available":
            return jsonify({
                'error': f'No TAF data available for airport {airport_code}',
                'airport': airport_code
            }), 404
        
        # Parse the raw TAF data
        parsed_taf = parse_taf(taf_text)
        
        return jsonify({
            'airport': airport_code,
            'raw_taf': taf_text,
            'parsed_taf': parsed_taf,
            'status': 'success'
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': f'Failed to fetch TAF data: {str(e)}',
            'airport': airport.upper()
        }), 500
    except Exception as e:
        return jsonify({
            'error': f'Unexpected error: {str(e)}',
            'airport': airport.upper()
        }), 500

@app.route('/api/briefing/airport/<string:airport>', methods=['GET'])
def get_airport_briefing(airport):
    """
    Comprehensive airport weather briefing combining METAR, TAF, and weather classification
    
    Args:
        airport (str): 4-letter ICAO airport code (e.g., KJFK, KLAX)
    
    Returns:
        JSON response with complete weather briefing including:
        - Current conditions (METAR)
        - Forecast (TAF)
        - Weather classification (Clear/Significant/Severe)
        - Unified briefing summary
    """
    try:
        airport_code = airport.upper()
        briefing = {
            'airport': airport_code,
            'briefing_time': None,
            'current_conditions': None,
            'forecast': None,
            'weather_classification': None,
            'status': 'success',
            'errors': []
        }
        
        # Fetch METAR data
        try:
            params = {
                'ids': airport_code,
                'format': 'raw',
                'taf': 'false',
                'hours': '3'
            }
            response = requests.get(AVIATION_WEATHER_METAR_URL, params=params, timeout=10)
            response.raise_for_status()
            
            metar_text = response.text.strip()
            if metar_text and metar_text != "No METAR available":
                parsed_metar = parse_metar(metar_text)
                briefing['current_conditions'] = {
                    'raw_metar': metar_text,
                    'parsed': parsed_metar
                }
                # Set briefing time from METAR if available
                if 'time' in parsed_metar:
                    briefing['briefing_time'] = parsed_metar['time']
            else:
                briefing['errors'].append(f'No current METAR data available for {airport_code}')
                
        except Exception as e:
            briefing['errors'].append(f'Failed to fetch METAR: {str(e)}')
        
        # Fetch TAF data
        try:
            params = {
                'ids': airport_code,
                'format': 'raw',
                'hours': '30'
            }
            response = requests.get(AVIATION_WEATHER_TAF_URL, params=params, timeout=10)
            response.raise_for_status()
            
            taf_text = response.text.strip()
            if taf_text and taf_text != "No TAF available":
                parsed_taf = parse_taf(taf_text)
                briefing['forecast'] = {
                    'raw_taf': taf_text,
                    'parsed': parsed_taf
                }
            else:
                briefing['errors'].append(f'No TAF forecast data available for {airport_code}')
                
        except Exception as e:
            briefing['errors'].append(f'Failed to fetch TAF: {str(e)}')
        
        # Fetch PIREP data
        try:
            pireps, pirep_summary = fetch_and_parse_pireps(airport_code, radius_nm=100)
            
            # Filter out error entries for the main data
            valid_pireps = [p for p in pireps if not p.get('error')]
            error_pireps = [p for p in pireps if p.get('error')]
            
            briefing['pilot_reports'] = {
                'reports': valid_pireps,
                'summary': pirep_summary,
                'count': len(valid_pireps)
            }
            
            # Add any PIREP errors to the main error list
            for error_pirep in error_pireps:
                if 'error' in error_pirep:
                    briefing['errors'].append(f"PIREP: {error_pirep['error']}")
                    
        except Exception as e:
            briefing['errors'].append(f'Failed to fetch PIREPs: {str(e)}')
            briefing['pilot_reports'] = {
                'reports': [],
                'summary': {
                    'urgent_reports': [],
                    'routine_reports': [],
                    'total_count': 0,
                    'has_turbulence': False,
                    'has_icing': False,
                    'has_weather': False,
                    'summary': ['Error fetching pilot reports']
                },
                'count': 0
            }
        
        # Classify weather conditions
        try:
            if briefing['current_conditions']:
                parsed_metar = briefing['current_conditions']['parsed']
                parsed_taf = briefing['forecast']['parsed'] if briefing['forecast'] else None
                
                weather_classification = classify_weather(parsed_metar, parsed_taf)
                briefing['weather_classification'] = weather_classification
            else:
                briefing['weather_classification'] = {
                    'category': 'Unknown',
                    'score': 0,
                    'confidence': 'Low',
                    'reasoning': ['No current weather data available for classification'],
                    'factors': {}
                }
        except Exception as e:
            briefing['errors'].append(f'Failed to classify weather: {str(e)}')
            briefing['weather_classification'] = {
                'category': 'Unknown',
                'score': 0,
                'confidence': 'Low',
                'reasoning': [f'Classification error: {str(e)}'],
                'factors': {}
            }
        
        # Generate briefing summary
        summary = []
        if briefing['weather_classification']:
            category = briefing['weather_classification']['category']
            summary.append(f"Weather Category: {category}")
            
            if briefing['weather_classification']['reasoning']:
                summary.extend(briefing['weather_classification']['reasoning'][:3])  # Top 3 reasons
        
        if briefing['current_conditions'] and briefing['current_conditions']['parsed']:
            metar = briefing['current_conditions']['parsed']
            if 'wind' in metar and metar['wind'].get('speed'):
                wind_speed = metar['wind']['speed']
                wind_dir = metar['wind'].get('direction', 'VRB')
                summary.append(f"Wind: {wind_dir}° at {wind_speed} knots")
                
            if 'visibility' in metar:
                vis = metar['visibility']
                if 'distance' in vis:
                    unit = vis.get('unit', 'statute_miles')
                    unit_abbr = 'SM' if unit == 'statute_miles' else 'm'
                    summary.append(f"Visibility: {vis['distance']} {unit_abbr}")
        
        # Add PIREP summary information
        if briefing['pilot_reports'] and briefing['pilot_reports']['summary']:
            pirep_summary = briefing['pilot_reports']['summary']
            if pirep_summary['summary']:
                summary.extend(pirep_summary['summary'][:2])  # Add top 2 PIREP summary items
        
        briefing['summary'] = summary
        
        # Determine overall status
        if briefing['errors']:
            if not briefing['current_conditions'] and not briefing['forecast']:
                return jsonify(briefing), 404
            else:
                briefing['status'] = 'partial'  # Some data available despite errors
                
        return jsonify(briefing)
        
    except Exception as e:
        return jsonify({
            'error': f'Unexpected error during briefing generation: {str(e)}',
            'airport': airport.upper(),
            'status': 'error'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Aerolytics Backend'})

if __name__ == '__main__':
    print("Starting Aerolytics Backend Server...")
    print("API available at: http://localhost:5000")
    print("Test with: http://localhost:5000/api/metar/KJFK")
    app.run(debug=True, host='0.0.0.0', port=5000)