from selene import browser

BASE_URL = "https://demowebshop.tricentis.com"


def pytest_sessionstart(session):
    browser.config.base_url = BASE_URL
    browser.config.window_width = 1920
    browser.config.window_height = 1080