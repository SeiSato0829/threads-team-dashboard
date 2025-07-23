#!/usr/bin/env python3
"""
Threads自動投稿システム - 起動スクリプト
フロントエンドとバックエンドの同時起動
"""

import os
import sys
import subprocess
import time
import signal
import platform
from pathlib import Path
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemLauncher:
    """システム起動管理クラス"""
    
    def __init__(self):
        self.processes = []
        self.is_running = False
        
    def check_dependencies(self):
        """依存関係をチェック"""
        logger.info("依存関係をチェックしています...")
        
        # Python依存関係
        required_packages = [
            'flask',
            'flask_cors',
            'anthropic', 
            'requests',
            'pandas',
            'schedule',
            'werkzeug',
            'dotenv'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"不足しているPythonパッケージ: {', '.join(missing_packages)}")
            logger.info("以下のコマンドでインストールしてください:")
            logger.info(f"pip install {' '.join(missing_packages)}")
            return False
        
        # Node.js依存関係
        if not os.path.exists('node_modules'):
            logger.error("Node.jsの依存関係がインストールされていません")
            logger.info("npm install を実行してください")
            return False
        
        # 必要なファイルの存在確認
        required_files = [
            'complete_backend_server_final.py',
            'post_diversity_manager.py',
            'enhanced_post_generator.py',
            'src/App-Final.tsx',
            'src/services/api-fixed.ts',
            'package.json'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            logger.error(f"不足しているファイル: {', '.join(missing_files)}")
            return False
        
        logger.info("依存関係チェック完了")
        return True
    
    def start_backend(self):
        """バックエンドサーバーを起動"""
        logger.info("バックエンドサーバーを起動しています...")
        
        try:
            # Pythonのバージョンを確認
            python_cmd = 'python' if platform.system() == 'Windows' else 'python3'
            
            # バックエンドプロセスを起動
            process = subprocess.Popen(
                [python_cmd, 'complete_backend_server_final.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            self.processes.append(('backend', process))
            
            # 起動確認（5秒待機）
            time.sleep(5)
            
            if process.poll() is None:
                logger.info("バックエンドサーバー起動成功: http://localhost:5000")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"バックエンドサーバー起動失敗: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"バックエンドサーバー起動エラー: {e}")
            return False
    
    def start_frontend(self):
        """フロントエンドサーバーを起動"""
        logger.info("フロントエンドサーバーを起動しています...")
        
        try:
            # package.jsonの確認
            if not os.path.exists('package.json'):
                logger.error("package.jsonが見つかりません")
                return False
            
            # npm devサーバーを起動
            npm_cmd = 'npm.cmd' if platform.system() == 'Windows' else 'npm'
            
            process = subprocess.Popen(
                [npm_cmd, 'run', 'dev'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            self.processes.append(('frontend', process))
            
            # 起動確認（10秒待機）
            time.sleep(10)
            
            if process.poll() is None:
                logger.info("フロントエンドサーバー起動成功: http://localhost:5173")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"フロントエンドサーバー起動失敗: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"フロントエンドサーバー起動エラー: {e}")
            return False
    
    def setup_signal_handlers(self):
        """シグナルハンドラーを設定"""
        def signal_handler(signum, frame):
            logger.info("終了シグナルを受信しました")
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def shutdown(self):
        """全プロセスを終了"""
        logger.info("システムを終了しています...")
        
        for name, process in self.processes:
            try:
                if process.poll() is None:
                    logger.info(f"{name}プロセスを終了中...")
                    process.terminate()
                    
                    # 10秒待機して強制終了
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        logger.warning(f"{name}プロセスを強制終了します")
                        process.kill()
                        
            except Exception as e:
                logger.error(f"{name}プロセス終了エラー: {e}")
        
        self.is_running = False
        logger.info("システム終了完了")
    
    def monitor_processes(self):
        """プロセスの状態を監視"""
        while self.is_running:
            time.sleep(30)  # 30秒ごとにチェック
            
            for name, process in self.processes:
                if process.poll() is not None:
                    logger.error(f"{name}プロセスが予期せず終了しました")
                    self.shutdown()
                    return
    
    def run(self):
        """システムを起動"""
        logger.info("Threads自動投稿システム v3.2 - 完全版を起動しています...")
        
        # 依存関係チェック
        if not self.check_dependencies():
            logger.error("依存関係チェックに失敗しました")
            return False
        
        # シグナルハンドラー設定
        self.setup_signal_handlers()
        
        # バックエンド起動
        if not self.start_backend():
            logger.error("バックエンドサーバーの起動に失敗しました")
            return False
        
        # フロントエンド起動
        if not self.start_frontend():
            logger.error("フロントエンドサーバーの起動に失敗しました")
            self.shutdown()
            return False
        
        self.is_running = True
        
        # 起動完了メッセージ
        print("\n" + "="*60)
        print("Threads自動投稿システム v3.2 - 完全版")
        print("="*60)
        print("✅ バックエンドサーバー: http://localhost:5000")
        print("✅ フロントエンド: http://localhost:5173")
        print()
        print("🔧 管理画面にアクセスして、APIキーを設定してください")
        print("📝 設定 > Claude API Key & Buffer API Token")
        print()
        print("🛑 終了: Ctrl+C")
        print("="*60)
        
        # プロセス監視
        try:
            self.monitor_processes()
        except KeyboardInterrupt:
            logger.info("ユーザーによる終了要求")
            self.shutdown()
        
        return True

def main():
    """メイン関数"""
    launcher = SystemLauncher()
    
    try:
        success = launcher.run()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("起動中にキャンセルされました")
        launcher.shutdown()
        sys.exit(0)
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        launcher.shutdown()
        sys.exit(1)

if __name__ == '__main__':
    main()