## 6. Depth 3, MultiCore, Multi Machineでスクレイピングする
現代のモダンなコンピュータはCPUを複数備えることが一般的になっています。  

通常のPythonスクリプトはSingle CPUしかリソースを使えませんが、大量のCPUのコア（スレッドと表現することもありますがコアと統一します）を効率的に使える標準ライブラリと動作原理をお伝えします。

- 1. concurrent.futures.ProcessPoolExecutor
- 2. concurrent.futures.ThreadPoolExecutor
- 3. asyncio

よく整理されて使い勝手が良いライブラリがこちらになります。  

ProcessPoolExcutorがマルチプロセスで、ThreadPoolExecutorがGILというレガシーな仕組みをつかったスレッド、asyncioがノンブロッキングIOという方法で動作するスレッドになります。  

マルチプロセスとマルチスレッドは大学でコンピュターサイエンスをやった人には、釈迦に説法ですが、そうでない人のために説明させていただけると幸いです。  

マルチプロセスは、forkという機能を使って実行しているプログラムのOSから見る実態を増やします。このときメモリに重なる部分が多いので消費を低減して、実態を複数個作ります。forkで新たに作られた子プログラムと親プログラムは原則としてなんらか細工をしない限り通信できません。  

マルチスレッドは、一つのプログラムの中で、CPUリソースを割り当てを変えながら同時に２つ異常動作せる仕組みです。このCPU割あてスケジューリングには色々手法があって、ioがブロックされている間は別の処理をするようにしたものがasyncioが行うスレッドになります。

これらの特性をまとめると以下のような表になります。 

<div align="center">
  <div> 表.X 特性比較</div>
  <img width="500px" src="https://www.dropbox.com/s/6fcgvwgguh5fgb0/Screen%20Shot%202020-01-16%20at%2016.32.53.png?raw=1">
</div>

つまりユースケースに応じて、並列化の手法を使い分ければ良いとわかります。  

例えば今回の主ミッションであるスクレイピングにたいしては、ThreadとMultiprocessはどちらが良いのでしょうか？

### 6.1 Thread vs Multiprocessing
では、実際にスクレイピングの文脈に対しては、ThreadとMultiprocessingはどちらが効果的に動作するのでしょうか。  

実際にユニークなドメイン `2941件` のURLに全量をスクレイピングするのにどの程度かかるかを示します。  

スクレイピングの速度をベンチマークするに当たって、ドメインを限定するは不適切ですので、ドメインでユニークにすることで負荷を分散しました。  


なお、使っているwrapperが `concurrent.futures.ProcessPoolExecutor` か `concurrent.futures.ThreadPoolExecutor` の違い飲みになっているのでここでは、Multiprocessの方のコードだけを例示します。  

必要に応じで、巻末のgithubのリンクを参照してください。　　

```python
from urllib.parse import urlparse
from pathlib import Path

from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urlparse
from concurrent.futures import ProcessPoolExecutor
import pickle
import random
import requests
import time
with open('002.pkl', 'rb') as fp:
    netloc_urls = pickle.load(fp)

urls = []
for netloc, _urls in netloc_urls.items():
        if len(_urls) >= 10:
                url = random.sample(list(_urls), k=1)[0]
                urls.append(url)

print('total uniq domain(netloc) url size is', len(urls))

def parallel(arg):
        try:
                url = arg
                print(url)
                r = requests.get(url, timeout=5.0)
                soup = BeautifulSoup(r.text, 'html5lib')
                hrefs = set()
                for a in soup.find_all('a', {'href':True}):
                        a.get('href')
                return hrefs
        except Exception as exc:
                print(exc)
                return set()

start = time.time()
hrefs = set()
with ProcessPoolExecutor(max_workers=16) as exe:
        for child_hrefs in exe.map(parallel, urls):
                hrefs |= child_hrefs
elapsed = time.time() - start
print(f'elapsed time {elapsed}')
```

**MultiProcessingの結果**
```console
$ python3 003-multiprocess.py
elapsed time 496.5804433822632
```
単位は秒になります。  

**Threadingの結果**
```console
$ python3 003-threading.py
elapsed time 1580.4620769023895
```
単位は秒になります。


このように、基本的に戻り値だけで制御できたり重い操作をやる場合は、Multiprocessingの方が速度的に優れていることがわかりました。 

実はMultiprocessingの真価は、全CPUを効率的に用いられるというだけではありません。ロジックの組み方によってはマルチコアのCPU内部に閉じずに、マシンを横断しての並列処理ができることを次の章で示します。  


### 6.2 MultiprocessingをMulti Machineに拡張

Multiprocessingは原則として（例外の非常に多い原則ですが）プロセス間でメモリ内容の共有ができません。  

一見不便なようなこの制約ですが、Linux, UnixのPIPEやhttp通信やファイルシステムをバイパスすればこれらの制約は回避することができます。  

Multiprocessingの1プロセスがアクセスする先をファイルシステムにすることで、PIPEや、httpなどを用いなくても簡単かつ大規模な共有メモリプールとして利用できます。  

例えば、オーバーヘッドを避けるために、すでにスクレイピングしたURLのキーが共有フォルダー上に存在したら処理をスキップするなどが簡単に組めます。  

例えばデータをホストするマシンを一台組み、nfsやsshfsなどで、リモートのマシンのフォルダーやハードディスクを共有すると同時に並列にアクセスできるようになります。

スクレイピングしたurlをhtml等以外にもlinkをjson等で保存すれば、そのjsonファイルを別のマシンで読み書きできるようになります。  

このコードはnfsでマウントしたSSD等から起動すると、どのマシンでも並列で実行できるよになります。

```python
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor as PPE
from urllib.parse import urlparse
from hashlib import sha224
from pathlib import Path
from multiprocessing import Process, Manager
import random
import json
import glob
from tqdm import tqdm
manager = Manager()
domain_freq = manager.dict()

def run(arg):
    i, url = arg
    mst_p = urlparse(url)
    mst_netloc = mst_p.netloc
    group_key = mst_netloc 
    key = sha224(bytes(url, 'utf8')).hexdigest()[:24]
    if Path(f'htmls/{group_key}/{key}').exists():
        return set()
    if Path(f'errs/{group_key}/{key}').exists():
        return set()
    try:
        r = requests.get(url, timeout=30)

        if mst_netloc not in domain_freq:
            domain_freq[mst_netloc] = 0

        all_count = sum(domain_freq.values())
        if all_count > 10 and random.random() < domain_freq[mst_netloc]/all_count:
            return set([url])
        domain_freq[mst_netloc] += 1

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

            href = p.geturl()
            next_urls.add(href)

        Path(f'htmls/{group_key}').mkdir(exist_ok=True, parents=True)
        with open(f'htmls/{group_key}/{key}', 'w') as fp:
            fp.write(r.text)
        Path(f'links/{group_key}').mkdir(exist_ok=True, parents=True)
        with open(f'links/{group_key}/{key}', 'w') as fp:
            fp.write(json.dumps(list(next_urls)))

        return next_urls
    except Exception as exc:
        print(exc)
        Path(f'errs/{group_key}').mkdir(exist_ok=True, parents=True)
        Path(f'errs/{group_key}/{key}').touch()
        return set()


args = [(0, 'https://news.yahoo.co.jp/pickup/6348371')]
while True:
    next_urls = set()
    with PPE(max_workers=32) as exe:
        for _next_urls in exe.map(run, args):
            next_urls |= _next_urls
    if len(next_urls) == 0:
        fns = glob.glob('links/*/*')
        random.shuffle(fns)
        for fn in tqdm(fns):
            next_urls |= set(json.load(open(fn)))
    print('do')
    args = [(i, url) for i, url in enumerate(next_urls)]
```

この方法での並列化は2 ~ 10台程度では、ほとんど線形に性能が向上することが多く、気軽にハイパフォーマンス・コンピューティングをするのに向いている方法になります。  

