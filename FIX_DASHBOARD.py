#!/usr/bin/env python3
"""
🔧 ダッシュボード修正スクリプト - データベース構造の統一
"""

import sqlite3
import os
from datetime import datetime

def fix_databases():
    """データベース構造修正"""
    
    print("🔧 データベース構造を修正中...")
    
    # 各データベースの正しい構造を確認・修正
    databases = {
        "scheduled_posts.db": {
            "table": "scheduled_posts",
            "columns": """
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                scheduled_time TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'pending',
                posted_at TIMESTAMP,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                engagement_prediction REAL DEFAULT 0,
                actual_engagement REAL DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                content_type TEXT,
                pattern_type TEXT,
                hashtags TEXT
            """
        },
        "threads_optimized.db": {
            "table": "threads_posts",
            "columns": """
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE,
                content TEXT,
                pattern_type TEXT,
                engagement_score REAL DEFAULT 0,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                hashtags TEXT,
                actual_engagement REAL DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                scheduled_time TIMESTAMP,
                status TEXT DEFAULT 'generated'
            """
        },
        "buzz_history.db": {
            "table": "buzz_history", 
            "columns": """
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE,
                content TEXT,
                pattern_type TEXT,
                hashtag TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                engagement_score REAL DEFAULT 0,
                actual_engagement REAL DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                scheduled_time TIMESTAMP,
                status TEXT DEFAULT 'generated'
            """
        },
        "viral_history.db": {
            "table": "post_history",
            "columns": """
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE,
                content TEXT,
                template_id TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                theme TEXT,
                emotion TEXT,
                pattern_type TEXT DEFAULT 'viral',
                engagement_score REAL DEFAULT 0,
                actual_engagement REAL DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                scheduled_time TIMESTAMP,
                hashtags TEXT,
                status TEXT DEFAULT 'generated'
            """
        }
    }
    
    for db_path, config in databases.items():
        print(f"\n📁 処理中: {db_path}")
        
        if os.path.exists(db_path):
            # 既存データをバックアップ
            backup_existing_data(db_path, config["table"])
        
        # 新しい構造でテーブル作成
        create_unified_table(db_path, config["table"], config["columns"])
        
        print(f"✅ {db_path} 修正完了")
    
    print("\n🎉 全データベースの修正完了！")

def backup_existing_data(db_path: str, table_name: str):
    """既存データのバックアップ"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # テーブル存在確認
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if cursor.fetchone():
            # データをバックアップ
            backup_table = f"{table_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            cursor.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM {table_name}")
            conn.commit()
            print(f"  💾 データバックアップ: {backup_table}")
        
        conn.close()
    except Exception as e:
        print(f"  ⚠️ バックアップエラー: {e}")

def create_unified_table(db_path: str, table_name: str, columns: str):
    """統一されたテーブル構造作成"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 既存テーブル削除
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        # 新しいテーブル作成
        cursor.execute(f"CREATE TABLE {table_name} ({columns})")
        
        conn.commit()
        conn.close()
        
        print(f"  ✅ テーブル {table_name} 作成完了")
        
    except Exception as e:
        print(f"  ❌ テーブル作成エラー: {e}")

def create_sample_data():
    """サンプルデータ作成"""
    print("\n📝 サンプルデータを作成中...")
    
    sample_posts = [
        {
            "content": "Web制作業界で革命が起きてる。30万円のサイトが1万円で作れる時代に。SEO最適化まで込みでこの価格って、もう従来の制作会社の存在意義って何？\n\nもっと詳しく→ https://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u",
            "pattern_type": "shock_value",
            "hashtags": "Web制作 AI活用",
            "engagement_score": 9.2
        },
        {
            "content": "3ヶ月前、クライアントから「サイト制作10万円以内で」って言われて困ってた。従来なら30万円は最低必要。でもLiteWEB+使ったら19,800円で完成。クライアントも大満足。\n\n解決策はこちら→ https://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u",
            "pattern_type": "storytelling", 
            "hashtags": "格安制作 個人事業主",
            "engagement_score": 8.8
        },
        {
            "content": "Web制作の価格破壊が数字で見えてきた。従来：平均40万円 / 新サービス：19,800円 = 95%削減。しかもSEO最適化＋レスポンシブデザイン＋高速表示込み。業界構造が根本から変わる。\n\nもっと詳しく→ https://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u",
            "pattern_type": "data_driven",
            "hashtags": "ホームページ制作 コスト削減", 
            "engagement_score": 8.6
        }
    ]
    
    # scheduled_posts.dbにサンプルデータ追加
    try:
        conn = sqlite3.connect("scheduled_posts.db")
        cursor = conn.cursor()
        
        from datetime import timedelta
        base_time = datetime.now()
        
        for i, post in enumerate(sample_posts):
            scheduled_time = base_time + timedelta(hours=i*4)
            
            cursor.execute("""
            INSERT INTO scheduled_posts 
            (content, scheduled_time, status, engagement_prediction, pattern_type, hashtags)
            VALUES (?, ?, 'pending', ?, ?, ?)
            """, (
                post["content"],
                scheduled_time,
                post["engagement_score"],
                post["pattern_type"],
                post["hashtags"]
            ))
        
        conn.commit()
        conn.close()
        
        print("✅ サンプルデータ作成完了")
        
    except Exception as e:
        print(f"❌ サンプルデータ作成エラー: {e}")

def main():
    """メイン実行"""
    print("🔧 Threadsダッシュボード修正ツール")
    print("=" * 60)
    
    # データベース構造修正
    fix_databases()
    
    # サンプルデータ作成
    create_sample_data()
    
    print("\n🎉 修正完了！")
    print("ダッシュボードを再起動してください:")
    print("DASHBOARD_START.bat")

if __name__ == "__main__":
    main()