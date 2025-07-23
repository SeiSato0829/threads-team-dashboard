@echo off
echo ========================================
echo Restarting Threads Auto Post System v3.2
echo ========================================
echo.

cd /d "%~dp0"

echo [1] Starting Backend Server...
start "Backend Server" cmd /k "python complete_backend_server.py"

echo [2] Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

echo [3] Starting Frontend App...
start "Frontend App" cmd /k "npm run dev"

echo.
echo ========================================
echo System Restart Complete!
echo ========================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Press any key to close this window...
pause > nul