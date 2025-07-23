#!/usr/bin/env python3
"""
📱 極上ホスピタリティ Threads投稿管理ダッシュボード
投稿管理の究極体験を提供
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import os
from typing import Dict, List, Tuple

# ページ設定
st.set_page_config(
    page_title="🌟 Threads投稿管理ダッシュボード",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .status-posted { 
        background: linear-gradient(90deg, #10B981, #059669);
        color: white; 
        padding: 8px 16px; 
        border-radius: 20px; 
        font-weight: bold;
        text-align: center;
    }
    .status-scheduled { 
        background: linear-gradient(90deg, #3B82F6, #1D4ED8);
        color: white; 
        padding: 8px 16px; 
        border-radius: 20px; 
        font-weight: bold;
        text-align: center;
    }
    .status-failed { 
        background: linear-gradient(90deg, #EF4444, #DC2626);
        color: white; 
        padding: 8px 16px; 
        border-radius: 20px; 
        font-weight: bold;
        text-align: center;
    }
    .time-urgent { color: #EF4444; font-weight: bold; }
    .time-soon { color: #F59E0B; font-weight: bold; }
    .time-normal { color: #6B7280; }
    .metrics-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def get_database_info():
    """データベース情報を詳細に取得"""
    databases = {
        'scheduled_posts.db': 'scheduled_posts',
        'threads_optimized.db': 'threads_posts', 
        'buzz_history.db': 'buzz_history',
        'viral_history.db': 'post_history'
    }
    
    db_info = {}
    
    for db_path, table_name in databases.items():
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                all_tables = [t[0] for t in cursor.fetchall()]
                
                if table_name in all_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    record_count = cursor.fetchone()[0]
                    
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    db_info[db_path] = {
                        'table': table_name,
                        'records': record_count,
                        'columns': columns,
                        'status': 'OK',
                        'last_updated': datetime.now()
                    }
                else:
                    db_info[db_path] = {
                        'table': table_name,
                        'records': 0,
                        'columns': [],
                        'status': f'TABLE_NOT_FOUND',
                        'last_updated': None
                    }
                
                conn.close()
                
            except Exception as e:
                db_info[db_path] = {
                    'table': table_name,
                    'records': 0,
                    'columns': [],
                    'status': f'ERROR: {str(e)}',
                    'last_updated': None
                }
        else:
            db_info[db_path] = {
                'table': table_name,
                'records': 0,
                'columns': [],
                'status': 'FILE_NOT_EXISTS',
                'last_updated': None
            }
    
    return db_info

def load_data_with_status(db_path, table_name):
    """ステータス情報付きでデータ読み込み"""
    try:
        conn = sqlite3.connect(db_path)
        
        # 基本クエリ
        query = f"SELECT * FROM {table_name} ORDER BY "
        
        # 時間カラムでソート（利用可能なものを使用）
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'scheduled_time' in columns:
            query += "scheduled_time DESC"
        elif 'generated_at' in columns:
            query += "generated_at DESC"
        elif 'created_at' in columns:
            query += "created_at DESC"
        else:
            query += "id DESC"
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # 時間カラムの変換
        for time_col in ['scheduled_time', 'generated_at', 'created_at', 'posted_at']:
            if time_col in df.columns:
                df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
        
        return df, "SUCCESS"
        
    except Exception as e:
        return pd.DataFrame(), f"ERROR: {str(e)}"

def get_time_status(scheduled_time):
    """時間に基づくステータス判定"""
    if pd.isna(scheduled_time):
        return "⏰ 時間未設定", "time-normal"
    
    now = datetime.now()
    diff = (scheduled_time - now).total_seconds() / 60  # 分単位
    
    if diff < 0:
        return "⏰ 予定時刻経過", "time-urgent"
    elif diff < 30:
        return f"🚨 {int(diff)}分後", "time-urgent"
    elif diff < 120:
        return f"⚡ {int(diff)}分後", "time-soon"
    elif diff < 1440:  # 24時間
        hours = int(diff / 60)
        return f"🕐 {hours}時間後", "time-normal"
    else:
        days = int(diff / 1440)
        return f"📅 {days}日後", "time-normal"

def render_status_badge(status):
    """ステータスバッジをレンダリング"""
    if status in ['posted', 'completed']:
        return '<div class="status-posted">✅ 投稿済み</div>'
    elif status in ['scheduled', 'pending', 'generated']:
        return '<div class="status-scheduled">⏰ 投稿予定</div>'
    elif status == 'failed':
        return '<div class="status-failed">❌ 投稿失敗</div>'
    else:
        return f'<div class="status-scheduled">📝 {status or "未設定"}</div>'

def show_smart_overview():
    """スマート概要ダッシュボード"""
    st.markdown("## 🌟 投稿管理センター")
    
    # データ取得
    db_info = get_database_info()
    
    # 全データ統合
    all_posts = []
    for db_path, info in db_info.items():
        if info['status'] == 'OK' and info['records'] > 0:
            df, status = load_data_with_status(db_path, info['table'])
            if status == "SUCCESS" and not df.empty:
                df['source'] = db_path.replace('.db', '')
                all_posts.append(df)
    
    if not all_posts:
        st.warning("📭 投稿データがありません")
        show_getting_started()
        return
    
    combined_df = pd.concat(all_posts, ignore_index=True, sort=False)
    
    # メインKPI
    col1, col2, col3, col4 = st.columns(4)
    
    # 投稿状況の分析
    posted_count = len(combined_df[combined_df['status'].isin(['posted', 'completed'])])
    scheduled_count = len(combined_df[combined_df['status'].isin(['scheduled', 'pending', 'generated'])])
    failed_count = len(combined_df[combined_df['status'] == 'failed'])
    total_count = len(combined_df)
    
    with col1:
        st.markdown(f"""
        <div class="metrics-card">
            <h3>✅ 投稿完了</h3>
            <h1>{posted_count:,}</h1>
            <p>成功率: {(posted_count/total_count*100):.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metrics-card">
            <h3>⏰ 投稿予定</h3>
            <h1>{scheduled_count:,}</h1>
            <p>待機中の投稿</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_engagement = combined_df['likes'].fillna(0).sum() if 'likes' in combined_df.columns else 0
        st.markdown(f"""
        <div class="metrics-card">
            <h3>❤️ 総エンゲージメント</h3>
            <h1>{int(total_engagement):,}</h1>
            <p>いいね・反応数</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_performance = combined_df['likes'].fillna(0).mean() if 'likes' in combined_df.columns else 0
        st.markdown(f"""
        <div class="metrics-card">
            <h3>📊 平均パフォーマンス</h3>
            <h1>{avg_performance:.1f}</h1>
            <p>投稿あたりのいいね</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 次の投稿予定
    show_next_schedule(combined_df)
    
    # 最新の投稿状況
    show_recent_activity(combined_df)

def show_next_schedule(df):
    """次の投稿スケジュール表示"""
    st.subheader("🕐 次の投稿スケジュール")
    
    # 未来の投稿のみフィルタ
    future_posts = df.copy()
    
    if 'scheduled_time' in future_posts.columns:
        future_posts = future_posts[
            (future_posts['scheduled_time'] > datetime.now()) & 
            (future_posts['status'].isin(['scheduled', 'pending', 'generated']))
        ].sort_values('scheduled_time')
    
    if future_posts.empty:
        st.info("📅 現在、予定されている投稿はありません")
        return
    
    # 次の5つの投稿を表示
    next_posts = future_posts.head(5)
    
    for idx, post in next_posts.iterrows():
        col1, col2, col3 = st.columns([2, 2, 3])
        
        with col1:
            scheduled_time = post.get('scheduled_time')
            if pd.notna(scheduled_time):
                time_str = scheduled_time.strftime('%m/%d %H:%M')
                time_status, time_class = get_time_status(scheduled_time)
                st.markdown(f"""
                <div class="{time_class}">
                    📅 {time_str}<br>
                    {time_status}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.write("⏰ 時間未設定")
        
        with col2:
            status = post.get('status', 'unknown')
            st.markdown(render_status_badge(status), unsafe_allow_html=True)
            
            source = post.get('source', 'unknown')
            st.caption(f"📊 {source}")
        
        with col3:
            content = post.get('content', '')
            preview = content[:100] + "..." if len(content) > 100 else content
            st.write(f"📝 {preview}")
            
            if 'pattern_type' in post:
                st.caption(f"🎯 {post.get('pattern_type', 'N/A')}")

def show_recent_activity(df):
    """最近のアクティビティ表示"""
    st.subheader("📈 最新の投稿活動")
    
    # 最新20件を表示
    recent_posts = df.head(20)
    
    for idx, post in recent_posts.iterrows():
        with st.expander(f"📝 {post.get('source', 'unknown')} - {post.get('status', 'unknown')}"):
            col1, col2 = st.columns([2, 3])
            
            with col1:
                # 時間情報
                for time_col in ['posted_at', 'scheduled_time', 'generated_at', 'created_at']:
                    if time_col in post and pd.notna(post[time_col]):
                        time_str = post[time_col].strftime('%Y/%m/%d %H:%M')
                        st.write(f"🕐 {time_col.replace('_', ' ').title()}: {time_str}")
                        break
                
                # ステータス
                status = post.get('status', 'unknown')
                st.markdown(render_status_badge(status), unsafe_allow_html=True)
                
                # パフォーマンス
                if 'likes' in post and post['likes'] > 0:
                    st.metric("❤️ いいね", int(post['likes']))
                if 'clicks' in post and post['clicks'] > 0:
                    st.metric("🔗 クリック", int(post['clicks']))
            
            with col2:
                content = post.get('content', '')
                st.text_area("投稿内容", content, height=100, key=f"content_{idx}", disabled=True)

def show_schedule_manager():
    """スケジュール管理画面"""
    st.markdown("## 📅 投稿スケジュール管理")
    
    # データ取得
    db_info = get_database_info()
    all_posts = []
    
    for db_path, info in db_info.items():
        if info['status'] == 'OK' and info['records'] > 0:
            df, status = load_data_with_status(db_path, info['table'])
            if status == "SUCCESS" and not df.empty:
                df['source'] = db_path.replace('.db', '')
                all_posts.append(df)
    
    if not all_posts:
        st.warning("📭 スケジュールデータがありません")
        return
    
    combined_df = pd.concat(all_posts, ignore_index=True, sort=False)
    
    # フィルター
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "📊 ステータスフィルター", 
            ['すべて', '投稿予定', '投稿済み', '失敗']
        )
    
    with col2:
        source_filter = st.selectbox(
            "🗂️ データソースフィルター",
            ['すべて'] + list(combined_df['source'].unique())
        )
    
    with col3:
        days_filter = st.selectbox(
            "📅 期間フィルター",
            ['すべて', '今日', '明日', '今週', '来週']
        )
    
    # フィルタリング適用
    filtered_df = combined_df.copy()
    
    if status_filter == '投稿予定':
        filtered_df = filtered_df[filtered_df['status'].isin(['scheduled', 'pending', 'generated'])]
    elif status_filter == '投稿済み':
        filtered_df = filtered_df[filtered_df['status'].isin(['posted', 'completed'])]
    elif status_filter == '失敗':
        filtered_df = filtered_df[filtered_df['status'] == 'failed']
    
    if source_filter != 'すべて':
        filtered_df = filtered_df[filtered_df['source'] == source_filter]
    
    # 期間フィルタ
    if days_filter != 'すべて' and 'scheduled_time' in filtered_df.columns:
        now = datetime.now()
        if days_filter == '今日':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif days_filter == '明日':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            end = start + timedelta(days=1)
        elif days_filter == '今週':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=now.weekday())
            end = start + timedelta(days=7)
        elif days_filter == '来週':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=now.weekday()) + timedelta(days=7)
            end = start + timedelta(days=7)
        
        filtered_df = filtered_df[
            (filtered_df['scheduled_time'] >= start) & 
            (filtered_df['scheduled_time'] < end)
        ]
    
    st.info(f"📋 {len(filtered_df)} 件の投稿を表示中")
    
    # カレンダービュー
    if st.checkbox("📅 カレンダービューで表示"):
        show_calendar_view(filtered_df)
    else:
        show_list_view(filtered_df)

def show_calendar_view(df):
    """カレンダービュー表示"""
    st.subheader("📅 カレンダービュー")
    
    if 'scheduled_time' not in df.columns or df['scheduled_time'].isna().all():
        st.warning("⏰ スケジュール時間情報がありません")
        return
    
    # 日別グループ化
    df_with_date = df.copy()
    df_with_date['date'] = df_with_date['scheduled_time'].dt.date
    daily_posts = df_with_date.groupby('date').size().reset_index(name='post_count')
    
    # 投稿数のヒートマップ（簡易版）
    if not daily_posts.empty:
        fig = px.bar(
            daily_posts, 
            x='date', 
            y='post_count',
            title="📅 日別投稿予定数",
            color='post_count',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def show_list_view(df):
    """リストビュー表示"""
    st.subheader("📋 投稿リスト")
    
    # ソート
    sort_by = st.selectbox("📊 並び替え", ['時間順', 'ステータス順', 'パフォーマンス順'])
    
    if sort_by == '時間順' and 'scheduled_time' in df.columns:
        df = df.sort_values('scheduled_time', ascending=False)
    elif sort_by == 'パフォーマンス順' and 'likes' in df.columns:
        df = df.sort_values('likes', ascending=False)
    elif sort_by == 'ステータス順' and 'status' in df.columns:
        df = df.sort_values('status')
    
    # 投稿表示
    for idx, post in df.head(20).iterrows():
        col1, col2, col3 = st.columns([1, 1, 3])
        
        with col1:
            scheduled_time = post.get('scheduled_time')
            if pd.notna(scheduled_time):
                time_str = scheduled_time.strftime('%m/%d %H:%M')
                time_status, time_class = get_time_status(scheduled_time)
                st.markdown(f"""
                <div class="{time_class}">
                    📅 {time_str}<br>
                    <small>{time_status}</small>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            status = post.get('status', 'unknown')
            st.markdown(render_status_badge(status), unsafe_allow_html=True)
            
            # パフォーマンス
            if 'likes' in post and post['likes'] > 0:
                st.metric("❤️", int(post['likes']))
        
        with col3:
            content = post.get('content', '')
            preview = content[:150] + "..." if len(content) > 150 else content
            
            with st.expander(f"📝 {preview[:50]}..."):
                st.write(content)
                
                # 詳細情報
                col_a, col_b = st.columns(2)
                with col_a:
                    st.caption(f"📊 Source: {post.get('source', 'N/A')}")
                    st.caption(f"🎯 Pattern: {post.get('pattern_type', 'N/A')}")
                
                with col_b:
                    if 'clicks' in post:
                        st.caption(f"🔗 Clicks: {post.get('clicks', 0)}")
                    if 'shares' in post:
                        st.caption(f"🔄 Shares: {post.get('shares', 0)}")

def show_getting_started():
    """スタートガイド"""
    st.markdown("### 🚀 投稿データを作成しましょう！")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 📝 新しい投稿を生成
        ```bash
        THREADS_ULTIMATE_START.bat
        ```
        - AI による高品質投稿生成
        - 複数パターンの投稿作成
        - 自動スケジューリング
        """)
    
    with col2:
        st.markdown("""
        #### 🚀 自動投稿システム起動
        ```bash
        BUZZ_SETUP.bat
        ```
        - バズりやすい投稿の自動生成
        - 最適なタイミングで投稿
        - エンゲージメント追跡
        """)

def main():
    """メイン画面"""
    st.sidebar.title("🌟 投稿管理メニュー")
    
    menu = st.sidebar.selectbox(
        "📋 表示内容を選択",
        [
            "🏠 スマート概要",
            "📅 スケジュール管理", 
            "📊 パフォーマンス分析",
            "🔧 システム設定"
        ]
    )
    
    if menu == "🏠 スマート概要":
        show_smart_overview()
    elif menu == "📅 スケジュール管理":
        show_schedule_manager()
    elif menu == "📊 パフォーマンス分析":
        show_analytics_dashboard()
    elif menu == "🔧 システム設定":
        show_system_settings()
    
    # サイドバー情報
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 クイックアクション")
    
    if st.sidebar.button("🔄 データ再読み込み"):
        st.rerun()
    
    if st.sidebar.button("📊 システム診断"):
        show_system_diagnosis()

def show_analytics_dashboard():
    """パフォーマンス分析ダッシュボード"""
    st.markdown("## 📊 パフォーマンス分析")
    
    # 分析コードはここに追加
    st.info("📈 高度な分析機能を開発中...")

def show_system_settings():
    """システム設定画面"""
    st.markdown("## 🔧 システム設定")
    
    # 設定コードはここに追加
    st.info("⚙️ システム設定機能を開発中...")

def show_system_diagnosis():
    """システム診断"""
    with st.sidebar:
        with st.spinner("🔍 診断中..."):
            db_info = get_database_info()
            
            working_dbs = sum(1 for info in db_info.values() if info['status'] == 'OK')
            total_records = sum(info['records'] for info in db_info.values())
            
            st.success(f"✅ {working_dbs}/4 DBが正常動作")
            st.info(f"📊 総レコード数: {total_records:,}")

if __name__ == "__main__":
    main()