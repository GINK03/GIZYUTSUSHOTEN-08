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
import plyvel
Datum = namedtuple('Datum', ['depth', 'domain', 'html', 'links'])

db =  plyvel.DB('/tmp/db/', create_if_missing=True)
def flash(url, datum):
    # keyとなるurlのhash値を計算(長過ぎるのトリムする)
    key = sha224(bytes(url, 'utf8')).hexdigest()[:24]
    # valueとなるDatum型のシリアライズと圧縮
    value = gzip.compress(pickle.dumps(datum))
    with db.write_batch() as wb:
        wb.put(bytes(key, 'utf8'), value)


def isExists(url):
    key = sha224(bytes(url, 'utf8')).hexdigest()[:24]
    if db.get(bytes(key, 'utf8')) is not None:
        return True
    else:
        return False


def parallel(arg):
    url, depth = arg
    try:
        if isExists(url) is True:
            return
        depth = 1
        dummy_html = '<html> dummy </html>'
        dummy_domain = 'example.com'
        dummy_links = ['1', '2', '3']
        datum = Datum(depth=depth, domain=dummy_domain, html=dummy_html, links=dummy_links)
        flash(url, datum)
    except Exception as exc:
        print(exc)

dummy_urls = [f'{k:04d}' for k in range(1000)]
# ランダムなURLをスクレイピングしたとする
dummy_urls = [(random.choice(dummy_urls), i) for i in range(10000)]

with ProcessPoolExecutor(max_workers=8) as exe:
    exe.map(parallel, dummy_urls)

#for arg in dummy_urls:
#    parallel(arg)
for key, value in db.iterator():
    print(key)
'''
urls = ['https://www.yahoo.co.jp/']
for cnt in count(0):
    next_urls = set()
    for url in urls:
        r = requests
'''
