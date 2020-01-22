import requests
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor as PPE
from concurrent.futures import ThreadPoolExecutor as TPE
from urllib.parse import urlparse
from hashlib import sha224
from pathlib import Path
from multiprocessing import Process, Manager
import random
import json
import glob
from tqdm import tqdm
from itertools import count

def hashing(x):
    ret = sha224(bytes(x, 'utf8')).hexdigest()[:24]
    return ret

def push_ssd(url):
    p = urlparse(url)
    netloc = p.netloc
    key = hashing(url)
    if not Path(f'htmls/{netloc}/{key}').exists():
        Path(f'links/{netloc}').mkdir(exist_ok=True, parents=True)
        with open(f'links/{netloc}/{key}', 'w') as fp:
            fp.write(url)
import shutil
def get_fairness_ssd():

    for trial in count(0):
        try:
            netlocs = glob.glob('links/*')
            #print(netlocs)
            netloc = random.sample(netlocs, 1).pop()
            keys = glob.glob(f'{netloc}/*')
            if len(keys) == 0:
                shutil.rmtree(netloc)
                raise Exception("非同期制御失敗")
            break
        except Exception as exc:
            print(exc)
    #print(keys)
    key = random.sample(keys, 1).pop()
    with open(key, 'r') as fp:
        url = fp.read()
    Path(key).unlink()
    if len(keys) == 1:
        shutil.rmtree(netloc)
    
    return url

def run(arg):
    i = arg
    
    url = get_fairness_ssd()
    mst_p = urlparse(url)
    mst_netloc = mst_p.netloc
    group_key = mst_netloc 
    key = sha224(bytes(url, 'utf8')).hexdigest()[:24]
    if Path(f'htmls/{group_key}/{key}').exists():
        return 
    if Path(f'errs/{group_key}/{key}').exists():
        return
    try:
        print(url)
        r = requests.get(url, timeout=30)

        mst_scheme = mst_p.scheme
        soup = BeautifulSoup(r.text, 'html5lib')

        next_urls = set()
        for tag in soup.find_all('a', {'href': True}):
            href = tag.get('href')
            if 'javascript' in href:
                continue
            p = urlparse(href)
            if p.netloc == '':
                p = p._replace(scheme=mst_scheme, netloc=mst_netloc)

            p = p._replace(params='')
            p = p._replace(query='')
            #print('push', p.geturl())
            push_ssd(p.geturl())         

        Path(f'htmls/{group_key}').mkdir(exist_ok=True, parents=True)
        with open(f'htmls/{group_key}/{key}', 'w') as fp:
            fp.write(r.text)

    except Exception as exc:
        print(exc)
        Path(f'errs/{group_key}').mkdir(exist_ok=True, parents=True)
        Path(f'errs/{group_key}/{key}').touch()


push_ssd(url='https://news.yahoo.co.jp/pickup/6348616')
for depth in count(0):
    next_urls = set()
    with PPE(max_workers=32) as exe:
        for r in exe.map(run, [i for i in range(100000)]):
            r
