@echo off
cd /d %~dp0
echo ================================================
echo   FIXED Threads Dashboard - Error Resolved
echo   Database structure unified
echo ================================================
echo.

REM Fix database structure first
echo Fixing database structure...
python FIX_DASHBOARD.py

echo.
echo Starting fixed dashboard...
echo Dashboard will open at: http://localhost:8501
echo.

REM Start fixed dashboard
streamlit run FIXED_DASHBOARD.py --server.port 8501