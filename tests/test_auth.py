import time
import pytest
from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from pages.reset_password_page import ResetPasswordPage

class TestAuthentication:

    def test_01_valid_student_login(self, driver):
        """TC-AUTH-01: Verify valid student login redirects to student dashboard."""
        login_page = LoginPage(driver)
        login_page.open()
        login_page.login("alice1", "Student@123")
        time.sleep(1.5)
        assert "/student-dashboard" in driver.current_url

    def test_02_valid_admin_login(self, driver):
        """TC-AUTH-02: Verify valid admin login redirects to admin dashboard."""
        login_page = LoginPage(driver)
        login_page.open()
        login_page.login("admin", "Admin@123")
        time.sleep(1.5)
        assert "/admin-dashboard" in driver.current_url

    def test_03_invalid_username(self, driver):
        """TC-AUTH-03: Verify login with invalid username displays generic error message."""
        login_page = LoginPage(driver)
        login_page.open()
        login_page.login("non_existent_user", "Student@123")
        time.sleep(1)
        assert "Invalid credentials" in login_page.get_error_message()

    def test_04_invalid_password(self, driver):
        """TC-AUTH-04: Verify login with invalid password displays generic error message."""
        login_page = LoginPage(driver)
        login_page.open()
        login_page.login("alice1", "WrongPassword123!")
        time.sleep(1)
        assert "Invalid credentials" in login_page.get_error_message()

    def test_05_empty_login_fields(self, driver):
        """TC-AUTH-05: Verify submitting empty login form shows validation error."""
        login_page = LoginPage(driver)
        login_page.open()
        login_page.login("", "")
        time.sleep(0.5)
        assert login_page.is_visible(login_page.ERROR_ALERT)

    def test_06_blocked_student_login(self, driver):
        """TC-AUTH-06: Verify blocked student account cannot log in."""
        login_page = LoginPage(driver)
        login_page.open()
        login_page.login("charlie3", "Student@123")
        time.sleep(1)
        assert "blocked" in login_page.get_error_message().lower()

    def test_07_valid_registration(self, driver):
        """TC-REG-01: Verify new student registration with valid data succeeds."""
        reg_page = RegisterPage(driver)
        reg_page.open()
        timestamp = int(time.time())
        username = f"testuser_{timestamp}"
        email = f"test_{timestamp}@student.com"
        student_id = f"STU_{timestamp}"

        reg_page.fill_form(
            full_name="Test Student",
            student_id=student_id,
            email=email,
            phone="9988776655",
            username=username,
            password="NewPassword123",
            confirm_password="NewPassword123",
            course_id="1",
            dob="2000-01-01"
        )
        reg_page.submit()
        time.sleep(2)
        assert reg_page.is_visible(reg_page.SUCCESS_ALERT)

    def test_08_registration_duplicate_username(self, driver):
        """TC-REG-02: Verify registering with an existing username fails."""
        reg_page = RegisterPage(driver)
        reg_page.open()
        reg_page.fill_form(
            full_name="Duplicate User",
            student_id="STU9999",
            email="unique_email@student.com",
            phone="9988776655",
            username="alice1", # Existing username
            password="Password123",
            confirm_password="Password123",
            course_id="2",
            dob="2000-01-01"
        )
        reg_page.submit()
        time.sleep(1)
        assert reg_page.is_visible(reg_page.ERROR_ALERT)

    def test_09_registration_password_mismatch(self, driver):
        """TC-REG-03: Verify registering with mismatched passwords shows error."""
        reg_page = RegisterPage(driver)
        reg_page.open()
        reg_page.fill_form(
            full_name="Mismatch User",
            student_id="STU8888",
            email="mismatch@student.com",
            phone="9988776655",
            username="mismatch_user",
            password="Password123",
            confirm_password="DifferentPassword123",
            course_id="1",
            dob="2000-01-01"
        )
        reg_page.submit()
        time.sleep(0.5)
        assert reg_page.is_visible(reg_page.ERROR_ALERT)

    def test_10_registration_underage_dob(self, driver):
        """TC-REG-04: Verify student registration fails if student age is < 15 years."""
        reg_page = RegisterPage(driver)
        reg_page.open()
        reg_page.fill_form(
            full_name="Young Student",
            student_id="STU7777",
            email="young@student.com",
            phone="9988776655",
            username="young_student",
            password="Password123",
            confirm_password="Password123",
            course_id="1",
            dob="2020-01-01" # Underage date
        )
        reg_page.submit()
        time.sleep(0.5)
        assert reg_page.is_visible(reg_page.ERROR_ALERT)

    def test_11_password_reset_flow(self, driver):
        """TC-RESET-01: Verify requesting password reset generates demo link and resets password."""
        reset_page = ResetPasswordPage(driver)
        reset_page.open_forgot_password()
        reset_page.request_reset("alice@student.com")
        time.sleep(1.5)
        
        # Click the generated demo reset link
        reset_page.click_demo_reset_link()
        time.sleep(1)
        assert "/reset-password" in driver.current_url

        # Perform password reset
        reset_page.perform_reset("NewAlicePass123", "NewAlicePass123")
        time.sleep(2.5)
        assert "/login" in driver.current_url

    def test_12_logout_flow(self, driver):
        """TC-AUTH-07: Verify logging out clears session and redirects to login."""
        login_page = LoginPage(driver)
        login_page.open()
        login_page.login("alice1", "Student@123") # Or new pass if reset
        time.sleep(1.5)
        
        # Click logout
        from selenium.webdriver.common.by import By
        driver.find_element(By.ID, "logout-btn").click()
        time.sleep(1)
        assert "/login" in driver.current_url
