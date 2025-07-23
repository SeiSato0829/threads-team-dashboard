#!/usr/bin/env python3
"""
Threads自動データ取得アドオン
既存の収益化システムにスクレイピング機能を追加
"""

import requests
import csv
import json
from datetime import datetime
import time
import os

class ThreadsScrapingAddon:
    def __init__(self):
        self.access_token = ""  # Threads Graph API アクセストークン
        self.user_id = ""       # あなたのThreadsユーザーID
        self.csv_file = "money_optimization_sheets/01_収益トラッキング.tsv"
        
    def setup_api_credentials(self):
        """API認証情報の設定"""
        print("🔑 Threads API設定")
        print("=" * 50)
        
        # 環境変数から取得を試行
        self.access_token = os.getenv('THREADS_ACCESS_TOKEN')
        self.user_id = os.getenv('THREADS_USER_ID')
        
        if not self.access_token:
            print("⚠️ THREADS_ACCESS_TOKEN が設定されていません")
            print("以下の手順でAPIアクセストークンを取得してください：")
            print()
            print("1. Meta for Developers (developers.facebook.com) にアクセス")
            print("2. アプリを作成")
            print("3. Threads Basic Display API を有効化")
            print("4. アクセストークンを生成")
            print()
            
            # 手動入力オプション
            self.access_token = input("アクセストークンを入力（空白の場合は手動モード）: ").strip()
            
        if not self.user_id:
            self.user_id = input("ThreadsユーザーIDを入力: ").strip()
            
        return bool(self.access_token and self.user_id)
    
    def get_threads_data(self, post_url=None):
        """Threads投稿データを取得"""
        
        if not self.access_token:
            print("❌ API設定が完了していません")
            return self._manual_data_entry()
            
        try:
            # Threads Graph API呼び出し
            url = f"https://graph.threads.net/{self.user_id}/threads"
            params = {
                'fields': 'id,media_type,text,timestamp,like_count,reply_count,repost_count,views',
                'access_token': self.access_token,
                'limit': 10
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return self._process_api_data(data)
            else:
                print(f"❌ API呼び出しエラー: {response.status_code}")
                return self._manual_data_entry()
                
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
            return self._manual_data_entry()
    
    def _process_api_data(self, api_data):
        """APIデータを処理"""
        posts = []
        
        for post in api_data.get('data', []):
            processed_post = {
                'id': post.get('id'),
                'content': post.get('text', '')[:50] + '...',
                'timestamp': post.get('timestamp'),
                'likes': post.get('like_count', 0),
                'comments': post.get('reply_count', 0),
                'reposts': post.get('repost_count', 0),
                'views': post.get('views', 0)
            }
            posts.append(processed_post)
            
        return posts
    
    def _manual_data_entry(self):
        """手動データ入力モード"""
        print("📱 手動データ入力モード")
        print("投稿のパフォーマンスデータを入力してください")
        
        post_data = {
            'content': input("投稿内容（一部）: "),
            'likes': int(input("いいね数: ") or 0),
            'comments': int(input("コメント数: ") or 0),
            'reposts': int(input("リポスト数: ") or 0),
            'profile_clicks': int(input("プロフィールクリック数: ") or 0),
            'new_followers': int(input("新規フォロワー数: ") or 0),
            'link_clicks': int(input("リンククリック数: ") or 0),
            'revenue': float(input("売上貢献額（円）: ") or 0)
        }
        
        return [post_data]
    
    def update_spreadsheet_data(self, posts_data):
        """スプレッドシートデータを更新"""
        
        if not os.path.exists(self.csv_file):
            print("❌ 収益トラッキングファイルが見つかりません")
            return False
            
        try:
            # 既存データを読み込み
            with open(self.csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f, delimiter='\t')
                rows = list(reader)
            
            # 新しいデータを追加
            for post in posts_data:
                new_row = [
                    datetime.now().strftime('%Y/%m/%d %H:%M'),  # 投稿日時
                    datetime.now().strftime('%a'),              # 曜日
                    '画像',                                      # 投稿タイプ
                    'education',                                # カテゴリ
                    post.get('content', ''),                    # 投稿内容
                    '',                                         # ハッシュタグ
                    'プロフィールリンク',                        # CTA
                    post.get('likes', 0),                       # いいね数
                    post.get('comments', 0),                    # コメント数
                    post.get('reposts', 0),                     # シェア数
                    0,                                          # DM数
                    '',                                         # エンゲージメント率
                    post.get('profile_clicks', 0),              # プロフィールクリック
                    post.get('new_followers', 0),               # 新規フォロワー
                    post.get('link_clicks', 0),                 # リンククリック
                    post.get('revenue', 0),                     # 売上貢献額
                    '',                                         # ROI
                    '',                                         # CPF
                    ''                                          # メモ
                ]
                rows.append(new_row)
            
            # ファイルに書き戻し
            with open(self.csv_file, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerows(rows)
                
            print("✅ データ更新完了！")
            return True
            
        except Exception as e:
            print(f"❌ データ更新エラー: {e}")
            return False
    
    def setup_automation(self):
        """自動化スケジュールの設定"""
        print("⚙️ 自動化設定")
        print("=" * 30)
        
        schedule_code = '''
# Windows タスクスケジューラ用バッチファイル
# threads_auto_update.bat として保存

@echo off
cd C:\\Users\\music-020\\threads-auto-post
python threads_scraping_addon.py --auto
pause
'''
        
        batch_file = "threads_auto_update.bat"
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write(schedule_code)
            
        print(f"✅ {batch_file} を作成しました")
        print()
        print("自動実行設定:")
        print("1. Windowsキー + R")
        print("2. 'taskschd.msc' と入力してEnter")
        print("3. '基本タスクの作成'をクリック")
        print(f"4. 作成した {batch_file} を指定")
        print("5. 毎日の実行スケジュールを設定")

def main():
    scraper = ThreadsScrapingAddon()
    
    print("🚀 Threads自動データ取得システム")
    print("=" * 50)
    
    # API設定
    if scraper.setup_api_credentials():
        print("✅ API設定完了")
    else:
        print("⚠️ 手動モードで継続")
    
    # データ取得
    print("\n📊 投稿データを取得中...")
    posts_data = scraper.get_threads_data()
    
    if posts_data:
        print(f"✅ {len(posts_data)}件のデータを取得")
        
        # スプレッドシート更新
        if scraper.update_spreadsheet_data(posts_data):
            print("✅ 収益トラッキングシートを更新しました")
        
        # 自動化設定
        setup_auto = input("\n自動化を設定しますか？ (y/n): ").lower() == 'y'
        if setup_auto:
            scraper.setup_automation()
    
    print("\n🎯 次のステップ:")
    print("1. Googleスプレッドシートを確認")
    print("2. ROI分析を実行")
    print("3. 高収益パターンを確認")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        # 自動実行モード
        scraper = ThreadsScrapingAddon()
        if scraper.setup_api_credentials():
            posts_data = scraper.get_threads_data()
            if posts_data:
                scraper.update_spreadsheet_data(posts_data)
    else:
        # 対話モード
        main()