"""Build the static GitHub Pages demo into _site/: the full UI with no generation backend."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.main import _label  # noqa: E402
from app.hyperportrait import STYLES  # noqa: E402

SITE = ROOT / "_site"


def main() -> None:
    shutil.rmtree(SITE, ignore_errors=True)
    shutil.copytree(ROOT / "web", SITE / "static")
    index = (ROOT / "web" / "index.html").read_text()
    index = index.replace("<head>", '<head>\n  <meta name="hp-demo" content="1" />', 1)
    (SITE / "index.html").write_text(index)
    (SITE / "static" / "index.html").unlink()
    styles = [{"id": style, "label": _label(style)} for style in STYLES]
    (SITE / "static" / "styles.json").write_text(json.dumps(styles))
    (SITE / ".nojekyll").write_text("")
    print(f"Built {SITE} with {len(styles)} styles")


if __name__ == "__main__":
    main()
