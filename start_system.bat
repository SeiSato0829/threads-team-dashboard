@echo off
REM Threads自動投稿システム - Windows起動スクリプト

echo ============================================================
echo Threads自動投稿システム v3.2 - 完全版
echo ============================================================
echo.

REM 現在のディレクトリを確認
echo 現在のディレクトリ: %cd%
echo.

REM Pythonのバージョンを確認
echo Pythonバージョンを確認中...
python --version
if %errorlevel% neq 0 (
    echo エラー: Pythonがインストールされていません
    pause
    exit /b 1
)

REM Node.jsのバージョンを確認
echo Node.jsバージョンを確認中...
node --version
if %errorlevel% neq 0 (
    echo エラー: Node.jsがインストールされていません
    pause
    exit /b 1
)

REM 必要なファイルの存在確認
echo 必要なファイルを確認中...
if not exist "complete_backend_server_final.py" (
    echo エラー: complete_backend_server_final.py が見つかりません
    pause
    exit /b 1
)

if not exist "package.json" (
    echo エラー: package.json が見つかりません
    pause
    exit /b 1
)

if not exist "node_modules" (
    echo Node.js依存関係をインストール中...
    npm install
    if %errorlevel% neq 0 (
        echo エラー: npm install に失敗しました
        pause
        exit /b 1
    )
)

REM Python依存関係の確認
echo Python依存関係を確認中...
python -c "import flask, flask_cors, anthropic, requests, pandas, schedule" 2>nul
if %errorlevel% neq 0 (
    echo Python依存関係をインストール中...
    pip install flask flask-cors anthropic requests pandas schedule
    if %errorlevel% neq 0 (
        echo エラー: Python依存関係のインストールに失敗しました
        pause
        exit /b 1
    )
)

echo.
echo 起動スクリプトを実行中...
python start_system.py

echo.
echo システムが終了しました
pause