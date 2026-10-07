"""Sync hyperportrait API. Generation runs in a worker thread and returns images."""

from __future__ import annotations

import asyncio
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.types import Scope

from app.catalog import ARTISTS
from app.hyperportrait import STYLES, generate_hyperportraits
from app.storage import load_recipe, save_recipe

ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIR = ROOT / "data" / "uploads"
OUTPUT_DIR = ROOT / "data" / "outputs"
WEB_INDEX = ROOT / "web" / "index.html"

MAX_BYTES = 10 * 1024 * 1024
REVALIDATE = {"Cache-Control": "no-cache"}
IMMUTABLE = {"Cache-Control": "public, max-age=31536000, immutable"}
INTENSITY = {"low": 0.5, "medium": 1.0, "high": 1.8}
_JOB_ID = re.compile(r"^[a-f0-9]{32}$")
_VARIANT_ID = re.compile(r"^(source|v\d{1,2})$")

class WebFiles(StaticFiles):
    """Static files that always revalidate, so a deploy never mixes old and new code."""

    async def get_response(self, path: str, scope: Scope):
        response = await super().get_response(path, scope)
        response.headers.update(REVALIDATE)
        return response


app = FastAPI(title="Hyperportraits")
app.add_middleware(GZipMiddleware, minimum_size=1024)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", WebFiles(directory=ROOT / "web"), name="static")


@app.get("/")
def index():
    return FileResponse(WEB_INDEX, headers=REVALIDATE)


@app.post("/api/generate")
async def generate(
    file: UploadFile = File(...),
    n_variants: int = Form(3),
    n_transforms: int = Form(3),
    intensity: str = Form("medium"),
    style: str = Form("peter_max"),
    seed: int | None = Form(None),
):
    if style not in STYLES:
        raise HTTPException(status_code=400, detail=f"Style must be one of: {', '.join(STYLES)}")
    if intensity not in INTENSITY:
        raise HTTPException(status_code=400, detail="Intensity must be low, medium, or high")
    if not 1 <= n_variants <= 30:
        raise HTTPException(status_code=400, detail="Variants must be between 1 and 30")
    if not 1 <= n_transforms <= 6:
        raise HTTPException(status_code=400, detail="Transforms must be between 1 and 6")

    data = await file.read(MAX_BYTES + 1)
    if not data:
        raise HTTPException(status_code=400, detail="Empty upload")
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB)")
    suffix = _sniff(data)
    if suffix is None:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, or WebP allowed")

    job_id = uuid4().hex
    src_path = UPLOAD_DIR / f"{job_id}{suffix}"
    src_path.write_bytes(data)
    out_dir = OUTPUT_DIR / job_id

    try:
        result = await asyncio.to_thread(
            generate_hyperportraits,
            str(src_path),
            n_variants,
            n_transforms,
            INTENSITY[intensity],
            seed,
            str(out_dir),
            style,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    save_recipe(
        job_id,
        {
            "source": src_path.name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "intensity": intensity,
            "style": style,
            "seed": result["base_seed"],
            "face": result["face"],
            "variants": result["variants"],
        },
    )
    return {
        "job_id": job_id,
        "face_detected": result["face"]["detected"],
        "seed": result["base_seed"],
        "source_url": f"/api/image/{job_id}/source",
        "variants": [
            {
                "id": variant["id"],
                "style": variant["style"],
                "label": _label(variant["style"]),
                "url": f"/api/image/{job_id}/{variant['id']}",
                "recipe": variant["recipe"],
                "seed": variant["seed"],
            }
            for variant in result["variants"]
        ],
    }


@app.get("/api/recipe/{job_id}")
def get_recipe(job_id: str):
    _check_job(job_id)
    recipe = load_recipe(job_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Not found")
    return recipe


@app.get("/api/image/{job_id}/{variant_id}")
def get_image(job_id: str, variant_id: str):
    _check_job(job_id)
    if not _VARIANT_ID.match(variant_id):
        raise HTTPException(status_code=404, detail="Not found")
    path = OUTPUT_DIR / job_id / f"{variant_id}.png"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(path, media_type="image/png", headers=IMMUTABLE)


@app.get("/api/styles")
def styles():
    return [{"id": style, "label": _label(style)} for style in STYLES]


def _label(style: str) -> str:
    if style in ARTISTS:
        return ARTISTS[style].label
    return {"mix": "Artist Mix", "flattering": "Flattering Photo", "glitch": "Glitch"}[style]


def _sniff(data: bytes) -> str | None:
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    return None


def _check_job(job_id: str) -> None:
    if not _JOB_ID.match(job_id):
        raise HTTPException(status_code=404, detail="Not found")
