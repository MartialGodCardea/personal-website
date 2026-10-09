# -*- coding: utf-8 -*-
"""从水面横幅底图裁出社交分享封面 site/img/og-cover.jpg（1200×630）。

为什么是 1200×630：这是 og:image 的通行尺寸（1.91:1），微信 / 社交平台
抓取时按这个比例出卡片。water-bg.jpg 是 2400×1388（1.73:1），
按「覆盖」方式等比缩放后居中裁切即可，不会拉伸变形。

刻意**不做灰调**：站点正文里的灰阶是 CSS `filter: grayscale()` 现算的，
而分享卡片是在站外显示的，彩色涟漪比灰调更抓眼。

需要 Pillow。用法：
    python tools/make_og_cover.py
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
SRC = os.path.join(SITE, "img", "water-bg.jpg")
OUT = os.path.join(SITE, "img", "og-cover.jpg")

W, H = 1200, 630


def main():
    im = Image.open(SRC).convert("RGB")
    # 等比缩放到「至少盖住」目标框，再居中裁切
    scale = max(W / im.width, H / im.height)
    scaled = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    left = (scaled.width - W) // 2
    top = (scaled.height - H) // 2
    cover = scaled.crop((left, top, left + W, top + H))
    cover.save(OUT, "JPEG", quality=82, optimize=True, progressive=True)
    print("  wrote %s  %d×%d  %.0f KB"
          % (os.path.relpath(OUT, ROOT).replace(os.sep, "/"), W, H,
             os.path.getsize(OUT) / 1024))


if __name__ == "__main__":
    main()
