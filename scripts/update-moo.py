#!/usr/bin/env python3
"""构建完成后更新 moo.json 索引"""
import argparse
import hashlib
import json
import os
import time

ap = argparse.ArgumentParser()
ap.add_argument("--version", required=True)
ap.add_argument("--fpk", required=True)
ap.add_argument("--repo", required=True, help="owner/repo")
ap.add_argument("--out", default="moo.json")
a = ap.parse_args()

data = open(a.fpk, "rb").read()
sha = hashlib.sha256(data).hexdigest()
size = len(data)
name = os.path.basename(a.fpk)

index = {
    "schema_version": "moo",
    "source_info": {
        "name": "Zerobyte (官方镜像重打包)",
        "author": "HUSTHKX",
        "homepage": f"https://github.com/{a.repo}",
        "description": "基于 nicotsx/zerobyte 官方镜像构建的 fnOS 原生包，内置 restic/rclone/shoutrrr，界面中文。",
    },
    "apps": {
        "zerobyte": {
            "display_name": "Zerobyte 加密备份",
            "version": a.version,
            "download_url": f"https://github.com/{a.repo}/releases/download/v{a.version}/{name}",
            "platform": "x86",
            "sha256": sha,
            "size_bytes": size,
            "categories": ["备份"],
            "desc": f"Zerobyte {a.version}，基于官方镜像构建，中文界面，内置 restic/rclone/shoutrrr。",
            "homepage": "https://github.com/nicotsx/zerobyte",
            "bug_report_url": f"https://github.com/{a.repo}/issues",
            "maintainer": "HUSTHKX",
            "distributor": "HUSTHKX",
            "updated_at": time.strftime("%Y-%m-%d"),
            "changelog": f"基于官方镜像 {a.version} 构建。",
        }
    },
}

with open(a.out, "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"已更新 {a.out}: v{a.version} sha256={sha[:16]}... size={size}")
