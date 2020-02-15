## 6. Depth 3, MultiCore, Multi Machineでスクレイピングする
現代のモダンなコンピュータはCPUを複数備えることが一般的になっています。  

通常のPythonスクリプトはSingle CPUしかリソースを使えませんが、大量のCPUのコア（スレッドと表現することもありますがコアと統一します）を効率的に使える標準ライブラリと動作原理をお伝えします。

- 1. concurrent.futures.ProcessPoolExecutor
- 2. concurrent.futures.ThreadPoolExecutor
- 3. asyncio

よく整理されて使い勝手が良いライブラリがこちらになります。  

ProcessPoolExcutorがマルチプロセスで、ThreadPoolExecutorがGILというレガシーな仕組みをつかったスレッド、asyncioがノンブロッキングIOという方法で動作するスレッドになります。  

マルチプロセスとマルチスレッドは大学等でコンピュターサイエンスを履修された人には、釈迦に説法ですが、説明させていただけると幸いです。  

マルチプロセスは、forkという機能を使って実行しているプログラムのOSから見る実態を増やします。このときメモリに重なる部分が多いので消費を低減して、実態を複数個作ります。forkで新たに作られた子プログラムと親プログラムは原則としてなんらか細工をしない限り通信できません。  

マルチスレッドは、一つのプログラムの中で、CPUリソースを割り当てを変えながら同時に２つ以上動作せる仕組みです。このCPU割あてスケジューリングには多くの手法があって、ioがブロックされている間は別の処理をするようにしたものがasyncioが行うスレッドになります。

これらの特性をまとめると以下のような表になります。 

<div align="center">
  <div> 表.1 特性比較</div>
  <img width="500px" src="https://www.dropbox.com/s/6fcgvwgguh5fgb0/Screen%20Shot%202020-01-16%20at%2016.32.53.png?raw=1">
</div>

つまりユースケースに応じて、並列化の手法を使い分ければ良いとわかります。  

例えば今回の主ミッションであるスクレイピングに対しては、ThreadとMultiprocessはどちらが良いのでしょうか？

### 6.1 Thread vs Multiprocessing
では、実際にスクレイピングの文脈に対しては、ThreadとMultiprocessingはどちらが効果的に動作するのでしょうか。  

実際にユニークなドメイン `5443件` のURLに全量をスクレイピングするのにどの程度かかるかを示します。  

スクレイピングの速度をベンチマークするに当たって、ドメインを限定するのは不適切ですので、ドメインでユニークにすることで負荷を分散しました。  


なお、使っているwrapperが `concurrent.futures.ProcessPoolExecutor` か `concurrent.futures.ThreadPoolExecutor` の違いになっているので、ここでは、Multiprocessの方のコードだけを例示します。  

必要に応じで、巻末のgithubのリンクを参照してください。　　

```python
from urllib.parse import urlparse
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urlparse
from concurrent.futures import ProcessPoolExecutor  # <- ここをThreadPoolExecutorに変えればThreadのパフォーマンスがわかる
import random
import requests
import time
import json
from hashlib import sha224

def get_digest(x):
    return sha224(bytes(x,'utf8')).hexdigest()[:16]

def process(arg):
    try:
        url = arg
        with requests.get(url, timeout=5.0) as r:
            header = r.headers
            html = r.text
        if 'text/html' not in header.get('Content-Type'):
            return set()
        soup = BeautifulSoup(html, 'lxml')
        hrefs = set()
        for a in soup.find_all('a', {'href': True}):
            hrefs.add(a.get('href'))
        Path(f'logs/{get_digest(url)}').touch()
        return hrefs
    except Exception as exc:
        #print(exc)
        return set()

# ベンチマークに使うURLをlistで保存したjson
with open('urls.json') as fp:
    urls = json.load(fp)
NUM = 256
print('total uniq domain(netloc) url size is', len(urls))
start = time.time()
hrefs = set()
with ProcessPoolExecutor(max_workers=NUM) as exe:
    for child_hrefs in tqdm(exe.map(process, urls), total=len(urls)):
        hrefs |= child_hrefs

print(f'total result urls = {len(hrefs)}')
elapsed = time.time() - start
print(f'elapsed time {elapsed}')
```

**MultiProcessingの結果**
```console
$ python3 multiprocessing_benchmark.py
...
elapsed time 242.38
```
単位は秒になります。  

**Threadingの結果**
```console
$ python3 thread_benchmark.py
...
elapsed time 1580.46
```
単位は秒になります。


このように、基本的に戻り値だけで制御できたり重い操作をやる場合は、Multiprocessingの方が速度的に優れていることがわかりました。 

実はMultiprocessingの真価は、全CPUを効率的に用いられるというだけではありません。ロジックの組み方によってはマルチコアのCPU内部に閉じずに、マシンを横断しての並列処理ができることを次の章で示します。  


### 6.2 MultiprocessingをMulti Machineに拡張

Multiprocessingは原則として（例外の非常に多い原則ですが）プロセス間でメモリ内容の共有ができません。  

一見不便なようなこの制約ですが、Linux, UnixのPIPEやhttp通信やファイルシステムをバイパスすればこれらの制約は回避することができます。  

Multiprocessingの1プロセスがアクセスする先をファイルシステムにすることで、PIPEや、httpなどを用いなくても簡単かつ大規模な共有メモリプールとして利用できます。  

例えば、オーバーヘッドを避けるために、すでにスクレイピングしたURLのキーが共有フォルダー上に存在したら処理をスキップするなどが簡単にコードとして組めます。  

例えばデータをホストするマシンを一台用意し、nfsやsshfsなどで、リモートのマシンのフォルダーやハードディスクを共有すると同時に並列にアクセスできるようになります。

スクレイピングしたurlをhtml等以外にもlinkをjson等で保存すれば、そのjsonファイルを別のマシンで読み書きできるようになります。  

このコードはnfsでマウントしたSSD等から起動すると、どのマシンでも並列で実行できるようになります。

```python
from urllib.parse import urlparse
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urlparse
from concurrent.futures import ProcessPoolExecutor  # <- ここをThreadPoolExecutorに変えればThreadのパフォーマンスがわかる
import random
import requests
import time
import json
from hashlib import sha224

def get_digest(x):
    return sha224(bytes(x,'utf8')).hexdigest()[:16]

def process(arg):
    try:
        url = arg
        # logですでに取得されていたら、取得をスキップする
        # これはNFSでデータがマウントされていたら他のマシンでスクレイピングされていたら再度行わないということと等価である
        if Path(f'logs/{get_digest(url)}').exists():
            return set()

        with requests.get(url, timeout=5.0) as r:
            header = r.headers
            html = r.text
        if 'text/html' not in header.get('Content-Type'):
            return set()
        soup = BeautifulSoup(html, 'lxml')
        hrefs = set()
        for a in soup.find_all('a', {'href': True}):
            hrefs.add(a.get('href'))
        Path(f'logs/{get_digest(url)}').touch()
        return hrefs
    except Exception as exc:
        #print(exc)
        return set()

# ベンチマークに使うURLをlistで保存したjson
with open('urls.json') as fp:
    urls = json.load(fp)
# 必ずshuffleする
random.shuffle(urls)
NUM = 256
print('total uniq domain(netloc) url size is', len(urls))
start = time.time()
hrefs = set()
with ProcessPoolExecutor(max_workers=NUM) as exe:
    for child_hrefs in tqdm(exe.map(process, urls), total=len(urls)):
        hrefs |= child_hrefs

print(f'total result urls = {len(hrefs)}')
elapsed = time.time() - start
print(f'elapsed time {elapsed}')
```

この方法での並列化は2 ~ 10台程度では、ほとんど線形に性能が向上することが多く、気軽にハイパフォーマンス・コンピューティングをするのに向いている方法になります。  

