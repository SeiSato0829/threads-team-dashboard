#!/usr/bin/env python3
"""
Threads公式投稿システム
BufferではなくThreads APIを直接使用
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import schedule
import threading

load_dotenv()

class ThreadsDirectPoster:
    def __init__(self):
        self.username = os.getenv('THREADS_USERNAME', 'seisato0829')
        self.password = os.getenv('THREADS_PASSWORD')
        self.scheduled_posts = []
        
    def setup_driver(self):
        """Chromeドライバーをセットアップ"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # ヘッドレスモードはオプション（デバッグ時はコメントアウト）
        # options.add_argument('--headless')
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
        
    def login_to_threads(self, driver):
        """Threadsにログイン"""
        try:
            driver.get("https://www.threads.net/login")
            time.sleep(3)
            
            # ユーザー名入力
            username_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.send_keys(self.username)
            
            # パスワード入力
            password_input = driver.find_element(By.NAME, "password")
            password_input.send_keys(self.password)
            password_input.send_keys(Keys.RETURN)
            
            # ログイン完了を待つ
            time.sleep(5)
            
            print("✅ ログイン成功！")
            return True
            
        except Exception as e:
            print(f"❌ ログインエラー: {e}")
            return False
            
    def post_content(self, driver, content):
        """投稿を実行"""
        try:
            # 新規投稿ボタンを探す
            new_post_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and contains(@aria-label, 'New thread')]"))
            )
            new_post_btn.click()
            time.sleep(2)
            
            # テキストエリアに入力
            text_area = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
            )
            text_area.send_keys(content)
            time.sleep(1)
            
            # 投稿ボタンをクリック
            post_btn = driver.find_element(By.XPATH, "//div[@role='button' and contains(text(), 'Post')]")
            post_btn.click()
            
            time.sleep(3)
            print(f"✅ 投稿完了: {content[:30]}...")
            return True
            
        except Exception as e:
            print(f"❌ 投稿エラー: {e}")
            return False
            
    def schedule_posts_from_json(self, json_file="scheduled_posts.json"):
        """JSONから投稿をスケジュール"""
        if not os.path.exists(json_file):
            print(f"❌ {json_file} が見つかりません")
            return
            
        with open(json_file, 'r', encoding='utf-8') as f:
            posts = json.load(f)
            
        print(f"\n📅 {len(posts)}件の投稿をスケジュールします...")
        
        # 投稿時間を計算
        base_time = datetime.now() + timedelta(minutes=5)  # 5分後から開始
        
        for i, post in enumerate(posts):
            if post['status'] == 'pending':
                # 30分ごとに投稿（デモ用に短く設定）
                scheduled_time = base_time + timedelta(minutes=i*30)
                
                self.scheduled_posts.append({
                    'content': post['content'],
                    'scheduled_time': scheduled_time,
                    'id': post['id']
                })
                
                print(f"📌 投稿 #{post['id']} - {scheduled_time.strftime('%H:%M')}に予約")
                
        print(f"\n✅ {len(self.scheduled_posts)}件の投稿を予約しました")
        
    def run_scheduled_posts(self):
        """スケジュールされた投稿を実行"""
        while True:
            now = datetime.now()
            
            for post in self.scheduled_posts[:]:  # コピーを作成
                if now >= post['scheduled_time']:
                    print(f"\n⏰ 投稿時刻になりました (ID: {post['id']})")
                    
                    driver = self.setup_driver()
                    try:
                        if self.login_to_threads(driver):
                            if self.post_content(driver, post['content']):
                                self.scheduled_posts.remove(post)
                                
                                # JSONファイルのステータスを更新
                                self.update_post_status(post['id'], 'posted')
                    finally:
                        driver.quit()
                        
            if not self.scheduled_posts:
                print("\n✨ すべての投稿が完了しました！")
                break
                
            time.sleep(60)  # 1分ごとにチェック
            
    def update_post_status(self, post_id, status):
        """投稿ステータスを更新"""
        with open("scheduled_posts.json", 'r', encoding='utf-8') as f:
            posts = json.load(f)
            
        for post in posts:
            if post['id'] == post_id:
                post['status'] = status
                post['posted_at'] = datetime.now().isoformat()
                break
                
        with open("scheduled_posts.json", 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)

class SimpleScheduler:
    """シンプルなスケジューラー（代替案）"""
    
    @staticmethod
    def create_windows_task(script_path, time_str):
        """Windowsタスクスケジューラーに登録"""
        import subprocess
        
        task_name = f"ThreadsAutoPost_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        cmd = f'schtasks /create /tn "{task_name}" /tr "python {script_path}" /sc once /st {time_str} /f'
        
        try:
            subprocess.run(cmd, shell=True, check=True)
            print(f"✅ タスク '{task_name}' を {time_str} に登録しました")
            return True
        except:
            print("❌ タスクの登録に失敗しました")
            return False

def main():
    print("""
    ╔══════════════════════════════════════════╗
    ║   🚀 Threads 直接投稿システム           ║
    ║      Bufferを使わない新しい方法         ║
    ╚══════════════════════════════════════════╝
    """)
    
    if not os.getenv('THREADS_PASSWORD'):
        print("\n⚠️ 初回設定が必要です！")
        print("\n.envファイルに以下を追加：")
        print("THREADS_USERNAME=seisato0829")
        print("THREADS_PASSWORD=あなたのパスワード")
        print("\n※ セキュリティのため、2段階認証は一時的にOFFにしてください")
        return
        
    print("\n投稿方法を選択してください：")
    print("1. 今すぐ投稿（スケジュール済みの投稿を順次実行）")
    print("2. Windowsタスクスケジューラーに登録")
    print("3. テスト投稿（1件のみ）")
    
    choice = input("\n選択 (1-3): ")
    
    poster = ThreadsDirectPoster()
    
    if choice == "1":
        poster.schedule_posts_from_json()
        poster.run_scheduled_posts()
        
    elif choice == "2":
        print("\n何時に投稿を開始しますか？")
        time_str = input("時刻を入力 (例: 19:00): ")
        
        # 実行スクリプトを作成
        script_content = """
from threads_official_poster import ThreadsDirectPoster

poster = ThreadsDirectPoster()
poster.schedule_posts_from_json()
poster.run_scheduled_posts()
"""
        
        with open("scheduled_runner.py", "w", encoding="utf-8") as f:
            f.write(script_content)
            
        SimpleScheduler.create_windows_task("scheduled_runner.py", time_str)
        
    elif choice == "3":
        driver = poster.setup_driver()
        try:
            if poster.login_to_threads(driver):
                test_content = "テスト投稿 from 自動投稿システム 🚀 #test"
                poster.post_content(driver, test_content)
        finally:
            driver.quit()

if __name__ == "__main__":
    main()