#!/bin/bash
#
# 从官方镜像导出的 rootfs 构建 fnOS fpk
# 用法: bash scripts/build-fpk.sh <版本号> <rootfs目录> [输出目录]
#
set -euo pipefail

VER="${1:?需要版本号}"
ROOTFS="${2:?需要 rootfs 目录}"
OUTDIR="${3:-out}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

[ -d "$ROOTFS/app" ] || { echo "rootfs 里找不到 app/"; exit 1; }

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/fpk" "$WORK/payload" "$OUTDIR"

# 1. fpk 外壳
cp -a "$REPO_ROOT/fpk/." "$WORK/fpk/"

# 2. 负载
cp -a "$ROOTFS/app" "$WORK/payload/app"
mkdir -p "$WORK/payload/bin"
for b in bun rclone restic shoutrrr; do
    cp "$ROOTFS/usr/local/bin/$b" "$WORK/payload/bin/$b"
    chmod +x "$WORK/payload/bin/$b"
done
[ -d "$REPO_ROOT/fpk/ui" ] && cp -a "$REPO_ROOT/fpk/ui" "$WORK/payload/ui"

# 3. 汉化
python3 "$REPO_ROOT/scripts/apply-zh.py" "$WORK/payload/app/.output" "$REPO_ROOT/i18n/zh.json"

# 4. app.tgz
tar czf "$WORK/fpk/app.tgz" -C "$WORK/payload" app bin ui 2>/dev/null || \
    tar czf "$WORK/fpk/app.tgz" -C "$WORK/payload" app bin
SUM=$(md5sum "$WORK/fpk/app.tgz" | cut -d' ' -f1)

# 5. manifest
python3 - "$WORK/fpk/manifest" "$VER" "$SUM" <<'PY'
import sys
p, ver, sum_ = sys.argv[1], sys.argv[2], sys.argv[3]
lines = open(p, encoding="utf-8").read().split("\n")
out = []
for ln in lines:
    if ln.startswith("version"): ln = f"version                    = {ver}"
    elif ln.startswith("checksum"): ln = f"checksum                   = {sum_}"
    elif ln.startswith("changelog"): ln = f"changelog                  = 基于官方镜像 {ver} 构建，内置 restic/rclone/shoutrrr，中文界面"
    out.append(ln)
open(p, "w", encoding="utf-8").write("\n".join(out))
PY

# 5.5 规范化权限（飞牛要求 755/644 + root 属主）
find "$WORK/fpk" -type d -exec chmod 755 {} +
find "$WORK/fpk" -type f -exec chmod 644 {} +
chmod 755 "$WORK/fpk/cmd/"* "$WORK/fpk/wizard/"* 2>/dev/null || true

# 6. 打包
FINAL="$OUTDIR/zerobyte-x86-${VER}.fpk"
tar czf "$FINAL" -C "$WORK/fpk" $(ls -A "$WORK/fpk")
echo "生成: $FINAL"
ls -lh "$FINAL"
sha256sum "$FINAL"
