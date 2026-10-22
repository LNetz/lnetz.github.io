# Style guide for the article series (MDE, AI4SE, Digital Twins, Evolutionary Algorithms)

The four articles (`research-mde/-ai4se/-dt/-ea.html`) should look made by one hand. This file holds the rules and
the shared helpers that enforce them. Read it before adding or changing a figure, a demo or an article's frame.

## Visual rules

```
CANVAS   full-width viewBox 784 (1 unit = 1 px on desktop), half width 380; never stretch a narrow SVG
         (give it max-width: <viewBox width>px instead).
TYPE     box title 13/500 sans · label 11 mono --ink-2 · annotation 11 mono --ink-3 ·
         header in a figure 10.5 mono UPPERCASE .06em · floor 10 px rendered · demo prose 14 sans ≤ 34ch.
         Tokens: --t-title --t-label --t-head --t-floor --t-prose; code --code 12.5 (listing) / --code-s 11.5 (in a figure).
STROKE   .75 hairline · 1 box/connector · 1.5 emphasis/data · 2 accent path · 2.5 handles; one 6×6 arrow marker.
         Tokens --sw-hair --sw-1 --sw-em --sw-acc --sw-handle; classes .sw-hair .sw-em .sw-acc .sw-handle.
DASHES   only "3 3" (optional / not generated: .ln.dash, .dash-opt) and "1 3" (guides: .dash-guide).
COLOUR   pure accent = the one subject (current, best, selected) · accent 45 % = generated/derived (--c-gen, .gen) ·
         --ink-3 at 35 % = everything else (--c-rest, .rest). Square bars, 12 px high, 4 px gap.
         No solid accent fills for pills, tabs or buttons.
LABELS   halo on every label that may cross a line: class "halo" (paint-order stroke, 4 px in --bg; inside a grey
         zone add "on-tile" to the group). Never put a label on a frame line; leaders are hairlines.
         Orthogonal connectors only.
CONTROLS segmented mono chips (.chips > button[aria-pressed]; accent border + text when pressed, never a fill;
         mark the "try this first" chip with class "first") · one stepper (▶ / ❚❚ / ↺, thin track, "step n of N") ·
         thin slider (every input[type=range] in an article is styled; the fill follows the value automatically).
MOTION   200 ms for a state change · 600–900 ms per step · drag follows the pointer live · settle 150 ms ·
         prefers-reduced-motion: no autoplay, no transitions over 50 ms.
AUTOPLAY narrated sequences (a story told in steps) play once when scrolled into view and stop when they leave it;
         parameter demos (sliders, presets) never autoplay. Use SiteDemo.stepper / SiteDemo.autoplay.
HEIGHT   no figure.demo may change height between steps or presets: lock the variable panel (SiteDemo.lock).
PHONE    every figure fits 358 px, or has a stacked variant (hero-wide / hero-tall pattern), or scrolls in a
         .dia-scroll with a visible "↔" hint. No key content in the right 40 % of a scrolling figure.
TEXT     concept first, case study after; at most ~1 citation per paragraph in running text; thesis- and
         paper-specific detail goes into a case study or a "For the curious" box.
```

## The article frame: `_build/article_common.py`

One source for everything around the content. An article module only builds its sections and calls `page()`.

| Helper | What it does |
|---|---|
| `SERIES` | One entry per part: `file, module, part, thumb, abbr, long, short, date, card` (all texts as `T(en, de)`). Change names, dates and teaser texts **here** — card, header, series line, `<title>`, phone bar and "next in the series" all read it. |
| `sections(S, lang)` | Renders the section list. Entries `(id, level, heading, html[, nav])`: level 2 = numbered chapter (`01 …`), 3 = sub chapter (h3), 1 = closing chapter without number ("In short"), 0 = untitled block. The optional 5th element is a short side-nav label `T(...)` (written as `data-nav` on the heading). |
| `page(lang, file, sections_html, refs, own, hero, lead, desc, scripts)` | The whole page: header (`← all articles`, `n / 4`, title, date, lead, series line, numbered chapter list incl. "In short" and "Literature"), hero, the article, the literature block and the "next in the series" block. Returns `(file, title, desc, body, scripts)` for `build.py`. |
| `scripts(lang, name, css=False)` | `assets/demo-common.js` + `assets/<name>.js` (+ `<name>.css`). |
| `src(kind, *keys, where=None, note=None)` | A caption's source line as `T()`. `kind`: `"after"`, `"data"`, `"from"`, `"illustrative"`, `"fictional"`. Keys: own-paper keys (strings) or literature numbers (ints). `where` in English (`"Fig. 3"`, `"Table 2"`, `"§6.3"`, `"ch. 6"`), translated to Abb./Tabelle/Kap. for German. Examples: `src("after", "Net24", where="Fig. 2.4")` → "After [Net24], Fig. 2.4" / "Nach [Net24], Abb. 2.4"; `src("data", "NWN+15", where="Table 2")`; `src("illustrative")`. Rules: no author names, `§` for sections, "fictional data" goes here, not in the prose. |
| `fig(svg, caption, lang, scroll=True, source=None)`, `demo(kind, data, inner, caption, lang, source=None)` (in `ai4se.py`) | `source=src(...)` appends the source line to the caption. For hand-built `<figure>`s use `source_line(src(...), lang)` at the end of the figcaption. |
| `curious(lang, body, title=None)` (in `ai4se.py`) | Renders "＋ FOR THE CURIOUS · *title*". Pass the **topic only** as title (e.g. `T("Takeover time", "Übernahmezeit")`). |
| `art_link(lang, file, anchor="")` | "Background: Part N · Title →" on project pages (`project_pages.ARTICLE_LINKS`). |
| `cards(lang)` | The research page's article cards; the figure count is counted from the page (`figure.demo`). |

**Citations.** `cite("KEY")` (own paper) links to `#pub-KEY`, `ref(n)` / `r(key)` (literature) to `#ref-n` — both on
the same page. `page()` then

- renumbers the literature by first citation (German uses the English order), so add new entries anywhere in `REFS`;
- lists literature that is never cited under "Further reading" (cite it or delete it);
- lists under "My papers on the topic" exactly the own papers that are cited (in `OWN` order). Uncited `OWN` keys are
  reported on stderr by the build; cited keys missing from `OWN` are listed last and reported too;
- gives each own paper a link "in the publication list →" to `research.html#pub-KEY`.

## The demo helpers: `assets/demo-common.js` (`window.SiteDemo`)

Loaded before every article script. Use these instead of a local copy.

```js
SiteDemo.reduce                        // prefers-reduced-motion
SiteDemo.words                         // { play, pause, replay, step, of } in the page language
SiteDemo.whenSeen(el, fn, t = .35)     // run fn once when a share t of el is visible
SiteDemo.press(buttons, on)            // segmented chips: aria-pressed only on `on`

// height lock: render every state, min-height = tallest, restore current(); re-measures on width change and
// after web fonts load. states: a count n (render(0..n-1)) or an array of values passed to render.
SiteDemo.lock(el, states, render, current)
//   e.g. presets: SiteDemo.lock(fig.querySelector(".enc-note"), PRESETS, p => note(p), () => active)

// the autoplay rule: narrated → start once on view (not under reduced motion); always stop on leaving the view
SiteDemo.autoplay(fig, { start, stop, narrated = true })

// the one stepper on the usual markup (.play, input.step, .where): ▶ / ❚❚ / ↺ with aria-label "replay" at the end,
// "step n of N" in .where (label: false to write it yourself), height lock over all steps for the elements in `lock`,
// autoplay rule built in. delay: ms or (k) => ms.
const st = SiteDemo.stepper(fig, count, render, { delay: 900, narrated: true, lock: [panel], label: true, onStop });
st.show(i); st.start(); st.stop(); st.setCount(n); st.k; st.running;
```

Every demo in the four articles now uses `SiteDemo.stepper` / `SiteDemo.lock`; a new demo whose panel changes height
between steps or presets must use them too.

## Shared figure CSS (style.css)

- **Heroes** (`.art-hero`): the wide drawing is 860 units and renders at ~784 px, the phone variant (`.hero-tall`,
  430 units) at ~358 px. style.css sets `text.s` to 11 and every `.hero-tall` label to 12 units, which keeps them at
  the 10 px floor. All four heroes have a `hero-wide` + `hero-tall` pair. Give the two SVGs **separate marker ids**:
  the hidden wide SVG would otherwise own the marker and the phone arrow loses its head.
- **"↔ scroll"**: `site.js` marks a `.dia-scroll` that really overflows with `.scrolls`; the figure's caption then
  starts with "↔ scroll" / "↔ scrollen". No per-article hint needed.
- **`.pill`** is outlined (accent border and text), never a solid fill.
- **"In short"**: `ul.pts` bullets, then `div.fit` with two `span.k.mono` headings ("WORTH IT WHEN" / "SOMETHING ELSE
  IS ENOUGH WHEN", DE "LOHNT SICH, WENN" / "ETWAS ANDERES REICHT, WENN"), each followed by a `ul.pts`; an optional
  `div.tryit` box after it.

## Navigation (site.js, no per-article code)

- The chapter list in the header and the side nav are built from the h2s; h3s join the side nav under their chapter,
  labelled with `data-nav` when given. The current chapter and section are in the accent; "In short" and
  "Literature" are entries of their own.
- On phones the bar shows `ABBR · 02 Chapter`; anchors land below the sticky bar (`html{scroll-padding-top}`).
- The back-to-top button steps aside while a `figure.demo` is under it.
