import requests
from bs4 import BeautifulSoup
import time
import re
from collections import namedtuple

DepthUrl = namedtuple('DepthUrl', ['depth', 'url'])
urls = [DepthUrl(0, 'https://www.yahoo.co.jp/')]
all_urls = set()
flatten_urls = set('https://www.yahoo.co.jp/')
depth = 0
for I in range(3):
    depth += 1
    for depth_, url in urls:
        print('深さ', depth_, 'URL', url)
        try:
            with requests.get(url) as r:
                html = r.text
            soup = BeautifulSoup(html)
            for a in soup.find_all('a', {'href': re.compile(r'^https://.*?\.yahoo\.co\.jp')}):
                next_url = a.get('href')
                if next_url not in flatten_urls:
                    all_urls.add(DepthUrl(depth_+1, next_url))
        except Exception as exc:
            continue
        flatten_urls.add(url)
        all_urls -= {DepthUrl(depth_, url)}
    urls = sorted(all_urls, key=lambda x: x[0])
    min_depth = min([url.depth for url in urls])  # ここに注目
    urls = [url for url in urls if url.depth == min_depth]
