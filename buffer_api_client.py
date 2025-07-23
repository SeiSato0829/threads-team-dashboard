#!/usr/bin/env python3
"""
Buffer API クライアント
Threads投稿を自動化するためのBuffer API連携
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class BufferAPIClient:
    """Buffer API クライアント"""
    
    def __init__(self):
        self.access_token = os.getenv('BUFFER_ACCESS_TOKEN')
        self.profile_id = os.getenv('BUFFER_PROFILE_ID')
        self.base_url = "https://api.bufferapp.com/1"
        
        if not self.access_token:
            raise ValueError("BUFFER_ACCESS_TOKENが設定されていません。")
        if not self.profile_id:
            raise ValueError("BUFFER_PROFILE_IDが設定されていません。")
    
    def get_profile_info(self) -> Dict:
        """プロファイル情報を取得"""
        response = requests.get(
            f"{self.base_url}/profiles/{self.profile_id}.json",
            params={"access_token": self.access_token}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Profile取得エラー: {response.text}")
    
    def create_post(self, text: str, scheduled_at: Optional[datetime] = None) -> Dict:
        """投稿を作成"""
        data = {
            "profile_ids[]": self.profile_id,
            "text": text,
            "access_token": self.access_token
        }
        
        # スケジュール投稿の場合
        if scheduled_at:
            # Buffer APIはUNIXタイムスタンプを期待
            data["scheduled_at"] = int(scheduled_at.timestamp())
        else:
            # 即座に投稿
            data["now"] = True
        
        response = requests.post(
            f"{self.base_url}/updates/create.json",
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return {
                    "success": True,
                    "update_id": result.get("updates", [{}])[0].get("id"),
                    "scheduled_at": scheduled_at.isoformat() if scheduled_at else datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error")
                }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
    
    def get_pending_posts(self) -> List[Dict]:
        """予約投稿一覧を取得"""
        response = requests.get(
            f"{self.base_url}/profiles/{self.profile_id}/updates/pending.json",
            params={"access_token": self.access_token}
        )
        
        if response.status_code == 200:
            return response.json().get("updates", [])
        else:
            return []
    
    def get_sent_posts(self, limit: int = 10) -> List[Dict]:
        """送信済み投稿を取得"""
        response = requests.get(
            f"{self.base_url}/profiles/{self.profile_id}/updates/sent.json",
            params={
                "access_token": self.access_token,
                "limit": limit
            }
        )
        
        if response.status_code == 200:
            return response.json().get("updates", [])
        else:
            return []
    
    def delete_post(self, update_id: str) -> bool:
        """投稿を削除"""
        response = requests.post(
            f"{self.base_url}/updates/{update_id}/destroy.json",
            data={"access_token": self.access_token}
        )
        
        return response.status_code == 200
    
    def get_analytics(self, update_id: str) -> Dict:
        """投稿の分析データを取得"""
        response = requests.get(
            f"{self.base_url}/updates/{update_id}/analytics.json",
            params={"access_token": self.access_token}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {}

def test_connection():
    """Buffer API接続テスト"""
    print("🔍 Buffer API接続テストを開始...")
    
    try:
        client = BufferAPIClient()
        
        # プロファイル情報を取得
        profile = client.get_profile_info()
        print(f"\n✅ 接続成功！")
        print(f"   サービス: {profile.get('service', 'N/A')}")
        print(f"   ユーザー名: {profile.get('service_username', 'N/A')}")
        print(f"   プロファイルID: {profile.get('id', 'N/A')}")
        
        # 予約投稿を確認
        pending = client.get_pending_posts()
        print(f"\n📅 予約投稿: {len(pending)}件")
        
        # 最近の投稿を確認
        sent = client.get_sent_posts(limit=5)
        print(f"\n📝 最近の投稿:")
        for i, post in enumerate(sent[:3], 1):
            created_at = datetime.fromtimestamp(post.get('created_at', 0))
            print(f"   {i}. {created_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"      {post.get('text', '')[:50]}...")
        
        return True
        
    except ValueError as e:
        print(f"\n⚠️  設定エラー: {str(e)}")
        print("\n📝 .envファイルに以下を設定してください:")
        print("   BUFFER_ACCESS_TOKEN=your_buffer_access_token")
        print("   BUFFER_PROFILE_ID=your_buffer_profile_id")
        return False
    except Exception as e:
        print(f"\n❌ エラー: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()