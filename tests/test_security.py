import time
import pytest
from pages.login_page import LoginPage
from pages.register_page import RegisterPage

class TestSecurityControls:

    def test_13_sqli_injection_attempt_in_login(self, driver):
        """TC-SEC-01: Verify SQL Injection payload in username/password field is mitigated by parameterized query."""
        login_page = LoginPage(driver)
        login_page.open()
        sqli_payload = "' OR '1'='1' --"
        login_page.login(sqli_payload, sqli_payload)
        time.sleep(1)
        # Should not bypass authentication, should show Invalid credentials
        assert "Invalid credentials" in login_page.get_error_message()
        assert "/login" in driver.current_url

    def test_14_xss_injection_attempt_in_registration(self, driver):
        """TC-SEC-02: Verify XSS payload script tags in registration inputs do not execute."""
        reg_page = RegisterPage(driver)
        reg_page.open()
        xss_payload = "<script>document.title='XSS_ATTACK'</script>"
        
        reg_page.fill_form(
            full_name=xss_payload,
            student_id="STUXSS01",
            email="xss_test@student.com",
            phone="9876543210",
            username="xss_user",
            password="Password123",
            confirm_password="Password123",
            course_id="1",
            dob="2000-01-01"
        )
        reg_page.submit()
        time.sleep(1.5)
        # Verify page title was NOT overwritten by XSS script execution
        assert driver.title != "XSS_ATTACK"

    def test_15_direct_url_access_student_dashboard_unauthenticated(self, driver):
        """TC-SEC-03: Verify unauthenticated user accessing student dashboard URL is redirected to login."""
        driver.get("http://localhost:5000/student-dashboard")
        time.sleep(1)
        assert "/login" in driver.current_url

    def test_16_direct_url_access_admin_dashboard_unauthenticated(self, driver):
        """TC-SEC-04: Verify unauthenticated user accessing admin dashboard URL is redirected to login."""
        driver.get("http://localhost:5000/admin-dashboard")
        time.sleep(1)
        assert "/login" in driver.current_url

    def test_17_student_cannot_access_admin_dashboard(self, driver):
        """TC-SEC-05: Verify authenticated student cannot access admin dashboard page."""
        login_page = LoginPage(driver)
        login_page.open()
        login_page.login("alice1", "Student@123") # Log in as student
        time.sleep(1.5)
        assert "/student-dashboard" in driver.current_url

        # Attempt to bypass role restriction by navigating directly to /admin-dashboard
        driver.get("http://localhost:5000/admin-dashboard")
        time.sleep(1)
        # Session role validation redirects student away from admin dashboard
        assert "/admin-dashboard" not in driver.current_url or "/login" in driver.current_url
