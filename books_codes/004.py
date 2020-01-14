# referrerを付ける例

import requests
import re
from bs4 import BeautifulSoup

headers = {'referer':'https://google.com', 
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}
r = requests.get('https://www.yahoo.co.jp/', headers=headers)
soup = BeautifulSoup(r.text, features='html5lib')
for img in soup.find_all('img'):
    print(img.get('src'))
