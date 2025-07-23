#!/usr/bin/env python3
"""
🔄 既存システムを動的エンジンに更新
AI_POWERED_VIRAL_ENGINE.pyを動的版に置き換え
"""

import os
import shutil
from datetime import datetime

def update_system():
    """システム更新"""
    print("🔄 既存システムを動的エンジンに更新")
    print("=" * 60)
    
    # バックアップ作成
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # 既存ファイルをバックアップ
    files_to_backup = [
        "AI_POWERED_VIRAL_ENGINE.py",
        "ULTIMATE_AI_VIRAL_SYSTEM.py"
    ]
    
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy(file, os.path.join(backup_dir, file))
            print(f"✅ バックアップ: {file}")
    
    print(f"\nバックアップ完了: {backup_dir}/")
    
    # 設定ファイル作成
    print("\n📝 設定ファイル作成中...")
    
    # auto_post_config.json の更新
    config = {
        "posts_per_day": 5,
        "posting_times": ["08:00", "12:00", "19:00", "21:00", "23:00"],
        "generate_days_ahead": 3,
        "retry_attempts": 3,
        "retry_delay": 300,
        "threads_login_url": "https://threads.net/login",
        "headless_mode": False,
        "execution_times": ["07:00", "11:00", "18:00", "20:00", "22:00"],
        "use_dynamic_engine": True,
        "dynamic_features": {
            "weekday_optimization": True,
            "seasonal_content": True,
            "time_based_templates": True,
            "trending_integration": True,
            "history_tracking": True
        }
    }
    
    import json
    with open("auto_post_config.json", 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("✅ 設定ファイル更新完了")
    
    # 使用方法の表示
    print("\n📚 更新後の使用方法:")
    print("\n1. 動的投稿生成（推奨）:")
    print("   ULTRA_DYNAMIC_START.bat をクリック")
    print("   → 毎日完全に異なる投稿を生成")
    
    print("\n2. 毎日自動実行設定:")
    print("   QUICK_DAILY_SETUP.bat をクリック")
    print("   → 指定時間に自動的に実行")
    
    print("\n3. 手動実行:")
    print("   RUN_DAILY_POST.bat をクリック")
    print("   → 今すぐ投稿を実行")
    
    print("\n✨ 動的エンジンの特徴:")
    print("- 日付ベースで毎日異なる内容")
    print("- 曜日別の最適化")
    print("- 季節対応コンテンツ")
    print("- 時間帯別テンプレート")
    print("- 完全重複防止")
    
    print("\n✅ システム更新完了！")

if __name__ == "__main__":
    update_system()