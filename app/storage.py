"""Recipe JSON written next to each generation job."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECIPE_DIR = ROOT / "data" / "recipes"


def save_recipe(job_id: str, data: dict) -> None:
    RECIPE_DIR.mkdir(parents=True, exist_ok=True)
    (RECIPE_DIR / f"{job_id}.json").write_text(json.dumps(data, indent=2))


def load_recipe(job_id: str) -> dict | None:
    path = RECIPE_DIR / f"{job_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())
