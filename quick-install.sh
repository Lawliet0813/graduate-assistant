#!/bin/bash

# 研究生助理系統 - 快速安裝腳本
# 作者: Claude
# 日期: 2024-11-21

set -e

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎓 研究生助理系統 - 快速安裝  "
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 檢查是否在 Mac 上
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}❌ 錯誤: 此腳本僅適用於 macOS${NC}"
    exit 1
fi

echo -e "${BLUE}步驟 1/6: 檢查 Homebrew...${NC}"
if ! command -v brew &> /dev/null; then
    echo -e "${YELLOW}⚠️  Homebrew 未安裝，正在安裝...${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo -e "${GREEN}✅ Homebrew 已安裝${NC}"
else
    echo -e "${GREEN}✅ Homebrew 已存在${NC}"
fi
echo ""

echo -e "${BLUE}步驟 2/6: 安裝 PostgreSQL...${NC}"
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠️  正在安裝 PostgreSQL@16...${NC}"
    brew install postgresql@16
    
    # 加入 PATH
    echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
    export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"
    
    echo -e "${GREEN}✅ PostgreSQL 已安裝${NC}"
else
    echo -e "${GREEN}✅ PostgreSQL 已存在${NC}"
fi
echo ""

echo -e "${BLUE}步驟 3/6: 安裝 Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  正在安裝 Python@3.12...${NC}"
    brew install python@3.12
    echo -e "${GREEN}✅ Python 已安裝${NC}"
else
    echo -e "${GREEN}✅ Python 已存在${NC}"
fi
echo ""

echo -e "${BLUE}步驟 4/6: 安裝 ChromeDriver...${NC}"
if ! command -v chromedriver &> /dev/null; then
    echo -e "${YELLOW}⚠️  正在安裝 ChromeDriver...${NC}"
    brew install chromedriver
    echo -e "${GREEN}✅ ChromeDriver 已安裝${NC}"
else
    echo -e "${GREEN}✅ ChromeDriver 已存在${NC}"
fi
echo ""

echo -e "${BLUE}步驟 5/6: 設定 Python 處環境...${NC}"
if [ -d "services/moodle-service" ]; then
    cd services/moodle-service
    
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}⚠️  正在建立 Python 處環境...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        deactivate
        echo -e "${GREEN}✅ Python 處環境已建立${NC}"
    else
        echo -e "${GREEN}✅ Python 處環境已存在${NC}"
    fi
    
    cd ../..
else
    echo -e "${YELLOW}⚠️  找不到 Moodle 服務目錄，跳過${NC}"
fi
echo ""

echo -e "${BLUE}步驟 6/6: 生成 NextAuth Secret...${NC}"
if [ -f ".env" ]; then
    if grep -q "your-nextauth-secret-change-this" .env; then
        SECRET=$(openssl rand -base64 32)
        sed -i '' "s/your-nextauth-secret-change-this-in-production/$SECRET/" .env
        echo -e "${GREEN}✅ NextAuth Secret 已生成${NC}"
    else
        echo -e "${GREEN}✅ NextAuth Secret 已設定${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  .env 檔案不存在${NC}"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ 安裝完成!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}⚠️  重要: 接下來的步驟${NC}"
echo ""
echo "1. 編輯 .env 檔案，填入你的 Google OAuth 憑證："
echo "   open -a 'Visual Studio Code' .env"
echo ""
echo "2. 啟動系統："
echo "   ./start.sh"
echo ""
echo "3. 打開瀏覽器前往："
echo "   http://localhost:3000"
echo ""
echo -e "${BLUE}📚 詳細說明請查看: SETUP_GUIDE.md${NC}"
echo ""