import React, { useState } from 'react';
import './App.css';

function App() {
  const [airport, setAirport] = useState('');
  const [metarData, setMetarData] = useState(null);
  const [tafData, setTafData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('current'); // 'current' or 'forecast'

  const fetchWeatherData = async () => {
    if (!airport.trim()) {
      setError('Please enter an airport code');
      return;
    }

    setLoading(true);
    setError(null);
    setMetarData(null);
    setTafData(null);

    try {
      // Fetch both METAR and TAF data in parallel
      const [metarResponse, tafResponse] = await Promise.all([
        fetch(`http://localhost:5000/api/metar/${airport.toUpperCase()}`),
        fetch(`http://localhost:5000/api/taf/${airport.toUpperCase()}`)
      ]);

      const metarData = await metarResponse.json();
      const tafDataResponse = await tafResponse.json();
      
      if (metarResponse.ok) {
        setMetarData(metarData);
      } else {
        setError(metarData.error || 'Failed to fetch METAR data');
      }

      if (tafResponse.ok) {
        setTafData(tafDataResponse);
      } else {
        // TAF might not be available for all airports, so just log the error
        console.warn('TAF not available:', tafDataResponse.error);
      }
    } catch (err) {
      setError('Failed to connect to server. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchWeatherData();
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
              {loading ? 'Loading...' : 'Get Weather'}
            </button>
          </div>
        </form>

        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}

        {(metarData || tafData) && (
          <div className="weather-result">
            <h3>Weather Report for {metarData?.airport || tafData?.airport}</h3>
            
            {/* Tab Navigation */}
            <div className="tab-navigation">
              <button 
                className={`tab-button ${activeTab === 'current' ? 'active' : ''}`}
                onClick={() => setActiveTab('current')}
                disabled={!metarData}
              >
                Current (METAR)
              </button>
              <button 
                className={`tab-button ${activeTab === 'forecast' ? 'active' : ''}`}
                onClick={() => setActiveTab('forecast')}
                disabled={!tafData}
              >
                Forecast (TAF)
              </button>
            </div>

            {/* Current Weather (METAR) Tab */}
            {activeTab === 'current' && metarData && (
              <div className="tab-content">
                <h4>Current Weather Conditions</h4>
                
                {/* Raw METAR */}
                <div className="raw-metar">
                  <strong>Raw METAR:</strong>
                  <pre>{metarData.raw_metar}</pre>
                </div>

                {/* Parsed METAR Display */}
                {metarData.parsed_metar && !metarData.parsed_metar.error && (
                  <div className="parsed-metar">
                    <h5>Decoded Weather Information</h5>
                    
                    {/* Basic Info */}
                    <div className="weather-section">
                      <h6>Observation Details</h6>
                      <p><strong>Station:</strong> {metarData.parsed_metar.station}</p>
                      {metarData.parsed_metar.observation_time && (
                        <p><strong>Time:</strong> {metarData.parsed_metar.observation_time.formatted}</p>
                      )}
                    </div>

                    {/* Wind */}
                    {metarData.parsed_metar.wind && metarData.parsed_metar.wind.description && (
                      <div className="weather-section">
                        <h6>Wind</h6>
                        <p>{metarData.parsed_metar.wind.description}</p>
                      </div>
                    )}

                    {/* Visibility */}
                    {metarData.parsed_metar.visibility && metarData.parsed_metar.visibility.description && (
                      <div className="weather-section">
                        <h6>Visibility</h6>
                        <p>{metarData.parsed_metar.visibility.description}</p>
                      </div>
                    )}

                    {/* Weather */}
                    {metarData.parsed_metar.weather && metarData.parsed_metar.weather.length > 0 && (
                      <div className="weather-section">
                        <h6>Current Weather</h6>
                        {metarData.parsed_metar.weather.map((weather, index) => (
                          <p key={index}>{weather.description}</p>
                        ))}
                      </div>
                    )}

                    {/* Clouds */}
                    {metarData.parsed_metar.clouds && metarData.parsed_metar.clouds.length > 0 && (
                      <div className="weather-section">
                        <h6>Cloud Layers</h6>
                        {metarData.parsed_metar.clouds.map((cloud, index) => (
                          <p key={index}>{cloud.description}</p>
                        ))}
                      </div>
                    )}

                    {/* Temperature */}
                    {metarData.parsed_metar.temperature && metarData.parsed_metar.temperature.description && (
                      <div className="weather-section">
                        <h6>Temperature</h6>
                        <p>{metarData.parsed_metar.temperature.description}</p>
                      </div>
                    )}

                    {/* Pressure */}
                    {metarData.parsed_metar.pressure && metarData.parsed_metar.pressure.description && (
                      <div className="weather-section">
                        <h6>Barometric Pressure</h6>
                        <p>{metarData.parsed_metar.pressure.description}</p>
                      </div>
                    )}

                    {/* Remarks */}
                    {metarData.parsed_metar.remarks && (
                      <div className="weather-section">
                        <h6>Remarks</h6>
                        <p>{metarData.parsed_metar.remarks}</p>
                      </div>
                    )}

                    {/* Parsing Errors */}
                    {metarData.parsed_metar.parsing_errors && metarData.parsed_metar.parsing_errors.length > 0 && (
                      <div className="weather-section parsing-errors">
                        <h6>Parsing Notes</h6>
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
                    <h5>Parser Error</h5>
                    <p>{metarData.parsed_metar.error}</p>
                  </div>
                )}
              </div>
            )}

            {/* Forecast Weather (TAF) Tab */}
            {activeTab === 'forecast' && tafData && (
              <div className="tab-content">
                <h4>Weather Forecast</h4>
                
                {/* Raw TAF */}
                <div className="raw-metar">
                  <strong>Raw TAF:</strong>
                  <pre>{tafData.raw_taf}</pre>
                </div>

                {/* Parsed TAF Display */}
                {tafData.parsed_taf && !tafData.parsed_taf.error && (
                  <div className="parsed-metar">
                    <h5>Decoded Forecast Information</h5>
                    
                    {/* Header Info */}
                    <div className="weather-section">
                      <h6>Forecast Details</h6>
                      <p><strong>Station:</strong> {tafData.parsed_taf.station}</p>
                      {tafData.parsed_taf.issue_time && (
                        <p><strong>Issued:</strong> {tafData.parsed_taf.issue_time.formatted}</p>
                      )}
                      {tafData.parsed_taf.valid_period && (
                        <p><strong>Valid Period:</strong> {tafData.parsed_taf.valid_period.description}</p>
                      )}
                    </div>

                    {/* Base Forecast */}
                    {tafData.parsed_taf.base_forecast && (
                      <div className="weather-section">
                        <h6>Base Forecast</h6>
                        {tafData.parsed_taf.base_forecast.wind && tafData.parsed_taf.base_forecast.wind.description && (
                          <p><strong>Wind:</strong> {tafData.parsed_taf.base_forecast.wind.description}</p>
                        )}
                        {tafData.parsed_taf.base_forecast.visibility && tafData.parsed_taf.base_forecast.visibility.description && (
                          <p><strong>Visibility:</strong> {tafData.parsed_taf.base_forecast.visibility.description}</p>
                        )}
                        {tafData.parsed_taf.base_forecast.weather && tafData.parsed_taf.base_forecast.weather.length > 0 && (
                          <div>
                            <strong>Weather:</strong>
                            {tafData.parsed_taf.base_forecast.weather.map((weather, index) => (
                              <p key={index} style={{marginLeft: '1rem'}}>{weather.description}</p>
                            ))}
                          </div>
                        )}
                        {tafData.parsed_taf.base_forecast.clouds && tafData.parsed_taf.base_forecast.clouds.length > 0 && (
                          <div>
                            <strong>Clouds:</strong>
                            {tafData.parsed_taf.base_forecast.clouds.map((cloud, index) => (
                              <p key={index} style={{marginLeft: '1rem'}}>{cloud.description}</p>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Change Groups */}
                    {tafData.parsed_taf.change_groups && tafData.parsed_taf.change_groups.length > 0 && (
                      <div className="weather-section">
                        <h6>Forecast Changes</h6>
                        {tafData.parsed_taf.change_groups.map((group, index) => (
                          <div key={index} className="change-group">
                            <h6 className="change-header">
                              {group.type} 
                              {group.time_period && group.time_period.formatted && (
                                <span> - {group.time_period.formatted}</span>
                              )}
                              {group.time_period && group.time_period.description && (
                                <span> - {group.time_period.description}</span>
                              )}
                            </h6>
                            {group.conditions && group.conditions.wind && group.conditions.wind.description && (
                              <p><strong>Wind:</strong> {group.conditions.wind.description}</p>
                            )}
                            {group.conditions && group.conditions.visibility && group.conditions.visibility.description && (
                              <p><strong>Visibility:</strong> {group.conditions.visibility.description}</p>
                            )}
                            {group.conditions && group.conditions.weather && group.conditions.weather.length > 0 && (
                              <div>
                                <strong>Weather:</strong>
                                {group.conditions.weather.map((weather, wIndex) => (
                                  <p key={wIndex} style={{marginLeft: '1rem'}}>{weather.description}</p>
                                ))}
                              </div>
                            )}
                            {group.conditions && group.conditions.clouds && group.conditions.clouds.length > 0 && (
                              <div>
                                <strong>Clouds:</strong>
                                {group.conditions.clouds.map((cloud, cIndex) => (
                                  <p key={cIndex} style={{marginLeft: '1rem'}}>{cloud.description}</p>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* TAF Parser Error */}
                {tafData.parsed_taf && tafData.parsed_taf.error && (
                  <div className="parser-error">
                    <h5>Parser Error</h5>
                    <p>{tafData.parsed_taf.error}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
