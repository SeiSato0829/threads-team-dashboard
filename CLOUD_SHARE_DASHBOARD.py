#!/usr/bin/env python3
"""
🌐 クラウド共有対応 Threads投稿管理ダッシュボード
社内共有・チーム協働機能付き
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import os
import socket
import qrcode
import io
import base64
from typing import Dict, List, Tuple

# ページ設定
st.set_page_config(
    page_title="🌟 Threads投稿管理ダッシュボード - クラウド共有版",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_local_ip():
    """ローカルIPアドレスを取得"""
    try:
        # ダミー接続でローカルIPを取得
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def generate_qr_code(url):
    """QRコード生成"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # バイトストリームに変換
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    
    # Base64エンコード
    img_base64 = base64.b64encode(img_bytes).decode()
    
    return img_base64

def show_sharing_panel():
    """共有パネル表示"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌐 社内共有")
    
    # 現在のポート番号取得
    current_port = st.session_state.get('server_port', '8502')
    local_ip = get_local_ip()
    
    # 共有URL生成
    local_url = f"http://localhost:{current_port}"
    network_url = f"http://{local_ip}:{current_port}"
    
    # URL表示
    st.sidebar.markdown("#### 📱 アクセス方法")
    
    with st.sidebar.expander("🔗 共有リンク"):
        st.code(network_url, language="text")
        st.caption("👆 このURLをコピーして社内で共有")
        
        # QRコード生成・表示
        try:
            qr_base64 = generate_qr_code(network_url)
            st.markdown(f"""
            <div style="text-align: center;">
                <img src="data:image/png;base64,{qr_base64}" width="150">
                <br><small>📱 QRコードでアクセス</small>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.caption("QRコード生成エラー")
    
    # 接続手順
    with st.sidebar.expander("📋 接続手順"):
        st.markdown("""
        **📱 スマホ・タブレット:**
        1. QRコードを読み取り
        2. ブラウザで開く
        
        **💻 PC・ノート:**
        1. 上記URLをコピー
        2. ブラウザのアドレスバーに貼り付け
        3. Enterキーを押す
        
        **⚠️ 注意事項:**
        - 同じネットワーク内のみアクセス可能
        - ファイアウォールで許可が必要な場合あり
        """)
    
    # ネットワーク状態
    st.sidebar.markdown("#### 🔧 ネットワーク状況")
    st.sidebar.success(f"✅ サーバー稼働中")
    st.sidebar.info(f"📡 ローカルIP: {local_ip}")
    st.sidebar.info(f"🚪 ポート: {current_port}")
    
    return network_url

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
        
        query = f"SELECT * FROM {table_name} ORDER BY "
        
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

def main():
    """メイン画面"""
    # 共有URL取得
    network_url = show_sharing_panel()
    
    # メインコンテンツ
    st.title("🌟 Threads投稿管理ダッシュボード")
    st.markdown("### 📱 社内共有対応・クラウドアクセス版")
    
    # 共有情報を上部に表示
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.info(f"🌐 **社内共有URL**: `{network_url}`")
    
    with col2:
        st.success("✅ **チームアクセス**: 有効")
    
    with col3:
        if st.button("🔄 更新"):
            st.rerun()
    
    # データ取得・表示
    db_info = get_database_info()
    
    # 統計表示
    total_records = sum(info['records'] for info in db_info.values())
    working_databases = sum(1 for info in db_info.values() if info['status'] == 'OK' and info['records'] > 0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🗄️ 総レコード数", f"{total_records:,}")
    
    with col2:
        st.metric("✅ 稼働中DB", f"{working_databases}/4")
    
    with col3:
        health_percent = (working_databases / 4) * 100
        st.metric("🏥 システム健全性", f"{health_percent:.0f}%")
    
    with col4:
        online_users = 1  # 現在は1（実際の実装では接続数を取得）
        st.metric("👥 オンライン", f"{online_users}人")
    
    # データ詳細
    st.header("📊 投稿データ概要")
    
    all_posts = []
    for db_path, info in db_info.items():
        if info['status'] == 'OK' and info['records'] > 0:
            df, status = load_data_with_status(db_path, info['table'])
            if status == "SUCCESS" and not df.empty:
                df['source'] = db_path.replace('.db', '')
                all_posts.append(df)
    
    if all_posts:
        combined_df = pd.concat(all_posts, ignore_index=True, sort=False)
        
        # 投稿状況の分析
        posted_count = len(combined_df[combined_df['status'].isin(['posted', 'completed'])])
        scheduled_count = len(combined_df[combined_df['status'].isin(['scheduled', 'pending', 'generated'])])
        
        # グラフ表示
        col1, col2 = st.columns(2)
        
        with col1:
            # ステータス分布
            status_data = {
                '投稿済み': posted_count,
                '投稿予定': scheduled_count,
                'その他': len(combined_df) - posted_count - scheduled_count
            }
            
            fig = px.pie(
                values=list(status_data.values()),
                names=list(status_data.keys()),
                title="📊 投稿ステータス分布",
                hole=0.4,
                color_discrete_sequence=['#10B981', '#3B82F6', '#6B7280']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # データソース分布
            if 'source' in combined_df.columns:
                source_counts = combined_df['source'].value_counts()
                
                fig = px.bar(
                    x=source_counts.values,
                    y=source_counts.index,
                    title="📈 データソース別投稿数",
                    orientation='h',
                    color=source_counts.values,
                    color_continuous_scale='Blues'
                )
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
        
        # 次の投稿予定
        st.subheader("🕐 次の投稿スケジュール")
        
        future_posts = combined_df.copy()
        if 'scheduled_time' in future_posts.columns:
            future_posts = future_posts[
                (future_posts['scheduled_time'] > datetime.now()) & 
                (future_posts['status'].isin(['scheduled', 'pending', 'generated']))
            ].sort_values('scheduled_time')
        
        if not future_posts.empty:
            next_posts = future_posts.head(5)
            
            for idx, post in next_posts.iterrows():
                col1, col2, col3 = st.columns([1, 1, 3])
                
                with col1:
                    scheduled_time = post.get('scheduled_time')
                    if pd.notna(scheduled_time):
                        time_str = scheduled_time.strftime('%m/%d %H:%M')
                        time_status, time_class = get_time_status(scheduled_time)
                        
                        if "urgent" in time_class:
                            st.error(f"📅 {time_str}\n{time_status}")
                        elif "soon" in time_class:
                            st.warning(f"📅 {time_str}\n{time_status}")
                        else:
                            st.info(f"📅 {time_str}\n{time_status}")
                
                with col2:
                    status = post.get('status', 'unknown')
                    if status in ['posted', 'completed']:
                        st.success("✅ 投稿済み")
                    elif status in ['scheduled', 'pending', 'generated']:
                        st.info("⏰ 投稿予定")
                    else:
                        st.warning(f"📝 {status}")
                    
                    source = post.get('source', 'unknown')
                    st.caption(f"📊 {source}")
                
                with col3:
                    content = post.get('content', '')
                    preview = content[:100] + "..." if len(content) > 100 else content
                    st.write(f"📝 {preview}")
                    
                    if 'pattern_type' in post:
                        st.caption(f"🎯 {post.get('pattern_type', 'N/A')}")
        else:
            st.info("📅 現在、予定されている投稿はありません")
    
    else:
        st.warning("📭 投稿データがありません")
        
        st.markdown("""
        ### 🚀 投稿データを作成しましょう！
        
        **1. 新しい投稿を生成**
        ```bash
        THREADS_ULTIMATE_START.bat
        ```
        
        **2. 自動投稿システム起動**  
        ```bash
        BUZZ_SETUP.bat
        ```
        """)
    
    # フッター
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #6B7280;">
        🌐 社内共有URL: <code>{network_url}</code><br>
        💡 このURLを社内で共有してチーム全員でアクセスできます<br>
        🔄 最終更新: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()