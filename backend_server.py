"""
Threads自動投稿システム - バックエンドサーバー
このファイルを実行することで、実際の投稿機能が使えるようになります。
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import requests
import json
import os
from datetime import datetime, timedelta
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # フロントエンドからのアクセスを許可

# 設定ファイルの読み込み
def load_config():
    """settings.jsonから設定を読み込む"""
    try:
        with open('settings.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("settings.jsonが見つかりません。settings_example.jsonをコピーして設定してください。")
        return {}

config = load_config()

# Claude APIクライアントの初期化
claude_client = None
if config.get('CLAUDE_API_KEY'):
    claude_client = anthropic.Anthropic(api_key=config['CLAUDE_API_KEY'])

# Buffer API設定
BUFFER_API_URL = "https://api.bufferapp.com/1"
BUFFER_ACCESS_TOKEN = config.get('BUFFER_ACCESS_TOKEN')

@app.route('/')
def home():
    """ヘルスチェック用エンドポイント"""
    return jsonify({
        "status": "running",
        "message": "Threads自動投稿システム バックエンドサーバー",
        "version": "1.0.0"
    })

@app.route('/api/generate-post', methods=['POST'])
def generate_post():
    """AI投稿生成エンドポイント"""
    try:
        data = request.json
        original_text = data.get('text', '')
        genre = data.get('genre', '')
        reference_posts = data.get('reference_posts', [])
        
        if not claude_client:
            return jsonify({"error": "Claude APIが設定されていません"}), 500
        
        # プロンプトの作成
        prompt = f"""
        あなたはSNS投稿の専門家です。以下の情報を基に、魅力的なThreads投稿を生成してください。

        【元の投稿文】
        {original_text}

        【ジャンル】
        {genre}

        【参考にする人気投稿】
        {chr(10).join([f"- {post}" for post in reference_posts[:3]])}

        【要件】
        - 500文字以内
        - 読みやすく、共感を得やすい文章
        - 適切なハッシュタグを3-5個含める
        - 絵文字を適度に使用
        - CTAを含める

        改善された投稿文を生成してください。
        """
        
        # Claude APIを呼び出し
        response = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.7,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        improved_text = response.content[0].text
        
        return jsonify({
            "success": True,
            "original_text": original_text,
            "improved_text": improved_text,
            "model_used": "claude-3-haiku"
        })
        
    except Exception as e:
        logger.error(f"投稿生成エラー: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/schedule-post', methods=['POST'])
def schedule_post():
    """Buffer経由で投稿を予約"""
    try:
        data = request.json
        post_text = data.get('text', '')
        scheduled_time = data.get('scheduled_time')
        image_urls = data.get('image_urls', [])
        
        if not BUFFER_ACCESS_TOKEN:
            return jsonify({"error": "Buffer APIが設定されていません"}), 500
        
        # Buffer APIに送信するデータ
        buffer_data = {
            "text": post_text,
            "profile_ids": [config.get('BUFFER_PROFILE_ID')],
            "scheduled_at": scheduled_time,
            "media": {
                "link": image_urls[0] if image_urls else None,
                "description": "Threads投稿画像"
            } if image_urls else None
        }
        
        # Buffer APIを呼び出し
        headers = {
            "Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{BUFFER_API_URL}/updates/create.json",
            headers=headers,
            json=buffer_data
        )
        
        if response.status_code == 200:
            return jsonify({
                "success": True,
                "buffer_id": response.json().get('id'),
                "scheduled_time": scheduled_time
            })
        else:
            return jsonify({
                "error": "Buffer API error",
                "details": response.json()
            }), response.status_code
            
    except Exception as e:
        logger.error(f"投稿予約エラー: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/process-csv', methods=['POST'])
def process_csv():
    """CSVデータを処理して投稿候補を生成"""
    try:
        data = request.json
        csv_data = data.get('csv_data', [])
        company_concepts = data.get('company_concepts', [])
        
        # いいね数でソート
        sorted_posts = sorted(csv_data, key=lambda x: x.get('likes', 0), reverse=True)
        
        # 上位10件を取得
        top_posts = sorted_posts[:10]
        
        # 各投稿に対してAI改善を適用
        processed_posts = []
        for post in top_posts:
            # ここで自社構想とマッチング
            matched_concept = find_matching_concept(post, company_concepts)
            
            if claude_client and matched_concept:
                # AI生成
                improved = generate_with_concept(post, matched_concept)
                processed_posts.append(improved)
            else:
                processed_posts.append(post)
        
        return jsonify({
            "success": True,
            "processed_count": len(processed_posts),
            "posts": processed_posts
        })
        
    except Exception as e:
        logger.error(f"CSV処理エラー: {str(e)}")
        return jsonify({"error": str(e)}), 500

def find_matching_concept(post, concepts):
    """投稿と自社構想のマッチング"""
    post_genre = post.get('genre', '').lower()
    for concept in concepts:
        if concept.get('genre', '').lower() in post_genre:
            return concept
    return None

def generate_with_concept(post, concept):
    """自社構想を反映した投稿生成"""
    try:
        prompt = f"""
        以下の人気投稿を参考に、自社の構想を反映した新しい投稿を作成してください。

        【参考投稿】
        {post.get('text', '')}
        いいね数: {post.get('likes', 0)}

        【自社構想】
        キーワード: {concept.get('keywords', '')}
        ジャンル: {concept.get('genre', '')}

        【要件】
        - 元の投稿の良い要素を活かす
        - 自社の構想を自然に組み込む
        - 500文字以内
        - 適切なハッシュタグを含める
        """
        
        response = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        
        post['text'] = response.content[0].text
        post['concept_source'] = concept.get('keywords', '')
        return post
        
    except Exception as e:
        logger.error(f"構想反映エラー: {str(e)}")
        return post

@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    """設定の取得・更新"""
    if request.method == 'GET':
        # APIキーは隠して返す
        safe_config = {
            "claude_configured": bool(config.get('CLAUDE_API_KEY')),
            "buffer_configured": bool(config.get('BUFFER_ACCESS_TOKEN')),
            "profile_id": config.get('BUFFER_PROFILE_ID', '')
        }
        return jsonify(safe_config)
    
    elif request.method == 'POST':
        try:
            new_settings = request.json
            
            # 設定を更新
            if 'CLAUDE_API_KEY' in new_settings:
                config['CLAUDE_API_KEY'] = new_settings['CLAUDE_API_KEY']
            if 'BUFFER_ACCESS_TOKEN' in new_settings:
                config['BUFFER_ACCESS_TOKEN'] = new_settings['BUFFER_ACCESS_TOKEN']
            if 'BUFFER_PROFILE_ID' in new_settings:
                config['BUFFER_PROFILE_ID'] = new_settings['BUFFER_PROFILE_ID']
            
            # ファイルに保存
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            return jsonify({"success": True, "message": "設定を更新しました"})
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 設定ファイルのサンプルを作成
    if not os.path.exists('settings.json') and not os.path.exists('settings_example.json'):
        example_settings = {
            "CLAUDE_API_KEY": "your-claude-api-key-here",
            "BUFFER_ACCESS_TOKEN": "your-buffer-token-here",
            "BUFFER_PROFILE_ID": "your-buffer-profile-id",
            "GOOGLE_SHEETS_ID": "optional-google-sheets-id"
        }
        with open('settings_example.json', 'w', encoding='utf-8') as f:
            json.dump(example_settings, f, ensure_ascii=False, indent=2)
        print("settings_example.jsonを作成しました。")
        print("settings.jsonにリネームして、APIキーを設定してください。")
    
    # サーバー起動
    print("="*50)
    print("Threads自動投稿システム - バックエンドサーバー")
    print("="*50)
    print("URL: http://localhost:5000")
    print("終了: Ctrl+C")
    print("="*50)
    
    app.run(debug=True, port=5000)