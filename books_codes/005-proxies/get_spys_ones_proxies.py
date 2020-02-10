from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time
import re
import requests
from bs4 import BeautifulSoup
import json

options = Options()
options.add_argument("--headless")
options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
)
options.add_argument(f"user-data-dir=/tmp/work")
options.add_argument("lang=ja")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1080,10800")
driver = webdriver.Chrome(options=options, executable_path="/usr/bin/chromedriver")

proxies = set()
for proxy_src in [
    "http://spys.one/free-proxy-list/JP/",
    "http://spys.one/en/free-proxy-list/",
]:
    driver.get("http://spys.one/en/free-proxy-list/")
    time.sleep(1.0)
    driver.find_element_by_xpath("//select[@name='xpp']/option[@value='5']").click()
    time.sleep(1.0)
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    [s.extract() for s in soup("script")]
    # print(soup.title.text)
    for tr in soup.find_all("tr"):
        if len(tr.find_all("td")) == 10:
            tds = tr.find_all("td")
            ip_port = tds[0].text.strip()
            protocol = re.sub(r"\(.*?\)", "", tds[1].text.strip()).lower().strip()
            proxy = f"{protocol}://{ip_port}"
            proxies.add(proxy)
proxies = list(proxies)

with open("proxies.json", "w") as fp:
    json.dump(proxies, fp, indent=2)
