#!/usr/bin/env python3
"""
シンプルな自動投稿スケジューラーのテスト
"""

import sqlite3
from datetime import datetime, timedelta
import random

def test_scheduler():
    """スケジューラーのテスト"""
    
    # データベース接続
    conn = sqlite3.connect('threads_optimized.db')
    cursor = conn.cursor()
    
    # scheduled_postsテーブルを作成
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scheduled_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        scheduled_time TIMESTAMP NOT NULL,
        status TEXT DEFAULT 'pending',
        posted_at TIMESTAMP,
        pattern_type TEXT,
        hashtags TEXT,
        engagement_prediction REAL
    )
    """)
    
    print("📅 今後24時間の投稿をスケジュール中...")
    
    # 投稿パターン
    patterns = [
        {
            "time": "08:00",
            "type": "morning_greeting",
            "content": "おはようございます！今日も素晴らしい一日になりますように✨ #朝活 #ポジティブ",
        },
        {
            "time": "12:00",
            "type": "tips",
            "content": "💡 ランチタイムの学び：効率的な作業のコツは、タスクを小さく分けること。一つずつクリアしていきましょう！ #仕事術 #生産性向上",
        },
        {
            "time": "18:00",
            "type": "evening",
            "content": "今日も一日お疲れ様でした！小さな成功も大切な一歩です。明日への活力にしていきましょう🌙 #振り返り #成長",
        },
        {
            "time": "21:00",
            "type": "night",
            "content": "夜の読書タイム📚 新しい知識は明日への投資。みなさんは何を学んでいますか？ #読書 #学習",
        }
    ]
    
    # 今日と明日の投稿をスケジュール
    for day_offset in range(2):
        base_date = datetime.now().date() + timedelta(days=day_offset)
        
        for pattern in patterns:
            # 時間を設定
            hour, minute = map(int, pattern["time"].split(":"))
            scheduled_time = datetime.combine(base_date, datetime.min.time().replace(hour=hour, minute=minute))
            
            # 過去の時間はスキップ
            if scheduled_time < datetime.now():
                continue
            
            # データベースに挿入
            cursor.execute("""
                INSERT INTO scheduled_posts (content, scheduled_time, pattern_type, hashtags, engagement_prediction, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                pattern["content"],
                scheduled_time,
                pattern["type"],
                "#朝活 #ポジティブ",  # サンプルハッシュタグ
                random.uniform(30, 80),  # エンゲージメント予測
                'pending'
            ))
            
            # post_historyにも追加
            cursor.execute("""
                INSERT INTO post_history (content, pattern_type, engagement_score, engagement_prediction,
                                        generated_at, hashtags, source, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern["content"],
                pattern["type"],
                random.uniform(30, 80),
                random.uniform(30, 80),
                scheduled_time,
                "#朝活 #ポジティブ",
                'scheduler',
                'pending'
            ))
            
            print(f"  ✅ {scheduled_time.strftime('%Y-%m-%d %H:%M')} - {pattern['type']}")
    
    conn.commit()
    
    # 統計を表示
    cursor.execute("SELECT COUNT(*) FROM scheduled_posts WHERE status = 'pending'")
    pending_count = cursor.fetchone()[0]
    
    print(f"\n📊 統計:")
    print(f"  - 予約投稿数: {pending_count}件")
    
    conn.close()
    print("\n✅ スケジューラーのテストが完了しました！")
    print("ダッシュボードをリロードして確認してください。")

if __name__ == "__main__":
    test_scheduler()