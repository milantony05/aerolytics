from flask import Flask, jsonify
from flask_cors import CORS
import requests
from metar_parser import parse_metar
from taf_parser import parse_taf

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

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Aerolytics Backend'})

if __name__ == '__main__':
    print("Starting Aerolytics Backend Server...")
    print("API available at: http://localhost:5000")
    print("Test with: http://localhost:5000/api/metar/KJFK")
    app.run(debug=True, host='0.0.0.0', port=5000)