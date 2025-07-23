# 🚀 Threads公式API設定ガイド（2025年版）

## 📊 重要な変更点

Buffer APIは2019年から新規登録を停止しているため、**Threads公式API**を使用します。

## 🔧 セットアップ手順

### ステップ1: Meta開発者アカウント作成

1. https://developers.facebook.com にアクセス
2. 「Get Started」をクリック
3. Facebookアカウントでログイン
4. 開発者アカウントを作成

### ステップ2: アプリ作成

1. 「My Apps」→「Create App」
2. アプリタイプ：「Business」を選択
3. アプリ名：「Threads Auto Post」など
4. 作成完了

### ステップ3: Threads APIを有効化

1. アプリダッシュボードで「Add Product」
2. 「Threads」を探して「Set Up」
3. 必要な権限を設定：
   - threads_basic
   - threads_content_publish
   - threads_manage_insights

### ステップ4: アクセストークン取得

1. 「Tools」→「Access Token Tool」
2. 必要な権限を選択
3. 「Generate Token」をクリック
4. トークンをコピー

### ステップ5: .envファイル設定

```env
# Claude AI設定
CLAUDE_MODEL=claude-sonnet-4-20250514

# Threads API設定（Buffer APIの代わり）
THREADS_ACCESS_TOKEN=YOUR_THREADS_ACCESS_TOKEN_HERE
THREADS_USER_ID=YOUR_THREADS_USER_ID_HERE

# Buffer API設定（使用しない）
BUFFER_ACCESS_TOKEN=
BUFFER_PROFILE_ID=
```

## 📝 APIの制限事項

- **投稿数**: 24時間で250投稿まで
- **返信数**: 24時間で1000返信まで
- **文字数**: 1投稿500文字まで
- **画像**: JPEG/PNG形式
- **動画**: 最大5分

## 🔄 システム修正が必要な箇所

現在のシステムはBuffer API用に作られているため、以下の修正が必要です：

1. バックエンドのAPI呼び出し部分をThreads APIに変更
2. エンドポイントURLの変更
3. 認証方法の変更
4. レスポンス形式の対応

## 💡 代替案

### 方法1: 半自動化（推奨）

現在のシステムをそのまま使用し：
1. Claude APIで投稿内容を自動生成
2. 生成された内容をコピー
3. Threadsアプリに手動で投稿

**メリット:**
- システム修正不要
- すぐに使える
- API制限なし

### 方法2: システム改修

Threads APIに対応するようバックエンドを修正。
（技術的な知識が必要）

### 方法3: 既存ツール利用

- Hootsuite（月額$49〜）
- Sprout Social（月額$199〜）

これらは既にThreads APIに対応済み。

## 🎯 推奨する進め方

1. **まずは半自動化で運用開始**
   - Claude APIだけ設定
   - 投稿内容を自動生成
   - 手動でThreadsに投稿

2. **運用が軌道に乗ったら**
   - Threads API対応を検討
   - または有料ツールを導入

この方法なら、今すぐ始められます！