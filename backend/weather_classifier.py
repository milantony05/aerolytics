"""
Weather Classifier Module for Aerolytics

This module provides functionality to classify weather conditions based on parsed 
METAR data into categories that help pilots quickly assess weather severity.

Weather Categories:
- Clear: Good flying conditions with minimal weather impact
- Significant: Marginal conditions that require attention
- Severe: Poor conditions that may significantly impact flight operations

Classification Criteria:
- Wind: Speed, gusts, and variability
- Visibility: Distance and obstructions
- Weather: Precipitation, fog, storms
- Clouds: Coverage and height
- Temperature: Extreme conditions
"""

from typing import Dict, List, Optional, Tuple
import re


class WeatherClassifier:
    def __init__(self):
        # Classification thresholds
        self.thresholds = {
            'wind': {
                'significant_speed': 15,    # knots
                'severe_speed': 25,         # knots
                'significant_gust': 20,     # knots
                'severe_gust': 35,          # knots
            },
            'visibility': {
                'significant_sm': 3,        # statute miles
                'severe_sm': 1,             # statute miles
                'significant_m': 5000,      # meters
                'severe_m': 1600,           # meters
            },
            'clouds': {
                'significant_ceiling': 1000,  # feet AGL
                'severe_ceiling': 500,        # feet AGL
            },
            'temperature': {
                'severe_hot_c': 40,         # Celsius
                'severe_cold_c': -20,       # Celsius
            }
        }
        
        # Weather phenomena severity
        self.weather_severity = {
            # Severe weather phenomena
            'TS': 'severe',     # Thunderstorm
            'GR': 'severe',     # Hail
            'FC': 'severe',     # Funnel cloud/tornado
            'SS': 'severe',     # Sandstorm
            'SQ': 'severe',     # Squalls
            '+': 'severe',      # Heavy intensity (when prefix)
            
            # Significant weather phenomena
            'RA': 'significant', # Rain
            'SN': 'significant', # Snow
            'FG': 'significant', # Fog
            'BR': 'significant', # Mist
            'FZ': 'significant', # Freezing
            'SH': 'significant', # Showers
            'IC': 'significant', # Ice crystals
            'PL': 'significant', # Ice pellets
            
            # Light phenomena (when light intensity)
            '-': 'light'
        }

    def classify_weather(self, parsed_metar: Dict, parsed_taf: Optional[Dict] = None) -> Dict:
        """
        Classify weather conditions based on parsed METAR and optional TAF data
        
        Args:
            parsed_metar (Dict): Parsed METAR data
            parsed_taf (Dict, optional): Parsed TAF data for forecast consideration
            
        Returns:
            Dict: Weather classification with category, score, and reasoning
        """
        if not parsed_metar or 'error' in parsed_metar:
            return {
                'category': 'Unknown',
                'score': 0,
                'confidence': 'Low',
                'reasoning': ['Unable to classify due to parsing errors'],
                'factors': {}
            }
            
        # Initialize classification result
        classification = {
            'category': 'Clear',
            'score': 0,
            'confidence': 'High',
            'reasoning': [],
            'factors': {
                'wind': {'score': 0, 'impact': 'None'},
                'visibility': {'score': 0, 'impact': 'None'},
                'weather': {'score': 0, 'impact': 'None'},
                'clouds': {'score': 0, 'impact': 'None'},
                'temperature': {'score': 0, 'impact': 'None'}
            }
        }
        
        # Analyze each weather factor
        total_score = 0
        
        # Wind analysis
        wind_score, wind_impact, wind_reason = self._analyze_wind(parsed_metar.get('wind', {}))
        classification['factors']['wind'] = {'score': wind_score, 'impact': wind_impact}
        if wind_reason:
            classification['reasoning'].append(wind_reason)
        total_score += wind_score
        
        # Visibility analysis
        vis_score, vis_impact, vis_reason = self._analyze_visibility(parsed_metar.get('visibility', {}))
        classification['factors']['visibility'] = {'score': vis_score, 'impact': vis_impact}
        if vis_reason:
            classification['reasoning'].append(vis_reason)
        total_score += vis_score
        
        # Weather phenomena analysis
        wx_score, wx_impact, wx_reason = self._analyze_weather_phenomena(parsed_metar.get('weather', []))
        classification['factors']['weather'] = {'score': wx_score, 'impact': wx_impact}
        if wx_reason:
            classification['reasoning'].extend(wx_reason)
        total_score += wx_score
        
        # Cloud analysis
        cloud_score, cloud_impact, cloud_reason = self._analyze_clouds(parsed_metar.get('clouds', []))
        classification['factors']['clouds'] = {'score': cloud_score, 'impact': cloud_impact}
        if cloud_reason:
            classification['reasoning'].append(cloud_reason)
        total_score += cloud_score
        
        # Temperature analysis
        temp_score, temp_impact, temp_reason = self._analyze_temperature(parsed_metar.get('temperature', {}))
        classification['factors']['temperature'] = {'score': temp_score, 'impact': temp_impact}
        if temp_reason:
            classification['reasoning'].append(temp_reason)
        total_score += temp_score
        
        # Include TAF forecast considerations
        if parsed_taf and not parsed_taf.get('error'):
            forecast_impact = self._analyze_forecast_trends(parsed_taf)
            if forecast_impact:
                classification['reasoning'].extend(forecast_impact)
                # Add slight score adjustment for forecast trends
                if any('deteriorating' in reason.lower() for reason in forecast_impact):
                    total_score += 1
        
        # Determine final category based on total score
        classification['score'] = total_score
        
        if total_score >= 8:
            classification['category'] = 'Severe'
            classification['confidence'] = 'High'
        elif total_score >= 4:
            classification['category'] = 'Significant'
            classification['confidence'] = 'High'
        else:
            classification['category'] = 'Clear'
            classification['confidence'] = 'High'
            
        # Add default reasoning if none provided
        if not classification['reasoning']:
            classification['reasoning'] = [f"Weather conditions are {classification['category'].lower()} with minimal impact on flight operations"]
            
        return classification

    def _analyze_wind(self, wind_data: Dict) -> Tuple[int, str, str]:
        """Analyze wind conditions and return score, impact level, and reasoning"""
        if not wind_data or 'error' in wind_data:
            return 0, 'None', None
            
        score = 0
        impact = 'None'
        reason = None
        
        speed = wind_data.get('speed', 0)
        gust_speed = wind_data.get('gust_speed', 0)
        variable = wind_data.get('direction_variable', False)
        
        # Check wind speed
        if speed >= self.thresholds['wind']['severe_speed']:
            score += 3
            impact = 'Severe'
            reason = f"Strong winds at {speed} knots"
        elif speed >= self.thresholds['wind']['significant_speed']:
            score += 2
            impact = 'Significant'
            reason = f"Moderate winds at {speed} knots"
        elif speed >= 10:
            score += 1
            impact = 'Minor'
            reason = f"Light winds at {speed} knots"
            
        # Check gusts
        if gust_speed:
            if gust_speed >= self.thresholds['wind']['severe_gust']:
                score += 3
                impact = 'Severe'
                reason = f"Strong gusts to {gust_speed} knots"
            elif gust_speed >= self.thresholds['wind']['significant_gust']:
                score += 2
                impact = 'Significant' if impact != 'Severe' else 'Severe'
                reason = f"Moderate gusts to {gust_speed} knots"
            else:
                score += 1
                
        # Check variable winds
        if variable:
            score += 1
            if not reason:
                reason = "Variable wind direction"
                
        return score, impact, reason

    def _analyze_visibility(self, visibility_data: Dict) -> Tuple[int, str, str]:
        """Analyze visibility conditions"""
        if not visibility_data or 'error' in visibility_data:
            return 0, 'None', None
            
        score = 0
        impact = 'None'
        reason = None
        
        distance = visibility_data.get('distance', float('inf'))
        unit = visibility_data.get('unit', 'statute_miles')
        
        # Convert to common unit for comparison
        if unit == 'meters':
            if distance <= self.thresholds['visibility']['severe_m']:
                score += 4
                impact = 'Severe'
                reason = f"Very low visibility: {distance} meters"
            elif distance <= self.thresholds['visibility']['significant_m']:
                score += 2
                impact = 'Significant'
                reason = f"Reduced visibility: {distance} meters"
        else:  # statute_miles
            if distance <= self.thresholds['visibility']['severe_sm']:
                score += 4
                impact = 'Severe'
                reason = f"Very low visibility: {distance} statute miles"
            elif distance <= self.thresholds['visibility']['significant_sm']:
                score += 2
                impact = 'Significant'
                reason = f"Reduced visibility: {distance} statute miles"
                
        return score, impact, reason

    def _analyze_weather_phenomena(self, weather_list: List[Dict]) -> Tuple[int, str, List[str]]:
        """Analyze weather phenomena"""
        if not weather_list:
            return 0, 'None', []
            
        score = 0
        impact = 'None'
        reasons = []
        
        for weather in weather_list:
            if 'phenomena' not in weather:
                continue
                
            intensity = weather.get('intensity', 'moderate')
            phenomena = weather.get('phenomena', [])
            
            # Check each phenomenon
            for phenomenon in phenomena:
                code = phenomenon.get('code', '')
                desc = phenomenon.get('description', '')
                
                # Check for severe weather
                if code in self.weather_severity:
                    severity = self.weather_severity[code]
                    if severity == 'severe':
                        score += 4
                        impact = 'Severe'
                        reasons.append(f"Severe weather: {desc.lower()}")
                    elif severity == 'significant':
                        if intensity == 'heavy':
                            score += 3
                            impact = 'Severe' if impact != 'Severe' else 'Severe'
                            reasons.append(f"Heavy {desc.lower()}")
                        else:
                            score += 2
                            impact = 'Significant' if impact not in ['Severe'] else impact
                            reasons.append(f"{intensity.title()} {desc.lower()}")
                            
            # Check intensity modifiers
            if intensity == 'heavy' and score == 0:
                score += 2
                impact = 'Significant'
                reasons.append("Heavy precipitation intensity")
                
        return score, impact, reasons

    def _analyze_clouds(self, clouds_list: List[Dict]) -> Tuple[int, str, str]:
        """Analyze cloud conditions"""
        if not clouds_list:
            return 0, 'None', None
            
        score = 0
        impact = 'None'
        reason = None
        
        # Find the lowest ceiling (BKN or OVC)
        lowest_ceiling = float('inf')
        ceiling_type = None
        
        for cloud in clouds_list:
            if 'error' in cloud:
                continue
                
            cloud_type = cloud.get('type', '')
            height = cloud.get('height_feet', float('inf'))
            
            # Check for ceiling conditions (BKN or OVC)
            if cloud_type in ['BKN', 'OVC'] and height < lowest_ceiling:
                lowest_ceiling = height
                ceiling_type = cloud.get('type_description', cloud_type)
                
        # Evaluate ceiling height
        if lowest_ceiling != float('inf'):
            if lowest_ceiling <= self.thresholds['clouds']['severe_ceiling']:
                score += 3
                impact = 'Severe'
                reason = f"Very low ceiling: {ceiling_type.lower()} at {lowest_ceiling:,} feet"
            elif lowest_ceiling <= self.thresholds['clouds']['significant_ceiling']:
                score += 2
                impact = 'Significant'
                reason = f"Low ceiling: {ceiling_type.lower()} at {lowest_ceiling:,} feet"
            elif lowest_ceiling <= 3000:
                score += 1
                impact = 'Minor'
                reason = f"Moderate ceiling: {ceiling_type.lower()} at {lowest_ceiling:,} feet"
                
        return score, impact, reason

    def _analyze_temperature(self, temperature_data: Dict) -> Tuple[int, str, str]:
        """Analyze temperature conditions"""
        if not temperature_data or 'error' in temperature_data:
            return 0, 'None', None
            
        score = 0
        impact = 'None'
        reason = None
        
        temp_c = temperature_data.get('temperature_celsius')
        if temp_c is None:
            return 0, 'None', None
            
        # Check for extreme temperatures
        if temp_c >= self.thresholds['temperature']['severe_hot_c']:
            score += 2
            impact = 'Significant'
            reason = f"Very high temperature: {temp_c}°C"
        elif temp_c <= self.thresholds['temperature']['severe_cold_c']:
            score += 2
            impact = 'Significant'
            reason = f"Very low temperature: {temp_c}°C"
            
        return score, impact, reason

    def _analyze_forecast_trends(self, parsed_taf: Dict) -> List[str]:
        """Analyze TAF forecast for deteriorating conditions"""
        trends = []
        
        if not parsed_taf or 'error' in parsed_taf:
            return trends
            
        change_groups = parsed_taf.get('change_groups', [])
        
        for group in change_groups:
            group_type = group.get('type', '')
            conditions = group.get('conditions', {})
            
            # Check for deteriorating visibility
            if conditions.get('visibility'):
                vis_distance = conditions['visibility'].get('distance', float('inf'))
                if vis_distance <= 3:  # Less than 3 SM/5000m
                    trends.append(f"Forecast shows deteriorating visibility ({group_type.lower()})")
                    
            # Check for adverse weather in forecast
            if conditions.get('weather'):
                for weather in conditions['weather']:
                    if any(phenom.get('code') in ['TS', 'GR', 'FC', '+'] 
                          for phenom in weather.get('phenomena', [])):
                        trends.append(f"Forecast shows severe weather ({group_type.lower()})")
                        
            # Check for low ceilings in forecast
            if conditions.get('clouds'):
                for cloud in conditions['clouds']:
                    if (cloud.get('type') in ['BKN', 'OVC'] and 
                        cloud.get('height_feet', float('inf')) <= 1000):
                        trends.append(f"Forecast shows low ceiling ({group_type.lower()})")
                        
        return trends


# Convenience function for easy import
def classify_weather(parsed_metar: Dict, parsed_taf: Optional[Dict] = None) -> Dict:
    """
    Classify weather conditions based on parsed METAR and optional TAF data
    
    Args:
        parsed_metar (Dict): Parsed METAR data
        parsed_taf (Dict, optional): Parsed TAF data
        
    Returns:
        Dict: Weather classification
    """
    classifier = WeatherClassifier()
    return classifier.classify_weather(parsed_metar, parsed_taf)