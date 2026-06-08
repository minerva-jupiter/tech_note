---
title: Rust WASM のgetrandomに苦しんだ話
tags:
- rust
- wasm
- getrandom
private: false
updated_at: 2025-11-27 19:19
id: null
organization_url_name: null
slide: false
---
# ‌‌‌‌状況
‌‌いつものようにnext.jsからWASMのRustを呼び出してました。
‌今回は、形態素解析のビブラートというソフトウェアを入れて、‌ それによってチャットの返答が変わるようなアプリケーションを作成しようとしてました。
‌しかしながら、ビルドが通りません。
‌前回、一度同じようなエラーが出た時に、`getrandom`の問題で長い事詰まってたので、‌今回は、その時の資料を引っ張り出して、‌早急に解決できると思っていました。

# ‌前回のこと
‌前にwebtoolsを作っていた時に、同じようにRustのWASMの呼び出しをしてました。
‌今回と同じように、`getrandom`‌のエラーが起きて、‌ググって、ググッた結果、以下のような変更を加えることで治りました。

### Cargo.toml
```diff
[package]
name = "wasm-webtools"
version = "0.1.0"
edition = "2024"

[lib]
crate-type = ["cdylib"]

[dependencies]
rand = "0.9.2"
wasm-bindgen = "0.2"
-- getrandom = "0.3"
++ getrandom = { version = "0.3", features = ["wasm_js"] }
```
### .cargo/config.toml
```diff
++ [target.wasm32-unknown-unknown]
++ rustflags = ["--cfg", 'getrandom_backend="wasm_js"']
```

# 今回起きたこと
‌しかしながら、今回は前回のようにはいきませんでした。
‌そもそも、明示的に`getrandom`を使用していなかったので、‌同様のことが起こったりはしないだろうなあと思っていたら、‌どうやら使っているライブラリーが`getrandom`が必須なようでした。
‌前回と同じようにファイルに変更を加えます。
‌しながら、今回は動きませんでした。
‌最初はビブラートが悪さしてるのかな？とか思いましたが、‌そんなこともなく。
‌‌AIにも聞いてみましたが、‌それはFSを使っているから泊まるんだよみたいなことを言われて。
確かにWASMでFSを使うことは無理なんですが、‌今止まっているのは、そこじゃないんですよねー。
‌そして、AIと‌Google検索と格闘すること、一時間ぐらい。
‌もしかして、`wasm-bingen`が使ってるのと`js-sys`が使ってる`getrandom`ってバージョンが違うんじゃね？という話になりまして。
‌`getrandom`って、version0.2系と0.3系でフィーチャーの名前が`js`から`wams_js`に変更されてるので、‌両方を内包するようなコンフィグを書きましょう、という話になりました。
‌めでたく、これで終わりましたね。
‌非常に長ったらしく、馬鹿らしいコンフィグになりました。
```
[package]
name = "rust-wasm"
version = "0.1.0"
edition = "2024"

[lib]
crate-type = ["cdylib"]

[dependencies]
js-sys = "0.3.81"
vibrato = "0.5.2"
wasm-bindgen = "0.2.104"
getrandom_v02 = { package = "getrandom", version = "0.2", features = ["js"] }
getrandom_v03 = { package = "getrandom", version = "0.3", features = ["wasm_js"] }
```
‌バージョンの依存って、Ubuntu以外で考えたことなかったんですけど、Rustにも普通に存在しますわね。よく考えたら。
‌ということで2時間ぐらいはまってたので、‌ ~~恨み節~~次回の自分への教訓と言うことで書いておきます。
# 余談
‌`js-sys`を使った理由も‌、ためになりそうなので書いておきます。
‌実際に書いたコードはこちらなんですけど、エラーが発生する可能性があるコードを書いていたので、エラーを取得してJSのエラーにぶち込むために`js-sys`のエラー型を使って新しいエラーを作るっていうことをしてました。
```Rust
use std::io::Cursor;
use vibrato::{Dictionary, Tokenizer};
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn chat(dict_data: &[u8], input: &str) -> Result<String, JsValue> {
    let reader = Cursor::new(dict_data);
    let dict = Dictionary::read(reader)
        .map_err(|_|{JsValue::from(js_sys::Error::new("Dictionary road Error"))})?;
    let tokenizer = Tokenizer::new(dict);
    let mut worker = tokenizer.new_worker();

    worker.reset_sentence(input);
    worker.tokenize();
    worker.token(0);
    let &mut ans = worker.token(0).to_string();
    Ok(ans)
```