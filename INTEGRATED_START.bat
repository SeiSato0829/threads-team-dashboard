@echo off
cd /d %~dp0
echo ================================================
echo   Integrated Threads Management System
echo   Posts + Dashboard + Analytics
echo ================================================

REM Start dashboard in background
start /min AUTO_DASHBOARD_UPDATER.bat

REM Wait for system ready
timeout /t 3

REM Start main dashboard
echo Starting dashboard at http://localhost:8501
streamlit run THREADS_DASHBOARD.py --server.port 8501
