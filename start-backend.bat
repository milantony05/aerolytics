@echo off
echo Starting Aerolytics FastAPI Backend Server...
cd backend
call ..\.venv\Scripts\activate.bat
uvicorn main:app --reload --host 127.0.0.1 --port 8000