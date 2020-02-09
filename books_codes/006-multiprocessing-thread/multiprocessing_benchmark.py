from urllib.parse import urlparse
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urlparse
from concurrent.futures import ProcessPoolExecutor  # <- ここをThreadPoolExecutorに変えればThreadのパフォーマンスがわかる
import random
import requests
import time
import json


def process(arg):
    try:
        url = arg
        print(url)
        r = requests.get(url, timeout=5.0)
        soup = BeautifulSoup(r.text, 'html5lib')
        hrefs = set()
        for a in soup.find_all('a', {'href': True}):
            a.get('href')
        return hrefs
    except Exception as exc:
        return set()

# ベンチマークに使うURLをlistで保存したjson
with open('urls.json') as fp:
    urls = json.load(fp)

print('total uniq domain(netloc) url size is', len(urls))
start = time.time()
hrefs = set()
with ProcessPoolExecutor(max_workers=16) as exe:
    for child_hrefs in exe.map(process, urls):
        hrefs |= child_hrefs
elapsed = time.time() - start
print(f'elapsed time {elapsed}')
