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

### Backend (Flask)
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
python app.py
```

### Frontend (React)
```bash
cd frontend
npm install
npm start
```

## Development Phases

This project follows a 12-phase development roadmap focusing on:
1. Core weather data fetching and parsing
2. Integration of pilot reports and NOTAMs
3. Advanced visualization and risk assessment

## API Endpoints

- `GET /api/metar/{airport}` - Fetch METAR data for an airport
- More endpoints to be added in subsequent phases

## Technology Stack

- **Backend:** Python Flask
- **Frontend:** React
- **Data Source:** AviationWeather.gov API