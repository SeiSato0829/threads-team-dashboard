# 🚀 Buffer API トークン取得ガイド

## 📋 Buffer APIトークン取得手順

### ステップ1: Buffer開発者ページにアクセス

1. **Buffer Developersサイトにアクセス**
   - URL: https://buffer.com/developers/apps
   - Bufferアカウントでログイン

### ステップ2: 新しいアプリを作成

1. **「Create an App」をクリック**

2. **アプリ情報を入力**
   - **App Name**: `Threads Auto Poster`（任意）
   - **Description**: `Automated posting system for Threads`
   - **Website URL**: `http://localhost:8501`（ローカル開発用）
   - **Redirect URI**: `http://localhost:8501/callback`

3. **「Create Application」をクリック**

### ステップ3: アクセストークンを生成

1. **作成したアプリのページで**
   - 「Access Token」セクションを探す
   - 「Create Access Token」ボタンをクリック

2. **パーミッションを確認**
   - 必要な権限にチェックが入っていることを確認
   - 「Authorize」をクリック

3. **アクセストークンが表示される**
   - 長い文字列が表示されます（例：`1/1234567890abcdef...`）
   - **このトークンをコピーして安全に保管**

### ステップ4: Profile IDを取得

1. **Buffer APIエクスプローラーを使用**
   - URL: https://buffer.com/developers/api/profiles
   - または以下のcURLコマンドを実行：

```bash
curl https://api.bufferapp.com/1/profiles.json?access_token=YOUR_ACCESS_TOKEN
```

2. **レスポンスからThreadsプロファイルを探す**
```json
[
  {
    "id": "123456789abcdef",
    "service": "twitter",
    "service_username": "@example"
  },
  {
    "id": "987654321fedcba",  // ← これがProfile ID
    "service": "threads",
    "service_username": "@yourthreadsusername"
  }
]
```

### ステップ5: .envファイルに設定

`.env`ファイルを編集して以下を追加：

```env
# Buffer API設定
BUFFER_ACCESS_TOKEN=1/your-actual-buffer-access-token-here
BUFFER_PROFILE_ID=987654321fedcba
```

## 🧪 接続テスト

設定が完了したら、以下のPythonスクリプトで接続をテスト：

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

access_token = os.getenv('BUFFER_ACCESS_TOKEN')
profile_id = os.getenv('BUFFER_PROFILE_ID')

# プロファイル情報を取得
response = requests.get(
    f"https://api.bufferapp.com/1/profiles/{profile_id}.json",
    params={"access_token": access_token}
)

if response.status_code == 200:
    profile = response.json()
    print(f"✅ 接続成功！")
    print(f"   サービス: {profile['service']}")
    print(f"   ユーザー名: {profile['service_username']}")
else:
    print(f"❌ エラー: {response.status_code}")
    print(response.text)
```

## 📝 Buffer APIでできること

1. **投稿のスケジュール**
   - 最適な時間に自動投稿
   - 複数の投稿を一括スケジュール

2. **投稿の管理**
   - 予約投稿の確認・編集
   - 投稿の削除

3. **分析データの取得**
   - エンゲージメント統計
   - 最適な投稿時間の分析

## ⚠️ 注意事項

1. **APIレート制限**
   - 1時間あたり60リクエスト（無料プラン）
   - 1時間あたり2000リクエスト（有料プラン）

2. **投稿制限**
   - 無料プラン：各プロファイル10件まで
   - 有料プラン：無制限

3. **セキュリティ**
   - アクセストークンは絶対に公開しない
   - `.gitignore`に`.env`が含まれていることを確認

## 🔧 トラブルシューティング

### エラー：「Invalid access token」
- トークンが正しくコピーされているか確認
- トークンの前後に空白がないか確認

### エラー：「Profile not found」
- Profile IDが正しいか確認
- Threadsアカウントが正しく連携されているか確認

### エラー：「Rate limit exceeded」
- APIリクエスト数が制限を超えています
- 1時間待つか、有料プランにアップグレード