@echo off
echo ========================================
echo   Threads AI自動投稿システム
echo   シンプル起動バージョン
echo ========================================
echo.

cd /d "%~dp0"

echo Pythonのバージョンを確認中...
python --version

echo.
echo システムを起動します...
python test_system.py

pause