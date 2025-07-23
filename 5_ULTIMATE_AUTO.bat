@echo off
echo ================================================
echo   Ultimate Threads Automation System 2024
echo   Meta Official API - Full Automation
echo ================================================
echo.

cd /d %~dp0

echo Installing required packages...
pip install aiohttp asyncio schedule requests pandas python-dotenv

echo.
echo Starting system...
python ULTIMATE_THREADS_AUTOMATION.py

pause