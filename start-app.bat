@echo off
echo.
echo ======================================
echo   Threads 自動投稿システム v3.2
echo ======================================
echo.
echo アプリケーションを起動中...
echo.

cd /d "%~dp0"

where python >nul 2>&1
if %errorlevel% equ 0 (
    echo Pythonサーバーで起動します...
    cd dist
    start http://localhost:8000
    python -m http.server 8000
) else (
    where npx >nul 2>&1
    if %errorlevel% equ 0 (
        echo Node.jsサーバーで起動します...
        start http://localhost:8080
        npx serve dist
    ) else (
        echo.
        echo 警告: PythonもNode.jsも見つかりません。
        echo distフォルダ内のindex.htmlを直接開いてください。
        echo.
        start "" "%~dp0dist\index.html"
        pause
    )
)