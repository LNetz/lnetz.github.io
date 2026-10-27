# Global search

Every generated page gets the shared search form above the sidebar navigation.
Search replaces the content column temporarily; clearing it or choosing “Back to
page” restores the page. A `?q=` URL restores a query when returning from a result.
The desktop field is capped at 168 px within the existing 200 px column. On
phones and portrait tablets, the header's search button opens the menu directly
at the search field; submitting closes the sheet and shows the results.

`search_index.py` adds short heading/figure aliases outside the article series,
preserving existing IDs. Article references (`ai-1`, `ai-2.4`, `ai-f12`, etc.) keep
their existing generator. Linked card headings get aliases without nested links;
photo tiles retain their lightbox interaction.

The normal build regenerates `assets/search-en.json` and `assets/search-de.json`
from page bodies, including sections, figure captions, explanatory text,
publication metadata and photo descriptions. Navigation, controls, SVG internals
and scripts are excluded. Repeated photos and duplicate destinations are merged.
The 404 page has a search form but is not indexed. Figure records carry their
parent section so related figure hits can be displayed below a section result.
Multiple matching sections from one page share a single result group. The best
section remains the main link; further passages are expandable, with every direct
anchor retained. Own publications and exact anchor queries stay individually
addressable.

`assets/search.js` loads only the current language's index, on the first query.
`assets/search-core.js` owns tokenization, field-weighted BM25 scoring, phrase and
proximity bonuses, snippets and grouping. Whole words precede final-word prefixes;
arbitrary substrings are a last fallback and require at least four characters.
Thus `RAG` does not match the letters inside `Frage`. Small curated concept groups
cover technical synonyms, German/English terms and acronyms. If fewer than three
regular results exist, bounded edit-distance/transposition matching adds labelled
approximate results below the regular ones. Exact reference queries retain direct
figure destinations instead of being absorbed into a group.

Snippets compare passages across the entire result group, prioritize coverage of
distinct query concepts and substantive complete sentences, and avoid padding
with unrelated neighbouring sentences. The displayed passage has a 280-character
budget; truncation is used when a sentence is too long. If a better passage comes
from another section, an explicit source-anchor link identifies it. Matching
ignores case and accents; snippets and highlights are rendered
as text nodes. No server or external search service is required. Highlight offsets
map back to the original text, so accent-insensitive queries and German ß/ss
matching highlight the right characters. The in-memory word-frequency index is
prepared once per loaded language index; no worker is needed at this site's size.
Fetch failures expose a retry action. Results are added
in batches of 30.

## Own paper abstracts

`assets/pubs.js` is the authoritative allowlist. `_build/paper-abstracts.json`
contains sourced abstracts and explicit missing-data statuses for these papers
only. The normal build reads it offline; it never follows citation-map nodes or
downloads metadata. The first collection covers 29 of 32 own publications:
17 from identity-checked OpenAlex singleton records and 12 reviewed PDF excerpts.
Net25 and GJN+15b have no public PDF in the list; Net17 has no abstract in its
reviewed front matter. These three remain searchable through their metadata.

Abstracts remain in their source language, appear as expandable content on the
research page, and are searchable by both the global search and the publication
list filter. Search snippets label abstract matches and link their source. Links
to a publication open its abstract automatically. Source URLs, extraction pages,
retrieval dates and review markers live in the cache.

To refresh metadata (public, free singleton lookups; no citation refresh):

```sh
node _build/tools/update_abstracts.mjs [--fresh] [paper-key ...]
```

Reviewed PDF records are preserved even with `--fresh`. For missing abstracts:

```sh
node _build/tools/extract_abstracts.mjs [--two-columns] [paper-key ...]
```

The extractor needs the citation pipeline's existing `pdfjs-dist` dependency.
It writes ignored PDF/front-matter candidates into `_build/search-work/` and
does not automatically publish them. Review abstract boundaries and reading order
before adding a source-backed excerpt to the cache. Never fill gaps with generated
text. The ordinary site build and search have no new package dependencies.

Rebuild after editing content, using the normal generator or its Python/Node
capture workaround. Check the generated index and ranking with:

```sh
python -I _build/tools/check_search.py
node _build/tools/check_search.mjs
```

Browser checks: sidebar above navigation; desktop live query; phone menu submit;
exact anchors and cross-page results; browser Back; clear/restore; empty results;
German; keyboard focus; no console errors.

`check_search_browser.mjs` exports an automated regression suite for the documented
CUA browser APIs. Pass a tab, its browser's viewport capability and the local server
origin. It checks grouped figures, fuzzy results, an abstract-only hit, source
labels, direct paper links, Back, empty results, restoration, phone/tablet controls,
German synonyms, and failed-index/retry recovery. Its temporary fixture files are
removed afterwards; viewport overrides are reset in `finally`.

Existing public URLs are intentionally unchanged. The saved anchor baseline
is checked on both language versions so a build cannot silently remove one.
Changes to this baseline require deliberate link-compatibility review.
