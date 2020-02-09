
from concurrent.futures import ProcessPoolExecutor 
from bs4 import BeautifulSoup as BS
import gzip
import re
import glob
from tqdm import tqdm
from pathlib import Path
from urllib.parse import urlparse
import json

FILE = Path(__name__).name
NOW_FOLDER = Path(__name__).resolve().parent
TOP_FOLDER = Path(__name__).resolve().parent.parent

def process(fn):
    try:
        with open(fn, 'rb') as fp:
            html = gzip.decompress(fp.read())
        soup = BS(html, 'lxml')

        urls = set()
        for a in soup.find_all('a', {'href':re.compile(r'^https://')}):
            urls.add(a.get('href'))
        return urls
    except Exception as exc:
        print(exc)
        return set()

def run():
    fns = glob.glob(f'{NOW_FOLDER}/htmls/*')
    urls = set()
    with ProcessPoolExecutor(max_workers=16) as exe:
        for _urls in tqdm(exe.map(process, fns), total=len(fns)):
            urls |= _urls

    netloc_url = {}
    for url in urls:
        o = urlparse(url)
        netloc = '.'.join(o.netloc.split('.')[-2:])
        o = o._replace(params='', query='')
        netloc_url[netloc] = o.geturl()
    with open(f'{NOW_FOLDER}/urls.json', 'w') as fp:
        json.dump(netloc_url, fp, indent=2)


if __name__ == '__main__':
    run()
