# Aerolytics: The Pilot's Weather Co-Pilot

## 1. Problem Statement

Aircraft pilots are responsible for gathering and analyzing extensive pre-flight information, including weather data and other critical advisories. This process is often time-consuming and highly complex due to the sheer volume of information and the coded nature in which it is presented. The resulting high workload can overwhelm the flight crew, leading to the risk of critical reports being unintentionally ignored.

This project aims to develop a solution that simplifies, automates, and optimizes this process by transforming the coded textual reports into a simplified, easy-to-read summary. This ensures pilots can make informed decisions efficiently without being overwhelmed.

## 2. Core Features

The application will focus on delivering the following key features:

* **Automated Data Aggregation:**
    * Fetch real-time SIGMETs (Significant Meteorological Information), METAR, TAF, and PIREPs.
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

To ensure rapid and focused development, the following technology stack is proposed:

* **Backend:** A minimal **Python** server using the **Flask** framework to handle API requests, data fetching, and parsing logic.
* **Frontend:** A modern, component-based user interface built with **React**.
* **Code Principles:** The implementation should be clean, simple, and minimal, avoiding redundancy or unnecessary complexity.

---

## 4. Development Roadmap

This project is divided into three main parts and 11 distinct phases, ordered according to the new data priority.

### Part 1: Foundational Data Layers (Phases 1-5)
*Goal: Establish the project and integrate each essential weather and pilot report data type in the correct priority order.*

* **Phase 1: Project Scaffolding**
    * **Goal:** Establish a stable project foundation for both frontend and backend development.
    * **Tasks:**
        1.  Initialize the Git repository and define the project structure.
        2.  **Backend:** Set up a minimal Flask server.
        3.  **Frontend:** Use create-react-app to scaffold the frontend application.

* **Phase 2: SIGMET (Significant Weather) Integration**
    * **Goal:** Integrate the highest-priority data first: critical, en-route hazardous weather advisories.
    * **Tasks:**
        1.  **Backend:** Write a function to fetch and parse active SIGMETs from the API.
        2.  **Backend:** Create a `GET /api/sigmets` endpoint that returns parsed SIGMET data.
        3.  **Frontend:** Create a high-visibility "Advisories" component to display active SIGMETs with prominent warning styles.

* **Phase 3: METAR (Current Conditions) Integration**
    * **Goal:** Integrate and decode the current weather conditions at specified airports.
    * **Tasks:**
        1.  **Backend:** Write a function to fetch a raw METAR report and a dedicated parser to decode it into a structured dictionary.
        2.  **Backend:** Create a `GET /api/metar/{airport}` endpoint that returns the parsed METAR as JSON.
        3.  **Frontend:** Build a component to display the decoded METAR data for a requested airport.

* **Phase 4: TAF (Forecast) Integration**
    * **Goal:** Augment the application with forward-looking weather forecast data.
    * **Tasks:**
        1.  **Backend:** Write a new function and parser for TAF data.
        2.  **Backend:** Create a `GET /api/taf/{airport}` endpoint that returns parsed TAF data as structured JSON.
        3.  **Frontend:** Add a 'Forecast (TAF)' section to the UI to display the parsed data.

* **Phase 5: PIREP (Pilot Reports) Integration**
    * **Goal:** Incorporate real-time, in-flight observations from other pilots.
    * **Tasks:**
        1.  **Backend:** Write a function to fetch and parse PIREPs for a given area.
        2.  **Backend:** Create a `GET /api/pireps` endpoint that returns a list of reports.
        3.  **Frontend:** Create a "Pilot Reports" section in the UI to display PIREPs in a readable list.

### Part 2: Data Consolidation & Route Planning (Phases 6-8)
*Goal: Unify the separate data sources into a single, cohesive briefing and apply it to a flight route.*

* **Phase 6: Unified Endpoint & Weather Categorization**
    * **Goal:** Consolidate all data sources into a single API call and implement the core weather categorization logic.
    * **Tasks:**
        1.  **Backend:** Refactor to create a single, unified `GET /api/briefing/airport/{airport}` endpoint.
        2.  **Backend:** This endpoint will orchestrate calls to fetch SIGMETs, METAR, TAF, and PIREPs relevant to the airport.
        3.  **Backend:** Implement a 'Weather Classifier' function that takes the parsed METAR and returns a 'Clear', 'Significant', or 'Severe' category.
        4.  **Frontend:** Update the UI to use this new unified endpoint to populate all data components at once.

* **Phase 7: Flight Route Briefing Endpoint**
    * **Goal:** Implement the "Flight Plan Summary" feature.
    * **Tasks:**
        1.  **Backend:** Create a `POST /api/briefing/route` endpoint that accepts `departure` and `arrival` airport codes.
        2.  **Backend:** The endpoint logic should call the unified airport briefing logic for both airports.
        3.  **Frontend:** Create a "Route Briefing" page for a user to input two airports and view the consolidated briefings.

* **Phase 8: Geospatial Route Visualization**
    * **Goal:** Provide a map-based overview of the flight route and weather.
    * **Tasks:**
        1.  **Backend:** Ensure that airport coordinates are included in the API response.
        2.  **Frontend:** On the Route Briefing page, integrate a mapping library (e.g., Leaflet) to draw the flight path and place color-coded markers representing weather severity.

### Part 3: Advanced Features and Final Polish (Phases 9-11)
*Goal: Enhance the user experience with advanced analytics, a refined UI, and robust error handling.*

* **Phase 9: Advanced Risk Assessment Model**
    * **Goal:** Evolve the categorization into a more granular numerical risk score.
    * **Tasks:**
        1.  **Backend:** Refactor the 'Weather Classifier' into a 'Risk Scoring Engine' that assigns weighted points for adverse conditions to produce a numerical score.
        2.  **Backend:** Include the `risk_score` in the API response.
        3.  **Frontend:** Display the risk score prominently in the UI.

* **Phase 10: UI/UX Refinement & Error Handling**
    * **Goal:** Ensure the application is stable, professional, and user-friendly.
    * **Tasks:**
        1.  **Frontend:** Conduct a full UI review, add loading indicators, and ensure responsive design.
        2.  **Backend:** Implement comprehensive error handling for all endpoints.

* **Phase 11: Final Review and Documentation**
    * **Goal:** Prepare for project completion.
    * **Tasks:**
        1.  Add code comments and finalize this README to accurately reflect the final project.