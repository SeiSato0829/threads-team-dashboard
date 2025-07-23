# 🚀 Streamlit Cloud デプロイ完全ガイド

## 📋 デプロイ前チェックリスト

✅ 必要なファイル:
- [x] `THREADS_DASHBOARD.py` - メインアプリ
- [x] `requirements_streamlit.txt` - 依存関係
- [x] `.streamlit/config.toml` - 設定ファイル
- [x] `README_STREAMLIT.md` - ドキュメント
- [x] `.gitignore` - 除外設定
- [x] サンプルデータベース（.db files）

## 🎯 ステップバイステップ手順

### 1️⃣ GitHubリポジトリ作成

1. [GitHub.com](https://github.com) にログイン
2. 右上の「+」→「New repository」
3. 設定:
   - Repository name: `threads-team-dashboard`
   - Description: 「Threads投稿管理 - チーム共有・モバイル対応」
   - Public（無料プランの場合）
   - ✅ Add a README file
4. 「Create repository」

### 2️⃣ コードをGitHubにプッシュ

```bash
# ローカルで実行（Git Bash推奨）
cd /mnt/c/Users/music-020/threads-auto-post

# Gitリポジトリ初期化
git init

# ファイルを追加
git add THREADS_DASHBOARD.py
git add requirements_streamlit.txt
git add .streamlit/
git add *.db  # 軽量サンプルDB
git add threads_simple_automation.py
git add README_STREAMLIT.md
git add .gitignore

# コミット
git commit -m "Initial commit: Threads Dashboard for Streamlit Cloud"

# リモート追加（YOUR_USERNAMEを置き換え）
git remote add origin https://github.com/YOUR_USERNAME/threads-team-dashboard.git

# プッシュ
git push -u origin main
```

### 3️⃣ Streamlit Cloudでデプロイ

1. [share.streamlit.io](https://share.streamlit.io) にアクセス
2. 「New app」をクリック
3. 設定:
   - Repository: `YOUR_USERNAME/threads-team-dashboard`
   - Branch: `main`
   - Main file path: `THREADS_DASHBOARD.py`
4. 「Deploy!」をクリック

### 4️⃣ Secrets設定（重要！）

デプロイ後、アプリの設定画面で:

1. 「Settings」→「Secrets」
2. 以下を追加:

```toml
[database]
db_path = "threads_optimized.db"

[security]
admin_password = "your-secure-password-here"
team_passwords = ["team123", "member456"]

[app]
company_name = "Your Company"
timezone = "Asia/Tokyo"
```

### 5️⃣ カスタムドメイン設定（オプション）

1. Settings → General
2. Custom subdomain: `threads-team`
3. 結果: `https://threads-team.streamlit.app`

## 🎉 デプロイ完了！

### アクセスURL
```
https://YOUR_APP_NAME.streamlit.app
```

### 共有方法
1. **社内PC**: ブラウザでURL入力
2. **スマホ**: QRコード生成してスキャン
3. **チーム**: SlackやメールでURL共有

## 🔧 トラブルシューティング

### エラー: ModuleNotFoundError
→ `requirements_streamlit.txt` を確認

### エラー: Database not found
→ サンプルDBファイルがコミットされているか確認

### エラー: Authentication failed
→ Secrets設定を確認

### アプリが起動しない
→ ログを確認（Manage app → Logs）

## 📱 モバイルアクセステスト

1. スマホのブラウザでURL開く
2. ホーム画面に追加（PWA対応）
3. チーム全員でテスト

## 🚀 アップデート方法

```bash
# 変更をコミット
git add .
git commit -m "Update: 新機能追加"
git push

# 自動的にStreamlit Cloudが再デプロイ！
```

## 🎯 成功のポイント

1. **シンプルに始める** - 最小構成でデプロイ
2. **段階的に機能追加** - 動作確認しながら
3. **チームでテスト** - 全員でアクセス確認
4. **フィードバック収集** - 改善を継続

## 🌟 完了後の次のステップ

1. チーム全員にURL共有
2. 使い方説明会の実施
3. フィードバック収集
4. 機能改善の継続

---

**🎉 おめでとうございます！**
社内チーム共有・モバイル対応システムがクラウドで稼働開始です！