import React, { useState, useEffect, useRef, useCallback } from 'react';
import './AirportSearchInput.css';

const AMADEUS_API_BASE = process.env.REACT_APP_AMADEUS_API_BASE;
const AMADEUS_CLIENT_ID = process.env.REACT_APP_AMADEUS_API_KEY;
const AMADEUS_CLIENT_SECRET = process.env.REACT_APP_AMADEUS_API_SECRET;

// IATA to ICAO conversion map (since Amadeus primarily uses IATA codes)
const IATA_TO_ICAO = {
  // United States - Major Airports
  'LAX': 'KLAX', 'JFK': 'KJFK', 'ORD': 'KORD', 'ATL': 'KATL',
  'SFO': 'KSFO', 'DEN': 'KDEN', 'LAS': 'KLAS', 'BOS': 'KBOS',
  'MIA': 'KMIA', 'SEA': 'KSEA', 'DFW': 'KDFW', 'CLT': 'KCLT',
  'LGA': 'KLGA', 'EWR': 'KEWR', 'PHX': 'KPHX', 'IAH': 'KIAH',
  'MSP': 'KMSP', 'DTW': 'KDTW', 'PHL': 'KPHL', 'BWI': 'KBWI',
  'SAN': 'KSAN', 'TPA': 'KTPA', 'PDX': 'KPDX', 'STL': 'KSTL',
  'HNL': 'PHNL', 'ANC': 'PANC', 'OAK': 'KOAK', 'MDW': 'KMDW',
  'BUR': 'KBUR', 'SJC': 'KSJC', 'SMF': 'KSMF', 'RDU': 'KRDU',
  'AUS': 'KAUS', 'BNA': 'KBNA', 'MCI': 'KMCI', 'CLE': 'KCLE',
  'PIT': 'KPIT', 'IND': 'KIND', 'CVG': 'KCVG', 'CMH': 'KCMH',
  'MKE': 'KMKE', 'BDL': 'KBDL', 'PVD': 'KPVD', 'ALB': 'KALB',
  
  // Canada
  'YYZ': 'CYYZ', 'YVR': 'CYVR', 'YUL': 'CYUL', 'YYC': 'CYYC',
  'YOW': 'CYOW', 'YWG': 'CYWG', 'YHZ': 'CYHZ', 'YEG': 'CYEG',
  'YQB': 'CYQB', 'YXE': 'CYXE', 'YQR': 'CYQR', 'YQX': 'CYQX',
  
  // India - Major Airports
  'DEL': 'VIDP', 'BOM': 'VABB', 'BLR': 'VOBL', 'MAA': 'VOMM',
  'CCU': 'VECC', 'HYD': 'VOHS', 'AMD': 'VOCI', 'COK': 'VOSR',
  'GOI': 'VOGO', 'PNQ': 'VAPO', 'JAI': 'VIJP', 'LKO': 'VILK',
  'IXC': 'VOCI', 'NAG': 'VANP', 'TRV': 'VOTV', 'CJB': 'VOCB',
  'IXB': 'VEBI', 'GAU': 'VEGT', 'IXA': 'VEAT', 'IXJ': 'VEJM',
  'IXR': 'VERC', 'PAT': 'VEPT', 'RPR': 'VARP', 'BHO': 'VABP',
  
  // United Kingdom & Ireland
  'LHR': 'EGLL', 'LGW': 'EGKK', 'STN': 'EGSS', 'LTN': 'EGGW',
  'MAN': 'EGCC', 'EDI': 'EGPH', 'GLA': 'EGPF', 'BHX': 'EGBB',
  'LPL': 'EGGP', 'NCL': 'EGNT', 'BRS': 'EGGD', 'CWL': 'EGFF',
  'BEL': 'EGAA', 'DUB': 'EIDW', 'ORK': 'EICK', 'SNN': 'EINN',
  
  // France
  'CDG': 'LFPG', 'ORY': 'LFPO', 'NCE': 'LFMN', 'LYS': 'LFLL',
  'MRS': 'LFML', 'TLS': 'LFBO', 'BOD': 'LFBD', 'NTE': 'LFRS',
  'MLH': 'LFSB', 'LIL': 'LFQQ', 'MPL': 'LFMT', 'BIQ': 'LFBZ',
  
  // Germany
  'FRA': 'EDDF', 'MUC': 'EDDM', 'DUS': 'EDDL', 'TXL': 'EDDT',
  'BER': 'EDDB', 'HAM': 'EDDH', 'CGN': 'EDDK', 'STR': 'EDDS',
  'HAJ': 'EDDV', 'NUE': 'EDDN', 'LEJ': 'EDDP', 'FDH': 'EDAH',
  
  // Netherlands & Belgium
  'AMS': 'EHAM', 'RTM': 'EHRD', 'EIN': 'EHEH', 'GRQ': 'EHGG',
  'BRU': 'EBBR', 'ANR': 'EBAW', 'CRL': 'EBCI', 'LGG': 'EBLG',
  
  // Spain & Portugal
  'MAD': 'LEMD', 'BCN': 'LEBL', 'PMI': 'LEPA', 'LPA': 'GCLP',
  'AGP': 'LEMG', 'BIO': 'LEBB', 'SVQ': 'LEZL', 'VLC': 'LEVC',
  'LIS': 'LPPT', 'OPO': 'LPPR', 'FAO': 'LPFR', 'FNC': 'LPMA',
  
  // Italy
  'FCO': 'LIRF', 'MXP': 'LIMC', 'LIN': 'LIML', 'BGY': 'LIME',
  'VCE': 'LIPZ', 'NAP': 'LIRN', 'CTA': 'LICC', 'BLQ': 'LIPE',
  'FLR': 'LIRQ', 'PSA': 'LIRP', 'BRI': 'LIBD', 'CAG': 'LIEE',
  
  // Switzerland & Austria
  'ZUR': 'LSZH', 'GVA': 'LSGG', 'BSL': 'LFSB', 'BRN': 'LSZB',
  'VIE': 'LOWV', 'SZG': 'LOWS', 'INN': 'LOWI', 'GRZ': 'LOWG',
  
  // Scandinavia
  'ARN': 'ESSA', 'GOT': 'ESGG', 'MMX': 'ESMS', 'CPH': 'EKCH',
  'AAL': 'EKYT', 'BLL': 'EKBI', 'OSL': 'ENGM', 'BGO': 'ENBR',
  'TRD': 'ENVA', 'SVG': 'ENZV', 'HEL': 'EFHK', 'TMP': 'EFTP',
  
  // Eastern Europe
  'SVO': 'UUEE', 'DME': 'UUDD', 'VKO': 'UUWW', 'LED': 'ULLI',
  'WAW': 'EPWA', 'KRK': 'EPKK', 'GDN': 'EPGD', 'WRO': 'EPWR',
  'PRG': 'LKPR', 'BUD': 'LHBP', 'OTP': 'LROP', 'SOF': 'LBSF',
  
  // Asia-Pacific - Japan
  'NRT': 'RJAA', 'HND': 'RJTT', 'KIX': 'RJBB', 'ITM': 'RJOO',
  'CTS': 'RJCC', 'FUK': 'RJFF', 'SDJ': 'RJSN', 'KMJ': 'RJOK',
  'OKA': 'ROAH', 'NGO': 'RJGG', 'HIJ': 'RJOA', 'TAK': 'RJFK',
  
  // South Korea
  'ICN': 'RKSI', 'GMP': 'RKSS', 'PUS': 'RKPK', 'CJU': 'RKPC',
  'TAE': 'RKTN', 'KWJ': 'RKJK', 'USN': 'RKPU', 'YNY': 'RKNY',
  
  // China
  'PEK': 'ZBAA', 'PKX': 'ZBAD', 'PVG': 'ZSPD', 'SHA': 'ZSSS',
  'CAN': 'ZGGG', 'SZX': 'ZGSZ', 'CTU': 'ZUUU', 'KMG': 'ZPPP',
  'XIY': 'ZLXY', 'CGO': 'ZHCC', 'WUH': 'ZHHH', 'CSX': 'ZSCX',
  'HGH': 'ZSHC', 'NKG': 'ZSNJ', 'TSN': 'ZBTJ', 'DLC': 'ZYTL',
  
  // Southeast Asia
  'HKG': 'VHHH', 'SIN': 'WSSS', 'KUL': 'WMKK', 'CGK': 'WIII',
  'BKK': 'VTBS', 'DMK': 'VTBD', 'MNL': 'RPLL', 'CEB': 'RPVM',
  'SGN': 'VVTS', 'HAN': 'VVNB', 'DAD': 'VVDN', 'RGN': 'VYYY',
  'PNH': 'VDPP', 'VTE': 'VLVT', 'BWN': 'WBSB', 'DPS': 'WADD',
  
  // Australia & New Zealand
  'SYD': 'YSSY', 'MEL': 'YMML', 'BNE': 'YBBN', 'PER': 'YPPH',
  'ADL': 'YPAD', 'DRW': 'YPDN', 'CNS': 'YBCS', 'HBA': 'YMHB',
  'CBR': 'YSCB', 'OOL': 'YBCG', 'AKL': 'NZAA', 'WLG': 'NZWN',
  'CHC': 'NZCH', 'ZQN': 'NZQN', 'DUD': 'NZDN', 'PMR': 'NZPM',
  
  // Middle East
  'DXB': 'OMDB', 'AUH': 'OMAA', 'DOH': 'OTHH', 'DWC': 'OMDW',
  'SHJ': 'OMSJ', 'RAS': 'OMRK', 'KWI': 'OKBK', 'RUH': 'OERK',
  'JED': 'OEJN', 'DMM': 'OEDF', 'MED': 'OEMA', 'TIF': 'OETF',
  'BAH': 'OBBI', 'MCT': 'OOMS', 'SLL': 'OOSA', 'TLV': 'LLBG',
  'VDA': 'LLOV', 'ETH': 'OIEL', 'AMM': 'OJAI', 'AQJ': 'OJAQ',
  'BEY': 'OLBA', 'DAM': 'OSDI', 'ALP': 'OSAP', 'BGW': 'ORBI',
  'BSR': 'ORMM', 'EBL': 'OREB', 'IKA': 'OIIE', 'THR': 'OIII',
  
  // Africa
  'CAI': 'HECA', 'SSH': 'HESH', 'HRG': 'HEGN', 'LXR': 'HELX',
  'CMN': 'GMMN', 'RAK': 'GMMX', 'FEZ': 'GMFF',
  'CPT': 'FACT', 'JNB': 'FAJS', 'DUR': 'FALE', 'PLZ': 'FAPE',
  'LOS': 'DNMM', 'ABV': 'DNAA', 'KAN': 'DNKN', 'PHC': 'DNPO',
  'ACC': 'DGAA', 'KMS': 'DGSI', 'ABJ': 'DIAP', 'NBO': 'HKJK',
  'MBA': 'HKMO', 'EBB': 'HUEN', 'KGL': 'HRYR', 'DAR': 'HTDA',
  'ZNZ': 'HTZA', 'ADD': 'HAAB', 'BJM': 'HADR', 'ASM': 'HEAS',
  
  // South America
  'GRU': 'SBGR', 'CGH': 'SBSP', 'SDU': 'SBRJ', 'GIG': 'SBGL',
  'BSB': 'SBBR', 'CNF': 'SBCF', 'FOR': 'SBFZ', 'REC': 'SBRF',
  'SSA': 'SBSV', 'CWB': 'SBCT', 'POA': 'SBPA', 'MAO': 'SBEG',
  'VCP': 'SBKP', 'EZE': 'SAEZ', 'AEP': 'SABE',
  'COR': 'SACO', 'MDZ': 'SAME', 'SCL': 'SCEL', 'BOG': 'SKBO',
  'MDE': 'SKRG', 'CTG': 'SKCG', 'CLO': 'SKCL', 'LIM': 'SPJC',
  'CUZ': 'SPZO', 'AQP': 'SPQU', 'UIO': 'SEQM', 'GYE': 'SEGU',
  'CCS': 'SVMI', 'MAR': 'SVMC', 'VLN': 'SVVL', 'GEO': 'SYCJ'
};

// Function to convert IATA to ICAO
const convertIataToIcao = (iataCode) => {
  const icao = IATA_TO_ICAO[iataCode?.toUpperCase()];
  console.log(`🔄 Converting ${iataCode} → ${icao || iataCode}`);
  return icao || iataCode; // Return ICAO if found, otherwise return original
};



const AirportSearchInput = ({ value, onChange, placeholder, label }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [, setSelectedAirport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [accessToken, setAccessToken] = useState(null);
  const inputRef = useRef(null);
  const suggestionsRef = useRef(null);

  // Get Amadeus access token
  const getAccessToken = useCallback(async () => {
    try {
      console.log('🔑 Attempting to get Amadeus access token...');
      console.log('🌐 API Base:', AMADEUS_API_BASE);
      console.log('🔑 Client ID:', AMADEUS_CLIENT_ID ? 'Present' : 'Missing');
      console.log('🔐 Client Secret:', AMADEUS_CLIENT_SECRET ? 'Present' : 'Missing');
      
      const response = await fetch(`${AMADEUS_API_BASE}/v1/security/oauth2/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `grant_type=client_credentials&client_id=${AMADEUS_CLIENT_ID}&client_secret=${AMADEUS_CLIENT_SECRET}`
      });

      console.log('🔑 Token response status:', response.status);
      console.log('🔑 Response headers:', Object.fromEntries(response.headers));
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Access token obtained successfully', data);
        setAccessToken(data.access_token);
        return data.access_token;
      } else {
        const errorData = await response.text();
        console.error('❌ Token request failed:', response.status);
        console.error('❌ Error response:', errorData);
        throw new Error(`Failed to get access token: ${response.status} - ${errorData}`);
      }
    } catch (error) {
      console.error('❌ Error getting Amadeus access token:', error);
      return null;
    }
  }, []);

  // Initialize access token on component mount
  useEffect(() => {
    getAccessToken();
  }, [getAccessToken]);

  // Search airports using Amadeus API
  const searchAmadeusAirports = useCallback(async (query, token) => {
    try {
      const url = `${AMADEUS_API_BASE}/v1/reference-data/locations?subType=AIRPORT&keyword=${encodeURIComponent(query)}&page%5Blimit%5D=10`;
      console.log('🔍 Searching airports for:', query);
      console.log('🌐 Request URL:', url);
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('🔍 Airport search response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Full API response:', JSON.stringify(data, null, 2));
        console.log('📊 Response keys:', Object.keys(data));
        console.log('📊 Data array:', data.data);
        console.log('📊 Data array length:', data.data?.length || 'No data array');
        
        // Check if data exists and has the expected structure
        if (!data.data || !Array.isArray(data.data)) {
          console.error('❌ Unexpected API response structure:', data);
          return [];
        }
        
        const airports = data.data.map((airport, index) => {
          console.log(`🛩️ Airport ${index + 1}:`, JSON.stringify(airport, null, 2));
          console.log(`📋 Available keys:`, Object.keys(airport));
          
          // Extract IATA code from Amadeus response
          const iataCode = airport.iataCode || airport.id;
          // Convert IATA to ICAO for backend compatibility
          const icaoCode = convertIataToIcao(iataCode);
          
          const mapped = {
            iata: iataCode,
            icao: icaoCode,
            name: airport.name || airport.detailedName || 'Unknown Airport',
            city: airport.address?.cityName || airport.cityName || '',
            country: airport.address?.countryName || airport.countryName || '',
            location: `${airport.address?.cityName || airport.cityName || ''}, ${airport.address?.countryName || airport.countryName || ''}`
          };
          
          console.log(`✈️ Mapped airport - IATA: ${mapped.iata} → ICAO: ${mapped.icao}`);
          return mapped;
        });
        
        console.log('📍 Final mapped airports:', airports);
        return airports;
      } else {
        const errorData = await response.text();
        console.error('❌ Airport search failed:', response.status, errorData);
        throw new Error(`Failed to search airports: ${response.status}`);
      }
    } catch (error) {
      console.error('❌ Error searching airports:', error);
      return [];
    }
  }, []);

  // Handle search input changes with API call
  const handleInputChange = async (e) => {
    const query = e.target.value;
    console.log('📝 Input changed to:', query);
    setSearchQuery(query);
    setSelectedAirport(null);

    if (query.length >= 3) {
      console.log('🚀 Starting search for:', query);
      setLoading(true);
      let token = accessToken;
      
      // Get new token if needed
      if (!token) {
        console.log('🔑 No token, getting new one...');
        token = await getAccessToken();
      }

      if (token) {
        console.log('✅ Token available, searching...');
        const results = await searchAmadeusAirports(query, token);
        console.log('📊 Search results:', results);
        setSuggestions(results);
        setShowSuggestions(true);
      } else {
        console.error('❌ No token available for search');
        setSuggestions([]);
        setShowSuggestions(false);
      }
      setLoading(false);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }

    // Only update parent when an airport is selected, not on every character
  };

  // Handle airport selection from dropdown
  const handleAirportSelect = (airport) => {
    setSelectedAirport(airport);
    setSearchQuery(`${airport.name} (${airport.iata})`);
    setShowSuggestions(false);
    
    console.log('✈️ Selected airport:', airport);
    console.log('🏷️ Using ICAO code:', airport.icao);
    
    // Use ICAO directly from API response
    onChange(airport.icao); // Pass ICAO code to parent
  };

  // Handle input focus
  const handleFocus = () => {
    if (searchQuery.length >= 3 && suggestions.length > 0) {
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
          placeholder={placeholder || "Search by airport name, city, or IATA code..."}
          className="airport-search-input"
          autoComplete="off"
        />
        
        {loading && (
          <div className="airport-suggestions">
            <div className="airport-suggestion-item loading">
              🔍 Searching airports...
            </div>
          </div>
        )}
        
        {showSuggestions && !loading && suggestions.length > 0 && (
          <div ref={suggestionsRef} className="airport-suggestions">
            {suggestions.map((airport, index) => (
              <div
                key={airport.iata || index}
                className="airport-suggestion-item"
                onClick={() => handleAirportSelect(airport)}
              >
                <div className="airport-suggestion-main">
                  <span className="airport-name">{airport.name}</span>
                  <span className="airport-icao">
                    ({airport.iata}{airport.icao && airport.icao !== airport.iata ? `/${airport.icao}` : ''})
                  </span>
                </div>
                <div className="airport-suggestion-location">
                  {airport.location}
                </div>
              </div>
            ))}
          </div>
        )}
        
        {showSuggestions && !loading && suggestions.length === 0 && searchQuery.length >= 3 && (
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