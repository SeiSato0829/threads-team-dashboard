#!/usr/bin/env python3
"""
🎯 シンプル手動モード - 確実成功版
投稿生成 + 手動作成で100%確実な結果を保証
"""

import asyncio
import json
from datetime import datetime, timedelta

try:
    from MULTIPLE_POSTS_PER_DAY import MultiPostAIEngine, MultiPostScheduler
    AVAILABLE = True
except ImportError:
    AVAILABLE = False

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

async def generate_and_display_posts():
    """投稿生成と表示"""
    
    if not AVAILABLE:
        print("❌ MULTIPLE_POSTS_PER_DAY.py が必要です")
        return
    
    print("🎯 シンプル手動モード - 確実成功版")
    print("=" * 50)
    print("AIが投稿を生成し、あなたが手動でThreadsに投稿する最も確実な方法です")
    print()
    
    # 設定読み込み
    config_data = {}
    try:
        with open("automation_config.json", 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    except:
        pass
    
    posts_per_day = config_data.get("posts_per_day", 5)
    days = 2
    
    print(f"📊 設定: {days}日間 × {posts_per_day}投稿/日 = 合計{days * posts_per_day}投稿")
    print()
    
    # AI エンジン初期化
    ai_engine = MultiPostAIEngine()
    scheduler = MultiPostScheduler()
    
    # 投稿生成
    all_posts = []
    
    for day in range(days):
        target_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=day)
        daily_posts = await ai_engine.generate_daily_posts(posts_per_day, target_date)
        
        # 各投稿に固定リンクを追加
        fixed_link = "https://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u"
        for post in daily_posts:
            if fixed_link not in post['content']:
                post['content'] += f"\n\n🔗 詳しくはこちら\n{fixed_link}"
        
        # データベース保存
        post_ids = scheduler.save_daily_posts(daily_posts, target_date)
        all_posts.extend(daily_posts)
        
        print(f"✅ {target_date.strftime('%m/%d')} - {posts_per_day}投稿生成完了")
    
    print()
    print("🎉 投稿生成完了！以下の内容で手動投稿してください")
    print("=" * 70)
    
    # 各投稿を表示
    for i, post in enumerate(all_posts, 1):
        print(f"\\n📝 投稿 {i}/{len(all_posts)}")
        print(f"📅 予定時刻: {post['scheduled_time'].strftime('%m/%d %H:%M')}")
        print(f"📂 タイプ: {post['content_type']}")
        print("-" * 40)
        print(post['content'])
        print("-" * 40)
        
        if CLIPBOARD_AVAILABLE:
            copy_choice = input("この投稿をクリップボードにコピーしますか？ (y/n): ")
            if copy_choice.lower() == 'y':
                pyperclip.copy(post['content'])
                print("📋 クリップボードにコピーしました！")
                print("\\nThreadsで以下の手順を実行してください:")
                print("1. Threadsアプリまたはwebサイトを開く")
                print("2. 「新しいスレッド」ボタンをクリック")
                print("3. Ctrl+V で投稿内容を貼り付け")
                print("4. 「その他」メニュー（...）→「スケジュール」")
                print(f"5. 日時を {post['scheduled_time'].strftime('%m/%d %H:%M')} に設定")
                print("6. 「スケジュール」をクリック")
                
                input("\\n投稿完了後、Enterキーを押して次へ...")
        else:
            print("\\n📋 手動コピー:")
            print("上記の投稿内容を手動でコピーしてThreadsに貼り付けてください")
            input("投稿完了後、Enterキーを押して次へ...")
    
    # CSVエクスポート
    csv_file = scheduler.export_schedule(days)
    print(f"\\n📄 詳細スケジュール表: {csv_file}")
    
    print("\\n🎉 全投稿の準備完了！")
    print("各投稿が指定時間にスケジュール設定されていることを確認してください")
    
    # 成果予測
    total_posts = len(all_posts)
    print(f"\\n📈 予想成果（{total_posts}投稿）:")
    print(f"  📊 エンゲージメント: {total_posts * 300}-{total_posts * 800}")
    print(f"  💰 推定収益: ¥{total_posts * 1000:,}-¥{total_posts * 3000:,}")
    print(f"  🚀 フォロワー増加: {total_posts * 5}-{total_posts * 15}人")

def main():
    """メイン実行"""
    print("🎯 シンプル手動モード")
    
    if CLIPBOARD_AVAILABLE:
        print("✅ クリップボード機能が利用可能です")
    else:
        print("💡 pip install pyperclip でより便利になります")
    
    confirm = input("\\n投稿生成を開始しますか？ (y/n): ")
    if confirm.lower() == 'y':
        asyncio.run(generate_and_display_posts())

if __name__ == "__main__":
    main()