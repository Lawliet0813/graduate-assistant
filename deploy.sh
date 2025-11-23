#!/bin/bash

# 研究生智能助理系統 - 快速部署腳本

set -e  # 遇到錯誤立即停止

echo "🚀 研究生智能助理系統 - 部署腳本"
echo "========================================="
echo ""

# 顏色定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 檢查必要工具
check_tools() {
    echo -e "${BLUE}檢查必要工具...${NC}"

    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js 未安裝${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Node.js $(node --version)${NC}"

    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm 未安裝${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ npm $(npm --version)${NC}"

    if ! command -v git &> /dev/null; then
        echo -e "${RED}❌ Git 未安裝${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Git $(git --version | head -n1)${NC}"

    echo ""
}

# 檢查環境變數
check_env() {
    echo -e "${BLUE}檢查環境變數...${NC}"

    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠ .env 檔案不存在${NC}"
        echo -e "${YELLOW}正在從 .env.example 複製...${NC}"
        cp .env.example .env
        echo -e "${YELLOW}請編輯 .env 檔案並填入您的設定${NC}"
        echo -e "${RED}部署前請先設定環境變數！${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ .env 檔案存在${NC}"
    echo ""
}

# 安裝依賴
install_deps() {
    echo -e "${BLUE}安裝依賴套件...${NC}"
    npm install
    echo -e "${GREEN}✓ 依賴安裝完成${NC}"
    echo ""
}

# 資料庫設定
setup_database() {
    echo -e "${BLUE}設定資料庫...${NC}"

    # 檢查 DATABASE_URL
    if ! grep -q "DATABASE_URL=" .env; then
        echo -e "${RED}❌ 請在 .env 中設定 DATABASE_URL${NC}"
        exit 1
    fi

    echo -e "${YELLOW}生成 Prisma Client...${NC}"
    npm run db:generate

    echo -e "${YELLOW}推送資料庫 Schema...${NC}"
    npm run db:push

    echo -e "${GREEN}✓ 資料庫設定完成${NC}"
    echo ""
}

# 建置應用程式
build_app() {
    echo -e "${BLUE}建置應用程式...${NC}"
    npm run build
    echo -e "${GREEN}✓ 建置完成${NC}"
    echo ""
}

# Vercel 部署
deploy_vercel() {
    echo -e "${BLUE}部署到 Vercel...${NC}"

    if ! command -v vercel &> /dev/null; then
        echo -e "${YELLOW}安裝 Vercel CLI...${NC}"
        npm install -g vercel
    fi

    echo -e "${YELLOW}執行 Vercel 部署...${NC}"
    vercel --prod

    echo -e "${GREEN}✓ Vercel 部署完成${NC}"
    echo ""
}

# 主選單
main() {
    check_tools

    echo "請選擇操作:"
    echo "1) 本地開發設定"
    echo "2) 建置並測試"
    echo "3) 部署到 Vercel"
    echo "4) 完整部署流程"
    echo "5) 退出"
    echo ""
    read -p "請輸入選項 [1-5]: " choice

    case $choice in
        1)
            echo ""
            check_env
            install_deps
            setup_database
            echo -e "${GREEN}=========================================${NC}"
            echo -e "${GREEN}✅ 本地開發環境設定完成！${NC}"
            echo -e "${GREEN}=========================================${NC}"
            echo ""
            echo "執行以下命令啟動開發伺服器:"
            echo -e "${BLUE}  npm run dev${NC}"
            echo ""
            ;;
        2)
            echo ""
            check_env
            install_deps
            setup_database
            build_app
            echo -e "${GREEN}=========================================${NC}"
            echo -e "${GREEN}✅ 建置完成！${NC}"
            echo -e "${GREEN}=========================================${NC}"
            echo ""
            echo "執行以下命令測試生產版本:"
            echo -e "${BLUE}  npm start${NC}"
            echo ""
            ;;
        3)
            echo ""
            deploy_vercel
            echo -e "${GREEN}=========================================${NC}"
            echo -e "${GREEN}✅ 部署完成！${NC}"
            echo -e "${GREEN}=========================================${NC}"
            echo ""
            ;;
        4)
            echo ""
            check_env
            install_deps
            setup_database
            build_app
            deploy_vercel
            echo -e "${GREEN}=========================================${NC}"
            echo -e "${GREEN}✅ 完整部署流程完成！${NC}"
            echo -e "${GREEN}=========================================${NC}"
            echo ""
            echo "下一步:"
            echo "1. 訪問您的 Vercel URL 測試應用"
            echo "2. 部署 Moodle Service 到 Render.com"
            echo "3. 更新 Vercel 環境變數中的 MOODLE_SERVICE_URL"
            echo ""
            ;;
        5)
            echo "退出"
            exit 0
            ;;
        *)
            echo -e "${RED}無效選項${NC}"
            exit 1
            ;;
    esac
}

# 執行主程式
main
