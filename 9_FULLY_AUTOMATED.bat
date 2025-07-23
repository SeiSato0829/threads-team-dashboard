@echo off
chcp 65001 >nul
cls

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║  🚀 完全自動化Threadsシステム - 究極の自動化       ║
echo ║     投稿生成 → 予約設定 → 自動投稿まで100%自動     ║
echo ╚════════════════════════════════════════════════════╝
echo.

cd /d %~dp0

echo 📦 必要パッケージをインストール中...
pip install selenium schedule asyncio

echo.
echo 🔧 ChromeDriverの確認...
python -c "
import subprocess
import sys
import os

def check_chrome_driver():
    try:
        result = subprocess.run(['chromedriver', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print('✅ ChromeDriver が利用可能です')
            print(f'   バージョン: {result.stdout.strip()}')
            return True
    except:
        pass
    
    print('❌ ChromeDriver が見つかりません')
    print('📥 自動ダウンロードを試行中...')
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'webdriver-manager'])
        print('✅ webdriver-manager をインストールしました')
        return True
    except:
        print('❌ 自動インストールに失敗しました')
        print('手動でChromeDriverをダウンロードしてください:')
        print('https://chromedriver.chromium.org/')
        return False

check_chrome_driver()
"

echo.
echo 🚀 完全自動化システムを起動中...
python FULLY_AUTOMATED_SYSTEM.py

pause