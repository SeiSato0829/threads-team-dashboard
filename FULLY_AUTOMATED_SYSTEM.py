#!/usr/bin/env python3
"""
🚀 完全自動化Threadsシステム - 投稿予約まで100%自動実行
生成 → データベース保存 → Threads自動予約 → スケジューラー設定
"""

import os
import json
import asyncio
import time
import sqlite3
import logging
import schedule
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import subprocess
import sys

# Seleniumを使用したThreads自動投稿
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# 既存のマルチポストエンジンを継承
try:
    from MULTIPLE_POSTS_PER_DAY import MultiPostAIEngine, MultiPostScheduler
    MULTIPOST_AVAILABLE = True
except ImportError:
    MULTIPOST_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('threads_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class AutomationConfig:
    """完全自動化設定"""
    threads_username: str = ""
    threads_password: str = ""
    posts_per_day: int = 4
    auto_schedule_days: int = 7
    browser_headless: bool = False
    retry_attempts: int = 3
    delay_between_posts: int = 30  # 秒
    
class ThreadsAutomator:
    """Threads完全自動化クラス"""
    
    def __init__(self, config: AutomationConfig):
        self.config = config
        self.driver = None
        self.wait = None
        
    def setup_browser(self):
        """ブラウザ設定"""
        if not SELENIUM_AVAILABLE:
            logger.error("Seleniumが利用できません。pip install selenium を実行してください")
            return False
            
        try:
            options = Options()
            if self.config.browser_headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # User-Agentを設定
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 20)
            
            logger.info("ブラウザを起動しました")
            return True
            
        except Exception as e:
            logger.error(f"ブラウザ起動エラー: {e}")
            return False
    
    def login_to_threads(self) -> bool:
        """Threadsにログイン"""
        try:
            logger.info("Threadsにログイン中...")
            self.driver.get("https://threads.net")
            time.sleep(3)
            
            # ログインボタンを探す
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/login')]"))
            )
            login_button.click()
            time.sleep(2)
            
            # ユーザー名入力
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys(self.config.threads_username)
            time.sleep(1)
            
            # パスワード入力
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.send_keys(self.config.threads_password)
            time.sleep(1)
            
            # ログインボタンクリック
            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            time.sleep(5)
            
            # ログイン成功確認
            if "threads.net" in self.driver.current_url and "/login" not in self.driver.current_url:
                logger.info("ログインに成功しました")
                return True
            else:
                logger.error("ログインに失敗しました")
                return False
                
        except Exception as e:
            logger.error(f"ログインエラー: {e}")
            return False
    
    def schedule_post(self, content: str, scheduled_time: datetime) -> bool:
        """投稿をスケジュール"""
        try:
            logger.info(f"投稿をスケジュール中: {scheduled_time}")
            
            # 新規投稿ボタンをクリック
            compose_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, '新しいスレッド')]"))
            )
            compose_button.click()
            time.sleep(2)
            
            # 投稿内容入力
            textarea = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='新しいスレッドを開始...']"))
            )
            textarea.clear()
            textarea.send_keys(content)
            time.sleep(2)
            
            # その他のオプションボタン（三点メニュー）
            more_options = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='その他のオプション']"))
            )
            more_options.click()
            time.sleep(1)
            
            # スケジュールオプション選択
            schedule_option = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'スケジュール')]"))
            )
            schedule_option.click()
            time.sleep(2)
            
            # 日時設定
            self._set_schedule_datetime(scheduled_time)
            
            # スケジュール確定
            confirm_schedule = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'スケジュール')]"))
            )
            confirm_schedule.click()
            time.sleep(3)
            
            logger.info(f"投稿スケジュールが完了しました: {scheduled_time}")
            return True
            
        except Exception as e:
            logger.error(f"投稿スケジュールエラー: {e}")
            return False
    
    def _set_schedule_datetime(self, target_time: datetime):
        """スケジュール日時を設定"""
        try:
            # 日付設定
            date_input = self.driver.find_element(By.XPATH, "//input[@type='date']")
            date_input.clear()
            date_input.send_keys(target_time.strftime("%Y-%m-%d"))
            
            # 時間設定
            time_input = self.driver.find_element(By.XPATH, "//input[@type='time']")
            time_input.clear()
            time_input.send_keys(target_time.strftime("%H:%M"))
            
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"日時設定エラー: {e}")
    
    def close_browser(self):
        """ブラウザを閉じる"""
        if self.driver:
            self.driver.quit()
            logger.info("ブラウザを閉じました")

class FullyAutomatedSystem:
    """完全自動化システム統合クラス"""
    
    def __init__(self):
        self.config = AutomationConfig()
        self.ai_engine = None
        self.scheduler = None
        self.automator = None
        
        # 設定ファイル読み込み
        self._load_config()
        
        # コンポーネント初期化
        if MULTIPOST_AVAILABLE:
            self.ai_engine = MultiPostAIEngine()
            self.scheduler = MultiPostScheduler()
        
    def _load_config(self):
        """設定ファイル読み込み"""
        config_file = "automation_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    
                self.config.threads_username = config_data.get("threads_username", "")
                self.config.threads_password = config_data.get("threads_password", "")
                self.config.posts_per_day = config_data.get("posts_per_day", 4)
                self.config.auto_schedule_days = config_data.get("auto_schedule_days", 7)
                self.config.browser_headless = config_data.get("browser_headless", False)
                
            except Exception as e:
                logger.error(f"設定ファイル読み込みエラー: {e}")
    
    def _save_config(self):
        """設定ファイル保存"""
        config_data = {
            "threads_username": self.config.threads_username,
            "threads_password": self.config.threads_password,
            "posts_per_day": self.config.posts_per_day,
            "auto_schedule_days": self.config.auto_schedule_days,
            "browser_headless": self.config.browser_headless
        }
        
        with open("automation_config.json", 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
    
    def setup_initial_config(self):
        """初期設定セットアップ"""
        print("""
        ╔════════════════════════════════════════════════════╗
        ║  🚀 完全自動化システム - 初期設定                 ║
        ║     投稿生成からスケジュール予約まで100%自動       ║
        ╚════════════════════════════════════════════════════╝
        """)
        
        print("\n⚙️ Threads認証情報を設定してください:")
        self.config.threads_username = input("Threadsユーザー名: ")
        self.config.threads_password = input("Threadsパスワード: ")
        
        print(f"\n📊 投稿設定:")
        try:
            self.config.posts_per_day = int(input(f"1日の投稿数 (現在: {self.config.posts_per_day}): ") or self.config.posts_per_day)
            self.config.auto_schedule_days = int(input(f"自動化する日数 (現在: {self.config.auto_schedule_days}): ") or self.config.auto_schedule_days)
        except ValueError:
            pass
        
        headless_choice = input(f"ブラウザを非表示で実行? (y/n, 現在: {'y' if self.config.browser_headless else 'n'}): ")
        if headless_choice.lower() == 'y':
            self.config.browser_headless = True
        elif headless_choice.lower() == 'n':
            self.config.browser_headless = False
        
        # 設定保存
        self._save_config()
        print("✅ 設定が保存されました")
    
    async def run_full_automation(self):
        """完全自動化実行"""
        logger.info("完全自動化システムを開始します")
        
        try:
            # 1. 投稿コンテンツ生成
            logger.info("投稿コンテンツを生成中...")
            all_posts = []
            
            for day in range(self.config.auto_schedule_days):
                target_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=day)
                daily_posts = await self.ai_engine.generate_daily_posts(self.config.posts_per_day, target_date)
                
                # データベースに保存
                post_ids = self.scheduler.save_daily_posts(daily_posts, target_date)
                all_posts.extend(daily_posts)
                
                logger.info(f"✅ {target_date.strftime('%m/%d')} - {self.config.posts_per_day}投稿完了")
            
            # 2. Threads自動予約
            logger.info("Threads自動予約を開始...")
            self.automator = ThreadsAutomator(self.config)
            
            if not self.automator.setup_browser():
                raise Exception("ブラウザ起動に失敗")
            
            if not self.automator.login_to_threads():
                raise Exception("Threadsログインに失敗")
            
            # 各投稿をスケジュール
            success_count = 0
            for i, post in enumerate(all_posts):
                try:
                    success = self.automator.schedule_post(
                        post['content'], 
                        post['scheduled_time']
                    )
                    
                    if success:
                        success_count += 1
                        logger.info(f"✅ 投稿 {i+1}/{len(all_posts)} スケジュール完了")
                    else:
                        logger.error(f"❌ 投稿 {i+1}/{len(all_posts)} スケジュール失敗")
                    
                    # 投稿間の遅延
                    time.sleep(self.config.delay_between_posts)
                    
                except Exception as e:
                    logger.error(f"投稿 {i+1} スケジュールエラー: {e}")
            
            # 3. 結果レポート
            total_posts = len(all_posts)
            logger.info(f"🎉 完全自動化完了!")
            logger.info(f"📊 結果: {success_count}/{total_posts} 投稿がスケジュール済み")
            
            if success_count == total_posts:
                logger.info("🏆 100%の投稿が自動予約されました!")
            else:
                logger.warning(f"⚠️ {total_posts - success_count}件の投稿で問題が発生しました")
            
            # CSVエクスポート
            csv_file = self.scheduler.export_schedule(self.config.auto_schedule_days)
            logger.info(f"📄 詳細レポート: {csv_file}")
            
        except Exception as e:
            logger.error(f"完全自動化エラー: {e}")
        
        finally:
            if self.automator:
                self.automator.close_browser()
    
    def setup_windows_scheduler(self):
        """Windowsタスクスケジューラー設定"""
        print("\n🕐 定期実行スケジュールを設定しますか？")
        setup_choice = input("Windowsタスクスケジューラーに登録? (y/n): ")
        
        if setup_choice.lower() != 'y':
            return
        
        script_path = os.path.abspath(__file__)
        python_path = sys.executable
        
        # バッチファイル作成
        batch_content = f"""@echo off
cd /d "{os.path.dirname(script_path)}"
"{python_path}" "{script_path}" --auto-run
"""
        
        batch_file = "auto_threads_scheduler.bat"
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        
        print(f"✅ バッチファイルを作成: {batch_file}")
        print(f"📝 Windowsタスクスケジューラーで以下を設定してください:")
        print(f"   プログラム: {os.path.abspath(batch_file)}")
        print(f"   頻度: 毎日または毎週")
        print(f"   実行時刻: お好みの時間")

def main():
    """メイン実行"""
    system = FullyAutomatedSystem()
    
    # コマンドライン引数チェック
    if len(sys.argv) > 1 and sys.argv[1] == "--auto-run":
        # 自動実行モード
        asyncio.run(system.run_full_automation())
        return
    
    # 対話的セットアップ
    if not SELENIUM_AVAILABLE:
        print("❌ Seleniumが必要です。以下のコマンドを実行してください:")
        print("pip install selenium")
        print("また、ChromeDriverが必要です。")
        return
    
    if not MULTIPOST_AVAILABLE:
        print("❌ MULTIPLE_POSTS_PER_DAY.pyが必要です。")
        return
    
    print("🚀 完全自動化システムへようこそ！")
    
    # 初期設定
    system.setup_initial_config()
    
    # 実行選択
    print(f"\n📋 実行オプション:")
    print("  1. 🔥 今すぐ完全自動化実行")
    print("  2. ⏰ 定期実行スケジュール設定")
    print("  3. ⚙️ 設定変更")
    
    choice = input("\n選択 (1-3): ")
    
    if choice == "1":
        asyncio.run(system.run_full_automation())
    elif choice == "2":
        system.setup_windows_scheduler()
    elif choice == "3":
        system.setup_initial_config()

if __name__ == "__main__":
    main()