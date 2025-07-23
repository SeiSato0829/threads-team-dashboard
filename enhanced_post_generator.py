"""
強化版投稿生成システム
より多様で魅力的な投稿を生成するためのプロンプトとテンプレート
"""

import random
from datetime import datetime

class EnhancedPostGenerator:
    """強化版投稿生成クラス"""
    
    def __init__(self):
        # 投稿スタイルのバリエーション
        self.post_styles = {
            'story': {
                'name': 'ストーリーテリング型',
                'template': '私の{experience}、実は{discovery}だったんです。{detail}。みんなも{action}してみて！',
                'prompts': [
                    '個人的な体験談を交えて',
                    '読者が共感できるエピソードで',
                    '起承転結のある構成で'
                ]
            },
            'question': {
                'name': '質問投げかけ型',
                'template': '{topic}について質問！{question}？みんなの意見を聞かせて！{hashtag}',
                'prompts': [
                    '読者の意見を引き出す質問形式で',
                    'アンケート風の選択肢を含めて',
                    '議論を生む問いかけで'
                ]
            },
            'tips': {
                'name': 'お役立ち情報型',
                'template': '【{category}の豆知識】知ってた？{fact}。これを使えば{benefit}！',
                'prompts': [
                    '実用的なTipsを3つ含めて',
                    '今すぐ使える情報を中心に',
                    '具体的な数字やデータを交えて'
                ]
            },
            'news': {
                'name': 'ニュース速報型',
                'template': '【速報】{topic}が{action}！{impact}との情報。詳細は{source}',
                'prompts': [
                    '最新情報を速報風に',
                    'インパクトのある見出しで',
                    '信頼性を感じさせる構成で'
                ]
            },
            'review': {
                'name': 'レビュー・感想型',
                'template': '{product}を{duration}使ってみた結果...{verdict}！特に{highlight}が最高',
                'prompts': [
                    '実体験に基づくレビューとして',
                    'メリット・デメリットを公平に',
                    '具体的な使用感を詳しく'
                ]
            },
            'comparison': {
                'name': '比較型',
                'template': '{item1} vs {item2}、どっちがいい？{criteria}で比較すると{result}',
                'prompts': [
                    '公平な比較視点で',
                    '表や箇条書きを活用して',
                    '読者が選びやすい情報提供で'
                ]
            },
            'listicle': {
                'name': 'リスト型',
                'template': '【保存版】{topic}のおすすめ{number}選！\n1. {item1}\n2. {item2}\n3. {item3}',
                'prompts': [
                    'わかりやすいリスト形式で',
                    '番号付きの箇条書きで',
                    'それぞれに短い説明を添えて'
                ]
            },
            'emotional': {
                'name': '感情訴求型',
                'template': '{emotion}な時、{action}すると{result}。これって私だけ？{community}',
                'prompts': [
                    '読者の感情に訴える内容で',
                    '共感を呼ぶ表現を使って',
                    '心に響くメッセージで'
                ]
            }
        }
        
        # ジャンル別の特化プロンプト
        self.genre_prompts = {
            'ゲーム': [
                'ゲーマー向けの専門用語を適度に使用',
                '攻略情報やTipsを含める',
                'プレイ体験や実況風の要素を加える',
                '新作情報や期待の要素を表現'
            ],
            'エンタメ': [
                'トレンドや話題性を重視',
                'ファン心理に訴える表現',
                '期待感や驚きを演出',
                'ビジュアル要素への言及'
            ],
            'ビジネス': [
                'プロフェッショナルな表現',
                '具体的な成果や数値を含める',
                'ビジネスパーソンに役立つ内容',
                '信頼性のある情報源への言及'
            ],
            'マーケティング': [
                '最新のマーケティングトレンド',
                '実践的なケーススタディ',
                'ROIや効果測定への言及',
                '戦略的な視点を含める'
            ]
        }
        
        # エンゲージメント向上テクニック
        self.engagement_techniques = [
            '数字を使って具体性を出す（例：3つの方法、90%の人が知らない）',
            '限定感を演出（例：今だけ、先着順、期間限定）',
            'FOMOを刺激（例：見逃し厳禁、知らないと損）',
            '社会的証明（例：話題沸騰中、みんな使ってる）',
            '権威性の演出（例：専門家も推奨、業界トップが実践）',
            '簡潔さと読みやすさ（箇条書き、短い段落）',
            'ビジュアル要素への言及（画像参照、動画あり）',
            '行動喚起の明確化（今すぐチェック、フォロー推奨）'
        ]
    
    def create_enhanced_prompt(self, base_text, genre, style=None, reference_posts=None):
        """強化されたプロンプトを生成"""
        # スタイルをランダムに選択（指定がない場合）
        if not style:
            style = random.choice(list(self.post_styles.keys()))
        
        style_info = self.post_styles[style]
        genre_prompt = random.choice(self.genre_prompts.get(genre, ['一般的な内容で']))
        technique = random.choice(self.engagement_techniques)
        
        prompt = f"""
あなたは人気SNSインフルエンサーです。以下の要件に従って魅力的なThreads投稿を作成してください。

【投稿スタイル】
{style_info['name']}
{random.choice(style_info['prompts'])}

【元の内容】
{base_text}

【ジャンル】
{genre}
{genre_prompt}

【エンゲージメント向上】
{technique}

【参考投稿】
{self._format_reference_posts(reference_posts)}

【厳守事項】
1. 500文字以内（必須）
2. 自然で読みやすい日本語
3. 適切な改行で見やすく
4. ハッシュタグは3-5個（関連性の高いものを選択）
5. 絵文字は効果的に使用（過度な使用は避ける）
6. 明確なCTA（行動喚起）を含める
7. オリジナリティのある内容
8. ターゲット層に響く表現

【避けるべきこと】
- テンプレート的な定型文
- 過度な煽り表現
- 信憑性のない情報
- ネガティブな内容
- 他者を傷つける表現

【出力形式】
投稿文のみを出力。説明や注釈は不要。
"""
        
        return prompt
    
    def _format_reference_posts(self, reference_posts):
        """参考投稿をフォーマット"""
        if not reference_posts:
            return "なし"
        
        formatted = []
        for i, post in enumerate(reference_posts[:3], 1):
            likes = post.get('likes', 0)
            text = post.get('text', '')[:100] + '...'
            formatted.append(f"{i}. いいね{likes}件: {text}")
        
        return '\n'.join(formatted)
    
    def generate_time_sensitive_content(self, genre):
        """時間や季節に応じたコンテンツ要素を生成"""
        now = datetime.now()
        hour = now.hour
        
        time_elements = {
            'morning': (5, 11, ['おはよう', '朝活', '今日も一日', 'モーニング']),
            'lunch': (11, 14, ['ランチ', 'お昼休み', '午後も頑張ろう', 'ランチタイム']),
            'afternoon': (14, 17, ['午後のひととき', '仕事の合間に', '休憩時間', 'ティータイム']),
            'evening': (17, 21, ['お疲れ様', '今日も一日', '夜活', 'ディナータイム']),
            'night': (21, 5, ['おやすみ前に', '夜更かし', '深夜', 'ナイトタイム'])
        }
        
        season_elements = {
            'spring': (3, 5, ['春', '桜', '新生活', '花見']),
            'summer': (6, 8, ['夏', '暑い', '夏休み', '海']),
            'autumn': (9, 11, ['秋', '紅葉', '読書の秋', '食欲の秋']),
            'winter': (12, 2, ['冬', '寒い', 'クリスマス', '年末年始'])
        }
        
        # 時間帯の要素を取得
        time_element = None
        for period, (start, end, elements) in time_elements.items():
            if start <= hour < end or (start > end and (hour >= start or hour < end)):
                time_element = random.choice(elements)
                break
        
        # 季節の要素を取得
        month = now.month
        season_element = None
        for season, (start_month, end_month, elements) in season_elements.items():
            if start_month <= month <= end_month:
                season_element = random.choice(elements)
                break
        
        return {
            'time': time_element,
            'season': season_element,
            'weekday': ['月曜', '火曜', '水曜', '木曜', '金曜', '土曜', '日曜'][now.weekday()],
            'date': f"{now.month}月{now.day}日"
        }
    
    def create_trend_aware_content(self, base_text, current_trends=None):
        """トレンドを意識したコンテンツを生成"""
        trend_templates = [
            "今話題の{trend}について、{content}",
            "{trend}が注目される中、{content}",
            "みんなが気になる{trend}。実は{content}",
            "{trend}ブームに乗って、{content}"
        ]
        
        if current_trends and len(current_trends) > 0:
            trend = random.choice(current_trends)
            template = random.choice(trend_templates)
            return template.format(trend=trend, content=base_text)
        
        return base_text