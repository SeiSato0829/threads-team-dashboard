@echo off
echo ============================================
echo 🚀 Threads自動投稿システム - 完全起動版
echo ============================================
echo.

:: 現在のディレクトリに移動
cd /d "%~dp0"

:: Python検出
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
    ) else (
        echo ❌ Pythonが見つかりません！
        echo https://www.python.org/downloads/ からインストールしてください
        pause
        exit /b 1
    )
)

echo ✅ Python: %PYTHON_CMD%
echo.

:: 依存関係チェック
echo 📦 依存関係を確認中...
%PYTHON_CMD% -m pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo Flask がインストールされていません。インストール中...
    %PYTHON_CMD% -m pip install flask flask-cors anthropic requests pandas schedule werkzeug python-dotenv
)

:: NPMチェック
npm -v >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.jsが見つかりません！
    echo https://nodejs.org/ からインストールしてください
    pause
    exit /b 1
)

:: バックエンドを新しいウィンドウで起動
echo.
echo 🌐 バックエンドサーバーを起動中...
start "Backend Server - Port 5000" cmd /k "%PYTHON_CMD% complete_backend_server_final.py"

:: 3秒待機
timeout /t 3 /nobreak >nul

:: API接続テスト
echo.
echo 🔍 API接続をテスト中...
curl -s http://localhost:5000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ バックエンドサーバー: 正常起動
) else (
    echo ⚠️ バックエンドサーバーの起動を待機中...
    timeout /t 5 /nobreak >nul
)

:: フロントエンドを新しいウィンドウで起動
echo.
echo 🎨 フロントエンドサーバーを起動中...
start "Frontend Server - Port 5173/5175" cmd /k "npm run dev"

:: 5秒待機
echo.
echo ⏳ システム起動中... (5秒)
timeout /t 5 /nobreak >nul

:: ブラウザを開く
echo.
echo 🌏 ブラウザを開いています...
start http://localhost:5173
timeout /t 2 /nobreak >nul
start http://localhost:5175

echo.
echo ============================================
echo ✅ システム起動完了！
echo ============================================
echo.
echo 📍 アクセスURL:
echo    - http://localhost:5173
echo    - http://localhost:5175
echo.
echo 📍 実行中のサーバー:
echo    - バックエンド: http://localhost:5000
echo    - フロントエンド: 上記URL
echo.
echo 🛑 停止方法:
echo    各ウィンドウで Ctrl+C を押す
echo ============================================
echo.
pause