# 🔐 環境変数（.env）でのAPI設定ガイド

## 📋 概要
セキュリティを重視して、APIキーを環境変数（.env）ファイルで管理する方法を説明します。

## 🚀 設定手順

### ステップ1: .envファイルの作成

プロジェクトのルートディレクトリに `.env` ファイルを作成します：

```bash
# Windows
copy env_example.txt .env

# Linux/Mac
cp env_example.txt .env
```

### ステップ2: APIキーの設定

`.env` ファイルを開いて、以下のように実際のAPIキーを入力します：

```env
# Claude API設定
CLAUDE_API_KEY=sk-ant-api03-実際のAPIキーをここに入力

# Buffer API設定
BUFFER_ACCESS_TOKEN=1/実際のトークンをここに入力
BUFFER_PROFILE_ID=実際のプロファイルIDをここに入力

# その他の設定（オプション）
POST_INTERVAL=60
SCRAPING_INTERVAL=8
DAILY_POST_LIMIT=10
POST_START_TIME=09:00
POST_END_TIME=21:00
```

### ステップ3: 各APIキーの取得方法

#### 🤖 Claude API Key
1. https://console.anthropic.com にアクセス
2. アカウント作成・ログイン
3. 「Settings」→「API Keys」
4. 「Create Key」をクリック
5. 生成されたキーをコピー（`sk-ant-api03-...`）

#### 📱 Buffer API Token & Profile ID
1. https://buffer.com でアカウント作成
2. Threadsアカウントを連携
3. https://publish.buffer.com/account/apps でアプリ作成
4. Access Token（`1/...`）をコピー
5. Profile ID（`5d5a3b2c...`）をコピー

## 📁 ファイル構成

```
threads-auto-post/
├── .env                          # ←ここにAPIキーを設定
├── env_example.txt              # テンプレートファイル
├── complete_backend_server_final.py
└── ...
```

## 🔒 セキュリティ機能

### 自動優先順位
1. **環境変数（.env）** ←最優先
2. データベース設定 ←フォールバック

### 設定確認
起動時にログで確認できます：
```
Claude API初期化成功
Buffer API設定確認済み
```

## 🛡️ セキュリティのメリット

### .envファイルの利点
✅ **Gitにコミットされない**（.gitignoreに追加済み）
✅ **外部に漏洩しない**
✅ **簡単に変更可能**
✅ **環境ごとに異なる設定が可能**

### 従来の方法との比較
| 方法 | セキュリティ | 使いやすさ |
|------|-------------|------------|
| .env | 🔒 高 | 😊 簡単 |
| Web UI | 🔓 低 | 🙂 普通 |
| ハードコード | ❌ 危険 | 😰 危険 |

## 🔄 設定の更新

### .envファイルを変更後
```bash
# サーバーを再起動
python complete_backend_server_final.py
```

### 設定が反映されない場合
1. .envファイルの場所を確認
2. ファイル名が正確か確認（`.env`）
3. APIキーの形式を確認
4. サーバーを再起動

## 💡 よくある質問

### Q: .envファイルはどこに置く？
A: プロジェクトのルートディレクトリ（`complete_backend_server_final.py`と同じ場所）

### Q: APIキーが間違っている場合は？
A: ログに「初期化エラー」と表示されます。キーを再確認してください。

### Q: .envファイルを他人に共有しても大丈夫？
A: **絶対ダメ！** APIキーは個人情報です。

### Q: バックアップは必要？
A: はい。APIキーは再発行が難しい場合があります。

## 🎯 設定例

### 本番環境用
```env
CLAUDE_API_KEY=sk-ant-api03-本番用キー
BUFFER_ACCESS_TOKEN=1/本番用トークン
BUFFER_PROFILE_ID=本番用ID
LOG_LEVEL=WARNING
```

### 開発環境用
```env
CLAUDE_API_KEY=sk-ant-api03-開発用キー
BUFFER_ACCESS_TOKEN=1/開発用トークン
BUFFER_PROFILE_ID=開発用ID
LOG_LEVEL=DEBUG
```

## 🎉 完了後の確認

### 起動ログを確認
```
Claude API初期化成功
Buffer API設定確認済み
サーバー起動: http://localhost:5000
```

### テスト投稿
「手動投稿」タブで短い投稿をテストしてください。

## 🔧 トラブルシューティング

### エラー: "Claude API初期化エラー"
- APIキーの形式確認
- キーの有効性確認
- 料金残高確認

### エラー: "Buffer API error"
- トークンの有効性確認
- Profile IDの確認
- Threadsアカウント連携確認

---

**これで完全にセキュアなAPI設定が完了です！**