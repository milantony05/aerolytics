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

### Part 2: Integrating Pilot and Airspace Data (Phases 5-8)
*Goal: Expand the briefing to include real-time pilot reports and critical airspace notices.*

* **Phase 5: PIREP (Pilot Reports) Integration**
    * **Goal:** Incorporate real-time, in-flight observations into the briefing package.
    * **Tasks:**
        1.  **Backend:** Write a function to fetch PIREPs and add the data to the consolidated API response.
        2.  **Frontend:** Create a new 'Pilot Reports' section in the UI to display the PIREPs in a clean, readable format.

* **Phase 6: Raw NOTAM Integration**
    * **Goal:** Fetch and display critical airspace and airport facility notices.
    * **Tasks:**
        1.  **Backend:** Write a function to fetch relevant NOTAMs for an airport and add the raw text array to the API response.
        2.  **Frontend:** Add a 'NOTAMs' tab to the UI to display the raw list.

* **Phase 7: NLP for NOTAM Summarization**
    * **Goal:** Enhance the usability of NOTAMs by extracting key information.
    * **Tasks:**
        1.  **Backend:** Use a simple text-processing approach to identify keywords (e.g., 'RWY CLOSED', 'U/S') and categorize each NOTAM.
        2.  **Backend:** Update the API to return a list of NOTAM objects, each containing the raw text and a new category/summary field.
        3.  **Frontend:** Update the NOTAMs display to show the category for each notice.

* **Phase 8: Flight Route Briefing Endpoint**
    * **Goal:** Implement the core 'Flight Plan Summary' feature.
    * **Tasks:**
        1.  **Backend:** Create a `POST /api/briefing/route` endpoint that accepts departure and arrival airports.
        2.  **Backend:** The service should call the existing airport briefing logic for the departure and destination airports.
        3.  **Frontend:** Create a 'Route Briefing' page for a user to input two airports and see the consolidated briefings.

### Part 3: Advanced Features and Final Polish (Phases 9-12)
*Goal: Enhance the user experience with visualization, refined logic, and a polished interface.*

* **Phase 9: Geospatial Route Visualization**
    * **Goal:** Provide a graphical, map-based overview of the flight route and weather.
    * **Tasks:**
        1.  **Backend:** Ensure airport coordinates are included in the API response.
        2.  **Frontend:** Integrate a mapping library (e.g., Leaflet) to draw the flight path and place color-coded markers for weather severity at each airport.

* **Phase 10: Advanced Risk Assessment Model**
    * **Goal:** Evolve the simple categorization into a more granular numerical risk score.
    * **Tasks:**
        1.  **Backend:** Refactor the 'Weather Classifier' into a 'Risk Scoring Engine' that assigns weighted points for adverse conditions to output a numerical score.
        2.  **Frontend:** Display the numerical risk score prominently in the UI.

* **Phase 11: UI/UX Refinement and Robustness**
    * **Goal:** Ensure the application is stable, professional, and provides a polished user experience.
    * **Tasks:**
        1.  **Frontend:** Conduct a full UI/UX review, add loading indicators, smooth transitions, and ensure responsive design.
        2.  **Backend:** Implement comprehensive error handling for all endpoints, returning clear error messages.

* **Phase 12: Presentation and Demonstration Preparation**
    * **Goal:** Prepare a winning pitch and a flawless live demonstration of the application.
    * **Tasks:**
        1.  Create presentation slides articulating the problem, solution, architecture, and benefits.
        2.  Rehearse the presentation and live demo flow.
        3.  Finalize the project's README and ensure the codebase is clean and well-commented.