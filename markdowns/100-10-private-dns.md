## 10. 閑話休題2, リクエストが多すぎるとDNSが応答しなくなる
膨大な通信を行うと、Googleの `8.8.8.8` やCloudFlareの `1.1.1.1` などにアクセスしてドメインを解決するのはかなりのコストであり、家や会社のルータでは膨大なリクエストを捌くにあたってすべてをGoogleやCloudFlareに投げると、だんだんDNSが応答してくれなくなってきます。 

そのため、自前で簡単なDNSサーバを立てたほうがいいのですが、何年前か調べたDNSサーバの立て方が、実に簡単になっていたのでご紹介します。  

```console
$ docker run -d --restart=always \
  --publish 53:53/tcp --publish 53:53/udp --publish 10000:10000/tcp \
  --volume /srv/docker/bind:/data \
  sameersbn/bind:9.11.3-20190706
```
なお、Ubuntuなどではデフォルトでport 53を専有するサービスがあるのでこれをstopしておく必要があることがあります。  

```console
$ sudo systemctl stop systemd-resolved
$ sudo ln -sf /run/systemd/resolve/resolv.conf /etc/resolv.conf
```

これで何かドメインが与えられたときに、解決が自分のネットワーク上のDNSを見るか（最初の一回だけキャッシュするために遅くなるが以降は早い）、毎回GoogleかCloudFlareに聞くかなど変わってくるので、総合的に自分のローカル環境にdockerなどでいいのでbind9を入れておくと便利で、高速です。  

