"""
METAR Parser Module for Aerolytics

This module provides functionality to parse raw METAR (Meteorological Aerodrome Report) 
strings into structured JSON objects with human-readable field names.

METAR Format Overview:
METAR KJFK 261951Z 26008KT 10SM FEW250 24/18 A2995 RMK AO2 SLP141 T02440183
- Station: KJFK
- Date/Time: 261951Z (26th day, 19:51 UTC)
- Wind: 26008KT (260 degrees at 8 knots)
- Visibility: 10SM (10 statute miles)
- Clouds: FEW250 (few clouds at 25,000 feet)
- Temperature/Dewpoint: 24/18 (24°C/18°C)
- Altimeter: A2995 (29.95 inches of mercury)
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Union


class MetarParser:
    def __init__(self):
        self.cloud_types = {
            'SKC': 'Sky Clear',
            'CLR': 'Clear',
            'FEW': 'Few',
            'SCT': 'Scattered', 
            'BKN': 'Broken',
            'OVC': 'Overcast',
            'VV': 'Vertical Visibility'
        }
        
        self.weather_phenomena = {
            # Intensity
            '-': 'Light',
            '+': 'Heavy',
            'VC': 'In the vicinity',
            
            # Descriptors
            'MI': 'Shallow',
            'PR': 'Partial',
            'BC': 'Patches',
            'DR': 'Drifting',
            'BL': 'Blowing',
            'SH': 'Showers',
            'TS': 'Thunderstorm',
            'FZ': 'Freezing',
            
            # Precipitation
            'DZ': 'Drizzle',
            'RA': 'Rain',
            'SN': 'Snow',
            'SG': 'Snow Grains',
            'IC': 'Ice Crystals',
            'PL': 'Ice Pellets',
            'GR': 'Hail',
            'GS': 'Small Hail/Snow Pellets',
            'UP': 'Unknown Precipitation',
            
            # Obscuration
            'BR': 'Mist',
            'FG': 'Fog',
            'FU': 'Smoke',
            'VA': 'Volcanic Ash',
            'DU': 'Dust',
            'SA': 'Sand',
            'HZ': 'Haze',
            'PY': 'Spray',
            
            # Other
            'PO': 'Dust/Sand Whirls',
            'SQ': 'Squalls',
            'FC': 'Funnel Cloud/Tornado',
            'SS': 'Sandstorm'
        }

    def parse_metar(self, raw_metar: str) -> Dict:
        """
        Parse a raw METAR string into a structured dictionary
        
        Args:
            raw_metar (str): Raw METAR string from weather service
            
        Returns:
            Dict: Parsed METAR data with structured fields
        """
        if not raw_metar or not raw_metar.strip():
            return {'error': 'Empty METAR string provided'}
            
        try:
            # Remove extra whitespace and split into components
            parts = raw_metar.strip().split()
            
            parsed_data = {
                'raw_metar': raw_metar,
                'station': None,
                'observation_time': None,
                'wind': {},
                'visibility': {},
                'weather': [],
                'clouds': [],
                'temperature': {},
                'pressure': {},
                'remarks': None,
                'parsing_errors': []
            }
            
            i = 0
            
            # Skip METAR identifier if present
            if parts[i] == 'METAR':
                i += 1
                
            # Parse station identifier (4 characters, usually starts with K for US)
            if i < len(parts):
                parsed_data['station'] = parts[i]
                i += 1
                
            # Parse observation time (6 digits + Z)
            if i < len(parts) and re.match(r'\d{6}Z', parts[i]):
                parsed_data['observation_time'] = self._parse_time(parts[i])
                i += 1
                
            # Parse wind information
            if i < len(parts):
                wind_match = re.match(r'(\d{3}|VRB)(\d{2,3})(G\d{2,3})?(KT|MPS)', parts[i])
                if wind_match:
                    parsed_data['wind'] = self._parse_wind(parts[i])
                    i += 1
                    
            # Parse visibility
            if i < len(parts):
                vis_result = self._parse_visibility(parts[i])
                if vis_result:
                    parsed_data['visibility'] = vis_result
                    i += 1
                    
            # Parse weather phenomena and clouds
            while i < len(parts):
                part = parts[i]
                
                # Check for weather phenomena
                if self._is_weather_phenomenon(part):
                    parsed_data['weather'].append(self._parse_weather(part))
                    i += 1
                    continue
                    
                # Check for cloud information
                if self._is_cloud_layer(part):
                    parsed_data['clouds'].append(self._parse_cloud_layer(part))
                    i += 1
                    continue
                    
                # Check for temperature/dewpoint
                if re.match(r'M?\d{2}/M?\d{2}', part):
                    parsed_data['temperature'] = self._parse_temperature(part)
                    i += 1
                    continue
                    
                # Check for altimeter setting
                if re.match(r'A\d{4}', part):
                    parsed_data['pressure'] = self._parse_pressure(part)
                    i += 1
                    continue
                    
                # Check for remarks section
                if part == 'RMK':
                    parsed_data['remarks'] = ' '.join(parts[i+1:])
                    break
                    
                # Skip unknown parts
                parsed_data['parsing_errors'].append(f"Unknown component: {part}")
                i += 1
                
            return parsed_data
            
        except Exception as e:
            return {
                'error': f'Failed to parse METAR: {str(e)}',
                'raw_metar': raw_metar
            }

    def _parse_time(self, time_str: str) -> Dict:
        """Parse observation time (e.g., 261951Z)"""
        try:
            day = int(time_str[:2])
            hour = int(time_str[2:4])
            minute = int(time_str[4:6])
            
            return {
                'day': day,
                'hour': hour,
                'minute': minute,
                'timezone': 'UTC',
                'formatted': f"Day {day}, {hour:02d}:{minute:02d} UTC"
            }
        except:
            return {'raw': time_str, 'error': 'Failed to parse time'}

    def _parse_wind(self, wind_str: str) -> Dict:
        """Parse wind information (e.g., 26008KT, VRB05KT, 09014G25KT)"""
        match = re.match(r'(\d{3}|VRB)(\d{2,3})(G(\d{2,3}))?(KT|MPS)', wind_str)
        if not match:
            return {'raw': wind_str, 'error': 'Failed to parse wind'}
            
        direction = match.group(1)
        speed = int(match.group(2))
        gust_speed = int(match.group(4)) if match.group(4) else None
        unit = match.group(5)
        
        result = {
            'direction_degrees': None if direction == 'VRB' else int(direction),
            'direction_variable': direction == 'VRB',
            'speed': speed,
            'gust_speed': gust_speed,
            'unit': 'knots' if unit == 'KT' else 'meters_per_second'
        }
        
        # Add human-readable description
        if direction == 'VRB':
            desc = f"Variable direction at {speed} {result['unit']}"
        else:
            desc = f"From {direction}° at {speed} {result['unit']}"
            
        if gust_speed:
            desc += f", gusting to {gust_speed} {result['unit']}"
            
        result['description'] = desc
        return result

    def _parse_visibility(self, vis_str: str) -> Optional[Dict]:
        """Parse visibility (e.g., 10SM, 1/2SM, 9999)"""
        # Statute miles
        if 'SM' in vis_str:
            vis_match = re.match(r'(\d+/?(\d+)?)SM', vis_str)
            if vis_match:
                vis_val = vis_match.group(1)
                if '/' in vis_val:
                    # Handle fractions like 1/2
                    parts = vis_val.split('/')
                    distance = float(parts[0]) / float(parts[1])
                else:
                    distance = float(vis_val)
                    
                return {
                    'distance': distance,
                    'unit': 'statute_miles',
                    'description': f"{vis_val} statute miles"
                }
                
        # Meters (international format)
        elif re.match(r'\d{4}', vis_str):
            distance = int(vis_str)
            return {
                'distance': distance,
                'unit': 'meters',
                'description': f"{distance} meters"
            }
            
        return None

    def _is_weather_phenomenon(self, code: str) -> bool:
        """Check if code represents weather phenomena"""
        # Remove intensity indicators
        clean_code = code.lstrip('-+')
        return any(phenom in clean_code for phenom in self.weather_phenomena.keys())

    def _parse_weather(self, weather_str: str) -> Dict:
        """Parse weather phenomena (e.g., -RA, +TSRA, VCFG)"""
        result = {
            'raw': weather_str,
            'intensity': 'moderate',
            'phenomena': [],
            'description': ''
        }
        
        # Parse intensity
        if weather_str.startswith('-'):
            result['intensity'] = 'light'
            weather_str = weather_str[1:]
        elif weather_str.startswith('+'):
            result['intensity'] = 'heavy'
            weather_str = weather_str[1:]
            
        # Parse phenomena codes
        desc_parts = []
        i = 0
        while i < len(weather_str):
            for length in [2, 1]:  # Try 2-char codes first, then 1-char
                if i + length <= len(weather_str):
                    code = weather_str[i:i+length]
                    if code in self.weather_phenomena:
                        phenomenon = self.weather_phenomena[code]
                        result['phenomena'].append({
                            'code': code,
                            'description': phenomenon
                        })
                        desc_parts.append(phenomenon.lower())
                        i += length
                        break
            else:
                i += 1  # Skip unknown character
                
        result['description'] = f"{result['intensity'].title()} {' '.join(desc_parts)}"
        return result

    def _is_cloud_layer(self, code: str) -> bool:
        """Check if code represents cloud layer"""
        return any(code.startswith(cloud_type) for cloud_type in self.cloud_types.keys())

    def _parse_cloud_layer(self, cloud_str: str) -> Dict:
        """Parse cloud layer (e.g., FEW250, SCT015, BKN005, OVC000)"""
        for cloud_type in self.cloud_types.keys():
            if cloud_str.startswith(cloud_type):
                height_str = cloud_str[len(cloud_type):]
                if height_str.isdigit():
                    height = int(height_str) * 100  # Convert to feet AGL
                    return {
                        'type': cloud_type,
                        'type_description': self.cloud_types[cloud_type],
                        'height_feet': height,
                        'description': f"{self.cloud_types[cloud_type]} at {height:,} feet"
                    }
                    
        return {'raw': cloud_str, 'error': 'Failed to parse cloud layer'}

    def _parse_temperature(self, temp_str: str) -> Dict:
        """Parse temperature/dewpoint (e.g., 24/18, M05/M12)"""
        parts = temp_str.split('/')
        if len(parts) != 2:
            return {'raw': temp_str, 'error': 'Invalid temperature format'}
            
        try:
            # Parse temperature
            temp_c = int(parts[0].replace('M', '-'))
            dewpoint_c = int(parts[1].replace('M', '-'))
            
            # Convert to Fahrenheit
            temp_f = round(temp_c * 9/5 + 32)
            dewpoint_f = round(dewpoint_c * 9/5 + 32)
            
            return {
                'temperature_celsius': temp_c,
                'temperature_fahrenheit': temp_f,
                'dewpoint_celsius': dewpoint_c,
                'dewpoint_fahrenheit': dewpoint_f,
                'description': f"{temp_c}°C ({temp_f}°F), dewpoint {dewpoint_c}°C ({dewpoint_f}°F)"
            }
        except:
            return {'raw': temp_str, 'error': 'Failed to parse temperature'}

    def _parse_pressure(self, pressure_str: str) -> Dict:
        """Parse altimeter setting (e.g., A2995)"""
        if pressure_str.startswith('A') and len(pressure_str) == 5:
            try:
                # Parse as inches of mercury (hundredths)
                inches_hg = float(pressure_str[1:]) / 100
                # Convert to millibars/hectopascals
                mb = round(inches_hg * 33.8639, 1)
                
                return {
                    'altimeter_inches_hg': inches_hg,
                    'altimeter_millibars': mb,
                    'description': f"{inches_hg:.2f} inHg ({mb} mb)"
                }
            except:
                pass
                
        return {'raw': pressure_str, 'error': 'Failed to parse pressure'}


# Convenience function for easy import
def parse_metar(raw_metar: str) -> Dict:
    """
    Parse a raw METAR string into structured data
    
    Args:
        raw_metar (str): Raw METAR string
        
    Returns:
        Dict: Parsed METAR data
    """
    parser = MetarParser()
    return parser.parse_metar(raw_metar)