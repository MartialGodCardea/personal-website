# -*- coding: utf-8 -*-
"""Generate a 1920x1080 HD water photograph-style background.

Produces site/img/water-bg.jpg: deep blue ocean gradient with soft caustic
light ripples, subtle wave highlights and film grain. Designed to sit under
the canvas procedural water band (soft-light blended) so the two combine
into a rich, realistic water surface.
"""
import math
import os
import random

from PIL import Image, ImageFilter, ImageDraw

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "site", "img")
OUT_PATH = os.path.join(OUT_DIR, "water-bg.jpg")

W, H = 1920, 1080


def gradient(w, h, stops, angle=82):
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


def caustics(w, h, seed=42):
    """Soft sin-composed caustic light streaks, horizontal water perspective."""
    rng = random.Random(seed)
    img = Image.new("F", (w, h), 0.0)
    px = img.load()
    layers = [
        (3.0, 9.0, 0.50, 1.70, rng.random() * 6.28),
        (-2.2, 14.0, 0.34, 2.14, rng.random() * 6.28),
        (7.5, 23.0, 0.20, 2.90, rng.random() * 6.28),
        (-5.2, 31.0, 0.12, 3.70, rng.random() * 6.28),
        (1.6, 6.2, 0.28, 1.30, rng.random() * 6.28),
    ]
    for y in range(h):
        v = y / (h - 1)
        depth_fade = 1.0 - math.pow(v, 0.9) * 0.72
        for x in range(w):
            u = x / (w - 1)
            c = 0.0
            for fx, fy, amp, scale, ph in layers:
                t = (u * fx + v * fy) * math.pi * scale + ph
                c += (math.sin(t) * 0.5 + 0.5) * amp
            # soft threshold to mimic focused caustic streaks
            c = max(0.0, c - 0.45)
            c = math.pow(c, 2.2) * 2.6
            px[x, y] = c * depth_fade
    return img


def highlights(w, h, seed=11):
    """Soft blurred bright patches mimicking specular reflection."""
    rng = random.Random(seed)
    base = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(base)
    for _ in range(140):
        cx = rng.randrange(w)
        cy = rng.randrange(int(h * 0.55))
        r = rng.randint(6, 60)
        a = rng.random() * 0.45 + 0.08
        a *= 1.0 - (cy / h) * 0.6
        fill_val = max(0, min(255, int(round(a * 255))))
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill_val)
    base = base.filter(ImageFilter.GaussianBlur(22))
    return base


def grain(img, sigma=5.0, amount=0.06):
    noise = Image.effect_noise(img.size, sigma).convert("L")
    return Image.blend(img, Image.merge("RGB", (noise, noise, noise)), amount)


def vignette(img, amount=0.38, spread=0.14):
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    cx, cy = w / 2, h * 0.42
    r = max(w, h) * (1.0 + spread)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=max(2, int(min(w, h) * 0.22))))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.composite(img, dark,
                           Image.blend(mask, Image.new("L", (w, h), 255), 1 - amount))


def main():
    print("building water-bg.jpg %dx%d ..." % (W, H))
    # Ocean water depth gradient: shallow turquoise top -> deep indigo bottom
    base = gradient(W, H, [
        (0.00, (38, 96, 132)),
        (0.18, (22, 74, 118)),
        (0.42, (14, 54, 94)),
        (0.72, (9, 36, 72)),
        (1.00, (6, 22, 44)),
    ])

    ca = caustics(W, H)
    hi = highlights(W, H)

    out = base.copy()
    op = out.load()
    cp = ca.load()
    hp = hi.load()
    bp = base.load()

    for y in range(H):
        for x in range(W):
            r, g, b = bp[x, y]
            c = cp[x, y]
            # L-mode 0-255 -> floating 0-1
            s = hp[x, y] / 255.0
            # warm caustics lean green/cyan (underwater sun streaks)
            nr = min(255, int(r + c * 90 + s * 120))
            ng = min(255, int(g + c * 130 + s * 130))
            nb = min(255, int(b + c * 140 + s * 115))
            op[x, y] = (nr, ng, nb)

    out = out.filter(ImageFilter.GaussianBlur(0.9))
    out = grain(out, sigma=4.5, amount=0.045)
    out = vignette(out, amount=0.30, spread=0.12)

    os.makedirs(OUT_DIR, exist_ok=True)
    out.save(OUT_PATH, format="JPEG", quality=93, optimize=True, progressive=True)
    size_kb = os.path.getsize(OUT_PATH) / 1024
    print("  wrote", os.path.relpath(OUT_PATH, os.path.dirname(OUT_DIR)),
          "(%.1f KB)" % size_kb)


if __name__ == "__main__":
    main()
