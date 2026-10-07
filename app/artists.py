"""Artist-inspired poster styles. Each samples JSON-safe params, then renders BGR uint8."""

from __future__ import annotations

import functools
import hashlib
import random
import threading
from collections import OrderedDict
from dataclasses import dataclass
from typing import Callable

import cv2
import numpy as np

from app.framing import PADDING, face_mask, skin_mask

LUMA = np.array([0.114, 0.587, 0.299], dtype=np.float32)
BLACK = (0.06, 0.06, 0.07)


@dataclass(frozen=True)
class Artist:
    label: str
    render: Callable[..., np.ndarray]
    sample: Callable[[random.Random, float], dict]


def _c(hex_color: str) -> np.ndarray:
    value = hex_color.lstrip("#")
    r, g, b = (int(value[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    return np.array([b, g, r], dtype=np.float32)


def _ref(img: np.ndarray) -> float:
    return min(img.shape[:2]) / 512.0


def _f(img: np.ndarray) -> np.ndarray:
    return img.astype(np.float32) / 255.0


def _u(x: np.ndarray) -> np.ndarray:
    return np.clip(np.round(x * 255.0), 0, 255).astype(np.uint8)


def _fill(h: int, w: int, color) -> np.ndarray:
    return np.broadcast_to(np.asarray(color, dtype=np.float32), (h, w, 3)).copy()


def _paint(base: np.ndarray, alpha: np.ndarray, color) -> np.ndarray:
    a = alpha[..., None] if alpha.ndim == 2 else alpha
    return base * (1.0 - a) + np.asarray(color, dtype=np.float32) * a


def _over(fig: np.ndarray, bg: np.ndarray, mask: np.ndarray) -> np.ndarray:
    m = mask[..., None]
    return fig * m + bg * (1.0 - m)


def _saturate(img: np.ndarray, factor: float) -> np.ndarray:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * factor, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def _prep(img: np.ndarray, passes: int = 2) -> np.ndarray:
    """Bilateral passes flatten skin into clean poster regions."""
    out = img
    diameter = max(5, int(7 * _ref(img)) | 1)
    for _ in range(passes):
        out = cv2.bilateralFilter(out, diameter, 45, diameter)
    return out


def _levels(img: np.ndarray, mask: np.ndarray, n: int) -> np.ndarray:
    """Luminance bands with cut points balanced over the subject, not the backdrop."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    gray = cv2.GaussianBlur(gray, (0, 0), 1.5 * _ref(img))
    inside = gray[mask > 0.5]
    if inside.size < 100:
        inside = gray.ravel()
    cuts = np.quantile(inside, np.linspace(0, 1, n + 1)[1:-1])
    levels = np.digitize(gray, cuts).astype(np.uint8)
    return cv2.medianBlur(levels, 5)


def _ink(img: np.ndarray, thickness: int = 1, c: int = 5) -> np.ndarray:
    ref = _ref(img)
    gray = cv2.medianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 5)
    block = max(3, int(11 * ref) | 1)
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block, c
    )
    lines = (binary == 0).astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(lines, connectivity=8)
    keep = stats[:, cv2.CC_STAT_AREA] >= max(8, int(40 * ref * ref))
    keep[0] = False
    lines = keep[labels].astype(np.uint8)
    if thickness > 1:
        lines = cv2.dilate(lines, np.ones((thickness, thickness), np.uint8))
    return cv2.GaussianBlur(lines.astype(np.float32), (0, 0), 0.6)


def _outline(mask: np.ndarray, width: float) -> np.ndarray:
    width = max(1, int(round(width)))
    solid = (mask > 0.5).astype(np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * width + 1, 2 * width + 1))
    ring = cv2.dilate(solid, kernel) - solid
    return cv2.GaussianBlur(ring.astype(np.float32), (0, 0), 0.8)


def _quantize(img: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    h, w = img.shape[:2]
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32)
    sample = lab[:: max(1, lab.shape[0] // 20000)]
    cv2.setRNGSeed(k * 7 + 1)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.5)
    _, _, centers = cv2.kmeans(sample, k, None, criteria, 2, cv2.KMEANS_PP_CENTERS)
    centers = centers[np.argsort(centers[:, 0])]
    distance = ((lab[:, None, :] - centers[None]) ** 2).sum(-1)
    labels = distance.argmin(1).reshape(h, w)
    bgr = cv2.cvtColor(centers.astype(np.uint8)[None], cv2.COLOR_LAB2BGR)[0]
    return labels, bgr.astype(np.float32) / 255.0


_MASKS: OrderedDict[str, np.ndarray] = OrderedDict()
_MASKS_MAX = 4
_MASKS_LOCK = threading.Lock()


def subject_mask(img: np.ndarray) -> np.ndarray:
    """GrabCut seeded by where the aligned crop puts head and shoulders."""
    key = hashlib.sha1(img.tobytes()).hexdigest() + str(img.shape)
    with _MASKS_LOCK:
        if key in _MASKS:
            _MASKS.move_to_end(key)
            return _MASKS[key]
    h, w = img.shape[:2]
    scale = 256.0 / max(h, w)
    small = cv2.resize(
        img, (max(8, int(w * scale)), max(8, int(h * scale))), interpolation=cv2.INTER_AREA
    )
    sh, sw = small.shape[:2]
    ys, xs = np.ogrid[:sh, :sw]
    cx, cy = sw / 2.0, sh / 2.0
    face_r = sw / (1.0 + PADDING) / 2.0
    head = ((xs - cx) / (face_r * 1.3)) ** 2 + ((ys - cy) / (face_r * 1.7)) ** 2 <= 1
    core = ((xs - cx) / (face_r * 0.7)) ** 2 + ((ys - cy) / (face_r * 0.9)) ** 2 <= 1
    torso = (ys > cy + face_r * 1.1) & (np.abs(xs - cx) < sw * 0.38)
    fallback = (head | torso).astype(np.float32)

    gc = np.full((sh, sw), cv2.GC_PR_BGD, np.uint8)
    gc[head | torso] = cv2.GC_PR_FGD
    gc[core] = cv2.GC_FGD
    gc[:2, :] = cv2.GC_BGD
    gc[:, :2] = cv2.GC_BGD
    gc[:, -2:] = cv2.GC_BGD
    cv2.setRNGSeed(1234)
    try:
        cv2.grabCut(
            small,
            gc,
            None,
            np.zeros((1, 65), np.float64),
            np.zeros((1, 65), np.float64),
            4,
            cv2.GC_INIT_WITH_MASK,
        )
        fg = np.isin(gc, (cv2.GC_FGD, cv2.GC_PR_FGD)).astype(np.uint8)
    except cv2.error:
        fg = fallback.astype(np.uint8)

    count, labels, stats, _ = cv2.connectedComponentsWithStats(fg)
    if count > 1:
        fg = (labels == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    coverage = fg.mean()
    if coverage < 0.06 or coverage > 0.9:
        fg = fallback.astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    mask = cv2.resize(fg.astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)
    mask = np.clip(cv2.GaussianBlur(mask, (0, 0), 1.5 * _ref(img)), 0.0, 1.0)
    mask.setflags(write=False)
    with _MASKS_LOCK:
        _MASKS[key] = mask
        while len(_MASKS) > _MASKS_MAX:
            _MASKS.popitem(last=False)
    return mask


def _halftone(h: int, w: int, coverage: np.ndarray, cell: float) -> np.ndarray:
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = (xx + yy) * 0.70710678
    v = (xx - yy) * 0.70710678
    fu = (u % cell) - cell / 2.0
    fv = (v % cell) - cell / 2.0
    distance = np.sqrt(fu * fu + fv * fv)
    radius = np.sqrt(np.clip(coverage, 0.0, 1.0)) * cell * 0.62
    return np.clip(radius - distance + 0.5, 0.0, 1.0)


def _sparkles(h, w, count, seed, avoid, ref) -> np.ndarray:
    layer = np.zeros((h, w), np.uint8)
    rng = np.random.default_rng(seed + 1)
    placed = tries = 0
    thick = max(1, int(1.6 * ref))
    while placed < count and tries < count * 25:
        tries += 1
        x, y = int(rng.uniform(0, w)), int(rng.uniform(0, h))
        if avoid[y, x] > 0.1:
            continue
        r = rng.uniform(6, 18) * ref
        cv2.line(layer, (int(x - r), y), (int(x + r), y), 255, thick, cv2.LINE_AA)
        cv2.line(layer, (x, int(y - r)), (x, int(y + r)), 255, thick, cv2.LINE_AA)
        cv2.circle(layer, (x, y), max(1, int(r * 0.25)), 255, -1, cv2.LINE_AA)
        placed += 1
    return layer.astype(np.float32) / 255.0


def _pop(out: np.ndarray, pop: float) -> np.ndarray:
    return _saturate(_u(out), 0.85 + 0.17 * float(pop))


def _artist(fn):
    @functools.wraps(fn)
    def render(img, pop=1.0, **params):
        return _pop(fn(img, **params), pop)

    return render


MAX_RAMPS = {
    "cosmic": ["#1d0b5e", "#c2187a", "#ff5e1f", "#ffc21a", "#fff6a8"],
    "sky": ["#0a1f7a", "#1f6fe0", "#19c3d6", "#9cf06b", "#fffb9c"],
    "love": ["#4b0a5c", "#e8178a", "#ff7aa8", "#ffb347", "#fff0c2"],
    "neon": ["#101060", "#7a2cff", "#ff2fb0", "#ff9d00", "#e8ff4a"],
}
RAINBOW = ["#ff2a6d", "#ff8c1a", "#ffe11a", "#3ddc84", "#1fb6ff", "#8f5bff"]


@_artist
def peter_max(img, ramp, backdrop, stripes, line, seed):
    h, w = img.shape[:2]
    ref = _ref(img)
    base = _prep(img, 3)
    mask = subject_mask(img)
    colors = np.stack([_c(x) for x in MAX_RAMPS[ramp]])
    fig = colors[_levels(base, mask, len(colors))]

    phase = float(np.random.default_rng(seed).uniform())
    ys = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    xs = np.linspace(0, 1, w, dtype=np.float32)[None, :]
    rainbow = np.stack([_c(x) for x in RAINBOW])
    n = len(rainbow)
    if backdrop == "rays":
        angle = np.arctan2(ys - 0.42, xs - 0.5)
        band = np.floor((angle + np.pi) / (2 * np.pi) * stripes * 2 + phase * n)
    elif backdrop == "sun":
        radius = np.sqrt((xs - 0.5) ** 2 + (ys - 0.42) ** 2)
        band = np.floor(radius * stripes * 1.6 + phase * n)
    else:
        wave = ys + 0.09 * np.sin(2 * np.pi * (xs * 1.4 + phase))
        wave = wave + 0.05 * np.sin(2 * np.pi * (xs * 3.1 + phase * 2))
        band = np.floor(wave * stripes)
    bg = rainbow[band.astype(np.int64) % n]
    sky = colors[0] * (1.0 - ys[..., None]) + colors[1] * ys[..., None]
    bg = bg * 0.85 + sky * 0.15

    dark = colors[0] * 0.35
    out = _paint(bg, _outline(mask, 11 * ref), colors[-1])
    out = _paint(out, _outline(mask, 3 * ref), dark)
    out = _over(fig, out, mask)
    out = _paint(out, _ink(base, int(line)) * mask, dark)
    halo = cv2.dilate((mask > 0.2).astype(np.uint8), np.ones((int(30 * ref) | 1,) * 2, np.uint8))
    out = _paint(out, _sparkles(h, w, 22, seed, halo, ref), (1.0, 1.0, 1.0))
    return out


def _sample_max(rng, scale):
    return {
        "ramp": rng.choice(list(MAX_RAMPS)),
        "backdrop": rng.choice(["stripes", "rays", "sun"]),
        "stripes": rng.randint(7, 13),
        "line": 1 + int(scale >= 1.0) + int(scale > 1.5),
        "seed": rng.randint(0, 2**31 - 1),
        "pop": scale,
    }


WARHOL = [
    ("#2ec4b6", "#ff8fab", "#ffd60a"),
    ("#ff006e", "#ffbe0b", "#3a86ff"),
    ("#fb5607", "#8ecae6", "#ff006e"),
    ("#ffd60a", "#ff70a6", "#70d6ff"),
    ("#7209b7", "#ffb3c6", "#f72585"),
    ("#06d6a0", "#fff3b0", "#ef476f"),
    ("#3a0ca3", "#4cc9f0", "#f9c74f"),
    ("#ff9f1c", "#cbf3f0", "#2ec4b6"),
]


@_artist
def warhol(img, palettes, offset):
    h, w = img.shape[:2]
    th, tw = h // 2, w // 2
    small = cv2.resize(img, (tw, th), interpolation=cv2.INTER_AREA)
    base = _prep(small, 3)
    mask = subject_mask(small)
    levels = _levels(base, mask, 3)
    ref = _ref(small)
    dark = (levels == 0).astype(np.float32) * mask
    shift = np.float32([[1, 0, offset[0] * ref], [0, 1, offset[1] * ref]])
    dark = cv2.warpAffine(dark, shift, (tw, th), borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    tiles = []
    for index in palettes:
        bg, light, mid = (_c(x) for x in WARHOL[index])
        fig = np.where((levels == 2)[..., None], light, mid)
        tile = _over(fig, _fill(th, tw, bg), mask)
        tiles.append(_paint(tile, dark, BLACK))
    grid = np.vstack([np.hstack(tiles[:2]), np.hstack(tiles[2:])])
    if grid.shape[:2] != (h, w):
        grid = cv2.resize(grid, (w, h), interpolation=cv2.INTER_LINEAR)
    return grid


def _sample_warhol(rng, scale):
    return {
        "palettes": rng.sample(range(len(WARHOL)), 4),
        "offset": [rng.uniform(-6, 6) * scale, rng.uniform(-6, 6) * scale],
        "pop": scale,
    }


DOT_COLORS = {"red": "#e8333a", "pink": "#ff5fa2"}


@_artist
def lichtenstein(img, backdrop, dot_color, cell, line):
    h, w = img.shape[:2]
    ref = _ref(img)
    base = _prep(img, 3)
    mask = subject_mask(img)
    skin = skin_mask(base) * mask
    gray = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    inside = gray[mask > 0.5]
    lo, hi = np.percentile(inside, [5, 95]) if inside.size > 100 else (0.0, 1.0)
    light = np.clip((gray - lo) / (hi - lo + 1e-6), 0.0, 1.0)

    paper = _c("#fffaf0")
    dots = _halftone(h, w, (1.0 - light) * 0.85 + 0.1, cell * ref)
    skin_layer = _paint(_fill(h, w, paper), dots, _c(DOT_COLORS[dot_color]))
    flat = np.where((light < 0.45)[..., None], _c("#1d3f9e"), _c("#ffd31a"))
    fig = skin_layer * skin[..., None] + flat * (1.0 - skin[..., None])

    if backdrop == "blue_dots":
        bg = _paint(_fill(h, w, _c("#3f8efc")), _halftone(h, w, np.full((h, w), 0.3), cell * ref * 2.2), paper)
    elif backdrop == "stripes":
        yy, xx = np.mgrid[0:h, 0:w]
        bands = ((xx + yy) // max(4, int(cell * ref * 2.5))) % 2 == 0
        bg = np.where(bands[..., None], _c("#3f8efc"), paper)
    else:
        bg = _fill(h, w, _c({"yellow": "#ffd31a", "red": "#e8333a"}[backdrop]))

    out = _over(fig, bg, mask)
    out = _paint(out, _ink(base, int(line), c=6) * mask, BLACK)
    return _paint(out, _outline(mask, 4 * ref), BLACK)


def _sample_lichtenstein(rng, scale):
    return {
        "backdrop": rng.choice(["yellow", "red", "blue_dots", "stripes"]),
        "dot_color": rng.choice(list(DOT_COLORS)),
        "cell": rng.uniform(6.5, 9.0),
        "line": 2 + int(scale > 1.4),
        "pop": scale,
    }


HARING = ["#ffde00", "#ff2a1a", "#00a651", "#1e90ff", "#ff3fa4", "#ff7a00", "#8a2be2"]


def _action_lines(mask, marks, seed, ref) -> np.ndarray:
    h, w = mask.shape
    solid = (mask > 0.5).astype(np.uint8)
    contours, _ = cv2.findContours(solid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    layer = np.zeros((h, w), np.uint8)
    if not contours:
        return layer.astype(np.float32)
    points = max(contours, key=cv2.contourArea)[:, 0, :].astype(np.float32)
    count = len(points)
    if count < 20:
        return layer.astype(np.float32)
    rng = np.random.default_rng(seed)
    thick = max(2, int(4 * ref))
    for i in rng.choice(count, size=min(int(marks), count), replace=False):
        x, y = points[i]
        if x < 4 or y < 4 or x > w - 5 or y > h - 5:
            continue
        tx, ty = points[(i + 6) % count] - points[(i - 6) % count]
        nx, ny = ty, -tx
        norm = float(np.hypot(nx, ny))
        if norm < 1e-3:
            continue
        nx, ny = nx / norm, ny / norm
        px, py = int(x + nx * 6), int(y + ny * 6)
        if 0 <= px < w and 0 <= py < h and solid[py, px]:
            nx, ny = -nx, -ny
        gap, length = 12 * ref, rng.uniform(16, 30) * ref
        start = (int(x + nx * gap), int(y + ny * gap))
        end = (int(x + nx * (gap + length)), int(y + ny * (gap + length)))
        cv2.line(layer, start, end, 255, thick, cv2.LINE_AA)
    return layer.astype(np.float32) / 255.0


@_artist
def haring(img, bg, fig, marks, seed):
    h, w = img.shape[:2]
    ref = _ref(img)
    base = _prep(img, 3)
    mask = subject_mask(img)
    color = _c(HARING[fig])
    levels = _levels(base, mask, 2)
    layer = np.where((levels == 0)[..., None], color * 0.72, color)
    out = _over(layer, _fill(h, w, _c(HARING[bg])), mask)
    out = _paint(out, _ink(base, max(2, int(3 * ref)), c=6) * mask, BLACK)
    out = _paint(out, _outline(mask, 6 * ref), BLACK)
    return _paint(out, _action_lines(mask, marks, seed, ref), BLACK)


def _sample_haring(rng, scale):
    bg, fig = rng.sample(range(len(HARING)), 2)
    return {
        "bg": bg,
        "fig": fig,
        "marks": int(rng.randint(26, 44) * min(scale, 1.4)),
        "seed": rng.randint(0, 2**31 - 1),
        "pop": scale,
    }


FAIREY = {
    "hope": ["#112e51", "#d71a21", "#70969f", "#fce4a8"],
    "obey": ["#1a1a1a", "#e2231a", "#8c8c8c", "#f2e6c8"],
    "teal": ["#0b2e33", "#e85d04", "#7fb7be", "#f4e9cd"],
    "violet": ["#1b1035", "#ff2e63", "#8f7ae5", "#ffe8b0"],
}
WORDS = ["DREAM", "VIBE", "ICON", "GROOVE", "HOPE", "LOVE", "FUTURE"]


@_artist
def fairey(img, scheme, word, stripe):
    h, w = img.shape[:2]
    ref = _ref(img)
    base = _prep(img, 3)
    mask = subject_mask(img)
    navy, red, blue, cream = (_c(x) for x in FAIREY[scheme])
    levels = _levels(base, mask, 4)
    period = max(3, int(stripe * ref))
    xx = np.arange(w)[None, :]
    hatch = np.where(((xx % period) < period / 3)[..., None], cream, blue)
    hatch = np.broadcast_to(hatch, (h, w, 3))
    fig = np.empty((h, w, 3), np.float32)
    fig[levels == 0] = navy
    fig[levels == 1] = red
    fig[levels == 2] = hatch[levels == 2]
    fig[levels == 3] = cream

    xs = np.linspace(0, 1, w, dtype=np.float32)[None, :, None]
    bg = np.broadcast_to(np.where(xs < 0.5, blue, red), (h, w, 3)).copy()
    out = _over(fig, bg, mask)
    out = _paint(out, _outline(mask, 3 * ref), navy)

    band = int(0.13 * h)
    out[h - band :] = navy
    text = np.zeros((h, w), np.uint8)
    font = cv2.FONT_HERSHEY_DUPLEX
    thick = max(2, int(band * 0.09))
    (tw, th), _ = cv2.getTextSize(word, font, 1.0, thick)
    size = min(0.8 * w / tw, 0.6 * band / th)
    (tw, th), _ = cv2.getTextSize(word, font, size, thick)
    origin = ((w - tw) // 2, h - (band - th) // 2)
    cv2.putText(text, word, origin, font, size, 255, thick, cv2.LINE_AA)
    return _paint(out, text.astype(np.float32) / 255.0, cream)


def _sample_fairey(rng, scale):
    return {
        "scheme": rng.choice(list(FAIREY)),
        "word": rng.choice(WORDS),
        "stripe": rng.uniform(7, 11),
        "pop": scale,
    }


@_artist
def hockney(img, grid, seed):
    h, w = img.shape[:2]
    ref = _ref(img)
    src = _f(_saturate(img, 1.2))
    canvas = _fill(h, w, _c("#f1ece2"))
    rng = np.random.default_rng(seed)
    cw, ch = w / grid, h / grid
    cells = [(i, j) for i in range(grid) for j in range(grid)]
    border = max(1, int(2 * ref))
    for index in rng.permutation(len(cells)):
        i, j = cells[index]
        cx, cy = (j + 0.5) * cw, (i + 0.5) * ch
        spread = 0.4 + 1.2 * float(np.hypot((cx - w / 2) / w, (cy - h / 2) / h))
        angle = rng.uniform(-6, 6) * spread
        zoom = 1.0 + rng.uniform(-0.04, 0.06)
        ox, oy = rng.uniform(-0.07, 0.07, 2) * cw * spread
        gain = rng.uniform(0.92, 1.1)
        tint = rng.uniform(-0.03, 0.03, 3).astype(np.float32)
        matrix = cv2.getRotationMatrix2D((cx, cy), angle, zoom)
        matrix[0, 2] += ox
        matrix[1, 2] += oy
        warped = cv2.warpAffine(src, matrix, (w, h), borderMode=cv2.BORDER_REFLECT_101)
        hw, hh = 0.58 * cw, 0.58 * ch
        square = np.float32(
            [[cx - hw, cy - hh], [cx + hw, cy - hh], [cx + hw, cy + hh], [cx - hw, cy + hh]]
        )
        poly = (square @ matrix[:, :2].T + matrix[:, 2]).astype(np.int32)

        shadow = np.zeros((h, w), np.uint8)
        cv2.fillPoly(shadow, [poly + np.int32([3 * ref, 4 * ref])], 255, cv2.LINE_AA)
        shadow = cv2.GaussianBlur(shadow.astype(np.float32) / 255.0, (0, 0), 3 * ref)
        canvas *= (1.0 - 0.35 * shadow)[..., None]

        photo = np.zeros((h, w), np.uint8)
        cv2.fillPoly(photo, [poly], 255, cv2.LINE_AA)
        canvas = _paint(canvas, photo.astype(np.float32) / 255.0, np.clip(warped * gain + tint, 0, 1))
        edge = np.zeros((h, w), np.uint8)
        cv2.polylines(edge, [poly], True, 255, border, cv2.LINE_AA)
        canvas = _paint(canvas, edge.astype(np.float32) / 255.0, _c("#fbfbf7"))
    return canvas


def _sample_hockney(rng, scale):
    return {"grid": rng.choice([3, 3, 4]), "seed": rng.randint(0, 2**31 - 1), "pop": scale}


MONDRIAN = {
    "red": "#d40920",
    "blue": "#1356a2",
    "yellow": "#f7d842",
    "white": "#f2efe6",
    "black": "#222222",
}


def _mondrian_rects(w, h, splits, rng, ref):
    rects = [(0, 0, w, h)]
    minimum = 50 * ref
    for _ in range(splits):
        rects.sort(key=lambda r: r[2] * r[3], reverse=True)
        x, y, rw, rh = rects.pop(int(rng.integers(0, min(3, len(rects)))))
        vertical = rw > rh * 0.8 and rng.random() < 0.65
        if vertical and rw > 2 * minimum:
            cut = int(rw * rng.uniform(0.3, 0.7))
            rects += [(x, y, cut, rh), (x + cut, y, rw - cut, rh)]
        elif rh > 2 * minimum:
            cut = int(rh * rng.uniform(0.3, 0.7))
            rects += [(x, y, rw, cut), (x, y + cut, rw, rh - cut)]
        else:
            rects.append((x, y, rw, rh))
    return rects


@_artist
def mondrian(img, seed, splits):
    h, w = img.shape[:2]
    ref = _ref(img)
    rng = np.random.default_rng(seed)
    rects = _mondrian_rects(w, h, splits, rng, ref)
    order = rng.permutation(len(rects))
    names = []
    for rank in range(len(rects)):
        if rank < 3:
            names.append(("red", "blue", "yellow")[rank])
        else:
            names.append(rng.choice(["white"] * 6 + ["red", "blue", "yellow", "black"]))

    bg = _fill(h, w, _c(MONDRIAN["white"]))
    lines = np.zeros((h, w), np.uint8)
    thick = max(4, int(9 * ref))
    tint = np.zeros((h, w, 3), np.float32)
    tint_alpha = np.zeros((h, w), np.float32)
    for rank, index in enumerate(order):
        x, y, rw, rh = rects[index]
        color = _c(MONDRIAN[names[rank]])
        bg[y : y + rh, x : x + rw] = color
        if names[rank] in ("red", "blue", "yellow"):
            tint[y : y + rh, x : x + rw] = color
            tint_alpha[y : y + rh, x : x + rw] = 0.4
        cv2.rectangle(lines, (x, y), (x + rw, y + rh), 255, thick)

    base = _prep(img, 3)
    mask = subject_mask(img)
    labels, centers = _quantize(_saturate(base, 1.25), 5)
    fig = centers[labels]
    keep = face_mask(h, w, 1.05)
    fig = _paint(fig, tint_alpha * (1.0 - keep), tint)
    out = _over(fig, bg, mask)
    out = _paint(out, _ink(base, 1) * mask * 0.7, BLACK)
    out = _paint(out, (lines.astype(np.float32) / 255.0) * (1.0 - keep), _c(MONDRIAN["black"]))
    return _paint(out, _outline(mask, 4 * ref), _c(MONDRIAN["black"]))


def _sample_mondrian(rng, scale):
    return {"seed": rng.randint(0, 2**31 - 1), "splits": rng.randint(6, 10), "pop": scale}


KUSAMA = {
    "red": ("#e60012", "#ffffff"),
    "yellow": ("#ffd700", "#111111"),
    "night": ("#111111", "#ffd700"),
    "pink": ("#ff4fa3", "#ffffff"),
    "white": ("#f7f4ee", "#e60012"),
}


def _dot_field(h, w, spacing, seed) -> np.ndarray:
    layer = np.zeros((h, w), np.uint8)
    rng = np.random.default_rng(seed)
    rows = int(h / (spacing * 0.87)) + 2
    cols = int(w / spacing) + 2
    for r in range(rows):
        for c in range(cols):
            x = c * spacing + (r % 2) * spacing / 2 + rng.uniform(-0.12, 0.12) * spacing
            y = r * spacing * 0.87 + rng.uniform(-0.12, 0.12) * spacing
            radius = spacing * 0.3 * rng.uniform(0.7, 1.15)
            cv2.circle(
                layer, (int(x * 16), int(y * 16)), int(radius * 16), 255, -1, cv2.LINE_AA, shift=4
            )
    return layer.astype(np.float32) / 255.0


@_artist
def kusama(img, scheme, spacing, seed):
    h, w = img.shape[:2]
    ref = _ref(img)
    bg_color, dot_color = (_c(x) for x in KUSAMA[scheme])
    base = _prep(img, 2)
    mask = subject_mask(img)
    fig = _f(_saturate(base, 1.35))
    dots = _dot_field(h, w, spacing * ref, seed)
    keep = np.maximum(face_mask(h, w, 1.05), skin_mask(base) * face_mask(h, w, 1.6))
    fig = _paint(fig, dots * 0.85 * (1.0 - keep), dot_color)
    out = _over(fig, _paint(_fill(h, w, bg_color), dots, dot_color), mask)
    return _paint(out, _outline(mask, 3 * ref), dot_color)


def _sample_kusama(rng, scale):
    return {
        "scheme": rng.choice(list(KUSAMA)),
        "spacing": rng.uniform(14, 24),
        "seed": rng.randint(0, 2**31 - 1),
        "pop": scale,
    }


def _gold_mosaic(h, w, seed, density, ref) -> np.ndarray:
    rng = np.random.default_rng(seed)
    low = cv2.resize(
        rng.random((h // 24 + 2, w // 24 + 2)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC
    )
    fine = rng.random((h, w)).astype(np.float32)
    t = np.clip(0.55 * low + 0.25 * fine + 0.2, 0.0, 1.0)[..., None]
    gold = _c("#7a5a16") * (1.0 - t) + _c("#f4d26a") * t
    canvas = _u(gold)
    bright = (106, 210, 244)
    tiles = [(20, 20, 20), (210, 210, 210), (40, 30, 140), (110, 120, 40)]
    count = int(density * w * h / (48 * ref) ** 2)
    thin = max(1, int(1.5 * ref))
    for _ in range(count):
        kind = rng.random()
        x, y = int(rng.integers(0, w)), int(rng.integers(0, h))
        s = rng.uniform(5, 16) * ref
        if kind < 0.45:
            color = tiles[int(rng.integers(0, len(tiles)))]
            cv2.rectangle(canvas, (int(x - s), int(y - s)), (int(x + s), int(y + s)), color, -1)
            inner = s * 0.45
            cv2.rectangle(canvas, (int(x - inner), int(y - inner)), (int(x + inner), int(y + inner)), bright, -1)
        elif kind < 0.8:
            for radius, color in ((1.6, (20, 20, 20)), (1.1, bright), (0.6, (210, 210, 210))):
                cv2.circle(canvas, (x, y), max(1, int(s * radius)), color, -1, cv2.LINE_AA)
        else:
            theta = np.linspace(0, 4 * np.pi, 40)
            a = s * 0.12
            pts = np.stack([x + a * theta * np.cos(theta), y + a * theta * np.sin(theta)], -1)
            cv2.polylines(canvas, [pts.astype(np.int32)], False, (20, 20, 20), thin, cv2.LINE_AA)
    return _f(canvas)


@_artist
def klimt(img, seed, density):
    h, w = img.shape[:2]
    ref = _ref(img)
    base = _prep(img, 1)
    mask = subject_mask(img)
    x = _f(base)
    tint = np.array([0.40, 0.54, 0.64], np.float32)
    warm = x * 0.6 + ((1 - 2 * tint) * x * x + 2 * tint * x) * 0.4
    mosaic = _gold_mosaic(h, w, seed, density, ref)
    lum = (x * LUMA).sum(-1, keepdims=True)
    keep = np.maximum(face_mask(h, w, 1.1), skin_mask(base) * face_mask(h, w, 1.5))
    robe = (mask * (1.0 - keep))[..., None] * 0.75
    fig = warm * (1.0 - robe) + np.clip(mosaic * (0.45 + 0.8 * lum), 0, 1) * robe
    out = _over(fig, mosaic * 0.82, mask)
    glow = cv2.GaussianBlur(out, (0, 0), 10 * ref)
    return out * 0.8 + (1.0 - (1.0 - out) * (1.0 - glow)) * 0.2


def _sample_klimt(rng, scale):
    return {"seed": rng.randint(0, 2**31 - 1), "density": rng.uniform(0.8, 1.3), "pop": scale}


def _wall(h, w, kind, seed, ref) -> np.ndarray:
    rng = np.random.default_rng(seed)
    low = cv2.resize(
        rng.random((h // 40 + 2, w // 40 + 2)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC
    )
    fine = rng.random((h, w)).astype(np.float32)
    if kind == "brick":
        canvas = np.full((h, w, 3), (189, 200, 207), np.uint8)
        bh = max(8, int(h / 15))
        bw = int(bh * 2.3)
        gap = max(2, int(3 * ref))
        base = np.array([134, 148, 163], np.float32)
        for row, y in enumerate(range(0, h, bh)):
            offset = bw // 2 if row % 2 else 0
            for x in range(-offset, w, bw):
                color = tuple(int(v) for v in np.clip(base * rng.uniform(0.85, 1.08), 0, 255))
                cv2.rectangle(canvas, (x + gap // 2, y + gap // 2), (x + bw - gap, y + bh - gap), color, -1)
        wall = _f(canvas) * (0.92 + 0.08 * fine)[..., None]
        return wall * 0.7 + 0.3 * 0.82
    t = (0.82 + 0.1 * low + 0.06 * fine)[..., None]
    return _c("#c9c5bd") * t


def _drips(black, keep, seed, ref) -> np.ndarray:
    h, w = black.shape
    solid = (black > 0.5).astype(np.uint8)
    edge = solid.copy()
    edge[:-1] &= (solid[1:] == 0).astype(np.uint8)
    edge[-1] = 0
    edge[keep > 0.3] = 0
    ys, xs = np.nonzero(edge)
    layer = np.zeros((h, w), np.uint8)
    if len(xs) == 0:
        return layer.astype(np.float32)
    rng = np.random.default_rng(seed)
    for i in rng.choice(len(xs), size=min(14, len(xs)), replace=False):
        x, y = int(xs[i]), int(ys[i])
        length = rng.uniform(15, 60) * ref
        thick = max(1, int(rng.uniform(1.5, 3.0) * ref))
        end = (x, int(min(h - 1, y + length)))
        cv2.line(layer, (x, y), end, 255, thick, cv2.LINE_AA)
        cv2.circle(layer, end, max(1, int(thick * 0.9)), 255, -1, cv2.LINE_AA)
    return layer.astype(np.float32) / 255.0


def _balloon(h, w, side, ref):
    cx = w * (0.82 if side == "right" else 0.18)
    cy = h * 0.17
    k = w * 0.075 / 17.0
    t = np.linspace(0, 2 * np.pi, 120)
    x = 16 * np.sin(t) ** 3
    y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
    pts = np.stack([cx + x * k, cy - y * k], -1).astype(np.int32)
    heart = np.zeros((h, w), np.uint8)
    cv2.fillPoly(heart, [pts], 255, cv2.LINE_AA)
    direction = 1 if side == "right" else -1
    start = np.array([cx, cy + 17 * k])
    end = np.array([cx - direction * w * 0.07, h * 0.55])
    control = np.array([cx + direction * w * 0.05, (start[1] + end[1]) / 2])
    s = np.linspace(0, 1, 40)[:, None]
    curve = ((1 - s) ** 2) * start + 2 * (1 - s) * s * control + (s ** 2) * end
    string = np.zeros((h, w), np.uint8)
    cv2.polylines(string, [curve.astype(np.int32)], False, 255, max(1, int(1.5 * ref)), cv2.LINE_AA)
    shine = np.zeros((h, w), np.uint8)
    cv2.ellipse(
        shine, (int(cx - 6 * k), int(cy - 3 * k)), (max(1, int(3 * k)), max(1, int(1.6 * k))),
        -35, 0, 360, 255, -1, cv2.LINE_AA,
    )
    return heart, string, shine


@_artist
def banksy(img, wall, side, seed):
    h, w = img.shape[:2]
    ref = _ref(img)
    base = _prep(img, 3)
    mask = subject_mask(img)
    out = _wall(h, w, wall, seed, ref)
    levels = _levels(base, mask, 3)
    black = (levels == 0).astype(np.float32) * mask
    gray = (levels == 1).astype(np.float32) * mask
    ink = _c("#141414")
    out = _paint(out, cv2.GaussianBlur(black, (0, 0), 3 * ref) * 0.35, ink)
    out = _paint(out, gray * 0.92, _c("#5e5e5e"))
    out = _paint(out, black * 0.96, ink)
    out = _paint(out, _drips(black, face_mask(h, w, 0.9), seed, ref), ink)
    heart, string, shine = (layer.astype(np.float32) / 255.0 for layer in _balloon(h, w, side, ref))
    out = _paint(out, string, ink)
    out = _paint(out, heart, _c("#d6001c"))
    return _paint(out, shine * 0.7, (1.0, 1.0, 1.0))


def _sample_banksy(rng, scale):
    return {
        "wall": rng.choice(["concrete", "brick"]),
        "side": rng.choice(["left", "right"]),
        "seed": rng.randint(0, 2**31 - 1),
        "pop": scale,
    }


ARTISTS: dict[str, Artist] = {
    "peter_max": Artist("Peter Max", peter_max, _sample_max),
    "warhol": Artist("Andy Warhol", warhol, _sample_warhol),
    "lichtenstein": Artist("Roy Lichtenstein", lichtenstein, _sample_lichtenstein),
    "haring": Artist("Keith Haring", haring, _sample_haring),
    "fairey": Artist("Shepard Fairey", fairey, _sample_fairey),
    "hockney": Artist("David Hockney", hockney, _sample_hockney),
    "mondrian": Artist("Piet Mondrian", mondrian, _sample_mondrian),
    "kusama": Artist("Yayoi Kusama", kusama, _sample_kusama),
    "klimt": Artist("Gustav Klimt", klimt, _sample_klimt),
    "banksy": Artist("Banksy", banksy, _sample_banksy),
}
