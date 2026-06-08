---
title: "Stuck of Zed Remote"
emoji: "🙆"
type: "tech"
topics:
  - "remote"
  - "zed"
published: true
published_at: "2026-02-28 10:47"
---

# 想定読者
ZedのRemote機能の利用者

# 経緯(TL;DR)
インストーラのTUIで実機に`debian`をインストールし，その環境のコードを弄りたかったのでWindowsのZedからリモートとして接続しようとしました．
debianのインストール時，幾つかのライブラリを選択的に入れられるのですが，私はssh connectionのみを入れて，それ以外のdesktop env等は省きました．
`curl`も`net-tools`も入っていないまっさらなdebian環境にzedからリモートでつなごうとすると，バイナリのダウンロードが失敗しました．`curl`が必要みたいです．私は`wget`を使って色々とダウンロードしてたので気づきませんでした．それからbunのインストール用にと`unzip`もついでに入れて接続すると，サーバーのセットアップができたと言ったので早速，フォルダを追加しようとadd folderボタンを押してssh keyのパスワードを入れて……
ずっと`connecting`で止まってるんです．謎でした．
`ldd`コマンドで必要なライブラリが抜けてるのかなとか調べましたが`statically linked`って言われます．[公式のドキュメント](https://zed.dev/docs/remote-development)を見ても64bitのLinuxで動くよとしか書いてなくて困った．
以前，LXCのAlpine Linuxで似たような症状が出たときはnetbaseを入れたら治ったのですが，既に入ってました．
logを漁ってみたんですけど，セットアップが成功しただけだったんですよね
```log
{"level":3,"module_path":"remote_server","file":"crates/remote_server/src/server.rs","line":463,"message":"(remote server) starting up with PID 12272:\npid_file: \"/home/ user/.local/share/zed/server_state/setup-1/server.pid\", log_file: \"/home/ user/.local/share/zed/logs/server-setup-1.log\", stdin_socket: \"/home/ user/.local/share/zed/server_state/setup-1/stdin.sock\", stdout_socket: \"/home/ user/.local/share/zed/server_state/setup-1/stdout.sock\", stderr_socket: \"/home/ user/.local/share/zed/server_state/setup-1/stderr.sock\""}
{"level":3,"module_path":"crashes","file":"/home/runner/work/zed/zed/crates/crashes/src/crashes.rs","line":87,"message":"(remote server) spawning crash handler process"}
{"level":3,"module_path":"remote_server","file":"crates/remote_server/src/server.rs","line":520,"message":"(remote server) gpui app started, initializing server"}
{"level":3,"module_path":"remote_server","file":"crates/remote_server/src/server.rs","line":323,"message":"(remote server) accepting new connections"}
{"level":3,"module_path":"remote_server","file":"crates/remote_server/src/server.rs","line":330,"message":"(remote server) accepted new connections"}
{"level":3,"module_path":"util","file":"/home/runner/work/zed/zed/crates/util/src/util.rs","line":389,"message":"(remote server) set environment variables from shell:/bin/bash, path:/home/ user/.cargo/bin:/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games"}
{"level":3,"module_path":"crashes","file":"/home/runner/work/zed/zed/crates/crashes/src/crashes.rs","line":95,"message":"(remote server) connected to crash handler process after 100ms"}
{"level":3,"module_path":"crashes","file":"/home/runner/work/zed/zed/crates/crashes/src/crashes.rs","line":139,"message":"(remote server) crash handler registered"}
{"level":2,"module_path":"remote_server","file":"crates/remote_server/src/server.rs","line":374,"message":"(remote server) error reading message on stdin, dropping connection."}
{"level":3,"module_path":"remote_server","file":"crates/remote_server/src/server.rs","line":323,"message":"(remote server) accepting new connections"}
{"level":2,"module_path":"remote_server","file":"crates/remote_server/src/server.rs","line":334,"message":"(remote server) timed out waiting for new connections after 600s. exiting."}
{"level":3,"module_path":"remote_server","file":"crates/remote_server/src/server.rs","line":309,"message":"(remote server) app quitting. sending signal to server main loop"}
{"level":3,"module_path":"remote_server","file":"crates/remote_server/src/server.rs","line":594,"message":"(remote server) gpui app is shut down. quitting."}
```
ということで，他にこのフォルダーの中になんかないかなと思って`tree`コマンドを打って，システムに存在しなかったから`sudo apt install tree`をして，なんでだろうなーって思って実行したら，動いたんですよ．つまりRemoteされる先にtreeコマンドが存在してないと動かないってことです．正直，lddで見れない分，もっとたちが悪いです．
みなさんも気をつけてください．
# 教訓
ZedのRemoteされる側に，少なくとも
```
ssh netbase curl tree
```
コマンドが使える状態じゃないと駄目ってことです．
きっと`std::process::Command`で叩いてるんだろうなーって．
それはそうと，requirementとしてドキュメントに書くべきだと思うんですよ．(個人の感想です)
これで何回目だって気分になってきたので，issueを書こうと思います．(気力があれば)