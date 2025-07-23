@echo off
echo 🚀 Threads自動投稿システム - バックエンドサーバー起動中...
echo.

cd /d "%~dp0"

:: Python実行可能ファイルを探す
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    where python3 >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python3
    ) else (
        where py >nul 2>&1
        if %errorlevel% equ 0 (
            set PYTHON_CMD=py
        ) else (
            echo ❌ エラー: Pythonが見つかりません
            echo Pythonをインストールしてください: https://www.python.org/downloads/
            pause
            exit /b 1
        )
    )
)

echo ✅ Python実行環境: %PYTHON_CMD%
echo.

:: 依存関係をインストール
echo 📦 必要なパッケージをインストール中...
%PYTHON_CMD% -m pip install -r requirements_python.txt
if %errorlevel% neq 0 (
    echo.
    echo ⚠️ pipが見つかりません。インストールします...
    %PYTHON_CMD% -m ensurepip --default-pip
    %PYTHON_CMD% -m pip install --upgrade pip
    %PYTHON_CMD% -m pip install -r requirements_python.txt
)

echo.
echo ✅ パッケージインストール完了
echo.

:: バックエンドサーバーを起動
echo 🌐 バックエンドサーバーを起動中...
echo URL: http://localhost:5000
echo.
echo 停止するには Ctrl+C を押してください
echo.

%PYTHON_CMD% complete_backend_server_final.py

pause