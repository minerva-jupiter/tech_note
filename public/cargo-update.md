# update apps installed with cargo

# まとめ
```bash
cargo install cargo-update
```
```
cargo install-update -a
```

# 詳細
## cargo-update
cargoのサブコマンドで、cargoでインストールした実行可能パッケージを更新するものです。
[cargo-update - crates.io](https://crates.io/crates/cargo-update)

## install cargo-update
これ自身もcargoからインストールします。
```bash
cargo install cargo-update
```
## cargo-updateを実行
cargo-updateの実行はサブコマンド`install-update`で行います。
パッケージ名とも違いますし、`cargo update`コマンドは他に存在しますので、この名前なのを忘れて、毎度ググっています(記事を書いた動機)
```bash
cargo install-update -a
```
最後の`-a`は`--all`の意味です。

# 参考文献
- thkyamaさんのブログ(https://blog.htkyama.org/cargo_update)
