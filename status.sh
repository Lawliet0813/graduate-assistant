#!/bin/bash

# 研究生助理系統 - 狀態檢查腳本
# 作者: Claude
# 日期: 2024-11-21

echo "🔍 研究生助理系統 - 服務狀態"
echo ""

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PG_DATA="/Volumes/TEAM PD20M/graduate-assistant-data/postgresql"

# 1. 檢查外接硬碟
echo -n "📀 外接硬碟: "
if [ -d "/Volumes/TEAM PD20M/graduate-assistant-data" ]; then
    echo -e "${GREEN}✅ 已連接${NC}"
else
    echo -e "${RED}❌ 未連接${NC}"
fi

# 2. 檢查 PostgreSQL
echo -n "🗄️  PostgreSQL: "
if command -v pg_ctl &> /dev/null; then
    if [ -d "$PG_DATA" ]; then
        if pg_ctl -D "$PG_DATA" status &> /dev/null; then
            echo -e "${GREEN}✅ 運行中${NC}"
        else
            echo -e "${YELLOW}⚠️  已安裝但未啟動${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  已安裝但未初始化${NC}"
    fi
else
    echo -e "${RED}❌ 未安裝${NC}"
fi

# 3. 檢查資料庫
echo -n "🗄️  資料庫: "
if command -v psql &> /dev/null; then
    if psql -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw graduate_assistant; then
        echo -e "${GREEN}✅ 已創建${NC}"
    else
        echo -e "${YELLOW}⚠️  未創建${NC}"
    fi
else
    echo -e "${RED}❌ PostgreSQL 未安裝${NC}"
fi

# 4. 檢查 Next.js
echo -n "🌐 Next.js: "
if pgrep -f "next dev" > /dev/null; then
    echo -e "${GREEN}✅ 運行中${NC}"
    echo "   → http://localhost:3000"
else
    echo -e "${YELLOW}⚠️  未運行${NC}"
fi

# 5. 檢查 Python 服務
echo -n "🐍 Python Moodle 服務: "
if pgrep -f "python.*moodle" > /dev/null; then
    echo -e "${GREEN}✅ 運行中${NC}"
else
    echo -e "${YELLOW}⚠️  未運行${NC}"
fi

# 6. 檢查 node_modules
echo -n "📦 Node.js 依賴: "
if [ -d "node_modules" ]; then
    echo -e "${GREEN}✅ 已安裝${NC}"
else
    echo -e "${RED}❌ 未安裝${NC}"
    echo "   請執行: npm install"
fi

# 7. 檢查 .env 檔案
echo -n "⚙️  環境變數: "
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ 已設定${NC}"
    
    # 檢查關鍵設定
    missing_keys=()
    
    if ! grep -q "DATABASE_URL=" .env || grep -q "DATABASE_URL=\"postgresql://postgres:postgres@localhost" .env; then
        missing_keys+=("DATABASE_URL")
    fi
    
    if ! grep -q "NEXTAUTH_SECRET=" .env || grep -q "your-nextauth-secret" .env; then
        missing_keys+=("NEXTAUTH_SECRET")
    fi
    
    if [ ${#missing_keys[@]} -gt 0 ]; then
        echo -e "   ${YELLOW}⚠️  需要設定: ${missing_keys[*]}${NC}"
    fi
else
    echo -e "${RED}❌ 未設定${NC}"
    echo "   請執行: cp .env.example .env"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 快速指令:"
echo "   ./start.sh   - 啟動所有服務"
echo "   ./stop.sh    - 停止所有服務"
echo "   ./status.sh  - 檢查服務狀態"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""