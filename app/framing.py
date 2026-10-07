"""Where the aligned crop places the face, plus a skin-tone mask."""

from __future__ import annotations

import cv2
import numpy as np

PADDING = 1.0


def face_mask(height: int, width: int, grow: float = 1.0) -> np.ndarray:
    """Feathered ellipse where the aligned crop places the face."""
    ys = np.arange(height, dtype=np.float32)[:, None]
    xs = np.arange(width, dtype=np.float32)[None, :]
    rx = width / (1.0 + PADDING) / 2.0 * 0.95 * grow
    ry = height / (1.0 + PADDING) / 2.0 * 1.3 * grow
    d = ((xs - width / 2.0) / rx) ** 2 + ((ys - height * 0.5) / ry) ** 2
    return np.clip(1.6 - 0.9 * d, 0.0, 1.0).astype(np.float32)


def skin_mask(img: np.ndarray) -> np.ndarray:
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    cr, cb = ycrcb[..., 1], ycrcb[..., 2]
    mask = ((cr >= 133) & (cr <= 178) & (cb >= 75) & (cb <= 132)).astype(np.float32)
    sigma = max(1.5, 3.0 * min(img.shape[:2]) / 512.0)
    return cv2.GaussianBlur(mask, (0, 0), sigma)
