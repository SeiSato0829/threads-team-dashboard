# 📱 Threads Team Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

社内チーム共有・モバイル完全対応のThreads投稿管理システム

## 🚀 Features

- **AI投稿生成** - LiteWEB+スタイルで自動生成（絵文字なし、1万円正確表記）
- **2週間分一括生成** - 最適な時間帯（9時、12時、19時、21時）に自動スケジュール
- **チーム共有** - URLを共有するだけで全員アクセス可能
- **モバイル対応** - スマホ・タブレットで完璧動作
- **リアルタイム同期** - チーム間でデータ自動同期
- **パフォーマンス分析** - 投稿効果を可視化

## 📱 Access

### Public URL (After Deploy)
```
https://your-app-name.streamlit.app
```

### Local Development
```bash
streamlit run THREADS_DASHBOARD.py
```

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.12
- **Database**: SQLite
- **Visualization**: Plotly
- **Deployment**: Streamlit Cloud

## 📋 Setup

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/threads-dashboard.git
cd threads-dashboard
```

### 2. Install Dependencies
```bash
pip install -r requirements_streamlit.txt
```

### 3. Run Locally
```bash
streamlit run THREADS_DASHBOARD.py
```

## 🌐 Deployment

### Streamlit Cloud (Recommended)

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select repository and branch
5. Deploy!

### Environment Variables

Set these in Streamlit Cloud Secrets:
```toml
[database]
db_path = "threads_optimized.db"

[security]
admin_password = "your-secure-password"
```

## 📱 Mobile Access

1. Open browser on mobile device
2. Enter the Streamlit Cloud URL
3. Enjoy full functionality!

## 🔐 Security

- HTTPS encryption
- Optional password protection
- Team access control

## 👥 Team Usage

1. **Admin**: Deploy and manage
2. **Team Members**: Access via shared URL
3. **Mobile Users**: Full functionality on smartphones

## 📊 Features Overview

### Dashboard
- Real-time metrics
- Post history
- Performance analysis

### AI Generation
- 20 unique patterns
- Business-focused content
- Optimal timing

### Team Collaboration
- Shared access
- Real-time updates
- Mobile-friendly UI

## 🆘 Support

- Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/threads-dashboard/issues)
- Documentation: [Wiki](https://github.com/YOUR_USERNAME/threads-dashboard/wiki)

## 📄 License

MIT License - Feel free to use and modify!

---

Made with ❤️ for efficient team collaboration