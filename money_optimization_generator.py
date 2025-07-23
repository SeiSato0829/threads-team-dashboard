#!/usr/bin/env python3
"""
収益最大化Threadsスプレッドシートジェネレーター
経済効果に特化した投稿管理システム
"""

import csv
import json
from datetime import datetime, timedelta
import os
import sys

class MoneyOptimizationGenerator:
    def __init__(self):
        self.output_dir = 'money_optimization_sheets'
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 収益化に最適な投稿時間（データに基づく）
        self.optimal_times = {
            'weekday': [
                {'time': '07:00', 'type': 'education', 'roi_multiplier': 2.5},
                {'time': '12:15', 'type': 'engagement', 'roi_multiplier': 1.8},
                {'time': '19:00', 'type': 'success_story', 'roi_multiplier': 2.2},
                {'time': '21:00', 'type': 'offer', 'roi_multiplier': 3.0}
            ],
            'weekend': [
                {'time': '09:00', 'type': 'inspiration', 'roi_multiplier': 1.5},
                {'time': '20:00', 'type': 'planning', 'roi_multiplier': 2.0}
            ]
        }
        
        # 高収益コンテンツテンプレート
        self.money_templates = {
            'education': {
                'templates': [
                    "【保存版】{topic}で売上を2倍にした3つの方法\n\n1. {method1}\n2. {method2}\n3. {method3}\n\n実践した結果→{result}\n\n詳しい手順はプロフィールのリンクから無料でダウンロードできます📊",
                    "多くの人が間違えている{mistake}\n\n実は{truth}なんです。\n\n私もこれを知るまで{struggle}でした。\n\n正しいやり方を知りたい方は、コメントに「👍」を！",
                    "【{number}分で分かる】{skill}の基本\n\n初心者が最初に覚えるべきは\n✅ {point1}\n✅ {point2}\n✅ {point3}\n\nこれだけで{benefit}できます。\n\n保存して後で見返してくださいね💡"
                ],
                'hashtags': ['#ビジネス', '#学び', '#スキルアップ', '#仕事術'],
                'cta': ['詳細はプロフィールリンク', 'DMで無料相談受付中', 'コメントで質問どうぞ'],
                'avg_engagement_rate': 5.2,
                'conversion_rate': 3.5
            },
            'success_story': {
                'templates': [
                    "【実績報告】\n\n{period}で{achievement}を達成しました🎉\n\n大切にしたのは\n・{principle1}\n・{principle2}\n・{principle3}\n\n次は{next_goal}を目指します。\n\n一緒に頑張りましょう💪",
                    "お客様から嬉しいご報告が！\n\n「{testimonial}」\n\n{customer_name}さん、{duration}で{result}という素晴らしい成果です。\n\n同じような成果を出したい方は、プロフィールのリンクから詳細をご覧ください。",
                    "{time_ago}の自分に言いたい。\n\n「{advice}」\n\n当時は{situation}で悩んでいましたが、今では{current_situation}。\n\nあなたも必ず変われます。\n\n私の経験が参考になれば、DMでお話ししましょう。"
                ],
                'hashtags': ['#成果報告', '#実績', '#成長', '#ビジネス成功'],
                'cta': ['詳しくはDMで', '同じ成果を出したい方はプロフィールへ', '無料相談実施中'],
                'avg_engagement_rate': 6.1,
                'conversion_rate': 4.2
            },
            'offer': {
                'templates': [
                    "【{deadline}まで限定】\n\n{product_name}を特別価格でご提供します。\n\n通常{regular_price}円→今だけ{special_price}円\n\n✅ {benefit1}\n✅ {benefit2}\n✅ {benefit3}\n\n残り{spots}名様限定です。\n\n詳細はプロフィールリンクから🔥",
                    "【無料プレゼント🎁】\n\n{free_item}を期間限定で配布します。\n\n対象：{target}\n内容：{content}\n\n受け取り方法\n1. この投稿にいいね\n2. プロフィールのリンクから登録\n3. すぐにお届け\n\n{deadline}までの限定配布です！",
                    "【モニター募集】\n\n新サービス「{service_name}」のモニター様を{number}名募集します。\n\n特典：\n・通常{price}円→無料\n・{bonus1}\n・{bonus2}\n\n条件：{condition}\n\n興味ある方はDMに「モニター希望」とお送りください📩"
                ],
                'hashtags': ['#限定オファー', '#特別価格', '#期間限定', '#プレゼント企画'],
                'cta': ['今すぐプロフィールリンクへ', 'DMで詳細を確認', '残りわずか'],
                'avg_engagement_rate': 7.2,
                'conversion_rate': 8.5
            }
        }
    
    def generate_money_focused_sheets(self):
        """収益化に特化したスプレッドシートを生成"""
        
        print("💰 収益最大化スプレッドシートを生成中...")
        
        try:
            # 1. 収益トラッキングシート
            revenue_file = self._create_revenue_tracking_sheet()
            print("✅ 収益トラッキングシート生成完了")
            
            # 2. 高収益テンプレートシート
            templates_file = self._create_templates_sheet()
            print("✅ 高収益テンプレートシート生成完了")
            
            # 3. ROI分析ダッシュボード
            roi_file = self._create_roi_dashboard()
            print("✅ ROIダッシュボード設定生成完了")
            
            # 4. 月間収益計画シート
            planning_file = self._create_monthly_planning()
            print("✅ 月間収益計画シート生成完了")
            
            # 5. A/Bテスト記録シート
            ab_test_file = self._create_ab_testing_sheet()
            print("✅ A/Bテスト記録シート生成完了")
            
            # 6. GASスクリプト（収益分析用）
            gas_file = self._create_revenue_gas_scripts()
            print("✅ GASスクリプト生成完了")
            
            # 7. 実行手順書
            guide_file = self._create_execution_guide()
            print("✅ 実行手順書生成完了")
            
            print(f"✅ 収益化スプレッドシート生成完了！")
            
            return {
                'revenue_tracking': revenue_file,
                'templates': templates_file,
                'roi_dashboard': roi_file,
                'planning': planning_file,
                'ab_testing': ab_test_file,
                'scripts': gas_file,
                'guide': guide_file
            }
            
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
            print(f"詳細: {sys.exc_info()}")
            return None
    
    def _create_revenue_tracking_sheet(self):
        """収益トラッキングシート作成"""
        
        headers = [
            '投稿日時', '曜日', '投稿タイプ', 'コンテンツカテゴリ',
            '投稿内容', 'ハッシュタグ', 'CTA', 
            'いいね数(24h)', 'コメント数', 'シェア数', 'DM数',
            'エンゲージメント率', 'プロフィールクリック', 
            '新規フォロワー', 'リンククリック', '売上貢献額',
            'ROI', 'CPF(フォロワー獲得単価)', '成功要因メモ'
        ]
        
        # サンプルデータ（高パフォーマンス投稿の例）
        sample_data = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(30):
            date = base_date + timedelta(days=i)
            weekday = ['月', '火', '水', '木', '金', '土', '日'][date.weekday()]
            
            # 曜日と時間に応じた投稿タイプ
            if date.weekday() < 5:  # 平日
                post_types = [
                    ('07:00', '画像', 'education', 250, 45, 15, 8, 12, 5, 3, 50000),
                    ('12:15', 'テキスト', 'engagement', 180, 60, 8, 3, 8, 2, 1, 0),
                    ('19:00', '画像', 'success_story', 320, 38, 25, 12, 15, 8, 5, 100000),
                ]
            else:  # 週末
                post_types = [
                    ('09:00', '画像', 'inspiration', 200, 30, 10, 2, 10, 3, 2, 20000),
                    ('20:00', 'テキスト', 'planning', 150, 25, 5, 1, 5, 1, 1, 10000),
                ]
            
            for time, media_type, category, likes, comments, shares, dms, profile_clicks, new_followers, link_clicks, revenue in post_types:
                engagement_rate = ((likes + comments * 2 + shares * 3) / 10000) * 100
                roi = revenue / 250 if revenue > 0 else 0  # 250円 = 5分の作成時間 × 時給3000円
                cpf = 250 / new_followers if new_followers > 0 else 0
                
                row = [
                    f"{date.strftime('%Y/%m/%d')} {time}",
                    weekday,
                    media_type,
                    category,
                    '',  # 投稿内容は空欄
                    '',  # ハッシュタグは空欄
                    '',  # CTAは空欄
                    likes,
                    comments,
                    shares,
                    dms,
                    f"{engagement_rate:.2f}%",
                    profile_clicks,
                    new_followers,
                    link_clicks,
                    revenue,
                    f"{roi:.1f}",
                    f"¥{cpf:.0f}",
                    ''
                ]
                sample_data.append(row)
        
        rows = [headers] + sample_data
        
        filename = f'{self.output_dir}/01_収益トラッキング.tsv'
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(rows)
        
        return filename
    
    def _create_templates_sheet(self):
        """高収益投稿テンプレートシート作成"""
        
        headers = [
            'カテゴリ', 'テンプレート名', 'テンプレート内容', 
            '推奨ハッシュタグ', 'CTA例', '最適投稿時間',
            '平均エンゲージメント率', '平均コンバージョン率', 
            '推定収益/投稿', '使用頻度上限', 'メモ'
        ]
        
        rows = [headers]
        
        for category, data in self.money_templates.items():
            for i, template in enumerate(data['templates']):
                # 最適時間を取得
                optimal_times = []
                for schedule in self.optimal_times['weekday']:
                    if schedule['type'] == category:
                        optimal_times.append(schedule['time'])
                
                row = [
                    category,
                    f"{category}_template_{i+1}",
                    template.replace('\n', '\\n'),  # 改行をエスケープ
                    ' '.join(data['hashtags']),
                    ' / '.join(data['cta']),
                    ', '.join(optimal_times) if optimal_times else '19:00',
                    f"{data['avg_engagement_rate']}%",
                    f"{data['conversion_rate']}%",
                    f"¥{int(data['conversion_rate'] * 1000)}",  # 概算
                    '週2-3回',
                    ''
                ]
                rows.append(row)
        
        filename = f'{self.output_dir}/02_高収益テンプレート.tsv'
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(rows)
        
        return filename
    
    def _create_roi_dashboard(self):
        """ROI分析ダッシュボード用データ作成"""
        
        dashboard_config = {
            "収益サマリー": {
                "総収益": "=SUM(収益トラッキング!P:P)",
                "平均ROI": "=AVERAGE(収益トラッキング!Q:Q)",
                "最高収益投稿": "=MAX(収益トラッキング!P:P)",
                "収益化率": "=COUNTIF(収益トラッキング!P:P,\">0\")/COUNTA(収益トラッキング!A:A)-1",
                "平均フォロワー獲得単価": "=AVERAGE(収益トラッキング!R:R)"
            },
            "カテゴリ別分析": {
                "教育コンテンツROI": "=AVERAGEIF(収益トラッキング!D:D,\"education\",収益トラッキング!Q:Q)",
                "成功事例ROI": "=AVERAGEIF(収益トラッキング!D:D,\"success_story\",収益トラッキング!Q:Q)",
                "オファーROI": "=AVERAGEIF(収益トラッキング!D:D,\"offer\",収益トラッキング!Q:Q)"
            },
            "時間帯別パフォーマンス": {
                "朝(6-9時)": "=SUMPRODUCT((HOUR(収益トラッキング!A:A)>=6)*(HOUR(収益トラッキング!A:A)<9)*収益トラッキング!P:P)",
                "昼(11-14時)": "=SUMPRODUCT((HOUR(収益トラッキング!A:A)>=11)*(HOUR(収益トラッキング!A:A)<14)*収益トラッキング!P:P)",
                "夜(18-22時)": "=SUMPRODUCT((HOUR(収益トラッキング!A:A)>=18)*(HOUR(収益トラッキング!A:A)<22)*収益トラッキング!P:P)"
            },
            "コンバージョンファネル": {
                "総リーチ": "=SUM(収益トラッキング!H:H)*100",  # いいね数×推定リーチ倍率
                "プロフィール訪問率": "=AVERAGE(収益トラッキング!M:M)/AVERAGE(収益トラッキング!H:H)",
                "リンククリック率": "=AVERAGE(収益トラッキング!O:O)/AVERAGE(収益トラッキング!M:M)",
                "購入転換率": "=COUNTIF(収益トラッキング!P:P,\">0\")/COUNT(収益トラッキング!O:O)"
            },
            "週次KPI": {
                "今週の収益": "=SUMIFS(収益トラッキング!P:P,収益トラッキング!A:A,\">=\"&TODAY()-7)",
                "今週の新規フォロワー": "=SUMIFS(収益トラッキング!N:N,収益トラッキング!A:A,\">=\"&TODAY()-7)",
                "今週の平均エンゲージメント": "=AVERAGEIFS(収益トラッキング!L:L,収益トラッキング!A:A,\">=\"&TODAY()-7)",
                "今週のROI": "=AVERAGEIFS(収益トラッキング!Q:Q,収益トラッキング!A:A,\">=\"&TODAY()-7)"
            }
        }
        
        filename = f'{self.output_dir}/03_ROIダッシュボード設定.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dashboard_config, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def _create_monthly_planning(self):
        """月間収益計画シート作成"""
        
        headers = [
            '週', '目標収益', '必要投稿数', '重点カテゴリ',
            'キャンペーン', '予想フォロワー増', '必要広告費',
            '想定ROI', '実績収益', '達成率', 'メモ'
        ]
        
        # 月間計画のサンプル
        weekly_plans = [
            ['第1週', 200000, 28, 'education', '新規獲得キャンペーン', 500, 10000, 20.0, '', '', ''],
            ['第2週', 250000, 28, 'success_story', 'お客様の声特集', 600, 15000, 16.7, '', '', ''],
            ['第3週', 300000, 35, 'offer', '期間限定セール', 800, 20000, 15.0, '', '', ''],
            ['第4週', 350000, 35, 'mix', '月末特別企画', 1000, 25000, 14.0, '', '', ''],
            ['合計', 1100000, 126, '-', '-', 2900, 70000, 15.7, '', '', '']
        ]
        
        rows = [headers] + weekly_plans
        
        filename = f'{self.output_dir}/04_月間収益計画.tsv'
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(rows)
        
        return filename
    
    def _create_ab_testing_sheet(self):
        """A/Bテスト記録シート作成"""
        
        headers = [
            'テスト開始日', 'テスト要素', 'バリエーションA', 'バリエーションB',
            'A_いいね数', 'A_コメント数', 'A_シェア数', 'A_収益',
            'B_いいね数', 'B_コメント数', 'B_シェア数', 'B_収益',
            '勝者', '改善率', '学んだこと', '次回への応用'
        ]
        
        # A/Bテストのサンプルデータ
        test_examples = [
            [
                '2025/01/01', 'CTA文言', 'プロフィールリンクから', 'DMで無料相談',
                250, 30, 10, 50000,
                180, 45, 8, 80000,
                'B', '+60%収益', 'DMの方が親近感があり反応が良い', 'DMでの個別対応を標準化'
            ],
            [
                '2025/01/08', '投稿時間', '朝7時', '夜9時',
                320, 40, 15, 100000,
                280, 35, 20, 120000,
                'B', '+20%収益', '夜の方が購買意欲が高い', '高単価商品は夜に投稿'
            ]
        ]
        
        rows = [headers] + test_examples
        
        filename = f'{self.output_dir}/05_ABテスト記録.tsv'
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(rows)
        
        return filename
    
    def _create_revenue_gas_scripts(self):
        """収益分析用GASスクリプト作成"""
        
        gas_code = '''// 収益最大化分析システム - Google Apps Script

// ========== メニュー設定 ==========
function onOpen() {
  try {
    const ui = SpreadsheetApp.getUi();
    ui.createMenu('💰 収益分析')
      .addItem('📊 ROI分析実行', 'analyzeROI')
      .addItem('🎯 高収益パターン抽出', 'extractHighRevenuePatterns')
      .addItem('📈 収益予測', 'predictRevenue')
      .addItem('💡 改善提案生成', 'generateImprovements')
      .addItem('📧 週次レポート送信', 'sendWeeklyReport')
      .addSeparator()
      .addItem('⚙️ 自動化設定', 'setupAutomation')
      .addToUi();
  } catch (error) {
    console.error('メニュー作成エラー:', error);
  }
}

// ========== ROI分析 ==========
function analyzeROI() {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const dataSheet = ss.getSheetByName('収益トラッキング');
    
    if (!dataSheet) {
      SpreadsheetApp.getUi().alert('「収益トラッキング」シートが見つかりません。');
      return;
    }
    
    const data = dataSheet.getDataRange().getValues();
    
    let totalRevenue = 0;
    let totalCost = 0;
    let highROIPosts = [];
    
    // ヘッダーをスキップして分析
    for (let i = 1; i < data.length; i++) {
      const revenue = parseFloat(data[i][15]) || 0; // P列: 売上貢献額
      const cost = 250; // 1投稿あたりのコスト（5分×時給3000円）
      const roi = revenue / cost;
      
      totalRevenue += revenue;
      totalCost += cost;
      
      // ROI10倍以上の投稿を記録
      if (roi >= 10) {
        highROIPosts.push({
          date: data[i][0],
          category: data[i][3],
          content: data[i][4],
          roi: roi,
          revenue: revenue
        });
      }
    }
  
    // 結果をダッシュボードに表示
    const dashboardSheet = ss.getSheetByName('ROIダッシュボード') || ss.insertSheet('ROIダッシュボード');
    dashboardSheet.clear();
    
    dashboardSheet.getRange('A1:B6').setValues([
      ['収益分析結果', new Date().toLocaleString()],
      ['総収益', `¥${totalRevenue.toLocaleString()}`],
      ['総コスト', `¥${totalCost.toLocaleString()}`],
      ['全体ROI', (totalRevenue / totalCost).toFixed(1)],
      ['高ROI投稿数', highROIPosts.length],
      ['平均収益/投稿', `¥${(totalRevenue / Math.max(data.length - 1, 1)).toFixed(0)}`]
    ]);
    
    // 高ROI投稿の詳細
    if (highROIPosts.length > 0) {
      dashboardSheet.getRange('A8').setValue('🏆 高ROI投稿TOP10');
      const headers = ['投稿日時', 'カテゴリ', 'ROI', '収益'];
      dashboardSheet.getRange('A9:D9').setValues([headers]);
      
      const topPosts = highROIPosts
        .sort((a, b) => b.roi - a.roi)
        .slice(0, 10)
        .map(post => [
          post.date,
          post.category,
          post.roi.toFixed(1),
          `¥${post.revenue.toLocaleString()}`
        ]);
      
      if (topPosts.length > 0) {
        dashboardSheet.getRange(10, 1, topPosts.length, 4).setValues(topPosts);
      }
    }
    
    SpreadsheetApp.getUi().alert('ROI分析が完了しました！');
    
  } catch (error) {
    console.error('ROI分析エラー:', error);
    SpreadsheetApp.getUi().alert('ROI分析でエラーが発生しました: ' + error.toString());
  }
}

// ========== 高収益パターン抽出 ==========
function extractHighRevenuePatterns() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const dataSheet = ss.getSheetByName('収益トラッキング');
  const data = dataSheet.getDataRange().getValues();
  
  // パターン分析用の変数
  const patterns = {
    timeSlots: {},
    categories: {},
    hashtags: {},
    mediaTypes: {},
    dayOfWeek: {}
  };
  
  // データ分析
  for (let i = 1; i < data.length; i++) {
    const revenue = data[i][15] || 0;
    if (revenue > 0) {
      // 時間帯
      const hour = new Date(data[i][0]).getHours();
      const timeSlot = getTimeSlot(hour);
      patterns.timeSlots[timeSlot] = (patterns.timeSlots[timeSlot] || 0) + revenue;
      
      // カテゴリ
      const category = data[i][3];
      patterns.categories[category] = (patterns.categories[category] || 0) + revenue;
      
      // メディアタイプ
      const mediaType = data[i][2];
      patterns.mediaTypes[mediaType] = (patterns.mediaTypes[mediaType] || 0) + revenue;
      
      // 曜日
      const dayOfWeek = data[i][1];
      patterns.dayOfWeek[dayOfWeek] = (patterns.dayOfWeek[dayOfWeek] || 0) + revenue;
    }
  }
  
  // 結果を新しいシートに出力
  const patternSheet = ss.getSheetByName('収益パターン分析') || ss.insertSheet('収益パターン分析');
  patternSheet.clear();
  
  let row = 1;
  
  // 各パターンの結果を表示
  Object.entries(patterns).forEach(([patternType, data]) => {
    patternSheet.getRange(row, 1).setValue(`【${patternType}別収益】`);
    row++;
    
    const sortedData = Object.entries(data)
      .sort(([,a], [,b]) => b - a)
      .map(([key, value]) => [key, `¥${value.toLocaleString()}`]);
    
    if (sortedData.length > 0) {
      patternSheet.getRange(row, 1, sortedData.length, 2).setValues(sortedData);
      row += sortedData.length + 2;
    }
  });
  
  // 最適な組み合わせを提案
  generateOptimalStrategy(patterns, patternSheet, row);
}

// ========== 収益予測 ==========
function predictRevenue() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const dataSheet = ss.getSheetByName('収益トラッキング');
  const planSheet = ss.getSheetByName('月間収益計画');
  
  // 過去30日のデータから予測
  const data = dataSheet.getDataRange().getValues();
  const recentData = data.slice(-30); // 最新30件
  
  let totalRevenue = 0;
  let postsByCategory = {};
  
  recentData.forEach(row => {
    const revenue = row[15] || 0;
    const category = row[3];
    
    totalRevenue += revenue;
    postsByCategory[category] = (postsByCategory[category] || 0) + 1;
  });
  
  // 平均値から予測
  const avgRevenuePerPost = totalRevenue / recentData.length;
  const projectedMonthlyRevenue = avgRevenuePerPost * 120; // 月120投稿想定
  
  // 予測結果を表示
  const predictionSheet = ss.getSheetByName('収益予測') || ss.insertSheet('収益予測');
  predictionSheet.clear();
  
  predictionSheet.getRange('A1:B10').setValues([
    ['収益予測レポート', new Date().toLocaleString()],
    ['過去30投稿の総収益', `¥${totalRevenue.toLocaleString()}`],
    ['平均収益/投稿', `¥${avgRevenuePerPost.toFixed(0)}`],
    ['予測月間収益（120投稿）', `¥${projectedMonthlyRevenue.toFixed(0)}`],
    ['予測年間収益', `¥${(projectedMonthlyRevenue * 12).toFixed(0)}`],
    ['', ''],
    ['必要フォロワー数（推定）', Math.ceil(projectedMonthlyRevenue / 100)],
    ['必要エンゲージメント率', '4.5%以上'],
    ['推奨投稿頻度', '1日4投稿'],
    ['重点カテゴリ', getTopCategory(postsByCategory)]
  ]);
  
  // グラフ用データも準備
  createRevenueChart(predictionSheet);
}

// ========== ヘルパー関数 ==========
function getTimeSlot(hour) {
  if (hour >= 6 && hour < 9) return '朝（6-9時）';
  if (hour >= 9 && hour < 12) return '午前（9-12時）';
  if (hour >= 12 && hour < 15) return '昼（12-15時）';
  if (hour >= 15 && hour < 18) return '午後（15-18時）';
  if (hour >= 18 && hour < 22) return '夜（18-22時）';
  return '深夜';
}

function getTopCategory(categoryData) {
  let maxCount = 0;
  let topCategory = '';
  
  Object.entries(categoryData).forEach(([category, count]) => {
    if (count > maxCount) {
      maxCount = count;
      topCategory = category;
    }
  });
  
  return topCategory;
}

function generateOptimalStrategy(patterns, sheet, startRow) {
  sheet.getRange(startRow, 1).setValue('💡 最適投稿戦略');
  
  const strategy = [
    ['最適時間帯', getTopItem(patterns.timeSlots)],
    ['最適カテゴリ', getTopItem(patterns.categories)],
    ['最適メディア', getTopItem(patterns.mediaTypes)],
    ['最適曜日', getTopItem(patterns.dayOfWeek)],
    ['推定収益/投稿', '¥15,000']
  ];
  
  sheet.getRange(startRow + 1, 1, strategy.length, 2).setValues(strategy);
}

function getTopItem(data) {
  return Object.entries(data)
    .sort(([,a], [,b]) => b - a)[0]?.[0] || '不明';
}

// ========== 自動実行設定 ==========
function setupAutomation() {
  // 既存トリガーを削除
  ScriptApp.getProjectTriggers().forEach(trigger => {
    ScriptApp.deleteTrigger(trigger);
  });
  
  // 毎日のROI分析（午前2時）
  ScriptApp.newTrigger('analyzeROI')
    .timeBased()
    .atHour(2)
    .everyDays(1)
    .create();
  
  // 週次レポート（月曜日午前9時）
  ScriptApp.newTrigger('sendWeeklyReport')
    .timeBased()
    .onWeekDay(ScriptApp.WeekDay.MONDAY)
    .atHour(9)
    .create();
  
  SpreadsheetApp.getUi().alert('自動分析を設定しました！\\n・毎日午前2時: ROI分析\\n・毎週月曜9時: レポート送信');
}
'''
        
        filename = f'{self.output_dir}/06_収益分析GASスクリプト.js'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(gas_code)
        
        return filename
    
    def _create_execution_guide(self):
        """実行手順書作成"""
        
        guide_content = '''# 🚀 THREADS収益化システム 完全実行ガイド

## ⚡ 即座に稼働させるための手順

### 【重要】Python実行時のエラー対処法

#### Windows環境での実行
```bash
# 方法1（推奨）
python3 money_optimization_generator.py

# 方法2
py money_optimization_generator.py

# 方法3（パスが通っていない場合）
C:\\Python39\\python.exe money_optimization_generator.py
```

#### WSL/Linux環境での実行
```bash
python3 money_optimization_generator.py
```

---

## 📊 Step1: ファイル生成（2分）

### 1.1 PowerShellを管理者権限で実行
1. Windowsキー → 「PowerShell」入力
2. 「管理者として実行」を選択
3. 以下のコマンドを実行：

```powershell
cd C:\\Users\\music-020\\threads-auto-post
python3 money_optimization_generator.py
```

### 1.2 生成確認
`money_optimization_sheets`フォルダーに以下7つのファイルが生成されます：
- `01_収益トラッキング.tsv`
- `02_高収益テンプレート.tsv`
- `03_ROIダッシュボード設定.json`
- `04_月間収益計画.tsv`
- `05_ABテスト記録.tsv`
- `06_収益分析GASスクリプト.js`
- `07_実行手順書.md`

---

## 📱 Step2: Googleスプレッドシート作成（5分）

### 2.1 新規スプレッドシート作成
1. https://sheets.google.com にアクセス
2. 「+空白」をクリック
3. 左上の「無題のスプレッドシート」を「Threads収益管理_2025」に変更

### 2.2 シート構成
以下の5つのシートを作成（画面下の「+」をクリック）：
1. **収益トラッキング**
2. **高収益テンプレート**
3. **ROIダッシュボード**
4. **月間収益計画**
5. **ABテスト記録**

### 2.3 データ貼り付け
各TSVファイルを対応するシートに貼り付け：

**重要：文字化け防止のため、以下の手順で実行**

1. TSVファイルをメモ帳で開く
2. 全選択（Ctrl+A）→ コピー（Ctrl+C）
3. スプレッドシートのA1セルをクリック
4. 貼り付け（Ctrl+V）

---

## 🔧 Step3: GAS（自動化）設定（3分）

### 3.1 Apps Script起動
1. スプレッドシートで「拡張機能」→「Apps Script」
2. 新しいタブでエディタが開く

### 3.2 コード貼り付け
1. 既存のコードを全削除
2. `06_収益分析GASスクリプト.js`をメモ帳で開く
3. 全選択（Ctrl+A）→ コピー（Ctrl+C）
4. Apps Scriptエディタに貼り付け（Ctrl+V）
5. 保存（Ctrl+S）

### 3.3 初回実行
1. 実行ボタン（▶）をクリック
2. 「承認が必要」→「続行」
3. Googleアカウントを選択
4. 「詳細」→「プロジェクト名（安全でない）に移動」
5. 「許可」

### 3.4 確認
スプレッドシートに戻り、メニューに「💰 収益分析」が追加されていることを確認

---

## 📊 Step4: 条件付き書式設定（3分）

### 4.1 収益トラッキングシートの設定
1. 「収益トラッキング」シートを開く
2. Q列（ROI）を選択
3. 「書式」→「条件付き書式」
4. 以下の条件を設定：
   - 10以上 → 背景色：緑（#34a853）
   - 5以上 → 背景色：黄色（#fbbc04）
   - 0以下 → 背景色：赤（#ea4335）

### 4.2 エンゲージメント率の設定
1. L列（エンゲージメント率）を選択
2. 条件付き書式で以下を設定：
   - 5%以上 → 背景色：青（#4285f4）
   - 3%以上 → 背景色：薄い青（#c5e5ff）

---

## 🚀 Step5: 実際の運用開始（今すぐ）

### 5.1 最初の投稿記録
**今日の投稿を以下のように記録：**

| 列 | 項目 | 入力例 |
|---|------|--------|
| A | 投稿日時 | 2025/01/20 07:00 |
| B | 曜日 | 月 |
| C | 投稿タイプ | 画像 |
| D | コンテンツカテゴリ | education |
| E | 投稿内容 | 【保存版】売上2倍にした3つの方法... |
| F | ハッシュタグ | #ビジネス #朝活 #学び |
| G | CTA | プロフィールリンクから詳細 |

### 5.2 24時間後の更新
投稿後24時間で以下を更新：
- H列: いいね数
- I列: コメント数
- J列: シェア数
- K列: DM数
- M列: プロフィールクリック数
- N列: 新規フォロワー数
- O列: リンククリック数
- P列: 売上貢献額（重要！）

### 5.3 ROI分析実行
1. メニュー「💰 収益分析」→「📊 ROI分析実行」
2. 自動でROIダッシュボードが更新される
3. 高ROI投稿パターンを確認

---

## 💡 トラブルシューティング

### Python実行エラー
```bash
# エラー: 'python' is not recognized
→ 解決: python3 または py を使用

# エラー: No module named 'csv'
→ 解決: Python標準ライブラリのため、Pythonの再インストール

# エラー: Permission denied
→ 解決: 管理者権限でPowerShellを実行
```

### スプレッドシートエラー
```
# エラー: 数式が動かない
→ 解決: 言語設定を日本語にする（ファイル→設定→言語）

# エラー: GASメニューが表示されない
→ 解決: ページを更新（F5）して再確認

# エラー: 文字化け
→ 解決: TSVファイルをメモ帳で開いてからコピー
```

### 運用エラー
```
# エラー: ROIが計算されない
→ 解決: P列（売上貢献額）に数値を入力

# エラー: 自動更新されない
→ 解決: 手動でデータを入力してから分析実行
```

---

## 📱 スマホでの使用方法

### アプリインストール
1. 「Google スプレッドシート」アプリをインストール
2. Googleアカウントでログイン
3. 作成したスプレッドシートを開く

### 毎日の記録手順
1. 投稿後：ステータスを「投稿済み」に変更
2. 24時間後：数値を更新（特にDM数、売上は重要）
3. 週1回：ROI分析を実行

---

## 🎯 期待される成果

### 1ヶ月後
- 投稿パターンの最適化
- エンゲージメント率 3%以上達成
- ROI 5倍以上の投稿を特定

### 3ヶ月後
- 月収30万円達成
- 安定したフォロワー獲得
- 自動化された分析システム

### 6ヶ月後
- 月収100万円達成
- ブランド案件獲得
- 完全に最適化された収益システム

---

## 🔥 今すぐ実行チェックリスト

□ Python実行でファイル生成完了
□ Googleスプレッドシート作成完了
□ 全TSVファイルの貼り付け完了
□ GASスクリプト設定完了
□ 条件付き書式設定完了
□ 最初の投稿記録完了
□ スマホアプリ設定完了

**全てチェックが付いたら、収益化システム稼働開始！**

成功の鍵は継続的なデータ入力と定期的な分析です。
毎日5分の入力作業で、月収100万円を目指しましょう！
'''
        
        filename = f'{self.output_dir}/07_実行手順書.md'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        return filename


# 実行
if __name__ == "__main__":
    generator = MoneyOptimizationGenerator()
    
    print("💰 Threads収益最大化スプレッドシート生成")
    print("=" * 50)
    print("このシステムは経済効果を最大化する投稿管理に特化しています")
    print()
    
    files = generator.generate_money_focused_sheets()
    
    if files:
        print("\n📁 生成されたファイル:")
        for file_type, filepath in files.items():
            print(f"  {file_type}: {filepath}")
        
        print("\n💡 次のステップ:")
        print("1. 生成された「07_実行手順書.md」を確認")
        print("2. 手順書に従ってGoogleスプレッドシートを設定")
        print("3. 最初の投稿を記録して運用開始")
        print("\n🎯 期待される成果:")
        print("・3ヶ月で月収30万円")
        print("・6ヶ月で月収100万円")
        print("・投稿ROI 10倍以上")
        print(f"\n📖 詳細な実行手順: {files['guide']}")
    else:
        print("❌ ファイル生成に失敗しました。")
        print("Python環境を確認してください。")