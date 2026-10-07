"""Signature face effects layered on top of artist renders. Positions assume the aligned crop."""

from __future__ import annotations

import random

import cv2
import numpy as np

from app.artists import LUMA, Artist, _c, _f, _paint, _ref, _u, subject_mask
from app.framing import face_mask

EYES = ((0.40, 0.44), (0.60, 0.44))
CHEEKS = ((0.355, 0.575), (0.645, 0.575))
NOSE = (0.5, 0.56)
MOUTH = (0.5, 0.66)
BROW_Y = 0.405
AA = cv2.LINE_AA
SHIFT = 4


def _p(x, y):
    return int(round(x * 16)), int(round(y * 16))


def _draw(h, w, draw, blur=0.0):
    canvas = np.zeros((h, w), np.uint8)
    draw(canvas)
    mask = canvas.astype(np.float32) / 255.0
    return cv2.GaussianBlur(mask, (0, 0), blur) if blur else mask


def _disk(h, w, cx, cy, rx, ry=None, feather=1.0):
    ys, xs = np.ogrid[:h, :w]
    ry = rx if ry is None else ry
    d = np.sqrt(((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2)
    return np.clip((1.0 - d) * min(rx, ry) / max(feather, 1e-3), 0.0, 1.0).astype(np.float32)


def _lum(x):
    return (x * LUMA).sum(axis=-1)


def _grid(h, w):
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    return xs, ys


def _remap(x, mx, my):
    return cv2.remap(x, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)


def _noise(rng, h, w, cells, sigma=0.0):
    field = cv2.resize(rng.normal(0, 1, (cells, cells)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
    return cv2.GaussianBlur(field, (0, 0), sigma) if sigma else field


# ---------- warps ----------

def melt(x, img, amount, rng):
    """Dalí: everything below the eyes slides down in drips."""
    h, w = x.shape[:2]
    xs, ys = _grid(h, w)
    col = np.arange(w, dtype=np.float32)
    profile = np.full(w, 0.3, np.float32)
    for _ in range(8):
        c, width, strength = rng.uniform(0.28, 0.72) * w, rng.uniform(0.02, 0.06) * w, rng.uniform(0.4, 1.1)
        profile += strength * np.exp(-(((col - c) / width) ** 2))
    profile *= np.exp(-(((col - w / 2) / (0.26 * w)) ** 4))
    t = np.clip((ys - 0.49 * h) / (0.5 * h), 0, 1)
    ramp = t * t * (3 - 2 * t)
    dy = amount * 0.17 * h * profile[None, :] * ramp
    wobble = np.sin(ys / (0.028 * h) + rng.uniform(0, 6)) * 0.006 * w * ramp * amount
    melted = _remap(x, xs - wobble, ys - dy)
    sheen = np.clip(np.gradient(dy, axis=1) * 0.9, 0, 1) * ramp
    return _paint(melted, sheen * 0.35, (1.0, 1.0, 1.0))


def cubist(x, img, amount, rng):
    """Picasso: one half of the face is seen from a second viewpoint."""
    h, w = x.shape[:2]
    ref = _ref(img)
    xs, ys = _grid(h, w)
    side = rng.choice([-1, 1])
    cx = w * (0.5 + rng.uniform(-0.02, 0.02))
    scale = 1 + 0.1 * amount
    dx = side * amount * 0.025 * w
    dy = rng.choice([-1, 1]) * amount * 0.05 * h
    moved = _remap(x, (xs - w / 2 - dx) / scale + w / 2, (ys - h / 2 - dy) / scale + h / 2)
    tint = _c(rng.choice(["#d9a35b", "#7f9cb5", "#c46b4f"]))
    moved = moved * 0.8 + tint * 0.2
    zig = (np.abs(((ys / (0.07 * h)) % 2) - 1) - 0.5) * 0.03 * w
    seam = cx + zig
    half = np.clip((xs - seam) * side / (1.2 * ref), 0, 1)
    region = np.clip(face_mask(h, w, 1.3) * 1.6, 0, 1)
    m = half * region
    out = _paint(x, m, 0) + moved * m[..., None]
    edge = np.clip(1 - np.abs(xs - seam) / (2.2 * ref), 0, 1) * region
    return _paint(out, edge * 0.9, _c("#2a1d14"))


def bulge(x, img, amount, rng):
    """Vasarely: the face swells into an op-art sphere."""
    h, w = x.shape[:2]
    xs, ys = _grid(h, w)
    cx, cy, radius = w / 2, h * 0.52, 0.44 * w
    dx, dy = xs - cx, ys - cy
    r = np.sqrt(dx * dx + dy * dy) + 1e-3
    power = 1 + 0.6 * amount
    inside = r < radius
    src = np.where(inside, radius * (r / radius) ** power, r)
    out = _remap(x, cx + dx * src / r, cy + dy * src / r)
    t = np.clip(r / radius, 0, 1)
    shade = np.where(inside, 1 - 0.22 * amount * t ** 3, 1.0)[..., None]
    out = out * shade
    gloss = _disk(h, w, cx - 0.14 * w, cy - 0.16 * h, 0.12 * w, feather=0.12 * w)
    return _paint(out, gloss * 0.22, (1.0, 1.0, 1.0))


def twist(x, img, amount, rng):
    """Van Gogh: the face turns with the swirling sky, painted yellow over blue."""
    h, w = x.shape[:2]
    xs, ys = _grid(h, w)
    cx, cy = w / 2, h * 0.52
    dx, dy = xs - cx, ys - cy
    r = np.sqrt(dx * dx + dy * dy)
    angle = rng.choice([-1, 1]) * amount * 0.55 * np.exp(-((r / (0.26 * w)) ** 2))
    c, s = np.cos(angle), np.sin(angle)
    out = _remap(x, cx + dx * c - dy * s, cy + dx * s + dy * c)
    m = face_mask(h, w, 1.05)
    lum = _lum(out)
    out = _paint(out, np.clip(lum - 0.55, 0, 1) * m * 0.9 * amount, _c("#f5c936"))
    return _paint(out, np.clip(0.45 - lum, 0, 1) * m * 0.9 * amount, _c("#2c5bb8"))


def ripples(x, img, amount, rng):
    """Hockney: wavy pool light refracts across the face."""
    h, w = x.shape[:2]
    ref = _ref(img)
    xs, ys = _grid(h, w)
    a = _noise(rng, h, w, 6) * 2.2
    b = _noise(rng, h, w, 9) * 1.6
    wobble = 0.006 * w * amount
    out = _remap(x, xs + np.sin(ys / (0.035 * h) + a) * wobble, ys + np.cos(xs / (0.04 * w) + b) * wobble)
    caustic = (1 - np.abs(np.sin(xs / (0.05 * w) + a * 2) * np.sin(ys / (0.045 * h) + b * 2))) ** 10
    caustic = cv2.GaussianBlur(caustic.astype(np.float32), (0, 0), 0.8 * ref)
    region = np.clip(subject_mask(img) * 0.6 + face_mask(h, w, 1.1), 0, 1)
    return 1 - (1 - out) * (1 - caustic[..., None] * region[..., None] * 0.5 * amount * _c("#d6fbff"))


# ---------- paint over ----------

def spots(x, img, amount, rng):
    """Hirst: the face is rebuilt from colored spots."""
    h, w = x.shape[:2]
    spacing = w * 0.024 * (0.75 + 0.35 * amount)
    region = face_mask(h, w, 1.08)
    colors = cv2.GaussianBlur(x, (0, 0), spacing * 0.45)
    hsv = cv2.cvtColor(_u(colors), cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * 1.5 + 20, 0, 255)
    colors = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    canvas = _u(np.broadcast_to(_c("#f6f1e7"), x.shape)).copy()
    radius = int(spacing * 0.4 * 16)
    row = 0
    y = h * 0.12
    while y < h * 0.92:
        offset = (spacing / 2) if row % 2 else 0
        xx = w * 0.2 + offset
        while xx < w * 0.8:
            if region[int(y), int(xx)] > 0.3:
                color = colors[int(y), int(xx)].tolist()
                cv2.circle(canvas, _p(xx, y), radius, color, -1, AA, SHIFT)
            xx += spacing
        y += spacing * 0.87
        row += 1
    m = np.clip(region * 1.4, 0, 1)
    return _paint(x, m, 0) + _f(canvas) * m[..., None]


def bands(x, img, amount, rng):
    """Rothko: the face dissolves into glowing horizontal color fields."""
    h, w = x.shape[:2]
    ref = _ref(img)
    smear = cv2.blur(x, (int(0.24 * w) | 1, 3))
    smear = cv2.GaussianBlur(smear, (0, 0), 4 * ref)
    detail = _lum(x) - _lum(cv2.GaussianBlur(x, (0, 0), 6 * ref))
    field = np.clip(smear + detail[..., None] * 0.9, 0, 1)
    m = face_mask(h, w, 1.15) * min(1.0, 0.55 + 0.3 * amount)
    glow = cv2.GaussianBlur(field, (0, 0), 14 * ref)
    field = 1 - (1 - field) * (1 - glow * 0.25)
    return _paint(x, m, 0) + field * m[..., None]


def drips(x, img, amount, rng):
    """Pollock: paint is flung right across the face."""
    h, w = x.shape[:2]
    ref = _ref(img)
    canvas = _u(x)
    palette = ["#111111", "#f4efe2", "#c9a227", "#8c2f1b", "#3f5a7a"]
    for _ in range(int(6 + 8 * amount)):
        color = (_c(rng.choice(palette)) * 255).tolist()
        px, py = rng.normal(w / 2, 0.16 * w), rng.normal(h * 0.5, 0.16 * h)
        heading = rng.uniform(0, 2 * np.pi)
        points = []
        for _ in range(int(rng.integers(30, 70))):
            heading += rng.normal(0, 0.35)
            px += np.cos(heading) * 0.012 * w
            py += np.sin(heading) * 0.012 * h
            points.append(_p(px, py))
        thickness = max(1, int(rng.uniform(0.8, 3.2) * ref))
        cv2.polylines(canvas, [np.array(points, np.int32)], False, color, thickness, AA, SHIFT)
        for _ in range(int(rng.integers(2, 6))):
            sx, sy = points[int(rng.integers(0, len(points)))]
            cv2.circle(canvas, (sx, sy), int(rng.uniform(1.5, 5) * ref * 16), color, -1, AA, SHIFT)
    return _f(canvas)


def poster_ink(x, img, amount, rng):
    """Mucha: flat poster tones with sepia ink linework on the face."""
    h, w = x.shape[:2]
    ref = _ref(img)
    flat = x.copy()
    for _ in range(3):
        flat = cv2.bilateralFilter(flat, max(5, int(9 * ref) | 1), 0.12, 9 * ref)
    flat = np.round(flat * 6) / 6
    gray = cv2.medianBlur(cv2.cvtColor(_u(x), cv2.COLOR_BGR2GRAY), 5)
    block = max(3, int(13 * ref) | 1)
    lines = (cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block, 6) == 0)
    lines = cv2.GaussianBlur(lines.astype(np.float32), (0, 0), 0.7)
    m = face_mask(h, w, 1.1)
    out = _paint(x, m * min(1.0, 0.5 + 0.4 * amount), 0) + flat * (m * min(1.0, 0.5 + 0.4 * amount))[..., None]
    return _paint(out, lines * m * 0.75, _c("#4a2b1c"))


def light_split(x, img, amount, rng):
    """Hopper: a hard slab of window light cuts across a posterized face."""
    h, w = x.shape[:2]
    ref = _ref(img)
    xs, ys = _grid(h, w)
    tilt = rng.uniform(0.5, 1.1) * rng.choice([-1, 1])
    line = (xs - w / 2) * tilt + (ys - h / 2) + rng.uniform(-0.04, 0.04) * h
    lit = np.clip(-line / (2.5 * ref), 0, 1)
    m = face_mask(h, w, 1.1)
    poster = np.round(cv2.GaussianBlur(x, (0, 0), 1.2 * ref) * 4) / 4
    out = _paint(x, m * 0.7, 0) + poster * (m * 0.7)[..., None]
    warm = 1 - (1 - out) * (1 - _c("#ffd27a") * 0.45 * amount)
    cool = out * (1 - (1 - _c("#4d6f9c")) * 0.45 * amount)
    shaped = warm * lit[..., None] + cool * (1 - lit[..., None])
    return _paint(out, np.clip(m * 1.3, 0, 1), 0) + shaped * np.clip(m * 1.3, 0, 1)[..., None]


def cel_blush(x, img, amount, rng):
    """Murakami: flat anime cel shading, hatched blush, and sparkling eyes."""
    h, w = x.shape[:2]
    ref = _ref(img)
    m = face_mask(h, w, 1.05)
    smooth = cv2.bilateralFilter(x, max(5, int(11 * ref) | 1), 0.15, 11 * ref)
    lum = _lum(smooth)
    cel = smooth / (lum[..., None] + 1e-3) * (np.round(lum * 3) / 3)[..., None]
    out = _paint(x, m * 0.75, 0) + np.clip(cel, 0, 1) * (m * 0.75)[..., None]
    for cx, cy in CHEEKS:
        out = _paint(out, _disk(h, w, cx * w, cy * h, 0.06 * w, 0.035 * h, 0.03 * w) * 0.6 * min(1, amount), _c("#ff7eb6"))

        def hatch(canvas, cx=cx, cy=cy):
            for k in (-1, 0, 1):
                x0 = cx * w + k * 0.018 * w
                cv2.line(canvas, _p(x0 - 0.008 * w, cy * h + 0.012 * h), _p(x0 + 0.008 * w, cy * h - 0.012 * h), 255, max(1, int(1.6 * ref)), AA, SHIFT)

        out = _paint(out, _draw(h, w, hatch) * 0.85, (1.0, 1.0, 1.0))
    size = 0.02 * w * (0.7 + 0.4 * amount)

    def stars(canvas):
        for ex, ey in EYES:
            sx, sy = ex * w + 0.022 * w, ey * h - 0.03 * h
            points = []
            for i in range(8):
                r = size if i % 2 == 0 else size * 0.28
                a = i * np.pi / 4
                points.append(_p(sx + np.cos(a) * r, sy + np.sin(a) * r))
            cv2.fillPoly(canvas, [np.array(points, np.int32)], 255, AA, SHIFT)

    star = _draw(h, w, stars)
    out = _paint(out, cv2.GaussianBlur(star, (0, 0), 2.5 * ref) * 0.8, _c("#ff4fa8"))
    return _paint(out, star, (1.0, 1.0, 1.0))


def unibrow(x, img, amount, rng):
    """Kahlo: smooth painted skin, rosy cheeks, and the famous joined brow."""
    h, w = x.shape[:2]
    ref = _ref(img)
    m = face_mask(h, w, 1.0)
    painted = x.copy()
    for _ in range(3):
        painted = cv2.bilateralFilter(painted, max(5, int(9 * ref) | 1), 0.1, 9 * ref)
    out = _paint(x, m * 0.8, 0) + painted * (m * 0.8)[..., None]
    for cx, cy in CHEEKS:
        out = _paint(out, _disk(h, w, cx * w, cy * h, 0.055 * w, feather=0.04 * w) * 0.4, _c("#d9485f"))

    def brow(canvas):
        xs = np.linspace(EYES[0][0] - 0.07, EYES[1][0] + 0.07, 24)
        arch = -0.012 * np.cos((xs - 0.5) / 0.17 * np.pi / 2) + 0.004
        points = [_p(px * w, (BROW_Y + a) * h) for px, a in zip(xs, arch)]
        cv2.polylines(canvas, [np.array(points, np.int32)], False, 255, max(2, int(0.012 * h * amount)), AA, SHIFT)

    stroke = _draw(h, w, brow, 1.2 * ref)
    return out * (1 - stroke[..., None] * 0.7) + _c("#2b1a14") * stroke[..., None] * 0.7


def tear(x, img, amount, rng):
    """Lichtenstein: a big comic-book tear rolls down one cheek."""
    h, w = x.shape[:2]
    ref = _ref(img)
    ex, ey = EYES[int(rng.integers(0, 2))]
    cx, cy = ex * w + 0.012 * w, ey * h + 0.075 * h
    r = 0.022 * w * (0.8 + 0.35 * amount)

    def shape(canvas):
        cv2.circle(canvas, _p(cx, cy), int(r * 16), 255, -1, AA, SHIFT)
        tri = [_p(cx - r * 0.95, cy - r * 0.3), _p(cx + r * 0.95, cy - r * 0.3), _p(cx, cy - r * 2.4)]
        cv2.fillPoly(canvas, [np.array(tri, np.int32)], 255, AA, SHIFT)

    body = _draw(h, w, shape)
    ring = np.clip(cv2.dilate(body, np.ones((int(3 * ref) | 1,) * 2, np.uint8)) - body, 0, 1)
    out = _paint(x, body, _c("#bfe6ff"))
    out = _paint(out, _disk(h, w, cx - r * 0.35, cy - r * 0.2, r * 0.32) * body, (1.0, 1.0, 1.0))
    return _paint(out, ring, _c("#111111"))


def polka(x, img, amount, rng):
    """Kusama: polka dots spread across the skin itself."""
    h, w = x.shape[:2]
    m = face_mask(h, w, 1.05)
    canvas = _u(x)
    color = (_c(rng.choice(["#e60012", "#111111", "#f7f3ea"])) * 255).tolist()
    placed = []
    for _ in range(400):
        if len(placed) >= int(16 + 14 * amount):
            break
        px, py = rng.uniform(0.25, 0.75) * w, rng.uniform(0.2, 0.82) * h
        r = rng.uniform(0.008, 0.024) * w
        if m[int(py), int(px)] < 0.5 or any(np.hypot(px - qx, py - qy) < r + qr + 0.006 * w for qx, qy, qr in placed):
            continue
        placed.append((px, py, r))
        cv2.circle(canvas, _p(px, py), int(r * 16), color, -1, AA, SHIFT)
    return _f(canvas)


def geometry(x, img, amount, rng):
    """Kandinsky: circles, a triangle, and lines composed over the face."""
    h, w = x.shape[:2]
    ref = _ref(img)
    out = x
    palette = ["#e8333a", "#1356a2", "#ffd31a", "#2e9e6a", "#8f5bff"]
    rng.shuffle(palette)
    ex, ey = EYES[int(rng.integers(0, 2))]
    ring = _disk(h, w, ex * w, ey * h, 0.07 * w, feather=1.5 * ref) - _disk(h, w, ex * w, ey * h, 0.045 * w, feather=1.5 * ref)
    out = _paint(out, np.clip(ring, 0, 1) * 0.85, _c(palette[0]))
    other = CHEEKS[1] if ex < 0.5 else CHEEKS[0]
    out = out * (1 - _disk(h, w, other[0] * w, other[1] * h, 0.055 * w, feather=1.5 * ref)[..., None] * (1 - _c(palette[1])) * 0.6)

    def marks(canvas):
        tri = [_p(0.5 * w, 0.24 * h), _p(0.43 * w, 0.34 * h), _p(0.57 * w, 0.34 * h)]
        cv2.fillPoly(canvas, [np.array(tri, np.int32)], 255, AA, SHIFT)

    out = _paint(out, _draw(h, w, marks) * 0.75 * min(1, amount), _c(palette[2]))

    def lines(canvas):
        for _ in range(int(2 + 2 * amount)):
            a = rng.uniform(0, np.pi)
            cx, cy = rng.uniform(0.4, 0.6) * w, rng.uniform(0.4, 0.7) * h
            dx, dy = np.cos(a) * 0.3 * w, np.sin(a) * 0.3 * w
            cv2.line(canvas, _p(cx - dx, cy - dy), _p(cx + dx, cy + dy), 255, max(1, int(2 * ref)), AA, SHIFT)

    return _paint(out, _draw(h, w, lines) * 0.9, _c("#111111"))


def scrawl(x, img, amount, rng):
    """Basquiat: chalky scribbled eyes and crude painted teeth."""
    h, w = x.shape[:2]
    ref = _ref(img)
    thick = max(2, int(2.4 * ref))

    def chalk(canvas):
        for ex, ey in EYES:
            for loop in range(2):
                pts = []
                for t in np.linspace(0, 2 * np.pi, 28):
                    rr = 0.05 * w * (1 + 0.18 * loop) * (1 + rng.normal(0, 0.06))
                    pts.append(_p(ex * w + np.cos(t) * rr, ey * h + np.sin(t) * rr * 0.8))
                cv2.polylines(canvas, [np.array(pts, np.int32)], False, 255, thick, AA, SHIFT)
        mx, my = MOUTH[0] * w, MOUTH[1] * h
        half = 0.075 * w * (0.8 + 0.3 * amount)
        top, bottom = my - 0.018 * h, my + 0.018 * h
        cv2.rectangle(canvas, _p(mx - half, top), _p(mx + half, bottom), 255, thick, AA, SHIFT)
        for k in range(1, 6):
            xk = mx - half + k * half / 3
            cv2.line(canvas, _p(xk, top), _p(xk + rng.normal(0, 0.002 * w), bottom), 255, thick, AA, SHIFT)

    stroke = _draw(h, w, chalk)
    shadow = cv2.GaussianBlur(stroke, (0, 0), 1.5 * ref)
    out = _paint(x, shadow * 0.6, _c("#111111"))
    return _paint(out, stroke * 0.92, _c("#f4efe2"))


def grid_panes(x, img, amount, rng):
    """Mondrian: black bars cut through the face with primary panes."""
    h, w = x.shape[:2]
    ref = _ref(img)
    vx = w * rng.uniform(0.44, 0.56)
    hy = h * rng.uniform(0.5, 0.6)
    m = face_mask(h, w, 1.2)
    xs, ys = _grid(h, w)
    quads = [(xs < vx) & (ys < hy), (xs >= vx) & (ys < hy), (xs < vx) & (ys >= hy), (xs >= vx) & (ys >= hy)]
    picks = rng.choice(4, 2, replace=False)
    out = x
    for q, color in zip(picks, ["#d40920", "#1356a2"]):
        pane = quads[int(q)].astype(np.float32) * m * 0.5 * min(1, amount)
        out = out * (1 - pane[..., None] * (1 - _c(color)))
    bar = max(3, int(5 * ref))
    lines = ((np.abs(xs - vx) < bar) | (np.abs(ys - hy) < bar)).astype(np.float32) * np.clip(m * 2, 0, 1)
    return _paint(out, lines, (0.07, 0.07, 0.07))


def gold_flecks(x, img, amount, rng):
    """Klimt: hammered gold leaf flecks across cheeks and brow."""
    h, w = x.shape[:2]
    ref = _ref(img)
    m = face_mask(h, w, 1.05)
    canvas = np.zeros((h, w), np.uint8)
    for _ in range(int(40 + 40 * amount)):
        px, py = rng.uniform(0.28, 0.72) * w, rng.uniform(0.25, 0.8) * h
        size = rng.uniform(1.5, 5) * ref
        pts = [_p(px + np.cos(a) * size * rng.uniform(0.6, 1.3), py + np.sin(a) * size * rng.uniform(0.6, 1.3))
               for a in np.linspace(0, 2 * np.pi, 6, endpoint=False)]
        cv2.fillPoly(canvas, [np.array(pts, np.int32)], 255, AA, SHIFT)
    flecks = canvas.astype(np.float32) / 255.0 * m
    shimmer = 0.75 + 0.25 * _noise(rng, h, w, 24)
    gold = _c("#e8b84a") * shimmer[..., None]
    return _paint(x, flecks * 0.9, 0) + gold * (flecks * 0.9)[..., None]


def star_freckles(x, img, amount, rng):
    """Peter Max: cosmic star freckles sprinkled over the cheeks."""
    h, w = x.shape[:2]
    ref = _ref(img)

    def stars(canvas):
        for cx, cy in CHEEKS:
            for _ in range(int(3 + 3 * amount)):
                sx, sy = rng.normal(cx * w, 0.03 * w), rng.normal(cy * h, 0.02 * h)
                size = rng.uniform(2.5, 5.5) * ref
                pts = [_p(sx + np.cos(a) * (size if i % 2 == 0 else size * 0.4), sy + np.sin(a) * (size if i % 2 == 0 else size * 0.4))
                       for i, a in enumerate(np.linspace(-np.pi / 2, 1.5 * np.pi, 10, endpoint=False))]
                cv2.fillPoly(canvas, [np.array(pts, np.int32)], 255, AA, SHIFT)

    star = _draw(h, w, stars)
    out = _paint(x, cv2.GaussianBlur(star, (0, 0), 2 * ref) * 0.7, _c("#ff3fa4"))
    return _paint(out, star, _c("#fff6a8"))


def bloom(x, img, amount, rng):
    """Monet: the face blooms into soft pastel light."""
    h, w = x.shape[:2]
    ref = _ref(img)
    glow = cv2.GaussianBlur(x, (0, 0), 10 * ref)
    m = face_mask(h, w, 1.2)[..., None]
    pastel = glow * 0.7 + _c(rng.choice(["#f7c6d9", "#c9d8f5", "#f3e3b0"])) * 0.3
    return 1 - (1 - x) * (1 - pastel * m * 0.45 * amount)


def apple(x, img, amount, rng):
    """Magritte: a green apple hovers in front of the face."""
    h, w = x.shape[:2]
    ref = _ref(img)
    cx = w * (0.5 + rng.uniform(-0.012, 0.012))
    cy = h * (0.6 + rng.uniform(-0.01, 0.02))
    r = w * 0.095 * (0.85 + 0.25 * amount)
    ys, xs = np.ogrid[:h, :w]

    def circle(ox, oy, rad):
        return np.sqrt((xs - (cx + ox)) ** 2 + (ys - (cy + oy)) ** 2) - rad

    sdf = np.minimum(np.minimum(circle(-0.3 * r, -0.05 * r, 0.78 * r), circle(0.3 * r, -0.05 * r, 0.78 * r)), circle(0, 0.15 * r, 0.86 * r))
    body = np.clip(0.5 - sdf / (1.2 * ref), 0, 1).astype(np.float32)
    shadow = cv2.GaussianBlur(np.roll(np.roll(body, int(0.15 * r), 0), int(0.12 * r), 1), (0, 0), 0.25 * r)
    out = x * (1 - shadow[..., None] * 0.35)
    light = np.clip(1 - np.sqrt((xs - (cx - 0.3 * r)) ** 2 + (ys - (cy - 0.35 * r)) ** 2) / (1.7 * r), 0, 1)[..., None]
    skin = _c("#2f7d32") * (1 - light) + _c("#9ad85f") * light
    out = _paint(out, body, 0) + skin * body[..., None]
    out = _paint(out, _disk(h, w, cx - 0.32 * r, cy - 0.3 * r, 0.16 * r, 0.1 * r, 0.08 * r) * body * 0.75, (1.0, 1.0, 1.0))

    def stem(canvas):
        cv2.line(canvas, _p(cx, cy - 0.7 * r), _p(cx + 0.08 * r, cy - 1.12 * r), 255, max(2, int(0.08 * r)), AA, SHIFT)

    def leaf(canvas):
        cv2.ellipse(canvas, _p(cx + 0.33 * r, cy - 1.0 * r), _p(0.3 * r, 0.12 * r), -28, 0, 360, 255, -1, AA, SHIFT)

    out = _paint(out, _draw(h, w, stem), _c("#5a3a1e"))
    return _paint(out, _draw(h, w, leaf), _c("#3fa34d"))


FACE_PLAY = {
    "peter_max": star_freckles,
    "lichtenstein": tear,
    "hockney": ripples,
    "mondrian": grid_panes,
    "kusama": polka,
    "klimt": gold_flecks,
    "van_gogh": twist,
    "monet": bloom,
    "picasso": cubist,
    "mucha": poster_ink,
    "kandinsky": geometry,
    "kahlo": unibrow,
    "dali": melt,
    "basquiat": scrawl,
    "rothko": bands,
    "pollock": drips,
    "hopper": light_split,
    "magritte": apple,
    "hirst": spots,
    "murakami": cel_blush,
    "vasarely": bulge,
}


def with_face(artist: Artist, effect) -> Artist:
    """Wrap an artist so its face effect runs after the render and lands in the recipe."""
    if effect is None:
        return artist

    def render(img, face=0.0, face_seed=0, **params):
        out = artist.render(img, **params)
        if not face:
            return out
        x = _f(out)
        return _u(np.clip(effect(x, img, float(face), np.random.default_rng(int(face_seed))), 0, 1))

    def sample(rng: random.Random, scale: float) -> dict:
        params = artist.sample(rng, scale)
        params["face"] = round(min(1.6, 0.55 + 0.5 * float(scale)), 3)
        params["face_seed"] = rng.randint(0, 2**31 - 1)
        return params

    return Artist(artist.label, render, sample)
