# Citation map pipeline

Builds the data behind the **citation map** and the **mini graphs** on the research page
(`research.html`, `de/research.html`):

| Output (in `assets/`) | What it is | Drawn by |
|---|---|---|
| `citations.js` (`window.GRAPH`) | "cites": my papers → the works they cite → (fainter) works cited by ≥ 3 of those | `assets/graph-view.js` |
| `citedby.js` (`window.GRAPH_IN`) | "cited by": works citing my papers → (fainter) every work citing those | `assets/graph-view.js` |
| `pubs-mini.js` (`window.PUBS_MINI`) | per paper: topics of what it cites / what cites it (mini graph in the publication list) | `assets/site.js` |

The list of my papers is `assets/pubs.js` — the single source of truth. Everything here is static:
the site never calls an API; data is refreshed by running this pipeline and committing the outputs.

## Refresh (the short version)

```sh
cd _build/citations && npm install          # once: pdfjs-dist, d3-force-3d
export OPENALEX_KEY=...                      # free key, https://openalex.org/settings/api (ask the owner)
node _build/citations/update.mjs --fresh     # all steps, everything fetched anew (≈ 15–30 min)
```

Then regenerate the pages, update the Scholar metrics, check locally (see the root `AGENTS.md`).
Without `--fresh`, cached results in `work/` are reused (fast; useful after adding one paper).
Single steps: `node _build/citations/update.mjs graph mini` etc.

## Steps (`update.mjs` runs them in this order)

1. **openalex** — `fetch_openalex.mjs`: finds my papers in OpenAlex (by DOI, else title) → `work/own.json`,
   and their OpenAlex reference lists → `work/hop1.json`.
2. **pdfs** — `fetch_pdfs.mjs` + `pdf_refs.mjs`: downloads each paper's PDF (`pdf` in pubs.js, or an override
   in `work/pdf_sources.json`) and reads its reference list → `work/pdfrefs/<key>.json`.
3. **crossref** — `resolve_crossref.mjs`: matches each reference entry to a DOI with Crossref's
   bibliographic search → `work/pdf_cr.json`. Resumable per paper; slow (~1 s per entry), no budget.
4. **scholar** — `fetch_scholar.mjs`: citation counts of my papers from the public Scholar profile → `work/scholar.json`;
   also prints the profile totals for the METRICS block in `_build/build.py`.
5. **graph** — `build_graph.mjs`: assembles "cites", looks up the Crossref DOIs in OpenAlex (free single-work
   lookups) for topics and their own reference lists, picks the second hop, computes 2D + 3D layouts → `assets/citations.js`.
6. **citedby** — `fetch_citedby.mjs` (OpenAlex `cites:` filter, needs a key in practice) + `build_citedby.mjs` → `assets/citedby.js`.
7. **mini** — `build_mini.mjs` → `assets/pubs-mini.js`.

`resolve_openalex.mjs` is an older alternative to step 3 (OpenAlex full-text search). It is NOT part of
`update.mjs` because it burns the OpenAlex budget fast; its past results (`work/pdf_resolved.json`) are still used.

## Rules learned the hard way

- **A paper's own PDF reference list is the truth.** OpenAlex reference lists are often incomplete and
  were even mixed up between papers of the same proceedings (NRR24 had CMNR24's references). OpenAlex lists
  are only used for papers without a PDF.
- **Self-citations** are recognised by DOI or by the paper's title inside the reference text, so they link to
  my own node instead of creating a copy.
- **PDFs that yield (almost) no references** are scans or have broken fonts. Find a better copy (the GI Digital
  Library has many, `dl.gi.de`) and add it to `work/pdf_sources.json`. Papers without any PDF
  (currently Net25, GJN+15b) simply have no references.
- **OpenAlex budget**: list/filter queries cost money from a daily budget ($0.10/day without a key, shared by the
  whole network IP — often already used up; $1/day with a free key). Single-work lookups (`/works/<id>`,
  `/works/doi:<doi>`) cost nothing. Use batches of ≤ 50 ids and the key. Pass the key only via `OPENALEX_KEY`;
  never write it into a file or the repo.
- **Google Scholar**: only the one profile request in `fetch_scholar.mjs` is allowed by its robots.txt
  (no `cstart`, no search or "cited by" pages). Don't crawl Scholar.
- **Semantic Scholar** without a key is throttled to near uselessness and withholds many publishers' reference lists.
- Topics are guessed from titles and OpenAlex topics (`RULES` in `build_graph.mjs`); the "SE RWTH" ring from author
  names (`SE_NAMES`). Colours must match `MAP_TOPICS` in `_build/build.py` and `TOPIC` in `assets/graph-view.js`.
- Thresholds: "cites" second hop = cited by ≥ 3 first-hop works (`update.mjs` passes `3`); "cited by" second hop =
  all (`1`). Raising them makes the map lighter (≥ 4 roughly halves "cites").

## `work/`

Committed (small, slow or impossible to recreate): `own.json`, `pdfrefs/`, `pdf_cr.json`, `pdf_resolved.json`,
`scholar.json`, `pdf_sources.json`. Ignored (large, re-fetchable): PDFs, `hop1.json`, `hop2_meta.json`,
`oa_by_doi.json`, `citing1.json`, `citing2.json` — a fresh clone fetches them on the first run.
