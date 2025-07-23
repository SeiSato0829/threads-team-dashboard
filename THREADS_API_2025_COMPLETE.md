# 🚀 Threads API 完全ガイド 2025年最新版

## 📊 2025年1月の最新情報

### API公式情報
- **公式エンドポイント**: `https://graph.threads.net`
- **リリース**: 2024年6月正式公開
- **最新アップデート**: 2024年12月（検索・分析機能追加）
- **料金**: 完全無料

### 最新機能（2025年1月現在）

1. **キーワード検索API** 🔍
   - 公開投稿をキーワードで検索可能
   - 制限: 7日間で500クエリまで

2. **高度な分析機能** 📊
   - シェア数の追跡
   - デモグラフィックデータ
   - エンゲージメント分析

3. **自動化機能** 🤖
   - プログラムによる返信
   - リポスト・引用機能
   - メンション追跡

4. **oEmbed対応** 💻
   - 外部サイトへの埋め込み
   - アプリトークンで500万リクエスト/24時間

## 🔧 完全無料自動化の実装方法

### ステップ1: Threads API認証設定

**1. Meta開発者アカウント作成**
```
1. https://developers.facebook.com にアクセス
2. Facebookでログイン
3. 「My Apps」→「Create App」
4. Business typeを選択
```

**2. Threads APIを有効化**
```
1. Add Product → Threads
2. 必要な権限:
   - threads_basic
   - threads_content_publish
   - threads_manage_insights（分析用）
```

**3. アクセストークン取得**

OAuth 2.0フロー:
```
認証URL: https://threads.net/oauth/authorize
トークン交換: https://graph.threads.net/oauth/access_token
長期トークン: https://graph.threads.net/access_token
```

### ステップ2: バックエンド実装（最新版）

```python
# complete_backend_server_final.py への追加コード

import os
import requests
import schedule
import time
from threading import Thread
from datetime import datetime
import random

# Threads API設定（2025年最新）
THREADS_API_BASE = "https://graph.threads.net/v1.0"
THREADS_ACCESS_TOKEN = os.getenv('THREADS_ACCESS_TOKEN')
THREADS_USER_ID = os.getenv('THREADS_USER_ID')

# APIレート制限管理
class RateLimiter:
    def __init__(self):
        self.daily_posts = 0
        self.weekly_searches = 0
        self.last_reset = datetime.now()
        
    def can_post(self):
        # 24時間で250投稿まで
        return self.daily_posts < 250
        
    def can_search(self):
        # 7日間で500検索まで
        return self.weekly_searches < 500

rate_limiter = RateLimiter()

@app.route('/api/threads/auto-post', methods=['POST'])
def threads_auto_post():
    """最新のThreads API対応自動投稿"""
    try:
        if not rate_limiter.can_post():
            return jsonify({
                'success': False,
                'error': 'API制限に達しました（24時間で250投稿まで）'
            }), 429
            
        # 1. Claude AIで投稿生成
        post_data = generate_advanced_post()
        
        # 2. メディアコンテナ作成
        container_id = create_threads_container(post_data)
        
        # 3. 投稿を公開
        result = publish_threads_post(container_id)
        
        if result['success']:
            rate_limiter.daily_posts += 1
            
            # 4. 投稿後の分析データを取得（新機能）
            analytics = get_post_analytics(result['post_id'])
            
            return jsonify({
                'success': True,
                'post_id': result['post_id'],
                'content': post_data['text'],
                'analytics': analytics
            })
            
    except Exception as e:
        logger.error(f"Threads投稿エラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def generate_advanced_post():
    """Claude AIで高度な投稿を生成"""
    # トレンドトピックをランダムに選択
    topics = [
        "2025年のビジネストレンド",
        "AI活用術",
        "生産性向上のヒント",
        "健康的なライフスタイル",
        "サステナビリティ",
        "リモートワークのコツ",
        "クリエイティブな発想法",
        "マインドフルネス"
    ]
    
    topic = random.choice(topics)
    
    # 時間帯に応じた投稿スタイル
    hour = datetime.now().hour
    if 6 <= hour < 12:
        style = "朝の活力を与える"
    elif 12 <= hour < 17:
        style = "午後の生産性を高める"
    else:
        style = "夜のリラックスを促す"
    
    if claude_client:
        response = claude_client.messages.create(
            model=os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022'),
            max_tokens=200,
            messages=[{
                'role': 'user',
                'content': f"""
                {topic}について、{style}Threads投稿を作成してください。
                
                要件:
                - 500文字以内
                - 絵文字を効果的に使用
                - ハッシュタグを2-3個含める
                - 行動を促すCTAを含める
                - 2025年のトレンドを意識した内容
                """
            }]
        )
        
        text = response.content[0].text
    else:
        text = f"今日も素晴らしい1日を！ 🌟 #{topic} #2025年"
    
    return {
        'text': text,
        'media_type': 'TEXT'
    }

def create_threads_container(post_data):
    """メディアコンテナを作成"""
    url = f"{THREADS_API_BASE}/{THREADS_USER_ID}/threads"
    
    data = {
        'media_type': post_data['media_type'],
        'text': post_data['text'],
        'access_token': THREADS_ACCESS_TOKEN
    }
    
    response = requests.post(url, data=data)
    
    if response.status_code != 200:
        raise Exception(f"Container creation failed: {response.text}")
        
    return response.json()['id']

def publish_threads_post(container_id):
    """投稿を公開"""
    url = f"{THREADS_API_BASE}/{THREADS_USER_ID}/threads_publish"
    
    data = {
        'creation_id': container_id,
        'access_token': THREADS_ACCESS_TOKEN
    }
    
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        return {
            'success': True,
            'post_id': response.json()['id']
        }
    else:
        raise Exception(f"Publishing failed: {response.text}")

def get_post_analytics(post_id):
    """投稿の分析データを取得（2025年新機能）"""
    url = f"{THREADS_API_BASE}/{post_id}/insights"
    
    params = {
        'metric': 'views,likes,replies,reposts,quotes,shares',
        'access_token': THREADS_ACCESS_TOKEN
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    return {}

@app.route('/api/threads/search', methods=['GET'])
def search_threads():
    """キーワード検索（2025年新機能）"""
    keyword = request.args.get('q', '')
    
    if not rate_limiter.can_search():
        return jsonify({
            'success': False,
            'error': 'API制限に達しました（7日間で500検索まで）'
        }), 429
    
    url = f"{THREADS_API_BASE}/threads/search"
    
    params = {
        'q': keyword,
        'access_token': THREADS_ACCESS_TOKEN
    }
    
    response = requests.get(url, params=params)
    rate_limiter.weekly_searches += 1
    
    if response.status_code == 200:
        return jsonify({
            'success': True,
            'results': response.json()
        })
    else:
        return jsonify({
            'success': False,
            'error': response.text
        }), response.status_code

# 高度なスケジューラー設定
def setup_advanced_scheduler():
    """2025年版の高度なスケジューラー"""
    
    # 最適な投稿時間（エンゲージメント最大化）
    optimal_times = [
        "07:30",  # 朝の通勤時間
        "12:15",  # ランチタイム
        "17:45",  # 退勤時間
        "21:00"   # プライムタイム
    ]
    
    for time_str in optimal_times:
        schedule.every().day.at(time_str).do(scheduled_post)
    
    # 週末特別スケジュール
    schedule.every().saturday.at("10:00").do(weekend_special_post)
    schedule.every().sunday.at("11:00").do(weekend_special_post)
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(30)
    
    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    logger.info("✅ 高度なスケジューラー起動（2025年版）")

def scheduled_post():
    """スケジュールされた投稿"""
    try:
        response = requests.post('http://localhost:5000/api/threads/auto-post')
        logger.info(f"定期投稿完了: {response.json()}")
    except Exception as e:
        logger.error(f"定期投稿エラー: {e}")

def weekend_special_post():
    """週末の特別投稿"""
    # 週末用の特別なコンテンツを生成
    pass

# アプリ起動時に追加
if __name__ == '__main__':
    setup_advanced_scheduler()
    app.run(debug=True, port=5000)
```

### ステップ3: .envファイル設定（2025年版）

```env
# Claude AI（最新モデル）
CLAUDE_MODEL=claude-opus-4-20250514
CLAUDE_API_KEY=sk-ant-api03-xxxxx

# Threads API（公式）
THREADS_ACCESS_TOKEN=YOUR_LONG_LIVED_TOKEN
THREADS_USER_ID=YOUR_THREADS_USER_ID

# API設定
THREADS_API_VERSION=v1.0
THREADS_RATE_LIMIT_POSTS=250
THREADS_RATE_LIMIT_SEARCHES=500
```

## 🎯 実装のポイント

### 1. レート制限の管理
- 投稿: 24時間で250件まで
- 検索: 7日間で500クエリまで
- リクエスト: 500万/24時間（アプリトークン）

### 2. 最適な投稿時間
- 朝: 7:00-9:00
- 昼: 12:00-13:00
- 夕方: 17:00-19:00
- 夜: 20:00-22:00

### 3. エンゲージメント最大化
- ハッシュタグ: 2-3個
- 絵文字: 適度に使用
- CTA（Call to Action）: 必須
- 文字数: 300-400文字が最適

## 💡 主要な統合済みツール

- **Hootsuite**: Threads完全対応
- **Sprout Social**: 分析機能付き
- **Make.com**: ビジュアル自動化
- **Sprinklr**: エンタープライズ向け
- **Grabyo**: 動画特化
- **Techmeme**: ニュース配信

## ✅ 今すぐ始める手順

1. **Meta開発者登録**（5分）
2. **Threads API有効化**（5分）
3. **バックエンド更新**（20分）
4. **動作確認**（10分）

合計40分で完全自動化システムの完成！

## 🔥 サポート

実装で困ったら具体的な箇所を教えてください。
最新のThreads APIドキュメントに基づいてサポートします！