---
title: PVE upgrade 8 to 9
tags:
- debian
- proxmox
- pve
- pve8to9
private: false
updated_at: 2025-11-07 15:00
id: null
organization_url_name: null
slide: false
---
# 想定読者
- Proxmox VEをCLIからも触ることができ、よく保守している利用者
- Debian系OSのメジャーバージョンアップグレードをする人
# 本編
絶対に参照してください。
**[公式ドキュメント](https://pve.proxmox.com/wiki/Upgrade_from_8_to_9)**
## `pve8to9`を通す
### 一回目
チェック用のスクリプトのコマンドが入ってるので実行します。
```
pve8to9
```
そしたらなんかエラーが出ました。
どうやらsystemd-bootがあるとコンフィグが上書きされてうまく行かないようです。
ログはコピーするの忘れてました。
### 二回目
systemd-bootを削除後の出力
```
root@pve01:~# pve8to9
= CHECKING VERSION INFORMATION FOR PVE PACKAGES =

Checking for package updates..
PASS: all packages up-to-date

Checking proxmox-ve package version..
PASS: proxmox-ve package has version >= 8.4-0

Checking running kernel version..
PASS: running kernel '6.8.12-14-pve' is considered suitable for upgrade.

= CHECKING CLUSTER HEALTH/SETTINGS =

SKIP: standalone node.

= CHECKING HYPER-CONVERGED CEPH STATUS =

SKIP: no hyper-converged ceph setup detected!

= CHECKING CONFIGURED STORAGES =

PASS: storage 'datahdd' enabled and active.
PASS: storage 'local' enabled and active.
PASS: storage 'local-lvm' enabled and active.
INFO: Checking storage content type configuration..
PASS: no storage content problems found
PASS: no storage re-uses a directory for multiple content types.
INFO: Check for usage of native GlusterFS storage plugin...
PASS: No GlusterFS storage found.
INFO: Checking whether all external RBD storages have the 'keyring' option configured
SKIP: No RBD storage configured.

= VIRTUAL GUEST CHECKS =

INFO: Checking for running guests..
WARN: 4 running guest(s) detected - consider migrating or stopping them.
INFO: Checking if LXCFS is running with FUSE3 library, if already upgraded..
SKIP: not yet upgraded, no need to check the FUSE library version LXCFS uses
INFO: Checking for VirtIO devices that would change their MTU...
PASS: All guest config descriptions fit in the new limit of 8 KiB
INFO: Checking container configs for deprecated lxc.cgroup entries
PASS: No legacy 'lxc.cgroup' keys found.
INFO: Checking VM configurations for outdated machine versions
PASS: All VM machine versions are recent enough

= MISCELLANEOUS CHECKS =

INFO: Checking common daemon services..
PASS: systemd unit 'pveproxy.service' is in state 'active'
PASS: systemd unit 'pvedaemon.service' is in state 'active'
PASS: systemd unit 'pvescheduler.service' is in state 'active'
PASS: systemd unit 'pvestatd.service' is in state 'active'
INFO: Checking for supported & active NTP service..
PASS: Detected active time synchronisation unit 'chrony.service'
INFO: Checking if the local node's hostname 'pve01' is resolvable..
INFO: Checking if resolved IP is configured on local node..
PASS: Resolved node IP '192.168.0.15' configured and active on single interface.
INFO: Check node certificate's RSA key size
PASS: Certificate 'pve-root-ca.pem' passed Debian Busters (and newer) security level for TLS connections (4096 >= 2048)
PASS: Certificate 'pve-ssl.pem' passed Debian Busters (and newer) security level for TLS connections (2048 >= 2048)
INFO: Checking backup retention settings..
PASS: no backup retention problems found.
INFO: checking CIFS credential location..
PASS: no CIFS credentials at outdated location found.
INFO: Checking permission system changes..
INFO: Checking custom role IDs
PASS: no custom roles defined
INFO: Checking node and guest description/note length..
PASS: All node config descriptions fit in the new limit of 64 KiB
INFO: Checking if the suite for the Debian security repository is correct..
PASS: found no suite mismatch
INFO: Checking for existence of NVIDIA vGPU Manager..
PASS: No NVIDIA vGPU Service found.
INFO: Checking bootloader configuration...
PASS: bootloader packages installed correctly
INFO: Check for dkms modules...
SKIP: could not get dkms status
INFO: Check for legacy 'filter' or 'group' sections in /etc/pve/notifications.cfg...
INFO: Check for legacy 'notification-policy' or 'notification-target' options in /etc/pve/jobs.cfg...
PASS: No legacy 'notification-policy' or 'notification-target' options found!
INFO: Check for LVM autoactivation settings on LVM and LVM-thin storages...
NOTICE: storage 'datahdd' has guest volumes with autoactivation enabled
NOTICE: storage 'local-lvm' has guest volumes with autoactivation enabled
NOTICE: Starting with PVE 9, autoactivation will be disabled for new LVM/LVM-thin guest volumes. This system has some volumes that still have autoactivation enabled. All volumes with autoactivations reside on local storage, where this normally does not cause any issues.
You can run the following command to disable autoactivation for existing LVM/LVM-thin guest volumes:

        /usr/share/pve-manager/migrations/pve-lvm-disable-autoactivation

INFO: Checking lvm config for thin_check_options...
PASS: Check for correct thin_check_options passed
INFO: Check space requirements for RRD migration...
PASS: Enough free disk space for increased RRD metric granularity requirements, which is roughly 24.60 MiB.
INFO: Checking for IPAM DB files that have not yet been migrated.
PASS: No legacy IPAM DB found.
PASS: No legacy MAC DB found.
INFO: Checking if the legacy sysctl file '/etc/sysctl.conf' needs to be migrated to new '/etc/sysctl.d/' path.
PASS: Legacy file '/etc/sysctl.conf' exists but does not contain any settings.
INFO: Checking if matching CPU microcode package is installed.
WARN: The matching CPU microcode package 'intel-microcode' could not be found! Consider installing it to receive the latest security and bug fixes for your CPU.
        Ensure you enable the 'non-free-firmware' component in the apt sources and run:
        apt install intel-microcode
SKIP: NOTE: Expensive checks, like CT cgroupv2 compat, not performed without '--full' parameter

= SUMMARY =

TOTAL:    44
PASSED:   33
SKIPPED:  6
WARNINGS: 2
FAILURES: 0

ATTENTION: Please check the output for detailed information!
```
### 三回目
ゲストを落としてもう一回
```
root@pve01:~# pve8to9 --full
= CHECKING VERSION INFORMATION FOR PVE PACKAGES =

Checking for package updates..
PASS: all packages up-to-date

Checking proxmox-ve package version..
PASS: proxmox-ve package has version >= 8.4-0

Checking running kernel version..
PASS: running kernel '6.8.12-14-pve' is considered suitable for upgrade.

= CHECKING CLUSTER HEALTH/SETTINGS =

SKIP: standalone node.

= CHECKING HYPER-CONVERGED CEPH STATUS =

SKIP: no hyper-converged ceph setup detected!

= CHECKING CONFIGURED STORAGES =

PASS: storage 'datahdd' enabled and active.
PASS: storage 'local' enabled and active.
PASS: storage 'local-lvm' enabled and active.
INFO: Checking storage content type configuration..
PASS: no storage content problems found
PASS: no storage re-uses a directory for multiple content types.
INFO: Check for usage of native GlusterFS storage plugin...
PASS: No GlusterFS storage found.
INFO: Checking whether all external RBD storages have the 'keyring' option configured
SKIP: No RBD storage configured.

= VIRTUAL GUEST CHECKS =

INFO: Checking for running guests..
PASS: no running guest detected.
INFO: Checking if LXCFS is running with FUSE3 library, if already upgraded..
SKIP: not yet upgraded, no need to check the FUSE library version LXCFS uses
INFO: Checking for VirtIO devices that would change their MTU...
PASS: All guest config descriptions fit in the new limit of 8 KiB
INFO: Checking container configs for deprecated lxc.cgroup entries
PASS: No legacy 'lxc.cgroup' keys found.
INFO: Checking VM configurations for outdated machine versions
PASS: All VM machine versions are recent enough

= MISCELLANEOUS CHECKS =

INFO: Checking common daemon services..
PASS: systemd unit 'pveproxy.service' is in state 'active'
PASS: systemd unit 'pvedaemon.service' is in state 'active'
PASS: systemd unit 'pvescheduler.service' is in state 'active'
PASS: systemd unit 'pvestatd.service' is in state 'active'
INFO: Checking for supported & active NTP service..
PASS: Detected active time synchronisation unit 'chrony.service'
INFO: Checking if the local node's hostname 'pve01' is resolvable..
INFO: Checking if resolved IP is configured on local node..
PASS: Resolved node IP '192.168.0.15' configured and active on single interface.
INFO: Check node certificate's RSA key size
PASS: Certificate 'pve-root-ca.pem' passed Debian Busters (and newer) security level for TLS connections (4096 >= 2048)
PASS: Certificate 'pve-ssl.pem' passed Debian Busters (and newer) security level for TLS connections (2048 >= 2048)
INFO: Checking backup retention settings..
PASS: no backup retention problems found.
INFO: checking CIFS credential location..
PASS: no CIFS credentials at outdated location found.
INFO: Checking permission system changes..
INFO: Checking custom role IDs
PASS: no custom roles defined
INFO: Checking node and guest description/note length..
PASS: All node config descriptions fit in the new limit of 64 KiB
INFO: Checking if the suite for the Debian security repository is correct..
PASS: found no suite mismatch
INFO: Checking for existence of NVIDIA vGPU Manager..
PASS: No NVIDIA vGPU Service found.
INFO: Checking bootloader configuration...
PASS: bootloader packages installed correctly
INFO: Check for dkms modules...
SKIP: could not get dkms status
INFO: Check for legacy 'filter' or 'group' sections in /etc/pve/notifications.cfg...
INFO: Check for legacy 'notification-policy' or 'notification-target' options in /etc/pve/jobs.cfg...
PASS: No legacy 'notification-policy' or 'notification-target' options found!
INFO: Check for LVM autoactivation settings on LVM and LVM-thin storages...
NOTICE: storage 'datahdd' has guest volumes with autoactivation enabled
NOTICE: storage 'local-lvm' has guest volumes with autoactivation enabled
NOTICE: Starting with PVE 9, autoactivation will be disabled for new LVM/LVM-thin guest volumes. This system has some volumes that still have autoactivation enabled. All volumes with autoactivations reside on local storage, where this normally does not cause any issues.
You can run the following command to disable autoactivation for existing LVM/LVM-thin guest volumes:

        /usr/share/pve-manager/migrations/pve-lvm-disable-autoactivation

INFO: Checking lvm config for thin_check_options...
PASS: Check for correct thin_check_options passed
INFO: Check space requirements for RRD migration...
PASS: Enough free disk space for increased RRD metric granularity requirements, which is roughly 24.60 MiB.
INFO: Checking for IPAM DB files that have not yet been migrated.
PASS: No legacy IPAM DB found.
PASS: No legacy MAC DB found.
INFO: Checking if the legacy sysctl file '/etc/sysctl.conf' needs to be migrated to new '/etc/sysctl.d/' path.
PASS: Legacy file '/etc/sysctl.conf' exists but does not contain any settings.
INFO: Checking if matching CPU microcode package is installed.
WARN: The matching CPU microcode package 'intel-microcode' could not be found! Consider installing it to receive the latest security and bug fixes for your CPU.
        Ensure you enable the 'non-free-firmware' component in the apt sources and run:
        apt install intel-microcode

= SUMMARY =

TOTAL:    43
PASSED:   34
SKIPPED:  5
WARNINGS: 1
FAILURES: 0

ATTENTION: Please check the output for detailed information!
```
non-free-firmwareは金を払ってないので勘弁してください。次に進みます。
## リポジトリの更新
自分はお金を払っていないので、払っていない人向けって書いてあるスクリプトをコピペして実行するだけでいいです。
```
apt update
```
```
apt dist-upgrade
```
```
pveversion
```
```
sed -i 's/bookworm/trixie/g' /etc/apt/sources.list
```
```
sed -i 's/bookworm/trixie/g' /etc/apt/sources.list.d/pve-enterprise.list
```
```
cat > /etc/apt/sources.list.d/proxmox.sources << EOF
Types: deb
URIs: http://download.proxmox.com/debian/pve
Suites: trixie
Components: pve-no-subscription
Signed-By: /usr/share/keyrings/proxmox-archive-keyring.gpg
EOF
```
ワイはcephを使ってないのでceph系はそもそもファイルがないですね。
私の環境だと行間に空白行があってaptから認識されない形式になっちゃったので、viで適宜修正しながら`apt update`がちゃんと実行されるのを待つだけです。
ちゃんとリポジトリを取ってこれてそうだったら次です。
## `dist-upgrade`
Ubuntuの`do-release-update`みたい！
なんか途中でニュースが表示されたが、知らん。へーそうなんだ～って読んで(Shift+G)、qキーで閉じてたら実行が再び進む。
途中でなんか出てきたので、見てみる。
### `/etc/issue` Update
`/etc/issue`の変更みたいですね。変更をDで確認すると、元のProxmoxのヤツのほうがいいからNとします。
```
Configuration file '/etc/issue'                                                     　==> Modified (by you or by a script) since installation.                            ==> Package distributor has shipped an updated version.                             　What would you like to do about it ?  Your options are:                             　Y or I  : install the package maintainer's version                                  N or O  : keep your currently-installed version                                     　D     : show the differences between the versions                                   Z     : start a shell to examine the situation                                　The default action is to keep your current version.                             *** issue (Y/I/N/O/D/Z) [default=N] ? D                                             --- /etc/issue  2025-11-07 12:56:29.654409431 +0900
+++ /etc/issue.dpkg-new 2025-08-25 01:20:00.000000000 +0900
@@ -1,10 +1,2 @@
-
-------------------------------------------------------------------------------
-
-Welcome to the Proxmox Virtual Environment. Please use your web browser to
-configure this server - connect to:
-
-  https://192.168.0.15:8006/
-
-------------------------------------------------------------------------------
+Debian GNU/Linux 13 \n \l


Configuration file '/etc/issue'
 ==> Modified (by you or by a script) since installation.
 ==> Package distributor has shipped an updated version.
   What would you like to do about it ?  Your options are:
    Y or I  : install the package maintainer's version
    N or O  : keep your currently-installed version
      D     : show the differences between the versions
      Z     : start a shell to examine the situation
 The default action is to keep your current version.
*** issue (Y/I/N/O/D/Z) [default=N] ? N
Installing new version of config file /etc/issue.net ...
```
### `/etc/lvm/lvm.conf` Update
続きましては`/etc/lvm/lvm.conf`らしいです。
```
Configuration file '/etc/lvm/lvm.conf'
 ==> Modified (by you or by a script) since installation.
 ==> Package distributor has shipped an updated version.
   What would you like to do about it ?  Your options are:
    Y or I  : install the package maintainer's version
    N or O  : keep your currently-installed version
      D     : show the differences between the versions
      Z     : start a shell to examine the situation
 The default action is to keep your current version.
*** lvm.conf (Y/I/N/O/D/Z) [default=N] ? D
--- /etc/lvm/lvm.conf   2025-04-26 20:47:17.070430178 +0900
+++ /etc/lvm/lvm.conf.dpkg-new  2025-08-11 17:46:22.000000000 +0900
```
こっちはめちゃ長い！
コメントの綴ミスがほとんどだけど、最後にコメントアウトされてない設定が消されてました。
```
-devices {
-     # added by pve-manager to avoid scanning ZFS zvols and Ceph rbds
-     global_filter=["r|/dev/zd.*|","r|/dev/rbd.*|"]
-}
```
これはpve-managerが追加したみたいなので、消したくないよー。修正されたオプションや綴ミスだけを取り入れてこの設定だけは残したいところ。
ま、むりなんで元のバーションを残します。こういうときにgitのコンフリクトを込んだ画面みたいにしててくれたら直しやすいのになーって思います。
ということでなんやかんやあって、PVEの更新完了！
## 更新チェック
```
root@pve01:~# pveversion
Target Packages (pve-no-subscription/binary-amd64/Packages) is configured multiple times in /etc/apt/sources.list:8 and /etc/apt/sources.list.d/proxmox.sources:1
Target Packages (pve-no-subscription/binary-all/Packages) is configured multiple times in /etc/apt/sources.list:8 and /etc/apt/sources.list.d/proxmox.sources:1
Target Translations (pve-no-subscription/i18n/Translation-en_US) is configured multiple times in /etc/apt/sources.list:8 and /etc/apt/sources.list.d/proxmox.sources:1
Target Translations (pve-no-subscription/i18n/Translation-en) is configured multiple times in /etc/apt/sources.list:8 and /etc/apt/sources.list.d/proxmox.sources:1
pve-manager/9.0.11/3bf5476b8a4699e2 (running kernel: 6.8.12-14-pve)
```
バージョンを確認したらちゃんと上がっとります。
何故かsshが切れなかったので、念の為にtmuxを張っていたけど切れなくて良かったです。
# Ref
[公式ドキュメント(In-place_upgradeの章)](https://pve.proxmox.com/wiki/Upgrade_from_8_to_9#In-place_upgrade)