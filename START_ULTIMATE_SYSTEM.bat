@echo off
echo ========================================
echo   究極のThreads AI自動投稿システム
echo   限界を超えた完全自動化を実現！
echo ========================================
echo.

REM Python仮想環境をアクティベート
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Python仮想環境が見つかりません。セットアップを実行してください。
    pause
    exit /b 1
)

REM 必要なパッケージをインストール
echo [1/4] 必要なパッケージをインストール中...
pip install -r requirements_ai.txt >nul 2>&1

REM データベースをセットアップ
echo [2/4] データベースを初期化中...
python -c "from ultimate_ai_post_engine import UltimateThreadsAIEngine; engine = UltimateThreadsAIEngine(); import sqlite3; conn = sqlite3.connect('threads_auto_post.db'); conn.close()"

REM 各システムを起動
echo [3/4] システムを起動中...
echo.

REM 1. リアルタイムエンゲージメントトラッカー
echo ⚡ リアルタイムエンゲージメントトラッカーを起動...
start /min cmd /c "python realtime_engagement_tracker.py"

REM 2. AI投稿生成エンジン
echo 🤖 AI投稿生成エンジンを起動...
start /min cmd /c "python ultimate_ai_post_engine.py"

REM 3. 自動投稿スケジューラー
echo 📅 自動投稿スケジューラーを起動...
start /min cmd /c "python auto_post_scheduler.py"

REM 4. 既存のバックエンドサーバー
echo 🌐 バックエンドサーバーを起動...
start /min cmd /c "python complete_backend_server_final.py"

REM 5. フロントエンド開発サーバー
echo 💻 フロントエンドを起動...
start cmd /c "npm run dev"

echo.
echo [4/4] 起動完了！
echo.
echo ========================================
echo ✨ システムが稼働中です！
echo.
echo 📊 ダッシュボード: http://localhost:5173
echo 🔍 エンゲージメント監視: 30分ごとに自動実行
echo 🤖 AI投稿生成: 毎日6時に自動生成
echo 📅 自動投稿: 最適な時間に自動投稿
echo.
echo 💡 ヒント:
echo - 初回はThreadsのログイン情報を.envファイルに設定してください
echo - 高エンゲージメント投稿は自動的に学習されます
echo - 投稿は1日最大4回、最適な時間に配信されます
echo.
echo 終了するには、このウィンドウを閉じてください。
echo ========================================

timeout /t 5 >nul
start http://localhost:5173

pause