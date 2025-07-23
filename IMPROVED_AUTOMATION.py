#!/usr/bin/env python3
"""
🚀 改良版完全自動化Threadsシステム - ログインエラー修正版
より確実なログイン処理とエラー処理の改善
"""

import os
import json
import asyncio
import time
import sqlite3
import logging
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
    from selenium.webdriver.common.action_chains import ActionChains
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
        logging.FileHandler('threads_automation_fixed.log', encoding='utf-8'),
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
    
class ImprovedThreadsAutomator:
    """改良版Threads自動化クラス"""
    
    def __init__(self, config: AutomationConfig):
        self.config = config
        self.driver = None
        self.wait = None
        
    def setup_browser(self):
        """改良版ブラウザ設定"""
        if not SELENIUM_AVAILABLE:
            logger.error("Seleniumが利用できません。pip install selenium を実行してください")
            return False
            
        try:
            options = Options()
            
            # より安定した設定
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # ユーザーエージェント（最新版）
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
            
            # ヘッドレスモード設定
            if self.config.browser_headless:
                options.add_argument("--headless")
            else:
                # デバッグモードでは画面を表示
                options.add_argument("--start-maximized")
            
            # その他の安定性向上設定
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-notifications")
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 30)  # タイムアウトを30秒に延長
            
            logger.info("ブラウザを起動しました")
            return True
            
        except Exception as e:
            logger.error(f"ブラウザ起動エラー: {e}")
            return False
    
    def login_to_threads(self) -> bool:
        """改良版Threadsログイン"""
        try:
            logger.info("Threadsにログイン中...")
            
            # 直接ログインページへ
            self.driver.get("https://www.threads.net/login")
            time.sleep(5)
            
            # ページが完全に読み込まれるまで待機
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            current_url = self.driver.current_url
            logger.info(f"現在のURL: {current_url}")
            
            # すでにログイン済みかチェック
            if "/login" not in current_url:
                logger.info("既にログイン済みです")
                return True
            
            # ログインフィールド検索（複数パターン）
            username_field = None
            password_field = None
            
            # パターン1: 標準的なname属性
            try:
                username_field = self.wait.until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
                password_field = self.driver.find_element(By.NAME, "password")
                logger.info("ログインフィールドをname属性で発見")
            except:
                pass
            
            # パターン2: type属性で検索
            if not username_field:
                try:
                    username_field = self.driver.find_element(By.XPATH, "//input[@type='text']")
                    password_field = self.driver.find_element(By.XPATH, "//input[@type='password']")
                    logger.info("ログインフィールドをtype属性で発見")
                except:
                    pass
            
            # パターン3: aria-label属性
            if not username_field:
                try:
                    username_field = self.driver.find_element(By.XPATH, "//input[@aria-label='ユーザーネーム' or @aria-label='Username']")
                    password_field = self.driver.find_element(By.XPATH, "//input[@aria-label='パスワード' or @aria-label='Password']")
                    logger.info("ログインフィールドをaria-label属性で発見")
                except:
                    pass
            
            # パターン4: 汎用的なinput要素
            if not username_field:
                try:
                    input_elements = self.driver.find_elements(By.TAG_NAME, "input")
                    for element in input_elements:
                        input_type = element.get_attribute("type")
                        if input_type in ["text", "email"] and not username_field:
                            username_field = element
                        elif input_type == "password" and not password_field:
                            password_field = element
                    if username_field and password_field:
                        logger.info("ログインフィールドを汎用検索で発見")
                except:
                    pass
            
            if not username_field or not password_field:
                logger.error("ログインフィールドが見つかりません")
                self._save_debug_screenshot("login_fields_not_found")
                self._save_page_source("login_fields_not_found")
                return False
            
            # ログイン情報入力
            logger.info("認証情報を入力中...")
            username_field.clear()
            username_field.send_keys(self.config.threads_username)
            time.sleep(1)
            
            password_field.clear()
            password_field.send_keys(self.config.threads_password)
            time.sleep(1)
            
            # ログインボタンをクリック
            login_success = False
            
            # パターン1: type="submit"ボタン
            try:
                submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                submit_button.click()
                logger.info("submitボタンでログイン試行")
                login_success = True
            except:
                pass
            
            # パターン2: ログインテキストを含むボタン
            if not login_success:
                try:
                    login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'ログイン') or contains(text(), 'Log in')]")
                    login_button.click()
                    logger.info("テキスト検索でログインボタンをクリック")
                    login_success = True
                except:
                    pass
            
            # パターン3: 汎用的なボタン
            if not login_success:
                try:
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            button.click()
                            logger.info("汎用ボタンでログイン試行")
                            login_success = True
                            break
                except:
                    pass
            
            # パターン4: Enterキーでログイン
            if not login_success:
                try:
                    password_field.send_keys(Keys.RETURN)
                    logger.info("Enterキーでログイン試行")
                    login_success = True
                except:
                    pass
            
            if not login_success:
                logger.error("ログインボタンが見つかりません")
                self._save_debug_screenshot("login_button_not_found")
                return False
            
            # ログイン処理完了まで待機
            time.sleep(10)
            
            # ログイン成功確認
            current_url = self.driver.current_url
            logger.info(f"ログイン後のURL: {current_url}")
            
            # 成功パターンをチェック
            success_indicators = [
                "/login" not in current_url and "threads.net" in current_url,
                "threads.net/@" in current_url,
                "threads.net/home" in current_url
            ]
            
            # 追加確認：プロフィールボタンの存在
            try:
                profile_elements = self.driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'プロフィール') or contains(@aria-label, 'Profile')]")
                if profile_elements:
                    success_indicators.append(True)
            except:
                pass
            
            if any(success_indicators):
                logger.info("✅ ログインに成功しました")
                self._save_debug_screenshot("login_success")
                return True
            else:
                # エラーメッセージをチェック
                try:
                    error_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'エラー') or contains(text(), 'error') or contains(text(), '無効')]")
                    if error_elements:
                        logger.error(f"ログインエラー: {error_elements[0].text}")
                except:
                    pass
                
                logger.error("❌ ログインに失敗しました")
                self._save_debug_screenshot("login_failed")
                self._save_page_source("login_failed")
                return False
                
        except Exception as e:
            logger.error(f"ログインエラー: {e}")
            self._save_debug_screenshot("login_exception")
            return False
    
    def create_post_draft(self, content: str) -> bool:
        """投稿のドラフト作成（スケジュール機能の代替）"""
        try:
            logger.info("投稿ドラフトを作成中...")
            
            # ホーム画面に移動
            self.driver.get("https://www.threads.net")
            time.sleep(3)
            
            # 新規投稿ボタンを探す
            compose_button = None
            
            # パターン1: aria-labelで検索
            try:
                compose_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, '新しいスレッド') or contains(@aria-label, 'New thread')]"))
                )
                logger.info("新規投稿ボタンをaria-labelで発見")
            except:
                pass
            
            # パターン2: クラス名で検索
            if not compose_button:
                try:
                    compose_button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'compose') or contains(@class, 'create')]")
                    logger.info("新規投稿ボタンをclassで発見")
                except:
                    pass
            
            # パターン3: 汎用的なボタン検索
            if not compose_button:
                try:
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for button in buttons:
                        if "作成" in button.get_attribute("innerHTML") or "compose" in button.get_attribute("class"):
                            compose_button = button
                            break
                    if compose_button:
                        logger.info("新規投稿ボタンを汎用検索で発見")
                except:
                    pass
            
            if not compose_button:
                logger.error("新規投稿ボタンが見つかりません")
                self._save_debug_screenshot("compose_button_not_found")
                return False
            
            compose_button.click()
            time.sleep(3)
            
            # テキストエリア検索
            textarea = None
            
            # パターン1: placeholder属性
            try:
                textarea = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder or @aria-label]"))
                )
                logger.info("テキストエリアを発見")
            except:
                pass
            
            # パターン2: contenteditable div
            if not textarea:
                try:
                    textarea = self.driver.find_element(By.XPATH, "//div[@contenteditable='true']")
                    logger.info("contenteditableエリアを発見")
                except:
                    pass
            
            # パターン3: 汎用的なtextarea
            if not textarea:
                try:
                    textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                    if textareas:
                        textarea = textareas[0]
                        logger.info("汎用textareaを発見")
                except:
                    pass
            
            if not textarea:
                logger.error("テキストエリアが見つかりません")
                self._save_debug_screenshot("textarea_not_found")
                return False
            
            # 投稿内容入力
            textarea.clear()
            textarea.send_keys(content)
            time.sleep(2)
            
            logger.info("✅ 投稿内容を入力完了（手動でスケジュール設定してください）")
            self._save_debug_screenshot("post_content_entered")
            
            # 注意メッセージを表示
            print(f"\\n📝 投稿内容が入力されました:")
            print(f"内容: {content[:50]}...")
            print(f"⏰ この画面で手動でスケジュール設定を行ってください")
            print(f"1. 「その他」または「...」メニューをクリック")
            print(f"2. 「スケジュール」を選択")
            print(f"3. 投稿時間を設定")
            print(f"4. 「スケジュール」ボタンをクリック")
            
            # 手動操作待機
            input("\\nスケジュール設定が完了したらEnterキーを押してください...")
            
            return True
            
        except Exception as e:
            logger.error(f"投稿ドラフト作成エラー: {e}")
            self._save_debug_screenshot("draft_creation_error")
            return False
    
    def _save_debug_screenshot(self, filename_prefix):
        """デバッグ用スクリーンショット保存"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"debug_{filename_prefix}_{timestamp}.png"
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"スクリーンショット保存: {screenshot_path}")
        except Exception as e:
            logger.error(f"スクリーンショット保存エラー: {e}")
    
    def _save_page_source(self, filename_prefix):
        """デバッグ用ページソース保存"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            source_path = f"debug_{filename_prefix}_{timestamp}.html"
            with open(source_path, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            logger.info(f"ページソース保存: {source_path}")
        except Exception as e:
            logger.error(f"ページソース保存エラー: {e}")
    
    def close_browser(self):
        """ブラウザを閉じる"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("ブラウザを閉じました")
            except:
                pass

class ImprovedAutomationSystem:
    """改良版完全自動化システム"""
    
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
    
    async def run_semi_automation(self):
        """半自動化実行（投稿生成 + ログイン + 手動スケジュール）"""
        logger.info("改良版自動化システムを開始します")
        
        try:
            # 1. 投稿コンテンツ生成
            logger.info("投稿コンテンツを生成中...")
            all_posts = []
            
            for day in range(min(2, self.config.auto_schedule_days)):  # 最初は2日分のみ
                target_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=day)
                daily_posts = await self.ai_engine.generate_daily_posts(self.config.posts_per_day, target_date)
                
                # データベースに保存
                post_ids = self.scheduler.save_daily_posts(daily_posts, target_date)
                all_posts.extend(daily_posts)
                
                logger.info(f"✅ {target_date.strftime('%m/%d')} - {self.config.posts_per_day}投稿完了")
            
            # 2. Threadsログインとドラフト作成
            logger.info("Threadsにログインして投稿準備中...")
            self.automator = ImprovedThreadsAutomator(self.config)
            
            if not self.automator.setup_browser():
                raise Exception("ブラウザ起動に失敗")
            
            if not self.automator.login_to_threads():
                raise Exception("Threadsログインに失敗")
            
            # 各投稿のドラフト作成（手動スケジュール設定）
            success_count = 0
            for i, post in enumerate(all_posts):
                try:
                    logger.info(f"投稿 {i+1}/{len(all_posts)} を準備中...")
                    
                    success = self.automator.create_post_draft(post['content'])
                    
                    if success:
                        success_count += 1
                        logger.info(f"✅ 投稿 {i+1}/{len(all_posts)} ドラフト作成完了")
                    else:
                        logger.error(f"❌ 投稿 {i+1}/{len(all_posts)} ドラフト作成失敗")
                    
                    if i < len(all_posts) - 1:  # 最後以外は次の投稿へ
                        continue_choice = input(f"\\n次の投稿({i+2}/{len(all_posts)})に進みますか？ (y/n): ")
                        if continue_choice.lower() != 'y':
                            break
                    
                except Exception as e:
                    logger.error(f"投稿 {i+1} ドラフト作成エラー: {e}")
            
            # 3. 結果レポート
            total_posts = len(all_posts)
            logger.info(f"🎉 改良版自動化完了!")
            logger.info(f"📊 結果: {success_count}/{total_posts} 投稿がドラフト作成済み")
            
            # CSVエクスポート
            csv_file = self.scheduler.export_schedule(2)
            logger.info(f"📄 詳細レポート: {csv_file}")
            
            print(f"\\n✨ 次のステップ:")
            print(f"1. 各投稿のスケジュール設定を手動で完了")
            print(f"2. 問題なければ残りの日数も同様に実行")
            print(f"3. 定期実行の設定を検討")
            
        except Exception as e:
            logger.error(f"自動化エラー: {e}")
        
        finally:
            if self.automator:
                input("\\nEnterキーを押してブラウザを閉じます...")
                self.automator.close_browser()

def main():
    """メイン実行"""
    if not SELENIUM_AVAILABLE:
        print("❌ Seleniumが必要です。以下のコマンドを実行してください:")
        print("pip install selenium")
        return
    
    if not MULTIPOST_AVAILABLE:
        print("❌ MULTIPLE_POSTS_PER_DAY.pyが必要です。")
        return
    
    print("🔧 改良版完全自動化システム")
    print("ログインエラーを修正し、より安定した動作を実現")
    
    system = ImprovedAutomationSystem()
    
    print("\\n🚀 半自動化モードで実行します")
    print("（投稿生成 + ログイン + 手動スケジュール設定）")
    
    confirm = input("\\n続行しますか？ (y/n): ")
    if confirm.lower() == 'y':
        asyncio.run(system.run_semi_automation())

if __name__ == "__main__":
    main()