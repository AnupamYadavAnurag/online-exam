from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .base_page import BasePage

class AdminPage(BasePage):
    URL = "http://localhost:5000/admin-dashboard"

    # Navigation Tabs
    TAB_OVERVIEW = (By.ID, "nav-overview")
    TAB_STUDENTS = (By.ID, "nav-students")
    TAB_COURSES = (By.ID, "nav-courses")
    TAB_EXAMS = (By.ID, "nav-exams")

    # Overview Stats Elements
    STAT_STUDENTS = (By.ID, "stat-students")
    STAT_BLOCKED = (By.ID, "stat-blocked")
    STAT_COURSES = (By.ID, "stat-courses")
    STAT_EXAMS = (By.ID, "stat-exams")
    STAT_PUBLISHED = (By.ID, "stat-published")

    # Course Form Inputs
    COURSE_CODE_INPUT = (By.ID, "course-code")
    COURSE_NAME_INPUT = (By.ID, "course-name")
    COURSE_DEPT_SELECT = (By.ID, "course-dept")
    ADD_COURSE_BTN = (By.ID, "btn-add-course")
    COURSE_ALERT = (By.ID, "course-form-alert")

    # Exam Form Inputs
    EXAM_TITLE_INPUT = (By.ID, "exam-title")
    EXAM_COURSE_SELECT = (By.ID, "exam-course")
    EXAM_DURATION_INPUT = (By.ID, "exam-duration")
    EXAM_MARKS_INPUT = (By.ID, "exam-marks")
    CREATE_EXAM_BTN = (By.ID, "btn-create-exam")
    EXAM_ALERT = (By.ID, "exam-form-alert")
    ERR_DURATION = (By.ID, "err-duration_minutes")

    # Question Modal Inputs
    Q_TEXT_INPUT = (By.ID, "q-text")
    Q_OPA_INPUT = (By.ID, "q-op-a")
    Q_OPB_INPUT = (By.ID, "q-op-b")
    Q_OPC_INPUT = (By.ID, "q-op-c")
    Q_OPD_INPUT = (By.ID, "q-op-d")
    Q_CORRECT_SELECT = (By.ID, "q-correct")
    ADD_Q_BTN = (By.ID, "btn-add-question")
    Q_ALERT = (By.ID, "q-form-alert")

    def open(self):
        self.driver.get(self.URL)

    def go_to_students(self):
        self.click(self.TAB_STUDENTS)

    def go_to_courses(self):
        self.click(self.TAB_COURSES)

    def go_to_exams(self):
        self.click(self.TAB_EXAMS)

    def create_course(self, code, name, dept_id="1"):
        self.go_to_courses()
        self.type(self.COURSE_CODE_INPUT, code)
        self.type(self.COURSE_NAME_INPUT, name)
        
        select_element = self.find(self.COURSE_DEPT_SELECT)
        select = Select(select_element)
        select.select_by_value(str(dept_id))

        self.click(self.ADD_COURSE_BTN)

    def create_exam(self, title, course_id="1", duration="15", marks="10"):
        self.go_to_exams()
        self.type(self.EXAM_TITLE_INPUT, title)
        
        select_element = self.find(self.EXAM_COURSE_SELECT)
        select = Select(select_element)
        select.select_by_value(str(course_id))

        self.type(self.EXAM_DURATION_INPUT, duration)
        self.type(self.EXAM_MARKS_INPUT, marks)
        self.click(self.CREATE_EXAM_BTN)
