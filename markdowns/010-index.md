# 目次

## 1. 現代の最強の科学・意思決定法、定量分析
 - 1.1 なぜ、定量分析が最強なのか

## 2.  データを集める手段、スクレイピングの基礎
 - 2.1 Requests + BeautifulSoupでスクレイピングする
 - 2.2 Google Chrome + Seleniumでスクレイピングする
 - 2.2.1 Pixivを例に取る
 - 2.2.2 Pixivを例に取る: Google Chrome + Seleniumでデータを取得する
 - 2.2.3 Pixivを例に取る: 自動でログインしてデータを取得する
 - 2.3 ハイパーリンクが作るネットワークは探索問題
 - 2.3.1 幅優先探索・深さ優先探索・ビームサーチ
 - 2.4 法的問題

## 3. 最強のDB、自作DBを作る
- 3.1 自作KVSとその関連
- 3.2 最強のDBは結局ファイルシステム

## ４. Depth 1, UserAngent, Referrer を偽装する
- 4.1 自分が使っているUserAgentを確認する
- 4.2 サイト管理人格に配慮する
- 4.3 Referrerを偽装する

## 5. Depth 2, IPを偽装する
- 5.1 プロキシサーバを立ててアクセス
- 5.1.2 閑話休題, AWSアカウントをバンされる
- 5.2 公開プロキシ経由でのアクセス
- 5.3 tor経由でのアクセス
- 5.3.1 Dockerでtorのsocks5 proxyサーバを立てる
- 5.3.2 環境変数でsocks5を指定する
- 5.3.3 pythonでsocks5を指定する

## 6. Depth 3, MultiCore, Multi Machineでスクレイピングする
- 6.1 Thread vs Multiprocessing
- 6.2 MultiprocessingをMulti Machineに拡張

## 7. フェアネスを考慮したスクレイピング
- 7.1 ユニフォーム分布に基づいたドメイン選択 

## 8. 練習 
### 8.1 Practice 1, 無料のphotstockをスクレイピングして大量のフリー画像を集める
- 8.1.1 https://unsplash.com/
- 8.1.2 シンプルな全探索

### 8.2 Practice 3, YouTubeの動画をダウンロードする
 - 8.2.1 YouTubeの動画のダウンロードに便利な `youtube-dl`
 - 8.2.2 IPを使い潰すしかなさそう

## 9. 閑話休題1, スクレイピングするのにおすすめのプロバイダとOS
 - おすすめを紹介

## 10. 閑話休題2, リクエストが多すぎるとDNSが応答しなくなる
 - 解決法
