import React, { useState, useEffect, useRef } from 'react';
import './SearchInput.css';
import { searchAirports } from './airportDatabase';

const SearchInput = ({ label, onAirportSelect, placeholder, initialValue }) => {
  const [searchTerm, setSearchTerm] = useState(initialValue || '');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const wrapperRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (initialValue) {
      setSearchTerm(initialValue);
    }
  }, [initialValue]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      if (searchTerm.length >= 2) {
        const results = searchAirports(searchTerm);
        setSuggestions(results.slice(0, 10));
        setShowSuggestions(true);
      } else {
        setSuggestions([]);
        setShowSuggestions(false);
      }
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [searchTerm]);

  const handleInputChange = (e) => {
    const value = e.target.value.toUpperCase();
    setSearchTerm(value);
    setSelectedIndex(-1);
  };

  const handleSelectAirport = (airport) => {
    setSearchTerm(airport.icao);
    setShowSuggestions(false);
    setSuggestions([]);
    if (onAirportSelect) {
      onAirportSelect(airport.icao);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => 
        prev < suggestions.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (selectedIndex >= 0 && suggestions[selectedIndex]) {
        handleSelectAirport(suggestions[selectedIndex]);
      } else if (searchTerm.length === 4) {
        setShowSuggestions(false);
        if (onAirportSelect) {
          onAirportSelect(searchTerm);
        }
      }
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  const handleFocus = () => {
    if (searchTerm.length >= 2 && suggestions.length > 0) {
      setShowSuggestions(true);
    }
  };

  return (
    <div className="airport-search-container" ref={wrapperRef}>
      <label className="airport-search-label">{label}</label>
      <div className="airport-input-wrapper">
        <input
          ref={inputRef}
          type="text"
          className="airport-search-input"
          value={searchTerm}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          placeholder={placeholder || 'Enter ICAO code or search...'}
          maxLength="4"
        />
        {searchTerm && (
          <button
            className="clear-button"
            onClick={() => {
              setSearchTerm('');
              setSuggestions([]);
              setShowSuggestions(false);
              inputRef.current?.focus();
            }}
            aria-label="Clear search"
          >
            ✕
          </button>
        )}
      </div>
      
      {showSuggestions && suggestions.length > 0 && (
        <div className="suggestions-dropdown">
          <div className="suggestions-header">
            {suggestions.length} airport{suggestions.length !== 1 ? 's' : ''} found
          </div>
          <ul className="suggestions-list">
            {suggestions.map((airport, index) => (
              <li
                key={airport.icao}
                className={`suggestion-item ${index === selectedIndex ? 'selected' : ''}`}
                onClick={() => handleSelectAirport(airport)}
                onMouseEnter={() => setSelectedIndex(index)}
              >
                <div className="suggestion-main">
                  <span className="suggestion-code">{airport.icao}</span>
                  <span className="suggestion-name">{airport.name}</span>
                </div>
                <div className="suggestion-location">
                  {airport.city}, {airport.country}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {showSuggestions && searchTerm.length >= 2 && suggestions.length === 0 && (
        <div className="suggestions-dropdown">
          <div className="no-results">
            No airports found. Enter a valid ICAO code.
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchInput;
