import React, { useState } from 'react';
import './App.css';

function App() {
  const [airport, setAirport] = useState('');
  const [metarData, setMetarData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchMetar = async () => {
    if (!airport.trim()) {
      setError('Please enter an airport code');
      return;
    }

    setLoading(true);
    setError(null);
    setMetarData(null);

    try {
      const response = await fetch(`http://localhost:5000/api/metar/${airport.toUpperCase()}`);
      const data = await response.json();
      
      if (response.ok) {
        setMetarData(data);
      } else {
        setError(data.error || 'Failed to fetch METAR data');
      }
    } catch (err) {
      setError('Failed to connect to server. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchMetar();
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Aerolytics</h1>
        <p>The Pilot's Weather Co-Pilot</p>
        
        <form onSubmit={handleSubmit} className="metar-form">
          <div className="input-group">
            <input
              type="text"
              value={airport}
              onChange={(e) => setAirport(e.target.value)}
              placeholder="Enter airport code (e.g., KJFK)"
              className="airport-input"
              maxLength="4"
            />
            <button 
              type="submit" 
              className="fetch-button"
              disabled={loading}
            >
              {loading ? 'Loading...' : 'Get METAR'}
            </button>
          </div>
        </form>

        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}

        {metarData && (
          <div className="metar-result">
            <h3>Weather Report for {metarData.airport}</h3>
            
            {/* Raw METAR */}
            <div className="raw-metar">
              <strong>Raw METAR:</strong>
              <pre>{metarData.raw_metar}</pre>
            </div>

            {/* Parsed METAR Display */}
            {metarData.parsed_metar && !metarData.parsed_metar.error && (
              <div className="parsed-metar">
                <h4>Decoded Weather Information</h4>
                
                {/* Basic Info */}
                <div className="weather-section">
                  <h5>Observation Details</h5>
                  <p><strong>Station:</strong> {metarData.parsed_metar.station}</p>
                  {metarData.parsed_metar.observation_time && (
                    <p><strong>Time:</strong> {metarData.parsed_metar.observation_time.formatted}</p>
                  )}
                </div>

                {/* Wind */}
                {metarData.parsed_metar.wind && metarData.parsed_metar.wind.description && (
                  <div className="weather-section">
                    <h5>Wind</h5>
                    <p>{metarData.parsed_metar.wind.description}</p>
                  </div>
                )}

                {/* Visibility */}
                {metarData.parsed_metar.visibility && metarData.parsed_metar.visibility.description && (
                  <div className="weather-section">
                    <h5>Visibility</h5>
                    <p>{metarData.parsed_metar.visibility.description}</p>
                  </div>
                )}

                {/* Weather */}
                {metarData.parsed_metar.weather && metarData.parsed_metar.weather.length > 0 && (
                  <div className="weather-section">
                    <h5>Current Weather</h5>
                    {metarData.parsed_metar.weather.map((weather, index) => (
                      <p key={index}>{weather.description}</p>
                    ))}
                  </div>
                )}

                {/* Clouds */}
                {metarData.parsed_metar.clouds && metarData.parsed_metar.clouds.length > 0 && (
                  <div className="weather-section">
                    <h5>Cloud Layers</h5>
                    {metarData.parsed_metar.clouds.map((cloud, index) => (
                      <p key={index}>{cloud.description}</p>
                    ))}
                  </div>
                )}

                {/* Temperature */}
                {metarData.parsed_metar.temperature && metarData.parsed_metar.temperature.description && (
                  <div className="weather-section">
                    <h5>Temperature</h5>
                    <p>{metarData.parsed_metar.temperature.description}</p>
                  </div>
                )}

                {/* Pressure */}
                {metarData.parsed_metar.pressure && metarData.parsed_metar.pressure.description && (
                  <div className="weather-section">
                    <h5>Barometric Pressure</h5>
                    <p>{metarData.parsed_metar.pressure.description}</p>
                  </div>
                )}

                {/* Remarks */}
                {metarData.parsed_metar.remarks && (
                  <div className="weather-section">
                    <h5>Remarks</h5>
                    <p>{metarData.parsed_metar.remarks}</p>
                  </div>
                )}

                {/* Parsing Errors */}
                {metarData.parsed_metar.parsing_errors && metarData.parsed_metar.parsing_errors.length > 0 && (
                  <div className="weather-section parsing-errors">
                    <h5>Parsing Notes</h5>
                    {metarData.parsed_metar.parsing_errors.map((error, index) => (
                      <p key={index} className="error-note">{error}</p>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Parser Error */}
            {metarData.parsed_metar && metarData.parsed_metar.error && (
              <div className="parser-error">
                <h4>Parser Error</h4>
                <p>{metarData.parsed_metar.error}</p>
              </div>
            )}
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
