@echo off
echo ========================================
echo Installing Dependencies for Threads Auto Post System
echo ========================================
echo.

cd /d "%~dp0"

echo [1/6] Installing Flask...
pip install flask

echo.
echo [2/6] Installing Flask-CORS...
pip install flask-cors

echo.
echo [3/6] Installing Anthropic (Claude API)...
pip install anthropic

echo.
echo [4/6] Installing Requests...
pip install requests

echo.
echo [5/6] Installing Schedule...
pip install schedule

echo.
echo [6/6] Installing Pandas...
pip install pandas

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo You can now run: python complete_backend_server.py
echo.
pause