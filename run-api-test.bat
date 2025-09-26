@echo off
echo Running Aerolytics API Test...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found! Please install Python first.
    pause
    exit /b 1
)

REM Check if test file exists
if not exist "test_api_trustworthiness.py" (
    echo Error: Test file not found: test_api_trustworthiness.py
    pause
    exit /b 1
)

python test_api_trustworthiness.py

echo.
echo Test completed! Press any key to exit...
pause >nul