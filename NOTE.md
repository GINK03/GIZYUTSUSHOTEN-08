# 技術書典8の製作物を無料公開します

お久しぶりです。
私生活で反省することが多く、心身ともに疲弊し、しばらくTwitterやブログなど対外的なアウトプットをお休みしていました。

技術書典8で復活を遂げようと思っていたのですが、コロナのために開催がなくなってしまいました。

いろいろな人を頼り、助けてもらい、多くの人の力で作ったコンテンツであったので、死蔵させいても仕方がないと思い、公開します。

サークル名は `Practical Data Science and Data Engineering` で、いかにも、、、な名前にしました。あまりひねったり、ギャグに走るのは性分でないためです。

ここのGitHubからダイレクトにPDFをダウンロードすることもできますが、もしnardtreeにお茶でも奢っていいと言う優しい方がいらしたら、BOOTHのコンテンツを販売しているサイトから購入していただけると幸いです。

また、著作権は主張したいのですが、GitHubからダウンロードしたコンテンツを教育目的や学術目的でシェアする分には構いませんので自由に使っていただけると幸いです。

**GitHub版(無料)**  
<div align="center">
  <a href="https://github.com/GINK03/GIZYUTSUSHOTEN-08/blob/master/GIZYUTSUSHOTEN-08.pdf">
   <img src="https://user-images.githubusercontent.com/4949982/75841165-624e2e80-5e10-11ea-93a4-3e685087a26d.png">
  </a>
</div>


**BOOTHでの販売**  
<div align="center">
  <a href="https://twovolts.booth.pm/items/1880819">
   <img src="https://user-images.githubusercontent.com/4949982/75841177-67ab7900-5e10-11ea-8e3a-06a5a3d6d4e6.png">
  </a>
</div>


私の印刷所に持ち込むPDFの作り方が全てmarkdown + OSSだけで完結したのでその方法についてもご紹介します。


## メジャーなOSSだけで日光印刷さんのレビューをクリアできた

最初はAdobeの製品であったり、一部の使う機会が少ないソフトを学ばなくてはいけないのか、、、と学習コストを心配していたのですが、pandocとgoogle chrome + nodejsだけでなんとか日光印刷さんのレビューをクリアする程度には品質を確保できたのでその方法をご紹介します。
MacOSで作成しましたが、Linuxでもいけるはずです。

## Markdownで資料をつくる

 GitHubやVS CodeのインタラクティブにMarkdownを編集できるモードで、コンテンツを作成します。MarkdownはGithubのREADMEなどを作成するときに使用できるフォーマットで、プログラムを作成する機会のある人なら大体書けると思います。

## PandocでMarkdownをデザイン付きHTMLにコンパイルする

Pandocを製本のように使う人は、あまり国内で使用している人はいないようでしたが、Markdown形式をHTML形式に変換する際にたいへん便利です。また、この変換にはCSSを指定することができ、GitHubのウェブサイトのようにコードに対してシンタックスハイライトなどを行うことも可能です。

```console
 $ pandoc \
      -s ${インプットファイル.md} \
      -f markdown \
      --metadata title="Practical Data Science & Engineering Vol.1" \
      -c ${シンタックスハイライト.css} \
      -o ${出力ファイル名.html}
```

このようなコマンドで簡単にMarkdownをシンタックスハイライト付きのHTML化することができます。

## HTMLをPDFに変換する

最もめんどくさく、かつ、辛いのがPDF化の作業なのですが、海外のサイトなどを見ているとhtmlでフォーマットされたコンテンツをPDF化するにはGoogle ChromeのPDF生成機能を用いるのがよいとされていることが多いようです。

**Google Chromeをデバッグモードで起動する**   

```console
 $ /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --headless --remote-debugging-port=9222
```

実際にGUIで操作するスタイルでは無くCUIで操作するため、Google Chromeをデバッグモードで起動する必要があります。

Debug Modeで起動したGoogle Chromeにhtmlをpdfに変換する命令を行う

NodeJSをインストールしたのち、NodeJSからGoogle Chromeを操作するモジュールである、 [chrome-remote-interface](https://github.com/cyrus-and/chrome-remote-interface)をインストールします。

chrome-remote-interface経由で以下のようなスクリプトを介してPDFに変換すると、PDFの各ページの余白やヘッダーやフッターの幅を調整したり、ページ番号を入れたりすることができます。
（印刷会社の日光企画さんに持ち込んで色々ヒアリングしたところ、ページナンバーを入れるのは必須であると言うことでした。）

```js
    #!/usr/bin/env node
    const homedir = require('os').homedir();
    const CDP = require(homedir+'/.config/yarn/global/node_modules/chrome-remote-interface/');
    const fs = require('fs');
    
    const port = process.argv[2];
    const htmlFilePath = process.argv[3];
    const pdfFilePath = process.argv[4];
    
    (async function() {
            const protocol = await CDP({port: port});
            // Extract the DevTools protocol domains we need and enable them.
            // See API docs: https://chromedevtools.github.io/devtools-protocol/
            const {Page} = protocol;
            await Page.enable();
    
            Page.loadEventFired(function () {
                    console.log("Waiting 100ms just to be sure.")
                    setTimeout(function () {
                            //https://chromedevtools.github.io/devtools-protocol/tot/Page/#method-printToPDF
                            console.log("Printing...")
                            Page.printToPDF({
                                    marginTop: 0.8,
                                    marginBottom: 0.2,
                                    displayHeaderFooter: true,
                                    headerTemplate: '<div></div>',
                                    footerTemplate: '<div class="text center"><span class="pageNumber"></span></div>',
                            }).then((base64EncodedPdf) => {
                                    fs.writeFileSync(pdfFilePath, Buffer.from(base64EncodedPdf.data, 'base64'), 'utf8');
                                    console.log("Done")
                                    protocol.close();
                            });
                    }, 100);
            });
    
            Page.navigate({url: 'file://'+htmlFilePath});
    })();
```

このJavaScritpをprint-via-chrome.jsとして、実行権限を付与すると、実行できるようになるので、このように引数にchromeのデバッグポート、インプットのhtml、出力ファイル名を引数にして実行するとpdfを得ることができます。

```console
 $ print-via-chrome.js 9222 ${HTML_FILE} ${PDF_FILE}
```

## 一連のコード

`DocCompile.py` というファイルを作成して、pandocでカバーしきれないHTML, CSSの編集と、Google Chromeに印刷させる一連のフローをPython Scriptにラップアップしました。
自分の環境に書き換えて用いていただけると幸いです。

https://github.com/GINK03/GIZYUTSUSHOTEN-08


## 参考
 - MacでPandocを使ってMarkdownをpdfに変換 : https://note.nkmk.me/mac-pandoc-markdown-pdf-japanese/
 - GitHub-pandoc.css : https://gist.github.com/dashed/6714393#file-github-pandoc-css
 - ChromeDevTools : https://chromedevtools.github.io/devtools-protocol/tot/Page/
