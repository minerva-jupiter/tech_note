---
title: "レポートレビューLLMをLoRAで作る"
emoji: "⛏️"
type: "tech"
topics:
  - "lora"
  - "llm"
  - "typst"
  - "qlora"
published: true
published_at: "2025-12-13 00:11"
---

# 想定読者

この記事の想定読者は以下の人です．専門用語に関しては，検索すれば出てくるものとして，こちらで注釈を付けることはしません．誤用などあればコメント下さい．

- ローカルLLMの開発の経験のある人
- LLMのファインチューニングの知識がある人

# はじめに

本記事は，ローカル環境でLLMを動かし，物理学実験のレポートを提出前にレビューするアプリケーションを作ってみた備忘録です．
最終的な目標は，Typstで書かれた物理学実験のレポートに対し，教員から提示されるであろう指摘事項を前もって指摘してくれることです．
なお，当該リポジトリは私の書いた実験レポートそのものが含まれる学習データがありますので，Private Repositoryになっています．
公開できる部分は公開したいのですが，記事に書き込んでしまうと冗長なのと，Geminiに同じことを頼んだら，同じようなコードが返ってくると思いますので，擬似コードだけ置いておきます．
学習に使用したデータはレポート2本とその指摘事項です．圧倒的に少ないですね．

## 初期計画と環境コンテキスト

プロジェクト開始時の主要な計画と環境は以下の通りです．

### 動作環境
| 項目 | 詳細 |
| :--- | :--- |
| OS | Windows 11 |
| CPU | AMD Ryzen 9 3900XT (12コア/24スレッド) |
| GPU | NVIDIA GeForce RTX 3060 |

### モデルと手法
| 項目 | 詳細 |
| :--- | :--- |
| ベースモデル | Mistral 7B (GGUF 形式) |
| ファインチューニング | QRoLA |


# 仮実装
## 環境構築

とりあえず初期計画のために環境を整えます．
どっかでPythonのパッケージマネージャーとしてRust製の`uv`ってのが巷で流行っているという話を聞いたので，今回は`uv`を使います．
それにしてもRust製のPythonパッケージマネージャーなんて，もはやRustにしちまえよって感じですけどね．学習コストが高いんでね．
環境構築は備忘録的に書いた`README.md`の中身を掲示して置くことで代替とします．
```Markdown
# Prepare Python
## create venv
### install uv
`pip install uv`
### create .venv
`uv venv .venv`
## activate venv
`source .venv/bin/activate`
if you use windows powershell, use `.\.venv\Scripts\activate.ps1`

## install requirements
`uv pip install -r requirements.txt`

## setting for cuda
please make sure you have cuda installed and set the environment variable CUDA_HOME to the path of your cuda installation.
check for it can do with `nvcc --version`
and install pytorch for your cuda version.
for example nvcc version is 13.0
`uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130 --reinstall`
And then, check this python env can use cuda with `python gpu_check.py`

## set API key for gemini(only need to use structuring-training-data)
`export GEMINI_API_KEY=your_api_key`
if you use windows powershell, use `$env:GEMINI_API_KEY="あなたのAPIキー"`
```
厳密にはMarkdownのベストプラクティスには従ってないですが，許してください．読めりゃ，わかりゃいいんですよ．
なぜかGPUに対応したPyTorch等が入らなくて，なんでだろうなとか思ってたら，そもそもPCに`cuda`がインストールされてませんでした．
## 学習用データ

自分の書いたレポートとそれについた指摘事項を統合して学習データにします．
指摘事項とそれに当たっている部分を抜き出してセットにして入れるといいみたいなのですが，そのJSONを書くのがめんどくさかったので，GeminiのAPIを叩いてJSONを返してもらってます．

次に，まとめられたJSONとレポート本体を合体させ，さらに合体した各レポートのセットを一つのjsonlファイルに合体させます．
レポートを連番にして，連番毎にレポートのtypstファイルと指摘事項のtxtファイルを学習用データのディレクトリに入れて，それを読むようにすれば，学習用データが多くなっても安心です．

## 学習

いよいよ学習です．
学習プログラムの入力はjsonlで出力はアダプターのアセット達です．
それぞれ設定値です．

| パラメータ名 | 値 |
| :--- | :--- |
| **ベースモデル** | `Mistral-7B-Instruct-v0.2` |
| **量子化 (4bit)** | `load_in_4bit=True` |
| **量子化タイプ** | `bnb_4bit_quant_type="nf4"` |
| **LoRA R (ランク)** | `16` |
| **LoRA Alpha** | `32` |
| **バッチサイズ** | `1` |
| **勾配蓄積** | `4` |
| **学習率** | `2e-4` |
| **最大ステップ数** | `50` |
| **FP16** | `True` |

## GGUF化

先程の出力をllama.cppでRoLAしたモデルを読み込むために，GGUF化します．
Gitのサブモジュールとして，llama.cppをクローンして，リポジトリのルートでこのコマンドを叩けばできます．
```
python vendor/llama.cpp/convert_hf_to_gguf.py mistral_typst_merged --outfile mistral_typst_merged.f16.gguf --outtype f16
```
(`mistral_typst_merged`はモデルのディレクトリ，`mistral_typst_merged.f16.gguf`は出力です)

## 量子化

リソースバカ食いの可能性を危惧して，モデルを量子化します．
ただ，何故かllama.cppの量子化が上手く動かなかったので，公式ビルドを落としてきてバイナリを叩いて量子化しました．

## APIサーバー

何をトチ狂ったのか，私はこの推論をAPIサーバーにしようと考えて，PythonでAPIサーバーを立て始めました．
もともとはフロントエンドアプリをつけて，APIだけを自宅サーバーに立てて叩きたいなと思っていた名残です．
名残を実装に反映してしまうのがGeminiの悪い癖ですね．自分は間違わないと思っているのか，モジュールテストとかをしない方向で動いているように見えます．
冗談はさておき，このAPIサーバー，とても重大な欠陥がありました．
モデルがJSONでない形式で返してきたときにパースエラーが起きるんです．
APIの行き帰りは厳格にJSONでなければなりませんが，量子化したモデルにそれをやらすのもそもそも無理があります．
良く見てみると，トランスフォーマー型らしいと言えばそうなのですが，一行一行に対して支離滅裂な指摘事項が挙げられていて，到底設定したいた`max_tokens`では足りずにパースエラーを起こしていました．

## 仮実装で露呈した問題点

- JSON形式の破壊
- 量子化の問題
- CPU推論

です．次の章から順番に説明と施した対策を挙げていきます．

# JSON形式

そもそもモデルに(それも量子化した)JSONを書かせるなんてエラーの元ですし，APIにしたいなら，出てきたテキストをそのままJSONにぶち込むように変更すればいいので，JSON形式で出力させるようなプロンプト(システムイントロダクション)は削除しました．
そしてAPIサーバーを立てて，それを叩くpythonを作ってとやっているのが無駄なので，モデルを直接読み込んでtypstファイルをぶち込むようなpythonプログラムを書きました．

# QLoRAの問題

JSON問題が解決しても，回答の長さが`max_tokens`を軽々と突破する問題は依然として存在しました．
そこで，私は諦めて量子化されていないf16のモデルを使いました．
するとどうでしょう．10行程度のリストに収まりました．

# CPU推論

推論を動かしていると，CPUとDRAMの使用率が最大に張り付きます．当然ですね．f16なLLMをローカルで動かしているのですから．
問題はそこではなくて，GPUを使ってくれないという点です．
私が1年前くらいに奮発して買ったGDDDR5が12GBも積まれているRTX3060をせっかく搭載しているというのに，一個も使わないんです．
QLoRAではバイナリのバージョンを揃えてインストールしたので，llama.cppでも同様のことをしようと思ってやりました．
参考にさせていただいた記事です．
https://zenn.dev/hellohazime/articles/ccd01c2df0b5c3
でも，インストールに失敗しました．
仕方ないので，環境変数による強制ビルドをしました．
```PowerShell
$env:CMAKE_ARGS='-DGGML_CUDA=ON -DCMAKE_CUDA_COMPILER="C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v13.0/bin/nvcc.exe" -DCUDA_TOOLKIT_ROOT_DIR="C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v13.0" -DCUDA_ARCHITECTURES=native'
$env:FORCE_CMAKE=1
uv pip install -r requirements.txt --no-cache-dir
```
これでも失敗しました．
エラーログに`Use GGML_CUDA instead`
って書いてあったので，次の記事を参考にmakeの環境変数を書き換えしました．
https://qiita.com/Nikeri/items/27490eb865c42803d14c
それでもエラーは止まりません．
```
No CUDA toolset found.
```
意味がわかりません．ご丁寧にnvcc.exeのパスを入れてるのに，無いとか言われるんですからもうどうしようもないです．
今は諦めてCPUで推論を回してますが，時間と電気代がかかるのでぜひともやめてほしいところです．
Gemini君が言うにはDLL地獄という状態らしくて，どうしたらいいかわかんないです．

# 今後への課題

現状の問題点は以下の2つです．
- CPUで推論している
- レビューの品質が低い

前者については前章で述べたので後者について述べます．
レビュー品質が低い原因は色々と考えられます．
当初は50ステップとしていたLoRAですが，25ステップのあたりでlossが0.1412とかまで下がってるので，過学習が疑われます．
25ステップにすると，ファジーさはだいぶ弱まりましたが，全体的に当たらない指摘をしている部分が多いです．
開発途中に教員のレビューを受けたレポートが一本増えたので学習用データに追加してみましたが，反応は芳しくないです．
他の人のレポートを学習用データとして入れればもっと良いのですけどね．

# まとめ

レポートのレビューをするLLMをLoRAで作るには，まだ超えなければならい壁が幾つもあるように思います．
私のこれも到底，学科の仲間には見せることができない出来栄えですからね．
人間の脳も大概，説明可能性に欠けていると思うのですが，それを補おうとしてきた科学とそこから生まれたそれに矛盾する再現性のない深層学習．
その表層にちょっとでも触れることができたかなと思います．
皆さんはくれぐれも，これを応用して，教科書の内容からレポートを生成しようなんて思わないでくださいね．
科学の自壊が進んでしまわないように．
