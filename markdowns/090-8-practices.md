## 8. 練習
この章では、いくつかの目的を設定してそれぞれのユースケース別に同スクレイピングをしていくのか実演形式でお伝えします。

### 8.1 Practice 1, 無料のphotostockをスクレイピングして大量のフリー画像を集める

いくつかのサイトではphotostockと呼ばれる無料の写真を提供していることがあります。ブログのイメージ画像に設定したり、タグやなにかの属性が付与されていれば、機械学習に用いることができたりなど、汎用性が高いサービスです。  
何らかの理由により、これらのデータが必要になった場合、どのような戦略で集めることができるかを述べます。  

#### 8.1.1 https://unsplash.com/
対象とするサイトは `unsplash.com` としました。 

このサイトは画像を大量に公開しているサイトで、商用利用等を含めて競合しない限り自由に利用してOKというすごい太っ腹なサイトです。  

構造的にはシンプルですが、htmlの作りが機械的で法則性が弱く一部ヒューリスティックとアドホックを入れて対応することになります。  

例えば、 `div` の classやidが唯一に特定できればそれが一番ありがたいのですが、特に指定がない構造であったり、では、順番によって特定できるかというと、ページによって再現性がなかったりなど、行き着くところはルールを発見し（ヒューリスティック）、場当たり的に対応（アドホック）するしかないです。  

ウェブページに限らず、データがきれいに整備されているとき、ヒューリスティックとアドホックが多く入るとき、そのデータは完全性や完成度が低いとみなすことができますが、実際のデータ構造に近いので、練習になります。

小さいコードを組んで、目的に対して動作するかを検証することから始めます。このときchromeやvivaldiなどで、タグ構造を把握しながら、どのような方針が適切か検討します。 

<div align="center">
<img width="600px" src="https://www.dropbox.com/s/60lmigecynmltk1/%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%202020-01-19%205.23.55.png?raw=1">
<div> 図.1 chromeの"検証"から挙動をチェックしている</div>
</div>

様々な角度でこのウェブサイトの構造を検証したところ、以下のことが判明しました。

 - divのclass名がページごとのユニークなhashが与えられており、指定することができない
 - 構造に多様性があるため "https://unsplash.com/photos" で始まるURLに限定して見たほうがいい
 - 今回ほしい画像とその説明は最も大きい画像であり、その画像のみalt属性が存在し、それがフラグになりそうである
 - "https://unsplash.com/photos/.{1,}/download" のURLを踏んでしまうと応答が帰ってこなく、requestsがtimeoutしてしまうので、このURLは避ける

など、多くのこのドメイン限りのルールが判明しました。  

以下にコードを記します。

```python
from concurrent.futures import ProcessPoolExecutor as PPE
import glob
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from hashlib import sha224
from pathlib import Path
import random 
import json
import gzip
from tqdm import tqdm
import re
from multiprocessing import Process, Manager
import time

manager = Manager()
shared_d = manager.dict({'requests':0, 'bs4':0, 'img_dl':0, 'href':0 })

def hashing(url):
    x = sha224(bytes(url, 'utf8')).hexdigest()[:16]
    return x

def parallel(arg):
    try:
        url = arg
        mst_p = urlparse(url)

        mst_p = mst_p._replace(query='')
        url = mst_p.geturl()
        if re.search('download$', url):
            return set()
        if 'https://unsplash.com/photos' not in url:
            return set()

        print(url)
        start = time.time()
        with requests.get(url) as r:
            html = r.text
        shared_d['requests'] += time.time() - start 

        start = time.time()
        soup = BeautifulSoup(html, 'lxml')
                shared_d['bs4'] += time.time() - start 

        mst_x = hashing(url)
        if Path(f'htmls/{mst_x}').exists():
            return set()

        start = time.time()
        for img in soup.find_all('img', {'src': re.compile('https://images.unsplash.com/photo'), 'alt':True}):
            src = img.get('src')
            alt = img.get('alt')
            p = urlparse(src)
            p = p._replace(query='')
            src = p.geturl()
            name = hashing(src)
            #print('query removed url', src, 'hashing', name)
            if Path(f'imgs/{mst_x}/{name}.jpg').exists():
                continue
            print('try download', src, alt, 'at', url)
            with requests.get(src) as r:
                binary = r.content
            Path(f'imgs/{mst_x}').mkdir(exist_ok=True, parents=True)
            with open(f'imgs/{mst_x}/{name}.jpg', 'wb') as fp:
                fp.write(binary)
            with open(f'imgs/{mst_x}/{name}.txt', 'w') as fp:
                fp.write(alt)
        shared_d['img_dl'] += time.time() - start 

        start = time.time()
        hrefs = set()
        for a in soup.find_all('a', {'href': True}):
            href = a.get('href')
            try:
                if href[0] == '/' or 'https://unsplash.com' in href:
                    if href[0] == '/':
                        href = 'https://unsplash.com' + href
                    hrefs.add(href)
                else:
                    continue
            except Exception as exc:
                print(exc)
        shared_d['href'] += time.time() - start 

        x = hashing(url)
        with Path(f'links/{x}').open('w') as fp:
            json.dump(list(hrefs), fp, indent=2)
        with Path(f'htmls/{x}').open('wb') as fp:
            ser = gzip.compress(bytes(html, 'utf8'))
            fp.write(ser)

        print(shared_d)
        return hrefs

    except Exception as exc:
        print('exc', exc, url)
        return set()

urls = ['https://unsplash.com/photos/D1IS5s5O9xo']
while True:
    nexts = set()
    with PPE(max_workers=24) as exe:
        # for url in urls:
        #        nexts |= parallel(url)
        for hrefs in exe.map(parallel, urls):
            nexts |= hrefs

    if len(nexts) == 0:
        nexts = set()
        for fn in tqdm(glob.glob('links/*')):
            try:
                with open(fn) as fp:
                    nexts |= set(json.load(fp))
            except:
                continue
        urls = list(nexts)
    else:
        urls = list(nexts)
```  

### 8.2 Practice 2, YouTubeの動画をダウンロードする
誰もがチャレンジしたくなるYouTubeのダウンロードですが、YouTubeはGoogle社に買収されてからというもの、機械学習による高速な異常検知による自動BAN等で、ダウンロードをできる手法だったり穴が発見されても、なかなか利用できないというのが現状になります。  

異常検知に引っかかると、IPごとBANになるのでこれを避けながらダウンロードする術があるので、ご紹介したいと思います。  

#### 8.2.1 YouTubeの動画のダウンロードに便利な `youtube-dl`
chromedriverでhtmlを解析して動画のstream通信をディスクに保存する手法を最初は検討していたのですが、YouTubeというサイトが高速に仕様やセキュリティの様相を変化させるので、キャッチアップしきれず、ライブラリに頼ることになりました。  

もっともダウンロード成功率が高いのがpipで入る `youtube-dl` というソフトで、最新のYouTubeの仕様に対応するため、github経由でインストールすると確実です。  

```console
$ pip install git+https://github.com/ytdl-org/youtube-dl
```
具体的に、動画をダウンロードするには以下のコマンドが必要です。　

```console
$ youtube-dl "https://www.youtube.com/watch?v=xxxxx" # xxxxはサンプル
```

いろんな動画をダウンロードできるのですが、何回か使っていると気づくはずです。。。突然、ダウンロードできなくなることに。  

この状態になってしまうとしばらく待ってもなかなか解除されませんが、MacBookなどのChromeでYouTubeを見るぶんには大丈夫だったりします。

#### 8.2.2 IPを使い潰すしかなさそう
"IPレベル"×"ツールレベル"で規制されることがわかっているので、IPアドレスを無限に変え続ければいいという単純な発想に落ち着きます。  

これを回避するには、以前の章で紹介した `http://spys.one/en` のプロキシサーバリストを使うことができます。  

`spys.one`から回線状態がよいProxyで以下のコマンドを実行すると、Proxy経由のアクセスになり、ダウンロードを継続することができます。  

```console
$ youtube-dl --proxy 118.27.31.50:3128 "https://www.youtube.com/watch?v=xxxxxx"
```

(xxxxxとIPアドレスは例であり、適宜読み替えてください)

<div align="center">
    <img width="100%" src="https://www.dropbox.com/s/h56hsxgb8wky670/%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%202020-01-22%208.55.29.png?raw=1">
    図.2 フリー素材をダウンロードする例 
</div>

 `spys.one/en` を更に別の章で紹介したgoogle chrome + seleniumでのダウンロードを用いることにより、Proxyの取得すら自動化できるので、ほぼ制限なしに使えるようになることできます。

 YouTubeのすべての動画と音声がダウンロード可能ではありますが、法で規制されているコンテンツも多いので、十分に留意してください。
