#!/usr/bin/env python3
"""
🚀 1日複数投稿対応版 - 時間指定自動化システム
1日3-5投稿の収益最大化戦略対応
"""

import os
import json
import asyncio
import time
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import pandas as pd

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

@dataclass
class MultiplePostStrategy:
    """1日複数投稿戦略"""
    posts_per_day: int
    optimal_times: List[str]  # ["07:00", "12:30", "19:00", "21:00"]
    content_mix: Dict[str, float]  # {"educational": 0.4, "viral": 0.3, "cta": 0.3}
    min_interval_hours: float  # 最小間隔時間

class MultiPostAIEngine:
    """1日複数投稿対応AIエンジン"""
    
    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None
        self.setup_ai_clients()
        
        # コンテンツタイプ別テンプレート - 大幅に多様化
        self.content_templates = {
            "educational": [
                {
                    "template": "【{time_period}で習得】{skill_name}入門\n\n初心者が最初に覚えるべきは：\n✅ {point1}\n✅ {point2}\n✅ {point3}\n\nこれだけで{benefit}できます。\n\n詳しい手順はコメントで質問してください📝\n\n#{hashtag1} #学び #スキルアップ",
                    "optimal_hours": [7, 8, 9, 12, 13]
                },
                {
                    "template": "知らないと損する{skill_name}の真実\n\n多くの人が勘違いしていること：\n❌ {misconception}\n✅ 正解：{truth}\n\n実際に試してみると{result}でした。\n\n#{hashtag1} #豆知識 #なるほど",
                    "optimal_hours": [12, 13, 16, 17]
                },
                {
                    "template": "【保存版】{skill_name}を完全マスターする3ステップ\n\nステップ1: {point1}\nステップ2: {point2}\nステップ3: {point3}\n\n実践すれば{time_period}で{benefit}可能です✨\n\n#{hashtag1} #マスター #実践",
                    "optimal_hours": [8, 14, 18, 20]
                },
                {
                    "template": "なぜ{skill_name}で差がつくのか？\n\n成功する人の共通点：\n🔥 {point1}\n🔥 {point2}\n🔥 {point3}\n\n{time_period}続けるだけで人生変わります。\n\n#{hashtag1} #成功法則 #差別化",
                    "optimal_hours": [7, 13, 19, 21]
                }
            ],
            "viral": [
                {
                    "template": "これ見て震えた...\n\n{shocking_fact}\n\n調べてみたら本当でした😨\n\n特に{detail}は衝撃的。\n\n皆さんはどう思いますか？\n\n#{hashtag1} #衝撃 #マジで",
                    "optimal_hours": [19, 20, 21, 22]
                },
                {
                    "template": "【警告】まだ{bad_habit}してる人いる？\n\n2025年の常識：{new_way}\n\n変えただけで{improvement}しました。\n\n遅れる前に今すぐ始めましょう🔥\n\n#{hashtag1} #2025年 #常識",
                    "optimal_hours": [18, 19, 20, 21]
                },
                {
                    "template": "【衡撃】バズったこのデータ...\n\n{shocking_fact}って知ってました？😱\n\n私も最初は信じられなかったけど、{detail}を見て納得。\n\nこれは知っておくべき情報ですね✨\n\n#{hashtag1} #知らなきゃ損 #真実",
                    "optimal_hours": [17, 20, 22]
                },
                {
                    "template": "みんなが間違えてる{topic}の話\n\nリアルな真実を暴露します…\n\n❌ 多くの人：{misconception}\n✅ 本当のところ：{truth}\n\n実証結果：{result}\n\n騙されないで🔥\n\n#{hashtag1} #真実 #暴露",
                    "optimal_hours": [19, 21, 23]
                }
            ],
            "cta": [
                {
                    "template": "【限定公開】{offer_name}を無料配布中\n\n今だけ{normal_price}→無料🎁\n\n内容：\n・{feature1}\n・{feature2}\n・{feature3}\n\n受け取りはプロフィールリンクから\n\n#{hashtag1} #無料 #限定",
                    "optimal_hours": [11, 14, 17, 20]
                },
                {
                    "template": "{question}\n\n同じ悩みを持つ方、一緒に解決しませんか？\n\n実は{solution_hint}があるんです。\n\n詳しく知りたい方はDMください💌\n\n#{hashtag1} #相談 #解決法",
                    "optimal_hours": [10, 15, 18, 21]
                }
            ]
        }
        
        # より多様なCTAテンプレートを追加
        self.content_templates["cta"].extend([
            {
                "template": "【コメントまで読んで🙏】\n\n{question}でお悩みの方に…\n\n特別に{offer_name}をプレゼントします✨\n\n通常{normal_price}の内容が今だけ無料です！\n\nコメントで「欲しい」と一言ください💬\n\n#{hashtag1} #プレゼント #限定",
                "optimal_hours": [12, 16, 19, 22]
            },
            {
                "template": "本気で変わりたい人だけ見て🔥\n\n{offer_name}で人生が激変した人たちの声：\n\n\"✨{feature1}で作業が10倍効率化した\"\n\"🚀{feature2}で収入が3倍に\"\n\"🏆{feature3}で結果がでるまでサポート\"\n\n本気の方だけDMください。\n\n#{hashtag1} #人生激変 #本気",
                "optimal_hours": [13, 17, 20, 23]
            }
        ])
        
        # 1日の最適投稿スケジュールパターン（カスタム時間帯：8時、12時、19時、21時、23時）
        self.daily_patterns = {
            3: {  # 1日3投稿
                "times": ["09:00", "19:00", "23:00"],
                "types": ["educational", "viral", "cta"],
                "intervals": [10.0, 4.0, 10.0]  # 時間間隔
            },
            4: {  # 1日4投稿
                "times": ["09:00", "12:00", "19:00", "23:00"],
                "types": ["educational", "viral", "viral", "cta"],
                "intervals": [3.0, 7.0, 4.0, 10.0]
            },
            5: {  # 1日5投稿（全指定時間帯使用）
                "times": ["09:00", "12:00", "19:00", "21:00", "23:00"],
                "types": ["educational", "viral", "educational", "viral", "cta"],
                "intervals": [3.0, 7.0, 2.0, 2.0, 10.0]
            },
            6: {  # 1日6投稿（指定時間帯を最大活用）
                "times": ["09:00", "12:00", "19:00", "21:00", "23:00", "09:00"],
                "types": ["educational", "viral", "educational", "viral", "cta", "educational"],
                "intervals": [3.0, 7.0, 2.0, 2.0, 10.0, 0.0]
            }
        }
    
    def setup_ai_clients(self):
        """AIクライアント設定"""
        if ANTHROPIC_AVAILABLE and os.getenv('ANTHROPIC_API_KEY'):
            self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            self.openai_client = openai.Client(api_key=os.getenv('OPENAI_API_KEY'))
    
    async def generate_daily_posts(self, posts_per_day: int = 4, target_date: datetime = None) -> List[Dict]:
        """1日分の投稿を生成"""
        if target_date is None:
            target_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if posts_per_day not in self.daily_patterns:
            posts_per_day = 4  # デフォルト
            
        pattern = self.daily_patterns[posts_per_day]
        posts = []
        
        print(f"📅 {target_date.strftime('%m/%d')} - {posts_per_day}投稿を生成中...")
        
        for i, (time_str, content_type) in enumerate(zip(pattern["times"], pattern["types"])):
            print(f"  🤖 {i+1}/{posts_per_day} - {time_str} ({content_type}) 生成中...")
            
            # 投稿時刻を設定
            hour, minute = map(int, time_str.split(':'))
            post_time = target_date.replace(hour=hour, minute=minute)
            
            # コンテンツ生成
            content = await self._generate_content_by_type(content_type, i+1)
            
            posts.append({
                "content": content,
                "scheduled_time": post_time,
                "content_type": content_type,
                "post_number": i + 1,
                "total_posts": posts_per_day
            })
            
            await asyncio.sleep(0.5)  # API制限対策
        
        return posts
    
    async def _generate_content_by_type(self, content_type: str, post_number: int) -> str:
        """コンテンツタイプ別生成 - 高エンゲージメント最適化版"""
        templates = self.content_templates[content_type]
        
        # テンプレート選択を改善 - ランダム性と時間ベースで選択
        import time
        import random
        
        # 時刻と投稿番号でシードを変更
        seed_value = int(time.time() * 1000) + post_number * 17  # 素数を使ってよりランダムに
        random.seed(seed_value)
        
        # ランダムにテンプレートを選択（単純なモジュロではなく）
        template = random.choice(templates)
        
        # 変数データを準備（ランダム性を含む）
        variables = self._get_variables_for_type(content_type, post_number)
        
        # AI生成またはテンプレート置換
        if self.anthropic_client or self.openai_client:
            content = await self._ai_enhance_content(template["template"], variables, content_type)
        else:
            content = self._replace_template_variables(template["template"], variables)
        
        # どのケースでも固定リンクを追加保証
        fixed_link = "https://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u"
        if fixed_link not in content:
            content += f"\n\n🔗 詳しくはこちら\n{fixed_link}"
        
        return content
    
    def _get_variables_for_type(self, content_type: str, post_number: int) -> Dict[str, str]:
        """コンテンツタイプ別変数データ - 改良版で重複回避"""
        import random
        import time
        
        # より多様なデータセットで重複を防ぐ
        random.seed(time.time() + post_number)  # 時間ベースのシード
        
        if content_type == "educational":
            time_periods = ["5分", "10分", "15分", "30分", "1時間", "3分", "7分", "20分"]
            skill_names = ["時間管理", "AI活用", "副業準備", "投資基礎", "効率化", "自動化", "収益アップ", "生産性向上"]
            points = [
                ["基本概念を理解する", "実践的な手順を覚える", "継続的な改善を行う"],
                ["正しいマインドセットを身につける", "具体的なアクションプランを作る", "結果を測定・改善する"],
                ["必要な知識を体系的に学ぶ", "実際に手を動かして経験する", "PDCAサイクルを回す"],
                ["基礎から応用まで段階的に進む", "実例を通じて理解を深める", "習慣化まで継続する"]
            ]
            benefits = ["確実に成果を出す", "短期間で結果を実感", "収益を最大化", "時間を有効活用"]
            hashtags = ["効率化", "スキルアップ", "学び", "成長"]
            
            point_set = points[post_number % len(points)]
            
            return {
                "time_period": random.choice(time_periods),
                "skill_name": skill_names[post_number % len(skill_names)],
                "point1": point_set[0],
                "point2": point_set[1], 
                "point3": point_set[2],
                "benefit": benefits[post_number % len(benefits)],
                "hashtag1": hashtags[post_number % len(hashtags)]
            }
            
        elif content_type == "viral":
            shocking_facts = [
                "成功者の95%が朝型人間",
                "AI導入企業の収益が40%向上", 
                "副業年収500万円の人が急増中",
                "リモートワーク導入で生産性25%アップ",
                "自動化ツール活用で作業時間70%削減",
                "効率化を実践する人の年収が平均30%高い",
                "時間管理スキルで人生満足度が2倍に",
                "投資を始めた人の80%が資産増加を実感"
            ]
            
            details = [
                "その理由と具体的データ",
                "実際の成功事例と統計",
                "専門家が分析した背景",
                "最新の調査結果による裏付け",
                "業界レポートが示す真実"
            ]
            
            # viral用のテンプレート変数追加
            bad_habits = ["効率の悪い作業", "時間の無駄遣い", "古い手法", "非効率な習慣"]
            new_ways = ["AI活用の最新手法", "自動化による効率化", "データ駆動の判断", "科学的アプローチ"]
            improvements = ["作業効率が劇的向上", "収益が倍増", "ストレスが激減", "自由時間が3倍に"]
            
            misconceptions = ["時間をかければ良い結果が出る", "忙しいほど価値がある", "完璧主義が成功への道", "多くのタスクをこなすべき"]
            truths = ["効率的な方法で短時間で成果を出す", "価値の高い活動に集中する", "80%の完成度で素早く実行する", "重要なタスクを選別して集中する"]
            results = ["生産性が2倍になった", "収入が50%アップした", "自由時間が増えた", "ストレスが激減した"]
            
            topics = ["時間管理", "効率化", "副業", "投資", "AI活用", "自動化", "生産性向上", "収益最大化"]
            
            return {
                "shocking_fact": shocking_facts[post_number % len(shocking_facts)],
                "detail": details[post_number % len(details)],
                "bad_habit": bad_habits[post_number % len(bad_habits)],
                "new_way": new_ways[post_number % len(new_ways)],
                "improvement": improvements[post_number % len(improvements)],
                "topic": topics[post_number % len(topics)],
                "misconception": misconceptions[post_number % len(misconceptions)],
                "truth": truths[post_number % len(truths)],
                "result": results[post_number % len(results)],
                "hashtag1": "衝撃事実"
            }
            
        elif content_type == "cta":
            offer_names = [
                "効率化テンプレート集",
                "AI活用ガイド",
                "副業スターターキット",
                "時間管理マスターパック",
                "自動化ツールセット",
                "収益最大化レポート",
                "生産性向上プログラム",
                "成功法則ハンドブック"
            ]
            
            prices = ["9,800円", "12,800円", "15,800円", "19,800円"]
            
            feature_sets = [
                ["即実践可能なテンプレート30個", "成功事例の詳細解説", "個別サポート30日間"],
                ["AIツールの実践ガイド50選", "効率化の具体的手順", "専門家による個別相談"],
                ["収益化戦略の完全マップ", "実証済みノウハウ集", "メンバー限定コミュニティ"],
                ["時短テクニック100選", "生産性2倍化メソッド", "継続サポートシステム"]
            ]
            
            questions = [
                "効率化で悩んでいませんか？",
                "時間管理でお困りですか？",
                "収益アップしたくありませんか？",
                "自動化に興味ありませんか？",
                "生産性を向上させたいですか？"
            ]
            
            solution_hints = [
                "実は3つのポイントを押さえるだけ",
                "たった1つの習慣を変えるだけ",
                "シンプルな仕組みを作るだけ",
                "正しい優先順位をつけるだけ"
            ]
            
            feature_set = feature_sets[post_number % len(feature_sets)]
            
            return {
                "offer_name": offer_names[post_number % len(offer_names)],
                "normal_price": prices[post_number % len(prices)],
                "feature1": feature_set[0],
                "feature2": feature_set[1],
                "feature3": feature_set[2],
                "question": questions[post_number % len(questions)],
                "solution_hint": solution_hints[post_number % len(solution_hints)],
                "hashtag1": "無料配布"
            }
        
        return {}
    
    async def _ai_enhance_content(self, template: str, variables: Dict[str, str], content_type: str) -> str:
        """AI でコンテンツを強化 - 2025年高エンゲージメント最適化"""
        base_content = self._replace_template_variables(template, variables)
        
        # コンテンツタイプ別の特化プロンプト
        type_specific_instructions = {
            "educational": "学びの価値と実践的なメリットを強調。数値や具体例を多用し、アクションを促す要素を含める",
            "viral": "衝撃的で情緒に訴える内容。データや統計で信懘性を高め、シェアしたくなる要素を含む",
            "cta": "明確なベネフィットと価値提案を提示。緊急性と希少性を演出し、具体的なアクションを促す"
        }
        
        # 2025年のトレンドを反映したプロンプト
        prompt = f"""
        あなたは2025年のSNSバイラル投稿のエキスパートです。以下の投稿をより魅力的でエンゲージメントの高い内容に改良してください：
        
        元の投稿：
        {base_content}
        
        改良指針 ({content_type}タイプ):
        {type_specific_instructions.get(content_type, "魅力的でエンゲージメントの高い内容にする")}
        
        2025年の最新条件：
        ✅ 500文字以内で簡潔に
        ✅ エンゲージメント率9%以上を目指す
        ✅ 具体的な数値やデータを含む
        ✅ 感情に訴える表現を使う
        ✅ アクションを促すCTAを含む
        ✅ 2025年の最新トレンドを反映
        ✅ 自然で読みやすい日本語
        ✅ ハッシュタグは3個以内
        
        最適化された投稿を生成してください。
        """
        
        if self.anthropic_client:
            try:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1200,
                    temperature=0.8  # クリエイティビティを高める
                )
                return response.content[0].text.strip()
            except Exception as e:
                print(f"⚠️ AI生成エラー: {e}")
                return base_content
        
        elif self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1200,
                    temperature=0.8
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"⚠️ AI生成エラー: {e}")
                return base_content
        
        return base_content
    
    def _replace_template_variables(self, template: str, variables: Dict[str, str]) -> str:
        """テンプレート変数を置換 + 固定リンク追加"""
        content = template
        for key, value in variables.items():
            content = content.replace(f"{{{key}}}", value)
        
        # 固定リンクを必ず追加
        fixed_link = "https://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u"
        
        # リンクがまだ含まれていない場合のみ追加
        if fixed_link not in content:
            content += f"\n\n🔗 詳しくはこちら\n{fixed_link}"
        
        return content

class MultiPostScheduler:
    """複数投稿スケジューラー"""
    
    def __init__(self):
        self.db_path = "multiple_posts_2025.db"
        self._init_database()
    
    def _init_database(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_date DATE,
            post_number INTEGER,
            total_posts INTEGER,
            content TEXT,
            content_type TEXT,
            scheduled_time TIMESTAMP,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        conn.close()
    
    def save_daily_posts(self, posts: List[Dict], target_date: datetime) -> List[int]:
        """1日分の投稿を保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        post_ids = []
        for post in posts:
            cursor.execute("""
            INSERT INTO daily_posts 
            (target_date, post_number, total_posts, content, content_type, scheduled_time)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                target_date.date(),
                post['post_number'],
                post['total_posts'],
                post['content'],
                post['content_type'],
                post['scheduled_time'].isoformat()
            ))
            post_ids.append(cursor.lastrowid)
        
        conn.commit()
        conn.close()
        
        return post_ids
    
    def export_schedule(self, days: int = 7) -> str:
        """スケジュールをエクスポート"""
        conn = sqlite3.connect(self.db_path)
        
        end_date = datetime.now() + timedelta(days=days)
        
        posts_df = pd.read_sql_query("""
        SELECT 
            target_date,
            post_number,
            content,
            content_type,
            scheduled_time
        FROM daily_posts
        WHERE scheduled_time <= ?
        AND status = 'pending'
        ORDER BY scheduled_time
        """, conn, params=[end_date.isoformat()])
        
        conn.close()
        
        # 投稿スケジュール表をCSVで出力
        filename = f"threads_schedule_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        posts_df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        return filename

class MultiPostSystem:
    """複数投稿システム統合"""
    
    def __init__(self):
        self.ai_engine = MultiPostAIEngine()
        self.scheduler = MultiPostScheduler()
    
    async def run_multi_post_generator(self):
        """複数投稿ジェネレーター実行"""
        print("""
        ╔════════════════════════════════════════════════════╗
        ║  📱 1日複数投稿対応 - 時間指定自動化システム      ║
        ║        収益最大化のための戦略的投稿計画           ║
        ╚════════════════════════════════════════════════════╝
        """)
        
        print("\n🎯 1日の投稿戦略を選択してください:")
        print("  1. 🔥 収益重視（3投稿/日）- 8時・19時・23時")
        print("  2. 🚀 バランス型（4投稿/日）- 8時・12時・19時・23時")
        print("  3. 💎 アグレッシブ（5投稿/日）- 8時・12時・19時・21時・23時")
        print("  4. 🏆 プロ仕様（6投稿/日）- 全時間帯最大活用")
        print("  5. 📊 カスタム設定")
        
        choice = input("\n選択 (1-5): ")
        
        if choice == "1":
            posts_per_day = 3
        elif choice == "2":
            posts_per_day = 4
        elif choice == "3":
            posts_per_day = 5
        elif choice == "4":
            posts_per_day = 6
        elif choice == "5":
            posts_per_day = int(input("1日の投稿数を入力 (3-6): "))
            posts_per_day = max(3, min(6, posts_per_day))
        else:
            posts_per_day = 4
        
        # 生成する日数を選択
        print(f"\n📅 {posts_per_day}投稿/日 で何日分生成しますか？")
        print("  1. 今日のみ（1日）")
        print("  2. 3日間")
        print("  3. 1週間（7日）")
        print("  4. 2週間（14日）")
        
        days_choice = input("\n選択 (1-4): ")
        
        if days_choice == "1":
            days = 1
        elif days_choice == "2":
            days = 3
        elif days_choice == "3":
            days = 7
        elif days_choice == "4":
            days = 14
        else:
            days = 1
        
        total_posts = posts_per_day * days
        
        print(f"\n🤖 生成開始: {days}日間 × {posts_per_day}投稿 = 合計{total_posts}投稿")
        print("⏳ 生成には数分かかります...")
        
        confirm = input("\n続行しますか？ (y/n): ")
        if confirm.lower() != 'y':
            return
        
        # 投稿生成
        all_posts = []
        
        for day in range(days):
            target_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=day)
            
            daily_posts = await self.ai_engine.generate_daily_posts(posts_per_day, target_date)
            post_ids = self.scheduler.save_daily_posts(daily_posts, target_date)
            
            all_posts.extend(daily_posts)
            
            print(f"✅ {target_date.strftime('%m/%d')} - {posts_per_day}投稿完了")
        
        print(f"\n🎉 全{total_posts}投稿の生成完了！")
        
        # 投稿スケジュール表示
        print(f"\n📋 投稿スケジュール:")
        print("="*70)
        
        for post in all_posts:
            scheduled_time = post['scheduled_time']
            content_preview = post['content'][:40] + "..."
            
            print(f"📅 {scheduled_time.strftime('%m/%d %H:%M')} | {post['content_type']:12} | {content_preview}")
        
        # エクスポート
        filename = self.scheduler.export_schedule(days)
        print(f"\n💾 詳細スケジュールを保存: {filename}")
        
        print(f"\n🎯 次のアクション:")
        print("1. Threadsアプリを開く")
        print("2. 各投稿を指定時間にスケジュール設定")
        print("3. 投稿内容は上記の通りコピー&ペースト")
        print("4. 自動投稿開始！")
        
        print(f"\n💡 投稿スケジュール詳細:")
        pattern = self.ai_engine.daily_patterns[posts_per_day]
        for i, time_str in enumerate(pattern["times"]):
            content_type = pattern["types"][i]
            type_emoji = {"educational": "📚", "viral": "🔥", "cta": "💰"}
            print(f"   {type_emoji.get(content_type, '📝')} {time_str} - {content_type}")
        
        print(f"\n⏰ 投稿時間帯:")
        print("   🌅 朝（09:00）- 朝活・出勤前ユーザー")
        if posts_per_day >= 4:
            print("   🌞 昼（12:00）- ランチタイム・休憩中")
        if posts_per_day >= 3:
            print("   🌆 夕（19:00）- 帰宅・夕食時間")
        if posts_per_day >= 5:
            print("   🌙 夜（21:00）- リラックスタイム")
        if posts_per_day >= 3:
            print("   🌌 深夜（23:00）- 寝る前チェック")
        
        print(f"\n🔥 期待される成果:")
        print(f"   📈 1日のエンゲージメント: {posts_per_day * 300}-{posts_per_day * 800}")
        print(f"   💰 推定収益/日: ¥{posts_per_day * 1000:,}-¥{posts_per_day * 3000:,}")
        print(f"   🚀 フォロワー増加/日: {posts_per_day * 5}-{posts_per_day * 15}人")

def main():
    """メイン実行"""
    system = MultiPostSystem()
    asyncio.run(system.run_multi_post_generator())

if __name__ == "__main__":
    main()