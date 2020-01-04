# 次目

## 1. 現代の最強の科学・意思決定法、定量分析
 - 何が真実かわからいない世の中で、真実は定量データに多く宿るという例を示す。
 - 例えば、ワクチンの統計調査について。
 - 1.1 なぜ、定量分析が最強なのか
## 2.  データを集める手段、スクレイピングの基礎
 - 2.1 Requests + BeautifulSoupでスクレイピングする
 - 2.2 Google Chrome + Seleniumでスクレイピングする
 - 2.3 ハイパーリンクが作るネットワークは探索問題
 - 2.3.1 幅優先探索・深さ優先探索・ビームサーチ
 - 2.4 法的問題

## 3. 最強のDB、自作DBを作る
- ３.1 自作KVSとその関連
- ３.2 最強のDBは結局ファイルシステム

## ４. Depth 1, UserAngent, Referrer を偽装する

## 5. Depth 2, IPを偽装する
 - 5.1 プロキシサーバを立ててアクセス
 - 5.1.x 閑話休題, AWSアク禁
- 5.2 公開プロキシ経由でのアクセス
- 5.3 tor経由でのアクセス

## 6. Depth 4, MultiCore, Multi Machineでスクレイピングする
- 6.1 Thread vs Multiprocessing
- 6.2 MultiprocessingをMulti Machineに拡張する

## 7. Practice 1, 無料のphotstockをスクレイピングして大量のフリー画像を集める
- 7.1 https://unsplash.com/
- 7.2 シンプルな全探索アルゴリズム（順序なし）

## 8. Practice 2, Bingの検索機能を利用して、大量のグラビア写真を集める

## 9. Practice 3, YouTubeの動画をIP制限を回避しながらダウンロードする

## 10. 閑話休題1, GCPで間違ったクエリを送って事故ったときの話 


# 1. 現代の最強の科学・意思決定法、定量分析
## 1.1 なぜ、定量分析が最強なのか
　エモい話をすると、世の中には簡単な法則で成り立っている事象と、複雑でカオス的な振る舞いをしる事象の２つに大きく二分できるます。  
簡単な法則とは、ニュートンの物理法則が適応できシンプルな演繹的な理論の導出が成立する世界になります。複雑でカオス的な振る舞いとは、木星の渦の模様や、何箇所の折り曲がるパーツで連結された振り子の振る舞いなどは鋭敏に初期値に依存し、解析的にはほとんど解くことが不可能になります。このカオス的な振る舞いは簡単な法則性が背景にあるだろうと仮定して、法則性を見つけ出そうとすると、思わぬお落とし穴にハマることがあり、代表的な例としてエセ科学や反ワクチンなどシンプルな法則性が後ろにあるような仮定をおいてしまう例などがあります。

<div align="center">
<img width="70%" src="https://upload.wikimedia.org/wikipedia/commons/1/17/Chaos_Theory_%26_Double_Pendulum_-_3.jpg">
<div>図x. 二重振り子の軌跡、この例ですら解析的に解くのは手計算では難しい</div>
</div>

では、ワクチンの副反応が実際に存在するとか、その影響度合いなどは結局複雑だからわからない、という疑問が出るかと思います。この課題に対して、答えを与えうるのが、定量分析になります。  

ワクチンの治療において２群にうまく恣意性がなく分けることができ、追跡調査をできたとして以下の結果が得られたとします。（データはフィクションです）


<div align="center">
<div>表 x. </div>
<img width="100%" src="https://www.dropbox.com/s/si8gl7sbt1zk8tr/%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%202019-12-31%2015.19.34.png?raw=1">

</div>

このデータが仮に得られたとしたら、どう判断すればよいでしょうか？  

ほとんど発生確率に差がないことからこのワクチンでの副反応自体はあまり高くないことが伺えます。実際には、事象にはガウシアンノイズなどのランダムネスが入り、こんなきれいな結果にはなりませんが、サンプルしたサイズに対して確率的に許容できる幅があり、その範囲を逸脱しなければ、差がないと言えます。

この結果を通して統計学が大切だという点も言えますが、もっともこの著書で言いたいのは、定量化、つまりデータを大量に束ねて大きな数にすることである程度の真実が初めて見えていくる、ということになります。Twitterなどでは、反ワクチンと呼ばれる方々が息子・娘や親戚や友達が副反応で今も苦しんでいる、という一部の証言から一般化した意見をそのまま鵜呑みにすればいいわではないわけです。

人間の本能により、原因と結果には単純でわかりやすいロジックを当てはめそうになります。それというのも、もう一つの人間の本能に腹落ちすること、納得することが大切であるというもう一つの本能があり、これにより事実の誤謬が世の中にはびこる結果になっています。

現代はインターネットにより誰もが手軽に様々な情報を手に入れる事が可能になりました。専門のサイト、サービスやSNSなどに多くの人間が様々なことを報告しています。これらの情報を束ねると手軽に真実がわかることがあります。正しい情報とはそれだけで皆さんの判断にプラスの影響をもたらしますし、世界を見る視野を正しく広げる一助にもなります。そんなわけで、"Practical Data Science and Data Engineering Vol.1" ではスクレイピングのテクニックについてお伝えしていこうと思います。 


# 2.  データを集める手段、スクレイピングの基礎

## 2.1 Requests + BeautifulSoupでスクレイピングする
スクレイピングの手法としてPythonで一般的である、requestsとBeautifulSoupのモジュールを利用したスクレイピングについて説明を行います。
環境はUbunut LinuxかMacOSを前提とします。Windowsをお使いの方はAWSかGCPで安いインスタンスを借りることができるので、Linuxをインストールして体験してみると良いと思います。

requestsはpythonで扱いにくかったhttp, httpsなどのアクセスを簡略化して様々なベストプラクティスを詰め込んだライブラリです。他にも様々なものがありますが、これが2020年現在、もっとも使いやすいものです。

BeautifulSoupとはhtmlパーサライブラリで、htmlは特定のフォーマットで記述された言語になり、機械で適切に処理させるにはパーサというものを介さないといけません。


### pipでのrequests, BeautifulSoupのインストール
Anacondaや特殊なPythonでは別のパッケージマネージャがありますが、pipで統一して話をす進めます。

```console
$ pip install requests bs4
```

<div align="center">
<img width="100%" src="https://www.dropbox.com/s/yr70t5z9ymj0z95/%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%202020-01-03%202.01.30.png?raw=1">
<div>図 x. インストール成功時に期待する画面</div>
</div>

### Pythonのファイルを書いて実行する

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


## 2.3 ハイパーリンクが作るネットワークは探索問題
  ハイパーリンクはネットワーク状に繋がったネットワークをいかに探索するか、という問題にも帰着できます。  

  例えば以下のような図のネットワークがあったとします。  

<div align="center">
<img width="100%" src="https://www.dropbox.com/s/07c2lcso578muxc/web.png?raw=1">
<div>図 x. インターネットのhyper linkの依存関係の例</div>
</div>

  このとき、どこからどのようにスクレイピングすれば、サイト全体を取得することが可能になるのでしょうか。  

  これには考え方がいくつかあって、全取得を前提とした深さをあまり考慮しない方法をご紹介します。  

  まず、エントリーポイントとなる、pageを一つ決め、そのページをスクレイピングします。そのスクレイピングしたページ内部にあるURLを取り出して、次のページをスクレイピングします。何度も同じページをスクレイピングしてもサイトの負荷になるし、意味がないデータが増えるだけです。  

  Pythonをイメージしたコードで表現すると、以下のようになります。  

```python
#!/usr/bin/env python3
urls = [entry_url]
all_urls = set()
while True:
  for url in urls:
	if exists_db(url):
	  continue
	html = get(url)
	store_db(url, html)
	for next_url in get_urls_from_html(html):
	  if next_url not in all_urls:
		all_urls.add(next_url)
  urls = list(all_urls)
```

  このようなコードが全探索を前提としたスクレイピングする際の最小のコードになります。  

  実際にはこのような理想通りに動作することはレアであり正しく動作させるために様々なヒューリスティックを入れることになります。  

  まずこのコードはシングルプロセスでしか動作させることができませんし、store_db, exists_dbで dbに大量にアクセスが発生します。  

  通常このようなユースケースではRDBは不向きで、例えばAWSのauroraのようなクエリ単位とスキャン量に対して課金されるようなDBの場合、一瞬で破産することが期待できます。  
  この問題を解決するには次の章の `3. 最強のDB、自作DBを作る` に記述します。 

### 2.3.1 幅優先探索・深さ優先探索・ビームサーチ
　ネットワーク状になっているので、探索方式がいくつか考えられます。  
例えば幅優先探索でスクレイピングする場合、浅い領域を優先してスクレイピングを継続します。できるだけ外部ドメインに出ないようにコードを取得するなど向いています。  

深さ優先探索になると、深い方を優先して探索するようになるのでネットワークから遠いところを優先してスクレイピングするようになります。URLが遠い場合などが有効です。 

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
    min_depth = min([url.depth for url in urls])
    urls = [url for url in urls if url.depth == min_depth]
```

  
