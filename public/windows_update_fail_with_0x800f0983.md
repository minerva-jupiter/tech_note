---
title: "Windows Update fail with 0x800f0983"
emoji: "🪟"
type: "tech"
topics:
  - "windows11"
  - "0x800f0983"
published: true
published_at: "2025-10-17 19:52"
---

# What is this article
これは、一人でWindowsを保守できる程度の技量を持ち合わせた人間向けの文章です。
Windows Updateが以下の文言と共に失敗しました。
```
Install error - 0x800f0983
```
今回はこれに関して収集した情報を書きます。
# 状況詳細
```
2025-10 Cumulative Update for Windows 11 Version 24H2 for x64-based Systems (KB5066835) (26100.6899)
```
install fail with this
```
Install error - 0x800f0983
```
- 以前にWindows Updateを停止しませんでした
- 前回の初期化から1年近く経っているので、そろそろ初期化の時期かもしれません
## device specification
```
Device name	DESKTOP-MINERVA
Processor	AMD Ryzen 9 3900XT 12-Core Processor            (3.80 GHz)
Installed RAM	32.0 GB
System type	64-bit operating system, x64-based processor
Pen and touch	No pen or touch input is available for this display
```
# 問題点
[ms QA](https://learn.microsoft.com/en-us/answers/questions/3891780/0x800f0983)
QAの記事にあるように
>エラー コード 0x800f0983 は、コンポーネント ストア (WinSxS) の破損を示します。

らしいです。
# solution 1 (DISM)
大人しくQAにあるコマンドを実行します。
```
Dism /Online /Cleanup-Image /StartComponentCleanup
```
私はtermにalacrittyを使っているのですが、権限昇格とかの機能がないので、sudoを使ったらfileのRL権限がないと怒られました。大人しくalacritty自体をRun as administorします。
なんか59.9%でスタックしてました。長いなぁと思ってたら100%に。やった！って思ったら75%くらいに巻き戻ってゆっくり進み始めました。なんだこりゃ。
```
Deployment Image Servicing and Management tool
Version: 10.0.26100.5074

Image Version: 10.0.26100.6584

[==========================100.0%==========================]
The operation completed successfully.
```
らしいので、健康にしていきます。
```
Dism /Online /Cleanup-Image /RestoreHealth
```
こんどはスムーズ
```
Deployment Image Servicing and Management tool
Version: 10.0.26100.5074

Image Version: 10.0.26100.6584

[==========================100.0%==========================] The restore operation completed successfully.
The operation completed successfully.
```
再起動します。
`Retry`します。
失敗します。
ま、Dismコマンドでうまくいったことなんて一度も無かったので、そうだよなって感じですね。
# solution 2 (Reinstall windows)
In settiong, System -> Recover -> Reinstall
でボタンをポチッとします。
あとは1.5時間くらい放置です。
壁紙が吹き飛んでましたが、他は設定が変わってるとかはなく、最新の状態になってました。
そういえば、Retryする前に候補に上がっていた25H2は設定のwin update画面からは見えなくなってますね。なんででしょう。
ま、治ったんで良かったです。
# 余談
WinSxSっていうのはWindowsの根幹のコンポーネントが入ってるフォルダーらしいのですが、中身(`C:\Windows\WinSxS\`)dllファイルしか見当たらないし、これをダウンロードし直すだけで良いような気もするんですけどね。Windowsは複雑怪奇。