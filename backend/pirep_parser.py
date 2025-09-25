"""
PIREP (Pilot Report) Parser Module for Aerolytics

This module provides functionality to fetch and parse PIREP (Pilot Report) data
from the AviationWeather.gov API. PIREPs contain real-time observations from 
pilots in flight, providing valuable information about actual conditions.

PIREP types include:
- Routine PIREPs: General observations about flight conditions
- Urgent PIREPs: Reports of hazardous conditions requiring immediate attention
"""

import requests
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json


class PirepParser:
    def __init__(self):
        # PIREP parsing patterns
        self.pirep_patterns = {
            'aircraft_type': r'/TY\s+([A-Z0-9]+)',
            'flight_level': r'/FL\s*(\d+)',
            'altitude': r'(\d+)\s*FT',
            'location': r'/OV\s+([A-Z]{3,4}[/\-\d\w]*)',
            'time': r'/TM\s+(\d{4})',
            'flight_level_fl': r'/FL(\d+)',
            'temperature': r'/TP\s*(M?\d+)',
            'wind': r'/WV\s*(\d{3})(\d{2,3})(?:KT)?',
            'turbulence': r'/TB\s+([^/]+)',
            'icing': r'/IC\s+([^/]+)',
            'sky_conditions': r'/SK\s+([^/]+)',
            'flight_visibility': r'/WX\s+([^/]+)',
            'remarks': r'/RM\s+(.+?)(?=/[A-Z]{2}|\s*$)'
        }
        
        # PIREP urgency indicators
        self.urgent_indicators = [
            'URGENT', 'UUA', 'SEVERE', 'EXTREME', 'MODERATE', 'SEV TURB',
            'SEV ICE', 'LLWS', 'WINDSHEAR', 'MICROBURST'
        ]
        
        # Turbulence severity mapping
        self.turbulence_severity = {
            'NEG': 'None',
            'SMTH': 'Smooth',
            'LGT': 'Light',
            'MOD': 'Moderate', 
            'SEV': 'Severe',
            'EXTRM': 'Extreme'
        }
        
        # Icing severity mapping
        self.icing_severity = {
            'NEG': 'None',
            'TRC': 'Trace',
            'LGT': 'Light',
            'MOD': 'Moderate',
            'SEV': 'Severe'
        }

    def fetch_pireps(self, airport_code: str, radius_nm: int = 100) -> List[Dict]:
        """
        Fetch PIREPs for a given airport area from AviationWeather.gov
        
        Args:
            airport_code (str): 4-letter ICAO airport code
            radius_nm (int): Radius in nautical miles around the airport
            
        Returns:
            List[Dict]: List of parsed PIREP dictionaries
        """
        try:
            # AviationWeather.gov PIREP API endpoint
            base_url = "https://aviationweather.gov/api/data/airsigmet"
            
            params = {
                'format': 'json',
                'type': 'pirep',
                'bbox': self._get_bbox_for_airport(airport_code, radius_nm),
                'date': datetime.utcnow().strftime('%Y%m%d'),
                'time': '00'  # Get PIREPs from today
            }
            
            response = requests.get(base_url, params=params, timeout=15)
            response.raise_for_status()
            
            # Try to parse as JSON first (newer API format)
            try:
                pirep_data = response.json()
                if isinstance(pirep_data, list):
                    return [self.parse_pirep_json(pirep) for pirep in pirep_data]
                elif isinstance(pirep_data, dict) and 'features' in pirep_data:
                    return [self.parse_pirep_json(feature) for feature in pirep_data['features']]
            except (json.JSONDecodeError, KeyError):
                pass
            
            # Fallback to text parsing
            pirep_text = response.text.strip()
            if not pirep_text or pirep_text == "No PIREP data available":
                return []
                
            # Parse raw PIREP text
            return self.parse_pirep_text(pirep_text)
            
        except requests.exceptions.RequestException as e:
            return [{
                'error': f'Failed to fetch PIREPs: {str(e)}',
                'airport': airport_code,
                'timestamp': datetime.utcnow().isoformat()
            }]
        except Exception as e:
            return [{
                'error': f'Unexpected error fetching PIREPs: {str(e)}',
                'airport': airport_code,
                'timestamp': datetime.utcnow().isoformat()
            }]

    def _get_bbox_for_airport(self, airport_code: str, radius_nm: int) -> str:
        """
        Get a bounding box string for the API based on airport and radius
        This is a simplified implementation - in production you'd use actual coordinates
        """
        # Simplified bounding box - in production, you'd look up actual airport coordinates
        # and calculate proper lat/lon bounds based on radius
        return f"-180,-90,180,90"  # Global for now - API will filter appropriately

    def parse_pirep_json(self, pirep_data: Dict) -> Dict:
        """Parse PIREP data from JSON format"""
        try:
            parsed = {
                'raw_pirep': pirep_data.get('rawOb', ''),
                'report_type': 'PIREP',
                'urgency': 'Routine',
                'timestamp': None,
                'location': None,
                'aircraft_type': None,
                'altitude': None,
                'conditions': {
                    'turbulence': None,
                    'icing': None,
                    'sky_conditions': None,
                    'visibility': None,
                    'temperature': None,
                    'wind': None
                },
                'remarks': None,
                'parsed_successfully': True
            }
            
            # Extract basic information
            if 'obsTime' in pirep_data:
                parsed['timestamp'] = pirep_data['obsTime']
            
            if 'location' in pirep_data:
                parsed['location'] = pirep_data['location']
                
            # Parse the raw observation text if available
            raw_text = pirep_data.get('rawOb', '')
            if raw_text:
                parsed.update(self._parse_pirep_text_content(raw_text))
                
            return parsed
            
        except Exception as e:
            return {
                'error': f'Failed to parse PIREP JSON: {str(e)}',
                'raw_data': pirep_data,
                'parsed_successfully': False
            }

    def parse_pirep_text(self, pirep_text: str) -> List[Dict]:
        """Parse PIREPs from raw text format"""
        try:
            # Split individual PIREPs (typically separated by newlines or specific patterns)
            pirep_lines = [line.strip() for line in pirep_text.split('\n') if line.strip()]
            
            parsed_pireps = []
            for line in pirep_lines:
                if self._is_pirep_line(line):
                    parsed = self._parse_pirep_text_content(line)
                    parsed['raw_pirep'] = line
                    parsed_pireps.append(parsed)
                    
            return parsed_pireps if parsed_pireps else [{
                'error': 'No valid PIREPs found in response',
                'raw_text': pirep_text,
                'parsed_successfully': False
            }]
            
        except Exception as e:
            return [{
                'error': f'Failed to parse PIREP text: {str(e)}',
                'raw_text': pirep_text,
                'parsed_successfully': False
            }]

    def _is_pirep_line(self, line: str) -> bool:
        """Check if a line contains a PIREP"""
        pirep_indicators = ['UA', 'UUA', '/OV', '/TM', '/FL', '/TY']
        return any(indicator in line.upper() for indicator in pirep_indicators)

    def _parse_pirep_text_content(self, pirep_text: str) -> Dict:
        """Parse the content of a single PIREP text"""
        parsed = {
            'report_type': 'PIREP',
            'urgency': 'Routine',
            'timestamp': None,
            'location': None,
            'aircraft_type': None,
            'altitude': None,
            'conditions': {
                'turbulence': None,
                'icing': None,
                'sky_conditions': None,
                'visibility': None,
                'temperature': None,
                'wind': None
            },
            'remarks': None,
            'parsed_successfully': True
        }
        
        # Determine urgency
        if any(indicator in pirep_text.upper() for indicator in self.urgent_indicators):
            parsed['urgency'] = 'Urgent'
        if 'UUA' in pirep_text.upper():
            parsed['urgency'] = 'Urgent'
            
        # Extract structured information using regex patterns
        for field, pattern in self.pirep_patterns.items():
            match = re.search(pattern, pirep_text, re.IGNORECASE)
            if match:
                if field == 'aircraft_type':
                    parsed['aircraft_type'] = match.group(1)
                elif field == 'flight_level' or field == 'flight_level_fl':
                    parsed['altitude'] = f"FL{match.group(1)}"
                elif field == 'altitude':
                    parsed['altitude'] = f"{match.group(1)} ft"
                elif field == 'location':
                    parsed['location'] = match.group(1)
                elif field == 'time':
                    parsed['timestamp'] = self._parse_pirep_time(match.group(1))
                elif field == 'temperature':
                    temp = match.group(1)
                    if temp.startswith('M'):
                        temp = f"-{temp[1:]}"
                    parsed['conditions']['temperature'] = f"{temp}°C"
                elif field == 'wind':
                    direction = match.group(1)
                    speed = match.group(2)
                    parsed['conditions']['wind'] = f"{direction}° at {speed} knots"
                elif field == 'turbulence':
                    turb_text = match.group(1).strip()
                    parsed['conditions']['turbulence'] = self._parse_turbulence(turb_text)
                elif field == 'icing':
                    ice_text = match.group(1).strip()
                    parsed['conditions']['icing'] = self._parse_icing(ice_text)
                elif field == 'sky_conditions':
                    parsed['conditions']['sky_conditions'] = match.group(1).strip()
                elif field == 'flight_visibility':
                    parsed['conditions']['visibility'] = match.group(1).strip()
                elif field == 'remarks':
                    parsed['remarks'] = match.group(1).strip()
        
        return parsed

    def _parse_pirep_time(self, time_str: str) -> str:
        """Parse PIREP time format (HHMM) to readable format"""
        try:
            if len(time_str) == 4:
                hour = time_str[:2]
                minute = time_str[2:]
                return f"{hour}:{minute} UTC"
            return time_str
        except:
            return time_str

    def _parse_turbulence(self, turb_text: str) -> Dict:
        """Parse turbulence information"""
        turb_upper = turb_text.upper()
        
        # Find severity
        severity = 'Unknown'
        for code, desc in self.turbulence_severity.items():
            if code in turb_upper:
                severity = desc
                break
                
        # Extract altitude if present
        altitude_match = re.search(r'(\d+)-?(\d+)?', turb_text)
        altitude_range = None
        if altitude_match:
            if altitude_match.group(2):
                altitude_range = f"{altitude_match.group(1)}-{altitude_match.group(2)}"
            else:
                altitude_range = altitude_match.group(1)
                
        return {
            'severity': severity,
            'altitude_range': altitude_range,
            'description': turb_text,
            'raw_text': turb_text
        }

    def _parse_icing(self, ice_text: str) -> Dict:
        """Parse icing information"""
        ice_upper = ice_text.upper()
        
        # Find severity
        severity = 'Unknown'
        for code, desc in self.icing_severity.items():
            if code in ice_upper:
                severity = desc
                break
                
        # Extract altitude if present
        altitude_match = re.search(r'(\d+)-?(\d+)?', ice_text)
        altitude_range = None
        if altitude_match:
            if altitude_match.group(2):
                altitude_range = f"{altitude_match.group(1)}-{altitude_match.group(2)}"
            else:
                altitude_range = altitude_match.group(1)
                
        return {
            'severity': severity,
            'altitude_range': altitude_range,
            'description': ice_text,
            'raw_text': ice_text
        }

    def categorize_pireps(self, pireps: List[Dict]) -> Dict:
        """Categorize PIREPs by urgency and type"""
        categorized = {
            'urgent_reports': [],
            'routine_reports': [],
            'total_count': len([p for p in pireps if not p.get('error')]),
            'has_turbulence': False,
            'has_icing': False,
            'has_weather': False,
            'summary': []
        }
        
        for pirep in pireps:
            if pirep.get('error'):
                continue
                
            if pirep.get('urgency') == 'Urgent':
                categorized['urgent_reports'].append(pirep)
            else:
                categorized['routine_reports'].append(pirep)
                
            # Check for specific conditions
            conditions = pirep.get('conditions', {})
            if conditions.get('turbulence'):
                categorized['has_turbulence'] = True
            if conditions.get('icing'):
                categorized['has_icing'] = True
            if conditions.get('visibility') or conditions.get('sky_conditions'):
                categorized['has_weather'] = True
        
        # Generate summary
        if categorized['urgent_reports']:
            categorized['summary'].append(f"{len(categorized['urgent_reports'])} urgent pilot report(s)")
        if categorized['routine_reports']:
            categorized['summary'].append(f"{len(categorized['routine_reports'])} routine pilot report(s)")
        if categorized['has_turbulence']:
            categorized['summary'].append("Turbulence reported")
        if categorized['has_icing']:
            categorized['summary'].append("Icing conditions reported")
            
        return categorized


# Convenience function for easy import
def fetch_and_parse_pireps(airport_code: str, radius_nm: int = 100) -> Tuple[List[Dict], Dict]:
    """
    Fetch and parse PIREPs for an airport area
    
    Args:
        airport_code (str): Airport ICAO code
        radius_nm (int): Search radius in nautical miles
        
    Returns:
        Tuple[List[Dict], Dict]: Raw PIREPs and categorized summary
    """
    parser = PirepParser()
    pireps = parser.fetch_pireps(airport_code, radius_nm)
    categorized = parser.categorize_pireps(pireps)
    return pireps, categorized