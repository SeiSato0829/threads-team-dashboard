#!/usr/bin/env python3
"""
🤖 毎日自動投稿エンジン - 完全自動化版
指定時間に自動的に投稿を実行
"""

import os
import asyncio
import sqlite3
import json
import logging
from datetime import datetime, timedelta, time
from typing import List, Dict, Optional
import sys

# Seleniumインポート
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# AIエンジンインポート
try:
    from AI_POWERED_VIRAL_ENGINE import AdvancedViralEngine
    AI_ENGINE_AVAILABLE = True
except ImportError:
    AI_ENGINE_AVAILABLE = False

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_auto_post.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DailyAutoPostEngine:
    """毎日自動投稿エンジン"""
    
    def __init__(self):
        self.db_path = "scheduled_posts.db"
        self.config_path = "auto_post_config.json"
        self.credentials_path = "threads_credentials.json"
        
        # 設定読み込み
        self.config = self._load_config()
        
        # AIエンジン初期化
        if AI_ENGINE_AVAILABLE:
            self.ai_engine = AdvancedViralEngine()
        
        # データベース初期化
        self._init_database()
    
    def _load_config(self) -> Dict:
        """設定読み込み"""
        default_config = {
            "posts_per_day": 5,
            "posting_times": ["08:00", "12:00", "19:00", "21:00", "23:00"],
            "generate_days_ahead": 3,
            "retry_attempts": 3,
            "retry_delay": 300,  # 5分
            "threads_login_url": "https://threads.net/login",
            "headless_mode": False
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                logger.error(f"設定ファイル読み込みエラー: {e}")
        
        return default_config
    
    def _init_database(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 投稿テーブル
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scheduled_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            scheduled_time TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'pending',
            posted_at TIMESTAMP,
            error_message TEXT,
            retry_count INTEGER DEFAULT 0,
            engagement_prediction REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 実行ログテーブル
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS execution_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            action TEXT,
            status TEXT,
            details TEXT
        )
        """)
        
        conn.commit()
        conn.close()
    
    async def daily_execution(self):
        """毎日の自動実行メイン処理"""
        logger.info("=== 毎日自動投稿処理開始 ===")
        
        try:
            # 1. 今日の投稿を確認
            todays_posts = self._get_todays_pending_posts()
            logger.info(f"今日の未投稿: {len(todays_posts)}件")
            
            # 2. 必要に応じて新規投稿生成
            if len(todays_posts) < self.config['posts_per_day']:
                await self._generate_posts_if_needed()
            
            # 3. 現在時刻の投稿を実行
            current_time = datetime.now()
            for post in todays_posts:
                scheduled_time = datetime.fromisoformat(post['scheduled_time'])
                
                # 投稿時刻を過ぎていたら投稿
                if scheduled_time <= current_time and post['status'] == 'pending':
                    await self._post_to_threads(post)
            
            # 4. ログ記録
            self._log_execution("daily_execution", "success", 
                              f"処理完了 - 投稿数: {len(todays_posts)}")
            
        except Exception as e:
            logger.error(f"自動実行エラー: {e}")
            self._log_execution("daily_execution", "error", str(e))
    
    async def _generate_posts_if_needed(self):
        """必要に応じて投稿生成"""
        try:
            # 今後3日分の投稿を確認
            future_posts = self._get_future_posts_count()
            
            days_to_generate = []
            for i in range(self.config['generate_days_ahead']):
                target_date = datetime.now() + timedelta(days=i)
                day_key = target_date.strftime('%Y-%m-%d')
                
                if future_posts.get(day_key, 0) < self.config['posts_per_day']:
                    days_to_generate.append(target_date)
            
            if days_to_generate:
                logger.info(f"{len(days_to_generate)}日分の投稿を生成します")
                
                for target_date in days_to_generate:
                    # AI駆動型投稿生成
                    if AI_ENGINE_AVAILABLE:
                        posts = await self.ai_engine.generate_daily_posts(
                            self.config['posts_per_day'], 
                            target_date
                        )
                        
                        # データベースに保存
                        self._save_generated_posts(posts)
                        logger.info(f"{target_date.strftime('%Y-%m-%d')}: {len(posts)}件生成完了")
                    else:
                        logger.error("AIエンジンが利用できません")
        
        except Exception as e:
            logger.error(f"投稿生成エラー: {e}")
    
    async def _post_to_threads(self, post: Dict) -> bool:
        """Threadsへの投稿実行"""
        if not SELENIUM_AVAILABLE:
            logger.error("Seleniumが利用できません")
            return False
        
        driver = None
        try:
            logger.info(f"投稿開始: ID {post['id']}")
            
            # Selenium設定
            options = Options()
            if self.config['headless_mode']:
                options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=options)
            wait = WebDriverWait(driver, 20)
            
            # 認証情報読み込み
            credentials = self._load_credentials()
            if not credentials:
                raise Exception("認証情報が見つかりません")
            
            # Threadsログイン
            driver.get(self.config['threads_login_url'])
            await asyncio.sleep(3)
            
            # Instagram経由でログイン
            try:
                # Instagramでログインボタンを探す
                login_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Instagramアカウントでログイン')]"))
                )
                login_button.click()
            except:
                logger.info("別のログイン方法を試行中...")
            
            # ユーザー名とパスワード入力
            username_input = wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.send_keys(credentials['username'])
            
            password_input = driver.find_element(By.NAME, "password")
            password_input.send_keys(credentials['password'])
            password_input.send_keys(Keys.RETURN)
            
            await asyncio.sleep(5)
            
            # 新規投稿ボタンを探す
            compose_button = self._find_compose_button(driver, wait)
            if not compose_button:
                raise Exception("投稿ボタンが見つかりません")
            
            compose_button.click()
            await asyncio.sleep(2)
            
            # テキスト入力
            text_area = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea, [contenteditable='true']"))
            )
            text_area.send_keys(post['content'])
            await asyncio.sleep(1)
            
            # 投稿ボタンをクリック
            post_button = self._find_post_button(driver, wait)
            if post_button:
                post_button.click()
                await asyncio.sleep(3)
                
                # 投稿成功を記録
                self._update_post_status(post['id'], 'posted', datetime.now())
                logger.info(f"投稿成功: ID {post['id']}")
                return True
            else:
                raise Exception("投稿ボタンが見つかりません")
        
        except Exception as e:
            logger.error(f"投稿エラー: {e}")
            
            # リトライカウント更新
            retry_count = post.get('retry_count', 0) + 1
            self._update_post_retry(post['id'], retry_count, str(e))
            
            # リトライ上限チェック
            if retry_count < self.config['retry_attempts']:
                logger.info(f"リトライ予定: {retry_count}/{self.config['retry_attempts']}")
            else:
                self._update_post_status(post['id'], 'failed')
                logger.error(f"投稿失敗（リトライ上限）: ID {post['id']}")
            
            return False
        
        finally:
            if driver:
                driver.quit()
    
    def _find_compose_button(self, driver, wait):
        """投稿作成ボタンを探す"""
        button_patterns = [
            (By.XPATH, "//a[@href='/new/post']"),
            (By.CSS_SELECTOR, "[aria-label*='新規投稿']"),
            (By.CSS_SELECTOR, "[aria-label*='New post']"),
            (By.CSS_SELECTOR, "[aria-label*='新しいスレッド']"),
            (By.CSS_SELECTOR, "[aria-label*='Create']"),
            (By.XPATH, "//button[contains(., '新規投稿')]"),
            (By.XPATH, "//div[@role='button'][contains(., 'スレッドを作成')]")
        ]
        
        for by, pattern in button_patterns:
            try:
                element = wait.until(EC.element_to_be_clickable((by, pattern)))
                if element:
                    return element
            except:
                continue
        
        return None
    
    def _find_post_button(self, driver, wait):
        """投稿実行ボタンを探す"""
        button_patterns = [
            (By.XPATH, "//button[contains(text(), '投稿')]"),
            (By.XPATH, "//button[contains(text(), 'Post')]"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//div[@role='button'][contains(text(), '投稿')]")
        ]
        
        for by, pattern in button_patterns:
            try:
                element = driver.find_element(by, pattern)
                if element and element.is_enabled():
                    return element
            except:
                continue
        
        return None
    
    def _get_todays_pending_posts(self) -> List[Dict]:
        """今日の未投稿を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today_start = datetime.now().replace(hour=0, minute=0, second=0)
        today_end = today_start + timedelta(days=1)
        
        cursor.execute("""
        SELECT id, content, scheduled_time, status, retry_count
        FROM scheduled_posts
        WHERE scheduled_time >= ? AND scheduled_time < ?
        AND status IN ('pending', 'retry')
        ORDER BY scheduled_time
        """, (today_start, today_end))
        
        columns = [col[0] for col in cursor.description]
        posts = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return posts
    
    def _get_future_posts_count(self) -> Dict[str, int]:
        """将来の投稿数を日付別に取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT DATE(scheduled_time) as date, COUNT(*) as count
        FROM scheduled_posts
        WHERE scheduled_time >= DATE('now')
        AND status != 'failed'
        GROUP BY DATE(scheduled_time)
        """)
        
        results = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return results
    
    def _save_generated_posts(self, posts: List[Dict]):
        """生成した投稿を保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for post in posts:
            cursor.execute("""
            INSERT INTO scheduled_posts 
            (content, scheduled_time, engagement_prediction)
            VALUES (?, ?, ?)
            """, (
                post['content'],
                post['scheduled_time'].isoformat(),
                post.get('engagement_prediction', 0)
            ))
        
        conn.commit()
        conn.close()
    
    def _update_post_status(self, post_id: int, status: str, posted_at: datetime = None):
        """投稿ステータス更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if posted_at:
            cursor.execute("""
            UPDATE scheduled_posts
            SET status = ?, posted_at = ?
            WHERE id = ?
            """, (status, posted_at, post_id))
        else:
            cursor.execute("""
            UPDATE scheduled_posts
            SET status = ?
            WHERE id = ?
            """, (status, post_id))
        
        conn.commit()
        conn.close()
    
    def _update_post_retry(self, post_id: int, retry_count: int, error_message: str):
        """リトライ情報更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        UPDATE scheduled_posts
        SET retry_count = ?, error_message = ?, status = 'retry'
        WHERE id = ?
        """, (retry_count, error_message, post_id))
        
        conn.commit()
        conn.close()
    
    def _load_credentials(self) -> Optional[Dict]:
        """認証情報読み込み"""
        if os.path.exists(self.credentials_path):
            try:
                with open(self.credentials_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # デフォルト値（ユーザーが提供した情報）
        return {
            "username": "seisato0829",
            "password": "zx7bhh53"
        }
    
    def _log_execution(self, action: str, status: str, details: str = ""):
        """実行ログ記録"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO execution_log (action, status, details)
        VALUES (?, ?, ?)
        """, (action, status, details))
        
        conn.commit()
        conn.close()

async def main():
    """メイン実行"""
    engine = DailyAutoPostEngine()
    
    # コマンドライン引数チェック
    if len(sys.argv) > 1:
        if sys.argv[1] == "--execute":
            # 即時実行
            await engine.daily_execution()
        elif sys.argv[1] == "--generate":
            # 投稿生成のみ
            await engine._generate_posts_if_needed()
    else:
        # 通常の定期実行
        logger.info("毎日自動投稿エンジン起動")
        await engine.daily_execution()

if __name__ == "__main__":
    asyncio.run(main())