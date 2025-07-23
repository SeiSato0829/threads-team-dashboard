"""
Threads自動投稿システム - 完全版バックエンドサーバー（最終版）
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
import random
import hashlib
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

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
CORS(app, origins=['http://localhost:5173', 'http://localhost:5174', 'http://localhost:5175', 'http://localhost:3000'])

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
                retry_attempts INTEGER DEFAULT 0,
                post_hash TEXT UNIQUE
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
                posts_found INTEGER DEFAULT 0,
                posts_processed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 統計テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                date TEXT PRIMARY KEY,
                total_posts INTEGER DEFAULT 0,
                scheduled_posts INTEGER DEFAULT 0,
                completed_posts INTEGER DEFAULT 0,
                failed_posts INTEGER DEFAULT 0,
                unique_posts INTEGER DEFAULT 0,
                duplicate_posts INTEGER DEFAULT 0,
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
    
    def create_mock_data(self):
        """モックデータを作成"""
        logger.info("モックデータ作成開始")
        
        # モック設定データ
        mock_settings = [
            ('CLAUDE_API_KEY', ''),
            ('BUFFER_ACCESS_TOKEN', ''),
            ('BUFFER_PROFILE_ID', ''),
            ('automation_status', 'stopped'),
            ('post_interval', '60'),
            ('scraping_interval', '8'),
            ('daily_post_limit', '10'),
            ('post_start_time', '09:00'),
            ('post_end_time', '21:00')
        ]
        
        for key, value in mock_settings:
            self.execute_query(
                "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
                (key, value, datetime.now().isoformat())
            )
        
        # モック自社構想データ
        mock_concepts = [
            {
                'id': str(uuid.uuid4()),
                'keywords': 'AI, 自動化, 効率化',
                'genre': 'テクノロジー',
                'reflection_status': False
            },
            {
                'id': str(uuid.uuid4()),
                'keywords': 'マーケティング, SNS, ブランディング',
                'genre': 'ビジネス',
                'reflection_status': False
            },
            {
                'id': str(uuid.uuid4()),
                'keywords': 'ライフスタイル, ワークライフバランス, 健康',
                'genre': 'ライフスタイル',
                'reflection_status': False
            }
        ]
        
        for concept in mock_concepts:
            self.execute_query('''
                INSERT OR REPLACE INTO company_concepts 
                (id, keywords, genre, reflection_status, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                concept['id'],
                concept['keywords'],
                concept['genre'],
                concept['reflection_status'],
                datetime.now().isoformat()
            ))
        
        # モック投稿データ
        genres = ['テクノロジー', 'ビジネス', 'ライフスタイル', 'エンタメ', '教育']
        statuses = ['pending', 'scheduled', 'posted', 'failed']
        
        for i in range(20):
            post_text = diversity_manager.generate_unique_post(
                f"サンプル投稿 {i+1}: 興味深いコンテンツをお届けします",
                random.choice(genres),
                []
            )
            
            post_id = str(uuid.uuid4())
            scheduled_time = (datetime.now() + timedelta(hours=random.randint(1, 48))).isoformat()
            
            # ハッシュ値を生成
            post_hash = hashlib.sha256(post_text.encode()).hexdigest()
            
            self.execute_query('''
                INSERT OR REPLACE INTO posts 
                (id, text, image_urls, genre, scheduled_time, buffer_sent_time, 
                 status, concept_source, reference_post, created_at, updated_at, 
                 is_unique, retry_attempts, post_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                post_id,
                post_text,
                json.dumps([]),
                random.choice(genres),
                scheduled_time,
                None,
                random.choice(statuses),
                None,
                None,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                True,
                0,
                post_hash
            ))
        
        # モックスクレイピング履歴
        for i in range(5):
            history_id = str(uuid.uuid4())
            timestamp = (datetime.now() - timedelta(hours=i*8)).isoformat()
            
            self.execute_query('''
                INSERT INTO scraping_history 
                (id, timestamp, status, message, posts_found, posts_processed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                history_id,
                timestamp,
                'success' if i % 3 != 0 else 'failed',
                f'スクレイピング完了: {10 + i*2}件の投稿を処理' if i % 3 != 0 else 'ネットワークエラー',
                10 + i*2 if i % 3 != 0 else 0,
                8 + i*2 if i % 3 != 0 else 0,
                datetime.now().isoformat()
            ))
        
        logger.info("モックデータ作成完了")

# データベースインスタンス
db = Database()

# グローバル変数
automation_worker = None

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
            (key, str(value), datetime.now().isoformat())
        )
    
    @staticmethod
    def get_all_settings():
        """すべての設定を取得"""
        result = db.execute_query(
            "SELECT key, value FROM settings",
            fetch=True
        )
        return {row[0]: row[1] for row in result} if result else {}

# 環境変数からAPI設定を取得
def get_api_config():
    """環境変数またはデータベースからAPI設定を取得"""
    claude_api_key = os.getenv('CLAUDE_API_KEY') or ConfigManager.get_setting('CLAUDE_API_KEY')
    buffer_access_token = os.getenv('BUFFER_ACCESS_TOKEN') or ConfigManager.get_setting('BUFFER_ACCESS_TOKEN')
    buffer_profile_id = os.getenv('BUFFER_PROFILE_ID') or ConfigManager.get_setting('BUFFER_PROFILE_ID')
    
    return claude_api_key, buffer_access_token, buffer_profile_id

# Claude APIクライアント
claude_client = None
claude_api_key, buffer_access_token, buffer_profile_id = get_api_config()

if claude_api_key:
    try:
        claude_client = anthropic.Anthropic(api_key=claude_api_key)
        logger.info("Claude API初期化成功")
    except Exception as e:
        logger.error(f"Claude API初期化エラー: {e}")
else:
    logger.warning("Claude API キーが設定されていません")

# Buffer API設定
BUFFER_API_URL = "https://api.bufferapp.com/1"
BUFFER_ACCESS_TOKEN = buffer_access_token

if BUFFER_ACCESS_TOKEN:
    logger.info("Buffer API設定確認済み")
else:
    logger.warning("Buffer API トークンが設定されていません")

def allowed_file(filename):
    """ファイル拡張子チェック"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    """ヘルスチェック"""
    return jsonify({
        "status": "running",
        "message": "Threads自動投稿システム v3.2 - 完全版",
        "version": "3.2.0",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if os.path.exists('threads_auto_post.db') else "not found"
    })

@app.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    """ダッシュボード統計情報を取得"""
    try:
        # 投稿統計を取得
        total_posts = db.execute_query(
            "SELECT COUNT(*) FROM posts", fetch=True
        )[0][0]
        
        scheduled_posts = db.execute_query(
            "SELECT COUNT(*) FROM posts WHERE status = 'scheduled' OR status = 'pending'", 
            fetch=True
        )[0][0]
        
        completed_posts = db.execute_query(
            "SELECT COUNT(*) FROM posts WHERE status = 'posted'", 
            fetch=True
        )[0][0]
        
        failed_posts = db.execute_query(
            "SELECT COUNT(*) FROM posts WHERE status = 'failed'", 
            fetch=True
        )[0][0]
        
        # 今日の投稿数
        today = datetime.now().date().isoformat()
        today_posts = db.execute_query(
            "SELECT COUNT(*) FROM posts WHERE DATE(created_at) = ?",
            (today,),
            fetch=True
        )[0][0]
        
        # 自動化ステータス
        automation_status = ConfigManager.get_setting('automation_status') or 'stopped'
        
        return jsonify({
            "success": True,
            "data": {
                "totalPosts": total_posts,
                "scheduledPosts": scheduled_posts,
                "completedPosts": completed_posts,
                "failedPosts": failed_posts,
                "todayPosts": today_posts,
                "automationStatus": automation_status
            }
        })
        
    except Exception as e:
        logger.error(f"ダッシュボード統計エラー: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/scraping/history', methods=['GET'])
def scraping_history():
    """スクレイピング履歴を取得"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        result = db.execute_query(
            """SELECT id, timestamp, status, message, posts_found, posts_processed 
               FROM scraping_history 
               ORDER BY timestamp DESC 
               LIMIT ?""",
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
                "postsFound": row[4],
                "postsProcessed": row[5]
            })
        
        return jsonify({
            "success": True,
            "data": history
        })
        
    except Exception as e:
        logger.error(f"履歴取得エラー: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/automation/start', methods=['POST'])
def start_automation():
    """自動化を開始"""
    try:
        global automation_worker
        
        # すでに実行中かチェック
        if automation_worker and automation_worker.is_alive():
            return jsonify({
                "success": False,
                "error": "自動化はすでに実行中です"
            }), 400
        
        # ステータスを更新
        ConfigManager.set_setting('automation_status', 'running')
        
        # ワーカースレッドを開始
        automation_worker = AutomationWorker()
        automation_worker.start()
        
        logger.info("自動化を開始しました")
        
        return jsonify({
            "success": True,
            "message": "自動化を開始しました"
        })
        
    except Exception as e:
        logger.error(f"自動化開始エラー: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/automation/stop', methods=['POST'])
def stop_automation():
    """自動化を停止"""
    try:
        global automation_worker
        
        # ワーカーを停止
        if automation_worker:
            automation_worker.stop()
            automation_worker = None
        
        # ステータスを更新
        ConfigManager.set_setting('automation_status', 'stopped')
        
        logger.info("自動化を停止しました")
        
        return jsonify({
            "success": True,
            "message": "自動化を停止しました"
        })
        
    except Exception as e:
        logger.error(f"自動化停止エラー: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/scraping/trigger', methods=['POST'])
def trigger_scraping():
    """手動でスクレイピングを実行"""
    try:
        # スクレイピング履歴を記録
        history_id = str(uuid.uuid4())
        
        # CSVファイルをチェック
        csv_path = ConfigManager.get_setting('csvWatchPath') or './csv_input'
        csv_files = list(Path(csv_path).glob('*.csv'))
        
        if not csv_files:
            db.execute_query('''
                INSERT INTO scraping_history 
                (id, timestamp, status, message, posts_found, posts_processed)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                history_id,
                datetime.now().isoformat(),
                'failed',
                'CSVファイルが見つかりません',
                0,
                0
            ))
            
            return jsonify({
                "success": False,
                "error": "CSVファイルが見つかりません"
            }), 404
        
        # 最新のCSVを処理
        latest_csv = max(csv_files, key=os.path.getctime)
        
        try:
            df = pd.read_csv(latest_csv)
            posts_found = len(df)
            
            # 上位10件を処理
            top_posts = df.nlargest(10, 'likes') if 'likes' in df.columns else df.head(10)
            posts_processed = len(top_posts)
            
            # 各投稿を生成・保存
            for _, row in top_posts.iterrows():
                text = row.get('text', '')
                genre = row.get('genre', 'その他')
                
                # 多様性を考慮した投稿生成
                improved_text = diversity_manager.generate_unique_post(text, genre, [])
                
                # 投稿を保存
                post_id = str(uuid.uuid4())
                scheduled_time = (datetime.now() + timedelta(hours=random.randint(1, 24))).isoformat()
                post_hash = hashlib.sha256(improved_text.encode()).hexdigest()
                
                db.execute_query('''
                    INSERT OR IGNORE INTO posts 
                    (id, text, image_urls, genre, scheduled_time, status, 
                     created_at, updated_at, is_unique, post_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    post_id,
                    improved_text,
                    json.dumps([]),
                    genre,
                    scheduled_time,
                    'pending',
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    True,
                    post_hash
                ))
            
            # 成功履歴を記録
            db.execute_query('''
                INSERT INTO scraping_history 
                (id, timestamp, status, message, posts_found, posts_processed)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                history_id,
                datetime.now().isoformat(),
                'success',
                f'{posts_processed}件の投稿を処理しました',
                posts_found,
                posts_processed
            ))
            
            # 処理済みフォルダに移動
            processed_path = Path('./csv_processed') / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{latest_csv.name}"
            latest_csv.rename(processed_path)
            
            logger.info(f"スクレイピング完了: {posts_processed}件を処理")
            
            return jsonify({
                "success": True,
                "message": f"{posts_processed}件の投稿を処理しました",
                "postsFound": posts_found,
                "postsProcessed": posts_processed
            })
            
        except Exception as e:
            db.execute_query('''
                INSERT INTO scraping_history 
                (id, timestamp, status, message, posts_found, posts_processed)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                history_id,
                datetime.now().isoformat(),
                'failed',
                f'CSV処理エラー: {str(e)}',
                0,
                0
            ))
            raise e
            
    except Exception as e:
        logger.error(f"スクレイピングエラー: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-post', methods=['POST'])
def generate_post():
    """AI投稿生成エンドポイント（多様性強化版）"""
    try:
        data = request.json
        original_text = data.get('text', '')
        genre = data.get('genre', '')
        reference_posts = data.get('reference_posts', [])
        use_diversity = data.get('use_diversity', True)
        
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
        
        logger.info(f"AI投稿生成完了: {len(improved_text)}文字")
        
        return jsonify({
            "success": True,
            "original_text": original_text,
            "improved_text": improved_text,
            "model_used": "claude-3-haiku-20240307",
            "character_count": len(improved_text),
            "is_unique": not is_duplicate
        })
        
    except Exception as e:
        logger.error(f"投稿生成エラー: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/posts', methods=['GET', 'POST'])
def posts():
    """投稿データの取得・保存"""
    if request.method == 'GET':
        try:
            # フィルタリングパラメータ
            status = request.args.get('status')
            genre = request.args.get('genre')
            limit = request.args.get('limit', 100, type=int)
            
            # クエリ構築
            query = "SELECT * FROM posts"
            params = []
            conditions = []
            
            if status:
                conditions.append("status = ?")
                params.append(status)
            
            if genre:
                conditions.append("genre = ?")
                params.append(genre)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            result = db.execute_query(query, params, fetch=True)
            
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
                    "isUnique": bool(row[11]),
                    "retryAttempts": row[12]
                }
                posts_data.append(post)
            
            return jsonify({
                "success": True,
                "posts": posts_data,
                "count": len(posts_data)
            })
            
        except Exception as e:
            logger.error(f"投稿取得エラー: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            
            # 単一投稿の作成
            if 'text' in data:
                post_id = str(uuid.uuid4())
                text = data.get('text', '')
                genre = data.get('genre', 'その他')
                scheduled_time = data.get('scheduledTime', 
                    (datetime.now() + timedelta(hours=1)).isoformat())
                
                # 重複チェック
                post_hash = hashlib.sha256(text.encode()).hexdigest()
                is_unique = not diversity_manager.is_duplicate(text)
                
                db.execute_query('''
                    INSERT INTO posts 
                    (id, text, image_urls, genre, scheduled_time, status, 
                     created_at, updated_at, is_unique, retry_attempts, post_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    post_id,
                    text,
                    json.dumps(data.get('imageUrls', [])),
                    genre,
                    scheduled_time,
                    'pending',
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    is_unique,
                    0,
                    post_hash
                ))
                
                logger.info(f"投稿作成完了: {post_id}")
                
                return jsonify({
                    "success": True,
                    "postId": post_id,
                    "message": "投稿を作成しました"
                })
            
            # 複数投稿の保存
            else:
                posts_to_save = data.get('posts', [])
                saved_count = 0
                
                for post in posts_to_save:
                    post_id = post.get('id', str(uuid.uuid4()))
                    text = post.get('text', '')
                    post_hash = hashlib.sha256(text.encode()).hexdigest()
                    
                    db.execute_query('''
                        INSERT OR REPLACE INTO posts 
                        (id, text, image_urls, genre, scheduled_time, buffer_sent_time, 
                         status, concept_source, reference_post, created_at, updated_at,
                         is_unique, retry_attempts, post_hash)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        post_id,
                        text,
                        json.dumps(post.get('imageUrls', [])),
                        post.get('genre', ''),
                        post.get('scheduledTime', ''),
                        post.get('bufferSentTime'),
                        post.get('status', 'pending'),
                        post.get('conceptSource'),
                        post.get('referencePost'),
                        post.get('createdAt', datetime.now().isoformat()),
                        datetime.now().isoformat(),
                        True,
                        0,
                        post_hash
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

@app.route('/api/process-csv', methods=['POST'])
def process_csv():
    """CSVデータを処理して投稿候補を生成"""
    try:
        data = request.json
        csv_data = data.get('csvData', [])
        company_concepts = data.get('companyConcepts', [])
        limit = data.get('limit', 10)
        sort_by = data.get('sortBy', 'likes')
        
        # いいね数でソート
        if sort_by == 'likes':
            sorted_posts = sorted(csv_data, key=lambda x: x.get('likes', 0), reverse=True)
        else:
            sorted_posts = csv_data
        
        # 上位N件を取得
        top_posts = sorted_posts[:limit]
        
        processed_posts = []
        for post in top_posts:
            # 自社構想とのマッチング
            matched_concept = find_matching_concept(post, company_concepts)
            
            text = post.get('postText', '')
            genre = post.get('genre', 'その他')
            
            # 多様性を考慮した投稿生成
            if claude_client and matched_concept:
                # AI生成で自社構想を反映
                improved_text = generate_with_concept(post, matched_concept)
            else:
                # 多様性マネージャーで生成
                improved_text = diversity_manager.generate_unique_post(text, genre, [])
            
            # 投稿を作成
            post_id = str(uuid.uuid4())
            scheduled_time = (datetime.now() + timedelta(hours=random.randint(1, 24))).isoformat()
            
            processed_post = {
                'id': post_id,
                'text': improved_text,
                'imageUrls': [],
                'genre': genre,
                'scheduledTime': scheduled_time,
                'status': 'pending',
                'createdAt': datetime.now().isoformat(),
                'updatedAt': datetime.now().isoformat(),
                'isUnique': True,
                'conceptSource': matched_concept.get('keywords', '') if matched_concept else None
            }
            
            processed_posts.append(processed_post)
        
        logger.info(f"CSV処理完了: {len(processed_posts)}件の投稿候補を生成")
        
        return jsonify({
            "success": True,
            "data": {
                "posts": processed_posts,
                "processedCount": len(processed_posts),
                "totalCount": len(csv_data)
            }
        })
        
    except Exception as e:
        logger.error(f"CSV処理エラー: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

def find_matching_concept(post, concepts):
    """投稿と自社構想のマッチング"""
    post_genre = post.get('genre', '').lower()
    post_text = post.get('postText', '').lower()
    
    for concept in concepts:
        concept_genre = concept.get('genre', '').lower()
        concept_keywords = concept.get('keywords', '').lower()
        
        # ジャンルまたはキーワードでマッチング
        if (concept_genre in post_genre or 
            any(keyword.strip() in post_text for keyword in concept_keywords.split(','))):
            return concept
    
    return None

def generate_with_concept(post, concept):
    """自社構想を反映した投稿生成"""
    try:
        prompt = f"""
以下の人気投稿を参考に、自社の構想を自然に組み込んだ新しい投稿を作成してください。

【参考投稿】
{post.get('postText', '')}
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
        
        improved_text = response.content[0].text
        
        logger.info(f"構想反映投稿生成完了: {concept.get('keywords', '')}")
        return improved_text
        
    except Exception as e:
        logger.error(f"構想反映エラー: {str(e)}")
        # エラー時は多様性マネージャーで生成
        return diversity_manager.generate_unique_post(
            post.get('postText', ''), 
            post.get('genre', ''), 
            []
        )

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
                "profile_id": profile_id,
                "all_settings": ConfigManager.get_all_settings()
            })
            
        except Exception as e:
            logger.error(f"設定取得エラー: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'POST':
        try:
            new_settings = request.json
            
            # 設定を更新
            for key, value in new_settings.items():
                ConfigManager.set_setting(key, value)
            
            # Claude APIクライアントを再初期化
            global claude_client
            claude_api_key = ConfigManager.get_setting('CLAUDE_API_KEY')
            if claude_api_key:
                try:
                    claude_client = anthropic.Anthropic(api_key=claude_api_key)
                except Exception as e:
                    logger.error(f"Claude API再初期化エラー: {e}")
            
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

# 自動化ワーカークラス
class AutomationWorker(threading.Thread):
    """自動化処理を行うワーカースレッド"""
    
    def __init__(self):
        super().__init__(daemon=True)
        self.running = True
        self.last_scraping = datetime.now()
        self.last_post = datetime.now()
    
    def stop(self):
        """ワーカーを停止"""
        self.running = False
        logger.info("自動化ワーカーを停止します")
    
    def run(self):
        """ワーカーのメインループ"""
        logger.info("自動化ワーカーを開始しました")
        
        while self.running:
            try:
                # 設定を取得
                post_interval = int(ConfigManager.get_setting('post_interval') or 60)
                scraping_interval = int(ConfigManager.get_setting('scraping_interval') or 8)
                daily_limit = int(ConfigManager.get_setting('daily_post_limit') or 10)
                start_time = ConfigManager.get_setting('post_start_time') or '09:00'
                end_time = ConfigManager.get_setting('post_end_time') or '21:00'
                
                now = datetime.now()
                current_time = now.strftime('%H:%M')
                
                # 投稿時間内かチェック
                if start_time <= current_time <= end_time:
                    # スクレイピング実行チェック
                    if (now - self.last_scraping).total_seconds() >= scraping_interval * 3600:
                        self.perform_scraping()
                        self.last_scraping = now
                    
                    # 投稿実行チェック
                    if (now - self.last_post).total_seconds() >= post_interval * 60:
                        # 今日の投稿数をチェック
                        today = now.date().isoformat()
                        today_posts = db.execute_query(
                            "SELECT COUNT(*) FROM posts WHERE DATE(created_at) = ? AND status = 'posted'",
                            (today,),
                            fetch=True
                        )[0][0]
                        
                        if today_posts < daily_limit:
                            self.perform_posting()
                            self.last_post = now
                        else:
                            logger.info(f"本日の投稿上限（{daily_limit}件）に達しました")
                
                # 30秒待機
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"自動化ワーカーエラー: {str(e)}")
                time.sleep(60)  # エラー時は1分待機
    
    def perform_scraping(self):
        """スクレイピングを実行"""
        try:
            logger.info("自動スクレイピングを開始します")
            
            # trigger_scraping と同様の処理
            csv_path = ConfigManager.get_setting('csvWatchPath') or './csv_input'
            csv_files = list(Path(csv_path).glob('*.csv'))
            
            if csv_files:
                latest_csv = max(csv_files, key=os.path.getctime)
                df = pd.read_csv(latest_csv)
                
                # 処理とログ記録
                history_id = str(uuid.uuid4())
                posts_found = len(df)
                
                # 上位投稿を処理
                top_posts = df.nlargest(10, 'likes') if 'likes' in df.columns else df.head(10)
                posts_processed = 0
                
                for _, row in top_posts.iterrows():
                    text = row.get('text', '')
                    genre = row.get('genre', 'その他')
                    
                    # 多様性を考慮した投稿生成
                    improved_text = diversity_manager.generate_unique_post(text, genre, [])
                    
                    # 投稿を保存
                    post_id = str(uuid.uuid4())
                    scheduled_time = (datetime.now() + timedelta(hours=random.randint(1, 24))).isoformat()
                    post_hash = hashlib.sha256(improved_text.encode()).hexdigest()
                    
                    db.execute_query('''
                        INSERT OR IGNORE INTO posts 
                        (id, text, image_urls, genre, scheduled_time, status, 
                         created_at, updated_at, is_unique, post_hash)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        post_id,
                        improved_text,
                        json.dumps([]),
                        genre,
                        scheduled_time,
                        'pending',
                        datetime.now().isoformat(),
                        datetime.now().isoformat(),
                        True,
                        post_hash
                    ))
                    posts_processed += 1
                
                # 履歴を記録
                db.execute_query('''
                    INSERT INTO scraping_history 
                    (id, timestamp, status, message, posts_found, posts_processed)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    history_id,
                    datetime.now().isoformat(),
                    'success',
                    f'自動スクレイピング完了: {posts_processed}件を処理',
                    posts_found,
                    posts_processed
                ))
                
                # CSVを処理済みフォルダに移動
                processed_path = Path('./csv_processed') / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{latest_csv.name}"
                latest_csv.rename(processed_path)
                
                logger.info(f"自動スクレイピング完了: {posts_processed}件を処理")
                
        except Exception as e:
            logger.error(f"自動スクレイピングエラー: {str(e)}")
    
    def perform_posting(self):
        """投稿を実行"""
        try:
            # 次の投稿を取得
            result = db.execute_query(
                """SELECT id, text, image_urls, genre FROM posts 
                   WHERE status = 'pending' 
                   ORDER BY scheduled_time ASC 
                   LIMIT 1""",
                fetch=True
            )
            
            if not result:
                logger.info("投稿する記事がありません")
                return
            
            post_id, text, image_urls_json, genre = result[0]
            image_urls = json.loads(image_urls_json) if image_urls_json else []
            
            # Buffer APIが設定されている場合は送信
            if BUFFER_ACCESS_TOKEN:
                try:
                    buffer_data = {
                        "text": text,
                        "profile_ids": [ConfigManager.get_setting('BUFFER_PROFILE_ID')],
                        "now": True
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
                    
                    if response.status_code == 200:
                        # 成功時のステータス更新
                        db.execute_query(
                            "UPDATE posts SET status = 'posted', updated_at = ? WHERE id = ?",
                            (datetime.now().isoformat(), post_id)
                        )
                        logger.info(f"投稿成功: {post_id}")
                    else:
                        raise Exception(f"Buffer API error: {response.status_code}")
                        
                except Exception as e:
                    # 失敗時のステータス更新
                    db.execute_query(
                        "UPDATE posts SET status = 'failed', updated_at = ? WHERE id = ?",
                        (datetime.now().isoformat(), post_id)
                    )
                    logger.error(f"投稿失敗 {post_id}: {str(e)}")
            else:
                # Buffer未設定の場合はシミュレーション
                db.execute_query(
                    "UPDATE posts SET status = 'posted', updated_at = ? WHERE id = ?",
                    (datetime.now().isoformat(), post_id)
                )
                logger.info(f"投稿シミュレーション完了: {post_id}")
                
        except Exception as e:
            logger.error(f"自動投稿エラー: {str(e)}")

if __name__ == '__main__':
    # 初回起動時にモックデータを作成
    if not os.path.exists('threads_auto_post.db'):
        logger.info("初回起動のため、モックデータを作成します")
        db.create_mock_data()
    
    # サーバー起動
    print("="*60)
    print("Threads自動投稿システム v3.2 - 完全版バックエンドサーバー")
    print("="*60)
    print("URL: http://localhost:5000")
    print("フロントエンド: http://localhost:5173")
    print("データベース: threads_auto_post.db")
    print("ログファイル: threads_auto_post.log")
    print()
    print("初回起動時はモックデータが自動生成されています")
    print("設定画面でAPIキーを設定してください")
    print()
    print("終了: Ctrl+C")
    print("="*60)
    
    try:
        app.run(debug=True, port=5000, threaded=True)
    except KeyboardInterrupt:
        logger.info("サーバーを終了します")
        if automation_worker:
            automation_worker.stop()