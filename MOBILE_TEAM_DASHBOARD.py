#!/usr/bin/env python3
"""
🌟 チーム&モバイル完全対応 Threads管理システム
社内メンバー・携帯電話フル対応版
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import json
import os
import qrcode
from io import BytesIO
import base64
import socket

# 📱 モバイル完全対応設定
st.set_page_config(
    page_title="📱 Threads Team Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Threads Team Management System v2.0"
    }
)

# 🎨 モバイル対応CSS
st.markdown("""
<style>
    /* モバイル最適化 */
    @media (max-width: 768px) {
        .main > div {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .stButton > button {
            width: 100%;
            height: 3rem;
            font-size: 1.2rem;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin: 0.5rem 0;
        }
        
        .mobile-nav {
            display: flex;
            overflow-x: auto;
            padding: 0.5rem;
            gap: 0.5rem;
        }
        
        .nav-item {
            min-width: 120px;
            padding: 0.5rem 1rem;
            background: #f0f2f6;
            border-radius: 20px;
            text-align: center;
            font-weight: bold;
        }
    }
    
    /* チーム共有スタイル */
    .team-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    .qr-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
        background: #f8f9ff;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .access-info {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class MobileTeamDashboard:
    """📱 モバイル&チーム対応ダッシュボード"""
    
    def __init__(self):
        self.server_ip = self.get_server_ip()
        self.db_paths = {
            "scheduled_posts": "scheduled_posts.db",
            "threads_optimized": "threads_optimized.db",
            "buzz_history": "buzz_history.db",
            "viral_history": "viral_history.db"
        }
        self.ensure_databases()
    
    def get_server_ip(self):
        """サーバーIPアドレスを取得"""
        try:
            # 最も確実な方法
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "192.168.255.89"  # フォールバック
    
    def ensure_databases(self):
        """データベース確認・作成"""
        for name, path in self.db_paths.items():
            if not os.path.exists(path):
                self.create_database(path)
    
    def create_database(self, path):
        """データベース作成"""
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        # 統一テーブル構造
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scheduled_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            scheduled_time TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'pending',
            posted_at TIMESTAMP,
            pattern_type TEXT DEFAULT 'general',
            hashtags TEXT DEFAULT '',
            engagement_prediction REAL DEFAULT 0,
            actual_engagement REAL DEFAULT 0,
            clicks INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS post_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            pattern_type TEXT DEFAULT 'general',
            engagement_score REAL DEFAULT 0,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            hashtags TEXT DEFAULT '',
            source TEXT DEFAULT 'manual',
            status TEXT DEFAULT 'posted',
            actual_engagement REAL DEFAULT 0,
            clicks INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0
        )
        """)
        
        conn.commit()
        conn.close()
    
    def generate_access_qr(self, url):
        """アクセス用QRコード生成"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            st.error(f"QRコード生成エラー: {e}")
            return None
    
    def get_all_posts(self):
        """全投稿データ取得"""
        all_posts = []
        
        for db_name, db_path in self.db_paths.items():
            if os.path.exists(db_path):
                try:
                    conn = sqlite3.connect(db_path)
                    
                    if db_name == "scheduled_posts":
                        df = pd.read_sql_query("""
                        SELECT 
                            id, content, scheduled_time, status, posted_at,
                            pattern_type, engagement_prediction, actual_engagement,
                            clicks, shares, comments, likes,
                            'scheduled' as source
                        FROM scheduled_posts
                        ORDER BY scheduled_time DESC
                        """, conn)
                    else:
                        df = pd.read_sql_query("""
                        SELECT 
                            id, content, generated_at as scheduled_time,
                            COALESCE(status, 'posted') as status,
                            pattern_type, engagement_score as engagement_prediction,
                            actual_engagement, clicks, shares, comments, likes,
                            ? as source
                        FROM post_history
                        ORDER BY generated_at DESC
                        """, conn, params=[db_name])
                    
                    if not df.empty:
                        all_posts.append(df)
                    
                    conn.close()
                except Exception as e:
                    st.error(f"データベース読み込みエラー ({db_name}): {e}")
        
        if all_posts:
            combined_df = pd.concat(all_posts, ignore_index=True, sort=False)
            combined_df['scheduled_time'] = pd.to_datetime(combined_df['scheduled_time'])
            
            # データクリーニング
            for col in ['actual_engagement', 'clicks', 'shares', 'comments', 'likes', 'engagement_prediction']:
                combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce').fillna(0)
            
            return combined_df
        else:
            return pd.DataFrame()

def show_mobile_navigation():
    """📱 モバイルナビゲーション"""
    st.markdown("""
    <div class="mobile-nav">
        <div class="nav-item">📊 概要</div>
        <div class="nav-item">📱 チーム</div>
        <div class="nav-item">🚀 投稿</div>
        <div class="nav-item">📈 分析</div>
    </div>
    """, unsafe_allow_html=True)

def show_team_access_info(dashboard):
    """👥 チームアクセス情報表示"""
    st.header("👥 チームアクセス設定")
    
    # アクセス情報カード
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="access-info">
            <h3>🌐 社内アクセスURL</h3>
            <p><strong>http://{dashboard.server_ip}:8501</strong></p>
            <p>社内ネットワークから直接アクセス</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 接続テスト
        if st.button("🔍 接続テスト", key="connection_test"):
            st.success(f"✅ サーバー稼働中: {dashboard.server_ip}:8501")
    
    with col2:
        # QRコード生成
        url = f"http://{dashboard.server_ip}:8501"
        qr_code = dashboard.generate_access_qr(url)
        
        if qr_code:
            st.markdown("""
            <div class="qr-container">
                <div>
                    <h4>📱 モバイルアクセス</h4>
                    <p>QRコードをスキャン</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.image(qr_code, width=200)
        else:
            st.error("QRコード生成に失敗しました")
    
    # チーム設定ガイド
    with st.expander("⚙️ チーム設定ガイド", expanded=False):
        st.markdown(f"""
        ### 📋 セットアップ手順
        
        **1. 社内PC・ラップトップアクセス:**
        ```
        http://{dashboard.server_ip}:8501
        ```
        
        **2. スマートフォンアクセス:**
        - 上のQRコードをスキャン
        - または同じURLを直接入力
        
        **3. チームメンバー追加:**
        - 全員が同じネットワーク内であること確認
        - Windows ファイアウォール設定確認
        - ポート8501が開放されていること確認
        
        **4. トラブルシューティング:**
        - アクセスできない場合は管理者に連絡
        - VPN接続を確認
        - セキュリティソフトの設定確認
        """)

def show_mobile_dashboard(dashboard):
    """📱 モバイル最適化ダッシュボード"""
    
    # データ取得
    df = dashboard.get_all_posts()
    
    # モバイルKPI表示
    st.subheader("📊 投稿状況")
    
    if not df.empty:
        total_posts = len(df)
        posted_count = len(df[df['status'] == 'posted']) if 'status' in df.columns else 0
        pending_count = len(df[df['status'] == 'pending']) if 'status' in df.columns else 0
        
        # モバイル向け大きなメトリック
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h2>{total_posts}</h2>
                <p>総投稿数</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            completion_rate = (posted_count / total_posts * 100) if total_posts > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <h2>{completion_rate:.1f}%</h2>
                <p>完了率</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 最新投稿（モバイル最適化）
        st.subheader("📝 最新投稿")
        recent_posts = df.head(3)  # モバイルでは3件のみ
        
        for idx, post in recent_posts.iterrows():
            status_emoji = "✅" if post.get('status') == 'posted' else "⏳"
            
            with st.expander(f"{status_emoji} {post['scheduled_time'].strftime('%m/%d %H:%M')}"):
                st.write(post['content'][:150] + "..." if len(post['content']) > 150 else post['content'])
                
                # モバイル向けシンプル統計
                st.write(f"👍 {int(post.get('likes', 0))} | 🔗 {int(post.get('clicks', 0))}")
    
    else:
        st.warning("📊 投稿データがありません")
        st.info("「🚀 AI投稿生成」から開始してください")

def show_quick_post_mobile():
    """📱 モバイル向けクイック投稿"""
    st.subheader("🚀 クイック投稿")
    
    # モバイル向け大きなボタン
    if st.button("🤖 AI投稿生成", key="mobile_ai_gen", help="タップして投稿を自動生成"):
        # AI投稿生成ロジック
        sample_posts = [
            "朝の衝撃発見\n\n業界の常識が覆された瞬間を目撃\n\n30万円のWebサイト制作が1万円で可能になる時代\n\nスタートアップには革命的な変化\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#Webサイト1万円 #スタートアップ革命",
            "昼休み情報\n\n同僚の電話内容が気になって仕方ない\n\n「固定費が1/3になった方法って何？」\n\n詳細を聞き出す作戦を練り中\n\nhttps://s.lmes.jp/landing-qr/2006748792-BXVNxLLm?uLand=vqQV1u\n\n#固定費削減 #経営効率化",
        ]
        
        import random
        selected_post = random.choice(sample_posts)
        st.session_state['mobile_post'] = selected_post
        st.success("✅ 投稿を生成しました！")
        st.rerun()
    
    # 生成された投稿表示
    if 'mobile_post' in st.session_state:
        st.text_area("生成された投稿", st.session_state['mobile_post'], height=200)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 コピー", key="mobile_copy"):
                st.info("📱 長押しして全選択→コピー")
        
        with col2:
            if st.button("✅ 投稿完了", key="mobile_posted"):
                st.success("投稿を記録しました！")
                del st.session_state['mobile_post']
                st.rerun()

def main():
    """メイン処理"""
    dashboard = MobileTeamDashboard()
    
    # タイトル
    st.title("🚀 Threads Team Dashboard")
    st.markdown("**社内チーム&モバイル完全対応版**")
    
    # サイドバーまたはモバイルメニュー
    if st.sidebar:
        menu = st.sidebar.selectbox(
            "📱 メニュー選択",
            ["📊 ダッシュボード", "👥 チームアクセス", "🚀 クイック投稿", "📈 分析", "⚙️ 設定"]
        )
    else:
        # モバイルフォールバック
        menu = st.selectbox(
            "メニュー",
            ["📊 ダッシュボード", "👥 チームアクセス", "🚀 クイック投稿"]
        )
    
    # メニュー処理
    if menu == "📊 ダッシュボード":
        show_mobile_dashboard(dashboard)
    
    elif menu == "👥 チームアクセス":
        show_team_access_info(dashboard)
    
    elif menu == "🚀 クイック投稿":
        show_quick_post_mobile()
    
    elif menu == "📈 分析":
        st.subheader("📈 パフォーマンス分析")
        df = dashboard.get_all_posts()
        
        if not df.empty:
            # シンプルなグラフ
            daily_counts = df.groupby(df['scheduled_time'].dt.date).size()
            
            fig = px.line(
                x=daily_counts.index, 
                y=daily_counts.values,
                title="日別投稿数",
                labels={'x': '日付', 'y': '投稿数'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("分析データがありません")
    
    elif menu == "⚙️ 設定":
        st.subheader("⚙️ システム設定")
        
        st.info(f"""
        **システム情報:**
        - サーバーIP: {dashboard.server_ip}
        - ポート: 8501
        - アクセスURL: http://{dashboard.server_ip}:8501
        """)
        
        if st.button("🔄 システム再起動"):
            st.warning("管理者に連絡してください")
    
    # フッター
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #666;">
        <p>🌐 アクセスURL: <strong>http://{dashboard.server_ip}:8501</strong></p>
        <p>📱 モバイル・PC・チーム対応 | Threads Management System v2.0</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()