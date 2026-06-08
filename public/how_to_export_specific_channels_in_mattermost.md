---
title: Mattermostの特定のチャンネルをexportする方法
tags:
- export
- mattermost
private: false
updated_at: 2026-02-26 21:10
id: null
organization_url_name: null
slide: false
---
# 総集編
### ログイン(トークンの取得)
```bash
curl -i -d '{"login_id":"username@example.com","password":"thisbadpassword"}' https://yourdomain/api/v4/users/login
```
### export
```bash
curl -i -H 'Authorization: Bearer TOKEN' https://yourdomain/api/v4/channels/CHANNEL_ID/posts -o mattermost-export.json
```

# 想定読者
~~Mattermostの新たなFreeEditionへの規制の追加で~~Mattermostの提供が終了するため，履歴をexportしておきたい方

# 詳細な手順

### ログイン
アカウントでログインします．
アカウントのアクセス範囲にあるAPIが叩けるようになります．
```bash
curl -i -d '{"login_id":"username@example.com","password":"thisbadpassword"}' https://yourdomain/api/v4/users/login
```
もちろんのこと，username@example.comとそのpassword，yourdomainはexportしたいMattermostのURLのドメインです．
成功すると以下のようなレスポンスが返ってきます．
```bash
HTTP/2 200
date: Thu, 26 Feb 2026 11:15:29 GMT
content-type: application/json
content-length: 772
permissions-policy:
referrer-policy: no-referrer
token: TOKEN
vary: Accept-Encoding
x-content-type-options: nosniff
x-ratelimit-limit: 101
x-ratelimit-remaining: 100
x-ratelimit-reset: 1
x-request-id: X-REQUEST-ID
x-version-id: 11.0.7.20090702019.12a90a33d692853deafd8a4c7a7162684aa60dfcb310709dd96061b261c1b24b.false
cf-cache-status: DYNAMIC
nel: {"report_to":"cf-nel","success_fraction":0.0,"max_age":604800}
report-to: {"group":"cf-nel","max_age":604800,"endpoints":[{"url":"URL"}]}
server: SERVER
cf-ray: CF-RAY
alt-svc: h3=":443"; ma=86400

(以下，ユーザーの詳細)
```
これの上から7行目`token:`の後ろにあるのが，貴方の一時的なアクセストークンです．

### `channel ID`の取得
`Channel ID`はMattermostのUIから確認することができます．
![](https://storage.googleapis.com/zenn-user-upload/86ada553531c-20260226.png)
当該チャンネルを開いて，右上のinfoマークを押したら，画像のようなタブが出てきます．
これの赤く塗りつぶした部分，ここにチャンネルのIDが表示されています．
参考文献の2にはAPIだけでチャンネルのIDを取得する方法が掲載されています．
※チャンネルIDは任意の文字列です．チャンネル名やチャンネルのURLとは異なります．

### エクスポート
```bash
curl -i -H 'Authorization: Bearer TOKEN' https://yourdomain/api/v4/channels/CHANNEL_ID/posts
```
この`TOKEN`は先程ログインのときにもらったものです．
yourdomainは引き続きexportしたいMattermostのURLのドメインです．
そして`CHANNEL_ID`は先程説明したチャンネルIDです．
そうしたらJSON形式で降ってきます．
cURLではファイルをエクスポートすることができます．
エクスポート後のファイル名を`mattermost-export.json`とすると
```bash
curl -i -H 'Authorization: Bearer TOKEN' https://yourdomain/api/v4/channels/CHANNEL_ID/posts -o mattermost-export.json
```
とできる．

# 参考文献
1. [Mattermost API Document](https://developers.mattermost.com/api-documentation/)
2. [Mattermost Forums ~How do I extract posts from a Mattermost channel?~](https://forum.mattermost.com/t/how-do-i-extract-posts-from-a-mattermost-channel/6285)