# ファイルシステムベースのKVSの例
import gzip
import pickle
from pathlib import Path
from collections import namedtuple
from itertools import count
import requests
import random
from hashlib import sha224
from concurrent.futures import ProcessPoolExecutor

Path('db').mkdir(exist_ok=True)
Datum = namedtuple('Datum', ['depth', 'domain', 'html', 'links'])


def flash(url, datum):
    # keyとなるurlのhash値を計算(長過ぎるのトリムする)
    key = sha224(bytes(url, 'utf8')).hexdigest()[:24]
    # valueとなるDatum型のシリアライズと圧縮
    value = gzip.compress(pickle.dumps(datum))

    # db/にhash値のファイル名で書き込む
    with open(f'db/{key}', 'wb') as fp:
        fp.write(value)


def isExists(url):
    # keyとなるurlのhash値を計算(長過ぎるのトリムする)
    key = sha224(bytes(url, 'utf8')).hexdigest()[:24]
    # もし、キーとなるファイルが存在していたら、それは過去にスクレイピングしたURLである
    if Path(f'db/{key}').exists():
        return True
    else:
        return False

def parallel(arg):
    url, depth = arg
    if isExists(url) is True:
        return
    depth = 1
    dummy_html = '<html> dummy </html>'
    dummy_domain = 'example.com'
    dummy_links = ['1', '2', '3']
    datum = Datum(depth=depth, domain=dummy_domain, html=dummy_html, links=dummy_links)
    flash(url, datum)

dummy_urls = [f'{k:04d}' for k in range(1000)]
# ランダムなURLをスクレイピングしたとする
dummy_urls = [(random.choice(dummy_urls), i) for i in range(10000)]
with ProcessPoolExecutor(max_workers=8) as exe:
    exe.map(parallel, dummy_urls)
