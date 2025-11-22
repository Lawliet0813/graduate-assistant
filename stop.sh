#!/bin/bash

# 研究生助理系統 - 停止腳本
# 作者: Claude
# 日期: 2024-11-21

set -e

echo "🛑 停止研究生助理系統..."
echo ""

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PG_DATA="/Volumes/TEAM PD20M/graduate-assistant-data/postgresql"

# 1. 停止 Next.js 開發伺服器
echo "🌐 停止 Next.js 伺服器..."
if pgrep -f "next dev" > /dev/null; then
    pkill -f "next dev"
    echo -e "${GREEN}✅ Next.js 伺服器已停止${NC}"
else
    echo -e "${YELLOW}⚠️  Next.js 伺服器未運行${NC}"
fi
echo ""

# 2. 停止 PostgreSQL
echo "🗄️  停止 PostgreSQL..."
if [ -d "$PG_DATA" ]; then
    if pg_ctl -D "$PG_DATA" status &> /dev/null; then
        pg_ctl -D "$PG_DATA" stop
        echo -e "${GREEN}✅ PostgreSQL 已停止${NC}"
    else
        echo -e "${YELLOW}⚠️  PostgreSQL 未運行${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  找不到 PostgreSQL 資料目錄${NC}"
fi
echo ""

# 3. 停止 Python Moodle 服務 (如果有運行)
echo "🐍 檢查 Python 服務..."
if pgrep -f "python.*moodle" > /dev/null; then
    pkill -f "python.*moodle"
    echo -e "${GREEN}✅ Python 服務已停止${NC}"
else
    echo -e "${YELLOW}⚠️  Python 服務未運行${NC}"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ 所有服務已停止${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""