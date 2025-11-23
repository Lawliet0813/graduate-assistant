"""
Moodle Web Services API Client

使用 Moodle 官方 Web Services API 進行資料同步
這比 Selenium 爬蟲更穩定、更快速、更可靠
"""

import requests
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)


class MoodleAPIClient:
    """Moodle Web Services API 客戶端"""

    def __init__(self, base_url: str, username: str = None, password: str = None, token: str = None):
        """
        初始化 API 客戶端

        Args:
            base_url: Moodle 網站基礎 URL (例: https://moodle45.nccu.edu.tw)
            username: 登入帳號（用於獲取 token）
            password: 登入密碼（用於獲取 token）
            token: Web Service Token（如果已有 token 可直接使用）
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self._token = token
        self.session = requests.Session()

        # 設定預設的請求參數
        self.session.headers.update({
            'User-Agent': 'Moodle-API-Client/1.0'
        })

    @property
    def token(self) -> Optional[str]:
        """獲取或生成 token"""
        if not self._token and self.username and self.password:
            self._token = self.get_token()
        return self._token

    def get_token(self, service: str = "moodle_mobile_app") -> Optional[str]:
        """
        使用帳號密碼獲取 Web Service Token

        Args:
            service: Web Service 名稱，預設使用 moodle_mobile_app

        Returns:
            Token 字串，如果失敗則返回 None
        """
        try:
            url = f"{self.base_url}/login/token.php"
            params = {
                'username': self.username,
                'password': self.password,
                'service': service
            }

            logger.info(f"正在獲取 token: {url}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if 'token' in data:
                logger.info("✓ Token 獲取成功")
                return data['token']
            elif 'error' in data:
                logger.error(f"✗ Token 獲取失敗: {data.get('error', 'Unknown error')}")
                if 'errorcode' in data:
                    logger.error(f"  錯誤代碼: {data['errorcode']}")
                if 'debuginfo' in data:
                    logger.error(f"  除錯資訊: {data['debuginfo']}")
                return None
            else:
                logger.error(f"✗ 未知的回應格式: {data}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"✗ 網路請求失敗: {e}")
            return None
        except Exception as e:
            logger.error(f"✗ 獲取 token 時發生錯誤: {e}")
            return None

    def call_api(self, function: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        呼叫 Moodle Web Service API

        Args:
            function: API 函數名稱 (例: core_course_get_courses)
            params: API 參數

        Returns:
            API 回應的 JSON 資料
        """
        if not self.token:
            raise ValueError("No token available. Please provide token or username/password.")

        url = f"{self.base_url}/webservice/rest/server.php"

        request_params = {
            'wstoken': self.token,
            'wsfunction': function,
            'moodlewsrestformat': 'json'
        }

        if params:
            request_params.update(params)

        try:
            logger.debug(f"呼叫 API: {function}")
            response = self.session.get(url, params=request_params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # 檢查是否有錯誤
            if isinstance(data, dict) and 'exception' in data:
                logger.error(f"API 錯誤: {data.get('message', 'Unknown error')}")
                raise Exception(f"Moodle API Error: {data.get('message', 'Unknown error')}")

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"API 請求失敗: {e}")
            raise
        except Exception as e:
            logger.error(f"API 呼叫錯誤: {e}")
            raise

    def get_user_courses(self) -> List[Dict[str, Any]]:
        """
        獲取當前使用者的所有課程

        Returns:
            課程列表
        """
        try:
            # 首先獲取當前使用者 ID
            user_info = self.call_api('core_webservice_get_site_info')
            user_id = user_info.get('userid')

            if not user_id:
                logger.error("無法獲取使用者 ID")
                return []

            # 獲取使用者的課程
            courses = self.call_api('core_enrol_get_users_courses', {
                'userid': user_id
            })

            logger.info(f"✓ 找到 {len(courses)} 門課程")

            # 格式化課程資料
            formatted_courses = []
            for course in courses:
                formatted_courses.append({
                    'id': str(course.get('id')),
                    'name': course.get('fullname', course.get('shortname', 'Unknown')),
                    'shortname': course.get('shortname', ''),
                    'url': f"{self.base_url}/course/view.php?id={course.get('id')}",
                    'description': course.get('summary', ''),
                    'visible': course.get('visible', 1) == 1,
                    'startdate': course.get('startdate'),
                    'enddate': course.get('enddate'),
                })

            return formatted_courses

        except Exception as e:
            logger.error(f"獲取課程列表失敗: {e}")
            return []

    def get_course_contents(self, course_id: int) -> List[Dict[str, Any]]:
        """
        獲取課程內容（章節、活動、資源）

        Args:
            course_id: 課程 ID

        Returns:
            課程內容列表（按章節組織）
        """
        try:
            contents = self.call_api('core_course_get_contents', {
                'courseid': course_id
            })

            logger.info(f"✓ 獲取課程 {course_id} 的內容，共 {len(contents)} 個章節")

            # 格式化章節資料
            formatted_sections = []
            for section in contents:
                activities = []

                for module in section.get('modules', []):
                    activity = {
                        'id': module.get('id'),
                        'name': module.get('name'),
                        'modname': module.get('modname'),  # 活動類型 (assign, resource, forum, etc.)
                        'url': module.get('url'),
                        'description': module.get('description', ''),
                        'visible': module.get('visible', 1) == 1,
                    }

                    # 如果是檔案資源，加入檔案資訊
                    if 'contents' in module:
                        activity['files'] = [
                            {
                                'filename': content.get('filename'),
                                'fileurl': content.get('fileurl'),
                                'filesize': content.get('filesize'),
                                'mimetype': content.get('mimetype'),
                            }
                            for content in module.get('contents', [])
                        ]

                    activities.append(activity)

                formatted_sections.append({
                    'id': section.get('id'),
                    'name': section.get('name', f"Section {section.get('section', 0)}"),
                    'section': section.get('section'),
                    'summary': section.get('summary', ''),
                    'visible': section.get('visible', 1) == 1,
                    'activities': activities
                })

            return formatted_sections

        except Exception as e:
            logger.error(f"獲取課程內容失敗: {e}")
            return []

    def get_assignments(self, course_ids: List[int] = None) -> List[Dict[str, Any]]:
        """
        獲取作業列表

        Args:
            course_ids: 課程 ID 列表（可選，如果不提供則獲取所有課程的作業）

        Returns:
            作業列表
        """
        try:
            params = {}
            if course_ids:
                params['courseids'] = course_ids

            assignments = self.call_api('mod_assign_get_assignments', params)

            logger.info(f"✓ 找到 {len(assignments.get('courses', []))} 個課程的作業")

            # 格式化作業資料
            all_assignments = []
            for course in assignments.get('courses', []):
                course_id = course.get('id')
                course_name = course.get('fullname', '')

                for assignment in course.get('assignments', []):
                    all_assignments.append({
                        'id': str(assignment.get('id')),
                        'course_id': str(course_id),
                        'course_name': course_name,
                        'name': assignment.get('name'),
                        'intro': assignment.get('intro', ''),
                        'duedate': assignment.get('duedate'),
                        'allowsubmissionsfromdate': assignment.get('allowsubmissionsfromdate'),
                        'cutoffdate': assignment.get('cutoffdate'),
                        'url': f"{self.base_url}/mod/assign/view.php?id={assignment.get('cmid')}",
                    })

            logger.info(f"✓ 總共 {len(all_assignments)} 個作業")
            return all_assignments

        except Exception as e:
            logger.error(f"獲取作業列表失敗: {e}")
            return []

    def get_calendar_events(self) -> List[Dict[str, Any]]:
        """
        獲取行事曆事件（包含作業截止日等）

        Returns:
            事件列表
        """
        try:
            events = self.call_api('core_calendar_get_calendar_upcoming_view')

            logger.info(f"✓ 找到 {len(events.get('events', []))} 個即將到來的事件")

            # 格式化事件資料
            formatted_events = []
            for event in events.get('events', []):
                formatted_events.append({
                    'id': event.get('id'),
                    'name': event.get('name'),
                    'description': event.get('description', ''),
                    'eventtype': event.get('eventtype'),
                    'timestart': event.get('timestart'),
                    'timeduration': event.get('timeduration'),
                    'course_id': event.get('course', {}).get('id') if event.get('course') else None,
                    'url': event.get('url'),
                })

            return formatted_events

        except Exception as e:
            logger.error(f"獲取行事曆事件失敗: {e}")
            return []

    def test_connection(self) -> bool:
        """
        測試 API 連線

        Returns:
            連線是否成功
        """
        try:
            info = self.call_api('core_webservice_get_site_info')
            logger.info(f"✓ 連線成功！")
            logger.info(f"  網站名稱: {info.get('sitename')}")
            logger.info(f"  使用者: {info.get('fullname')} ({info.get('username')})")
            logger.info(f"  Moodle 版本: {info.get('release')}")
            return True
        except Exception as e:
            logger.error(f"✗ 連線測試失敗: {e}")
            return False
