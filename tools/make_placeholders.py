# -*- coding: utf-8 -*-
"""Generate a coherent set of placeholder plates.

They stand in for photography so the layout reads correctly: abstract
monochrome compositions with a real tonal range, so the site's
grayscale -> colour hover treatment has something to work with.

Replace the files in site/img/ with real photographs (same filenames) whenever
you are ready — the layout does not care which image is in there.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "site", "img")


# --------------------------------------------------------------- primitives ---
def gradient(w, h, stops, angle=90):
    """stops: [(pos 0..1, (r,g,b)), ...] painted along `angle` degrees."""
    img = Image.new("RGB", (w, h))
    px = img.load()
    rad = math.radians(angle)
    dx, dy = math.cos(rad), math.sin(rad)
    span = abs(dx) * w + abs(dy) * h
    for y in range(h):
        for x in range(w):
            t = (x * dx + y * dy) / span
            t = 0.0 if t < 0 else (1.0 if t > 1 else t)
            for i in range(len(stops) - 1):
                p0, c0 = stops[i]
                p1, c1 = stops[i + 1]
                if p0 <= t <= p1:
                    k = (t - p0) / max(p1 - p0, 1e-6)
                    px[x, y] = tuple(int(c0[j] + (c1[j] - c0[j]) * k) for j in range(3))
                    break
            else:
                px[x, y] = stops[-1][1]
    return img


def soft_shape(img, box, fill, blur):
    layer = Image.new("RGB", img.size, (255, 255, 255))
    d = ImageDraw.Draw(layer)
    d.ellipse(box, fill=fill)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return Image.blend(img, layer, 1.0)


def grain(img, sigma=6.0, amount=0.10):
    noise = Image.effect_noise(img.size, sigma).convert("L")
    return Image.blend(img, Image.merge("RGB", (noise, noise, noise)), amount)


def vignette(img, amount=0.30, spread=0.18):
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse([-w * 0.2, -h * 0.3, w * 1.2, h * 1.3], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(min(w, h) * spread))
    dark = Image.new("RGB", (w, h), (12, 12, 12))
    return Image.composite(img, Image.blend(img, dark, amount), mask)


def finish(img, name, blur=1.2, grain_amount=0.10, vig=0.30):
    img = img.filter(ImageFilter.GaussianBlur(blur))
    img = grain(img, 6.0, grain_amount)
    img = vignette(img, vig)
    img = img.filter(ImageFilter.GaussianBlur(0.4))
    img.save(os.path.join(OUT, name), "JPEG", quality=90, optimize=True)
    print("   %-18s %s" % (name, img.size))


# -------------------------------------------------------------- compositions ---
def plate_checklist(w, h):
    """AI 辅助排障清单 — a checked list on a bright surface."""
    img = gradient(w, h, [(0, (243, 241, 237)), (0.55, (222, 219, 213)),
                          (1, (176, 172, 166))], angle=100)
    d = ImageDraw.Draw(img)
    n = 9
    top, bottom = h * 0.22, h * 0.80
    step = (bottom - top) / (n - 1)
    for i in range(n):
        y = top + i * step
        x0 = w * 0.18
        box = min(w, h) * 0.032
        done = i in (0, 3, 6)
        d.rectangle([x0, y - box / 2, x0 + box, y + box / 2],
                    fill=(38, 37, 36) if done else None,
                    outline=(38, 37, 36), width=2)
        if done:
            d.line([x0 + box * 0.2, y, x0 + box * 0.42, y + box * 0.28], fill=(243, 241, 237), width=2)
            d.line([x0 + box * 0.42, y + box * 0.28, x0 + box * 0.82, y - box * 0.30],
                   fill=(243, 241, 237), width=2)
        d.line([x0 + box * 1.9, y, x0 + box * 1.9 + w * (0.30 + 0.14 * ((i * 7) % 5) / 4), y],
               fill=(52, 51, 50) if done else (120, 118, 114), width=2)
    return img


def plate_flow(w, h):
    """工单闭环流程优化 — nodes and connectors."""
    img = gradient(w, h, [(0, (232, 230, 226)), (0.5, (166, 163, 157)),
                          (1, (70, 69, 66))], angle=120)
    d = ImageDraw.Draw(img)
    pts = [(0.14, 0.30), (0.34, 0.66), (0.55, 0.26), (0.76, 0.62), (0.92, 0.36)]
    pts = [(x * w, y * h) for x, y in pts]
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        mx = (x0 + x1) / 2
        d.line([x0, y0, mx, y0, mx, y1, x1, y1], fill=(248, 247, 244), width=3, joint="curve")
    for i, (x, y) in enumerate(pts):
        r = min(w, h) * (0.036 if i % 2 else 0.026)
        if i % 2:
            d.ellipse([x - r, y - r, x + r, y + r], fill=(248, 247, 244))
        else:
            d.rectangle([x - r, y - r, x + r, y + r], fill=(30, 30, 29))
            d.rectangle([x - r, y - r, x + r, y + r], outline=(248, 247, 244), width=2)
    return img


def plate_grid(w, h):
    """内部知识库重建 — a field of entries."""
    img = gradient(w, h, [(0, (60, 59, 57)), (0.6, (128, 126, 121)),
                          (1, (206, 203, 198))], angle=75)
    d = ImageDraw.Draw(img)
    cols, rows = 7, 5
    x0, y0 = w * 0.14, h * 0.22
    cw, chh = w * 0.72 / cols, h * 0.56 / rows
    for r in range(rows):
        for c in range(cols):
            x = x0 + c * cw
            y = y0 + r * chh
            box = [x, y, x + cw * 0.56, y + chh * 0.46]
            if (r * cols + c) % 6 == 0:
                d.rectangle(box, fill=(240, 238, 234))
            else:
                d.rectangle(box, outline=(226, 223, 218), width=2)
    return img


def plate_steps(w, h):
    """客户自助排查引导 — nested steps."""
    img = gradient(w, h, [(0, (216, 213, 208)), (1, (58, 57, 55))], angle=135)
    d = ImageDraw.Draw(img)
    for i in range(5):
        m = 0.13 + i * 0.075
        x0, y0 = w * m, h * (0.18 + i * 0.058)
        x1, y1 = w * (1 - m * 0.6), h * (0.88 - i * 0.05)
        tone = (244, 242, 238) if i % 2 == 0 else (34, 33, 32)
        d.rectangle([x0, y0, x1, y1], outline=tone, width=3)
    return img


def plate_portrait(w, h):
    """关于我 — head-and-shoulders silhouette, softly side-lit."""
    img = gradient(w, h, [(0, (218, 215, 210)), (0.5, (176, 173, 167)),
                          (1, (104, 102, 98))], angle=110)
    # soft pool of light behind the figure
    img = soft_shape(img, [w * 0.12, h * 0.06, w * 0.92, h * 0.74], (238, 236, 232), min(w, h) * 0.12)
    d = ImageDraw.Draw(img)
    cx = w * 0.50
    # shoulders
    d.ellipse([cx - w * 0.40, h * 0.72, cx + w * 0.40, h * 1.30], fill=(62, 61, 59))
    # neck
    d.rectangle([cx - w * 0.085, h * 0.60, cx + w * 0.085, h * 0.80], fill=(70, 69, 67))
    # head
    hr = min(w, h) * 0.175
    cy = h * 0.40
    d.ellipse([cx - hr, cy - hr * 1.16, cx + hr, cy + hr * 1.16], fill=(74, 73, 71))
    # rim light on one side
    d.arc([cx - hr, cy - hr * 1.16, cx + hr, cy + hr * 1.16], start=250, end=20,
          fill=(232, 230, 226), width=4)
    img = img.filter(ImageFilter.GaussianBlur(1.6))
    return img


def plate_horizon(w, h, level=0.58, tint=(214, 209, 200), deep=(46, 46, 45)):
    """清晨 / 旅途 — horizon with a low disc."""
    img = gradient(w, h, [(0, (236, 234, 230)), (level, tint), (1, deep)], angle=90)
    d = ImageDraw.Draw(img)
    r = min(w, h) * 0.17
    cx, cy = w * 0.46, h * level
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(250, 249, 246))
    d.line([0, h * level, w, h * level], fill=(250, 249, 246), width=2)
    for i in range(7):
        y = h * level + h * 0.055 * (i + 1)
        d.line([w * (0.02 + i * 0.025), y, w * (0.98 - i * 0.025), y],
               fill=(196, 193, 187), width=2)
    return img


def plate_window(w, h):
    """窗边 — a lit window against a dark room."""
    img = gradient(w, h, [(0, (58, 57, 55)), (1, (34, 34, 33))], angle=90)
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = w * 0.24, h * 0.14, w * 0.76, h * 0.86
    d.rectangle([x0, y0, x1, y1], fill=(226, 223, 218))
    mx = (x0 + x1) / 2
    d.rectangle([x0 + 6, y0 + 6, mx - 4, h * 0.44], fill=(248, 247, 244))
    d.rectangle([x0 + 6, h * 0.44 + 6, mx - 4, y1 - 6], fill=(198, 195, 189))
    d.rectangle([mx + 4, y0 + 6, x1 - 6, h * 0.44], fill=(210, 207, 201))
    d.rectangle([mx + 4, h * 0.44 + 6, x1 - 6, y1 - 6], fill=(236, 234, 230))
    d.rectangle([x0, y0, x1, y1], outline=(20, 20, 19), width=6)
    d.line([mx, y0, mx, y1], fill=(20, 20, 19), width=4)
    d.line([x0, h * 0.44, x1, h * 0.44], fill=(20, 20, 19), width=4)
    return img


def plate_arcs(w, h):
    """concentric arcs on a dark ground."""
    img = gradient(w, h, [(0, (48, 47, 46)), (1, (128, 125, 120))], angle=135)
    d = ImageDraw.Draw(img)
    cx, cy = w * 0.40, h * 0.64
    for i in range(10):
        r = min(w, h) * (0.09 + i * 0.072)
        d.arc([cx - r, cy - r, cx + r, cy + r], start=196, end=364,
              fill=(240, 238, 234) if i % 3 == 0 else (170, 167, 161), width=3)
    return img


def plate_diagonals(w, h):
    """diagonal rules."""
    img = gradient(w, h, [(0, (222, 219, 214)), (1, (72, 71, 68))], angle=45)
    d = ImageDraw.Draw(img)
    for i in range(24):
        o = i * w * 0.052 - w * 0.30
        d.line([o, h, o + h * 0.92, 0],
               fill=(248, 247, 244) if i % 4 == 0 else (176, 173, 167),
               width=3 if i % 4 == 0 else 2)
    return img


def plate_ridges(w, h, seed=1):
    """layered ridges — the trip band.

    保留但已无调用：trip-01..03.jpg 随水面横幅改版停用后已从 PLATES 移除。
    日后若恢复，把三行加回 PLATES 即可。
    """
    img = gradient(w, h, [(0, (232, 230, 226)), (0.38, (176, 172, 165)),
                          (1, (62, 61, 59))], angle=90)
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    tones = [(216, 213, 208), (176, 173, 167), (132, 130, 125), (92, 91, 88), (54, 53, 52)]
    for layer in range(5):
        pts = []
        base = h * (0.40 + layer * 0.105)
        amp = h * (0.11 - layer * 0.013)
        for i in range(0, w + 1, max(w // 70, 1)):
            pts.append((i, base
                        + math.sin(i / w * math.pi * (1.6 + layer) + seed * 1.7) * amp
                        + rnd.uniform(-amp * 0.18, amp * 0.18)))
        d.polygon(pts + [(w, h), (0, h)], fill=tones[layer])
        d.line(pts, fill=(246, 244, 241), width=2)
    return img


PLATES = [
    ("design-01.jpg", plate_checklist, 1600, 1067),
    ("design-02.jpg", plate_flow, 1600, 1067),
    ("design-03.jpg", plate_grid, 1600, 1067),
    ("design-04.jpg", plate_steps, 1600, 1067),
    ("profile.jpg", plate_portrait, 1200, 1500),
    ("journal-01.jpg", lambda w, h: plate_horizon(w, h, 0.56), 1400, 1050),
    ("journal-02.jpg", lambda w, h: plate_horizon(w, h, 0.68), 1400, 1050),
    ("journal-03.jpg", plate_window, 1400, 1050),
    ("note-01.jpg", plate_arcs, 1200, 1200),
    ("note-02.jpg", plate_diagonals, 1200, 1200),
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("generating placeholder plates ->", OUT)
    for name, fn, w, h in PLATES:
        finish(fn(w, h), name)
    print("done")
