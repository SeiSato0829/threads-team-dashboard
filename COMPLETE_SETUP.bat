@echo off
cd /d %~dp0
echo ================================================
echo   COMPLETE THREADS AUTOMATION SETUP
echo   Posts + Analytics + Team Dashboard
echo ================================================
echo.
echo This will set up:
echo - Post generation system
echo - Automatic posting
echo - Visual dashboard at http://localhost:8501
echo - Performance analytics
echo - Team collaboration tools
echo - Automated reporting
echo.

REM Install all required packages
echo Installing all required packages...
pip install --quiet streamlit plotly pandas selenium pyperclip

echo.
echo Running complete setup...
python AUTO_DASHBOARD_SETUP.py

echo.
echo ================================================
echo   SETUP COMPLETE!
echo ================================================
echo.
echo Your integrated system is ready:
echo.
echo 1. Generate posts: THREADS_ULTIMATE_START.bat
echo 2. Setup automation: BUZZ_SETUP.bat  
echo 3. View dashboard: DASHBOARD_START.bat
echo 4. Integrated view: INTEGRATED_START.bat
echo.
echo Dashboard will be available at: http://localhost:8501
echo.
pause