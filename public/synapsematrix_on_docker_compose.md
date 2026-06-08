---
title: Synapse(Matrix) on Docker Compose
tags:
- docker
- matrix
- selfhosted
- synapse
private: false
updated_at: 2025-11-10 21:49
id: null
organization_url_name: null
slide: false
---
# 想定読者
- Synapseのバックエンドをセルフホステッドする人
- まともにCLI onlyのサーバを運用する人
# Ref
- [公式のDockerComposeについてのドキュメント](https://github.com/element-hq/synapse/tree/develop/contrib/docker)
- [EclipseのSynapseリポジトリ](https://gitlab.eclipse.org/eclipsefdn/it/releng/chat-service/chat-service-provisioner)

## edit docker-compose.yaml

docker-compose.yamlを完全に設定します。
生成コマンドによって出力されたファイル数にはシークレット鍵等々の情報が記載されるので、あとからdocker-compose.yamlを変更することは非常に推奨されません。
サンプル

```YAML
# This compose file is compatible with Compose itself, it might need some
# adjustments to run properly with stack.

services:

  synapse:
    build:
      context: ../..
      dockerfile: docker/Dockerfile
    image: docker.io/matrixdotorg/synapse:latest
    # Since synapse does not retry to connect to the database, restart upon
    # failure
    restart: unless-stopped
    # See the readme for a full documentation of the environment settings
    # NOTE: You must edit homeserver.yaml to use postgres, it defaults to sqlite
    environment:
      - SYNAPSE_CONFIG_PATH=/data/homeserver.yaml
    volumes:
      # You may either store all the files in a local folder
      - ./files:/data
      # .. or you may split this between different storage points
      # - ./files:/data
      # - /path/to/ssd:/data/uploads
      # - /path/to/large_hdd:/data/media
    depends_on:
      - db
    # In order to expose Synapse, remove one of the following, you might for
    # instance expose the TLS port directly:
    ports:
      - 8448:8448/tcp
      - 8008:8008/tcp

  db:
    image: docker.io/postgres:15-alpine
    # Change that password, of course!
    environment:
      - POSTGRES_USER=synapse_user
      - POSTGRES_PASSWORD=changeme
      # ensure the database gets created correctly
      # https://element-hq.github.io/synapse/latest/postgres.html#set-up-database
      - POSTGRES_INITDB_ARGS=--encoding=UTF-8 --lc-collate=C --lc-ctype=C
    volumes:
      # You may store the database tables in a local folder..
      - ./schemas:/var/lib/postgresql/data
      # .. or store them on some high performance storage for better results
      # - /path/to/ssd/storage:/var/lib/postgresql/data
```

## generate homeserver files

次にこのdocker-composeファイルを使って必要なファイル群を生成します。
サーバー名のところは適宜書き換えてください。

```
docker compose run --rm -e SYNAPSE_SERVER_NAME=my.matrix.host -e SYNAPSE_REPORT_STATS=yes synapse generate
```

## edit homeserver.yaml

生成された`file`フォルダの中にあるhomeserver.yamlに必要な設定を書き込んでいきます。
少なくとも必要な設定は以下です。

```diff
- listeners:
-   - port: 8008
-     tls: false
-     type: http
-     x_forwarded: true
-     resources:
-       - names: [client,federation]
-         compress: false

+ listeners:
+   - port: 8008
+     tls: false
+     type: http
+     x_forwarded: true
+     resources:
+       - names: [client]
+         compress: false
+ 
+   - port: 8448
+     tls: false
+     type: http
+     x_forwarded: true
+     resources:
+       - names: [federation]
+         compress: false

-----------------------------------

- database: 
-   name: sqlite3
-   

+ database:
+   name: psycopg2
+   args:
+     user: synapse_user
+     password: changeme
+     dbname: synapse_user
+     host: db
+     cp_min: 5
+     cp_max: 10
```

この設定で細かなSynapseの動作を設定します。
たとえばTokenの所持者のみ自己登録を可能にするなど。
詳しい設定は公式ドキュメントを見てください。
[Configuration Manual](https://element-hq.github.io/synapse/latest/usage/configuration/config_documentation.html)

### deploy synapse

これらの設定が終了すれば、docker-compose.yamlのあるディレクトリに戻って、サーバーのデプロイを実行します。

```
sudo docker compose up -d
```

サーバーが無事に動いているかのテストは、curlを使うことで可能です。

```
curl localhost:8008
```

```
curl localhost:8448
```

成功している場合の返答は以下のようになります。

```
$ curl localhost:8008
<html>
    <head>
        <meta http-equiv="refresh" content="0;URL=/_matrix/static">
    </head>
    <body bgcolor="#FFFFFF" text="#000000">
    <a href="/_matrix/static">click here</a>
    </body>
</html>
$ curl localhost:8448
<html>
  <head><title>404 - No Such Resource</title></head>
  <body>
    <h1>No Such Resource</h1>
    <p>Sorry. No luck finding that resource.</p>
  </body>
</html>
```

## Setting Cloudflare Tunnel

Cloudflare One のダッシュボードからnetwork以下にあるtunnel項目を開き、tunnelの設定を開きます。
「公開されたアプリケーション」タブに移動し、synapseのホスト名(とfederation用のホスト名)を追加します。
フェデレーション用のホスト名にはhttpHostHeaderをsynapseのホスト名に設定します。

## .well-known/matrixの設定

Cloudflare workersで適当なものを立ち上げます。
worker.js

```JavaScript
const HOMESERVER_URL = "https://my.matrix.host.net:443";
const IDENTITY_SERVER_URL = "https://vector.im";
const FEDERATION_SERVER = "my.matrix.host.net:443";

export default {
  async fetch(request, env) {
    const path = new URL(request.url).pathname;
    switch (path) {
      case "/.well-known/matrix/client":
        return new Response(
          `{"m.homeserver": {"base_url": "${HOMESERVER_URL}"},"m.identity_server": {"base_url": "${IDENTITY_SERVER_URL}"}}`
        );
      case "/.well-known/matrix/server":
        return new Response(`{"m.server": "${FEDERATION_SERVER}"}`);
      default:
        return new Response("Invalid request");
    }
  },
};
```

適宜、以下のページに示されているクライアント向けにE2EEを無効化する設定を追加してください。

 https://github.com/element-hq/element-web/blob/develop/docs/e2ee.md