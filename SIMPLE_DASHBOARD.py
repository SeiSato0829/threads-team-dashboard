#!/usr/bin/env python3
"""
📊 超シンプル Threads投稿管理ダッシュボード
完全動作保証版
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os

# ページ設定
st.set_page_config(
    page_title="Threads投稿管理ダッシュボード",
    page_icon="📱",
    layout="wide"
)

def load_database_safely(db_path, table_name):
    """安全にデータベースを読み込み"""
    if not os.path.exists(db_path):
        return pd.DataFrame(), f"📂 {db_path} が見つかりません"
    
    try:
        conn = sqlite3.connect(db_path)
        
        # テーブル存在確認
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        
        if table_name not in tables:
            conn.close()
            return pd.DataFrame(), f"❌ テーブル '{table_name}' が見つかりません。利用可能: {tables}"
        
        # データ取得（シンプルクエリ）
        query = f"SELECT * FROM {table_name} LIMIT 50"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df, f"✅ {len(df)}件読み込み成功"
        
    except Exception as e:
        return pd.DataFrame(), f"❌ エラー: {str(e)}"

def main():
    """メイン画面"""
    st.title("📱 Threads投稿管理ダッシュボード")
    st.markdown("### 超シンプル版・確実動作")
    
    # データベース設定（実際のテーブル名）
    databases = {
        "scheduled_posts.db": "scheduled_posts",
        "threads_optimized.db": "threads_posts", 
        "buzz_history.db": "buzz_history",
        "viral_history.db": "post_history"
    }
    
    all_data = []
    
    # 各データベース読み込み
    for db_path, table_name in databases.items():
        st.subheader(f"📊 {db_path}")
        
        df, status = load_database_safely(db_path, table_name)
        st.write(status)
        
        if not df.empty:
            # 基本情報表示
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("レコード数", len(df))
            
            with col2:
                st.metric("カラム数", len(df.columns))
            
            with col3:
                # いいね数があれば表示
                if 'likes' in df.columns:
                    total_likes = df['likes'].sum()
                    st.metric("総いいね", int(total_likes))
                else:
                    st.metric("総いいね", "N/A")
            
            # データプレビュー
            if st.checkbox(f"データ表示 ({db_path})", key=db_path):
                st.dataframe(df.head(10), use_container_width=True)
            
            # 全データに追加
            df['source'] = db_path.replace('.db', '')
            all_data.append(df)
        
        st.markdown("---")
    
    # 統合データ分析
    if all_data:
        st.header("📈 統合データ分析")
        
        try:
            # データ統合
            combined_df = pd.concat(all_data, ignore_index=True, sort=False)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🔢 総レコード数", len(combined_df))
            
            with col2:
                if 'likes' in combined_df.columns:
                    total_likes = combined_df['likes'].fillna(0).sum()
                    st.metric("❤️ 総いいね", f"{int(total_likes):,}")
                else:
                    st.metric("❤️ 総いいね", "N/A")
            
            with col3:
                if 'clicks' in combined_df.columns:
                    total_clicks = combined_df['clicks'].fillna(0).sum()
                    st.metric("🔗 総クリック", f"{int(total_clicks):,}")
                else:
                    st.metric("🔗 総クリック", "N/A")
            
            with col4:
                unique_sources = combined_df['source'].nunique()
                st.metric("📊 データソース", unique_sources)
            
            # データソース分布
            if 'source' in combined_df.columns:
                st.subheader("📊 データソース分布")
                source_counts = combined_df['source'].value_counts()
                
                fig = px.pie(
                    values=source_counts.values,
                    names=source_counts.index,
                    title="投稿データ分布"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # 最新データ表示
            st.subheader("📝 最新データ（上位20件）")
            display_df = combined_df.head(20)
            
            # 重要カラムのみ表示
            important_columns = ['content', 'source']
            
            # 利用可能なカラムを追加
            for col in ['scheduled_time', 'generated_at', 'created_at', 'status', 'pattern_type', 'likes', 'clicks']:
                if col in display_df.columns:
                    important_columns.append(col)
            
            # 利用可能なカラムのみでフィルタ
            available_columns = [col for col in important_columns if col in display_df.columns]
            
            if available_columns:
                st.dataframe(display_df[available_columns], use_container_width=True)
            else:
                st.dataframe(display_df, use_container_width=True)
            
        except Exception as e:
            st.error(f"統合データ処理エラー: {e}")
    
    else:
        st.warning("📭 投稿データがありません")
        
        st.markdown("""
        ### 🚀 投稿データを作成するには:
        
        **1. 投稿生成**
        ```bash
        THREADS_ULTIMATE_START.bat
        ```
        
        **2. 投稿実行** 
        ```bash
        BUZZ_SETUP.bat
        ```
        """)
    
    # リフレッシュボタン
    if st.button("🔄 データ再読み込み"):
        st.rerun()

if __name__ == "__main__":
    main()