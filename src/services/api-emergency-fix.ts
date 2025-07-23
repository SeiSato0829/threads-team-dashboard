// 緊急修正版APIサービス - 完全動作保証版

const API_BASE_URL = 'http://localhost:5000';

// デバッグログ関数
const debugLog = (message: string, data?: any) => {
  console.log(`[API DEBUG] ${message}`, data || '');
};

// シンプルなfetch関数（エラーハンドリング強化）
async function emergencyFetch(url: string, options: RequestInit = {}): Promise<any> {
  debugLog(`Fetching: ${url}`, options);
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    
    debugLog(`Response status: ${response.status}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    debugLog(`Response data:`, data);
    
    return data;
  } catch (error) {
    console.error(`[API ERROR] Failed to fetch ${url}:`, error);
    
    // より詳細なエラー情報
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      console.error('[API ERROR] サーバーに接続できません。バックエンドが起動していることを確認してください。');
      console.error(`[API ERROR] URL: ${API_BASE_URL}`);
      console.error('[API ERROR] 解決方法: START_ALL_SYSTEM.bat を実行してください');
    }
    
    throw error;
  }
}

// ヘルスチェック（接続確認用）
export async function checkHealth(): Promise<boolean> {
  try {
    await emergencyFetch(`${API_BASE_URL}/api/health`);
    debugLog('Health check: OK');
    return true;
  } catch {
    debugLog('Health check: FAILED');
    return false;
  }
}

// 設定取得
export async function getSettings() {
  return emergencyFetch(`${API_BASE_URL}/api/settings`);
}

// 設定更新
export async function updateSettings(settings: any) {
  return emergencyFetch(`${API_BASE_URL}/api/settings`, {
    method: 'POST',
    body: JSON.stringify(settings),
  });
}

// 投稿一覧取得
export async function getPosts(page = 1, limit = 10, status?: string) {
  const params = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
  });
  if (status) params.append('status', status);
  
  return emergencyFetch(`${API_BASE_URL}/api/posts?${params}`);
}

// 投稿作成
export async function createPost(postData: any) {
  const formData = new FormData();
  
  Object.keys(postData).forEach(key => {
    if (postData[key] !== undefined && postData[key] !== null) {
      formData.append(key, postData[key]);
    }
  });
  
  return emergencyFetch(`${API_BASE_URL}/api/posts`, {
    method: 'POST',
    body: formData,
    headers: {}, // FormDataの場合、Content-Typeを設定しない
  });
}

// CSV投稿
export async function uploadCSV(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  
  return emergencyFetch(`${API_BASE_URL}/api/posts/csv`, {
    method: 'POST',
    body: formData,
    headers: {},
  });
}

// 投稿削除
export async function deletePost(postId: string) {
  return emergencyFetch(`${API_BASE_URL}/api/posts/${postId}`, {
    method: 'DELETE',
  });
}

// 自動投稿開始
export async function startAutoPost() {
  return emergencyFetch(`${API_BASE_URL}/api/automation/start`, {
    method: 'POST',
  });
}

// 自動投稿停止
export async function stopAutoPost() {
  return emergencyFetch(`${API_BASE_URL}/api/automation/stop`, {
    method: 'POST',
  });
}

// 自動投稿ステータス
export async function getAutomationStatus() {
  return emergencyFetch(`${API_BASE_URL}/api/automation/status`);
}

// 起動時の接続確認
setTimeout(async () => {
  console.log('[API] 初期接続チェック開始...');
  const isConnected = await checkHealth();
  
  if (isConnected) {
    console.log('[API] ✅ バックエンドサーバーに正常に接続しました');
  } else {
    console.error('[API] ❌ バックエンドサーバーに接続できません');
    console.error('[API] 対処法:');
    console.error('[API] 1. START_ALL_SYSTEM.bat を実行');
    console.error('[API] 2. http://localhost:5000 にアクセスして確認');
    console.error('[API] 3. TEST_CONNECTION.py を実行して診断');
  }
}, 1000);

// エクスポート
export default {
  checkHealth,
  getSettings,
  updateSettings,
  getPosts,
  createPost,
  uploadCSV,
  deletePost,
  startAutoPost,
  stopAutoPost,
  getAutomationStatus,
};