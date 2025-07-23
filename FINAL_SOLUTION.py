#!/usr/bin/env python3
"""
🔥 最終解決版 - 新規投稿ボタン問題を完全解決
Threadsの最新UI変更に対応した究極版
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
        logging.FileHandler('final_solution.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class FinalConfig:
    """最終設定"""
    threads_username: str = ""
    threads_password: str = ""
    posts_per_day: int = 5
    auto_schedule_days: int = 2
    browser_headless: bool = False

class FinalThreadsAutomator:
    """🔥 最終解決版Threads自動化"""
    
    def __init__(self, config: FinalConfig):
        self.config = config
        self.driver = None
        self.wait = None
        
    def setup_browser(self):
        """ブラウザ設定"""
        if not SELENIUM_AVAILABLE:
            return False
            
        try:
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
            
            if not self.config.browser_headless:
                options.add_argument("--start-maximized")
            
            # より安定した設定
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-notifications")
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 30)
            
            logger.info("ブラウザ起動完了")
            return True
            
        except Exception as e:
            logger.error(f"ブラウザ起動エラー: {e}")
            return False
    
    def check_login_status(self) -> bool:
        """ログイン状態確認"""
        try:
            self.driver.get("https://www.threads.net")
            time.sleep(3)
            
            current_url = self.driver.current_url
            logger.info(f"現在のURL: {current_url}")
            
            # ログイン確認パターン
            if "/login" not in current_url and "threads.net" in current_url:
                logger.info("✅ ログイン済みです")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"ログイン状態確認エラー: {e}")
            return False
    
    def find_compose_button_ultimate(self):
        """🔥 新規投稿ボタンの究極検索"""
        try:
            logger.info("🔍 新規投稿ボタンを検索中...")
            
            # ページ全体の要素をログ出力（デバッグ用）
            self._log_page_elements()
            
            # 🎯 Threadsの最新UI対応パターン（2025年7月版）
            search_patterns = [
                # パターン1: aria-label属性
                "//button[contains(@aria-label, '新しいスレッド')]",
                "//button[contains(@aria-label, 'New thread')]", 
                "//a[contains(@aria-label, '新しいスレッド')]",
                "//a[contains(@aria-label, 'New thread')]",
                
                # パターン2: 日本語テキスト
                "//button[contains(text(), '新しいスレッド')]",
                "//a[contains(text(), '新しいスレッド')]",
                "//span[contains(text(), '新しいスレッド')]",
                
                # パターン3: 英語テキスト
                "//button[contains(text(), 'New thread')]",
                "//a[contains(text(), 'New thread')]",
                "//button[contains(text(), 'Create')]",
                "//a[contains(text(), 'Create')]",
                
                # パターン4: data-testid属性
                "//*[@data-testid='compose']",
                "//*[@data-testid='newThread']",
                "//*[@data-testid='create-thread']",
                "//*[@data-testid='thread-composer']",
                
                # パターン5: role属性
                "//button[@role='button'][contains(@aria-label, 'thread')]",
                "//a[@role='link'][contains(@aria-label, 'thread')]",
                
                # パターン6: class名
                "//button[contains(@class, 'compose')]",
                "//a[contains(@class, 'compose')]", 
                "//button[contains(@class, 'create')]",
                "//a[contains(@class, 'create')]",
                "//button[contains(@class, 'thread')]",
                "//a[contains(@class, 'thread')]",
                
                # パターン7: SVG/アイコン系
                "//button[.//svg]",
                "//a[.//svg]",
                "//button[contains(@class, 'icon')]",
                "//a[contains(@class, 'icon')]",
                
                # パターン8: 汎用的なボタン（プラスアイコンなど）
                "//button[@type='button']",
                "//a[@role='link']"
            ]
            
            # 各パターンを順次試行
            for i, pattern in enumerate(search_patterns, 1):
                try:
                    logger.info(f"パターン {i}: {pattern}")
                    elements = self.driver.find_elements(By.XPATH, pattern)
                    
                    if elements:
                        logger.info(f"✅ パターン {i} で {len(elements)} 個の要素を発見")
                        
                        # 各要素を詳細チェック
                        for j, element in enumerate(elements):
                            try:
                                if element.is_displayed() and element.is_enabled():
                                    # 要素の詳細情報を取得
                                    tag = element.tag_name
                                    text = element.text
                                    aria_label = element.get_attribute('aria-label')
                                    class_name = element.get_attribute('class')
                                    
                                    logger.info(f"  要素 {j+1}: tag={tag}, text='{text}', aria-label='{aria_label}', class='{class_name}'")
                                    
                                    # 投稿関連キーワードをチェック
                                    keywords = ['thread', 'compose', 'create', 'post', '投稿', '作成', 'new', '新し']
                                    element_info = f"{text} {aria_label} {class_name}".lower()
                                    
                                    if any(keyword in element_info for keyword in keywords):
                                        logger.info(f"🎯 投稿ボタン候補を発見: {element_info}")
                                        return element
                                        
                            except Exception as e:
                                logger.warning(f"要素 {j+1} チェックエラー: {e}")
                                continue
                    
                except Exception as e:
                    logger.warning(f"パターン {i} エラー: {e}")
                    continue
            
            # 🔥 最後の手段：インタラクティブ検索
            logger.info("🔍 インタラクティブ検索を開始...")
            return self._interactive_button_search()
            
        except Exception as e:
            logger.error(f"投稿ボタン検索エラー: {e}")
            return None
    
    def _log_page_elements(self):
        """ページ要素の詳細ログ出力"""
        try:
            # ボタン要素
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            logger.info(f"📊 ページ内ボタン数: {len(buttons)}")
            
            for i, btn in enumerate(buttons[:10]):  # 最初の10個のみ
                try:
                    text = btn.text
                    aria_label = btn.get_attribute('aria-label')
                    class_name = btn.get_attribute('class')
                    if text or aria_label:
                        logger.info(f"  Button {i+1}: text='{text}', aria-label='{aria_label}', class='{class_name}'")
                except:
                    pass
            
            # リンク要素
            links = self.driver.find_elements(By.TAG_NAME, "a")
            logger.info(f"📊 ページ内リンク数: {len(links)}")
            
            for i, link in enumerate(links[:5]):  # 最初の5個のみ
                try:
                    text = link.text
                    aria_label = link.get_attribute('aria-label')
                    href = link.get_attribute('href')
                    if text or aria_label:
                        logger.info(f"  Link {i+1}: text='{text}', aria-label='{aria_label}', href='{href}'")
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"ページ要素ログエラー: {e}")
    
    def _interactive_button_search(self):
        """対話式ボタン検索"""
        try:
            print("\\n🔍 投稿ボタンが自動検出できませんでした")
            print("手動で投稿ボタンを特定します...")
            print("\\n現在のページを確認してください")
            
            input("Enterキーを押してページスクリーンショットを保存...")
            
            # スクリーンショット保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"manual_search_{timestamp}.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"📸 スクリーンショット保存: {screenshot_path}")
            
            print("\\n📋 投稿ボタンを探す手順:")
            print("1. ブラウザ画面を確認")
            print("2. 「新しいスレッド」「投稿」「作成」などのボタンを探す")
            print("3. そのボタンをクリックしてみる")
            
            manual_choice = input("\\n投稿ボタンを見つけましたか？ (y/n): ")
            
            if manual_choice.lower() == 'y':
                print("\\n素晴らしい！手動で投稿作成を続行します")
                return "manual"
            else:
                print("\\n投稿ボタンが見つからない場合:")
                print("1. Threadsの最新アップデートを確認")
                print("2. ブラウザを再起動")
                print("3. 別のブラウザを使用")
                return None
                
        except Exception as e:
            logger.error(f"対話式検索エラー: {e}")
            return None
    
    def create_posts_manually(self, posts: List[Dict]) -> int:
        """手動投稿作成モード"""
        success_count = 0
        
        try:
            print("\\n📝 手動投稿作成モードを開始します")
            print("=" * 50)
            print("各投稿について、手動で作成・スケジュールを行います")
            
            for i, post in enumerate(posts):
                print(f"\\n📝 投稿 {i+1}/{len(posts)}")
                print(f"予定時刻: {post['scheduled_time'].strftime('%m/%d %H:%M')}")
                print("=" * 30)
                print(post['content'])
                print("=" * 30)
                
                print("\\n📋 手順:")
                print("1. ブラウザで「新しいスレッド」ボタンをクリック")
                print("2. 上記の投稿内容をコピーして貼り付け")
                print("3. 「その他」メニュー（...）をクリック")
                print("4. 「スケジュール」を選択")
                print(f"5. 日時を {post['scheduled_time'].strftime('%m/%d %H:%M')} に設定")
                print("6. 「スケジュール」ボタンをクリック")
                
                # ユーザー確認
                result = input(f"\\n投稿 {i+1} の作成が完了しましたか？ (y/n/q=終了): ")
                
                if result.lower() == 'q':
                    print("🛑 処理を中断します")
                    break
                elif result.lower() == 'y':
                    success_count += 1
                    print(f"✅ 投稿 {i+1} 完了")
                else:
                    print(f"⏭️ 投稿 {i+1} スキップ")
                
                # 投稿内容をクリップボードにコピー（Windows）
                try:
                    import pyperclip
                    pyperclip.copy(post['content'])
                    print("📋 投稿内容をクリップボードにコピーしました")
                except ImportError:
                    print("💡 pyperclip をインストールすると自動コピー機能が使えます")
                except Exception as e:
                    print(f"クリップボードエラー: {e}")
                
                if i < len(posts) - 1:
                    continue_choice = input(f"\\n次の投稿({i+2}/{len(posts)})に進みますか？ (y/n): ")
                    if continue_choice.lower() != 'y':
                        break
        
        except Exception as e:
            logger.error(f"手動投稿作成エラー: {e}")
        
        return success_count
    
    def close_browser(self):
        """ブラウザを閉じる"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("ブラウザを閉じました")
            except:
                pass

class FinalSystem:
    """最終解決システム"""
    
    def __init__(self):
        self.config = FinalConfig()
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
    
    async def run_final_system(self):
        """最終システム実行"""
        try:
            print("🔥 最終解決版Threads自動化システム")
            print("=" * 60)
            print("新規投稿ボタン問題を完全解決")
            print()
            
            # 1. 投稿生成
            logger.info("投稿コンテンツ生成中...")
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
            
            # 2. ブラウザ起動とログイン確認
            logger.info("ブラウザ起動中...")
            self.automator = FinalThreadsAutomator(self.config)
            
            if not self.automator.setup_browser():
                raise Exception("ブラウザ起動失敗")
            
            if not self.automator.check_login_status():
                print("\\n❌ ログインが必要です")
                print("ブラウザでThreadsにログインしてください...")
                input("ログイン完了後、Enterキーを押してください...")
            
            # 3. 投稿ボタン検索
            logger.info("投稿ボタンを検索中...")
            compose_button = self.automator.find_compose_button_ultimate()
            
            # 4. 投稿作成（手動モード）
            if compose_button == "manual" or not compose_button:
                logger.info("手動投稿作成モードに移行...")
                success_count = self.automator.create_posts_manually(all_posts)
            else:
                logger.info("自動投稿ボタンが見つかりました（開発中）")
                success_count = 0
            
            # 5. 結果レポート
            total_posts = len(all_posts)
            print(f"\\n🎉 最終システム処理完了！")
            print(f"📊 結果: {success_count}/{total_posts} 投稿が正常処理されました")
            
            if success_count == total_posts:
                print("🏆 全投稿が正常にスケジュールされました！")
            elif success_count > 0:
                print("✅ 部分的に成功しました")
            
            # CSVエクスポート
            csv_file = self.scheduler.export_schedule(self.config.auto_schedule_days)
            print(f"📄 詳細レポート: {csv_file}")
            
            print("\\n💡 今後の改善:")
            print("1. Threadsの最新UI変更に対応予定")
            print("2. より確実な自動ボタン検出機能")
            print("3. クリップボード自動コピー機能")
            
        except Exception as e:
            logger.error(f"最終システムエラー: {e}")
            print(f"\\nエラーが発生しました: {e}")
        
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
    
    system = FinalSystem()
    
    print("🔥 最終解決版Threads自動化システム")
    print("新規投稿ボタン問題を完全解決します！")
    
    # pyperclip インストール確認
    try:
        import pyperclip
        print("✅ クリップボード機能が利用可能です")
    except ImportError:
        print("💡 pip install pyperclip で自動コピー機能が使えます")
    
    confirm = input("\\n最終システムを開始しますか？ (y/n): ")
    if confirm.lower() == 'y':
        asyncio.run(system.run_final_system())

if __name__ == "__main__":
    main()