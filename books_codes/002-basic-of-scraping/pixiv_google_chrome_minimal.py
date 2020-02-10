# headless google-chromeの例
import os
import shutil
from bs4 import BeautifulSoup
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

HOME = os.environ["HOME"]
target_url = "https://www.pixiv.net/artworks/75863105"
options = Options()
options.add_argument("--headless")
options.add_argument("window-size=2024x2024")
options.add_argument(f"user-data-dir=work_dir")
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

driver = webdriver.Chrome(executable_path=shutil.which("chromedriver"), options=options)
driver.get(target_url)
time.sleep(5.0)
html = driver.page_source
soup = BeautifulSoup(html, "html5lib")
driver.save_screenshot("pixiv_google_chrome_minimal_screenshot.png")
