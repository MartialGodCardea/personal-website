#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成全站中文字体子集（Noto Serif SC）。

把下面三处出现的字符取并集，从 Noto Serif SC 可变字体里切出只含这些字的 woff2：

  1. site/ 下全部 *.html        —— 正文 + 属性里的运行时文案
                                  （data-label / aria-label / alt / title / 导航副标签）
  2. site/js/main.js            —— 运行时字符串（「复制」「已复制」「二维码」「预览」…）
  3. tools/build_pages.py       —— NOTES / JOURNAL 正文 + 生成器文案

为什么要它：旧的 noto-serif-sc-name.woff2 只含「王松林」三个字。页面上其它中文
（署名「署名给你和我自由的心」、弹窗标签、复制按钮）会 fallback 到系统宋体，
而它们设了 font-weight: 900 —— 系统宋体没有 900 字重，浏览器就用伪粗体机械加粗，
衬线糊、笔画发胖。结果是同一页上的中文衬线实际是两种字体、两种字重渲染方式，
也就是「拼接感」。做成全站子集后，这些字全部由同一个可变字体渲染。

用法：
    python tools/build_font_subset.py

产物：
    site/fonts/noto-serif-sc-subset.woff2

脚本末尾会读回产物的 cmap，断言「用到的字符 ⊆ 产物字形」，
缺字则打印缺失字符并非零退出 —— 所以它可以进自查清单反复跑。

注意：woff2 不是可复现产物（不同 fontTools 版本的字节不同），
      校验以 cmap 覆盖为准，不以文件字节为准。
"""

import os
import sys
import glob
import tempfile
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
OUT = os.path.join(SITE, "fonts", "noto-serif-sc-subset.woff2")

# 源字体：优先用系统里那份可变字体（OFL 授权，可自由再分发）
WINDIR = os.environ.get("WINDIR", r"C:\Windows")
SRC_CANDIDATES = [
    os.path.join(WINDIR, "Fonts", "NotoSerifSC-VF.ttf"),
    os.path.join(WINDIR, "Fonts", "NotoSerifSC-Regular.otf"),
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
]

# 留一组兜底字符，避免运行时才出现的字符（日期后缀、序号等）掉回系统字体
SAFETY = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" \
         " .,:;!?()[]{}<>/\\|-_+=*&%$#@~^'\"`" \
         "、。，．：；！？（）「」『』【】《》〈〉—…·©®°±×÷≈≠≤≥∞"


def collect_chars():
    """三源并集。返回 (字符集合, 各来源的贡献统计)。

    控制字符（换行、制表、回车…）会被剔除 —— 它们不需要字形，
    留着会让覆盖校验误报。
    """
    chars = set(SAFETY)
    detail = []

    html_files = sorted(glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True))
    n = 0
    for path in html_files:
        with open(path, encoding="utf-8") as f:
            got = set(f.read())
        chars |= got
        n += len(got)
    detail.append(("site/**/*.html（%d 个文件）" % len(html_files), n))

    for rel in ("js/main.js", "css/style.css"):
        path = os.path.join(SITE, rel.replace("/", os.sep))
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                got = set(f.read())
            chars |= got
            detail.append(("site/" + rel, len(got)))

    bp = os.path.join(ROOT, "tools", "build_pages.py")
    if os.path.exists(bp):
        with open(bp, encoding="utf-8") as f:
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


def find_source():
    for p in SRC_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


def main():
    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont
    except ImportError:
        print("缺少 fontTools。请先安装：", file=sys.stderr)
        print('  pip install "fonttools[woff]"', file=sys.stderr)
        return 2

    src = find_source()
    if not src:
        print("找不到源字体，试过：", file=sys.stderr)
        for p in SRC_CANDIDATES:
            print("  " + p, file=sys.stderr)
        return 2

    chars, detail = collect_chars()
    text = "".join(sorted(chars))
    cjk, punct, ascii_chars, other = classify(chars)

    print("源字体   : %s" % src)
    print("字符总数 : %d" % len(chars))
    print("  汉字   : %d" % len(cjk))
    print("  全角标点: %d" % len(punct))
    print("  ASCII  : %d" % len(ascii_chars))
    print("  其它   : %d  %s" % (len(other), "".join(sorted(other))[:40]))
    print("各来源贡献（去重前）：")
    for name, n in detail:
        print("  %-28s %d" % (name, n))

    with TTFont(src, lazy=True) as probe:
        axes = [(a.axisTag, a.minValue, a.maxValue) for a in probe["fvar"].axes] \
            if "fvar" in probe else []
        print("源字体可变轴: %s" % (axes or "（静态字体）"))

    # 写临时字符表，交给 subsetter
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
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        subset.save_font(font, OUT, options)
        font.close()
    finally:
        os.unlink(text_file)

    size = os.path.getsize(OUT)
    print("\n产物     : %s" % os.path.relpath(OUT, ROOT))
    print("体积     : %s KB" % format(size / 1024, ".1f"))

    # ---- 覆盖自校验：产物的 cmap 必须包含全部用到的字符 ----
    with TTFont(OUT, lazy=True) as out:
        cmap = set(out.getBestCmap().keys())
    missing = sorted(c for c in chars if ord(c) not in cmap)
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


if __name__ == "__main__":
    sys.exit(main())
