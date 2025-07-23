"""
Threads自動投稿システム - 完全版バックエンドサーバー（修正版）
多様性システムを統合し、完全に動作するバージョン
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

# 多様性システムをインポート
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
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
CORS(app, origins=['http://localhost:5173', 'http://localhost:3000'])

# 設定
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# アップロードフォルダの作成
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('csv_input', exist_ok=True)
os.makedirs('csv_processed', exist_ok=True)

# 多様性マネージャーのインスタンス
diversity_manager = PostDiversityManager()
enhanced_generator = EnhancedPostGenerator()

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
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                is_unique BOOLEAN DEFAULT TRUE,
                retry_attempts INTEGER DEFAULT 0
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
        
        # スクレイピング履歴テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_history (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                posts_generated INTEGER DEFAULT 0,
                error TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
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

class ConfigManager:
    """設定管理クラス"""
    
    @staticmethod
    def get_setting(key, default=None):
        """設定値を取得"""
        result = db.execute_query(
            "SELECT value FROM settings WHERE key = ?", 
            (key,), 
            fetch=True
        )
        return result[0][0] if result else default
    
    @staticmethod
    def set_setting(key, value):
        """設定値を保存"""
        db.execute_query(
            "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
            (key, str(value), datetime.now().isoformat())
        )
    
    @staticmethod
    def load_config():
        """すべての設定を読み込み"""
        try:
            # 設定ファイルが存在する場合は読み込む
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # データベースに保存
                for key, value in config.items():
                    ConfigManager.set_setting(key, value)
                    
                return config
            else:
                # デフォルト設定を作成
                default_config = {
                    "CLAUDE_API_KEY": "",
                    "BUFFER_ACCESS_TOKEN": "",
                    "BUFFER_PROFILE_ID": "",
                    "csv_watch_path": "./csv_input",
                    "post_interval": 60,
                    "scraping_interval": 8,
                    "daily_post_limit": 10,
                    "post_start_time": "09:00",
                    "post_end_time": "21:00",
                    "enable_ai_generation": True,
                    "enable_buffer_scheduling": True,
                    "enable_auto_scraping": True
                }
                
                # デフォルト設定を保存
                for key, value in default_config.items():
                    ConfigManager.set_setting(key, value)
                
                return default_config
                
        except Exception as e:
            logger.error(f"設定読み込みエラー: {e}")
            return {}

# 設定の読み込み
config = ConfigManager.load_config()

# Claude APIクライアント
claude_client = None
claude_api_key = ConfigManager.get_setting('CLAUDE_API_KEY')
if claude_api_key:
    try:
        claude_client = anthropic.Anthropic(api_key=claude_api_key)
        logger.info("Claude APIクライアント初期化完了")
    except Exception as e:
        logger.error(f"Claude API初期化エラー: {e}")

# Buffer API設定
BUFFER_API_URL = "https://api.bufferapp.com/1"
BUFFER_ACCESS_TOKEN = ConfigManager.get_setting('BUFFER_ACCESS_TOKEN')

# 自動化の状態
automation_running = False
automation_thread = None

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
        "timestamp": datetime.now().isoformat(),
        "database": "connected",
        "claude_api": "configured" if claude_client else "not configured",
        "buffer_api": "configured" if BUFFER_ACCESS_TOKEN else "not configured"
    })

@app.route('/api/generate-post', methods=['POST'])
def generate_post():
    """AI投稿生成エンドポイント（多様性強化版）"""
    try:
        data = request.json
        original_text = data.get('text', '')
        genre = data.get('genre', '')
        reference_posts = data.get('reference_posts', [])
        use_diversity = data.get('use_diversity', True)
        
        if not claude_client and use_diversity:
            # Claude APIなしでも多様性システムで生成
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
        
        if not claude_client:
            return jsonify({"error": "Claude APIが設定されていません"}), 500
        
        # 強化版プロンプトの作成
        if use_diversity:
            prompt = enhanced_generator.create_enhanced_prompt(
                original_text, genre, reference_posts=reference_posts
            )
        else:
            # 従来のプロンプト
            prompt = f"""
あなたはThreads投稿の専門家です。以下の要件に従って魅力的な投稿を生成してください。

【元の投稿文】
{original_text}

【ジャンル】
{genre}

【生成要件】
- 500文字以内厳守
- エンゲージメントを高める文章構成
- 適切なハッシュタグを3-5個含める
- 絵文字を効果的に使用
- 明確なCTA（Call to Action）を含める

改善された投稿文のみを出力してください。
"""
        
        # Claude API呼び出し
        response = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.8 if use_diversity else 0.7,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        improved_text = response.content[0].text
        
        # 重複チェック
        is_duplicate = diversity_manager.is_duplicate(improved_text)
        retry_count = 0
        
        # 重複している場合は再生成
        while is_duplicate and retry_count < 3 and use_diversity:
            logger.warning(f"重複検出: 再生成試行 {retry_count + 1}/3")
            
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

@app.route('/api/posts', methods=['GET', 'POST'])
def posts():
    """投稿データの取得・保存"""
    if request.method == 'GET':
        try:
            # ページネーション対応
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 100))
            offset = (page - 1) * limit
            
            # 総数を取得
            total_result = db.execute_query(
                "SELECT COUNT(*) FROM posts",
                fetch=True
            )
            total = total_result[0][0] if total_result else 0
            
            # データベースから投稿を取得
            result = db.execute_query(
                "SELECT * FROM posts ORDER BY scheduled_time DESC LIMIT ? OFFSET ?",
                (limit, offset),
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
                    "updatedAt": row[10],
                    "isUnique": row[11] if len(row) > 11 else True,
                    "retryAttempts": row[12] if len(row) > 12 else 0
                }
                posts_data.append(post)
            
            return jsonify({
                "success": True,
                "posts": posts_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "totalPages": (total + limit - 1) // limit
                }
            })
            
        except Exception as e:
            logger.error(f"投稿取得エラー: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'POST':
        try:
            # フォームデータまたはJSONを処理
            if request.content_type and 'multipart/form-data' in request.content_type:
                # 手動投稿の処理
                text = request.form.get('text', '')
                genre = request.form.get('genre', '')
                scheduled_time = request.form.get('scheduledTime', '')
                ai_mode = request.form.get('aiMode', 'false') == 'true'
                use_diversity = request.form.get('useDiversity', 'true') == 'true'
                
                # 画像の処理
                image_urls = []
                if 'images' in request.files:
                    files = request.files.getlist('images')
                    for file in files:
                        if file and allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            filename = f"{timestamp}_{filename}"
                            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                            file.save(filepath)
                            image_urls.append(f"/uploads/{filename}")
                
                # AI生成モードの場合
                if ai_mode and text:
                    response = generate_post_internal(text, genre, use_diversity)
                    if response['success']:
                        text = response['improved_text']
                
                # 投稿を保存
                post_id = str(uuid.uuid4())
                
                db.execute_query('''
                    INSERT INTO posts 
                    (id, text, image_urls, genre, scheduled_time, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    post_id,
                    text,
                    json.dumps(image_urls),
                    genre,
                    scheduled_time,
                    'pending',
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                
                logger.info(f"手動投稿作成完了: {post_id}")
                
                return jsonify({
                    "success": True,
                    "post_id": post_id,
                    "message": "投稿が作成されました"
                })
                
            else:
                # JSON形式の一括保存
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

def generate_post_internal(text, genre, use_diversity=True):
    """内部用の投稿生成関数"""
    try:
        if use_diversity and not claude_client:
            improved_text = diversity_manager.generate_unique_post(text, genre)
            return {
                "success": True,
                "improved_text": improved_text,
                "is_unique": not diversity_manager.is_duplicate(improved_text)
            }
        
        if not claude_client:
            return {"success": False, "error": "Claude APIが設定されていません"}
        
        # プロンプト作成と生成処理（上記と同じ）
        if use_diversity:
            prompt = enhanced_generator.create_enhanced_prompt(text, genre)
        else:
            prompt = f"""
あなたはThreads投稿の専門家です。以下の投稿を改善してください。

【元の投稿文】
{text}

【ジャンル】
{genre}

【要件】
- 500文字以内
- ハッシュタグ3-5個
- 絵文字を効果的に使用
- エンゲージメントを高める

改善された投稿文のみを出力してください。
"""
        
        response = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.8,
            messages=[{"role": "user", "content": prompt}]
        )
        
        improved_text = response.content[0].text
        
        return {
            "success": True,
            "improved_text": improved_text,
            "is_unique": not diversity_manager.is_duplicate(improved_text)
        }
        
    except Exception as e:
        logger.error(f"内部投稿生成エラー: {str(e)}")
        return {"success": False, "error": str(e)}

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

@app.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    """ダッシュボード統計情報"""
    try:
        # 総投稿数
        total_result = db.execute_query(
            "SELECT COUNT(*) FROM posts",
            fetch=True
        )
        total_posts = total_result[0][0] if total_result else 0
        
        # ステータス別カウント
        status_counts = {
            'scheduled': 0,
            'posted': 0,
            'failed': 0,
            'pending': 0
        }
        
        status_result = db.execute_query(
            "SELECT status, COUNT(*) FROM posts GROUP BY status",
            fetch=True
        )
        
        for row in status_result:
            if row[0] in status_counts:
                status_counts[row[0]] = row[1]
        
        # 今日の投稿数
        today = datetime.now().date().isoformat()
        today_result = db.execute_query(
            "SELECT COUNT(*) FROM posts WHERE DATE(scheduled_time) = ?",
            (today,),
            fetch=True
        )
        today_posts = today_result[0][0] if today_result else 0
        
        # 自動化ステータス
        automation_status = 'running' if automation_running else 'stopped'
        
        # 最後のスクレイピング情報
        last_scraping = db.execute_query(
            "SELECT timestamp, status FROM scraping_history ORDER BY timestamp DESC LIMIT 1",
            fetch=True
        )
        
        stats = {
            "totalPosts": total_posts,
            "scheduledPosts": status_counts['scheduled'] + status_counts['pending'],
            "completedPosts": status_counts['posted'],
            "failedPosts": status_counts['failed'],
            "todayPosts": today_posts,
            "automationStatus": automation_status,
            "lastScraping": last_scraping[0][0] if last_scraping else None,
            "nextScraping": calculate_next_scraping_time() if automation_running else None,
            "nextPost": calculate_next_post_time() if automation_running else None
        }
        
        return jsonify({
            "success": True,
            "data": stats
        })
        
    except Exception as e:
        logger.error(f"ダッシュボード統計エラー: {str(e)}")
        return jsonify({"error": str(e)}), 500

def calculate_next_scraping_time():
    """次回のスクレイピング時刻を計算"""
    interval = ConfigManager.get_setting('scraping_interval', 8)
    last_scraping = db.execute_query(
        "SELECT timestamp FROM scraping_history ORDER BY timestamp DESC LIMIT 1",
        fetch=True
    )
    
    if last_scraping:
        last_time = datetime.fromisoformat(last_scraping[0][0])
        next_time = last_time + timedelta(hours=int(interval))
        return next_time.isoformat()
    else:
        return datetime.now().isoformat()

def calculate_next_post_time():
    """次回の投稿時刻を計算"""
    pending_posts = db.execute_query(
        "SELECT scheduled_time FROM posts WHERE status = 'pending' ORDER BY scheduled_time ASC LIMIT 1",
        fetch=True
    )
    
    if pending_posts:
        return pending_posts[0][0]
    else:
        return None

@app.route('/api/scraping/history', methods=['GET'])
def scraping_history():
    """スクレイピング履歴の取得"""
    try:
        limit = int(request.args.get('limit', 50))
        
        result = db.execute_query(
            "SELECT * FROM scraping_history ORDER BY timestamp DESC LIMIT ?",
            (limit,),
            fetch=True
        )
        
        history = []
        for row in result:
            history.append({
                "id": row[0],
                "timestamp": row[1],
                "status": row[2],
                "message": row[3],
                "postsGenerated": row[4] if len(row) > 4 else 0,
                "error": row[5] if len(row) > 5 else None
            })
        
        return jsonify({
            "success": True,
            "data": history
        })
        
    except Exception as e:
        logger.error(f"スクレイピング履歴取得エラー: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/scraping/trigger', methods=['POST'])
def trigger_scraping():
    """手動スクレイピングの実行"""
    try:
        # スクレイピング実行（モック）
        scraping_id = str(uuid.uuid4())
        
        # 履歴に記録
        db.execute_query('''
            INSERT INTO scraping_history 
            (id, timestamp, status, message, posts_generated)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            scraping_id,
            datetime.now().isoformat(),
            'success',
            'Manual scraping completed',
            10  # モックデータ
        ))
        
        # モック投稿データを生成
        generate_mock_posts(10)
        
        logger.info("手動スクレイピング実行完了")
        
        return jsonify({
            "success": True,
            "data": {
                "status": "completed",
                "message": "スクレイピングが完了しました",
                "postsGenerated": 10
            }
        })
        
    except Exception as e:
        logger.error(f"スクレイピング実行エラー: {str(e)}")
        return jsonify({"error": str(e)}), 500

def generate_mock_posts(count=10):
    """モック投稿データを生成"""
    genres = ['ゲーム', 'エンタメ', 'ビジネス', 'マーケティング']
    
    for i in range(count):
        genre = genres[i % len(genres)]
        scheduled_time = datetime.now() + timedelta(hours=i+1, minutes=i*10)
        
        # 多様性システムでユニークな投稿を生成
        base_text = f"{genre}に関する興味深い投稿 #{i+1}"
        post_text = diversity_manager.generate_unique_post(base_text, genre)
        
        post_id = str(uuid.uuid4())
        
        db.execute_query('''
            INSERT INTO posts 
            (id, text, image_urls, genre, scheduled_time, status, is_unique, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            post_id,
            post_text,
            json.dumps([]),
            genre,
            scheduled_time.isoformat(),
            'pending',
            True,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
    
    logger.info(f"モック投稿データ {count}件を生成")

@app.route('/api/automation/start', methods=['POST'])
def start_automation():
    """自動化の開始"""
    global automation_running, automation_thread
    
    try:
        if automation_running:
            return jsonify({
                "success": True,
                "data": {"status": "already_running", "message": "自動化は既に実行中です"}
            })
        
        automation_running = True
        
        # 自動化スレッドを開始
        automation_thread = threading.Thread(target=automation_worker)
        automation_thread.daemon = True
        automation_thread.start()
        
        logger.info("自動化を開始しました")
        
        return jsonify({
            "success": True,
            "data": {"status": "started", "message": "自動化を開始しました"}
        })
        
    except Exception as e:
        logger.error(f"自動化開始エラー: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/automation/stop', methods=['POST'])
def stop_automation():
    """自動化の停止"""
    global automation_running
    
    try:
        automation_running = False
        
        logger.info("自動化を停止しました")
        
        return jsonify({
            "success": True,
            "data": {"status": "stopped", "message": "自動化を停止しました"}
        })
        
    except Exception as e:
        logger.error(f"自動化停止エラー: {str(e)}")
        return jsonify({"error": str(e)}), 500

def automation_worker():
    """自動化ワーカースレッド"""
    global automation_running
    
    logger.info("自動化ワーカーを開始")
    
    while automation_running:
        try:
            # 現在時刻をチェック
            now = datetime.now()
            current_time = now.strftime('%H:%M')
            
            # 設定を取得
            start_time = ConfigManager.get_setting('post_start_time', '09:00')
            end_time = ConfigManager.get_setting('post_end_time', '21:00')
            post_interval = int(ConfigManager.get_setting('post_interval', 60))
            
            # 投稿時間内かチェック
            if start_time <= current_time <= end_time:
                # 次の投稿を処理
                process_next_post()
            
            # インターバル待機
            time.sleep(post_interval * 60)
            
        except Exception as e:
            logger.error(f"自動化ワーカーエラー: {str(e)}")
            time.sleep(60)  # エラー時は1分待機
    
    logger.info("自動化ワーカーを終了")

def process_next_post():
    """次の投稿を処理"""
    try:
        # 次の未投稿を取得
        result = db.execute_query(
            "SELECT id, text, scheduled_time FROM posts WHERE status = 'pending' ORDER BY scheduled_time ASC LIMIT 1",
            fetch=True
        )
        
        if not result:
            return
        
        post_id, text, scheduled_time = result[0]
        
        # スケジュール時刻をチェック
        scheduled_dt = datetime.fromisoformat(scheduled_time)
        if scheduled_dt > datetime.now():
            return
        
        # 投稿処理（ここではステータスを更新するだけ）
        db.execute_query(
            "UPDATE posts SET status = 'posted', updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), post_id)
        )
        
        logger.info(f"投稿処理完了: {post_id}")
        
    except Exception as e:
        logger.error(f"投稿処理エラー: {str(e)}")

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
        
        processed_posts = []
        for i, post in enumerate(top_posts):
            # スケジュール時刻を設定
            scheduled_time = datetime.now() + timedelta(hours=i+1)
            
            # 多様性システムで投稿を生成
            post_text = post.get('postText', '')
            genre = post.get('genre', 'エンタメ')
            
            if post_text:
                improved_text = diversity_manager.generate_unique_post(post_text, genre)
            else:
                improved_text = f"{genre}の話題 #{i+1}"
            
            post_id = str(uuid.uuid4())
            
            # データベースに保存
            db.execute_query('''
                INSERT INTO posts 
                (id, text, image_urls, genre, scheduled_time, status, reference_post, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                post_id,
                improved_text,
                json.dumps([post.get('imageUrl', '')] if post.get('imageUrl') else []),
                genre,
                scheduled_time.isoformat(),
                'pending',
                post_text,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            processed_posts.append({
                "id": post_id,
                "text": improved_text,
                "genre": genre,
                "scheduledTime": scheduled_time.isoformat(),
                "originalLikes": post.get('likes', 0)
            })
        
        logger.info(f"CSV処理完了: {len(processed_posts)}件の投稿候補を生成")
        
        return jsonify({
            "success": True,
            "processed_count": len(processed_posts),
            "posts": processed_posts
        })
        
    except Exception as e:
        logger.error(f"CSV処理エラー: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/automation/settings', methods=['GET', 'PUT'])
def automation_settings():
    """自動化設定の取得・更新"""
    if request.method == 'GET':
        try:
            settings = {
                "csvWatchPath": ConfigManager.get_setting('csv_watch_path', './csv_input'),
                "postInterval": int(ConfigManager.get_setting('post_interval', 60)),
                "scrapingInterval": int(ConfigManager.get_setting('scraping_interval', 8)),
                "dailyPostLimit": int(ConfigManager.get_setting('daily_post_limit', 10)),
                "postStartTime": ConfigManager.get_setting('post_start_time', '09:00'),
                "postEndTime": ConfigManager.get_setting('post_end_time', '21:00'),
                "enableAIGeneration": ConfigManager.get_setting('enable_ai_generation', 'true') == 'true',
                "enableBufferScheduling": ConfigManager.get_setting('enable_buffer_scheduling', 'true') == 'true',
                "enableAutoScraping": ConfigManager.get_setting('enable_auto_scraping', 'true') == 'true'
            }
            
            return jsonify({
                "success": True,
                "data": settings
            })
            
        except Exception as e:
            logger.error(f"設定取得エラー: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            data = request.json
            
            # 設定を保存
            settings_map = {
                'csvWatchPath': 'csv_watch_path',
                'postInterval': 'post_interval',
                'scrapingInterval': 'scraping_interval',
                'dailyPostLimit': 'daily_post_limit',
                'postStartTime': 'post_start_time',
                'postEndTime': 'post_end_time',
                'enableAIGeneration': 'enable_ai_generation',
                'enableBufferScheduling': 'enable_buffer_scheduling',
                'enableAutoScraping': 'enable_auto_scraping'
            }
            
            for key, db_key in settings_map.items():
                if key in data:
                    ConfigManager.set_setting(db_key, data[key])
            
            logger.info("自動化設定を更新しました")
            
            return jsonify({
                "success": True,
                "data": data
            })
            
        except Exception as e:
            logger.error(f"設定更新エラー: {str(e)}")
            return jsonify({"error": str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """アップロードされたファイルの配信"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 初期データの生成
def initialize_sample_data():
    """サンプルデータの初期化"""
    try:
        # 既存のデータがあるかチェック
        result = db.execute_query("SELECT COUNT(*) FROM posts", fetch=True)
        if result[0][0] > 0:
            logger.info("既存のデータがあるため、サンプルデータの生成をスキップ")
            return
        
        # サンプル投稿を生成
        logger.info("サンプルデータを生成中...")
        generate_mock_posts(20)
        
        # サンプルスクレイピング履歴
        for i in range(5):
            db.execute_query('''
                INSERT INTO scraping_history 
                (id, timestamp, status, message, posts_generated)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                (datetime.now() - timedelta(hours=i*8)).isoformat(),
                'success' if i % 2 == 0 else 'error',
                f'Scraping {"completed" if i % 2 == 0 else "failed"}',
                10 if i % 2 == 0 else 0
            ))
        
        logger.info("サンプルデータの生成完了")
        
    except Exception as e:
        logger.error(f"サンプルデータ生成エラー: {str(e)}")

if __name__ == '__main__':
    # 初期データを生成
    initialize_sample_data()
    
    # サーバーを起動
    logger.info("Threads自動投稿システム v3.2 を起動中...")
    app.run(debug=True, host='0.0.0.0', port=5000)