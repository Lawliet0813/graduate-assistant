# 研究生助理系統 - 安裝與使用指南

## 📍 系統概述

這是一個專為研究生設計的智能學習助理，整合以下功能：

- 🎓 **Moodle 自動化**: 自動爬取政大 Moodle 課程資料與下載檔案
- 📝 **語音筆記**: 錄音、轉文字、AI 生成筆記
- 📅 **Google Calendar**: 自動同步作業截止日期
- 📧 **Gmail 整合**: 自動處理作業郵件
- 📚 **Notion 同步**: 將筆記同步到 Notion
- 🤖 **AI 助手**: Claude 和 OpenAI 整合

---

## 💾 資料儲存架構

```
Mac 主機 (內建硬碟)
├── ~/Projects/graduate-assistant/    ← 程式碼
│   ├── src/
│   ├── node_modules/
│   └── package.json

外接硬碟 (/Volumes/TEAM PD20M)
└── graduate-assistant-data/
    ├── postgresql/        ← PostgreSQL 資料庫
    ├── downloads/         ← Moodle 下載的課程檔案
    ├── voice-notes/       ← 錄音檔案
    └── uploads/           ← 上傳的檔案
```

---

## 🚀 安裝步驟

### 步驟 1: 安裝 Homebrew (如果還沒有)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 步驟 2: 安裝 PostgreSQL

```bash
# 安裝 PostgreSQL 16
brew install postgresql@16

# 將 PostgreSQL 加入 PATH
echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 驗證安裝
psql --version
```

### 步驟 3: 安裝 Python (用於 Moodle 爬蟲)

```bash
# 安裝 Python 3.12
brew install python@3.12

# 驗證安裝
python3 --version
pip3 --version
```

### 步驟 4: 安裝 ChromeDriver (用於 Selenium)

```bash
# 安裝 ChromeDriver
brew install chromedriver

# 驗證安裝
chromedriver --version
```

### 步驟 5: 設定 Python 處環境

```bash
# 進入 Moodle 服務目錄
cd ~/Projects/graduate-assistant/services/moodle-service

# 建立處環境
python3 -m venv venv

# 啟用處環境
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 離開處環境
deactivate
```

### 步驟 6: 設定環境變數

編輯 `~/Projects/graduate-assistant/.env` 檔案，填入你的 API Keys：

```bash
# 使用任何文字編輯器打開
open -a "Visual Studio Code" ~/Projects/graduate-assistant/.env
# 或
nano ~/Projects/graduate-assistant/.env
```

**必填項目**：
1. `NEXTAUTH_SECRET` - 生成一個隨機字串：
   ```bash
   openssl rand -base64 32
   ```

2. `GOOGLE_CLIENT_ID` 和 `GOOGLE_CLIENT_SECRET` - 從 Google Cloud Console 取得：
   - 前往: https://console.cloud.google.com
   - 建立專案 → 啟用 API (Calendar, Gmail) → 建立 OAuth 憑證
   - 授權重導向 URI: `http://localhost:3000/api/auth/callback/google`

**選填項目** (可先跳過)：
- `OPENAI_API_KEY` - 語音轉文字功能
- `ANTHROPIC_API_KEY` - Claude AI 助手
- `NOTION_API_KEY` - Notion 同步功能

---

## 🎮 使用說明

### 第一次啟動

```bash
cd ~/Projects/graduate-assistant
./start.sh
```

`start.sh` 會自動：
1. ✅ 檢查外接硬碟是否連接
2. ✅ 初始化 PostgreSQL 資料庫 (如果還沒有)
3. ✅ 啟動 PostgreSQL
4. ✅ 安裝 Node.js 依賴 (如果還沒有)
5. ✅ 同步資料庫結構
6. ✅ 啟動 Next.js 開發伺服器

啟動成功後，打開瀏覽器前往：**http://localhost:3000**

### 其他指令

```bash
# 檢查服務狀態
./status.sh

# 停止所有服務
./stop.sh

# 查看 PostgreSQL 日誌
cat /Volumes/TEAM\ PD20M/graduate-assistant-data/postgresql/logfile

# 進入資料庫 (除錯)
psql graduate_assistant

# 查看 Prisma Studio (資料庫 GUI)
npm run db:studio
```

---

## 🛠️ 常見問題

### Q1: 啟動時提示找不到外接硬碟？

**A**: 確保 TEAM PD20M 硬碟已連接，並且路徑為 `/Volumes/TEAM PD20M`

```bash
ls /Volumes/
```

### Q2: PostgreSQL 無法啟動？

**A**: 檢查是否有其他 PostgreSQL 實例在運行：

```bash
# 查看所有 PostgreSQL 進程
ps aux | grep postgres

# 停止其他實例
brew services stop postgresql@16

# 然後重新啟動
./start.sh
```

### Q3: npm install 失敗？

**A**: 清除快取並重試：

```bash
rm -rf node_modules package-lock.json
npm install
```

### Q4: Google OAuth 登入失敗？

**A**: 檢查：
1. Google Cloud Console 中的授權重導向 URI 設定為 `http://localhost:3000/api/auth/callback/google`
2. `.env` 中的 `GOOGLE_CLIENT_ID` 和 `GOOGLE_CLIENT_SECRET` 正確
3. Calendar API 和 Gmail API 已啟用

### Q5: 語音錄製功能無法使用？

**A**: 確保：
1. 使用 `http://localhost:3000` 而非 `http://127.0.0.1:3000`
2. 瀏覽器有麥克風權限
3. 使用 Chrome 或 Edge 瀏覽器

---

## 📚 功能介紹

### 1. Dashboard (主控台)
- 課程總覽
- 作業截止日提醒
- 學習統計

### 2. Courses (課程管理)
- 查看所有課程
- Moodle 同步
- 課程資料下載

### 3. Assignments (作業管理)
- 作業列表
- 截止日追蹤
- 狀態更新

### 4. Notes (語音筆記)
- 瀏覽器內錄音
- 自動轉文字 (Whisper)
- AI 生成筆記 (Claude)

### 5. Calendar (行事曆)
- 月曆/週曆視圖
- Google Calendar 同步
- 事件管理

### 6. Assistant (AI 助手)
- 智能問答
- 學習建議
- 整理筆記

### 7. Settings (設定)
- 帳號管理
- API 整合
- Voice Watcher 設定

---

## 🔐 安全性建議

1. **不要分享 `.env` 檔案**
2. **定期更新 API Keys**
3. **備份資料庫**
   ```bash
   pg_dump graduate_assistant > backup.sql
   ```
4. **使用強式 `NEXTAUTH_SECRET`**

---

## 📝 技術支持

如果遇到問題：

1. **查看日誌**：
   ```bash
   # PostgreSQL 日誌
   cat /Volumes/TEAM\ PD20M/graduate-assistant-data/postgresql/logfile
   
   # Next.js 日誌
   # 在終端機中直接查看
   ```

2. **檢查服務狀態**：
   ```bash
   ./status.sh
   ```

3. **重新啟動**：
   ```bash
   ./stop.sh
   ./start.sh
   ```

4. **資料庫重置** (只有在必要時)：
   ```bash
   ./stop.sh
   rm -rf /Volumes/TEAM\ PD20M/graduate-assistant-data/postgresql
   ./start.sh
   ```

---

## 🎉 完成!

現在你可以開始使用研究生助理系統了! 🎓

如有任何問題，随時詢問。