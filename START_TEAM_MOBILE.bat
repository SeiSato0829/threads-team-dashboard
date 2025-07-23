@echo off
echo 🚀 チーム&モバイル完全対応 Threads Dashboard 起動中...
echo.

REM 環境設定
set PATH=%PATH%;C:\Users\music-020\.local\bin
cd /d "C:\Users\music-020\threads-auto-post"

echo 📱 モバイル&チーム対応ダッシュボード起動中...
echo.
echo ✅ アクセスURL情報:

REM IPアドレス取得
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%i
    goto :found
)
:found
set IP=%IP: =%

echo 🌐 社内アクセス: http://%IP%:8501
echo 📱 モバイルアクセス: 上記URLをスマホで開く
echo 👥 チームアクセス: 同じネットワーク内で共有可能
echo.

REM Streamlit起動 (ネットワーク公開)
python -m streamlit run MOBILE_TEAM_DASHBOARD.py --server.address 0.0.0.0 --server.port 8501 --server.headless false

pause