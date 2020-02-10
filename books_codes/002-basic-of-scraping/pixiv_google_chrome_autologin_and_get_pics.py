import os
import shutil
from bs4 import BeautifulSoup
import time
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

HOME = os.environ["HOME"]
EMAIL = os.environ["EMAIL"]
PASSWORD = os.environ["PASSWORD"]

target_url = "https://www.pixiv.net/artworks/75863105"
options = Options()
options.add_argument("--headless")
options.add_argument("window-size=2024x2024")
options.add_argument(f"user-data-dir=work_dir")
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

driver = webdriver.Chrome(executable_path=shutil.which("chromedriver"), options=options)
if not Path("init_chrome").exists():
    driver.get("https://accounts.pixiv.net/login")
    time.sleep(2.0)

    elm = driver.find_element_by_xpath("""//input[@autocomplete="username"]""")
    elm.click()
    elm.send_keys(EMAIL)
    elm = driver.find_element_by_xpath("""//input[@autocomplete="current-password"]""")
    elm.click()
    elm.send_keys(PASSWORD)
    time.sleep(1.0)
    elm = driver.find_element_by_xpath(
        """//div[@id='LoginComponent']//button[@class='signup-form__submit']"""
    )
    elm.click()
    time.sleep(5.0)
    Path("init_chrome").touch()

driver.get(target_url)  # ここでまみみのページがログイン状態を保存してアクセスしてほしい
time.sleep(5.0)
html = driver.page_source
soup = BeautifulSoup(html, "html5lib")
driver.save_screenshot(
    "pixiv_google_chrome_autologin_and_get_pics_screenshot.png"
)  # screenshotを取得する
