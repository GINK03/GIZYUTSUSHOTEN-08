#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re

def main():
    r = requests.get('https://yahoo.co.jp')
    html = r.text
    soup = BeautifulSoup(html)
    for a in soup.find_all('a', {'href':re.compile('https://news.yahoo.co.jp*')}):
        news_title = a.text
        link = a['href']
        print(news_title, link)
if __name__ == '__main__':
    main()
