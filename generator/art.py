"""Procedural cover art. Every image is drawn by code from shapes and gradients. No photographs, no sampled artwork."""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_R = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SS = 2  # supersample factor


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vgrad(w, h, c0, c1, gamma=1.0):
    t = (np.linspace(0, 1, h) ** gamma)[:, None, None]
    a = np.array(c0, float)[None, None, :]
    b = np.array(c1, float)[None, None, :]
    arr = np.repeat(a + (b - a) * t, w, axis=1)
    return Image.fromarray(arr.astype(np.uint8), 'RGB')


def glow(base, layer_fn, radius, strength=1.0):
    """Draw on a transparent layer, blur it, composite additively-ish, then draw it sharp on top."""
    lay = Image.new('RGBA', base.size, (0, 0, 0, 0))
    layer_fn(ImageDraw.Draw(lay))
    blur = lay.filter(ImageFilter.GaussianBlur(radius))
    if strength != 1.0:
        a = blur.getchannel('A').point(lambda v: min(255, int(v * strength)))
        blur.putalpha(a)
    base.paste(blur, (0, 0), blur)
    base.paste(lay, (0, 0), lay)


def scene(key, pal, w, h, seed=1):
    W, H = w * SS, h * SS
    rnd = random.Random(seed)
    c = [rgb(x) for x in pal]
    bg, a1, a2, a3, wh = c
    img = getattr(sys_mod, 'draw_' + key)(W, H, c, rnd)
    return img.convert('RGB').resize((w, h), Image.LANCZOS)


def draw_spiral(W, H, c, rnd):
    bg, a1, a2, a3, wh = c
    img = vgrad(W, H, bg, mix(bg, a2, 0.25))
    cx, cy = W * 0.62, H * 0.44
    R = H * 0.95
    d = ImageDraw.Draw(img, 'RGBA')
    for k in range(1, 9):
        r = R * k / 8 * 0.9
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=mix(bg, a2, 0.35) + (90,), width=max(1, W // 700))

    def arms(dr):
        for arm in range(5):
            col = (a1, a2, a3, a1, a2)[arm]
            pts = []
            for i in range(0, 361):
                r = R * i / 360
                th = arm * 2 * math.pi / 5 + i / 360 * 5.2
                pts.append((cx + r * math.cos(th), cy + r * math.sin(th) * 0.92))
            for i in range(len(pts) - 1):
                wdt = max(2, int((1 - i / 360) * H * 0.028) + 2)
                dr.line([pts[i], pts[i + 1]], fill=col + (int(235 * (1 - i / 420)),), width=wdt)

    glow(img, arms, H * 0.012, 0.9)
    d = ImageDraw.Draw(img, 'RGBA')
    d.ellipse([cx - H * 0.05, cy - H * 0.05, cx + H * 0.05, cy + H * 0.05], fill=wh + (255,))
    for _ in range(90):
        x, y = rnd.random() * W, rnd.random() * H
        r = rnd.random() * H * 0.006 + 1
        d.ellipse([x - r, y - r, x + r, y + r], fill=wh + (rnd.randint(60, 160),))
    return img


def draw_moss(W, H, c, rnd):
    bg, a1, a2, a3, wh = c
    img = vgrad(W, H, mix(bg, (0, 0, 0), 0.35), mix(bg, a3, 0.25), 0.9)
    d = ImageDraw.Draw(img, 'RGBA')
    for _ in range(140):
        x, y = rnd.random() * W, rnd.random() * H * 0.55
        r = rnd.random() * H * 0.004 + 1
        d.ellipse([x - r, y - r, x + r, y + r], fill=wh + (rnd.randint(40, 140),))
    lamps = []
    layers = 6
    for L in range(layers):
        t = L / (layers - 1)
        base_y = H * (0.5 + 0.09 * L)
        ph = rnd.random() * 6
        amp = H * (0.07 - 0.006 * L)
        col = mix(mix(bg, a3, 0.55), mix(bg, (0, 0, 0), 0.5), t)
        col = mix(col, a1, 0.18 * (1 - t))
        pts = [(0, H)]
        for x in range(0, W + 8, 8):
            y = base_y + amp * math.sin(x / W * (3.2 + L * 0.6) + ph) + amp * 0.4 * math.sin(x / W * 9 + ph * 2)
            pts.append((x, y))
        pts.append((W, H))
        d.polygon(pts, fill=col + (255,))
        if L in (1, 3):
            for _ in range(3):
                x = rnd.randint(int(W * 0.08), int(W * 0.92))
                y = base_y + amp * math.sin(x / W * (3.2 + L * 0.6) + ph) + amp * 0.4 * math.sin(x / W * 9 + ph * 2)
                lamps.append((x, y - H * 0.03))

    def lights(dr):
        for x, y in lamps:
            r = H * 0.016
            dr.ellipse([x - r, y - r, x + r, y + r], fill=a2 + (255,))

    glow(img, lights, H * 0.03, 1.4)
    return img


def draw_vinyl(W, H, c, rnd):
    bg, a1, a2, a3, wh = c
    img = vgrad(W, H, mix(bg, (0, 0, 0), 0.2), mix(bg, a3, 0.3))
    d = ImageDraw.Draw(img, 'RGBA')
    cx, cy, R = W * 0.66, H * 0.5, H * 0.46
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(14, 10, 8, 255))
    gaps = np.linspace(R * 0.36, R * 0.97, 46)
    for i, r in enumerate(gaps):
        a = 40 + (i * 37 % 50)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=a2 + (a,), width=max(1, W // 1400))
    lr = R * 0.31
    d.ellipse([cx - lr, cy - lr, cx + lr, cy + lr], fill=a3 + (255,))
    d.ellipse([cx - lr * 0.62, cy - lr * 0.62, cx + lr * 0.62, cy + lr * 0.62], outline=wh + (210,), width=max(2, W // 500))
    d.ellipse([cx - R * 0.025, cy - R * 0.025, cx + R * 0.025, cy + R * 0.025], fill=bg + (255,))
    sheen = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sheen)
    for ang in (35, 215):
        th = math.radians(ang)
        sd.polygon([(cx, cy), (cx + R * math.cos(th - 0.18), cy - R * math.sin(th - 0.18)), (cx + R * math.cos(th + 0.18), cy - R * math.sin(th + 0.18))], fill=(255, 255, 255, 26))
    mask = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mask).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
    img.paste(sheen, (0, 0), Image.composite(sheen.getchannel('A'), Image.new('L', (W, H), 0), mask))
    d = ImageDraw.Draw(img, 'RGBA')
    # tonearm and soft bars on the left
    d.line([(W * 0.93, H * 0.08), (W * 0.84, H * 0.3), (W * 0.76, H * 0.42)], fill=wh + (220,), width=max(3, W // 300))
    for i in range(5):
        y = H * (0.2 + 0.1 * i)
        d.rounded_rectangle([W * 0.06, y, W * (0.12 + 0.05 * ((i * 3) % 5)), y + H * 0.03], radius=H * 0.015, fill=mix(a1, a2, i / 5) + (200,))
    return img


def draw_sun(W, H, c, rnd):
    bg, a1, a2, a3, wh = c
    img = vgrad(W, H, bg, mix(bg, a1, 0.55), 1.4)
    d = ImageDraw.Draw(img, 'RGBA')
    cx, cy, R = W * 0.62, H * 0.5, H * 0.34
    sun = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    sd.ellipse([cx - R, cy - R, cx + R, cy + R], fill=a2 + (255,))
    # stripes cut into the sun: wider toward the bottom
    y = cy - R * 0.1
    gap = R * 0.05
    while y < cy + R:
        sd.rectangle([cx - R, y, cx + R, y + gap], fill=(0, 0, 0, 0))
        y += gap * 2.4
        gap *= 1.28
    # cut by erasing: composite with alpha
    arr = np.array(sun)
    sun_img = Image.fromarray(arr, 'RGBA')
    sg = vgrad(W, H, a2, a1)
    sun_fill = Image.new('RGBA', (W, H))
    sun_fill.paste(sg, (0, 0))
    sun_fill.putalpha(Image.fromarray(arr[:, :, 3]))
    img.paste(sun_fill, (0, 0), sun_fill)
    d = ImageDraw.Draw(img, 'RGBA')
    # shutters on the left
    for i in range(7):
        x = W * (0.06 + 0.045 * i)
        d.polygon([(x, H * 0.12), (x + W * 0.032, H * 0.1), (x + W * 0.032, H * 0.62), (x, H * 0.64)], fill=wh + (60 + i * 16,))
    # sea
    for k in range(9):
        y0 = H * (0.66 + 0.04 * k)
        pts = [(x, y0 + math.sin(x / W * (14 + k) + k) * H * 0.008) for x in range(0, W + 6, 6)]
        d.line(pts, fill=mix(a3, wh, k / 9) + (200 - k * 12,), width=max(2, int(H * (0.004 + 0.0012 * k))))
    return img


def draw_neon(W, H, c, rnd):
    bg, a1, a2, a3, wh = c
    img = vgrad(W, H, mix(bg, (0, 0, 0), 0.3), mix(bg, a3, 0.5), 1.6)
    hy = H * 0.58
    cx = W * 0.5
    d = ImageDraw.Draw(img, 'RGBA')
    # skyline bars
    for i in range(22):
        x = W * i / 22
        bh = H * (0.08 + 0.2 * rnd.random())
        d.rectangle([x, hy - bh, x + W / 22 * 0.8, hy], fill=mix(bg, (0, 0, 0), 0.35) + (255,))

    def sunset(dr):
        R = H * 0.26
        dr.pieslice([cx - R, hy - R, cx + R, hy + R], 180, 360, fill=a1 + (255,))

    glow(img, sunset, H * 0.04, 1.0)
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle([0, hy, W, H], fill=mix(bg, (0, 0, 0), 0.5) + (255,))

    def grid(dr):
        for i in range(-16, 17):
            dr.line([(cx + i * W * 0.012, hy), (cx + i * W * 0.14, H)], fill=a2 + (255,), width=max(2, W // 640))
        for k in range(1, 12):
            y = hy + (H - hy) * (k / 12) ** 2
            dr.line([(0, y), (W, y)], fill=a3 + (255,), width=max(2, W // 640))

    glow(img, grid, H * 0.006, 1.2)
    d = ImageDraw.Draw(img, 'RGBA')
    d.line([(0, hy), (W, hy)], fill=wh + (255,), width=max(2, W // 500))
    return img


def draw_memphis(W, H, c, rnd):
    bg, a1, a2, a3, wh = c
    img = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(img, 'RGBA')
    cols = [a1, a2, a3, wh]
    # big striped circle
    cx, cy, R = W * 0.7, H * 0.45, H * 0.3
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=a3 + (255,))
    for i in range(-8, 9):
        x = cx + i * R * 0.22
        d.polygon([(x - R * 0.06, cy - R), (x + R * 0.06, cy - R), (x + R * 0.06 + R * 0.5, cy + R), (x - R * 0.06 + R * 0.5, cy + R)], fill=bg + (255,))
    mask = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mask).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
    base = vgrad(W, H, bg, bg)
    ring = Image.new('RGB', (W, H), bg)
    ring.paste(img, (0, 0), mask)
    img = Image.composite(ring, base, mask)
    d = ImageDraw.Draw(img, 'RGBA')
    shapes = 0
    spots = []
    tries = 0
    while shapes < 46 and tries < 6000:
        tries += 1
        x, y = rnd.random() * W, rnd.random() * H
        if y > H * 0.62 or any(math.hypot(x - sx, y - sy) < min(W, H) * 0.075 for sx, sy in spots) or math.hypot(x - cx, y - cy) < R * 1.05:
            continue
        spots.append((x, y))
        shapes += 1
        col = rnd.choice(cols)
        s = H * (0.025 + 0.03 * rnd.random())
        kind = rnd.choice(['tri', 'circ', 'zig', 'dots', 'cross'])
        if kind == 'tri':
            a = rnd.random() * 6.28
            d.polygon([(x + s * math.cos(a + k * 2.094), y + s * math.sin(a + k * 2.094)) for k in range(3)], fill=col + (255,))
        elif kind == 'circ':
            d.ellipse([x - s * 0.7, y - s * 0.7, x + s * 0.7, y + s * 0.7], outline=col + (255,), width=max(3, int(s * 0.25)))
        elif kind == 'zig':
            pts = [(x + i * s * 0.6, y + (s * 0.5 if i % 2 else -s * 0.5)) for i in range(-3, 4)]
            d.line(pts, fill=col + (255,), width=max(3, int(s * 0.22)), joint='curve')
        elif kind == 'dots':
            for i in range(3):
                for j in range(3):
                    r = s * 0.1
                    d.ellipse([x + i * s * 0.5 - r, y + j * s * 0.5 - r, x + i * s * 0.5 + r, y + j * s * 0.5 + r], fill=col + (255,))
        else:
            d.line([(x - s * 0.6, y), (x + s * 0.6, y)], fill=col + (255,), width=max(3, int(s * 0.22)))
            d.line([(x, y - s * 0.6), (x, y + s * 0.6)], fill=col + (255,), width=max(3, int(s * 0.22)))
    return img


def draw_starburst(W, H, c, rnd):
    bg, a1, a2, a3, wh = c
    img = vgrad(W, H, bg, mix(bg, a3, 0.35))
    cx, cy = W * 0.5, H * 0.46
    d = ImageDraw.Draw(img, 'RGBA')
    n = 28
    L = math.hypot(W, H)
    for i in range(n):
        if i % 2:
            continue
        a0 = 2 * math.pi * i / n
        a1_ = 2 * math.pi * (i + 1) / n
        d.polygon([(cx, cy), (cx + L * math.cos(a0), cy + L * math.sin(a0)), (cx + L * math.cos(a1_), cy + L * math.sin(a1_))], fill=mix(a1, bg, 0.7) + (120,))

    def burst(dr):
        for k, (r, col) in enumerate(((H * 0.36, a2), (H * 0.27, a1), (H * 0.18, wh))):
            pts = []
            for j in range(24):
                rr = r if j % 2 == 0 else r * 0.72
                th = 2 * math.pi * j / 24 + k * 0.1
                pts.append((cx + rr * math.cos(th), cy + rr * math.sin(th)))
            dr.polygon(pts, fill=col + (255,))

    glow(img, burst, H * 0.01, 0.8)
    d = ImageDraw.Draw(img, 'RGBA')
    for _ in range(26):
        x, y = rnd.random() * W, rnd.random() * H
        if math.hypot(x - cx, y - cy) < H * 0.42:
            continue
        r = H * (0.012 + 0.012 * rnd.random())
        d.polygon([(x + (r if j % 2 == 0 else r * 0.4) * math.cos(math.pi * j / 4), y + (r if j % 2 == 0 else r * 0.4) * math.sin(math.pi * j / 4)) for j in range(8)], fill=rnd.choice([wh, a1, a2]) + (230,))
    return img


def draw_keys(W, H, c, rnd):
    bg, a1, a2, a3, wh = c
    img = vgrad(W, H, mix(bg, (0, 0, 0), 0.25), bg)
    d = ImageDraw.Draw(img, 'RGBA')
    floor = H * 0.56
    # amber floor grid
    for k in range(0, 9):
        y = floor + (H - floor) * (k / 8)
        d.line([(0, y), (W, y)], fill=a1 + (110,), width=max(1, W // 900))
    for i in range(0, 33):
        d.line([(W * i / 32, floor), (W * i / 32, H)], fill=a1 + (60,), width=max(1, W // 900))
    # four ticks
    for i in range(4):
        x = W * (0.2 + 0.2 * i)
        d.rectangle([x - W * 0.004, floor - H * 0.03, x + W * 0.004, floor + H * 0.01], fill=a1 + (255,))
    # stacked piano blocks above the ticks
    heights = [3, 3, 2, 3]
    for i, hn in enumerate(heights):
        x = W * (0.2 + 0.2 * i)
        bw = W * 0.12
        for k in range(hn):
            y1 = floor - H * 0.05 - k * H * 0.095
            fill = wh if (k + i) % 2 == 0 else mix(bg, (0, 0, 0), 0.6)
            edge = a1 if (k + i) % 2 else bg
            d.rounded_rectangle([x - bw / 2, y1 - H * 0.085, x + bw / 2, y1], radius=H * 0.008, fill=fill + (255,), outline=edge + (255,), width=max(2, W // 700))
            if (k + i) % 2 == 0:
                for j in (-1, 1):
                    d.rectangle([x + j * bw * 0.18 - bw * 0.04, y1 - H * 0.085, x + j * bw * 0.18 + bw * 0.04, y1 - H * 0.04], fill=mix(bg, (0, 0, 0), 0.4) + (255,))
    # thin bass line
    pts = [(W * (0.04 + 0.92 * t / 60), floor + H * 0.045 + math.sin(t / 60 * 12.6) * H * 0.012 + (H * 0.02 if (t // 8) % 2 else 0)) for t in range(61)]

    def bass(dr):
        dr.line(pts, fill=a2 + (255,), width=max(3, W // 350), joint='curve')

    glow(img, bass, H * 0.006, 1.0)
    return img


def draw_dawn(W, H, c, rnd):
    bg, a1, a2, a3, wh = c
    img = vgrad(W, H, bg, mix(a1, a3, 0.25), 1.2)
    d = ImageDraw.Draw(img, 'RGBA')
    cx, hy, R = W * 0.58, H * 0.62, H * 0.22

    def sun(dr):
        dr.ellipse([cx - R, hy - R, cx + R, hy + R], fill=mix(a1, wh, 0.3) + (255,))

    glow(img, sun, H * 0.05, 1.3)
    d = ImageDraw.Draw(img, 'RGBA')
    # rays
    for i in range(18):
        th = math.pi + math.pi * i / 17
        d.line([(cx + R * 1.1 * math.cos(th), hy + R * 1.1 * math.sin(th)), (cx + H * 1.2 * math.cos(th), hy + H * 1.2 * math.sin(th))], fill=a1 + (22,), width=max(2, W // 300))
    for L in range(5):
        t = L / 4
        base_y = H * (0.6 + 0.07 * L)
        col = mix(mix(bg, a2, 0.25), bg, t)
        col = mix(col, (0, 0, 0), 0.15 + 0.5 * t)
        ph = rnd.random() * 6
        pts = [(0, H)]
        for x in range(0, W + 8, 8):
            y = base_y - H * 0.08 * abs(math.sin(x / W * (2.1 + L) + ph)) - H * 0.03 * math.sin(x / W * 11 + ph)
            pts.append((x, y))
        pts.append((W, H))
        d.polygon(pts, fill=col + (255,))
    for _ in range(6):
        x, y = rnd.random() * W, rnd.random() * H * 0.35
        d.ellipse([x - W * 0.09, y - H * 0.012, x + W * 0.09, y + H * 0.012], fill=wh + (40,))
    return img


def _fit(fnt_path, text, size, maxw):
    while size > 10:
        f = ImageFont.truetype(fnt_path, size)
        if f.getlength(text) <= maxw:
            return f
        size -= 2
    return ImageFont.truetype(fnt_path, 10)


def overlay(img, title, sub, foot, pal, on_picture=None):
    """Title band along the bottom. Text is drawn on a dark translucent gradient for contrast."""
    w, h = img.size
    img = img.convert('RGBA')
    band_h = int(h * (0.34 if h <= w else 0.26))
    grad = Image.new('RGBA', (w, band_h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(band_h):
        a = int(215 * (y / band_h) ** 1.2)
        gd.line([(0, y), (w, y)], fill=(6, 6, 10, a))
    img.alpha_composite(grad, (0, h - band_h))
    d = ImageDraw.Draw(img)
    m = int(w * 0.05)
    f1 = _fit(FONT_B, title, int(h * 0.1 if h <= w else w * 0.085), w - 2 * m)
    f2 = _fit(FONT_R, sub, int(h * 0.036 if h <= w else w * 0.034), w - 2 * m)
    f3 = _fit(FONT_R, foot, int(h * 0.026 if h <= w else w * 0.026), w - 2 * m)
    y = h - m * 0.7
    d.text((m, y), foot, font=f3, fill=(235, 235, 235, 255), anchor='ls')
    y -= f3.size * 1.5
    d.text((m, y), sub, font=f2, fill=(255, 255, 255, 255), anchor='ls')
    y -= f2.size * 1.3
    d.text((m, y), title, font=f1, fill=(255, 255, 255, 255), anchor='ls')
    if on_picture:
        f4 = ImageFont.truetype(FONT_B, int(h * 0.045))
        tw = f4.getlength(on_picture)
        px, py = (w - tw) / 2, h * 0.07
        d.rounded_rectangle([px - 22, py - 14, px + tw + 22, py + f4.size + 14], radius=10, fill=(0, 0, 0, 175))
        d.text((px, py), on_picture, font=f4, fill=(255, 255, 255, 255))
    return img.convert('RGB')


def mark_svg(pal):
    bg, a1, a2, a3, wh = pal
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Pack mark: a circle above four ticks">'
            '<rect width="64" height="64" rx="10" fill="%s"/><circle cx="32" cy="26" r="13" fill="%s"/>'
            '<rect x="12" y="46" width="6" height="8" fill="%s"/><rect x="24" y="46" width="6" height="8" fill="%s"/>'
            '<rect x="36" y="46" width="6" height="8" fill="%s"/><rect x="48" y="46" width="6" height="8" fill="%s"/></svg>\n') % (bg, a2, a1, a1, a1, a3)


import sys as _s
sys_mod = _s.modules[__name__]
