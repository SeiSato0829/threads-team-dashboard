#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Threads Automation Starter
"""

import sys
import os
import subprocess

def main():
    print("🚀 Threads Auto-Posting System")
    print("=" * 50)
    
    try:
        # 必要なパッケージをインストール
        print("Installing packages...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "selenium", "schedule"], check=True)
        
        # メインスクリプト実行
        print("Starting automation...")
        subprocess.run([sys.executable, "IMPROVED_AUTOMATION.py"], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()