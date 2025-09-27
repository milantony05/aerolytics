# 🛩️ Aerolytics: The Pilot's Weather Co-Pilot

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


## Gallery

<img width="1919" height="945" alt="1" src="https://github.com/user-attachments/assets/5fe89802-832d-4d94-a0af-d23633a738c8" />

<img width="1919" height="945" alt="2" src="https://github.com/user-attachments/assets/9c420b73-3cb1-4599-a401-a611dca60e2d" />

<img width="421" height="326" alt="3" src="https://github.com/user-attachments/assets/053366f7-a3bf-4938-8617-5a2ab5938949" />

<img width="434" height="374" alt="4" src="https://github.com/user-attachments/assets/1b07661e-39a2-47ab-9284-a734ad3b696b" />

<img width="451" height="174" alt="5" src="https://github.com/user-attachments/assets/5ef3d744-905c-4938-a08c-8cab2071c3b2" />

<img width="282" height="383" alt="6" src="https://github.com/user-attachments/assets/e67b1334-6387-433d-aa1f-4dde29d5dd0e" />

## 🚀 Quick Start

### Prerequisites
- **Python 3.13+** (recommended)
- **Node.js 16+** and npm
- **Git** for version control

### Installation

#### Option 1: Quick Start (Windows)
```bash
# Clone the repository
git clone https://github.com/milantony05/aerolytics.git
cd aerolytics

# Start backend server
start-backend.bat

# In a new terminal, start frontend
start-frontend.bat
```

#### Option 2: Manual Setup

**Backend Setup:**
```bash
cd aerolytics

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Frontend Setup:**
```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Start React development server
npm start
```

### Access the Application
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs (Swagger UI)

## 📁 Project Structure

```
aerolytics/
├── 📂 backend/                 # FastAPI Backend Server
│   ├── main.py                # Main API server with all endpoints
│   ├── gemini_chat.py         # AI chat integration
│   ├── metar_parser.py        # METAR data parsing
│   ├── sigmet_parser.py       # SIGMET data parsing  
│   ├── taf_parser.py          # TAF forecast parsing
│   ├── pirep_parser.py        # PIREP data parsing
│   └── weather_classifier.py  # Weather risk classification
├── 📂 frontend/               # React Frontend Application
│   ├── public/               # Static assets
│   └── src/                  # React components and logic
│       ├── App.js           # Main application component
│       ├── FlightChatbot.js # AI chat interface
│       ├── GoogleFlightMap.js # Interactive map
│       └── AirportSearchInput.js # Airport search
├── 📄 test_api.py            # Comprehensive API testing suite
├── 📄 requirements.txt       # Python dependencies
├── 📄 start-backend.bat      # Windows backend launcher
├── 📄 start-frontend.bat     # Windows frontend launcher
└── 📄 README.md             # This documentation
```

## 🔗 API Endpoints

### Core Weather Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check and API information |
| `GET` | `/metar/decoded/{icao}` | Get parsed METAR data for airport |
| `GET` | `/metar/analyzed/{icao}` | Get METAR with risk analysis |
| `GET` | `/route-weather/{departure}/{arrival}` | Complete route weather briefing |

### SIGMET Endpoints  
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/sigmet/current` | Current SIGMET alerts |
| `GET` | `/sigmet/analysis` | Analyzed SIGMET data for flight planning |
| `GET` | `/sigmet/raw` | Raw SIGMET text data |

### AI Chat Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/gemini/chat` | Chat with AI weather assistant |
| `GET` | `/api/gemini/health` | AI service health check |

### Example API Usage

**Get Current Weather:**
```bash
curl http://localhost:8000/metar/decoded/KLAX
```

**Get Route Weather:**
```bash
curl http://localhost:8000/route-weather/KLAX/KJFK
```

**Chat with AI Assistant:**
```bash
curl -X POST http://localhost:8000/api/gemini/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What's the weather like at LAX?"}'
```

## 🧪 Testing

The project includes comprehensive test coverage for all API endpoints:

```bash
# Run smoke tests (quick validation)
python test_api.py

# Run full test suite
python -m pytest test_api.py -v

# Run specific test categories
python -m pytest test_api.py::TestAerolyticsAPI::test_metar_decoded_valid_icao -v
```

### Test Coverage
- ✅ All API endpoints (success and error cases)
- ✅ ICAO and IATA airport code validation
- ✅ Weather data parsing and analysis
- ✅ AI chat functionality
- ✅ Error handling and response validation
- ✅ CORS and content-type verification

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework for APIs
- **Uvicorn** - ASGI server for FastAPI
- **Python-METAR** - Aviation weather parsing library
- **Google Generative AI** - AI chat capabilities
- **NumPy** - Numerical computing for weather analysis
- **Requests/HTTPX** - HTTP clients for external APIs

### Frontend  
- **React 18.2+** - Modern UI library
- **Axios** - HTTP client for API calls
- **Google Maps API** - Interactive mapping
- **CSS3** - Responsive styling

### Data Sources
- **AviationWeather.gov** - Official FAA weather data
- **NOAA Aviation Weather** - METAR observations
- **Google Gemini AI** - Natural language processing

## 🌐 Supported Airports

The system includes a comprehensive database of major airports worldwide:

**United States:** LAX, JFK, ORD, ATL, SFO, DEN, LAS, BOS, MIA, SEA  
**India:** DEL, BOM, BLR, MAA, CCU, HYD, AMD  
**Europe:** LHR, CDG, FRA, AMS, MAD, FCO  
**Asia-Pacific:** NRT, ICN, HKG, SIN, SYD  
**Middle East:** DXB, DOH, RUH  
**And many more...**

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:
```env
GEMINI_API_KEY=your_google_ai_api_key_here
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### API Configuration
- **Backend Port:** 8000 (configurable in `start-backend.bat`)
- **Frontend Port:** 3000 (default React development server)
- **CORS:** Configured for local development

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

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/amazing-feature`
3. **Commit changes:** `git commit -m 'Add amazing feature'`
4. **Push to branch:** `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint configuration for JavaScript
- Write tests for new features
- Update documentation as needed

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

## 📞 Support

If you encounter any issues or have questions:

1. **Check the documentation** in this README
2. **Review API docs** at http://localhost:8000/docs
3. **Run tests** to verify installation: `python test_api.py`
4. **Open an issue** on GitHub for bugs or feature requests

---

**✈️ Safe Flying with Aerolytics!** 

*Making aviation weather data accessible, intelligent, and actionable for pilots worldwide.*
