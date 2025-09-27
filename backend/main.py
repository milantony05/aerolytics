from fastapi import FastAPI, HTTPException
import requests
import httpx
from typing import List, Any, Dict
from fastapi.middleware.cors import CORSMiddleware
from metar import Metar
import numpy as np
from datetime import datetime
from gemini_chat import router as gemini_router
from sigmet_parser import SigmetParser
from metar_parser import MetarParser

app = FastAPI(title="Aviation Weather API")

# --- UNCHANGED: Your existing URLs and CORS setup ---
METAR_URL = "https://aviationweather.gov/api/data/metar"
PIREP_URL = "https://aviationweather.gov/api/data/pirep"
SIGMET_URL = "https://aviationweather.gov/api/data/isigmet"
AIRSIGMET_URL = "https://aviationweather.gov/api/data/airsigmet"
TAF_URL = "https://aviationweather.gov/api/data/taf"

origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Gemini chat router
app.include_router(gemini_router, prefix="/api/gemini", tags=["gemini"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Aerolytics Aviation Weather API",
        "version": "1.0.0",
        "endpoints": [
            "/metar/decoded/{icao}",
            "/metar/analyzed/{icao}", 
            "/route-weather/{departure_icao}/{arrival_icao}",
            "/sigmet/current",
            "/sigmet/analysis", 
            "/sigmet/raw",
            "/api/gemini/chat",
            "/api/gemini/health"
        ]
    }

# Comprehensive worldwide airport coordinates database
STATION_COORDS = {
    # United States Major Airports
    "KLAX": [33.9416, -118.4085],  # Los Angeles
    "KJFK": [40.6413, -73.7781],   # New York JFK
    "KORD": [41.9742, -87.9073],   # Chicago O'Hare
    "KATL": [33.6407, -84.4277],   # Atlanta
    "KSFO": [37.6188, -122.3750],  # San Francisco
    "KDEN": [39.8561, -104.6737],  # Denver
    "KLAS": [36.0840, -115.1537],  # Las Vegas
    "KBOS": [42.3656, -71.0096],   # Boston
    "KMIA": [25.7959, -80.2870],   # Miami
    "KSEA": [47.4502, -122.3088],  # Seattle
    
    # India Major Airports
    "VIDP": [28.5562, 77.1000],    # Delhi
    "VABB": [19.0896, 72.8656],    # Mumbai
    "VOBL": [12.9716, 77.5946],    # Bangalore
    "VOMM": [13.0827, 80.2707],    # Chennai
    "VECC": [22.6546, 88.4473],    # Kolkata
    "VOHS": [17.2313, 78.4298],    # Hyderabad
    "VOCI": [22.3284, 70.7794],    # Ahmedabad
    "VOSR": [11.1361, 75.9553],    # Calicut
    "VOTV": [8.4821, 76.9200],     # Thiruvananthapuram
    "VEGY": [26.1061, 91.5859],    # Guwahati
    
    # Europe Major Airports
    "EGLL": [51.4700, -0.4543],    # London Heathrow
    "LFPG": [49.0097, 2.5479],     # Paris Charles de Gaulle
    "EDDF": [50.0264, 8.5431],     # Frankfurt
    "EHAM": [52.3086, 4.7639],     # Amsterdam
    "LEMD": [40.4719, -3.5626],    # Madrid
    "LIRF": [41.8003, 12.2389],    # Rome
    "EGKK": [51.1481, -0.1903],    # London Gatwick
    "EDDM": [48.3538, 11.7861],    # Munich
    "LSZH": [47.4647, 8.5492],     # Zurich
    
    # Asia-Pacific Major Airports
    "RJTT": [35.7647, 140.3864],   # Tokyo Haneda
    "RKSI": [37.4691, 126.4505],   # Seoul Incheon
    "VHHH": [22.3080, 113.9185],   # Hong Kong
    "WSSS": [1.3644, 103.9915],    # Singapore
    "YBBN": [-27.3942, 153.1218],  # Brisbane
    "YSSY": [-33.9399, 151.1753],  # Sydney
    "NZAA": [-37.0082, 174.7850],  # Auckland
    "RJAA": [35.7720, 140.3929],   # Tokyo Narita
    
    # Middle East Major Airports
    "OMDB": [25.2532, 55.3657],    # Dubai
    "OTHH": [25.2731, 51.6089],    # Doha
    "OERK": [24.9576, 46.6986],    # Riyadh
    "LTBA": [40.9769, 28.8146],    # Istanbul
    
    # Canada Major Airports
    "CYYZ": [43.6777, -79.6248],   # Toronto
    "CYVR": [49.1967, -123.1816],  # Vancouver
    "CYUL": [45.4706, -73.7408],   # Montreal
    
    # Other Notable Airports
    "SBGR": [-23.4356, -46.4731],  # São Paulo
    "SAEZ": [-34.8222, -58.5358],  # Buenos Aires
    "FAJS": [-26.1392, 28.2460],   # Johannesburg
    "HECA": [30.1219, 31.4056],    # Cairo
}

def get_airport_coordinates(icao_code: str):
    """
    Get coordinates for an airport ICAO code.
    First checks local database, then falls back to estimation based on ICAO prefix.
    """
    icao_upper = icao_code.upper()
    
    # First check our comprehensive database
    if icao_upper in STATION_COORDS:
        return STATION_COORDS[icao_upper]
    
    # Fallback: Estimate based on ICAO code prefix (regional approximation)
    region_estimates = {
        'K': [39.0, -98.0],    # USA (center)
        'C': [56.0, -106.0],   # Canada
        'EG': [54.0, -2.0],    # UK
        'LF': [46.0, 2.0],     # France
        'ED': [51.0, 10.0],    # Germany
        'EH': [52.0, 5.0],     # Netherlands
        'LE': [40.0, -4.0],    # Spain
        'LI': [42.0, 12.0],    # Italy
        'LS': [47.0, 8.0],     # Switzerland
        'VI': [20.0, 77.0],    # India (North)
        'VO': [15.0, 78.0],    # India (South)
        'VE': [26.0, 91.0],    # India (East)
        'RJ': [36.0, 140.0],   # Japan
        'RK': [37.0, 127.0],   # South Korea
        'VH': [22.0, 114.0],   # Hong Kong
        'WS': [1.0, 104.0],    # Singapore
        'YS': [-34.0, 151.0],  # Australia (Sydney area)
        'YB': [-27.0, 153.0],  # Australia (Brisbane area)
        'OM': [25.0, 55.0],    # UAE
        'OT': [25.0, 51.0],    # Qatar
        'OE': [24.0, 47.0],    # Saudi Arabia
        'LT': [39.0, 35.0],    # Turkey
        'SB': [-23.0, -46.0],  # Brazil (São Paulo area)
        'SA': [-34.0, -64.0],  # Argentina
        'FA': [-26.0, 28.0],   # South Africa
        'HE': [30.0, 31.0],    # Egypt
    }
    
    # Try different prefix lengths
    for prefix_len in [2, 1]:
        prefix = icao_upper[:prefix_len]
        if prefix in region_estimates:
            return region_estimates[prefix]
    
    # Ultimate fallback: Return center of world map
    return [20.0, 0.0]

def parse_temp(t_str: str):
    try: return float(t_str.replace("C", ""))
    except: return np.nan

def parse_wind(w_str: str):
    try: return float(w_str.split(' at ')[1].split(' ')[0])
    except: return 0

def parse_visibility(v_str: str):
    try: return float(v_str.split(' miles')[0])
    except: return 10

def sigmet_affects_station(station_coord, sigmet):
    coords = sigmet.get("bbox")
    if not coords or not isinstance(coords, list) or len(coords) != 4: return False
    lat, lon = station_coord
    lat_min, lat_max, lon_min, lon_max = coords
    return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max

def analyze_station(metar: dict, sigmets: list) -> dict:
    wind = parse_wind(metar.get("wind", ""))
    vis = parse_visibility(metar.get("visibility", ""))
    
    # Handle both old string format and new structured weather format
    weather_list = metar.get("weather", [])
    weather = []
    for w in weather_list:
        if isinstance(w, dict):
            # Extract description from structured weather data
            desc = w.get('description', '').lower()
            if desc:
                weather.append(desc)
            # Also check phenomena codes
            for phenomenon in w.get('phenomena', []):
                code = phenomenon.get('code', '').lower()
                if code:
                    weather.append(code)
        elif isinstance(w, str):
            weather.append(w.lower())
    
    overall = "green"
    hazards = []
    
    # Check for severe weather conditions
    if wind >= 25 or vis < 3 or any("thunderstorm" in w or "tornado" in w or "ts" in w for w in weather):
        overall = "red"
        hazards.append("Severe weather conditions")
    elif wind >= 15 or vis < 5 or any("rain" in w or "snow" in w or "ra" in w or "sn" in w for w in weather):
        overall = "yellow"
        hazards.append("Significant weather conditions")
    
    # Check SIGMET impacts
    station_coord = None
    if "station" in metar:
        station_coord = get_airport_coordinates(metar["station"])
    
    if station_coord:
        for sigmet in sigmets:
            if sigmet_affects_station(station_coord, sigmet):
                overall = "red"
                hazards.append(f"SIGMET: {sigmet.get('hazard', 'Unknown hazard')}")
    
    return {
        "overall": overall,
        "wind_speed": wind, 
        "visibility": vis,
        "hazards": hazards,
        "weather_phenomena": weather
    }

def generate_summary_text(analysis: dict, metar: dict) -> str:
    """Generate human-readable weather summary"""
    station = metar.get("station", "Unknown")
    time = metar.get("time", "Unknown time")
    temp = metar.get("temperature", "Unknown")
    wind = metar.get("wind", "Unknown")
    vis = metar.get("visibility", "Unknown")
    weather = metar.get("weather", [])
    
    summary = f"Weather Report for {station} at {time}\n"
    summary += f"Temperature: {temp}\n"
    summary += f"Wind: {wind}\n" 
    summary += f"Visibility: {vis}\n"
    
    if weather:
        weather_text = format_weather_phenomena(weather)
        summary += f"Weather: {weather_text}\n"
    
    if analysis.get("hazards"):
        summary += f"\nHAZARDS: {'; '.join(analysis['hazards'])}\n"
        
    level = analysis.get("overall", "green")
    if level == "red":
        summary += "\n⚠️  SEVERE CONDITIONS - EXERCISE EXTREME CAUTION"
    elif level == "yellow":
        summary += "\n⚠️  SIGNIFICANT CONDITIONS - USE CAUTION"
    else:
        summary += "\n✅ CONDITIONS APPEAR FAVORABLE"
        
    return summary

# --- NEW: Weather formatting helper ---
def format_weather_phenomena(weather_list) -> str:
    """Helper function to format weather phenomena consistently"""
    if not weather_list:
        return "Clear conditions"
    
    weather_descriptions = []
    for weather_item in weather_list:
        if isinstance(weather_item, dict):
            # Use the description field from parsed weather
            desc = weather_item.get('description', '').strip()
            if not desc:
                # Fallback to raw if description is empty
                desc = weather_item.get('raw', '').strip()
            if not desc:
                # Last resort - try to build from phenomena
                phenomena = weather_item.get('phenomena', [])
                if phenomena:
                    intensity = weather_item.get('intensity', 'moderate')
                    phenom_names = [p.get('description', p.get('code', '')) for p in phenomena]
                    desc = f"{intensity.title()} {', '.join(phenom_names)}"
                else:
                    desc = "Unknown weather condition"
            weather_descriptions.append(desc)
        elif isinstance(weather_item, str) and weather_item.strip():
            weather_descriptions.append(weather_item.strip())
        else:
            # Skip empty or invalid entries
            continue
    
    return ", ".join(weather_descriptions) if weather_descriptions else "Clear conditions"

# --- NEW: Enhanced Summary Generation ---
def generate_summary_text(analysis: dict, metar: dict) -> str:
    """Generates a multi-line, human-readable weather summary."""
    overall = analysis.get('overall', 'Unknown')
    wind = metar.get('wind', 'N/A')
    visibility = metar.get('visibility', 'N/A')
    
    # Format weather phenomena using helper function
    weather_list = metar.get('weather', [])
    weather_phenomena = format_weather_phenomena(weather_list)

    summary_lines = [
        f"Overall condition is assessed as: {overall}.",
        f"Winds are currently {wind}.",
        f"Visibility is reported at {visibility}.",
        f"Current weather includes: {weather_phenomena}."
    ]
    if "Severe" in overall and analysis.get('hazards'):
        summary_lines.append(f"Active hazards: {', '.join(analysis['hazards'])}.")
    
    return "\n".join(summary_lines)

# --- UNCHANGED: Existing data endpoints ---
# (get_metar, get_pirep, etc. remain here, unchanged for brevity)
# IATA to ICAO conversion map for backend compatibility
IATA_TO_ICAO = {
    # United States - Major Airports
    'LAX': 'KLAX', 'JFK': 'KJFK', 'ORD': 'KORD', 'ATL': 'KATL',
    'SFO': 'KSFO', 'DEN': 'KDEN', 'LAS': 'KLAS', 'BOS': 'KBOS',
    'MIA': 'KMIA', 'SEA': 'KSEA', 'DFW': 'KDFW', 'CLT': 'KCLT',
    'LGA': 'KLGA', 'EWR': 'KEWR', 'PHX': 'KPHX', 'IAH': 'KIAH',
    'MSP': 'KMSP', 'DTW': 'KDTW', 'PHL': 'KPHL', 'BWI': 'KBWI',
    'SAN': 'KSAN', 'TPA': 'KTPA', 'PDX': 'KPDX', 'STL': 'KSTL',
    'HNL': 'PHNL', 'ANC': 'PANC', 'OAK': 'KOAK', 'MDW': 'KMDW',
    'BUR': 'KBUR', 'SJC': 'KSJC', 'SMF': 'KSMF', 'RDU': 'KRDU',
    'AUS': 'KAUS', 'BNA': 'KBNA', 'MCI': 'KMCI', 'CLE': 'KCLE',
    'PIT': 'KPIT', 'IND': 'KIND', 'CVG': 'KCVG', 'CMH': 'KCMH',
    'MKE': 'KMKE', 'BDL': 'KBDL', 'PVD': 'KPVD', 'ALB': 'KALB',
    
    # Canada
    'YYZ': 'CYYZ', 'YVR': 'CYVR', 'YUL': 'CYUL', 'YYC': 'CYYC',
    'YOW': 'CYOW', 'YWG': 'CYWG', 'YHZ': 'CYHZ', 'YEG': 'CYEG',
    'YQB': 'CYQB', 'YXE': 'CYXE', 'YQR': 'CYQR', 'YQX': 'CYQX',
    
    # India - Major Airports
    'DEL': 'VIDP', 'BOM': 'VABB', 'BLR': 'VOBL', 'MAA': 'VOMM',
    'CCU': 'VECC', 'HYD': 'VOHS', 'AMD': 'VOCI', 'COK': 'VOSR',
    'GOI': 'VOGO', 'PNQ': 'VAPO', 'JAI': 'VIJP', 'LKO': 'VILK',
    'IXC': 'VOCI', 'NAG': 'VANP', 'TRV': 'VOTV', 'CJB': 'VOCB',
    'IXB': 'VEBI', 'GAU': 'VEGT', 'IXA': 'VEAT', 'IXJ': 'VEJM',
    'IXR': 'VERC', 'PAT': 'VEPT', 'RPR': 'VARP', 'BHO': 'VABP',
    
    # United Kingdom & Ireland
    'LHR': 'EGLL', 'LGW': 'EGKK', 'STN': 'EGSS', 'LTN': 'EGGW',
    'MAN': 'EGCC', 'EDI': 'EGPH', 'GLA': 'EGPF', 'BHX': 'EGBB',
    'LPL': 'EGGP', 'NCL': 'EGNT', 'BRS': 'EGGD', 'CWL': 'EGFF',
    'BEL': 'EGAA', 'DUB': 'EIDW', 'ORK': 'EICK', 'SNN': 'EINN',
    
    # France
    'CDG': 'LFPG', 'ORY': 'LFPO', 'NCE': 'LFMN', 'LYS': 'LFLL',
    'MRS': 'LFML', 'TLS': 'LFBO', 'BOD': 'LFBD', 'NTE': 'LFRS',
    'MLH': 'LFSB', 'LIL': 'LFQQ', 'MPL': 'LFMT', 'BIQ': 'LFBZ',
    
    # Germany
    'FRA': 'EDDF', 'MUC': 'EDDM', 'DUS': 'EDDL', 'TXL': 'EDDT',
    'BER': 'EDDB', 'HAM': 'EDDH', 'CGN': 'EDDK', 'STR': 'EDDS',
    'HAJ': 'EDDV', 'NUE': 'EDDN', 'LEJ': 'EDDP', 'FDH': 'EDAH',
    
    # Netherlands & Belgium
    'AMS': 'EHAM', 'RTM': 'EHRD', 'EIN': 'EHEH', 'GRQ': 'EHGG',
    'BRU': 'EBBR', 'ANR': 'EBAW', 'CRL': 'EBCI', 'LGG': 'EBLG',
    
    # Spain & Portugal
    'MAD': 'LEMD', 'BCN': 'LEBL', 'PMI': 'LEPA', 'LPA': 'GCLP',
    'AGP': 'LEMG', 'BIO': 'LEBB', 'SVQ': 'LEZL', 'VLC': 'LEVC',
    'LIS': 'LPPT', 'OPO': 'LPPR', 'FAO': 'LPFR', 'FNC': 'LPMA',
    
    # Italy
    'FCO': 'LIRF', 'MXP': 'LIMC', 'LIN': 'LIML', 'BGY': 'LIME',
    'VCE': 'LIPZ', 'NAP': 'LIRN', 'CTA': 'LICC', 'BLQ': 'LIPE',
    'FLR': 'LIRQ', 'PSA': 'LIRP', 'BRI': 'LIBD', 'CAG': 'LIEE',
    
    # Switzerland & Austria
    'ZUR': 'LSZH', 'GVA': 'LSGG', 'BSL': 'LFSB', 'BRN': 'LSZB',
    'VIE': 'LOWV', 'SZG': 'LOWS', 'INN': 'LOWI', 'GRZ': 'LOWG',
    
    # Scandinavia
    'ARN': 'ESSA', 'GOT': 'ESGG', 'MMX': 'ESMS', 'CPH': 'EKCH',
    'AAL': 'EKYT', 'BLL': 'EKBI', 'OSL': 'ENGM', 'BGO': 'ENBR',
    'TRD': 'ENVA', 'SVG': 'ENZV', 'HEL': 'EFHK', 'TMP': 'EFTP',
    
    # Eastern Europe
    'SVO': 'UUEE', 'DME': 'UUDD', 'VKO': 'UUWW', 'LED': 'ULLI',
    'WAW': 'EPWA', 'KRK': 'EPKK', 'GDN': 'EPGD', 'WRO': 'EPWR',
    'PRG': 'LKPR', 'BUD': 'LHBP', 'OTP': 'LROP', 'SOF': 'LBSF',
    
    # Asia-Pacific - Japan
    'NRT': 'RJAA', 'HND': 'RJTT', 'KIX': 'RJBB', 'ITM': 'RJOO',
    'CTS': 'RJCC', 'FUK': 'RJFF', 'SDJ': 'RJSN', 'KMJ': 'RJOK',
    'OKA': 'ROAH', 'NGO': 'RJGG', 'HIJ': 'RJOA', 'TAK': 'RJFK',
    
    # South Korea
    'ICN': 'RKSI', 'GMP': 'RKSS', 'PUS': 'RKPK', 'CJU': 'RKPC',
    'TAE': 'RKTN', 'KWJ': 'RKJK', 'USN': 'RKPU', 'YNY': 'RKNY',
    
    # China
    'PEK': 'ZBAA', 'PKX': 'ZBAD', 'PVG': 'ZSPD', 'SHA': 'ZSSS',
    'CAN': 'ZGGG', 'SZX': 'ZGSZ', 'CTU': 'ZUUU', 'KMG': 'ZPPP',
    'XIY': 'ZLXY', 'CGO': 'ZHCC', 'WUH': 'ZHHH', 'CSX': 'ZSCX',
    'HGH': 'ZSHC', 'NKG': 'ZSNJ', 'TSN': 'ZBTJ', 'DLC': 'ZYTL',
    
    # Southeast Asia
    'HKG': 'VHHH', 'SIN': 'WSSS', 'KUL': 'WMKK', 'CGK': 'WIII',
    'BKK': 'VTBS', 'DMK': 'VTBD', 'MNL': 'RPLL', 'CEB': 'RPVM',
    'SGN': 'VVTS', 'HAN': 'VVNB', 'DAD': 'VVDN', 'RGN': 'VYYY',
    'PNH': 'VDPP', 'VTE': 'VLVT', 'BWN': 'WBSB', 'DPS': 'WADD',
    
    # Australia & New Zealand
    'SYD': 'YSSY', 'MEL': 'YMML', 'BNE': 'YBBN', 'PER': 'YPPH',
    'ADL': 'YPAD', 'DRW': 'YPDN', 'CNS': 'YBCS', 'HBA': 'YMHB',
    'CBR': 'YSCB', 'OOL': 'YBCG', 'AKL': 'NZAA', 'WLG': 'NZWN',
    'CHC': 'NZCH', 'ZQN': 'NZQN', 'DUD': 'NZDN', 'PMR': 'NZPM',
    
    # Middle East
    'DXB': 'OMDB', 'AUH': 'OMAA', 'DOH': 'OTHH', 'DWC': 'OMDW',
    'SHJ': 'OMSJ', 'RAS': 'OMRK', 'KWI': 'OKBK', 'RUH': 'OERK',
    'JED': 'OEJN', 'DMM': 'OEDF', 'MED': 'OEMA', 'TIF': 'OETF',
    'BAH': 'OBBI', 'MCT': 'OOMS', 'SLL': 'OOSA', 'TLV': 'LLBG',
    'VDA': 'LLOV', 'ETH': 'OIEL', 'AMM': 'OJAI', 'AQJ': 'OJAQ',
    'BEY': 'OLBA', 'DAM': 'OSDI', 'ALP': 'OSAP', 'BGW': 'ORBI',
    'BSR': 'ORMM', 'EBL': 'OREB', 'IKA': 'OIIE', 'THR': 'OIII',
    
    # Africa
    'CAI': 'HECA', 'SSH': 'HESH', 'HRG': 'HEGN', 'LXR': 'HELX',
    'CMN': 'GMMN', 'RAK': 'GMMX', 'FEZ': 'GMFF',
    'CPT': 'FACT', 'JNB': 'FAJS', 'DUR': 'FALE', 'PLZ': 'FAPE',
    'LOS': 'DNMM', 'ABV': 'DNAA', 'KAN': 'DNKN', 'PHC': 'DNPO',
    'ACC': 'DGAA', 'KMS': 'DGSI', 'ABJ': 'DIAP', 'NBO': 'HKJK',
    'MBA': 'HKMO', 'EBB': 'HUEN', 'KGL': 'HRYR', 'DAR': 'HTDA',
    'ZNZ': 'HTZA', 'ADD': 'HAAB', 'BJM': 'HADR', 'ASM': 'HEAS',
    
    # South America
    'GRU': 'SBGR', 'CGH': 'SBSP', 'SDU': 'SBRJ', 'GIG': 'SBGL',
    'BSB': 'SBBR', 'CNF': 'SBCF', 'FOR': 'SBFZ', 'REC': 'SBRF',
    'SSA': 'SBSV', 'CWB': 'SBCT', 'POA': 'SBPA', 'MAO': 'SBEG',
    'VCP': 'SBKP', 'EZE': 'SAEZ', 'AEP': 'SABE',
    'COR': 'SACO', 'MDZ': 'SAME', 'SCL': 'SCEL', 'BOG': 'SKBO',
    'MDE': 'SKRG', 'CTG': 'SKCG', 'CLO': 'SKCL', 'LIM': 'SPJC',
    'CUZ': 'SPZO', 'AQP': 'SPQU', 'UIO': 'SEQM', 'GYE': 'SEGU',
    'CCS': 'SVMI', 'MAR': 'SVMC', 'VLN': 'SVVL', 'GEO': 'SYCJ'
}

def validate_airport_code(code: str) -> str:
    """Validate and convert airport code (accepts both IATA and ICAO)"""
    if not code:
        raise HTTPException(status_code=400, detail="Airport code cannot be empty")
    
    code = code.strip().upper()
    
    # Check if code contains only letters
    if not code.isalpha():
        raise HTTPException(status_code=400, detail="Airport code must contain only letters")
    
    # Handle IATA codes (3 letters) - convert to ICAO
    if len(code) == 3:
        if code in IATA_TO_ICAO:
            icao_code = IATA_TO_ICAO[code]
            print(f"🔄 Converted IATA {code} to ICAO {icao_code}")
            return icao_code
        else:
            raise HTTPException(status_code=400, detail=f"Unknown IATA code: {code}. Please use a supported airport.")
    
    # Handle ICAO codes (4 letters)
    elif len(code) == 4:
        return code
    
    # Invalid length
    else:
        raise HTTPException(status_code=400, detail="Airport code must be 3 letters (IATA) or 4 letters (ICAO)")

# Keep old function for backward compatibility
def validate_icao_code(icao: str) -> str:
    """Legacy function - use validate_airport_code instead"""
    return validate_airport_code(icao)

@app.get("/metar/decoded/{icao}")
def get_metar_decoded(icao: str) -> Dict[str, Any]:
    # Validate airport code (accepts IATA or ICAO)
    icao = validate_airport_code(icao)
    
    try:
        url = f"https://tgftp.nws.noaa.gov/data/observations/metar/stations/{icao}.TXT"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"No METAR data available for airport {icao}")
        
        response.raise_for_status()
        lines = response.text.strip().split("\n")
        
        if len(lines) < 2:
            raise HTTPException(status_code=404, detail=f"No METAR report available for {icao}")
        
        raw_metar = lines[1]
        obs = Metar.Metar(raw_metar)
        
        # Use custom METAR parser for weather phenomena
        try:
            custom_parser = MetarParser()
            parsed_data = custom_parser.parse_metar(raw_metar)
        except Exception as parser_error:
            print(f"Warning: Custom METAR parser failed: {parser_error}")
            # Fallback to basic parsing if custom parser fails
            parsed_data = {'weather': []}
        
        return {
            "station_id": obs.station_id, 
            "time": str(obs.time), 
            "temperature": str(obs.temp), 
            "dew_point": str(obs.dewpt), 
            "wind": str(obs.wind()), 
            "visibility": str(obs.vis), 
            "pressure": str(obs.press), 
            "weather": parsed_data.get('weather', []),  # Use our structured weather data
            "sky": [str(layer) for layer in obs.sky], 
            "raw": raw_metar
        }
        
    except HTTPException:
        raise
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Weather service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Unable to parse METAR data for {icao}: {str(e)}")

@app.get("/metar/analyzed/{icao}")
def get_metar_analyzed(icao: str) -> Dict[str, Any]:
    # Validation is handled in get_metar_decoded
    decoded_metar = get_metar_decoded(icao)
    
    try:
        sigmets = requests.get(f"{SIGMET_URL}", timeout=10).json()
    except Exception:
        sigmets = []
    
    analysis = analyze_station(decoded_metar, sigmets)
    return {"analysis": analysis, "decoded_metar": decoded_metar}

# --- ✅ UPDATED AND ENHANCED: Route Weather Endpoint ---
@app.get("/route-weather/{departure_icao}/{arrival_icao}")
def get_route_weather(departure_icao: str, arrival_icao: str):
    """
    Provides a full weather briefing for a flight route, including detailed summaries and coordinates.
    """
    try:
        print(f"🛫 Route weather request: {departure_icao} → {arrival_icao}")
        
        # Validate both airport codes (accepts IATA or ICAO)
        print(f"🔍 Validating airport codes...")
        dep_icao = validate_airport_code(departure_icao)
        arr_icao = validate_airport_code(arrival_icao)
        print(f"✅ Validated: {departure_icao} → {dep_icao}, {arrival_icao} → {arr_icao}")
        
        print(f"📊 Getting departure weather for {dep_icao}...")
        departure_weather = get_metar_analyzed(dep_icao)
        print(f"📊 Getting arrival weather for {arr_icao}...")
        arrival_weather = get_metar_analyzed(arr_icao)

        dep_summary = generate_summary_text(departure_weather['analysis'], departure_weather['decoded_metar'])
        arr_summary = generate_summary_text(arrival_weather['analysis'], arrival_weather['decoded_metar'])

        return {
            "departure": {
                "icao": dep_icao,
                "coords": get_airport_coordinates(dep_icao),
                "summary_text": dep_summary,
                "analysis": departure_weather['analysis'],
                "decoded_metar": departure_weather['decoded_metar']
            },
            "arrival": {
                "icao": arr_icao,
                "coords": get_airport_coordinates(arr_icao),
                "summary_text": arr_summary,
                "analysis": arrival_weather['analysis'],
                "decoded_metar": arrival_weather['decoded_metar']
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Route weather error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Route weather error: {str(e)}")

@app.get("/route-weather")
def get_route_weather_query(departure: str, arrival: str):
    """
    Route weather endpoint with query parameters (for testing compatibility)
    """
    # Validation happens in get_route_weather
    return get_route_weather(departure, arrival)

# Initialize SIGMET parser
sigmet_parser = SigmetParser()

@app.get("/sigmet/current")
async def get_current_sigmets():
    """
    Get current SIGMET data
    """
    try:
        sigmets = sigmet_parser.get_current_sigmets()
        return {
            "status": "success",
            "count": len(sigmets),
            "sigmets": sigmets,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch SIGMET data: {str(e)}")

@app.get("/sigmet/analysis")
async def get_sigmet_analysis():
    """
    Get analyzed SIGMET data for flight planning
    """
    try:
        sigmets = sigmet_parser.get_current_sigmets()
        analysis = sigmet_parser.analyze_sigmets_for_flight(sigmets)
        return {
            "status": "success",
            "analysis": analysis,
            "raw_sigmets": sigmets,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze SIGMET data: {str(e)}")

@app.get("/sigmet/raw")
async def get_raw_sigmets():
    """
    Get raw SIGMET text data
    """
    try:
        response = requests.get(SIGMET_URL, timeout=10)
        if response.status_code == 200:
            return {
                "status": "success", 
                "raw_data": response.text,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch SIGMET data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching SIGMET data: {str(e)}")

