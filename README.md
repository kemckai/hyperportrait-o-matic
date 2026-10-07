# Hyperportraits

Upload a portrait and get seeded, face-aligned variants. Each variant stores the transform recipe that produced it.

[Demo page](https://kemckai.github.io/hyperportrait-o-matic/) shows the interface only. Generation needs the Python server, so run it locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000. Same seed and same image reproduce the same variants.

Styles:

- Artist styles (default `peter_max`): `warhol`, `lichtenstein`, `haring`, `fairey`, `hockney`, `mondrian`, `kusama`, `klimt`, `banksy`.
- Masters (`app/masters.py`): `van_gogh`, `monet`, `seurat`, `picasso`, `matisse`, `mucha`, `hokusai`, `kandinsky`, `kahlo`, `dali`, `basquiat`, `rothko`, `pollock`, `hopper`, `magritte`, `escher`, `hirst`, `murakami`, `vasarely`, `britto`.
- `mix` gives each variant a different artist, starting with Peter Max. Ask for 30 variants to get every artist once.
- `flattering`: color grades, glow, light leaks, and backdrop color. Skin smoothing and feature sharpening are masked to the face, so features are never warped.
- `glitch`: posterize, swirl, elastic warps, and band glitches applied across the face.

To update the demo page after changing `web/`, run `scripts/publish_pages.sh`. It rebuilds `_site/` and force-pushes it to the `gh-pages` branch.
