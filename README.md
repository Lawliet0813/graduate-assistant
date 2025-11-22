# 🎓 研究生智能助理系統 | Graduate Assistant System

> 專為研究生打造的全方位學習管理平台，整合 Moodle、Google Calendar、Gmail 和 Notion

[![Next.js](https://img.shields.io/badge/Next.js-16.0-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

## 📖 目錄

- [功能特色](#-功能特色)
- [技術架構](#-技術架構)
- [系統需求](#-系統需求)
- [快速開始](#-快速開始)
- [詳細安裝](#-詳細安裝)
- [使用說明](#-使用說明)
- [專案結構](#-專案結構)
- [開發指南](#-開發指南)
- [常見問題](#-常見問題)
- [授權條款](#-授權條款)

## ✨ 功能特色

### 🎓 課程管理
- **Moodle 自動同步**：一鍵同步政大 Moodle 所有課程資料
- **課程內容整理**：自動分類課程章節、講義、資源
- **進度追蹤**：記錄學習活動，追蹤完成進度

### 📝 作業追蹤
- **截止日提醒**：自動抓取作業截止日期
- **狀態管理**：待辦/進行中/已完成
- **Calendar 整合**：同步到 Google Calendar
- **智能提醒**：到期前自動通知

### 🎤 語音筆記
- **即時錄音**：瀏覽器內直接錄音
- **AI 轉文字**：使用 OpenAI Whisper 自動轉錄
- **智能摘要**：Claude AI 生成筆記摘要和重點
- **iCloud 整合**：自動監控 iCloud 資料夾，匯入錄音檔
- **課程識別**：自動判斷錄音屬於哪門課程

### 📅 行事曆整合
- **Google Calendar 雙向同步**：作業、課程、事件自動同步
- **月曆/週曆視圖**：清楚檢視所有行程
- **快速新增**：直接在系統內建立事件

### 📧 郵件處理
- **Gmail 整合**：自動讀取課程相關郵件
- **智能分類**：AI 自動分類郵件類型
- **規則設定**：自訂過濾和處理規則

### 📚 Notion 同步
- **筆記同步**：語音筆記自動同步到 Notion
- **課程頁面**：為每門課程建立專屬頁面
- **結構化整理**：自動建立資料庫和關聯

### 🤖 AI 助手
- **智能問答**：使用 Claude 回答學習相關問題
- **內容總結**：快速摘要長文本
- **學習建議**：根據歷史資料提供個人化建議

### 📊 學習分析
- **時數統計**：追蹤各課程學習時間
- **完成率分析**：作業和進度完成率
- **趨勢圖表**：視覺化學習習慣

## 🛠️ 技術架構

### 前端
- **框架**: Next.js 16 (App Router)
- **語言**: TypeScript 5.x
- **UI 框架**: React 19
- **樣式**: Tailwind CSS v4 + shadcn/ui
- **狀態管理**: Zustand + TanStack Query
- **表單處理**: React Hook Form + Zod

### 後端
- **API**: tRPC v11 (Type-safe API)
- **認證**: NextAuth.js v4 (Google OAuth)
- **資料庫**: PostgreSQL 16
- **ORM**: Prisma v6
- **快取**: React Query

### AI & ML
- **語音轉文字**: OpenAI Whisper API
- **AI 助手**: Anthropic Claude API
- **文本分析**: OpenAI GPT API

### 外部整合
- **Moodle**: Python FastAPI + Selenium
- **Google APIs**: Calendar, Gmail
- **Notion**: Official Notion API

## 💻 系統需求

### 硬體需求
- **記憶體**: 最少 8GB RAM（建議 16GB）
- **儲存空間**: 最少 10GB 可用空間
- **外接硬碟**: 建議使用（用於儲存資料庫和檔案）

### 軟體需求
- **作業系統**: macOS 11.0+ / Windows 10+ / Linux
- **Node.js**: v20.x 或更高版本
- **Python**: 3.12+ (用於 Moodle 爬蟲)
- **PostgreSQL**: 16.x
- **Chrome/Chromium**: 最新版本
- **ChromeDriver**: 與 Chrome 版本相符

### 必要帳號
- **Google Account**: 用於 OAuth 登入和 Calendar/Gmail 整合
- **Moodle 帳號**: 政大 Moodle 學號密碼
- **OpenAI API Key**: (可選) 用於語音轉文字
- **Anthropic API Key**: (可選) 用於 AI 助手
- **Notion API Key**: (可選) 用於 Notion 同步

## 🚀 快速開始

```bash
# 1. Clone repository
git clone https://github.com/Lawliet0813/graduate-assistant.git
cd graduate-assistant

# 2. 安裝依賴
npm install

# 3. 設定環境變數
cp .env.example .env
# 編輯 .env 填入必要的 API Keys

# 4. 初始化資料庫
npm run db:push

# 5. 啟動系統
./start.sh
```

訪問 http://localhost:3000 開始使用！

## 📦 詳細安裝

詳細的安裝步驟請參考 [SETUP_GUIDE.md](SETUP_GUIDE.md)

包含：
- 完整的環境設定說明
- Google OAuth 設定教學
- PostgreSQL 資料庫設定
- Python 虛擬環境配置
- 常見問題排除

## 📚 使用說明

### 1. Moodle 課程同步

1. 進入「課程管理」頁面
2. 點擊「同步 Moodle 課程」按鈕
3. 輸入政大學號和 Moodle 密碼
4. 等待同步完成（約 1-3 分鐘）

### 2. 語音筆記錄製

1. 進入「語音筆記」頁面
2. 點擊「開始錄音」
3. 對著麥克風說話
4. 點擊「停止錄音」
5. 系統自動轉文字並生成摘要

### 3. 作業管理

1. 進入「作業管理」頁面
2. 查看所有待完成作業
3. 更新作業狀態
4. 作業自動同步到 Google Calendar

### 4. AI 助手使用

1. 進入「AI 助手」頁面
2. 輸入問題或需求
3. Claude 會根據你的課程和筆記提供回答

## 📁 專案結構

```
graduate-assistant/
├── prisma/                    # 資料庫 Schema
├── services/
│   └── moodle-service/       # Python Moodle 爬蟲
├── src/
│   ├── app/                  # Next.js App Router
│   │   ├── (auth)/          # 認證相關頁面
│   │   ├── dashboard/       # Dashboard 頁面
│   │   └── api/             # API Routes
│   ├── components/          # React 組件
│   ├── lib/                # 工具函數
│   ├── server/             # 後端邏輯
│   │   ├── api/           # tRPC API
│   │   └── services/      # 業務邏輯服務
│   └── types/             # TypeScript 型別定義
├── start.sh               # 啟動腳本
├── stop.sh                # 停止腳本
├── status.sh              # 狀態檢查腳本
└── package.json
```

## 🔧 開發指南

### 開發環境設定

```bash
# 安裝依賴
npm install

# 啟動開發模式
npm run dev

# 開啟 Prisma Studio
npm run db:studio

# 執行 Linter
npm run lint
```

### 資料庫操作

```bash
# 同步 Schema 到資料庫
npm run db:push

# 建立 migration
npm run db:migrate

# 重新生成 Prisma Client
npm run db:generate
```

## ❓ 常見問題

### Q: Google OAuth 登入失敗？

檢查：
1. Google Cloud Console 授權重導向 URI 設定
2. `.env` 中的 `GOOGLE_CLIENT_ID` 和 `GOOGLE_CLIENT_SECRET`
3. Calendar API 和 Gmail API 是否已啟用

### Q: Moodle 同步失敗？

可能原因：
1. 學號或密碼錯誤
2. ChromeDriver 版本與 Chrome 不符
3. 查看日誌：`tail -f services/moodle-service/moodle-service.log`

### Q: 資料庫連線失敗？

檢查：
1. PostgreSQL 是否正在運行
2. 資料庫是否存在
3. 連線字串是否正確

更多問題請參考 [SETUP_GUIDE.md](SETUP_GUIDE.md)

## 📄 授權條款

本專案採用 MIT License - 詳見 [LICENSE](LICENSE) 檔案

## 🙏 致謝

- [Next.js](https://nextjs.org/) - React 框架
- [Prisma](https://www.prisma.io/) - ORM
- [tRPC](https://trpc.io/) - Type-safe API
- [shadcn/ui](https://ui.shadcn.com/) - UI 組件
- [OpenAI](https://openai.com/) - Whisper API
- [Anthropic](https://www.anthropic.com/) - Claude API

## 📧 聯絡方式

**作者**: Lawliet  
**Email**: ym90039@gmail.com  
**GitHub**: [@Lawliet0813](https://github.com/Lawliet0813)

---

⭐ 如果這個專案對你有幫助，請給個 Star！

**Built with ❤️ for Graduate Students**
