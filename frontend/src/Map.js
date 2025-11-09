import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { getAirportByICAO } from './airportDatabase';

// Fix default marker icons in Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Custom icons for departure and arrival
const createCustomIcon = (color) => {
  return L.divIcon({
    className: 'custom-icon',
    html: `<div style="
      background-color: ${color};
      width: 30px;
      height: 30px;
      border-radius: 50% 50% 50% 0;
      border: 3px solid white;
      transform: rotate(-45deg);
      box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    "><div style="
      width: 10px;
      height: 10px;
      background-color: white;
      border-radius: 50%;
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
    "></div></div>`,
    iconSize: [30, 30],
    iconAnchor: [15, 30],
    popupAnchor: [0, -30]
  });
};

const departureIcon = createCustomIcon('#4CAF50');
const arrivalIcon = createCustomIcon('#F44336');

// Component to fit bounds when airports change
const FitBounds = ({ departure, arrival }) => {
  const map = useMap();

  useEffect(() => {
    if (departure && arrival) {
      const depAirport = getAirportByICAO(departure);
      const arrAirport = getAirportByICAO(arrival);

      if (depAirport && arrAirport) {
        const bounds = L.latLngBounds(
          [depAirport.coords[0], depAirport.coords[1]],
          [arrAirport.coords[0], arrAirport.coords[1]]
        );
        map.fitBounds(bounds, { padding: [50, 50] });
      }
    }
  }, [departure, arrival, map]);

  return null;
};

const GoogleFlightMap = ({ departure, arrival, onMapReady }) => {
  const [depAirport, setDepAirport] = useState(null);
  const [arrAirport, setArrAirport] = useState(null);

  useEffect(() => {
    if (departure) {
      const airport = getAirportByICAO(departure);
      setDepAirport(airport);
    }
  }, [departure]);

  useEffect(() => {
    if (arrival) {
      const airport = getAirportByICAO(arrival);
      setArrAirport(airport);
    }
  }, [arrival]);

  const calculateDistance = (dep, arr) => {
    if (!dep || !arr) return 0;
    const R = 6371; // Earth's radius in kilometers
    const dLat = (arr.coords[0] - dep.coords[0]) * Math.PI / 180;
    const dLon = (arr.coords[1] - dep.coords[1]) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(dep.coords[0] * Math.PI / 180) * Math.cos(arr.coords[0] * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return Math.round(R * c);
  };

  const distance = depAirport && arrAirport ? calculateDistance(depAirport, arrAirport) : 0;

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <MapContainer
        center={[40.7128, -74.0060]}
        zoom={3}
        style={{ width: '100%', height: '100%', borderRadius: '8px' }}
        whenCreated={(map) => {
          if (onMapReady) onMapReady(map);
        }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {depAirport && (
          <Marker position={[depAirport.coords[0], depAirport.coords[1]]} icon={departureIcon}>
            <Popup>
              <div style={{ fontFamily: 'Arial, sans-serif' }}>
                <h4 style={{ margin: '0 0 8px 0', color: '#4CAF50' }}>
                  ✈️ {depAirport.name}
                </h4>
                <p style={{ margin: 0 }}>
                  <strong>ICAO:</strong> {depAirport.icao}<br/>
                  <strong>Location:</strong> {depAirport.city}, {depAirport.country}<br/>
                  <strong>Type:</strong> Departure Airport
                </p>
              </div>
            </Popup>
          </Marker>
        )}

        {arrAirport && (
          <Marker position={[arrAirport.coords[0], arrAirport.coords[1]]} icon={arrivalIcon}>
            <Popup>
              <div style={{ fontFamily: 'Arial, sans-serif' }}>
                <h4 style={{ margin: '0 0 8px 0', color: '#F44336' }}>
                  🛬 {arrAirport.name}
                </h4>
                <p style={{ margin: 0 }}>
                  <strong>ICAO:</strong> {arrAirport.icao}<br/>
                  <strong>Location:</strong> {arrAirport.city}, {arrAirport.country}<br/>
                  <strong>Type:</strong> Destination Airport
                </p>
              </div>
            </Popup>
          </Marker>
        )}

        {depAirport && arrAirport && (
          <Polyline
            positions={[
              [depAirport.coords[0], depAirport.coords[1]],
              [arrAirport.coords[0], arrAirport.coords[1]]
            ]}
            color="#FF6B35"
            weight={3}
            opacity={1}
          />
        )}

        <FitBounds departure={departure} arrival={arrival} />
      </MapContainer>

      {departure && arrival && depAirport && arrAirport && (
        <div style={{
          position: 'absolute',
          bottom: '16px',
          left: '16px',
          background: 'rgba(0, 0, 0, 0.8)',
          color: 'white',
          padding: '12px 16px',
          borderRadius: '8px',
          fontSize: '14px',
          fontFamily: 'monospace',
          zIndex: 1000
        }}>
          <div><strong>Route:</strong> {departure} → {arrival}</div>
          <div style={{ fontSize: '12px', marginTop: '4px', opacity: 0.8 }}>
            Distance: {distance} km ({Math.round(distance * 0.621371)} mi)
          </div>
        </div>
      )}
    </div>
  );
};

export default GoogleFlightMap;