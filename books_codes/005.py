# headless google-chromeの例


import os  
import shutil
from selenium import webdriver  
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options  

options = Options()  
options.add_argument("--headless")  
options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

driver = webdriver.Chrome(executable_path=shutil.which('chromedriver'), chrome_options=options)  
driver.get('https://www.pixiv.net/artworks/78881202')

driver.implicitly_wait(1)

html = driver.page_source

print(html)
