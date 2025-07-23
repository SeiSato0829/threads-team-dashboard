#!/usr/bin/env python3
"""
🚀 ワンクリック起動システム
すべてを統合した最強の自動化システム
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

def check_requirements():
    """必要な環境をチェック"""
    print("🔍 環境チェック中...")
    
    # .envファイルチェック
    if not Path(".env").exists():
        print("⚠️ .envファイルが見つかりません！")
        create_env_file()
    
    # 依存関係インストール
    print("📦 依存関係をインストール中...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_ultimate.txt", "-q"])
    
    print("✅ 環境チェック完了！")

def create_env_file():
    """初期.envファイルを作成"""
    print("\n🔧 初期設定を行います...")
    
    env_content = """# Threads認証情報
THREADS_ACCESS_TOKEN=your_threads_access_token
THREADS_USERNAME=your_username

# AI API (少なくとも1つ必須)
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key

# オプション
CONVERSION_TRACKER_URL=https://your-tracker.com
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("📝 .envファイルを作成しました。")
    print("   必要な情報を入力してから再実行してください。")
    input("\nEnterキーを押して終了...")
    sys.exit(0)

def start_system():
    """システムを起動"""
    print("\n🚀 究極のThreads収益最大化システムを起動中...")
    print("=" * 50)
    
    # メインシステムを起動
    cmd = [sys.executable, "ULTIMATE_THREADS_SYSTEM_2025.py"]
    process = subprocess.Popen(cmd)
    
    # 少し待機
    time.sleep(3)
    
    # ブラウザを開く
    print("\n🌐 ダッシュボードを開いています...")
    webbrowser.open("http://localhost:8000")
    
    print("\n✨ システムが稼働中！")
    print("\n📊 ダッシュボード: http://localhost:8000")
    print("📱 スマホからもアクセス可能: http://[あなたのIPアドレス]:8000")
    print("\n🔥 機能:")
    print("  • AI投稿自動生成（6時間ごと）")
    print("  • A/Bテスト自動実行")
    print("  • 収益トラッキング")
    print("  • 機械学習による最適化")
    print("\n終了するには Ctrl+C を押してください。")
    
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\n\n👋 システムを終了します...")
        process.terminate()

def main():
    """メイン関数"""
    print("""
    ╔══════════════════════════════════════════╗
    ║   🚀 究極のThreads収益最大化システム    ║
    ║          2025 Ultimate Edition           ║
    ╚══════════════════════════════════════════╝
    """)
    
    # 環境チェック
    check_requirements()
    
    # システム起動
    start_system()

if __name__ == "__main__":
    main()