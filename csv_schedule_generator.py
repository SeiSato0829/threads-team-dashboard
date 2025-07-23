#!/usr/bin/env python3
"""
CSV スケジュール生成機能
週間・月間の投稿スケジュールを生成
"""

import os
import csv
import requests
from datetime import datetime, timedelta
import json

# APIエンドポイント
API_URL = "http://localhost:5000/api"

def generate_weekly_schedule():
    """1週間分の投稿スケジュールを生成"""
    
    print("📅 週間投稿スケジュールを生成中...")
    
    # 最適な投稿時間（エンゲージメント最大化）
    posting_times = [
        {"hour": 9, "minute": 0, "type": "morning", "emoji": "☀️"},
        {"hour": 12, "minute": 30, "type": "lunch", "emoji": "🍽️"},
        {"hour": 19, "minute": 0, "type": "evening", "emoji": "🌙"}
    ]
    
    posts = []
    base_date = datetime.now()
    
    # 7日間分を生成
    for day in range(7):
        current_date = base_date + timedelta(days=day)
        day_name = current_date.strftime('%A')
        
        for time_slot in posting_times:
            post_time = current_date.replace(
                hour=time_slot["hour"], 
                minute=time_slot["minute"],
                second=0,
                microsecond=0
            )
            
            # 投稿内容を生成（APIコール）
            prompt = f"""
            {day_name}の{time_slot['type']}に投稿する内容を生成してください。
            時間帯: {time_slot['emoji']} {post_time.strftime('%H:%M')}
            雰囲気: {get_mood_for_time(time_slot['type'])}
            """
            
            content = generate_post_content(prompt)
            
            posts.append({
                'date': post_time.strftime('%Y-%m-%d'),
                'time': post_time.strftime('%H:%M'),
                'day': day_name,
                'type': time_slot['type'],
                'content': content,
                'hashtags': generate_hashtags(time_slot['type']),
                'status': 'scheduled',
                'posted': 'FALSE'
            })
    
    # CSVファイルに保存
    filename = f"weekly_schedule_{datetime.now().strftime('%Y%m%d')}.csv"
    save_to_csv(posts, filename)
    
    print(f"✅ 週間スケジュール生成完了: {filename}")
    print(f"📊 合計投稿数: {len(posts)}件")
    
    return filename

def generate_monthly_schedule():
    """1ヶ月分の投稿スケジュールを生成"""
    
    print("📅 月間投稿スケジュールを生成中...")
    
    # バランスの取れた投稿頻度（1日2-3投稿）
    posting_patterns = [
        # 平日パターン
        [
            {"hour": 7, "minute": 30, "type": "morning"},
            {"hour": 12, "minute": 15, "type": "lunch"},
            {"hour": 18, "minute": 45, "type": "evening"}
        ],
        # 週末パターン
        [
            {"hour": 10, "minute": 0, "type": "weekend_morning"},
            {"hour": 15, "minute": 30, "type": "weekend_afternoon"}
        ]
    ]
    
    posts = []
    base_date = datetime.now()
    
    # 30日間分を生成
    for day in range(30):
        current_date = base_date + timedelta(days=day)
        day_name = current_date.strftime('%A')
        is_weekend = current_date.weekday() >= 5
        
        # 平日/週末でパターンを選択
        pattern = posting_patterns[1] if is_weekend else posting_patterns[0]
        
        for time_slot in pattern:
            post_time = current_date.replace(
                hour=time_slot["hour"], 
                minute=time_slot["minute"],
                second=0,
                microsecond=0
            )
            
            # テーマを日替わりで設定
            theme = get_daily_theme(day % 7)
            
            content = generate_themed_content(theme, time_slot['type'])
            
            posts.append({
                'date': post_time.strftime('%Y-%m-%d'),
                'time': post_time.strftime('%H:%M'),
                'day': day_name,
                'theme': theme,
                'type': time_slot['type'],
                'content': content,
                'hashtags': generate_themed_hashtags(theme),
                'status': 'scheduled',
                'posted': 'FALSE'
            })
    
    # CSVファイルに保存
    filename = f"monthly_schedule_{datetime.now().strftime('%Y%m')}.csv"
    save_to_csv(posts, filename)
    
    print(f"✅ 月間スケジュール生成完了: {filename}")
    print(f"📊 合計投稿数: {len(posts)}件")
    
    # 統計情報を表示
    show_statistics(posts)
    
    return filename

def generate_post_content(prompt):
    """APIを使用して投稿内容を生成"""
    try:
        response = requests.post(
            f"{API_URL}/generate",
            json={"prompt": prompt}
        )
        
        if response.status_code == 200:
            return response.json().get('content', 'デフォルト投稿内容')
    except:
        pass
    
    # フォールバック
    return f"今日も素晴らしい1日を！ {prompt.split()[0]} #Threads"

def generate_themed_content(theme, time_type):
    """テーマに基づいた投稿を生成"""
    templates = {
        "motivation": [
            "新しい1日の始まり！今日の目標は何ですか？ 🎯",
            "小さな一歩が大きな変化を生む 💪",
            "今日も自分らしく輝こう ✨"
        ],
        "productivity": [
            "効率的な仕事術：ポモドーロテクニックを試してみよう 🍅",
            "タスク管理のコツ：優先順位を明確に 📝",
            "集中力を高める環境づくり 🎧"
        ],
        "wellness": [
            "深呼吸で心を落ち着けよう 🧘",
            "水分補給を忘れずに 💧",
            "5分間のストレッチタイム 🤸"
        ]
    }
    
    import random
    return random.choice(templates.get(theme, ["素敵な1日を！"]))

def get_mood_for_time(time_type):
    """時間帯に応じたムードを返す"""
    moods = {
        "morning": "前向きで活力的",
        "lunch": "リラックスして親しみやすい",
        "evening": "落ち着いて振り返りを促す",
        "weekend_morning": "のんびりとした休日感",
        "weekend_afternoon": "アクティブで楽しい"
    }
    return moods.get(time_type, "ポジティブ")

def get_daily_theme(day_index):
    """日替わりテーマを返す"""
    themes = [
        "motivation",     # 月曜日
        "productivity",   # 火曜日
        "wellness",       # 水曜日
        "creativity",     # 木曜日
        "reflection",     # 金曜日
        "adventure",      # 土曜日
        "relaxation"      # 日曜日
    ]
    return themes[day_index % 7]

def generate_hashtags(time_type):
    """時間帯に応じたハッシュタグを生成"""
    hashtag_sets = {
        "morning": "#朝活 #GoodMorning #今日の目標",
        "lunch": "#ランチタイム #午後も頑張ろう",
        "evening": "#今日の振り返り #お疲れ様でした"
    }
    return hashtag_sets.get(time_type, "#Threads")

def generate_themed_hashtags(theme):
    """テーマに応じたハッシュタグを生成"""
    hashtag_sets = {
        "motivation": "#モチベーション #目標達成 #成長",
        "productivity": "#生産性向上 #仕事術 #効率化",
        "wellness": "#健康 #ウェルネス #セルフケア",
        "creativity": "#クリエイティブ #アイデア #創造性",
        "reflection": "#振り返り #学び #成長記録",
        "adventure": "#週末 #冒険 #新しい体験",
        "relaxation": "#リラックス #休日 #充電"
    }
    return hashtag_sets.get(theme, "#Threads #SNS")

def save_to_csv(posts, filename):
    """投稿データをCSVファイルに保存"""
    
    # CSVディレクトリを作成
    os.makedirs('csv_schedules', exist_ok=True)
    filepath = os.path.join('csv_schedules', filename)
    
    # UTF-8 BOM付きで保存（Excel対応）
    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        if posts:
            fieldnames = posts[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(posts)

def show_statistics(posts):
    """投稿統計を表示"""
    total = len(posts)
    by_type = {}
    by_theme = {}
    
    for post in posts:
        # タイプ別集計
        post_type = post.get('type', 'unknown')
        by_type[post_type] = by_type.get(post_type, 0) + 1
        
        # テーマ別集計
        theme = post.get('theme', 'unknown')
        by_theme[theme] = by_theme.get(theme, 0) + 1
    
    print("\n📊 投稿統計:")
    print(f"  総投稿数: {total}件")
    print(f"  1日平均: {total / 30:.1f}件")
    
    print("\n  時間帯別:")
    for post_type, count in by_type.items():
        print(f"    {post_type}: {count}件")
    
    print("\n  テーマ別:")
    for theme, count in by_theme.items():
        print(f"    {theme}: {count}件")

# スタンドアロン実行
if __name__ == "__main__":
    print("Threads投稿スケジュール生成ツール")
    print("1. 週間スケジュール")
    print("2. 月間スケジュール")
    
    choice = input("\n選択してください (1/2): ")
    
    if choice == "1":
        generate_weekly_schedule()
    elif choice == "2":
        generate_monthly_schedule()
    else:
        print("無効な選択です")