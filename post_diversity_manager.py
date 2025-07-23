"""
投稿多様性管理システム
重複や類似投稿を防ぎ、バリエーション豊かなコンテンツを生成
"""

import random
import hashlib
from datetime import datetime
import json

class PostDiversityManager:
    """投稿の多様性を管理するクラス"""
    
    def __init__(self):
        # 絵文字パターンを大幅に拡張
        self.emoji_patterns = {
            'excitement': ['🔥', '⚡', '💫', '✨', '🌟', '💥', '🎯', '🚀', '🌈', '☄️'],
            'joy': ['😊', '😄', '🥳', '🎉', '🎊', '🤗', '😍', '💖', '💝', '🌺'],
            'thinking': ['💡', '🤔', '💭', '🧠', '📝', '✍️', '📖', '🔍', '🔎', '💬'],
            'gaming': ['🎮', '🕹️', '👾', '🎯', '🏆', '🥇', '⚔️', '🛡️', '🎲', '🃏'],
            'entertainment': ['🎬', '🎭', '🎪', '🎨', '🎵', '🎸', '🎤', '📺', '🎥', '🍿'],
            'business': ['💼', '📊', '📈', '💰', '🏢', '🤝', '👔', '📱', '💻', '🌐'],
            'marketing': ['📢', '📣', '🎯', '📱', '💡', '🚀', '📊', '🔗', '🌟', '💎'],
            'tech': ['💻', '📱', '🤖', '🔧', '⚙️', '🛠️', '💾', '🖥️', '📡', '🔬'],
            'nature': ['🌸', '🌺', '🌻', '🌷', '🌿', '🍃', '🌲', '🌴', '🌊', '☀️'],
            'food': ['🍜', '🍱', '🍙', '🍣', '🍰', '☕', '🍵', '🥟', '🍛', '🍲']
        }
        
        # CTAパターンを多様化
        self.cta_patterns = [
            "みんなの意見も聞かせて！",
            "あなたはどう思う？",
            "コメントで教えて！",
            "シェアして広めよう！",
            "保存して後でチェック！",
            "フォローして最新情報をゲット！",
            "いいねで応援してね！",
            "気になったらRT！",
            "詳細はプロフィールのリンクから！",
            "一緒に盛り上がろう！",
            "あなたの体験談も教えて！",
            "これ知ってた？",
            "続きが気になる人は👇",
            "詳しくはコメント欄で！",
            "みんなはどっち派？"
        ]
        
        # 投稿開始パターン
        self.opening_patterns = [
            "【{genre}速報】",
            "◆{genre}ニュース◆",
            "＼{genre}情報／",
            "📍{genre}トピック",
            "▶︎{genre}最新情報",
            "《{genre}》",
            "★{genre}★",
            "【必見】{genre}",
            "〜{genre}話題〜",
            "#{genre}",
            "💫{genre}トレンド",
            "🔔{genre}アップデート",
            "{emoji} {genre}の話",
            "今話題の{genre}",
            "{genre}好き必見"
        ]
        
        # トレンドハッシュタグ組み合わせ
        self.hashtag_sets = {
            'general': [
                ['#Threads', '#スレッズ', '#SNS', '#フォロー'],
                ['#トレンド', '#話題', '#バズり', '#注目'],
                ['#拡散希望', '#シェア', '#RT希望', '#みんなに教えたい'],
                ['#最新情報', '#ニュース', '#速報', '#必見'],
                ['#今日の発見', '#なるほど', '#知らなかった', '#豆知識']
            ],
            'engagement': [
                ['#いいねした人全員フォロー', '#相互フォロー', '#フォロバ100', '#繋がりたい'],
                ['#コメント歓迎', '#意見募集', '#教えて', '#アンケート'],
                ['#みんなの意見', '#共感したらRT', '#あるある', '#わかる'],
                ['#体験談募集', '#エピソード', '#思い出', '#シェアしよう'],
                ['#参加型', '#一緒に', '#募集中', '#仲間募集']
            ]
        }
        
        # 投稿履歴を保存（重複チェック用）
        self.post_history = set()
        self.recent_emojis = []
        self.recent_ctas = []
        self.recent_openings = []
    
    def generate_unique_post(self, base_text, genre, reference_posts=None):
        """ユニークな投稿を生成"""
        # ジャンルに適した絵文字セットを選択
        emoji_categories = self._get_relevant_emoji_categories(genre)
        
        # 最近使用していない要素を選択
        emoji_set = self._get_diverse_emojis(emoji_categories, 3)
        opening = self._get_unique_opening(genre, emoji_set[0])
        cta = self._get_unique_cta()
        hashtags = self._get_diverse_hashtags(genre)
        
        # 投稿を構築
        post_parts = []
        
        # 開始部分
        post_parts.append(opening)
        post_parts.append("")
        
        # メインコンテンツ（base_textを活用）
        enhanced_text = self._enhance_text(base_text, emoji_set[1:])
        post_parts.append(enhanced_text)
        post_parts.append("")
        
        # CTA
        post_parts.append(f"{random.choice(emoji_set)} {cta}")
        post_parts.append("")
        
        # ハッシュタグ
        post_parts.append(" ".join(hashtags))
        
        # 投稿を組み立て
        final_post = "\n".join(post_parts)
        
        # 文字数チェックと調整
        if len(final_post) > 500:
            final_post = self._trim_post(final_post, 500)
        
        # ハッシュを生成して履歴に追加
        post_hash = self._generate_hash(final_post)
        self.post_history.add(post_hash)
        
        return final_post
    
    def _get_relevant_emoji_categories(self, genre):
        """ジャンルに関連する絵文字カテゴリを取得"""
        genre_lower = genre.lower()
        
        category_mapping = {
            'ゲーム': ['gaming', 'excitement', 'joy'],
            'エンタメ': ['entertainment', 'joy', 'excitement'],
            'ビジネス': ['business', 'thinking', 'tech'],
            'マーケティング': ['marketing', 'business', 'thinking'],
            'テック': ['tech', 'thinking', 'excitement'],
            '料理': ['food', 'joy', 'nature'],
            'スポーツ': ['excitement', 'joy', 'gaming']
        }
        
        for key, categories in category_mapping.items():
            if key in genre_lower:
                return categories
        
        # デフォルト
        return ['excitement', 'joy', 'thinking']
    
    def _get_diverse_emojis(self, categories, count=3):
        """多様な絵文字を選択"""
        selected_emojis = []
        
        for category in categories[:count]:
            available_emojis = [e for e in self.emoji_patterns.get(category, []) 
                               if e not in self.recent_emojis[-10:]]
            if available_emojis:
                emoji = random.choice(available_emojis)
                selected_emojis.append(emoji)
                self.recent_emojis.append(emoji)
        
        # 履歴を管理
        if len(self.recent_emojis) > 30:
            self.recent_emojis = self.recent_emojis[-30:]
        
        return selected_emojis
    
    def _get_unique_opening(self, genre, emoji):
        """ユニークな開始パターンを取得"""
        available_openings = [op for op in self.opening_patterns 
                            if op not in self.recent_openings[-5:]]
        
        if not available_openings:
            available_openings = self.opening_patterns
        
        opening = random.choice(available_openings)
        opening = opening.format(genre=genre, emoji=emoji)
        
        self.recent_openings.append(opening)
        if len(self.recent_openings) > 10:
            self.recent_openings = self.recent_openings[-10:]
        
        return opening
    
    def _get_unique_cta(self):
        """ユニークなCTAを取得"""
        available_ctas = [cta for cta in self.cta_patterns 
                         if cta not in self.recent_ctas[-5:]]
        
        if not available_ctas:
            available_ctas = self.cta_patterns
        
        cta = random.choice(available_ctas)
        self.recent_ctas.append(cta)
        
        if len(self.recent_ctas) > 10:
            self.recent_ctas = self.recent_ctas[-10:]
        
        return cta
    
    def _get_diverse_hashtags(self, genre):
        """多様なハッシュタグセットを取得"""
        hashtags = []
        
        # ジャンル固有のハッシュタグ
        hashtags.append(f"#{genre}")
        
        # 一般的なハッシュタグセットから選択
        general_set = random.choice(self.hashtag_sets['general'])
        engagement_set = random.choice(self.hashtag_sets['engagement'])
        
        # ランダムに2-3個選択
        hashtags.extend(random.sample(general_set, 2))
        hashtags.extend(random.sample(engagement_set, 1))
        
        # 時期的なハッシュタグを追加（季節や曜日）
        hashtags.append(self._get_temporal_hashtag())
        
        return hashtags[:5]  # 最大5個
    
    def _get_temporal_hashtag(self):
        """時期的なハッシュタグを生成"""
        now = datetime.now()
        weekday_tags = {
            0: '#月曜日', 1: '#火曜日', 2: '#水曜日', 
            3: '#木曜日', 4: '#金曜日', 5: '#土曜日', 6: '#日曜日'
        }
        
        season_tags = {
            (3, 4, 5): '#春',
            (6, 7, 8): '#夏', 
            (9, 10, 11): '#秋',
            (12, 1, 2): '#冬'
        }
        
        # 30%の確率で曜日タグ
        if random.random() < 0.3:
            return weekday_tags[now.weekday()]
        
        # 30%の確率で季節タグ
        if random.random() < 0.3:
            month = now.month
            for months, tag in season_tags.items():
                if month in months:
                    return tag
        
        # それ以外は年月タグ
        return f"#{now.year}年{now.month}月"
    
    def _enhance_text(self, text, emojis):
        """テキストを絵文字で強化"""
        # 文を分割
        sentences = text.split('。')
        enhanced_sentences = []
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                # 30%の確率で文頭に絵文字
                if random.random() < 0.3 and emojis:
                    sentence = f"{random.choice(emojis)} {sentence}"
                
                enhanced_sentences.append(sentence)
        
        return '。'.join(enhanced_sentences) + ('。' if text.endswith('。') else '')
    
    def _trim_post(self, post, max_length):
        """投稿を最大文字数に収める"""
        if len(post) <= max_length:
            return post
        
        # ハッシュタグ部分を保持
        lines = post.split('\n')
        hashtag_line = lines[-1] if lines[-1].startswith('#') else ''
        
        # 本文を調整
        main_content = '\n'.join(lines[:-1]) if hashtag_line else post
        available_length = max_length - len(hashtag_line) - 2  # 改行分
        
        trimmed_content = main_content[:available_length-3] + '...'
        
        return f"{trimmed_content}\n\n{hashtag_line}" if hashtag_line else trimmed_content
    
    def _generate_hash(self, text):
        """投稿のハッシュを生成"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def check_similarity(self, post1, post2, threshold=0.7):
        """2つの投稿の類似度をチェック"""
        # 簡易的な類似度計算（実際にはより高度なアルゴリズムを使用可能）
        words1 = set(post1.split())
        words2 = set(post2.split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0
        
        similarity = len(intersection) / len(union)
        return similarity
    
    def is_duplicate(self, post):
        """投稿が重複していないかチェック"""
        post_hash = self._generate_hash(post)
        return post_hash in self.post_history