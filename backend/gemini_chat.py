import google.generativeai as genai
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router for Gemini chat endpoints
router = APIRouter()

# Configure Gemini API
API_KEY = 'AIzaSyBRxFkLNWje4AVHdRQ_K0o2zBXZcdjZjJ0'
genai.configure(api_key=API_KEY)

# Initialize the model with the correct model name for Generative Language API
model = genai.GenerativeModel('gemini-2.5-flash')

# Simple in-memory conversation storage (single chat)
conversation_history = []

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    system_prompt: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    success: bool
    error: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_with_gemini(request: ChatRequest):
    """
    Chat endpoint that uses Google's generativeai library with conversation memory and weather data
    """
    global conversation_history
    
    try:
        logger.info(f"Received chat request: {request.message[:50]}...")
        
        # Check if user is asking about weather and needs data
        weather_context = ""
        if any(word in request.message.lower() for word in ['weather', 'temperature', 'wind', 'metar', 'conditions', 'forecast', 'taf', 'sigmet', 'pirep', 'turbulence', 'icing', 'hazard']):
            import re
            import requests
            
            # City to airport code mapping for common cities
            city_to_airport = {
                'bangalore': 'VOBL',
                'bengaluru': 'VOBL', 
                'mumbai': 'VABB',
                'delhi': 'VIDP',
                'chennai': 'VOMM',
                'kolkata': 'VECC',
                'hyderabad': 'VOHS',
                'pune': 'VAPO',
                'ahmedabad': 'VAAH',
                'kochi': 'VOCI',
                'new york': 'KJFK',
                'los angeles': 'KLAX',
                'chicago': 'KORD',
                'london': 'EGLL',
                'paris': 'LFPG',
                'tokyo': 'RJTT',
                'singapore': 'WSSS',
                'dubai': 'OMDB'
            }
            
            airport_code = None
            
            # First try to find explicit airport codes
            airport_match = re.search(r'\b[A-Z]{4}\b|\b[A-Z]{3}\b', request.message.upper())
            if airport_match:
                airport_code = airport_match.group()
            else:
                # Try to find city names and convert to airport codes
                message_lower = request.message.lower()
                for city, code in city_to_airport.items():
                    if city in message_lower:
                        airport_code = code
                        logger.info(f"Converted city '{city}' to airport code '{code}'")
                        break
            
            if airport_code:
                weather_data_parts = []
                
                try:
                    # Get METAR data
                    metar_url = f"https://aviationweather.gov/api/data/metar?ids={airport_code}&format=decoded"
                    metar_response = requests.get(metar_url, timeout=5)
                    if metar_response.status_code == 200 and metar_response.text.strip():
                        weather_data_parts.append(f"METAR: {metar_response.text.strip()}")
                        
                    # Get TAF data
                    taf_url = f"https://aviationweather.gov/api/data/taf?ids={airport_code}&format=decoded"
                    taf_response = requests.get(taf_url, timeout=5)
                    if taf_response.status_code == 200 and taf_response.text.strip():
                        weather_data_parts.append(f"TAF: {taf_response.text.strip()}")
                        
                    # Get PIREP data (pilot reports)
                    pirep_url = f"https://aviationweather.gov/api/data/pirep?ids={airport_code}"
                    pirep_response = requests.get(pirep_url, timeout=5)
                    if pirep_response.status_code == 200 and pirep_response.text.strip():
                        weather_data_parts.append(f"PIREP: {pirep_response.text.strip()}")
                        
                except Exception as e:
                    logger.warning(f"Could not fetch weather data for {airport_code}: {e}")
                
                # Get SIGMET and AIRMET data (area-wide hazards)
                try:
                    # Get SIGMETs
                    sigmet_url = "https://aviationweather.gov/api/data/isigmet"
                    sigmet_response = requests.get(sigmet_url, timeout=5)
                    if sigmet_response.status_code == 200 and sigmet_response.text.strip():
                        weather_data_parts.append(f"SIGMET: {sigmet_response.text.strip()}")
                    
                    # Get AIRMETs    
                    airmet_url = "https://aviationweather.gov/api/data/airsigmet"
                    airmet_response = requests.get(airmet_url, timeout=5)
                    if airmet_response.status_code == 200 and airmet_response.text.strip():
                        weather_data_parts.append(f"AIRMET: {airmet_response.text.strip()}")
                        
                except Exception as e:
                    logger.warning(f"Could not fetch SIGMET/AIRMET data: {e}")
                
                if weather_data_parts:
                    weather_context = f"\n\nAVIATION WEATHER DATA for {airport_code}:\n" + "\n\n".join(weather_data_parts) + "\n"
                    logger.info(f"Retrieved comprehensive weather data for {airport_code}")
            
            # If no airport code found, still get general SIGMET/AIRMET data
            elif not airport_code:
                try:
                    general_hazards = []
                    
                    # Get current SIGMETs
                    sigmet_url = "https://aviationweather.gov/api/data/isigmet"
                    sigmet_response = requests.get(sigmet_url, timeout=5)
                    if sigmet_response.status_code == 200 and sigmet_response.text.strip():
                        general_hazards.append(f"CURRENT SIGMETS: {sigmet_response.text.strip()}")
                    
                    # Get current AIRMETs
                    airmet_url = "https://aviationweather.gov/api/data/airsigmet"
                    airmet_response = requests.get(airmet_url, timeout=5)
                    if airmet_response.status_code == 200 and airmet_response.text.strip():
                        general_hazards.append(f"CURRENT AIRMETS: {airmet_response.text.strip()}")
                    
                    if general_hazards:
                        weather_context = f"\n\nCURRENT AVIATION HAZARDS:\n" + "\n\n".join(general_hazards) + "\n"
                        logger.info("Retrieved general aviation hazard data")
                        
                except Exception as e:
                    logger.warning(f"Could not fetch general hazard data: {e}")
        
        # Default system prompt for aviation assistant
        default_system_prompt = """You are a friendly aviation weather copilot with access to live weather data. Speak like an experienced pilot talking to another pilot - casual, confident, and helpful.

RESPONSE STYLE:
- Be conversational and natural, not robotic
- Use pilot slang and aviation terms naturally 
- Keep it concise but engaging (2-3 sentences)
- Sound like you're talking in the cockpit, not reading a manual
- Add personality - be encouraging about good weather, cautious about bad weather

EXAMPLES OF GOOD RESPONSES:
- "Bangalore's looking pretty good right now - winds are light out of the west at 12 knots, visibility is solid at 6km. Perfect VFR conditions!"
- "Delhi's got some decent weather today. You've got WSW winds at 15 knots and visibility is holding at 4000m - not bad for IFR if needed."
- "Mumbai's a bit rough today with moderate turbulence reported. Might want to brief the passengers and check your routing."

Use the EXACT weather data provided, but present it in a natural, pilot-to-pilot way."""
        
        # Use provided system prompt or default
        system_prompt = request.system_prompt or default_system_prompt
        
        # Build conversation context
        conversation_context = f"{system_prompt}{weather_context}\n\n"
        for msg in conversation_history:
            conversation_context += f"User: {msg['user']}\nAssistant: {msg['assistant']}\n\n"
        conversation_context += f"User: {request.message}\nAssistant:"
        
        # Generate response using Gemini
        logger.info("Sending request to Gemini API...")
        response = model.generate_content(conversation_context)
        
        logger.info("Successfully received response from Gemini")
        
        # Store conversation
        conversation_history.append({
            "user": request.message,
            "assistant": response.text
        })
        
        # Keep only last 10 exchanges to prevent memory issues
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
        
        return ChatResponse(
            response=response.text,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return ChatResponse(
            response="Sorry, I encountered an error processing your request.",
            success=False,
            error=str(e)
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "gemini-chat"}