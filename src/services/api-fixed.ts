// 修正版APIサービス - 問題を段階的に解決

// シンプルな型定義（循環参照を避ける）
interface SimpleApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

// 環境変数を安全に取得
const getApiUrl = () => {
  try {
    return (window as any).import?.meta?.env?.VITE_API_URL || 'http://localhost:5000';
  } catch {
    return 'http://localhost:5000';
  }
};

const API_BASE_URL = getApiUrl();

// シンプルなfetch関数
async function safeFetch(url: string, options?: RequestInit): Promise<Response> {
  try {
    return await fetch(url, options);
  } catch (error) {
    console.error('Fetch error:', error);
    throw error;
  }
}

export const api = {
  async checkHealth(): Promise<boolean> {
    try {
      const response = await safeFetch(`${API_BASE_URL}/`);
      return response.ok;
    } catch {
      return false;
    }
  },

  async getPosts(options?: any): Promise<SimpleApiResponse> {
    try {
      const params = new URLSearchParams();
      
      if (options?.filter) {
        Object.entries(options.filter).forEach(([key, value]) => {
          if (value !== undefined) {
            params.append(key, JSON.stringify(value));
          }
        });
      }
      
      const response = await safeFetch(
        `${API_BASE_URL}/api/posts?${params}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : '投稿の取得に失敗しました'
      };
    }
  },

  async getDashboardStats(): Promise<SimpleApiResponse> {
    try {
      const response = await safeFetch(
        `${API_BASE_URL}/api/dashboard/stats`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'ダッシュボード統計の取得に失敗しました'
      };
    }
  },

  async getScrapingHistory(limit = 50): Promise<SimpleApiResponse> {
    try {
      const response = await safeFetch(
        `${API_BASE_URL}/api/scraping/history?limit=${limit}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'スクレイピング履歴の取得に失敗しました'
      };
    }
  },

  async deletePost(id: string): Promise<SimpleApiResponse> {
    try {
      const response = await safeFetch(
        `${API_BASE_URL}/api/posts/${id}`,
        {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : '投稿の削除に失敗しました'
      };
    }
  },

  async createPost(data: any): Promise<SimpleApiResponse> {
    try {
      const formData = new FormData();
      formData.append('text', data.text);
      formData.append('genre', data.genre);
      formData.append('scheduledTime', data.scheduledTime);
      formData.append('aiMode', data.aiMode.toString());
      
      if (data.images) {
        data.images.forEach((image: File) => {
          formData.append('images', image);
        });
      }
      
      const response = await safeFetch(
        `${API_BASE_URL}/api/posts`,
        {
          method: 'POST',
          body: formData,
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      return { success: true, data: result };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : '投稿の作成に失敗しました'
      };
    }
  },

  async processCSV(data: any): Promise<SimpleApiResponse> {
    try {
      const response = await safeFetch(
        `${API_BASE_URL}/api/process-csv`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      return { success: true, data: result };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'CSV処理に失敗しました'
      };
    }
  },

  async startAutomation(): Promise<SimpleApiResponse> {
    try {
      const response = await safeFetch(
        `${API_BASE_URL}/api/automation/start`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      return { success: true, data: result };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : '自動化の開始に失敗しました'
      };
    }
  },

  async stopAutomation(): Promise<SimpleApiResponse> {
    try {
      const response = await safeFetch(
        `${API_BASE_URL}/api/automation/stop`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      return { success: true, data: result };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : '自動化の停止に失敗しました'
      };
    }
  },

  async triggerScraping(): Promise<SimpleApiResponse> {
    try {
      const response = await safeFetch(
        `${API_BASE_URL}/api/scraping/trigger`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      return { success: true, data: result };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'スクレイピングの実行に失敗しました'
      };
    }
  }
};