import React, { useState } from 'react';
import { Upload, AlertCircle, CheckCircle, X } from 'lucide-react';
import type { CSVData } from '../types';

interface CSVUploadProps {
  onUpload: (data: CSVData[]) => void;
}

const CSVUpload: React.FC<CSVUploadProps> = ({ onUpload }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [previewData, setPreviewData] = useState<CSVData[]>([]);
  const [fileName, setFileName] = useState('');
  const [processOptions, setProcessOptions] = useState({
    topN: 10,
    removeDuplicates: true
  });

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const parseCSV = (text: string): CSVData[] => {
    const lines = text.split('\n').filter(line => line.trim());
    if (lines.length < 2) throw new Error('CSVファイルが空です');

    const headers = lines[0].split(',').map(h => h.trim());
    const requiredHeaders = ['投稿文', '画像URL', 'いいね数', 'ジャンル'];
    
    const headerIndices = requiredHeaders.map(reqHeader => {
      const index = headers.findIndex(h => h === reqHeader);
      if (index === -1) throw new Error(`必須ヘッダー「${reqHeader}」が見つかりません`);
      return index;
    });

    const data: CSVData[] = [];
    
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim());
      if (values.length < headers.length) continue;
      
      data.push({
        postText: values[headerIndices[0]],
        imageUrl: values[headerIndices[1]],
        likes: parseInt(values[headerIndices[2]]) || 0,
        genre: values[headerIndices[3]]
      });
    }

    return data;
  };

  const handleFile = (file: File) => {
    if (file.size > 5 * 1024 * 1024) {
      setErrorMessage('ファイルサイズは5MB以内にしてください');
      setUploadStatus('error');
      return;
    }

    if (!file.name.endsWith('.csv')) {
      setErrorMessage('CSVファイルをアップロードしてください');
      setUploadStatus('error');
      return;
    }

    setFileName(file.name);
    setUploadStatus('processing');
    
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target?.result as string;
        const data = parseCSV(text);
        
        let processedData = [...data];
        
        if (processOptions.removeDuplicates) {
          const seen = new Set<string>();
          processedData = processedData.filter(item => {
            const key = `${item.postText}-${item.imageUrl}`;
            if (seen.has(key)) return false;
            seen.add(key);
            return true;
          });
        }
        
        processedData.sort((a, b) => b.likes - a.likes);
        
        if (processOptions.topN > 0) {
          processedData = processedData.slice(0, processOptions.topN);
        }
        
        setPreviewData(processedData);
        setUploadStatus('success');
        setErrorMessage('');
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : 'CSVの解析に失敗しました');
        setUploadStatus('error');
      }
    };
    
    reader.readAsText(file);
  };

  const handleProcess = () => {
    onUpload(previewData);
  };

  const clearUpload = () => {
    setUploadStatus('idle');
    setPreviewData([]);
    setFileName('');
    setErrorMessage('');
  };

  return (
    <div className="space-y-6">
      {uploadStatus === 'idle' && (
        <form onDragEnter={handleDrag} onSubmit={(e) => e.preventDefault()}>
          <label htmlFor="csv-upload" className={`
            flex flex-col items-center justify-center w-full h-64 
            border-2 border-dashed rounded-lg cursor-pointer 
            transition-colors duration-200
            ${dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50 hover:bg-gray-100'}
          `}>
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              <Upload className={`w-12 h-12 mb-4 ${dragActive ? 'text-blue-500' : 'text-gray-400'}`} />
              <p className="mb-2 text-sm text-gray-500">
                <span className="font-semibold">クリックしてアップロード</span> またはドラッグ＆ドロップ
              </p>
              <p className="text-xs text-gray-500">CSV (最大5MB)</p>
              <p className="text-xs text-gray-400 mt-2">必須項目: 投稿文, 画像URL, いいね数, ジャンル</p>
            </div>
            <input id="csv-upload" type="file" className="hidden" accept=".csv" onChange={handleChange} />
          </label>
          {dragActive && (
            <div 
              className="absolute inset-0 z-10" 
              onDragEnter={handleDrag} 
              onDragLeave={handleDrag} 
              onDragOver={handleDrag} 
              onDrop={handleDrop}
            />
          )}
        </form>
      )}

      {uploadStatus === 'processing' && (
        <div className="flex items-center justify-center p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      )}

      {uploadStatus === 'error' && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
              <span className="text-sm text-red-800">{errorMessage}</span>
            </div>
            <button onClick={clearUpload} className="text-red-400 hover:text-red-600">
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>
      )}

      {uploadStatus === 'success' && (
        <div className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-400 mr-2" />
                <span className="text-sm text-green-800">
                  {fileName} - {previewData.length}件のデータを読み込みました
                </span>
              </div>
              <button onClick={clearUpload} className="text-green-400 hover:text-green-600">
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">処理オプション</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label htmlFor="topN" className="text-sm text-gray-700">
                  上位N件のみ処理
                </label>
                <input
                  id="topN"
                  type="number"
                  min="1"
                  max="100"
                  value={processOptions.topN}
                  onChange={(e) => setProcessOptions({...processOptions, topN: parseInt(e.target.value) || 10})}
                  className="w-20 px-2 py-1 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex items-center">
                <input
                  id="removeDuplicates"
                  type="checkbox"
                  checked={processOptions.removeDuplicates}
                  onChange={(e) => setProcessOptions({...processOptions, removeDuplicates: e.target.checked})}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="removeDuplicates" className="ml-2 text-sm text-gray-700">
                  重複を削除
                </label>
              </div>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <h3 className="text-lg font-semibold p-4 border-b">プレビュー</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">順位</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">投稿文</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">いいね数</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ジャンル</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {previewData.slice(0, 5).map((item, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">{index + 1}</td>
                      <td className="px-4 py-4 text-sm text-gray-900 max-w-xs truncate">{item.postText}</td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">{item.likes.toLocaleString()}</td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">{item.genre}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {previewData.length > 5 && (
                <div className="px-4 py-3 bg-gray-50 text-sm text-gray-500 text-center">
                  他 {previewData.length - 5} 件
                </div>
              )}
            </div>
          </div>

          <button
            onClick={handleProcess}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-200"
          >
            データを処理して投稿候補を生成
          </button>
        </div>
      )}
    </div>
  );
};

export default CSVUpload;