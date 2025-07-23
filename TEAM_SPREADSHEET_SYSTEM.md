# 📊 Threads投稿 チーム共同管理システム

## 🚀 スプレッドシートで完璧なチーム管理

### システム概要

**1つのスプレッドシートで全てを管理**
- 投稿スケジュール
- 担当者割り当て
- パフォーマンス分析
- リアルタイム同期

## 📋 スプレッドシート構成

### シート1: 📅 投稿カレンダー

| 列 | 項目 | 説明 | 自動化 |
|---|------|------|--------|
| A | 日付 | 投稿日 | 自動入力 |
| B | 時間 | 投稿時刻 | 最適時間を提案 |
| C | 曜日 | 曜日表示 | 自動計算 |
| D | 担当者 | 投稿担当 | ドロップダウン |
| E | 投稿内容 | 本文 | AI生成ボタン |
| F | ハッシュタグ | タグ | 自動提案 |
| G | ステータス | 進捗 | 色分け自動 |
| H | 投稿URL | Threads URL | 自動取得 |
| I | いいね数 | エンゲージメント | 自動更新 |
| J | コメント数 | エンゲージメント | 自動更新 |
| K | シェア数 | エンゲージメント | 自動更新 |
| L | メモ | 備考 | 自由記入 |

### シート2: 👥 チームメンバー

| 列 | 項目 | 説明 |
|---|------|------|
| A | メンバー名 | 担当者リスト |
| B | 役割 | 管理者/投稿者/分析者 |
| C | 担当曜日 | 月火水木金土日 |
| D | 投稿数/週 | ノルマ管理 |
| E | 達成率 | 自動計算 |

### シート3: 📊 分析ダッシュボード

- 週間パフォーマンス
- 時間帯別エンゲージメント
- 担当者別成績
- トレンド分析

### シート4: 💡 アイデアバンク

| 列 | 項目 | 説明 |
|---|------|------|
| A | 提案者 | アイデア提供者 |
| B | カテゴリ | テーマ分類 |
| C | 内容案 | 投稿アイデア |
| D | 優先度 | 高/中/低 |
| E | 使用済み | チェックボックス |

## 🔧 Google Apps Script (GAS) 自動化機能

### 1. 投稿内容の自動生成

```javascript
function generatePost() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const row = sheet.getActiveCell().getRow();
  
  // 日付と時間を取得
  const date = sheet.getRange(row, 1).getValue();
  const time = sheet.getRange(row, 2).getValue();
  const dayOfWeek = sheet.getRange(row, 3).getValue();
  
  // Claude APIを呼び出し（実際はWebhook経由）
  const prompt = `${dayOfWeek}の${time}に投稿する魅力的な内容を生成`;
  const content = callClaudeAPI(prompt);
  
  // セルに入力
  sheet.getRange(row, 5).setValue(content);
  
  // ハッシュタグも自動生成
  const hashtags = generateHashtags(dayOfWeek, time);
  sheet.getRange(row, 6).setValue(hashtags);
}

// カスタムメニューに追加
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🤖 Threads管理')
    .addItem('投稿を生成', 'generatePost')
    .addItem('週間スケジュール作成', 'createWeeklySchedule')
    .addItem('パフォーマンス更新', 'updatePerformance')
    .addItem('レポート作成', 'createReport')
    .addToUi();
}
```

### 2. ステータスの自動更新と通知

```javascript
function updateStatus() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('投稿カレンダー');
  const dataRange = sheet.getDataRange();
  const values = dataRange.getValues();
  
  const now = new Date();
  
  for (let i = 1; i < values.length; i++) {
    const scheduledDate = new Date(values[i][0] + ' ' + values[i][1]);
    const status = values[i][6];
    const assignee = values[i][3];
    
    // 投稿時間が過ぎている場合
    if (scheduledDate < now && status === '予定') {
      sheet.getRange(i + 1, 7).setValue('遅延');
      sheet.getRange(i + 1, 7).setBackground('#ff9999');
      
      // 担当者に通知
      sendNotification(assignee, '投稿が遅延しています！');
    }
    
    // 30分前リマインダー
    const thirtyMinBefore = new Date(scheduledDate.getTime() - 30 * 60000);
    if (now > thirtyMinBefore && now < scheduledDate && status === '予定') {
      sendNotification(assignee, '30分後に投稿予定です');
    }
  }
}

// 1時間ごとに実行
function setupTriggers() {
  ScriptApp.newTrigger('updateStatus')
    .timeBased()
    .everyHours(1)
    .create();
}
```

### 3. パフォーマンスの自動取得

```javascript
function updatePerformance() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('投稿カレンダー');
  const lastRow = sheet.getLastRow();
  
  for (let i = 2; i <= lastRow; i++) {
    const url = sheet.getRange(i, 8).getValue();
    const status = sheet.getRange(i, 7).getValue();
    
    if (url && status === '投稿済み') {
      // Threads APIからデータ取得（実装例）
      const stats = getThreadsStats(url);
      
      sheet.getRange(i, 9).setValue(stats.likes);
      sheet.getRange(i, 10).setValue(stats.comments);
      sheet.getRange(i, 11).setValue(stats.shares);
      
      // 高パフォーマンス投稿をハイライト
      if (stats.likes > 100) {
        sheet.getRange(i, 1, 1, 12).setBackground('#c6efce');
      }
    }
  }
  
  // ダッシュボード更新
  updateDashboard();
}
```

## 📱 スマホからの使い方

### Googleスプレッドシートアプリ

1. **投稿時**
   - アプリを開く
   - 今日の日付を探す
   - ステータスを「投稿済み」に変更
   - URLを貼り付け

2. **アイデア追加**
   - 「アイデアバンク」シートへ
   - 新規行追加
   - アイデアを入力

## 🎯 役割分担の例

### 管理者（1名）
- 月間スケジュール作成
- パフォーマンス分析
- 改善策の立案

### 投稿担当者（3-5名）
- 割り当てられた投稿を実行
- ステータス更新
- 簡易レポート

### 分析担当者（1名）
- エンゲージメント分析
- レポート作成
- 改善提案

## 🚀 導入手順

### ステップ1: テンプレートをコピー

1. [テンプレートURL]にアクセス
2. 「ファイル」→「コピーを作成」
3. チーム用の名前を付ける

### ステップ2: メンバー追加

1. 右上の「共有」ボタン
2. メンバーのメールアドレスを入力
3. 権限を設定（編集者/閲覧者）

### ステップ3: 初期設定

1. 「チームメンバー」シートに全員追加
2. 担当曜日を決定
3. GASスクリプトを有効化

### ステップ4: 運用開始

1. 月初に管理者がスケジュール作成
2. 各担当者が投稿実行
3. 週次でパフォーマンスレビュー

## 📊 便利な関数集

### 担当者の自動割り当て

```
=INDEX(チームメンバー!A:A,MOD(ROW()-2,COUNTA(チームメンバー!A:A)-1)+2)
```

### エンゲージメント率の計算

```
=IF(I2="","",（I2+J2*2+K2*3)/1000)
```

### 週間パフォーマンス

```
=QUERY(A:K,"SELECT D, COUNT(D), AVG(I), AVG(J), AVG(K) WHERE G='投稿済み' GROUP BY D")
```

## 💡 プロのTips

### 1. 条件付き書式の活用

```
ステータス列：
- "予定" → 黄色
- "投稿済み" → 緑色
- "遅延" → 赤色
- "高パフォーマンス" → 青色
```

### 2. データ検証でミス防止

```
担当者列：ドロップダウンリスト
ステータス列：選択肢制限
日付列：日付形式のみ
```

### 3. フィルタービューで個人管理

各メンバーが自分の担当分だけを表示できるフィルタービューを作成

## 🎉 期待される効果

- **作業効率**: 50%向上
- **投稿品質**: 標準化で安定
- **チーム連携**: スムーズ化
- **分析精度**: データ蓄積で向上

## 📱 おすすめ連携ツール

1. **Slack/Discord**
   - 投稿リマインダー
   - パフォーマンス通知
   - 日次レポート

2. **Zapier/Make**
   - 自動ステータス更新
   - 投稿URLの自動取得
   - 分析データの同期

3. **Looker Studio**
   - 高度な分析ダッシュボード
   - 月次レポート自動生成
   - トレンド予測

これで、チーム全員で効率的にThreads投稿を管理できます！