import time
import pytest
from pages.login_page import LoginPage
from pages.student_page import StudentPage

class TestStudentModule:

    @pytest.fixture(autouse=True)
    def student_login(self, driver):
        """Helper fixture to log in as student before each test."""
        login_page = LoginPage(driver)
        login_page.open()
        login_page.login("alice1", "Student@123")
        time.sleep(1.5)
        assert "/student-dashboard" in driver.current_url

    def test_01_student_profile_view(self, driver):
        """TC-STU-01: Verify student profile details render correctly."""
        student_page = StudentPage(driver)
        student_page.go_to_profile()
        time.sleep(1)

        fullname = student_page.get_text(student_page.PROFILE_FULLNAME)
        student_id = student_page.get_text(student_page.PROFILE_STUDENTID)

        assert "Alice Smith" in fullname
        assert "STU001" in student_id

    def test_02_published_exams_catalog_visibility(self, driver):
        """TC-STU-02: Verify only published exams are visible in the catalog."""
        student_page = StudentPage(driver)
        student_page.go_to_exams()
        time.sleep(1)

        from selenium.webdriver.common.by import By
        # Published Exam 1 ("Software Testing Fundamentals") should be visible
        assert len(driver.find_elements(By.ID, "btn-start-exam-1")) > 0

        # Unpublished Exam 3 ("Advanced Cybersecurity Concepts") should NOT be visible
        assert len(driver.find_elements(By.ID, "btn-start-exam-3")) == 0

    def test_03_start_exam_and_timer_display(self, driver):
        """TC-STU-03: Verify starting an exam launches the fullscreen session and live timer."""
        student_page = StudentPage(driver)
        student_page.start_exam(exam_id=2) # Exam 2: Database Systems Midterm
        time.sleep(1.5)

        assert student_page.is_visible(student_page.EXAM_MODAL)
        timer_text = student_page.get_text(student_page.TIMER_DISPLAY)
        assert ":" in timer_text # e.g. "20:00"

    def test_04_select_answers_and_submit_exam(self, driver):
        """TC-STU-04: Verify answering MCQs, submitting exam, and receiving instant scorecard."""
        student_page = StudentPage(driver)
        student_page.start_exam(exam_id=2)
        time.sleep(1.5)

        # Select answers for questions
        student_page.select_option(question_id=11, option_letter='A')
        student_page.select_option(question_id=12, option_letter='A')
        student_page.select_option(question_id=13, option_letter='B')

        student_page.submit_exam()
        time.sleep(2)

        assert student_page.is_visible(student_page.SCORECARD_MODAL)
        score_text = student_page.get_text(student_page.CARD_SCORE)
        assert "/" in score_text
        status_text = student_page.get_text(student_page.CARD_STATUS)
        assert status_text in ["PASS", "FAIL"]

    def test_05_single_attempt_rule_enforcement(self, driver):
        """TC-STU-05: Verify student cannot re-attempt an already submitted exam."""
        student_page = StudentPage(driver)
        student_page.go_to_exams()
        time.sleep(1)

        from selenium.webdriver.common.by import By
        # Exam 2 was completed in test_04, so start button for exam 2 should now be disabled/completed badge
        exam_2_btn = driver.find_elements(By.ID, "btn-start-exam-2")
        assert len(exam_2_btn) == 0 # Start button no longer present; replaced by Completed badge
