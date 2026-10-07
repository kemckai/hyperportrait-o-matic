"""Face-aligned hyperportrait variants with a reproducible transform recipe."""

from __future__ import annotations

import os
import random
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

from app.artists import subject_mask
from app.catalog import ARTISTS
from app.framing import PADDING
from app.framing import face_mask as _face_mask
from app.framing import skin_mask as _skin_mask

_FACE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
_EYE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

LUMA = np.array([0.114, 0.587, 0.299], dtype=np.float32)

INT_PARAMS = {"levels", "num_bands", "max_shift"}
NEEDS_SEED = {"elastic_warp", "glitch_shift", "channel_glitch", "perspective", "grain"}

FACE_CARE = ["skin_smooth", "clarity"]
STATEMENT = ["backdrop_color", "soft_glow", "light_leak", "bokeh_background"]
ATMOSPHERE = ["tone_curve", "vignette", "grain"]
FLATTER_ORDER = [
    "skin_smooth",
    "clarity",
    "tone_curve",
    "color_grade",
    "backdrop_color",
    "bokeh_background",
    "soft_glow",
    "light_leak",
    "vignette",
    "grain",
]
SCALED = {"amount", "contrast", "strength", "sigma"}

# Shadow and highlight tints in BGR for a soft-light blend; 0.5 is neutral.
PALETTES = {
    "golden_hour": ((0.28, 0.36, 0.46), (0.36, 0.58, 0.70)),
    "teal_orange": ((0.66, 0.54, 0.30), (0.36, 0.55, 0.68)),
    "rose": ((0.54, 0.34, 0.50), (0.52, 0.48, 0.66)),
    "cool_film": ((0.64, 0.50, 0.36), (0.50, 0.55, 0.56)),
    "neon_night": ((0.72, 0.30, 0.58), (0.60, 0.56, 0.52)),
    "bw_portrait": ((0.46, 0.50, 0.54), (0.46, 0.50, 0.54)),
}
BACKDROPS = {
    "electric_blue": (1.0, 0.45, 0.1),
    "magenta": (0.85, 0.2, 0.95),
    "teal": (0.75, 0.7, 0.1),
    "sunset": (0.2, 0.45, 1.0),
    "violet": (0.95, 0.3, 0.55),
}
LEAK_TINTS = {
    "amber": (0.25, 0.65, 1.0),
    "peach": (0.6, 0.72, 1.0),
    "rose": (0.7, 0.55, 1.0),
    "lilac": (1.0, 0.65, 0.85),
}
COLOR = ["hue_shift", "saturation_boost", "channel_swap", "posterize"]
WARP = ["elastic_warp", "swirl", "perspective"]
GLITCH = ["glitch_shift", "channel_glitch"]
STYLE = ["pencil_sketch"]

CLAMPS: dict[str, dict[str, tuple]] = {
    "hue_shift": {"degrees": (-90, 90)},
    "saturation_boost": {"factor": (0.05, 4.0)},
    "posterize": {"levels": (2, 16)},
    "elastic_warp": {"alpha": (1.0, 120.0), "sigma": (0.5, 30.0)},
    "swirl": {"strength": (-8.0, 8.0), "radius": (20.0, 800.0)},
    "perspective": {"jitter": (0.0, 0.25)},
    "glitch_shift": {"num_bands": (1, 24), "max_shift": (1, 80)},
    "channel_glitch": {"max_shift": (0, 40)},
    "skin_smooth": {"amount": (0.0, 0.85)},
    "clarity": {"amount": (0.0, 1.0)},
    "tone_curve": {"contrast": (0.0, 0.6)},
    "color_grade": {"amount": (0.0, 0.95)},
    "backdrop_color": {"amount": (0.0, 0.9)},
    "bokeh_background": {"sigma": (1.0, 14.0)},
    "soft_glow": {"amount": (0.0, 0.55)},
    "light_leak": {"amount": (0.0, 0.5)},
    "vignette": {"strength": (0.0, 0.55)},
    "grain": {"amount": (0.0, 0.05)},
}


def hue_shift(img, degrees):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv[..., 0] = (hsv[..., 0].astype(np.int16) + int(round(degrees))) % 180
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def saturation_boost(img, factor):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * float(factor), 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def channel_swap(img, order):
    index = [int(channel) for channel in order]
    return np.ascontiguousarray(img[..., index])


def posterize(img, levels):
    levels = max(int(levels), 2)
    step = 256.0 / levels
    return np.clip(np.floor(img.astype(np.float32) / step) * step, 0, 255).astype(np.uint8)


def elastic_warp(img, alpha, sigma, seed):
    h, w = img.shape[:2]
    gen = np.random.default_rng(int(seed))
    ref = min(h, w) / 512.0
    dx = cv2.GaussianBlur(gen.uniform(-1, 1, (h, w)).astype(np.float32), (0, 0), float(sigma))
    dy = cv2.GaussianBlur(gen.uniform(-1, 1, (h, w)).astype(np.float32), (0, 0), float(sigma))
    weight = _center_weight(h, w)
    dx = dx * float(alpha) * ref * weight
    dy = dy * float(alpha) * ref * weight
    xs, ys = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    return cv2.remap(
        img,
        xs + dx,
        ys + dy,
        cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT_101,
    )


def swirl(img, strength, radius):
    h, w = img.shape[:2]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    ref = min(h, w) / 512.0
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    dx, dy = xs - cx, ys - cy
    dist = np.sqrt(dx ** 2 + dy ** 2)
    theta = np.arctan2(dy, dx) + float(strength) * np.exp(-dist / (float(radius) * ref))
    warped = cv2.remap(
        img,
        (cx + dist * np.cos(theta)).astype(np.float32),
        (cy + dist * np.sin(theta)).astype(np.float32),
        cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT_101,
    )
    return _blend(img, warped, _center_weight(h, w))


def perspective_warp(img, jitter, seed):
    h, w = img.shape[:2]
    gen = np.random.default_rng(int(seed))
    span = float(jitter) * min(h, w)
    src = np.float32([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]])
    dst = src + gen.uniform(-span, span, src.shape).astype(np.float32)
    matrix = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(
        img, matrix, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101
    )
    return _blend(img, warped, _center_weight(h, w))


def glitch_shift(img, num_bands, max_shift, seed):
    rng = random.Random(int(seed))
    out = img.copy()
    h, w = img.shape[:2]
    ref = min(h, w) / 512.0
    y_lo = int(h * 0.12)
    y_hi = max(y_lo + 1, int(h * 0.88))
    band_cap = max(2, h // 12)
    shift_cap = max(1, int(round(int(max_shift) * ref)))
    for _ in range(int(num_bands)):
        y = rng.randint(y_lo, y_hi - 1)
        band_h = rng.randint(2, band_cap)
        shift = rng.randint(-shift_cap, shift_cap)
        y2 = min(h, y + band_h)
        out[y:y2] = np.roll(out[y:y2], shift, axis=1)
    return out


def channel_shift_glitch(img, max_shift, seed):
    rng = random.Random(int(seed))
    out = img.copy()
    h, w = img.shape[:2]
    ref = min(h, w) / 512.0
    shift_cap = max(0, int(round(int(max_shift) * ref)))
    for channel in range(3):
        shift = 0 if shift_cap == 0 else rng.randint(-shift_cap, shift_cap)
        out[..., channel] = np.roll(out[..., channel], shift, axis=1)
    return out


def pencil_sketch(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(255 - gray, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - blurred, scale=256)
    sketch = np.clip(sketch, 0, 255).astype(np.uint8)
    return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)


def skin_smooth(img, amount, sigma_color):
    """Bilateral smoothing limited to skin inside the face; eyes and brows stay sharp."""
    h, w = img.shape[:2]
    ref = min(h, w) / 512.0
    diameter = max(5, int(9 * ref) | 1)
    smooth = _f(cv2.bilateralFilter(img, diameter, float(sigma_color), diameter * 1.5))
    x = _f(img)
    weight = (float(amount) * _skin_mask(img) * _face_mask(h, w, 1.15))[..., None]
    out = x * (1.0 - weight) + smooth * weight
    texture = x - cv2.GaussianBlur(x, (0, 0), max(0.8, 1.0 * ref))
    return _u(out + texture * 0.3 * weight)


def clarity(img, amount):
    """Local sharpening on eyes, brows, and lips rather than skin."""
    h, w = img.shape[:2]
    ref = min(h, w) / 512.0
    x = _f(img)
    detail = x - cv2.GaussianBlur(x, (0, 0), max(1.0, 2.0 * ref))
    features = _face_mask(h, w, 1.1) * (1.0 - 0.75 * _skin_mask(img))
    return _u(x + detail * float(amount) * (0.25 + 0.75 * features)[..., None])


def tone_curve(img, contrast, lift, warmth):
    x = _f(img)
    y = x - float(contrast) * np.sin(2 * np.pi * x) / (2 * np.pi)
    y = float(lift) + (1.0 - float(lift)) * y
    y[..., 2] *= 1.0 + float(warmth)
    y[..., 0] *= 1.0 - float(warmth)
    return _u(y)


def color_grade(img, palette, amount):
    """Split-tone grade, eased off on the face so skin stays natural."""
    h, w = img.shape[:2]
    x = _f(img)
    lum = (x * LUMA).sum(axis=-1, keepdims=True)
    shadow, highlight = (np.array(c, dtype=np.float32) for c in PALETTES[palette])
    base = np.repeat(lum, 3, axis=-1) if palette == "bw_portrait" else x
    tint = shadow * (1.0 - lum) + highlight * lum
    graded = (1.0 - 2.0 * tint) * base * base + 2.0 * tint * base
    if palette == "bw_portrait":
        weight = np.full((h, w, 1), float(amount), dtype=np.float32)
    else:
        weight = (float(amount) * (1.0 - 0.4 * _face_mask(h, w)))[..., None]
    return _u(x * (1.0 - weight) + graded * weight)


def backdrop_color(img, color, amount):
    """Duotone the backdrop in a bold color while skin and face keep their tones."""
    h, w = img.shape[:2]
    x = _f(img)
    lum = (x * LUMA).sum(axis=-1, keepdims=True)
    tone = np.array(BACKDROPS[color], dtype=np.float32)
    duo = np.clip(lum * 1.15, 0.0, 1.0) * tone + (1.0 - tone) * lum * 0.25
    protect = np.maximum(_face_mask(h, w, 1.3), _skin_mask(img) * _face_mask(h, w, 1.7))
    weight = (float(amount) * (1.0 - protect))[..., None]
    return _u(x * (1.0 - weight) + duo * weight)


def bokeh_background(img, sigma):
    h, w = img.shape[:2]
    ref = min(h, w) / 512.0
    x = _f(img)
    blurred = cv2.GaussianBlur(x, (0, 0), float(sigma) * ref)
    keep = _face_mask(h, w, 1.75)[..., None]
    return _u(blurred * (1.0 - keep) + x * keep)


def soft_glow(img, radius, amount):
    h, w = img.shape[:2]
    ref = min(h, w) / 512.0
    x = _f(img)
    blur = cv2.GaussianBlur(x, (0, 0), float(radius) * ref)
    screen = 1.0 - (1.0 - x) * (1.0 - blur)
    return _u(x * (1.0 - float(amount)) + screen * float(amount))


def light_leak(img, corner, tint, amount):
    h, w = img.shape[:2]
    x = _f(img)
    cx = 0.0 if corner in ("tl", "bl") else 1.0
    cy = 0.0 if corner in ("tl", "tr") else 1.0
    ys = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
    xs = np.linspace(0.0, 1.0, w, dtype=np.float32)[None, :]
    glow = np.exp(-((xs - cx) ** 2 + (ys - cy) ** 2) / (2 * 0.38 ** 2))
    overlay = np.array(LEAK_TINTS[tint], dtype=np.float32) * (glow * float(amount))[..., None]
    return _u(1.0 - (1.0 - x) * (1.0 - overlay))


def vignette(img, strength):
    h, w = img.shape[:2]
    ys = np.linspace(-1.0, 1.0, h, dtype=np.float32)[:, None]
    xs = np.linspace(-1.0, 1.0, w, dtype=np.float32)[None, :]
    r = np.sqrt(xs ** 2 + ys ** 2) / np.sqrt(2.0)
    t = np.clip((r - 0.35) / 0.65, 0.0, 1.0)
    t = t * t * (3.0 - 2.0 * t)
    return _u(_f(img) * (1.0 - float(strength) * t)[..., None])


def grain(img, amount, seed):
    h, w = img.shape[:2]
    noise = np.random.default_rng(int(seed)).normal(0.0, float(amount), (h, w, 1))
    return _u(_f(img) + noise.astype(np.float32))


TRANSFORMS = {
    "hue_shift": (hue_shift, {"degrees": (-30, 30)}),
    "saturation_boost": (saturation_boost, {"factor": (0.6, 1.8)}),
    "channel_swap": (channel_swap, {"order": [[0, 1, 2], [2, 1, 0], [1, 0, 2], [2, 0, 1]]}),
    "posterize": (posterize, {"levels": (3, 8)}),
    "elastic_warp": (elastic_warp, {"alpha": (10.0, 50.0), "sigma": (4.0, 12.0)}),
    "swirl": (swirl, {"strength": (-3.0, 3.0), "radius": (100.0, 300.0)}),
    "perspective": (perspective_warp, {"jitter": (0.02, 0.10)}),
    "glitch_shift": (glitch_shift, {"num_bands": (2, 12), "max_shift": (5, 30)}),
    "channel_glitch": (channel_shift_glitch, {"max_shift": (3, 15)}),
    "pencil_sketch": (pencil_sketch, {}),
    "skin_smooth": (skin_smooth, {"amount": (0.35, 0.6), "sigma_color": (25.0, 45.0)}),
    "clarity": (clarity, {"amount": (0.3, 0.6)}),
    "tone_curve": (
        tone_curve,
        {"contrast": (0.15, 0.35), "lift": (0.0, 0.04), "warmth": (-0.01, 0.05)},
    ),
    "color_grade": (color_grade, {"palette": list(PALETTES), "amount": (0.5, 0.75)}),
    "backdrop_color": (backdrop_color, {"color": list(BACKDROPS), "amount": (0.45, 0.7)}),
    "bokeh_background": (bokeh_background, {"sigma": (3.0, 7.0)}),
    "soft_glow": (soft_glow, {"radius": (8.0, 16.0), "amount": (0.2, 0.35)}),
    "light_leak": (
        light_leak,
        {"corner": ["tl", "tr", "bl", "br"], "tint": list(LEAK_TINTS), "amount": (0.25, 0.4)},
    ),
    "vignette": (vignette, {"strength": (0.2, 0.35)}),
    "grain": (grain, {"amount": (0.012, 0.025)}),
}

TRANSFORMS.update({name: (artist.render, None) for name, artist in ARTISTS.items()})

STYLES = ("mix", *ARTISTS, "flattering", "glitch")
_WORKERS = max(1, min(4, (os.cpu_count() or 2) - 1))


def apply_random_chain(
    img, n_transforms=3, scale=1.0, seed=0, style="flattering", palette=None
):
    """Apply a balanced chain. The recipe alone replays the same image."""
    rng = random.Random(int(seed))
    if style in ARTISTS:
        params = ARTISTS[style].sample(rng, float(scale))
        out = ARTISTS[style].render(img, **params)
        return _finalize(out), [{"transform": style, "params": params}]
    if style == "flattering":
        names = _choose_flattering(int(n_transforms), rng)
        sample = _sample_scaled
    else:
        names = _choose_chain(int(n_transforms), rng)
        sample = _sample_params
    recipe = []
    out = img
    for name in names:
        fn, spec = TRANSFORMS[name]
        params = sample(name, spec, float(scale), rng)
        if name == "color_grade" and palette is not None:
            params["palette"] = palette
        if name in NEEDS_SEED:
            params["seed"] = rng.randint(0, 2**31 - 1)
        out = fn(out, **params)
        recipe.append({"transform": name, "params": params})
    return _finalize(out), recipe


def replay(img, recipe):
    out = img
    for step in recipe:
        fn = TRANSFORMS[step["transform"]][0]
        out = fn(out, **step["params"])
    return _finalize(out)


def generate_hyperportraits(
    src_path,
    n_variants=3,
    n_transforms=3,
    intensity=1.0,
    seed=None,
    out_dir=".",
    style="flattering",
):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    bgr = _limit(_load_bgr(src_path), 1600)
    aligned, face = detect_and_align(bgr)
    aligned = _limit(aligned, 768)
    if min(aligned.shape[:2]) < 32:
        raise ValueError("Image is too small")

    base = int(seed) if seed is not None else random.SystemRandom().randrange(1, 2**31)
    if not cv2.imwrite(str(out_dir / "source.png"), aligned):
        raise ValueError("Could not write aligned face")

    shuffler = random.Random(base)
    palettes = list(PALETTES)
    shuffler.shuffle(palettes)
    artists = [name for name in ARTISTS if name != "peter_max"]
    shuffler.shuffle(artists)
    artists.insert(0, "peter_max")
    if style == "mix" or style in ARTISTS:
        subject_mask(aligned)

    def render(index: int) -> dict:
        variant_seed = base + index
        variant_style = artists[index % len(artists)] if style == "mix" else style
        variant, recipe = apply_random_chain(
            aligned,
            n_transforms=n_transforms,
            scale=intensity,
            seed=variant_seed,
            style=variant_style,
            palette=palettes[index % len(palettes)],
        )
        variant_id = f"v{index}"
        if not cv2.imwrite(str(out_dir / f"{variant_id}.png"), variant):
            raise ValueError("Could not write variant")
        return {"id": variant_id, "style": variant_style, "recipe": recipe, "seed": variant_seed}

    count = int(n_variants)
    workers = min(count, _WORKERS)
    if workers <= 1:
        variants = [render(index) for index in range(count)]
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            variants = list(pool.map(render, range(count)))
    return {"base_seed": base, "face": face, "style": style, "variants": variants}


def detect_and_align(bgr: np.ndarray, padding: float = PADDING) -> tuple[np.ndarray, dict]:
    """Level the eyes and return a square crop centered on the largest face."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    faces = _FACE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(48, 48))
    height, width = bgr.shape[:2]
    if len(faces) == 0:
        side = min(height, width)
        return _crop_square(bgr, width / 2, height / 2, side), {
            "detected": False,
            "box": None,
            "angle": 0.0,
        }

    x, y, fw, fh = max(faces, key=lambda face: int(face[2]) * int(face[3]))
    angle = _eye_angle(gray, int(x), int(y), int(fw), int(fh))
    rotated, center_x, center_y = _rotate_around(
        bgr, x + fw / 2.0, y + fh / 2.0, angle
    )
    side = max(32, int(round(max(fw, fh) * (1.0 + padding))))
    crop = _crop_square(rotated, center_x, center_y, side)
    return crop, {
        "detected": True,
        "box": [int(x), int(y), int(fw), int(fh)],
        "angle": float(angle),
    }


def _choose_chain(n_transforms: int, rng: random.Random) -> list[str]:
    """One color op, at most one heavy warp, sketch pinned to the end."""
    count = min(6, max(1, n_transforms))
    chosen = [rng.choice(COLOR)]
    if count >= 2:
        chosen.append(rng.choice(WARP))
    extras = COLOR + GLITCH + STYLE
    guard = 0
    while len(chosen) < count and guard < 40:
        guard += 1
        pick = rng.choice(extras)
        if pick in WARP:
            continue
        if pick in chosen and pick not in COLOR:
            continue
        chosen.append(pick)
    body = [name for name in chosen if name != "pencil_sketch"]
    rng.shuffle(body)
    if "pencil_sketch" in chosen:
        body.append("pencil_sketch")
    return body


def _choose_flattering(n_transforms: int, rng: random.Random) -> list[str]:
    """A grade and a statement effect lead; face care and atmosphere fill the rest."""
    count = min(6, max(1, n_transforms))
    statement = STATEMENT[:]
    rng.shuffle(statement)
    care = FACE_CARE[:]
    rng.shuffle(care)
    chosen = ["color_grade"]
    if count >= 2:
        chosen.append(statement.pop())
    if count >= 3:
        chosen.append(care.pop())
    pool = statement + care + ATMOSPHERE
    rng.shuffle(pool)
    chosen.extend(pool[: count - len(chosen)])
    return sorted(chosen, key=FLATTER_ORDER.index)


def _sample_scaled(name: str, spec: dict, scale: float, rng: random.Random) -> dict:
    """Intensity multiplies effect strength, clamped so faces stay recognizable."""
    params = {}
    for key, value in spec.items():
        if isinstance(value, list):
            params[key] = rng.choice(value)
            continue
        number = rng.uniform(*value)
        if key in SCALED:
            number *= scale
            if key in CLAMPS.get(name, {}):
                lo, hi = CLAMPS[name][key]
                number = min(max(number, lo), hi)
        params[key] = float(number)
    return params


def _sample_params(name: str, spec: dict, scale: float, rng: random.Random) -> dict:
    params = {}
    for key, value in spec.items():
        if isinstance(value, list):
            picked = rng.choice(value)
            params[key] = list(picked) if isinstance(picked, (list, tuple)) else picked
            continue
        lo, hi = value
        mid = (lo + hi) / 2
        lo2 = mid - (mid - lo) * scale
        hi2 = mid + (hi - mid) * scale
        if key in CLAMPS.get(name, {}):
            clo, chi = CLAMPS[name][key]
            lo2, hi2 = max(lo2, clo), min(hi2, chi)
        if lo2 > hi2:
            lo2, hi2 = hi2, lo2
        if key in INT_PARAMS:
            lo_i, hi_i = int(round(lo2)), int(round(hi2))
            if lo_i > hi_i:
                lo_i, hi_i = hi_i, lo_i
            params[key] = rng.randint(lo_i, hi_i) if lo_i != hi_i else lo_i
        else:
            params[key] = float(rng.uniform(lo2, hi2))
    return params


def _center_weight(height: int, width: int) -> np.ndarray:
    ys = np.linspace(-1.0, 1.0, height, dtype=np.float32)[:, None]
    xs = np.linspace(-1.0, 1.0, width, dtype=np.float32)[None, :]
    return np.exp(-(xs ** 2 + ys ** 2) / (2 * 0.55 ** 2)).astype(np.float32)


def _f(img: np.ndarray) -> np.ndarray:
    return img.astype(np.float32) / 255.0


def _u(x: np.ndarray) -> np.ndarray:
    return np.clip(np.round(x * 255.0), 0, 255).astype(np.uint8)


def _blend(original: np.ndarray, warped: np.ndarray, weight: np.ndarray) -> np.ndarray:
    mask = weight[..., None]
    mixed = warped.astype(np.float32) * mask + original.astype(np.float32) * (1.0 - mask)
    return np.clip(np.round(mixed), 0, 255).astype(np.uint8)


def _finalize(img: np.ndarray) -> np.ndarray:
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return np.clip(img, 0, 255).astype(np.uint8)


def _limit(bgr: np.ndarray, target: int) -> np.ndarray:
    height, width = bgr.shape[:2]
    longest = max(height, width)
    if longest <= target:
        return bgr
    scale = target / longest
    return cv2.resize(
        bgr,
        (max(1, int(width * scale)), max(1, int(height * scale))),
        interpolation=cv2.INTER_AREA,
    )


def _load_bgr(path) -> np.ndarray:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        rgb = np.asarray(image)
    if rgb.size == 0:
        raise ValueError("Could not read image")
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def _eye_angle(gray: np.ndarray, x: int, y: int, fw: int, fh: int) -> float:
    roi = gray[y : y + fh, x : x + fw]
    eyes = _EYE.detectMultiScale(roi, scaleFactor=1.1, minNeighbors=6, minSize=(12, 12))
    upper = []
    for ex, ey, ew, eh in eyes:
        if ey + eh / 2 > fh * 0.62:
            continue
        upper.append((ex + ew / 2, ey + eh / 2))
    if len(upper) < 2:
        return 0.0
    upper.sort(key=lambda point: point[0])
    left, right = upper[0], upper[-1]
    dx = right[0] - left[0]
    if dx < fw * 0.15:
        return 0.0
    angle = float(np.degrees(np.arctan2(right[1] - left[1], dx)))
    if abs(angle) > 25:
        return 0.0
    return angle


def _rotate_around(bgr, cx, cy, angle):
    height, width = bgr.shape[:2]
    matrix = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
    cos, sin = abs(matrix[0, 0]), abs(matrix[0, 1])
    new_w = int(height * sin + width * cos)
    new_h = int(height * cos + width * sin)
    matrix[0, 2] += new_w / 2 - cx
    matrix[1, 2] += new_h / 2 - cy
    rotated = cv2.warpAffine(
        bgr,
        matrix,
        (new_w, new_h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT_101,
    )
    return rotated, new_w / 2, new_h / 2


def _crop_square(img, cx, cy, side: int) -> np.ndarray:
    height, width = img.shape[:2]
    half = side / 2
    x0 = int(round(cx - half))
    y0 = int(round(cy - half))
    x1 = x0 + side
    y1 = y0 + side
    pad_l, pad_t = max(0, -x0), max(0, -y0)
    pad_r, pad_b = max(0, x1 - width), max(0, y1 - height)
    if pad_l or pad_t or pad_r or pad_b:
        img = cv2.copyMakeBorder(
            img, pad_t, pad_b, pad_l, pad_r, borderType=cv2.BORDER_REFLECT_101
        )
        x0 += pad_l
        y0 += pad_t
    return img[y0 : y0 + side, x0 : x0 + side]
