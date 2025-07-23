@echo off
echo ========================================
echo   必要なパッケージをインストール
echo ========================================
echo.

cd /d %~dp0

echo Streamlitをインストール中...
pip install streamlit

echo.
echo その他の必要なパッケージをインストール中...
pip install -r requirements_ultimate.txt

echo.
echo ========================================
echo   インストール完了！
echo ========================================
echo.
pause