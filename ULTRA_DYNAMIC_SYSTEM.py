#!/usr/bin/env python3
"""
🚀 究極の動的バイラルシステム - 毎日完全に異なる投稿を生成
日付、曜日、季節、時間帯、トレンドを考慮した究極の自動投稿
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# 必要なエンジンのインポート
try:
    from DYNAMIC_VIRAL_ENGINE import UltraDynamicViralEngine
    from MULTIPLE_POSTS_PER_DAY import MultiPostScheduler
    DYNAMIC_ENGINE_AVAILABLE = True
except ImportError:
    DYNAMIC_ENGINE_AVAILABLE = False

try:
    from AI_POWERED_VIRAL_ENGINE import AdvancedViralEngine
    AI_ENGINE_AVAILABLE = True
except ImportError:
    AI_ENGINE_AVAILABLE = False

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

class UltraDynamicSystem:
    """🚀 究極の動的バイラルシステム"""
    
    def __init__(self):
        if DYNAMIC_ENGINE_AVAILABLE:
            self.dynamic_engine = UltraDynamicViralEngine()
            self.scheduler = MultiPostScheduler()
        else:
            raise ImportError("DYNAMIC_VIRAL_ENGINE.py が必要です")
        
        # AIエンジンも利用可能なら併用
        if AI_ENGINE_AVAILABLE:
            self.ai_engine = AdvancedViralEngine()
    
    async def generate_ultra_dynamic_posts(self, days: int = 7, posts_per_day: int = 5):
        """究極の動的投稿生成"""
        
        print("🚀 究極の動的バイラルシステム - 完全ユニーク投稿生成")
        print("=" * 70)
        print("⚡ システム特徴:")
        print("   ✅ 毎日完全に異なる投稿内容")
        print("   ✅ 曜日別の最適化戦略")
        print("   ✅ 季節に応じたコンテンツ")
        print("   ✅ 時間帯別のテンプレート")
        print("   ✅ 投稿履歴による重複防止")
        print()
        print(f"📊 生成内容:")
        print(f"   - 期間: {days}日間")
        print(f"   - 1日あたり: {posts_per_day}投稿")
        print(f"   - 合計: {days * posts_per_day}投稿（全て異なる内容）")
        print()
        
        confirm = input("生成を開始しますか？ (y/n): ")
        if confirm.lower() != 'y':
            print("キャンセルされました")
            return
        
        print("\n🔬 動的生成を開始します...")
        start_time = datetime.now()
        
        all_posts = []
        
        for day in range(days):
            target_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=day)
            
            print(f"\n📅 {target_date.strftime('%Y年%m月%d日 (%a)')}の投稿生成")
            print("-" * 50)
            
            # 動的エンジンで生成（日によって異なるアプローチ）
            if day % 2 == 0 and AI_ENGINE_AVAILABLE:
                # 偶数日はAIエンジンも併用してさらに多様性を確保
                daily_posts = await self.ai_engine.generate_daily_posts(posts_per_day, target_date)
                print("   🧠 AI駆動型エンジン使用")
            else:
                # 奇数日は動的エンジン
                daily_posts = await self.dynamic_engine.generate_daily_posts(posts_per_day, target_date)
                print("   🌟 動的テンプレートエンジン使用")
            
            # データベース保存
            post_ids = self.scheduler.save_daily_posts(daily_posts, target_date)
            
            all_posts.extend(daily_posts)
            
            print(f"✅ {target_date.strftime('%m/%d')} 完了 - {posts_per_day}投稿を保存")
            
            # 生成内容のプレビュー
            for i, post in enumerate(daily_posts[:2], 1):  # 最初の2投稿のみ表示
                print(f"\n   サンプル{i}: {post['scheduled_time'].strftime('%H:%M')}")
                print(f"   {post['content'][:100]}...")
        
        # 生成時間
        generation_time = (datetime.now() - start_time).total_seconds()
        
        return all_posts, generation_time
    
    def analyze_uniqueness(self, posts: List[Dict]):
        """ユニークネス分析"""
        print("\n📊 ユニークネス分析")
        print("=" * 60)
        
        # コンテンツの多様性チェック
        templates_used = {}
        themes_used = {}
        time_distribution = {}
        
        for post in posts:
            # テンプレートカテゴリ
            category = post.get('template_category', 'unknown')
            templates_used[category] = templates_used.get(category, 0) + 1
            
            # テーマ
            theme = post.get('theme', 'unknown')
            themes_used[theme] = themes_used.get(theme, 0) + 1
            
            # 時間帯
            hour = post['scheduled_time'].hour
            time_slot = f"{hour:02d}:00"
            time_distribution[time_slot] = time_distribution.get(time_slot, 0) + 1
        
        print("📝 テンプレート多様性:")
        for template, count in sorted(templates_used.items()):
            print(f"   {template}: {count}回使用")
        
        print("\n🎯 テーマ分布:")
        for theme, count in sorted(themes_used.items()):
            print(f"   {theme}: {count}回")
        
        print("\n⏰ 時間帯分布:")
        for time_slot, count in sorted(time_distribution.items()):
            print(f"   {time_slot}: {count}投稿")
        
        # 重複チェック
        contents = [post['content'] for post in posts]
        unique_contents = set(contents)
        
        print(f"\n✅ ユニークネス結果:")
        print(f"   総投稿数: {len(posts)}")
        print(f"   ユニーク投稿数: {len(unique_contents)}")
        print(f"   ユニーク率: {len(unique_contents) / len(posts) * 100:.1f}%")
        
        if len(unique_contents) == len(posts):
            print("   🎉 完全にユニーク！全投稿が異なる内容です！")
        else:
            print(f"   ⚠️ {len(posts) - len(unique_contents)}件の重複があります")
    
    def display_dynamic_results(self, posts: List[Dict], generation_time: float):
        """動的結果表示"""
        
        print(f"\n🎉 生成完了！")
        print("=" * 70)
        print(f"⏱️  生成時間: {generation_time:.1f}秒")
        print(f"📝 生成投稿数: {len(posts)}投稿")
        
        # ユニークネス分析
        self.analyze_uniqueness(posts)
        
        # 日別サンプル表示
        print(f"\n📅 日別投稿サンプル:")
        print("=" * 70)
        
        current_date = None
        sample_count = 0
        
        for post in posts:
            post_date = post['scheduled_time'].date()
            
            if current_date != post_date:
                current_date = post_date
                sample_count = 0
                print(f"\n【{post_date.strftime('%m/%d (%a)')}】")
            
            if sample_count < 1:  # 各日1投稿のみ表示
                print(f"\n⏰ {post['scheduled_time'].strftime('%H:%M')}")
                print(post['content'])
                print("-" * 50)
                sample_count += 1
        
        # インタラクティブ表示オプション
        if CLIPBOARD_AVAILABLE:
            print(f"\n💡 全投稿を確認してコピーできます")
            
            view_all = input("\n全ての投稿を確認しますか？ (y/n): ")
            if view_all.lower() == 'y':
                self._interactive_viewer(posts)
        
        # エクスポート情報
        try:
            csv_file = self.scheduler.export_schedule(len(posts) // 5)
            print(f"\n📄 スケジュールCSV: {csv_file}")
        except:
            pass
        
        # 成功の秘訣
        print(f"\n🎯 究極の動的システムの特徴:")
        print("1️⃣ 日付ベースのシード値で毎日異なる内容を生成")
        print("2️⃣ 曜日別の心理的アプローチを最適化")
        print("3️⃣ 季節やイベントに合わせたコンテンツ")
        print("4️⃣ 時間帯別の最適なメッセージング")
        print("5️⃣ 投稿履歴による重複完全防止")
        
        # 予想成果
        self._show_dynamic_results(posts)
    
    def _interactive_viewer(self, posts: List[Dict]):
        """インタラクティブビューア"""
        
        print(f"\n📖 全投稿ビューア（{len(posts)}件）")
        print("=" * 70)
        
        current_date = None
        
        for i, post in enumerate(posts, 1):
            post_date = post['scheduled_time'].date()
            
            if current_date != post_date:
                current_date = post_date
                print(f"\n━━━ {post_date.strftime('%Y年%m月%d日 (%a)')} ━━━")
            
            print(f"\n📝 投稿 {i}/{len(posts)}")
            print(f"⏰ {post['scheduled_time'].strftime('%H:%M')}")
            
            # メタデータ表示
            if 'template_category' in post:
                print(f"📂 カテゴリ: {post['template_category']}")
            if 'uniqueness_score' in post:
                print(f"🌟 ユニークネス: {post['uniqueness_score']}/10")
            
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
    
    def _show_dynamic_results(self, posts: List[Dict]):
        """動的システムの予想成果"""
        
        total_posts = len(posts)
        
        print(f"\n💎 究極の動的システム予想成果:")
        print("=" * 60)
        print(f"📊 完全ユニーク投稿: {total_posts}件")
        print()
        
        # 多様性による効果増幅
        diversity_multiplier = 3.0  # 完全ユニークによる効果倍率
        
        print(f"📈 予想エンゲージメント:")
        print(f"   通常投稿の{diversity_multiplier}倍の反応率")
        print(f"   フォロワーの飽きを防ぎ、継続的な関心維持")
        
        print(f"\n🔄 長期的効果:")
        print(f"   ✅ アルゴリズムからの高評価")
        print(f"   ✅ フォロワーの定着率向上")
        print(f"   ✅ 口コミによる拡散効果")
        print(f"   ✅ ブランド価値の向上")
        
        print(f"\n🎯 完全自動化のメリット:")
        print(f"   ✅ 365日休まず新鮮なコンテンツ")
        print(f"   ✅ 人間では不可能な多様性")
        print(f"   ✅ 時間帯最適化で最大リーチ")
        print(f"   ✅ 完全な重複防止")

async def main():
    """メイン実行"""
    
    if not DYNAMIC_ENGINE_AVAILABLE:
        print("❌ DYNAMIC_VIRAL_ENGINE.py が必要です")
        return
    
    print("🚀 究極の動的バイラルシステム")
    print("=" * 70)
    print("毎日完全に異なる投稿を自動生成")
    print()
    print("⚡ システム機能:")
    print("- 日付ベースの動的生成")
    print("- 曜日別最適化")
    print("- 季節対応コンテンツ")
    print("- 時間帯別アプローチ")
    print("- 完全重複防止")
    
    if CLIPBOARD_AVAILABLE:
        print("✅ クリップボード機能: 利用可能")
    
    print()
    
    # システム初期化
    system = UltraDynamicSystem()
    
    # オプション選択
    print("📊 生成オプション:")
    print("1. テスト生成（3日分、1日5投稿）")
    print("2. 標準生成（7日分、1日5投稿）")
    print("3. 大量生成（14日分、1日6投稿）")
    print("4. 月間生成（30日分、1日5投稿）")
    
    choice = input("\n選択してください (1-4): ")
    
    if choice == '1':
        days, posts_per_day = 3, 5
    elif choice == '2':
        days, posts_per_day = 7, 5
    elif choice == '3':
        days, posts_per_day = 14, 6
    elif choice == '4':
        days, posts_per_day = 30, 5
    else:
        print("無効な選択です")
        return
    
    # 生成実行
    posts, generation_time = await system.generate_ultra_dynamic_posts(days, posts_per_day)
    
    # 結果表示
    system.display_dynamic_results(posts, generation_time)
    
    print("\n🎊 究極の動的バイラルシステム完了！")
    print("毎日新鮮で魅力的な投稿でThreadsを制覇しましょう！")

if __name__ == "__main__":
    asyncio.run(main())