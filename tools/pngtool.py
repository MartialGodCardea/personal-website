# -*- coding: utf-8 -*-
"""Minimal PNG read/write + pixel probes + crop, stdlib only."""
import struct
import sys
import zlib


def load_png(path):
    data = open(path, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a png"
    pos, idat = 8, b""
    w = h = depth = ctype = None
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", chunk[:10])
        elif typ == b"IDAT":
            idat += chunk
        elif typ == b"IEND":
            break
        pos += 12 + ln
    raw = zlib.decompress(idat)
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[ctype]
    assert depth == 8
    stride = w * channels
    out = bytearray(w * h * channels)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        ft = raw[p]; p += 1
        line = bytearray(raw[p:p + stride]); p += stride
        if ft == 1:
            for i in range(channels, stride):
                line[i] = (line[i] + line[i - channels]) & 0xFF
        elif ft == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif ft == 3:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif ft == 4:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                b = prev[i]
                c = prev[i - channels] if i >= channels else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 0xFF
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return w, h, channels, out


def save_png(path, w, h, rgb):
    """rgb: bytearray of w*h*3"""
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += rgb[y * w * 3:(y + 1) * w * 3]

    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data
                + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))

    out = b"\x89PNG\r\n\x1a\n"
    out += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    out += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    out += chunk(b"IEND", b"")
    open(path, "wb").write(out)


def to_rgb(img):
    w, h, ch, buf = img
    if ch == 3:
        return w, h, bytearray(buf)
    out = bytearray(w * h * 3)
    for i in range(w * h):
        out[i * 3:i * 3 + 3] = buf[i * ch:i * ch + 3]
    return w, h, out


def crop(path_in, path_out, x0, y0, x1, y1, scale=1):
    w, h, rgb = to_rgb(load_png(path_in))
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w, x1), min(h, y1)
    cw, chh = x1 - x0, y1 - y0
    ow, oh = cw * scale, chh * scale
    out = bytearray(ow * oh * 3)
    for y in range(oh):
        sy = y0 + y // scale
        for x in range(ow):
            sx = x0 + x // scale
            i = (sy * w + sx) * 3
            j = (y * ow + x) * 3
            out[j:j + 3] = rgb[i:i + 3]
    save_png(path_out, ow, oh, out)
    print("cropped ->", path_out, ow, "x", oh)


def darkest_in(img, x0, y0, x1, y1):
    w, h, ch, buf = img
    best = (999, 0, 0)
    for y in range(y0, min(y1, h)):
        for x in range(x0, min(x1, w)):
            i = (y * w + x) * ch
            v = (buf[i] + buf[i + 1] + buf[i + 2]) // 3
            if v < best[0]:
                best = (v, x, y)
    return best


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "probe":
        img = load_png(sys.argv[2])
        print("size", img[0], "x", img[1])
        for spec in sys.argv[3:]:
            x0, y0, x1, y1 = [int(v) for v in spec.split(",")]
            v, x, y = darkest_in(img, x0, y0, x1, y1)
            print("  %-22s darkest=%3d at (%d,%d)" % (spec, v, x, y))
    elif cmd == "crop":
        crop(sys.argv[2], sys.argv[3], *[int(v) for v in sys.argv[4:8]],
             scale=int(sys.argv[8]) if len(sys.argv) > 8 else 1)
