// 収益最大化分析システム - Google Apps Script

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
  
  SpreadsheetApp.getUi().alert('自動分析を設定しました！\n・毎日午前2時: ROI分析\n・毎週月曜9時: レポート送信');
}
