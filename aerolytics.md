# Aerolytics: The Pilot's Weather Co-Pilot

## 1. Problem Statement

Aircraft pilots are responsible for gathering and analyzing extensive pre-flight information, including weather data, NOTAMs (Notice to Airmen), and other briefings. This process is often time-consuming and highly complex due to the sheer volume of information and the coded nature in which it is presented. The resulting high workload can overwhelm the flight crew, leading to the risk of critical reports being unintentionally ignored.

This project aims to develop a solution that simplifies, automates, and optimizes this process by transforming the coded textual reports into a simplified, easy-to-read summary. This ensures pilots can make informed decisions efficiently without being overwhelmed.

## 2. Core Features

The application will focus on delivering the following key features as specified in the hackathon requirements:

* **Automated Data Aggregation:**
    * Fetch real-time METAR (Meteorological Aerodrome Report), TAF (Terminal Aerodrome Forecast), and NOTAMs.
    * Allow flight crews to request individual reports or combinations, such as METAR + NOTAM + PIREP (Pilot Reports).
    * Utilize the live data API from AviationWeather.gov.
* **Intuitive Data Presentation:**
    * Decode and transform the coded textual reports into a simplified, easy-to-read summary report.
    * Build a user-friendly interface that helps pilots process and prioritize critical information.
    * Employ effective data visualization techniques like charts or mapping tools.
* **Weather Categorization:**
    * Individual reports at an airport should be categorized along with a weather summary.
    * METAR reports will be summarized into categories such as "Clear," "Significant," or "Severe".
* **Flight Route Briefing:**
    * When a flight plan is provided, the system will automatically extract the required data along the flight path.
    * It will provide a consolidated weather briefing for the entire route.

## 3. Proposed Technology Stack

To ensure rapid and focused development, the following technology stack is proposed based on the project roadmap:

* **Backend:** A minimal **Python** server using the **Flask** framework to handle API requests, data fetching, and parsing logic.
* **Frontend:** A modern, component-based user interface built with **React**.
* **Data Source:** The live weather data API from **AviationWeather.gov**.
* **Code Principles:** The implementation should be clean, simple, and minimal, avoiding redundancy or unnecessary complexity.

---

## 4. Development Roadmap for AI Agent

This project is divided into three main parts, broken down into 12 distinct phases. This entire roadmap is adapted from the interactive plan provided in `info.html`.

### Part 1: Core Weather Engine (Phases 1-4)
*Goal: Establish a stable application foundation and build the core functionality for fetching, parsing, and categorizing airport weather data.*

* **Phase 1: Project Scaffolding & METAR Foundation**
    * **Goal:** Establish a stable project foundation and achieve the first data call to fetch raw METAR data.
    * **Tasks:**
        1.  Initialize the Git repository and define the project structure for frontend/backend.
        2.  **Backend:** Set up a minimal Flask server with a `GET /api/metar/{airport}` endpoint that fetches and returns the raw METAR string.
        3.  **Frontend:** Use create-react-app to scaffold the frontend and build a basic component with an input field and a button.

* **Phase 2: Structured METAR Decoding**
    * **Goal:** Translate a raw, coded METAR string into a structured, machine-readable JSON object.
    * **Tasks:**
        1.  **Backend:** Develop a dedicated Python METAR parser module that accepts a raw string and returns a dictionary with clearly named keys.
        2.  **Backend:** Integrate the parser into the `/api/metar/{airport}` endpoint to return parsed METAR as a JSON object.
        3.  **Frontend:** Wire the UI to call the API and display the returned JSON for verification.

* **Phase 3: TAF (Forecast) Integration**
    * **Goal:** Augment the application with forward-looking weather forecast data.
    * **Tasks:**
        1.  **Backend:** Write a new function and parser for TAF data.
        2.  **Backend:** Create a new `GET /api/taf/{airport}` endpoint that returns parsed TAF data as structured JSON.
        3.  **Frontend:** Add a 'Forecast (TAF)' section to the UI to display the parsed data.

* **Phase 4: Weather Categorization & Unified Endpoint**
    * **Goal:** Implement the core business logic to classify weather severity and streamline the backend.
    * **Tasks:**
        1.  **Backend:** Create a 'Weather Classifier' module that takes parsed METAR JSON and returns 'Clear', 'Significant', or 'Severe'.
        2.  **Backend:** Refactor to a single, unified `GET /api/briefing/airport/{airport}` endpoint that returns a consolidated JSON object containing METAR, TAF, and the classification.
        3.  **Frontend:** Update the UI to use the new unified endpoint and display the weather category prominently.

### Part 2: Integrating Pilot and Airspace Data (Phases 5-9)
*Goal: Expand the briefing to include real-time pilot reports, official warnings, and critical airspace notices.*

* **Phase 5: PIREP (Pilot Reports) Integration**
    * **Goal:** Incorporate real-time, in-flight observations into the briefing package.
    * **Tasks:**
        1.  **Backend:** Write a function to fetch PIREPs for a given area.
        2.  **Backend:** Add the fetched PIREP data to the consolidated response from the `/api/briefing/airport/{airport}` endpoint.
        3.  **Frontend:** Create a "Pilot Reports" section in the UI to display PIREPs in a readable list.

* **Phase 6: SIGMET (Significant Weather) Integration**
    * **Goal:** Incorporate critical, en-route hazardous weather advisories into the briefing.
    * **Tasks:**
        1.  **Backend:** Write a function to fetch active SIGMETs from the API.
        2.  **Backend:** Parse SIGMET data to extract key details: phenomenon (e.g., severe turbulence), affected area, altitude, and valid time.
        3.  **Backend:** Integrate the parsed SIGMET information into the airport and route briefing responses.
        4.  **Frontend:** Create a new, high-visibility "Advisories" component. Use prominent styling (e.g., warning colors) to draw immediate attention to active SIGMETs.

* **Phase 7: Raw NOTAM Integration**
    * **Goal:** Fetch and display critical airspace and airport facility notices.
    * **Tasks:**
        1.  **Backend:** Write a function to fetch relevant NOTAMs for a specific airport.
        2.  **Backend:** Add the raw NOTAM text array to the unified endpoint's response.
        3.  **Frontend:** Add a "NOTAMs" tab to the UI and display the raw list of NOTAMs.

* **Phase 8: NLP for NOTAM Summarization**
    * **Goal:** Make NOTAMs more scannable by extracting key information.
    * **Tasks:**
        1.  **Backend:** Implement a simple text-processing function to identify keywords in NOTAMs (e.g., 'RWY CLOSED', 'OBSTRUCTION', 'U/S') and generate a simple category or summary.
        2.  **Backend:** Update the API to return a list of NOTAM objects, each with the raw text and a `summary` field.
        3.  **Frontend:** Enhance the NOTAMs display to show the summary for each notice.

* **Phase 9: Flight Route Briefing Endpoint**
    * **Goal:** Implement the "Flight Plan Summary" feature.
    * **Tasks:**
        1.  **Backend:** Create a `POST /api/briefing/route` endpoint that accepts a JSON object with `departure` and `arrival` airport codes.
        2.  **Backend:** The endpoint logic should call the existing `/api/briefing/<airport_code>` logic for both airports.
        3.  **Frontend:** Create a "Route Briefing" page where a user can input two airports and view the consolidated briefings for the route.

### Part 3: Advanced Features and Final Polish (Phases 10-13)
*Goal: Enhance the user experience with visualization, refined logic, and a polished interface.*

* **Phase 10: Geospatial Route Visualization**
    * **Goal:** Provide a map-based overview of the flight route and weather.
    * **Tasks:**
        1.  **Backend:** Ensure that airport coordinates are included in the API response.
        2.  **Frontend:** On the Route Briefing page, integrate a mapping library (e.g., Leaflet) to draw a line representing the flight path.
        3.  **Frontend:** Place color-coded markers on the map for each airport, representing the weather severity.

* **Phase 11: Advanced Risk Assessment Model**
    * **Goal:** Evolve the categorization into a more granular numerical risk score.
    * **Tasks:**
        1.  **Backend:** Refactor the "Weather Classifier" into a "Risk Scoring Engine." Assign weighted points for adverse conditions (e.g., low visibility, high winds) to produce a numerical score.
        2.  **Backend:** Include the `risk_score` in the API response.
        3.  **Frontend:** Display the risk score prominently in the UI.

* **Phase 12: UI/UX Refinement & Error Handling**
    * **Goal:** Ensure the application is stable, professional, and user-friendly.
    * **Tasks:**
        1.  **Frontend:** Conduct a full UI review. Add loading indicators, ensure the layout is responsive, and refine the design.
        2.  **Backend:** Implement comprehensive error handling for all endpoints to manage invalid inputs and external API failures gracefully.

* **Phase 13: Final Review and Documentation**
    * **Goal:** Prepare for project completion.
    * **Tasks:**
        1.  **Code:** Add comments to clarify complex sections of the code.
        2.  **Documentation:** Review and finalize this README, ensuring it accurately reflects the final project.