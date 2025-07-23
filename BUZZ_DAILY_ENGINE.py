#!/usr/bin/env python3
"""
🤖 バズ投稿用毎日自動実行エンジン
口コミ風投稿を毎日自動生成・投稿
"""

import os
import sys
import json
from datetime import datetime

# 既存のDAILY_AUTO_POST_ENGINEを拡張
try:
    # エンジン切り替え設定
    config_path = "auto_post_config.json"
    
    # 設定更新
    config = {
        "posts_per_day": 5,
        "posting_times": ["08:00", "12:00", "19:00", "21:00", "23:00"],
        "generate_days_ahead": 3,
        "retry_attempts": 3,
        "retry_delay": 300,
        "threads_login_url": "https://threads.net/login",
        "headless_mode": False,
        "execution_times": ["07:00", "11:00", "18:00", "20:00", "22:00"],
        "use_buzz_engine": True,  # バズエンジンを使用
        "engine_type": "viral_buzz"  # エンジンタイプ指定
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("✅ バズ投稿用設定に更新しました")
    
    # 既存のエンジンを実行
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        # DAILY_AUTO_POST_ENGINEを動的に修正して実行
        import importlib.util
        
        # モジュールを動的にロード
        spec = importlib.util.spec_from_file_location(
            "daily_auto_post_engine", 
            "DAILY_AUTO_POST_ENGINE.py"
        )
        module = importlib.util.module_from_spec(spec)
        
        # エンジンを差し替える処理を追加
        original_code = open("DAILY_AUTO_POST_ENGINE.py", 'r', encoding='utf-8').read()
        
        # インポート部分を修正
        modified_code = original_code.replace(
            "from AI_POWERED_VIRAL_ENGINE import AdvancedViralEngine",
            "from VIRAL_BUZZ_ENGINE import BuzzViralEngine as AdvancedViralEngine"
        )
        
        # 一時的に修正版を実行
        exec(modified_code)
        
    else:
        print("\n使い方:")
        print("1. バズ投稿の自動実行設定:")
        print("   BUZZ_SETUP.bat を実行")
        print("\n2. 今すぐバズ投稿を実行:")
        print("   python BUZZ_DAILY_ENGINE.py --execute")

except Exception as e:
    print(f"エラー: {e}")
    print("\n既存のシステムをバズ投稿用に設定できませんでした")
    print("BUZZ_START.bat から手動で実行してください")