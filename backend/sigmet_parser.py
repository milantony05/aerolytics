"""
SIGMET Parser Module for Aerolytics

This module provides functionality to parse and analyze SIGMET (Significant Meteorological Information) 
data for aviation weather hazards.

SIGMET provides information about:
- Severe turbulence
- Severe icing
- Dust/sandstorms
- Volcanic ash
- Tropical cyclones
- Severe squall lines
- Hail
- Severe mountain wave activity
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import requests


class SigmetParser:
    def __init__(self):
        self.hazard_types = {
            'TURB': 'Turbulence',
            'ICE': 'Icing', 
            'IFR': 'Instrument Flight Rules',
            'MTN_OBSCN': 'Mountain Obscuration',
            'SFC_WND': 'Surface Wind',
            'LLWS': 'Low Level Wind Shear',
            'CONVECTIVE': 'Convective Activity',
            'FZLVL': 'Freezing Level',
            'MULT': 'Multiple Hazards'
        }
        
        self.severity_levels = {
            'LIGHT': 'Light',
            'MOD': 'Moderate', 
            'SEV': 'Severe',
            'EXTREME': 'Extreme'
        }
        
        self.flight_levels = {
            'SFC': 'Surface',
            'FL': 'Flight Level'
        }

    def parse_sigmet_raw(self, sigmet_text: str) -> Dict:
        """
        Parse raw SIGMET text into structured data
        """
        try:
            parsed = {
                'raw_text': sigmet_text,
                'type': 'SIGMET',
                'hazard': self._extract_hazard(sigmet_text),
                'severity': self._extract_severity(sigmet_text),
                'area': self._extract_area(sigmet_text),
                'altitude': self._extract_altitude(sigmet_text),
                'valid_time': self._extract_valid_time(sigmet_text),
                'movement': self._extract_movement(sigmet_text),
                'outlook': self._extract_outlook(sigmet_text)
            }
            return parsed
        except Exception as e:
            return {
                'raw_text': sigmet_text,
                'error': f"Failed to parse SIGMET: {str(e)}",
                'type': 'SIGMET'
            }

    def _extract_hazard(self, text: str) -> str:
        """Extract hazard type from SIGMET text"""
        text_upper = text.upper()
        
        # Common hazard patterns
        if 'TURB' in text_upper or 'TURBULENCE' in text_upper:
            return 'Turbulence'
        elif 'ICE' in text_upper or 'ICING' in text_upper:
            return 'Icing'  
        elif 'TS' in text_upper or 'THUNDERSTORM' in text_upper:
            return 'Thunderstorms'
        elif 'DUST' in text_upper or 'SAND' in text_upper:
            return 'Dust/Sand'
        elif 'VA' in text_upper or 'VOLCANIC' in text_upper:
            return 'Volcanic Ash'
        elif 'TC' in text_upper or 'TROPICAL' in text_upper:
            return 'Tropical Cyclone'
        elif 'SQL' in text_upper or 'SQUALL' in text_upper:
            return 'Squall Line'
        elif 'GR' in text_upper or 'HAIL' in text_upper:
            return 'Hail'
        elif 'MTW' in text_upper or 'MOUNTAIN WAVE' in text_upper:
            return 'Mountain Wave'
        else:
            return 'Unknown Hazard'

    def _extract_severity(self, text: str) -> str:
        """Extract severity level from SIGMET text"""
        text_upper = text.upper()
        
        if 'SEV' in text_upper or 'SEVERE' in text_upper:
            return 'Severe'
        elif 'MOD' in text_upper or 'MODERATE' in text_upper:
            return 'Moderate'
        elif 'LIGHT' in text_upper:
            return 'Light'
        elif 'EXTREME' in text_upper:
            return 'Extreme'
        else:
            return 'Not Specified'

    def _extract_area(self, text: str) -> str:
        """Extract affected area from SIGMET text"""
        # Look for coordinate patterns or area descriptions
        area_match = re.search(r'(\d{4}N \d{5}W.*?)|([A-Z]{2,4}[\s\-][A-Z]{2,4})', text)
        if area_match:
            return area_match.group(0)
        
        # Look for state/region mentions
        state_match = re.search(r'\b[A-Z]{2}\b', text)
        if state_match:
            return f"Area including {state_match.group(0)}"
            
        return "Area not specified"

    def _extract_altitude(self, text: str) -> Dict:
        """Extract altitude information from SIGMET text"""
        altitude_info = {
            'base': None,
            'top': None,
            'text': None
        }
        
        # Look for flight level patterns
        fl_pattern = re.search(r'FL(\d{3})', text)
        if fl_pattern:
            altitude_info['flight_level'] = int(fl_pattern.group(1)) * 100
        
        # Look for altitude ranges
        alt_range = re.search(r'(\d{1,2}),?(\d{3})\s*-\s*(\d{1,2}),?(\d{3})\s*FT', text)
        if alt_range:
            altitude_info['base'] = int(alt_range.group(1) + alt_range.group(2))
            altitude_info['top'] = int(alt_range.group(3) + alt_range.group(4))
        
        # Look for surface mentions
        if 'SFC' in text.upper() or 'SURFACE' in text.upper():
            altitude_info['base'] = 0
            
        return altitude_info

    def _extract_valid_time(self, text: str) -> Dict:
        """Extract valid time period from SIGMET text"""
        time_info = {
            'start': None,
            'end': None,
            'text': None
        }
        
        # Look for time patterns like 1200/1600
        time_pattern = re.search(r'(\d{4})/(\d{4})', text)
        if time_pattern:
            time_info['start'] = time_pattern.group(1)
            time_info['end'] = time_pattern.group(2)
            time_info['text'] = f"Valid {time_pattern.group(1)}-{time_pattern.group(2)}Z"
        
        return time_info

    def _extract_movement(self, text: str) -> str:
        """Extract movement information from SIGMET text"""
        text_upper = text.upper()
        
        # Look for movement patterns
        if 'MOV' in text_upper:
            mov_match = re.search(r'MOV\s+([NSEW]+)\s+(\d+)\s*KT', text_upper)
            if mov_match:
                return f"Moving {mov_match.group(1)} at {mov_match.group(2)} knots"
        
        if 'STNR' in text_upper or 'STATIONARY' in text_upper:
            return "Stationary"
            
        return "Movement not specified"

    def _extract_outlook(self, text: str) -> str:
        """Extract outlook/forecast information from SIGMET text"""
        text_upper = text.upper()
        
        if 'INTSF' in text_upper or 'INTENSIFYING' in text_upper:
            return "Intensifying"
        elif 'WKN' in text_upper or 'WEAKENING' in text_upper:
            return "Weakening"
        elif 'NC' in text_upper or 'NO CHANGE' in text_upper:
            return "No Change"
        elif 'CONT' in text_upper or 'CONTINUING' in text_upper:
            return "Continuing"
        else:
            return "Not specified"

    def analyze_sigmets_for_flight(self, sigmets: List[Dict], route_coords: List[tuple] = None) -> Dict:
        """
        Analyze SIGMET data for flight planning
        """
        analysis = {
            'active_sigmets': len(sigmets),
            'hazard_summary': {},
            'flight_impacts': [],
            'recommendations': []
        }
        
        # Count hazard types
        for sigmet in sigmets:
            hazard = sigmet.get('hazard', 'Unknown')
            analysis['hazard_summary'][hazard] = analysis['hazard_summary'].get(hazard, 0) + 1
        
        # Generate flight impacts
        if sigmets:
            analysis['flight_impacts'].append(f"{len(sigmets)} active SIGMET(s)")
            
            # Check for high-impact hazards
            high_impact_hazards = ['Turbulence', 'Icing', 'Thunderstorms', 'Volcanic Ash']
            for hazard in high_impact_hazards:
                if hazard in analysis['hazard_summary']:
                    count = analysis['hazard_summary'][hazard]
                    analysis['flight_impacts'].append(f"{count} {hazard} SIGMET(s) active")
        
        # Generate recommendations
        if analysis['hazard_summary']:
            if 'Turbulence' in analysis['hazard_summary']:
                analysis['recommendations'].append("Consider turbulence avoidance and secure cabin")
            if 'Icing' in analysis['hazard_summary']:
                analysis['recommendations'].append("Verify anti-ice/de-ice systems operational")
            if 'Thunderstorms' in analysis['hazard_summary']:
                analysis['recommendations'].append("Plan for weather deviations and delays")
            if 'Volcanic Ash' in analysis['hazard_summary']:
                analysis['recommendations'].append("AVOID - Volcanic ash can cause engine failure")
        else:
            analysis['recommendations'].append("No active SIGMETs - Monitor for updates")
        
        return analysis

    def get_current_sigmets(self) -> List[Dict]:
        """
        Fetch and parse current SIGMET data from aviationweather.gov
        """
        try:
            # Fetch SIGMET data
            sigmet_url = "https://aviationweather.gov/api/data/isigmet"
            response = requests.get(sigmet_url, timeout=10)
            
            if response.status_code == 200:
                raw_data = response.text.strip()
                if raw_data:
                    # Split multiple SIGMETs if present
                    sigmet_texts = raw_data.split('\n\n')
                    parsed_sigmets = []
                    
                    for sigmet_text in sigmet_texts:
                        if sigmet_text.strip():
                            parsed = self.parse_sigmet_raw(sigmet_text.strip())
                            parsed_sigmets.append(parsed)
                    
                    return parsed_sigmets
                else:
                    return []
            else:
                return []
                
        except Exception as e:
            return [{'error': f"Failed to fetch SIGMET data: {str(e)}"}]