import time
import pytest
from pages.login_page import LoginPage
from pages.admin_page import AdminPage

class TestAdminModule:

    @pytest.fixture(autouse=True)
    def admin_login(self, driver):
        """Helper fixture to log in as admin before each test."""
        login_page = LoginPage(driver)
        login_page.open()
        login_page.login("admin", "Admin@123")
        time.sleep(1.5)
        assert "/admin-dashboard" in driver.current_url

    def test_01_admin_stats_overview(self, driver):
        """TC-ADM-01: Verify admin overview stats load correctly."""
        admin_page = AdminPage(driver)
        students_count = admin_page.get_text(admin_page.STAT_STUDENTS)
        assert int(students_count) >= 0

    def test_02_block_and_unblock_student(self, driver):
        """TC-ADM-02: Verify admin can block and unblock a student account."""
        admin_page = AdminPage(driver)
        admin_page.go_to_students()
        time.sleep(1)

        # Toggle student status for Student ID STU001 (id=3)
        from selenium.webdriver.common.by import By
        toggle_btn = driver.find_element(By.ID, "btn-toggle-student-3")
        btn_text_initial = toggle_btn.text.strip()

        toggle_btn.click()
        time.sleep(1)

        toggle_btn_updated = driver.find_element(By.ID, "btn-toggle-student-3")
        assert toggle_btn_updated.text.strip() != btn_text_initial

        # Toggle back to original state
        toggle_btn_updated.click()
        time.sleep(1)

    def test_03_create_course_success(self, driver):
        """TC-ADM-03: Verify admin can create a new academic course."""
        admin_page = AdminPage(driver)
        timestamp = int(time.time())
        course_code = f"CS{timestamp % 10000}"
        
        admin_page.create_course(course_code, "Automated Testing Course", dept_id="1")
        time.sleep(1)
        assert admin_page.is_visible(admin_page.COURSE_ALERT)
        assert "success" in admin_page.get_text(admin_page.COURSE_ALERT).lower()

    def test_04_create_exam_valid_duration(self, driver):
        """TC-ADM-04: Verify admin can create an exam with valid duration (15 mins)."""
        admin_page = AdminPage(driver)
        timestamp = int(time.time())
        exam_title = f"Selenium Exam {timestamp}"

        admin_page.create_exam(title=exam_title, course_id="1", duration="15", marks="10")
        time.sleep(1)
        assert admin_page.is_visible(admin_page.EXAM_ALERT)
        assert "success" in admin_page.get_text(admin_page.EXAM_ALERT).lower()

    def test_05_create_exam_duration_bva_under_min(self, driver):
        """TC-ADM-05: BVA Test - Exam duration 4 mins (Under min boundary 5 mins) fails validation."""
        admin_page = AdminPage(driver)
        admin_page.create_exam(title="BVA Under Min Exam", course_id="1", duration="4", marks="10")
        time.sleep(1)
        assert admin_page.is_visible(admin_page.EXAM_ALERT)
        assert "between 5 and 180" in admin_page.get_text(admin_page.EXAM_ALERT).lower()

    def test_06_create_exam_duration_bva_over_max(self, driver):
        """TC-ADM-06: BVA Test - Exam duration 181 mins (Over max boundary 180 mins) fails validation."""
        admin_page = AdminPage(driver)
        admin_page.create_exam(title="BVA Over Max Exam", course_id="1", duration="181", marks="10")
        time.sleep(1)
        assert admin_page.is_visible(admin_page.EXAM_ALERT)
        assert "between 5 and 180" in admin_page.get_text(admin_page.EXAM_ALERT).lower()

    def test_07_toggle_exam_publish_status(self, driver):
        """TC-ADM-07: Verify admin can publish and unpublish an exam."""
        admin_page = AdminPage(driver)
        admin_page.go_to_exams()
        time.sleep(1)

        from selenium.webdriver.common.by import By
        publish_btn = driver.find_element(By.ID, "btn-toggle-publish-1")
        initial_text = publish_btn.text.strip()

        publish_btn.click()
        time.sleep(1)

        updated_btn = driver.find_element(By.ID, "btn-toggle-publish-1")
        assert updated_btn.text.strip() != initial_text

        # Toggle back
        updated_btn.click()
        time.sleep(1)

    def test_08_add_mcq_question_to_exam(self, driver):
        """TC-ADM-08: Verify admin can add an MCQ question with 4 options to an exam."""
        admin_page = AdminPage(driver)
        admin_page.go_to_exams()
        time.sleep(1)

        from selenium.webdriver.common.by import By
        # Click Questions button for Exam 1
        driver.find_element(By.ID, "btn-manage-questions-1").click()
        time.sleep(1)

        # Fill question form
        admin_page.type(admin_page.Q_TEXT_INPUT, "What is the result of 2 + 2 in Python?")
        admin_page.type(admin_page.Q_OPA_INPUT, "3")
        admin_page.type(admin_page.Q_OPB_INPUT, "4")
        admin_page.type(admin_page.Q_OPC_INPUT, "5")
        admin_page.type(admin_page.Q_OPD_INPUT, "22")
        
        from selenium.webdriver.support.ui import Select
        select_element = admin_page.find(admin_page.Q_CORRECT_SELECT)
        Select(select_element).select_by_value("B")

        admin_page.click(admin_page.ADD_Q_BTN)
        time.sleep(1)

        assert admin_page.is_visible(admin_page.Q_ALERT)
        assert "success" in admin_page.get_text(admin_page.Q_ALERT).lower()
