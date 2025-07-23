@echo off
chcp 65001 >nul
cls

echo.
echo ╔══════════════════════════════════════════╗
echo ║   🚀 究極のThreads収益最大化システム    ║
echo ║          2025 Ultimate Edition           ║
echo ╚══════════════════════════════════════════╝
echo.

REM Pythonがインストールされているかチェック
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Pythonがインストールされていません！
    echo    https://www.python.org/ からインストールしてください。
    pause
    exit /b 1
)

REM ワンクリック起動
echo 🚀 システムを起動します...
python ONE_CLICK_START.py

pause