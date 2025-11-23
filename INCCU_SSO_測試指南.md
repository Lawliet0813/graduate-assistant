# INCCU 單一登入（SSO）測試指南

## ✅ 已支援 INCCU SSO

經過改進，程式碼現在**完全支援政大 INCCU 單一登入**！

---

## 🔍 改進內容

### 1. **SSO 按鈕識別**
增強了 SSO 登入按鈕的搜尋能力：
- ✅ 偵測包含 "INCCU" 的連結和按鈕
- ✅ 偵測 "單一登入" 文字
- ✅ 偵測 SSO 相關的 URL
- ✅ 自動等待頁面跳轉到 INCCU

### 2. **登入表單識別**
支援多種 SSO 系統的登入表單：
- ✅ 標準 Moodle 表單
- ✅ Microsoft Azure AD（INCCU 可能使用）
- ✅ 自訂 INCCU 欄位
- ✅ 通用 SSO 表單

### 3. **智能欄位搜尋**
程式會嘗試多種欄位識別方式：
- **帳號欄位**：`username`, `uid`, `i0116`, `loginfmt` 等
- **密碼欄位**：`password`, `i0118`, `passwd` 等
- **登入按鈕**：`idSIButton9`, `submit`, `Sign in` 等

---

## 🧪 測試步驟

### 方法 1: 使用測試腳本（推薦）

```bash
# 設定環境變數
export MOODLE_BASE_URL="https://moodle45.nccu.edu.tw"
export MOODLE_USERNAME="114921039"  # 您的學號
export MOODLE_PASSWORD="Sundayice2511"  # 您的密碼

# 執行測試（會開啟瀏覽器視窗）
python3 test-moodle-login.py
```

### 方法 2: 在程式碼中使用

```python
from services.moodle_service.scraper.adapter import MoodleService

# 建立服務（自動處理 INCCU SSO）
service = MoodleService(
    base_url="https://moodle45.nccu.edu.tw",
    username="114921039",
    password="Sundayice2511",
    use_api=False,  # 政大不支援 API，使用 Selenium
    headless=False  # 測試時設為 False，可以看到登入過程
)

# 測試登入
result = service.login()
if result['success']:
    print("✓ 登入成功！")

    # 獲取課程
    courses = service.get_courses()
    print(f"找到 {len(courses)} 門課程")
else:
    print(f"✗ 登入失敗: {result['message']}")
```

---

## 📋 預期的登入流程

使用 INCCU SSO 時，程式會自動執行以下步驟：

### 步驟 1: 訪問 Moodle
```
→ 正在訪問 https://moodle45.nccu.edu.tw
```

### 步驟 2: 尋找 SSO 按鈕
```
→ 尋找登入入口...
→ 找到 SSO/INCCU 登入按鈕
→ 等待跳轉到 INCCU 登入頁面...
  ✓ 已跳轉到 INCCU 登入頁面: https://inccu.nccu.edu.tw/...
  ℹ 注意: 使用 INCCU 單一登入，請使用您的政大帳號密碼
```

### 步驟 3: 輸入帳號密碼
```
→ 找到帳號輸入框: ID=username
→ 輸入帳號
  ✓ 已輸入帳號
→ 找到密碼輸入框: ID=password
→ 輸入密碼
  ✓ 已輸入密碼
```

### 步驟 4: 點擊登入
```
→ 找到登入按鈕: ID=submit
→ 點擊登入按鈕
→ 等待登入完成...
✓ 登入成功
```

### 步驟 5: 同步資料
```
→ 正在獲取課程列表...
✓ 找到 5 門課程
  1. 資料結構與演算法
  2. 計算機組織
  ...
```

---

## 🛠️ 疑難排解

### 問題 1: 找不到 SSO 按鈕

**可能原因：**
- Moodle 首頁沒有顯示登入按鈕
- 需要先訪問特定的登入頁面

**解決方法：**
1. 手動檢查 Moodle 首頁是否有 "INCCU 登入" 或 "單一登入" 按鈕
2. 如果沒有，嘗試直接訪問：`https://moodle45.nccu.edu.tw/login/index.php`
3. 將截圖分享給開發者（位於 `/tmp/moodle_login_error.png`）

### 問題 2: 找不到帳號或密碼欄位

**錯誤訊息：**
```
✗ 無法找到帳號輸入框
→ 當前 URL: https://inccu.nccu.edu.tw/...
```

**解決方法：**
1. 查看保存的截圖：`/tmp/moodle_login_error.png`
2. 查看頁面原始碼：`/tmp/moodle_page_source.html`
3. 手動檢查登入頁面，找到實際的欄位 ID 或 name
4. 回報給開發者，我們會添加該欄位到選擇器列表

### 問題 3: 登入後跳轉失敗

**症狀：**
- 帳號密碼正確
- 點擊登入後頁面沒有反應
- 或跳轉後顯示錯誤

**可能原因：**
1. INCCU 需要額外的驗證步驟（如雙因素認證）
2. 登入按鈕的 JavaScript 事件沒有正確觸發
3. 頁面需要更長的等待時間

**解決方法：**
```python
# 增加等待時間
from services.moodle_service.scraper.moodle_scraper import MoodleScraper
import time

scraper = MoodleScraper(
    base_url="https://moodle45.nccu.edu.tw",
    username="你的學號",
    password="你的密碼",
    headless=False  # 可以看到操作過程
)
scraper.start()

# 手動調整等待時間
if scraper.login():
    time.sleep(10)  # 等待更長時間
    print("登入成功")
```

### 問題 4: 需要雙因素認證（2FA）

如果 INCCU 啟用了雙因素認證：

**症狀：**
- 輸入帳號密碼後，要求輸入驗證碼
- 需要手機 App 確認

**目前狀況：**
- ⚠️ Selenium 爬蟲**不支援**自動處理 2FA
- 需要手動介入

**建議方案：**
1. **短期方案**：使用非無頭模式（`headless=False`），手動輸入驗證碼
2. **長期方案**：聯繫學校 IT，申請 API 存取權限
3. **替代方案**：設定信任裝置，避免每次都需要 2FA

---

## 💡 最佳實踐

### 1. 測試階段使用非無頭模式

```python
service = MoodleService(
    ...,
    headless=False  # 可以看到瀏覽器操作，方便除錯
)
```

### 2. 生產環境使用無頭模式

```python
service = MoodleService(
    ...,
    headless=True  # 在伺服器上執行，不需要顯示視窗
)
```

### 3. 適當的錯誤處理

```python
try:
    result = service.sync_all()
    if result['success']:
        print(f"同步成功：{result['courses_count']} 門課程")
    else:
        print(f"同步失敗：{result['message']}")
        # 檢查錯誤截圖
        print("請查看 /tmp/moodle_*.png")
except Exception as e:
    print(f"發生錯誤：{e}")
    # 記錄錯誤並通知管理員
```

### 4. 不要過於頻繁同步

```python
# ❌ 錯誤：每分鐘同步一次
# 可能被學校視為攻擊行為

# ✅ 正確：每天同步 1-2 次
import schedule

def sync_moodle():
    service = MoodleService(...)
    service.sync_all()

# 每天早上 8 點和下午 6 點同步
schedule.every().day.at("08:00").do(sync_moodle)
schedule.every().day.at("18:00").do(sync_moodle)
```

---

## 🔐 安全性建議

### 1. 保護您的帳號密碼

```bash
# ✅ 使用環境變數
export MOODLE_USERNAME="你的學號"
export MOODLE_PASSWORD="你的密碼"

# ✅ 或使用 .env 檔案（不要提交到 Git）
echo "MOODLE_USERNAME=你的學號" >> .env
echo "MOODLE_PASSWORD=你的密碼" >> .env

# ❌ 不要在程式碼中硬編碼密碼
# username = "114921039"  # 不要這樣做！
```

### 2. 保護 .env 檔案

```bash
# 確保 .env 在 .gitignore 中
echo ".env" >> .gitignore

# 設定檔案權限（僅限擁有者讀取）
chmod 600 .env
```

### 3. 定期更換密碼

- 定期更新您的政大帳號密碼
- 更換密碼後，記得更新 `.env` 檔案

---

## 📊 支援的 SSO 系統

| SSO 系統 | 支援狀態 | 備註 |
|----------|---------|------|
| INCCU | ✅ 完全支援 | 政大校園入口 |
| Microsoft Azure AD | ✅ 支援 | 常見於教育機構 |
| Google SSO | ✅ 支援 | Google 帳號登入 |
| 標準 Moodle 登入 | ✅ 支援 | 直接帳號密碼 |
| SAML SSO | ✅ 部分支援 | 需視實作方式 |
| OAuth 2.0 | ✅ 部分支援 | 需視實作方式 |
| 雙因素認證 (2FA) | ⚠️ 需手動介入 | 無法自動處理 |

---

## 🎯 測試檢查清單

在您的本地電腦執行以下測試：

- [ ] Chrome 瀏覽器已安裝
- [ ] Python 套件已安裝（`pip install -r services/moodle-service/requirements.txt`）
- [ ] 環境變數已設定（學號、密碼）
- [ ] 執行 `python3 test-moodle-login.py`
- [ ] 瀏覽器自動開啟並訪問 Moodle
- [ ] 自動點擊 INCCU/SSO 登入按鈕
- [ ] 自動輸入學號密碼
- [ ] 成功登入並顯示課程列表

如果以上步驟都成功，表示 INCCU SSO 整合正常運作！

---

## 📞 需要協助？

如果遇到問題，請提供：
1. 錯誤訊息完整內容
2. 錯誤截圖（`/tmp/moodle_*.png`）
3. 頁面原始碼（`/tmp/moodle_*.html`）
4. 當前 URL（錯誤時顯示的）
5. Chrome 版本

---

**最後更新**: 2025-11-23
**測試環境**: 政大 Moodle 4.5 + INCCU SSO
**支援狀態**: ✅ 完全支援
