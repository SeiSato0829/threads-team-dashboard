@echo off
cd /d "%~dp0"

echo Starting Threads Auto Post System...
echo.

echo [1] Starting Backend Server...
start cmd /k python complete_backend_server.py

timeout /t 5 /nobreak > nul

echo [2] Starting Frontend...
start cmd /k npm run dev

echo.
echo System started successfully!
echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:5173
echo.
pause