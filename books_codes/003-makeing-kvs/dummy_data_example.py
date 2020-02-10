# ファイルシステムベースのKVSの例
import gzip
import pickle
from pathlib import Path
from collections import namedtuple
from itertools import count
import requests
import random
from hashlib import sha224

Path("db").mkdir(exist_ok=True)
Datum = namedtuple("Datum", ["depth", "domain", "html", "links"])


def get_digest(url):
    return sha224(bytes(url, "utf8")).hexdigest()[:24]


def flash(url, datum):
    # keyとなるurlのhash値を計算
    key = get_digest(url)
    # valueとなるDatum型のシリアライズと圧縮
    value = gzip.compress(pickle.dumps(datum))
    # dbフォルダーにhash値のファイル名で書き込む
    with open(f"db/{key}", "wb") as fp:
        fp.write(value)


def isExists(url):
    # keyとなるurlのhash値を計算
    key = get_digest(url)
    # もし、キーとなるファイルが存在していたら、それは過去にスクレイピングしたURLである
    if Path(f"db/{key}").exists():
        return True
    else:
        return False


# ランダムなURLをスクレイピングしたとする
dummy_urls = [f"{k:04d}" for k in range(1000)]
for i in range(10000):
    dummy_url = random.choice(dummy_urls)
    # すでにスクレイピングしていたURLならスキップする
    if isExists(dummy_url) is True:
        continue
    depth = 1
    dummy_html = "<html> dummy </html>"
    dummy_domain = "example.com"
    dummy_links = ["1", "2", "3"]
    datum = Datum(depth=depth, domain=dummy_domain, html=dummy_html, links=dummy_links)
    flash(dummy_url, datum)
