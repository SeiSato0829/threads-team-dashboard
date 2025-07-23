@echo off
echo ========================================
echo 🚨 緊急修復スクリプト - 完全リセット版
echo ========================================
echo.

:: 管理者権限チェック
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ 管理者権限で実行してください！
    echo 右クリック → 「管理者として実行」
    pause
    exit /b 1
)

echo 1️⃣ すべてのNode.jsとPythonプロセスを強制終了中...
taskkill /F /IM node.exe /T 2>nul
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM py.exe /T 2>nul
echo ✅ プロセス終了完了
echo.

echo 2️⃣ ポートを解放中...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000') do (
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do (
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5175') do (
    taskkill /F /PID %%a 2>nul
)
echo ✅ ポート解放完了
echo.

echo 3️⃣ ファイアウォール例外を追加中...
netsh advfirewall firewall add rule name="Threads Auto Post Backend" dir=in action=allow protocol=TCP localport=5000 2>nul
netsh advfirewall firewall add rule name="Threads Auto Post Frontend" dir=in action=allow protocol=TCP localport=5173,5175 2>nul
echo ✅ ファイアウォール設定完了
echo.

echo 4️⃣ キャッシュをクリア中...
rd /s /q node_modules\.vite 2>nul
rd /s /q dist 2>nul
del /q *.log 2>nul
echo ✅ キャッシュクリア完了
echo.

echo ========================================
echo ✅ 修復完了！次のステップへ進みます
echo ========================================
pause