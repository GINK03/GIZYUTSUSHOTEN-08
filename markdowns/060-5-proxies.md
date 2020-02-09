## 5. Depth 2, IPを偽装する
最近のGoogle社のサービスや、GAFAなどの強いプレイヤーのサービスは機械学習によるBANが活発に行われていますが、今も現在もおそらく最強の不正利用（と彼らが定義する）の判別は、IPアドレスになります。  

IPアドレスを偽装したり変えたりするのは、かなり重要で、一発アウト制をとっているサービスさんだと、復旧は事実上不可能になり、そのサービスに二度とアクセスできなくなります。  

私の経験を踏まえつつ、どの程度まではやっていいのか、どこからはダメなのか、駄目ならどう駄目なのか、お伝えしていこうと思います。

### 5.1 プロキシサーバを立ててアクセス
最も簡単なのが何らかのクラウド業者にLinuxのインスタンスを借りて、プロキシサーバを立てて、そこ経由でアクセスすることです。  

有名なプロキシソフトウェアは `squid` などがありこれをdockerで利用した際の利用法について述べます。  

dockerはLinuxのコンテナという技術を用いて必要なソフトウェアの依存や環境などをまとめて、パッケージ化して、どのLinux環境でも再現できるようにしたものです。  

例えば以下のコマンドで `squid` というソフトウェアのパスワード等の認証なしのプロキシサーバを建てることができます。  

```console
$ docker run -d -p 3128:3128 nardtree/squid
```

dockerが正しくインストールされていれば、これだけでOKです。とても簡単ですね。 

これを利用して、curlコマンド等でアクセスするには以下のようになります。  

```console
$ curl  --proxy http://user:user@133.130.97.98:3128/ https://ifconfig.co/
133.130.97.98
$ curl https://ifconfig.co/
27.131.***.*** # オリジナルの私のIPが出てしまう
```

IPアドレスは適宜インストールしたサーバのグローバルIPアドレスと読み替えてください。

単純な発想では、これをGCPやAWSやGMOクラウドやconohaの一番安価なインスタンスにデプロイしてIPを払い出せば、無限にアクセス制限が回避できることになります。しかし、本当にクラウド業者がそんなことを考えていないなどありうるのでしょうか？


pythonのrequestsでプロキシ経由で悪世するにはこのようなコードで実行する事ができます。  

```python
# proxy の例

import requests

proxies = {
        "https": "http://user:user@133.130.97.98:3128/",
        "http": "http://user:user@133.130.97.98:3128/"
}
r = requests.get('https://ifconfig.co/', proxies=proxies, verify=False)

print(r.text)
```

### 5.1.2 閑話休題, AWSアカウントをバンされる
インセキュアなsquidなどを利用して、AWSで安いインスタンスにdockerを立ててプロキシサーバにしていると、当然、AWSとしては貴重なIPv4をブラックリストに入れられるリスクが増加するので許容できるものではありません。  

ある日、私は個人で契約していたAWSがなんどインスタンスを立てても数秒でshutdownされてしまう謎の現象に遭遇しました。ドキュメントを漁っても該当する設定は存在しなく、有償サポートに賭けるしかない状況です。  

いくらかの節制の結果、サポート一回分の費用を捻出した私は、有償サポートとは思えない冷たい一言を投げらます。  

「不正利用の疑いがあるので、インスタンスの操作はできない。復旧の時期も、いつ利用再開になるのかも答えられない」　

目の前が真っ暗になるようでした。

インセキュアで海外の攻撃者や第三者が利用した可能性が高いことが事態を余計に混迷させました。

幸いにして、趣味のwebサービスや分析用インスタンスは、GCP, AWSどちらに依存することなくdocker-composeで済む用なモジュール単位でwebサービスを作っていたので事なきを得ましたが、AWSのサービスに結合したものを作っていたり、動かす金額が大きいと個人で責任を取れなくなってきます。

### 5.2 公開プロキシ経由でのアクセス
全て自分でサーバを建ててアクセス、を行わなくても、Proxyサーバ自体は多くの人にいろんな政治的・思想的理由があり、それを補助するためにあらゆる地域と国家で建てられていたりします。  

例えば, `spys.one/en` では、ロシアのサーバに様々なproxyが公開されています。 

<div align="center">
  <img width="500px" src="https://www.dropbox.com/s/db9y0cr8nshwk37/%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%202020-01-17%2023.45.29.png?raw=1">
  <div> 図.X spys.one/en</div>
</div>

このサイトでは、常にフレッシュなプロキシサーバが公開されて、IPバンリスクが高く、IPがすぐ何らかの理由でバンされてしまったとしても、すぐ次のプロキシに乗り換えることができます。  

このバンされたらIPを乗り換える、ということを自動化しようとすると、実はハードルが一箇所あります。  
<div align="center">
  <img width="500px" src="https://www.dropbox.com/s/dzom1mq0rryxu3s/%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%202020-01-18%2011.56.46.png?raw=1">
  <div> 図.X Proxyのポートの表示が実は、JavaScriptの演算で得られる</div>
</div>
JavaScriptでPortが描画されている、かつ、変数の定義がこの面だけは解析的に出すのが難しめの競プロのようになってしまっています。

概して、このような障害がある際に、有効な方法はchromeのheadlessブラウザによるアクセスであり、JavaScriptを実行させてからhtmlをパースさせるという方法が有効です。  

以下にchromedriverを用いて、google-chromeをheadlessで動作させて、`spys.one/en` からプロキシのリストを取得するコードを例示します。  

```python
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time
import re
import requests
from bs4 import BeautifulSoup
import json

options = Options()
options.add_argument('--headless')
options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36")
options.add_argument(f"user-data-dir=/tmp/work")
options.add_argument('lang=ja')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--window-size=1080,10800")
driver = webdriver.Chrome(options=options,
                          executable_path='/usr/bin/chromedriver')

proxies = set()
for proxy_src in ['http://spys.one/free-proxy-list/JP/', 'http://spys.one/en/free-proxy-list/']:
    driver.get('http://spys.one/en/free-proxy-list/')
    time.sleep(1.0)
    driver.find_element_by_xpath(
        "//select[@name='xpp']/option[@value='5']").click()
    time.sleep(1.0)
    html = driver.page_source
    soup = BeautifulSoup(html)
    [s.extract() for s in soup('script')]
    #print(soup.title.text)
    for tr in soup.find_all('tr'):
        if len(tr.find_all('td')) == 10:
            tds = tr.find_all('td')
            ip_port = tds[0].text.strip()
            protocol = re.sub(
                r'\(.*?\)', '', tds[1].text.strip()).lower().strip()
            proxy = f'{protocol}://{ip_port}'
            proxies.add(proxy)
proxies = list(proxies)

with open('proxies.json', 'w') as fp:
    json.dump(proxies, fp, indent=2)

```

### 5.3 tor経由でのアクセス

よほどのことがない限りtorは使う機会が無いのですが、ダークウェブを定量的な視点で分析するなどのモチベーションがあればユースケースとして最適です。  

tor経由でアクセスするとほぼ通信元がたどれなくなるという匿名性がありいます。  

dockerを用いたサーバの立て方、環境変数を用いたアクセスの仕方、pythonのモジュール内で指定して悪世する方法をお伝えします。

#### 5.3.1 Dockerでtorのsocks5 proxyサーバを立てる

`socks5` というプロトコルでtorネットワーク経由でアクセスするproxyサーバを建てることができます。  

サーバとなるLinuxなどで、以下のコマンドを入力するだけでサーバーが立ち上がります。

```console
$ docker run -d --restart=always -p 0.0.0.0:9150:9150 peterdavehello/tor-socks-proxy:latest 
```

conoha(IP:133.130.97.98)というクラウドサービスにサーバを建てて自宅のMac(IP:126.140.215.0)からアクセスして、IPアドレス確認サービスにIPを問い合わせると以下の結果が帰ってきました。

```console
$ curl --socks5-hostname 133.130.97.98:9150 https://ipinfo.tw/ip
209.95.51.11
```

このIPを `whois` で確認すると以下のような結果が得られ、全く関係のないIP担っていることがわかります。（headerの特定可能な情報も削っているようです）
```console
OrgName:        Hosting Services, Inc.
OrgId:          HOSTI-20
Address:        517 W 100 N STE 225
City:           Providence
StateProv:      UT
PostalCode:     84332
Country:        US
RegDate:        2008-03-03
Updated:        2017-02-08
Ref:            https://rdap.arin.net/registry/entity/HOSTI-20
```

#### 5.3.2 環境変数でsocks5を指定する
環境変数に設定して用いるとproxyを広いレンジで用いることができて便利です。  
torのプロトコルはsocks5hというものになっていて、curlでは用いることができるが、wgetはできないなどの微妙な成約があります。 

```console
$ export http_proxy=socks5h://133.130.97.98:9150
$ export https_proxy=socks5h://133.130.97.98:9150
$ export all_proxy=socks5h://133.130.97.98:9150
```

#### 5.3.3 Pythonでsocks5を指定する

**requestsで用いるとき** 
socksのサポートをpythonで行うため、このようなモジュールをインストールする必要があります。  
```console
$ pip install "requests[socks]"
```
pythonは以下のようなコードが期待されます。
```python
import requests
proxies=dict(http='socks5h://133.130.97.98:9150',
             https='socks5h://133.130.97.98:9150')
r = requests.get('https://ipinfo.tw/ip', proxies=proxies)
print(r.text)
```
出力は `109.70.100.30` でした。このIPの所有者は `TOR-EXIT--FOUNDATION-FOR-APPLIED-PRIVACY` ですので、無事隠蔽されました。   
