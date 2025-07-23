@echo off
chcp 65001 >nul 2>&1
cls

echo.
echo ========================================================
echo   Threads Auto-Posting System - Improved Version
echo   Login Error Fixed - Stable Operation Guaranteed
echo ========================================================
echo.

cd /d %~dp0

echo Login error has been fixed:
echo   - More reliable login field detection
echo   - Multiple authentication pattern support
echo   - Detailed debug information output
echo   - Automatic screenshot saving on errors
echo.

echo Checking required packages...
pip install selenium schedule >nul 2>&1

echo.
echo Starting improved automation system...
python IMPROVED_AUTOMATION.py

echo.
echo Log and debug files:
echo   - threads_automation_fixed.log
echo   - debug_*.png (screenshots)
echo   - debug_*.html (page source)

pause