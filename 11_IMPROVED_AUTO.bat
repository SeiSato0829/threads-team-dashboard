@echo off
chcp 65001 >nul
cls

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║  🔧 改良版Threads自動化システム                   ║
echo ║     ログインエラー修正版 - 安定動作保証           ║
echo ╚════════════════════════════════════════════════════╝
echo.

cd /d %~dp0

echo 🔧 ログインエラーを修正しました:
echo   ✅ より確実なログインフィールド検索
echo   ✅ 複数パターンの認証方式に対応
echo   ✅ デバッグ情報の詳細出力
echo   ✅ エラー時のスクリーンショット自動保存
echo.

echo 📦 必要パッケージの確認...
pip install selenium schedule

echo.
echo 🚀 改良版自動化システムを起動中...
python IMPROVED_AUTOMATION.py

echo.
echo 📋 ログとデバッグファイル:
echo   - threads_automation_fixed.log
echo   - debug_*.png (スクリーンショット)
echo   - debug_*.html (ページソース)

pause