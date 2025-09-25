"""
TAF Parser Module for Aerolytics

This module provides functionality to parse raw TAF (Terminal Aerodrome Forecast) 
strings into structured JSON objects with human-readable field names.

TAF Format Overview:
TAF KJFK 261720Z 2618/2724 26008KT P6SM FEW250 
     FM270200 27012KT P6SM SCT250 
     FM271400 28015KT P6SM BKN250

- Header: TAF KJFK 261720Z 2618/2724 (TAF for KJFK, issued 26th 17:20Z, valid from 26th 18Z to 27th 24Z)
- Base conditions: 26008KT P6SM FEW250 (260° at 8kt, >6SM vis, few at 25,000ft)
- Change groups: FM270200 (From 27th 02:00Z), TEMPO, BECMG, PROB30, etc.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union


class TafParser:
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
        
        self.change_indicators = {
            'FM': 'From',
            'TEMPO': 'Temporary',
            'BECMG': 'Becoming',
            'PROB30': '30% Probability',
            'PROB40': '40% Probability'
        }
        
        # Reuse weather phenomena from METAR parser
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

    def parse_taf(self, raw_taf: str) -> Dict:
        """
        Parse a raw TAF string into a structured dictionary
        
        Args:
            raw_taf (str): Raw TAF string from weather service
            
        Returns:
            Dict: Parsed TAF data with structured fields
        """
        if not raw_taf or not raw_taf.strip():
            return {'error': 'Empty TAF string provided'}
            
        try:
            # Clean up the TAF string
            raw_taf = re.sub(r'\s+', ' ', raw_taf.strip())
            
            parsed_data = {
                'raw_taf': raw_taf,
                'station': None,
                'issue_time': None,
                'valid_period': None,
                'base_forecast': None,
                'change_groups': [],
                'parsing_errors': []
            }
            
            # Split into lines for multi-line TAFs
            lines = raw_taf.split('\n')
            taf_text = ' '.join(lines)
            
            # Parse the header
            header_match = re.match(r'TAF\s+(\w{4})\s+(\d{6}Z)\s+(\d{4}/\d{4})', taf_text)
            if not header_match:
                return {'error': 'Invalid TAF format - missing header', 'raw_taf': raw_taf}
                
            parsed_data['station'] = header_match.group(1)
            parsed_data['issue_time'] = self._parse_issue_time(header_match.group(2))
            parsed_data['valid_period'] = self._parse_valid_period(header_match.group(3))
            
            # Remove the header from the text
            remaining_text = taf_text[header_match.end():].strip()
            
            # Split into base forecast and change groups
            base_forecast, change_groups = self._split_forecast_sections(remaining_text)
            
            # Parse base forecast
            if base_forecast:
                parsed_data['base_forecast'] = self._parse_forecast_conditions(base_forecast)
            
            # Parse change groups
            for group in change_groups:
                parsed_group = self._parse_change_group(group)
                if parsed_group:
                    parsed_data['change_groups'].append(parsed_group)
                    
            return parsed_data
            
        except Exception as e:
            return {
                'error': f'Failed to parse TAF: {str(e)}',
                'raw_taf': raw_taf
            }

    def _parse_issue_time(self, time_str: str) -> Dict:
        """Parse TAF issue time (e.g., 261720Z)"""
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
            return {'raw': time_str, 'error': 'Failed to parse issue time'}

    def _parse_valid_period(self, period_str: str) -> Dict:
        """Parse TAF valid period (e.g., 2618/2724)"""
        try:
            start_str, end_str = period_str.split('/')
            
            start_day = int(start_str[:2])
            start_hour = int(start_str[2:])
            end_day = int(end_str[:2])
            end_hour = int(end_str[2:])
            
            return {
                'from': {
                    'day': start_day,
                    'hour': start_hour,
                    'formatted': f"Day {start_day}, {start_hour:02d}:00 UTC"
                },
                'to': {
                    'day': end_day,
                    'hour': end_hour,
                    'formatted': f"Day {end_day}, {end_hour:02d}:00 UTC"
                },
                'duration_hours': self._calculate_duration(start_day, start_hour, end_day, end_hour),
                'description': f"Valid from Day {start_day} {start_hour:02d}:00Z to Day {end_day} {end_hour:02d}:00Z"
            }
        except:
            return {'raw': period_str, 'error': 'Failed to parse valid period'}

    def _calculate_duration(self, start_day: int, start_hour: int, end_day: int, end_hour: int) -> int:
        """Calculate duration in hours between start and end times"""
        try:
            if end_day >= start_day:
                return (end_day - start_day) * 24 + (end_hour - start_hour)
            else:
                # Handle month rollover
                return (31 - start_day + end_day) * 24 + (end_hour - start_hour)
        except:
            return 0

    def _split_forecast_sections(self, forecast_text: str) -> tuple:
        """Split TAF text into base forecast and change groups"""
        # Find change indicators
        change_pattern = r'\b(FM\d{6}|TEMPO\s+\d{4}/\d{4}|BECMG\s+\d{4}/\d{4}|PROB[34]0\s+\d{4}/\d{4}|PROB[34]0\s+TEMPO\s+\d{4}/\d{4})'
        
        matches = list(re.finditer(change_pattern, forecast_text))
        
        if not matches:
            # No change groups, entire text is base forecast
            return forecast_text.strip(), []
        
        # Base forecast is everything before the first change group
        base_forecast = forecast_text[:matches[0].start()].strip()
        
        # Extract change groups
        change_groups = []
        for i, match in enumerate(matches):
            start_pos = match.start()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(forecast_text)
            group_text = forecast_text[start_pos:end_pos].strip()
            change_groups.append(group_text)
            
        return base_forecast, change_groups

    def _parse_forecast_conditions(self, conditions_text: str) -> Dict:
        """Parse forecast conditions (wind, visibility, weather, clouds)"""
        parts = conditions_text.strip().split()
        
        result = {
            'raw': conditions_text,
            'wind': {},
            'visibility': {},
            'weather': [],
            'clouds': [],
            'parsing_errors': []
        }
        
        i = 0
        while i < len(parts):
            part = parts[i]
            
            # Parse wind
            if re.match(r'(\d{3}|VRB)(\d{2,3})(G\d{2,3})?(KT|MPS)', part):
                result['wind'] = self._parse_wind(part)
                i += 1
                continue
                
            # Parse visibility
            if self._is_visibility(part):
                result['visibility'] = self._parse_visibility(part)
                i += 1
                continue
                
            # Parse weather phenomena
            if self._is_weather_phenomenon(part):
                result['weather'].append(self._parse_weather(part))
                i += 1
                continue
                
            # Parse cloud layers
            if self._is_cloud_layer(part):
                result['clouds'].append(self._parse_cloud_layer(part))
                i += 1
                continue
                
            # Skip unknown parts
            result['parsing_errors'].append(f"Unknown component: {part}")
            i += 1
            
        return result

    def _parse_change_group(self, group_text: str) -> Dict:
        """Parse a change group (FM, TEMPO, BECMG, etc.)"""
        parts = group_text.strip().split()
        if not parts:
            return None
            
        result = {
            'raw': group_text,
            'type': None,
            'time_period': None,
            'probability': None,
            'conditions': {}
        }
        
        # Parse change type and time
        first_part = parts[0]
        
        if first_part.startswith('FM'):
            result['type'] = 'From'
            time_str = first_part[2:]  # Remove 'FM'
            result['time_period'] = self._parse_fm_time(time_str)
            conditions_start = 1
            
        elif first_part.startswith('TEMPO'):
            result['type'] = 'Temporary'
            if len(parts) > 1 and '/' in parts[1]:
                result['time_period'] = self._parse_period_time(parts[1])
                conditions_start = 2
            else:
                conditions_start = 1
                
        elif first_part.startswith('BECMG'):
            result['type'] = 'Becoming'
            if len(parts) > 1 and '/' in parts[1]:
                result['time_period'] = self._parse_period_time(parts[1])
                conditions_start = 2
            else:
                conditions_start = 1
                
        elif first_part.startswith('PROB'):
            prob_match = re.match(r'PROB(\d{2})', first_part)
            if prob_match:
                result['probability'] = int(prob_match.group(1))
                result['type'] = f"{result['probability']}% Probability"
                
                if len(parts) > 1 and '/' in parts[1]:
                    result['time_period'] = self._parse_period_time(parts[1])
                    conditions_start = 2
                elif len(parts) > 1 and parts[1] == 'TEMPO':
                    result['type'] += ' Temporary'
                    if len(parts) > 2 and '/' in parts[2]:
                        result['time_period'] = self._parse_period_time(parts[2])
                        conditions_start = 3
                    else:
                        conditions_start = 2
                else:
                    conditions_start = 1
            else:
                conditions_start = 1
        else:
            conditions_start = 0
            
        # Parse conditions
        if conditions_start < len(parts):
            conditions_text = ' '.join(parts[conditions_start:])
            result['conditions'] = self._parse_forecast_conditions(conditions_text)
            
        return result

    def _parse_fm_time(self, time_str: str) -> Dict:
        """Parse FM time (e.g., 270200 = 27th day, 02:00Z)"""
        try:
            if len(time_str) == 6:
                day = int(time_str[:2])
                hour = int(time_str[2:4])
                minute = int(time_str[4:6])
                
                return {
                    'day': day,
                    'hour': hour,
                    'minute': minute,
                    'formatted': f"Day {day}, {hour:02d}:{minute:02d} UTC"
                }
        except:
            pass
        return {'raw': time_str, 'error': 'Failed to parse FM time'}

    def _parse_period_time(self, period_str: str) -> Dict:
        """Parse period time (e.g., 2618/2622)"""
        try:
            start_str, end_str = period_str.split('/')
            start_day = int(start_str[:2])
            start_hour = int(start_str[2:])
            end_day = int(end_str[:2])
            end_hour = int(end_str[2:])
            
            return {
                'from': {
                    'day': start_day,
                    'hour': start_hour,
                    'formatted': f"Day {start_day}, {start_hour:02d}:00 UTC"
                },
                'to': {
                    'day': end_day,
                    'hour': end_hour,
                    'formatted': f"Day {end_day}, {end_hour:02d}:00 UTC"
                },
                'description': f"From Day {start_day} {start_hour:02d}:00Z to Day {end_day} {end_hour:02d}:00Z"
            }
        except:
            return {'raw': period_str, 'error': 'Failed to parse period time'}

    # Reuse parsing methods from METAR parser
    def _parse_wind(self, wind_str: str) -> Dict:
        """Parse wind information (reused from METAR parser)"""
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
        
        if direction == 'VRB':
            desc = f"Variable direction at {speed} {result['unit']}"
        else:
            desc = f"From {direction}° at {speed} {result['unit']}"
            
        if gust_speed:
            desc += f", gusting to {gust_speed} {result['unit']}"
            
        result['description'] = desc
        return result

    def _is_visibility(self, code: str) -> bool:
        """Check if code represents visibility"""
        return ('SM' in code or 
                re.match(r'\d{4}', code) or 
                code.startswith('P6SM') or 
                code.startswith('M1/4SM'))

    def _parse_visibility(self, vis_str: str) -> Dict:
        """Parse visibility (reused from METAR parser with TAF additions)"""
        # Handle P6SM (greater than 6 statute miles)
        if vis_str == 'P6SM':
            return {
                'distance': 6,
                'greater_than': True,
                'unit': 'statute_miles',
                'description': 'Greater than 6 statute miles'
            }
            
        # Handle M1/4SM (less than 1/4 statute mile)
        if vis_str == 'M1/4SM':
            return {
                'distance': 0.25,
                'less_than': True,
                'unit': 'statute_miles',
                'description': 'Less than 1/4 statute mile'
            }
            
        # Regular visibility parsing
        if 'SM' in vis_str:
            vis_match = re.match(r'(\d+/?(\d+)?)SM', vis_str)
            if vis_match:
                vis_val = vis_match.group(1)
                if '/' in vis_val:
                    parts = vis_val.split('/')
                    distance = float(parts[0]) / float(parts[1])
                else:
                    distance = float(vis_val)
                    
                return {
                    'distance': distance,
                    'unit': 'statute_miles',
                    'description': f"{vis_val} statute miles"
                }
                
        elif re.match(r'\d{4}', vis_str):
            distance = int(vis_str)
            return {
                'distance': distance,
                'unit': 'meters',
                'description': f"{distance} meters"
            }
            
        return {'raw': vis_str, 'error': 'Failed to parse visibility'}

    def _is_weather_phenomenon(self, code: str) -> bool:
        """Check if code represents weather phenomena"""
        clean_code = code.lstrip('-+')
        return any(phenom in clean_code for phenom in self.weather_phenomena.keys())

    def _parse_weather(self, weather_str: str) -> Dict:
        """Parse weather phenomena (reused from METAR parser)"""
        result = {
            'raw': weather_str,
            'intensity': 'moderate',
            'phenomena': [],
            'description': ''
        }
        
        if weather_str.startswith('-'):
            result['intensity'] = 'light'
            weather_str = weather_str[1:]
        elif weather_str.startswith('+'):
            result['intensity'] = 'heavy'
            weather_str = weather_str[1:]
            
        desc_parts = []
        i = 0
        while i < len(weather_str):
            for length in [2, 1]:
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
                i += 1
                
        result['description'] = f"{result['intensity'].title()} {' '.join(desc_parts)}"
        return result

    def _is_cloud_layer(self, code: str) -> bool:
        """Check if code represents cloud layer"""
        return any(code.startswith(cloud_type) for cloud_type in self.cloud_types.keys())

    def _parse_cloud_layer(self, cloud_str: str) -> Dict:
        """Parse cloud layer (reused from METAR parser)"""
        for cloud_type in self.cloud_types.keys():
            if cloud_str.startswith(cloud_type):
                height_str = cloud_str[len(cloud_type):]
                if height_str.isdigit():
                    height = int(height_str) * 100
                    return {
                        'type': cloud_type,
                        'type_description': self.cloud_types[cloud_type],
                        'height_feet': height,
                        'description': f"{self.cloud_types[cloud_type]} at {height:,} feet"
                    }
                    
        return {'raw': cloud_str, 'error': 'Failed to parse cloud layer'}


# Convenience function for easy import
def parse_taf(raw_taf: str) -> Dict:
    """
    Parse a raw TAF string into structured data
    
    Args:
        raw_taf (str): Raw TAF string
        
    Returns:
        Dict: Parsed TAF data
    """
    parser = TafParser()
    return parser.parse_taf(raw_taf)