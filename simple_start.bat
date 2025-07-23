@echo off
cd /d %~dp0

echo ========================================
echo   Threads AI 自動投稿システム
echo   シンプル起動
echo ========================================
echo.

echo 必要なパッケージをインストール中...
pip install streamlit fastapi uvicorn aiohttp pandas numpy scikit-learn plotly python-dotenv anthropic openai

echo.
echo システムを起動します...
python simple_auto_post.py

pause