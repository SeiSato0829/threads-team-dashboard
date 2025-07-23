#!/usr/bin/env python3
"""
完全自動Buffer投稿予約システム
生成した投稿を自動的にBufferに送信して予約投稿
"""

import os
import json
import requests
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv

load_dotenv()

class AutoBufferPoster:
    def __init__(self):
        self.buffer_token = os.getenv('BUFFER_ACCESS_TOKEN')
        self.buffer_profile_id = os.getenv('BUFFER_PROFILE_ID')
        self.base_url = "https://api.bufferapp.com/1"
        
    def check_config(self):
        """設定をチェック"""
        if not self.buffer_token:
            print("\n⚠️ Buffer設定が必要です！")
            print("\n以下の手順で設定してください：")
            print("1. https://buffer.com/app/account/apps にアクセス")
            print("2. 'Create App'をクリック")
            print("3. アプリ名を入力して作成")
            print("4. Access Tokenをコピー")
            print("\n5. .envファイルに追加：")
            print("BUFFER_ACCESS_TOKEN=あなたのトークン")
            print("BUFFER_PROFILE_ID=あなたのプロファイルID")
            return False
            
        return True
        
    def get_profiles(self):
        """Bufferプロファイルを取得"""
        url = f"{self.base_url}/profiles.json"
        params = {"access_token": self.buffer_token}
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                profiles = response.json()
                print("\n📱 利用可能なプロファイル:")
                for profile in profiles:
                    print(f"  - {profile['service']}: {profile['id']}")
                return profiles
            else:
                print(f"❌ エラー: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 接続エラー: {e}")
            return None
            
    def schedule_post(self, content, scheduled_time=None, media=None):
        """Bufferに投稿を予約"""
        if not self.buffer_profile_id:
            profiles = self.get_profiles()
            if profiles:
                self.buffer_profile_id = profiles[0]['id']
                print(f"\n✅ プロファイルID: {self.buffer_profile_id} を使用")
            else:
                return False
                
        url = f"{self.base_url}/updates/create.json"
        
        # 投稿時間を設定（指定なければ最適な時間を自動選択）
        if not scheduled_time:
            scheduled_time = self._get_optimal_time()
            
        data = {
            "text": content,
            "profile_ids[]": self.buffer_profile_id,
            "scheduled_at": scheduled_time.isoformat(),
            "access_token": self.buffer_token
        }
        
        # 画像がある場合
        if media:
            data["media[photo]"] = media
            
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 投稿を予約しました！")
                print(f"   予定時刻: {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
                print(f"   Buffer ID: {result.get('updates', [{}])[0].get('id', 'N/A')}")
                return True
            else:
                print(f"❌ 予約失敗: {response.status_code}")
                print(f"   詳細: {response.text}")
                return False
        except Exception as e:
            print(f"❌ エラー: {e}")
            return False
            
    def _get_optimal_time(self):
        """最適な投稿時間を計算"""
        optimal_hours = [7, 12, 19, 21]  # 最適な投稿時間
        now = datetime.now()
        
        # 次の最適な時間を見つける
        for hour in optimal_hours:
            target_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if target_time > now + timedelta(minutes=30):  # 30分以上先
                return target_time
                
        # 今日の時間が全て過ぎていたら翌日の最初の時間
        return (now + timedelta(days=1)).replace(hour=optimal_hours[0], minute=0, second=0, microsecond=0)
        
    def bulk_schedule_from_json(self, json_file="scheduled_posts.json"):
        """JSONファイルから一括予約"""
        if not os.path.exists(json_file):
            print(f"❌ {json_file} が見つかりません")
            return
            
        with open(json_file, 'r', encoding='utf-8') as f:
            posts = json.load(f)
            
        print(f"\n📋 {len(posts)}件の投稿を予約します...")
        
        success_count = 0
        base_time = self._get_optimal_time()
        
        for i, post in enumerate(posts):
            if post['status'] == 'pending':
                # 3時間ごとに投稿時間を設定
                scheduled_time = base_time + timedelta(hours=i*3)
                
                print(f"\n[{i+1}/{len(posts)}] 投稿を処理中...")
                
                if self.schedule_post(post['content'], scheduled_time):
                    # ステータスを更新
                    post['status'] = 'scheduled'
                    post['buffer_scheduled_time'] = scheduled_time.isoformat()
                    success_count += 1
                    
                # API制限を避けるため少し待機
                time.sleep(2)
                
        # 更新したJSONを保存
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
            
        print(f"\n✨ 完了！ {success_count}/{len(posts)}件を予約しました")
        
def main():
    """メイン処理"""
    print("🚀 Buffer自動投稿予約システム")
    print("="*50)
    
    poster = AutoBufferPoster()
    
    # 設定チェック
    if not poster.check_config():
        return
        
    print("\n何をしますか？")
    print("1. 生成済み投稿を一括予約")
    print("2. 新規投稿を生成して予約")
    print("3. Bufferプロファイルを確認")
    print("4. テスト投稿")
    
    choice = input("\n選択してください (1-4): ")
    
    if choice == "1":
        poster.bulk_schedule_from_json()
        
    elif choice == "2":
        # 投稿生成システムを呼び出し
        from simple_auto_post import generate_simple_post, save_to_schedule
        
        count = int(input("何件生成しますか？: "))
        
        for i in range(count):
            print(f"\n生成中... ({i+1}/{count})")
            content = generate_simple_post()
            save_to_schedule(content)
            
        print("\n生成完了！予約を開始します...")
        poster.bulk_schedule_from_json()
        
    elif choice == "3":
        poster.get_profiles()
        
    elif choice == "4":
        test_content = "テスト投稿 from Threads自動投稿システム 🚀"
        poster.schedule_post(test_content)

if __name__ == "__main__":
    main()