#!/usr/bin/env python3
"""
データベースの修正スクリプト
post_historyテーブルの作成とデータ移行
"""

import sqlite3
import os

def fix_database():
    db_path = 'threads_optimized.db'
    
    if not os.path.exists(db_path):
        print(f"❌ {db_path} が見つかりません")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # post_historyテーブルを作成（threads_postsと同じ構造）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT,
                content TEXT NOT NULL,
                pattern_type TEXT DEFAULT 'general',
                engagement_score REAL DEFAULT 0.0,
                engagement_prediction REAL DEFAULT 0.0,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                hashtags TEXT,
                source TEXT DEFAULT 'manual',
                actual_engagement REAL DEFAULT 0.0,
                clicks INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                scheduled_time TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # threads_postsからデータをコピー
        cursor.execute('''
            INSERT OR IGNORE INTO post_history (
                content_hash, content, pattern_type, engagement_score,
                engagement_prediction, generated_at, hashtags, source,
                actual_engagement, clicks, shares, comments, likes,
                scheduled_time, status
            )
            SELECT 
                content_hash, content, pattern_type, engagement_score,
                engagement_score as engagement_prediction, generated_at, 
                hashtags, 'imported' as source, actual_engagement, 
                clicks, shares, comments, likes, scheduled_time, status
            FROM threads_posts
        ''')
        
        # インデックスを作成
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_post_history_generated_at ON post_history(generated_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_post_history_status ON post_history(status)')
        
        conn.commit()
        
        # 結果を確認
        cursor.execute('SELECT COUNT(*) FROM post_history')
        count = cursor.fetchone()[0]
        print(f"✅ post_historyテーブルを作成しました")
        print(f"✅ {count}件のデータを移行しました")
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database()