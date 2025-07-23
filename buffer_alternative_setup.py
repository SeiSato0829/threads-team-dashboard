#!/usr/bin/env python3
"""
Buffer API代替実装
BufferのWeb UIを使用した半自動投稿システム
"""

import os
import time
import json
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

load_dotenv()

class BufferWebAutomation:
    """Buffer Web UIを使用した自動投稿"""
    
    def __init__(self):
        self.buffer_email = os.getenv('BUFFER_EMAIL')
        self.buffer_password = os.getenv('BUFFER_PASSWORD')
        self.driver = None
        
    def setup_driver(self):
        """Chromeドライバーのセットアップ"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
    def login_to_buffer(self):
        """Bufferにログイン"""
        self.driver.get("https://login.buffer.com/login")
        
        # メールアドレス入力
        email_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_input.send_keys(self.buffer_email)
        
        # パスワード入力
        password_input = self.driver.find_element(By.NAME, "password")
        password_input.send_keys(self.buffer_password)
        
        # ログインボタンクリック
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # ログイン完了を待つ
        WebDriverWait(self.driver, 20).until(
            EC.url_contains("publish.buffer.com")
        )
        
        print("✅ Bufferにログインしました")
        
    def create_post(self, content: str, schedule_time: datetime = None):
        """投稿を作成"""
        # 新規投稿ボタンをクリック
        new_post_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='create-post-button']"))
        )
        new_post_button.click()
        
        # Threadsチャンネルを選択（既に選択されている場合はスキップ）
        
        # テキストエリアに投稿内容を入力
        text_area = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='composer-text-area']"))
        )
        text_area.clear()
        text_area.send_keys(content)
        
        # スケジュール設定
        if schedule_time:
            # スケジュールボタンをクリック
            schedule_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='schedule-post-button']")
            schedule_button.click()
            
            # 日時を設定（実装は簡略化）
            print(f"📅 スケジュール: {schedule_time}")
        else:
            # 今すぐ投稿
            post_now_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='share-now-button']")
            post_now_button.click()
        
        print("✅ 投稿を作成しました")
        
    def close(self):
        """ブラウザを閉じる"""
        if self.driver:
            self.driver.quit()

class SimpleThreadsScheduler:
    """シンプルな投稿スケジューラー（Buffer不要版）"""
    
    def __init__(self):
        self.db_path = "threads_optimized.db"
        
    def add_scheduled_post(self, content: str, schedule_time: datetime):
        """データベースに予約投稿を追加"""
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO scheduled_posts (content, scheduled_time, status, pattern_type, hashtags)
            VALUES (?, ?, 'pending', 'manual', '')
        """, (content, schedule_time))
        
        conn.commit()
        conn.close()
        
        print(f"✅ 投稿をスケジュールしました: {schedule_time.strftime('%Y-%m-%d %H:%M')}")
        
    def get_pending_posts(self):
        """未投稿の予約を取得"""
        import sqlite3
        import pandas as pd
        
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("""
            SELECT * FROM scheduled_posts
            WHERE status = 'pending' AND scheduled_time <= datetime('now')
            ORDER BY scheduled_time
        """, conn)
        conn.close()
        
        return df

def main():
    """メイン処理"""
    print("📊 Threads投稿管理システム")
    print("\n選択してください:")
    print("1. Buffer Web UIを使用（要ログイン）")
    print("2. ローカルスケジューラーを使用")
    print("3. 手動投稿用のテキストを生成")
    
    choice = input("\n選択 (1-3): ")
    
    if choice == "1":
        # Buffer Web自動化
        automation = BufferWebAutomation()
        automation.setup_driver()
        automation.login_to_buffer()
        
        content = input("\n投稿内容: ")
        automation.create_post(content)
        
        automation.close()
        
    elif choice == "2":
        # ローカルスケジューラー
        scheduler = SimpleThreadsScheduler()
        
        content = input("\n投稿内容: ")
        hours_later = int(input("何時間後に投稿？ (0で即時): "))
        
        schedule_time = datetime.now() + timedelta(hours=hours_later)
        scheduler.add_scheduled_post(content, schedule_time)
        
    elif choice == "3":
        # 手動投稿用テキスト生成
        from ultimate_ai_post_engine import generate_sample_post
        
        print("\n生成された投稿内容:")
        print("-" * 50)
        print(generate_sample_post())
        print("-" * 50)
        print("\n👆 この内容をコピーしてThreadsに手動で投稿してください")

if __name__ == "__main__":
    main()