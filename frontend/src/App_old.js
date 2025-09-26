import React, { useState } from 'react';
import './App.css';

function App() {
  const [airport, setAirport] = useState('');
  const [briefingData, setBriefingData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'current', or 'forecast'

  const fetchWeatherBriefing = async () => {
    if (!airport.trim()) {
      setError('Please enter an airport code');
      return;
    }

    setLoading(true);
    setError(null);
    setBriefingData(null);

    try {
      const response = await fetch(`http://localhost:5000/api/briefing/airport/${airport.toUpperCase()}`);
      const briefing = await response.json();
      
      if (response.ok) {
        setBriefingData(briefing);
        if (briefing.errors && briefing.errors.length > 0) {
          setError(`Partial data: ${briefing.errors.join(', ')}`);
        }
      } else {
        setError(briefing.error || 'Failed to fetch weather briefing');
      }
    } catch (err) {
      setError('Failed to connect to server. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchWeatherBriefing();
  };

  const getWeatherCategoryColor = (category) => {
    switch (category) {
      case 'Clear':
        return '#28a745'; // Green
      case 'Significant':
        return '#ffc107'; // Yellow/Orange
      case 'Severe':
        return '#dc3545'; // Red
      default:
        return '#6c757d'; // Gray
    }
  };

  const getWeatherCategoryIcon = (category) => {
    switch (category) {
      case 'Clear':
        return '☀️';
      case 'Significant':
        return '⚠️';
      case 'Severe':
        return '⛈️';
      default:
        return '❓';
    }
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

        {briefingData && (
          <div className="weather-result">
            <h3>Weather Briefing for {briefingData.airport}</h3>
            
            {/* Weather Classification Banner */}
            {briefingData.weather_classification && (
              <div 
                className="weather-category-banner"
                style={{
                  backgroundColor: getWeatherCategoryColor(briefingData.weather_classification.category),
                  color: 'white',
                  padding: '1rem',
                  margin: '1rem 0',
                  borderRadius: '8px',
                  textAlign: 'center'
                }}
              >
                <div className="category-header">
                  <span className="category-icon" style={{ fontSize: '2rem', marginRight: '0.5rem' }}>
                    {getWeatherCategoryIcon(briefingData.weather_classification.category)}
                  </span>
                  <span className="category-text" style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                    {briefingData.weather_classification.category} Conditions
                  </span>
                </div>
                <div className="category-score" style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
                  Confidence: {briefingData.weather_classification.confidence} | 
                  Score: {briefingData.weather_classification.score}/12
                </div>
              </div>
            )}

            {/* Summary Section */}
            {briefingData.summary && briefingData.summary.length > 0 && (
              <div className="briefing-summary">
                <h4>Key Information</h4>
                <ul>
                  {briefingData.summary.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Tab Navigation */}
            <div className="tab-navigation">
              <button 
                className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                Overview
              </button>
              <button 
                className={`tab-button ${activeTab === 'current' ? 'active' : ''}`}
                onClick={() => setActiveTab('current')}
                disabled={!briefingData.current_conditions}
              >
                Current (METAR)
              </button>
                            <button 
                className={`tab-button ${activeTab === 'forecast' ? 'active' : ''}`}
                onClick={() => setActiveTab('forecast')}
                disabled={!briefingData.forecast}
              >
                Forecast (TAF)
              </button>
              <button 
                className={`tab-button ${activeTab === 'pireps' ? 'active' : ''}`}
                onClick={() => setActiveTab('pireps')}
                disabled={!briefingData.pilot_reports || briefingData.pilot_reports.count === 0}
              >
                Pilot Reports ({briefingData.pilot_reports ? briefingData.pilot_reports.count : 0})
              </button>
            </div>

            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="tab-content">
                <h4>Weather Analysis Overview</h4>
                
                {briefingData.weather_classification && (
                  <div className="classification-details">
                    <h5>Weather Classification Analysis</h5>
                    
                    {/* Reasoning */}
                    {briefingData.weather_classification.reasoning && briefingData.weather_classification.reasoning.length > 0 && (
                      <div className="weather-section">
                        <h6>Classification Reasoning</h6>
                        <ul>
                          {briefingData.weather_classification.reasoning.map((reason, index) => (
                            <li key={index}>{reason}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Factor Analysis */}
                    {briefingData.weather_classification.factors && (
                      <div className="weather-section">
                        <h6>Weather Factor Analysis</h6>
                        <div className="factor-grid">
                          {Object.entries(briefingData.weather_classification.factors).map(([factor, data]) => (
                            <div key={factor} className="factor-item">
                              <strong>{factor.charAt(0).toUpperCase() + factor.slice(1)}:</strong>
                              <span className={`impact-${data.impact?.toLowerCase() || 'none'}`}>
                                {data.impact || 'None'} Impact (Score: {data.score})
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Briefing Time */}
                {briefingData.briefing_time && (
                  <div className="weather-section">
                    <h6>Data Currency</h6>
                    <p><strong>Last Updated:</strong> {briefingData.briefing_time.formatted || briefingData.briefing_time}</p>
                  </div>
                )}

                {/* Errors/Warnings */}
                {briefingData.errors && briefingData.errors.length > 0 && (
                  <div className="weather-section">
                    <h6>Data Availability Notes</h6>
                    <ul className="error-list">
                      {briefingData.errors.map((error, index) => (
                        <li key={index} className="warning-item">{error}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Current Weather (METAR) Tab */}
            {activeTab === 'current' && briefingData.current_conditions && (
              <div className="tab-content">
                <h4>Current Weather Conditions</h4>
                
                {/* Raw METAR */}
                <div className="raw-metar">
                  <strong>Raw METAR:</strong>
                  <pre>{briefingData.current_conditions.raw_metar}</pre>
                </div>

                {/* Use same METAR display logic as before but with briefingData structure */}
                {briefingData.current_conditions.parsed && !briefingData.current_conditions.parsed.error && (
                  <div className="parsed-metar">
                    <h5>Decoded Weather Information</h5>
                    
                    {/* Time */}
                    {briefingData.current_conditions.parsed.time && (
                      <div className="weather-section">
                        <h6>Observation Time</h6>
                        <p><strong>UTC:</strong> {briefingData.current_conditions.parsed.time.formatted}</p>
                        <p><strong>Description:</strong> {briefingData.current_conditions.parsed.time.description}</p>
                      </div>
                    )}

                    {/* Wind */}
                    {briefingData.current_conditions.parsed.wind && (
                      <div className="weather-section">
                        <h6>Wind Information</h6>
                        <p><strong>Description:</strong> {briefingData.current_conditions.parsed.wind.description}</p>
                        {briefingData.current_conditions.parsed.wind.direction && (
                          <p><strong>Direction:</strong> {briefingData.current_conditions.parsed.wind.direction}°</p>
                        )}
                        {briefingData.current_conditions.parsed.wind.speed && (
                          <p><strong>Speed:</strong> {briefingData.current_conditions.parsed.wind.speed} knots</p>
                        )}
                        {briefingData.current_conditions.parsed.wind.gust_speed && (
                          <p><strong>Gust Speed:</strong> {briefingData.current_conditions.parsed.wind.gust_speed} knots</p>
                        )}
                        {briefingData.current_conditions.parsed.wind.direction_variable && (
                          <p><strong>Variable Direction:</strong> Yes</p>
                        )}
                      </div>
                    )}

                    {/* Visibility */}
                    {briefingData.current_conditions.parsed.visibility && (
                      <div className="weather-section">
                        <h6>Visibility</h6>
                        <p><strong>Description:</strong> {briefingData.current_conditions.parsed.visibility.description}</p>
                        {briefingData.current_conditions.parsed.visibility.distance && (
                          <p><strong>Distance:</strong> {briefingData.current_conditions.parsed.visibility.distance} {briefingData.current_conditions.parsed.visibility.unit || 'statute miles'}</p>
                        )}
                      </div>
                    )}

                    {/* Weather */}
                    {briefingData.current_conditions.parsed.weather && briefingData.current_conditions.parsed.weather.length > 0 && (
                      <div className="weather-section">
                        <h6>Weather Phenomena</h6>
                        {briefingData.current_conditions.parsed.weather.map((weather, index) => (
                          <div key={index} className="weather-phenomenon">
                            <p><strong>Description:</strong> {weather.description}</p>
                            {weather.intensity && (
                              <p><strong>Intensity:</strong> {weather.intensity}</p>
                            )}
                            {weather.phenomena && weather.phenomena.length > 0 && (
                              <div>
                                <strong>Phenomena:</strong>
                                {weather.phenomena.map((phenomenon, pIndex) => (
                                  <p key={pIndex} style={{marginLeft: '1rem'}}>
                                    {phenomenon.description} ({phenomenon.code})
                                  </p>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Clouds */}
                    {briefingData.current_conditions.parsed.clouds && briefingData.current_conditions.parsed.clouds.length > 0 && (
                      <div className="weather-section">
                        <h6>Cloud Information</h6>
                        {briefingData.current_conditions.parsed.clouds.map((cloud, index) => (
                          <div key={index} className="cloud-layer">
                            <p><strong>Description:</strong> {cloud.description}</p>
                            {cloud.height_feet && (
                              <p><strong>Height:</strong> {cloud.height_feet.toLocaleString()} feet AGL</p>
                            )}
                            {cloud.type && (
                              <p><strong>Type:</strong> {cloud.type_description || cloud.type}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Temperature and Pressure */}
                    {(briefingData.current_conditions.parsed.temperature || briefingData.current_conditions.parsed.pressure) && (
                      <div className="weather-section">
                        <h6>Temperature & Pressure</h6>
                        {briefingData.current_conditions.parsed.temperature && (
                          <>
                            {briefingData.current_conditions.parsed.temperature.temperature_celsius !== undefined && (
                              <p><strong>Temperature:</strong> {briefingData.current_conditions.parsed.temperature.temperature_celsius}°C ({briefingData.current_conditions.parsed.temperature.temperature_fahrenheit}°F)</p>
                            )}
                            {briefingData.current_conditions.parsed.temperature.dewpoint_celsius !== undefined && (
                              <p><strong>Dew Point:</strong> {briefingData.current_conditions.parsed.temperature.dewpoint_celsius}°C ({briefingData.current_conditions.parsed.temperature.dewpoint_fahrenheit}°F)</p>
                            )}
                          </>
                        )}
                        {briefingData.current_conditions.parsed.pressure && (
                          <>
                            {briefingData.current_conditions.parsed.pressure.altimeter_inhg && (
                              <p><strong>Altimeter:</strong> {briefingData.current_conditions.parsed.pressure.altimeter_inhg} inHg</p>
                            )}
                            {briefingData.current_conditions.parsed.pressure.altimeter_hpa && (
                              <p><strong>Pressure:</strong> {briefingData.current_conditions.parsed.pressure.altimeter_hpa} hPa</p>
                            )}
                          </>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {/* METAR Parser Error */}
                {briefingData.current_conditions.parsed && briefingData.current_conditions.parsed.error && (
                  <div className="parser-error">
                    <h5>Parser Error</h5>
                    <p>{briefingData.current_conditions.parsed.error}</p>
                  </div>
                )}
              </div>
            )}

            {/* Forecast Weather (TAF) Tab */}
            {activeTab === 'forecast' && briefingData.forecast && (
              <div className="tab-content">
                <h4>Weather Forecast</h4>
                
                {/* Raw TAF */}
                <div className="raw-metar">
                  <strong>Raw TAF:</strong>
                  <pre>{briefingData.forecast.raw_taf}</pre>
                </div>

                {/* Use same TAF display logic as before but with briefingData structure */}
                {briefingData.forecast.parsed && !briefingData.forecast.parsed.error && (
                  <div className="parsed-metar">
                    <h5>Decoded Forecast Information</h5>
                    
                    {/* Header Info */}
                    <div className="weather-section">
                      <h6>Forecast Details</h6>
                      <p><strong>Station:</strong> {briefingData.forecast.parsed.station}</p>
                      {briefingData.forecast.parsed.issue_time && (
                        <p><strong>Issued:</strong> {briefingData.forecast.parsed.issue_time.formatted}</p>
                      )}
                      {briefingData.forecast.parsed.valid_period && (
                        <p><strong>Valid Period:</strong> {briefingData.forecast.parsed.valid_period.description}</p>
                      )}
                    </div>

                    {/* Base Forecast */}
                    {briefingData.forecast.parsed.base_forecast && (
                      <div className="weather-section">
                        <h6>Base Forecast</h6>
                        {briefingData.forecast.parsed.base_forecast.wind && briefingData.forecast.parsed.base_forecast.wind.description && (
                          <p><strong>Wind:</strong> {briefingData.forecast.parsed.base_forecast.wind.description}</p>
                        )}
                        {briefingData.forecast.parsed.base_forecast.visibility && briefingData.forecast.parsed.base_forecast.visibility.description && (
                          <p><strong>Visibility:</strong> {briefingData.forecast.parsed.base_forecast.visibility.description}</p>
                        )}
                        {briefingData.forecast.parsed.base_forecast.weather && briefingData.forecast.parsed.base_forecast.weather.length > 0 && (
                          <div>
                            <strong>Weather:</strong>
                            {briefingData.forecast.parsed.base_forecast.weather.map((weather, index) => (
                              <p key={index} style={{marginLeft: '1rem'}}>{weather.description}</p>
                            ))}
                          </div>
                        )}
                        {briefingData.forecast.parsed.base_forecast.clouds && briefingData.forecast.parsed.base_forecast.clouds.length > 0 && (
                          <div>
                            <strong>Clouds:</strong>
                            {briefingData.forecast.parsed.base_forecast.clouds.map((cloud, index) => (
                              <p key={index} style={{marginLeft: '1rem'}}>{cloud.description}</p>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Change Groups */}
                    {briefingData.forecast.parsed.change_groups && briefingData.forecast.parsed.change_groups.length > 0 && (
                      <div className="weather-section">
                        <h6>Forecast Changes</h6>
                        {briefingData.forecast.parsed.change_groups.map((group, index) => (
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
                {briefingData.forecast.parsed && briefingData.forecast.parsed.error && (
                  <div className="parser-error">
                    <h5>Parser Error</h5>
                    <p>{briefingData.forecast.parsed.error}</p>
                  </div>
                )}
              </div>
            )}

            {/* Pilot Reports (PIREP) Tab */}
            {activeTab === 'pireps' && briefingData.pilot_reports && (
              <div className="tab-content">
                <h4>Pilot Reports (PIREPs)</h4>
                
                {/* PIREP Summary */}
                {briefingData.pilot_reports.summary && (
                  <div className="pirep-summary">
                    <h5>Summary</h5>
                    <div className="summary-stats">
                      <div className="stat-item">
                        <strong>Total Reports:</strong> {briefingData.pilot_reports.count}
                      </div>
                      {briefingData.pilot_reports.summary.urgent_reports.length > 0 && (
                        <div className="stat-item urgent">
                          <strong>Urgent Reports:</strong> {briefingData.pilot_reports.summary.urgent_reports.length}
                        </div>
                      )}
                      {briefingData.pilot_reports.summary.routine_reports.length > 0 && (
                        <div className="stat-item">
                          <strong>Routine Reports:</strong> {briefingData.pilot_reports.summary.routine_reports.length}
                        </div>
                      )}
                    </div>
                    
                    {/* Condition Indicators */}
                    <div className="condition-indicators">
                      {briefingData.pilot_reports.summary.has_turbulence && (
                        <span className="condition-badge turbulence">🌪️ Turbulence Reported</span>
                      )}
                      {briefingData.pilot_reports.summary.has_icing && (
                        <span className="condition-badge icing">🧊 Icing Reported</span>
                      )}
                      {briefingData.pilot_reports.summary.has_weather && (
                        <span className="condition-badge weather">🌦️ Weather Reported</span>
                      )}
                    </div>
                  </div>
                )}

                {/* Urgent PIREPs */}
                {briefingData.pilot_reports.summary && briefingData.pilot_reports.summary.urgent_reports.length > 0 && (
                  <div className="pirep-section urgent-section">
                    <h5>⚠️ Urgent Reports</h5>
                    {briefingData.pilot_reports.summary.urgent_reports.map((pirep, index) => (
                      <div key={index} className="pirep-item urgent">
                        <div className="pirep-header">
                          <span className="pirep-urgency">URGENT</span>
                          {pirep.timestamp && <span className="pirep-time">{pirep.timestamp}</span>}
                          {pirep.location && <span className="pirep-location">📍 {pirep.location}</span>}
                        </div>
                        
                        {pirep.aircraft_type && (
                          <div className="pirep-detail">
                            <strong>Aircraft:</strong> {pirep.aircraft_type}
                          </div>
                        )}
                        
                        {pirep.altitude && (
                          <div className="pirep-detail">
                            <strong>Altitude:</strong> {pirep.altitude}
                          </div>
                        )}

                        {/* Conditions */}
                        {pirep.conditions && (
                          <div className="pirep-conditions">
                            {pirep.conditions.turbulence && (
                              <div className="condition-detail">
                                <strong>Turbulence:</strong> {
                                  typeof pirep.conditions.turbulence === 'object' 
                                    ? `${pirep.conditions.turbulence.severity} ${pirep.conditions.turbulence.altitude_range ? `(${pirep.conditions.turbulence.altitude_range})` : ''}`
                                    : pirep.conditions.turbulence
                                }
                              </div>
                            )}
                            {pirep.conditions.icing && (
                              <div className="condition-detail">
                                <strong>Icing:</strong> {
                                  typeof pirep.conditions.icing === 'object'
                                    ? `${pirep.conditions.icing.severity} ${pirep.conditions.icing.altitude_range ? `(${pirep.conditions.icing.altitude_range})` : ''}`
                                    : pirep.conditions.icing
                                }
                              </div>
                            )}
                            {pirep.conditions.wind && (
                              <div className="condition-detail">
                                <strong>Wind:</strong> {pirep.conditions.wind}
                              </div>
                            )}
                            {pirep.conditions.visibility && (
                              <div className="condition-detail">
                                <strong>Visibility:</strong> {pirep.conditions.visibility}
                              </div>
                            )}
                            {pirep.conditions.sky_conditions && (
                              <div className="condition-detail">
                                <strong>Sky:</strong> {pirep.conditions.sky_conditions}
                              </div>
                            )}
                            {pirep.conditions.temperature && (
                              <div className="condition-detail">
                                <strong>Temperature:</strong> {pirep.conditions.temperature}
                              </div>
                            )}
                          </div>
                        )}

                        {pirep.remarks && (
                          <div className="pirep-remarks">
                            <strong>Remarks:</strong> {pirep.remarks}
                          </div>
                        )}

                        {/* Raw PIREP for reference */}
                        {pirep.raw_pirep && (
                          <details className="raw-pirep-details">
                            <summary>Raw PIREP</summary>
                            <pre>{pirep.raw_pirep}</pre>
                          </details>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Routine PIREPs */}
                {briefingData.pilot_reports.summary && briefingData.pilot_reports.summary.routine_reports.length > 0 && (
                  <div className="pirep-section routine-section">
                    <h5>📋 Routine Reports</h5>
                    {briefingData.pilot_reports.summary.routine_reports.map((pirep, index) => (
                      <div key={index} className="pirep-item routine">
                        <div className="pirep-header">
                          <span className="pirep-urgency">ROUTINE</span>
                          {pirep.timestamp && <span className="pirep-time">{pirep.timestamp}</span>}
                          {pirep.location && <span className="pirep-location">📍 {pirep.location}</span>}
                        </div>
                        
                        {pirep.aircraft_type && (
                          <div className="pirep-detail">
                            <strong>Aircraft:</strong> {pirep.aircraft_type}
                          </div>
                        )}
                        
                        {pirep.altitude && (
                          <div className="pirep-detail">
                            <strong>Altitude:</strong> {pirep.altitude}
                          </div>
                        )}

                        {/* Conditions */}
                        {pirep.conditions && (
                          <div className="pirep-conditions">
                            {pirep.conditions.turbulence && (
                              <div className="condition-detail">
                                <strong>Turbulence:</strong> {
                                  typeof pirep.conditions.turbulence === 'object'
                                    ? `${pirep.conditions.turbulence.severity} ${pirep.conditions.turbulence.altitude_range ? `(${pirep.conditions.turbulence.altitude_range})` : ''}`
                                    : pirep.conditions.turbulence
                                }
                              </div>
                            )}
                            {pirep.conditions.icing && (
                              <div className="condition-detail">
                                <strong>Icing:</strong> {
                                  typeof pirep.conditions.icing === 'object'
                                    ? `${pirep.conditions.icing.severity} ${pirep.conditions.icing.altitude_range ? `(${pirep.conditions.icing.altitude_range})` : ''}`
                                    : pirep.conditions.icing
                                }
                              </div>
                            )}
                            {pirep.conditions.wind && (
                              <div className="condition-detail">
                                <strong>Wind:</strong> {pirep.conditions.wind}
                              </div>
                            )}
                            {pirep.conditions.visibility && (
                              <div className="condition-detail">
                                <strong>Visibility:</strong> {pirep.conditions.visibility}
                              </div>
                            )}
                            {pirep.conditions.sky_conditions && (
                              <div className="condition-detail">
                                <strong>Sky:</strong> {pirep.conditions.sky_conditions}
                              </div>
                            )}
                            {pirep.conditions.temperature && (
                              <div className="condition-detail">
                                <strong>Temperature:</strong> {pirep.conditions.temperature}
                              </div>
                            )}
                          </div>
                        )}

                        {pirep.remarks && (
                          <div className="pirep-remarks">
                            <strong>Remarks:</strong> {pirep.remarks}
                          </div>
                        )}

                        {/* Raw PIREP for reference */}
                        {pirep.raw_pirep && (
                          <details className="raw-pirep-details">
                            <summary>Raw PIREP</summary>
                            <pre>{pirep.raw_pirep}</pre>
                          </details>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* No PIREPs Message */}
                {briefingData.pilot_reports.count === 0 && (
                  <div className="no-pireps">
                    <p>No pilot reports available for this area at this time.</p>
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
