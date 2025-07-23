# Threads自動投稿システム v3.2 - 完全版

## 概要
Threads（Twitter）の自動投稿システムです。AI（Claude）を使用して多様性のある投稿を生成し、Buffer APIを通じてスケジュール投稿を行います。

## 主な機能

### 📝 投稿機能
- **AI投稿生成**: Claude APIを使用したインテリジェントな投稿生成
- **多様性管理**: 重複投稿の防止と多様性の確保
- **手動投稿**: 即座に投稿を作成・編集
- **CSV一括投稿**: CSVファイルから複数の投稿を一括処理

### 🤖 自動化機能
- **自動スクレイピング**: 8時間ごとに人気投稿を収集
- **自動投稿**: 設定した間隔で投稿を自動実行
- **時間制御**: 投稿時間帯の制限（例：9:00-21:00）
- **投稿数制限**: 1日あたりの投稿数制限

### 📊 管理機能
- **投稿管理**: 投稿履歴の確認・編集・削除
- **ダッシュボード**: 統計情報とシステム状態の確認
- **スケジュール管理**: 投稿予定の管理
- **履歴追跡**: スクレイピングと投稿の履歴管理

## 技術スタック

### フロントエンド
- **React 19** + **TypeScript**
- **Vite** (開発・ビルドツール)
- **Tailwind CSS** (スタイリング)
- **Lucide React** (アイコン)

### バックエンド
- **Python 3.8+**
- **Flask** (Web API)
- **SQLite** (データベース)
- **Claude API** (AI投稿生成)
- **Buffer API** (投稿スケジュール)

### 多様性システム
- **PostDiversityManager**: 投稿の多様性を管理
- **EnhancedPostGenerator**: 高度な投稿生成

## インストール

### 1. 依存関係のインストール

#### Python依存関係
```bash
pip install flask flask-cors anthropic requests pandas schedule
```

#### Node.js依存関係
```bash
npm install
```

### 2. 環境設定
設定ファイルを作成し、APIキーを設定してください：

```json
{
  "CLAUDE_API_KEY": "your-claude-api-key",
  "BUFFER_ACCESS_TOKEN": "your-buffer-token",
  "BUFFER_PROFILE_ID": "your-buffer-profile-id"
}
```

## 起動方法

### 簡単起動（推奨）
```bash
# Windows
start_system.bat

# Linux/Mac
./start_system.sh
```

### 手動起動
```bash
# バックエンド起動
python complete_backend_server_final.py

# フロントエンド起動（別ターミナル）
npm run dev
```

## 使用方法

### 1. 初期設定
1. ブラウザで http://localhost:5173 にアクセス
2. 「設定」タブでAPIキーを設定
   - Claude API Key
   - Buffer Access Token
   - Buffer Profile ID

### 2. 手動投稿
1. 「手動投稿」タブを選択
2. 投稿内容を入力
3. AI生成または手動作成
4. 投稿を保存・スケジュール

### 3. CSV一括投稿
1. 「CSV投稿」タブを選択
2. CSVファイルをアップロード
3. 自動処理を実行
4. 生成された投稿を確認

### 4. 自動化設定
1. 「自動投稿」タブを選択
2. 自動化を開始
3. 投稿間隔・時間帯を設定
4. システムが自動で投稿を実行

## API設定

### Claude API
1. https://console.anthropic.com でアカウント作成
2. API Keyを生成
3. 月額使用料: $6-$23（使用量による）

### Buffer API
1. https://buffer.com でアカウント作成
2. Threadsアカウントを連携
3. https://publish.buffer.com/account/apps でアプリ作成
4. Access TokenとProfile IDを取得
5. 月額使用料: $5（Buffer Pro）

## ファイル構成

```
threads-auto-post/
├── complete_backend_server_final.py    # バックエンドサーバー
├── post_diversity_manager.py           # 多様性管理システム
├── enhanced_post_generator.py          # 投稿生成システム
├── start_system.py                     # 起動スクリプト（Python）
├── start_system.bat                    # 起動スクリプト（Windows）
├── start_system.sh                     # 起動スクリプト（Linux/Mac）
├── src/
│   ├── App-Final.tsx                   # メインアプリケーション
│   ├── services/api-fixed.ts           # API接続サービス
│   ├── components/                     # React コンポーネント
│   └── types/                          # TypeScript型定義
├── csv_input/                          # CSVファイル投入フォルダ
├── csv_processed/                      # 処理済みCSVフォルダ
├── uploads/                            # 画像アップロードフォルダ
├── threads_auto_post.db                # SQLiteデータベース
└── threads_auto_post.log               # ログファイル
```

## 多様性システム

### 機能
- **絵文字パターン**: 50種類以上の絵文字セット
- **CTAバリエーション**: 15種類のCall to Action
- **投稿スタイル**: 8種類の投稿パターン
- **重複検出**: ハッシュベースの重複防止
- **自動再生成**: 重複時の自動再生成

### 投稿スタイル
1. **ストーリーテリング型**: 体験談形式
2. **疑問提起型**: 質問形式
3. **リスト・ティップス型**: 箇条書き形式
4. **比較・対比型**: 比較分析形式
5. **引用・名言型**: 引用を活用
6. **データ・統計型**: 数値を活用
7. **トレンド分析型**: 最新情報を活用
8. **個人的見解型**: 個人の意見を表現

## データベース構造

### テーブル
- **posts**: 投稿データ
- **company_concepts**: 自社構想
- **settings**: システム設定
- **scraping_history**: スクレイピング履歴
- **statistics**: 統計情報

## API エンドポイント

### 基本API
- `GET /` - ヘルスチェック
- `GET /api/dashboard/stats` - ダッシュボード統計
- `GET /api/scraping/history` - スクレイピング履歴

### 投稿API
- `GET /api/posts` - 投稿一覧取得
- `POST /api/posts` - 投稿作成
- `PUT /api/posts/<id>` - 投稿更新
- `DELETE /api/posts/<id>` - 投稿削除

### 自動化API
- `POST /api/automation/start` - 自動化開始
- `POST /api/automation/stop` - 自動化停止
- `POST /api/scraping/trigger` - スクレイピング実行

### 投稿生成API
- `POST /api/generate-post` - AI投稿生成
- `POST /api/process-csv` - CSV処理

## トラブルシューティング

### よくある問題

#### 1. サーバーが起動しない
- Python依存関係を確認
- ポート5000/5173が使用中でないか確認
- ログファイルを確認

#### 2. フロントエンドが表示されない
- Node.js依存関係を確認（npm install）
- ブラウザキャッシュをクリア
- 開発者ツールでエラーを確認

#### 3. API接続エラー
- Claude API Keyが正しく設定されているか確認
- Buffer API Tokenが有効か確認
- ネットワーク接続を確認

#### 4. 投稿が重複する
- 多様性システムが有効か確認
- データベースの重複チェック機能を確認
- 投稿生成の温度設定を調整

### ログファイル
システムの動作状況は以下のファイルで確認できます：
- `threads_auto_post.log`: 全般的なログ
- ブラウザ開発者ツール: フロントエンドログ

## セキュリティ

### 注意事項
- APIキーは環境変数で管理
- データベースファイルのバックアップを定期的に取得
- 投稿内容の事前確認を推奨
- 自動化の投稿数制限を適切に設定

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## サポート

問題が発生した場合は、以下の情報を含めてお問い合わせください：
1. エラーメッセージ
2. ログファイルの内容
3. 実行環境（OS、Python/Node.jsバージョン）
4. 実行手順

## 更新履歴

### v3.2.0（最新）
- 多様性システムの完全実装
- 自動化機能の強化
- エラーハンドリングの改善
- 起動スクリプトの追加
- ダッシュボード機能の強化

### v3.1.0
- React 19対応
- TypeScript型安全性の向上
- API接続の安定化

### v3.0.0
- 全面的なリニューアル
- 多様性管理システムの導入
- Claude APIの完全統合