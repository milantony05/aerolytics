import React, { useState } from "react";
import axios from "axios";
import { MapContainer, TileLayer, Marker, Polyline, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import AirportSearchInput from './AirportSearchInput';

// --- STYLING & ICONS ---
const styles = {
  // Main dashboard styles
  app: {
    display: 'flex', height: '100vh', width: '100vw',
    backgroundColor: '#1a1a1a', color: '#f0f0f0',
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
  },
  mapPanel: { flex: 1, height: '100vh' },
  dashboardPanel: {
    width: '450px', height: '100vh', padding: '20px',
    backgroundColor: '#242424', overflowY: 'auto',
    borderLeft: '1px solid #333'
  },
  // Component styles
  inputContainer: { display: 'flex', gap: '10px', marginBottom: '15px' },
  input: {
    width: '100%', padding: '10px', fontSize: '16px',
    backgroundColor: '#333', border: '1px solid #555',
    color: '#f0f0f0', borderRadius: '5px', textTransform: 'uppercase'
  },
  button: {
    width: '100%', padding: '12px', fontSize: '18px', fontWeight: 'bold',
    backgroundColor: '#005f73', color: 'white', border: 'none',
    borderRadius: '5px', cursor: 'pointer'
  },
  card: {
    backgroundColor: '#2c2c2c', padding: '15px',
    borderRadius: '8px', marginBottom: '20px'
  },
  metricGrid: {
    display: 'grid', gridTemplateColumns: '1fr 1fr',
    gap: '10px', marginTop: '15px'
  },
  metricItem: {
    backgroundColor: '#333', padding: '10px',
    borderRadius: '5px', textAlign: 'center'
  }
};

// Custom departure airport icon (green airplane)
const departureIcon = new L.DivIcon({
  html: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#4caf50" width="32px" height="32px" style="filter: drop-shadow(0 0 3px black);">
    <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
  </svg>`,
  className: '', iconSize: [32, 32], iconAnchor: [16, 16]
});

// Custom arrival airport icon (red target)
const arrivalIcon = new L.DivIcon({
  html: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#f44336" width="32px" height="32px" style="filter: drop-shadow(0 0 3px black);">
    <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M12,6A6,6 0 0,0 6,12A6,6 0 0,0 12,18A6,6 0 0,0 18,12A6,6 0 0,0 12,6M12,8A4,4 0 0,1 16,12A4,4 0 0,1 12,16A4,4 0 0,1 8,12A4,4 0 0,1 12,8M12,10A2,2 0 0,0 10,12A2,2 0 0,0 12,14A2,2 0 0,0 14,12A2,2 0 0,0 12,10Z"/>
  </svg>`,
  className: '', iconSize: [32, 32], iconAnchor: [16, 16]
});

// --- UTILITY COMPONENTS ---
const LoadingSpinner = () => (
  <div style={{ textAlign: 'center', margin: '30px 0' }}>
    <div style={{ display: 'inline-block', width: '40px', height: '40px', border: '4px solid #333', borderTop: '4px solid #005f73', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
    <p>Loading weather data...</p>
  </div>
);

const WeatherBar = ({ level }) => {
  const colors = { green: '#4caf50', yellow: '#ffeb3b', red: '#f44336' };
  const color = colors[level] || '#666';
  return <div style={{ width: '100%', height: '8px', backgroundColor: color, borderRadius: '4px', margin: '10px 0' }}></div>;
};

const Metric = ({ label, value }) => (
  <div style={styles.metricItem}>
    <div style={{ fontSize: '12px', color: '#aaa' }}>{label}</div>
    <div style={{ fontSize: '16px', fontWeight: 'bold' }}>{value || 'N/A'}</div>
  </div>
);

// --- MAP COMPONENT ---
const WeatherMap = ({ departure, arrival }) => {
  const mapRef = React.useRef();

  // Handle case where coordinates might not be available (always calculate for hooks)
  const depCoords = departure?.coords || [20, 0];
  const arrCoords = arrival?.coords || [20, 0];
  
  const positions = [depCoords, arrCoords];
  
  // Calculate center and bounds for better fitting
  const latitudes = [depCoords[0], arrCoords[0]];
  const longitudes = [depCoords[1], arrCoords[1]];
  const center = [
    (Math.max(...latitudes) + Math.min(...latitudes)) / 2,
    (Math.max(...longitudes) + Math.min(...longitudes)) / 2
  ];
  
  // Calculate appropriate zoom level based on distance with padding
  const latDiff = Math.abs(depCoords[0] - arrCoords[0]);
  const lonDiff = Math.abs(depCoords[1] - arrCoords[1]);
  const maxDiff = Math.max(latDiff, lonDiff);
  
  let zoomLevel = 6; // Default zoom
  if (maxDiff > 80) zoomLevel = 2;      // Global
  else if (maxDiff > 40) zoomLevel = 3;  // Intercontinental
  else if (maxDiff > 20) zoomLevel = 4;  // Continental
  else if (maxDiff > 10) zoomLevel = 5;  // Regional
  else if (maxDiff > 5) zoomLevel = 6;   // Local
  else if (maxDiff > 1) zoomLevel = 7;   // City-to-city
  else zoomLevel = 8;                    // Very local
  
  const depLevel = departure?.analysis?.overall;
  const arrLevel = arrival?.analysis?.overall;
  const routeColor = (depLevel === 'red' || arrLevel === 'red') ? '#f44336' : (depLevel === 'yellow' || arrLevel === 'yellow') ? '#ffeb3b' : '#4caf50';

  // Effect to recenter map when data changes (MUST be called before any conditional returns)
  React.useEffect(() => {
    if (mapRef.current && departure && arrival) {
      const map = mapRef.current;
      setTimeout(() => {
        map.setView(center, zoomLevel);
      }, 100);
    }
  }, [departure?.icao, arrival?.icao, center, zoomLevel]);

  // Show world map if no data yet (conditional return AFTER all hooks)
  if (!departure || !arrival) {
    return (
      <MapContainer center={[20, 0]} zoom={2} style={styles.mapPanel} ref={mapRef}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' />
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', backgroundColor: 'rgba(0,0,0,0.7)', color: 'white', padding: '20px', borderRadius: '10px', textAlign: 'center', zIndex: 1000 }}>
          <p>🌍 Enter departure and arrival airports to view route</p>
        </div>
      </MapContainer>
    );
  }

  return (
    <MapContainer center={center} zoom={zoomLevel} style={styles.mapPanel} ref={mapRef}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' />
      <Marker position={depCoords} icon={departureIcon}>
        <Tooltip permanent direction="top" offset={[0, -10]}>
          <strong>🛫 {departure.icao}</strong><br/>
          Departure
        </Tooltip>
      </Marker>
      <Marker position={arrCoords} icon={arrivalIcon}>
        <Tooltip permanent direction="top" offset={[0, -10]}>
          <strong>🛬 {arrival.icao}</strong><br/>
          Arrival
        </Tooltip>
      </Marker>
      <Polyline positions={positions} color={routeColor} weight={4} opacity={0.8} />
    </MapContainer>
  );
};

// --- MAIN APP COMPONENT ---
function App() {
  const [departureIcao, setDepartureIcao] = useState("");
  const [arrivalIcao, setArrivalIcao] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    if (!departureIcao || !arrivalIcao) { setError("Both airport codes are required."); return; }
    setLoading(true); setError(null); setData(null);
    try {
      const url = `http://127.0.0.1:8000/route-weather/${departureIcao.toUpperCase()}/${arrivalIcao.toUpperCase()}`;
      const response = await axios.get(url);
      setData(response.data);
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to fetch route data");
    } finally { setLoading(false); }
  };
  
  const depMetar = data?.departure?.decoded_metar;
  const arrMetar = data?.arrival?.decoded_metar;

  return (
    <div style={styles.app}>
      <WeatherMap departure={data?.departure} arrival={data?.arrival} />
      <div style={styles.dashboardPanel}>
        <h2 style={{ textAlign: 'center', margin: '0 0 20px 0', fontSize: '24px', fontWeight: 'bold' }}>
          ✈️ Aerolytics - Weather Copilot
        </h2>
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
        <button onClick={fetchData} disabled={loading} style={styles.button}>{loading ? "Loading..." : "Get Briefing"}</button>
        {error && <p style={{ color: "#f44336", textAlign: 'center', marginTop: '10px' }}>{error}</p>}
        
        {loading && <LoadingSpinner />}

        {data && !loading && (
          <div>
            <div style={styles.card}>
              <h3>Departure: {data.departure.icao}</h3>
              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '14px', lineHeight: '1.5' }}>{data.departure.summary_text}</pre>
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
              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '14px', lineHeight: '1.5' }}>{data.arrival.summary_text}</pre>
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
    </div>
  );
}

export default App;