# Aerolytics: The Weather Copilot

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2+-61dafb.svg)](https://reactjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive aviation weather intelligence platform that simplifies flight planning by transforming complex meteorological data into actionable insights for pilots. Aerolytics aggregates, analyzes, and presents real-time weather information from multiple aviation sources with AI-powered assistance.

## 🌟 Features

### 🔄 **Real-Time Weather Data**
- **METAR Reports** - Current weather observations with intelligent parsing
- **TAF Forecasts** - Terminal aerodrome forecasts up to 30 hours
- **SIGMET Alerts** - Significant meteorological information and warnings
- **PIREP Integration** - Pilot reports for real-world conditions
- **Multi-Airport Support** - Both ICAO (KLAX) and IATA (LAX) codes

### 🎯 **Intelligent Analysis**
- **Weather Categorization** - Green/Yellow/Red risk assessment system  
- **Route Weather Briefing** - Complete departure to arrival analysis
- **Hazard Detection** - Automatic identification of severe weather conditions
- **Coordinate Mapping** - Global airport coordinate database with 50+ major airports

### 🤖 **AI-Powered Assistant**
- **Gemini Chat Integration** - Natural language weather queries
- **Context-Aware Responses** - Weather-specific AI assistance
- **Conversation Memory** - Maintains chat history for better context

### 🌍 **Interactive Visualization**
- **Flight Map Interface** - Visual route planning with weather overlays
- **Airport Search** - Intelligent airport code lookup
- **Responsive Design** - Works on desktop and mobile devices

## 📸 Gallery

<img width="1919" height="945" alt="1" src="https://github.com/user-attachments/assets/95ffe88f-b870-41d8-9f15-e12eee8eae65" />

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/milantony05/aerolytics.git
cd aerolytics

# 2. Configure environment
copy .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 3. Run with Docker (recommended)
docker-compose up -d

# 4. Access: http://localhost:3000
```

**Manual setup (without Docker):**
```bash
# Backend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
cd backend && uvicorn main:app --reload

# Frontend (new terminal)
cd frontend && npm install && npm start
```

**Common commands:** `docker-compose up -d` | `docker-compose down` | `docker-compose logs -f`

## 📁 Project Structure

```
aerolytics/
├── backend/           # FastAPI backend (Python)
│   ├── Dockerfile
│   ├── main.py       # API endpoints
│   ├── gemini_chat.py # AI chat integration
│   └── *_parser.py   # Weather data parsers
├── frontend/         # React frontend
│   ├── Dockerfile & Dockerfile.dev
│   ├── nginx.conf
│   ├── src/
│   │   ├── App.js         # Main component
│   │   ├── Map.js         # Flight route map
│   │   ├── Chatbot.js     # AI assistant
│   │   ├── SearchInput.js # Airport search
│   │   └── airportDatabase.js # Airport data
│   └── public/       # Static assets
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🔗 API Endpoints

**Core Weather:** `/metar/decoded/{icao}` • `/metar/analyzed/{icao}` • `/route-weather/{departure}/{arrival}`  
**SIGMET Alerts:** `/sigmet/current` • `/sigmet/analysis` • `/sigmet/raw`  
**AI Chat:** `POST /api/gemini/chat` • `GET /api/gemini/health`  
**Docs:** http://localhost:8000/docs

## 🛠️ Technology Stack

**Backend:** FastAPI • Python-METAR • Google Gemini AI • NumPy  
**Frontend:** React 18.2 • Axios • Leaflet (OpenStreetMap)  
**Data Sources:** AviationWeather.gov • NOAA • Google Gemini AI  
**Deployment:** Docker • Nginx • Uvicorn

## 🔧 Configuration

Create a `.env` file (copy from `.env.example`) and add:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

**Ports:** Frontend (3000) • Backend (8000) • API Docs (8000/docs)

## 📊 Weather Analysis System

Aerolytics uses a sophisticated 3-tier risk assessment:

- 🟢 **GREEN** - Favorable conditions
  - Wind < 15 knots
  - Visibility > 5 miles
  - No significant weather

- 🟡 **YELLOW** - Caution advised  
  - Wind 15-25 knots
  - Visibility 3-5 miles
  - Light precipitation

- 🔴 **RED** - Severe conditions
  - Wind > 25 knots
  - Visibility < 3 miles
  - Thunderstorms, severe weather

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push and open a Pull Request

Follow PEP 8 (Python) and ESLint (JavaScript) conventions.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Milan Tony**
- GitHub: [@milantony05](https://github.com/milantony05)
- Repository: [aerolytics](https://github.com/milantony05/aerolytics)

## 🙏 Acknowledgments

- **FAA Aviation Weather Center** for providing comprehensive weather data
- **AviationWeather.gov** for real-time METAR, TAF, and SIGMET data
- **Google AI** for Gemini integration
- **FastAPI community** for excellent documentation and support
- **React community** for modern frontend capabilities

---

**✈️ Safe Flying with Aerolytics!** 

*Making aviation weather data accessible, intelligent, and actionable for pilots worldwide.*
