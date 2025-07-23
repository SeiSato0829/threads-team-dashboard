#!/bin/bash

echo "🚀 限界突破！チーム&モバイル完全対応システム起動中..."
echo

# カラフル出力用
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# IPアドレス取得
SERVER_IP=$(hostname -I | awk '{print $1}')

echo -e "${GREEN}📱 チーム&モバイル完全対応ダッシュボード${NC}"
echo -e "${BLUE}================================${NC}"
echo

echo -e "${YELLOW}✅ アクセス情報:${NC}"
echo -e "🌐 社内PC・ラップトップ: ${GREEN}http://${SERVER_IP}:8501${NC}"
echo -e "📱 スマートフォン・タブレット: ${GREEN}http://${SERVER_IP}:8501${NC}"
echo -e "👥 チーム共有: ${GREEN}同じネットワーク内全デバイス対応${NC}"
echo

echo -e "${YELLOW}📋 対応デバイス:${NC}"
echo "✅ Windows PC・Mac・Linux"
echo "✅ iPhone・Android・iPad"  
echo "✅ 社内全メンバーのデバイス"
echo "✅ WiFi・有線ネットワーク対応"
echo

echo -e "${YELLOW}🚀 機能一覧:${NC}"
echo "✅ AI投稿生成 (LiteWEB+スタイル)"
echo "✅ 2週間分一括スケジュール"
echo "✅ モバイル最適化UI"
echo "✅ チーム共有機能"
echo "✅ QRコードアクセス"
echo "✅ リアルタイム同期"
echo

# 既存のStreamlitプロセスを停止
echo -e "${YELLOW}🔄 システム準備中...${NC}"
pkill -f streamlit > /dev/null 2>&1
sleep 2

# PATHを設定
export PATH=$PATH:/home/music-020/.local/bin

# ネットワーク公開でStreamlit起動
echo -e "${GREEN}🌟 システム起動中...${NC}"
echo

# バックグラウンドでStreamlit起動
nohup streamlit run MOBILE_TEAM_DASHBOARD.py \
    --server.address 0.0.0.0 \
    --server.port 8501 \
    --server.headless true \
    --server.runOnSave true \
    --server.enableCORS false \
    --server.enableXsrfProtection false > streamlit_team.log 2>&1 &

# 起動待機
sleep 5

echo -e "${GREEN}🎉 システム起動完了！${NC}"
echo
echo -e "${RED}📱 今すぐアクセス可能:${NC}"
echo -e "${GREEN}http://${SERVER_IP}:8501${NC}"
echo
echo -e "${YELLOW}💡 使用方法:${NC}"
echo "1. 上記URLをブラウザで開く"
echo "2. スマホの場合はQRコードをスキャン"  
echo "3. チームメンバーに同じURLを共有"
echo "4. 投稿管理・分析・編集すべて可能"
echo
echo -e "${BLUE}📞 問い合わせ: システム管理者まで${NC}"
echo

# ログファイル確認
if [ -f "streamlit_team.log" ]; then
    echo -e "${YELLOW}📋 システムログ:${NC}"
    tail -n 5 streamlit_team.log
fi

echo
echo -e "${GREEN}🌟 チーム&モバイル完全対応システム稼働中！${NC}"