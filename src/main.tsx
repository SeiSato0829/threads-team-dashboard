// エントリーポイント - シンプル版

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App-Final';
import { ErrorBoundary } from './components/ErrorBoundary';
import './index.css';

// アプリケーションのマウント
const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Root element not found');
}

const root = ReactDOM.createRoot(rootElement);

root.render(
  <ErrorBoundary>
    <App />
  </ErrorBoundary>
);

// アプリケーション起動後にローディング画面を非表示
setTimeout(() => {
  const loadingScreen = document.getElementById('loading-screen');
  if (loadingScreen) {
    loadingScreen.classList.add('hidden');
  }
}, 500);