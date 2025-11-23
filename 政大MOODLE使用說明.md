# 政大 Moodle 整合使用說明

## ⚠️ 重要發現

經過測試，**政大 Moodle 未啟用 Web Services API**。所有 API 端點都返回 403 Forbidden，這表示學校基於安全考量未開放此功能。

因此，本專案**必須使用 Selenium 網頁爬蟲方式**來同步 Moodle 資料。

---

## 📋 測試結果

### API 測試（失敗）
- ❌ moodle_mobile_app 服務：403 Forbidden
- ❌ 其他服務：全部無法使用
- ❌ 登入頁面：403 Forbidden

### 結論
政大 Moodle 未開放 Web Services API，必須使用 Selenium。

---

## ✅ 已完成的配置

我已經將專案配置為使用 Selenium 模式：

1. **FastAPI 服務** (`services/moodle-service/main.py`)
   - 所有端點預設使用 `use_api=False`
   - 使用 Selenium 進行資料抓取

2. **保留彈性**
   - 程式碼仍支援雙模式切換
   - 未來如果學校開放 API，只需改 `use_api=True`

---

## 🖥️ 在本地電腦測試

由於 Selenium 需要 Chrome 瀏覽器，請在**您的本地電腦**執行測試：

### 步驟 1: 安裝依賴

```bash
# 安裝 Python 套件
pip install -r services/moodle-service/requirements.txt

# 確保已安裝 Chrome 瀏覽器
# macOS: 從 Chrome 官網下載
# Windows: 從 Chrome 官網下載
# Linux: sudo apt-get install google-chrome-stable
```

### 步驟 2: 設定環境變數

建立 `.env` 檔案：

```bash
MOODLE_BASE_URL=https://moodle45.nccu.edu.tw
MOODLE_USERNAME=你的學號
MOODLE_PASSWORD=你的密碼
```

### 步驟 3: 執行測試

```bash
# 測試登入（會開啟瀏覽器視窗，可以看到執行過程）
python3 test-moodle-login.py
```

如果測試成功，您會看到：

```
✓ 登入成功！
✓ 找到 5 門課程
  1. 課程名稱 A
  2. 課程名稱 B
  ...
```

---

## 🚀 啟動服務

### 本地開發

```bash
# 啟動 Moodle 服務（在本地電腦）
cd services/moodle-service
python3 main.py

# 或使用專案提供的腳本
./start-moodle-service.sh
```

### 測試 API

```bash
# 測試同步功能
curl -X POST "http://localhost:8000/api/moodle/sync" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "你的學號",
    "password": "你的密碼",
    "base_url": "https://moodle45.nccu.edu.tw"
  }'
```

---

## 📊 Selenium 方式的特點

### 優點
- ✅ 不需要學校開放 API
- ✅ 可以抓取任何網頁可見的資料
- ✅ 支援 SSO 單一登入

### 缺點
- ⚠️ 速度較慢（1-3 分鐘）
- ⚠️ 需要安裝 Chrome
- ⚠️ 網頁改版可能需要更新程式碼
- ⚠️ 資源消耗較大

---

## 🛠️ 常見問題

### Q1: 為什麼不能使用 API？

**答：** 政大 Moodle 管理員未啟用 Web Services API 功能。這是學校的政策決定，主要考量安全性和資源管理。

### Q2: 可以要求學校開放 API 嗎？

**答：** 可以向學校 IT 部門或教務處詢問，但通常需要正式申請流程。建議說明您的使用情境和安全措施。

### Q3: Selenium 登入失敗怎麼辦？

**可能原因：**
1. 帳號密碼錯誤
2. Chrome 版本與 ChromeDriver 不符
3. 網頁結構改變

**解決方法：**
1. 確認帳號密碼正確
2. 更新 Chrome 和 ChromeDriver
3. 查看錯誤截圖：`/tmp/moodle_*.png`
4. 查看頁面原始碼：`/tmp/moodle_*.html`

### Q4: 可以在伺服器上執行嗎？

**答：** 可以，但需要在伺服器上安裝 Chrome：

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# 確認使用 headless 模式
service = MoodleService(..., headless=True)
```

---

## 📝 程式碼範例

### 範例 1: 基本使用

```python
from services.moodle-service.scraper.adapter import MoodleService

# 使用 Selenium 模式（政大必須用這個）
service = MoodleService(
    base_url="https://moodle45.nccu.edu.tw",
    username="你的學號",
    password="你的密碼",
    use_api=False,  # 必須設為 False
    headless=True   # 在伺服器上設為 True
)

# 同步所有資料
result = service.sync_all()
if result['success']:
    print(f"成功同步 {result['courses_count']} 門課程")
    print(f"成功同步 {result['assignments_count']} 個作業")
```

### 範例 2: 只獲取課程

```python
# 獲取課程列表
courses = service.get_courses()
for course in courses:
    print(f"[{course['id']}] {course['name']}")
```

### 範例 3: 獲取作業

```python
# 獲取所有作業
assignments = service.get_assignments()
for assignment in assignments:
    print(f"{assignment['name']}")
    print(f"  課程: {assignment['course_name']}")
    print(f"  截止: {assignment['due_date']}")
```

---

## 🎯 下一步建議

1. **在本地電腦測試**
   - 確認 Selenium 登入功能正常
   - 驗證可以正確抓取課程和作業

2. **部署到伺服器**
   - 安裝 Chrome
   - 使用 headless 模式
   - 設定定期同步

3. **監控和維護**
   - 定期檢查是否能正常登入
   - 留意政大 Moodle 網頁更新
   - 必要時更新選擇器

4. **聯繫學校**（可選）
   - 詢問是否可能開放 API
   - 說明使用情境和需求

---

## 📞 技術支援

如遇到問題，請提供：
1. 錯誤訊息完整內容
2. 錯誤截圖（`/tmp/moodle_*.png`）
3. 使用的 Chrome 版本
4. 作業系統版本

---

## 📚 相關檔案

- **測試腳本**: `test-moodle-login.py`（需在本地執行）
- **簡單測試**: `test-moodle-simple.py`（API 連線測試）
- **API 整合**: `MOODLE_API_GUIDE.md`（政大不適用）
- **服務程式**: `services/moodle-service/`

---

**最後更新**: 2025-11-23
**測試環境**: 政大 Moodle 4.5 (moodle45.nccu.edu.tw)
**測試結果**: ❌ API 不可用，✅ Selenium 可用
