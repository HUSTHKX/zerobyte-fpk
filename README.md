# zerobyte-fpk

[Zerobyte](https://github.com/nicotsx/zerobyte) 的 fnOS 原生安装包（fpk）自动构建仓库。

## 特点

- **直接基于官方 Docker 镜像** `ghcr.io/nicotsx/zerobyte:latest` 构建，不依赖任何第三方二次打包；
- 内置官方镜像自带的 `bun` / `restic` / `rclone` / `shoutrrr`；
- **中文界面**：构建时把 `i18n/zh.json` 的中英对照应用到产物上（服务端 SSR + 客户端 assets 都覆盖）；
- 启动脚本自带 `WEBHOOK_ALLOWED_ORIGINS`，通知功能开箱可用；
- 每天自动检查上游新版本，有新版就构建并发 Release，同时更新 `moo.json`。

## 目录

```
fpk/           fpk 外壳：manifest / cmd 生命周期脚本 / config / wizard / 图标 / ui
i18n/zh.json   英中对照字典（应用名 → 中文）
scripts/       build-fpk.sh 构建、apply-zh.py 汉化、update-moo.py 更新索引
moo.json       Moo 应用源索引（自动更新）
```

## 在 Moo 里添加

```
https://github.com/HUSTHKX/zerobyte-fpk
```

或 raw 直链：

```
https://raw.githubusercontent.com/HUSTHKX/zerobyte-fpk/main/moo.json
```

## 本地构建

```bash
docker pull ghcr.io/nicotsx/zerobyte:latest
cid=$(docker create ghcr.io/nicotsx/zerobyte:latest)
mkdir -p rootfs && docker export "$cid" | tar -xf - -C rootfs

bash scripts/build-fpk.sh 0.44.2 rootfs out
```

## 翻译

`i18n/zh.json` 是 `英文短语 → 中文` 的平铺映射。上游新增文案时，构建日志里的“汉化：替换 N 处”会变化，未覆盖的文案自动保持英文。

修改字典后重新构建即可生效，不需要改代码。
