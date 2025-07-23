#!/usr/bin/env python3
"""
シンプルなStreamlitダッシュボード
Threads自動投稿システム用
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ページ設定
st.set_page_config(
    page_title="Threads投稿管理",
    page_icon="📱",
    layout="wide"
)

def main():
    st.title("📱 Threads投稿管理ダッシュボード")
    st.markdown("---")
    
    # サイドバーでメニュー選択
    menu = st.sidebar.selectbox(
        "メニュー",
        ["📊 ダッシュボード", "📝 新規投稿", "📅 スケジュール管理", "⚙️ 設定"]
    )
    
    if menu == "📊 ダッシュボード":
        show_dashboard()
    elif menu == "📝 新規投稿":
        show_new_post()
    elif menu == "📅 スケジュール管理":
        show_schedule()
    elif menu == "⚙️ 設定":
        show_settings()

def show_dashboard():
    """ダッシュボード表示"""
    st.header("📊 投稿統計")
    
    # 統計情報を3列で表示
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("今日の投稿数", "5", "+2")
    
    with col2:
        st.metric("今週の投稿数", "35", "+10")
    
    with col3:
        st.metric("予約投稿数", "12", "-3")
    
    # 投稿履歴
    st.subheader("📋 最近の投稿")
    
    # サンプルデータ
    sample_data = pd.DataFrame({
        "投稿日時": [
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            "2025-01-23 14:30",
            "2025-01-23 12:00",
            "2025-01-23 09:00",
            "2025-01-22 18:00"
        ],
        "内容": [
            "今日も素晴らしい一日を！",
            "新しいプロジェクトを開始しました",
            "ランチタイムの風景",
            "おはようございます！",
            "今日もお疲れ様でした"
        ],
        "ステータス": ["投稿済み", "投稿済み", "投稿済み", "投稿済み", "投稿済み"],
        "エンゲージメント": ["👍 23", "👍 45", "👍 67", "👍 89", "👍 101"]
    })
    
    st.dataframe(sample_data, use_container_width=True)

def show_new_post():
    """新規投稿フォーム"""
    st.header("📝 新規投稿作成")
    
    # 投稿フォーム
    with st.form("new_post_form"):
        post_content = st.text_area(
            "投稿内容",
            placeholder="投稿したい内容を入力してください...",
            height=150
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            post_date = st.date_input("投稿日")
        
        with col2:
            post_time = st.time_input("投稿時刻")
        
        # 投稿タイプ
        post_type = st.radio(
            "投稿タイプ",
            ["即座に投稿", "予約投稿"]
        )
        
        # 送信ボタン
        submitted = st.form_submit_button("投稿する", type="primary")
        
        if submitted:
            if post_content:
                st.success("✅ 投稿が登録されました！")
                st.balloons()
            else:
                st.error("投稿内容を入力してください")

def show_schedule():
    """スケジュール管理"""
    st.header("📅 スケジュール管理")
    
    # カレンダービュー風の表示
    st.subheader("今週の投稿予定")
    
    schedule_data = pd.DataFrame({
        "日付": ["2025-01-24", "2025-01-24", "2025-01-25", "2025-01-26", "2025-01-27"],
        "時刻": ["09:00", "18:00", "12:00", "15:00", "10:00"],
        "内容": [
            "金曜日の朝の挨拶",
            "週末の予定について",
            "土曜日のランチ投稿",
            "日曜日の午後投稿",
            "新しい週の始まり"
        ],
        "ステータス": ["予約済み", "予約済み", "予約済み", "予約済み", "予約済み"]
    })
    
    st.dataframe(schedule_data, use_container_width=True)
    
    # アクションボタン
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 新規予約"):
            st.info("新規投稿画面から予約投稿を作成してください")
    
    with col2:
        if st.button("✏️ 編集"):
            st.info("編集する投稿を選択してください")
    
    with col3:
        if st.button("🗑️ 削除"):
            st.warning("削除する投稿を選択してください")

def show_settings():
    """設定画面"""
    st.header("⚙️ 設定")
    
    # 基本設定
    st.subheader("基本設定")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("ユーザー名", value="@your_username")
        st.number_input("1日の最大投稿数", min_value=1, max_value=50, value=10)
    
    with col2:
        st.selectbox("デフォルト投稿時間", ["09:00", "12:00", "15:00", "18:00", "21:00"])
        st.checkbox("自動投稿を有効にする", value=True)
    
    # 詳細設定
    st.subheader("詳細設定")
    
    st.slider("投稿間隔（分）", min_value=30, max_value=360, value=120)
    st.multiselect(
        "投稿カテゴリー",
        ["ビジネス", "ライフスタイル", "テクノロジー", "エンターテイメント"],
        default=["ビジネス", "テクノロジー"]
    )
    
    # 保存ボタン
    if st.button("設定を保存", type="primary"):
        st.success("✅ 設定が保存されました！")

if __name__ == "__main__":
    main()