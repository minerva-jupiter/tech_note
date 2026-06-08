---
title: "Blazor WebAssembly on Cloudflare Pages"
emoji: "💨"
type: "tech"
topics:
  - "csharp"
  - "blazor"
  - "cloudflarepages"
published: true
published_at: "2025-07-28 01:06"
---

# TL;DL
[リポジトリ](https://github.com/minerva-jupiter/webtools-mj)
ビルド設定は

|key|value|
|-|-|
|ビルドコマンド|chmod +x build.sh && ./build.sh|
|ビルド出力|output/wwwroot|

/build.sh
```sh
#!/bin/sh
curl -sSL https://dot.net/v1/dotnet-install.sh > dotnet-install.sh
chmod +x dotnet-install.sh
./dotnet-install.sh -c 9.0 -InstallDir ./dotnet
./dotnet/dotnet --version
./dotnet/dotnet publish -c Release -o output
```
## 参考
- [CloudflareのBlazor WebAssemblyドキュメント](https://developers.cloudflare.com/pages/framework-guides/deploy-a-blazor-site/)
- [Permission denied on build scriptへの回答](https://community.cloudflare.com/t/permission-denied-on-build-script/295840/3)
# 経緯
WASMを使ってランダムパスワードジェネレーターを作りたいなと思ったので、このプロジェクトが始まりました。最初はNext.js + WASM(Rust) on Cloudflareしようと思ってました。
`create next app`して、cloudflare pagesに入れたら`nodejs_compat`がいるよって言われた。
そこでworkersに入れようと思ったら、純粋なnext.jsとWASMの扱いが違ったので、cloudflareに適したWASMを含むセットアップを探してWranglerにたどり着いた。
ただ、WranglerがWindowsだとうまく動いてくれなかったので、断念。
Windowsのpowershellで動かすとWranglerが`C:\`みたいなパスはだめだからWSLで動かしてねって言われて、WSLで動かすと「そのファイルパスは許可してないからcmd.exeで実行するね。あとついでにファイルパスは標準の'C:\Windows\'以下だよ」って言われて、permissionエラー(当然)で、諦めて退散しました。(ここまで4日かかった)
ということで、私は諦めて、サークルの先輩が使ってたBlazorでWASMを実現することにしました。~~ほんとはRustを使いたかったんだけど。~~

# 手順
## 使用環境
|key|value|
|-|-|
|IDE|VisualStudio2022|
|ソースコード管理|GitHub|
|ライセンス|MIT|
|デプロイ先|Cloudflare Pages|

## Create Blazor Project
VisualStudio(以下VSと略)を起動して`新規プロジェクトを作成`から`Blazor WebAssembly スタンドアロン アプリ`を選択して、作成。残りはよしなに。
`プログレッシブWebアプリケーション`って項目があって、何かと思って調べたら、ネイティブアプリみたいに独立したウィンドウとして表示できる機能？みたい。間違ってたらごめんなさい。Next.jsだったかReactでも似たような機能あるよね。アプリとしてインストールってやつ。

## Setting up git
VSはgit clientも付いている超優秀な子です。上のツールバーの`Git`項目にマウスを持っていくと、リポジトリを作るところまでやってくれます。昔はこんな項目があった覚えがないのだけど。

## Push to GitHub
上の手順でやると、勝手にコミットメッセージ込みでプッシュしてくれます。~~しやがります~~
`プロジェクト ファイルを追加します。`というコミットメッセージ付きです。~~日本語コミットメッセージやめて~~
ただ、VSのデフォルト設定だと`master`ブランチが作られます。ただ、近年の差別的な言葉を避ける運動により`main`ブランチにしましょうという流れらしいです。
個人的にはbridgeのslaveとか言ったりするし分かり易い表現だと思うので、すべて変える必要があるとは思いませんが、ブランチに関してはmasterでもmainでも可用性に差があるように感じないので`main`ブランチにしときます。

## Ready for deploy
Cloudflare Pagesにデプロイするために必要な手順がひとつ残っています。
参考に挙げた[CloudflareドキュメントCreate the build script](https://developers.cloudflare.com/pages/framework-guides/deploy-a-blazor-site/#create-the-build-script)に書いてあるとおり、ビルド用のスクリプトを書きます。一応再掲。
```sh
#!/bin/sh
curl -sSL https://dot.net/v1/dotnet-install.sh > dotnet-install.sh
chmod +x dotnet-install.sh
./dotnet-install.sh -c 9.0 -InstallDir ./dotnet
./dotnet/dotnet --version
./dotnet/dotnet publish -c Release -o output
```
なお、4行目の9.0のところは各々が新規プロジェクト作成の際に選択したSDKバージョンを入れてください。
Window上のneovimを使ってこれを書いたところ、なんかバグったので、WSLでnanoやらvimやら使って書くことをおすすめします。
書けたら、そのファイルも含めてGitHubに上げときます。上げるっていうのは含めてコミットするわけで...VSのgit clientはcliにラッパーが被さった程度のものなので、プロジェクトのルートディレクトリ内にスクリプトを置いとけば、Add&Commitする欄に出てくるので、"適当に"コミットメッセージを書いてCommit&&Pushします。

## いざDeploy
CloudflareにログインしてDashboardからPages(表示は`コンピューティング(Workers)`)に飛んで、作成を押して、プロジェクトのリポジトリを選択します。
ビルドコマンドのところに"Cloudflareのドキュメント通りに"
|Configuration option|Value|
|-|-|
|Production branch|main|
|Build command|./build.sh|
|Build directory|output/wwwroot|
してみます。
```log
23:10:29.350	Executing user command: ./build.sh
23:10:29.358	/bin/sh: 1: ./build.sh: Permission denied
23:10:29.359	Failed: Error while executing user command. Exited with error code: 126
23:10:29.366	Failed: build command exited with code: 1
23:10:33.878	Failed: error occurred while running build command
```
らしいです。そう言えば公式ドキュメントに
> Your build.sh file needs to be executable for the build command to work. You can make it so by running chmod +x build.sh.

って書いてありました。ね。
### バカの遠回り
バカな私はローカルで`ls -l`してpermissionを確認し始めました。
```
-rwxrwxrwx 1 <user> <user> 1094 Jul 28 00:13 LICENSE.txt
-rwxrwxrwx 1 <user> <user>   13 Jul 27 22:36 README.md
-rwxrwxrwx 1 <user> <user>  223 Jul 27 23:12 build.sh
drwxrwxrwx 1 <user> <user> 4096 Jul 27 22:33 webtools-mj
-rwxrwxrwx 1 <user> <user> 1146 Jul 27 22:33 webtools-mj.sln
```
あれ、おかしいですね、実行権限どころか、他の権限まであるじゃないですか。
なんでだろうなと思いながら`chmod +x build.sh`を実行します。
まあ、何も変わるわけがなくてですね、英語の読み間違いかなと思って日本語に翻訳をかけました。
> ビルドコマンドを機能させるには、ファイルが実行可能である必要があります。実行することでそうすることができます. `build.sh chmod +x build.sh`

ん？じゃあ`build.sh chmod +x build.sh`を実行すればいいんだな？と思い、実行しました。
するとどうでしょう、ルートディレクトリ内に.NET SDKがインストールされました！
それをGitHubに上げて、Cloudflareがdeployしようとすると……
既に.NET SDKがあります！ってエラーが。まあ当然ですわな。
それから私は何をトチ狂ったか、インストールされている.NET SDKファイルらを削除してみたり、`build.sh`すら消してみたり色々とやりました。GitHubさん、本当にごめんなさい。
### 結局は……
そろそろ公式ドキュメントを信用しなくなってきた私はググりました。そして見つけたのです。
[Permission denied on build scriptへの回答](https://community.cloudflare.com/t/permission-denied-on-build-script/295840/3)
> The only way would be to change the build command from `./build.sh` to `chmod +x build.sh && ./build.sh`

天才か？
つまり、Cloudflareのサーバがgit cloneしてる時点でこっちのファイルのpermissionなんて向こうに関係ないわけでして、そのサーバ内でのpermissionを変更するにはこれしかないという、至極真っ当な答えでしたとさ。

|Configuration option|Value|
|-|-|
|Production branch|main|
|Build command|`chmod +x && ./build.sh`|
|Build directory|output/wwwroot|

## Deployの成功と今後
やっとのことでDeployが成功しましたとさ。
今後は、このWEBページの機能と見た目を開発していけたらいいなと思ってます。

# 反省
- 公式ドキュメントはきっちり読む(翻訳に頼らずに)
- 公式ドキュメントで詰まったらググってみてもよい
- 無知。よい勉強になりました

以上、長々と、私の右往左往の失敗談でした。