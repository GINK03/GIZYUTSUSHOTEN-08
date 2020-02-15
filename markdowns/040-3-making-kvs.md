## 3. 最強のDB、自作DBを作る
この章では、スクレイピングデータを保持したり可用性やSLAが高いDBをどう作っていくかを述べます。  

エンピリカルには、MySQLやPostgressSQLを用いるより、KVSなどより速度と非構造化データ(リレーショナル性が低いデータをこの本ではこう呼ぶとします)に対して、有効です。  

スクレイピングデータはHTMLなどはパースをしてきれいに整形すれば、RDBなどと相性がいいですが、本格的なパースや整形は後で行い、データを集めることを最初に行うとすると、KVSが相性が良くなってきます。 

### 3.1 自作KVSとその関連

優れたKVSにはいくつか種類があり、有名なよくマネージメントされたKVSとしては、 LevelDB, RocksDBなどがあります。  

これらのDBは様々な例外を考慮されているし、速度も早いのですが、致命的なデメリットが存在して、マルチプロセスでのプロセス間を横断したアクセスができないという点があります。  

逆に疎結合を意図したRBDのインターフェースなどはこの制約を受けないのですが、KVSと比較したときに速度が極めて遅くなります。  

この両者の欠点を解決した、実践的で、実際に役立つKVSの作り方をご紹介したいと思います。  

### 3.2 最強のDBは結局ファイルシステム

ファイルシステムという言葉は聞いたことがあるでしょうか。　　

ファイルシステムはOSやファイルを格納する際のSSDやHDDの、一定のルールで書き込み読み込みを制御するデータの格納ルールを示します。 

馴染みがあるところだと、WindowsのNTFSや、MacOSのApple File Systemや、Linuxのext4などがあります。  

いずれのファイルシステムも一長一短があり、たくさんのファイルを保存できるがデータ総量が少ない(xfs)、高速で動作して一定以上のパフォーマンスを発揮するが安定性が微妙(btrfs)、など多様性に富んできます。  

ファイルシステムは特定のキーに対して、計算量O(1)でアクセスできるので、実質KVSとして動作させることが可能であり、この発想から作られたLevelDBはファイルシステムベースのKVSと言われています。  

Pythonではファイルやバイナリデータのハッシュ値を扱うのが簡単であるため、簡単にKVSのようにファイルシステムを扱うことができます。

また、PythonではnamedtupleというscalaかkotlinなどのDataClassに相当するものがあり、シリアライズもサポートしています。

例として、なにかのkey, valueがある場合、O(1)でファイルシステムから書き込み、参照するコードを書いてみます。  

通常のスクレイピングでは、何度も同じURLが出現する事があり、そのたびに新規リクエストを投げていたら、対象のサイトに異常な負荷を掛ける結果になってしまいます。  

そのためダミーのURLを生成して、スクレイピングしたデータがあると仮定して、ファイルシステムを利用して、データを保存するコードを書いてみます。 

```python
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
```

このコードはキーとなるURLに対して行った処理に対して、hash値をキーに、valueにnamedtupleを利用することで、KVS Likeなことをしています。  
1000種類しかないURLに対して10000回も処理命令があった場合、重複するようなURLがあるはずでこのURLを効率的にスキップしたいです。その際に、hash名を持つファイルが存在するかどうかだけで判断するので、実質的にファイルシステムのアルゴリズムからこれはO(1)であることがわかります。  


さてシンプルなこのコードを、並列化してみましょう。  

この方法は、それぞれの並列化した関数（またはプロセス）から、ファイルシステムへアクセスすることが可能であり、例えばこれはLevelDBではバグってしまい完走することができません。

```python
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

Datum = namedtuple('Datum', ['depth', 'domain', 'html', 'links'])


def flash(url, datum):
    # keyとなるurlのhash値を計算(長過ぎるのをトリムする)
    key = sha224(bytes(url, 'utf8')).hexdigest()[:24]
    # valueとなるDatum型のシリアライズと圧縮
    value = gzip.compress(pickle.dumps(datum))

    # db/にhash値のファイル名で書き込む
    with open(f'db/{key}', 'wb') as fp:
        fp.write(value)


def isExists(url):
    # keyとなるurlのhash値を計算(長過ぎるのをトリムする)
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

```
ここで用いている `concurrent.future.ProcessPoolExecutor` は、引数に与えた関数をマルチコアで動作させるライブラリで、 `max_worker` で並列数を指定できるので、この場合は8コアで動作することになります。  
最近のCPUはコア数が多いのでリソースを最大に活かしながら、並列アクセス、並列パースなどができ、高速かつnon-blockingにKVSライクな処理を行うことができます。  

なお、例えばLevelDBを使って並列処理を行おうと試みた場合、levelDBは使っているうちはロックが掛かるのと、ロックを無理やり上記のようなマルチプロセスライブラリ等で並列化した場合、DBのファイルに不整合が生じて、結果としてDBそのものを破壊してしまう、という事態になります。  

```console
$ python3 010.py  | wc -l
Traceback (most recent call last):
  File "010.py", line 55, in <module>
    for key, value in db.iterator():
  File "plyvel/_plyvel.pyx", line 362, in plyvel._plyvel.DB.iterator
  File "plyvel/_plyvel.pyx", line 788, in plyvel._plyvel.Iterator.__init__
  File "plyvel/_plyvel.pyx", line 94, in plyvel._plyvel.raise_for_status
plyvel._plyvel.Error: b'NotFound: /tmp/db//000005.ldb: No such file or directory'
    1212
```
↑ LevelDBが並列処理により破壊された例。　 

経験則として、よく作られたKVSのライブラリを選択するより、ファイルシステムをうまく使用してKVS Likeなことを行ったほうが結果として安定性もスケールアウト性も優れており、最終的に並列処理が伴うようなプログラムを作る際、このような方法に落ち着くことがほとんどです。
