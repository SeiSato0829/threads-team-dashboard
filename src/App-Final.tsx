// 最終版App - すべての機能を統合

import React, { useState, useEffect, useCallback } from 'react';
import { Calendar, Upload, Settings, BarChart3, Zap, AlertCircle } from 'lucide-react';
import api from './services/api-emergency-fix';
import type {
  Post,
  ManualPostForm,
  DashboardStats,
  AutomationSettings,
  ScrapingHistory,
  AppState
} from './types';

// 遅延読み込みでパフォーマンス最適化
const ManualPostComponent = React.lazy(() => import('./components/ManualPostForm'));
const CSVUploadComponent = React.lazy(() => import('./components/CSVUpload'));
const PostDashboardComponent = React.lazy(() => import('./components/PostDashboard'));
const SettingsComponent = React.lazy(() => import('./components/SettingsSimple'));

// ローディングコンポーネント
const LoadingSpinner: React.FC = () => (
  <div className="flex items-center justify-center p-8">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
  </div>
);

// エラー表示コンポーネント
const ErrorAlert: React.FC<{ message: string; onDismiss?: () => void }> = ({ message, onDismiss }) => (
  <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
    <div className="flex">
      <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
      <div className="flex-1">
        <p className="text-sm text-red-800">{message}</p>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="ml-2 text-red-400 hover:text-red-600"
        >
          ✕
        </button>
      )}
    </div>
  </div>
);

const AppFinal: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'auto' | 'manual' | 'csv' | 'dashboard' | 'settings'>('auto');
  const [appState, setAppState] = useState<AppState>({
    posts: [],
    isLoading: false,
    error: null,
    automationSettings: {
      csvWatchPath: './csv_input',
      postInterval: 60,
      scrapingInterval: 8,
      dailyPostLimit: 10,
      postStartTime: '09:00',
      postEndTime: '21:00',
      enableAIGeneration: true,
      enableBufferScheduling: true,
      enableAutoScraping: true
    },
    dashboardStats: {
      totalPosts: 0,
      scheduledPosts: 0,
      completedPosts: 0,
      failedPosts: 0,
      todayPosts: 0,
      automationStatus: 'stopped'
    },
    scrapingHistory: [],
    isConnected: false
  });

  // サーバー接続状態の監視
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const connected = await api.checkHealth();
        setAppState(prev => ({ ...prev, isConnected: connected }));
      } catch (error) {
        console.error('Connection check error:', error);
        setAppState(prev => ({ ...prev, isConnected: false }));
      }
    };

    // 初回チェック
    checkConnection();

    // 定期的な接続チェック（30秒ごと）
    const interval = setInterval(checkConnection, 30000);

    return () => clearInterval(interval);
  }, []);

  // ダッシュボード統計の取得
  const fetchDashboardStats = useCallback(async () => {
    if (!appState.isConnected) return;

    try {
      setAppState(prev => ({ ...prev, isLoading: true, error: null }));
      
      const [statsResponse, historyResponse, postsResponse] = await Promise.all([
        api.getDashboardStats(),
        api.getScrapingHistory(10),
        api.getPosts()
      ]);

      setAppState(prev => {
        const newState = { ...prev, isLoading: false };
        
        if (statsResponse.success && statsResponse.data) {
          newState.dashboardStats = statsResponse.data;
        }

        if (historyResponse.success && historyResponse.data) {
          newState.scrapingHistory = historyResponse.data;
        }

        if (postsResponse.success && postsResponse.data) {
          newState.posts = postsResponse.data.posts || [];
        }
        
        return newState;
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'ダッシュボード統計の取得に失敗しました';
      console.error('Dashboard stats error:', error);
      setAppState(prev => ({
        ...prev,
        error: errorMessage,
        isLoading: false
      }));
    }
  }, [appState.isConnected]);

  // 初回ロード時と定期的な更新
  useEffect(() => {
    if (activeTab === 'auto' || activeTab === 'dashboard') {
      fetchDashboardStats();
      
      // 1分ごとに更新
      const interval = setInterval(fetchDashboardStats, 60000);
      return () => clearInterval(interval);
    }
  }, [activeTab, fetchDashboardStats]);

  // 自動化の開始/停止
  const handleAutomationToggle = async () => {
    try {
      setAppState(prev => ({ ...prev, isLoading: true, error: null }));

      const isRunning = appState.dashboardStats.automationStatus === 'running';
      const response = isRunning 
        ? await api.stopAutomation()
        : await api.startAutomation();

      if (response.success) {
        await fetchDashboardStats();
      } else {
        throw new Error(response.error || '自動化の切り替えに失敗しました');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '自動化の切り替えに失敗しました';
      console.error('Automation toggle error:', error);
      setAppState(prev => ({
        ...prev,
        error: errorMessage,
        isLoading: false
      }));
    }
  };

  // スクレイピングの実行
  const handleScrapingTrigger = async () => {
    try {
      setAppState(prev => ({ ...prev, isLoading: true, error: null }));

      const response = await api.triggerScraping();

      if (response.success) {
        await fetchDashboardStats();
      } else {
        throw new Error(response.error || 'スクレイピングの実行に失敗しました');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'スクレイピングの実行に失敗しました';
      console.error('Scraping trigger error:', error);
      setAppState(prev => ({
        ...prev,
        error: errorMessage,
        isLoading: false
      }));
    }
  };

  // エラーのクリア
  const clearError = () => {
    setAppState(prev => ({ ...prev, error: null }));
  };

  // タブのアイコンとラベル
  const tabs = [
    { id: 'auto', label: '自動投稿', icon: Zap },
    { id: 'manual', label: '手動投稿', icon: Upload },
    { id: 'csv', label: 'CSV投稿', icon: Calendar },
    { id: 'dashboard', label: '投稿管理', icon: BarChart3 },
    { id: 'settings', label: '設定', icon: Settings }
  ] as const;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                Threads自動投稿システム v3.2 - 完全版
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`flex items-center ${appState.isConnected ? 'text-green-600' : 'text-red-600'}`}>
                <div className={`w-2 h-2 rounded-full mr-2 ${appState.isConnected ? 'bg-green-600' : 'bg-red-600'}`}></div>
                <span className="text-sm font-medium">
                  {appState.isConnected ? 'サーバー接続OK' : 'サーバー未接続'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* エラー表示 */}
      {appState.error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
          <ErrorAlert message={appState.error} onDismiss={clearError} />
        </div>
      )}

      {/* タブナビゲーション */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {tabs.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`
                  group inline-flex items-center py-3 px-1 border-b-2 font-medium text-sm
                  ${activeTab === id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                  transition-colors duration-200
                `}
                // disabled={!appState.isConnected && id !== 'settings'} // 一時的に無効化
              >
                <Icon className={`
                  -ml-0.5 mr-2 h-5 w-5
                  ${activeTab === id ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'}
                `} />
                {label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* メインコンテンツ */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <React.Suspense fallback={<LoadingSpinner />}>
          {/* 自動投稿タブ */}
          {activeTab === 'auto' && (
            <div className="space-y-6">
              {/* 自動化ステータスカード */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold mb-4">自動化ステータス</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-gray-50 rounded">
                    <div className={`text-3xl mb-2 ${
                      appState.dashboardStats.automationStatus === 'running' 
                        ? 'text-green-600' 
                        : 'text-gray-400'
                    }`}>
                      {appState.dashboardStats.automationStatus === 'running' ? '🟢' : '⚪'}
                    </div>
                    <div className="text-sm text-gray-600">
                      {appState.dashboardStats.automationStatus === 'running' ? '稼働中' : '停止中'}
                    </div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded">
                    <div className="text-3xl mb-2">{appState.dashboardStats.todayPosts}</div>
                    <div className="text-sm text-gray-600">今日の投稿</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded">
                    <div className="text-3xl mb-2">{appState.dashboardStats.scheduledPosts}</div>
                    <div className="text-sm text-gray-600">待機中</div>
                  </div>
                </div>
                
                <div className="mt-6 flex gap-4">
                  <button
                    onClick={handleAutomationToggle}
                    disabled={appState.isLoading || !appState.isConnected}
                    className={`
                      flex-1 py-3 px-4 rounded-lg font-medium transition-colors
                      ${appState.dashboardStats.automationStatus === 'running'
                        ? 'bg-red-600 text-white hover:bg-red-700'
                        : 'bg-green-600 text-white hover:bg-green-700'
                      }
                      disabled:opacity-50 disabled:cursor-not-allowed
                    `}
                  >
                    {appState.isLoading ? (
                      <span className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        処理中...
                      </span>
                    ) : (
                      appState.dashboardStats.automationStatus === 'running' 
                        ? '🛑 自動化を停止' 
                        : '▶️ 自動化を開始'
                    )}
                  </button>
                  <button
                    onClick={handleScrapingTrigger}
                    disabled={appState.isLoading || !appState.isConnected}
                    className="
                      px-6 py-3 bg-blue-600 text-white rounded-lg font-medium
                      hover:bg-blue-700 transition-colors
                      disabled:opacity-50 disabled:cursor-not-allowed
                    "
                  >
                    🕷️ 今すぐスクレイピング
                  </button>
                </div>
              </div>

              {/* スクレイピング履歴 */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold mb-4">最近のスクレイピング履歴</h2>
                <div className="space-y-2">
                  {appState.scrapingHistory.length > 0 ? (
                    appState.scrapingHistory.map((history, index) => (
                      <div
                        key={`history-${history.id || index}-${history.timestamp || Date.now()}`}
                        className={`
                          p-3 rounded border
                          ${history.status === 'success' 
                            ? 'bg-green-50 border-green-200' 
                            : 'bg-red-50 border-red-200'
                          }
                        `}
                      >
                        <div className="flex justify-between items-center">
                          <div className="flex items-center">
                            <span className={`mr-2 ${
                              history.status === 'success' ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {history.status === 'success' ? '✓' : '✗'}
                            </span>
                            <span className="text-sm">
                              {new Date(history.timestamp).toLocaleString('ja-JP')}
                            </span>
                          </div>
                          <span className="text-sm text-gray-600">{history.message}</span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 text-center py-4">履歴がありません</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* 手動投稿タブ */}
          {activeTab === 'manual' && (
            <ManualPostComponent
              onSubmit={async (data) => {
                try {
                  const response = await api.createPost(data);
                  if (response.success) {
                    await fetchDashboardStats();
                  } else {
                    throw new Error(response.error || '投稿の作成に失敗しました');
                  }
                } catch (error) {
                  console.error('Post creation error:', error);
                  setAppState(prev => ({
                    ...prev,
                    error: error instanceof Error ? error.message : '投稿の作成に失敗しました'
                  }));
                }
              }}
            />
          )}

          {/* CSV投稿タブ */}
          {activeTab === 'csv' && (
            <CSVUploadComponent
              onUpload={async (csvData) => {
                try {
                  const response = await api.processCSV({
                    csvData,
                    companyConcepts: [],
                    limit: 10,
                    sortBy: 'likes'
                  });
                  if (response.success) {
                    await fetchDashboardStats();
                  } else {
                    throw new Error(response.error || 'CSV処理に失敗しました');
                  }
                } catch (error) {
                  console.error('CSV processing error:', error);
                  setAppState(prev => ({
                    ...prev,
                    error: error instanceof Error ? error.message : 'CSV処理に失敗しました'
                  }));
                }
              }}
            />
          )}

          {/* 投稿管理タブ */}
          {activeTab === 'dashboard' && (
            <PostDashboardComponent 
              posts={appState.posts}
              onEdit={async (post) => {
                console.log('編集:', post);
              }}
              onDelete={async (postId) => {
                try {
                  const response = await api.deletePost(postId);
                  if (response.success) {
                    await fetchDashboardStats();
                  } else {
                    throw new Error(response.error || '投稿の削除に失敗しました');
                  }
                } catch (error) {
                  console.error('Post deletion error:', error);
                  setAppState(prev => ({
                    ...prev,
                    error: error instanceof Error ? error.message : '投稿の削除に失敗しました'
                  }));
                }
              }}
            />
          )}

          {/* 設定タブ */}
          {activeTab === 'settings' && (
            <SettingsComponent />
          )}
        </React.Suspense>
      </main>
    </div>
  );
};

export default AppFinal;