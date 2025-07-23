"""
Threads自動投稿システム - 完全版バックエンドサーバー
要件定義書v3.2に完全準拠した実装
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import anthropic
import requests
import json
import os
import sqlite3
from datetime import datetime, timedelta
import logging
import uuid
import threading
import time
import schedule
from werkzeug.utils import secure_filename
import pandas as pd
from pathlib import Path

# 新しい多様性管理システムをインポート
from post_diversity_manager import PostDiversityManager
from enhanced_post_generator import EnhancedPostGenerator

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('threads_auto_post.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 設定
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# アップロードフォルダの作成
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class Database:
    """SQLiteデータベースマネージャー"""
    
    def __init__(self, db_path='threads_auto_post.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """データベースとテーブルの初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 投稿データテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                image_urls TEXT,
                genre TEXT NOT NULL,
                scheduled_time TEXT NOT NULL,
                buffer_sent_time TEXT,
                status TEXT DEFAULT 'pending',
                concept_source TEXT,
                reference_post TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 自社構想テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS company_concepts (
                id TEXT PRIMARY KEY,
                keywords TEXT NOT NULL,
                genre TEXT NOT NULL,
                reflection_status BOOLEAN DEFAULT FALSE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 設定テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("データベースの初期化完了")
    
    def get_connection(self):
        """データベース接続を取得"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query, params=None, fetch=False):
        """クエリを実行"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                result = cursor.fetchall()
                conn.close()
                return result
            else:
                conn.commit()
                conn.close()
                return cursor.rowcount
        except Exception as e:
            conn.close()
            raise e

# データベースインスタンス
db = Database()

# 投稿多様性管理インスタンス
diversity_manager = PostDiversityManager()
enhanced_generator = EnhancedPostGenerator()

class ConfigManager:
    """設定管理クラス"""
    
    @staticmethod
    def get_setting(key):
        """設定値を取得"""
        result = db.execute_query(
            "SELECT value FROM settings WHERE key = ?", 
            (key,), 
            fetch=True
        )
        return result[0][0] if result else None
    
    @staticmethod
    def set_setting(key, value):
        """設定値を保存"""
        db.execute_query(
            "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
            (key, value, datetime.now().isoformat())
        )
    
    @staticmethod
    def load_config():
        """すべての設定を読み込み"""
        try:
            with open('settings.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # データベースに保存
            for key, value in config.items():
                ConfigManager.set_setting(key, value)
                
            return config
        except FileNotFoundError:
            logger.warning("settings.jsonが見つかりません")
            return {}

# 設定の読み込み
config = ConfigManager.load_config()

# Claude APIクライアント
claude_client = None
claude_api_key = ConfigManager.get_setting('CLAUDE_API_KEY')
if claude_api_key:
    claude_client = anthropic.Anthropic(api_key=claude_api_key)

# Buffer API設定
BUFFER_API_URL = "https://api.bufferapp.com/1"
BUFFER_ACCESS_TOKEN = ConfigManager.get_setting('BUFFER_ACCESS_TOKEN')

def allowed_file(filename):
    """ファイル拡張子チェック"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    """ヘルスチェック"""
    return jsonify({
        "status": "running",
        "message": "Threads自動投稿システム v3.2",
        "version": "3.2.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/generate-post', methods=['POST'])
def generate_post():
    """AI投稿生成エンドポイント（多様性強化版）"""
    try:
        data = request.json
        original_text = data.get('text', '')
        genre = data.get('genre', '')
        reference_posts = data.get('reference_posts', [])
        use_diversity = data.get('use_diversity', True)  # 多様性機能の有効/無効
        
        if not claude_client:
            # 多様性マネージャーで生成（Claude APIなしでも動作）
            if use_diversity:
                improved_text = diversity_manager.generate_unique_post(
                    original_text, genre, reference_posts
                )
                logger.info(f"多様性マネージャーで投稿生成: {len(improved_text)}文字")
                
                return jsonify({
                    "success": True,
                    "original_text": original_text,
                    "improved_text": improved_text,
                    "model_used": "diversity_manager",
                    "character_count": len(improved_text),
                    "is_unique": not diversity_manager.is_duplicate(improved_text)
                })
            else:
                return jsonify({"error": "Claude APIが設定されていません"}), 500
        
        # 強化版プロンプトの作成
        if use_diversity:
            prompt = enhanced_generator.create_enhanced_prompt(
                original_text, genre, reference_posts=reference_posts
            )
        else:
            # 従来のプロンプト（後方互換性のため）
            prompt = f"""
あなたはThreads投稿の専門家です。以下の要件に従って魅力的な投稿を生成してください。

【元の投稿文】
{original_text}

【ジャンル】
{genre}

【参考にする人気投稿】
{chr(10).join([f"- {post}" for post in reference_posts[:3]])}

【生成要件】
- 500文字以内厳守
- エンゲージメントを高める文章構成
- 適切なハッシュタグを3-5個含める
- 絵文字を効果的に使用
- 明確なCTA（Call to Action）を含める
- 読みやすい改行と構成
- ターゲット読者に響く内容

【出力形式】
改善された投稿文のみを出力してください。説明や前置きは不要です。
            """
        
        # Claude API呼び出し
        response = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.8 if use_diversity else 0.7,  # 多様性モードでは温度を上げる
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        improved_text = response.content[0].text
        
        # 重複チェック
        is_duplicate = diversity_manager.is_duplicate(improved_text)
        
        # 重複している場合は再生成（最大3回試行）
        retry_count = 0
        while is_duplicate and retry_count < 3 and use_diversity:
            logger.warning(f"重複検出: 再生成試行 {retry_count + 1}/3")
            
            # 温度を上げて多様性を増す
            response = claude_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=min(0.9 + (retry_count * 0.05), 1.0),
                messages=[{
                    "role": "user",
                    "content": prompt + "\n\n【追加指示】以前と全く異なる切り口で作成してください。"
                }]
            )
            
            improved_text = response.content[0].text
            is_duplicate = diversity_manager.is_duplicate(improved_text)
            retry_count += 1
        
        logger.info(f"AI投稿生成完了: {len(improved_text)}文字")
        
        return jsonify({
            "success": True,
            "original_text": original_text,
            "improved_text": improved_text,
            "model_used": "claude-3-haiku-20240307",
            "character_count": len(improved_text),
            "is_unique": not is_duplicate,
            "retry_attempts": retry_count
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
        
        # 15分前の送信時刻を計算
        scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
        buffer_send_time = scheduled_dt - timedelta(minutes=15)
        
        # Buffer APIに送信するデータ
        buffer_data = {
            "text": post_text,
            "profile_ids": [ConfigManager.get_setting('BUFFER_PROFILE_ID')],
            "scheduled_at": buffer_send_time.isoformat(),
        }
        
        # 画像URLがある場合は追加
        if image_urls:
            buffer_data["media"] = {
                "link": image_urls[0],
                "description": "Threads投稿画像"
            }
        
        # Buffer API呼び出し
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
            buffer_response = response.json()
            logger.info(f"Buffer予約完了: {buffer_response.get('id')}")
            
            return jsonify({
                "success": True,
                "buffer_id": buffer_response.get('id'),
                "scheduled_time": scheduled_time,
                "buffer_send_time": buffer_send_time.isoformat()
            })
        else:
            logger.error(f"Buffer API error: {response.status_code} - {response.text}")
            return jsonify({
                "error": "Buffer API error",
                "details": response.json() if response.content else "No response body"
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
        
        # いいね数でソート（要件定義書準拠）
        sorted_posts = sorted(csv_data, key=lambda x: x.get('likes', 0), reverse=True)
        
        # 上位10件を取得
        top_posts = sorted_posts[:10]
        
        processed_posts = []
        for post in top_posts:
            # 自社構想とのマッチング
            matched_concept = find_matching_concept(post, company_concepts)
            
            if claude_client and matched_concept:
                # AI生成で自社構想を反映
                improved_post = generate_with_concept(post, matched_concept)
                processed_posts.append(improved_post)
            else:
                # そのまま追加
                processed_posts.append(post)
        
        logger.info(f"CSV処理完了: {len(processed_posts)}件の投稿候補を生成")
        
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
以下の人気投稿を参考に、自社の構想を自然に組み込んだ新しい投稿を作成してください。

【参考投稿】
{post.get('text', '')}
いいね数: {post.get('likes', 0)}

【自社構想】
キーワード: {concept.get('keywords', '')}
ジャンル: {concept.get('genre', '')}

【要件】
- 元の投稿の魅力的な要素を活かす
- 自社の構想を自然に組み込む
- 500文字以内
- 適切なハッシュタグを含める
- エンゲージメントを高める構成

改善された投稿文のみを出力してください。
        """
        
        response = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        
        post['text'] = response.content[0].text
        post['concept_source'] = concept.get('keywords', '')
        
        logger.info(f"構想反映投稿生成完了: {concept.get('keywords', '')}")
        return post
        
    except Exception as e:
        logger.error(f"構想反映エラー: {str(e)}")
        return post

@app.route('/api/posts', methods=['GET', 'POST'])
def posts():
    """投稿データの取得・保存"""
    if request.method == 'GET':
        try:
            # データベースから投稿を取得
            result = db.execute_query(
                "SELECT * FROM posts ORDER BY created_at DESC",
                fetch=True
            )
            
            posts_data = []
            for row in result:
                post = {
                    "id": row[0],
                    "text": row[1],
                    "imageUrls": json.loads(row[2]) if row[2] else [],
                    "genre": row[3],
                    "scheduledTime": row[4],
                    "bufferSentTime": row[5],
                    "status": row[6],
                    "conceptSource": row[7],
                    "referencePost": row[8],
                    "createdAt": row[9],
                    "updatedAt": row[10]
                }
                posts_data.append(post)
            
            return jsonify({
                "success": True,
                "posts": posts_data
            })
            
        except Exception as e:
            logger.error(f"投稿取得エラー: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            posts_to_save = data.get('posts', [])
            
            saved_count = 0
            for post in posts_to_save:
                post_id = post.get('id', str(uuid.uuid4()))
                
                db.execute_query('''
                    INSERT OR REPLACE INTO posts 
                    (id, text, image_urls, genre, scheduled_time, buffer_sent_time, 
                     status, concept_source, reference_post, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    post_id,
                    post.get('text', ''),
                    json.dumps(post.get('imageUrls', [])),
                    post.get('genre', ''),
                    post.get('scheduledTime', ''),
                    post.get('bufferSentTime'),
                    post.get('status', 'pending'),
                    post.get('conceptSource'),
                    post.get('referencePost'),
                    post.get('createdAt', datetime.now().isoformat()),
                    datetime.now().isoformat()
                ))
                saved_count += 1
            
            logger.info(f"投稿保存完了: {saved_count}件")
            
            return jsonify({
                "success": True,
                "saved_count": saved_count
            })
            
        except Exception as e:
            logger.error(f"投稿保存エラー: {str(e)}")
            return jsonify({"error": str(e)}), 500

@app.route('/api/posts/<post_id>', methods=['PUT', 'DELETE'])
def post_operations(post_id):
    """投稿の更新・削除"""
    if request.method == 'PUT':
        try:
            data = request.json
            
            db.execute_query('''
                UPDATE posts SET 
                text = ?, genre = ?, scheduled_time = ?, 
                status = ?, updated_at = ?
                WHERE id = ?
            ''', (
                data.get('text'),
                data.get('genre'),
                data.get('scheduledTime'),
                data.get('status'),
                datetime.now().isoformat(),
                post_id
            ))
            
            logger.info(f"投稿更新完了: {post_id}")
            
            return jsonify({
                "success": True,
                "post_id": post_id
            })
            
        except Exception as e:
            logger.error(f"投稿更新エラー: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            db.execute_query("DELETE FROM posts WHERE id = ?", (post_id,))
            
            logger.info(f"投稿削除完了: {post_id}")
            
            return jsonify({
                "success": True,
                "deleted_id": post_id
            })
            
        except Exception as e:
            logger.error(f"投稿削除エラー: {str(e)}")
            return jsonify({"error": str(e)}), 500

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    """画像アップロード"""
    try:
        if 'image' not in request.files:
            return jsonify({"error": "画像ファイルが必要です"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "ファイルが選択されていません"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # ユニークなファイル名を生成
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # アクセス可能なURLを生成
            file_url = f"http://localhost:5000/uploads/{unique_filename}"
            
            logger.info(f"画像アップロード完了: {unique_filename}")
            
            return jsonify({
                "success": True,
                "url": file_url,
                "filename": unique_filename
            })
        else:
            return jsonify({"error": "サポートされていないファイル形式です"}), 400
            
    except Exception as e:
        logger.error(f"画像アップロードエラー: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """アップロードされた画像の配信"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/concepts', methods=['GET', 'POST'])
def concepts():
    """自社構想の取得・保存"""
    if request.method == 'GET':
        try:
            result = db.execute_query(
                "SELECT * FROM company_concepts ORDER BY created_at DESC",
                fetch=True
            )
            
            concepts_data = []
            for row in result:
                concept = {
                    "id": row[0],
                    "keywords": row[1],
                    "genre": row[2],
                    "reflectionStatus": bool(row[3]),
                    "createdAt": row[4]
                }
                concepts_data.append(concept)
            
            return jsonify({
                "success": True,
                "concepts": concepts_data
            })
            
        except Exception as e:
            logger.error(f"自社構想取得エラー: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            concepts_to_save = data.get('concepts', [])
            
            saved_count = 0
            for concept in concepts_to_save:
                concept_id = concept.get('id', str(uuid.uuid4()))
                
                db.execute_query('''
                    INSERT OR REPLACE INTO company_concepts 
                    (id, keywords, genre, reflection_status, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    concept_id,
                    concept.get('keywords', ''),
                    concept.get('genre', ''),
                    concept.get('reflectionStatus', False),
                    concept.get('createdAt', datetime.now().isoformat())
                ))
                saved_count += 1
            
            logger.info(f"自社構想保存完了: {saved_count}件")
            
            return jsonify({
                "success": True,
                "saved_count": saved_count
            })
            
        except Exception as e:
            logger.error(f"自社構想保存エラー: {str(e)}")
            return jsonify({"error": str(e)}), 500

@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    """設定の取得・更新"""
    if request.method == 'GET':
        try:
            claude_configured = bool(ConfigManager.get_setting('CLAUDE_API_KEY'))
            buffer_configured = bool(ConfigManager.get_setting('BUFFER_ACCESS_TOKEN'))
            profile_id = ConfigManager.get_setting('BUFFER_PROFILE_ID') or ''
            
            return jsonify({
                "claude_configured": claude_configured,
                "buffer_configured": buffer_configured,
                "profile_id": profile_id
            })
            
        except Exception as e:
            logger.error(f"設定取得エラー: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'POST':
        try:
            new_settings = request.json
            
            # 設定を更新
            for key, value in new_settings.items():
                if key in ['CLAUDE_API_KEY', 'BUFFER_ACCESS_TOKEN', 'BUFFER_PROFILE_ID']:
                    ConfigManager.set_setting(key, value)
            
            # Claude APIクライアントを再初期化
            global claude_client
            claude_api_key = ConfigManager.get_setting('CLAUDE_API_KEY')
            if claude_api_key:
                claude_client = anthropic.Anthropic(api_key=claude_api_key)
            
            # Buffer設定を更新
            global BUFFER_ACCESS_TOKEN
            BUFFER_ACCESS_TOKEN = ConfigManager.get_setting('BUFFER_ACCESS_TOKEN')
            
            logger.info("設定更新完了")
            
            return jsonify({
                "success": True,
                "message": "設定を更新しました"
            })
            
        except Exception as e:
            logger.error(f"設定更新エラー: {str(e)}")
            return jsonify({"error": str(e)}), 500

# スケジューラー機能（要件定義書の15分前送信仕様）
class PostScheduler:
    """投稿スケジューラー"""
    
    def __init__(self):
        self.running = False
    
    def start(self):
        """スケジューラーを開始"""
        if self.running:
            return
        
        self.running = True
        schedule.every(5).minutes.do(self.check_pending_posts)
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(30)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("投稿スケジューラーを開始しました")
    
    def check_pending_posts(self):
        """投稿予定をチェックして送信"""
        try:
            now = datetime.now()
            # 現在時刻から15分後の投稿を検索
            target_time = now + timedelta(minutes=15)
            
            result = db.execute_query('''
                SELECT * FROM posts 
                WHERE status = 'pending' 
                AND datetime(scheduled_time) <= datetime(?)
                AND datetime(scheduled_time) > datetime(?)
            ''', (
                target_time.isoformat(),
                now.isoformat()
            ), fetch=True)
            
            for row in result:
                post_id = row[0]
                try:
                    # Buffer APIに送信
                    self.send_to_buffer(row)
                    
                    # ステータスを更新
                    db.execute_query(
                        "UPDATE posts SET status = 'scheduled', buffer_sent_time = ? WHERE id = ?",
                        (now.isoformat(), post_id)
                    )
                    
                    logger.info(f"投稿をBuffer送信: {post_id}")
                    
                except Exception as e:
                    logger.error(f"Buffer送信失敗 {post_id}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"スケジューラーエラー: {str(e)}")
    
    def send_to_buffer(self, post_row):
        """Buffer APIに投稿を送信"""
        if not BUFFER_ACCESS_TOKEN:
            raise Exception("Buffer APIが設定されていません")
        
        text = post_row[1]
        image_urls = json.loads(post_row[2]) if post_row[2] else []
        
        buffer_data = {
            "text": text,
            "profile_ids": [ConfigManager.get_setting('BUFFER_PROFILE_ID')],
            "now": True  # 即座に投稿
        }
        
        if image_urls:
            buffer_data["media"] = {
                "link": image_urls[0],
                "description": "Threads投稿画像"
            }
        
        headers = {
            "Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{BUFFER_API_URL}/updates/create.json",
            headers=headers,
            json=buffer_data
        )
        
        if response.status_code != 200:
            raise Exception(f"Buffer API error: {response.status_code}")
    
    def stop(self):
        """スケジューラーを停止"""
        self.running = False
        logger.info("投稿スケジューラーを停止しました")

# スケジューラーインスタンス
scheduler = PostScheduler()

if __name__ == '__main__':
    # 設定ファイルのサンプルを作成
    if not os.path.exists('settings.json'):
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
    
    # スケジューラーを開始
    scheduler.start()
    
    # サーバー起動
    print("="*60)
    print("Threads自動投稿システム v3.2 - 完全版バックエンドサーバー")
    print("="*60)
    print("URL: http://localhost:5000")
    print("管理画面: http://localhost:5000/admin")
    print("データベース: threads_auto_post.db")
    print("ログファイル: threads_auto_post.log")
    print("終了: Ctrl+C")
    print("="*60)
    
    try:
        app.run(debug=True, port=5000, threaded=True)
    finally:
        scheduler.stop()