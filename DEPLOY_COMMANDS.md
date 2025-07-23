# 📋 GitHubへのプッシュコマンド

以下のコマンドをGit Bashまたはコマンドプロンプトで実行してください：

```bash
# 1. プロジェクトディレクトリに移動
cd C:\Users\music-020\threads-auto-post

# 2. Gitリポジトリを初期化
git init

# 3. GitHubユーザー設定
git config user.name "SeiSato0829"
git config user.email "your-email@example.com"

# 4. 必要なファイルを追加
git add THREADS_DASHBOARD.py
git add requirements_streamlit.txt
git add .streamlit/config.toml
git add threads_simple_automation.py
git add *.db
git add README_STREAMLIT.md
git add .gitignore
git add app.py

# 5. 初回コミット
git commit -m "Initial commit: Threads Team Dashboard"

# 6. GitHubリポジトリを追加
git remote add origin https://github.com/SeiSato0829/threads-team-dashboard.git

# 7. mainブランチに変更
git branch -M main

# 8. GitHubにプッシュ
git push -u origin main
```

## 認証情報の入力
プッシュ時に以下を入力：
- Username: SeiSato0829
- Password: @Zx7bhh53

## エラーが出た場合

### リポジトリが存在しない場合：
1. https://github.com/new にアクセス
2. Repository name: `threads-team-dashboard`
3. Public を選択
4. Create repository

### 認証エラーの場合：
```bash
# HTTPSでの認証設定
git config --global credential.helper manager
```

## 🎉 プッシュ成功後

1. https://github.com/SeiSato0829/threads-team-dashboard にアクセス
2. コードがアップロードされていることを確認
3. Streamlit Cloudでデプロイ開始！