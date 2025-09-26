import React, { useState } from 'react';
import './App.css';
import AirportSearchInput from './AirportSearchInput';
import FlightChatbot from './FlightChatbot';
import GoogleFlightMap from './GoogleFlightMap';

const WeatherBar = ({ level }) => {
  const getColor = () => {
    switch(level) {
      case 'good': return '#28a745';
      case 'caution': return '#ffc107';
      case 'poor': return '#dc3545';
      default: return '#6c757d';
    }
  };

  return (
    <div className="weather-bar" style={{ backgroundColor: getColor() }} />
  );
};

const Metric = ({ label, value }) => (
  <div className="metric">
    <div className="metric-label">{label}</div>
    <div className="metric-value">{value || 'N/A'}</div>
  </div>
);

function App() {
  const [departureIcao, setDepartureIcao] = useState('');
  const [arrivalIcao, setArrivalIcao] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [chatbotOpen, setChatbotOpen] = useState(false);

  const parseMetar = (metarText) => {
    if (!metarText) return null;
    
    const windMatch = metarText.match(/(\d{3})(\d{2,3})(G\d{2,3})?KT/);
    const visMatch = metarText.match(/(\d+|\d+\/\d+)SM/);
    const tempMatch = metarText.match(/M?(\d{2})\/M?(\d{2})/);
    const pressureMatch = metarText.match(/A(\d{4})/);
    
    return {
      wind: windMatch ? `${windMatch[1]}°/${windMatch[2]}kt${windMatch[3] || ''}` : null,
      visibility: visMatch ? `${visMatch[1]}SM` : null,
      temperature: tempMatch ? `${tempMatch[1]}°C` : null,
      pressure: pressureMatch ? `${pressureMatch[1].slice(0,2)}.${pressureMatch[1].slice(2)}` : null
    };
  };

  const fetchData = async () => {
    if (!departureIcao || !arrivalIcao) {
      setError('Please enter both departure and arrival airports');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`http://localhost:8000/weather/${departureIcao}/${arrivalIcao}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(`Error fetching data: ${err.message}`);
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const depMetar = data?.departure?.raw_data?.metar ? parseMetar(data.departure.raw_data.metar) : null;
  const arrMetar = data?.arrival?.raw_data?.metar ? parseMetar(data.arrival.raw_data.metar) : null;



  return (
    <div className="app">
      <header className="app-header">
        <h1>Aerolytics - Flight Dashboard</h1>
      </header>

      <div className="main-content">
        <div className="weather-panel">
          <div className="search-section">
            <AirportSearchInput
              value={departureIcao}
              onChange={setDepartureIcao}
              placeholder="Departure airport..."
              label="From"
            />
            <AirportSearchInput
              value={arrivalIcao}
              onChange={setArrivalIcao}
              placeholder="Arrival airport..."
              label="To"
            />
            <button 
              onClick={fetchData} 
              disabled={loading}
              className="search-button"
            >
              {loading ? "Loading..." : "Get Report"}
            </button>
          </div>

          {error && <div className="error">{error}</div>}
          
          {loading && <div className="loading">Loading weather data...</div>}

          {data && !loading && (
            <div className="weather-results">
              <div className="weather-card">
                <h3>Departure: {data.departure.icao}</h3>
                <div className="weather-content">
                  {data.departure.summary_text}
                </div>
                <WeatherBar level={data.departure.analysis.overall} />
                <div className="metrics">
                  <Metric label="Wind" value={depMetar?.wind} />
                  <Metric label="Visibility" value={depMetar?.visibility} />
                  <Metric label="Temperature" value={depMetar?.temperature} />
                  <Metric label="Pressure" value={depMetar?.pressure} />
                </div>
              </div>

              <div className="weather-card">
                <h3>Arrival: {data.arrival.icao}</h3>
                <div className="weather-content">
                  {data.arrival.summary_text}
                </div>
                <WeatherBar level={data.arrival.analysis.overall} />
                <div className="metrics">
                  <Metric label="Wind" value={arrMetar?.wind} />
                  <Metric label="Visibility" value={arrMetar?.visibility} />
                  <Metric label="Temperature" value={arrMetar?.temperature} />
                  <Metric label="Pressure" value={arrMetar?.pressure} />
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="map-section">
          <GoogleFlightMap
            departure={departureIcao}
            arrival={arrivalIcao}
            weatherData={data}
          />
        </div>
      </div>

      <button 
        className="chatbot-toggle"
        onClick={() => setChatbotOpen(!chatbotOpen)}
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
        </svg>
      </button>

      {chatbotOpen && (
        <div className="chatbot-panel">
          <div className="chatbot-header">
            <span>Flight Assistant</span>
            <button onClick={() => setChatbotOpen(false)}>
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </button>
          </div>
          <FlightChatbot />
        </div>
      )}
    </div>
  );
}

export default App;