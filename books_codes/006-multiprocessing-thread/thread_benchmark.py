from urllib.parse import urlparse
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import random
import requests
import time
import json


def process(arg):
    try:
        url = arg
        print(url)
        r = requests.get(url, timeout=5.0)
        soup = BeautifulSoup(r.text, 'lxml')
        hrefs = set()
        for a in soup.find_all('a', {'href': True}):
            a.get('href')
        return hrefs
    except Exception as exc:
        return set()

# ベンチマークに使うURLをlistで保存したjson
with open('urls.json') as fp:
    urls = list(json.load(fp).values())
NUM = 256
print('total uniq domain(netloc) url size is', len(urls))
start = time.time()
hrefs = set()
with ThreadPoolExecutor(max_workers=NUM) as exe:
    for child_hrefs in tqdm(exe.map(process, urls), total=len(urls)):
        hrefs |= child_hrefs

print(f'total result urls = {len(hrefs)}')
elapsed = time.time() - start
print(f'elapsed time {elapsed}')
