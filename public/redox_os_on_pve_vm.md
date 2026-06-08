---
title: "Redox OS on PVE VM"
emoji: "🌀"
type: "tech"
topics:
  - "qemu"
  - "pve"
  - "redox"
published: true
published_at: "2026-02-20 22:24"
---

# 対象読者
PVEについてQEMUやddコマンドを扱う技量のある方

# Redox OS とは
> Redox OSTM is a complete Unix-like microkernel-based operating system written in Rust, with a focus on security, reliability and safety. Offering source compatibility and a full set of programs, Redox is intended to be a complete alternative to Linux and BSD, in the cloud and on the desktop.

意訳：Redox OS(以下Redox)はUnixに似たマイクロカーネルなRustで書かれたOSです．セキュリティ・信頼性・安全性を重視しています．ソースコード互換性と充実したプログラムセットを備えたRedoxは，クラウドでもデスクトップでも，LinuxやBSDの完全な代替となることを目指しています．

ということで，Rust製のOSということです．
Rustの向いている用途として，巨大で速度と安全性の両立が挙げられると思っているので，これは適任じゃないかなと目を向けています．
(RustでKernelを自作しようかなと検索をしていたら見つけました)

# PVEでの難しいところ(TL;DR)

Redoxは仮想環境上と実機での動作が確認されているようです．
[公式ドキュメント-VM上での実行](https://doc.redox-os.org/book/running-vm.html)に仮想環境，VirtualBoxとQEMUでの実行の仕方がコマンド付きで載っています．
しかし，PVEとは少々異なるところがあって苦労したので，そこについて述べていきます．

## コマンドが`qm`じゃない

QEMUのコマンドには2つあって，`qm`コマンドとそれぞれのアーキテクチャのついた`qemu-system-x86_64`コマンドなどがあります．公式ドキュメントは`qemu-system-x86_64`コマンドにオプションを指定してVMを実行すると書いています．これをしたところ，PVEから走ったVMが認識されなくて，コンソールに入れなかったです．

## ディスクを認識しない

これ，私，10時間程度格闘して，最終的に，改善しなかった問題です．
`qm`コマンドから実行することを諦めて，私はPVEのGUIからVMを作って，Redoxのlivecdをマウントし，ようやっとPVEから確認できるRedoxのVMをつくりました．
ここから，ハードディスク上にRedoxをインストールできたら良いなって思いました．
[公式ドキュメント-ドライブにRedoxをインストール](https://doc.redox-os.org/book/installing.html)
このドキュメントにある`redox_installer_gui`というものを使ってみました．
ちなみにこの時点でRedox OSの側がlivecdとは別にVMに接続したHDDを認識していませんでした．
この状態でも`redox_installer_gui`はこのHDDを認識して，色々と書き込んで，bootableなディスクを作ってくれました．
(ちなみに`redox_installer_tui`コマンドはRedoxOSがHDDを認識していないせいなのか`no device found`と言ってこの時点でだめでした)

しかーし，bootableなはずのHDDの起動順位をPVE側で1番目にしても，ルートファイルシステムが存在しません．って言って，止まっちゃったんです．

ええ，もちろん設定を色々と変えました．HDDをSATAにしてみたり，SCSIにしてみたり，でも，この状態を変えることは無かったです．

マシーン設定を`i449fx`から`q35`にしたらlivecdの読み込みは早くなりましたが，オーディオデバイスのエラーでブートがストップしましたね．それ以外は，上に書いた状態から変化することはなかったです．

# どうやったら動いたか

結論，pveのシェルでpveのシステムにVMのドライブをマウントして，`dd`でRedox OSのイメージを流し込みました．イメージというのは，[公式ドキュメント-実機で動かす-BootableなUSBを作成](https://doc.redox-os.org/book/real-hardware.html#creating-a-bootable-usb-drive)に示されたリンクの中の，`harddrive.img.zst`とついたやつです．これは実際に動作しているディスクの中身まるままです．これをHDDの中に流し込むことで，動きます(当然)

## これにたどり着いた経緯

どうしてもVMに繋げたHDDをRedox OSから認識しない割に`redox_installer_gui`が成功したというログを出すので，これが非常に怪しいなと気になって，書き込んだHDDの中身を見てやろうと思ったのがきっかけです．しかし，Redox OSから認識していないので，`redoxfs`でマウントしてlsしまくるみたいなことはできません．
なので，pveのシステムのコマンドを使ってVMに繋げた仮想HDDの中身を覗いてやろうと思ったのです．
```bash
# fdisk -l /dev/pve/vm-104-disk-0
Disk /dev/pve/vm-104-disk-0: 32 GiB, 34359738368 bytes, 67108864 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 65536 bytes / 65536 bytes
Disklabel type: gpt
Disk identifier: EF3ABDF1-F2AB-419E-BD11-102BE79A0040
Device                   Start      End  Sectors  Size Type
/dev/pve/vm-104-disk-0p1    34     2047     2014 1007K BIOS boot
/dev/pve/vm-104-disk-0p2  2048     4095     2048    1M EFI System
/dev/pve/vm-104-disk-0p3  4096 67106815 67102720   32G Linux filesystem

Partition 1 does not start on physical sector boundary.
```
という応答が返ってきました．ちなみにredoxを入れているVMのidは104です．
どうやら本当に書き込みは成功しているみたいです．
~~もうめんどくさいからGentooみたいに手動でやらせてくれ~~
`hexdump`の結果も
```bash
00000000  52 65 64 6f 78 46 53 00  06 00 00 00 00 00 00 00 |RedoxFS.........|
```
みたいな感じでした．SeaBIOSなのでEFIシステムいらない気が……
でも一個気になる結果が
```
# strings /tmp/mbr.bin
}fAf
?wlf
wcf=
Stage
ERROR
```
ということで，どうやらRedox OSのブートローダーが上手く入ってくれなかったみたいです．
(GRUBも使えるようにしといてほしい．設定次第では使えるのかな？)

みたいなことがあって，じゃあもう折角マウントしてるしddで流し込むかって事になりました．