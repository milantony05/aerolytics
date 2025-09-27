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
  const [modalData, setModalData] = useState(null);
  const [modalType, setModalType] = useState('');
  const [flightSummary, setFlightSummary] = useState('');
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [panelCollapsed, setPanelCollapsed] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);



  const fetchData = async () => {
    if (!departureIcao || !arrivalIcao) {
      setError('Please enter both departure and arrival airports');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`http://localhost:8000/route-weather/${departureIcao}/${arrivalIcao}`);
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

  const depMetar = data?.departure?.decoded_metar;
  const arrMetar = data?.arrival?.decoded_metar;



  const generateFlightSummary = async (depData, arrData) => {
    setLoadingSummary(true);
    try {
      const flightInfo = `
Flight Route: ${depData.icao} to ${arrData.icao}
Departure Weather: ${depData.summary_text}
Arrival Weather: ${arrData.summary_text}
Departure Conditions: ${depData.analysis.overall}
Arrival Conditions: ${arrData.analysis.overall}`;
      
      const response = await fetch('http://localhost:8000/api/gemini/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: `Provide a brief flight briefing summary (2-3 sentences) for this route with key weather insights and recommendations: ${flightInfo}`
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        setFlightSummary(result.response);
      }
    } catch (error) {
      console.error('Error generating flight summary:', error);
      setFlightSummary('Unable to generate flight summary at this time.');
    } finally {
      setLoadingSummary(false);
    }
  };

  const showDetailModal = (data, type) => {
    setModalData(data);
    setModalType(type);
  };

  const closeModal = () => {
    setModalData(null);
    setModalType('');
  };

  const togglePanel = () => {
    setPanelCollapsed(!panelCollapsed);
  };



  const goToPage = (page) => {
    setCurrentPage(page);
  };

  // Generate flight summary when data is available
  React.useEffect(() => {
    if (data && data.departure && data.arrival) {
      generateFlightSummary(data.departure, data.arrival);
      setCurrentPage(1); // Reset to first page when new data loads
    }
  }, [data]);

  // Manage body class for panel state
  React.useEffect(() => {
    if (panelCollapsed) {
      document.body.classList.add('panel-collapsed');
    } else {
      document.body.classList.remove('panel-collapsed');
    }
    
    return () => {
      document.body.classList.remove('panel-collapsed');
    };
  }, [panelCollapsed]);

  return (
    <div className="app">
      <header className="app-header" onClick={togglePanel}>
        <h1>Aerolytics - Flight Dashboard</h1>
      </header>

      {panelCollapsed && (
        <button className="panel-toggle" onClick={togglePanel}>
          ★
        </button>
      )}

      <div className={`main-content ${panelCollapsed ? 'collapsed' : ''}`}>
        {!panelCollapsed && (
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
              {/* Flight Summary Card - Always visible */}
              <div className="flight-summary-card">
                <h3>✈️ Flight Briefing</h3>
                <div className="summary-content">
                  {loadingSummary ? (
                    <div className="loading-summary">Generating flight briefing...</div>
                  ) : (
                    <p>{flightSummary}</p>
                  )}
                </div>
              </div>

              {/* Navigation Tabs - Always visible */}
              <div className="page-navigation">
                {[1, 2, 3].map(page => (
                  <button
                    key={page}
                    className={`nav-tab ${currentPage === page ? 'active' : ''}`}
                    onClick={() => goToPage(page)}
                  >
                    {page === 1 ? '📋 Overview' : page === 2 ? '🛫 Departure' : '🛬 Arrival'}
                  </button>
                ))}
              </div>

              {/* Page Content */}
              <div className="page-content">
                {currentPage === 1 && (
                  <div className="page-1">

                    {/* Airport Overview Cards */}
                    <div className="airport-overview">
                      <div className="airport-card">
                        <div className="card-header">
                          <h3>🛫 {data.departure.icao}</h3>
                          <WeatherBar level={data.departure.analysis.overall} />
                        </div>
                        <div className="airport-info">
                          <p className="airport-status">{data.departure.analysis.overall.toUpperCase()} CONDITIONS</p>
                          <p className="airport-summary">{data.departure.summary_text}</p>
                        </div>
                      </div>
                      
                      <div className="route-arrow">→</div>
                      
                      <div className="airport-card">
                        <div className="card-header">
                          <h3>🛬 {data.arrival.icao}</h3>
                          <WeatherBar level={data.arrival.analysis.overall} />
                        </div>
                        <div className="airport-info">
                          <p className="airport-status">{data.arrival.analysis.overall.toUpperCase()} CONDITIONS</p>
                          <p className="airport-summary">{data.arrival.summary_text}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {currentPage === 2 && (
                  <div className="page-2">
                    {/* Departure Weather Details */}
                    <div className="weather-card">
                      <div className="card-header">
                        <h3>🛫 Departure: {data.departure.icao}</h3>
                        <WeatherBar level={data.departure.analysis.overall} />
                      </div>
                      <div className="weather-content">
                        <div className="quick-stats">
                          <Metric label="Wind" value={depMetar?.wind || 'N/A'} />
                          <Metric label="Visibility" value={depMetar?.visibility || 'N/A'} />
                          <Metric label="Temperature" value={depMetar?.temperature || 'N/A'} />
                          <Metric label="Pressure" value={depMetar?.pressure || 'N/A'} />
                        </div>
                        <div className="weather-actions">
                          <button 
                            className="detail-btn" 
                            onClick={() => showDetailModal(depMetar, 'METAR')}
                          >
                            📊 Full METAR
                          </button>
                          <button 
                            className="detail-btn" 
                            onClick={() => showDetailModal(data.departure, 'ANALYSIS')}
                          >
                            📈 Analysis
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {currentPage === 3 && (
                  <div className="page-3">
                    {/* Arrival Weather Details */}
                    <div className="weather-card">
                      <div className="card-header">
                        <h3>🛬 Arrival: {data.arrival.icao}</h3>
                        <WeatherBar level={data.arrival.analysis.overall} />
                      </div>
                      <div className="weather-content">
                        <div className="quick-stats">
                          <Metric label="Wind" value={arrMetar?.wind || 'N/A'} />
                          <Metric label="Visibility" value={arrMetar?.visibility || 'N/A'} />
                          <Metric label="Temperature" value={arrMetar?.temperature || 'N/A'} />
                          <Metric label="Pressure" value={arrMetar?.pressure || 'N/A'} />
                        </div>
                        <div className="weather-actions">
                          <button 
                            className="detail-btn" 
                            onClick={() => showDetailModal(arrMetar, 'METAR')}
                          >
                            📊 Full METAR
                          </button>
                          <button 
                            className="detail-btn" 
                            onClick={() => showDetailModal(data.arrival, 'ANALYSIS')}
                          >
                            📈 Analysis
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>


            </div>
          )}
        </div>
        )}

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
      
      {/* Weather Detail Modal */}
      {modalData && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{modalType} Details</h3>
              <button className="modal-close" onClick={closeModal}>×</button>
            </div>
            <div className="modal-body">
              {modalType === 'METAR' && (
                <div className="metar-details">
                  <h4>Decoded METAR Report</h4>
                  <div className="data-grid">
                    <div><strong>Station:</strong> {modalData.station_id}</div>
                    <div><strong>Time:</strong> {modalData.time}</div>
                    <div><strong>Wind:</strong> {modalData.wind}</div>
                    <div><strong>Visibility:</strong> {modalData.visibility}</div>
                    <div><strong>Temperature:</strong> {modalData.temperature}</div>
                    <div><strong>Dew Point:</strong> {modalData.dew_point}</div>
                    <div><strong>Pressure:</strong> {modalData.pressure}</div>
                    <div><strong>Weather:</strong> {
                      typeof modalData.weather === 'string' 
                        ? modalData.weather 
                        : modalData.weather?.join(', ') || 'Clear conditions'
                    }</div>
                    <div><strong>Sky:</strong> {
                      typeof modalData.sky === 'string' 
                        ? modalData.sky 
                        : modalData.sky?.join(', ') || 'Clear'
                    }</div>
                  </div>
                  <div className="raw-metar">
                    <h5>Raw METAR:</h5>
                    <code>{modalData.raw}</code>
                  </div>
                </div>
              )}
              {modalType === 'ANALYSIS' && (
                <div className="analysis-details">
                  <h4>Weather Analysis</h4>
                  <div className="analysis-summary">
                    <p><strong>Overall Condition:</strong> 
                      <span className={`status-${modalData.analysis.overall}`}>
                        {modalData.analysis.overall.toUpperCase()}
                      </span>
                    </p>
                    <p><strong>Summary:</strong> {modalData.summary_text}</p>
                    {modalData.analysis.hazards?.length > 0 && (
                      <div className="hazards">
                        <h5>⚠️ Active Hazards:</h5>
                        <ul>
                          {modalData.analysis.hazards.map((hazard, idx) => (
                            <li key={idx}>{hazard}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;