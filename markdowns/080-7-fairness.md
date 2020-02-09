## 7. フェアネスを考慮したスクレイピング

AWSやGCPで特定のドメインに対して高頻度でアクセスを行うと攻撃とみなされ、通信がシャットダウンされたりします。  

また実際にアクセスが多すぎて、対象のサイトに対して過負荷を起こしていまうかもしれません。  

いくつかのロジックにて過負荷を防ぐ方法があるので、ご紹介するとともに、どういったロジックで作成したかを説明します。  

### 7.1 ランダムドメイン選択 

結局の所、攻撃とみなされる要素は特定のドメインに対して大量のリクエストを行うことで判定されるので、負荷を分散する必要があります。  

もっと簡単なロジックでは、すべてのドメインに対して平等なスクレイピングの機会を与える方法で、以下のような構造のファイルシステムがある場合に、まず階層1のSetからドメインを選択し、そのドメインのURLを一つ選択し、そのURLを消去します。この操作をすべてのSetが空になるまで繰り返し、空になったらスクレイピング終了です。（現実的な実世界のウェブページ数はものすごい数にのぼり、終了条件を満たせることはほぼありません）

<div align="center">
  <img width="500px" src="https://www.dropbox.com/s/f39me2llfwx40c8/2019-01-20-z1.png?raw=1">
  <div> 図1. ランダムドメイン選択 </div>
</div>

この手法はすべてのURLに対して平等な負荷をかけることになるので、現実的に誰かに迷惑をかけるということがありません。しかしながら、特定のどのdomainに注力をするということもしないので、無限に薄く広く広がることになります。(これを防ぐには日本語のドメインに限定するなどすると良いです)

これを実現するには少しプログラミングにおけるデザインパターンを使用する必要があり、以下の図のような構成にして、 `server-clientモデル` を構築する必要があります。　　


<div align="center">
  <img width="500px" src="https://www.dropbox.com/s/gn3eajradfak2lu/2020-02-09-01.png?raw=1">
  <div> 図2. server-clientモデル </div>
</div>

**server** 

serverでは、オンメモリでdomainとURLのSet情報の対を持っており、domain粒度でfairnessをコントロールすることで、実際にscrapingを行うclientにどのURLをスクレイピングしていいかを通知します。  

```python
from multiprocessing.managers import BaseManager as Manager
import os
import sys
import random
from hashlib import sha224
from pathlib import Path
from urllib.parse import urlparse
import gzip

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
        fp.write(gzip.compress(bytes(html,'utf8')))

if '--init' in sys.argv:
    from bs4 import BeautifulSoup
    import glob
    import re
    for fn in glob.glob('htmls/*'):
        html = gzip.decompress(open(fn, 'rb').read())
        soup = BeautifulSoup(html, 'html5lib')
        urls = set()
        for a in soup.find_all('a', {'href':re.compile(r'^https://')}):
            urls.add(a.get('href'))
        put(urls)

if __name__ == "__main__":
    port_num = 4343
    Manager.register("get", get) # 待受に使う関数を登録
    Manager.register("put", put)
    Manager.register("finish", finish)
    manager = Manager(("", port_num), authkey=b"password") # ホスト名を空白にすることで任意の箇所から命令を受け入れられる。パスワードが設定できる
    manager.start()
    input("Press any key to kill server".center(50, "-")) # なにか入力したら終了
    manager.shutdown()
```

**client**  

clientはserverに比べてシンプルな実装で、serverにURLを聞き、スクレイピングして、その結果をserverに返すだけです。  

```python
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
        url = manager.get()._getvalue()
        try:
            with requests.get(url, timeout=15) as r:
                html = r.text
        except Exception as exc:
            print(exc)
            manager.finish(url, f'<ERROR>ERROR {exc}</ERROR>')
            continue
        print(url, type(url))
        soup = BeautifulSoup(html, 'html5lib')
        urls = set()
        for a in soup.find_all('a', {'href': re.compile(r'^https://')}):
            urls.add(a.get('href'))
        manager.finish(url, html)
        manager.put(urls)

if __name__ == "__main__":
    NUM = 128
    with ProcessPoolExecutor(max_workers=NUM) as exe:
        exe.map(process, list(range(NUM)))
```

この本での例は、domainをキーとしたfairnessでしたが、様々なKGI, KPIをキーとすれば、その粒度でのfairnessを行うことができます。  

AWSやGCPでは特定のドメインに対する過負荷を嫌うので、domain粒度でのfairnessが有効です。 

必要に応じてこういったデザインパターンを活用し、誰かに迷惑をかけないようにしていきたいものです。  