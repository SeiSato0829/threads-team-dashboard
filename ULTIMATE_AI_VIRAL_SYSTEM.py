#!/usr/bin/env python3
"""
🚀 究極のAIバイラル投稿システム - 本気の投稿生成版
生成に時間をかけても、真に効果的なコンテンツを作成
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# 必要なエンジンのインポート
try:
    from AI_POWERED_VIRAL_ENGINE import AdvancedViralEngine
    from MULTIPLE_POSTS_PER_DAY import MultiPostScheduler
    AI_ENGINE_AVAILABLE = True
except ImportError:
    AI_ENGINE_AVAILABLE = False

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

class UltimateAIViralSystem:
    """🚀 究極のAIバイラル投稿システム"""
    
    def __init__(self):
        if AI_ENGINE_AVAILABLE:
            self.ai_engine = AdvancedViralEngine()
            self.scheduler = MultiPostScheduler()
        else:
            raise ImportError("AI_POWERED_VIRAL_ENGINE.py が必要です")
    
    async def generate_ultimate_viral_posts(self, days: int = 7, posts_per_day: int = 5):
        """究極のバイラル投稿生成"""
        
        print("🚀 究極のAIバイラル投稿システム - 本気モード起動")
        print("=" * 70)
        print("⚠️  注意: 高品質な投稿生成のため、処理に時間がかかります")
        print("📊 生成内容:")
        print(f"   - 期間: {days}日間")
        print(f"   - 1日あたり: {posts_per_day}投稿")
        print(f"   - 合計: {days * posts_per_day}投稿")
        print()
        print("🧠 AI分析内容:")
        print("   ✅ 実際のバイラルパターンを深層分析")
        print("   ✅ 心理的トリガーの最適化")
        print("   ✅ エンゲージメント予測")
        print("   ✅ 多様性とオリジナリティの確保")
        print()
        
        confirm = input("生成を開始しますか？ (y/n): ")
        if confirm.lower() != 'y':
            print("キャンセルされました")
            return
        
        print("\n🔬 生成を開始します...")
        start_time = datetime.now()
        
        all_posts = []
        
        for day in range(days):
            target_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=day)
            
            print(f"\n📅 {target_date.strftime('%Y年%m月%d日')}の投稿生成")
            print("-" * 50)
            
            # AI駆動型生成
            daily_posts = await self.ai_engine.generate_daily_posts(posts_per_day, target_date)
            
            # データベース保存
            post_ids = self.scheduler.save_daily_posts(daily_posts, target_date)
            
            all_posts.extend(daily_posts)
            
            print(f"✅ {target_date.strftime('%m/%d')} 完了 - {posts_per_day}投稿を保存")
        
        # 生成時間
        generation_time = (datetime.now() - start_time).total_seconds()
        
        return all_posts, generation_time
    
    def display_ultimate_results(self, posts: List[Dict], generation_time: float):
        """究極の結果表示"""
        
        print(f"\n🎉 生成完了！")
        print("=" * 70)
        print(f"⏱️  生成時間: {generation_time:.1f}秒")
        print(f"📝 生成投稿数: {len(posts)}投稿")
        
        # エンゲージメント予測統計
        avg_engagement = sum(p['engagement_prediction'] for p in posts) / len(posts)
        max_engagement = max(p['engagement_prediction'] for p in posts)
        min_engagement = min(p['engagement_prediction'] for p in posts)
        
        print(f"\n📊 エンゲージメント予測:")
        print(f"   平均: {avg_engagement:.1f}/10")
        print(f"   最高: {max_engagement:.1f}/10")
        print(f"   最低: {min_engagement:.1f}/10")
        
        # 使用されたバイラルフォーミュラの統計
        formulas = {}
        for post in posts:
            formula = post.get('viral_formula', 'unknown')
            formulas[formula] = formulas.get(formula, 0) + 1
        
        print(f"\n🎯 使用バイラルフォーミュラ:")
        for formula, count in formulas.items():
            print(f"   {formula}: {count}回")
        
        # テーマ別統計
        themes = {}
        for post in posts:
            theme = post.get('theme', 'unknown')
            themes[theme] = themes.get(theme, 0) + 1
        
        print(f"\n📚 テーマ分布:")
        for theme, count in themes.items():
            print(f"   {theme}: {count}回")
        
        # サンプル表示
        print(f"\n📝 生成投稿サンプル（上位3件）:")
        print("=" * 70)
        
        # エンゲージメント予測でソート
        sorted_posts = sorted(posts, key=lambda x: x['engagement_prediction'], reverse=True)
        
        for i, post in enumerate(sorted_posts[:3], 1):
            print(f"\n🏆 TOP {i} - 予測エンゲージメント: {post['engagement_prediction']:.1f}/10")
            print(f"📅 {post['scheduled_time'].strftime('%m/%d %H:%M')}")
            print(f"🎯 テーマ: {post.get('theme', 'N/A')} / 感情: {post.get('emotion', 'N/A')}")
            print("-" * 50)
            print(post['content'])
            print("-" * 50)
        
        # インタラクティブ表示オプション
        if CLIPBOARD_AVAILABLE:
            print(f"\n💡 ヒント: 投稿をクリップボードにコピーして、Threadsに直接貼り付けできます")
            
            view_all = input("\n全ての投稿を確認しますか？ (y/n): ")
            if view_all.lower() == 'y':
                self._interactive_post_viewer(posts)
        
        # エクスポート情報
        try:
            csv_file = self.scheduler.export_schedule(len(posts) // 5)
            print(f"\n📄 スケジュールCSV: {csv_file}")
        except:
            pass
        
        # 成功の秘訣
        print(f"\n🎯 成功のポイント:")
        print("1️⃣ 各投稿は実際のバイラルパターンに基づいて生成")
        print("2️⃣ 心理的トリガーで読者の行動を促進")
        print("3️⃣ 多様なテーマとアプローチで飽きさせない")
        print("4️⃣ 全ての投稿に収益化リンクを配置")
        print("5️⃣ 最適な投稿時間で最大リーチを実現")
        
        # 予想成果
        self._show_expected_ultimate_results(posts)
    
    def _interactive_post_viewer(self, posts: List[Dict]):
        """インタラクティブ投稿ビューア"""
        
        print(f"\n📖 投稿ビューア（{len(posts)}件）")
        print("=" * 70)
        
        for i, post in enumerate(posts, 1):
            print(f"\n📝 投稿 {i}/{len(posts)}")
            print(f"📅 {post['scheduled_time'].strftime('%Y/%m/%d %H:%M')}")
            print(f"🎯 {post.get('theme', 'N/A')} ({post.get('emotion', 'N/A')})")
            print(f"📊 予測: {post['engagement_prediction']:.1f}/10")
            print("-" * 50)
            print(post['content'])
            print("-" * 50)
            
            if CLIPBOARD_AVAILABLE:
                action = input("\n[Enter]=次へ / [c]=コピー / [q]=終了: ")
                
                if action.lower() == 'q':
                    break
                elif action.lower() == 'c':
                    pyperclip.copy(post['content'])
                    print("📋 クリップボードにコピーしました！")
                    input("Enterで続行...")
            else:
                action = input("\n[Enter]=次へ / [q]=終了: ")
                if action.lower() == 'q':
                    break
    
    def _show_expected_ultimate_results(self, posts: List[Dict]):
        """究極の予想成果表示"""
        
        total_posts = len(posts)
        avg_engagement = sum(p['engagement_prediction'] for p in posts) / len(posts)
        
        # AIパワーによる成果倍率
        ai_multiplier = avg_engagement / 5.0  # エンゲージメント基準の倍率
        
        print(f"\n💎 究極のAIバイラルシステム予想成果:")
        print("=" * 60)
        print(f"📊 投稿数: {total_posts}投稿")
        print(f"🧠 AI最適化レベル: {avg_engagement:.1f}/10")
        print()
        
        # 成果予測
        base_engagement = 1000
        base_revenue = 5000
        base_followers = 50
        base_clicks = 100
        
        print(f"📈 予想エンゲージメント:")
        print(f"   {int(base_engagement * ai_multiplier * total_posts / 5):,} ~ {int(base_engagement * ai_multiplier * 1.5 * total_posts / 5):,} 反応")
        
        print(f"\n💰 予想収益:")
        print(f"   ¥{int(base_revenue * ai_multiplier * total_posts / 5):,} ~ ¥{int(base_revenue * ai_multiplier * 1.5 * total_posts / 5):,}")
        
        print(f"\n👥 予想フォロワー増加:")
        print(f"   {int(base_followers * ai_multiplier * total_posts / 5):,} ~ {int(base_followers * ai_multiplier * 1.5 * total_posts / 5):,} 人")
        
        print(f"\n🔗 予想リンククリック:")
        print(f"   {int(base_clicks * ai_multiplier * total_posts / 5):,} ~ {int(base_clicks * ai_multiplier * 1.5 * total_posts / 5):,} クリック")
        
        print(f"\n🚀 AIの威力:")
        print(f"   ✅ 通常投稿の{ai_multiplier:.1f}倍の効果")
        print(f"   ✅ 心理学的最適化で行動促進")
        print(f"   ✅ バイラル確率大幅アップ")
        print(f"   ✅ 長期的なブランド構築")

async def main():
    """メイン実行"""
    
    if not AI_ENGINE_AVAILABLE:
        print("❌ AI_POWERED_VIRAL_ENGINE.py が必要です")
        print("このシステムにはAIエンジンが必須です")
        return
    
    print("🚀 究極のAIバイラル投稿システム")
    print("=" * 70)
    print("本気の投稿生成モード - 品質重視")
    print()
    print("⚡ 機能:")
    print("- 実際のバイラルパターンをAI分析")
    print("- 心理学的アプローチで最適化")
    print("- 多様性とオリジナリティを確保")
    print("- エンゲージメント予測付き")
    print("- 完全自動スケジューリング")
    
    if CLIPBOARD_AVAILABLE:
        print("✅ クリップボード機能: 利用可能")
    else:
        print("💡 pip install pyperclip でクリップボード機能が使えます")
    
    print()
    
    # システム初期化
    system = UltimateAIViralSystem()
    
    # オプション選択
    print("📊 生成オプション:")
    print("1. クイック生成（2日分、1日5投稿）")
    print("2. 標準生成（7日分、1日5投稿）")
    print("3. 大量生成（14日分、1日6投稿）")
    print("4. カスタム設定")
    
    choice = input("\n選択してください (1-4): ")
    
    if choice == '1':
        days, posts_per_day = 2, 5
    elif choice == '2':
        days, posts_per_day = 7, 5
    elif choice == '3':
        days, posts_per_day = 14, 6
    elif choice == '4':
        days = int(input("日数を入力: "))
        posts_per_day = int(input("1日の投稿数を入力: "))
    else:
        print("無効な選択です")
        return
    
    # 生成実行
    posts, generation_time = await system.generate_ultimate_viral_posts(days, posts_per_day)
    
    # 結果表示
    system.display_ultimate_results(posts, generation_time)
    
    print("\n🎊 究極のAIバイラル投稿システム完了！")
    print("生成された投稿で、Threadsを制覇しましょう！")

if __name__ == "__main__":
    asyncio.run(main())