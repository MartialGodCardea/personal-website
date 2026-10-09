#!/usr/bin/env python
"""把 main 分支的 site/ 目录发布到 gh-pages 分支（GitHub Pages 的发布源）。

为什么需要这个脚本
------------------
GitHub Pages 只能从「仓库根目录」或「/docs」发布，而本仓库的根目录放的是
构建脚本（tools/）和文档（*.md），成品全在 site/ 下。为了不给部署去改仓库
结构，改用 gh-pages 分支承载站点内容 —— 由本脚本从 main 的 site/ 子树生成。

流程
----
1. 确认 site/ 没有未提交的改动（否则线上会比本地旧，容易误判）
2. 取 `main:site` 的 tree 对象（这个 tree 已经在 main 的历史里）
3. 以该 tree 造一个提交，父提交是当前 gh-pages（保持线性、可快进推送）
4. 把 gh-pages 指向新提交并推送

用法
----
    python tools/deploy_pages.py

发布地址：https://martialgodcardea.github.io/personal-website/
（Pages 构建通常 1~3 分钟，之后刷新即可）
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://martialgodcardea.github.io/personal-website/"
DEPLOY_BRANCH = "gh-pages"
SOURCE = "main:site"


def git(*args: str, capture: bool = True) -> str:
    """跑一条 git 命令。失败就抛 SystemExit，把 stderr 原样带出来。"""
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=capture,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise SystemExit(f"✗ git {' '.join(args)} 失败：\n{detail}")
    return (proc.stdout or "").strip()


def main() -> int:
    # 1. site/ 必须干净。带未提交改动发布，线上会和本地对不上。
    dirty = git("status", "--porcelain", "--", "site")
    if dirty:
        print("✗ site/ 下有未提交的改动，先提交再发布：\n")
        print(dirty)
        return 1

    # 2. 取 site 子树。这个对象随 main 的推送已经存在于远端，不用重新上传。
    tree = git("rev-parse", SOURCE)
    print(f"· site tree   {tree[:12]}")

    # 3. 造提交。有旧 gh-pages 就挂上去，保持线性历史、可快进。
    parent = ""
    try:
        parent = git("rev-parse", "--verify", f"refs/heads/{DEPLOY_BRANCH}")
    except SystemExit:
        pass  # 分支还不存在，第一次发布

    args = ["commit-tree", tree]
    if parent:
        args += ["-p", parent]
    args += ["-m", f"部署：发布 {SOURCE} 的内容"]
    commit = git(*args)
    print(f"· 新提交      {commit[:12]}  (父 {parent[:12] or '无'})")

    # 4. 移动分支并推送
    git("branch", "-f", DEPLOY_BRANCH, commit)
    print(f"· 推送 {DEPLOY_BRANCH} → origin ...")
    git("push", "origin", DEPLOY_BRANCH, capture=False)

    print(f"\n✅ 已发布：{SITE_URL}")
    print("   Pages 构建通常 1~3 分钟，之后刷新即可。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
