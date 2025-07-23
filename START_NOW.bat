@echo off
chcp 932
cd /d %~dp0

echo.
echo =====================================
echo   Threads AI System - Quick Start
echo =====================================
echo.

echo Python check...
python --version

echo.
echo Starting test system...
python test_system.py

echo.
echo Press any key to continue...
pause >nul

echo.
echo Starting auto post demo...
python simple_auto_post.py

pause