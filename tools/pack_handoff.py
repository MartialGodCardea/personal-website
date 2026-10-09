# -*- coding: utf-8 -*-
"""打包交付压缩包 website-handoff.zip。

刻意排除：
  .git/           —— 无法靠复制可靠搬运（见 AGENTS.md §5.0）；需要带历史请用 git bundle
  .workbuddy-ai/  —— agent 的工作记录，不属于交付物
  __pycache__/    —— Python 字节码缓存
  *.zip           —— 避免把上一次的包打进新包
  _*              —— 截图 / 字体自查用的临时评审页（site/_shot.html、site/_cjkcheck.html 等），
                     它们是本地自查产物，不是交付物

用法：
    python tools/pack_handoff.py
"""
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "website-handoff.zip")

# 顶层散文件（保持这个顺序，解压后一眼能看到说明文档）
TOP = [".gitattributes", ".gitignore", "AGENTS.md", "README.md", "技术架构.md",
       "字体规范.md", "美术体检报告.md", "个人介绍.txt"]
TREES = ["site", "tools"]
# _font-compare/ 在根目录、不在任何一棵树里，天然不会被收进来
SKIP_DIRS = {".git", ".workbuddy-ai", "__pycache__", "node_modules"}


def collect():
    files = []
    for name in TOP:
        path = os.path.join(ROOT, name)
        if os.path.isfile(path):
            files.append((path, name))
        else:
            print("  ! 缺少 %s，已跳过" % name)
    for tree in TREES:
        base = os.path.join(ROOT, tree)
        for cur, dirs, names in os.walk(base):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for n in sorted(names):
                if n.endswith(".zip"):
                    continue
                # 下划线前缀 = 本地评审 / 自查的临时产物，不进交付包
                if n.startswith("_"):
                    continue
                path = os.path.join(cur, n)
                files.append((path, os.path.relpath(path, ROOT).replace(os.sep, "/")))
    return files


def main():
    files = collect()
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path, arc in files:
            z.write(path, arc)
    size = os.path.getsize(OUT)
    print("已写入 %s" % os.path.basename(OUT))
    print("  条目 %d 个，%s KB" % (len(files), format(size / 1024, ".0f")))
    print("  已排除：.git/  .workbuddy-ai/  __pycache__/  *.zip  _*(临时页)")


if __name__ == "__main__":
    main()
