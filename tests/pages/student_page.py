from selenium.webdriver.common.by import By
from .base_page import BasePage

class StudentPage(BasePage):
    URL = "http://localhost:5000/student-dashboard"

    TAB_EXAMS = (By.ID, "nav-exams")
    TAB_PROFILE = (By.ID, "nav-profile")

    # Profile Elements
    PROFILE_FULLNAME = (By.ID, "profile-fullname")
    PROFILE_STUDENTID = (By.ID, "profile-studentid")

    # Exam Session Elements
    EXAM_MODAL = (By.ID, "exam-session-modal")
    TIMER_DISPLAY = (By.ID, "timer-display")
    SUBMIT_EXAM_BTN = (By.ID, "btn-submit-exam")

    # Scorecard Elements
    SCORECARD_MODAL = (By.ID, "scorecard-modal")
    CARD_SCORE = (By.ID, "card-score")
    CARD_STATUS = (By.ID, "card-status")

    def open(self):
        self.driver.get(self.URL)

    def go_to_profile(self):
        self.click(self.TAB_PROFILE)

    def go_to_exams(self):
        self.click(self.TAB_EXAMS)

    def start_exam(self, exam_id=1):
        self.go_to_exams()
        btn = (By.ID, f"btn-start-exam-{exam_id}")
        self.click(btn)

    def select_option(self, question_id, option_letter='A'):
        opt_radio = (By.ID, f"q{question_id}-op-{option_letter}")
        self.click(opt_radio)

    def submit_exam(self):
        self.click(self.SUBMIT_EXAM_BTN)
        # Handle browser JavaScript confirm dialog if present
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
        except:
            pass
