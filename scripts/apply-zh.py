#!/usr/bin/env python3
"""
把中文字典应用到 Zerobyte 构建产物上（服务端 SSR + 客户端 assets）

用法: python3 apply-zh.py <产物目录(.output)> [字典路径]

实现：按「精确引号形式」替换，例如把 "Sources"、'Sources'、`Sources`
整体换成对应中文，不做 JS 语法解析——压缩代码里模板字符串含引号，
任何基于正则配对的扫描都会错位，反而漏掉大量字面量。
"""
import glob
import json
import os
import re
import sys

TARGET = sys.argv[1] if len(sys.argv) > 1 else "app/.output"

_default_dicts = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "i18n", "zh.json"),
    "/vol1/@appshare/fn-deepseek-harness/zerobyte-zh-dict.json",
]
if len(sys.argv) > 2:
    DICT = sys.argv[2]
else:
    DICT = next((d for d in _default_dicts if os.path.exists(d)), _default_dicts[0])

# 少量确认安全的短标签（首字母大写，通常是界面标签）
SHORT_ALLOW = {
    "Email": "邮箱", "Username": "用户名", "Password": "密码", "Name": "名称",
    "Cancel": "取消", "Save": "保存", "Delete": "删除", "Edit": "编辑",
    "Create": "创建", "Back": "返回", "Close": "关闭", "Continue": "继续",
    "Confirm": "确认", "Search": "搜索", "Settings": "设置", "Login": "登录",
    "Logout": "退出登录", "Next": "下一步", "Previous": "上一步",
    "Warning": "警告", "Success": "成功", "Description": "描述",
}

# 看起来像枚举值/状态值的单词不翻，避免破坏逻辑
BLOCK_SINGLE = {
    "None", "Never", "Unknown", "Enabled", "Disabled", "Current", "Done",
    "Copied", "Optional", "Required", "Stale", "Success", "Error",
    "Warning", "Cancelled", "Running", "Started", "Finished",
}

WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9 ,.!?:;'\u2019-]*")


def is_label(k: str) -> bool:
    if any(t in k for t in ("${", "<", ">", "%s")):
        return False
    if len(k) >= 8 and " " in k:
        return True
    if len(k) >= 4 and k[:1].isupper() and not k.isupper() and WORD_RE.fullmatch(k):
        return k not in BLOCK_SINGLE
    return False


def build_patterns(mapping, chunk=400):
    keys = sorted(mapping, key=len, reverse=True)
    pats = []
    for i in range(0, len(keys), chunk):
        alts = []
        for k in keys[i:i + chunk]:
            for q in ('"', "'", "`"):
                alts.append(re.escape(q + k + q))
        pats.append(re.compile("|".join(alts)))
    return pats


def replace_exact(s, mapping, patterns):
    count = 0

    def repl(m):
        nonlocal count
        tok = m.group(0)
        inner = tok[1:-1]
        if inner in mapping:
            count += 1
            return tok[0] + mapping[inner] + tok[0]
        return tok

    for pat in patterns:
        s = pat.sub(repl, s)
    return s, count


def main():
    pairs = json.load(open(DICT, encoding="utf-8"))
    safe = {k: v for k, v in pairs.items() if is_label(k)}
    safe.update({k: v for k, v in SHORT_ALLOW.items() if k in pairs})
    patterns = build_patterns(safe)

    total = 0
    files = 0
    targets = glob.glob(os.path.join(TARGET, "**/*.mjs"), recursive=True) + \
              glob.glob(os.path.join(TARGET, "**/*.js"), recursive=True)
    for f in targets:
        s = open(f, encoding="utf-8", errors="ignore").read()
        new, cnt = replace_exact(s, safe, patterns)
        if cnt:
            open(f, "w", encoding="utf-8").write(new)
            total += cnt
            files += 1
    print(f"汉化：替换 {total} 处，涉及 {files} 个文件（规则 {len(safe)} 条）")


if __name__ == "__main__":
    main()
