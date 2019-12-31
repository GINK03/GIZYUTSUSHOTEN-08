
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from hashlib import sha224
from pathlib import Path
import random
import json
def hashing(url):
    x = sha224(bytes(url, 'utf8')).hexdigest()
    return x


def parallel(arg):
    try:
        url = arg
        print(url)
        r = requests.get(url)
        soup = BeautifulSoup(r.text)
        
        x = hashing(url)
        if Path(f'html_labels/{x}').exists():
            return set()

        hrefs = set()
        for img in soup.find_all('img', {'src':True}):
            src = img.get('src')
            if 'https://images.unsplash.com/' in src:
                p = urlparse(src)
                p = p._replace(query='')
                src = p.geturl()
                print(src)
                name = hashing(src)
                if Path(f'imgs/{name}.jpg').exists():
                    continue
                r = requests.get(src)
                binary = r.content
                with open(f'imgs/{name}.jpg', 'wb') as fp:
                    fp.write(binary)
        for a in soup.find_all('a', {'href':True}):
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
        
        # 終了ラベル
        x = hashing(url)
        if random.random() <= 0.8:
            Path(f'html_labels/{x}').touch()
        else:
            fp = Path(f'html_labels/{x}').open('w')
            json.dump(list(hrefs), fp)
        return hrefs
    except Exception as exc:
        print('exc', exc)
        return set()
from concurrent.futures import ProcessPoolExecutor as PPE
urls = ['https://unsplash.com/']
while True:
    nexts = set()
    with PPE(max_workers=16) as exe:
        #for url in urls:
        #        nexts |= parallel(url)
        for hrefs in exe.map(parallel, urls):
            nexts |= hrefs
    urls = list(nexts)
