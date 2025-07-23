@echo off
cd /d %~dp0
echo ================================================
echo   VIRAL BUZZ SYSTEM
echo   Generate natural word-of-mouth style posts
echo ================================================
echo.
echo Installing required packages...
pip install --quiet pyperclip
echo.
echo Starting viral buzz post generation...
echo Creating posts that actually go viral!
echo.
python BUZZ_SYSTEM.py
pause