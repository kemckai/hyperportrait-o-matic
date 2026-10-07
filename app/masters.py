"""Twenty more artist-inspired styles built on the shared helpers in app.artists."""

from __future__ import annotations

import cv2
import numpy as np

from app.artists import (
    BLACK,
    LUMA,
    Artist,
    _artist,
    _c,
    _f,
    _fill,
    _ink,
    _levels,
    _outline,
    _over,
    _paint,
    _prep,
    _quantize,
    _ref,
    _saturate,
    _u,
    subject_mask,
)
from app.framing import face_mask, skin_mask


def _alpha(layer: np.ndarray) -> np.ndarray:
    return layer.astype(np.float32) / 255.0


def _lum(x: np.ndarray) -> np.ndarray:
    return (x * LUMA).sum(axis=-1)


def _stretch(lum: np.ndarray, mask: np.ndarray) -> np.ndarray:
    inside = lum[mask > 0.5]
    lo, hi = np.percentile(inside, [4, 96]) if inside.size > 100 else (0.0, 1.0)
    return np.clip((lum - lo) / (hi - lo + 1e-6), 0.0, 1.0)


def _grid_points(h, w, spacing, rng, keep=None):
    ys, xs = np.mgrid[0:h:spacing, 0:w:spacing].astype(np.float32)
    xs = (xs + rng.uniform(0, spacing, xs.shape)).ravel()
    ys = (ys + rng.uniform(0, spacing, ys.shape)).ravel()
    xs, ys = np.clip(xs, 0, w - 1), np.clip(ys, 0, h - 1)
    if keep is not None:
        inside = keep[ys.astype(int), xs.astype(int)] > 0.5
        xs, ys = xs[inside], ys[inside]
    return xs, ys


def _flow_angle(img: np.ndarray) -> np.ndarray:
    """Stroke direction that follows contours, from the smoothed structure tensor."""
    ref = _ref(img)
    gray = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 2 * ref)
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    sigma = 6 * ref
    jxx = cv2.GaussianBlur(gx * gx, (0, 0), sigma)
    jyy = cv2.GaussianBlur(gy * gy, (0, 0), sigma)
    jxy = cv2.GaussianBlur(gx * gy, (0, 0), sigma)
    return 0.5 * np.arctan2(2 * jxy, jxx - jyy) + np.pi / 2


def _strokes(canvas, src, angle, xs, ys, length, thick, rng, jitter=0.15, shade=0.08):
    h, w = canvas.shape[:2]
    if len(xs) == 0:
        return
    xi = np.clip(xs.astype(int), 0, w - 1)
    yi = np.clip(ys.astype(int), 0, h - 1)
    a = angle[yi, xi] + rng.normal(0, jitter, len(xs))
    dx = np.cos(a) * length / 2
    dy = np.sin(a) * length / 2
    colors = np.clip(src[yi, xi] * (1 + rng.uniform(-shade, shade, (len(xs), 1))), 0, 1) * 255
    p0 = np.stack([xs - dx, ys - dy], 1).astype(np.int32).tolist()
    p1 = np.stack([xs + dx, ys + dy], 1).astype(np.int32).tolist()
    colors = colors.tolist()
    thick = np.maximum(1, np.asarray(thick).astype(int)).tolist()
    for i in rng.permutation(len(xs)).tolist():
        cv2.line(canvas, p0[i], p1[i], colors[i], thick[i], cv2.LINE_AA)


def _blobs(h, w, palette, cells, rng, sigma):
    """Low-frequency patches of palette colors."""
    index = rng.integers(0, len(palette), (cells, cells))
    colors = np.stack([_c(x) for x in palette])[index]
    colors = cv2.resize(colors, (w, h), interpolation=cv2.INTER_CUBIC)
    return np.clip(cv2.GaussianBlur(colors, (0, 0), sigma), 0, 1)


# ---------- Van Gogh ----------

@_artist
def van_gogh(img, seed, spacing):
    h, w = img.shape[:2]
    ref = _ref(img)
    rng = np.random.default_rng(seed)
    base = _prep(img, 2)
    mask = subject_mask(img)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    centers = rng.uniform([0.1, 0.05], [0.9, 0.4], (3, 2)) * [w, h]
    vx = np.full((h, w), 0.35, np.float32)
    vy = np.zeros((h, w), np.float32)
    swirl = np.zeros((h, w), np.float32)
    glow = np.zeros((h, w), np.float32)
    for cx, cy in centers:
        dx, dy = xs - cx, ys - cy
        r = np.sqrt(dx * dx + dy * dy) + 1
        weight = np.exp(-r / (0.22 * w))
        vx += -dy / r * weight
        vy += dx / r * weight
        swirl += np.sin(r / (9 * ref)) * weight
        glow += np.exp(-r / (0.035 * w))
    t = np.clip(ys / h * 0.9 + 0.25 * swirl, 0, 1)[..., None]
    sky = _c("#0b1d51") * (1 - t) + _c("#3c6fd1") * t
    sky = _paint(sky, np.clip(swirl, 0, 1) * 0.5, _c("#9cc3ee"))
    sky = _paint(sky, np.clip(glow, 0, 1), _c("#f7d84a"))

    fig = _f(_saturate(base, 1.3))
    fig = _paint(fig, np.clip(0.5 - _lum(fig), 0, 0.5) * 0.5, _c("#1d3f8a"))
    src = _over(fig, sky, mask)
    angle = np.where(mask > 0.5, _flow_angle(base), np.arctan2(vy, vx))
    canvas = _u(cv2.GaussianBlur(src, (0, 0), 2 * ref))
    face = face_mask(h, w, 1.0)
    s = spacing * ref
    px, py = _grid_points(h, w, s, rng)
    f = face[py.astype(int), px.astype(int)]
    _strokes(canvas, src, angle, px, py, s * (2.8 - 1.5 * f), s * (0.8 - 0.35 * f), rng)
    px, py = _grid_points(h, w, s * 0.6, rng, face_mask(h, w, 1.05))
    _strokes(canvas, src, angle, px, py, np.full(len(px), s * 1.1), np.full(len(px), s * 0.4), rng, 0.1)
    return _paint(_f(canvas), face_mask(h, w, 0.85) * 0.3, _f(base))


def _sample_van_gogh(rng, scale):
    return {"seed": rng.randint(0, 2**31 - 1), "spacing": rng.uniform(4.5, 6.0), "pop": scale}


# ---------- Monet ----------

MONET = {
    "water_lilies": ["#3e6b5a", "#7fa98b", "#b7a6d6", "#e8c3d0", "#5b7fb5"],
    "poppies": ["#6f9a54", "#a9c46c", "#d94f3d", "#f2d5a0", "#8fb4d9"],
    "haystacks": ["#e3a857", "#f2cf8a", "#b48ab8", "#7d9bc1", "#e6b9a6"],
}


@_artist
def monet(img, seed, palette):
    h, w = img.shape[:2]
    ref = _ref(img)
    rng = np.random.default_rng(seed)
    base = _prep(img, 2)
    mask = subject_mask(img)
    x = _f(base)
    pastel = 1 - (1 - (x * 0.8 + _blobs(h, w, MONET[palette], 6, rng, 30 * ref) * 0.2)) * 0.88
    garden = _blobs(h, w, MONET[palette], 14, rng, 14 * ref)
    bg = cv2.GaussianBlur(x, (0, 0), 18 * ref) * 0.35 + garden * 0.65
    src = _over(pastel, bg, mask)
    noise = cv2.resize(rng.normal(0, 0.6, (8, 8)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
    angle = noise + np.where(mask > 0.5, 0.0, 0.1)
    canvas = _u(cv2.GaussianBlur(src, (0, 0), 4 * ref))
    face = face_mask(h, w, 1.0)
    s = 6.5 * ref
    px, py = _grid_points(h, w, s, rng)
    f = face[py.astype(int), px.astype(int)]
    _strokes(canvas, src, angle, px, py, s * (2.2 - 1.0 * f), s * (0.95 - 0.45 * f), rng, 0.4, 0.12)
    px, py = _grid_points(h, w, s * 0.55, rng, face_mask(h, w, 1.05))
    _strokes(canvas, src, angle, px, py, np.full(len(px), s * 0.9), np.full(len(px), s * 0.4), rng, 0.3, 0.06)
    return _paint(_f(canvas), face_mask(h, w, 0.85) * 0.4, pastel)


def _sample_monet(rng, scale):
    return {"seed": rng.randint(0, 2**31 - 1), "palette": rng.choice(list(MONET)), "pop": scale}


# ---------- Seurat ----------

@_artist
def seurat(img, seed, dot):
    h, w = img.shape[:2]
    ref = _ref(img)
    rng = np.random.default_rng(seed)
    base = _prep(img, 2)
    mask = subject_mask(img)
    fig = _f(_saturate(base, 1.25))
    park = _blobs(h, w, ["#4f7d3a", "#86a95a", "#4f86b5", "#e8d9a8", "#2f5d3a"], 9, rng, 20 * ref)
    bg = cv2.GaussianBlur(_f(base), (0, 0), 12 * ref) * 0.4 + park * 0.6
    src = _over(fig, bg, mask)
    canvas = _u(_fill(h, w, _c("#f1e9d6")))
    s = dot * ref

    def dots(spacing, radius, keep=None, fleck=0.14):
        px, py = _grid_points(h, w, spacing, rng, keep)
        colors = src[py.astype(int), px.astype(int)] + rng.uniform(-fleck, fleck, (len(px), 3))
        colors = (np.clip(colors, 0, 1) * 255).tolist()
        cx = (px * 16).astype(int).tolist()
        cy = (py * 16).astype(int).tolist()
        r = int(radius * 16)
        for i in rng.permutation(len(px)).tolist():
            cv2.circle(canvas, (cx[i], cy[i]), r, colors[i], -1, cv2.LINE_AA, shift=4)

    dots(s * 0.85, s * 0.55)
    dots(s * 0.55, s * 0.36, face_mask(h, w, 1.1), 0.08)
    return _f(canvas)


def _sample_seurat(rng, scale):
    return {"seed": rng.randint(0, 2**31 - 1), "dot": rng.uniform(4.0, 5.5), "pop": scale}


# ---------- Picasso ----------

CUBIST = ["#3d2b1f", "#7a5230", "#b0864f", "#d9b77e", "#efe1c0", "#5d6b73", "#8fa1a8", "#6b7a3a"]


@_artist
def picasso(img, seed, cells):
    h, w = img.shape[:2]
    ref = _ref(img)
    rng = np.random.default_rng(seed)
    base = _prep(img, 3)
    mask = subject_mask(img)
    face = face_mask(h, w, 1.0)

    n_face = int(cells * 0.18)
    pts = []
    while len(pts) < n_face:
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        if face[int(y), int(x)] > 0.5:
            pts.append((x, y))
    pts += [(rng.uniform(0, w), rng.uniform(0, h)) for _ in range(cells - n_face)]
    pts = np.array(pts, np.float32)

    sw = 192
    sh = max(1, int(h * sw / w))
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    small = pts * [sw / w, sh / h]
    d = (xx[..., None] - small[:, 0]) ** 2 + (yy[..., None] - small[:, 1]) ** 2
    labels = cv2.resize(d.argmin(-1).astype(np.float32), (w, h), interpolation=cv2.INTER_NEAREST).astype(np.int64)

    core = face[pts[:, 1].astype(int), pts[:, 0].astype(int)]
    shift = rng.normal(0, 12 * ref, (len(pts), 2)) * (1 - 0.85 * core)[:, None]
    gy, gx = np.mgrid[0:h, 0:w].astype(np.float32)
    x = cv2.remap(_f(base), gx - shift[labels, 0].astype(np.float32), gy - shift[labels, 1].astype(np.float32),
                  cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)

    n = len(pts)
    counts = np.bincount(labels.ravel(), minlength=n).astype(np.float32) + 1e-6
    means = np.stack([np.bincount(labels.ravel(), x[..., c].ravel(), n) for c in range(3)], 1) / counts[:, None]
    palette = np.stack([_c(c) for c in CUBIST])
    nearest = palette[((means[:, None, :] - palette[None]) ** 2).sum(-1).argmin(1)]
    in_fig = np.bincount(labels.ravel(), mask.ravel(), n) / counts
    pull = np.where(in_fig > 0.5, 0.35, 0.7)[:, None]
    fill = means * (1 - pull) + nearest * pull

    cx = np.bincount(labels.ravel(), gx.ravel(), n) / counts
    cy = np.bincount(labels.ravel(), gy.ravel(), n) / counts
    direction = rng.normal(0, 1, (n, 2))
    direction /= np.linalg.norm(direction, axis=1, keepdims=True) + 1e-6
    plane = ((gx - cx[labels]) * direction[labels, 0] + (gy - cy[labels]) * direction[labels, 1]) / (0.12 * w)
    shade = np.clip(1 + 0.12 * plane, 0.8, 1.2)[..., None]

    keep = (0.35 + 0.5 * face)[..., None]
    out = (x * keep + fill[labels] * (1 - keep)) * (1 + (shade - 1) * (1 - 0.6 * face[..., None]))
    edges = np.zeros((h, w), np.uint8)
    edges[:, :-1] |= (labels[:, :-1] != labels[:, 1:]).astype(np.uint8)
    edges[:-1, :] |= (labels[:-1, :] != labels[1:, :]).astype(np.uint8)
    edges = cv2.dilate(edges, np.ones((max(2, int(2 * ref)),) * 2, np.uint8))
    out = _paint(out, edges.astype(np.float32) * (0.85 - 0.7 * face), _c("#2a1d14"))
    return _paint(out, _outline(mask, 3 * ref), _c("#2a1d14"))


def _sample_picasso(rng, scale):
    return {"seed": rng.randint(0, 2**31 - 1), "cells": rng.randint(45, 75), "pop": scale}


# ---------- Matisse ----------

MATISSE = ["#1d4fa3", "#e9573f", "#f2c12e", "#2e9e6a", "#e85a8a"]


@_artist
def matisse(img, seed, bg):
    h, w = img.shape[:2]
    ref = _ref(img)
    rng = np.random.default_rng(seed)
    base = _prep(img, 3)
    mask = subject_mask(img)
    others = [c for i, c in enumerate(MATISSE) if i != bg]
    canvas = _u(_fill(h, w, _c(MATISSE[bg])))
    for _ in range(rng.integers(7, 12)):
        cx = rng.choice([rng.uniform(0, 0.3), rng.uniform(0.7, 1.0)]) * w
        cy = rng.uniform(0, 1) * h
        radius = rng.uniform(0.08, 0.18) * w
        lobes = rng.integers(3, 7)
        phase = rng.uniform(0, 2 * np.pi)
        theta = np.linspace(0, 2 * np.pi, 160)
        r = radius * (1 + 0.38 * np.sin(lobes * theta + phase) + 0.14 * np.sin(2 * lobes * theta))
        pts = np.stack([cx + r * np.cos(theta), cy + r * np.sin(theta)], -1).astype(np.int32)
        color = (_c(others[int(rng.integers(0, len(others)))]) * 255).tolist()
        cv2.fillPoly(canvas, [pts], color, cv2.LINE_AA)
    paper = 0.96 + 0.04 * rng.random((h, w)).astype(np.float32)
    bgf = _f(canvas) * paper[..., None]

    shadow = cv2.warpAffine(mask, np.float32([[1, 0, 6 * ref], [0, 1, 8 * ref]]), (w, h))
    bgf = bgf * (1 - 0.25 * cv2.GaussianBlur(shadow, (0, 0), 4 * ref))[..., None]

    levels = _levels(base, mask, 3)
    skin = skin_mask(base)[..., None]
    skin_tones = np.stack([_c("#8a3b2a"), _c("#e07a5f"), _c("#f6c9a9")])[levels]
    accent = [_c(others[0]), _c(others[1])]
    cloth = np.stack([_c("#111b3d"), accent[0], accent[1]])[levels]
    fig = skin_tones * skin + cloth * (1 - skin)
    crisp = np.clip((mask - 0.5) * 4 + 0.5, 0, 1)
    return _over(fig * paper[..., None], bgf, crisp)


def _sample_matisse(rng, scale):
    return {"seed": rng.randint(0, 2**31 - 1), "bg": rng.randrange(len(MATISSE)), "pop": scale}


# ---------- Mucha ----------

MUCHA = {
    "sage": ["#5b6b4a", "#a3b18a", "#efe4c8", "#c9a227", "#b7735f"],
    "rose": ["#6b3e4a", "#c78b8b", "#f1e2d0", "#c9a227", "#7a8f6a"],
    "sky": ["#3c5a6b", "#8fb1bf", "#efe6d2", "#c9a227", "#b56b5a"],
}


@_artist
def mucha(img, scheme):
    h, w = img.shape[:2]
    ref = _ref(img)
    dark, mid, light, gold, accent = (_c(x) for x in MUCHA[scheme])
    base = _prep(img, 2)
    mask = subject_mask(img)
    ys = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    bg = light * (1 - ys) + (mid * 0.6 + light * 0.4) * ys
    bg = np.broadcast_to(bg, (h, w, 3)).copy()

    layer = np.zeros((h, w), np.uint8)
    ring = np.zeros((h, w), np.uint8)
    cx, cy, radius = w // 2, int(h * 0.42), int(w * 0.4)
    cv2.circle(layer, (cx, cy), radius, 255, -1, cv2.LINE_AA)
    bg = _paint(bg, _alpha(layer) * 0.55, accent * 0.4 + light * 0.6)
    cv2.circle(ring, (cx, cy), radius, 255, max(2, int(3 * ref)), cv2.LINE_AA)
    cv2.circle(ring, (cx, cy), int(radius * 0.93), 255, max(1, int(1.5 * ref)), cv2.LINE_AA)
    for k in range(48):
        a = k / 48 * 2 * np.pi
        cv2.circle(ring, (int(cx + np.cos(a) * radius * 0.965), int(cy + np.sin(a) * radius * 0.965)),
                   max(1, int(3 * ref)), 255, -1, cv2.LINE_AA)
    for k in range(36):
        a = k / 36 * 2 * np.pi
        p0 = (int(cx + np.cos(a) * radius * 0.6), int(cy + np.sin(a) * radius * 0.6))
        p1 = (int(cx + np.cos(a) * radius * 0.9), int(cy + np.sin(a) * radius * 0.9))
        cv2.line(layer, p0, p1, 0, 1)
        cv2.line(ring, p0, p1, 110, max(1, int(ref)), cv2.LINE_AA)
    margin = int(0.04 * w)
    cv2.rectangle(ring, (margin, margin), (w - margin, h - margin), 255, max(2, int(3 * ref)), cv2.LINE_AA)
    bg = _paint(bg, _alpha(ring), gold)
    edge = int(0.02 * w)
    bg[:edge], bg[-edge:], bg[:, :edge], bg[:, -edge:] = dark, dark, dark, dark

    labels, centers = _quantize(base, 6)
    soft = _f(base) * 0.45 + centers[labels] * 0.55
    gray = _lum(soft)[..., None]
    soft = soft * 0.75 + gray * 0.25
    soft = soft * 0.85 + light * 0.15
    out = _over(soft, bg, mask)
    out = _paint(out, _ink(base, 1, c=7) * mask * 0.7, dark * 0.8)
    return _paint(out, _outline(mask, 3 * ref), dark)


def _sample_mucha(rng, scale):
    return {"scheme": rng.choice(list(MUCHA)), "pop": scale}


# ---------- Hokusai ----------

@_artist
def hokusai(img, seed, pattern):
    h, w = img.shape[:2]
    ref = _ref(img)
    rng = np.random.default_rng(seed)
    paper, blue, indigo = _c("#efe3c8"), _c("#1f3a5f"), _c("#4a6d8c")
    tan, dark, red = _c("#d9c39a"), _c("#2a2320"), _c("#b5442c")
    base = _prep(img, 3)
    mask = subject_mask(img)

    canvas = _u(_fill(h, w, paper))
    if pattern == "waves":
        r = int(34 * ref)
        rings = [(1.0, blue), (0.8, paper), (0.62, indigo), (0.44, paper), (0.26, blue)]
        for row, y in enumerate(range(-r, h + r, max(2, r // 2))):
            offset = r if row % 2 else 0
            for x in range(-r + offset, w + r, 2 * r):
                for scale, color in rings:
                    cv2.circle(canvas, (x, y), max(1, int(r * scale)), (color * 255).tolist(), -1, cv2.LINE_AA)
    else:
        ys = np.linspace(0, 1, h, dtype=np.float32)
        for band in range(5):
            center = rng.uniform(0.1, 0.95)
            width = rng.uniform(0.04, 0.09)
            alpha = np.exp(-((ys - center) / width) ** 2)[:, None]
            wobble = 0.5 + 0.5 * np.sin(np.linspace(0, rng.uniform(4, 9), w) + band)[None, :]
            stripe = np.clip(alpha * (0.5 + 0.5 * wobble), 0, 1)
            canvas = _u(_paint(_f(canvas), stripe * 0.8, indigo if band % 2 else blue))
    fiber = 0.95 + 0.07 * cv2.GaussianBlur(rng.random((h, w)).astype(np.float32), (0, 0), 0.8)
    bg = _f(canvas) * fiber[..., None]

    levels = _levels(base, mask, 4)
    skin = skin_mask(base)[..., None]
    skin_tones = np.stack([tan * 0.8, tan, tan * 0.5 + paper * 0.5, paper])[levels]
    cloth = np.stack([dark, blue, indigo, tan])[levels]
    fig = (skin_tones * skin + cloth * (1 - skin)) * fiber[..., None]
    out = _over(fig, bg, mask)
    out = _paint(out, _ink(base, 1, c=6) * mask, dark)
    out = _paint(out, _outline(mask, 2 * ref), dark)

    seal = np.zeros((h, w), np.uint8)
    inner = np.zeros((h, w), np.uint8)
    size = int(0.085 * w)
    x0, y0 = int(w * 0.88) - size, int(h * 0.05)
    cv2.rectangle(seal, (x0, y0), (x0 + size, y0 + size), 255, -1)
    pad = max(2, size // 8)
    cv2.rectangle(inner, (x0 + pad, y0 + pad), (x0 + size - pad, y0 + size - pad), 255, max(1, int(1.5 * ref)))
    for k in (1, 2):
        xk = x0 + k * size // 3
        cv2.line(inner, (xk, y0 + pad * 2), (xk, y0 + size - pad * 2), 255, max(1, int(2 * ref)))
    out = _paint(out, _alpha(seal) * 0.9, red)
    return _paint(out, _alpha(inner) * 0.9, paper)


def _sample_hokusai(rng, scale):
    return {"seed": rng.randint(0, 2**31 - 1), "pattern": rng.choice(["waves", "waves", "mist"]), "pop": scale}


# ---------- Kandinsky ----------

KANDINSKY = ["#d62828", "#f77f00", "#fcbf49", "#1d3557", "#457b9d", "#2a9d8f", "#111111", "#e76f51"]


def _kandinsky_layer(h, w, seed, ref):
    rng = np.random.default_rng(seed)
    canvas = _u(_fill(h, w, _c("#f3ead7")))
    lines = np.zeros((h, w), np.uint8)
    colors = [(_c(c) * 255).tolist() for c in KANDINSKY]
    for _ in range(30):
        kind = rng.random()
        x, y = int(rng.uniform(0, w)), int(rng.uniform(0, h))
        size = rng.uniform(12, 70) * ref
        if kind < 0.35:
            for k, scale in enumerate((1.0, 0.7, 0.4)):
                color = colors[int(rng.integers(0, len(colors)))]
                cv2.circle(canvas, (x, y), max(2, int(size * scale)), color, -1, cv2.LINE_AA)
        elif kind < 0.55:
            a = rng.uniform(0, 2 * np.pi)
            pts = np.array([[x + np.cos(a + k * 2.1) * size, y + np.sin(a + k * 2.1) * size] for k in range(3)], np.int32)
            cv2.fillPoly(canvas, [pts], colors[int(rng.integers(0, len(colors)))], cv2.LINE_AA)
        elif kind < 0.75:
            a = rng.uniform(0, np.pi)
            p0 = (int(x - np.cos(a) * size * 3), int(y - np.sin(a) * size * 3))
            p1 = (int(x + np.cos(a) * size * 3), int(y + np.sin(a) * size * 3))
            cv2.line(lines, p0, p1, 255, max(1, int(rng.uniform(1.5, 5) * ref)), cv2.LINE_AA)
        elif kind < 0.88:
            cell = max(2, int(size / 4))
            a, b = colors[int(rng.integers(0, len(colors)))], colors[6]
            for i in range(4):
                for j in range(4):
                    cv2.rectangle(canvas, (x + i * cell, y + j * cell), (x + (i + 1) * cell, y + (j + 1) * cell),
                                  a if (i + j) % 2 else b, -1)
        else:
            cv2.ellipse(canvas, (x, y), (int(size * 1.6), int(size)), rng.uniform(0, 180), 0, rng.uniform(90, 220),
                        colors[int(rng.integers(0, len(colors)))], max(2, int(5 * ref)), cv2.LINE_AA)
    return _f(canvas), _alpha(lines)


@_artist
def kandinsky(img, seed):
    h, w = img.shape[:2]
    ref = _ref(img)
    base = _prep(img, 3)
    mask = subject_mask(img)
    bg, lines = _kandinsky_layer(h, w, seed, ref)
    labels, centers = _quantize(_saturate(base, 1.4), 6)
    fig = centers[labels] * 0.7 + _f(base) * 0.3
    out = _over(fig, bg, mask)
    out = _paint(out, _ink(base, 1) * mask, BLACK)
    keep = face_mask(h, w, 1.1)
    out = _paint(out, lines * (1 - keep) * 0.9, BLACK)
    return _paint(out, _outline(mask, 3 * ref), BLACK)


def _sample_kandinsky(rng, scale):
    return {"seed": rng.randint(0, 2**31 - 1), "pop": scale}


# ---------- Frida Kahlo ----------

FLOWERS = ["#d7263d", "#f46036", "#ff4f9a", "#ffd23f", "#c2185b"]
LEAVES = ["#2d6a3e", "#3f8f4f", "#5aa75f", "#1b3d24", "#7cbf6a"]


@_artist
def kahlo(img, seed):
    h, w = img.shape[:2]
    ref = _ref(img)
    rng = np.random.default_rng(seed)
    base = _prep(img, 3)
    mask = subject_mask(img)

    canvas = _u(_fill(h, w, _c("#1f4d2b")))
    for _ in range(70):
        x, y = int(rng.uniform(0, w)), int(rng.uniform(0, h))
        length = rng.uniform(20, 60) * ref
        angle = rng.uniform(0, 180)
        color = (_c(LEAVES[int(rng.integers(0, len(LEAVES)))]) * 255).tolist()
        cv2.ellipse(canvas, (x, y), (int(length), int(length * 0.38)), angle, 0, 360, color, -1, cv2.LINE_AA)
        a = np.radians(angle)
        cv2.line(canvas, (int(x - np.cos(a) * length), int(y - np.sin(a) * length)),
                 (int(x + np.cos(a) * length), int(y + np.sin(a) * length)), (30, 60, 25), max(1, int(ref)), cv2.LINE_AA)
    x = _f(_saturate(base, 1.3))
    tint = np.array([0.42, 0.52, 0.62], np.float32)
    warm = x * 0.7 + ((1 - 2 * tint) * x * x + 2 * tint * x) * 0.3
    out = _over(warm, _f(canvas), mask)
    out = _paint(out, _ink(base, 1, c=7) * mask * 0.5, _c("#2a1a14"))
    out = _paint(out, _outline(mask, 2 * ref), _c("#2a1a14"))

    crown = _u(out)
    count = int(rng.integers(6, 9))
    for k in range(count):
        t = np.radians(205 + 130 * k / (count - 1))
        fx = int(w / 2 + np.cos(t) * w * 0.27)
        fy = int(h * 0.5 + np.sin(t) * h * 0.36)
        rf = w * 0.055 * rng.uniform(0.8, 1.2)
        leaf = (_c(LEAVES[int(rng.integers(0, 3))]) * 255).tolist()
        cv2.ellipse(crown, (int(fx + rf * 0.9), int(fy + rf * 0.2)), (int(rf * 0.8), int(rf * 0.3)),
                    rng.uniform(-40, 40), 0, 360, leaf, -1, cv2.LINE_AA)
        petal = (_c(FLOWERS[int(rng.integers(0, len(FLOWERS)))]) * 255).tolist()
        shade = (np.array(petal) * 0.7).tolist()
        for p in range(7):
            a = p / 7 * 2 * np.pi + k
            px, py = int(fx + np.cos(a) * rf * 0.55), int(fy + np.sin(a) * rf * 0.55)
            cv2.circle(crown, (px, py), int(rf * 0.5), shade, -1, cv2.LINE_AA)
            cv2.circle(crown, (px, py), int(rf * 0.42), petal, -1, cv2.LINE_AA)
        cv2.circle(crown, (fx, fy), int(rf * 0.32), (40, 200, 255), -1, cv2.LINE_AA)
        cv2.circle(crown, (fx, fy), int(rf * 0.15), (20, 40, 90), -1, cv2.LINE_AA)
    return _f(crown)


def _sample_kahlo(rng, scale):
    return {"seed": rng.randint(0, 2**31 - 1), "pop": scale}


# ---------- Dalí ----------

@_artist
def dali(img, seed, side):
    h, w = img.shape[:2]
    ref = _ref(img)
    rng = np.random.default_rng(seed)
    base = _prep(img, 2)
    mask = subject_mask(img)
    horizon = 0.68
    ys = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    sky = _c("#1e3c72") * (1 - ys / horizon) + _c("#f6b38a") * (ys / horizon)
    ground_t = np.clip((ys - horizon) / (1 - horizon), 0, 1)
    ground = _c("#d39a5a") * (1 - ground_t) + _c("#6e4120") * ground_t
    bg = np.broadcast_to(np.where(ys < horizon, sky, ground), (h, w, 3)).copy()
    ridge = np.zeros((h, w), np.uint8)
    xs = np.linspace(0, w, 60)
    heights = horizon * h - (np.abs(np.sin(xs / w * rng.uniform(5, 9) + rng.uniform(0, 6))) * 0.06 * h)
    pts = np.vstack([np.stack([xs, heights], 1), [[w, horizon * h], [0, horizon * h]]]).astype(np.int32)
    cv2.fillPoly(ridge, [pts], 255, cv2.LINE_AA)
    bg = _paint(bg, _alpha(ridge) * 0.7, _c("#8a5a7a"))
    for _ in range(3):
        sx, sy = rng.uniform(0, w), rng.uniform(horizon + 0.05, 0.95) * h
        shadow = np.zeros((h, w), np.uint8)
        cv2.ellipse(shadow, (int(sx), int(sy)), (int(rng.uniform(60, 140) * ref), int(6 * ref)), 0, 0, 360, 255, -1, cv2.LINE_AA)
        bg = _paint(bg, cv2.GaussianBlur(_alpha(shadow), (0, 0), 3 * ref) * 0.45, _c("#3a2210"))

    oil = cv2.stylization(base, sigma_s=40, sigma_r=0.3)
    fig = _f(_saturate(cv2.addWeighted(base, 0.5, oil, 0.5, 0), 1.15))
    out = _over(fig, bg, mask)

    solid = (mask > 0.5).astype(np.uint8)
    edge = solid.copy()
    edge[:-1] &= (solid[1:] == 0).astype(np.uint8)
    edge[-3:] = 0
    edge[face_mask(h, w, 1.0) > 0.2] = 0
    eys, exs = np.nonzero(edge)
    canvas = _u(out)
    for i in rng.choice(len(exs), size=min(12, len(exs)), replace=False) if len(exs) else []:
        x, y = int(exs[i]), int(eys[i])
        color = (fig[max(0, y - 3), x] * 255).tolist()
        thick = max(2, int(rng.uniform(4, 9) * ref))
        end = (x, int(min(h - 1, y + rng.uniform(20, 70) * ref)))
        cv2.line(canvas, (x, y - 2), end, color, thick, cv2.LINE_AA)
        cv2.circle(canvas, end, int(thick * 0.8), color, -1, cv2.LINE_AA)

    cx = int(w * (0.14 if side == "left" else 0.86))
    cy = int(h * 0.78)
    rx, ry = int(0.1 * w), int(0.06 * w)
    t = np.linspace(0, 2 * np.pi, 80)
    droop = np.where(np.sin(t) > 0, 1 + 0.9 * np.sin(t) ** 3 * (np.cos(t) > -0.2), 1.0)
    clock = np.stack([cx + rx * np.cos(t), cy + ry * np.sin(t) * droop], 1).astype(np.int32)
    cv2.fillPoly(canvas, [clock], (60, 162, 201), cv2.LINE_AA)
    inner = np.stack([cx + rx * 0.85 * np.cos(t), cy + ry * 0.8 * np.sin(t) * droop], 1).astype(np.int32)
    cv2.fillPoly(canvas, [inner], (210, 233, 243), cv2.LINE_AA)
    for k in range(12):
        a = k / 12 * 2 * np.pi
        p = (int(cx + np.cos(a) * rx * 0.7), int(cy + np.sin(a) * ry * 0.65 * (1.5 if np.sin(a) > 0 else 1)))
        cv2.circle(canvas, p, max(1, int(1.5 * ref)), (30, 30, 30), -1, cv2.LINE_AA)
    cv2.line(canvas, (cx, cy), (int(cx + rx * 0.5), int(cy - ry * 0.2)), (20, 20, 20), max(1, int(2 * ref)), cv2.LINE_AA)
    cv2.line(canvas, (cx, cy), (int(cx - rx * 0.1), int(cy + ry * 0.9)), (20, 20, 20), max(1, int(2 * ref)), cv2.LINE_AA)
    return _f(canvas)


def _sample_dali(rng, scale):
    return {"seed": rng.randint(0, 2**31 - 1), "side": rng.choice(["left", "right"]), "pop": scale}


# ---------- Basquiat ----------

BASQUIAT = ["#f2c14e", "#2f6690", "#d1495b", "#e8e2d0", "#3a3a3a"]
TAGS = ["KING", "CROWN", "HERO", "GOLD", "TAR", "ART", "FAMOUS", "100%", "SOUL"]


@_artist
def basquiat(img, seed, bg):
    h, w = img.shape[:2]
    ref = _ref(img)
    rng = np.random.default_rng(seed)
    base = _prep(img, 3)
    mask = subject_mask(img)
    others = [c for i, c in enumerate(BASQUIAT) if i != bg]
    canvas = _u(_fill(h, w, _c(BASQUIAT[bg])))
    for _ in range(5):
        x0, y0 = int(rng.uniform(-0.1, 0.8) * w), int(rng.uniform(-0.1, 0.8) * h)
        x1, y1 = x0 + int(rng.uniform(0.15, 0.45) * w), y0 + int(rng.uniform(0.1, 0.35) * h)
        color = (_c(others[int(rng.integers(0, len(others)))]) * 255).tolist()
        cv2.rectangle(canvas, (x0, y0), (x1, y1), color, -1)
    canvas = cv2.GaussianBlur(canvas, (0, 0), 1.2 * ref)
    for _ in range(26):
        steps = int(rng.integers(8, 20))
        pts = np.cumsum(rng.normal(0, 14 * ref, (steps, 2)), 0) + rng.uniform(0, 1, 2) * [w, h]
        color = [(15, 15, 15), (245, 245, 240), (40, 40, 200)][int(rng.integers(0, 3))]
        cv2.polylines(canvas, [pts.astype(np.int32)], False, color, max(1, int(rng.uniform(2, 4) * ref)), cv2.LINE_AA)
    for _ in range(int(rng.integers(4, 7))):
        word = TAGS[int(rng.integers(0, len(TAGS)))]
        size = rng.uniform(0.6, 1.3) * ref
        x, y = int(rng.uniform(0.02, 0.7) * w), int(rng.uniform(0.08, 0.95) * h)
        thick = max(1, int(2 * ref))
        cv2.putText(canvas, word, (x, y), cv2.FONT_HERSHEY_SIMPLEX, size, (15, 15, 15), thick, cv2.LINE_AA)
        if rng.random() < 0.4:
            (tw, th), _ = cv2.getTextSize(word, cv2.FONT_HERSHEY_SIMPLEX, size, thick)
            cv2.line(canvas, (x, y - th // 2), (x + tw, y - th // 2), (15, 15, 15), thick, cv2.LINE_AA)

    levels = _levels(base, mask, 4)
    tones = np.stack([_c("#141414"), _c(others[0]), _c(others[1]), _c("#f4ead5")])
    fig = tones[levels] * 0.75 + _f(base) * 0.25
    out = _over(fig, _f(canvas), mask)
    out = _paint(out, _ink(base, max(2, int(3 * ref)), c=6) * mask, BLACK)
    out = _paint(out, _outline(mask, 4 * ref), BLACK)

    final = _u(out)
    cx, top, width = w / 2, h * 0.11, w * 0.24
    height = width * 0.42
    pts = np.array([
        [cx - width / 2, top + height], [cx - width / 2 - width * 0.06, top + height * 0.15],
        [cx - width / 4, top + height * 0.6], [cx, top - height * 0.1],
        [cx + width / 4, top + height * 0.6], [cx + width / 2 + width * 0.06, top + height * 0.15],
        [cx + width / 2, top + height],
    ], np.int32)
    cv2.polylines(final, [pts], True, (15, 15, 15), max(4, int(9 * ref)), cv2.LINE_AA)
    cv2.polylines(final, [pts], True, (40, 200, 255), max(2, int(5 * ref)), cv2.LINE_AA)
    for tip in pts[[1, 3, 5]]:
        cv2.circle(final, tuple(int(v) for v in tip), max(2, int(5 * ref)), (40, 200, 255), -1, cv2.LINE_AA)
    return _f(final)


def _sample_basquiat(rng, scale):
    return {"seed": rng.randint(0, 2**31 - 1), "bg": rng.randrange(len(BASQUIAT)), "pop": scale}


# ---------- Rothko ----------

ROTHKO = {
    "ember": ["#3b0d11", "#a4161a", "#e85d04"],
    "dusk": ["#1b1b3a", "#693668", "#f0a6ca"],
    "ocean": ["#0b2027", "#40798c", "#cfd7c7"],
    "sun": ["#5c1a1b", "#f48c06", "#ffba08"],
}


@_artist
def rothko(img, scheme, split, seed):
    h, w = img.shape[:2]
    ref = _ref(img)
    rng = np.random.default_rng(seed)
    ground, top, bottom = (_c(x) for x in ROTHKO[scheme])
    base = _prep(img, 2)
    mask = subject_mask(img)
    bg = _fill(h, w, ground)
    brush = 0.92 + 0.12 * cv2.GaussianBlur(rng.random((h, w)).astype(np.float32), (0, 0), 6 * ref)
    for color, (y0, y1) in ((top, (0.06, split)), (bottom, (split + 0.04, 0.94))):
        block = np.zeros((h, w), np.float32)
        block[int(y0 * h) : int(y1 * h), int(0.07 * w) : int(0.93 * w)] = 1
        block = cv2.GaussianBlur(block, (0, 0), 10 * ref) * brush
        bg = _paint(bg, np.clip(block, 0, 1), color)

    x = _f(base)
    lum = _lum(x)[..., None]
    tone = (ground * 1.4) * (1 - lum) + (bottom * 0.6 + 0.4) * lum
    fig = x * 0.55 + np.clip(tone, 0, 1) * 0.45
    out = _over(fig, bg, mask)
    glow = cv2.GaussianBlur(out, (0, 0), 14 * ref)
    return out * 0.82 + (1 - (1 - out) * (1 - glow)) * 0.18


def _sample_rothko(rng, scale):
    return {
        "scheme": rng.choice(list(ROTHKO)),
        "split": rng.uniform(0.45, 0.6),
        "seed": rng.randint(0, 2**31 - 1),
        "pop": scale,
    }


# ---------- Pollock ----------

POLLOCK = [(15, 15, 15), (240, 240, 235), (58, 138, 196), (107, 107, 47), (43, 58, 139), (128, 128, 128)]


@_artist
def pollock(img, seed, layers):
    h, w = img.shape[:2]
    ref = _ref(img)
    rng = np.random.default_rng(seed)
    base = _prep(img, 2)
    mask = subject_mask(img)
    paint = np.zeros((h, w, 3), np.uint8)
    alpha = np.zeros((h, w), np.uint8)
    for _ in range(int(layers) * 40):
        steps = int(rng.integers(20, 40))
        heading = rng.uniform(0, 2 * np.pi) + np.cumsum(rng.normal(0, 0.5, steps))
        stride = rng.uniform(8, 25) * ref
        pts = np.cumsum(np.stack([np.cos(heading), np.sin(heading)], 1) * stride, 0) + rng.uniform(0, 1, 2) * [w, h]
        pts = [pts.astype(np.int32)]
        color = POLLOCK[int(rng.integers(0, len(POLLOCK)))]
        thick = max(1, int(rng.uniform(1, 5) * ref))
        cv2.polylines(paint, pts, False, color, thick, cv2.LINE_AA)
        cv2.polylines(alpha, pts, False, 255, thick, cv2.LINE_AA)
    for _ in range(260):
        x, y = int(rng.uniform(0, w)), int(rng.uniform(0, h))
        r = max(1, int(rng.exponential(2.5) * ref))
        color = POLLOCK[int(rng.integers(0, len(POLLOCK)))]
        cv2.circle(paint, (x, y), r, color, -1, cv2.LINE_AA)
        cv2.circle(alpha, (x, y), r, 255, -1, cv2.LINE_AA)
    drips, a = _f(paint), _alpha(alpha)
    bg = _paint(_fill(h, w, _c("#d9cdb4")), a, drips)
    fig = _f(_saturate(base, 0.9))
    keep = np.maximum(face_mask(h, w, 1.1), skin_mask(base) * face_mask(h, w, 1.5))
    fig = _paint(fig, a * 0.6 * (1 - keep), drips)
    return _over(fig, bg, mask)


def _sample_pollock(rng, scale):
    return {"seed": rng.randint(0, 2**31 - 1), "layers": rng.randint(2, 4), "pop": scale}


# ---------- Hopper ----------

HOPPER = ["#3f6f63", "#b9a46b", "#6d8a96", "#8a4f3d"]


@_artist
def hopper(img, seed, wall):
    h, w = img.shape[:2]
    ref = _ref(img)
    rng = np.random.default_rng(seed)
    base = _prep(img, 3)
    mask = subject_mask(img)
    light = np.zeros((h, w), np.uint8)
    x0 = rng.uniform(-0.2, 0.15) * w
    slant = rng.uniform(0.25, 0.45) * w
    width = rng.uniform(0.35, 0.5) * w
    poly = np.array([[x0, 0], [x0 + width, 0], [x0 + width + slant, h], [x0 + slant, h]], np.int32)
    cv2.fillPoly(light, [poly], 255, cv2.LINE_AA)
    bar = np.zeros((h, w), np.uint8)
    mid = x0 + width / 2
    cv2.line(bar, (int(mid), 0), (int(mid + slant), h), 255, max(3, int(10 * ref)), cv2.LINE_AA)
    lit = cv2.GaussianBlur(np.clip(_alpha(light) - _alpha(bar), 0, 1), (0, 0), 4 * ref)

    ys = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    color = _c(HOPPER[wall])
    room = np.broadcast_to(np.where(ys < 0.8, color, color * 0.6), (h, w, 3))
    bg = room * (0.72 + 0.45 * lit[..., None])
    bg = _paint(bg, lit * 0.35, _c("#f3d9a4"))

    labels, centers = _quantize(base, 6)
    fig = centers[labels] * 0.6 + _f(base) * 0.4
    fig = fig * 0.85 + _lum(fig)[..., None] * 0.15
    fig = fig * (0.8 + 0.38 * lit[..., None])
    fig = _paint(fig, lit * 0.15, _c("#f3d9a4"))
    out = _over(np.clip(fig, 0, 1), np.clip(bg, 0, 1), mask)
    yy = np.linspace(-1, 1, h, dtype=np.float32)[:, None]
    xx = np.linspace(-1, 1, w, dtype=np.float32)[None, :]
    return out * (1 - 0.25 * np.clip(np.sqrt(xx ** 2 + yy ** 2) - 0.6, 0, 1))[..., None]


def _sample_hopper(rng, scale):
    return {"seed": rng.randint(0, 2**31 - 1), "wall": rng.randrange(len(HOPPER)), "pop": scale}


# ---------- Magritte ----------

@_artist
def magritte(img, seed, side):
    h, w = img.shape[:2]
    ref = _ref(img)
    rng = np.random.default_rng(seed)
    base = _prep(img, 2)
    mask = subject_mask(img)
    ys = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    bg = np.broadcast_to(_c("#4f86d1") * (1 - ys) + _c("#b7d3f2") * ys, (h, w, 3)).copy()
    for _ in range(int(rng.integers(6, 10))):
        cloud = np.zeros((h, w), np.uint8)
        cx, cy = rng.uniform(0, w), rng.uniform(0, h * 0.85)
        size = rng.uniform(25, 55) * ref
        for _ in range(int(rng.integers(5, 9))):
            ox, oy = rng.normal(0, size * 0.9), rng.normal(0, size * 0.3)
            cv2.circle(cloud, (int(cx + ox), int(cy + oy)), int(size * rng.uniform(0.5, 1.0)), 255, -1, cv2.LINE_AA)
        a = cv2.GaussianBlur(_alpha(cloud), (0, 0), 5 * ref)
        belly = np.clip(cv2.warpAffine(a, np.float32([[1, 0, 0], [0, 1, -size * 0.25]]), (w, h)) - a, 0, 1)
        bg = _paint(bg, a, _c("#ffffff"))
        bg = _paint(bg, belly * 0.6, _c("#9fb6d4"))

    fig = _f(_saturate(base, 1.05))
    crisp = np.clip((mask - 0.5) * 3 + 0.5, 0, 1)
    out = _u(_over(fig, bg, crisp))
    r = int(0.085 * w)
    cx = int(w * (0.8 if side == "right" else 0.2))
    cy = int(h * 0.62)
    cv2.circle(out, (cx, cy), r, (40, 150, 70), -1, cv2.LINE_AA)
    cv2.circle(out, (cx - r // 4, cy - r // 4), int(r * 0.7), (60, 190, 110), -1, cv2.LINE_AA)
    cv2.circle(out, (cx - r // 3, cy - r // 3), int(r * 0.3), (150, 235, 190), -1, cv2.LINE_AA)
    cv2.line(out, (cx, cy - r + 4), (cx + r // 6, cy - int(r * 1.35)), (30, 60, 90), max(2, int(4 * ref)), cv2.LINE_AA)
    cv2.ellipse(out, (cx + r // 3, cy - int(r * 1.15)), (int(r * 0.35), int(r * 0.14)), -25, 0, 360, (40, 140, 50), -1, cv2.LINE_AA)
    return _f(out)


def _sample_magritte(rng, scale):
    return {"seed": rng.randint(0, 2**31 - 1), "side": rng.choice(["left", "right"]), "pop": scale}


# ---------- Escher ----------

@_artist
def escher(img, k, m):
    h, w = img.shape[:2]
    ref = _ref(img)
    ivory, ink = _c("#f1ead8"), _c("#1b1b1b")
    base = _prep(img, 2)
    mask = subject_mask(img)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    dx, dy = xs - w / 2, ys - h / 2
    r = np.sqrt(dx * dx + dy * dy) + 1
    theta = np.arctan2(dy, dx)
    band = (np.floor(np.log(r) * k + theta / np.pi * m)).astype(np.int64) % 2
    bg = np.where(band[..., None] == 1, ink, ivory)

    dark = 1 - _stretch(_lum(_f(base)), mask)
    period = 5 * ref
    hatch1 = 0.5 + 0.5 * np.sin(2 * np.pi * (xs + ys) / (period * 1.414))
    hatch2 = 0.5 + 0.5 * np.sin(2 * np.pi * (xs - ys) / (period * 1.414))
    line1 = np.clip((dark * 1.1 - hatch1) * 4, 0, 1)
    line2 = np.clip((dark - 0.55) * 2.2 - hatch2, 0, 1) * 3
    lines = np.clip(np.maximum(line1, np.clip(line2, 0, 1)), 0, 1)
    fig = _paint(_fill(h, w, ivory), lines, ink)
    fig = _paint(fig, _ink(base, 1, c=6) * 0.8, ink)
    out = _over(fig, bg, mask)
    return _paint(out, _outline(mask, 3 * ref), ink)


def _sample_escher(rng, scale):
    return {"k": rng.uniform(3.0, 5.0), "m": rng.choice([6, 8, 10]), "pop": scale}


# ---------- Hirst ----------

@_artist
def hirst(img, seed, spacing):
    h, w = img.shape[:2]
    ref = _ref(img)
    rng = np.random.default_rng(seed)
    base = _prep(img, 1)
    mask = subject_mask(img)
    canvas = _u(_fill(h, w, _c("#f7f7f5")))
    s = spacing * ref
    cols, rows = int(w / s), int(h / s)
    ox, oy = (w - (cols - 1) * s) / 2, (h - (rows - 1) * s) / 2
    hues = rng.permutation(cols * rows) * (180.0 / max(1, cols * rows))
    for i in range(rows):
        for j in range(cols):
            hue = hues[i * cols + j] % 180
            hsv = np.uint8([[[hue, rng.uniform(150, 240), rng.uniform(170, 240)]]])
            color = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0, 0].tolist()
            cv2.circle(canvas, (int(ox + j * s), int(oy + i * s)), int(s * 0.3), color, -1, cv2.LINE_AA)
    x = _f(base)
    tint = np.array([0.46, 0.52, 0.56], np.float32)
    fig = x * 0.75 + ((1 - 2 * tint) * x * x + 2 * tint * x) * 0.25
    return _over(fig, _f(canvas), mask)


def _sample_hirst(rng, scale):
    return {"seed": rng.randint(0, 2**31 - 1), "spacing": rng.uniform(40, 56), "pop": scale}


# ---------- Murakami ----------

PETALS = [(60, 60, 230), (40, 150, 250), (40, 220, 250), (90, 200, 80), (230, 160, 40), (200, 80, 150), (180, 90, 240)]


def _flower(canvas, cx, cy, radius, offset, ref):
    outline = (20, 20, 20)
    line = max(1, int(1.8 * ref))
    for p in range(12):
        a = p / 12 * 2 * np.pi
        px, py = int(cx + np.cos(a) * radius * 0.62), int(cy + np.sin(a) * radius * 0.62)
        axes = (int(radius * 0.36), int(radius * 0.22))
        color = PETALS[(p + offset) % len(PETALS)]
        cv2.ellipse(canvas, (px, py), axes, np.degrees(a), 0, 360, color, -1, cv2.LINE_AA)
        cv2.ellipse(canvas, (px, py), axes, np.degrees(a), 0, 360, outline, line, cv2.LINE_AA)
    face = int(radius * 0.42)
    cv2.circle(canvas, (int(cx), int(cy)), face, (40, 220, 255), -1, cv2.LINE_AA)
    cv2.circle(canvas, (int(cx), int(cy)), face, outline, line, cv2.LINE_AA)
    eye = (max(1, int(face * 0.12)), max(1, int(face * 0.2)))
    for side in (-1, 1):
        cv2.ellipse(canvas, (int(cx + side * face * 0.35), int(cy - face * 0.2)), eye, 0, 0, 360, outline, -1, cv2.LINE_AA)
    mouth = (int(face * 0.55), int(face * 0.42))
    cv2.ellipse(canvas, (int(cx), int(cy + face * 0.1)), mouth, 0, 0, 180, (60, 40, 220), -1, cv2.LINE_AA)
    cv2.ellipse(canvas, (int(cx), int(cy + face * 0.1)), mouth, 0, 0, 180, outline, line, cv2.LINE_AA)
    cv2.line(canvas, (int(cx - mouth[0]), int(cy + face * 0.1)), (int(cx + mouth[0]), int(cy + face * 0.1)), outline, line, cv2.LINE_AA)


@_artist
def murakami(img, seed):
    h, w = img.shape[:2]
    ref = _ref(img)
    rng = np.random.default_rng(seed)
    base = _prep(img, 3)
    mask = subject_mask(img)
    canvas = _u(_fill(h, w, _c("#ffffff")))
    for _ in range(int(rng.integers(30, 45))):
        _flower(canvas, rng.uniform(0, w), rng.uniform(0, h), rng.uniform(25, 70) * ref, int(rng.integers(0, 7)), ref)
    labels, centers = _quantize(_saturate(base, 1.4), 6)
    fig = centers[labels] * 0.75 + _f(base) * 0.25
    out = _paint(_f(canvas), _outline(mask, 11 * ref), BLACK)
    out = _paint(out, _outline(mask, 9 * ref), (1.0, 1.0, 1.0))
    out = _over(fig, out, mask)
    return _paint(out, _ink(base, 1) * mask * 0.8, BLACK)


def _sample_murakami(rng, scale):
    return {"seed": rng.randint(0, 2**31 - 1), "pop": scale}


# ---------- Vasarely ----------

VASARELY = {
    "magenta": ("#ff2d95", "#2b0b5e"),
    "cyan": ("#00d1ff", "#0b1d51"),
    "mono": ("#f2f2f2", "#111111"),
    "citrus": ("#ffd400", "#ff4d00"),
}


@_artist
def vasarely(img, scheme, cells):
    h, w = img.shape[:2]
    ref = _ref(img)
    a, b = (_c(x) for x in VASARELY[scheme])
    base = _prep(img, 3)
    mask = subject_mask(img)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    dx, dy = xs - w / 2, ys - h * 0.5
    radius = 0.48 * w
    rn = np.sqrt(dx * dx + dy * dy) / radius
    bulge = np.where(rn < 1, 1 / (1 + 0.9 * (1 - rn ** 2)), 1.0)
    size = w / cells
    u, v = dx * bulge / size, dy * bulge / size
    checker = ((np.floor(u) + np.floor(v)).astype(np.int64) % 2 == 0)[..., None]
    shade = np.clip(1.05 - 0.35 * np.clip(rn, 0, 1.4), 0.55, 1.05)[..., None]
    bg = np.where(checker, a, b) * shade

    levels = _levels(base, mask, 3)
    tones = np.stack([b * 0.6, a * 0.5 + b * 0.5, a * 0.85 + 0.15])
    fig = tones[levels] * 0.8 + _f(base) * 0.2
    out = _over(fig, bg, mask)
    out = _paint(out, _ink(base, 1) * mask, b * 0.4)
    return _paint(out, _outline(mask, 3 * ref), b * 0.4)


def _sample_vasarely(rng, scale):
    return {"scheme": rng.choice(list(VASARELY)), "cells": rng.randint(12, 18), "pop": scale}


# ---------- Britto ----------

BRITTO = ["#ff1f5a", "#ffd400", "#00c2ff", "#7cfc00", "#ff7a00", "#b05cff", "#ff5ec4", "#00e0a4"]


@_artist
def britto(img, seed, cuts):
    h, w = img.shape[:2]
    ref = _ref(img)
    rng = np.random.default_rng(seed)
    base = _prep(img, 3)
    mask = subject_mask(img)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    code = np.zeros((h, w), np.int64)
    lines = np.zeros((h, w), np.uint8)
    for k in range(cuts):
        p0 = rng.uniform(0, 1, 2) * [w, h]
        angle = rng.uniform(0, np.pi)
        d = np.array([np.cos(angle), np.sin(angle)])
        side = (xs - p0[0]) * d[1] - (ys - p0[1]) * d[0] > 0
        code |= side.astype(np.int64) << k
        a, b = p0 - d * 2 * w, p0 + d * 2 * w
        cv2.line(lines, tuple(int(v) for v in a), tuple(int(v) for v in b), 255, max(3, int(5 * ref)), cv2.LINE_AA)
    _, regions = np.unique(code, return_inverse=True)
    regions = regions.reshape(h, w)
    n = int(regions.max()) + 1
    palette = np.stack([_c(c) for c in BRITTO])
    primary = palette[rng.integers(0, len(palette), n)]
    secondary = np.where(rng.random((n, 1)) < 0.5, 1.0, 0.07) * np.ones((n, 3))
    kind = rng.integers(0, 4, n)

    period = 14 * ref
    stripes = ((xs + ys) % period) < period * 0.4
    dots = (np.hypot((xs % period) - period / 2, (ys % period) - period / 2) < period * 0.25)
    checks = ((np.floor(xs / period) + np.floor(ys / period)) % 2) == 0
    patterns = np.stack([np.zeros((h, w), bool), stripes, dots, checks])
    face = face_mask(h, w, 1.05)
    pat = patterns[kind[regions], ys.astype(int), xs.astype(int)] & (face < 0.5)
    colors = np.where(pat[..., None], secondary[regions], primary[regions])

    lum = _stretch(_lum(_f(base)), mask)[..., None]
    fig = colors * (0.5 + 0.65 * lum)
    out = _over(np.clip(fig, 0, 1), colors, mask)
    out = _paint(out, _alpha(lines) * (1 - face), BLACK)
    out = _paint(out, _ink(base, max(2, int(2 * ref))) * mask, BLACK)
    return _paint(out, _outline(mask, 6 * ref), BLACK)


def _sample_britto(rng, scale):
    return {"seed": rng.randint(0, 2**31 - 1), "cuts": rng.randint(5, 8), "pop": scale}


MASTERS: dict[str, Artist] = {
    "van_gogh": Artist("Vincent van Gogh", van_gogh, _sample_van_gogh),
    "monet": Artist("Claude Monet", monet, _sample_monet),
    "seurat": Artist("Georges Seurat", seurat, _sample_seurat),
    "picasso": Artist("Pablo Picasso", picasso, _sample_picasso),
    "matisse": Artist("Henri Matisse", matisse, _sample_matisse),
    "mucha": Artist("Alphonse Mucha", mucha, _sample_mucha),
    "hokusai": Artist("Katsushika Hokusai", hokusai, _sample_hokusai),
    "kandinsky": Artist("Wassily Kandinsky", kandinsky, _sample_kandinsky),
    "kahlo": Artist("Frida Kahlo", kahlo, _sample_kahlo),
    "dali": Artist("Salvador Dalí", dali, _sample_dali),
    "basquiat": Artist("Jean-Michel Basquiat", basquiat, _sample_basquiat),
    "rothko": Artist("Mark Rothko", rothko, _sample_rothko),
    "pollock": Artist("Jackson Pollock", pollock, _sample_pollock),
    "hopper": Artist("Edward Hopper", hopper, _sample_hopper),
    "magritte": Artist("René Magritte", magritte, _sample_magritte),
    "escher": Artist("M. C. Escher", escher, _sample_escher),
    "hirst": Artist("Damien Hirst", hirst, _sample_hirst),
    "murakami": Artist("Takashi Murakami", murakami, _sample_murakami),
    "vasarely": Artist("Victor Vasarely", vasarely, _sample_vasarely),
    "britto": Artist("Romero Britto", britto, _sample_britto),
}
