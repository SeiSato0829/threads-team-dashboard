#!/usr/bin/env python3
"""
基本データベーステスト - 外部ライブラリ不要
"""

import sqlite3
import os

def test_databases():
    """データベース接続テスト"""
    databases = {
        'scheduled_posts.db': 'scheduled_posts',
        'threads_optimized.db': 'threads_posts', 
        'buzz_history.db': 'buzz_history',
        'viral_history.db': 'post_history'
    }
    
    print("=== データベーステスト開始 ===")
    
    for db_path, table_name in databases.items():
        print(f"\n📊 {db_path}:")
        
        if not os.path.exists(db_path):
            print("  ❌ ファイルが存在しません")
            continue
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # テーブル一覧
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            all_tables = [t[0] for t in cursor.fetchall()]
            print(f"  📋 利用可能テーブル: {all_tables}")
            
            # 指定テーブル確認
            if table_name in all_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                record_count = cursor.fetchone()[0]
                print(f"  ✅ {table_name}: {record_count} レコード")
                
                if record_count > 0:
                    # カラム情報
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [col[1] for col in cursor.fetchall()]
                    print(f"  📝 カラム: {columns}")
                    
                    # サンプルデータ
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                    sample = cursor.fetchone()
                    if sample:
                        print(f"  🔍 サンプル: {sample[:3]}..." if len(sample) > 3 else f"  🔍 サンプル: {sample}")
                
            else:
                print(f"  ❌ テーブル '{table_name}' が見つかりません")
            
            conn.close()
            
        except Exception as e:
            print(f"  ❌ エラー: {str(e)}")
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    test_databases()