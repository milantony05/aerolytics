// Comprehensive airport database for search functionality
export const AIRPORTS_DATABASE = [
  // United States Major Airports
  { icao: 'KLAX', name: 'Los Angeles International', city: 'Los Angeles', country: 'United States', coords: [33.9416, -118.4085] },
  { icao: 'KJFK', name: 'John F Kennedy International', city: 'New York', country: 'United States', coords: [40.6413, -73.7781] },
  { icao: 'KORD', name: "Chicago O'Hare International", city: 'Chicago', country: 'United States', coords: [41.9742, -87.9073] },
  { icao: 'KATL', name: 'Hartsfield-Jackson Atlanta International', city: 'Atlanta', country: 'United States', coords: [33.6407, -84.4277] },
  { icao: 'KSFO', name: 'San Francisco International', city: 'San Francisco', country: 'United States', coords: [37.6188, -122.3750] },
  { icao: 'KDEN', name: 'Denver International', city: 'Denver', country: 'United States', coords: [39.8561, -104.6737] },
  { icao: 'KLAS', name: 'McCarran International', city: 'Las Vegas', country: 'United States', coords: [36.0840, -115.1537] },
  { icao: 'KBOS', name: 'Logan International', city: 'Boston', country: 'United States', coords: [42.3656, -71.0096] },
  { icao: 'KMIA', name: 'Miami International', city: 'Miami', country: 'United States', coords: [25.7959, -80.2870] },
  { icao: 'KSEA', name: 'Seattle-Tacoma International', city: 'Seattle', country: 'United States', coords: [47.4502, -122.3088] },
  { icao: 'KLGA', name: 'LaGuardia', city: 'New York', country: 'United States', coords: [40.7769, -73.8740] },
  { icao: 'KEWR', name: 'Newark Liberty International', city: 'Newark', country: 'United States', coords: [40.6895, -74.1745] },
  { icao: 'KPHX', name: 'Phoenix Sky Harbor International', city: 'Phoenix', country: 'United States', coords: [33.4373, -112.0078] },
  { icao: 'KIAH', name: 'George Bush Intercontinental', city: 'Houston', country: 'United States', coords: [29.9902, -95.3368] },
  { icao: 'KDFW', name: 'Dallas/Fort Worth International', city: 'Dallas', country: 'United States', coords: [32.8975, -97.0372] },

  // India Major Airports
  { icao: 'VIDP', name: 'Indira Gandhi International', city: 'Delhi', country: 'India', coords: [28.5562, 77.1000] },
  { icao: 'VABB', name: 'Chhatrapati Shivaji Maharaj International', city: 'Mumbai', country: 'India', coords: [19.0896, 72.8656] },
  { icao: 'VOBL', name: 'Kempegowda International', city: 'Bangalore', country: 'India', coords: [12.9716, 77.5946] },
  { icao: 'VOMM', name: 'Chennai International', city: 'Chennai', country: 'India', coords: [13.0827, 80.2707] },
  { icao: 'VECC', name: 'Netaji Subhas Chandra Bose International', city: 'Kolkata', country: 'India', coords: [22.6546, 88.4473] },
  { icao: 'VOHS', name: 'Rajiv Gandhi International', city: 'Hyderabad', country: 'India', coords: [17.2313, 78.4298] },
  { icao: 'VOCI', name: 'Sardar Vallabhbhai Patel International', city: 'Ahmedabad', country: 'India', coords: [22.3284, 70.7794] },
  { icao: 'VOSR', name: 'Calicut International', city: 'Calicut', country: 'India', coords: [11.1361, 75.9553] },
  { icao: 'VOTV', name: 'Thiruvananthapuram International', city: 'Thiruvananthapuram', country: 'India', coords: [8.4821, 76.9200] },
  { icao: 'VEGY', name: 'Lokpriya Gopinath Bordoloi International', city: 'Guwahati', country: 'India', coords: [26.1061, 91.5859] },
  { icao: 'VOPB', name: 'Biju Patnaik International', city: 'Bhubaneswar', country: 'India', coords: [20.2441, 85.8178] },
  { icao: 'VOTR', name: 'Tiruchirapalli International', city: 'Tiruchirappalli', country: 'India', coords: [10.7653, 78.7097] },

  // Europe Major Airports
  { icao: 'EGLL', name: 'Heathrow', city: 'London', country: 'United Kingdom', coords: [51.4700, -0.4543] },
  { icao: 'LFPG', name: 'Charles de Gaulle', city: 'Paris', country: 'France', coords: [49.0097, 2.5479] },
  { icao: 'EDDF', name: 'Frankfurt am Main', city: 'Frankfurt', country: 'Germany', coords: [50.0264, 8.5431] },
  { icao: 'EHAM', name: 'Amsterdam Airport Schiphol', city: 'Amsterdam', country: 'Netherlands', coords: [52.3086, 4.7639] },
  { icao: 'LEMD', name: 'Adolfo Suárez Madrid–Barajas', city: 'Madrid', country: 'Spain', coords: [40.4719, -3.5626] },
  { icao: 'LIRF', name: 'Leonardo da Vinci–Fiumicino', city: 'Rome', country: 'Italy', coords: [41.8003, 12.2389] },
  { icao: 'EGKK', name: 'Gatwick', city: 'London', country: 'United Kingdom', coords: [51.1481, -0.1903] },
  { icao: 'EDDM', name: 'Munich', city: 'Munich', country: 'Germany', coords: [48.3538, 11.7861] },
  { icao: 'LSZH', name: 'Zurich', city: 'Zurich', country: 'Switzerland', coords: [47.4647, 8.5492] },
  { icao: 'LFBO', name: 'Toulouse-Blagnac', city: 'Toulouse', country: 'France', coords: [43.6290, 1.3638] },
  { icao: 'LOWW', name: 'Vienna International', city: 'Vienna', country: 'Austria', coords: [48.1103, 16.5697] },
  { icao: 'LKPR', name: 'Václav Havel Airport Prague', city: 'Prague', country: 'Czech Republic', coords: [50.1008, 14.2632] },

  // Asia-Pacific Major Airports
  { icao: 'RJTT', name: 'Tokyo Haneda', city: 'Tokyo', country: 'Japan', coords: [35.7647, 140.3864] },
  { icao: 'RJAA', name: 'Narita International', city: 'Tokyo', country: 'Japan', coords: [35.7720, 140.3929] },
  { icao: 'RKSI', name: 'Incheon International', city: 'Seoul', country: 'South Korea', coords: [37.4691, 126.4505] },
  { icao: 'VHHH', name: 'Hong Kong International', city: 'Hong Kong', country: 'Hong Kong', coords: [22.3080, 113.9185] },
  { icao: 'WSSS', name: 'Singapore Changi', city: 'Singapore', country: 'Singapore', coords: [1.3644, 103.9915] },
  { icao: 'YBBN', name: 'Brisbane', city: 'Brisbane', country: 'Australia', coords: [-27.3942, 153.1218] },
  { icao: 'YSSY', name: 'Sydney Kingsford Smith', city: 'Sydney', country: 'Australia', coords: [-33.9399, 151.1753] },
  { icao: 'YMML', name: 'Melbourne', city: 'Melbourne', country: 'Australia', coords: [-37.6690, 144.8410] },
  { icao: 'NZAA', name: 'Auckland', city: 'Auckland', country: 'New Zealand', coords: [-37.0082, 174.7850] },
  { icao: 'VTBS', name: 'Suvarnabhumi', city: 'Bangkok', country: 'Thailand', coords: [13.6900, 100.7501] },
  { icao: 'WIII', name: 'Soekarno-Hatta International', city: 'Jakarta', country: 'Indonesia', coords: [-6.1256, 106.6558] },
  { icao: 'WMKK', name: 'Kuala Lumpur International', city: 'Kuala Lumpur', country: 'Malaysia', coords: [2.7456, 101.7072] },

  // Middle East Major Airports
  { icao: 'OMDB', name: 'Dubai International', city: 'Dubai', country: 'United Arab Emirates', coords: [25.2532, 55.3657] },
  { icao: 'OTHH', name: 'Hamad International', city: 'Doha', country: 'Qatar', coords: [25.2731, 51.6089] },
  { icao: 'OERK', name: 'King Khalid International', city: 'Riyadh', country: 'Saudi Arabia', coords: [24.9576, 46.6986] },
  { icao: 'LTBA', name: 'Istanbul Airport', city: 'Istanbul', country: 'Turkey', coords: [40.9769, 28.8146] },
  { icao: 'OEJN', name: 'King Abdulaziz International', city: 'Jeddah', country: 'Saudi Arabia', coords: [21.6796, 39.1565] },
  { icao: 'OMAA', name: 'Abu Dhabi International', city: 'Abu Dhabi', country: 'United Arab Emirates', coords: [24.4330, 54.6511] },

  // Canada Major Airports
  { icao: 'CYYZ', name: 'Toronto Pearson International', city: 'Toronto', country: 'Canada', coords: [43.6777, -79.6248] },
  { icao: 'CYVR', name: 'Vancouver International', city: 'Vancouver', country: 'Canada', coords: [49.1967, -123.1816] },
  { icao: 'CYUL', name: 'Montréal-Trudeau International', city: 'Montreal', country: 'Canada', coords: [45.4706, -73.7408] },
  { icao: 'CYYC', name: 'Calgary International', city: 'Calgary', country: 'Canada', coords: [51.1225, -114.0128] },

  // South America Major Airports
  { icao: 'SBGR', name: 'São Paulo-Guarulhos International', city: 'São Paulo', country: 'Brazil', coords: [-23.4356, -46.4731] },
  { icao: 'SAEZ', name: 'Ezeiza International', city: 'Buenos Aires', country: 'Argentina', coords: [-34.8222, -58.5358] },
  { icao: 'SCEL', name: 'Arturo Merino Benítez International', city: 'Santiago', country: 'Chile', coords: [-33.3930, -70.7858] },
  { icao: 'SKBO', name: 'El Dorado International', city: 'Bogotá', country: 'Colombia', coords: [4.7016, -74.1469] },

  // Africa Major Airports
  { icao: 'FAJS', name: 'OR Tambo International', city: 'Johannesburg', country: 'South Africa', coords: [-26.1392, 28.2460] },
  { icao: 'HECA', name: 'Cairo International', city: 'Cairo', country: 'Egypt', coords: [30.1219, 31.4056] },
  { icao: 'FALA', name: 'Cape Town International', city: 'Cape Town', country: 'South Africa', coords: [-33.9715, 18.6021] },
  { icao: 'FACT', name: 'Addis Ababa Bole International', city: 'Addis Ababa', country: 'Ethiopia', coords: [8.9806, 38.7990] }
];

// Search function for airports
export const searchAirports = (query) => {
  if (!query || query.length < 2) return [];
  
  const searchTerm = query.toLowerCase().trim();
  
  return AIRPORTS_DATABASE.filter(airport => {
    const nameMatch = airport.name.toLowerCase().includes(searchTerm);
    const cityMatch = airport.city.toLowerCase().includes(searchTerm);
    const countryMatch = airport.country.toLowerCase().includes(searchTerm);
    const icaoMatch = airport.icao.toLowerCase().includes(searchTerm);
    
    return nameMatch || cityMatch || countryMatch || icaoMatch;
  }).slice(0, 10); // Limit to 10 results for performance
};

// Get airport by ICAO code
export const getAirportByICAO = (icao) => {
  return AIRPORTS_DATABASE.find(airport => airport.icao.toUpperCase() === icao.toUpperCase());
};