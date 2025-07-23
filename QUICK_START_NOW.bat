@echo off
cd /d %~dp0

echo.
echo =====================================
echo   Threads AI System - Quick Start
echo =====================================
echo.

REM まず動作確認
python test_system.py

echo.
echo 続行しますか？
pause

REM 簡単な自動投稿デモを実行
python simple_auto_post.py

pause