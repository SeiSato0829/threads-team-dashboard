// API修正パッチ
// getDashboardStats関数を追加

export const getDashboardStats = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/stats', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      // エラーでも基本的なデフォルト値を返す
      return {
        totalPosts: 0,
        scheduledPosts: 0,
        publishedPosts: 0,
        totalEngagement: 0,
        avgEngagementRate: 0,
        lastPostDate: null
      };
    }
    
    return await response.json();
  } catch (error) {
    console.log('Dashboard stats not critical - continuing with defaults');
    // エラーでも動作を継続
    return {
      totalPosts: 0,
      scheduledPosts: 0,
      publishedPosts: 0,
      totalEngagement: 0,
      avgEngagementRate: 0,
      lastPostDate: null
    };
  }
};

// 既存のAPIオブジェクトに追加
if (window.api) {
  window.api.getDashboardStats = getDashboardStats;
}