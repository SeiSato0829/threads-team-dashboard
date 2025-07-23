#!/bin/bash
# Threads自動投稿システム - Linux/Mac起動スクリプト

echo "============================================================"
echo "Threads自動投稿システム v3.2 - 完全版"
echo "============================================================"
echo

# 現在のディレクトリを確認
echo "現在のディレクトリ: $(pwd)"
echo

# Pythonのバージョンを確認
echo "Pythonバージョンを確認中..."
if command -v python3 &> /dev/null; then
    python3 --version
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    python --version
    PYTHON_CMD="python"
else
    echo "エラー: Pythonがインストールされていません"
    exit 1
fi

# Node.jsのバージョンを確認
echo "Node.jsバージョンを確認中..."
if ! command -v node &> /dev/null; then
    echo "エラー: Node.jsがインストールされていません"
    exit 1
fi
node --version

# npmのバージョンを確認
if ! command -v npm &> /dev/null; then
    echo "エラー: npmがインストールされていません"
    exit 1
fi
npm --version

echo

# 必要なファイルの存在確認
echo "必要なファイルを確認中..."
required_files=(
    "complete_backend_server_final.py"
    "package.json"
    "post_diversity_manager.py"
    "enhanced_post_generator.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "エラー: $file が見つかりません"
        exit 1
    fi
done

# Node.js依存関係の確認
if [ ! -d "node_modules" ]; then
    echo "Node.js依存関係をインストール中..."
    npm install
    if [ $? -ne 0 ]; then
        echo "エラー: npm install に失敗しました"
        exit 1
    fi
fi

# Python依存関係の確認
echo "Python依存関係を確認中..."
$PYTHON_CMD -c "import flask, flask_cors, anthropic, requests, pandas, schedule" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Python依存関係をインストール中..."
    pip3 install flask flask-cors anthropic requests pandas schedule 2>/dev/null || \
    pip install flask flask-cors anthropic requests pandas schedule
    
    if [ $? -ne 0 ]; then
        echo "エラー: Python依存関係のインストールに失敗しました"
        echo "手動で以下を実行してください:"
        echo "pip install flask flask-cors anthropic requests pandas schedule"
        exit 1
    fi
fi

# 実行権限を付与
chmod +x start_system.py 2>/dev/null

echo
echo "起動スクリプトを実行中..."
$PYTHON_CMD start_system.py

echo
echo "システムが終了しました"