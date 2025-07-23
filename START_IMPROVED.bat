@echo off
setlocal enabledelayedexpansion
chcp 932 >nul 2>&1

cls
echo.
echo ================================================
echo  Threads Automation System - Fixed Version
echo ================================================
echo.
echo Starting system...
echo.

cd /d "%~dp0"

echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python.
    pause
    exit /b 1
)

echo Installing packages...
python -m pip install --quiet selenium schedule asyncio

echo.
echo Launching improved automation...
python IMPROVED_AUTOMATION.py

echo.
echo Process completed.
pause