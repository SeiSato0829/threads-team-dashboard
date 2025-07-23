#!/usr/bin/env python3
"""
Threads API クライアント
実際のThreadsアカウントと連携するためのモジュール
"""

import os
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class ThreadsAPIClient:
    """Threads API クライアント"""
    
    def __init__(self):
        self.access_token = os.getenv('THREADS_ACCESS_TOKEN')
        self.user_id = os.getenv('THREADS_USER_ID')
        self.base_url = "https://graph.threads.net/v1.0"
        
        if not self.access_token:
            raise ValueError("THREADS_ACCESS_TOKENが設定されていません。.envファイルを確認してください。")
    
    def verify_credentials(self) -> Dict:
        """認証情報の確認"""
        try:
            response = requests.get(
                f"{self.base_url}/me",
                params={
                    "fields": "id,username,threads_profile_picture_url,threads_biography",
                    "access_token": self.access_token
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 認証成功！")
                print(f"   ユーザー名: @{data.get('username', 'N/A')}")
                print(f"   ユーザーID: {data.get('id', 'N/A')}")
                return data
            else:
                print(f"❌ 認証失敗: {response.status_code}")
                print(f"   エラー: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 接続エラー: {str(e)}")
            return None
    
    def create_post(self, text: str, media_url: Optional[str] = None) -> Dict:
        """投稿を作成"""
        try:
            # Step 1: メディアコンテナを作成
            params = {
                "media_type": "TEXT",
                "text": text,
                "access_token": self.access_token
            }
            
            if media_url:
                params["media_type"] = "IMAGE"
                params["image_url"] = media_url
            
            response = requests.post(
                f"{self.base_url}/{self.user_id}/threads",
                params=params
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": response.json().get("error", {}).get("message", "Unknown error")
                }
            
            creation_id = response.json().get("id")
            
            # Step 2: 投稿を公開
            publish_response = requests.post(
                f"{self.base_url}/{self.user_id}/threads_publish",
                params={
                    "creation_id": creation_id,
                    "access_token": self.access_token
                }
            )
            
            if publish_response.status_code == 200:
                post_id = publish_response.json().get("id")
                return {
                    "success": True,
                    "post_id": post_id,
                    "url": f"https://www.threads.net/t/{post_id}",
                    "posted_at": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": publish_response.json().get("error", {}).get("message", "Publish failed")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_posts(self, limit: int = 10) -> List[Dict]:
        """投稿履歴を取得"""
        try:
            response = requests.get(
                f"{self.base_url}/{self.user_id}/threads",
                params={
                    "fields": "id,media_type,media_url,permalink,text,timestamp,username,is_quote_post",
                    "limit": limit,
                    "access_token": self.access_token
                }
            )
            
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                print(f"❌ 投稿取得エラー: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ 接続エラー: {str(e)}")
            return []
    
    def get_post_insights(self, post_id: str) -> Dict:
        """投稿のインサイトを取得"""
        try:
            response = requests.get(
                f"{self.base_url}/{post_id}/insights",
                params={
                    "metric": "engagement,impressions,reach,replies,reposts,quotes,likes",
                    "access_token": self.access_token
                }
            )
            
            if response.status_code == 200:
                data = response.json().get("data", [])
                insights = {}
                for metric in data:
                    name = metric.get("name")
                    values = metric.get("values", [])
                    if values:
                        insights[name] = values[0].get("value", 0)
                return insights
            else:
                return {}
                
        except Exception as e:
            print(f"❌ インサイト取得エラー: {str(e)}")
            return {}
    
    def delete_post(self, post_id: str) -> bool:
        """投稿を削除"""
        try:
            response = requests.delete(
                f"{self.base_url}/{post_id}",
                params={"access_token": self.access_token}
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ 削除エラー: {str(e)}")
            return False

def test_connection():
    """接続テスト"""
    print("🔍 Threads API接続テストを開始...")
    
    try:
        client = ThreadsAPIClient()
        
        # 認証確認
        user_info = client.verify_credentials()
        
        if user_info:
            print("\n📊 最近の投稿:")
            posts = client.get_posts(limit=5)
            
            for i, post in enumerate(posts, 1):
                timestamp = datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00'))
                print(f"\n{i}. {timestamp.strftime('%Y-%m-%d %H:%M')}")
                print(f"   {post.get('text', 'No text')[:50]}...")
                
                # インサイトを取得
                insights = client.get_post_insights(post['id'])
                if insights:
                    print(f"   👍 いいね: {insights.get('likes', 0)}")
                    print(f"   💬 返信: {insights.get('replies', 0)}")
                    print(f"   🔄 リポスト: {insights.get('reposts', 0)}")
            
            print("\n✅ 接続テスト成功！")
            return True
        else:
            print("\n❌ 接続テスト失敗")
            return False
            
    except ValueError as e:
        print(f"\n⚠️  設定エラー: {str(e)}")
        print("\n📝 .envファイルに以下を設定してください:")
        print("   THREADS_ACCESS_TOKEN=your_access_token")
        print("   THREADS_USER_ID=your_user_id")
        return False
    except Exception as e:
        print(f"\n❌ エラー: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()