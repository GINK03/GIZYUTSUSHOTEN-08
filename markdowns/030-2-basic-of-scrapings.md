# 2.  データを集める手段、スクレイピングの基礎

## 2.1 Requests + BeautifulSoupでスクレイピングする
スクレイピングの手法としてPythonで一般的である、requestsとBeautifulSoupのモジュールを利用したスクレイピングについて説明を行います。
環境はUbunut LinuxかMacOSを前提とします。Windowsをお使いの方はAWSかGCPで安いインスタンスを借りることができるので、Linuxをインストールして体験してみると良いと思います。

requestsはpythonで扱いにくかったhttp, httpsなどのアクセスを簡略化して様々なベストプラクティスを詰め込んだライブラリです。他にも様々なものがありますが、これが2020年現在、もっとも使いやすいものです。

BeautifulSoupとはhtmlパーサライブラリで、htmlは特定のフォーマットで記述された言語になり、機械で適切に処理させるにはパーサというものを介さないといけません。


#### pipでのrequests, BeautifulSoupのインストール
Anacondaや特殊なPythonでは別のパッケージマネージャがありますが、pipで統一して話をす進めます。

```console
$ pip install requests bs4
```

<div align="center">
<img width="100%" src="https://www.dropbox.com/s/yr70t5z9ymj0z95/%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%202020-01-03%202.01.30.png?raw=1">
<div>図 x. インストール成功時に期待する画面</div>
</div>

#### Pythonのファイルを書いて実行する

例えば、ヤフージャパンのサイトのタイトルをスクレイピングを試みると、以下のようなコードで実行することでできます。

```python
#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

def main():
    r = requests.get('https://yahoo.co.jp')
    html = r.text
    soup = BeautifulSoup(html)
    print(soup.title.text)
if __name__ == '__main__':
    main()
```

このようなコードを実行すると、ヤフージャパンのトップページのタイトルの「Yahoo! Japan」というテキストが得られます。

では、ヤフー砲と呼ばれるぐらい影響力がある、ヤフーのトップのニュースのタイトルとリンクをスクレイピングするように上記のコードを改良してみましょう。

```python
#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re

def main():
    r = requests.get('https://yahoo.co.jp')
    html = r.text
    soup = BeautifulSoup(html)
    for a in soup.find_all('a', {'href':re.compile('https://news.yahoo.co.jp*')}):
        news_title = a.text
        link = a['href']
        print(news_title, link)
if __name__ == '__main__':
    main()
```

このコードで以下のような出力が得られました。

<div align="center">
<img width="100%" src="https://www.dropbox.com/s/rlt2suifvxnvuzm/%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%202020-01-03%202.35.28.png?raw=1">
<div>図 x. インストール成功時に期待する画面</div>
</div>

これでヤフー砲を監視するスクリプトが書けますね。株価に重大な影響を及ぼすファクターだけに、いち早く察知することができるので他の人手の投資家に対して自動化などで先んじることができそうです。

BeautifulSoupはタグの種類とタグに与えられているプロパティのような要素で検索するようにアクセスすることができ、　`soup.find_all('a', {'href':re.compile('https://news.yahoo.co.jp*')})`は、 `<a>` のタグに対して `hrefで正規表現でhttps://news.yahoo.co.jp` に一致する範囲のタグをすべてリストで取り出す、という操作になります。

このタグはchromeのインスペクタで見たときと差があることに気づくと思います。実は、requestsではhttp, httpsで情報をくれというリクエストを投げるだけですのでJavaScript等の解釈ができません。つまり、JavaScriptが動くことで初めて描画されるようなコンテンツに関しては、全くのスルーになり、Google Chromeなどで見たときのhtml構造とは異なる事があるので、注意してください。Google ChromeなどでJavaScriptを停止するChrome拡張などを入れてhtmlの構造を最初に把握しておくと良いです。

## 2.2 Google Chrome + Seleniumでスクレイピングする
そもそもrequestsだけでスクレイピングが完結してしまうような構造のウェブサイトは多くのスクレイパーの餌食になると想像が付きます。  

このとき、スクレイピングする側と、ウェブサイト側のスクレイピングされる側に利益相反などがあると、スクレイピング難易度を上げて防御的な構造を取ることが多くあります。  

requestsで取得する際にはJavaScriptが動作しないので、コンテンツの多くをJavaScriptに描画させるなどの手法が取られます。  

### 2.2.1 Pixivを例に取る
数年前のPixivは割と簡単な構造で構築されており、簡単に殆どのイラストを収集することができましたが、現在はJavaScriptで多くのコンテンツをラップすることで、簡単には解析されないようにしています。  

例えば、このようなコンテンツをユーザ側のブラウザで見ることができました。  
<div align="center">
  <img width="450px" src="https://www.dropbox.com/s/bvvh4pt0yraq08h/Screen%20Shot%202020-01-14%20at%2018.04.29.png?raw=1">
  <div>図 x. https://www.pixiv.net/artworks/75863105 </div>
</div>

では、このhtmlを解析しようとして、requestsでhtmlを取得して解析してみましょう。  

```python
# pixiv example only requests
import requests
from bs4 import BeautifulSoup

r = requests.get('https://www.pixiv.net/artworks/75863105')
soup = BeautifulSoup(r.text, 'html5lib')
for div in soup.find_all('div'):
    print(div)
```

期待としては、大量のdivタグの構造を取得できるはずですが、実際の2020年1月時点での出力は以下のようになります。  

```console
$ python3 006.py
<div id="root"></div>
```
このプログラムは巻末のgithubからダウンロードできます。

では、どうやってマミミのイラストを集めればいいのでしょうか？  
シンプルで簡単な解決法としてGoogle Chromeをseleniumで動作させることで、期待する動作を得ることができます。  

### 2.2.2 Pixivを例に取る: Google Chrome + Seleniumでデータを取得する

SeleniumとChromeDriverはインストール済みという前提で進めると、以下のコードでこのマミミのサイトのhtmlを取得できるはずです。  

(Pixiv様のサイトのコンテンツの画像を含みますが、これは著作権法３２条・1. "公表された著作物は、引用して利用することができる。この場合において、その引用は、公正な慣行に合致するものであり、かつ、報道、批評、研究その他の引用の目的上正当な範囲内で行なわれるものでなければならない。"を論拠に、技術的な検証の観点として、引用させていただきます[1])

```python
# headless google-chromeの例
import os
import shutil
from bs4 import BeautifulSoup
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

HOME = os.environ['HOME']
target_url = 'https://www.pixiv.net/artworks/75863105'
options = Options()
options.add_argument("--headless")
options.add_argument('window-size=2024x2024')
options.add_argument(f'user-data-dir=work_dir')
options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

driver = webdriver.Chrome(executable_path=shutil.which('chromedriver'), options=options)
driver.get(target_url)
time.sleep(5.0)
html = driver.page_source
soup = BeautifulSoup(html, 'html5lib')
driver.save_screenshot("screenshot.png")
```

<div align="center">
  <img width="450px" src="https://www.dropbox.com/s/nint3yia9uei7n7/Untitled.png?raw=1">
  <div>図 1. 結果 </div>
</div>

残念ながら、ログインしていないため、マミミは見ることができません。  

次のステップでこれを更に拡張して、自動でログインしてJavaScriptを実行し問題なく描画してhtmlが取得できる方法をご紹介します。

### 2.2.3 Pixivを例に取る: 自動でログインしてデータを取得する

seleniumはユニークで、pure pythonでは代替ができない機能があって、その一つがGoogle Chrome等のブラウザを操作する機能です。  

この機能を利用すると、Google Chromeをプログラムした内容に従って自動でログインを行い、ログインのセッションが残っている間は、ログインしないと見えない、またはJavaScriptが動作しないと見えないはずのコンテンツを参照することができます。  


以下のコードの例では、最初にログインを指定ない状態でGoogle Chromeを起動した後、ログインページにジャンプしてユーザーネーム、パスワード等のログイン項目を埋めて、ほしいURLを描画してhtmlを取得します。  

```python
import os
import shutil
from bs4 import BeautifulSoup
import time
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

HOME = os.environ['HOME']
EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['PASSWORD']

target_url = 'https://www.pixiv.net/artworks/75863105'
options = Options()
options.add_argument("--headless")
options.add_argument('window-size=2024x2024')
options.add_argument(f'user-data-dir=work_dir')
options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

driver = webdriver.Chrome(executable_path=shutil.which('chromedriver'), options=options)
if not Path('init_chrome').exists():
    driver.get('https://accounts.pixiv.net/login')
    time.sleep(2.0)

    elm = driver.find_element_by_xpath('''//input[@autocomplete="username"]''')
    elm.click()
    elm.send_keys(EMAIL)
    elm = driver.find_element_by_xpath('''//input[@autocomplete="current-password"]''')
    elm.click()
    elm.send_keys(PASSWORD)
    time.sleep(1.0)
    elm = driver.find_element_by_xpath('''//div[@id='LoginComponent']//button[@class='signup-form__submit']''')
    elm.click()
    time.sleep(5.0)
    Path('init_chrome').touch()

driver.get(target_url) # ここでまみみのページがログイン状態を保存してアクセスしてほしい
time.sleep(5.0)
html = driver.page_source
soup = BeautifulSoup(html, 'html5lib')
driver.save_screenshot("screenshot.png") # screenshotを取得する
```

<div align="center">
<img width="600px" src="https://www.dropbox.com/s/zjz0sxaryd685zu/Untitled2.png?raw=1">
<div>図 2. 最終的な出力のscreenshot.png, ただしくマミミが表示されている</div>
</div>

Seleniumを用いれば、様々なWebサービスにログインして、コンテンツを表示した状態でスクレイピングできることを示しました。  

## 2.3 ハイパーリンクが作るネットワークは探索問題

ハイパーリンクはネットワーク状に繋がったネットワークをいかに探索するか、という問題にも帰着できます。  

例えば以下のような図のネットワークがあったとします。  

<div align="center">
<img width="600px" src="https://www.dropbox.com/s/07c2lcso578muxc/web.png?raw=1">
<div>図 3. インターネットのhyper linkの依存関係の例</div>
</div>

このとき、どこからどのようにスクレイピングすれば、サイト全体を取得することが可能になるのでしょうか。  

これには考え方がいくつかあって、全取得を前提とした方法をご紹介します。  

まず、エントリーポイントとなる、URLを一つ決め、そのURLをスクレイピングします。そのスクレイピングしたhtml内部にあるURLを取り出して、次のページをスクレイピングします。何度も同じページをスクレイピングしてもサイトの負荷になるし、意味がないデータが増えるだけなのでそれを防ぐ実装も行う必要があります。  

Pythonをイメージしたコードで表現すると、以下のようになります(すべて実装しきっていません)。  

```python
#!/usr/bin/env python3
urls = [entry_url]
all_urls = set()
while True:
  for url in urls:
	if exists_db(url): # 未実装
	  continue
	html = get(url)
	store_db(url, html) # 未実装　
	for next_url in get_urls_from_html(html):
	  if next_url not in all_urls:
		all_urls.add(next_url)
  urls = list(all_urls)
```

このようなコードが全探索を前提としたスクレイピングする際の最小のコードになります。  

実際にはこのような少ないコードで理想通りに動作することは稀であり、正しく動作させるために様々なヒューリスティックを入れることになります。  

まずこのコードの欠点はシングルプロセスでしか動作させることができませんし、store_db, exists_dbで dbに大量にアクセスが発生します。  

通常このようなユースケースではRDBは不向きで、KVSのようなキー(多くの場合はURL)に対して、O(1)の計算量でデータを引き出せるアルゴリズムが適しています。  

この問題を解決するには次の章の `3. 最強のDB、自作DBを作る` に記述します。 

### 2.3.1 幅優先探索・深さ優先探索・ビームサーチ

Webサイトはネットワーク状になっているので、ネットワークを探索するプラクティスの探索方式がいくつか使うことができます。  

例えば幅優先探索でスクレイピングする場合、浅い領域を優先してスクレイピングを継続します。できるだけ深いURLを取得しないで浅く広くhtmlを取得するなど向いています。  

深さ優先探索になると、深い方を優先して探索するようになるので最初に設定したURLから遠く深いところを優先してスクレイピングするようになります。

ビームサーチは幅優先探索と深さ優先探索のバランスを取ったような方法で、一定の探索幅を維持して、深さも幅も良いところどりをするものになります。

以下のコードの例では、幅優先探索で `yahoo.co.jp` のドメインをスクレイピングするものになります。

```python
import requests
from bs4 import BeautifulSoup
import time
import re
from collections import namedtuple

DepthUrl = namedtuple('DepthUrl', ['depth', 'url'])
urls = [DepthUrl(0, 'https://www.yahoo.co.jp/')]
all_urls = set()
flatten_urls = set('https://www.yahoo.co.jp/')
depth = 0
for I in range(3):
    depth += 1
    for depth_, url in urls:
        html = requests.get(url).text
        soup = BeautifulSoup(html, features="html.parser")
        for a in soup.find_all('a', {'href':re.compile(r'.*?\.yahoo\.co\.jp')}):
            next_url = a.get('href')
            if next_url not in flatten_urls:
                all_urls.add(DepthUrl(depth, next_url))
        flatten_urls.add(url)
        all_urls -= {DepthUrl(depth_, url)}
    urls = sorted(all_urls, key=lambda x:x[0])
    min_depth = min([url.depth for url in urls]) # ここに注目
    urls = [url for url in urls if url.depth == min_depth]
```

最も深さが浅いものをスクレイピングするように `min_depth` を算出していますが、ここを `max_depth` に変更したり、一定のルールでビーム幅を設定して計算量を抑えることでビームサーチに実装を変更することができます。  

### 2.4 スクレイピングと法的問題
スクレイピングに関連する問題として常に隣接しているのは法的な問題点です。  

何年も前の話ですが、図書館の在庫状態を確認するサービスを作成しようとして、秒間1アクセスを満たすような低頻度のアクセスで通常は業務妨害に当たらないものであったのに関わらず、警察にされるという事態が発生しました[2] 

常識的なアクセスを行い、データ取得祭のサーバに高い負荷にする意図がなくても、このスクレイピングを認識する人物や組織やシステムの都合で逮捕、勾留されてしまうリスクを示すものでした。  

基本的にはデータは提供しているサイトの個人や法人の持ち物であり、通常の常識の範囲内で想定される用途での利用が想定されています。  
　
例えば、何らかのデータを収集して機械学習等で法則性を取り出し、競合製品を作るなどは、業務妨害で訴えられても仕方がないでしょう。一方で、そのサービスをより便利に、より利益がある形でAPIやGoogle Chrome拡張など許容される範囲内だとだれも結果的に損をすることがないので争いになる確率は低いです。  
巷で言われる、秒間1アクセスは近年のサーバリソースの拡充に伴い、現実的な基準ではありませんが、「対象サイトの業務を妨害せず」に、可能ならば「相互に利益のある形」で分析やプロダクトづくりを行うといいでしょう。  

## 参考
- 1. 著作権法第32条 : https://ja.wikibooks.org/wiki/著作権法第32条
- 2. 岡崎市立中央図書館事件 :  https://ja.wikipedia.org/wiki/岡崎市立中央図書館事件

