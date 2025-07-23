@echo off
cd /d %~dp0
echo ================================================
echo   Daily Auto Post Setup Wizard
echo   Configure automatic posting every day
echo ================================================
echo.
echo This will set up automatic posting at specified times every day
echo.
python SETUP_DAILY_AUTOMATION.py
pause