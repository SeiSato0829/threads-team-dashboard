#!/usr/bin/env python3
"""
📊 修正版 Threads投稿管理ダッシュボード
データベース構造統一版
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

# ページ設定
st.set_page_config(
    page_title="Threads投稿管理ダッシュボード",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

class FixedThreadsDashboard:
    """📊 修正版Threadsダッシュボード"""
    
    def __init__(self):
        self.db_paths = {
            "scheduled_posts": "scheduled_posts.db",
            "threads_optimized": "threads_optimized.db",
            "buzz_history": "buzz_history.db",
            "viral_history": "viral_history.db"
        }
    
    def get_all_posts(self) -> pd.DataFrame:
        """全投稿データ取得（エラー対応版）"""
        all_posts = []
        
        for db_name, db_path in self.db_paths.items():
            if os.path.exists(db_path):
                try:
                    conn = sqlite3.connect(db_path)
                    
                    # まずテーブル構造を確認
                    tables_info = pd.read_sql_query(
                        "SELECT name FROM sqlite_master WHERE type='table'",
                        conn
                    )
                    
                    if tables_info.empty:
                        conn.close()
                        continue
                    
                    # 各データベースに応じたクエリ
                    if db_name == "scheduled_posts":
                        # scheduled_postsテーブル
                        df = self._get_scheduled_posts(conn)
                        
                    elif db_name == "threads_optimized": 
                        # threads_postsテーブル
                        df = self._get_threads_posts(conn)
                        
                    elif db_name == "buzz_history":
                        # buzz_historyテーブル
                        df = self._get_buzz_posts(conn)
                        
                    elif db_name == "viral_history":
                        # post_historyテーブル
                        df = self._get_viral_posts(conn)
                    
                    if not df.empty:
                        df['source'] = db_name
                        all_posts.append(df)
                    
                    conn.close()
                    
                except Exception as e:
                    st.error(f"データベース読み込みエラー ({db_name}): {e}")
                    continue
        
        if all_posts:
            combined_df = pd.concat(all_posts, ignore_index=True, sort=False)
            combined_df['scheduled_time'] = pd.to_datetime(combined_df['scheduled_time'])
            
            # データクリーニング
            combined_df = combined_df.fillna({
                'actual_engagement': 0,
                'clicks': 0,
                'shares': 0,
                'comments': 0,
                'likes': 0,
                'engagement_prediction': 0,
                'pattern_type': 'unknown',
                'status': 'unknown'
            })
            
            return combined_df
        else:
            return pd.DataFrame()
    
    def _get_scheduled_posts(self, conn) -> pd.DataFrame:
        """scheduled_posts取得"""
        try:
            # カラム存在確認
            columns_info = pd.read_sql_query("PRAGMA table_info(scheduled_posts)", conn)
            available_columns = columns_info['name'].tolist()
            
            # 基本カラム
            select_columns = ['id', 'content']
            
            # オプショナルカラム
            optional_columns = {
                'scheduled_time': 'scheduled_time',
                'status': 'status', 
                'engagement_prediction': 'engagement_prediction',
                'actual_engagement': 'actual_engagement',
                'clicks': 'clicks',
                'shares': 'shares',
                'comments': 'comments', 
                'likes': 'likes',
                'pattern_type': 'pattern_type',
                'hashtags': 'hashtags'
            }
            
            for col, alias in optional_columns.items():
                if col in available_columns:
                    select_columns.append(f"{col} as {alias}")
                else:
                    select_columns.append(f"NULL as {alias}")
            
            query = f"""
            SELECT {', '.join(select_columns)}
            FROM scheduled_posts
            ORDER BY COALESCE(scheduled_time, datetime('now')) DESC
            LIMIT 100
            """
            
            return pd.read_sql_query(query, conn)
            
        except Exception as e:
            st.warning(f"scheduled_posts読み込み警告: {e}")
            return pd.DataFrame()
    
    def _get_threads_posts(self, conn) -> pd.DataFrame:
        """threads_posts取得"""
        try:
            columns_info = pd.read_sql_query("PRAGMA table_info(threads_posts)", conn)
            if columns_info.empty:
                return pd.DataFrame()
            
            available_columns = columns_info['name'].tolist()
            
            select_columns = ['id', 'content']
            
            optional_columns = {
                'generated_at': 'scheduled_time',
                'pattern_type': 'pattern_type',
                'engagement_score': 'engagement_prediction',
                'actual_engagement': 'actual_engagement',
                'clicks': 'clicks',
                'shares': 'shares',
                'comments': 'comments',
                'likes': 'likes',
                'hashtags': 'hashtags',
                'status': 'status'
            }
            
            for col, alias in optional_columns.items():
                if col in available_columns:
                    select_columns.append(f"{col} as {alias}")
                else:
                    select_columns.append(f"NULL as {alias}")
            
            query = f"""
            SELECT {', '.join(select_columns)}
            FROM threads_posts
            ORDER BY COALESCE(generated_at, datetime('now')) DESC
            LIMIT 100
            """
            
            return pd.read_sql_query(query, conn)
            
        except Exception as e:
            st.warning(f"threads_posts読み込み警告: {e}")
            return pd.DataFrame()
    
    def _get_buzz_posts(self, conn) -> pd.DataFrame:
        """buzz_history取得"""
        try:
            columns_info = pd.read_sql_query("PRAGMA table_info(buzz_history)", conn)
            if columns_info.empty:
                return pd.DataFrame()
            
            available_columns = columns_info['name'].tolist()
            
            select_columns = ['id', 'content']
            
            optional_columns = {
                'generated_at': 'scheduled_time',
                'pattern_type': 'pattern_type',
                'engagement_score': 'engagement_prediction',
                'actual_engagement': 'actual_engagement',
                'clicks': 'clicks',
                'shares': 'shares',
                'comments': 'comments',
                'likes': 'likes',
                'hashtag': 'hashtags',
                'status': 'status'
            }
            
            for col, alias in optional_columns.items():
                if col in available_columns:
                    select_columns.append(f"{col} as {alias}")
                else:
                    select_columns.append(f"NULL as {alias}")
            
            query = f"""
            SELECT {', '.join(select_columns)}
            FROM buzz_history
            ORDER BY COALESCE(generated_at, datetime('now')) DESC
            LIMIT 100
            """
            
            return pd.read_sql_query(query, conn)
            
        except Exception as e:
            st.warning(f"buzz_history読み込み警告: {e}")
            return pd.DataFrame()
    
    def _get_viral_posts(self, conn) -> pd.DataFrame:
        """post_history取得"""
        try:
            # テーブル存在確認
            tables = pd.read_sql_query(
                "SELECT name FROM sqlite_master WHERE type='table'",
                conn
            )['name'].tolist()
            
            if 'post_history' not in tables:
                return pd.DataFrame()
            
            columns_info = pd.read_sql_query("PRAGMA table_info(post_history)", conn)
            available_columns = columns_info['name'].tolist()
            
            select_columns = ['id', 'content']
            
            optional_columns = {
                'generated_at': 'scheduled_time',
                'pattern_type': 'pattern_type',
                'engagement_score': 'engagement_prediction',
                'actual_engagement': 'actual_engagement',
                'clicks': 'clicks',
                'shares': 'shares',
                'comments': 'comments',
                'likes': 'likes',
                'hashtags': 'hashtags',
                'status': 'status'
            }
            
            for col, alias in optional_columns.items():
                if col in available_columns:
                    select_columns.append(f"{col} as {alias}")
                else:
                    # デフォルト値設定
                    if alias == 'pattern_type':
                        select_columns.append("'viral' as pattern_type")
                    else:
                        select_columns.append(f"NULL as {alias}")
            
            query = f"""
            SELECT {', '.join(select_columns)}
            FROM post_history
            ORDER BY COALESCE(generated_at, datetime('now')) DESC
            LIMIT 100
            """
            
            return pd.read_sql_query(query, conn)
            
        except Exception as e:
            st.warning(f"post_history読み込み警告: {e}")
            return pd.DataFrame()
    
    def get_performance_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """パフォーマンス統計（安全版）"""
        if df.empty:
            return {
                'total_posts': 0,
                'posted_count': 0,
                'pending_count': 0,
                'avg_engagement': 0,
                'avg_prediction': 0,
                'total_clicks': 0,
                'total_shares': 0,
                'total_comments': 0,
                'total_likes': 0,
                'daily_stats': pd.DataFrame()
            }
        
        total_posts = len(df)
        posted_count = len(df[df.get('status', '').fillna('') == 'posted'])
        pending_count = len(df[df.get('status', '').fillna('') == 'pending'])
        
        # エンゲージメント統計（NaN対応）
        df_clean = df.fillna(0)
        avg_engagement = df_clean['actual_engagement'].mean()
        avg_prediction = df_clean['engagement_prediction'].mean()
        
        total_clicks = df_clean['clicks'].sum()
        total_shares = df_clean['shares'].sum()
        total_comments = df_clean['comments'].sum()
        total_likes = df_clean['likes'].sum()
        
        # 日別統計
        if 'scheduled_time' in df.columns:
            df['date'] = df['scheduled_time'].dt.date
            daily_stats = df.groupby('date').agg({
                'clicks': lambda x: x.fillna(0).sum(),
                'shares': lambda x: x.fillna(0).sum(),
                'comments': lambda x: x.fillna(0).sum(),
                'likes': lambda x: x.fillna(0).sum(),
                'actual_engagement': lambda x: x.fillna(0).mean()
            }).reset_index()
        else:
            daily_stats = pd.DataFrame()
        
        return {
            'total_posts': total_posts,
            'posted_count': posted_count,
            'pending_count': pending_count,
            'avg_engagement': avg_engagement if pd.notna(avg_engagement) else 0,
            'avg_prediction': avg_prediction if pd.notna(avg_prediction) else 0,
            'total_clicks': int(total_clicks) if pd.notna(total_clicks) else 0,
            'total_shares': int(total_shares) if pd.notna(total_shares) else 0,
            'total_comments': int(total_comments) if pd.notna(total_comments) else 0,
            'total_likes': int(total_likes) if pd.notna(total_likes) else 0,
            'daily_stats': daily_stats
        }

def main():
    """メイン画面"""
    st.title("📱 Threads投稿管理ダッシュボード")
    st.markdown("### 修正版・エラー対応済み")
    
    # ダッシュボード初期化
    dashboard = FixedThreadsDashboard()
    
    # データ取得
    with st.spinner("データを読み込み中..."):
        df = dashboard.get_all_posts()
        stats = dashboard.get_performance_stats(df)
    
    # データ状況表示
    if not df.empty:
        st.success(f"✅ {len(df)}件の投稿データを読み込みました")
        
        # データソース内訳
        if 'source' in df.columns:
            source_counts = df['source'].value_counts()
            st.info(f"📊 データソース: {dict(source_counts)}")
    else:
        st.warning("⚠️ 投稿データが見つかりません")
        
        # データ作成ガイド
        st.markdown("""
        ### 📝 データを作成するには:
        1. **THREADS_ULTIMATE_START.bat** - 投稿生成
        2. **FIX_DASHBOARD.py** - データベース修正（必要に応じて）
        3. ダッシュボード再読み込み
        """)
        
        # 修正ツール実行ボタン
        if st.button("🔧 データベースを修正"):
            with st.spinner("修正中..."):
                try:
                    import subprocess
                    result = subprocess.run(['python', 'FIX_DASHBOARD.py'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        st.success("修正完了！ページを再読み込みしてください。")
                    else:
                        st.error(f"修正エラー: {result.stderr}")
                except Exception as e:
                    st.error(f"修正実行エラー: {e}")
        
        return
    
    # サイドバーメニュー
    st.sidebar.title("📊 メニュー")
    page = st.sidebar.selectbox(
        "表示内容を選択",
        ["📈 概要ダッシュボード", "📝 投稿履歴", "📊 パフォーマンス分析"]
    )
    
    # 概要ダッシュボード
    if page == "📈 概要ダッシュボード":
        show_overview_dashboard(df, stats)
    
    # 投稿履歴
    elif page == "📝 投稿履歴":
        show_post_history(df)
    
    # パフォーマンス分析
    elif page == "📊 パフォーマンス分析":
        show_performance_analysis(df, stats)

def show_overview_dashboard(df: pd.DataFrame, stats: Dict):
    """概要ダッシュボード表示"""
    st.header("📈 投稿管理概要")
    
    # KPI カード
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "総投稿数",
            f"{stats['total_posts']:,}",
            delta=f"+{stats['posted_count']} 投稿済み"
        )
    
    with col2:
        st.metric(
            "平均エンゲージメント",
            f"{stats['avg_engagement']:.1f}",
            delta=f"予測: {stats['avg_prediction']:.1f}"
        )
    
    with col3:
        st.metric(
            "総クリック数",
            f"{stats['total_clicks']:,}",
            delta=f"+{stats['total_shares']} シェア"
        )
    
    with col4:
        completion_rate = (stats['posted_count']/stats['total_posts']*100) if stats['total_posts'] > 0 else 0
        st.metric(
            "投稿完了率", 
            f"{completion_rate:.1f}%",
            delta=f"{stats['pending_count']} 予定"
        )
    
    # 最新投稿
    st.subheader("📝 最新投稿")
    recent_posts = df.head(10)
    
    for idx, post in recent_posts.iterrows():
        scheduled_time = post.get('scheduled_time', 'N/A')
        pattern_type = post.get('pattern_type', 'N/A')
        
        time_str = scheduled_time.strftime('%m/%d %H:%M') if pd.notna(scheduled_time) else 'N/A'
        
        with st.expander(f"{time_str} - {pattern_type}"):
            content = post.get('content', '')
            display_content = content[:200] + "..." if len(content) > 200 else content
            st.write(display_content)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.write(f"👍 いいね: {post.get('likes', 0)}")
            with col2:
                st.write(f"🔗 クリック: {post.get('clicks', 0)}")
            with col3:
                st.write(f"💬 コメント: {post.get('comments', 0)}")
            with col4:
                st.write(f"📊 エンゲージメント: {post.get('actual_engagement', 0):.1f}")

def show_post_history(df: pd.DataFrame):
    """投稿履歴表示"""
    st.header("📝 投稿履歴")
    
    # フィルター
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'source' in df.columns:
            source_options = ['全て'] + df['source'].unique().tolist()
            source_filter = st.selectbox("データソース", source_options)
        else:
            source_filter = '全て'
    
    with col2:
        if 'pattern_type' in df.columns:
            pattern_options = ['全て'] + df['pattern_type'].dropna().unique().tolist()
            pattern_filter = st.selectbox("投稿パターン", pattern_options)
        else:
            pattern_filter = '全て'
    
    with col3:
        if 'status' in df.columns:
            status_options = ['全て'] + df['status'].dropna().unique().tolist()
            status_filter = st.selectbox("ステータス", status_options)
        else:
            status_filter = '全て'
    
    # フィルタリング適用
    filtered_df = df.copy()
    
    if source_filter != '全て' and 'source' in df.columns:
        filtered_df = filtered_df[filtered_df['source'] == source_filter]
    
    if pattern_filter != '全て' and 'pattern_type' in df.columns:
        filtered_df = filtered_df[filtered_df['pattern_type'] == pattern_filter]
    
    if status_filter != '全て' and 'status' in df.columns:
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    st.write(f"📋 表示件数: {len(filtered_df)} / {len(df)}")
    
    # 投稿一覧表示
    for idx, post in filtered_df.head(20).iterrows():
        scheduled_time = post.get('scheduled_time', 'N/A')
        time_str = scheduled_time.strftime('%Y/%m/%d %H:%M') if pd.notna(scheduled_time) else 'N/A'
        
        pattern_type = post.get('pattern_type', 'N/A')
        source = post.get('source', 'N/A')
        
        with st.expander(f"{time_str} - {pattern_type} ({source})"):
            content = post.get('content', '')
            st.text_area("投稿内容", content, height=100, key=f"content_{idx}", disabled=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**統計情報**")
                st.write(f"いいね: {post.get('likes', 0)}")
                st.write(f"シェア: {post.get('shares', 0)}")
                st.write(f"コメント: {post.get('comments', 0)}")
                st.write(f"クリック: {post.get('clicks', 0)}")
            
            with col2:
                st.write("**メタデータ**")
                st.write(f"エンゲージメント予測: {post.get('engagement_prediction', 0):.1f}")
                st.write(f"実際のエンゲージメント: {post.get('actual_engagement', 0):.1f}")
                st.write(f"ハッシュタグ: {post.get('hashtags', 'N/A')}")
                st.write(f"ステータス: {post.get('status', 'N/A')}")

def show_performance_analysis(df: pd.DataFrame, stats: Dict):
    """パフォーマンス分析表示"""
    st.header("📊 パフォーマンス分析")
    
    # パターン別パフォーマンス
    if 'pattern_type' in df.columns and not df['pattern_type'].isna().all():
        st.subheader("🎯 パターン別エンゲージメント")
        
        pattern_stats = df.groupby('pattern_type').agg({
            'actual_engagement': lambda x: x.fillna(0).mean(),
            'clicks': lambda x: x.fillna(0).sum(),
            'likes': lambda x: x.fillna(0).sum(),
            'shares': lambda x: x.fillna(0).sum()
        }).reset_index()
        
        if not pattern_stats.empty:
            fig = px.bar(
                pattern_stats,
                x='pattern_type',
                y='actual_engagement',
                title="投稿パターン別平均エンゲージメント"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # データソース別統計
    if 'source' in df.columns:
        st.subheader("📊 データソース別統計")
        
        source_stats = df.groupby('source').agg({
            'actual_engagement': lambda x: x.fillna(0).mean(),
            'engagement_prediction': lambda x: x.fillna(0).mean(),
            'clicks': lambda x: x.fillna(0).sum()
        }).reset_index()
        
        st.dataframe(source_stats)
    
    # 基本統計
    st.subheader("📈 基本統計")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("平均エンゲージメント（実績）", f"{stats['avg_engagement']:.2f}")
        st.metric("総いいね数", f"{stats['total_likes']:,}")
        
    with col2:
        st.metric("平均エンゲージメント（予測）", f"{stats['avg_prediction']:.2f}")
        st.metric("総クリック数", f"{stats['total_clicks']:,}")

if __name__ == "__main__":
    main()