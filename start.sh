#!/bin/bash

# 研究生助理系統 - 啟動腳本
# 作者: Claude
# 日期: 2024-11-21

set -e

echo "🚀 啟動研究生助理系統..."
echo ""

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 檢查外接硬碟
echo "📀 檢查外接硬碟..."
if [ ! -d "/Volumes/TEAM PD20M/graduate-assistant-data" ]; then
    echo -e "${RED}❌ 錯誤: 找不到外接硬碟或資料目錄${NC}"
    echo "   請確保 TEAM PD20M 硬碟已連接"
    exit 1
fi
echo -e "${GREEN}✅ 外接硬碟已連接${NC}"
echo ""

# 2. 檢查 PostgreSQL 是否已安裝
echo "🗄️  檢查 PostgreSQL..."
if ! command -v pg_ctl &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL 未安裝${NC}"
    echo "   請執行: brew install postgresql@16"
    exit 1
fi

# 3. 檢查資料庫目錄
PG_DATA="/Volumes/TEAM PD20M/graduate-assistant-data/postgresql"
if [ ! -d "$PG_DATA" ]; then
    echo -e "${YELLOW}⚠️  資料庫目錄不存在，正在初始化...${NC}"
    initdb -D "$PG_DATA"
    echo -e "${GREEN}✅ 資料庫初始化完成${NC}"
fi

# 4. 啟動 PostgreSQL
echo "🗄️  啟動 PostgreSQL..."
if pg_ctl -D "$PG_DATA" status &> /dev/null; then
    echo -e "${YELLOW}⚠️  PostgreSQL 已在運行中${NC}"
else
    pg_ctl -D "$PG_DATA" -l "$PG_DATA/logfile" start
    sleep 2
    echo -e "${GREEN}✅ PostgreSQL 已啟動${NC}"
fi
echo ""

# 5. 檢查資料庫是否存在
echo "🗄️  檢查資料庫..."
if ! psql -lqt | cut -d \| -f 1 | grep -qw graduate_assistant; then
    echo -e "${YELLOW}⚠️  資料庫不存在，正在創建...${NC}"
    createdb graduate_assistant
    echo -e "${GREEN}✅ 資料庫已創建${NC}"
else
    echo -e "${GREEN}✅ 資料庫已存在${NC}"
fi
echo ""

# 6. 檢查 Node.js 依賴
echo "📦 檢查 Node.js 依賴..."
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules 不存在，正在安裝...${NC}"
    npm install
    echo -e "${GREEN}✅ 依賴安裝完成${NC}"
else
    echo -e "${GREEN}✅ 依賴已安裝${NC}"
fi
echo ""

# 7. 檢查並同步資料庫結構
echo "🔄 同步資料庫結構..."
npm run db:push
echo ""

# 8. 啟動開發伺服器
echo "🌐 啟動 Next.js 開發伺服器..."
echo -e "${GREEN}✅ 服務啟動中...${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 系統已啟動!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 應用網址: http://localhost:3000"
echo "📊 資料庫: PostgreSQL (外接硬碟)"
echo "📁 資料目錄: /Volumes/TEAM PD20M/graduate-assistant-data"
echo ""
echo "💡 提示:"
echo "   - 按 Ctrl+C 停止伺服器"
echo "   - 使用 ./stop.sh 停止所有服務"
echo "   - 使用 ./status.sh 檢查服務狀態"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 9. 執行 Next.js
npm run dev