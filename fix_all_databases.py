#!/usr/bin/env python3
"""
全てのデータベースにstatusカラムを追加
"""

import sqlite3
import os

def fix_database(db_path):
    """データベースを修正"""
    if not os.path.exists(db_path):
        print(f"❌ {db_path} が見つかりません")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # post_historyテーブルの存在確認
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='post_history'")
        if not cursor.fetchone():
            print(f"📂 {db_path}: post_historyテーブルがありません")
            conn.close()
            return
        
        # 既存のカラムを確認
        cursor.execute("PRAGMA table_info(post_history)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # statusカラムがない場合は追加
        if 'status' not in columns:
            cursor.execute("""
                ALTER TABLE post_history 
                ADD COLUMN status TEXT DEFAULT 'posted'
            """)
            print(f"✅ {db_path}: statusカラムを追加しました")
        else:
            print(f"✓ {db_path}: statusカラムは既に存在します")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ {db_path} エラー: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def main():
    """メイン処理"""
    databases = [
        "threads_optimized.db",
        "buzz_history.db",
        "viral_history.db"
    ]
    
    print("🔧 データベースの修正を開始...")
    
    for db in databases:
        fix_database(db)
    
    print("\n✅ 完了しました！")

if __name__ == "__main__":
    main()