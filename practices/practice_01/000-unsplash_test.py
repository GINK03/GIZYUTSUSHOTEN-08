
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
<<<<<<< HEAD
=======
import re
from multiprocessing import Process, Manager
import time

manager = Manager()
shared_d = manager.dict({'requests':0, 'bs4':0, 'img_dl':0, 'href':0 })
>>>>>>> a97fd00cb89a85cbbb93b40984bf5933964ba71c

def hashing(url):
    x = sha224(bytes(url, 'utf8')).hexdigest()[:16]
    return x

def parallel(arg):
    try:
        url = arg
        mst_p = urlparse(url)

        mst_p = mst_p._replace(query='')
        url = mst_p.geturl()
        if re.search('download$', url):
            return set()
        if 'https://unsplash.com/photos' not in url:
            return set()

        print(url)
        start = time.time()
        with requests.get(url) as r:
            html = r.text
        shared_d['requests'] += time.time() - start 

        start = time.time()
        soup = BeautifulSoup(html, 'lxml')
        shared_d['bs4'] += time.time() - start 

        mst_x = hashing(url)
        if Path(f'htmls/{mst_x}').exists():
            return set()

        start = time.time()
        for img in soup.find_all('img', {'src': re.compile('https://images.unsplash.com/photo'), 'alt':True}):
            src = img.get('src')
            alt = img.get('alt')
            p = urlparse(src)
            p = p._replace(query='')
            src = p.geturl()
            name = hashing(src)
            #print('query removed url', src, 'hashing', name)
            if Path(f'imgs/{mst_x}/{name}.jpg').exists():
                continue
            print('try download', src, alt, 'at', url)
            with requests.get(src) as r:
                binary = r.content
            Path(f'imgs/{mst_x}').mkdir(exist_ok=True, parents=True)
            with open(f'imgs/{mst_x}/{name}.jpg', 'wb') as fp:
                fp.write(binary)
            with open(f'imgs/{mst_x}/{name}.txt', 'w') as fp:
                fp.write(alt)
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
while True:
    nexts = set()
    with PPE(max_workers=128) as exe:
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
