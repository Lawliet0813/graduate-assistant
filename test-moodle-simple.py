#!/usr/bin/env python3
"""
簡單測試 Moodle 連線
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_moodle_connection():
    """測試基本連線"""
    base_url = os.getenv("MOODLE_BASE_URL", "https://moodle45.nccu.edu.tw")
    username = os.getenv("MOODLE_USERNAME")
    password = os.getenv("MOODLE_PASSWORD")

    print("=" * 60)
    print("測試 Moodle 連線")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print(f"Username: {username}")
    print()

    # 測試 1: 檢查網站是否可訪問
    print("1. 檢查 Moodle 網站是否可訪問...")
    try:
        response = requests.get(base_url, timeout=10)
        print(f"   ✓ 網站可訪問 (狀態碼: {response.status_code})")
    except Exception as e:
        print(f"   ✗ 網站無法訪問: {e}")
        return False

    # 測試 2: 嘗試獲取 API Token (預設服務)
    print("\n2. 嘗試使用 moodle_mobile_app 服務獲取 Token...")
    try:
        token_url = f"{base_url}/login/token.php"
        params = {
            'username': username,
            'password': password,
            'service': 'moodle_mobile_app'
        }
        response = requests.get(token_url, params=params, timeout=10)
        print(f"   狀態碼: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if 'token' in data:
                print(f"   ✓ Token 獲取成功！")
                print(f"   Token: {data['token'][:20]}...")
                return True
            elif 'error' in data:
                print(f"   ✗ 錯誤: {data.get('error')}")
                if 'errorcode' in data:
                    print(f"   錯誤代碼: {data['errorcode']}")
                if 'debuginfo' in data:
                    print(f"   除錯資訊: {data['debuginfo']}")
        elif response.status_code == 403:
            print(f"   ✗ 403 Forbidden - 學校未啟用 Web Services API")
        else:
            print(f"   ✗ 請求失敗")
            print(f"   回應: {response.text[:200]}")
    except Exception as e:
        print(f"   ✗ 請求失敗: {e}")

    # 測試 3: 嘗試其他常見的服務名稱
    print("\n3. 嘗試其他服務名稱...")
    services = [
        'moodle_mobile',
        'external_api',
        'webservice'
    ]

    for service in services:
        try:
            params = {
                'username': username,
                'password': password,
                'service': service
            }
            response = requests.get(token_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    print(f"   ✓ 使用 '{service}' 服務成功！")
                    print(f"   Token: {data['token'][:20]}...")
                    return True
        except:
            pass

    print(f"   ✗ 所有服務都無法使用")

    # 測試 4: 檢查登入頁面
    print("\n4. 檢查登入頁面...")
    try:
        login_url = f"{base_url}/login/index.php"
        response = requests.get(login_url, timeout=10)
        if response.status_code == 200:
            print(f"   ✓ 登入頁面可訪問")
            if 'SSO' in response.text or 'sso' in response.text.lower():
                print(f"   ℹ 偵測到 SSO 單一登入")
            if 'loginform' in response.text:
                print(f"   ℹ 偵測到標準登入表單")
        else:
            print(f"   ⚠ 登入頁面狀態異常: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 無法訪問登入頁面: {e}")

    print("\n" + "=" * 60)
    print("結論:")
    print("=" * 60)
    print("政大 Moodle 未啟用 Web Services API")
    print("建議使用 Selenium 網頁爬蟲方式")
    print()
    print("如需測試 Selenium，請在您的本地電腦執行：")
    print("  python3 test-moodle-login.py")
    print()
    print("或在程式碼中使用：")
    print("  service = MoodleService(..., use_api=False)")
    print("=" * 60)

    return False

if __name__ == "__main__":
    test_moodle_connection()
