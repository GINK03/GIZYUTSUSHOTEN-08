## ４. Depth 1, UserAngent, Referrer を偽装する

ブラウザには固有で、このブラウザの種類からアクセスした、とこちらから宣言するためのheader情報が付きます。  

requestsだとこのように書くことでUserAgentを変更することができます
```python
import requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
}
r = requests.get('https://www.yahoo.co.jp/', headers=headers)
```

このようにすることで、Linux上で動作するPythonでアクセスしているはずですが、MacOS XのGoogle Chromeでアクセスしたことになります。  


### 4.1 自分が使っているUserAgentを確認する

Googleで検索する際に、"my useragent"と入力すると、Googleが今使っているブラウザのUserAgentを教えてくれます。  

<div align="center">
  <img width="400px" src="https://www.dropbox.com/s/p742eoapdnwi14d/Screen%20Shot%202020-01-14%20at%2015.25.57.png?raw=1">
  <div> 図. 1 Googleで今使っているブラウザのUserAgentを知ることができる </div>
</div>

### 4.2 サイト管理人格に配慮する

サイト管理人格（個人や法人を想定しています）に対して、自分が行っているスクレイピング等の行為に対してフィードバックを得るチャンネルをUserAgentに組み込むことができます。 

UserAgentやIPなどは、基本的にはアクセスログとして残り、サービスの改善に役立つので、分析対象になっていることが多く、ログに自らの意思を組み込むことで、平等性と透明性を確保することができます。  

例えばこの例では、これが誰かのスクレパーであること、サポートを得るためのURLを乗せるなどで、意図しないアクセスであっても、穏便に済ますことができます。  
```python
import requests
headers = {
    'User-Agent': "ozilla/5.0 (Linux; Analytics) [This is a scraper of nardtree's analytics. htts://gink03.github.io/]"
}
r = requests.get('https://www.yahoo.co.jp/', headers=headers)
```

### 4.3 Referrerを偽装する

Referrerは翌千になんのサイトを見ていたかを示すものです。 

現在、Referrerが要素がクローラーであるかどうかを判断する要素にはなりませんが、昔からあるレガシーなクローラーを弾く作法の一つに、Referreで判断するサイトもあります。  

この場合、requestsなどのアクセスにheader情報をつけることで、アクセスすることが可能になります。  

Refererに何かURLを入れるとそのURLから来たという意思表示になるというわけです。  

```python
# referrerを付ける例
import requests
from bs4 import BeautifulSoup

headers = {'referer':'https://google.com',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}
r = requests.get('https://www.yahoo.co.jp/', headers=headers)
```
