# Moodle Web Services API 整合指南

## 📌 概述

本專案現在支援兩種 Moodle 整合方式：

1. **Moodle Web Services API**（推薦）⭐
   - ✅ 穩定可靠
   - ✅ 速度快（幾秒完成）
   - ✅ 資源消耗低
   - ✅ 官方標準 API
   - ❌ 需要學校啟用 Web Services

2. **Selenium 網頁爬蟲**（備用）
   - ✅ 不需要特殊權限
   - ✅ 可抓取任何網頁資料
   - ❌ 不穩定（網頁改版會失效）
   - ❌ 速度慢（1-3 分鐘）
   - ❌ 資源消耗高

---

## 🚀 快速開始

### 方法 1: 使用 API Token（最快）

如果您已經有 Moodle API Token：

```bash
# 在 .env 中設定
MOODLE_BASE_URL=https://moodle45.nccu.edu.tw
MOODLE_TOKEN=your_api_token_here
```

### 方法 2: 使用帳號密碼（自動獲取 Token）

```bash
# 在 .env 中設定
MOODLE_BASE_URL=https://moodle45.nccu.edu.tw
MOODLE_USERNAME=your_student_id
MOODLE_PASSWORD=your_password
```

系統會自動使用帳號密碼獲取 Token。

---

## 📖 如何取得 Moodle API Token

### 選項 1: 從 Moodle 網站取得（需要學校支援）

1. 登入學校 Moodle
2. 點擊右上角個人頭像 → **偏好設定**
3. 找到 **安全性金鑰** 或 **Security keys**
4. 建立新的 Token（服務選擇 `moodle_mobile_app`）
5. 複製 Token 並儲存到 `.env`

### 選項 2: 自動獲取（使用帳號密碼）

系統會自動呼叫 Moodle 的 Token API：

```python
# 自動執行
GET /login/token.php?username=xxx&password=xxx&service=moodle_mobile_app
```

### 選項 3: 手動測試 Token API

```bash
# 測試是否可以獲取 token
curl "https://moodle45.nccu.edu.tw/login/token.php?username=你的學號&password=你的密碼&service=moodle_mobile_app"
```

如果返回 JSON 包含 `token` 欄位，表示成功：

```json
{
  "token": "abc123def456...",
  "privatetoken": "..."
}
```

如果返回錯誤訊息，可能的原因：
- 學校未啟用 Web Services
- 帳號密碼錯誤
- 服務名稱不正確

---

## 🧪 測試 API 整合

### 執行測試腳本

```bash
# 測試 API 整合
python3 test-moodle-api.py
```

這個測試腳本會：
1. 測試連線
2. 獲取課程列表
3. 獲取課程內容
4. 獲取作業列表
5. 執行完整同步

### 測試範例輸出

```
=============================================================
Moodle Web Services API 整合測試
=============================================================

測試 1: 直接使用 Moodle API 客戶端
=============================================================
→ 測試連線...
✓ 連線成功！
  網站名稱: 政治大學 Moodle
  使用者: 王小明 (112345678)
  Moodle 版本: 4.5

→ 獲取課程列表...
✓ 找到 5 門課程

  1. [123] 資料結構與演算法
  2. [124] 計算機組織
  3. [125] 作業系統
  ...

→ 獲取作業列表...
✓ 找到 12 個作業

  1. 作業一：資料結構實作 (截止: 2025-12-01)
     課程: 資料結構與演算法
  ...
```

---

## 💻 程式碼使用範例

### 範例 1: 直接使用 API 客戶端

```python
from scraper.moodle_api_client import MoodleAPIClient

# 建立客戶端
client = MoodleAPIClient(
    base_url="https://moodle45.nccu.edu.tw",
    username="your_student_id",
    password="your_password"
)

# 測試連線
if client.test_connection():
    # 獲取課程
    courses = client.get_user_courses()
    print(f"找到 {len(courses)} 門課程")

    # 獲取作業
    assignments = client.get_assignments()
    print(f"找到 {len(assignments)} 個作業")
```

### 範例 2: 使用 MoodleService（推薦）

```python
from scraper.adapter import MoodleService

# 使用 API 模式
service = MoodleService(
    base_url="https://moodle45.nccu.edu.tw",
    username="your_student_id",
    password="your_password",
    use_api=True  # 使用 API（預設）
)

# 獲取所有資料
result = service.sync_all()
if result['success']:
    print(f"成功同步 {result['courses_count']} 門課程")
    print(f"成功同步 {result['assignments_count']} 個作業")
```

### 範例 3: 切換回 Selenium 模式

```python
# 如果 API 不可用，可以切換回 Selenium
service = MoodleService(
    base_url="https://moodle45.nccu.edu.tw",
    username="your_student_id",
    password="your_password",
    use_api=False,  # 使用 Selenium
    headless=True   # 無頭模式
)
```

---

## 🔧 FastAPI 服務整合

FastAPI 服務會自動使用 API 模式，如需切換可以修改環境變數：

```bash
# .env
MOODLE_USE_API=true  # 使用 API（預設）
# MOODLE_USE_API=false  # 使用 Selenium
```

---

## 📋 支援的 API 功能

### 課程相關
- ✅ 獲取使用者的所有課程
- ✅ 獲取課程詳細資訊
- ✅ 獲取課程內容（章節、活動、資源）
- ✅ 獲取課程檔案

### 作業相關
- ✅ 獲取所有作業
- ✅ 獲取作業截止日期
- ✅ 過濾特定課程的作業

### 行事曆相關
- ✅ 獲取即將到來的事件
- ✅ 獲取作業截止日提醒

### 使用者資訊
- ✅ 獲取使用者個人資訊
- ✅ 測試連線狀態

---

## 🔍 疑難排解

### 問題 1: 無法取得 Token

**錯誤訊息：**
```json
{
  "error": "Web service is not available",
  "errorcode": "servicenotavailable"
}
```

**解決方案：**
1. 學校可能未啟用 Web Services
2. 聯繫學校 IT 管理員確認
3. 改用 Selenium 模式：`use_api=False`

### 問題 2: Token 已過期

**錯誤訊息：**
```json
{
  "exception": "moodle_exception",
  "message": "Invalid token"
}
```

**解決方案：**
1. 刪除舊的 `MOODLE_TOKEN`
2. 讓系統重新獲取 token
3. 或從 Moodle 網站重新產生新的 token

### 問題 3: 權限不足

**錯誤訊息：**
```json
{
  "exception": "webservice_access_exception",
  "message": "Access control exception"
}
```

**解決方案：**
1. 確認帳號有存取課程的權限
2. 確認使用的 service 名稱正確
3. 嘗試使用 `moodle_mobile_app` 服務

### 問題 4: API 太慢

如果 API 回應很慢：

1. 檢查網路連線
2. 減少同時請求的數量
3. 使用 Token 而非每次都用帳號密碼

---

## 📚 更多資訊

### Moodle Web Services API 文檔
- [官方文檔](https://docs.moodle.org/dev/Web_services)
- [API 函數列表](https://docs.moodle.org/dev/Web_service_API_functions)

### 常用 API 函數
- `core_webservice_get_site_info` - 取得網站資訊
- `core_enrol_get_users_courses` - 取得使用者課程
- `core_course_get_contents` - 取得課程內容
- `mod_assign_get_assignments` - 取得作業
- `core_calendar_get_calendar_upcoming_view` - 取得行事曆

---

## 🎯 最佳實踐

1. **優先使用 Token**
   - 儲存 token 到 `.env`
   - 避免每次都用帳號密碼獲取

2. **錯誤處理**
   - 始終檢查 API 回應
   - 準備 Selenium 作為備用方案

3. **效能優化**
   - 批次獲取資料
   - 快取常用資料
   - 避免重複請求

4. **安全性**
   - 不要在程式碼中硬編碼密碼
   - 使用環境變數儲存敏感資訊
   - Token 視同密碼，妥善保管

---

## ✨ 總結

使用 Moodle Web Services API 的優點：

| 特性 | API | Selenium |
|------|-----|----------|
| 速度 | ⚡ 幾秒 | 🐌 1-3 分鐘 |
| 穩定性 | ✅ 非常穩定 | ⚠️ 容易失效 |
| 資源消耗 | 💚 低 | 💛 高 |
| 維護成本 | 💚 低 | 💛 高 |
| 功能完整性 | ✅ 完整 | ⚠️ 部分 |

**建議：優先使用 API，無法使用時再切換到 Selenium。**

---

## 📞 問題回報

如果遇到問題，請提供以下資訊：

1. 錯誤訊息完整內容
2. Moodle 版本
3. 使用的 service 名稱
4. 是否可以手動獲取 token

問題回報：[GitHub Issues](https://github.com/Lawliet0813/graduate-assistant/issues)
