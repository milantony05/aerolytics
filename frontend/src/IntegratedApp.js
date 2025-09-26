import React, { useState } from "react";
import axios from "axios";
import { MapContainer, TileLayer, Marker, Polyline, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import AirportSearchInput from './AirportSearchInput';
import FlightChatbot from './FlightChatbot';
import GoogleFlightMap from './GoogleFlightMap';
import './IntegratedApp.css';

// Custom departure airport icon (green airplane)
const departureIcon = new L.DivIcon({
  html: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#4caf50" width="32px" height="32px" style="filter: drop-shadow(0 0 3px black);">
    <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
  </svg>`,
  className: 'custom-div-icon',
  iconSize: [32, 32],
  iconAnchor: [16, 16]
});

// Custom arrival airport icon (blue airplane)
const arrivalIcon = new L.DivIcon({
  html: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#2196f3" width="32px" height="32px" style="filter: drop-shadow(0 0 3px black);">
    <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
  </svg>`,
  className: 'custom-div-icon',
  iconSize: [32, 32],
  iconAnchor: [16, 16]
});

const IntegratedApp = () => {
  const [departureIcao, setDepartureIcao] = useState("");
  const [arrivalIcao, setArrivalIcao] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeView, setActiveView] = useState('weather'); // 'weather', 'chatbot', 'both'
  const mapRef = React.useRef();

  const fetchData = async () => {
    if (!departureIcao.trim() || !arrivalIcao.trim()) {
      setError("Please enter both departure and arrival airports");
      return;
    }

    setLoading(true);
    setError("");
    
    try {
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000'}/route-weather`, {
        params: {
          departure: departureIcao.trim().toUpperCase(),
          arrival: arrivalIcao.trim().toUpperCase()
        }
      });
      setData(response.data);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || "Failed to fetch weather data";
      setError(errorMsg);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleChatbotRouteSelect = (departure, arrival) => {
    setDepartureIcao(departure);
    setArrivalIcao(arrival);
    // Auto-fetch weather data when chatbot suggests a route
    setTimeout(() => {
      fetchData();
    }, 500);
  };

  const WeatherMap = ({ departure, arrival }) => {
    if (!departure || !arrival) {
      return (
        <div style={{ 
          height: '100%', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          textAlign: 'center',
          padding: '40px'
        }}>
          <div>
            <h3>🌍 Flight Route Visualization</h3>
            <p>Enter departure and arrival airports to view weather conditions and flight path</p>
          </div>
        </div>
      );
    }

    // Use Google Maps for enhanced visualization
    return (
      <GoogleFlightMap 
        departure={departure.icao} 
        arrival={arrival.icao}
      />
    );
  };

  const LoadingSpinner = () => (
    <div style={{ textAlign: 'center', padding: '20px' }}>
      <div style={{ 
        width: '40px', 
        height: '40px', 
        border: '4px solid #f3f3f3', 
        borderTop: '4px solid #3498db', 
        borderRadius: '50%', 
        animation: 'spin 1s linear infinite',
        margin: '0 auto'
      }}></div>
      <p style={{ marginTop: '10px', color: '#7f8c8d' }}>Analyzing weather conditions...</p>
    </div>
  );

  const WeatherBar = ({ level }) => {
    const colors = { green: '#27ae60', yellow: '#f39c12', red: '#e74c3c' };
    const labels = { green: 'Good Conditions', yellow: 'Caution Advised', red: 'Severe Weather' };
    
    return (
      <div style={{
        background: colors[level] || '#95a5a6',
        color: 'white',
        padding: '8px 12px',
        borderRadius: '6px',
        textAlign: 'center',
        fontWeight: 'bold',
        fontSize: '14px',
        margin: '10px 0'
      }}>
        {labels[level] || 'Unknown'}
      </div>
    );
  };

  const Metric = ({ label, value }) => (
    <div style={{
      backgroundColor: '#34495e',
      padding: '8px',
      borderRadius: '4px',
      textAlign: 'center'
    }}>
      <div style={{ fontSize: '12px', color: '#bdc3c7', marginBottom: '4px' }}>{label}</div>
      <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#ecf0f1' }}>
        {value || 'N/A'}
      </div>
    </div>
  );

  const styles = {
    app: {
      display: 'flex',
      height: '100vh',
      width: '100vw',
      backgroundColor: '#1a1a1a',
      color: '#f0f0f0',
      fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
    },
    leftPanel: {
      width: activeView === 'both' ? '400px' : '450px',
      height: '100vh',
      padding: '20px',
      backgroundColor: '#242424',
      overflowY: 'auto',
      borderRight: '1px solid #333',
      transition: 'width 0.3s ease'
    },
    rightPanel: {
      flex: 1,
      height: '100vh',
      display: 'flex',
      flexDirection: 'column'
    },
    mapPanel: {
      flex: activeView === 'both' ? 1 : 1,
      transition: 'flex 0.3s ease'
    },
    chatPanel: {
      height: activeView === 'both' ? '50%' : '100%',
      borderTop: activeView === 'both' ? '1px solid #333' : 'none',
      transition: 'height 0.3s ease'
    },
    viewToggle: {
      display: 'flex',
      gap: '8px',
      marginBottom: '20px',
      padding: '4px',
      backgroundColor: '#333',
      borderRadius: '8px'
    },
    toggleButton: {
      flex: 1,
      padding: '8px 12px',
      border: 'none',
      borderRadius: '6px',
      fontSize: '12px',
      fontWeight: '600',
      cursor: 'pointer',
      transition: 'all 0.2s ease'
    },
    card: {
      backgroundColor: '#2c2c2c',
      padding: '15px',
      borderRadius: '8px',
      marginBottom: '20px'
    },
    metricGrid: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: '10px',
      marginTop: '15px'
    }
  };

  const getToggleButtonStyle = (view) => ({
    ...styles.toggleButton,
    backgroundColor: activeView === view ? '#3498db' : 'transparent',
    color: activeView === view ? 'white' : '#bdc3c7'
  });

  const depMetar = data?.departure?.decoded_metar;
  const arrMetar = data?.arrival?.decoded_metar;

  return (
    <div style={styles.app}>
      <div style={styles.leftPanel}>
        <h2 style={{ textAlign: 'center', margin: '0 0 20px 0', fontSize: '24px', fontWeight: 'bold' }}>
          ✈️ Aerolytics Flight Assistant
        </h2>

        <div style={styles.viewToggle}>
          <button 
            style={getToggleButtonStyle('weather')}
            onClick={() => setActiveView('weather')}
          >
            Weather Only
          </button>
          <button 
            style={getToggleButtonStyle('chatbot')}
            onClick={() => setActiveView('chatbot')}
          >
            Chatbot Only
          </button>
          <button 
            style={getToggleButtonStyle('both')}
            onClick={() => setActiveView('both')}
          >
            Both Views
          </button>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <AirportSearchInput
            value={departureIcao}
            onChange={setDepartureIcao}
            placeholder="Search departure airport by name, city, or ICAO code..."
            label="Departure Airport"
          />
          <AirportSearchInput
            value={arrivalIcao}
            onChange={setArrivalIcao}
            placeholder="Search arrival airport by name, city, or ICAO code..."
            label="Arrival Airport"
          />
        </div>

        <button 
          onClick={fetchData} 
          disabled={loading}
          style={{
            width: '100%',
            padding: '12px',
            fontSize: '18px',
            fontWeight: 'bold',
            backgroundColor: '#005f73',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            marginBottom: '20px'
          }}
        >
          {loading ? "Loading..." : "Get Weather Briefing"}
        </button>

        {error && <p style={{ color: "#f44336", textAlign: 'center', marginBottom: '20px' }}>{error}</p>}
        
        {loading && <LoadingSpinner />}

        {data && !loading && (
          <div>
            <div style={styles.card}>
              <h3>Departure: {data.departure.icao}</h3>
              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '14px', lineHeight: '1.5' }}>
                {data.departure.summary_text}
              </pre>
              <WeatherBar level={data.departure.analysis.overall} />
              <div style={styles.metricGrid}>
                <Metric label="Wind" value={depMetar?.wind} />
                <Metric label="Visibility" value={depMetar?.visibility} />
                <Metric label="Temperature" value={depMetar?.temperature} />
                <Metric label="Pressure" value={depMetar?.pressure} />
              </div>
            </div>

            <div style={styles.card}>
              <h3>Arrival: {data.arrival.icao}</h3>
              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '14px', lineHeight: '1.5' }}>
                {data.arrival.summary_text}
              </pre>
              <WeatherBar level={data.arrival.analysis.overall} />
              <div style={styles.metricGrid}>
                <Metric label="Wind" value={arrMetar?.wind} />
                <Metric label="Visibility" value={arrMetar?.visibility} />
                <Metric label="Temperature" value={arrMetar?.temperature} />
                <Metric label="Pressure" value={arrMetar?.pressure} />
              </div>
            </div>
          </div>
        )}
      </div>

      <div style={styles.rightPanel}>
        {(activeView === 'weather' || activeView === 'both') && (
          <div style={styles.mapPanel}>
            <WeatherMap departure={data?.departure} arrival={data?.arrival} />
          </div>
        )}
        
        {(activeView === 'chatbot' || activeView === 'both') && (
          <div style={styles.chatPanel}>
            <FlightChatbot onRouteSelect={handleChatbotRouteSelect} />
          </div>
        )}
      </div>
    </div>
  );
};

export default IntegratedApp;