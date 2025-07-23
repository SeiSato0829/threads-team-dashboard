#!/usr/bin/env python3
"""
モバイルアクセス可能なStreamlitダッシュボード起動スクリプト
"""

import streamlit as st
import os
import subprocess
import socket

def get_local_ip():
    """ローカルIPアドレスを取得"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

def main():
    print("📱 モバイルアクセス可能なダッシュボードを起動中...")
    
    # ローカルIPアドレスを取得
    local_ip = get_local_ip()
    
    print(f"\n✅ 以下のURLでアクセスできます:")
    print(f"   PCから: http://localhost:8501")
    print(f"   携帯から: http://{local_ip}:8501")
    print(f"\n⚠️  注意: 携帯と同じWi-Fiネットワークに接続してください")
    print("\n停止するには Ctrl+C を押してください\n")
    
    # Streamlitを起動（全てのネットワークインターフェースで受け付ける）
    cmd = [
        "streamlit", "run", "streamlit_app_simple.py",
        "--server.address", "0.0.0.0",  # 全てのインターフェースで受け付ける
        "--server.port", "8501",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n👋 ダッシュボードを停止しました")

if __name__ == "__main__":
    # 仮想環境の確認
    venv_path = os.path.join(os.path.dirname(__file__), "streamlit_env")
    if not os.path.exists(venv_path):
        print("❌ 仮想環境が見つかりません。先にセットアップを完了してください。")
        exit(1)
    
    main()