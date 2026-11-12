#!/usr/bin/env python3
"""
给修改过的资源文件改名（加 -zh 后缀），并更新所有引用。
这样浏览器缓存和 service worker 都不会复用旧文件。

用法: python3 version-assets.py <.output 目录>
"""
import glob
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "app/.output"
CJK = re.compile(r"[\u4e00-\u9fa5]")
ASSET_DIR = os.path.join(ROOT, "public", "assets")


def main():
    if not os.path.isdir(ASSET_DIR):
        print("找不到 assets 目录")
        return

    renames = {}
    for f in glob.glob(os.path.join(ASSET_DIR, "*")):
        base = os.path.basename(f)
        if "-zh." in base or not base.endswith((".js", ".css")):
            continue
        try:
            s = open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        if not CJK.search(s):
            continue
        stem, ext = os.path.splitext(base)
        new = f"{stem}-zh{ext}"
        renames[base] = new
        os.rename(f, os.path.join(ASSET_DIR, new))

    if not renames:
        print("没有需要改名的资源")
        return

    # 更新引用：public 下的 html/js/mjs + server 下的 mjs
    targets = []
    for pat in ("**/*.html", "**/*.js", "**/*.mjs", "**/*.css"):
        targets += glob.glob(os.path.join(ROOT, pat), recursive=True)

    changed = 0
    for f in set(targets):
        try:
            s = open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        new = s
        for old, rep in renames.items():
            if old in new:
                new = new.replace(old, rep)
        if new != s:
            open(f, "w", encoding="utf-8").write(new)
            changed += 1

    print(f"资源改名 {len(renames)} 个，更新引用 {changed} 个文件")


if __name__ == "__main__":
    main()
