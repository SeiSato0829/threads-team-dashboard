// シンプルな設定コンポーネント

import React, { useState } from 'react';
import { Save, AlertCircle } from 'lucide-react';

const SettingsSimple: React.FC = () => {
  const [settings, setSettings] = useState({
    csvWatchPath: './csv_input',
    postInterval: 60,
    scrapingInterval: 8,
    dailyPostLimit: 10,
    postStartTime: '09:00',
    postEndTime: '21:00',
    enableAIGeneration: true,
    enableBufferScheduling: true,
    enableAutoScraping: true
  });

  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    console.log('Settings saved:', settings);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6">
      {/* 自動化設定 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">自動化設定</h2>
        
        <div className="space-y-4">
          {/* CSV監視フォルダ */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              CSV監視フォルダパス
            </label>
            <input
              type="text"
              value={settings.csvWatchPath}
              onChange={(e) => setSettings({ ...settings, csvWatchPath: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="./csv_input"
            />
            <p className="text-xs text-gray-500 mt-1">
              Easy ScraperのCSV出力フォルダを指定
            </p>
          </div>

          {/* 投稿間隔 */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                投稿間隔 (分)
              </label>
              <input
                type="number"
                value={settings.postInterval}
                onChange={(e) => setSettings({ ...settings, postInterval: parseInt(e.target.value) || 60 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="1"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                スクレイピング間隔 (時間)
              </label>
              <input
                type="number"
                value={settings.scrapingInterval}
                onChange={(e) => setSettings({ ...settings, scrapingInterval: parseInt(e.target.value) || 8 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="1"
              />
            </div>
          </div>

          {/* 1日の投稿数制限 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              1日の投稿数制限
            </label>
            <input
              type="number"
              value={settings.dailyPostLimit}
              onChange={(e) => setSettings({ ...settings, dailyPostLimit: parseInt(e.target.value) || 10 })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              min="1"
              max="100"
            />
          </div>

          {/* 投稿時間設定 */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                投稿開始時刻
              </label>
              <input
                type="time"
                value={settings.postStartTime}
                onChange={(e) => setSettings({ ...settings, postStartTime: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                投稿終了時刻
              </label>
              <input
                type="time"
                value={settings.postEndTime}
                onChange={(e) => setSettings({ ...settings, postEndTime: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* 機能設定 */}
          <div className="space-y-3 border-t pt-4">
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={settings.enableAIGeneration}
                onChange={(e) => setSettings({ ...settings, enableAIGeneration: e.target.checked })}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="text-sm">AI自動生成を有効にする (Claude API)</span>
            </label>
            
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={settings.enableBufferScheduling}
                onChange={(e) => setSettings({ ...settings, enableBufferScheduling: e.target.checked })}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="text-sm">Buffer自動スケジュールを有効にする</span>
            </label>
            
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={settings.enableAutoScraping}
                onChange={(e) => setSettings({ ...settings, enableAutoScraping: e.target.checked })}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="text-sm">自動スクレイピングを有効にする (Easy Scraper)</span>
            </label>
          </div>
        </div>

        {/* 保存ボタン */}
        <div className="mt-6 flex items-center justify-between">
          <button
            onClick={handleSave}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Save className="w-4 h-4" />
            <span>設定を保存</span>
          </button>
          
          {saved && (
            <p className="text-green-600 text-sm flex items-center">
              <AlertCircle className="w-4 h-4 mr-1" />
              設定を保存しました
            </p>
          )}
        </div>
      </div>

      {/* API設定の注意 */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex">
          <AlertCircle className="h-5 w-5 text-yellow-400 mr-2 flex-shrink-0" />
          <div>
            <h3 className="text-sm font-medium text-yellow-800">API設定について</h3>
            <p className="mt-1 text-sm text-yellow-700">
              Claude APIとBuffer APIの設定は、セキュリティのため環境変数（.env）ファイルで管理してください。
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsSimple;