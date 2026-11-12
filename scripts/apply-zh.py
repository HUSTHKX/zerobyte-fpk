#!/usr/bin/env python3
"""把中文字典应用到 Zerobyte 构建产物上（覆盖服务端 SSR 和客户端 assets）"""
import json, glob, re, sys

DICT = "/vol1/@appshare/fn-deepseek-harness/zerobyte-zh-dict.json"
TARGET = sys.argv[1] if len(sys.argv) > 1 else "/tmp/zbofficial/app/.output"

pairs = json.load(open(DICT))
# 少量确认安全的短标签（首字母大写，通常是界面标签）
SHORT_ALLOW = {
    "Email": "邮箱", "Username": "用户名", "Password": "密码", "Name": "名称",
    "Cancel": "取消", "Save": "保存", "Delete": "删除", "Edit": "编辑",
    "Create": "创建", "Back": "返回", "Close": "关闭", "Continue": "继续",
    "Confirm": "确认", "Search": "搜索", "Settings": "设置", "Login": "登录",
    "Logout": "退出登录", "Next": "下一步", "Previous": "上一步",
    "Warning": "警告", "Success": "成功", "Description": "描述",
}

# 太短或像枚举值的单词不翻，避免破坏逻辑
BLOCK_SINGLE = {
    "None", "Never", "Unknown", "Enabled", "Disabled", "Current", "Done",
    "Copied", "Optional", "Required", "Stale", "Healthy", "Success", "Error",
    "Warning", "Cancelled", "Running", "Started", "Finished",
}

def is_label(k):
    if any(t in k for t in ("{{", "${", "<", ">", "%s", "%d")):
        return False
    if len(k) >= 8 and " " in k:
        return True
    # 单词型界面标签：首字母大写、非全大写
    if len(k) >= 4 and k[:1].isupper() and not k.isupper() and re.fullmatch(r"[A-Za-z][A-Za-z0-9 ,.!?:;'\u2019-]*", k):
        return k not in BLOCK_SINGLE
    return False

safe = {k: v for k, v in pairs.items() if is_label(k)}
safe.update({k: v for k, v in SHORT_ALLOW.items() if k in pairs})
keys_sorted = sorted(safe, key=len, reverse=True)

lit = re.compile(r"([\"\x27`])([^\"\x27`\n\\]*?)\1")
total = 0; files = 0
for f in glob.glob(TARGET + "/**/*.mjs", recursive=True) + glob.glob(TARGET + "/**/*.js", recursive=True):
    s = open(f, encoding="utf-8", errors="ignore").read()
    orig = s; cnt = [0]
    def repl(m):
        q, txt = m.group(1), m.group(2)
        if txt in safe:
            cnt[0] += 1
            return q + safe[txt] + q
        return m.group(0)
    s = lit.sub(repl, s)
    if s != orig:
        open(f, "w", encoding="utf-8").write(s)
        total += cnt[0]; files += 1
print(f"应用 {total} 处替换，涉及 {files} 个文件")
