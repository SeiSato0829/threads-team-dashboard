#!/usr/bin/env python3
"""
シンプルな自動投稿システム - 動作確認版
"""

import os
import json
import time
from datetime import datetime
import random

# 既存のCSVファイルを読み込んで活用
def load_existing_data():
    """既存の投稿データを読み込み"""
    data_sources = [
        "money_optimization_sheets/02_高収益テンプレート.tsv",
        "csv_input/sample_posts.csv"
    ]
    
    for source in data_sources:
        if os.path.exists(source):
            print(f"✅ データファイル発見: {source}")
            return source
    return None

def generate_simple_post():
    """シンプルな投稿を生成"""
    topics = [
        "Web制作を1万円で始める方法",
        "AI活用で業務効率90%アップ",
        "フリーランスが月収50万円を達成する秘訣",
        "SNSマーケティングの新常識",
        "副業で月10万円を確実に稼ぐ方法"
    ]
    
    templates = [
        """【保存版】{topic}

知ってましたか？
実は{fact}なんです。

私も最初は{struggle}でしたが、
今では{achievement}を達成しました。

詳しい方法を知りたい方は
コメントに「👍」をお願いします！

#ビジネス #副業 #フリーランス""",
        
        """多くの人が間違えている{topic}

❌ 間違い：{wrong}
✅ 正解：{right}

この違いを知るだけで
{benefit}できます。

実践した結果→{result}

詳細はプロフィールリンクから📝

#学び #スキルアップ #仕事術"""
    ]
    
    # ランダムに選択
    topic = random.choice(topics)
    template = random.choice(templates)
    
    # 変数を埋める
    post = template.format(
        topic=topic,
        fact="たった3つのポイントを押さえるだけ",
        struggle="月収20万円で停滞",
        achievement="安定した収益化",
        wrong="とにかく量をこなす",
        right="質の高いコンテンツに集中",
        benefit="収益が2倍以上に",
        result="3ヶ月で売上300%アップ"
    )
    
    return post

def save_to_schedule(post_content):
    """投稿をスケジュールファイルに保存"""
    schedule_file = "scheduled_posts.json"
    
    # 既存のスケジュールを読み込み
    if os.path.exists(schedule_file):
        with open(schedule_file, 'r', encoding='utf-8') as f:
            schedule = json.load(f)
    else:
        schedule = []
    
    # 新しい投稿を追加
    new_post = {
        "id": len(schedule) + 1,
        "content": post_content,
        "scheduled_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    schedule.append(new_post)
    
    # 保存
    with open(schedule_file, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, ensure_ascii=False, indent=2)
    
    return new_post

def display_dashboard():
    """簡単なダッシュボード表示"""
    print("\n" + "="*60)
    print("📊 Threads AI 自動投稿ダッシュボード")
    print("="*60)
    
    # スケジュールされた投稿を表示
    if os.path.exists("scheduled_posts.json"):
        with open("scheduled_posts.json", 'r', encoding='utf-8') as f:
            schedule = json.load(f)
        
        print(f"\n📅 スケジュール済み投稿: {len(schedule)}件")
        
        # 最新3件を表示
        for post in schedule[-3:]:
            print(f"\n[投稿 #{post['id']}] - {post['scheduled_time']}")
            print(f"内容: {post['content'][:50]}...")
            print(f"ステータス: {post['status']}")
    
    print("\n" + "="*60)

def main():
    """メイン処理"""
    print("\n🚀 Threads AI 自動投稿システム (シンプル版)")
    print("="*60)
    
    while True:
        print("\n何をしますか？")
        print("1. 新しい投稿を生成")
        print("2. スケジュール済み投稿を確認")
        print("3. 自動生成デモ（5件生成）")
        print("4. 終了")
        
        choice = input("\n選択してください (1-4): ")
        
        if choice == "1":
            print("\n🤖 AI投稿を生成中...")
            post = generate_simple_post()
            print("\n生成された投稿:")
            print("-"*40)
            print(post)
            print("-"*40)
            
            save_choice = input("\nこの投稿を保存しますか？ (y/n): ")
            if save_choice.lower() == 'y':
                saved = save_to_schedule(post)
                print(f"✅ 投稿 #{saved['id']} を保存しました！")
        
        elif choice == "2":
            display_dashboard()
        
        elif choice == "3":
            print("\n🎯 5件の投稿を自動生成します...")
            for i in range(5):
                print(f"\n生成中... ({i+1}/5)")
                post = generate_simple_post()
                saved = save_to_schedule(post)
                print(f"✅ 投稿 #{saved['id']} を生成・保存しました")
                time.sleep(1)  # 少し待機
            
            print("\n✨ 5件の投稿生成が完了しました！")
            display_dashboard()
        
        elif choice == "4":
            print("\n👋 終了します。")
            break
        
        else:
            print("\n❌ 無効な選択です。")

if __name__ == "__main__":
    main()