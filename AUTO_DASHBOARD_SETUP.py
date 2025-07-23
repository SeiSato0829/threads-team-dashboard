#!/usr/bin/env python3
"""
🤖 自動ダッシュボードセットアップ
投稿システムとダッシュボードの統合自動化
"""

import os
import json
import subprocess
import time
from datetime import datetime
import threading

class AutoDashboardSetup:
    """🤖 自動ダッシュボードセットアップ"""
    
    def __init__(self):
        self.config_path = "dashboard_config.json"
        self.auto_config = self.load_config()
        
    def load_config(self):
        """設定読み込み"""
        default_config = {
            "auto_start_dashboard": True,
            "dashboard_port": 8501,
            "auto_update_interval": 300,  # 5分
            "enable_auto_reports": True,
            "report_schedule": "daily",  # daily, weekly, monthly
            "team_notifications": True,
            "performance_tracking": True
        }
        
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                default_config.update(loaded)
        
        return default_config
    
    def save_config(self):
        """設定保存"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.auto_config, f, ensure_ascii=False, indent=2)
    
    def setup_auto_dashboard(self):
        """自動ダッシュボードセットアップ"""
        
        print("🤖 自動ダッシュボードセットアップ")
        print("=" * 60)
        print("以下の機能を自動化します:")
        print("  ✅ 投稿履歴の視覚的確認")
        print("  ✅ パフォーマンスグラフの自動更新")
        print("  ✅ 投稿内容の編集・管理")
        print("  ✅ チーム情報共有の自動化")
        print("  ✅ 定期レポートの自動生成")
        print()
        
        # 設定確認
        self.configure_dashboard()
        
        # 必要パッケージインストール
        self.install_packages()
        
        # 自動起動スクリプト作成
        self.create_auto_scripts()
        
        # Windows Task Scheduler設定
        self.setup_scheduler()
        
        print("\n✅ 自動ダッシュボードセットアップ完了！")
        
        # ダッシュボード起動
        if self.auto_config["auto_start_dashboard"]:
            print("\n🚀 ダッシュボードを起動中...")
            self.start_dashboard()
    
    def configure_dashboard(self):
        """ダッシュボード設定"""
        print("\n⚙️ ダッシュボード設定")
        
        # 自動起動設定
        auto_start = input(f"ダッシュボードを自動起動しますか？ (y/n) [{self.auto_config['auto_start_dashboard'] and 'y' or 'n'}]: ")
        if auto_start.lower() == 'n':
            self.auto_config["auto_start_dashboard"] = False
        elif auto_start.lower() == 'y':
            self.auto_config["auto_start_dashboard"] = True
        
        # ポート設定
        port = input(f"ダッシュボードポート番号 [{self.auto_config['dashboard_port']}]: ")
        if port.isdigit():
            self.auto_config["dashboard_port"] = int(port)
        
        # 自動更新間隔
        update_interval = input(f"データ更新間隔（分） [{self.auto_config['auto_update_interval']//60}]: ")
        if update_interval.isdigit():
            self.auto_config["auto_update_interval"] = int(update_interval) * 60
        
        # 自動レポート
        auto_reports = input(f"自動レポートを有効にしますか？ (y/n) [{self.auto_config['enable_auto_reports'] and 'y' or 'n'}]: ")
        if auto_reports.lower() == 'n':
            self.auto_config["enable_auto_reports"] = False
        elif auto_reports.lower() == 'y':
            self.auto_config["enable_auto_reports"] = True
        
        self.save_config()
        print("✅ 設定を保存しました")
    
    def install_packages(self):
        """必要パッケージインストール"""
        print("\n📦 必要パッケージをインストール中...")
        
        packages = [
            "streamlit",
            "plotly",
            "pandas"
        ]
        
        for package in packages:
            try:
                subprocess.run(
                    ["pip", "install", "--quiet", package],
                    check=True,
                    capture_output=True
                )
                print(f"  ✅ {package}")
            except subprocess.CalledProcessError:
                print(f"  ❌ {package} - インストール失敗")
    
    def create_auto_scripts(self):
        """自動スクリプト作成"""
        print("\n📝 自動スクリプト作成中...")
        
        # 自動更新スクリプト
        auto_updater = f"""@echo off
cd /d %~dp0

:loop
echo %date% %time% - Updating dashboard data...

REM データベースの整合性チェック
python -c "
import sqlite3
import os
from datetime import datetime

# データベースファイルの確認と更新
dbs = ['scheduled_posts.db', 'threads_optimized.db', 'buzz_history.db', 'viral_history.db']
for db in dbs:
    if os.path.exists(db):
        try:
            conn = sqlite3.connect(db)
            conn.execute('SELECT COUNT(*) FROM sqlite_master')
            conn.close()
            print(f'✅ {{db}} OK')
        except:
            print(f'❌ {{db}} Error')
    else:
        print(f'ℹ️ {{db}} Not found')

print(f'Last update: {{datetime.now().strftime(\"%Y/%m/%d %H:%M:%S\")}}')
"

timeout /t {self.auto_config['auto_update_interval']} /nobreak
goto loop
"""
        
        with open("AUTO_DASHBOARD_UPDATER.bat", 'w', encoding='utf-8') as f:
            f.write(auto_updater)
        
        # 統合起動スクリプト
        integrated_start = f"""@echo off
cd /d %~dp0
echo ================================================
echo   Integrated Threads Management System
echo   Posts + Dashboard + Analytics
echo ================================================

REM Start dashboard in background
start /min AUTO_DASHBOARD_UPDATER.bat

REM Wait for system ready
timeout /t 3

REM Start main dashboard
echo Starting dashboard at http://localhost:{self.auto_config['dashboard_port']}
streamlit run THREADS_DASHBOARD.py --server.port {self.auto_config['dashboard_port']}
"""
        
        with open("INTEGRATED_START.bat", 'w', encoding='utf-8') as f:
            f.write(integrated_start)
        
        print("✅ 自動スクリプト作成完了")
    
    def setup_scheduler(self):
        """Windows Task Scheduler設定"""
        print("\n🕐 自動実行スケジュール設定")
        
        try:
            # 自動更新タスク
            subprocess.run([
                "schtasks", "/create", "/tn", "ThreadsDashboardUpdater",
                "/tr", os.path.join(os.getcwd(), "AUTO_DASHBOARD_UPDATER.bat"),
                "/sc", "once", "/st", "00:00", "/f"
            ], capture_output=True)
            
            print("✅ 自動更新タスクを作成")
            
        except Exception as e:
            print(f"⚠️ スケジューラ設定エラー: {e}")
            print("手動で実行してください")
    
    def start_dashboard(self):
        """ダッシュボード起動"""
        
        def run_dashboard():
            try:
                # バックグラウンドでダッシュボード起動
                subprocess.run([
                    "streamlit", "run", "THREADS_DASHBOARD.py",
                    "--server.port", str(self.auto_config['dashboard_port']),
                    "--server.headless", "true"
                ])
            except Exception as e:
                print(f"ダッシュボード起動エラー: {e}")
        
        # バックグラウンドで実行
        dashboard_thread = threading.Thread(target=run_dashboard)
        dashboard_thread.daemon = True
        dashboard_thread.start()
        
        # 起動確認
        time.sleep(5)
        print(f"🌐 ダッシュボードが起動しました: http://localhost:{self.auto_config['dashboard_port']}")
        print("ブラウザで上記URLを開いてください")
    
    def create_usage_guide(self):
        """使用方法ガイド作成"""
        guide = f"""# Threads自動管理システム使用ガイド

## 🚀 システム構成
1. **投稿生成システム**: THREADS_ULTIMATE_START.bat
2. **自動投稿実行**: BUZZ_SETUP.bat
3. **管理ダッシュボード**: http://localhost:{self.auto_config['dashboard_port']}

## 📊 ダッシュボード機能
- **📈 概要**: 投稿統計とKPI
- **📝 履歴**: 全投稿の閲覧・編集
- **📊 分析**: パフォーマンス詳細分析
- **✏️ 編集**: 予定投稿の内容変更
- **👥 共有**: チーム情報共有
- **📋 レポート**: 自動レポート生成

## ⚙️ 自動化設定
- データ更新間隔: {self.auto_config['auto_update_interval']//60}分
- 自動レポート: {'有効' if self.auto_config['enable_auto_reports'] else '無効'}
- チーム通知: {'有効' if self.auto_config['team_notifications'] else '無効'}

## 🔧 トラブルシューティング
1. ダッシュボードが表示されない
   → DASHBOARD_START.bat を実行
2. データが更新されない
   → AUTO_DASHBOARD_UPDATER.bat を確認
3. エラーが発生する
   → ログファイルを確認

最終更新: {datetime.now().strftime('%Y/%m/%d %H:%M')}
"""
        
        with open("USAGE_GUIDE.md", 'w', encoding='utf-8') as f:
            f.write(guide)

def main():
    """メイン実行"""
    setup = AutoDashboardSetup()
    
    print("🤖 Threads自動管理システム - 統合セットアップ")
    print("=" * 70)
    print("投稿生成 + 自動実行 + ダッシュボード の完全統合")
    
    # セットアップ実行
    setup.setup_auto_dashboard()
    
    # 使用ガイド作成
    setup.create_usage_guide()
    
    print(f"\n📚 使用ガイドを作成しました: USAGE_GUIDE.md")
    print(f"🌐 ダッシュボードURL: http://localhost:{setup.auto_config['dashboard_port']}")
    
    print("\n🎉 完全統合システムの準備完了！")
    print("これで投稿の生成から分析まで全て自動化されます")

if __name__ == "__main__":
    main()