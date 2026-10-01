from selenium.webdriver.common.by import By
from .base_page import BasePage

class LoginPage(BasePage):
    URL = "http://localhost:5000/login"

    # Locators using exact stable IDs
    USERNAME_INPUT = (By.ID, "login-username")
    PASSWORD_INPUT = (By.ID, "login-password")
    REMEMBER_CHECKBOX = (By.ID, "login-remember")
    LOGIN_BTN = (By.ID, "login-btn")
    ERROR_ALERT = (By.ID, "login-error")
    SUCCESS_ALERT = (By.ID, "login-success")
    FORGOT_LINK = (By.ID, "forgot-password-link")
    REGISTER_LINK = (By.ID, "register-link")

    # Field specific error locators
    ERR_USERNAME = (By.ID, "err-username")
    ERR_PASSWORD = (By.ID, "err-password")

    def open(self):
        self.driver.get(self.URL)

    def login(self, username, password, remember=False):
        if username:
            self.type(self.USERNAME_INPUT, username)
        if password:
            self.type(self.PASSWORD_INPUT, password)
        if remember:
            self.click(self.REMEMBER_CHECKBOX)
        self.click(self.LOGIN_BTN)

    def get_error_message(self):
        return self.get_text(self.ERROR_ALERT)

    def get_success_message(self):
        return self.get_text(self.SUCCESS_ALERT)
