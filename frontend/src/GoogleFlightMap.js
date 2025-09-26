import React, { useEffect, useRef, useState } from 'react';
import { getAirportByICAO } from './airportDatabase';

const GoogleFlightMap = ({ departure, arrival, onMapReady }) => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const markersRef = useRef([]);
  const flightPathRef = useRef(null);

  useEffect(() => {
    loadGoogleMapsScript();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (mapLoaded && departure && arrival) {
      updateFlightRoute();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mapLoaded, departure, arrival]);

  const loadGoogleMapsScript = () => {
    if (window.google && window.google.maps) {
      initializeMap();
      return;
    }

    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.REACT_APP_GOOGLE_MAPS_API_KEY}&libraries=geometry`;
    script.async = true;
    script.defer = true;
    
    script.onload = () => {
      initializeMap();
    };
    
    script.onerror = () => {
      console.error('Failed to load Google Maps API');
    };

    document.head.appendChild(script);
  };

  const initializeMap = () => {
    if (!mapRef.current) return;

    const map = new window.google.maps.Map(mapRef.current, {
      zoom: 3,
      center: { lat: 40.7128, lng: -74.0060 }, // New York
      mapTypeId: window.google.maps.MapTypeId.HYBRID,
      styles: [
        {
          featureType: 'all',
          elementType: 'labels.text.fill',
          stylers: [{ color: '#ffffff' }]
        },
        {
          featureType: 'all',
          elementType: 'labels.text.stroke',
          stylers: [{ color: '#000000' }, { lightness: 13 }]
        },
        {
          featureType: 'administrative',
          elementType: 'geometry.fill',
          stylers: [{ color: '#000000' }]
        },
        {
          featureType: 'administrative',
          elementType: 'geometry.stroke',
          stylers: [{ color: '#144b53' }, { lightness: 14 }, { weight: 1.4 }]
        }
      ],
      streetViewControl: false,
      fullscreenControl: true,
      mapTypeControl: true,
      zoomControl: true
    });

    mapInstanceRef.current = map;
    setMapLoaded(true);
    
    if (onMapReady) {
      onMapReady(map);
    }
  };

  const clearMarkers = () => {
    markersRef.current.forEach(marker => marker.setMap(null));
    markersRef.current = [];
    
    if (flightPathRef.current) {
      flightPathRef.current.setMap(null);
      flightPathRef.current = null;
    }
  };

  const createAirportMarker = (airport, position, type) => {
    const icon = {
      path: window.google.maps.SymbolPath.CIRCLE,
      scale: 8,
      fillColor: type === 'departure' ? '#4CAF50' : '#2196F3',
      fillOpacity: 1,
      strokeColor: '#ffffff',
      strokeWeight: 2
    };

    const marker = new window.google.maps.Marker({
      position,
      map: mapInstanceRef.current,
      title: `${airport.name} (${airport.icao})`,
      icon
    });

    const infoWindow = new window.google.maps.InfoWindow({
      content: `
        <div style="padding: 8px; font-family: Arial, sans-serif;">
          <h4 style="margin: 0 0 8px 0; color: #333;">${airport.name}</h4>
          <p style="margin: 0; color: #666;">
            <strong>ICAO:</strong> ${airport.icao}<br>
            <strong>Location:</strong> ${airport.city}, ${airport.country}<br>
            <strong>Type:</strong> ${type === 'departure' ? 'Departure' : 'Arrival'} Airport
          </p>
        </div>
      `
    });

    marker.addListener('click', () => {
      infoWindow.open(mapInstanceRef.current, marker);
    });

    return marker;
  };

  const createFlightPath = (depCoords, arrCoords) => {
    const flightPath = new window.google.maps.Polyline({
      path: [
        { lat: depCoords.lat, lng: depCoords.lng },
        { lat: arrCoords.lat, lng: arrCoords.lng }
      ],
      geodesic: true,
      strokeColor: '#FF6B35',
      strokeOpacity: 1.0,
      strokeWeight: 3,
      icons: [{
        icon: {
          path: window.google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
          scale: 4,
          fillColor: '#FF6B35',
          fillOpacity: 1,
          strokeColor: '#ffffff',
          strokeWeight: 1
        },
        offset: '50%'
      }]
    });

    flightPath.setMap(mapInstanceRef.current);
    return flightPath;
  };

  const calculateDistance = (dep, arr) => {
    const R = 6371; // Earth's radius in kilometers
    const dLat = (arr.lat - dep.lat) * Math.PI / 180;
    const dLon = (arr.lng - dep.lng) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(dep.lat * Math.PI / 180) * Math.cos(arr.lat * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  };

  const updateFlightRoute = () => {
    if (!mapInstanceRef.current || !departure || !arrival) return;

    clearMarkers();

    // Get airport data
    const depAirport = getAirportByICAO(departure);
    const arrAirport = getAirportByICAO(arrival);

    if (!depAirport || !arrAirport) {
      console.error('Airport data not found for', departure, arrival);
      return;
    }

    // Create coordinates
    const depCoords = { lat: depAirport.coords[0], lng: depAirport.coords[1] };
    const arrCoords = { lat: arrAirport.coords[0], lng: arrAirport.coords[1] };

    // Create markers
    const depMarker = createAirportMarker(depAirport, depCoords, 'departure');
    const arrMarker = createAirportMarker(arrAirport, arrCoords, 'arrival');
    
    markersRef.current = [depMarker, arrMarker];

    // Create flight path
    flightPathRef.current = createFlightPath(depCoords, arrCoords);

    // Calculate and fit bounds
    const bounds = new window.google.maps.LatLngBounds();
    bounds.extend(depCoords);
    bounds.extend(arrCoords);
    
    mapInstanceRef.current.fitBounds(bounds);
    
    // Adjust zoom level based on distance
    const distance = calculateDistance(depCoords, arrCoords);
    let zoomLevel = 6;
    if (distance > 10000) zoomLevel = 3;
    else if (distance > 5000) zoomLevel = 4;
    else if (distance > 2000) zoomLevel = 5;
    else if (distance > 1000) zoomLevel = 6;
    else if (distance > 500) zoomLevel = 7;
    
    setTimeout(() => {
      mapInstanceRef.current.setZoom(Math.min(zoomLevel, mapInstanceRef.current.getZoom()));
    }, 1000);
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <div
        ref={mapRef}
        style={{
          width: '100%',
          height: '100%',
          borderRadius: '8px',
          overflow: 'hidden'
        }}
      />
      
      {!mapLoaded && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          background: 'rgba(0, 0, 0, 0.8)',
          color: 'white',
          padding: '16px 24px',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <div>Loading Google Maps...</div>
          <div style={{ fontSize: '12px', marginTop: '8px', opacity: 0.8 }}>
            Initializing flight route visualization
          </div>
        </div>
      )}

      {departure && arrival && mapLoaded && (
        <div style={{
          position: 'absolute',
          bottom: '16px',
          left: '16px',
          background: 'rgba(0, 0, 0, 0.8)',
          color: 'white',
          padding: '12px 16px',
          borderRadius: '8px',
          fontSize: '14px',
          fontFamily: 'monospace'
        }}>
          <div><strong>Route:</strong> {departure} → {arrival}</div>
          <div style={{ fontSize: '12px', marginTop: '4px', opacity: 0.8 }}>
            Flight path visualization
          </div>
        </div>
      )}
    </div>
  );
};

export default GoogleFlightMap;