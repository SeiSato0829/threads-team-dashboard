// 完全な型定義ファイル - エラーを防ぐための厳密な型定義

// 投稿データの型定義
export interface Post {
  id: string;
  text: string;
  imageUrls: string[];
  genre: string;
  scheduledTime: string;
  status: 'pending' | 'scheduled' | 'posted' | 'failed';
  createdAt: string;
  updatedAt: string;
  bufferSentTime?: string;
  referencePost?: string;
  conceptSource?: string;
  // 多様性システム用の追加フィールド
  isUnique?: boolean;
  retryAttempts?: number;
  diversityScore?: number;
}

// 手動投稿フォームの型定義
export interface ManualPostForm {
  text: string;
  images: File[];
  genre: string;
  scheduledTime: string;
  aiMode: boolean;
  useDiversity?: boolean; // 多様性モードの有効/無効
}

// CSVデータの型定義
export interface CSVData {
  postText: string;
  imageUrl: string;
  likes: number;
  genre: string;
  source?: string; // twitter/threads等のソース
  originalUrl?: string; // 元の投稿URL
}

// 自社構想の型定義
export interface CompanyConcept {
  id?: string;
  keywords: string;
  genre: string;
  reflectionStatus: boolean;
  createdAt?: string;
}

// API レスポンスの型定義
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// 自動化設定の型定義
export interface AutomationSettings {
  csvWatchPath: string;
  postInterval: number; // 分単位
  scrapingInterval: number; // 時間単位
  dailyPostLimit: number;
  postStartTime: string; // HH:MM形式
  postEndTime: string; // HH:MM形式
  enableAIGeneration: boolean;
  enableBufferScheduling: boolean;
  enableAutoScraping: boolean;
}

// スクレイピング履歴の型定義
export interface ScrapingHistory {
  id: string;
  timestamp: string;
  status: 'success' | 'error' | 'failed';
  message: string;
  postsFound?: number;
  postsProcessed?: number;
  error?: string;
}

// ダッシュボード統計の型定義
export interface DashboardStats {
  totalPosts: number;
  scheduledPosts: number;
  completedPosts: number;
  failedPosts: number;
  todayPosts: number;
  automationStatus: 'running' | 'stopped' | 'error';
  lastScraping?: string;
  nextScraping?: string;
  nextPost?: string;
}

// Buffer API設定の型定義
export interface BufferConfig {
  accessToken: string;
  profileId: string;
  enabled: boolean;
}

// Claude API設定の型定義
export interface ClaudeConfig {
  apiKey: string;
  model: string;
  enabled: boolean;
}

// 環境設定の型定義
export interface EnvironmentConfig {
  nodeEnv: 'development' | 'production' | 'test';
  apiUrl: string;
  uploadUrl: string;
  maxFileSize: number;
  allowedFileTypes: string[];
}

// エラーレスポンスの型定義
export interface ErrorResponse {
  error: string;
  details?: any;
  timestamp: Date;
  path?: string;
}

// ファイルアップロードレスポンスの型定義
export interface FileUploadResponse {
  success: boolean;
  files?: string[]; // アップロードされたファイルのURL
  error?: string;
}

// 投稿生成リクエストの型定義
export interface GeneratePostRequest {
  text: string;
  genre: string;
  referencePost?: string[];
  useDiversity?: boolean;
  style?: PostStyle;
}

// 投稿スタイルの型定義
export type PostStyle = 
  | 'story'
  | 'question'
  | 'tips'
  | 'news'
  | 'review'
  | 'comparison'
  | 'listicle'
  | 'emotional';

// 投稿生成レスポンスの型定義
export interface GeneratePostResponse {
  success: boolean;
  originalText: string;
  improvedText: string;
  modelUsed: string;
  characterCount: number;
  isUnique?: boolean;
  retryAttempts?: number;
}

// CSV処理リクエストの型定義
export interface ProcessCSVRequest {
  csvData: CSVData[];
  companyConcepts: CompanyConcept[];
  limit?: number;
  sortBy?: 'likes' | 'date';
}

// CSV処理レスポンスの型定義
export interface ProcessCSVResponse {
  success: boolean;
  processedCount: number;
  posts: Post[];
  skippedCount?: number;
  errors?: string[];
}

// WebSocket イベントの型定義
export interface WebSocketEvent {
  type: 'automation_status' | 'new_post' | 'scraping_update' | 'error';
  data: any;
  timestamp: Date;
}

// ページネーションの型定義
export interface Pagination {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

// フィルターオプションの型定義
export interface FilterOptions {
  status?: Post['status'][];
  genre?: string[];
  dateFrom?: Date;
  dateTo?: Date;
  searchText?: string;
}

// ソートオプションの型定義
export interface SortOptions {
  field: 'scheduledTime' | 'createdAt' | 'likes' | 'status';
  order: 'asc' | 'desc';
}

// バリデーションエラーの型定義
export interface ValidationError {
  field: string;
  message: string;
  value?: any;
}

// アプリケーション状態の型定義
export interface AppState {
  posts: Post[];
  isLoading: boolean;
  error: string | null;
  automationSettings: AutomationSettings;
  dashboardStats: DashboardStats;
  scrapingHistory: ScrapingHistory[];
  isConnected: boolean;
}