
import requests
import glob
import re
from bs4 import BeautifulSoup
from multiprocessing.managers import BaseManager as Manager
import os
import sys
import random
from hashlib import sha224
from pathlib import Path
from urllib.parse import urlparse
import gzip
from tqdm import tqdm

def get_digest(x):
    return sha224(bytes(x, 'utf8')).hexdigest()[:16]


# インメモリのKVSを想定
k_vs = {}


def get():
    while True:
        k = random.choice(list(k_vs.keys()))
        if len(k_vs[k]) == 0:
            del k_vs[k]
        else:
            break

    v = random.choice(list(k_vs[k]))
    k_vs[k] -= set([v])
    return v


def put(urls):
    for url in urls:
        o = urlparse(url)
        o = o._replace(params='', query='')
        url = o.geturl()
        digest = get_digest(url)
        if Path(f'htmls/{digest}').exists():
            continue
        netloc = o.netloc
        if netloc not in k_vs:
            k_vs[netloc] = set()
        k_vs[netloc].add(url)


def finish(url, html):
    o = urlparse(url)
    o = o._replace(params='', query='')
    url = o.geturl()
    digest = get_digest(url)
    print('finish', url, digest)
    with open(f'htmls/{digest}', 'wb') as fp:
        fp.write(gzip.compress(bytes(html, 'utf8')))

# test
if '--test' in sys.argv:
    put(['https://www.yahoo.co.jp/'])
    for i in range(10):
        url = get()
        with requests.get(url) as r:
            html = r.text
        soup = BeautifulSoup(html, 'html5lib')
        urls = set()
        for a in soup.find_all('a', {'href': re.compile(r'^https://')}):
            urls.add(a.get('href'))
        finish(url, html)
        put(urls)
    exit()

if __name__ == "__main__":
    if '--init' in sys.argv:
        for fn in tqdm(glob.glob('htmls/*')):
            html = gzip.decompress(open(fn, 'rb').read())
            soup = BeautifulSoup(html, 'html5lib')
            urls = set()
            for a in soup.find_all('a', {'href': re.compile(r'^https://')}):
                urls.add(a.get('href'))
            put(urls)

    port_num = 4343
    Manager.register("get", get)  # 待受に使う関数を登録
    Manager.register("put", put)
    Manager.register("finish", finish)
    manager = Manager(("", port_num), authkey=b"password")  # ホスト名を空白にすることで任意の箇所から命令を受け入れられる。パスワードが設定できる
    manager.start()
    input("Press any key to kill server".center(50, "-"))  # なにか入力したら終了
    manager.shutdown()
