
import requests
import re
from bs4 import BeautifulSoup
from multiprocessing.managers import BaseManager as Manager
from concurrent.futures import ProcessPoolExecutor 
Manager.register("get")  # 関数を登録
Manager.register("put")
Manager.register("finish")

def process(arg):
    port_num = 4343
    manager = Manager(address=('127.0.0.1', port_num), authkey=b"password")
    manager.connect()
    manager.put(['https://www.yahoo.co.jp/'])
        
    while True:
        try:
            url = manager.get()._getvalue()
            try:
                with requests.get(url, timeout=15) as r:
                    html = r.text
            except Exception as exc:
                print(exc)
                manager.finish(url, f'<ERROR>ERROR {exc}</ERROR>')
                continue
            print(url)
            soup = BeautifulSoup(html, 'html5lib')
            urls = set()
            for a in soup.find_all('a', {'href': re.compile(r'^https://')}):
                urls.add(a.get('href'))
            manager.finish(url, html)
            manager.put(urls)
        except Exception as exc:
            print(exc)

if __name__ == "__main__":
    NUM = 256
    with ProcessPoolExecutor(max_workers=NUM) as exe:
        exe.map(process, list(range(NUM)))


