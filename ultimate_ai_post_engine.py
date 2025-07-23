#!/usr/bin/env python3
"""
究極のThreads AI自動投稿エンジン
高エンゲージメント投稿を分析し、AIで新しい投稿を自動生成・投稿する
"""

import os
import json
import random
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import openai
from dotenv import load_dotenv
import sqlite3
import re
import requests
from collections import Counter
import numpy as np

load_dotenv()

class UltimateThreadsAIEngine:
    def __init__(self):
        self.db_path = "threads_auto_post.db"
        self.templates_path = "money_optimization_sheets/02_高収益テンプレート.tsv"
        self.engagement_threshold = 0.05  # 5%以上のエンゲージメント率
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.claude_api_key = os.getenv('CLAUDE_API_KEY')
        self.threads_api_token = os.getenv('THREADS_API_TOKEN')
        
    def analyze_high_engagement_patterns(self) -> Dict[str, Any]:
        """高エンゲージメント投稿のパターンを分析"""
        conn = sqlite3.connect(self.db_path)
        
        # スプレッドシートから高パフォーマンス投稿を取得
        query = """
        SELECT content, likes, comments, reposts, impressions,
               (likes + comments + reposts) * 1.0 / NULLIF(impressions, 0) as engagement_rate
        FROM posts
        WHERE impressions > 100
        ORDER BY engagement_rate DESC
        LIMIT 50
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        patterns = {
            'emoji_usage': self._analyze_emoji_patterns(df),
            'content_structure': self._analyze_content_structure(df),
            'keywords': self._extract_high_performing_keywords(df),
            'content_length': self._analyze_content_length(df),
            'hashtag_patterns': self._analyze_hashtag_patterns(df),
            'cta_patterns': self._analyze_cta_patterns(df)
        }
        
        return patterns
    
    def _analyze_emoji_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """絵文字の使用パターンを分析"""
        emoji_pattern = re.compile(r'[^\u0000-\u007F\u0080-\u00FF\u2000-\u206F]+')
        emoji_counts = Counter()
        
        for content in df['content']:
            emojis = emoji_pattern.findall(content)
            emoji_counts.update(emojis)
        
        return {
            'top_emojis': emoji_counts.most_common(10),
            'avg_emoji_count': np.mean([len(emoji_pattern.findall(c)) for c in df['content']])
        }
    
    def _analyze_content_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """コンテンツ構造を分析"""
        structures = []
        
        for content in df['content']:
            structure = {
                'has_numbered_list': bool(re.search(r'\d+\.', content)),
                'has_bullet_points': '・' in content or '✅' in content,
                'has_question': '？' in content or '?' in content,
                'line_count': len(content.split('\n')),
                'has_cta': any(cta in content for cta in ['詳細は', 'プロフィール', 'DM', 'コメント'])
            }
            structures.append(structure)
        
        return pd.DataFrame(structures).mean().to_dict()
    
    def _extract_high_performing_keywords(self, df: pd.DataFrame) -> List[str]:
        """高パフォーマンスキーワードを抽出"""
        all_words = []
        
        for content in df['content']:
            # 日本語の単語を抽出（簡易的な方法）
            words = re.findall(r'[ぁ-んァ-ヶー一-龠]+', content)
            all_words.extend(words)
        
        word_counts = Counter(all_words)
        # 2文字以上の頻出単語上位20個
        return [word for word, count in word_counts.most_common(50) if len(word) >= 2][:20]
    
    def _analyze_content_length(self, df: pd.DataFrame) -> Dict[str, float]:
        """コンテンツの長さを分析"""
        lengths = [len(content) for content in df['content']]
        return {
            'avg_length': np.mean(lengths),
            'optimal_range': (np.percentile(lengths, 25), np.percentile(lengths, 75))
        }
    
    def _analyze_hashtag_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """ハッシュタグパターンを分析"""
        hashtags = []
        
        for content in df['content']:
            tags = re.findall(r'#[^\s]+', content)
            hashtags.extend(tags)
        
        return {
            'popular_hashtags': Counter(hashtags).most_common(10),
            'avg_hashtag_count': np.mean([len(re.findall(r'#[^\s]+', c)) for c in df['content']])
        }
    
    def _analyze_cta_patterns(self, df: pd.DataFrame) -> List[str]:
        """CTA（Call to Action）パターンを分析"""
        cta_patterns = [
            r'詳細は.*リンク',
            r'DM.*受付',
            r'コメント.*ください',
            r'プロフィール.*から',
            r'保存.*ください',
            r'いいね.*お願い'
        ]
        
        found_ctas = []
        for content in df['content']:
            for pattern in cta_patterns:
                if re.search(pattern, content):
                    match = re.search(pattern, content)
                    found_ctas.append(match.group())
        
        return list(set(found_ctas))[:10]
    
    async def generate_ai_post(self, topic: str, patterns: Dict[str, Any]) -> str:
        """AIで新しい投稿を生成"""
        # 高収益テンプレートを読み込み
        templates_df = pd.read_csv(self.templates_path, sep='\t')
        
        # ランダムにテンプレートを選択
        template_row = templates_df.sample(1).iloc[0]
        template = template_row['テンプレート内容']
        
        # プロンプトを構築
        prompt = f"""
        以下の分析結果を参考に、Threadsで高いエンゲージメントを獲得できる投稿を生成してください。

        【トピック】: {topic}
        
        【使用テンプレート】:
        {template}
        
        【高パフォーマンス投稿の特徴】:
        - 平均文字数: {patterns['content_length']['avg_length']:.0f}文字
        - 人気の絵文字: {', '.join([e[0] for e in patterns['emoji_usage']['top_emojis'][:5]])}
        - 平均絵文字数: {patterns['emoji_usage']['avg_emoji_count']:.1f}個
        - 番号付きリスト使用率: {patterns['content_structure']['has_numbered_list']*100:.0f}%
        - 箇条書き使用率: {patterns['content_structure']['has_bullet_points']*100:.0f}%
        - 質問形式使用率: {patterns['content_structure']['has_question']*100:.0f}%
        - 効果的なキーワード: {', '.join(patterns['keywords'][:10])}
        - 人気ハッシュタグ: {', '.join([h[0] for h in patterns['hashtag_patterns']['popular_hashtags'][:5]])}
        
        【ルール】:
        1. テンプレートの{変数}部分を適切に埋める
        2. 自然で読みやすい日本語を使用
        3. エンゲージメントを促す要素を含める
        4. 500文字以内で収める
        5. 最後に適切なCTAを含める
        
        投稿文を生成してください：
        """
        
        # OpenAI APIで生成
        if self.openai_api_key:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "あなたは高いエンゲージメントを獲得するSNS投稿の専門家です。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=500
            )
            return response.choices[0].message.content
        
        # Claude APIで生成（OpenAIがない場合）
        elif self.claude_api_key:
            # Claude API実装
            pass
        
        # デモ用のダミー生成
        return self._generate_demo_post(topic, template, patterns)
    
    def _generate_demo_post(self, topic: str, template: str, patterns: Dict[str, Any]) -> str:
        """デモ用の投稿を生成"""
        # テンプレートの変数を置換
        replacements = {
            '{topic}': topic,
            '{method1}': '競合分析の徹底',
            '{method2}': 'ユーザーフィードバックの活用',
            '{method3}': 'A/Bテストの実施',
            '{result}': '売上が2.5倍に増加',
            '{mistake}': f'{topic}での失敗',
            '{truth}': '基本を押さえることが最重要',
            '{struggle}': '月10万円の売上で停滞',
            '{number}': '5',
            '{skill}': topic,
            '{point1}': '市場調査',
            '{point2}': 'ターゲット設定',
            '{point3}': '差別化戦略',
            '{benefit}': '確実に成果を出す'
        }
        
        post = template
        for key, value in replacements.items():
            post = post.replace(key, value)
        
        # 人気の絵文字を追加
        popular_emojis = [e[0] for e in patterns['emoji_usage']['top_emojis'][:3]]
        if popular_emojis:
            post += '\n\n' + ' '.join(popular_emojis)
        
        # ハッシュタグを追加
        hashtags = [h[0] for h in patterns['hashtag_patterns']['popular_hashtags'][:4]]
        if hashtags:
            post += '\n\n' + ' '.join(hashtags)
        
        return post
    
    async def schedule_and_post(self, content: str, scheduled_time: datetime = None):
        """投稿をスケジュールして実行"""
        if not scheduled_time:
            # 最適な投稿時間を選択（朝7時、昼12時、夜19時、21時）
            optimal_hours = [7, 12, 19, 21]
            now = datetime.now()
            
            # 次の最適な時間を見つける
            for hour in optimal_hours:
                scheduled = now.replace(hour=hour, minute=0, second=0)
                if scheduled > now:
                    scheduled_time = scheduled
                    break
            else:
                # 翌日の最初の時間
                scheduled_time = (now + timedelta(days=1)).replace(hour=optimal_hours[0], minute=0, second=0)
        
        # データベースに保存
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO scheduled_posts (content, scheduled_time, status, created_at)
        VALUES (?, ?, 'pending', ?)
        """, (content, scheduled_time.isoformat(), datetime.now().isoformat()))
        
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # 実際の投稿処理（Threads APIを使用）
        if self.threads_api_token:
            await self._post_to_threads(content, post_id)
        
        return {
            'post_id': post_id,
            'content': content,
            'scheduled_time': scheduled_time.isoformat(),
            'status': 'scheduled'
        }
    
    async def _post_to_threads(self, content: str, post_id: int):
        """Threads APIで投稿"""
        # ここにThreads API実装
        # 現在はデモなので実装省略
        pass
    
    async def run_auto_generation_cycle(self, topics: List[str], posts_per_day: int = 3):
        """自動生成サイクルを実行"""
        print("🚀 究極のAI自動投稿エンジンを起動します...")
        
        # 高エンゲージメントパターンを分析
        print("📊 高エンゲージメント投稿を分析中...")
        patterns = self.analyze_high_engagement_patterns()
        
        print(f"✅ 分析完了！")
        print(f"   - 人気キーワード: {', '.join(patterns['keywords'][:5])}")
        print(f"   - 最適文字数: {patterns['content_length']['optimal_range']}")
        
        # 各トピックについて投稿を生成
        generated_posts = []
        
        for topic in topics:
            print(f"\n🤖 「{topic}」に関する投稿を生成中...")
            
            # AI投稿生成
            content = await self.generate_ai_post(topic, patterns)
            
            # 投稿をスケジュール
            result = await self.schedule_and_post(content)
            generated_posts.append(result)
            
            print(f"✅ 投稿をスケジュールしました: {result['scheduled_time']}")
            print(f"📝 内容プレビュー: {content[:50]}...")
        
        return generated_posts

# 実行用のメイン関数
async def main():
    engine = UltimateThreadsAIEngine()
    
    # 投稿トピック（あなたのビジネスに合わせて変更）
    topics = [
        "Webサイト制作の効率化",
        "AI活用でコスト削減",
        "フリーランスの成功法則",
        "起業家の資金調達",
        "ビジネス自動化ツール"
    ]
    
    # 自動生成サイクルを実行
    results = await engine.run_auto_generation_cycle(topics, posts_per_day=3)
    
    print("\n🎉 全ての投稿生成が完了しました！")
    print(f"📊 生成された投稿数: {len(results)}")

if __name__ == "__main__":
    asyncio.run(main())