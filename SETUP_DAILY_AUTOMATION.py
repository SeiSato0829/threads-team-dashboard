#!/usr/bin/env python3
"""
⚙️ 毎日自動投稿セットアップ - Windows Task Scheduler設定
"""

import os
import sys
import json
import subprocess
from datetime import datetime, time

class DailyAutomationSetup:
    """毎日自動投稿セットアップ"""
    
    def __init__(self):
        self.task_name = "ThreadsAutoPost"
        self.script_path = os.path.join(os.getcwd(), "DAILY_AUTO_POST_ENGINE.py")
        self.bat_path = os.path.join(os.getcwd(), "RUN_DAILY_POST.bat")
        self.config_path = "auto_post_config.json"
    
    def setup(self):
        """セットアップメイン処理"""
        print("⚙️ 毎日自動投稿セットアップ")
        print("=" * 60)
        print("このセットアップで以下を設定します：")
        print("1. 毎日指定時間に自動実行")
        print("2. 投稿生成・投稿実行")
        print("3. エラー時の自動リトライ")
        print()
        
        # 1. 設定確認
        self._configure_settings()
        
        # 2. バッチファイル作成
        self._create_batch_file()
        
        # 3. タスクスケジューラ設定
        self._setup_task_scheduler()
        
        print("\n✅ セットアップ完了！")
        print("毎日自動的に投稿が実行されます")
    
    def _configure_settings(self):
        """設定確認と作成"""
        print("📋 設定確認")
        
        # デフォルト設定
        config = {
            "posts_per_day": 5,
            "posting_times": ["08:00", "12:00", "19:00", "21:00", "23:00"],
            "generate_days_ahead": 3,
            "retry_attempts": 3,
            "retry_delay": 300,
            "threads_login_url": "https://threads.net/login",
            "headless_mode": False,
            "execution_times": ["07:00", "11:00", "18:00", "20:00", "22:00"]  # 実行時間
        }
        
        # 既存設定があれば読み込み
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
                config.update(existing_config)
        
        print(f"投稿数/日: {config['posts_per_day']}")
        print(f"投稿時間: {', '.join(config['posting_times'])}")
        print(f"実行時間: {', '.join(config['execution_times'])}")
        
        # カスタマイズ確認
        customize = input("\n設定を変更しますか？ (y/n): ")
        if customize.lower() == 'y':
            # 投稿数
            posts_per_day = input(f"1日の投稿数 [{config['posts_per_day']}]: ")
            if posts_per_day:
                config['posts_per_day'] = int(posts_per_day)
            
            # 投稿時間
            print("\n投稿時間を入力（カンマ区切り、例: 08:00,12:00,19:00）")
            posting_times = input(f"投稿時間 [{','.join(config['posting_times'])}]: ")
            if posting_times:
                config['posting_times'] = [t.strip() for t in posting_times.split(',')]
            
            # 実行時間（投稿時間の1時間前に設定）
            config['execution_times'] = []
            for ptime in config['posting_times']:
                hour, minute = map(int, ptime.split(':'))
                exec_hour = hour - 1 if hour > 0 else 23
                config['execution_times'].append(f"{exec_hour:02d}:{minute:02d}")
        
        # 設定保存
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print("\n✅ 設定を保存しました")
        self.config = config
    
    def _create_batch_file(self):
        """実行用バッチファイル作成"""
        print("\n📝 バッチファイル作成中...")
        
        batch_content = f"""@echo off
cd /d %~dp0
echo ================================================
echo   Threads Auto Post - Daily Execution
echo   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
echo ================================================
echo.

REM Python環境確認
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM 必要なパッケージインストール（初回のみ）
pip install --quiet selenium pyperclip

REM ログディレクトリ作成
if not exist "logs" mkdir logs

REM 実行時刻を記録
echo Execution started at %date% %time% >> logs\\execution.log

REM メイン処理実行
echo Starting auto post engine...
python DAILY_AUTO_POST_ENGINE.py --execute

REM 実行結果確認
if errorlevel 1 (
    echo ERROR: Execution failed >> logs\\execution.log
    REM エラー時は5分後にリトライ
    timeout /t 300 /nobreak
    python DAILY_AUTO_POST_ENGINE.py --execute
) else (
    echo SUCCESS: Execution completed >> logs\\execution.log
)

REM ウィンドウを閉じる
exit
"""
        
        with open(self.bat_path, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        
        print("✅ バッチファイルを作成しました")
    
    def _setup_task_scheduler(self):
        """Windows Task Scheduler設定"""
        print("\n🕐 タスクスケジューラ設定")
        
        # 既存タスク削除
        try:
            subprocess.run(
                f'schtasks /delete /tn "{self.task_name}" /f',
                shell=True,
                capture_output=True
            )
        except:
            pass
        
        # 各実行時間に対してタスクを作成
        for i, exec_time in enumerate(self.config['execution_times']):
            task_name = f"{self.task_name}_{i+1}"
            
            # タスク作成コマンド
            create_command = f'''schtasks /create /tn "{task_name}" /tr "{self.bat_path}" /sc daily /st {exec_time} /f'''
            
            try:
                result = subprocess.run(
                    create_command,
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print(f"✅ タスク作成成功: {exec_time}")
                else:
                    print(f"❌ タスク作成失敗: {exec_time}")
                    print(f"   エラー: {result.stderr}")
            
            except Exception as e:
                print(f"❌ エラー: {e}")
        
        # 手動設定の案内
        print("\n📌 追加の推奨設定:")
        print("1. タスクスケジューラを開く（taskschd.msc）")
        print(f"2. 作成されたタスク（{self.task_name}_*）を右クリック→プロパティ")
        print("3. 「条件」タブ:")
        print("   - 「コンピューターをAC電源で...」のチェックを外す")
        print("   - 「スリープを解除して...」にチェック")
        print("4. 「設定」タブ:")
        print("   - 「タスクを停止するまでの時間」を「1時間」に設定")
        print("   - 「要求時に実行中のタスクが終了しない場合...」にチェック")
    
    def test_execution(self):
        """テスト実行"""
        print("\n🧪 テスト実行")
        print("今すぐテスト実行しますか？")
        
        test = input("テスト実行 (y/n): ")
        if test.lower() == 'y':
            print("\nテスト実行中...")
            subprocess.run([sys.executable, self.script_path, "--execute"])

def main():
    """メイン処理"""
    print("🤖 Threads毎日自動投稿 - セットアップウィザード")
    print("=" * 70)
    
    setup = DailyAutomationSetup()
    
    # セットアップ実行
    setup.setup()
    
    # テスト実行
    setup.test_execution()
    
    print("\n🎉 セットアップ完了！")
    print("以下の時間に自動実行されます:")
    for exec_time in setup.config['execution_times']:
        print(f"  - {exec_time}")
    
    print("\n💡 ヒント:")
    print("- ログは logs/daily_auto_post.log で確認できます")
    print("- 手動実行: RUN_DAILY_POST.bat をクリック")
    print("- 設定変更: auto_post_config.json を編集")

if __name__ == "__main__":
    main()