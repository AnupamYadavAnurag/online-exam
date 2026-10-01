from selenium.webdriver.common.by import By
from .base_page import BasePage

class ResetPasswordPage(BasePage):
    FORGOT_URL = "http://localhost:5000/forgot-password"

    FORGOT_EMAIL_INPUT = (By.ID, "forgot-email")
    FORGOT_BTN = (By.ID, "forgot-btn")
    FORGOT_MSG = (By.ID, "forgot-msg")
    DEMO_RESET_LINK = (By.ID, "demo-reset-link")

    RESET_PASSWORD_INPUT = (By.ID, "reset-password")
    RESET_CONFIRM_INPUT = (By.ID, "reset-confirm")
    RESET_BTN = (By.ID, "reset-btn")
    RESET_MSG = (By.ID, "reset-msg")

    def open_forgot_password(self):
        self.driver.get(self.FORGOT_URL)

    def request_reset(self, email):
        self.type(self.FORGOT_EMAIL_INPUT, email)
        self.click(self.FORGOT_BTN)

    def click_demo_reset_link(self):
        self.click(self.DEMO_RESET_LINK)

    def perform_reset(self, new_password, confirm_password):
        self.type(self.RESET_PASSWORD_INPUT, new_password)
        self.type(self.RESET_CONFIRM_INPUT, confirm_password)
        self.click(self.RESET_BTN)

    def get_reset_message(self):
        return self.get_text(self.RESET_MSG)
