@echo off
REM Aerolytics Docker Helper Script for Windows

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="build" goto build
if "%1"=="up" goto up
if "%1"=="down" goto down
if "%1"=="logs" goto logs
if "%1"=="restart" goto restart
if "%1"=="clean" goto clean
if "%1"=="dev" goto dev
if "%1"=="prod" goto prod
goto invalid

:help
echo.
echo Aerolytics Docker Helper
echo ========================
echo.
echo Available commands:
echo.
echo   docker-helper.bat build       - Build all Docker images
echo   docker-helper.bat up          - Start all services
echo   docker-helper.bat down        - Stop all services
echo   docker-helper.bat logs        - View logs from all services
echo   docker-helper.bat restart     - Restart all services
echo   docker-helper.bat clean       - Clean up Docker resources
echo   docker-helper.bat dev         - Start in development mode
echo   docker-helper.bat prod        - Start in production mode
echo   docker-helper.bat help        - Show this help message
echo.
goto end

:build
echo Building Docker images...
docker-compose build
goto end

:up
echo Starting Aerolytics services...
docker-compose up -d
echo.
echo Services started! Access the application at:
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Run 'docker-helper.bat logs' to view logs
goto end

:down
echo Stopping Aerolytics services...
docker-compose down
echo Services stopped.
goto end

:logs
echo Showing logs (press Ctrl+C to exit)...
docker-compose logs -f
goto end

:restart
echo Restarting Aerolytics services...
docker-compose restart
echo Services restarted.
goto end

:clean
echo Cleaning up Docker resources...
docker-compose down -v
docker system prune -f
echo Cleanup complete.
goto end

:dev
echo Starting Aerolytics in development mode...
docker-compose -f docker-compose.dev.yml up --build
goto end

:prod
echo Starting Aerolytics in production mode...
docker-compose up -d --build
echo.
echo Production services started!
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
goto end

:invalid
echo Invalid command: %1
echo Run 'docker-helper.bat help' for available commands
goto end

:end
