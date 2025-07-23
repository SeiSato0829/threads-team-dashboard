# 🔧 Threads API 実装ガイド

## 📋 現在の状況
あなたのプロジェクトには既にClaude APIキーが設定されています：
- `CLAUDE_API_KEY`: 設定済み ✅
- `CLAUDE_MODEL`: claude-sonnet-4-20250514 ✅

## 🚀 Threads API連携の手順

### ステップ1: Meta for Developersでアプリ作成

1. **Meta for Developersにアクセス**
   - URL: https://developers.facebook.com
   - Facebookアカウントでログイン

2. **新規アプリ作成**
   - 「マイアプリ」→「アプリを作成」
   - タイプ：「ビジネス」を選択
   - アプリ名：「Threads Auto Poster」（任意）

3. **必要な権限を設定**
   - threads_basic
   - threads_publish_posts
   - threads_manage_insights

### ステップ2: アクセストークン取得

1. **Graph API Explorer**を使用
   - https://developers.facebook.com/tools/explorer/
   - アプリを選択
   - 「User Token」を生成

2. **長期アクセストークンに変換**
   ```
   https://graph.facebook.com/v18.0/oauth/access_token?
   grant_type=fb_exchange_token&
   client_id={app-id}&
   client_secret={app-secret}&
   fb_exchange_token={short-lived-token}
   ```

### ステップ3: 環境変数の設定

`.env`ファイルに以下を追加：

```env
# Threads API設定
THREADS_ACCESS_TOKEN=your_long_lived_access_token
THREADS_USER_ID=your_threads_user_id
META_APP_ID=your_meta_app_id
META_APP_SECRET=your_meta_app_secret
```

### ステップ4: ユーザーIDの取得

```bash
curl -X GET "https://graph.threads.net/v1.0/me?fields=id,username&access_token={access-token}"
```

## ⚠️ 重要な注意事項

1. **API制限**
   - 1時間あたり200リクエスト
   - 1日あたり1000リクエスト

2. **投稿制限**
   - 1日最大25投稿
   - 最小投稿間隔：5分

3. **セキュリティ**
   - アクセストークンは絶対に公開しない
   - `.env`ファイルは`.gitignore`に追加済み

## 📝 次のステップ

環境変数を設定したら、以下のコマンドでテスト：

```bash
python test_threads_connection.py
```

問題がなければ、ダッシュボードが自動的にあなたのThreadsアカウントと連携します。