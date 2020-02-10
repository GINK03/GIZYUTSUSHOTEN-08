
from concurrent.futures import ProcessPoolExecutor as PPE
import glob
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from hashlib import sha224
from pathlib import Path
import random 
import json
import gzip
from tqdm import tqdm

import re
from multiprocessing import Process, Manager
import time

manager = Manager()
shared_d = manager.dict({'requests':0, 'bs4':0, 'img_dl':0, 'href':0 })

def hashing(url):
    if isinstance(url, str):
        x = sha224(bytes(url, 'utf8')).hexdigest()[:16]
        return x
    elif isinstance(url, bytes):
        x = sha224(url).hexdigest()[:16]
        return x

def parallel(arg):
    try:
        url = arg
        mst_p = urlparse(url)

        mst_p = mst_p._replace(query='')
        url = mst_p.geturl()
        
        mst_x = hashing(url)
        if Path(f'htmls/{mst_x}').exists():
            return set()

        print(url)
        start = time.time()
        with requests.get(url, timeout=60) as r:
            html = r.text
        shared_d['requests'] += time.time() - start 

        start = time.time()
        soup = BeautifulSoup(html, 'lxml')
        shared_d['bs4'] += time.time() - start 


        start = time.time()
        for img in soup.find_all('img', {'alt':True}):
            src = img.get('src')
            alt = img.get('alt')
            p = urlparse(src)
            p = p._replace(query='')
            src = p.geturl()
            digest = hashing(src)
            if Path(f'imgs/{digest}.jpg').exists():
                continue
            print('try download', src, alt, 'at', url)
            with requests.get(src, timeout=30) as r:
                binary = r.content
            with open(f'imgs/{digest}.jpg', 'wb') as fp:
                fp.write(binary)
        shared_d['img_dl'] += time.time() - start 

        start = time.time()
        hrefs = set()
        for a in soup.find_all('a', {'href': True}):
            href = a.get('href')
            try:
                if href[0] == '/' or 'https://unsplash.com' in href:
                    if href[0] == '/':
                        href = 'https://unsplash.com' + href
                    hrefs.add(href)
                else:
                    continue
            except Exception as exc:
                print(exc)
        shared_d['href'] += time.time() - start 

        x = hashing(url)
        with Path(f'links/{x}').open('w') as fp:
            json.dump(list(hrefs), fp, indent=2)
        with Path(f'htmls/{x}').open('wb') as fp:
            ser = gzip.compress(bytes(html, 'utf8'))
            fp.write(ser)

        print(shared_d)
        return hrefs

    except Exception as exc:
        print('exc', exc, url)
        return set()

urls = ['https://unsplash.com/photos/D1IS5s5O9xo']

[parallel(url) for url in urls]
while True:
    nexts = set()
    with PPE(max_workers=16) as exe:
        for hrefs in exe.map(parallel, urls):
            nexts |= hrefs

    if len(nexts) == 0:
        nexts = set()
        for fn in tqdm(glob.glob('links/*')):
            try:
                with open(fn) as fp:
                    nexts |= set(json.load(fp))
            except:
                continue
        urls = list(nexts)
    else:
        urls = list(nexts)
