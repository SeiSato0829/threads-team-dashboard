#!/usr/bin/env python3
"""
📊 Threads投稿管理ダッシュボード - セキュア版
Streamlit Cloud対応・認証機能付き
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
import hmac

# ページ設定
st.set_page_config(
    page_title="Threads投稿管理ダッシュボード",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🔐 認証機能
def check_password():
    """パスワード認証機能"""
    
    def password_entered():
        """パスワード確認"""
        if hmac.compare_digest(st.session_state["password"], st.secrets.get("security", {}).get("admin_password", "threads2025")):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # パスワードを削除
        else:
            st.session_state["password_correct"] = False

    # 初回アクセス時
    if "password_correct" not in st.session_state:
        # パスワード入力フォーム
        st.markdown("## 🔐 ログイン")
        st.text_input(
            "パスワードを入力してください", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.info("デモパスワード: threads2025")
        return False
    
    # パスワードが間違っている場合
    elif not st.session_state["password_correct"]:
        st.error("❌ パスワードが違います")
        st.text_input(
            "パスワードを入力してください", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    
    # 認証成功
    else:
        return True

# メイン処理（既存のThreadsDashboardクラスと関数をそのまま使用）
from THREADS_DASHBOARD import ThreadsDashboard, show_overview_dashboard, show_post_history, show_performance_analysis, show_post_editor, show_team_sharing, show_auto_reports, show_direct_posting

def main():
    """メイン画面（認証付き）"""
    
    # 認証チェック
    if not check_password():
        return
    
    # 認証成功後の処理
    st.title("📱 Threads投稿管理ダッシュボード")
    st.markdown("### 自動化対応・完全管理システム（セキュア版）")
    
    # ログアウトボタン
    if st.sidebar.button("🚪 ログアウト"):
        del st.session_state["password_correct"]
        st.rerun()
    
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
    
    # 各ページの表示
    if page == "📈 概要ダッシュボード":
        show_overview_dashboard(df, stats)
    elif page == "📝 投稿履歴":
        show_post_history(df, dashboard)
    elif page == "📊 パフォーマンス分析":
        show_performance_analysis(df, stats)
    elif page == "✏️ 投稿編集":
        show_post_editor(df, dashboard)
    elif page == "👥 チーム共有":
        show_team_sharing(df, stats)
    elif page == "📋 自動レポート":
        show_auto_reports(df, stats)
    elif page == "🤖 自動投稿設定":
        show_direct_posting()

if __name__ == "__main__":
    main()