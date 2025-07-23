@echo off
echo.
echo ======================================
echo   Threads 自動投稿システム v3.2
echo ======================================
echo.
echo 3つの起動方法を提供します：
echo.
echo [1] スタンドアロン版（推奨・確実に動作）
echo [2] ビルド済みReactアプリ
echo [3] ローカルサーバー経由
echo.
set /p choice="選択してください (1-3): "

if "%choice%"=="1" (
    start "" "%~dp0standalone.html"
) else if "%choice%"=="2" (
    start "" "%~dp0dist\index.html"
) else if "%choice%"=="3" (
    call "%~dp0start-app.bat"
) else (
    echo 無効な選択です。スタンドアロン版を開きます...
    timeout /t 2 >nul
    start "" "%~dp0standalone.html"
)