"""
Streamlit Cloud用のサンプルデータベース作成
"""

import sqlite3
import os
from datetime import datetime, timedelta

# データベースファイルのリスト
db_files = [
    "threads_optimized.db",
    "scheduled_posts.db", 
    "buzz_history.db",
    "viral_history.db"
]

# 各データベースを作成
for db_file in db_files:
    if os.path.exists(db_file):
        print(f"既存の {db_file} を削除...")
        os.remove(db_file)
    
    print(f"{db_file} を作成中...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # scheduled_posts テーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scheduled_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        scheduled_time TIMESTAMP NOT NULL,
        status TEXT DEFAULT 'pending',
        posted_at TIMESTAMP,
        pattern_type TEXT DEFAULT 'general',
        hashtags TEXT DEFAULT '',
        engagement_prediction REAL DEFAULT 0,
        actual_engagement REAL DEFAULT 0,
        clicks INTEGER DEFAULT 0,
        shares INTEGER DEFAULT 0,
        comments INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # post_history テーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS post_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        pattern_type TEXT DEFAULT 'general',
        engagement_score REAL DEFAULT 0,
        engagement_prediction REAL DEFAULT 0,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        hashtags TEXT DEFAULT '',
        source TEXT DEFAULT 'manual',
        status TEXT DEFAULT 'posted',
        actual_engagement REAL DEFAULT 0,
        clicks INTEGER DEFAULT 0,
        shares INTEGER DEFAULT 0,
        comments INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0
    )
    """)
    
    # サンプルデータを少しだけ追加
    if db_file == "threads_optimized.db":
        sample_posts = [
            ("サンプル投稿1: LiteWEB+で1万円でWebサイト作成可能！", "morning", "posted"),
            ("サンプル投稿2: 業界の常識を覆す価格設定", "lunch", "posted"),
            ("サンプル投稿3: スタートアップの味方、低コストWeb制作", "evening", "pending"),
        ]
        
        for i, (content, pattern, status) in enumerate(sample_posts):
            cursor.execute("""
            INSERT INTO post_history (content, pattern_type, status, engagement_score, actual_engagement, likes, clicks)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (content, pattern, status, 50 + i*10, 45 + i*5, 10 + i*2, 5 + i))
    
    conn.commit()
    conn.close()
    print(f"{db_file} 作成完了!")

print("\n✅ すべてのデータベースファイル作成完了！")
print("これらの軽量なデータベースファイルはGitHubにコミット可能です。")