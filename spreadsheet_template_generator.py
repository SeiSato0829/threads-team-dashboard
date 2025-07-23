#!/usr/bin/env python3
"""
Googleスプレッドシート用テンプレート生成ツール
チーム管理用の完璧なフォーマットを作成
"""

import csv
import json
from datetime import datetime, timedelta
import os

class SpreadsheetTemplateGenerator:
    def __init__(self):
        self.output_dir = 'spreadsheet_templates'
        os.makedirs(self.output_dir, exist_ok=True)
        
    def create_team_template(self, team_size=5, days=30):
        """チーム用の完全なテンプレートを生成"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 1. 投稿カレンダーシート
        calendar_file = self._create_calendar_sheet(days, team_size)
        
        # 2. チームメンバーシート
        members_file = self._create_members_sheet(team_size)
        
        # 3. 分析ダッシュボード用データ
        dashboard_file = self._create_dashboard_template()
        
        # 4. アイデアバンクシート
        ideas_file = self._create_ideas_bank()
        
        # 5. GASスクリプト
        gas_file = self._create_gas_scripts()
        
        # 6. 設定ガイド
        setup_guide = self._create_setup_guide()
        
        print(f"✅ スプレッドシートテンプレート生成完了！")
        print(f"📁 保存場所: {self.output_dir}")
        
        return {
            'calendar': calendar_file,
            'members': members_file,
            'dashboard': dashboard_file,
            'ideas': ideas_file,
            'scripts': gas_file,
            'guide': setup_guide
        }
    
    def _create_calendar_sheet(self, days, team_size):
        """投稿カレンダーシートを作成"""
        
        headers = [
            '日付', '時間', '曜日', '担当者', '投稿内容', 
            'ハッシュタグ', 'ステータス', '投稿URL', 
            'いいね数', 'コメント数', 'シェア数', 'メモ'
        ]
        
        rows = [headers]
        base_date = datetime.now()
        
        # 投稿時間の定義
        post_times = ['07:30', '12:15', '18:30', '21:00']
        
        # チームメンバー
        members = [f'メンバー{i+1}' for i in range(team_size)]
        member_index = 0
        
        # 曜日名（日本語）
        weekday_names = ['月', '火', '水', '木', '金', '土', '日']
        
        for day in range(days):
            current_date = base_date + timedelta(days=day)
            weekday = weekday_names[current_date.weekday()]
            
            # 週末は投稿数を減らす
            times_to_use = post_times[:3] if current_date.weekday() >= 5 else post_times
            
            for time in times_to_use:
                # 担当者を順番に割り当て
                assignee = members[member_index % len(members)]
                member_index += 1
                
                row = [
                    current_date.strftime('%Y/%m/%d'),  # 日付
                    time,                                # 時間
                    weekday,                             # 曜日
                    assignee,                            # 担当者
                    '',                                  # 投稿内容（空欄）
                    '',                                  # ハッシュタグ（空欄）
                    '予定',                              # ステータス
                    '',                                  # 投稿URL（空欄）
                    '',                                  # いいね数（空欄）
                    '',                                  # コメント数（空欄）
                    '',                                  # シェア数（空欄）
                    ''                                   # メモ（空欄）
                ]
                rows.append(row)
        
        # TSV形式で保存（スプレッドシートに直接貼り付け可能）
        filename = f'{self.output_dir}/01_投稿カレンダー.tsv'
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(rows)
        
        return filename
    
    def _create_members_sheet(self, team_size):
        """チームメンバーシートを作成"""
        
        headers = ['メンバー名', '役割', '担当曜日', '週間ノルマ', '今週の投稿数', '達成率']
        rows = [headers]
        
        # 役割の定義
        roles = ['管理者', '投稿担当', '投稿担当', '分析担当', '投稿担当']
        weekdays = ['月火', '水木', '金', '土', '日']
        
        for i in range(team_size):
            row = [
                f'メンバー{i+1}',
                roles[i % len(roles)],
                weekdays[i % len(weekdays)],
                '10',  # 週間ノルマ
                '=COUNTIFS(投稿カレンダー!D:D,A' + str(i+2) + ',投稿カレンダー!G:G,"投稿済み")',
                '=E' + str(i+2) + '/D' + str(i+2)
            ]
            rows.append(row)
        
        filename = f'{self.output_dir}/02_チームメンバー.tsv'
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(rows)
        
        return filename
    
    def _create_dashboard_template(self):
        """ダッシュボード用のテンプレートを作成"""
        
        dashboard_data = {
            'summary_formulas': {
                '総投稿数': '=COUNTIF(投稿カレンダー!G:G,"投稿済み")',
                '平均いいね数': '=AVERAGE(投稿カレンダー!I:I)',
                '平均コメント数': '=AVERAGE(投稿カレンダー!J:J)',
                '総エンゲージメント': '=SUM(投稿カレンダー!I:K)',
                '投稿達成率': '=COUNTIF(投稿カレンダー!G:G,"投稿済み")/COUNTA(投稿カレンダー!A:A)-1'
            },
            'time_analysis': {
                '時間帯別パフォーマンス': '''=QUERY(投稿カレンダー!A:K,
                    "SELECT B, AVG(I), AVG(J), AVG(K) 
                     WHERE G='投稿済み' 
                     GROUP BY B 
                     ORDER BY B")''',
                '曜日別パフォーマンス': '''=QUERY(投稿カレンダー!A:K,
                    "SELECT C, COUNT(C), AVG(I) 
                     WHERE G='投稿済み' 
                     GROUP BY C")'''
            },
            'member_performance': {
                'メンバー別成績': '''=QUERY(投稿カレンダー!A:K,
                    "SELECT D, COUNT(D), AVG(I), SUM(I) 
                     WHERE G='投稿済み' 
                     GROUP BY D 
                     ORDER BY SUM(I) DESC")'''
            }
        }
        
        # ダッシュボード設定をJSON形式で保存
        filename = f'{self.output_dir}/03_ダッシュボード設定.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def _create_ideas_bank(self):
        """アイデアバンクシートを作成"""
        
        headers = ['提案日', '提案者', 'カテゴリ', '内容案', '優先度', '使用済み', 'メモ']
        
        # サンプルアイデア
        sample_ideas = [
            ['2025/01/15', 'メンバー1', 'モチベーション', '月曜日の朝に読みたい、やる気が出る名言集', '高', 'FALSE', ''],
            ['2025/01/15', 'メンバー2', '生産性', 'ポモドーロテクニックの実践レポート', '中', 'FALSE', ''],
            ['2025/01/15', 'メンバー3', 'ライフハック', '朝のルーティンを1週間続けた結果', '高', 'FALSE', ''],
            ['2025/01/16', 'メンバー1', 'トレンド', '2025年注目のビジネストレンド5選', '中', 'FALSE', ''],
            ['2025/01/16', 'メンバー4', '健康', 'デスクワーカーのための3分ストレッチ', '低', 'FALSE', '']
        ]
        
        rows = [headers] + sample_ideas
        
        filename = f'{self.output_dir}/04_アイデアバンク.tsv'
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(rows)
        
        return filename
    
    def _create_gas_scripts(self):
        """Google Apps Scriptのコード集を生成"""
        
        gas_code = '''// Threads投稿管理システム - GASスクリプト集

// ========== 初期設定 ==========
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🤖 Threads管理')
    .addItem('📝 投稿を生成', 'generatePost')
    .addItem('📅 週間スケジュール作成', 'createWeeklySchedule')
    .addItem('📊 パフォーマンス更新', 'updatePerformance')
    .addItem('📈 レポート作成', 'createReport')
    .addItem('🔔 通知設定', 'setupNotifications')
    .addSeparator()
    .addItem('⚙️ 初期設定', 'initialSetup')
    .addToUi();
}

// ========== 投稿生成機能 ==========
function generatePost() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const row = sheet.getActiveCell().getRow();
  
  if (row < 2) {
    SpreadsheetApp.getUi().alert('データ行を選択してください');
    return;
  }
  
  const date = sheet.getRange(row, 1).getValue();
  const time = sheet.getRange(row, 2).getValue();
  const dayOfWeek = sheet.getRange(row, 3).getValue();
  
  // テーマを決定
  const theme = getThemeForDay(dayOfWeek);
  
  // 投稿内容を生成（実際はWebhook経由でClaude APIを呼ぶ）
  const content = generateContentForTheme(theme, time);
  const hashtags = generateHashtags(theme, dayOfWeek);
  
  // セルに入力
  sheet.getRange(row, 5).setValue(content);
  sheet.getRange(row, 6).setValue(hashtags);
  
  // 生成日時を記録
  sheet.getRange(row, 12).setValue('生成: ' + new Date().toLocaleString());
  
  SpreadsheetApp.getUi().alert('投稿を生成しました！');
}

// ========== 自動ステータス更新 ==========
function updateStatuses() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('投稿カレンダー');
  const dataRange = sheet.getDataRange();
  const values = dataRange.getValues();
  
  const now = new Date();
  const notifications = [];
  
  for (let i = 1; i < values.length; i++) {
    const dateTime = new Date(values[i][0] + ' ' + values[i][1]);
    const status = values[i][6];
    const assignee = values[i][3];
    const content = values[i][4];
    
    // 投稿時間を過ぎた場合
    if (dateTime < now && status === '予定' && content) {
      sheet.getRange(i + 1, 7).setValue('遅延');
      sheet.getRange(i + 1, 7).setBackground('#ffcccc');
      notifications.push({
        type: 'delay',
        assignee: assignee,
        time: values[i][1]
      });
    }
    
    // 30分前アラート
    const thirtyMinBefore = new Date(dateTime.getTime() - 30 * 60000);
    if (now >= thirtyMinBefore && now < dateTime && status === '予定') {
      notifications.push({
        type: 'reminder',
        assignee: assignee,
        time: values[i][1],
        content: content
      });
    }
  }
  
  // 通知を送信
  if (notifications.length > 0) {
    sendNotifications(notifications);
  }
}

// ========== パフォーマンス分析 ==========
function analyzePerformance() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('投稿カレンダー');
  const dashboard = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('ダッシュボード');
  
  // 時間帯別分析
  const timeAnalysis = {};
  const dayAnalysis = {};
  const memberAnalysis = {};
  
  const data = sheet.getDataRange().getValues();
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][6] === '投稿済み') {
      const time = data[i][1];
      const day = data[i][2];
      const member = data[i][3];
      const likes = data[i][8] || 0;
      
      // 集計
      if (!timeAnalysis[time]) timeAnalysis[time] = [];
      if (!dayAnalysis[day]) dayAnalysis[day] = [];
      if (!memberAnalysis[member]) memberAnalysis[member] = [];
      
      timeAnalysis[time].push(likes);
      dayAnalysis[day].push(likes);
      memberAnalysis[member].push(likes);
    }
  }
  
  // 結果をダッシュボードに反映
  updateDashboard(timeAnalysis, dayAnalysis, memberAnalysis);
}

// ========== 週次レポート生成 ==========
function createWeeklyReport() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const reportSheet = ss.insertSheet('週次レポート_' + new Date().toLocaleDateString());
  
  // レポートヘッダー
  reportSheet.getRange('A1').setValue('Threads投稿 週次レポート');
  reportSheet.getRange('A2').setValue('期間: ' + getWeekDateRange());
  
  // サマリー
  reportSheet.getRange('A4').setValue('📊 サマリー');
  reportSheet.getRange('A5:B9').setValues([
    ['総投稿数', '=COUNTIF(投稿カレンダー!G:G,"投稿済み")'],
    ['平均いいね数', '=AVERAGE(投稿カレンダー!I:I)'],
    ['最高いいね数', '=MAX(投稿カレンダー!I:I)'],
    ['総エンゲージメント', '=SUM(投稿カレンダー!I:K)'],
    ['投稿達成率', '=COUNTIF(投稿カレンダー!G:G,"投稿済み")/COUNTIF(投稿カレンダー!G:G,"予定")']
  ]);
  
  // フォーマット設定
  reportSheet.getRange('A1').setFontSize(18).setFontWeight('bold');
  reportSheet.getRange('A4').setFontSize(14).setFontWeight('bold');
  reportSheet.getRange('A5:B9').setBorder(true, true, true, true, true, true);
  
  SpreadsheetApp.getUi().alert('週次レポートを作成しました！');
}

// ========== ヘルパー関数 ==========
function getThemeForDay(dayOfWeek) {
  const themes = {
    '月': 'モチベーション',
    '火': '生産性向上',
    '水': 'ウェルネス',
    '木': '学習・成長',
    '金': '振り返り',
    '土': 'ライフスタイル',
    '日': '新週準備'
  };
  return themes[dayOfWeek] || 'ビジネス';
}

function generateContentForTheme(theme, time) {
  // 実際はClaude APIを使用
  const templates = {
    'モチベーション': '新しい週の始まり！今週の目標を1つ決めて、小さな一歩から始めてみませんか？',
    '生産性向上': 'タスク管理のコツ：大きな仕事は15分単位に分割すると、驚くほど進みます📝',
    'ウェルネス': '水曜日のリフレッシュタイム。深呼吸を3回して、心をリセットしましょう🧘'
  };
  return templates[theme] || '今日も素晴らしい1日を！';
}

function generateHashtags(theme, dayOfWeek) {
  const baseHashtags = '#Threads #ビジネス';
  const themeHashtags = {
    'モチベーション': '#月曜日 #やる気 #目標達成',
    '生産性向上': '#仕事術 #効率化 #タイムマネジメント',
    'ウェルネス': '#健康 #メンタルヘルス #セルフケア'
  };
  return baseHashtags + ' ' + (themeHashtags[theme] || '#ライフハック');
}

// ========== 自動実行の設定 ==========
function setupTriggers() {
  // 既存のトリガーを削除
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => ScriptApp.deleteTrigger(trigger));
  
  // ステータス更新（1時間ごと）
  ScriptApp.newTrigger('updateStatuses')
    .timeBased()
    .everyHours(1)
    .create();
  
  // パフォーマンス分析（毎日午前2時）
  ScriptApp.newTrigger('analyzePerformance')
    .timeBased()
    .atHour(2)
    .everyDays(1)
    .create();
  
  // 週次レポート（毎週月曜日午前9時）
  ScriptApp.newTrigger('createWeeklyReport')
    .timeBased()
    .onWeekDay(ScriptApp.WeekDay.MONDAY)
    .atHour(9)
    .create();
  
  SpreadsheetApp.getUi().alert('自動実行を設定しました！');
}
'''
        
        filename = f'{self.output_dir}/05_GASスクリプト.js'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(gas_code)
        
        return filename
    
    def _create_setup_guide(self):
        """セットアップガイドを作成"""
        
        guide = '''# 📋 Googleスプレッドシート チーム管理 セットアップガイド

## 🚀 10分でセットアップ完了！

### ステップ1: スプレッドシート作成（2分）

1. Google スプレッドシートを新規作成
2. ファイル名を「Threads投稿管理_チーム名」に変更

### ステップ2: シート作成（3分）

以下の4つのシートを作成：
1. 投稿カレンダー
2. チームメンバー
3. ダッシュボード
4. アイデアバンク

### ステップ3: データ貼り付け（2分）

1. 各TSVファイルを開く
2. 全選択（Ctrl+A）してコピー
3. 対応するシートのA1セルに貼り付け

### ステップ4: GASスクリプト設定（3分）

1. 拡張機能 → Apps Script
2. コード.gsの内容を全て削除
3. 05_GASスクリプト.jsの内容を貼り付け
4. 保存（Ctrl+S）
5. 実行 → onOpen（初回は承認が必要）

## 📱 条件付き書式の設定

### 投稿カレンダーシート

**ステータス列（G列）の色分け：**
- "予定" → 背景色: #fff2cc（薄い黄色）
- "投稿済み" → 背景色: #d9ead3（薄い緑）
- "遅延" → 背景色: #f4cccc（薄い赤）

**設定方法：**
1. G列を選択
2. 書式 → 条件付き書式
3. 条件を追加

### チームメンバーシート

**達成率列（F列）：**
- 100%以上 → 背景色: #b7e1cd（緑）
- 80%以上 → 背景色: #fce5cd（オレンジ）
- 80%未満 → 背景色: #f4cccc（赤）

## 🔧 カスタマイズ

### 投稿時間の変更

GASスクリプトの以下の部分を編集：
```javascript
const postTimes = ['07:30', '12:15', '18:30', '21:00'];
```

### メンバーの追加

チームメンバーシートに新しい行を追加

### 通知先の設定

GASスクリプトで通知用メールアドレスを設定：
```javascript
const NOTIFICATION_EMAIL = 'team@example.com';
```

## 🎯 運用開始チェックリスト

□ 全シートが正しく作成されている
□ GASメニューが表示される
□ チームメンバーが登録されている
□ 共有設定が完了している
□ 初回の投稿スケジュールが入力されている

## 💡 便利な使い方

1. **ショートカット**
   - Ctrl+Alt+M: コメント追加
   - Ctrl+;: 今日の日付入力

2. **フィルタービュー**
   - 各メンバー用のビューを作成
   - データ → フィルタービュー → 新規作成

3. **保護機能**
   - 重要な列を保護
   - データ → シートと範囲を保護

準備完了！素晴らしいチーム運用を始めましょう！
'''
        
        filename = f'{self.output_dir}/00_セットアップガイド.md'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(guide)
        
        return filename


# 実行
if __name__ == "__main__":
    generator = SpreadsheetTemplateGenerator()
    
    print("📊 Googleスプレッドシート チーム管理テンプレート生成")
    print("=" * 50)
    
    team_size = input("チーム人数を入力（デフォルト: 5）: ") or "5"
    days = input("スケジュール日数を入力（デフォルト: 30）: ") or "30"
    
    files = generator.create_team_template(int(team_size), int(days))
    
    print("\n生成されたファイル:")
    for file_type, filepath in files.items():
        print(f"  {file_type}: {filepath}")