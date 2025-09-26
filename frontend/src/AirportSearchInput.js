import React, { useState, useEffect, useRef } from 'react';
import { searchAirports, getAirportByICAO } from './airportDatabase';
import './AirportSearchInput.css';

const AirportSearchInput = ({ value, onChange, placeholder, label }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  // eslint-disable-next-line no-unused-vars
  const [selectedAirport, setSelectedAirport] = useState(null);
  const inputRef = useRef(null);
  const suggestionsRef = useRef(null);

  // Initialize with existing value
  useEffect(() => {
    if (value && value !== searchQuery) {
      const airport = getAirportByICAO(value);
      if (airport) {
        setSelectedAirport(airport);
        setSearchQuery(`${airport.name} (${airport.icao})`);
      } else {
        setSearchQuery(value);
      }
    }
  }, [value, searchQuery]);

  // Handle search input changes
  const handleInputChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    setSelectedAirport(null);

    if (query.length >= 2) {
      const results = searchAirports(query);
      setSuggestions(results);
      setShowSuggestions(true);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }

    // If user is typing, clear the selected airport and pass raw query
    onChange(query);
  };

  // Handle airport selection from dropdown
  const handleAirportSelect = (airport) => {
    setSelectedAirport(airport);
    setSearchQuery(`${airport.name} (${airport.icao})`);
    setShowSuggestions(false);
    onChange(airport.icao); // Pass ICAO code to parent
  };

  // Handle input focus
  const handleFocus = () => {
    if (searchQuery.length >= 2) {
      setShowSuggestions(true);
    }
  };

  // Handle input blur (with delay to allow clicking on suggestions)
  const handleBlur = () => {
    setTimeout(() => {
      setShowSuggestions(false);
    }, 200);
  };

  // Handle keyboard navigation
  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  return (
    <div className="airport-search-container">
      {label && <label className="airport-search-label">{label}</label>}
      <div className="airport-search-input-wrapper">
        <input
          ref={inputRef}
          type="text"
          value={searchQuery}
          onChange={handleInputChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          placeholder={placeholder || "Search by airport name, city, or ICAO code..."}
          className="airport-search-input"
          autoComplete="off"
        />
        
        {showSuggestions && suggestions.length > 0 && (
          <div ref={suggestionsRef} className="airport-suggestions">
            {suggestions.map((airport, index) => (
              <div
                key={airport.icao}
                className="airport-suggestion-item"
                onClick={() => handleAirportSelect(airport)}
              >
                <div className="airport-suggestion-main">
                  <span className="airport-name">{airport.name}</span>
                  <span className="airport-icao">({airport.icao})</span>
                </div>
                <div className="airport-suggestion-location">
                  {airport.city}, {airport.country}
                </div>
              </div>
            ))}
          </div>
        )}
        
        {showSuggestions && suggestions.length === 0 && searchQuery.length >= 2 && (
          <div className="airport-suggestions">
            <div className="airport-suggestion-item no-results">
              No airports found matching "{searchQuery}"
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AirportSearchInput;