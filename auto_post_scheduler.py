#!/usr/bin/env python3
"""
完全自動投稿スケジューラー
AIが生成した投稿を最適なタイミングで自動投稿
"""

import os
import asyncio
import sqlite3
import json
from datetime import datetime, timedelta
import random
import requests
from typing import List, Dict, Any
import schedule
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pyautogui
import threading
from dotenv import load_dotenv

load_dotenv()

class AutoPostScheduler:
    def __init__(self):
        self.db_path = "threads_auto_post.db"
        self.threads_username = os.getenv('THREADS_USERNAME', 'seisato0829')
        self.threads_password = os.getenv('THREADS_PASSWORD')
        self.optimal_posting_times = [
            {"hour": 7, "minute": 0, "weight": 1.2},   # 朝の通勤時間
            {"hour": 12, "minute": 30, "weight": 1.1}, # ランチタイム
            {"hour": 19, "minute": 0, "weight": 1.3},  # 夕方の帰宅時間
            {"hour": 21, "minute": 0, "weight": 1.5},  # ゴールデンタイム
        ]
        self.daily_post_limit = 4
        self.min_interval_hours = 3
        
    def setup_database(self):
        """データベースの初期設定"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS auto_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            hashtags TEXT,
            scheduled_time TIMESTAMP,
            posted_time TIMESTAMP,
            status TEXT DEFAULT 'pending',
            post_url TEXT,
            engagement_score REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS posting_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            impressions INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            reposts INTEGER DEFAULT 0,
            checked_at TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES auto_posts (id)
        )
        """)
        
        conn.commit()
        conn.close()
    
    def calculate_next_post_time(self) -> datetime:
        """次の最適な投稿時間を計算"""
        now = datetime.now()
        conn = sqlite3.connect(self.db_path)
        
        # 今日の投稿数をチェック
        today_posts = pd.read_sql_query("""
            SELECT COUNT(*) as count FROM auto_posts
            WHERE DATE(scheduled_time) = DATE('now')
            AND status IN ('posted', 'scheduled')
        """, conn).iloc[0]['count']
        
        # 最後の投稿時間を取得
        last_post = pd.read_sql_query("""
            SELECT scheduled_time FROM auto_posts
            WHERE status IN ('posted', 'scheduled')
            ORDER BY scheduled_time DESC
            LIMIT 1
        """, conn)
        
        conn.close()
        
        if not last_post.empty:
            last_time = datetime.fromisoformat(last_post.iloc[0]['scheduled_time'])
            min_next_time = last_time + timedelta(hours=self.min_interval_hours)
        else:
            min_next_time = now
        
        # 今日の投稿上限に達している場合は翌日
        if today_posts >= self.daily_post_limit:
            min_next_time = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0)
        
        # 最適な時間スロットを選択
        best_time = None
        best_score = -1
        
        for day_offset in range(3):  # 今後3日間をチェック
            check_date = now.date() + timedelta(days=day_offset)
            
            for time_slot in self.optimal_posting_times:
                candidate_time = datetime.combine(
                    check_date,
                    datetime.min.time().replace(
                        hour=time_slot['hour'],
                        minute=time_slot['minute']
                    )
                )
                
                # 過去の時間や最小間隔を満たさない時間はスキップ
                if candidate_time <= max(now, min_next_time):
                    continue
                
                # スコアを計算（重み + ランダム要素）
                score = time_slot['weight'] + random.uniform(0, 0.3)
                
                if score > best_score:
                    best_score = score
                    best_time = candidate_time
        
        # 微調整（±15分のランダム性を追加）
        if best_time:
            minutes_offset = random.randint(-15, 15)
            best_time += timedelta(minutes=minutes_offset)
        
        return best_time or (now + timedelta(hours=self.min_interval_hours))
    
    async def post_to_threads(self, content: str, hashtags: List[str] = None) -> Dict[str, Any]:
        """Seleniumを使ってThreadsに投稿"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Threadsにログイン
            driver.get("https://www.threads.net/login")
            
            # ログイン処理
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            
            username_input = driver.find_element(By.NAME, "username")
            password_input = driver.find_element(By.NAME, "password")
            
            username_input.send_keys(self.threads_username)
            password_input.send_keys(self.threads_password)
            password_input.send_keys(Keys.RETURN)
            
            # ログイン完了を待つ
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='New post']"))
            )
            
            # 新規投稿ボタンをクリック
            new_post_button = driver.find_element(By.CSS_SELECTOR, "[aria-label='New post']")
            new_post_button.click()
            
            # 投稿入力欄を待つ
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[contenteditable='true']"))
            )
            
            # テキストを入力
            post_input = driver.find_element(By.CSS_SELECTOR, "[contenteditable='true']")
            
            # ハッシュタグを追加
            full_content = content
            if hashtags:
                full_content += "\n\n" + " ".join([f"#{tag}" for tag in hashtags])
            
            post_input.send_keys(full_content)
            
            # 少し待つ（人間らしく）
            time.sleep(random.uniform(1, 3))
            
            # 投稿ボタンをクリック
            post_button = driver.find_element(By.CSS_SELECTOR, "[type='submit']")
            post_button.click()
            
            # 投稿完了を待つ
            time.sleep(5)
            
            # 投稿URLを取得（可能であれば）
            current_url = driver.current_url
            
            return {
                'success': True,
                'post_url': current_url,
                'posted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"投稿エラー: {e}")
            return {
                'success': False,
                'error': str(e),
                'posted_at': datetime.now().isoformat()
            }
            
        finally:
            driver.quit()
    
    def schedule_post(self, content: str, hashtags: List[str] = None, scheduled_time: datetime = None):
        """投稿をスケジュールに追加"""
        if not scheduled_time:
            scheduled_time = self.calculate_next_post_time()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO auto_posts (content, hashtags, scheduled_time, status)
        VALUES (?, ?, ?, 'scheduled')
        """, (content, json.dumps(hashtags) if hashtags else None, scheduled_time.isoformat()))
        
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"📅 投稿をスケジュールしました:")
        print(f"   ID: {post_id}")
        print(f"   予定時刻: {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"   内容: {content[:50]}...")
        
        return post_id
    
    async def execute_scheduled_posts(self):
        """スケジュールされた投稿を実行"""
        conn = sqlite3.connect(self.db_path)
        
        # 実行時刻を過ぎた投稿を取得
        pending_posts = pd.read_sql_query("""
            SELECT * FROM auto_posts
            WHERE status = 'scheduled'
            AND scheduled_time <= datetime('now')
            ORDER BY scheduled_time ASC
        """, conn)
        
        for _, post in pending_posts.iterrows():
            print(f"\n🚀 投稿を実行します (ID: {post['id']})")
            
            # ハッシュタグをパース
            hashtags = json.loads(post['hashtags']) if post['hashtags'] else None
            
            # 投稿を実行
            result = await self.post_to_threads(post['content'], hashtags)
            
            # 結果を更新
            cursor = conn.cursor()
            if result['success']:
                cursor.execute("""
                UPDATE auto_posts
                SET status = 'posted', posted_time = ?, post_url = ?
                WHERE id = ?
                """, (result['posted_at'], result.get('post_url'), post['id']))
                print(f"✅ 投稿成功!")
            else:
                cursor.execute("""
                UPDATE auto_posts
                SET status = 'failed'
                WHERE id = ?
                """, (post['id'],))
                print(f"❌ 投稿失敗: {result.get('error')}")
            
            conn.commit()
            
            # 次の投稿まで待機（人間らしく）
            if len(pending_posts) > 1:
                wait_time = random.uniform(60, 180)  # 1-3分待機
                print(f"⏳ 次の投稿まで{wait_time:.0f}秒待機...")
                await asyncio.sleep(wait_time)
        
        conn.close()
    
    def generate_daily_posts(self):
        """日次で投稿を生成してスケジュール"""
        from ultimate_ai_post_engine import UltimateThreadsAIEngine
        
        print("\n📝 本日の投稿を生成中...")
        
        engine = UltimateThreadsAIEngine()
        patterns = engine.analyze_high_engagement_patterns()
        
        # トピックをランダムに選択
        all_topics = [
            "Webサイト制作の効率化",
            "AI活用でコスト削減", 
            "フリーランスの成功法則",
            "起業家の資金調達",
            "ビジネス自動化ツール",
            "SNSマーケティング戦略",
            "生産性向上のコツ",
            "リモートワーク術",
            "副業で稼ぐ方法",
            "スタートアップ成功事例"
        ]
        
        # 今日のトピックを選択
        today_topics = random.sample(all_topics, min(self.daily_post_limit, len(all_topics)))
        
        for topic in today_topics:
            # AI投稿生成
            content = asyncio.run(engine.generate_ai_post(topic, patterns))
            
            # ハッシュタグを抽出
            hashtags = self._extract_hashtags_from_content(content)
            
            # スケジュール
            self.schedule_post(content, hashtags)
        
        print(f"✅ {len(today_topics)}件の投稿を生成・スケジュールしました")
    
    def _extract_hashtags_from_content(self, content: str) -> List[str]:
        """コンテンツからハッシュタグを抽出"""
        import re
        hashtags = re.findall(r'#([^\s#]+)', content)
        # コンテンツからハッシュタグを削除
        for tag in hashtags:
            content = content.replace(f'#{tag}', '')
        return hashtags[:5]  # 最大5個
    
    def run_scheduler(self):
        """スケジューラーを実行"""
        print("🤖 自動投稿スケジューラーを起動しました")
        
        self.setup_database()
        
        # 初回の投稿生成
        self.generate_daily_posts()
        
        # スケジュール設定
        # 毎日朝6時に新しい投稿を生成
        schedule.every().day.at("06:00").do(self.generate_daily_posts)
        
        # メインループ
        async def main_loop():
            while True:
                # スケジュールされたタスクを実行
                schedule.run_pending()
                
                # 投稿を実行
                await self.execute_scheduled_posts()
                
                # 60秒待機
                await asyncio.sleep(60)
        
        # 非同期ループを実行
        asyncio.run(main_loop())

if __name__ == "__main__":
    scheduler = AutoPostScheduler()
    scheduler.run_scheduler()