
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

def hashing(url):
    x = sha224(bytes(url, 'utf8')).hexdigest()
    return x

def parallel(arg):
    try:
        url = arg
        print(url)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html5lib')

        x = hashing(url)
        if Path(f'htmls/{x}').exists():
            return set()

        hrefs = set()
        for img in soup.find_all('img', {'src': True}):
            src = img.get('src')
            if 'https://images.unsplash.com/' in src:
                p = urlparse(src)
                p = p._replace(query='')
                src = p.geturl()
                name = hashing(src)
                #print('query removed url', src, 'hashing', name)
                if Path(f'imgs/{name}.jpg').exists():
                    continue
                r = requests.get(src)
                binary = r.content
                with open(f'imgs/{name}.jpg', 'wb') as fp:
                    fp.write(binary)
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

        x = hashing(url)
        with Path(f'links/{x}').open('w') as fp:
            json.dump(list(hrefs), fp, indent=2)
        with Path(f'htmls/{x}').open('wb') as fp:
            html = r.text
            ser = gzip.compress(bytes(html, 'utf8'))
            fp.write(ser)
        return hrefs

    except Exception as exc:
        print('exc', exc)
        return set()

urls = ['https://unsplash.com/']
for fn in glob.glob('./html_labels/*'):
    txt = open(fn).read()
    if txt != '':
        urls += json.loads(txt)
while True:
    nexts = set()
    with PPE(max_workers=16) as exe:
        # for url in urls:
        #        nexts |= parallel(url)
        for hrefs in exe.map(parallel, urls):
            nexts |= hrefs
        if len(nexts) == 0:
            raise Exception('somethins wrong.')
    urls = list(nexts)

    if len(urls) == 0:
        urls = set()
        for fn in tqdm(glob.glob('links/*')):
            urls |= set(json.loads(open(fn)))
        urls = list(urls)
