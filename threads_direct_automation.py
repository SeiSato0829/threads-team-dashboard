#!/usr/bin/env python3
"""
Threads直接自動投稿システム
BufferなどのAPIを使わずに直接Threadsに投稿
"""

import os
import time
import json
import sqlite3
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import streamlit as st
from typing import Dict, Optional
import threading
import schedule

class ThreadsDirectAutomation:
    """Threads直接自動投稿クラス"""
    
    def __init__(self):
        self.username = None
        self.password = None
        self.driver = None
        self.is_logged_in = False
        self.db_path = "threads_optimized.db"
        
    def setup_driver(self, headless: bool = False):
        """Chromeドライバーの設定"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        if headless:
            chrome_options.add_argument('--headless')
        
        # ユーザーデータを保存（ログイン状態を維持）
        chrome_options.add_argument(f'--user-data-dir=/tmp/threads_profile')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def login(self, username: str, password: str) -> bool:
        """Threadsにログイン"""
        try:
            self.username = username
            self.password = password
            
            # Threadsのログインページ
            self.driver.get("https://www.threads.net/login")
            time.sleep(3)
            
            # Instagramログインボタンをクリック
            try:
                instagram_login = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Instagram')]"))
                )
                instagram_login.click()
            except:
                pass
            
            # ユーザー名入力
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.clear()
            username_input.send_keys(username)
            
            # パスワード入力
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.clear()
            password_input.send_keys(password)
            
            # ログインボタンクリック
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # ログイン成功を確認
            WebDriverWait(self.driver, 20).until(
                EC.url_contains("threads.net")
            )
            
            self.is_logged_in = True
            return True
            
        except Exception as e:
            st.error(f"ログインエラー: {str(e)}")
            return False
    
    def create_post(self, content: str) -> Dict:
        """投稿を作成"""
        if not self.is_logged_in:
            return {"success": False, "error": "ログインしていません"}
        
        try:
            # ホームページに移動
            self.driver.get("https://www.threads.net")
            time.sleep(3)
            
            # 新規投稿ボタンを探す
            new_post_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='新規投稿']|//button[@aria-label='新規投稿']"))
            )
            new_post_button.click()
            
            # テキストエリアを待つ
            text_area = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
            )
            
            # テキストを入力
            text_area.click()
            text_area.send_keys(content)
            
            # 少し待つ（人間らしく）
            time.sleep(2)
            
            # 投稿ボタンを探してクリック
            post_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[text()='投稿']|//button[text()='投稿']"))
            )
            post_button.click()
            
            # 投稿完了を待つ
            time.sleep(5)
            
            # 投稿成功をデータベースに記録
            self.save_post_to_db(content, "posted")
            
            return {
                "success": True,
                "posted_at": datetime.now().isoformat(),
                "content": content
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_post_to_db(self, content: str, status: str):
        """投稿をデータベースに保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE scheduled_posts 
            SET status = ?, posted_at = CURRENT_TIMESTAMP
            WHERE content = ? AND status = 'pending'
            ORDER BY scheduled_time
            LIMIT 1
        """, (status, content))
        
        if cursor.rowcount == 0:
            # 新規投稿として保存
            cursor.execute("""
                INSERT INTO post_history (content, pattern_type, engagement_score, 
                                        generated_at, hashtags, source, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                content,
                'manual',
                0,
                datetime.now(),
                '',
                'direct_post',
                status
            ))
        
        conn.commit()
        conn.close()
    
    def execute_scheduled_posts(self):
        """スケジュールされた投稿を実行"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 実行時刻を過ぎた投稿を取得
        cursor.execute("""
            SELECT id, content FROM scheduled_posts
            WHERE status = 'pending' AND scheduled_time <= datetime('now')
            ORDER BY scheduled_time
            LIMIT 1
        """)
        
        post = cursor.fetchone()
        conn.close()
        
        if post:
            post_id, content = post
            result = self.create_post(content)
            
            if result["success"]:
                st.success(f"✅ 投稿成功: {content[:50]}...")
            else:
                st.error(f"❌ 投稿失敗: {result.get('error')}")
    
    def close(self):
        """ブラウザを閉じる"""
        if self.driver:
            self.driver.quit()

class ThreadsAutomationDashboard:
    """Streamlit用の自動投稿ダッシュボード"""
    
    def __init__(self):
        self.automation = ThreadsDirectAutomation()
        self.scheduler_thread = None
        
    def run_scheduler(self):
        """バックグラウンドでスケジューラーを実行"""
        schedule.every(5).minutes.do(self.automation.execute_scheduled_posts)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def render_login_section(self):
        """ログインセクションの表示"""
        st.subheader("🔐 Threadsログイン")
        
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("ユーザー名", key="threads_username")
        
        with col2:
            password = st.text_input("パスワード", type="password", key="threads_password")
        
        if st.button("ログイン", type="primary"):
            with st.spinner("ログイン中..."):
                self.automation.setup_driver()
                if self.automation.login(username, password):
                    st.success("✅ ログイン成功！")
                    st.session_state['threads_logged_in'] = True
                    
                    # スケジューラーを開始
                    if not self.scheduler_thread:
                        self.scheduler_thread = threading.Thread(
                            target=self.run_scheduler,
                            daemon=True
                        )
                        self.scheduler_thread.start()
                else:
                    st.error("❌ ログイン失敗")
    
    def render_post_section(self):
        """投稿セクションの表示"""
        st.subheader("📝 直接投稿")
        
        post_content = st.text_area("投稿内容", height=100)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("今すぐ投稿", type="primary"):
                if post_content:
                    with st.spinner("投稿中..."):
                        result = self.automation.create_post(post_content)
                        if result["success"]:
                            st.success("✅ 投稿成功！")
                            st.balloons()
                        else:
                            st.error(f"❌ エラー: {result.get('error')}")
                else:
                    st.warning("投稿内容を入力してください")
        
        with col2:
            if st.button("予約投稿に追加"):
                if post_content:
                    # 予約投稿の時間を選択
                    schedule_time = st.time_input("投稿時刻", datetime.now().time())
                    
                    # データベースに保存
                    conn = sqlite3.connect(self.automation.db_path)
                    cursor = conn.cursor()
                    
                    scheduled_datetime = datetime.combine(
                        datetime.now().date(),
                        schedule_time
                    )
                    
                    cursor.execute("""
                        INSERT INTO scheduled_posts (content, scheduled_time, status)
                        VALUES (?, ?, 'pending')
                    """, (post_content, scheduled_datetime))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success(f"✅ {schedule_time}に予約しました")

def integrate_with_dashboard():
    """既存のダッシュボードに統合するための関数"""
    st.markdown("### 🤖 Threads直接投稿機能")
    
    # セッション状態の初期化
    if 'threads_logged_in' not in st.session_state:
        st.session_state['threads_logged_in'] = False
    
    dashboard = ThreadsAutomationDashboard()
    
    if not st.session_state['threads_logged_in']:
        dashboard.render_login_section()
    else:
        dashboard.render_post_section()
        
        # 自動投稿の状態表示
        st.markdown("---")
        st.markdown("### ⚡ 自動投稿ステータス")
        
        conn = sqlite3.connect("threads_optimized.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM scheduled_posts
            WHERE status = 'pending' AND scheduled_time > datetime('now')
        """)
        
        pending_count = cursor.fetchone()[0]
        conn.close()
        
        st.info(f"📅 予約投稿: {pending_count}件")
        st.success("✅ 自動投稿スケジューラー: 稼働中")

if __name__ == "__main__":
    # テスト用のメイン関数
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        automation = ThreadsDirectAutomation()
        automation.setup_driver()
        
        username = input("Threadsユーザー名: ")
        password = input("Threadsパスワード: ")
        
        if automation.login(username, password):
            print("✅ ログイン成功")
            
            content = input("投稿内容: ")
            result = automation.create_post(content)
            
            if result["success"]:
                print("✅ 投稿成功！")
            else:
                print(f"❌ エラー: {result.get('error')}")
        
        automation.close()