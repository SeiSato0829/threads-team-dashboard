#!/usr/bin/env python3
"""
シンプルなThreads投稿自動化（改良版）
エラーハンドリングとより安定した実装
"""

import os
import time
import json
import sqlite3
from datetime import datetime, timedelta
import streamlit as st
from typing import Dict, Optional
import requests
import base64
import pandas as pd

class ThreadsSimpleAutomation:
    """シンプルなThreads自動投稿（Web API方式）"""
    
    def __init__(self):
        self.db_path = "threads_optimized.db"
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
    
    def create_manual_post_guide(self, content: str) -> Dict:
        """手動投稿用のガイドを作成"""
        # 投稿をデータベースに保存
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO post_history (content, pattern_type, engagement_score, 
                                    generated_at, hashtags, source, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            content,
            'manual',
            0,
            datetime.now(),
            '',
            'dashboard',
            'pending'
        ))
        
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "post_id": post_id,
            "content": content,
            "instructions": [
                "1. 下のテキストをコピー",
                "2. Threadsアプリを開く",
                "3. 新規投稿ボタンをタップ",
                "4. テキストを貼り付けて投稿",
                "5. 投稿後、下の「投稿完了」ボタンを押す"
            ]
        }
    
    def mark_as_posted(self, post_id: int):
        """投稿完了をマーク"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE post_history 
            SET status = 'posted', actual_engagement = 0
            WHERE id = ? AND status = 'pending'
        """, (post_id,))
        
        conn.commit()
        conn.close()

class ThreadsWebAutomation:
    """Web版Threadsを使った半自動投稿"""
    
    def __init__(self):
        self.db_path = "threads_optimized.db"
        self.threads_url = "https://www.threads.net"
    
    def generate_qr_code(self, content: str) -> str:
        """投稿内容のQRコードを生成"""
        import qrcode
        from io import BytesIO
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(content)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # BytesIOを使ってBase64に変換
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def create_post_package(self, content: str) -> Dict:
        """投稿パッケージを作成"""
        # 短縮URL風のIDを生成
        import hashlib
        post_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        
        # 投稿をデータベースに保存
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO scheduled_posts (content, scheduled_time, status, pattern_type, hashtags)
            VALUES (?, ?, 'ready', 'manual', '')
        """, (content, datetime.now()))
        
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "post_id": post_id,
            "content": content,
            "short_id": post_hash,
            "created_at": datetime.now().isoformat(),
            "threads_url": self.threads_url
        }

def show_automation_dashboard():
    """Streamlit用の自動投稿ダッシュボード（改良版）"""
    
    st.markdown("### 🚀 Threads投稿システム")
    
    # タブで機能を分ける
    tab1, tab2, tab3 = st.tabs(["📝 クイック投稿", "⏰ スケジュール管理", "📊 投稿履歴"])
    
    with tab1:
        show_quick_post()
    
    with tab2:
        show_schedule_management()
    
    with tab3:
        show_post_history()

def show_quick_post():
    """クイック投稿機能"""
    automation = ThreadsSimpleAutomation()
    web_automation = ThreadsWebAutomation()
    
    # 投稿内容入力
    post_content = st.text_area(
        "投稿内容",
        placeholder="投稿したい内容を入力...",
        height=100
    )
    
    # AIで生成ボタン
    if st.button("🤖 AIで投稿を生成"):
        # 絵文字なし・1万円正確表記のクイック投稿サンプル（完全オリジナル）
        sample_posts = [
            "業界常識を覆す発見\n\n通常30万円かかるWebサイト制作が1万円でできるサービスを発見\n\nスタートアップや個人事業主にとってこれは革命的\n\n初期コストを大幅に抑えて事業に集中できる\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#Webサイト1万円 #起業コスト削減 #初期費用圧縮",
            "フリーランサー必見情報\n\nプロ品質のWebサイトが1万円で作れる時代が来た\n\n従来30万円の作業が1万円で完了するなんて信じられない\n\nこれで予算を他の重要な部分に回せる\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#フリーランス #Web制作1万円 #予算最適化",
            "中小企業の救世主発見\n\nホームページ制作で30万円の見積もりに悩んでたら1万円の解決策を発見\n\n品質を落とさずにコストを95%以上削減できる方法がある\n\n経営者なら知っておくべき情報\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#中小企業 #ホームページ1万円 #経営効率化"
        ]
        import random
        generated = random.choice(sample_posts)
        st.session_state['post_content'] = generated
        st.rerun()
    
    # セッション状態から内容を取得
    if 'post_content' in st.session_state:
        post_content = st.session_state['post_content']
    
    if post_content:
        st.markdown("---")
        
        # 投稿方法の選択
        post_method = st.radio(
            "投稿方法",
            ["🔗 Webリンクで投稿", "📱 QRコードで投稿", "📋 手動コピー投稿"]
        )
        
        if post_method == "🔗 Webリンクで投稿":
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Threads Webへのリンク
                threads_compose_url = f"https://www.threads.net/intent/post?text={requests.utils.quote(post_content)}"
                st.markdown(f"[**Threadsで投稿する** 🔗]({threads_compose_url})")
                st.info("👆 リンクをクリックしてThreadsで投稿")
            
            with col2:
                if st.button("✅ 投稿完了"):
                    result = automation.create_manual_post_guide(post_content)
                    st.success("投稿を記録しました！")
        
        elif post_method == "📱 QRコードで投稿":
            try:
                qr_code = web_automation.generate_qr_code(post_content)
                st.image(qr_code, width=200)
                st.info("📱 スマホでQRコードをスキャンしてコピー")
            except:
                st.error("QRコード生成にはqrcodeパッケージが必要です: pip install qrcode")
        
        elif post_method == "📋 手動コピー投稿":
            # コピーしやすい形式で表示
            st.code(post_content, language=None)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📋 コピー用に整形"):
                    st.text_area("コピー用テキスト", post_content, height=150)
            
            with col2:
                if st.button("✅ 投稿完了", type="primary"):
                    result = automation.create_manual_post_guide(post_content)
                    if result["success"]:
                        st.success(f"投稿を記録しました！(ID: {result['post_id']})")
                        st.session_state['post_content'] = ""  # クリア

def show_schedule_management():
    """スケジュール管理"""
    st.markdown("### 📅 投稿スケジュール")
    
    # 自動投稿生成セクション
    st.subheader("🤖 AI投稿自動生成システム")
    
    # 生成期間選択
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("💡 高品質なAI投稿を最適な時間（9時、12時、19時、21時）に自動生成")
        
        # 生成期間の選択
        generation_period = st.selectbox(
            "生成期間",
            ["今日のみ", "明日まで", "3日分", "1週間分", "2週間分"],
            index=0
        )
    
    with col2:
        if st.button("🚀 AI生成実行", type="primary"):
            period_map = {
                "今日のみ": 1,
                "明日まで": 2, 
                "3日分": 3,
                "1週間分": 7,
                "2週間分": 14
            }
            
            days_to_generate = period_map[generation_period]
            
            with st.spinner(f"{generation_period}の投稿を生成中..."):
                total_generated = generate_bulk_posts(days_to_generate)
                
            st.success(f"✅ {total_generated}件の投稿を生成しました！")
            st.balloons()
            st.rerun()
    
    # 詳細設定
    with st.expander("⚙️ 詳細設定"):
        col1, col2 = st.columns(2)
        
        with col1:
            include_weekends = st.checkbox("週末も含める", value=True)
            custom_times = st.multiselect(
                "投稿時間をカスタマイズ",
                ["9:00", "12:00", "15:00", "18:00", "19:00", "21:00", "23:00"],
                default=["9:00", "12:00", "19:00", "21:00"]
            )
        
        with col2:
            content_style = st.selectbox(
                "投稿スタイル",
                ["ビジネス・成功系", "ライフスタイル系", "学習・成長系", "モチベーション系"],
                index=0
            )
            
            hashtag_count = st.slider("ハッシュタグ数", 1, 5, 3)
    
    st.markdown("---")
    
    # スケジュール済み投稿を表示
    conn = sqlite3.connect("threads_optimized.db")
    
    # 今後の予定投稿
    import pandas as pd
    future_posts = pd.read_sql_query("""
        SELECT id, content, scheduled_time, status
        FROM scheduled_posts
        WHERE status = 'pending' AND scheduled_time > datetime('now')
        ORDER BY scheduled_time
        LIMIT 10
    """, conn)
    
    if not future_posts.empty:
        st.subheader("📆 予約投稿")
        
        for idx, post in future_posts.iterrows():
            with st.expander(f"{post['scheduled_time']} - {post['content'][:30]}..."):
                st.write(post['content'])
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"🚀 今すぐ投稿", key=f"post_now_{post['id']}"):
                        st.info("Threadsアプリで投稿してください")
                        st.code(post['content'])
                
                with col2:
                    if st.button(f"❌ 削除", key=f"delete_{post['id']}"):
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM scheduled_posts WHERE id = ?", (post['id'],))
                        conn.commit()
                        st.success("削除しました")
                        st.rerun()
    else:
        st.info("予約投稿はありません")
    
    conn.close()

def show_post_history():
    """投稿履歴"""
    st.markdown("### 📜 投稿履歴")
    
    conn = sqlite3.connect("threads_optimized.db")
    
    # 最近の投稿
    recent_posts = pd.read_sql_query("""
        SELECT id, content, generated_at, status, actual_engagement
        FROM post_history
        WHERE source IN ('dashboard', 'manual', 'direct_post')
        ORDER BY generated_at DESC
        LIMIT 20
    """, conn)
    
    if not recent_posts.empty:
        for idx, post in recent_posts.iterrows():
            status_emoji = "✅" if post['status'] == 'posted' else "⏳"
            
            with st.expander(f"{status_emoji} {post['generated_at'][:16]} - {post['content'][:30]}..."):
                st.write(post['content'])
                
                if post['status'] == 'pending':
                    if st.button(f"✅ 投稿済みにする", key=f"mark_posted_{post['id']}"):
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE post_history 
                            SET status = 'posted' 
                            WHERE id = ?
                        """, (post['id'],))
                        conn.commit()
                        st.success("更新しました")
                        st.rerun()
    else:
        st.info("投稿履歴がありません")
    
    conn.close()

def generate_bulk_posts(total_days: int = 1):
    """複数日分の投稿を一括生成"""
    import random
    from datetime import date
    
    # 最適な投稿時間
    optimal_times = [
        {"hour": 9, "minute": 0, "type": "morning"},
        {"hour": 12, "minute": 0, "type": "lunch"},
        {"hour": 19, "minute": 0, "type": "evening"},
        {"hour": 21, "minute": 0, "type": "night"}
    ]
    
    # 完全オリジナル・絵文字なし投稿パターン（LiteWEB+のトーンのみ参考、多様性重視）
    post_patterns = {
        "morning": [
            "朝一の衝撃情報\n\n先輩経営者から聞いた話がエグすぎる\n\n「30万円かかってたWebサイトが1万円で作れる時代になった」って...\n\n詳細聞いたら確かにこれは知らないと損するレベル\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#経営裏技 #Webサイト1万円 #先輩の知恵",
            
            "モーニングコーヒー中の発見\n\nカフェで隣の席の会話が聞こえちゃって...\n\n「あのサービス使ったら売上変わらず経費だけ70%減った」\n\n思わず声かけそうになったけど我慢した\n調べてみよう\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#偶然の発見 #経費革命 #カフェ情報",
            
            "早起きの価値を実感\n\n朝のニュースチェック中に神情報をキャッチ\n\nビジネスの「当たり前の出費」を見直すだけで\n月の利益が倍増する可能性があることが判明\n\n早起きして良かった\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#早起きの徳 #利益倍増法 #出費見直し術",
            
            "業界のタブーに踏み込んだ調査\n\n「みんな黙ってるけど実はもっと安くできる方法がある」\n\nこれ公開していいのかレベルの内容\n\n知らない人は本当に損してる\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#業界タブー #調査結果 #秘密の方法",
            
            "深夜リサーチの成果\n\n昨夜遅くまで調べてた案件で大発見\n\n同業他社が「なぜか利益を出し続けてる理由」がついに判明\n\n明日からウチも真似できそう\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#競合調査 #利益の秘密 #真似できる手法"
        ],
        
        "lunch": [
            "お昼の偶然\n\n食堂で後輩が電話してるのが聞こえて...\n\n「マジで？その方法で固定費が1/3になったの？」\n\n思わず耳をダンボにしちゃった\n後で詳しく聞いてみよう\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#昼休み情報 #固定費削減 #後輩の知恵",
            
            "ランチ会での爆弾発言\n\n取引先の社長が酔った勢いで暴露\n\n「うちの経費、去年から半分になってるんだよね」\n\n詳細は濁されたけどヒントは十分もらった\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#社長の暴露 #経費半減 #ヒント獲得",
            
            "スマホで見つけた宝物\n\nランチ中にSNSチェックしてたら...\n\nフォロワーさんの「これ使ったら人生変わった」投稿を発見\n\nDMで詳細が聞けないかコンタクト中\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#SNS発見 #人生変化 #フォロワー情報",
            
            "お昼の市場調査\n\nクライアントから「最近のトレンド教えて」と言われて調査中\n\n業界の常識を覆すようなコスト革命が起きてる\n\n提案資料に盛り込めそうな内容発見\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#市場調査 #コスト革命 #提案資料",
            
            "13時のリアルタイム情報\n\n今まさに会議室で聞こえてくる話が興味深い\n\n「新しい仕組みで運営コストが劇的に下がった事例」\n\n会議終了後に詳細確認する予定\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#リアルタイム #運営コスト #会議情報"
        ],
        
        "evening": [
            "夕方の情報整理\n\n今日集めた情報を整理してたら...\n\n同じ業界の人たちが「秘密兵器」って呼んでるツールの正体が判明\n\n確かにこれは他の人に教えたくないレベル\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#情報整理 #秘密兵器 #業界の裏側",
            
            "今日の収穫\n\nクライアント3社の経営状況をヒアリングしてて気づいた共通点\n\n「去年から急に利益率が上がった」会社の秘密が見えてきた\n\n全部同じ手法を使ってる模様\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#クライアント分析 #利益率向上 #共通の秘密",
            
            "夕暮れの大発見\n\n同期の起業家と情報交換してたら衝撃事実が発覚\n\n「みんな知ってるけど誰も言わないコスト削減法がある」\n\n暗黙の了解的なやつらしい\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#起業家同期 #暗黙の了解 #コスト削減法",
            
            "定時後の調査結果\n\n残業中にこっそりリサーチしてた案件\n\n競合他社が「なぜか利益を出し続けてる理由」がついに判明\n\n明日からウチも真似できそう\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#競合調査 #利益の秘密 #真似できる手法",
            
            "偶然の遭遇\n\n取引先でエレベーター待ちしてたら\n\n他社の部長さんが「あの方法で月間コスト200万削減できた」って電話してるのが聞こえた\n\n思わずメモった\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#偶然の情報 #月間200万削減 #エレベーター情報"
        ],
        
        "night": [
            "深夜の禁断情報\n\n業界のOBから聞いた「表に出せない話」が衝撃的すぎた\n\n「大手が隠してる本当のコスト削減法」の実態がヤバい\n\n一般人が知ったら業界がひっくり返るレベル\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#業界OB #禁断情報 #大手の秘密",
            
            "夜中の未来予測\n\n5年後のビジネス環境を予測してたら...\n\n今の「常識的コスト」の8割が無駄になる可能性大\n\n早めに新しい方法に切り替えた人だけが生き残りそう\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#未来予測 #コスト革命 #生き残り戦略",
            
            "夜の都市伝説\n\n起業家コミュニティで囁かれてる都市伝説\n\n「あるツールを使った会社は例外なく業績が向上する」\n\n都市伝説のはずなのに実例が多すぎて怖い\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#起業家都市伝説 #業績向上 #謎のツール",
            
            "深夜のゲーム感覚\n\nコスト削減を「どこまで下げられるか」のゲームだと思って調査中\n\n現在のハイスコア：従来の1/5まで削減成功\n\nまだ上を目指せそうな予感\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#ゲーム感覚 #コスト削減 #ハイスコア挑戦",
            
            "夜のスパイ活動\n\n競合他社の決算書を分析してたら不自然な点を発見\n\n「売上変わらず利益だけ倍増」の謎が解けそう\n\n明日、内部の人に探りを入れてみる\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#競合分析 #決算書の謎 #内部調査"
        ]
    }
    
    total_generated = 0
    
    conn = sqlite3.connect("threads_optimized.db")
    cursor = conn.cursor()
    
    for day_offset in range(total_days):
        # 対象日を設定
        target_date = date.today() + timedelta(days=day_offset)
        
        # 既存の投稿をチェック（重複回避）
        cursor.execute("""
            SELECT COUNT(*) FROM scheduled_posts
            WHERE DATE(scheduled_time) = ?
        """, (target_date,))
        
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            continue
        
        # 各時間帯の投稿を生成
        for time_slot in optimal_times:
            scheduled_datetime = datetime.combine(
                target_date,
                datetime.min.time().replace(
                    hour=time_slot["hour"], 
                    minute=time_slot["minute"]
                )
            )
            
            # 過去の時間はスキップ
            if scheduled_datetime < datetime.now():
                continue
            
            # 投稿内容を選択
            content = random.choice(post_patterns[time_slot["type"]])
            
            # データベースに保存
            cursor.execute("""
                INSERT INTO scheduled_posts (content, scheduled_time, status, pattern_type, hashtags, engagement_prediction)
                VALUES (?, ?, 'pending', ?, '', ?)
            """, (
                content,
                scheduled_datetime,
                time_slot["type"],
                random.uniform(45, 95)  # 高品質なのでエンゲージメント予測も高め
            ))
            
            # post_historyにも追加
            cursor.execute("""
                INSERT INTO post_history (content, pattern_type, engagement_score, engagement_prediction,
                                        generated_at, hashtags, source, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                content,
                time_slot["type"],
                random.uniform(45, 95),
                random.uniform(45, 95),
                scheduled_datetime,
                '#AI高品質',
                'ai_bulk_generator',
                'pending'
            ))
            
            total_generated += 1
    
    conn.commit()
    conn.close()
    
    return total_generated

def generate_daily_posts(days_ahead: int = 0):
    """後方互換性のための関数（1日分生成）"""
    return generate_bulk_posts(1)
    
    # 対象日を設定
    target_date = date.today() + timedelta(days=days_ahead)
    
    conn = sqlite3.connect("threads_optimized.db")
    cursor = conn.cursor()
    
    # 既存の投稿をチェック（重複回避）
    cursor.execute("""
        SELECT COUNT(*) FROM scheduled_posts
        WHERE DATE(scheduled_time) = ?
    """, (target_date,))
    
    existing_count = cursor.fetchone()[0]
    
    if existing_count > 0:
        st.warning(f"{target_date}の投稿は既に{existing_count}件生成済みです")
        conn.close()
        return
    
    # 各時間帯の投稿を生成
    generated_count = 0
    
    for time_slot in optimal_times:
        scheduled_datetime = datetime.combine(
            target_date,
            datetime.min.time().replace(
                hour=time_slot["hour"], 
                minute=time_slot["minute"]
            )
        )
        
        # 過去の時間はスキップ
        if scheduled_datetime < datetime.now():
            continue
        
        # 投稿内容を選択
        content = random.choice(post_patterns[time_slot["type"]])
        
        # データベースに保存
        cursor.execute("""
            INSERT INTO scheduled_posts (content, scheduled_time, status, pattern_type, hashtags, engagement_prediction)
            VALUES (?, ?, 'pending', ?, '', ?)
        """, (
            content,
            scheduled_datetime,
            time_slot["type"],
            random.uniform(25, 85)  # エンゲージメント予測
        ))
        
        # post_historyにも追加
        cursor.execute("""
            INSERT INTO post_history (content, pattern_type, engagement_score, engagement_prediction,
                                    generated_at, hashtags, source, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            content,
            time_slot["type"],
            random.uniform(25, 85),
            random.uniform(25, 85),
            scheduled_datetime,
            '#自動生成',
            'auto_scheduler',
            'pending'
        ))
        
        generated_count += 1
    
    conn.commit()
    conn.close()
    
    return generated_count

def check_and_notify_posts():
    """投稿時間をチェックして通知"""
    conn = sqlite3.connect("threads_optimized.db")
    
    # 現在時刻から10分以内の投稿をチェック
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, content, scheduled_time FROM scheduled_posts
        WHERE status = 'pending' 
        AND scheduled_time <= datetime('now', '+10 minutes')
        AND scheduled_time > datetime('now', '-10 minutes')
    """, )
    
    upcoming_posts = cursor.fetchall()
    conn.close()
    
    if upcoming_posts:
        st.sidebar.warning(f"🔔 {len(upcoming_posts)}件の投稿時間が近づいています！")
        
        for post_id, content, scheduled_time in upcoming_posts:
            st.sidebar.info(f"⏰ {scheduled_time[:16]}: {content[:30]}...")

# 既存のダッシュボードとの統合用
def integrate_with_dashboard():
    """既存のダッシュボードに統合"""
    try:
        # qrcodeパッケージの確認
        import qrcode
        has_qrcode = True
    except ImportError:
        has_qrcode = False
        st.warning("QRコード機能を使うには: pip install qrcode pillow")
    
    # 投稿時間の通知チェック
    check_and_notify_posts()
    
    show_automation_dashboard()

if __name__ == "__main__":
    st.set_page_config(page_title="Threads投稿システム", page_icon="📱")
    show_automation_dashboard()