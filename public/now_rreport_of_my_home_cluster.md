---
title: Now Rreport of my home Cluster
tags:
- zennfes2025infra
private: false
updated_at: 2025-09-28 18:19
id: null
organization_url_name: null
slide: false
---
# 我が家のインフラまとめ
## Network
```mermaid
flowchart TD
    A[GlobalNetwork] --> B[Provider]
    B --> C[ONU & Router & AP]
    ceres-cf --> Cloudflare
    proxmox-cf --> Cloudflare
    Cloudflare --> A
    ironkube-con --> ironkube-work02

    subgraph Home /24
        C --> ceres[Proteus]
        C --> janus[iani]
        C --> proxmox[Proxmox]
    end

    subgraph ceres
        ceres-docker[docker]
        ceres-cf[Cloudflared]
        ironkube-work02
    end

    subgraph ceres-docker
        Minecraft01[priv Minecraft01]
    end

    subgraph proxmox
        proxmox-cf[Cloudflared]
        dokuwiki --> proxmox-cf
        proxmox-gate[Janus-gate] --> proxmox-cf
        Softether
        GithubRunners
        ironkube-con --> ironkube-work01
    end
```
※Ceres is internal server name.
※ironkube is internal k8s cluster name.
## Spec
### Proxmox
|||
|-|-|
|CPU|Intel Core i3-4170|
|Mem|DDR3 8GB|
|SSD|128GB|
|HDD1|512GB|
|HDD2|512GB|
### Ceres
|||
|-|-|
|CPU|AMD Ryzen 3 PRO 2200G|
|Mem|DDR4 16GB|
|SSD|1TB|
## OS
### Proxmox's VM
|||
|-|-|
|cloudflared|UbuntuServer|
|dokuwiki|AlpineLinux|
|moodle|AlpineLinux|
|softether|UbuntuServer|
|github runner|UbuntuServer|
|janus-gate|GentooLinux|
### Ceres
UbuntuServer
