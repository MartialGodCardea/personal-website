#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成全站字体子集（中文 Noto Serif SC ＋ 西文 Newsreader）。

把下面几处出现的字符取并集，再从各自的源字体里切出只含这些字的 woff2：

  1. site/ 下全部 *.html        —— 正文 + 属性里的运行时文案
                                  （data-label / aria-label / alt / title / 导航副标签）
  2. site/js/main.js            —— 运行时字符串（「复制」「已复制」「二维码」「预览」…）
  3. site/css/style.css         —— content 里的伪元素文案
  4. tools/build_pages.py       —— NOTES / JOURNAL 正文 + 生成器文案

两个产物：

  A. site/fonts/noto-serif-sc-subset.woff2   中文（含 ASCII 兜底），全字符集
  B. site/fonts/newsreader-latin.woff2       西文，只取源字体能渲染的那部分

为什么要 A：旧的 noto-serif-sc-name.woff2 只含「王松林」三个字。页面上其它中文
（署名、弹窗标签、复制按钮）会 fallback 到系统宋体，而它们设了 font-weight: 900 ——
系统宋体没有 900 字重，浏览器就用伪粗体机械加粗，衬线糊、笔画发胖。同一页上的中文
衬线实际是两种字体、两种字重渲染方式，也就是「拼接感」。

为什么要 B：西文改用 Newsreader 后，Google Fonts 的 latin 子集有 262 个字形、
130 KB，而站点实际只用到约 104 个字符。按用字再切一刀能省掉一半体积。

B 特意保留 wght（200–800）与 opsz（6–72）两条可变轴：
`font-optical-sizing: auto` 会让浏览器按字号自动取光学尺寸 ——
340px 的巨型字标取到显示档（笔画更锐、对比更强），
10px 的版权行取到文本档（笔画更粗、更抗虚）。

用法：
    python tools/build_font_subset.py

脚本末尾会读回产物的 cmap，断言「用到的字符 ⊆ 产物字形」，
缺字则打印缺失字符并非零退出 —— 所以它可以进自查清单反复跑。

注意：woff2 不是可复现产物（不同 fontTools 版本的字节不同），
      校验以 cmap 覆盖为准，不以文件字节为准。
"""

import os
import re
import sys
import glob
import tempfile
import unicodedata
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
FONTS = os.path.join(SITE, "fonts")

# 源字体 A：优先用系统里那份可变字体（OFL 授权，可自由再分发）
WINDIR = os.environ.get("WINDIR", r"C:\Windows")
CJK_SOURCES = [
    os.path.join(WINDIR, "Fonts", "NotoSerifSC-VF.ttf"),
    os.path.join(WINDIR, "Fonts", "NotoSerifSC-Regular.otf"),
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
]

# 源字体 B：随仓库携带（tools/font-src/），保证离线可重建
LATIN_SRC = os.path.join(ROOT, "tools", "font-src", "newsreader-vf.woff2")
# 若缺失则按此地址补下（Google Fonts 的 latin 子集，OFL）
LATIN_SRC_URL = ("https://fonts.googleapis.com/css2?family=Newsreader"
                 ":opsz,wght@6..72,200..800&display=swap")
LATIN_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# 留一组兜底字符，避免运行时才出现的字符（日期后缀、序号等）掉回系统字体
SAFETY = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" \
         " .,:;!?()[]{}<>/\\|-_+=*&%$#@~^'\"`" \
         "、。，．：；！？（）「」『』【】《》〈〉—…·©®°±×÷≈≠≤≥∞"

TARGETS = [
    {
        "label": "中文（Noto Serif SC）",
        "out": os.path.join(FONTS, "noto-serif-sc-subset.woff2"),
        "sources": CJK_SOURCES,
        "restrict": False,   # 用全字符集
    },
    {
        "label": "西文（Newsreader）",
        "out": os.path.join(FONTS, "newsreader-latin.woff2"),
        "sources": [LATIN_SRC],
        "restrict": True,    # 只取源字体能渲染的部分，其余交给中文字体兜底
    },
]


def strip_comments(text, kind):
    """去掉注释再取字。

    注释永远不会被渲染，把它们算进子集只会让字体随着文档改动而白白变大
    （实测：在 style.css 里补一段中文说明，中文子集就多了 6 KB）。
    这里只处理两种语法上无歧义的注释，避免误伤：
      · CSS / JS 的块注释 /* … */
      · HTML 注释 <!-- … -->
    刻意不处理 JS 的 // 行注释 —— 里面可能是 https:// 这类 URL。
    """
    if kind in ("css", "js"):
        return re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    if kind == "html":
        return re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return text


def collect_chars():
    """多源并集。返回 (字符集合, 各来源的贡献统计)。

    控制字符（换行、制表、回车…）会被剔除 —— 它们不需要字形，
    留着会让覆盖校验误报。
    """
    chars = set(SAFETY)
    detail = []

    html_files = [p for p in sorted(
        glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True))
        # 跳过临时评审页（_cjkcheck.html / _shot.html / _frame.html …）：
        # 它们不进交付包，不该影响字体子集的构成
        if not os.path.basename(p).startswith("_")]
    n = 0
    for path in html_files:
        with open(path, encoding="utf-8") as f:
            got = set(strip_comments(f.read(), "html"))
        chars |= got
        n += len(got)
    detail.append(("site/**/*.html（%d 个文件）" % len(html_files), n))

    for rel, kind in (("js/main.js", "js"), ("css/style.css", "css")):
        path = os.path.join(SITE, rel.replace("/", os.sep))
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                got = set(strip_comments(f.read(), kind))
            chars |= got
            detail.append(("site/" + rel, len(got)))

    bp = os.path.join(ROOT, "tools", "build_pages.py")
    if os.path.exists(bp):
        with open(bp, encoding="utf-8") as f:
            # Python 用 # 与三引号，没有 /* */；这里不做剥离，
            # 免得误伤模板里的十六进制色值（#111）或 URL。
            got = set(f.read())
        chars |= got
        detail.append(("tools/build_pages.py", len(got)))

    chars = {c for c in chars if unicodedata.category(c) != "Cc"}
    return chars, detail


def classify(chars):
    """粗略分类，便于在输出里看清子集构成。"""
    cjk = [c for c in chars if "\u4e00" <= c <= "\u9fff"]
    punct = [c for c in chars if unicodedata.category(c).startswith("P")
             and ord(c) > 0x2000]
    ascii_chars = [c for c in chars if ord(c) < 0x80]
    other = [c for c in chars if c not in set(cjk) | set(punct) | set(ascii_chars)]
    return cjk, punct, ascii_chars, other


def find_source(candidates):
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def ensure_latin_source():
    """西文源字体随仓库携带；万一缺失就按 Google Fonts 的 CSS 补下。"""
    if os.path.exists(LATIN_SRC):
        return LATIN_SRC
    print("西文源字体缺失，尝试补下 …", file=sys.stderr)
    try:
        req = urllib.request.Request(LATIN_SRC_URL, headers={"User-Agent": LATIN_UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            css = r.read().decode("utf-8")
        import re
        urls = re.findall(r"url\((https://[^)]+\.woff2)\)", css)
        if not urls:
            return None
        os.makedirs(os.path.dirname(LATIN_SRC), exist_ok=True)
        req2 = urllib.request.Request(urls[-1], headers={"User-Agent": LATIN_UA})
        with urllib.request.urlopen(req2, timeout=60) as r:
            data = r.read()
        with open(LATIN_SRC, "wb") as f:
            f.write(data)
        print("  ✓ 已写入 %s" % os.path.relpath(LATIN_SRC, ROOT), file=sys.stderr)
        return LATIN_SRC
    except Exception as e:
        print("  ✗ 补下失败：%s" % e, file=sys.stderr)
        return None


def build(target, all_chars):
    """切一个子集。返回 0 成功 / 非 0 失败。"""
    from fontTools import subset
    from fontTools.ttLib import TTFont

    print("\n" + "=" * 68)
    print("目标：%s" % target["label"])

    src = find_source(target["sources"])
    if not src:
        print("找不到源字体，试过：", file=sys.stderr)
        for p in target["sources"]:
            print("  " + p, file=sys.stderr)
        return 2
    print("源字体：%s" % os.path.relpath(src, ROOT))

    with TTFont(src, lazy=True) as probe:
        src_cmap = set(probe.getBestCmap().keys())
        axes = [(a.axisTag, a.minValue, a.maxValue) for a in probe["fvar"].axes] \
            if "fvar" in probe else []
        print("源字体可变轴：%s" % (axes or "（静态字体）"))

    if target["restrict"]:
        chars = {c for c in all_chars if ord(c) in src_cmap}
        dropped = sorted(c for c in all_chars if ord(c) not in src_cmap)
    else:
        chars = set(all_chars)
        dropped = []

    text = "".join(sorted(chars))
    print("字符数：%d" % len(chars))
    if dropped:
        print("源字体未覆盖、将交给下一顺位字体的 %d 个字符：%s"
              % (len(dropped), "".join(dropped)))

    fd, text_file = tempfile.mkstemp(suffix=".txt", prefix="fontsubset-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)

    try:
        options = subset.Options()
        options.flavor = "woff2"          # 需要 brotli，由 fonttools[woff] 带上
        options.layout_features = ["*"]   # 保留全部 OpenType 特性
        options.hinting = False
        options.desubroutinize = True
        options.drop_tables += ["DSIG"]
        options.recalc_bounds = True
        options.name_IDs = ["*"]

        font = subset.load_font(src, options)
        subsetter = subset.Subsetter(options=options)
        subsetter.populate(text=text)
        subsetter.subset(font)
        os.makedirs(os.path.dirname(target["out"]), exist_ok=True)
        subset.save_font(font, target["out"], options)
        font.close()
    finally:
        os.unlink(text_file)

    size = os.path.getsize(target["out"])
    print("产物：%s" % os.path.relpath(target["out"], ROOT))
    print("体积：%s KB" % format(size / 1024, ".1f"))

    with TTFont(target["out"], lazy=True) as out:
        out_cmap = set(out.getBestCmap().keys())
        out_axes = [(a.axisTag, a.minValue, a.maxValue) for a in out["fvar"].axes] \
            if "fvar" in out else []
    print("产物可变轴：%s" % (out_axes or "（静态字体）"))

    missing = sorted(c for c in chars if ord(c) not in out_cmap)
    if missing:
        print("\n✗ 覆盖校验失败，缺 %d 个字符：" % len(missing), file=sys.stderr)
        for c in missing[:40]:
            try:
                name = unicodedata.name(c)
            except ValueError:
                name = "<无名称>"
            print("  U+%04X  %-28s %r" % (ord(c), name, c), file=sys.stderr)
        if len(missing) > 40:
            print("  …还有 %d 个" % (len(missing) - 40), file=sys.stderr)
        print("  这些字会 fallback 到系统字体，出现字形突变。", file=sys.stderr)
        return 1

    print("✓ 覆盖校验通过：%d 个字符全部在产物字形内" % len(chars))
    return 0


def main():
    try:
        import fontTools  # noqa: F401
    except ImportError:
        print("缺少 fontTools。请先安装：", file=sys.stderr)
        print('  pip install "fonttools[woff]"', file=sys.stderr)
        return 2

    chars, detail = collect_chars()
    cjk, punct, ascii_chars, other = classify(chars)

    print("字符并集：%d" % len(chars))
    print("  汉字   ：%d" % len(cjk))
    print("  全角标点：%d" % len(punct))
    print("  ASCII  ：%d" % len(ascii_chars))
    print("  其它   ：%d  %s" % (len(other), "".join(sorted(other))[:40]))
    print("各来源贡献（去重前）：")
    for name, n in detail:
        print("  %-28s %d" % (name, n))

    if not os.path.exists(LATIN_SRC):
        ensure_latin_source()

    rc = 0
    for target in TARGETS:
        rc |= build(target, chars)

    print("\n" + "=" * 68)
    print("完成。" if rc == 0 else "有目标未通过校验。")
    return rc


if __name__ == "__main__":
    sys.exit(main())
