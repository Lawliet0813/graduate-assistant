#!/usr/bin/env python3
"""
測試 Moodle Web Services API 整合
"""
import sys
import os
from pathlib import Path
import logging

# 添加 services/moodle-service 到路徑
sys.path.insert(0, str(Path(__file__).parent / "services" / "moodle-service"))

from scraper.moodle_api_client import MoodleAPIClient
from scraper.adapter import MoodleService
from dotenv import load_dotenv

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 載入環境變數
load_dotenv()


def test_api_client():
    """測試直接使用 API 客戶端"""
    print("\n" + "=" * 60)
    print("測試 1: 直接使用 Moodle API 客戶端")
    print("=" * 60)

    # 從環境變數或用戶輸入獲取憑證
    base_url = os.getenv("MOODLE_BASE_URL") or input("請輸入 Moodle URL (例: https://moodle45.nccu.edu.tw): ")
    username = os.getenv("MOODLE_USERNAME") or input("請輸入學號: ")
    password = os.getenv("MOODLE_PASSWORD") or input("請輸入密碼: ")
    token = os.getenv("MOODLE_TOKEN")  # 可選，如果已有 token

    print(f"\nBase URL: {base_url}")
    print(f"Username: {username}")
    print(f"Token: {'已提供' if token else '需要獲取'}")
    print()

    try:
        # 建立 API 客戶端
        client = MoodleAPIClient(
            base_url=base_url,
            username=username,
            password=password,
            token=token
        )

        # 測試連線
        print("→ 測試連線...")
        if client.test_connection():
            print("✓ 連線測試成功！\n")

            # 獲取課程列表
            print("→ 獲取課程列表...")
            courses = client.get_user_courses()
            print(f"✓ 找到 {len(courses)} 門課程\n")

            for i, course in enumerate(courses[:5], 1):
                print(f"  {i}. [{course['id']}] {course['name']}")

            if len(courses) > 5:
                print(f"  ... 還有 {len(courses) - 5} 門課程\n")

            # 測試獲取第一門課程的內容
            if courses:
                first_course = courses[0]
                print(f"\n→ 獲取課程內容: {first_course['name']}")
                contents = client.get_course_contents(int(first_course['id']))
                print(f"✓ 找到 {len(contents)} 個章節\n")

                for i, section in enumerate(contents[:3], 1):
                    print(f"  章節 {i}: {section['name']}")
                    print(f"    - {len(section['activities'])} 個活動")

            # 獲取作業列表
            print("\n→ 獲取作業列表...")
            assignments = client.get_assignments()
            print(f"✓ 找到 {len(assignments)} 個作業\n")

            for i, assignment in enumerate(assignments[:5], 1):
                due_date = assignment.get('duedate')
                due_str = f" (截止: {due_date})" if due_date else ""
                print(f"  {i}. {assignment['name']}{due_str}")
                print(f"     課程: {assignment['course_name']}")

            if len(assignments) > 5:
                print(f"  ... 還有 {len(assignments) - 5} 個作業\n")

            return True
        else:
            print("✗ 連線測試失敗")
            return False

    except Exception as e:
        print(f"\n✗ 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_moodle_service():
    """測試透過 MoodleService 使用 API"""
    print("\n" + "=" * 60)
    print("測試 2: 透過 MoodleService 使用 API")
    print("=" * 60)

    base_url = os.getenv("MOODLE_BASE_URL")
    username = os.getenv("MOODLE_USERNAME")
    password = os.getenv("MOODLE_PASSWORD")
    token = os.getenv("MOODLE_TOKEN")

    if not all([base_url, username, password]):
        print("⚠ 請先設定環境變數 MOODLE_BASE_URL, MOODLE_USERNAME, MOODLE_PASSWORD")
        return False

    try:
        # 使用 API 模式
        service = MoodleService(
            base_url=base_url,
            username=username,
            password=password,
            token=token,
            use_api=True  # 使用 API 而非 Selenium
        )

        # 測試登入
        print("\n→ 測試 API 連線...")
        result = service.login()
        if result['success']:
            print(f"✓ {result['message']}")

            # 獲取課程
            print("\n→ 獲取課程...")
            courses = service.get_courses()
            print(f"✓ 找到 {len(courses)} 門課程")

            # 獲取作業
            print("\n→ 獲取作業...")
            assignments = service.get_assignments()
            print(f"✓ 找到 {len(assignments)} 個作業")

            # 完整同步
            print("\n→ 執行完整同步...")
            sync_result = service.sync_all()
            if sync_result['success']:
                print(f"✓ {sync_result['message']}")
                print(f"  - 課程數: {sync_result['courses_count']}")
                print(f"  - 作業數: {sync_result['assignments_count']}")
                return True
            else:
                print(f"✗ 同步失敗: {sync_result['message']}")
                return False
        else:
            print(f"✗ 連線失敗: {result['message']}")
            return False

    except Exception as e:
        print(f"\n✗ 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主測試函數"""
    print("\n" + "=" * 60)
    print("Moodle Web Services API 整合測試")
    print("=" * 60)

    print("\n📝 測試說明:")
    print("1. 此測試會使用 Moodle Web Services API")
    print("2. 需要您的學號、密碼（或已有的 API Token）")
    print("3. 比 Selenium 更快、更穩定")
    print("\n⚠ 注意事項:")
    print("1. 如果學校 Moodle 未啟用 Web Services，可能會失敗")
    print("2. 預設使用 'moodle_mobile_app' 服務")
    print("3. 失敗時請檢查錯誤訊息，可能需要聯繫學校管理員")

    # 詢問是否繼續
    choice = input("\n是否開始測試？(y/n): ").lower()
    if choice != 'y':
        print("測試已取消")
        return 0

    # 執行測試
    success = True

    # 測試 1: 直接使用 API 客戶端
    if not test_api_client():
        success = False

    # 測試 2: 透過 MoodleService
    if not test_moodle_service():
        success = False

    # 總結
    print("\n" + "=" * 60)
    if success:
        print("✓ 所有測試通過！")
        print("\n下一步:")
        print("1. 可以在 .env 中設定 MOODLE_TOKEN 以加快速度")
        print("2. FastAPI 服務會自動使用新的 API 整合")
        print("3. 舊的 Selenium 方法仍然保留作為備用")
    else:
        print("✗ 部分測試失敗")
        print("\n可能的原因:")
        print("1. 學校 Moodle 未啟用 Web Services")
        print("2. 帳號密碼錯誤")
        print("3. 網路連線問題")
        print("\n解決方案:")
        print("1. 確認帳號密碼正確")
        print("2. 聯繫學校確認是否支援 Web Services API")
        print("3. 如果無法使用 API，仍可使用 Selenium 方法 (use_api=False)")
    print("=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
