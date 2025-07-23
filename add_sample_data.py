#!/usr/bin/env python3
"""
サンプルデータをデータベースに追加
"""

import sqlite3
from datetime import datetime, timedelta
import random
import json

def add_sample_data():
    conn = sqlite3.connect('threads_optimized.db')
    cursor = conn.cursor()
    
    # サンプル投稿内容
    sample_posts = [
        {
            "content": "🌅 おはようございます！今日も素晴らしい一日になりますように。新しいプロジェクトの進捗をシェアします。",
            "pattern_type": "morning_greeting",
            "hashtags": "#朝活 #プロジェクト #モチベーション"
        },
        {
            "content": "🚀 新機能リリースのお知らせ！ユーザーの皆様からのフィードバックを元に、より使いやすいインターフェースを実装しました。",
            "pattern_type": "announcement",
            "hashtags": "#新機能 #アップデート #テクノロジー"
        },
        {
            "content": "💡 今日の学び：効率的なコードを書くには、まず問題を深く理解することが重要。急がば回れですね。",
            "pattern_type": "tips_and_tricks",
            "hashtags": "#プログラミング #学習 #エンジニアリング"
        },
        {
            "content": "🎯 目標達成！3ヶ月かけて取り組んできたプロジェクトが完成しました。チーム全員の努力の成果です。",
            "pattern_type": "achievement",
            "hashtags": "#達成 #チームワーク #成功"
        },
        {
            "content": "☕ コーヒーブレイク中。リフレッシュして午後も頑張ります！皆さんは何でリフレッシュしていますか？",
            "pattern_type": "casual",
            "hashtags": "#コーヒー #リフレッシュ #仕事"
        }
    ]
    
    # 過去7日間のデータを生成
    base_date = datetime.now()
    
    for i in range(20):  # 20件のサンプルデータ
        post = random.choice(sample_posts)
        days_ago = random.randint(0, 7)
        hours_ago = random.randint(0, 23)
        
        generated_at = base_date - timedelta(days=days_ago, hours=hours_ago)
        
        # エンゲージメントデータをランダムに生成
        likes = random.randint(10, 200)
        clicks = random.randint(5, 100)
        shares = random.randint(0, 50)
        comments = random.randint(0, 30)
        
        engagement_score = (likes * 1 + clicks * 2 + shares * 3 + comments * 4) / 10
        
        cursor.execute('''
            INSERT OR IGNORE INTO post_history (
                content, pattern_type, engagement_score, engagement_prediction,
                generated_at, hashtags, source, actual_engagement,
                clicks, shares, comments, likes, scheduled_time, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            post["content"],
            post["pattern_type"],
            engagement_score,
            engagement_score * random.uniform(0.8, 1.2),  # 予測値
            generated_at.isoformat(),
            post["hashtags"],
            'sample',
            engagement_score,
            clicks,
            shares,
            comments,
            likes,
            generated_at.isoformat(),
            'posted' if i < 15 else 'pending'  # 75%は投稿済み
        ))
    
    conn.commit()
    
    # 確認
    cursor.execute('SELECT COUNT(*) FROM post_history')
    count = cursor.fetchone()[0]
    print(f"✅ {count}件のデータがpost_historyテーブルに存在します")
    
    conn.close()

if __name__ == "__main__":
    add_sample_data()