# pixiv example only requests
import requests
from bs4 import BeautifulSoup

r = requests.get('https://www.pixiv.net/artworks/75863105')
soup = BeautifulSoup(r.text, 'html5lib')
for div in soup.find_all('div'):
    print(div)
