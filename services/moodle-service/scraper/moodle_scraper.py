"""Moodle 爬蟲核心模組"""
import time
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options


class MoodleScraper:
    """Moodle 爬蟲類"""

    def __init__(self, base_url: str, username: str, password: str, headless: bool = True):
        """
        初始化爬蟲

        Args:
            base_url: Moodle 網站基礎 URL
            username: 登入帳號
            password: 登入密碼
            headless: 是否使用無頭模式
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None

    def __enter__(self):
        """Context manager 入口"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 出口"""
        self.close()

    def start(self):
        """啟動瀏覽器"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')

        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')

        # 設定下載偏好
        prefs = {
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': False
        }
        options.add_experimental_option('prefs', prefs)

        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        print("✓ 瀏覽器已啟動")

    def close(self):
        """關閉瀏覽器"""
        if self.driver:
            self.driver.quit()
            print("✓ 瀏覽器已關閉")

    def login(self) -> bool:
        """
        登入 Moodle 系統（支援 SSO 單一登入）

        Returns:
            是否登入成功
        """
        if not self.driver:
            raise RuntimeError("瀏覽器未啟動，請先呼叫 start()")

        try:
            print(f"→ 正在訪問 {self.base_url}")
            self.driver.get(self.base_url)

            # 等待頁面載入
            wait = WebDriverWait(self.driver, 15)
            time.sleep(2)

            # 檢查是否已經登入
            try:
                self.driver.find_element(By.CLASS_NAME, "usermenu")
                print("✓ 已經是登入狀態")
                return True
            except NoSuchElementException:
                pass

            # 嘗試多種登入方式
            print("→ 尋找登入表單...")
            
            # 方式1: 尋找包含 "登入" 文字的連結或按鈕
            try:
                login_link = self.driver.find_element(By.PARTIAL_LINK_TEXT, "登入")
                print("→ 找到登入連結")
                login_link.click()
                time.sleep(2)
            except NoSuchElementException:
                print("→ 未找到登入連結，可能已在登入頁面")

            # 方式2: 直接尋找帳號輸入框（各種可能的 ID）
            username_field = None
            possible_username_ids = ["username", "userNameInput", "user", "userid", "login"]
            
            for field_id in possible_username_ids:
                try:
                    username_field = self.driver.find_element(By.ID, field_id)
                    print(f"→ 找到帳號輸入框: {field_id}")
                    break
                except NoSuchElementException:
                    continue

            # 如果還是找不到，嘗試用 name 屬性
            if not username_field:
                try:
                    username_field = self.driver.find_element(By.NAME, "username")
                    print("→ 找到帳號輸入框 (name=username)")
                except NoSuchElementException:
                    # 最後嘗試用 type
                    try:
                        username_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                        if username_fields:
                            username_field = username_fields[0]
                            print("→ 找到帳號輸入框 (type=text)")
                    except:
                        pass

            if not username_field:
                print("✗ 無法找到帳號輸入框")
                # 保存截圖以便除錯
                self.driver.save_screenshot("/tmp/moodle_login_error.png")
                print("→ 已儲存截圖至 /tmp/moodle_login_error.png")
                return False

            # 輸入帳號
            print("→ 輸入帳號")
            username_field.clear()
            username_field.send_keys(self.username)

            # 尋找密碼輸入框
            password_field = None
            possible_password_ids = ["password", "passwordInput", "pass", "passwd"]
            
            for field_id in possible_password_ids:
                try:
                    password_field = self.driver.find_element(By.ID, field_id)
                    print(f"→ 找到密碼輸入框: {field_id}")
                    break
                except NoSuchElementException:
                    continue

            if not password_field:
                try:
                    password_field = self.driver.find_element(By.NAME, "password")
                    print("→ 找到密碼輸入框 (name=password)")
                except NoSuchElementException:
                    try:
                        password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                        print("→ 找到密碼輸入框 (type=password)")
                    except:
                        pass

            if not password_field:
                print("✗ 無法找到密碼輸入框")
                return False

            # 輸入密碼
            print("→ 輸入密碼")
            password_field.clear()
            password_field.send_keys(self.password)

            # 尋找登入按鈕
            login_button = None
            possible_button_ids = ["loginbtn", "submitButton", "submit", "login"]
            
            for button_id in possible_button_ids:
                try:
                    login_button = self.driver.find_element(By.ID, button_id)
                    print(f"→ 找到登入按鈕: {button_id}")
                    break
                except NoSuchElementException:
                    continue

            if not login_button:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                    print("→ 找到登入按鈕 (type=submit)")
                except NoSuchElementException:
                    try:
                        login_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                        print("→ 找到登入按鈕 (input submit)")
                    except:
                        pass

            if not login_button:
                print("✗ 無法找到登入按鈕")
                return False

            # 點擊登入
            print("→ 點擊登入按鈕")
            login_button.click()

            # 等待登入完成
            time.sleep(5)
            
            # 檢查是否登入成功
            try:
                wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "usermenu"))
                )
                print("✓ 登入成功")
                return True
            except TimeoutException:
                # 可能已經在 dashboard，檢查 URL
                if "my" in self.driver.current_url or "dashboard" in self.driver.current_url:
                    print("✓ 登入成功 (已進入 dashboard)")
                    return True
                else:
                    print(f"✗ 登入失敗，當前 URL: {self.driver.current_url}")
                    self.driver.save_screenshot("/tmp/moodle_login_failed.png")
                    print("→ 已儲存截圖至 /tmp/moodle_login_failed.png")
                    return False

        except Exception as e:
            print(f"✗ 登入過程發生錯誤: {e}")
            try:
                self.driver.save_screenshot("/tmp/moodle_error.png")
                print("→ 已儲存錯誤截圖至 /tmp/moodle_error.png")
            except:
                pass
            return False

    def get_courses(self) -> List[Dict[str, Any]]:
        """
        獲取所有課程列表

        Returns:
            課程列表，每個課程包含 id, name, url
        """
        if not self.driver:
            raise RuntimeError("瀏覽器未啟動")

        try:
            # 訪問課程列表頁面
            courses_url = f"{self.base_url}/my/"
            print(f"→ 正在獲取課程列表: {courses_url}")
            self.driver.get(courses_url)

            wait = WebDriverWait(self.driver, 10)
            time.sleep(2)

            # 尋找所有課程連結
            course_elements = self.driver.find_elements(By.CSS_SELECTOR, ".coursename a")

            courses = []
            for elem in course_elements:
                course_name = elem.text.strip()
                course_url = elem.get_attribute('href')

                if course_name and course_url:
                    # 從 URL 中提取課程 ID
                    course_id = course_url.split('id=')[-1] if 'id=' in course_url else None

                    courses.append({
                        'id': course_id,
                        'name': course_name,
                        'url': course_url,
                        'sections': []
                    })

            print(f"✓ 找到 {len(courses)} 門課程")
            return courses

        except Exception as e:
            print(f"✗ 獲取課程列表失敗: {e}")
            return []

    def get_course_content(self, course: Dict[str, Any]) -> Dict[str, Any]:
        """
        獲取課程內容（章節、活動、資源）

        Args:
            course: 課程資訊字典

        Returns:
            包含完整章節內容的課程資訊
        """
        if not self.driver:
            raise RuntimeError("瀏覽器未啟動")

        try:
            print(f"→ 正在解析課程: {course['name']}")
            self.driver.get(course['url'])
            time.sleep(2)

            # 尋找所有章節
            sections = self.driver.find_elements(By.CSS_SELECTOR, "li.section.main")

            for idx, section_elem in enumerate(sections):
                try:
                    # 獲取章節標題
                    title_elem = section_elem.find_element(By.CSS_SELECTOR, ".sectionname")
                    section_title = title_elem.text.strip() if title_elem else f"Section {idx}"

                    # 獲取該章節的所有活動/資源
                    activities = []
                    activity_elements = section_elem.find_elements(By.CSS_SELECTOR, ".activity")

                    for activity_elem in activity_elements:
                        try:
                            # 獲取活動名稱和連結
                            link_elem = activity_elem.find_element(By.CSS_SELECTOR, "a")
                            activity_name = link_elem.text.strip()
                            activity_url = link_elem.get_attribute('href')

                            # 判斷活動類型
                            activity_type = 'unknown'
                            if 'resource' in activity_elem.get_attribute('class'):
                                activity_type = 'resource'
                            elif 'assign' in activity_elem.get_attribute('class'):
                                activity_type = 'assignment'
                            elif 'forum' in activity_elem.get_attribute('class'):
                                activity_type = 'forum'
                            elif 'quiz' in activity_elem.get_attribute('class'):
                                activity_type = 'quiz'
                            elif 'url' in activity_elem.get_attribute('class'):
                                activity_type = 'url'

                            if activity_name and activity_url:
                                activities.append({
                                    'name': activity_name,
                                    'url': activity_url,
                                    'type': activity_type
                                })

                        except NoSuchElementException:
                            continue

                    course['sections'].append({
                        'index': idx,
                        'title': section_title,
                        'activities': activities
                    })

                except NoSuchElementException:
                    continue

            print(f"✓ 解析完成: 找到 {len(course['sections'])} 個章節")
            return course

        except Exception as e:
            print(f"✗ 解析課程內容失敗: {e}")
            return course

    def scrape_all(self) -> Dict[str, Any]:
        """
        完整爬取流程：登入 -> 獲取課程 -> 解析內容

        Returns:
            包含所有課程資料的字典
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'username': self.username,
            'courses': []
        }

        print("=" * 60)
        print("開始爬取 Moodle 課程資料")
        print("=" * 60)

        # 登入
        if not self.login():
            print("✗ 無法繼續，登入失敗")
            return result

        # 獲取課程列表
        courses = self.get_courses()
        if not courses:
            print("✗ 未找到任何課程")
            return result

        # 解析每門課程的內容
        for course in courses:
            detailed_course = self.get_course_content(course)
            result['courses'].append(detailed_course)

        print("=" * 60)
        print(f"✓ 完成！共爬取 {len(result['courses'])} 門課程")
        print("=" * 60)

        return result

    def save_to_json(self, data: Dict[str, Any], output_path: str = "moodle_courses.json"):
        """
        將資料儲存為 JSON 檔案

        Args:
            data: 要儲存的資料
            output_path: 輸出檔案路徑
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ 已儲存至: {output_path}")
