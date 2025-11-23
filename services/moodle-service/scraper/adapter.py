"""
Adapter module to convert Moodle scraper output to API response format
Supports both Selenium scraping and Moodle Web Services API
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .moodle_scraper import MoodleScraper
from .moodle_api_client import MoodleAPIClient
import logging

logger = logging.getLogger(__name__)


class MoodleAdapter:
    """Adapter to convert scraped data to API response format"""

    @staticmethod
    def convert_course(course_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert course data from scraper format to API format

        Args:
            course_data: Raw course data from scraper

        Returns:
            Formatted course data
        """
        return {
            "id": course_data.get("id", ""),
            "name": course_data.get("name", ""),
            "url": course_data.get("url", ""),
            "description": course_data.get("description", ""),
            "teacher": course_data.get("teacher", ""),
            "semester": course_data.get("semester", ""),
        }

    @staticmethod
    def convert_course_content(content_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert course content from scraper format to API format

        Args:
            content_data: Raw content data from scraper (sections)

        Returns:
            Formatted course contents
        """
        formatted_contents = []

        for section in content_data:
            formatted_section = {
                "section_name": section.get("title", ""),
                "activities": []
            }

            for activity in section.get("activities", []):
                formatted_activity = {
                    "type": activity.get("type", ""),
                    "name": activity.get("name", ""),
                    "url": activity.get("url", ""),
                    "description": activity.get("description", ""),
                }
                formatted_section["activities"].append(formatted_activity)

            formatted_contents.append(formatted_section)

        return formatted_contents

    @staticmethod
    def convert_assignment(assignment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert assignment data from scraper format to API format

        Args:
            assignment_data: Raw assignment data from scraper

        Returns:
            Formatted assignment data
        """
        return {
            "id": assignment_data.get("id", ""),
            "course_id": assignment_data.get("course_id", ""),
            "course_name": assignment_data.get("course_name", ""),
            "name": assignment_data.get("name", ""),
            "due_date": assignment_data.get("due_date", None),
            "status": assignment_data.get("status", ""),
            "url": assignment_data.get("url", ""),
            "description": assignment_data.get("description", ""),
        }

    @staticmethod
    def extract_assignments_from_courses(courses_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract all assignments from courses data

        Args:
            courses_data: List of courses with contents

        Returns:
            List of formatted assignments
        """
        assignments = []

        for course in courses_data:
            course_id = course.get("id", "")
            course_name = course.get("name", "")

            # Check if course has sections
            if "sections" in course:
                for section in course["sections"]:
                    for activity in section.get("activities", []):
                        # If activity is an assignment
                        if activity.get("type", "").lower() in ["assign", "assignment", "作業"]:
                            assignment = {
                                "id": activity.get("url", "").split("id=")[-1] if "id=" in activity.get("url", "") else "",
                                "course_id": course_id,
                                "course_name": course_name,
                                "name": activity.get("name", ""),
                                "due_date": activity.get("due_date", None),
                                "status": activity.get("status", "pending"),
                                "url": activity.get("url", ""),
                                "description": activity.get("description", ""),
                            }
                            assignments.append(assignment)

        return assignments


class MoodleService:
    """Service class to handle Moodle operations"""

    def __init__(
        self,
        base_url: str,
        username: str = None,
        password: str = None,
        token: str = None,
        headless: bool = True,
        use_api: bool = True
    ):
        """
        Initialize Moodle service

        Args:
            base_url: Moodle base URL
            username: Username for login
            password: Password for login
            token: Web Service Token (optional, if available)
            headless: Whether to run browser in headless mode (for Selenium)
            use_api: Whether to use Web Services API (True) or Selenium scraper (False)
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token = token
        self.headless = headless
        self.use_api = use_api
        self.adapter = MoodleAdapter()

        # Initialize API client if using API mode
        if self.use_api:
            self.api_client = MoodleAPIClient(
                base_url=base_url,
                username=username,
                password=password,
                token=token
            )
        else:
            self.api_client = None

    def login(self) -> Dict[str, Any]:
        """
        Login to Moodle (or test API connection)

        Returns:
            Login result with success status
        """
        try:
            if self.use_api:
                # Test API connection and get token
                if self.api_client.test_connection():
                    return {
                        "success": True,
                        "message": "Successfully connected to Moodle API",
                        "session_id": self.api_client.token[:10] + "..." if self.api_client.token else None
                    }
                else:
                    return {
                        "success": False,
                        "message": "Failed to connect to Moodle API",
                        "session_id": None
                    }
            else:
                # Use Selenium scraper
                with MoodleScraper(self.base_url, self.username, self.password, self.headless) as scraper:
                    if scraper.login():
                        return {
                            "success": True,
                            "message": "Successfully logged in to Moodle",
                            "session_id": "selenium-session"
                        }
                    else:
                        return {
                            "success": False,
                            "message": "Login failed",
                            "session_id": None
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Login failed: {str(e)}",
                "session_id": None
            }

    def get_courses(self) -> List[Dict[str, Any]]:
        """
        Get all enrolled courses

        Returns:
            List of courses
        """
        try:
            if self.use_api:
                # Use API client
                courses = self.api_client.get_user_courses()
                logger.info(f"✓ 使用 API 獲取 {len(courses)} 門課程")
                return courses
            else:
                # Use Selenium scraper
                with MoodleScraper(self.base_url, self.username, self.password, self.headless) as scraper:
                    raw_data = scraper.scrape_all()

                    if not raw_data or "courses" not in raw_data:
                        return []

                    courses = [
                        self.adapter.convert_course(course)
                        for course in raw_data["courses"]
                    ]

                    return courses
        except Exception as e:
            logger.error(f"Error getting courses: {e}")
            return []

    def get_course_detail(self, course_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific course

        Args:
            course_id: Course ID to fetch

        Returns:
            Course details with contents, or None if not found
        """
        try:
            if self.use_api:
                # Use API client
                contents = self.api_client.get_course_contents(int(course_id))

                # Get basic course info from courses list
                courses = self.api_client.get_user_courses()
                course_info = next((c for c in courses if c['id'] == course_id), None)

                if course_info:
                    # Convert API format to expected format
                    formatted_contents = []
                    for section in contents:
                        formatted_section = {
                            "section_name": section['name'],
                            "activities": [
                                {
                                    "type": activity['modname'],
                                    "name": activity['name'],
                                    "url": activity.get('url', ''),
                                    "description": activity.get('description', ''),
                                }
                                for activity in section['activities']
                            ]
                        }
                        formatted_contents.append(formatted_section)

                    course_info['contents'] = formatted_contents
                    logger.info(f"✓ 使用 API 獲取課程 {course_id} 的詳細資訊")
                    return course_info
                else:
                    return None
            else:
                # Use Selenium scraper
                with MoodleScraper(self.base_url, self.username, self.password, self.headless) as scraper:
                    raw_data = scraper.scrape_all()

                    if not raw_data or "courses" not in raw_data:
                        return None

                    # Find course by ID
                    for course in raw_data["courses"]:
                        if course.get("id") == course_id:
                            course_info = self.adapter.convert_course(course)
                            course_info["contents"] = self.adapter.convert_course_content(
                                course.get("sections", [])
                            )
                            return course_info

                    return None
        except Exception as e:
            logger.error(f"Error getting course detail: {e}")
            return None

    def get_assignments(self, course_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all assignments, optionally filtered by course

        Args:
            course_id: Optional course ID to filter assignments

        Returns:
            List of assignments
        """
        try:
            if self.use_api:
                # Use API client
                course_ids = [int(course_id)] if course_id else None
                assignments = self.api_client.get_assignments(course_ids=course_ids)

                # Convert to expected format
                formatted_assignments = []
                for assignment in assignments:
                    formatted_assignments.append({
                        "id": assignment['id'],
                        "course_id": assignment['course_id'],
                        "course_name": assignment['course_name'],
                        "name": assignment['name'],
                        "due_date": datetime.fromtimestamp(assignment['duedate']).isoformat() if assignment.get('duedate') else None,
                        "status": "pending",  # API doesn't provide status, would need separate call
                        "url": assignment['url'],
                        "description": assignment.get('intro', ''),
                    })

                logger.info(f"✓ 使用 API 獲取 {len(formatted_assignments)} 個作業")
                return formatted_assignments
            else:
                # Use Selenium scraper
                with MoodleScraper(self.base_url, self.username, self.password, self.headless) as scraper:
                    raw_data = scraper.scrape_all()

                    if not raw_data or "courses" not in raw_data:
                        return []

                    # Extract assignments from all courses
                    assignments = self.adapter.extract_assignments_from_courses(raw_data["courses"])

                    # Filter by course_id if provided
                    if course_id:
                        assignments = [a for a in assignments if a["course_id"] == course_id]

                    return assignments
        except Exception as e:
            logger.error(f"Error getting assignments: {e}")
            return []

    def sync_all(self) -> Dict[str, Any]:
        """
        Perform full sync of all Moodle data

        Returns:
            Sync result with data
        """
        try:
            if self.use_api:
                # Use API client
                logger.info("開始使用 API 同步 Moodle 資料...")

                # Get courses
                courses = self.get_courses()

                # Get all assignments
                assignments = self.get_assignments()

                # Get detailed contents for each course
                for course in courses:
                    try:
                        course_detail = self.get_course_detail(course['id'])
                        if course_detail and 'contents' in course_detail:
                            course['contents'] = course_detail['contents']
                    except Exception as e:
                        logger.error(f"Failed to get contents for course {course['id']}: {e}")
                        course['contents'] = []

                logger.info(f"✓ API 同步完成: {len(courses)} 門課程, {len(assignments)} 個作業")

                return {
                    "success": True,
                    "message": "Successfully synced Moodle data using API",
                    "courses_count": len(courses),
                    "assignments_count": len(assignments),
                    "data": {
                        "courses": courses,
                        "assignments": assignments,
                        "synced_at": datetime.now().isoformat()
                    }
                }
            else:
                # Use Selenium scraper
                with MoodleScraper(self.base_url, self.username, self.password, self.headless) as scraper:
                    raw_data = scraper.scrape_all()

                    if not raw_data or "courses" not in raw_data:
                        return {
                            "success": False,
                            "message": "No data received from Moodle",
                            "courses_count": 0,
                            "assignments_count": 0,
                            "data": {}
                        }

                    # Convert courses
                    courses = [
                        {
                            **self.adapter.convert_course(course),
                            "contents": self.adapter.convert_course_content(course.get("sections", []))
                        }
                        for course in raw_data["courses"]
                    ]

                    # Extract assignments
                    assignments = self.adapter.extract_assignments_from_courses(raw_data["courses"])

                    return {
                        "success": True,
                        "message": "Successfully synced Moodle data using Selenium",
                        "courses_count": len(courses),
                        "assignments_count": len(assignments),
                        "data": {
                            "courses": courses,
                            "assignments": assignments,
                            "synced_at": datetime.now().isoformat()
                        }
                    }
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return {
                "success": False,
                "message": f"Sync failed: {str(e)}",
                "courses_count": 0,
                "assignments_count": 0,
                "data": {}
            }
