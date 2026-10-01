from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .base_page import BasePage

class RegisterPage(BasePage):
    URL = "http://localhost:5000/register"

    FULLNAME_INPUT = (By.ID, "register-fullname")
    STUDENTID_INPUT = (By.ID, "register-studentid")
    EMAIL_INPUT = (By.ID, "register-email")
    PHONE_INPUT = (By.ID, "register-phone")
    USERNAME_INPUT = (By.ID, "register-username")
    PASSWORD_INPUT = (By.ID, "register-password")
    CONFIRM_PASSWORD_INPUT = (By.ID, "register-confirm-password")
    COURSE_SELECT = (By.ID, "register-course")
    DOB_INPUT = (By.ID, "register-dob")
    REGISTER_BTN = (By.ID, "register-btn")
    ERROR_ALERT = (By.ID, "register-error")
    SUCCESS_ALERT = (By.ID, "register-success")

    # Field errors
    ERR_FULLNAME = (By.ID, "err-full_name")
    ERR_STUDENTID = (By.ID, "err-student_id")
    ERR_EMAIL = (By.ID, "err-email")
    ERR_PHONE = (By.ID, "err-phone")
    ERR_USERNAME = (By.ID, "err-username")
    ERR_PASSWORD = (By.ID, "err-password")
    ERR_CONFIRM = (By.ID, "err-confirm_password")
    ERR_COURSE = (By.ID, "err-course_id")
    ERR_DOB = (By.ID, "err-dob")

    def open(self):
        self.driver.get(self.URL)

    def select_course(self, course_value="3"):
        select_element = self.find(self.COURSE_SELECT)
        select = Select(select_element)
        select.select_by_value(str(course_value))

    def fill_form(self, full_name="", student_id="", email="", phone="", username="", password="", confirm_password="", course_id="3", dob="2001-05-15"):
        if full_name: self.type(self.FULLNAME_INPUT, full_name)
        if student_id: self.type(self.STUDENTID_INPUT, student_id)
        if email: self.type(self.EMAIL_INPUT, email)
        if phone: self.type(self.PHONE_INPUT, phone)
        if username: self.type(self.USERNAME_INPUT, username)
        if password: self.type(self.PASSWORD_INPUT, password)
        if confirm_password: self.type(self.CONFIRM_PASSWORD_INPUT, confirm_password)
        if course_id: self.select_course(course_id)
        if dob: self.type(self.DOB_INPUT, dob)

    def submit(self):
        self.click(self.REGISTER_BTN)

    def get_error_message(self):
        return self.get_text(self.ERROR_ALERT)

    def get_success_message(self):
        return self.get_text(self.SUCCESS_ALERT)
