#!/usr/bin/env python3
"""
測試 Moodle 登入功能
"""
import sys
import os
from pathlib import Path

# 添加 services/moodle-service 到路徑
sys.path.insert(0, str(Path(__file__).parent / "services" / "moodle-service"))

from scraper.moodle_scraper import MoodleScraper
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def test_login():
    """測試登入功能"""
    # 從環境變數或用戶輸入獲取憑證
    base_url = os.getenv("MOODLE_BASE_URL") or input("請輸入 Moodle URL (例: https://moodle45.nccu.edu.tw): ")
    username = os.getenv("MOODLE_USERNAME") or input("請輸入學號: ")
    password = os.getenv("MOODLE_PASSWORD") or input("請輸入密碼: ")
    
    print("\n" + "=" * 60)
    print("開始測試 Moodle 登入")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print(f"Username: {username}")
    print(f"使用非無頭模式（可以看到瀏覽器操作）")
    print("=" * 60 + "\n")
    
    try:
        # 使用非無頭模式方便觀察
        with MoodleScraper(base_url, username, password, headless=False) as scraper:
            if scraper.login():
                print("\n✓ 登入測試成功！")
                
                # 嘗試獲取課程列表
                print("\n嘗試獲取課程列表...")
                courses = scraper.get_courses()
                print(f"✓ 找到 {len(courses)} 門課程")
                
                for i, course in enumerate(courses[:5], 1):  # 顯示前 5 門課程
                    print(f"  {i}. {course['name']}")
                
                if len(courses) > 5:
                    print(f"  ... 還有 {len(courses) - 5} 門課程")
                
                return True
            else:
                print("\n✗ 登入測試失敗")
                print("\n請檢查：")
                print("1. 帳號密碼是否正確")
                print("2. Moodle URL 是否正確")
                print("3. 截圖檔案: /tmp/moodle_login_error.png")
                print("4. 頁面原始碼: /tmp/moodle_page_source.html")
                return False
                
    except KeyboardInterrupt:
        print("\n\n測試被使用者中斷")
        return False
    except Exception as e:
        print(f"\n✗ 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_login()
    sys.exit(0 if success else 1)
