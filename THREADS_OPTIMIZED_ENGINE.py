#!/usr/bin/env python3
"""
📱 Threads最適化エンジン - 商材特化型高エンゲージメント投稿生成
Threadsで実際に反応が高い様々な投稿パターンを分析・実装
"""

import os
import json
import asyncio
import random
import hashlib
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class ThreadsOptimizedEngine:
    """📱 Threads最適化エンジン"""
    
    def __init__(self):
        self.db_path = "threads_optimized.db"
        self.fixed_link = "https://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u"
        
        # データベース初期化
        self._init_database()
        
        # 🎯 Threadsで高反応の投稿パターン
        self.threads_patterns = {
            "shock_value": {
                "description": "衝撃的な事実で注意を引く",
                "templates": [
                    "Web制作業界で革命が起きてる。{old_price}のサイトが{new_price}で作れる時代に。{feature}まで込みでこの価格って、もう従来の制作会社の存在意義って何？",
                    "制作費{reduction}削減って聞いて「うそでしょ」って思ったけど、調べたら本当だった。{service}のせいで業界全体が価格見直しを迫られてる。",
                    "「{high_price}の見積もり出したら断られた」って制作会社の友人が嘆いてた理由がわかった。{low_price}で同等のサイトが作れるサービスがあるらしい。"
                ],
                "engagement_rate": 9.2
            },
            
            "storytelling": {
                "description": "具体的なストーリーで共感を誘う",
                "templates": [
                    "3ヶ月前、クライアントから「サイト制作{budget}以内で」って言われて困ってた。従来なら{normal_cost}は最低必要。でも{service_name}使ったら{actual_cost}で完成。クライアントも大満足。",
                    "スタートアップの知人が資金調達前にサイト必要になって。予算{tight_budget}しかないって相談されて。普通なら「無理」って答えるけど、{solution}があって救われた。",
                    "フリーランス1年目の時、{expensive_quote}の見積もり出して案件流れた苦い思い出がある。今なら{affordable_option}を提案できるのに。当時知ってたら人生変わってたかも。"
                ],
                "engagement_rate": 8.8
            },
            
            "data_driven": {
                "description": "具体的なデータで説得力を持たせる",
                "templates": [
                    "Web制作の価格破壊が数字で見えてきた。従来：平均{traditional_price} / 新サービス：{new_service_price} = {percentage}%削減。しかも{feature1}＋{feature2}＋{feature3}込み。業界構造が根本から変わる。",
                    "制作期間の比較データ見て驚愕。従来：{old_duration} / 最新：{new_duration}。品質は同等かそれ以上。{efficiency_factor}の効率化がここまで来た。",
                    "コスト内訳を分析してみた。人件費{labor_cost}%、ツール費{tool_cost}%、その他{other_cost}%。{technology}による自動化で人件費を{reduction}%削減したのが価格革命の正体。"
                ],
                "engagement_rate": 8.6
            },
            
            "problem_solution": {
                "description": "問題提起→解決策の流れ",
                "templates": [
                    "中小企業のWebサイト問題：「{problem1}」「{problem2}」「{problem3}」。でも{solution_service}なら全て解決。{benefit}で{outcome}を実現。",
                    "起業家あるある：{startup_problem}。資金は限られてるのにサイトは必要。そんな状況を想定して作られたのが{service}。{key_feature}が画期的。",
                    "フリーランスの悩み：{freelancer_issue}。案件取りたいけどサイト制作は外注すると利益が薄い。{solution}を使えば{margin_improvement}の利益改善。"
                ],
                "engagement_rate": 8.9
            },
            
            "industry_insider": {
                "description": "業界の内情を暴露するスタイル",
                "templates": [
                    "制作会社が言わない本当の話。{expensive_cost}の見積もりの内訳：実作業{actual_work}%、利益{profit}%、営業コスト{sales_cost}%。{automated_service}なら営業コスト削減で{final_price}を実現。",
                    "Web制作の「当たり前」を疑え。{myth1}？実際は{reality1}。{myth2}？本当は{reality2}。業界の常識を覆す{revolutionary_service}。",
                    "元制作会社勤務が暴露。{standard_process}で{typical_duration}かかる理由：{reason1}、{reason2}、{reason3}。でも{efficient_service}なら{shortened_time}で完成。"
                ],
                "engagement_rate": 9.0
            },
            
            "comparison": {
                "description": "他の選択肢との比較で優位性を示す",
                "templates": [
                    "サイト制作の選択肢比較：制作会社{company_cost}、フリーランス{freelancer_cost}、テンプレート{template_cost}、{our_service}{our_cost}。機能と価格の両立なら圧倒的に{our_service}。",
                    "{competitor_a} vs {competitor_b} vs {our_service}。価格：{price_comparison}。機能：{feature_comparison}。サポート：{support_comparison}。総合評価で{our_service}の勝利。",
                    "DIYサイト作成に挫折した人へ。WordPressは{wp_difficulty}、Wixは{wix_limitation}、{our_service}なら{our_advantage}。挫折する前に試してほしい。"
                ],
                "engagement_rate": 8.4
            },
            
            "urgency_scarcity": {
                "description": "緊急性や希少性で行動を促す",
                "templates": [
                    "この価格でサイト制作できるのは今だけかも。{technology}の普及で制作コストが下がってる今がチャンス。業界が価格調整する前に{action}した方がいい。",
                    "{limited_offer}まで残り{time_left}。通常{regular_price}の{discount_service}が{special_price}。{special_feature}も付いてこの価格は今後ありえない。",
                    "制作会社の価格見直しラッシュが始まってる。{affordable_service}の影響で業界全体の料金体系が崩れつつある。今のうちに{smart_choice}を。"
                ],
                "engagement_rate": 8.7
            },
            
            "social_proof": {
                "description": "他者の成功例や証言を活用",
                "templates": [
                    "導入企業{company_count}社突破。スタートアップから上場企業まで{service}を選ぶ理由：{reason1}、{reason2}、{reason3}。{testimonial}との声も。",
                    "利用者の{satisfaction}%が満足と回答。「{user_quote}」「{another_quote}」実際の声が{service_quality}を物語ってる。",
                    "{industry}業界での導入率{adoption_rate}%。{case_study}では{improvement}を実現。数字が証明する{service_effectiveness}。"
                ],
                "engagement_rate": 8.5
            },
            
            "behind_scenes": {
                "description": "制作過程や舞台裏を見せる",
                "templates": [
                    "{service}の制作工程を公開。{step1}→{step2}→{step3}→完成。{technology}と{human_touch}の組み合わせが{quality}と{speed}を両立。",
                    "なぜ{low_price}でプロ品質を実現できるのか。秘密は{secret1}と{secret2}。従来の{traditional_method}を{innovative_method}に変えたのがポイント。",
                    "{service_name}開発者が語る。「{developer_quote}」{optimization}により{cost_reduction}を実現しながら{quality_maintenance}を達成。"
                ],
                "engagement_rate": 8.3
            },
            
            "future_prediction": {
                "description": "業界の未来予測で関心を引く",
                "templates": [
                    "2025年のWeb制作業界予測。{prediction1}、{prediction2}、{prediction3}。今から{preparation}しておくべき。{forward_thinking_service}はその先を行ってる。",
                    "{years}後、サイト制作は{future_state}になる。{current_service}はその未来を先取り。{early_adopter_advantage}を得るなら今がタイミング。",
                    "AI時代のサイト制作。{ai_impact}により{industry_change}が加速。{adaptive_service}なら{future_proof}で安心。"
                ],
                "engagement_rate": 8.1
            }
        }
        
        # 🎯 商材特化データ
        self.service_data = {
            "service_names": ["LiteWEB+", "この革新的サービス", "話題のWebサービス"],
            "pricing": {
                "old_prices": ["30万円", "50万円", "40万円", "60万円", "25万円"],
                "new_prices": ["1万円", "19,800円", "9,800円"],
                "reductions": ["90%", "95%", "80%", "85%"],
                "budgets": ["10万円", "15万円", "20万円", "5万円"]
            },
            "features": [
                "SEO最適化", "レスポンシブデザイン", "高速表示", "独自ドメイン設定",
                "SSL証明書", "Google Analytics連携", "お問い合わせフォーム",
                "SNS連携", "検索エンジン登録", "アフターサポート"
            ],
            "benefits": [
                "制作期間3分の1", "維持費95%削減", "SEO効果2倍",
                "コンバージョン率向上", "ユーザビリティ改善", "ブランド価値向上"
            ],
            "problems": [
                "サイト制作費が高すぎる", "制作期間が長すぎる", "維持費が負担",
                "SEO効果がない", "スマホ対応していない", "デザインが古い"
            ]
        }
        
        # 🏷️ 効果的なハッシュタグ
        self.effective_hashtags = {
            "primary": ["Web制作", "ホームページ制作", "サイト制作", "格安制作"],
            "target": ["スタートアップ", "個人事業主", "中小企業", "起業家"],
            "benefit": ["コスト削減", "時短", "効率化", "DX推進"],
            "action": ["無料相談", "見積り無料", "今すぐ相談", "限定価格"],
            "trending": ["AI活用", "自動化", "デジタル化", "最新技術"]
        }
    
    def _init_database(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS threads_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_hash TEXT UNIQUE,
            content TEXT,
            pattern_type TEXT,
            engagement_score REAL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            hashtags TEXT
        )
        """)
        
        conn.commit()
        conn.close()
    
    async def generate_threads_post(self, post_number: int, target_datetime: datetime) -> Dict[str, Any]:
        """Threads最適化投稿生成"""
        
        # パターン選択（時間帯と投稿番号で最適化）
        hour = target_datetime.hour
        patterns = list(self.threads_patterns.keys())
        
        # 時間帯別パターン傾向
        if 7 <= hour < 10:
            # 朝：データ駆動、業界インサイダー
            preferred = ["data_driven", "industry_insider", "shock_value"]
        elif 10 <= hour < 14:
            # 午前：問題解決、比較
            preferred = ["problem_solution", "comparison", "storytelling"]
        elif 14 <= hour < 18:
            # 午後：ストーリー、舞台裏
            preferred = ["storytelling", "behind_scenes", "social_proof"]
        elif 18 <= hour < 21:
            # 夕方：緊急性、社会的証明
            preferred = ["urgency_scarcity", "social_proof", "future_prediction"]
        else:
            # 夜：衝撃、未来予測
            preferred = ["shock_value", "future_prediction", "industry_insider"]
        
        # 投稿番号も考慮してパターン選択
        pattern_type = preferred[post_number % len(preferred)]
        
        # コンテンツ生成
        content = await self._generate_pattern_content(pattern_type, post_number, target_datetime)
        
        # ハッシュタグ選択
        hashtags = self._select_hashtags(pattern_type, post_number)
        
        # リンク追加
        content = self._add_link_strategically(content, pattern_type)
        
        # エンゲージメント予測
        base_score = self.threads_patterns[pattern_type]["engagement_rate"]
        engagement_score = base_score + random.uniform(-0.3, 0.5)
        
        # 履歴保存
        content_hash = hashlib.md5(content.encode()).hexdigest()
        self._save_to_history(content_hash, content, pattern_type, engagement_score, " ".join(hashtags))
        
        return {
            "content": content,
            "hashtags": hashtags,
            "pattern_type": pattern_type,
            "engagement_prediction": engagement_score
        }
    
    async def _generate_pattern_content(self, pattern_type: str, post_number: int, target_datetime: datetime) -> str:
        """パターン別コンテンツ生成"""
        
        # ランダムシード（日付と投稿番号で一意性確保）
        random.seed(int(target_datetime.timestamp()) + post_number * 23)
        
        pattern_info = self.threads_patterns[pattern_type]
        template = random.choice(pattern_info["templates"])
        
        # テンプレート変数置換
        if pattern_type == "shock_value":
            variables = self._get_shock_variables()
        elif pattern_type == "storytelling":
            variables = self._get_story_variables()
        elif pattern_type == "data_driven":
            variables = self._get_data_variables()
        elif pattern_type == "problem_solution":
            variables = self._get_problem_solution_variables()
        elif pattern_type == "industry_insider":
            variables = self._get_insider_variables()
        elif pattern_type == "comparison":
            variables = self._get_comparison_variables()
        elif pattern_type == "urgency_scarcity":
            variables = self._get_urgency_variables()
        elif pattern_type == "social_proof":
            variables = self._get_social_proof_variables()
        elif pattern_type == "behind_scenes":
            variables = self._get_behind_scenes_variables()
        elif pattern_type == "future_prediction":
            variables = self._get_future_variables()
        else:
            variables = {}
        
        # 変数置換
        content = template
        for key, value in variables.items():
            content = content.replace(f"{{{key}}}", str(value))
        
        return content
    
    def _get_shock_variables(self) -> Dict[str, str]:
        """衝撃系変数"""
        return {
            "old_price": random.choice(self.service_data["pricing"]["old_prices"]),
            "new_price": random.choice(self.service_data["pricing"]["new_prices"]),
            "feature": random.choice(self.service_data["features"]),
            "reduction": random.choice(self.service_data["pricing"]["reductions"]),
            "service": random.choice(self.service_data["service_names"]),
            "high_price": random.choice(self.service_data["pricing"]["old_prices"]),
            "low_price": random.choice(self.service_data["pricing"]["new_prices"])
        }
    
    def _get_story_variables(self) -> Dict[str, str]:
        """ストーリー系変数"""
        return {
            "budget": random.choice(self.service_data["pricing"]["budgets"]),
            "normal_cost": random.choice(self.service_data["pricing"]["old_prices"]),
            "service_name": random.choice(self.service_data["service_names"]),
            "actual_cost": random.choice(self.service_data["pricing"]["new_prices"]),
            "tight_budget": random.choice(self.service_data["pricing"]["budgets"]),
            "solution": "この画期的なサービス",
            "expensive_quote": random.choice(self.service_data["pricing"]["old_prices"]),
            "affordable_option": random.choice(self.service_data["pricing"]["new_prices"]) + "の選択肢"
        }
    
    def _get_data_variables(self) -> Dict[str, str]:
        """データ系変数"""
        old_price_num = int(random.choice(self.service_data["pricing"]["old_prices"]).replace("万円", ""))
        new_price_num = int(random.choice(self.service_data["pricing"]["new_prices"]).replace("万円", "").replace("円", "")) / 10000
        percentage = int((old_price_num - new_price_num) / old_price_num * 100)
        
        return {
            "traditional_price": f"{old_price_num}万円",
            "new_service_price": f"{new_price_num}万円",
            "percentage": str(percentage),
            "feature1": self.service_data["features"][0],
            "feature2": self.service_data["features"][1],
            "feature3": self.service_data["features"][2],
            "old_duration": "2-3ヶ月",
            "new_duration": "最短3日",
            "efficiency_factor": "AI技術",
            "labor_cost": "60",
            "tool_cost": "20", 
            "other_cost": "20",
            "technology": "AI自動化",
            "reduction": "70"
        }
    
    def _get_problem_solution_variables(self) -> Dict[str, str]:
        """問題解決系変数"""
        problems = random.sample(self.service_data["problems"], 3)
        return {
            "problem1": problems[0],
            "problem2": problems[1], 
            "problem3": problems[2],
            "solution_service": random.choice(self.service_data["service_names"]),
            "benefit": random.choice(self.service_data["benefits"]),
            "outcome": "コスト削減と品質向上",
            "startup_problem": "資金調達前にサイトが必要",
            "service": random.choice(self.service_data["service_names"]),
            "key_feature": random.choice(self.service_data["features"]),
            "freelancer_issue": "制作費を抑えて利益を確保したい",
            "solution": "この効率的なサービス",
            "margin_improvement": "50%以上"
        }
    
    def _get_insider_variables(self) -> Dict[str, str]:
        """業界内情系変数"""
        return {
            "expensive_cost": random.choice(self.service_data["pricing"]["old_prices"]),
            "actual_work": "30",
            "profit": "40",
            "sales_cost": "30",
            "automated_service": "自動化サービス",
            "final_price": random.choice(self.service_data["pricing"]["new_prices"]),
            "myth1": "プロ品質には高額費用が必要",
            "reality1": "技術革新で低コスト化が実現",
            "myth2": "制作には数ヶ月必要",
            "reality2": "効率化で短期間完成が可能",
            "revolutionary_service": random.choice(self.service_data["service_names"]),
            "standard_process": "従来の制作工程",
            "typical_duration": "2-3ヶ月",
            "reason1": "過剰な打ち合わせ",
            "reason2": "非効率な作業工程", 
            "reason3": "手作業による時間ロス",
            "efficient_service": "効率化されたサービス",
            "shortened_time": "最短3日"
        }
    
    def _get_comparison_variables(self) -> Dict[str, str]:
        """比較系変数"""
        return {
            "company_cost": random.choice(self.service_data["pricing"]["old_prices"]),
            "freelancer_cost": "15-25万円",
            "template_cost": "月額1-3万円",
            "our_service": random.choice(self.service_data["service_names"]),
            "our_cost": random.choice(self.service_data["pricing"]["new_prices"]),
            "competitor_a": "A社サービス",
            "competitor_b": "B社プラン",
            "price_comparison": "圧倒的な低価格を実現",
            "feature_comparison": "同等以上の機能を提供", 
            "support_comparison": "充実したアフターサポート",
            "wp_difficulty": "設定が複雑で挫折しやすい",
            "wix_limitation": "カスタマイズに限界がある",
            "our_advantage": "プロ品質を簡単操作で実現"
        }
    
    def _get_urgency_variables(self) -> Dict[str, str]:
        """緊急性系変数"""
        return {
            "technology": "AI技術",
            "action": "導入",
            "limited_offer": "キャンペーン",
            "time_left": "48時間",
            "regular_price": random.choice(self.service_data["pricing"]["old_prices"]),
            "discount_service": "特別価格サービス", 
            "special_price": random.choice(self.service_data["pricing"]["new_prices"]),
            "special_feature": random.choice(self.service_data["features"]),
            "affordable_service": random.choice(self.service_data["service_names"]),
            "smart_choice": "賢い選択"
        }
    
    def _get_social_proof_variables(self) -> Dict[str, str]:
        """社会的証明系変数"""
        return {
            "company_count": f"{random.randint(100, 500)}",
            "service": random.choice(self.service_data["service_names"]),
            "reason1": "コストパフォーマンス",
            "reason2": "短期間での完成",
            "reason3": "充実したサポート",
            "testimonial": "期待以上の仕上がり",
            "satisfaction": f"{random.randint(85, 98)}",
            "user_quote": "想像以上のクオリティでした",
            "another_quote": "コスパが最高です",
            "service_quality": "高い満足度",
            "industry": "IT",
            "adoption_rate": f"{random.randint(60, 85)}",
            "case_study": "導入事例",
            "improvement": "売上30%向上",
            "service_effectiveness": "確かな効果"
        }
    
    def _get_behind_scenes_variables(self) -> Dict[str, str]:
        """舞台裏系変数"""
        return {
            "service": random.choice(self.service_data["service_names"]),
            "step1": "要件ヒアリング",
            "step2": "AI設計",
            "step3": "品質チェック",
            "technology": "最新AI技術",
            "human_touch": "プロの監修",
            "quality": "高品質",
            "speed": "高速制作",
            "low_price": random.choice(self.service_data["pricing"]["new_prices"]),
            "secret1": "自動化システム",
            "secret2": "効率的なワークフロー",
            "traditional_method": "従来の手作業",
            "innovative_method": "AI支援システム",
            "service_name": random.choice(self.service_data["service_names"]),
            "developer_quote": "技術革新により価格革命を実現しました",
            "optimization": "システム最適化",
            "cost_reduction": "大幅なコスト削減",
            "quality_maintenance": "品質水準の維持"
        }
    
    def _get_future_variables(self) -> Dict[str, str]:
        """未来予測系変数"""
        return {
            "prediction1": "AI主導の制作が標準化",
            "prediction2": "制作期間は週単位から日単位へ",
            "prediction3": "価格は現在の10分の1に",
            "preparation": "新技術への対応",
            "forward_thinking_service": random.choice(self.service_data["service_names"]),
            "years": f"{random.randint(2, 5)}",
            "future_state": "完全自動化",
            "current_service": random.choice(self.service_data["service_names"]),
            "early_adopter_advantage": "先行者利益",
            "ai_impact": "AI技術の発展",
            "industry_change": "業界構造の変化",
            "adaptive_service": "適応型サービス",
            "future_proof": "将来性"
        }
    
    def _select_hashtags(self, pattern_type: str, post_number: int) -> List[str]:
        """効果的なハッシュタグ選択"""
        hashtags = []
        
        # 基本ハッシュタグ
        hashtags.append(random.choice(self.effective_hashtags["primary"]))
        
        # パターン別ハッシュタグ
        if pattern_type in ["shock_value", "industry_insider"]:
            hashtags.append(random.choice(self.effective_hashtags["trending"]))
        elif pattern_type in ["storytelling", "problem_solution"]:
            hashtags.append(random.choice(self.effective_hashtags["target"]))
        elif pattern_type in ["data_driven", "comparison"]:
            hashtags.append(random.choice(self.effective_hashtags["benefit"]))
        else:
            hashtags.append(random.choice(self.effective_hashtags["action"]))
        
        return hashtags
    
    def _add_link_strategically(self, content: str, pattern_type: str) -> str:
        """戦略的リンク配置"""
        if self.fixed_link in content:
            return content
        
        # パターン別のリンク追加戦略
        if pattern_type in ["urgency_scarcity", "social_proof"]:
            return content + f"\n\n詳細確認→ {self.fixed_link}"
        elif pattern_type in ["problem_solution", "comparison"]:
            return content + f"\n\n解決策はこちら→ {self.fixed_link}"
        elif pattern_type in ["storytelling", "behind_scenes"]:
            return content + f"\n\n{self.fixed_link}"
        else:
            return content + f"\n\nもっと詳しく→ {self.fixed_link}"
    
    def _save_to_history(self, content_hash: str, content: str, pattern_type: str, 
                        engagement_score: float, hashtags: str):
        """履歴保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO threads_posts (content_hash, content, pattern_type, engagement_score, hashtags)
            VALUES (?, ?, ?, ?, ?)
            """, (content_hash, content, pattern_type, engagement_score, hashtags))
            conn.commit()
        except:
            pass
        
        conn.close()
    
    async def generate_daily_threads_posts(self, posts_per_day: int = 5, target_date: datetime = None) -> List[Dict]:
        """1日分のThreads最適化投稿生成"""
        
        if target_date is None:
            target_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        posting_times = ["08:00", "12:00", "19:00", "21:00", "23:00"][:posts_per_day]
        posts = []
        
        print(f"📱 {target_date.strftime('%m/%d')} - Threads最適化投稿生成中...")
        
        for i, time_str in enumerate(posting_times):
            hour, minute = map(int, time_str.split(':'))
            post_time = target_date.replace(hour=hour, minute=minute)
            
            # Threads最適化投稿生成
            post_data = await self.generate_threads_post(i, post_time)
            
            posts.append({
                "content": f"{post_data['content']}\t{' '.join(post_data['hashtags'])}",
                "scheduled_time": post_time,
                "content_type": "threads_optimized",
                "post_number": i + 1,
                "total_posts": posts_per_day,
                "pattern_type": post_data['pattern_type'],
                "engagement_prediction": post_data['engagement_prediction']
            })
            
            await asyncio.sleep(0.3)
        
        return posts

# 統合用インターフェース
class ThreadsOptimizedViralEngine:
    """統合用のThreads最適化エンジン"""
    
    def __init__(self):
        self.engine = ThreadsOptimizedEngine()
    
    async def generate_daily_posts(self, posts_per_day: int = 5, target_date: datetime = None) -> List[Dict]:
        """統合インターフェース"""
        return await self.engine.generate_daily_threads_posts(posts_per_day, target_date)

async def test_threads_patterns():
    """パターンテスト"""
    print("📱 Threads最適化エンジン - パターンテスト")
    print("=" * 70)
    
    engine = ThreadsOptimizedEngine()
    
    # 全パターンのサンプル生成
    patterns = list(engine.threads_patterns.keys())
    
    for i, pattern in enumerate(patterns):
        print(f"\n【{pattern.upper()}】パターン")
        print(f"エンゲージメント予測: {engine.threads_patterns[pattern]['engagement_rate']}")
        print("-" * 50)
        
        # 現在時刻でテスト
        test_time = datetime.now().replace(hour=10+i, minute=0)
        post_data = await engine.generate_threads_post(i, test_time)
        
        content_parts = post_data['content'].split('\t')
        if len(content_parts) > 1:
            content = content_parts[0]
            hashtags = content_parts[1]
        else:
            content = post_data['content'] 
            hashtags = ' '.join(post_data['hashtags'])
        
        print("投稿内容:")
        print(content)
        print(f"\nハッシュタグ: {hashtags}")
        print("-" * 50)
    
    print("\n✅ 全10パターンのサンプル生成完了！")

if __name__ == "__main__":
    asyncio.run(test_threads_patterns())