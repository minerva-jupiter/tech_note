---
title: "SSH from Internet via Cloudflare Zero Trust"
emoji: "⛩️"
type: "tech"
topics:
  - "cloudflare"
  - "zerotrust"
  - "openssh"
published: true
published_at: "2025-07-29 19:09"
---

# TL;DR
https://zenn.dev/jij_inc/articles/659fe35813b940
この記事の方がわかりやすいです。
当記事は、上記の記事を既に理解しているが、手順や細かいパスなどを忘れてしまった人が、確認をするための記事です。

# 新規クライアント追加手順
1. Install cloudflared
1.5. Check Where cloudflare binary file
2. edit `$HOME/.ssh/config`
```
Host ssh-server
    HostName <subdomain.domain.tld>
    ProxyCommand <path to cloudflared binary> access ssh --hostname %h
```

# Cloudflare Zero Trustの設定
1. Add public host name(may be it through cloudflare tunnel) with subdomain you like.
2. Create Access Application and set policy you like.

__NOT SETTING AS A BROUWSER RENDERING!!!!__

# Attention of this article
この記事の項目の順番は、自分が確認する頻度順であります。
実行手順としては、
1. Cloudflare Zero Trustの設定
2. 新規クライアント追加手順
の順で実行することをおすすめします。