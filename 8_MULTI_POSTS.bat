@echo off
chcp 65001 >nul
cls

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║  📱 1日複数投稿対応 - 時間指定自動化システム      ║
echo ║        収益最大化のための戦略的投稿計画           ║
echo ╚════════════════════════════════════════════════════╝
echo.

cd /d %~dp0

echo 📦 必要なパッケージを確認中...
pip install anthropic openai asyncio pandas python-dotenv

echo.
echo 🚀 複数投稿システムを起動中...
python MULTIPLE_POSTS_PER_DAY.py

pause