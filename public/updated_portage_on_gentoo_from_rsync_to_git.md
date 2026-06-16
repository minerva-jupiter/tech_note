---
title: GentooのPortageのアップデートをrsyncからgitにした
tags:
  - Gentoo
private: false
updated_at: '2026-06-17T07:14:21+09:00'
id: dbdf830dac681a6deec1
organization_url_name: null
slide: false
ignorePublish: false
---
# TL;DR
1. 必要なパッケージを入れる
```
emerge --ask app-eselect/eselect-repository dev-vcs/git
```
2. 元あった設定をクリア
```
eselect repository remove -f gentoo
```
3. rsync -> git
```
eselect repository add gentoo git https://github.com/gentoo-mirror/gentoo.git
```
3.5. もし、途中で引っかかったら、
```
rm -r /var/db/repos/gentoo
```
4. 更新
```
emaint sync -r gentoo
```
# Ref
- https://wiki.gentoo.org/wiki/Portage_with_Git
- [old resouse](https://www.jamescherti.com/gentoo-speed-up-emerge-sync-with-git/)
