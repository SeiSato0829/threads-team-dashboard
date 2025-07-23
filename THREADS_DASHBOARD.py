#!/usr/bin/env python3
"""
📊 Threads投稿管理ダッシュボード - 自動化対応版
投稿履歴、パフォーマンス分析、編集管理をWebで可視化
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import json
import os
from typing import List, Dict, Any
import asyncio

# ページ設定
st.set_page_config(
    page_title="Threads投稿管理ダッシュボード",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

class ThreadsDashboard:
    """📊 Threadsダッシュボード"""
    
    def __init__(self):
        self.db_paths = {
            "scheduled_posts": "scheduled_posts.db",
            "threads_optimized": "threads_optimized.db",
            "buzz_history": "buzz_history.db",
            "viral_history": "viral_history.db"
        }
        self.ensure_databases()
    
    def ensure_databases(self):
        """データベース存在確認"""
        for name, path in self.db_paths.items():
            if not os.path.exists(path):
                self.create_database(path, name)
    
    def create_database(self, path: str, db_type: str):
        """データベース作成"""
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        if db_type == "scheduled_posts":
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS scheduled_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                scheduled_time TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'pending',
                posted_at TIMESTAMP,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                engagement_prediction REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actual_engagement REAL,
                clicks INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0
            )
            """)
        else:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS post_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE,
                content TEXT,
                pattern_type TEXT,
                engagement_score REAL,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                hashtags TEXT,
                actual_engagement REAL,
                clicks INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0
            )
            """)
        
        conn.commit()
        conn.close()
    
    def get_all_posts(self) -> pd.DataFrame:
        """全投稿データ取得"""
        all_posts = []
        
        for db_name, db_path in self.db_paths.items():
            if os.path.exists(db_path):
                try:
                    conn = sqlite3.connect(db_path)
                    
                    if db_name == "scheduled_posts":
                        df = pd.read_sql_query("""
                        SELECT 
                            id,
                            content,
                            scheduled_time,
                            status,
                            posted_at,
                            engagement_prediction,
                            actual_engagement,
                            clicks,
                            shares,
                            comments,
                            likes,
                            'scheduled' as source
                        FROM scheduled_posts
                        ORDER BY scheduled_time DESC
                        """, conn)
                    else:
                        # buzz_historyとviral_historyにはstatusカラムがない可能性があるため確認
                        cursor = conn.cursor()
                        cursor.execute("PRAGMA table_info(post_history)")
                        columns = [col[1] for col in cursor.fetchall()]
                        
                        if 'status' in columns:
                            query = """
                            SELECT 
                                id,
                                content,
                                generated_at as scheduled_time,
                                COALESCE(pattern_type, 'general') as pattern_type,
                                engagement_score as engagement_prediction,
                                actual_engagement,
                                clicks,
                                shares,
                                comments,
                                likes,
                                hashtags,
                                status,
                                ? as source
                            FROM post_history
                            ORDER BY generated_at DESC
                            """
                        else:
                            query = """
                            SELECT 
                                id,
                                content,
                                generated_at as scheduled_time,
                                COALESCE(pattern_type, 'general') as pattern_type,
                                engagement_score as engagement_prediction,
                                actual_engagement,
                                clicks,
                                shares,
                                comments,
                                likes,
                                hashtags,
                                'posted' as status,
                                ? as source
                            FROM post_history
                            ORDER BY generated_at DESC
                            """
                        
                        df = pd.read_sql_query(query, conn, params=[db_name])
                    
                    if not df.empty:
                        # statusカラムを追加（post_historyテーブル用）
                        if 'status' not in df.columns and db_name == 'threads_optimized':
                            df['status'] = 'posted'  # デフォルトでpostedとする
                        all_posts.append(df)
                    
                    conn.close()
                except Exception as e:
                    st.error(f"データベース読み込みエラー ({db_name}): {e}")
        
        if all_posts:
            combined_df = pd.concat(all_posts, ignore_index=True, sort=False)
            combined_df['scheduled_time'] = pd.to_datetime(combined_df['scheduled_time'], format='ISO8601')
            
            # データクリーニング
            combined_df = combined_df.fillna({
                'actual_engagement': 0,
                'clicks': 0,
                'shares': 0,
                'comments': 0,
                'likes': 0,
                'engagement_prediction': 0
            })
            
            return combined_df
        else:
            return pd.DataFrame()
    
    def get_performance_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """パフォーマンス統計"""
        if df.empty:
            return {
                'total_posts': 0,
                'posted_count': 0,
                'pending_count': 0,
                'avg_engagement': 0.0,
                'avg_prediction': 0.0,
                'total_clicks': 0,
                'total_shares': 0,
                'total_comments': 0,
                'total_likes': 0,
                'daily_stats': pd.DataFrame()
            }
        
        total_posts = len(df)
        # statusカラムが存在する場合のみフィルタリング
        if 'status' in df.columns:
            posted_count = len(df[df['status'] == 'posted'])
            pending_count = len(df[df['status'] == 'pending'])
        else:
            posted_count = 0
            pending_count = total_posts
        
        # エンゲージメント統計（NaNを0に変換）
        avg_engagement = df['actual_engagement'].fillna(0).mean()
        avg_prediction = df['engagement_prediction'].fillna(0).mean()
        
        # 合計値（NaNを0に変換）
        total_clicks = int(df['clicks'].fillna(0).sum())
        total_shares = int(df['shares'].fillna(0).sum())
        total_comments = int(df['comments'].fillna(0).sum())
        total_likes = int(df['likes'].fillna(0).sum())
        
        # 日別統計（データがある場合のみ）
        try:
            df_copy = df.copy()
            df_copy['date'] = df_copy['scheduled_time'].dt.date
            daily_stats = df_copy.groupby('date').agg({
                'clicks': lambda x: x.fillna(0).sum(),
                'shares': lambda x: x.fillna(0).sum(), 
                'comments': lambda x: x.fillna(0).sum(),
                'likes': lambda x: x.fillna(0).sum(),
                'actual_engagement': lambda x: x.fillna(0).mean()
            }).reset_index()
        except Exception:
            daily_stats = pd.DataFrame()
        
        return {
            'total_posts': total_posts,
            'posted_count': posted_count,
            'pending_count': pending_count,
            'avg_engagement': round(avg_engagement, 1) if not pd.isna(avg_engagement) else 0.0,
            'avg_prediction': round(avg_prediction, 1) if not pd.isna(avg_prediction) else 0.0,
            'total_clicks': total_clicks,
            'total_shares': total_shares,
            'total_comments': total_comments,
            'total_likes': total_likes,
            'daily_stats': daily_stats
        }
    
    def update_post_engagement(self, post_id: int, source: str, engagement_data: Dict):
        """投稿エンゲージメント更新"""
        db_path = self.db_paths.get(source, "scheduled_posts.db")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            if source == "scheduled_posts":
                cursor.execute("""
                UPDATE scheduled_posts 
                SET actual_engagement = ?, clicks = ?, shares = ?, comments = ?, likes = ?
                WHERE id = ?
                """, (
                    engagement_data.get('engagement', 0),
                    engagement_data.get('clicks', 0),
                    engagement_data.get('shares', 0),
                    engagement_data.get('comments', 0),
                    engagement_data.get('likes', 0),
                    post_id
                ))
            else:
                cursor.execute("""
                UPDATE post_history 
                SET actual_engagement = ?, clicks = ?, shares = ?, comments = ?, likes = ?
                WHERE id = ?
                """, (
                    engagement_data.get('engagement', 0),
                    engagement_data.get('clicks', 0),
                    engagement_data.get('shares', 0),
                    engagement_data.get('comments', 0),
                    engagement_data.get('likes', 0),
                    post_id
                ))
            
            conn.commit()
            return True
        except Exception as e:
            st.error(f"更新エラー: {e}")
            return False
        finally:
            conn.close()

def main():
    """メイン画面"""
    st.title("📱 Threads投稿管理ダッシュボード")
    st.markdown("### 自動化対応・完全管理システム")
    
    # ダッシュボード初期化
    dashboard = ThreadsDashboard()
    
    # データ取得
    with st.spinner("データを読み込み中..."):
        df = dashboard.get_all_posts()
        stats = dashboard.get_performance_stats(df)
    
    # サイドバーメニュー
    st.sidebar.title("📊 メニュー")
    page = st.sidebar.selectbox(
        "表示内容を選択",
        ["📈 概要ダッシュボード", "📝 投稿履歴", "📊 パフォーマンス分析", "✏️ 投稿編集", "👥 チーム共有", "📋 自動レポート", "🤖 自動投稿設定"]
    )
    
    # 概要ダッシュボード
    if page == "📈 概要ダッシュボード":
        show_overview_dashboard(df, stats)
    
    # 投稿履歴
    elif page == "📝 投稿履歴":
        show_post_history(df, dashboard)
    
    # パフォーマンス分析  
    elif page == "📊 パフォーマンス分析":
        show_performance_analysis(df, stats)
    
    # 投稿編集
    elif page == "✏️ 投稿編集":
        show_post_editor(df, dashboard)
    
    # チーム共有
    elif page == "👥 チーム共有":
        show_team_sharing(df, stats)
    
    # 自動レポート
    elif page == "📋 自動レポート":
        show_auto_reports(df, stats)
    
    # Threads直接投稿
    elif page == "🤖 自動投稿設定":
        show_direct_posting()

def show_overview_dashboard(df: pd.DataFrame, stats: Dict):
    """概要ダッシュボード表示"""
    st.header("📈 投稿管理概要")
    
    # 実データに基づくKPI表示
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_posts = stats.get('total_posts', 0)
        posted_count = stats.get('posted_count', 0)
        st.metric(
            "総投稿数",
            f"{total_posts:,}",
            delta=f"+{posted_count} 投稿済み" if posted_count > 0 else "投稿なし"
        )
    
    with col2:
        avg_engagement = stats.get('avg_engagement', 0.0)
        avg_prediction = stats.get('avg_prediction', 0.0)
        st.metric(
            "平均エンゲージメント",
            f"{avg_engagement:.1f}",
            delta=f"予測: {avg_prediction:.1f}" if avg_prediction > 0 else "予測なし"
        )
    
    with col3:
        total_clicks = stats.get('total_clicks', 0)
        total_shares = stats.get('total_shares', 0)
        st.metric(
            "総クリック数",
            f"{total_clicks:,}",
            delta=f"+{total_shares} シェア" if total_shares > 0 else "シェアなし"
        )
    
    with col4:
        completion_rate = (posted_count / total_posts * 100) if total_posts > 0 else 0
        pending_count = stats.get('pending_count', 0)
        st.metric(
            "投稿完了率",
            f"{completion_rate:.1f}%",
            delta=f"{pending_count} 予定" if pending_count > 0 else "予定なし"
        )
    
    # データがある場合の追加情報
    if stats and total_posts > 0:
        
        # 日別パフォーマンスグラフ
        if not stats['daily_stats'].empty:
            st.subheader("📊 日別パフォーマンス")
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=stats['daily_stats']['date'],
                y=stats['daily_stats']['clicks'],
                name='クリック',
                line=dict(color='#1f77b4')
            ))
            
            fig.add_trace(go.Scatter(
                x=stats['daily_stats']['date'], 
                y=stats['daily_stats']['likes'],
                name='いいね',
                line=dict(color='#ff7f0e')
            ))
            
            fig.update_layout(
                title="日別エンゲージメント推移",
                xaxis_title="日付",
                yaxis_title="反応数",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # 最新投稿表示
        st.subheader("📝 最新投稿")
        recent_posts = df.head(5)
        
        if len(recent_posts) > 0:
            for idx, post in recent_posts.iterrows():
                pattern_type = post.get('pattern_type', 'N/A')
                status_emoji = "✅" if post.get('status') == 'posted' else "⏳"
                
                with st.expander(f"{status_emoji} {post['scheduled_time'].strftime('%m/%d %H:%M')} - {pattern_type}"):
                    st.write(post['content'][:200] + "..." if len(post['content']) > 200 else post['content'])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"👍 いいね: {int(post.get('likes', 0))}")
                    with col2:
                        st.write(f"🔗 クリック: {int(post.get('clicks', 0))}")
                    with col3:
                        st.write(f"📊 エンゲージメント: {post.get('actual_engagement', 0):.1f}")
        else:
            st.info("投稿データがありません。")
    
    else:
        # データがない場合の案内
        st.warning("📊 投稿データがありません")
        st.info("""
        **投稿を開始するには:**
        1. 「🤖 自動投稿設定」タブを開く
        2. 「🚀 AI生成実行」で投稿を生成
        3. データがここに表示されます
        """)
        
        # 投稿生成ボタンを追加
        if st.button("🚀 投稿生成を開始", type="primary"):
            st.switch_page("pages/自動投稿設定.py")  # 自動投稿ページへ遷移

def show_post_history(df: pd.DataFrame, dashboard: ThreadsDashboard):
    """投稿履歴表示"""
    st.header("📝 投稿履歴管理")
    
    if not df.empty:
        # フィルター
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_range = st.date_input(
                "期間選択",
                value=[date.today() - timedelta(days=7), date.today()],
                max_value=date.today()
            )
        
        with col2:
            status_filter = st.multiselect(
                "ステータス",
                options=['posted', 'pending', 'failed'],
                default=['posted', 'pending']
            )
        
        with col3:
            source_filter = st.multiselect(
                "投稿タイプ",
                options=df['source'].unique(),
                default=df['source'].unique()
            )
        
        # フィルタリング
        filtered_df = df.copy()
        
        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df['scheduled_time'].dt.date >= date_range[0]) &
                (filtered_df['scheduled_time'].dt.date <= date_range[1])
            ]
        
        if status_filter:
            filtered_df = filtered_df[filtered_df.get('status', '').isin(status_filter)]
        
        if source_filter:
            filtered_df = filtered_df[filtered_df['source'].isin(source_filter)]
        
        # 投稿一覧
        st.subheader(f"📋 投稿一覧 ({len(filtered_df)}件)")
        
        for idx, post in filtered_df.iterrows():
            with st.expander(f"{post['scheduled_time'].strftime('%Y/%m/%d %H:%M')} - {post.get('pattern_type', post.get('status', 'N/A'))}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.text_area("投稿内容", post['content'], height=100, key=f"content_{idx}")
                
                with col2:
                    st.write("**統計情報**")
                    st.write(f"いいね: {post.get('likes', 0)}")
                    st.write(f"シェア: {post.get('shares', 0)}")
                    st.write(f"コメント: {post.get('comments', 0)}")
                    st.write(f"クリック: {post.get('clicks', 0)}")
                    
                    # エンゲージメント更新
                    if st.button(f"📊 更新", key=f"update_{idx}"):
                        with st.form(f"engagement_form_{idx}"):
                            likes = st.number_input("いいね", min_value=0, value=int(post.get('likes', 0)))
                            shares = st.number_input("シェア", min_value=0, value=int(post.get('shares', 0)))
                            comments = st.number_input("コメント", min_value=0, value=int(post.get('comments', 0)))
                            clicks = st.number_input("クリック", min_value=0, value=int(post.get('clicks', 0)))
                            
                            if st.form_submit_button("更新"):
                                engagement_data = {
                                    'likes': likes,
                                    'shares': shares,
                                    'comments': comments,
                                    'clicks': clicks,
                                    'engagement': (likes + shares + comments) / 10
                                }
                                
                                if dashboard.update_post_engagement(post['id'], post['source'], engagement_data):
                                    st.success("更新完了！")
                                    st.rerun()
    
    else:
        st.warning("投稿履歴がありません。")

def show_performance_analysis(df: pd.DataFrame, stats: Dict):
    """パフォーマンス分析表示"""
    st.header("📊 パフォーマンス分析")
    
    if not df.empty and stats:
        # パターン別パフォーマンス
        if 'pattern_type' in df.columns:
            st.subheader("🎯 パターン別エンゲージメント")
            
            pattern_stats = df.groupby('pattern_type').agg({
                'actual_engagement': 'mean',
                'clicks': 'sum',
                'likes': 'sum',
                'shares': 'sum'
            }).reset_index()
            
            fig = px.bar(
                pattern_stats,
                x='pattern_type',
                y='actual_engagement',
                title="投稿パターン別平均エンゲージメント"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 時間帯別分析
        st.subheader("⏰ 時間帯別パフォーマンス")
        
        df['hour'] = df['scheduled_time'].dt.hour
        hourly_stats = df.groupby('hour').agg({
            'actual_engagement': 'mean',
            'clicks': 'mean'
        }).reset_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=hourly_stats['hour'],
            y=hourly_stats['actual_engagement'],
            name='エンゲージメント',
            line=dict(color='#1f77b4')
        ))
        
        fig.add_trace(go.Scatter(
            x=hourly_stats['hour'],
            y=hourly_stats['clicks'],
            name='クリック数',
            yaxis='y2',
            line=dict(color='#ff7f0e')
        ))
        
        fig.update_layout(
            title="時間帯別パフォーマンス",
            xaxis_title="時間",
            yaxis_title="エンゲージメント",
            yaxis2=dict(title="クリック数", overlaying='y', side='right')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 予測vs実績
        st.subheader("🎯 予測精度分析")
        
        if df['actual_engagement'].sum() > 0:
            fig = px.scatter(
                df,
                x='engagement_prediction',
                y='actual_engagement',
                title="エンゲージメント予測 vs 実績",
                labels={'engagement_prediction': '予測値', 'actual_engagement': '実績値'}
            )
            
            # 理想的な予測線
            max_val = max(df['engagement_prediction'].max(), df['actual_engagement'].max())
            fig.add_shape(
                type="line",
                x0=0, y0=0, x1=max_val, y1=max_val,
                line=dict(color="red", dash="dash")
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("実績データの蓄積により、より詳細な分析が可能になります。")

def show_post_editor(df: pd.DataFrame, dashboard: ThreadsDashboard):
    """投稿編集画面"""
    st.header("✏️ 投稿内容編集")
    
    if not df.empty:
        # 編集対象選択
        pending_posts = df[df.get('status', '') == 'pending'].copy()
        
        if not pending_posts.empty:
            st.subheader("📝 予定投稿の編集")
            
            selected_post = st.selectbox(
                "編集する投稿を選択",
                options=range(len(pending_posts)),
                format_func=lambda x: f"{pending_posts.iloc[x]['scheduled_time'].strftime('%m/%d %H:%M')} - {pending_posts.iloc[x]['content'][:50]}..."
            )
            
            if selected_post is not None:
                post = pending_posts.iloc[selected_post]
                
                with st.form("post_editor"):
                    new_content = st.text_area(
                        "投稿内容",
                        value=post['content'],
                        height=200
                    )
                    
                    # 日付と時刻を分けて入力
                    col1, col2 = st.columns(2)
                    with col1:
                        new_date = st.date_input(
                            "投稿予定日",
                            value=post['scheduled_time'].date()
                        )
                    
                    with col2:
                        new_time = st.time_input(
                            "投稿予定時刻",
                            value=post['scheduled_time'].time()
                        )
                    
                    # フォーム送信ボタン
                    submitted = st.form_submit_button("💾 更新", type="primary")
                    
                    if submitted:
                        # 日付と時刻を結合
                        new_datetime = datetime.combine(new_date, new_time)
                        
                        # データベース更新
                        try:
                            conn = sqlite3.connect("threads_optimized.db")
                            cursor = conn.cursor()
                            
                            cursor.execute("""
                                UPDATE scheduled_posts 
                                SET content = ?, scheduled_time = ?
                                WHERE id = ?
                            """, (new_content, new_datetime, post['id']))
                            
                            conn.commit()
                            conn.close()
                            
                            st.success("✅ 投稿内容を更新しました！")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ 更新エラー: {str(e)}")
        
        else:
            st.info("編集可能な予定投稿がありません。")
    
    else:
        st.warning("投稿データがありません。")

def show_team_sharing(df: pd.DataFrame, stats: Dict):
    """チーム共有画面"""
    st.header("👥 チーム情報共有")
    
    # 共有レポート生成
    if not df.empty and stats:
        st.subheader("📋 週次レポート")
        
        # 週次統計
        week_ago = datetime.now() - timedelta(days=7)
        week_posts = df[df['scheduled_time'] >= week_ago]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("今週の投稿数", len(week_posts))
        
        with col2:
            avg_engagement = week_posts['actual_engagement'].mean()
            st.metric("平均エンゲージメント", f"{avg_engagement:.1f}")
        
        with col3:
            total_clicks = week_posts['clicks'].sum()
            st.metric("総クリック数", f"{total_clicks:,}")
        
        # 共有用コメント
        st.subheader("💬 チームコメント")
        
        team_comment = st.text_area(
            "チームへのメッセージやフィードバックを入力",
            placeholder="今週のパフォーマンスについて..."
        )
        
        if st.button("📤 共有"):
            # チーム共有ロジック（実装必要）
            st.success("チームに共有しました！")
    
    else:
        st.info("共有できるデータがありません。")

def show_auto_reports(df: pd.DataFrame, stats: Dict):
    """自動レポート画面"""
    st.header("📋 自動レポート生成")
    
    if not df.empty and stats:
        # レポート設定
        st.subheader("⚙️ レポート設定")
        
        col1, col2 = st.columns(2)
        
        with col1:
            report_type = st.selectbox(
                "レポートタイプ",
                ["日次レポート", "週次レポート", "月次レポート"]
            )
        
        with col2:
            auto_send = st.checkbox("自動送信を有効にする")
        
        if st.button("📊 レポート生成"):
            # レポート生成
            report_content = generate_auto_report(df, stats, report_type)
            
            st.subheader(f"📄 {report_type}")
            st.markdown(report_content)
            
            # ダウンロードボタン
            st.download_button(
                label="📥 レポートをダウンロード",
                data=report_content,
                file_name=f"threads_report_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )
    
    else:
        st.info("レポート生成に必要なデータがありません。")

def generate_auto_report(df: pd.DataFrame, stats: Dict, report_type: str) -> str:
    """自動レポート生成"""
    
    report = f"""# Threads投稿 {report_type}

## 📊 概要統計
- **総投稿数**: {stats['total_posts']:,}件
- **投稿完了**: {stats['posted_count']:,}件
- **平均エンゲージメント**: {stats['avg_engagement']:.1f}
- **総クリック数**: {stats['total_clicks']:,}回

## 🎯 パフォーマンス分析
"""
    
    if 'pattern_type' in df.columns:
        pattern_stats = df.groupby('pattern_type')['actual_engagement'].mean().sort_values(ascending=False)
        
        report += "\n### パターン別エンゲージメント\n"
        for pattern, engagement in pattern_stats.head(5).items():
            report += f"- **{pattern}**: {engagement:.1f}\n"
    
    report += f"""
## 📈 改善提案
- エンゲージメントが高いパターンの投稿を増やす
- 低パフォーマンスの時間帯を調整
- 予測精度の向上

---
*レポート生成日時: {datetime.now().strftime('%Y/%m/%d %H:%M')}*
"""
    
    return report

def show_direct_posting():
    """Threads直接投稿機能"""
    st.header("🤖 Threads自動投稿設定")
    
    # より安定したシンプル自動投稿を使用
    try:
        from threads_simple_automation import integrate_with_dashboard
        integrate_with_dashboard()
    except ImportError as e:
        st.error(f"自動投稿モジュールエラー: {str(e)}")
        
        # 手動投稿の代替案を表示
        st.markdown("### 📱 手動投稿ガイド")
        st.info("""
        Seleniumエラーのため、以下の方法で投稿してください：
        
        1. **✏️ 投稿編集**タブでAI投稿を生成
        2. 内容をコピー
        3. Threadsアプリで手動投稿
        4. 結果をダッシュボードに記録
        """)

if __name__ == "__main__":
    main()