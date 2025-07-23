#!/usr/bin/env python3
"""
リアルタイムエンゲージメントトラッカー
Easy Scraperと連携して投稿のパフォーマンスを監視し、自動的に高パフォーマンス投稿を学習
"""

import os
import time
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import schedule
import threading
import numpy as np

class RealtimeEngagementTracker:
    def __init__(self):
        self.db_path = "threads_auto_post.db"
        self.spreadsheet_id = "1jdGRxpyM4n2Tri41AK7jn-tM6GbRZc6MYIStsco7gNs"
        self.threads_username = "seisato0829"
        self.check_interval = 30  # 30分ごとにチェック
        self.engagement_history = []
        
    def setup_database(self):
        """データベースの初期設定"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # エンゲージメント履歴テーブル
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS engagement_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_url TEXT UNIQUE,
            content TEXT,
            impressions INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            reposts INTEGER DEFAULT 0,
            saves INTEGER DEFAULT 0,
            engagement_rate REAL,
            checked_at TIMESTAMP,
            posted_at TIMESTAMP,
            is_high_performer BOOLEAN DEFAULT 0
        )
        """)
        
        # 学習データテーブル
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT,
            pattern_value TEXT,
            success_rate REAL,
            usage_count INTEGER DEFAULT 1,
            last_updated TIMESTAMP
        )
        """)
        
        conn.commit()
        conn.close()
    
    def scrape_threads_data(self) -> List[Dict]:
        """Seleniumを使ってThreadsデータをスクレイピング"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # ヘッドレスモード
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        posts_data = []
        
        try:
            # Threadsプロフィールページにアクセス
            url = f"https://www.threads.net/@{self.threads_username}"
            driver.get(url)
            
            # ページが完全に読み込まれるまで待機
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            
            # スクロールして投稿を読み込む
            last_height = driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            
            while scroll_attempts < 5:  # 最大5回スクロール
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                    
                last_height = new_height
                scroll_attempts += 1
            
            # 投稿を取得
            posts = driver.find_elements(By.TAG_NAME, "article")
            
            for post in posts[:20]:  # 最新20投稿を取得
                try:
                    post_data = self._extract_post_data(post, driver)
                    if post_data:
                        posts_data.append(post_data)
                except Exception as e:
                    print(f"投稿データ抽出エラー: {e}")
                    continue
                    
        finally:
            driver.quit()
            
        return posts_data
    
    def _extract_post_data(self, post_element, driver) -> Dict:
        """投稿要素からデータを抽出"""
        data = {}
        
        try:
            # 投稿URL
            link_element = post_element.find_element(By.CSS_SELECTOR, "a[href*='/post/']")
            data['url'] = link_element.get_attribute('href')
            
            # 投稿内容
            content_element = post_element.find_element(By.CSS_SELECTOR, "[data-testid='post-content']")
            data['content'] = content_element.text
            
            # エンゲージメント数値を取得
            # いいね数
            try:
                likes_element = post_element.find_element(By.CSS_SELECTOR, "[aria-label*='like']")
                data['likes'] = self._extract_number(likes_element.text)
            except:
                data['likes'] = 0
                
            # コメント数
            try:
                comments_element = post_element.find_element(By.CSS_SELECTOR, "[aria-label*='comment']")
                data['comments'] = self._extract_number(comments_element.text)
            except:
                data['comments'] = 0
                
            # リポスト数
            try:
                reposts_element = post_element.find_element(By.CSS_SELECTOR, "[aria-label*='repost']")
                data['reposts'] = self._extract_number(reposts_element.text)
            except:
                data['reposts'] = 0
            
            # 投稿時間
            time_element = post_element.find_element(By.TAG_NAME, "time")
            data['posted_at'] = time_element.get_attribute('datetime')
            
            # インプレッション数は推定値を使用
            data['impressions'] = self._estimate_impressions(data)
            
            # エンゲージメント率を計算
            total_engagement = data['likes'] + data['comments'] + data['reposts']
            data['engagement_rate'] = total_engagement / max(data['impressions'], 1)
            
            data['checked_at'] = datetime.now().isoformat()
            
        except Exception as e:
            print(f"データ抽出エラー: {e}")
            return None
            
        return data
    
    def _extract_number(self, text: str) -> int:
        """テキストから数値を抽出"""
        import re
        
        if not text:
            return 0
            
        # K, M表記を処理
        text = text.upper()
        if 'K' in text:
            num = float(re.findall(r'[\d.]+', text)[0])
            return int(num * 1000)
        elif 'M' in text:
            num = float(re.findall(r'[\d.]+', text)[0])
            return int(num * 1000000)
        else:
            nums = re.findall(r'\d+', text)
            return int(nums[0]) if nums else 0
    
    def _estimate_impressions(self, post_data: Dict) -> int:
        """インプレッション数を推定"""
        # フォロワー数 × 投稿経過時間による減衰率
        base_followers = 1000  # 基本フォロワー数（実際の値に置き換え）
        
        # 投稿からの経過時間を計算
        if post_data.get('posted_at'):
            posted_time = datetime.fromisoformat(post_data['posted_at'].replace('Z', '+00:00'))
            hours_passed = (datetime.now() - posted_time).total_seconds() / 3600
            
            # 時間による減衰（最初の24時間で90%のインプレッション）
            decay_rate = max(0.1, 1 - (hours_passed / 24) * 0.9)
        else:
            decay_rate = 0.5
            
        estimated = int(base_followers * decay_rate * random.uniform(0.8, 1.2))
        return max(estimated, 100)  # 最低100インプレッション
    
    def update_engagement_data(self, posts_data: List[Dict]):
        """エンゲージメントデータを更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for post in posts_data:
            # 高パフォーマンス判定（エンゲージメント率5%以上）
            is_high_performer = post['engagement_rate'] >= 0.05
            
            cursor.execute("""
            INSERT OR REPLACE INTO engagement_history 
            (post_url, content, impressions, likes, comments, reposts, 
             engagement_rate, checked_at, posted_at, is_high_performer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post['url'], post['content'], post['impressions'],
                post['likes'], post['comments'], post['reposts'],
                post['engagement_rate'], post['checked_at'],
                post.get('posted_at'), is_high_performer
            ))
            
            # 高パフォーマンス投稿から学習
            if is_high_performer:
                self._learn_from_post(post, cursor)
        
        conn.commit()
        conn.close()
    
    def _learn_from_post(self, post: Dict, cursor):
        """高パフォーマンス投稿から学習"""
        content = post['content']
        
        # 絵文字パターンを学習
        import re
        emojis = re.findall(r'[^\u0000-\u007F\u0080-\u00FF\u2000-\u206F]+', content)
        for emoji in emojis:
            self._update_learning_data(cursor, 'emoji', emoji, post['engagement_rate'])
        
        # キーワードを学習
        keywords = re.findall(r'[ぁ-んァ-ヶー一-龠]{2,}', content)
        for keyword in keywords[:10]:  # 上位10キーワード
            self._update_learning_data(cursor, 'keyword', keyword, post['engagement_rate'])
        
        # 文構造を学習
        if '？' in content or '?' in content:
            self._update_learning_data(cursor, 'structure', 'question', post['engagement_rate'])
        if re.search(r'\d+\.', content):
            self._update_learning_data(cursor, 'structure', 'numbered_list', post['engagement_rate'])
        if '✅' in content or '・' in content:
            self._update_learning_data(cursor, 'structure', 'bullet_points', post['engagement_rate'])
    
    def _update_learning_data(self, cursor, pattern_type: str, pattern_value: str, success_rate: float):
        """学習データを更新"""
        cursor.execute("""
        INSERT INTO learning_data (pattern_type, pattern_value, success_rate, last_updated)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(pattern_type, pattern_value) DO UPDATE SET
        success_rate = (success_rate * usage_count + ?) / (usage_count + 1),
        usage_count = usage_count + 1,
        last_updated = ?
        """, (pattern_type, pattern_value, success_rate, datetime.now().isoformat(),
              success_rate, datetime.now().isoformat()))
    
    def get_learning_insights(self) -> Dict:
        """学習から得られた洞察を取得"""
        conn = sqlite3.connect(self.db_path)
        
        insights = {
            'top_emojis': pd.read_sql_query("""
                SELECT pattern_value, success_rate, usage_count
                FROM learning_data
                WHERE pattern_type = 'emoji'
                ORDER BY success_rate DESC
                LIMIT 10
            """, conn).to_dict('records'),
            
            'top_keywords': pd.read_sql_query("""
                SELECT pattern_value, success_rate, usage_count
                FROM learning_data
                WHERE pattern_type = 'keyword'
                ORDER BY success_rate DESC
                LIMIT 20
            """, conn).to_dict('records'),
            
            'effective_structures': pd.read_sql_query("""
                SELECT pattern_value, success_rate, usage_count
                FROM learning_data
                WHERE pattern_type = 'structure'
                ORDER BY success_rate DESC
            """, conn).to_dict('records')
        }
        
        conn.close()
        return insights
    
    def export_to_spreadsheet(self):
        """データをGoogle Spreadsheetにエクスポート"""
        conn = sqlite3.connect(self.db_path)
        
        # 最新のエンゲージメントデータを取得
        df = pd.read_sql_query("""
            SELECT * FROM engagement_history
            WHERE checked_at >= datetime('now', '-7 days')
            ORDER BY engagement_rate DESC
        """, conn)
        
        # CSVとして保存（Google Sheetsにインポート用）
        export_path = f"engagement_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(export_path, index=False, encoding='utf-8-sig')
        
        print(f"✅ エンゲージメントデータをエクスポートしました: {export_path}")
        
        conn.close()
        return export_path
    
    def run_monitoring(self):
        """監視を実行"""
        print("🔍 リアルタイムエンゲージメント監視を開始します...")
        
        def job():
            print(f"\n📊 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - チェック開始")
            
            # データをスクレイピング
            posts_data = self.scrape_threads_data()
            print(f"✅ {len(posts_data)}件の投稿を取得")
            
            # データベースを更新
            self.update_engagement_data(posts_data)
            
            # 高パフォーマンス投稿を表示
            high_performers = [p for p in posts_data if p['engagement_rate'] >= 0.05]
            if high_performers:
                print(f"🌟 高パフォーマンス投稿: {len(high_performers)}件")
                for post in high_performers[:3]:
                    print(f"   - ER: {post['engagement_rate']*100:.1f}% | {post['content'][:30]}...")
            
            # 学習洞察を表示
            insights = self.get_learning_insights()
            if insights['top_keywords']:
                print(f"🔥 トレンドキーワード: {', '.join([k['pattern_value'] for k in insights['top_keywords'][:5]])}")
        
        # 初回実行
        self.setup_database()
        job()
        
        # スケジュール設定
        schedule.every(self.check_interval).minutes.do(job)
        
        # 毎日レポートをエクスポート
        schedule.every().day.at("09:00").do(self.export_to_spreadsheet)
        
        # 実行ループ
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    tracker = RealtimeEngagementTracker()
    tracker.run_monitoring()