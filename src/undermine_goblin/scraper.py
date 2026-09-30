import time

from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=False, executable_path="/usr/bin/chromium-browser"
    )

    page = browser.new_page()
    page.goto("https://undermine.exchange/")

    print("The page has been loaded")

    time.sleep(5)

    browser.close()
