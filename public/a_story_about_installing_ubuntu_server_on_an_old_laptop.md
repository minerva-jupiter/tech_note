---
title: "古いLaptopにUbuntuServerを入れた話"
emoji: "💻"
type: "idea"
topics:
  - "laptop"
  - "ubnutuserver"
  - "used"
published: true
published_at: "2025-07-30 07:59"
---

# 想定する読者
暇つぶしに、他人のPCのセットアップを見学したい方
# 経緯
Gentoo OSなどのインストールに挑戦した私であったが、Wi-Fi cardのドライバーの入れ方がわからない等々の問題があったので、結局のところUbuntuに戻って来ることにした。

けれども、GNOMEが入っているUbuntuを私などが好くわけがないので、今回はGUI系統の一切入っていないUbuntuとして、UbuntuServerをインストールして、好き勝手にアプリケーションを入れていってしまおうという魂胆である。

# UbuntuServerのインストール
とりあえずインストールする。

UbuntuServerのサイトからisoをダウンロードしてきて、rufusでUSBに焼いて、インストール。

TUIでとっても簡単。W-Fiの設定すらできてしまう。

Gentooから来た人からすると、非常に早くて快適。中で何をやっているのか見ることができないので、ちょっと残念な気もするが。

# 使うアプリをインストール
## DNS(不要になった手順)
DNSを設定していないと、github.comが解決されない問題があったので(google.com等は解決される)、/etc/systemd/resolved.confを書き換え。DNS=1.1.1.2 1.0.0.2

++追記
RouterのデフォルトDNSを上記に変更したので、この手順は不要になった++

# NetworkManager
UbuntuServerのデフォルトで、systemd-networkdが使われているけれど、設定とかがダルいので、NetworkManagerを使います。(甘え)

```
sudo apt install network-manager && vi /etc/netplan/50-cloud-init.yaml
```
して、
```
renderer: NetworkManager
```
をnetwork:2の下に明記

それから
```
sudo systemctl disable systemd-networkd
```
する。

近頃の大学ネットは不安定で、繋がらないことも多々あるので、wait-online系を切っとくと良いかな。

nmtuiは便利だけど、nmcliを使う必要のある設定をば一つ。 
```
sudo nmcli connection show #接続一覧
```
```
sudo nmcli connection show "{接続機器名}" | grep metric #メトリック値確認
```
```
sudo nmcli connection modify "{接続機器名}" ipv4.route-metric {メトリック値}
```
```
sudo nmcli connection up "{接続機器名}"
```
で、メトリックを適切に設定してあげないと、nmtuiからは全部-1になって、不安定な大学ネットに繋がっては切れを繰り返してしまう。

## GUI関連
```
xserver-xorg xinit xterm i3 feh
```

ターミナルはxtermじゃなくていいと思うけど、最初にxtermがないよって言われた記憶があったので、とりあえず入れてるだけ。

i3のconfigファイルは私のgitに保存してるのを持ってきます。

fehはwallpaperの画像を表示するためのものです。

## Font
私はプログラマ用のフォントの可視性が非常に好きなのでMoralerspaceNeonNF-Regularを使用します。
最近は資料作りもするので、Noto Sans JPもいれてますね。

インストールは.ttfファイルを~/.fontsフォルダーに入れるだけ。

## IME
```
fcitx-mozc fcitx-skk
```
fcitxはモダンで設定がしやすくて、ありがたい。skkを(お試し)しているので、入れた。まだ設定はしていない。

## apt mirrorの選定
安定性のいらない、Laptop環境だからこそ、apt mirrorは速いのにしたい！
私はicscoeを使わせてもらってます
```
sudo sed -i.bak -r 's@http://(jp\.)?archive\.ubuntu\.com/ubuntu/?@https://ftp.udx.icscoe.jp/Linux/ubuntu/@g' /etc/apt/sources.list.d/ubuntu.sources
```

## Audio
音声出力に関係した部分を設定する。

```
sudo apt install alsa-base pulseaudio pipewire pulseaudio-modules-bluetooth
```
```
sudo adduser {username} audio
```
再起動したら、音が出るようになってるはず。

alsaだけだと不便な部分があったので、pulseAudioとPipeWireもいれてる。PipeWireだけにしたかったけれど、ms-edgeくんがPipeWire Onlyだと動かなかったので致し方なく。

## themeの設定
なんか一括で変更できるsystem themeなるものは存在せず、そこから取得してくる系はデフォのlightテーマになりやがるので、edgeとxtermは強制でテーマを変えた。

## Terminalの選定
もともとは、デフォルトのXtermを使っていたのだけど、なんだか使い心地が悪かったので、変更しました。
私はRust大好き人間なので、Alacrittyを導入しました。Ubuntuのaptリポジトリに登録されてたのでsudo apt install alacrittyと入力するだけで終わりました。あとはi3のコンフィグを書き換えてexec alacrittyにしただけです。かんたんですね。