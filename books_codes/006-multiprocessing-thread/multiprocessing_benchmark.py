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
from hashlib import sha224

def get_digest(x):
    return sha224(bytes(x,'utf8')).hexdigest()[:16]

def process(arg):
    try:
        url = arg
        with requests.get(url, timeout=5.0) as r:
            header = r.headers
            html = r.text
        if 'text/html' not in header.get('Content-Type'):
            return set()
        soup = BeautifulSoup(html, 'lxml')
        hrefs = set()
        for a in soup.find_all('a', {'href': True}):
            hrefs.add(a.get('href'))
        Path(f'logs/{get_digest(url)}').touch()
        return hrefs
    except Exception as exc:
        #print(exc)
        return set()

# ベンチマークに使うURLをlistで保存したjson
with open('urls.json') as fp:
    urls = json.load(fp)
NUM = 256
print('total uniq domain(netloc) url size is', len(urls))
start = time.time()
hrefs = set()
#[process(url) for url in urls]
with ProcessPoolExecutor(max_workers=NUM) as exe:
    for child_hrefs in tqdm(exe.map(process, urls), total=len(urls)):
        hrefs |= child_hrefs

print(f'total result urls = {len(hrefs)}')
elapsed = time.time() - start
print(f'elapsed time {elapsed}')
