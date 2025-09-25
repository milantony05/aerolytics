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
            <h3>METAR for {metarData.airport}</h3>
            <div className="raw-metar">
              <strong>Raw METAR:</strong>
              <pre>{metarData.raw_metar}</pre>
            </div>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
