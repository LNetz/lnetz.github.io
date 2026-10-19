# Notes for AI assistants working on this repo

Personal website of Lukas Netz, published with GitHub Pages from `main` (lnetz.github.io).
Plain static HTML/CSS/JS, bilingual: English at `/`, German at `/de/`. No framework, no build server.

## Layout

| Path | What |
|---|---|
| `_build/build.py` | **Generator** for all pages (EN + DE) — edit content here, not in the HTML. Text pairs are `T("english", "deutsch")`. |
| `_build/project_*.py` | Project sub pages (imported by build.py). |
| `*.html`, `de/*.html` | Generated output — committed, never edited by hand. |
| `assets/pubs.js` | **The publication list** (single source of truth for papers). |
| `assets/site.js`, `assets/style.css` | Shared JS / CSS. |
| `assets/graph-view.js` | Citation map viewer (research page). |
| `assets/citations.js`, `citedby.js`, `pubs-mini.js` | Generated citation data — see `_build/citations/README.md`. |
| `_build/citations/` | Pipeline that refreshes the citation data. |
| `_build/tools/` | `serve.mjs` (local preview), `build_capture.py` + `write_capture.mjs` (generator workaround, below). |

Folders starting with `_` are not published by GitHub Pages.

## Regenerating the pages

```sh
python _build/build.py
```

On the owner's work laptop an endpoint protection (Sophos) blocks Python from writing files
(`PermissionError`). Then let Python only compute and Node write:

```sh
python -I _build/tools/build_capture.py _build/build.py 2>/dev/null | node _build/tools/write_capture.mjs            # all pages
python -I _build/tools/build_capture.py _build/build.py 2>/dev/null | node _build/tools/write_capture.mjs research.html   # only these
```

(In Git Bash, don't start a filter argument with `/` — it gets turned into a Windows path.)

## Checking locally

```sh
node _build/tools/serve.mjs . 8000      # then open http://127.0.0.1:8000/research.html
```

`file://` does not work (theme storage and the WebGL photo transitions need a real origin).

## Task: refresh the citation data (every few months)

The research page shows Google Scholar metrics, a citation map ("cites" / "cited by", 2D/3D) and a mini graph
per paper. All of it is static and goes stale. To refresh:

1. **New papers first**: add them to `assets/pubs.js` (same fields as the others; `pdf` link if there is one).
2. **Run the pipeline** — details, rules and pitfalls in `_build/citations/README.md` (read it first):
   ```sh
   cd _build/citations && npm install && cd ../..
   OPENALEX_KEY=<key> node _build/citations/update.mjs --fresh
   ```
   Ask the owner for an OpenAlex API key (free, https://openalex.org/settings/api). Pass it only as an
   environment variable — never write it into a file or commit it.
3. **Scholar metrics**: the `scholar` step prints the profile totals. Put them into `METRICS` in
   `_build/build.py` (citations, h-index, i10-index) and update the "as of / Stand" month there.
4. **Regenerate** the pages (above) — at least `research.html`, `de/research.html` and `index.html`.
5. **Check** the research page locally: the map loads (both directions, 2D/3D), the mini graphs show up,
   clicking a mini graph jumps to the paper in the map, no console errors. Look at the numbers the pipeline
   printed: a paper whose PDF suddenly yields < 5 references needs a better PDF source (see the README).
6. **Commit** the regenerated HTML and `assets/citations.js`, `citedby.js`, `pubs-mini.js` plus the small
   files in `_build/citations/work/` (the large ones are git-ignored). Push only when the owner asks.

## Conventions

- Keep EN and DE in sync — every visible text is a `T(en, de)` pair.
- Style: minimal, small type, lots of whitespace, one accent colour; light theme by default, dark/auto toggle.
- Images: keep full-size photos ≤ ~2000 px; grid thumbnails in `assets/photos/thumbs/` (340 px high).
- Commit messages: short imperative summary of what changed for the visitor.
