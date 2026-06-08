---
title: Windows PC setupスクリプト
tags: 
- Windows
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
---
# 概要
Windowsのセットアップを自動化する方式を検討する記事です．
# 対象読者
- (ライトではない)windowsユーザー
- windowsが`\ちょっとできる`人
# 現行方式
## 保管方法

|||
|-|-|
|保管場所|GibHub Private リポジトリ|
|パッケージマネージャー|winget|

てな感じです．

## 複数PC運用について
みなさん，Windows機を複数持ってますよね?(唐突)
それを全て一つのリポジトリにするのもなんだし，でも，2つのPCにしちゃうのもなんだかなぁという感じだと思います．
そこで思いついたのは，`メインPC`は`main`ブランチに，ノートPCは`note`ブランチに分割しちゃう方法です．開発用が在る方は`dev`ブランチとかできて面白いですね．ただし，この運用は，複数に共通する設定の変更が絶望的にやりにくいことです．私はWindows機が2台しかない民なのでこの運用で耐えてますが，流石に3つ4つ出てくると厳しいかもです．

## winget
最初はいちいちインストールを回すのがめんどくさくて，wingetのexport/import機能を使ってインストールされているアプリを一致させようとした感じです．ただ，色々と問題があったのでそれについて書きます．
### 既存パッケージ再インストール問題
最初から標準で入っているパッケージをwingetが再インストールしようとする問題がありました．
時間がかかって非常にだるいので，毎回それが起こるようなパッケージ.jsonをつくって，exportされたjsonから削除するようなpythonスクリプトを書きました．
```python
import json
import os
from datetime import datetime

# --- Configuration ---
INPUT_FILE = "winget.json"
REMOVE_LIST_FILE = "wingetRemoveList.json"
OUTPUT_DIR = "winget"
# ---------------------

# Ensure the output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"Created directory: {OUTPUT_DIR}")

# Read the main winget file
try:
    with open(INPUT_FILE, "r", encoding="utf-8") as fs:
        wingetJson = json.load(fs)
except FileNotFoundError:
    print(f"Error: Input file not found at '{INPUT_FILE}'")
    exit(1)
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from '{INPUT_FILE}'")
    exit(1)

# Read the remove list file
try:
    with open(REMOVE_LIST_FILE, "r", encoding="utf-8") as fl:
        wingetRemoveListJson = json.load(fl)
except FileNotFoundError:
    print(f"Error: Remove list file not found at '{REMOVE_LIST_FILE}'")
    exit(1)
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from '{REMOVE_LIST_FILE}'")
    exit(1)

remove_identifiers = set(wingetRemoveListJson.get("wingetRemoveList", []))
original_packages = wingetJson.get("Sources", [{}])[0].get("Packages", [])
packages_to_keep = []
removed_count = 0

for package in original_packages:
    if package.get("PackageIdentifier") in remove_identifiers:
        print(f"Removing: {package.get('PackageIdentifier')}")
        removed_count += 1
    else:
        packages_to_keep.append(package)

if removed_count == 0:
    print("No packages were removed from the list.")

wingetJson["Sources"][0]["Packages"] = packages_to_keep

# Generate the output filename with the current date
today_str = datetime.now().strftime("%Y%m%d")
output_filename = os.path.join(OUTPUT_DIR, f"winget-{today_str}.json")

# Write the modified data to the new file
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(wingetJson, f, indent=4, ensure_ascii=False)

print(f"\nSuccessfully created formatted winget file at: {output_filename}")
```
コードはAIが書いたので，品質は保証しません．私の環境だと上手く動きました．
あと，現時点での`wingetRemoveList.json`の中身も貼っておきます．
```json
{
    "wingetRemoveList" : [
        "CPUID.CPU-Z.MSI",
        "Microsoft.Office",
        "Microsoft.VCRedist.2010.x64",
        "Microsoft.VCRedist.2008.x64",
        "Ubisoft.Connect",
        "Python.Launcher",
        "Microsoft.VCRedist.2015+.x64",
        "Microsoft.VCRedist.2008.x86",
        "Microsoft.VCRedist.2010.x86",
        "Microsoft.DotNet.DesktopRuntime.8",
        "Microsoft.VCRedist.2015+.x86",
        "Python.Python.3.10",
        "OffSec.KaliLinux",
        "Microsoft.UI.Xaml.2.7",
        "Microsoft.UI.Xaml.2.8",
        "Microsoft.VCLibs.Desktop.14",
        "Microsoft.WSL",
        "Microsoft.WindowsTerminal"
    ]
}
```
## 種々の設定
私はこれら以外にも割と様々にWindowsの設定を施しているので，それらも入れたいなーとか思いました．
具体的に言うと，
- powershellの使い心地をbashに寄せるためのプロファイル適用
- タスクバーの時計に秒数を追加
- 高速スタートアップの無効化
- 視覚効果を無効化
- ダークモード
- システムサウンドの無効化
これらを全部やるようなスクリプトを作っちゃいました．
AIに書かせると楽ですね．この程度なら容易にレビューができるし，ハルシネーションの影響も割合，少なくて済むので有り難いです．
なんか`-Force`が多用されてて怖いですけどね．windowsはもともと品質がよろしくはないので良いかななんて()
`setup.ps1`
```powershell
<#
.SYNOPSIS
    PCのセットアップを自動化します。
.DESCRIPTION
    このPowerShellスクリプトは、以下のセットアップ処理を実行します:
    - Windowsテーマのダークモードへの変更
    - PowerShellプロファイルの更新
    - パフォーマンス向上のための視覚効果の無効化
    - タスクバー時計への秒表示の有効化
    - 高速スタートアップの無効化
    - システムサウンドの無効化
    - 最新のwinget JSON構成ファイルを使ったアプリケーションのインストール
    - shortcutsフォルダのユーザーPATHへの追加
.NOTES
    このスクリプトは管理者権限で実行する必要があります。
#>

# スクリプトが管理者として実行されているか確認
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "このスクリプトは管理者権限が必要です。管理者として再起動します..."
    # 管理者としてスクリプトを再実行
    Start-Process pwsh -Verb RunAs -ArgumentList "-NoProfile -File `"$PSCommandPath`""
    exit
}

# スクリプトの場所を基準に動作するようにカレントディレクトリを変更
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $scriptRoot

Write-Host "PCセットアップスクリプトを開始します..." -ForegroundColor Green
Write-Host "------------------------------------------------------------"

# 1. Set system and apps to Dark Mode
try {
    Write-Host "[1/8] Windowsとアプリのテーマをダークモードに設定しています..." -ForegroundColor Cyan
    $regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
    # 0 = Dark, 1 = Light
    Set-ItemProperty -Path $regPath -Name "AppsUseLightTheme" -Value 0 -ErrorAction Stop
    Set-ItemProperty -Path $regPath -Name "SystemUsesLightTheme" -Value 0 -ErrorAction Stop
    Write-Host "  テーマをダークモードに設定しました。"
}
catch {
    Write-Error "ダークモードへの設定に失敗しました: $_"
}

# 2. PowerShellプロファイルに内容を追記
try {
    Write-Host "[2/8] PowerShellプロファイルを更新しています..." -ForegroundColor Cyan
    $profileSourcePath = ".\Microsoft.PowerShell_profile.ps1"

    if (-not(Test-Path -Path $profileSourcePath)) {
        throw "プロファイルソースファイルが見つかりません: $profileSourcePath"
    }

    $profileContent = Get-Content -Path $profileSourcePath -Raw -ErrorAction Stop

    # プロファイル用のディレクトリが存在しない場合は作成
    $profileDir = Split-Path -Path $PROFILE -Parent
    if (-not (Test-Path -Path $profileDir)) {
        New-Item -Path $profileDir -ItemType Directory -Force | Out-Null
    }

    # プロファイルファイルが存在しないか、内容がまだ含まれていない場合に追記
    if (-not (Test-Path $PROFILE) -or -not ((Get-Content $PROFILE -Raw) -like "*$($profileContent)*")) {
         Add-Content -Path $PROFILE -Value $profileContent
         Write-Host "  PowerShellプロファイルを更新しました。"
    } else {
        Write-Host "  プロファイルは既に更新済みです。スキップします。" -ForegroundColor Yellow
    }
}
catch {
    Write-Error "プロファイルの更新に失敗しました: $_"
}

# 3. パフォーマンスのために視覚効果を無効化
try {
    Write-Host "[3/8] 視覚効果をパフォーマンス優先に設定しています..." -ForegroundColor Cyan
    $regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
    Set-ItemProperty -Path $regPath -Name "VisualFxSetting" -Value 2 -ErrorAction Stop
    Write-Host "  視覚効果を「パフォーマンスを優先する」に設定しました。"
}
catch {
    Write-Error "視覚効果の無効化に失敗しました: $_"
}

# 4. タスクバーの時計に秒を表示
try {
    Write-Host "[4/8] タスクバーの時計に秒を表示する設定を有効にしています..." -ForegroundColor Cyan
    $regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
    if (-not (Test-Path $regPath)) {
        New-Item -Path $regPath -Force | Out-Null
    }
    Set-ItemProperty -Path $regPath -Name "ShowSecondsInSystemClock" -Value 1 -ErrorAction Stop
    Write-Host "  タスクバーの時計に秒が表示されるようになります。"
}
catch {
    Write-Error "時計の秒表示設定に失敗しました: $_"
}

# 5. 高速スタートアップを無効化
try {
    Write-Host "[5/8] 高速スタートアップを無効化しています..." -ForegroundColor Cyan
    $regPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power"
    Set-ItemProperty -Path $regPath -Name "HiberbootEnabled" -Value 0 -ErrorAction Stop
    Write-Host "  高速スタートアップを無効化しました。"
}
catch {
    Write-Error "高速スタートアップの無効化に失敗しました: $_"
}

# 6. システムサウンドを無効化
try {
    Write-Host "[6/8] システムサウンドを無効化しています..." -ForegroundColor Cyan
    $schemePath = "HKCU:\AppEvents\Schemes"
    Set-ItemProperty -Path $schemePath -Name "(Default)" -Value ".None" -ErrorAction Stop
    Write-Host "  サウンド設定を「サウンドなし」に変更しました。"
}
catch {
    Write-Error "システムサウンドの無効化に失敗しました: $_"
}

# 7. 最新のwinget JSONファイルからパッケージをインストール
try {
    Write-Host "[7/8] Wingetによるアプリケーションのインストールを開始します..." -ForegroundColor Cyan
    $latestWingetFile = Get-ChildItem -Path ".\winget" -Filter "winget-*.json" | Sort-Object Name -Descending | Select-Object -First 1
    if ($latestWingetFile) {
        Write-Host "  最新の構成ファイルが見つかりました: $($latestWingetFile.Name)"
        Write-Host "  インポートを開始します。完了まで時間がかかる場合があります..."
        winget import -i $latestWingetFile.FullName --accept-package-agreements --accept-source-agreements
    } else {
        Write-Warning "  'winget-*.json' ファイルが見つかりませんでした。アプリケーションのインストールをスキップします。"
    }
}
catch {
    Write-Error "Wingetでのアプリケーションインストールに失敗しました: $_"
}

# 8. shortcutsフォルダをPATH環境変数に追加
try {
    Write-Host "[8/8] 'shortcuts' フォルダをPATH環境変数に追加しています..." -ForegroundColor Cyan
    $shortcutsPath = Join-Path -Path $scriptRoot -ChildPath "shortcuts"

    if (-not (Test-Path -Path $shortcutsPath)) {
         Write-Warning "  'shortcuts' フォルダが見つかりません。スキップします。"
    }
    else {
        $currentUserPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
        if ($currentUserPath -notlike "*$shortcutsPath*") {
            $newPath = $currentUserPath.TrimEnd(';') + ";" + $shortcutsPath
            [System.Environment]::SetEnvironmentVariable("Path", $newPath, "User")
            $env:Path = $newPath # 現在のセッションにも反映
            Write-Host "  'shortcuts' フォルダをユーザーのPATHに追加しました。"
        } else {
            Write-Host "  'shortcuts' フォルダは既にユーザーPATHに存在します。スキップします。" -ForegroundColor Yellow
        }
    }
}
catch {
     Write-Error "'shortcuts' フォルダのPATHへの追加に失敗しました: $_"
}

Write-Host "------------------------------------------------------------"
Write-Host "セットアップスクリプトが完了しました。" -ForegroundColor Green
Write-Host "UI関連の変更を適用するためにExplorerを再起動します。" -ForegroundColor Yellow
Stop-Process -Name explorer -Force
Write-Host "すべての変更を確実に適用するために、コンピューターの再起動を推奨します。" -ForegroundColor Yellow
```
私は画面が2つある関係でwallpaperの自動設定は諦めました．そもそもは動画をwallpaperにするよう試みたりしてたので，その辺りは今後気が向けばやります．
あとはpowershellのプロファイルの中にインストールが必要なモジュールがあった気がするので，それもこのスクリプトに入れておくと便利かななどと思ってます．

# まとめ
これでPC初期化は怖くない！
みなさんも1年くらいの周期で初期化していると思うので，この機会にぜひとも自動セットアップを構築して，やってみてください．私は今度は大量のVMのパッケージのバージョンを何とかするansibleを作るかもしれないです．乞うご期待！(のんびりやります)
