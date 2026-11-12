#!/usr/bin/env python3
"""
把中文字典应用到 Zerobyte 构建产物上（覆盖服务端 SSR 和客户端 assets）

用法: python3 apply-zh.py <产物目录(.output)> [字典路径]
"""
import glob
import json
import os
import re
import sys

TARGET = sys.argv[1] if len(sys.argv) > 1 else "app/.output"
DICT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "..", "i18n", "zh.json")

# 少量确认安全的短标签（首字母大写，通常是界面标签）
SHORT_ALLOW = {
    "Email": "邮箱", "Username": "用户名", "Password": "密码", "Name": "名称",
    "Cancel": "取消", "Save": "保存", "Delete": "删除", "Edit": "编辑",
    "Create": "创建", "Back": "返回", "Close": "关闭", "Continue": "继续",
    "Confirm": "确认", "Search": "搜索", "Settings": "设置", "Login": "登录",
    "Logout": "退出登录", "Next": "下一步", "Previous": "上一步",
    "Warning": "警告", "Success": "成功", "Description": "描述",
}

pairs = json.load(open(DICT, encoding="utf-8"))
safe = {
    k: v for k, v in pairs.items()
    if len(k) >= 8 and " " in k and not any(t in k for t in ("{{", "${", "<", ">", "%s", "%d"))
}
safe.update({k: v for k, v in SHORT_ALLOW.items() if k in pairs})

lit = re.compile(r"([\"\x27`])([^\"\x27`\n\\]*?)\1")


def repl_factory(counter):
    def repl(m):
        q, txt = m.group(1), m.group(2)
        if txt in safe:
            counter[0] += 1
            return q + safe[txt] + q
        return m.group(0)
    return repl


def main():
    total = 0
    files = 0
    targets = glob.glob(os.path.join(TARGET, "**/*.mjs"), recursive=True) + \
              glob.glob(os.path.join(TARGET, "**/*.js"), recursive=True)
    for f in targets:
        s = open(f, encoding="utf-8", errors="ignore").read()
        counter = [0]
        new = lit.sub(repl_factory(counter), s)
        if new != s:
            open(f, "w", encoding="utf-8").write(new)
            total += counter[0]
            files += 1
    print(f"汉化：替换 {total} 处，涉及 {files} 个文件（字典 {len(safe)} 条规则）")


if __name__ == "__main__":
    main()
