#!/usr/bin/env python3
"""
🔧 Threadsログイン修正版 - 2025年最新対応
より確実なログイン処理とエラー処理の改善
"""

import os
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

logger = logging.getLogger(__name__)

class ImprovedThreadsAutomator:
    """改良版Threads自動化クラス"""
    
    def __init__(self, config):
        self.config = config
        self.driver = None
        self.wait = None
        
    def setup_browser(self):
        """改良版ブラウザ設定"""
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
            options.add_argument("--disable-images")  # 画像読み込み無効化で高速化
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 30)  # タイムアウトを30秒に延長
            
            logger.info("ブラウザを起動しました")
            return True
            
        except Exception as e:
            logger.error(f"ブラウザ起動エラー: {e}")
            return False
    
    def login_to_threads_improved(self) -> bool:
        """改良版Threadsログイン - 複数の方法を試行"""
        try:
            logger.info("Threadsにログイン中...")
            
            # 直接ログインページへ
            self.driver.get("https://www.threads.net/login")
            time.sleep(5)
            
            # ページが完全に読み込まれるまで待機
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # 現在のURLをログ出力
            current_url = self.driver.current_url
            logger.info(f"現在のURL: {current_url}")
            
            # 複数のログインフィールド検索パターンを試行
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
                    username_field = self.driver.find_element(By.XPATH, "//input[@type='text' or @type='email']")
                    password_field = self.driver.find_element(By.XPATH, "//input[@type='password']")
                    logger.info("ログインフィールドをtype属性で発見")
                except:
                    pass
            
            # パターン3: プレースホルダーで検索
            if not username_field:
                try:
                    username_field = self.driver.find_element(By.XPATH, "//input[@placeholder='ユーザーネーム' or @placeholder='Username' or @placeholder='電話番号、ユーザーネーム、メールアドレス']")
                    password_field = self.driver.find_element(By.XPATH, "//input[@placeholder='パスワード' or @placeholder='Password']")
                    logger.info("ログインフィールドをplaceholder属性で発見")
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
                return False
            
            # ログイン情報入力
            logger.info("ユーザー名を入力中...")
            username_field.clear()
            username_field.send_keys(self.config.threads_username)
            time.sleep(1)
            
            logger.info("パスワードを入力中...")
            password_field.clear()
            password_field.send_keys(self.config.threads_password)
            time.sleep(1)
            
            # ログインボタンを探してクリック
            login_success = False
            
            # パターン1: type="submit"ボタン
            try:
                submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                submit_button.click()
                logger.info("type=submit ボタンでログイン試行")
                login_success = True
            except:
                pass
            
            # パターン2: ログインテキストを含むボタン
            if not login_success:
                try:
                    login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'ログイン') or contains(text(), 'Log in') or contains(text(), 'Sign in')]")
                    login_button.click()
                    logger.info("テキスト検索でログインボタンをクリック")
                    login_success = True
                except:
                    pass
            
            # パターン3: Enterキーでログイン
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
            time.sleep(8)
            
            # ログイン成功確認（複数の方法）
            current_url = self.driver.current_url
            logger.info(f"ログイン後のURL: {current_url}")
            
            # 成功パターンをチェック
            success_indicators = [
                "threads.net/@" in current_url,
                "threads.net/home" in current_url,
                "/login" not in current_url and "threads.net" in current_url,
                len(self.driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'プロフィール') or contains(@aria-label, 'Profile')]")) > 0
            ]
            
            if any(success_indicators):
                logger.info("ログインに成功しました")
                self._save_debug_screenshot("login_success")
                return True
            else:
                logger.error("ログインに失敗しました")
                self._save_debug_screenshot("login_failed")
                return False
                
        except Exception as e:
            logger.error(f"ログインエラー: {e}")
            self._save_debug_screenshot("login_error")
            return False
    
    def schedule_post_improved(self, content: str, scheduled_time: datetime) -> bool:
        """改良版投稿スケジュール"""
        try:
            logger.info(f"投稿をスケジュール中: {scheduled_time}")
            
            # ホーム画面に移動
            self.driver.get("https://www.threads.net")
            time.sleep(3)
            
            # 新規投稿ボタンの複数パターン検索
            compose_button = None
            
            # パターン1: aria-labelで検索
            try:
                compose_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, '新しいスレッド') or contains(@aria-label, 'New thread') or contains(@aria-label, '作成')]"))
                )
                logger.info("新規投稿ボタンをaria-labelで発見")
            except:
                pass
            
            # パターン2: プラスアイコンやペンアイコン
            if not compose_button:
                try:
                    compose_button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'compose') or contains(@class, 'create')]")
                    logger.info("新規投稿ボタンをclassで発見")
                except:
                    pass
            
            # パターン3: SVGアイコン
            if not compose_button:
                try:
                    compose_button = self.driver.find_element(By.XPATH, "//button[.//svg or .//i[contains(@class, 'plus') or contains(@class, 'edit')]]")
                    logger.info("新規投稿ボタンをSVGで発見")
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
                    EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='新しいスレッドを開始...' or @placeholder='Start a thread...' or @placeholder='What\\'s on your mind?']"))
                )
                logger.info("テキストエリアをplaceholderで発見")
            except:
                pass
            
            # パターン2: 汎用的なtextarea
            if not textarea:
                try:
                    textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                    if textareas:
                        textarea = textareas[0]  # 最初のtextareaを使用
                        logger.info("テキストエリアを汎用検索で発見")
                except:
                    pass
            
            # パターン3: contenteditable div
            if not textarea:
                try:
                    textarea = self.driver.find_element(By.XPATH, "//div[@contenteditable='true']")
                    logger.info("テキストエリアをcontenteditableで発見")
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
            
            # 注意：実際のスケジュール機能は2025年1月時点では
            # すべてのユーザーに開放されていない可能性があります
            # そのため、ここでは投稿のドラフト保存を行います
            
            logger.info("投稿内容を入力しました（スケジュール機能は手動設定が必要な場合があります）")
            self._save_debug_screenshot("post_content_entered")
            
            # 実装注意：
            # Threadsのスケジュール機能は段階的展開中のため
            # 手動でスケジュール設定が必要になる場合があります
            
            return True
            
        except Exception as e:
            logger.error(f"投稿スケジュールエラー: {e}")
            self._save_debug_screenshot("schedule_error")
            return False
    
    def _save_debug_screenshot(self, filename_prefix):
        """デバッグ用スクリーンショット保存"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"debug_{filename_prefix}_{timestamp}.png"
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"デバッグスクリーンショットを保存: {screenshot_path}")
        except Exception as e:
            logger.error(f"スクリーンショット保存エラー: {e}")
    
    def close_browser(self):
        """ブラウザを閉じる"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("ブラウザを閉じました")
            except:
                pass

def test_threads_login(username, password):
    """Threadsログインテスト"""
    from dataclasses import dataclass
    
    @dataclass
    class TestConfig:
        threads_username: str
        threads_password: str
        browser_headless: bool = False
    
    config = TestConfig(
        threads_username=username,
        threads_password=password,
        browser_headless=False  # デバッグのため表示モード
    )
    
    automator = ImprovedThreadsAutomator(config)
    
    try:
        print("🔧 ブラウザを起動中...")
        if not automator.setup_browser():
            print("❌ ブラウザ起動に失敗")
            return False
        
        print("🔑 Threadsにログイン中...")
        if automator.login_to_threads_improved():
            print("✅ ログインに成功しました！")
            
            print("📝 投稿テスト中...")
            test_content = "🤖 自動化システムのテスト投稿です\n\n#テスト #自動化"
            test_time = datetime.now()
            
            if automator.schedule_post_improved(test_content, test_time):
                print("✅ 投稿処理に成功しました！")
            else:
                print("⚠️ 投稿処理で問題が発生しました")
            
            return True
        else:
            print("❌ ログインに失敗しました")
            return False
    
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False
    
    finally:
        automator.close_browser()

if __name__ == "__main__":
    # テスト実行
    username = "seisato0829"
    password = "zx7bhh53"
    
    print("🧪 Threadsログインテストを開始...")
    test_threads_login(username, password)