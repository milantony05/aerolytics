# Aerolytics: The Pilot's Weather Co-Pilot

A web application that simplifies aviation weather briefings by fetching, parsing, and categorizing METAR, TAF, and NOTAM data for pilots.

## Project Structure

```
hackspace/
├── backend/          # Flask API server
├── frontend/         # React web application
├── sky-stream.md     # Project documentation
└── README.md         # This file
```

## Quick Start

### Option 1: Use the provided batch files (Windows)
1. **Start Backend:** Double-click `start-backend.bat` or run it from command line
2. **Start Frontend:** Double-click `start-frontend.bat` or run it from command line

### Option 2: Manual setup

#### Backend (Flask)
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
python app.py
```

#### Frontend (React)
```bash
cd frontend
npm start  # npm install already done during create-react-app
```

### Testing the Application
1. Start both backend (port 5000) and frontend (port 3000)
2. Open http://localhost:3000 in your browser
3. Enter an airport code (e.g., KJFK, KLAX, KORD) and click "Get METAR"
4. The raw METAR data should be displayed

## Development Phases

This project follows a 12-phase development roadmap focusing on:
1. Core weather data fetching and parsing
2. Integration of pilot reports and NOTAMs
3. Advanced visualization and risk assessment

## API Endpoints

- `GET /api/metar/{airport}` - Fetch and parse METAR data for an airport
  - Returns both raw METAR string and structured parsed data
  - Includes wind, visibility, weather, clouds, temperature, and pressure
- More endpoints to be added in subsequent phases

## Current Features (Phase 2)

- ✅ **Raw METAR Fetching** - Get real-time weather data from AviationWeather.gov
- ✅ **METAR Parsing** - Decode aviation weather codes into human-readable format
- ✅ **Structured Data** - JSON response with clearly named fields
- ✅ **Weather Translation** - Convert aviation codes to plain English descriptions
- ✅ **Multiple Units** - Temperature in Celsius/Fahrenheit, pressure in inHg/millibars
- ✅ **Error Handling** - Graceful handling of parsing errors and invalid data

### Supported METAR Elements:
- Station identifier and observation time
- Wind direction, speed, and gusts
- Visibility in statute miles or meters  
- Weather phenomena (rain, snow, fog, etc.)
- Cloud layers with heights and coverage
- Temperature and dewpoint
- Barometric pressure
- Remarks section

## Technology Stack

- **Backend:** Python Flask
- **Frontend:** React
- **Data Source:** AviationWeather.gov API