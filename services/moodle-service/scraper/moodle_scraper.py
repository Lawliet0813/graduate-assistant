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
            wait = WebDriverWait(self.driver, 20)
            time.sleep(3)

            # 檢查是否已經登入
            try:
                self.driver.find_element(By.CLASS_NAME, "usermenu")
                print("✓ 已經是登入狀態")
                return True
            except NoSuchElementException:
                pass

            # 嘗試多種登入方式
            print("→ 尋找登入入口...")
            
            # 檢查是否在 iframe 中
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                print(f"→ 發現 {len(iframes)} 個 iframe，嘗試切換...")
                for i, iframe in enumerate(iframes):
                    try:
                        self.driver.switch_to.frame(iframe)
                        # 檢查是否有登入表單
                        if self.driver.find_elements(By.ID, "username") or \
                           self.driver.find_elements(By.NAME, "username") or \
                           self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']"):
                            print(f"  ✓ 在 iframe {i} 中找到登入表單")
                            break
                        else:
                            # 切換回主頁面
                            self.driver.switch_to.default_content()
                    except:
                        self.driver.switch_to.default_content()
                        continue
            
            # 方式1: 尋找 SSO 登入按鈕（NCCU INCCU 單一登入）
            try:
                # 擴展搜尋範圍，包含 INCCU 相關的按鈕和連結
                sso_selectors = [
                    # INCCU 單一登入相關
                    "//a[contains(@href, 'inccu')]",
                    "//a[contains(text(), 'INCCU')]",
                    "//button[contains(text(), 'INCCU')]",
                    "//a[contains(text(), '單一登入')]",
                    # 一般 SSO 按鈕
                    "//button[contains(., 'SSO')] | //a[contains(., 'SSO')]",
                    "//a[contains(@href, 'sso')] | //a[contains(@href, 'SSO')]",
                    # 登入相關
                    "//button[contains(@class, 'login')] | //a[contains(@class, 'login')]",
                    "//button[contains(., '登入')] | //a[contains(., '登入')]",
                ]

                sso_button_found = False
                for selector in sso_selectors:
                    try:
                        sso_buttons = self.driver.find_elements(By.XPATH, selector)
                        if sso_buttons:
                            print(f"→ 找到 SSO/INCCU 登入按鈕")
                            sso_buttons[0].click()
                            sso_button_found = True
                            print("→ 等待跳轉到 INCCU 登入頁面...")
                            time.sleep(5)  # 增加等待時間，等待頁面跳轉

                            # 檢查是否已跳轉到 INCCU
                            current_url = self.driver.current_url.lower()
                            if 'inccu' in current_url or 'sso' in current_url:
                                print(f"  ✓ 已跳轉到 INCCU 登入頁面: {self.driver.current_url}")
                            break
                    except:
                        continue

                if sso_button_found:
                    print("  ℹ 注意: 使用 INCCU 單一登入，請使用您的政大帳號密碼")
            except Exception as e:
                print(f"→ 尋找 SSO 按鈕時發生錯誤: {e}")
            
            # 方式2: 檢查是否有 "login" 連結或導向到登入頁面
            try:
                login_links = self.driver.find_elements(By.XPATH, 
                    "//a[contains(@href, 'login')] | //a[contains(text(), '登入')]")
                if login_links:
                    print("→ 找到登入連結")
                    login_links[0].click()
                    time.sleep(3)
            except Exception as e:
                print(f"→ 尋找登入連結時發生錯誤: {e}")

            # 方式3: 直接尋找帳號輸入框（包含 INCCU SSO 登入表單）
            username_field = None
            possible_selectors = [
                # 標準 Moodle 欄位
                (By.ID, "username"),
                (By.NAME, "username"),
                # Microsoft/Azure AD SSO (INCCU 可能使用)
                (By.ID, "userNameInput"),
                (By.ID, "i0116"),  # Microsoft 登入頁面
                (By.NAME, "loginfmt"),  # Microsoft 帳號輸入
                # 其他常見欄位
                (By.ID, "user"),
                (By.ID, "userid"),
                (By.ID, "login"),
                (By.ID, "account"),
                (By.NAME, "UserName"),
                (By.NAME, "user"),
                (By.NAME, "account"),
                # INCCU 相關欄位
                (By.NAME, "uid"),  # INCCU 常用欄位
                (By.NAME, "id"),
                # 通用搜尋
                (By.CSS_SELECTOR, "input[type='text'][name*='user']"),
                (By.CSS_SELECTOR, "input[type='text'][id*='user']"),
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.CSS_SELECTOR, "input[placeholder*='帳號']"),
                (By.CSS_SELECTOR, "input[placeholder*='學號']"),
                (By.CSS_SELECTOR, "input[placeholder*='Email']"),
            ]
            
            for by_method, selector in possible_selectors:
                try:
                    username_field = wait.until(
                        EC.presence_of_element_located((by_method, selector))
                    )
                    print(f"→ 找到帳號輸入框: {by_method}={selector}")
                    break
                except (NoSuchElementException, TimeoutException):
                    continue

            # 如果還是找不到，嘗試所有可見的 text input
            if not username_field:
                try:
                    text_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email']")
                    visible_inputs = [inp for inp in text_inputs if inp.is_displayed()]
                    if visible_inputs:
                        username_field = visible_inputs[0]
                        print("→ 找到可見的文字輸入框")
                except:
                    pass

            if not username_field:
                print("✗ 無法找到帳號輸入框")
                print(f"→ 當前 URL: {self.driver.current_url}")
                print(f"→ 頁面標題: {self.driver.title}")
                # 保存頁面資訊以便除錯
                self.driver.save_screenshot("/tmp/moodle_login_error.png")
                with open("/tmp/moodle_page_source.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                print("→ 已儲存截圖至 /tmp/moodle_login_error.png")
                print("→ 已儲存頁面原始碼至 /tmp/moodle_page_source.html")
                return False

            # 輸入帳號
            print("→ 輸入帳號")
            try:
                # 等待輸入框變為可點擊
                wait.until(EC.element_to_be_clickable(username_field))
                time.sleep(0.5)
                
                # 點擊輸入框以獲得焦點
                try:
                    username_field.click()
                    time.sleep(0.3)
                except:
                    pass
                
                # 清空並輸入
                try:
                    username_field.clear()
                except:
                    pass
                
                username_field.send_keys(self.username)
                time.sleep(0.5)
                print(f"  ✓ 已輸入帳號")
            except Exception as e:
                print(f"  ⚠ 輸入帳號時發生錯誤: {e}")
                # 嘗試用 JavaScript 輸入
                try:
                    self.driver.execute_script(
                        f"arguments[0].value = '{self.username}';",
                        username_field
                    )
                    print(f"  ✓ 已使用 JavaScript 輸入帳號")
                except Exception as js_error:
                    print(f"  ✗ JavaScript 輸入也失敗: {js_error}")
                    self.driver.save_screenshot("/tmp/moodle_username_error.png")
                    return False

            # 尋找密碼輸入框（包含 INCCU SSO）
            password_field = None
            password_selectors = [
                # 標準欄位
                (By.ID, "password"),
                (By.NAME, "password"),
                # Microsoft/Azure AD SSO
                (By.ID, "passwordInput"),
                (By.ID, "i0118"),  # Microsoft 密碼頁面
                (By.NAME, "passwd"),
                # 其他常見欄位
                (By.ID, "pass"),
                (By.ID, "pwd"),
                (By.NAME, "Password"),
                (By.NAME, "pwd"),
                # 通用搜尋
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.CSS_SELECTOR, "input[placeholder*='密碼']"),
                (By.CSS_SELECTOR, "input[placeholder*='Password']"),
            ]
            
            for by_method, selector in password_selectors:
                try:
                    password_field = self.driver.find_element(by_method, selector)
                    print(f"→ 找到密碼輸入框: {by_method}={selector}")
                    break
                except NoSuchElementException:
                    continue

            if not password_field:
                print("✗ 無法找到密碼輸入框")
                print(f"→ 當前 URL: {self.driver.current_url}")
                return False

            # 輸入密碼
            print("→ 輸入密碼")
            try:
                # 確保密碼框可點擊
                time.sleep(0.5)
                try:
                    password_field.click()
                    time.sleep(0.3)
                except:
                    pass
                
                # 清空並輸入
                try:
                    password_field.clear()
                except:
                    pass
                
                password_field.send_keys(self.password)
                time.sleep(0.5)
                print(f"  ✓ 已輸入密碼")
            except Exception as e:
                print(f"  ⚠ 輸入密碼時發生錯誤: {e}")
                # 嘗試用 JavaScript 輸入
                try:
                    self.driver.execute_script(
                        f"arguments[0].value = '{self.password}';",
                        password_field
                    )
                    print(f"  ✓ 已使用 JavaScript 輸入密碼")
                except Exception as js_error:
                    print(f"  ✗ JavaScript 輸入也失敗: {js_error}")
                    self.driver.save_screenshot("/tmp/moodle_password_error.png")
                    return False

            # 尋找登入按鈕（包含 INCCU SSO）
            login_button = None
            button_selectors = [
                # 標準按鈕
                (By.ID, "loginbtn"),
                (By.ID, "submitButton"),
                (By.ID, "submit"),
                (By.ID, "login"),
                # Microsoft/Azure AD SSO
                (By.ID, "idSIButton9"),  # Microsoft "Sign in" 按鈕
                (By.ID, "idBtn_Back"),  # Microsoft 其他按鈕
                # 其他常見按鈕
                (By.NAME, "submitButton"),
                (By.NAME, "submit"),
                (By.NAME, "login"),
                # 通用搜尋
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, "input[type='submit']"),
                (By.CSS_SELECTOR, "button.btn-primary"),
                (By.XPATH, "//button[contains(., '登入')] | //button[contains(., 'Login')] | //button[contains(., '送出')] | //button[contains(., 'Sign in')] | //input[@value='登入'] | //input[@value='Login']"),
            ]
            
            for by_method, selector in button_selectors:
                try:
                    buttons = self.driver.find_elements(by_method, selector)
                    visible_buttons = [btn for btn in buttons if btn.is_displayed() and btn.is_enabled()]
                    if visible_buttons:
                        login_button = visible_buttons[0]
                        print(f"→ 找到登入按鈕: {by_method}={selector}")
                        break
                except:
                    continue

            if not login_button:
                print("✗ 無法找到登入按鈕，嘗試按 Enter")
                # 如果找不到按鈕，嘗試在密碼框按 Enter
                from selenium.webdriver.common.keys import Keys
                password_field.send_keys(Keys.RETURN)
            else:
                # 點擊登入
                print("→ 點擊登入按鈕")
                try:
                    login_button.click()
                except:
                    # 如果點擊失敗，嘗試用 JavaScript 點擊
                    self.driver.execute_script("arguments[0].click();", login_button)

            # 等待登入完成（增加等待時間）
            print("→ 等待登入完成...")
            time.sleep(5)
            
            # 檢查是否登入成功（多種方式）
            success_indicators = [
                (By.CLASS_NAME, "usermenu"),
                (By.CSS_SELECTOR, ".usermenu"),
                (By.XPATH, "//*[contains(@class, 'usermenu')]"),
                (By.XPATH, "//*[contains(@class, 'userbutton')]"),
            ]
            
            for by_method, selector in success_indicators:
                try:
                    wait.until(EC.presence_of_element_located((by_method, selector)))
                    print("✓ 登入成功")
                    return True
                except TimeoutException:
                    continue
            
            # 檢查 URL 是否改變（表示可能登入成功）
            current_url = self.driver.current_url.lower()
            if any(keyword in current_url for keyword in ["my", "dashboard", "course", "/my/"]):
                print(f"✓ 登入成功 (URL 已變更: {self.driver.current_url})")
                return True
            
            # 檢查是否有錯誤訊息
            try:
                error_elements = self.driver.find_elements(By.XPATH, 
                    "//*[contains(@class, 'error')] | //*[contains(@class, 'alert')]")
                if error_elements:
                    error_text = " ".join([e.text for e in error_elements if e.text])
                    print(f"✗ 登入失敗，錯誤訊息: {error_text}")
            except:
                pass
            
            print(f"✗ 登入失敗，當前 URL: {self.driver.current_url}")
            self.driver.save_screenshot("/tmp/moodle_login_failed.png")
            with open("/tmp/moodle_login_failed.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print("→ 已儲存截圖至 /tmp/moodle_login_failed.png")
            print("→ 已儲存頁面原始碼至 /tmp/moodle_login_failed.html")
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

            # 嘗試多種課程選擇器
            course_elements = []
            selectors = [
                ".coursename a",  # 標準 Moodle
                "a.aalink.coursename",  # 新版 Moodle
                "[data-type='course'] a",  # 使用 data 屬性
                ".course-info-container a",  # 課程資訊容器
                "div.course-content a[href*='course/view']",  # 包含課程連結
                "a[href*='course/view.php']",  # 直接找課程連結
                ".dashboard-card a",  # Dashboard 卡片
                "[class*='course'] a[href*='/course/']",  # 通用課程連結
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"  → 使用選擇器找到 {len(elements)} 個元素: {selector}")
                        course_elements = elements
                        break
                except:
                    continue
            
            # 如果還是找不到，嘗試尋找所有包含 course/view 的連結
            if not course_elements:
                try:
                    all_links = self.driver.find_elements(By.TAG_NAME, "a")
                    course_elements = [
                        link for link in all_links 
                        if link.get_attribute('href') and 'course/view' in link.get_attribute('href')
                    ]
                    print(f"  → 使用通用方法找到 {len(course_elements)} 個課程連結")
                except:
                    pass

            courses = []
            seen_urls = set()  # 避免重複
            
            for elem in course_elements:
                try:
                    course_name = elem.text.strip()
                    course_url = elem.get_attribute('href')

                    if course_name and course_url and course_url not in seen_urls:
                        # 過濾掉非課程連結
                        if 'course/view' in course_url and '?' in course_url:
                            seen_urls.add(course_url)
                            
                            # 從 URL 中提取課程 ID
                            course_id = course_url.split('id=')[-1].split('&')[0] if 'id=' in course_url else None

                            courses.append({
                                'id': course_id,
                                'name': course_name,
                                'url': course_url,
                                'sections': []
                            })
                except Exception as e:
                    continue

            print(f"✓ 找到 {len(courses)} 門課程")
            
            # 如果沒找到課程，保存頁面供除錯
            if len(courses) == 0:
                print("⚠ 未找到任何課程，保存頁面供除錯...")
                try:
                    self.driver.save_screenshot("/tmp/moodle_no_courses.png")
                    with open("/tmp/moodle_no_courses.html", "w", encoding="utf-8") as f:
                        f.write(self.driver.page_source)
                    print("  → 截圖: /tmp/moodle_no_courses.png")
                    print("  → 頁面: /tmp/moodle_no_courses.html")
                    print(f"  → 當前 URL: {self.driver.current_url}")
                except:
                    pass
            
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
