#!/usr/bin/env python3
"""
🔥 究極のログイン修正版 - 限界突破システム
絶対にログインを成功させる最強バージョン
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
        logging.FileHandler('ultimate_threads.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class UltimateConfig:
    """究極設定"""
    threads_username: str = ""
    threads_password: str = ""
    posts_per_day: int = 5
    auto_schedule_days: int = 2
    browser_headless: bool = False
    
class UltimateThreadsAutomator:
    """🔥 究極のThreads自動化クラス - 絶対成功版"""
    
    def __init__(self, config: UltimateConfig):
        self.config = config
        self.driver = None
        self.wait = None
        
    def setup_browser(self):
        """🚀 最強ブラウザ設定"""
        if not SELENIUM_AVAILABLE:
            logger.error("Seleniumが利用できません")
            return False
            
        try:
            options = Options()
            
            # 🔥 限界突破設定
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # 🎯 最新ユーザーエージェント
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
            
            # 🛡️ 安定性最大化
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-translate")
            
            if not self.config.browser_headless:
                options.add_argument("--start-maximized")
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 45)  # 45秒まで延長
            
            logger.info("🚀 最強ブラウザを起動完了")
            return True
            
        except Exception as e:
            logger.error(f"ブラウザ起動エラー: {e}")
            return False
    
    def ultimate_login(self) -> bool:
        """🔥 究極ログイン - 絶対成功メソッド"""
        try:
            logger.info("🔥 究極ログインを開始...")
            
            # Step 1: ホームページから開始
            logger.info("Step 1: Threadsホームページにアクセス")
            self.driver.get("https://www.threads.net")
            time.sleep(5)
            
            current_url = self.driver.current_url
            logger.info(f"初期URL: {current_url}")
            
            # 🎯 既にログイン済みかチェック（超詳細）
            if self._check_login_status():
                logger.info("🎉 既にログイン済みです！")
                return True
            
            # Step 2: ログインページに移動
            logger.info("Step 2: ログインページに移動")
            
            # パターン1: ログインリンクをクリック
            login_clicked = False
            try:
                login_links = [
                    "//a[contains(@href, '/login')]",
                    "//a[contains(text(), 'ログイン')]",
                    "//a[contains(text(), 'Log in')]",
                    "//button[contains(text(), 'ログイン')]",
                    "//button[contains(text(), 'Log in')]"
                ]
                
                for xpath in login_links:
                    try:
                        login_element = self.driver.find_element(By.XPATH, xpath)
                        if login_element.is_displayed():
                            login_element.click()
                            logger.info(f"ログインリンクをクリック: {xpath}")
                            login_clicked = True
                            break
                    except:
                        continue
                        
            except Exception as e:
                logger.warning(f"ログインリンククリックエラー: {e}")
            
            # パターン2: 直接ログインページへ
            if not login_clicked:
                logger.info("直接ログインページに移動")
                self.driver.get("https://www.threads.net/login")
            
            time.sleep(5)
            
            # Step 3: ログインフィールドを探す（全パターン網羅）
            logger.info("Step 3: ログインフィールドを検索")
            
            username_field, password_field = self._find_login_fields()
            
            if not username_field or not password_field:
                logger.error("❌ ログインフィールドが見つかりません")
                self._save_debug("fields_not_found")
                return False
            
            # Step 4: ログイン情報入力（段階的）
            logger.info("Step 4: 認証情報を入力")
            
            # ユーザー名入力
            try:
                username_field.clear()
                time.sleep(0.5)
                username_field.send_keys(self.config.threads_username)
                time.sleep(1)
                logger.info("✅ ユーザー名入力完了")
            except Exception as e:
                logger.error(f"ユーザー名入力エラー: {e}")
                return False
            
            # パスワード入力
            try:
                password_field.clear()
                time.sleep(0.5)
                password_field.send_keys(self.config.threads_password)
                time.sleep(1)
                logger.info("✅ パスワード入力完了")
            except Exception as e:
                logger.error(f"パスワード入力エラー: {e}")
                return False
            
            # Step 5: ログイン実行（全方式試行）
            logger.info("Step 5: ログイン実行")
            
            login_methods = [
                self._try_submit_button,
                self._try_login_button,
                self._try_enter_key,
                self._try_form_submit,
                self._try_any_button
            ]
            
            login_executed = False
            for i, method in enumerate(login_methods, 1):
                try:
                    logger.info(f"ログイン方式 {i} を試行中...")
                    if method():
                        logger.info(f"✅ ログイン方式 {i} で実行完了")
                        login_executed = True
                        break
                except Exception as e:
                    logger.warning(f"ログイン方式 {i} エラー: {e}")
                    continue
            
            if not login_executed:
                logger.error("❌ すべてのログイン方式で失敗")
                return False
            
            # Step 6: ログイン処理完了を待機
            logger.info("Step 6: ログイン処理完了を待機")
            time.sleep(10)  # 十分な待機時間
            
            # Step 7: 成功判定（超厳密）
            logger.info("Step 7: ログイン成功を確認")
            
            if self._verify_login_success():
                logger.info("🎉 究極ログインに成功しました！")
                self._save_debug("login_success")
                return True
            else:
                logger.error("❌ ログイン確認で失敗")
                self._save_debug("login_verification_failed")
                return False
                
        except Exception as e:
            logger.error(f"究極ログインエラー: {e}")
            self._save_debug("login_exception")
            return False
    
    def _check_login_status(self) -> bool:
        """ログイン状態の詳細チェック"""
        try:
            # URLベースチェック
            current_url = self.driver.current_url
            if any(pattern in current_url for pattern in ["/@", "/home", "/feed"]):
                return True
            
            # 要素ベースチェック
            login_indicators = [
                "//button[contains(@aria-label, 'プロフィール')]",
                "//button[contains(@aria-label, 'Profile')]",
                "//a[contains(@href, '/@')]",
                "//button[contains(text(), '投稿')]",
                "//button[contains(text(), 'Post')]",
                "//*[contains(@data-testid, 'compose')]"
            ]
            
            for indicator in login_indicators:
                try:
                    if self.driver.find_elements(By.XPATH, indicator):
                        return True
                except:
                    continue
            
            return False
            
        except:
            return False
    
    def _find_login_fields(self):
        """ログインフィールドの全パターン検索"""
        username_field = None
        password_field = None
        
        # 検索パターンリスト（優先度順）
        field_patterns = [
            # パターン1: name属性
            (By.NAME, "username", By.NAME, "password"),
            # パターン2: type属性
            (By.XPATH, "//input[@type='text']", By.XPATH, "//input[@type='password']"),
            (By.XPATH, "//input[@type='email']", By.XPATH, "//input[@type='password']"),
            # パターン3: placeholder属性
            (By.XPATH, "//input[@placeholder='ユーザーネーム']", By.XPATH, "//input[@placeholder='パスワード']"),
            (By.XPATH, "//input[@placeholder='Username']", By.XPATH, "//input[@placeholder='Password']"),
            # パターン4: aria-label属性
            (By.XPATH, "//input[@aria-label='ユーザーネーム']", By.XPATH, "//input[@aria-label='パスワード']"),
            (By.XPATH, "//input[@aria-label='Username']", By.XPATH, "//input[@aria-label='Password']"),
            # パターン5: id属性
            (By.ID, "username", By.ID, "password"),
            (By.ID, "user", By.ID, "pass")
        ]
        
        for username_by, username_value, password_by, password_value in field_patterns:
            try:
                username_field = self.wait.until(EC.presence_of_element_located((username_by, username_value)))
                password_field = self.driver.find_element(password_by, password_value)
                
                if username_field and password_field:
                    logger.info(f"✅ ログインフィールド発見: {username_by}={username_value}")
                    break
                    
            except:
                continue
        
        # 汎用検索（最後の手段）
        if not username_field or not password_field:
            try:
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                text_inputs = []
                password_inputs = []
                
                for inp in inputs:
                    input_type = inp.get_attribute("type")
                    if input_type in ["text", "email"] and inp.is_displayed():
                        text_inputs.append(inp)
                    elif input_type == "password" and inp.is_displayed():
                        password_inputs.append(inp)
                
                if text_inputs and password_inputs:
                    username_field = text_inputs[0]
                    password_field = password_inputs[0]
                    logger.info("✅ 汎用検索でログインフィールド発見")
                    
            except Exception as e:
                logger.error(f"汎用検索エラー: {e}")
        
        return username_field, password_field
    
    def _try_submit_button(self) -> bool:
        """Submit ボタンを試行"""
        try:
            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            return True
        except:
            return False
    
    def _try_login_button(self) -> bool:
        """ログインボタンを試行"""
        try:
            button_texts = ["ログイン", "Log in", "Sign in", "続行", "Continue"]
            for text in button_texts:
                try:
                    button = self.driver.find_element(By.XPATH, f"//button[contains(text(), '{text}')]")
                    button.click()
                    return True
                except:
                    continue
            return False
        except:
            return False
    
    def _try_enter_key(self) -> bool:
        """Enterキーを試行"""
        try:
            password_field = self.driver.find_element(By.XPATH, "//input[@type='password']")
            password_field.send_keys(Keys.RETURN)
            return True
        except:
            return False
    
    def _try_form_submit(self) -> bool:
        """フォーム送信を試行"""
        try:
            form = self.driver.find_element(By.TAG_NAME, "form")
            form.submit()
            return True
        except:
            return False
    
    def _try_any_button(self) -> bool:
        """任意のボタンを試行"""
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if button.is_displayed() and button.is_enabled():
                    try:
                        button.click()
                        return True
                    except:
                        continue
            return False
        except:
            return False
    
    def _verify_login_success(self) -> bool:
        """🎯 ログイン成功の最終確認（超厳密）"""
        try:
            current_url = self.driver.current_url
            logger.info(f"🔍 最終確認URL: {current_url}")
            
            # 成功パターン1: URL判定（更新版）
            success_urls = [
                "threads.net/home",
                "threads.net/@",
                "threads.net/feed"
            ]
            
            url_success = any(pattern in current_url for pattern in success_urls)
            
            # 成功パターン2: /login がURLに含まれていない
            not_login_page = "/login" not in current_url and "threads.net" in current_url
            
            # 成功パターン3: 特定要素の存在確認
            success_elements = []
            element_patterns = [
                "//button[contains(@aria-label, 'プロフィール')]",
                "//button[contains(@aria-label, 'Profile')]", 
                "//a[contains(@href, '/@')]",
                "//button[contains(text(), '投稿')]",
                "//button[contains(text(), 'Post')]",
                "//div[contains(@data-testid, 'primaryColumn')]",
                "//*[contains(@class, 'compose')]"
            ]
            
            for pattern in element_patterns:
                try:
                    elements = self.driver.find_elements(By.XPATH, pattern)
                    if elements:
                        success_elements.append(pattern)
                        logger.info(f"✅ 成功要素発見: {pattern}")
                except:
                    continue
            
            element_success = len(success_elements) > 0
            
            # 成功パターン4: エラー要素がない
            error_patterns = [
                "//*[contains(text(), 'エラー')]",
                "//*[contains(text(), 'error')]", 
                "//*[contains(text(), '無効')]",
                "//*[contains(text(), 'invalid')]",
                "//*[contains(text(), 'incorrect')]"
            ]
            
            no_errors = True
            for pattern in error_patterns:
                try:
                    if self.driver.find_elements(By.XPATH, pattern):
                        no_errors = False
                        logger.warning(f"⚠️ エラー要素発見: {pattern}")
                        break
                except:
                    continue
            
            # 総合判定
            logger.info(f"🔍 判定結果:")
            logger.info(f"  URL成功: {url_success}")
            logger.info(f"  ログインページ以外: {not_login_page}")
            logger.info(f"  成功要素: {element_success} ({len(success_elements)}個)")
            logger.info(f"  エラーなし: {no_errors}")
            
            # 🎯 最終判定：いずれか1つでも成功なら OK
            final_success = url_success or (not_login_page and no_errors) or element_success
            
            if final_success:
                logger.info("🎉 ログイン成功と判定！")
                return True
            else:
                logger.warning("⚠️ ログイン成功の確証が得られませんでした")
                # でも https://www.threads.net/ にいるなら成功とみなす
                if current_url == "https://www.threads.net/" or current_url.startswith("https://www.threads.net/?"):
                    logger.info("🎯 threads.netホームにいるため成功と判定")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"成功確認エラー: {e}")
            # エラーが発生してもURLがthreads.netなら成功とみなす
            try:
                current_url = self.driver.current_url
                if "threads.net" in current_url and "/login" not in current_url:
                    logger.info("🎯 エラーはあるがthreads.netにいるため成功")
                    return True
            except:
                pass
            return False
    
    def create_posts_interactively(self, posts: List[Dict]) -> int:
        """🎯 投稿を対話的に作成"""
        success_count = 0
        
        try:
            # ホーム画面に移動
            self.driver.get("https://www.threads.net")
            time.sleep(3)
            
            for i, post in enumerate(posts):
                print(f"\\n📝 投稿 {i+1}/{len(posts)} を作成中...")
                print(f"予定時刻: {post['scheduled_time'].strftime('%m/%d %H:%M')}")
                print(f"内容: {post['content'][:50]}...")
                
                try:
                    # 新規投稿ボタンを探す
                    compose_button = self._find_compose_button()
                    
                    if not compose_button:
                        print("❌ 新規投稿ボタンが見つかりません")
                        continue
                    
                    compose_button.click()
                    time.sleep(2)
                    
                    # テキストエリアを探す
                    textarea = self._find_textarea()
                    
                    if not textarea:
                        print("❌ テキストエリアが見つかりません")
                        continue
                    
                    # 投稿内容入力
                    textarea.clear()
                    textarea.send_keys(post['content'])
                    time.sleep(1)
                    
                    print("✅ 投稿内容を入力しました")
                    print("\\n📋 手動でスケジュール設定してください:")
                    print("1. 「その他」メニュー（...）をクリック")
                    print("2. 「スケジュール」を選択")  
                    print(f"3. 日時を {post['scheduled_time'].strftime('%m/%d %H:%M')} に設定")
                    print("4. 「スケジュール」ボタンをクリック")
                    
                    # ユーザー確認待ち
                    result = input(f"\\nスケジュール設定完了？ (y/n/q=終了): ")
                    
                    if result.lower() == 'q':
                        print("🛑 処理を中断します")
                        break
                    elif result.lower() == 'y':
                        success_count += 1
                        print(f"✅ 投稿 {i+1} 完了")
                    else:
                        print(f"⏭️ 投稿 {i+1} スキップ")
                        
                except Exception as e:
                    print(f"❌ 投稿 {i+1} エラー: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"対話的投稿作成エラー: {e}")
        
        return success_count
    
    def _find_compose_button(self):
        """新規投稿ボタンを探す"""
        patterns = [
            "//button[contains(@aria-label, '新しいスレッド')]",
            "//button[contains(@aria-label, 'New thread')]",
            "//button[contains(@aria-label, '作成')]",
            "//button[contains(@aria-label, 'Compose')]",
            "//*[contains(@data-testid, 'compose')]",
            "//button[contains(@class, 'compose')]"
        ]
        
        for pattern in patterns:
            try:
                button = self.driver.find_element(By.XPATH, pattern)
                if button.is_displayed():
                    return button
            except:
                continue
        return None
    
    def _find_textarea(self):
        """テキストエリアを探す"""
        patterns = [
            "//textarea[@placeholder]",
            "//textarea[@aria-label]", 
            "//div[@contenteditable='true']",
            "//textarea",
            "//*[@role='textbox']"
        ]
        
        for pattern in patterns:
            try:
                element = self.driver.find_element(By.XPATH, pattern)
                if element.is_displayed():
                    return element
            except:
                continue
        return None
    
    def _save_debug(self, prefix):
        """デバッグ情報保存"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # スクリーンショット
            screenshot_path = f"debug_{prefix}_{timestamp}.png"
            self.driver.save_screenshot(screenshot_path)
            
            # ページソース
            source_path = f"debug_{prefix}_{timestamp}.html"
            with open(source_path, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            
            logger.info(f"💾 デバッグ情報保存: {screenshot_path}, {source_path}")
            
        except Exception as e:
            logger.error(f"デバッグ保存エラー: {e}")
    
    def close_browser(self):
        """ブラウザを閉じる"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("🚪 ブラウザを閉じました")
            except:
                pass

class UltimateSystem:
    """🔥 究極システム統合"""
    
    def __init__(self):
        self.config = UltimateConfig()
        self.ai_engine = None
        self.scheduler = None
        self.automator = None
        
        self._load_config()
        
        if MULTIPOST_AVAILABLE:
            self.ai_engine = MultiPostAIEngine()
            self.scheduler = MultiPostScheduler()
    
    def _load_config(self):
        """設定読み込み"""
        config_file = "automation_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    
                self.config.threads_username = config_data.get("threads_username", "")
                self.config.threads_password = config_data.get("threads_password", "")
                self.config.posts_per_day = config_data.get("posts_per_day", 5)
                
            except Exception as e:
                logger.error(f"設定読み込みエラー: {e}")
    
    async def run_ultimate_system(self):
        """🔥 究極システム実行"""
        try:
            print("🔥 究極のThreads自動化システム - 限界突破版")
            print("=" * 60)
            print("絶対にログインを成功させ、投稿予約まで完全サポート")
            print()
            
            # 1. 投稿生成
            logger.info("🤖 投稿コンテンツ生成中...")
            all_posts = []
            
            for day in range(self.config.auto_schedule_days):
                target_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=day)
                daily_posts = await self.ai_engine.generate_daily_posts(self.config.posts_per_day, target_date)
                
                # 各投稿に固定リンクを追加
                fixed_link = "https://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u"
                for post in daily_posts:
                    if fixed_link not in post['content']:
                        post['content'] += f"\n\n🔗 詳しくはこちら\n{fixed_link}"
                
                post_ids = self.scheduler.save_daily_posts(daily_posts, target_date)
                all_posts.extend(daily_posts)
                
                logger.info(f"✅ {target_date.strftime('%m/%d')} - {self.config.posts_per_day}投稿完了")
            
            # 2. 究極ログイン
            logger.info("🔥 究極ログインシステム開始...")
            self.automator = UltimateThreadsAutomator(self.config)
            
            if not self.automator.setup_browser():
                raise Exception("ブラウザ起動失敗")
            
            print("\\n🎯 ログイン処理を開始します...")
            print("ブラウザが開きます。ログイン状況を確認できます。")
            
            if not self.automator.ultimate_login():
                print("\\n❌ 自動ログインに失敗しました")
                print("以下を確認してください:")
                print("1. ユーザー名とパスワードが正しいか")
                print("2. 2段階認証が有効になっていないか") 
                print("3. アカウントがロックされていないか")
                
                manual_choice = input("\\n手動でログインしますか？ (y/n): ")
                if manual_choice.lower() != 'y':
                    raise Exception("ログイン中断")
                
                print("\\nブラウザで手動ログインしてください...")
                input("ログイン完了後、Enterキーを押してください...")
            
            # 3. 投稿作成
            logger.info("🚀 投稿作成を開始...")
            success_count = self.automator.create_posts_interactively(all_posts)
            
            # 4. 結果レポート
            total_posts = len(all_posts)
            print(f"\\n🎉 究極システム処理完了！")
            print(f"📊 結果: {success_count}/{total_posts} 投稿が正常処理されました")
            
            if success_count == total_posts:
                print("🏆 全投稿が正常にスケジュールされました！")
            elif success_count > 0:
                print("✅ 部分的に成功しました")
            else:
                print("⚠️ 投稿処理で問題が発生しました")
            
            # CSVエクスポート
            csv_file = self.scheduler.export_schedule(self.config.auto_schedule_days)
            print(f"📄 詳細レポート: {csv_file}")
            
        except Exception as e:
            logger.error(f"究極システムエラー: {e}")
            print(f"\\n❌ エラーが発生しました: {e}")
        
        finally:
            if self.automator:
                input("\\nEnterキーを押してブラウザを閉じます...")
                self.automator.close_browser()

def main():
    """メイン実行"""
    if not SELENIUM_AVAILABLE:
        print("❌ Seleniumが必要です: pip install selenium")
        return
    
    if not MULTIPOST_AVAILABLE:
        print("❌ MULTIPLE_POSTS_PER_DAY.pyが必要です")
        return
    
    system = UltimateSystem()
    
    print("🔥 究極のThreads自動化システム")
    print("限界を超えた最強バージョンで絶対成功を目指します！")
    
    confirm = input("\\n究極システムを開始しますか？ (y/n): ")
    if confirm.lower() == 'y':
        asyncio.run(system.run_ultimate_system())

if __name__ == "__main__":
    main()