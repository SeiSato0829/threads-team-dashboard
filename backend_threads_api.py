#!/usr/bin/env python3
"""
Threads API対応バックエンド拡張
complete_backend_server_final.py に追加するコード
"""

import os
import requests
from flask import jsonify
from datetime import datetime
import schedule
import time
from threading import Thread

# Threads API設定
THREADS_ACCESS_TOKEN = os.getenv('THREADS_ACCESS_TOKEN')
THREADS_USER_ID = os.getenv('THREADS_USER_ID')
THREADS_API_URL = "https://graph.threads.net/v1.0"

def add_threads_routes(app, claude_client, logger):
    """Threads API対応ルートを追加"""
    
    @app.route('/api/webhook/auto-post', methods=['POST'])
    def webhook_auto_post():
        """Webhookトリガーで自動投稿"""
        try:
            # Claude APIで投稿を生成
            post_content = generate_post_with_claude(claude_client)
            
            # データベースに保存
            from datetime import datetime
            post_data = {
                'content': post_content,
                'created_at': datetime.now().isoformat(),
                'status': 'draft'
            }
            
            # Threads APIで投稿
            if THREADS_ACCESS_TOKEN and THREADS_USER_ID:
                result = post_to_threads(post_content)
                if result['success']:
                    post_data['status'] = 'posted'
                    post_data['threads_id'] = result.get('post_id')
                    logger.info(f"Threads投稿成功: {result.get('post_id')}")
                    
                    return jsonify({
                        'success': True,
                        'message': 'Threadsに投稿しました',
                        'post_id': result.get('post_id'),
                        'content': post_content
                    })
                else:
                    logger.error(f"Threads投稿失敗: {result.get('error')}")
            else:
                logger.warning("Threads APIトークンが設定されていません")
                
            return jsonify({
                'success': True,
                'message': '投稿を生成しました（手動投稿が必要）',
                'content': post_content
            })
            
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/threads/test', methods=['GET'])
    def test_threads_connection():
        """Threads API接続テスト"""
        if not THREADS_ACCESS_TOKEN or not THREADS_USER_ID:
            return jsonify({
                'success': False,
                'error': 'Threads APIが設定されていません'
            })
            
        try:
            # ユーザー情報を取得
            url = f"{THREADS_API_URL}/{THREADS_USER_ID}"
            params = {
                'fields': 'id,username,threads_profile_picture_url',
                'access_token': THREADS_ACCESS_TOKEN
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                user_data = response.json()
                return jsonify({
                    'success': True,
                    'message': 'Threads API接続成功',
                    'user': user_data
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'API Error: {response.status_code}',
                    'details': response.text
                })
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            })

def generate_post_with_claude(claude_client):
    """Claude APIで投稿を生成"""
    if not claude_client:
        return "テスト投稿です 🚀"
        
    try:
        # 多様性のあるプロンプト
        prompts = [
            "ビジネスの生産性を高めるヒントを1つ、Threadsに投稿する内容を生成してください。絵文字を使って親しみやすく。",
            "日常生活を豊かにするライフハックを1つ、Threadsに投稿する内容を生成してください。",
            "モチベーションが上がる言葉を、Threadsに投稿する内容として生成してください。",
            "テクノロジーの面白い活用法について、Threadsに投稿する内容を生成してください。",
            "健康的な習慣について、Threadsに投稿する内容を生成してください。"
        ]
        
        import random
        prompt = random.choice(prompts)
        
        response = claude_client.messages.create(
            model=os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022'),
            max_tokens=150,
            messages=[{
                'role': 'user',
                'content': f"{prompt} 500文字以内で。"
            }]
        )
        
        return response.content[0].text
        
    except Exception as e:
        print(f"Claude API error: {e}")
        return "今日も素晴らしい1日を！ 🌟"

def post_to_threads(content):
    """Threads APIで投稿"""
    try:
        # ステップ1: メディアコンテナ作成
        create_url = f"{THREADS_API_URL}/{THREADS_USER_ID}/threads"
        create_data = {
            'media_type': 'TEXT',
            'text': content,
            'access_token': THREADS_ACCESS_TOKEN
        }
        
        response = requests.post(create_url, data=create_data)
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'Container creation failed: {response.text}'
            }
            
        container_id = response.json()['id']
        
        # ステップ2: 投稿を公開
        publish_url = f"{THREADS_API_URL}/{THREADS_USER_ID}/threads_publish"
        publish_data = {
            'creation_id': container_id,
            'access_token': THREADS_ACCESS_TOKEN
        }
        
        publish_response = requests.post(publish_url, data=publish_data)
        
        if publish_response.status_code == 200:
            return {
                'success': True,
                'post_id': publish_response.json()['id']
            }
        else:
            return {
                'success': False,
                'error': f'Publishing failed: {publish_response.text}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# スケジューラー設定
def setup_scheduler(app):
    """自動投稿スケジューラーを設定"""
    
    def scheduled_post():
        """スケジュールされた投稿を実行"""
        with app.app_context():
            try:
                response = requests.post('http://localhost:5000/api/webhook/auto-post')
                print(f"Scheduled post: {response.json()}")
            except Exception as e:
                print(f"Scheduled post error: {e}")
    
    # 投稿スケジュール設定（カスタマイズ可能）
    schedule.every().day.at("09:00").do(scheduled_post)  # 朝9時
    schedule.every().day.at("12:30").do(scheduled_post)  # 昼12時半
    schedule.every().day.at("19:00").do(scheduled_post)  # 夜7時
    
    # 週末は追加投稿
    schedule.every().saturday.at("15:00").do(scheduled_post)
    schedule.every().sunday.at("15:00").do(scheduled_post)
    
    def run_scheduler():
        """スケジューラーを実行"""
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    # バックグラウンドスレッドで実行
    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    print("✅ 自動投稿スケジューラーが開始されました")
    print("  - 毎日: 9:00, 12:30, 19:00")
    print("  - 週末追加: 15:00")

# 使用方法：
# 1. このコードをcomplete_backend_server_final.pyに統合
# 2. app初期化後に以下を追加:
#    add_threads_routes(app, claude_client, logger)
#    setup_scheduler(app)
# 3. .envファイルにThreads APIトークンを追加