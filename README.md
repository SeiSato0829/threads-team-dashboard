# Threads 自動投稿システム v3.2

## 概要
SNS（Threads）での反応が高い投稿を参考にしつつ、自社テーマを活かした投稿をAIが生成し、Bufferを通じて予約投稿するシステムです。

## 機能

### 1. 手動投稿
- 500文字以内のテキスト投稿
- 最大4枚の画像アップロード（JPG/PNG/GIF、各5MB以内）
- 投稿ジャンルの指定
- 投稿予定日時の設定（30分後以降）
- AI生成モード（人気投稿を参考に文章改善）

### 2. CSV一括アップロード
- Easy Scraperから取得したCSVファイルをアップロード
- いいね数で上位10件を自動抽出
- 重複削除機能
- プレビュー表示
- 一括投稿候補生成

### 3. 投稿管理ダッシュボード
- ステータス別の投稿統計
- フィルタリング・検索機能
- 投稿の編集・削除
- ソート機能（投稿予定日時/作成日時）

## 起動方法

### 方法1: ビルド済みファイルを直接開く（推奨）
1. エクスプローラーで `threads-auto-post` フォルダを開く
2. `dist` フォルダ内の `index.html` をダブルクリックして開く
3. ブラウザで自動的にアプリケーションが起動します

### 方法2: 開発サーバーを使用
```bash
# プロジェクトディレクトリに移動
cd threads-auto-post

# 依存関係をインストール（初回のみ）
npm install

# 開発サーバーを起動
npm run dev
```

### 方法3: ビルドして実行
```bash
# ビルド
npm run build

# distフォルダ内のindex.htmlを開く
```

## 使い方

### 手動投稿の作成
1. 「手動投稿」タブをクリック
2. 投稿テキストを入力（500文字以内）
3. 必要に応じて画像をアップロード
4. 投稿ジャンルを入力
5. 投稿希望日時を選択
6. AI生成モードを使用する場合はチェック
7. 「投稿を予約」ボタンをクリック

### CSV投稿の処理
1. 「CSV投稿」タブをクリック
2. CSVファイルをドラッグ&ドロップまたは選択
3. 処理オプションを設定（上位N件、重複削除）
4. プレビューを確認
5. 「データを処理して投稿候補を生成」をクリック

### 投稿の管理
1. 「投稿管理」タブをクリック
2. 投稿一覧から編集・削除が可能
3. フィルタリングやソート機能で投稿を整理

## 技術仕様
- React 18 + TypeScript
- Vite（ビルドツール）
- Tailwind CSS（スタイリング）
- React Hook Form（フォーム管理）
- Lucide React（アイコン）
- date-fns（日付処理）

## 注意事項
- 投稿は予定時刻の15分前にBufferに送信されます
- 実際の投稿にはBuffer APIとClaude APIの設定が必要です
- 現在はフロントエンドのみの実装です

## ライセンス
このプロジェクトは要件定義書v3.2に基づいて開発されています。