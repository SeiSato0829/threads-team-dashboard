# 🚀 究極のThreads AI自動投稿システム セットアップガイド

## 概要
このシステムは、Threadsの投稿を完全自動化し、AIが高エンゲージメント投稿を学習・生成・投稿まで行う究極のシステムです。

## 🎯 システムの特徴

### 1. リアルタイムエンゲージメント追跡
- 30分ごとに投稿のパフォーマンスを自動チェック
- 高エンゲージメント投稿（5%以上）を自動検出
- パターンを学習してデータベースに蓄積

### 2. AI投稿生成エンジン
- 高パフォーマンス投稿のパターンを分析
- 絵文字、キーワード、構造を学習
- OpenAI/Claude APIで自然な投稿を生成

### 3. 完全自動投稿
- 最適な時間（7時、12時半、19時、21時）に自動投稿
- 1日最大4投稿まで
- 最低3時間の間隔を確保

### 4. スプレッドシート連携
- エンゲージメントデータを自動エクスポート
- Google Sheetsで分析可能

## 📋 セットアップ手順

### 1. 環境変数の設定

`.env`ファイルを作成し、以下を設定：

```env
# Threads認証情報
THREADS_USERNAME=あなたのユーザー名
THREADS_PASSWORD=あなたのパスワード

# AI API（どちらか1つ必須）
OPENAI_API_KEY=your_openai_api_key
CLAUDE_API_KEY=your_claude_api_key

# オプション
THREADS_API_TOKEN=your_threads_api_token
```

### 2. 依存関係のインストール

```bash
# Python依存関係
pip install -r requirements_ai.txt

# Node.js依存関係
npm install

# Chrome WebDriverのインストール
python -m webdriver_manager.chrome
```

### 3. システムの起動

```bash
# Windows
START_ULTIMATE_SYSTEM.bat

# または個別に起動
python realtime_engagement_tracker.py  # エンゲージメント監視
python auto_post_scheduler.py          # 自動投稿
python ultimate_ai_post_engine.py      # AI生成（単発実行）
```

## 🔧 カスタマイズ

### 投稿トピックの変更

`auto_post_scheduler.py`の`all_topics`リストを編集：

```python
all_topics = [
    "あなたのビジネステーマ1",
    "あなたのビジネステーマ2",
    # ...
]
```

### 投稿頻度の調整

`auto_post_scheduler.py`で調整：

```python
self.daily_post_limit = 4  # 1日の最大投稿数
self.min_interval_hours = 3  # 最小投稿間隔（時間）
```

### エンゲージメント閾値の変更

`realtime_engagement_tracker.py`で調整：

```python
# 高パフォーマンス判定（デフォルト5%）
is_high_performer = post['engagement_rate'] >= 0.05
```

## 📊 データ分析

### エンゲージメントデータの確認

```sql
-- SQLiteデータベースに接続
sqlite3 threads_auto_post.db

-- 高パフォーマンス投稿を表示
SELECT content, engagement_rate, likes, comments
FROM engagement_history
WHERE is_high_performer = 1
ORDER BY engagement_rate DESC;

-- 学習データを確認
SELECT pattern_type, pattern_value, success_rate
FROM learning_data
ORDER BY success_rate DESC
LIMIT 20;
```

### CSVエクスポート

毎日9時に自動でCSVがエクスポートされます。
手動でエクスポートする場合：

```python
from realtime_engagement_tracker import RealtimeEngagementTracker
tracker = RealtimeEngagementTracker()
tracker.export_to_spreadsheet()
```

## ⚡ トラブルシューティング

### Seleniumエラー
- ChromeDriverが古い場合は更新
- `chrome_options.add_argument('--headless')`をコメントアウトしてデバッグ

### API制限
- OpenAI/Claude APIの利用制限に注意
- レート制限エラーが出た場合は投稿頻度を調整

### ログイン失敗
- 2段階認証を一時的に無効化
- またはSeleniumのheadlessモードを無効にして手動ログイン

## 🎉 完了！

これで究極のAI自動投稿システムが稼働します！
高エンゲージメント投稿を自動学習し、最適なタイミングで投稿を続けます。

質問や問題があれば、issueを作成してください。