@echo off
chcp 65001 > nul
title Threads Auto Post System v3.2 - Complete Version

echo.
echo ========================================================
echo   Threads Auto Post System v3.2 - Complete Version
echo ========================================================
echo.
echo Full implementation compliant with Requirements v3.2
echo - SQLite Database Support
echo - 15-minute Buffer Scheduler
echo - Complete API Integration
echo - Image Upload Function
echo - Data Persistence
echo.

cd /d "%~dp0"

REM Check Python
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Install dependencies
echo [2/4] Installing dependencies...
pip install -r requirements-complete.txt --quiet

REM Initialize database
echo [3/4] Initializing database...

REM Start backend server
echo [4/4] Starting backend server...
echo.
echo Backend Server: http://localhost:5000
echo Frontend App: http://localhost:5173
echo.
echo NOTE: Do not close this window or the server will stop
echo.

REM Start frontend in new window
start "Frontend" cmd /k "echo Starting frontend... && npm run dev"

REM Start backend server (main process)
python complete_backend_server.py

echo.
echo Server has stopped
pause