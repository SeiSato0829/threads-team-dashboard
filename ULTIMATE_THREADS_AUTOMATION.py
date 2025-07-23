#!/usr/bin/env python3
"""
🚀 究極のThreads自動投稿システム 2024
Meta公式Threads APIを使用した完全自動化
"""

import os
import json
import time
import asyncio
import aiohttp
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
import sqlite3
import hashlib
from dotenv import load_dotenv
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import schedule

load_dotenv()

class ThreadsAPIAuth:
    """Threads API認証管理"""
    
    def __init__(self):
        self.client_id = os.getenv('THREADS_APP_ID')
        self.client_secret = os.getenv('THREADS_APP_SECRET')
        self.redirect_uri = "http://localhost:8888/callback"
        self.access_token = os.getenv('THREADS_ACCESS_TOKEN')
        self.user_id = os.getenv('THREADS_USER_ID')
        
    def get_auth_url(self) -> str:
        """認証URLを生成"""
        base_url = "https://threads.net/oauth/authorize"
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "threads_basic,threads_content_publish,threads_manage_insights,threads_manage_replies",
            "response_type": "code"
        }
        return f"{base_url}?{urllib.parse.urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Dict:
        """認証コードをアクセストークンに交換"""
        url = "https://graph.threads.net/oauth/access_token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "code": code
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as resp:
                result = await resp.json()
                
        # 短期トークンを長期トークンに変換
        if result.get("access_token"):
            return await self.get_long_lived_token(result["access_token"])
            
        return result
    
    async def get_long_lived_token(self, short_token: str) -> Dict:
        """短期トークンを長期トークン（60日間有効）に変換"""
        url = "https://graph.threads.net/access_token"
        params = {
            "grant_type": "th_exchange_token",
            "client_secret": self.client_secret,
            "access_token": short_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                result = await resp.json()
                
        # トークンを.envに保存
        if result.get("access_token"):
            self.save_token(result["access_token"])
            
        return result
    
    def save_token(self, token: str):
        """トークンを.envファイルに保存"""
        env_content = []
        env_path = ".env"
        
        # 既存の.envを読み込み
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_content = f.readlines()
        
        # トークンを更新または追加
        token_found = False
        for i, line in enumerate(env_content):
            if line.startswith("THREADS_ACCESS_TOKEN="):
                env_content[i] = f"THREADS_ACCESS_TOKEN={token}\n"
                token_found = True
                break
        
        if not token_found:
            env_content.append(f"THREADS_ACCESS_TOKEN={token}\n")
        
        # 保存
        with open(env_path, 'w') as f:
            f.writelines(env_content)
        
        self.access_token = token
        print("✅ アクセストークンを保存しました")

class ThreadsAPI:
    """Threads API操作"""
    
    def __init__(self, auth: ThreadsAPIAuth):
        self.auth = auth
        self.base_url = "https://graph.threads.net/v1.0"
        
    async def create_media_container(self, text: str, media_url: Optional[str] = None) -> str:
        """メディアコンテナを作成"""
        url = f"{self.base_url}/{self.auth.user_id}/threads"
        
        params = {
            "media_type": "TEXT",
            "text": text,
            "access_token": self.auth.access_token
        }
        
        if media_url:
            params["media_type"] = "IMAGE"
            params["image_url"] = media_url
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as resp:
                result = await resp.json()
                
        return result.get("id")
    
    async def publish_media(self, container_id: str) -> Dict:
        """メディアを公開"""
        url = f"{self.base_url}/{self.auth.user_id}/threads_publish"
        
        params = {
            "creation_id": container_id,
            "access_token": self.auth.access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as resp:
                result = await resp.json()
                
        return result
    
    async def get_insights(self, media_id: str) -> Dict:
        """投稿のインサイトを取得"""
        url = f"{self.base_url}/{media_id}/insights"
        
        params = {
            "metric": "views,likes,replies,reposts,quotes",
            "access_token": self.auth.access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                result = await resp.json()
                
        return result

class ThreadsScheduler:
    """投稿スケジューラー"""
    
    def __init__(self, api: ThreadsAPI):
        self.api = api
        self.db_path = "threads_scheduler.db"
        self._init_database()
        
    def _init_database(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scheduled_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            media_url TEXT,
            scheduled_time TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'pending',
            thread_id TEXT,
            posted_at TIMESTAMP,
            insights TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        conn.close()
    
    def schedule_post(self, content: str, scheduled_time: datetime, media_url: Optional[str] = None) -> int:
        """投稿をスケジュール"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO scheduled_posts (content, media_url, scheduled_time)
        VALUES (?, ?, ?)
        """, (content, media_url, scheduled_time.isoformat()))
        
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return post_id
    
    async def publish_scheduled_posts(self):
        """スケジュールされた投稿を公開"""
        conn = sqlite3.connect(self.db_path)
        
        # 公開時刻になった投稿を取得
        posts = pd.read_sql_query("""
        SELECT * FROM scheduled_posts
        WHERE status = 'pending'
        AND scheduled_time <= datetime('now')
        ORDER BY scheduled_time
        """, conn)
        
        for _, post in posts.iterrows():
            try:
                # メディアコンテナを作成
                container_id = await self.api.create_media_container(
                    post['content'],
                    post['media_url']
                )
                
                # 少し待機（APIレート制限対策）
                await asyncio.sleep(2)
                
                # 公開
                result = await self.api.publish_media(container_id)
                
                # ステータスを更新
                cursor = conn.cursor()
                cursor.execute("""
                UPDATE scheduled_posts
                SET status = 'published',
                    thread_id = ?,
                    posted_at = ?
                WHERE id = ?
                """, (result.get('id'), datetime.now().isoformat(), post['id']))
                
                conn.commit()
                
                print(f"✅ 投稿完了: {post['content'][:30]}...")
                
            except Exception as e:
                print(f"❌ 投稿エラー (ID: {post['id']}): {e}")
                
                # エラーステータスを記録
                cursor = conn.cursor()
                cursor.execute("""
                UPDATE scheduled_posts
                SET status = 'error'
                WHERE id = ?
                """, (post['id'],))
                conn.commit()
        
        conn.close()

class AutoPostGenerator:
    """AI投稿生成"""
    
    def __init__(self):
        self.templates = self.load_templates()
        
    def load_templates(self) -> List[Dict]:
        """高収益テンプレートを読み込み"""
        templates_file = "money_optimization_sheets/02_高収益テンプレート.tsv"
        
        if os.path.exists(templates_file):
            df = pd.read_csv(templates_file, sep='\t')
            return df.to_dict('records')
        
        # デフォルトテンプレート
        return [
            {
                "テンプレート内容": "【{time}の気づき】\n\n{topic}について考えたこと。\n\n{insight}\n\nこれを実践したら{result}になりました。\n\n皆さんはどう思いますか？\n\n#学び #成長 #ビジネス"
            },
            {
                "テンプレート内容": "知ってましたか？\n\n{fact}なんです。\n\n私も最初は{misconception}と思ってましたが、\n実は{truth}でした。\n\n詳しく知りたい方はコメントで教えてください💬\n\n#豆知識 #なるほど"
            }
        ]
    
    def generate_post(self) -> str:
        """投稿を生成"""
        import random
        
        template = random.choice(self.templates)
        content = template.get("テンプレート内容", "")
        
        # 変数を置換
        replacements = {
            "{time}": ["朝", "昼", "夜", "今日"][random.randint(0, 3)],
            "{topic}": ["AI活用", "時間管理", "目標設定", "習慣化"][random.randint(0, 3)],
            "{insight}": "小さな改善の積み重ねが大きな成果につながる",
            "{result}": "生産性が2倍に向上",
            "{fact}": "成功者の90%が朝型人間",
            "{misconception}": "夜型の方が集中できる",
            "{truth}": "朝の1時間は夜の3時間に匹敵する価値がある"
        }
        
        for key, value in replacements.items():
            content = content.replace(key, value)
        
        return content

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """OAuth コールバックハンドラー"""
    
    auth_code = None
    
    def do_GET(self):
        """GETリクエストを処理"""
        if self.path.startswith("/callback"):
            # URLからcodeパラメータを抽出
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            
            if 'code' in params:
                OAuthCallbackHandler.auth_code = params['code'][0]
                
                # 成功レスポンス
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""
                <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: #4CAF50;">認証成功！</h1>
                    <p>このウィンドウを閉じて、ターミナルに戻ってください。</p>
                </body>
                </html>
                """)
            else:
                # エラーレスポンス
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<h1>Error: No authorization code received</h1>")

async def setup_oauth_flow():
    """OAuth認証フローを実行"""
    auth = ThreadsAPIAuth()
    
    # 認証URLを生成
    auth_url = auth.get_auth_url()
    print(f"\n🌐 ブラウザで以下のURLを開いて認証してください:")
    print(auth_url)
    
    # ブラウザを自動的に開く
    webbrowser.open(auth_url)
    
    # コールバックサーバーを起動
    server = HTTPServer(('localhost', 8888), OAuthCallbackHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    print("\n⏳ 認証を待っています...")
    
    # 認証コードを待つ
    while OAuthCallbackHandler.auth_code is None:
        await asyncio.sleep(1)
    
    server.shutdown()
    
    # トークンを取得
    print("\n🔄 アクセストークンを取得中...")
    result = await auth.exchange_code_for_token(OAuthCallbackHandler.auth_code)
    
    if result.get("access_token"):
        print("✅ 認証完了！アクセストークンを取得しました。")
        return auth
    else:
        print(f"❌ エラー: {result}")
        return None

async def main():
    """メイン処理"""
    print("""
    ╔═══════════════════════════════════════════════╗
    ║   🚀 究極のThreads自動投稿システム 2024      ║
    ║      Meta公式API使用・完全自動化             ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    # 認証チェック
    auth = ThreadsAPIAuth()
    
    if not auth.access_token:
        print("\n⚠️ 初回認証が必要です")
        
        if not auth.client_id or not auth.client_secret:
            print("\n【設定手順】")
            print("1. https://developers.facebook.com にアクセス")
            print("2. 新しいアプリを作成（Use case: Threads API）")
            print("3. アプリIDとシークレットをコピー")
            print("\n.envファイルに追加：")
            print("THREADS_APP_ID=あなたのアプリID")
            print("THREADS_APP_SECRET=あなたのアプリシークレット")
            return
        
        # OAuth認証フロー
        auth = await setup_oauth_flow()
        if not auth:
            return
    
    # API初期化
    api = ThreadsAPI(auth)
    scheduler = ThreadsScheduler(api)
    generator = AutoPostGenerator()
    
    print("\n📋 メニュー:")
    print("1. 今すぐ投稿")
    print("2. 投稿を自動生成してスケジュール")
    print("3. 24時間自動投稿モード")
    print("4. インサイトを確認")
    
    choice = input("\n選択 (1-4): ")
    
    if choice == "1":
        # 今すぐ投稿
        content = input("投稿内容: ")
        container_id = await api.create_media_container(content)
        result = await api.publish_media(container_id)
        print(f"✅ 投稿完了！ID: {result.get('id')}")
        
    elif choice == "2":
        # 自動生成してスケジュール
        count = int(input("生成する投稿数: "))
        
        print(f"\n🤖 {count}件の投稿を生成します...")
        
        base_time = datetime.now() + timedelta(hours=1)
        
        for i in range(count):
            content = generator.generate_post()
            scheduled_time = base_time + timedelta(hours=i*3)
            
            post_id = scheduler.schedule_post(content, scheduled_time)
            print(f"📅 投稿 #{post_id} を {scheduled_time.strftime('%m/%d %H:%M')} に予約")
            print(f"   内容: {content[:40]}...")
        
        print("\n✅ スケジュール完了！")
        
        # スケジューラーを起動
        print("\n⏰ スケジューラーを起動します...")
        while True:
            await scheduler.publish_scheduled_posts()
            await asyncio.sleep(60)  # 1分ごとにチェック
            
    elif choice == "3":
        # 24時間自動投稿モード
        print("\n🤖 24時間自動投稿モードを開始します...")
        print("停止するには Ctrl+C を押してください")
        
        async def auto_generate_and_schedule():
            """定期的に投稿を生成してスケジュール"""
            # 1日4回投稿（6時間ごと）
            times = [7, 12, 19, 21]
            
            for hour in times:
                content = generator.generate_post()
                scheduled_time = datetime.now().replace(
                    hour=hour, minute=0, second=0, microsecond=0
                )
                
                # 過去の時間なら翌日に
                if scheduled_time <= datetime.now():
                    scheduled_time += timedelta(days=1)
                
                post_id = scheduler.schedule_post(content, scheduled_time)
                print(f"📅 自動生成: 投稿 #{post_id} を {scheduled_time.strftime('%m/%d %H:%M')} に予約")
        
        # 初回実行
        await auto_generate_and_schedule()
        
        # 定期実行
        while True:
            await scheduler.publish_scheduled_posts()
            
            # 毎日午前5時に新しい投稿を生成
            now = datetime.now()
            if now.hour == 5 and now.minute == 0:
                await auto_generate_and_schedule()
            
            await asyncio.sleep(60)
            
    elif choice == "4":
        # インサイト確認
        media_id = input("投稿ID: ")
        insights = await api.get_insights(media_id)
        
        print("\n📊 インサイト:")
        for metric in insights.get("data", []):
            print(f"  {metric['name']}: {metric['values'][0]['value']}")

if __name__ == "__main__":
    asyncio.run(main())