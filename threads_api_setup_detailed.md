# 📱 Threads API 詳細設定ガイド

## 🚨 重要な前提条件

**2024年7月時点で、Threads APIには以下の制限があります：**

1. **ビジネス認証が必要**
   - 個人アカウントでは利用不可
   - ビジネス認証済みのアカウントが必要

2. **アクセス制限**
   - 現在は限定的なベータ版
   - 全てのユーザーが利用できるわけではない

## 📋 Meta for Developersでの設定手順

### ステップ1: アプリの作成

1. **Meta for Developersにログイン**
   - https://developers.facebook.com
   - 右上の「マイアプリ」をクリック

2. **「アプリを作成」をクリック**
   - アプリタイプを選択する画面が表示されます

3. **アプリタイプの選択**
   - 「ビジネス」を選択
   - 「次へ」をクリック

4. **アプリ情報の入力**
   - アプリ表示名: `Threads Auto Poster`（任意）
   - アプリの連絡先メールアドレス: あなたのメール
   - 「アプリを作成」をクリック

### ステップ2: 基本設定

1. **アプリダッシュボードが開きます**
   - 左側のメニューから「設定」→「ベーシック」

2. **アプリIDとapp secretをメモ**
   - アプリID: 数字の羅列
   - app secret: 「表示」をクリックして確認

### ステップ3: Threads APIを探す

⚠️ **現在の状況（2024年7月）:**

Threads APIは以下のいずれかの状態です：

#### A. 製品として表示される場合
1. 左メニューの「製品を追加」をクリック
2. 「Threads」または「Threads API」を探す
3. 「設定」をクリック

#### B. 表示されない場合（最も一般的）
**Threads APIはまだ一般公開されていません。**

代わりに以下の方法を使用できます：

## 🔄 代替案：Instagram Basic Display APIを使用

### なぜInstagram APIを使うのか？
- ThreadsはInstagramアカウントと連携している
- Instagram APIを通じて一部の機能にアクセス可能

### 設定手順：

1. **Instagram Basic Display APIを追加**
   - 「製品を追加」→「Instagram Basic Display」
   - 「設定」をクリック

2. **アプリの設定**
   - 有効なOAuth リダイレクトURI: `https://localhost:8000/auth/`
   - 認証解除コールバックURL: `https://localhost:8000/deauth/`
   - データ削除リクエストURL: `https://localhost:8000/delete/`

3. **アプリレビュー**
   - 「アプリレビュー」→「リクエスト」
   - 必要な権限をリクエスト

## 🛠️ 現実的な実装方法

### オプション1: 公式APIの代わりにWebスクレイピング

既にプロジェクトに含まれている`auto_post_scheduler.py`はSeleniumを使用した自動投稿を実装しています。

### オプション2: Buffer/Hootsuiteなどのサードパーティツール

プロジェクトには既にBuffer APIの設定があります：
- `BUFFER_ACCESS_TOKEN`
- `BUFFER_PROFILE_ID`

### オプション3: Threads Web版の自動化

```python
# 既存のauto_post_scheduler.pyを使用
python auto_post_scheduler.py
```

## 📝 推奨される次のステップ

1. **Seleniumベースの自動投稿を使用**
   - 既に実装済み
   - Threads APIの代替として機能

2. **Buffer APIを設定**
   - https://buffer.com でアカウント作成
   - APIトークンを取得
   - .envファイルに設定

3. **手動でThreads APIのアクセスを申請**
   - https://developers.facebook.com/docs/threads-api
   - アクセスリクエストフォームを探す（利用可能な場合）

## 🔍 Threads API利用可能性の確認方法

1. **Metaのドキュメントを確認**
   - https://developers.facebook.com/docs/

2. **Threads公式発表をフォロー**
   - @threads on Threads
   - Meta for Developersブログ

3. **コミュニティフォーラム**
   - Stack Overflow
   - Meta Developer Community

## ⚡ 即座に使える代替実装

プロジェクトには既に以下が含まれています：

1. **Seleniumベースの自動投稿**
   ```bash
   python auto_post_scheduler.py
   ```

2. **手動投稿用ダッシュボード**
   ```bash
   streamlit run THREADS_DASHBOARD.py
   ```

これらを使用すれば、公式APIを待たずに自動投稿システムを構築できます。