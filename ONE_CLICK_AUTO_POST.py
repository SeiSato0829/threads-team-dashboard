#!/usr/bin/env python3
"""
ワンクリック完全自動投稿システム
投稿生成→Buffer予約まで全自動
"""

import os
import time
from simple_auto_post import generate_simple_post, save_to_schedule
from auto_post_to_buffer import AutoBufferPoster
from dotenv import load_dotenv

load_dotenv()

def main():
    print("""
    ╔══════════════════════════════════════════╗
    ║   🚀 ワンクリック自動投稿システム      ║
    ║      生成→予約まで完全自動化           ║
    ╚══════════════════════════════════════════╝
    """)
    
    # Buffer設定チェック
    if not os.getenv('BUFFER_ACCESS_TOKEN'):
        print("\n⚠️ 初回設定が必要です！")
        print("\n【簡単3ステップ】")
        print("1. https://buffer.com にアクセスしてログイン")
        print("2. https://buffer.com/app/account/apps で新規アプリ作成")
        print("3. Access Tokenをコピー")
        print("\n.envファイルに以下を追加：")
        print("BUFFER_ACCESS_TOKEN=あなたのトークン")
        print("\n設定後、もう一度実行してください。")
        input("\nEnterキーで終了...")
        return
    
    # 投稿数を選択
    print("\n📝 何件の投稿を自動生成・予約しますか？")
    print("1. 1日分（4件）")
    print("2. 3日分（12件）")
    print("3. 1週間分（28件）")
    print("4. カスタム")
    
    choice = input("\n選択 (1-4): ")
    
    if choice == "1":
        count = 4
    elif choice == "2":
        count = 12
    elif choice == "3":
        count = 28
    elif choice == "4":
        count = int(input("投稿数を入力: "))
    else:
        count = 4
    
    print(f"\n🤖 {count}件の投稿を生成します...")
    print("="*50)
    
    # 投稿を生成
    for i in range(count):
        print(f"\n生成中... [{i+1}/{count}]", end="")
        post = generate_simple_post()
        saved = save_to_schedule(post)
        print(f" ✅")
        print(f"内容: {post[:50]}...")
        time.sleep(1)  # API制限対策
    
    print("\n✨ 生成完了！")
    print("="*50)
    
    # Bufferに予約
    print("\n📅 Bufferに予約投稿を開始します...")
    
    poster = AutoBufferPoster()
    poster.bulk_schedule_from_json()
    
    print("\n🎉 すべて完了しました！")
    print("\nBufferダッシュボードで確認：")
    print("https://buffer.com/app/profile/threads/tab/queue")

if __name__ == "__main__":
    main()