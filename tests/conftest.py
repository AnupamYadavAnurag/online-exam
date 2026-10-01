import os
import time
import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="session", autouse=True)
def reset_database_before_tests():
    """Resets database to fresh seed data before running the test suite."""
    try:
        res = requests.post(f"{BASE_URL}/api/test/reset", timeout=10)
        if res.status_code == 200:
            print("\n[OK] Test Database successfully reset to clean seed state.")
        else:
            print(f"\n[WARN] Database reset warning: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"\n[WARN] Could not connect to application server at {BASE_URL}. Ensure Flask app is running. Error: {e}")

@pytest.fixture(scope="function")
def driver(request):
    """Initializes Selenium Chrome WebDriver fixture with headless option."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") # Run in headless mode for CI/test automation
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        # Fallback to direct Chrome initialization
        driver = webdriver.Chrome(options=chrome_options)

    driver.implicitly_wait(5)
    
    yield driver

    # Take screenshot on test failure
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        screenshots_dir = os.path.join(os.path.dirname(__file__), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        screenshot_file = os.path.join(screenshots_dir, f"{request.node.name}.png")
        driver.save_screenshot(screenshot_file)
        print(f"\n[SCREENSHOT] Screenshot captured on failure: {screenshot_file}")

    driver.quit()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Pytest hook to capture test outcome for screenshot processing."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
