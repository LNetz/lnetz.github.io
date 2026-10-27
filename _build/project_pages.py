"""
Project pages: one deeper page per project (projects-<slug>.html), linked from the project list.
Imported by build.py; the content lives in project_content.py.

Each page: back link · title · lead · facts · one visual (video, diagram or figure) ·
short chapters · the papers behind it (read from assets/pubs.js) · previous / next project.
"""
import json
import os
import re

from project_content import PROJECTS
import article_common

# project → the articles it is background for: (article file, anchor)
ARTICLE_LINKS = {
    "esaca": [("research-ai4se.html", "harness")],
    "macoco": [("research-mde.html", "practice")],
    "se-chatty": [("research-ai4se.html", "rag")],
    "ford": [("research-mde.html", "")],
    "add": [("research-mde.html", ""), ("research-dt.html", "wind")],
    "montigem": [("research-mde.html", "montigem"), ("research-ai4se.html", "app")],
    "geneial": [("research-ea.html", "")],
    "smt-rat": [("research-ea.html", "")],
}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = "\n"


def T(en, de):
    return {"en": en, "de": de}


def _pubs():
    """assets/pubs.js is a JS object literal; quoting its keys makes it JSON."""
    src = open(os.path.join(ROOT, "assets", "pubs.js"), encoding="utf8").read()
    body = src[src.index("["): src.rindex("]") + 1]
    return {p["key"]: p for p in json.loads(re.sub(r'([{,]\s*)([A-Za-z_]\w*):', r'\1"\2":', body))}


PUBS = _pubs()


def file_of(slug):
    return f"projects-{slug}.html"


def ext(label, url):
    return f'<a href="{url}" target="_blank" rel="noopener">{label} ↗</a>'


def pub_list(lang, keys, id_prefix="", full_list=False):
    """Same markup as the publication list on the research page (site.js); the <li>s only.
    Articles pass id_prefix="pub-" (their cites point to #pub-KEY on the same page) and full_list=True, which adds a
    link to the entry in the research page's full list."""
    flags = {"Article": T("Article", "Artikel"), "Dissertation": T("Dissertation", "Dissertation"),
             "MastersThesis": T("Master’s thesis", "Masterarbeit"), "BachelorsThesis": T("Bachelor’s thesis", "Bachelorarbeit")}
    items = []
    for k in keys:
        p = PUBS[k]
        links = []
        if p.get("pdf"): links.append(ext("pdf", p["pdf"]))
        if p.get("doi"): links.append(ext("doi", "https://doi.org/" + p["doi"]))
        if p.get("url"): links.append(ext(p.get("urlLabel", "link"), p["url"]))
        flag = f'<span class="flag mono">{flags[p["flag"]][lang]}</span>' if p.get("flag") else ""
        if full_list:
            links.append(f'<a class="int" href="research.html#pub-{k}">{T("in the publication list", "in der Publikationsliste")[lang]} →</a>')
        items.append(f'''        <li id="{id_prefix}{k}">
          <span class="key mono">{k}</span>
          <div>
            <div class="t">{p["title"]}{flag}</div>
            <div class="a">{p["authors"].replace("L. Netz", "<b>L. Netz</b>")}</div>
            <div class="v mono">{p["venue"]}</div>
            <div class="plinks mono">{"".join(links)}</div>
          </div>
        </li>''')
    return NL.join(items)


# Lifeline on the project list: a flat, sideways-scrolling year rail. Each project is a title at its
# start year, followed by a thin line to its end (running projects: to today) — no line when only
# one year is known. Projects that ran at the same time get their own row. Titles link to the list.
SPANS = {"geneial": (2012, 2016), "smt-rat": (2015, 2015), "macoco": (2018, None), "add": (2018, 2022),
         "montigem": (2018, 2024), "ford": (2020, 2022), "epha": (2024, None), "golden-uml": (2025, 2025),
         "se-chatty": (2025, 2025), "esaca": (2026, None)}
# further involvement without a page of its own: (start, end, name), row #p-<slug> in "Further involvement"
OTHER = {"blended": (2015, 2018, T("Blended Learning", "Blended Learning"))}
# Degrees on the same rail: a mono label and an accent dot on the rail, linking to the thesis
# in the publication list of the research page (#pub-<key>, site.js).
DEGREES = [
    (2015, T("B.Sc. Computer Science", "B.Sc. Informatik"), "Net15"),
    (2017, T("M.Sc. Computer Science", "M.Sc. Informatik"), "Net17"),
    (2024, T("PhD · Dr. rer. nat.", "Promotion · Dr. rer. nat."), "Net24"),
]
TL_FROM, TL_NOW, TL_TODAY = 2010, 2026, 2026.8      # TL_TODAY: where "now" ends on the rail (Oct 2026)
TL_PAD, TL_W, TL_W_HAS = 24, 76, 230                # px: left padding, empty year, year with a start
TL_TOP, TL_ROW = 46, 26                             # px: first row, row pitch (must match style.css)


def timeline(lang, A):
    """Scrolling behaviour: assets/site.js (lifeline)."""
    L = lambda x: x[lang] if isinstance(x, dict) else x
    by = {p["slug"]: p for p in PROJECTS}
    starts = {y0 for y0, _ in SPANS.values()} | {y for y, _, _ in DEGREES} | {y0 for y0, _, _ in OTHER.values()}
    widths = {y: TL_W_HAS if y in starts else TL_W for y in range(TL_FROM, TL_NOW + 1)}
    def X(t):                                        # rail position of a (fractional) year
        y, f, x = int(t), t - int(t), TL_PAD
        for k in range(TL_FROM, min(y, TL_NOW + 1)):
            x += widths[k]
        return x + f * widths.get(y, TL_W)
    cols = NL.join(f'          <div class="ll-col{" has" if y in starts else ""}{" now" if y == TL_NOW else ""}" style="--i:{k}">'
                   f'<span class="ll-y">{y}</span><i class="ll-tick"></i></div>'
                   for k, y in enumerate(range(TL_FROM, TL_NOW + 1)))
    entries = [(y0, y1, slug, L(by[slug]["name"]), None) for slug, (y0, y1) in SPANS.items()]
    entries += [(y0, y1, slug, L(name), None) for slug, (y0, y1, name) in OTHER.items()]
    entries += [(y, y, None, L(label), f"research.html#pub-{key}") for y, label, key in DEGREES]
    rows, runs, dots = [], [], []                    # rows: px up to which each row is taken
    for y0, y1, slug, name, url in sorted(entries, key=lambda e: (e[0], e[2] is None, -(e[1] or TL_NOW))):
        point = y1 == y0                             # only one year known: title, no line
        x0 = X(y0)
        x1 = x0 + len(name) * 7.2 + 8 if point else X(y1 + 1 if y1 else TL_TODAY)
        taken = max(x1, x0 + len(name) * 7.2 + 12)   # the title may be longer than the line
        r = next((i for i, until in enumerate(rows) if until + 10 <= x0), None)
        if r is None:
            rows.append(taken); r = len(rows) - 1
        else:
            rows[r] = taken
        top = TL_TOP + r * TL_ROW
        if url:                                      # a degree
            dots.append(f'          <i class="ll-dot" style="left:{x0:.0f}px"></i>')
            runs.append(f'          <a class="ll-p point deg mono" href="{url}" title="{name} · {y0} · RWTH Aachen" '
                        f'style="left:{x0:.0f}px;top:{top}px;--len:0px;--i:{y0 - TL_FROM}"><span>{name}</span></a>')
            continue
        when = f'{y0}' + ("" if y1 == y0 else f' — {y1 if y1 else L(T("today", "heute"))}')
        runs.append(f'          <a class="ll-p{" open" if not y1 else ""}{" point" if point else ""}" href="#p-{slug}" title="{name} · {when}" '
                    f'style="left:{x0:.0f}px;top:{TL_TOP + r * TL_ROW}px;--len:{x1 - x0:.0f}px;--i:{y0 - TL_FROM}"><span>{name}</span></a>')
    height = TL_TOP + len(rows) * TL_ROW
    # .lifeline scrolls; its edges fade out where there is more to see
    return f'''
      <div class="ll-wrap">
        <div class="lifeline" tabindex="0" role="region" aria-label="{L(T("Timeline of my projects, scrolls sideways", "Zeitleiste meiner Projekte, seitlich scrollbar"))}">
          <div class="ll-track" style="height:{height}px">
{cols}
{NL.join(dots)}
{NL.join(runs)}
          </div>
        </div>
        <p class="ll-hint mono" aria-hidden="true">← {L(T("swipe sideways", "seitlich wischen"))} →</p>
      </div>'''



def video(lang, A, yt, thumb, title, caption):
    """Click-to-load YouTube facade (assets/project.js); a plain link without JS."""
    L = lambda x: x[lang] if isinstance(x, dict) else x
    play = L(T("play video", "Video abspielen"))
    return f'''    <figure class="media">
      <a class="yt frame-16x9" href="https://youtu.be/{yt}" data-yt="{yt}" target="_blank" rel="noopener" aria-label="{L(title)} — {play}">
        <img src="{A}assets/projects/{thumb}" alt="" width="1280" height="720" loading="lazy">
        <span class="play mono"><i aria-hidden="true">▶</i>{play}</span>
      </a>
      <figcaption class="mono">{L(caption)} {L(T("The video is loaded from YouTube only when you start it.", "Das Video wird erst beim Start von YouTube geladen."))}</figcaption>
    </figure>
'''


def page(lang, idx):
    """Returns (file, title, description, body, scripts) for PROJECTS[idx]."""
    L = lambda x: x[lang] if isinstance(x, dict) else x
    A = "../" if lang == "de" else ""
    p = PROJECTS[idx]

    logo = (f'\n      <div class="proj-logo"><img src="{A}assets/logos/{p["logo"]}" alt="" width="48" height="48"></div>'
            if p.get("logo") else "")
    facts = "".join(f'<div><dt>{L(k)}</dt><dd>{L(v)}</dd></div>' for k, v in p["facts"])
    links = "".join(ext(L(a), b) for a, b in p.get("links", ()))
    links = f'\n      <div class="links-top mono">{links}</div>' if links else ""
    # "Background: Part N · Title →" — the articles that explain what this project builds on (article_common.SERIES)
    background = "".join(article_common.art_link(lang, f, a) for f, a in ARTICLE_LINKS.get(p["slug"], ()))
    background = f"\n      {background}" if background else ""
    head = f'''    <header class="page proj">
      <a class="back mono" href="projects.html">← {L(T("all projects", "alle Projekte"))}</a>
      <div class="section-head">
        <h1><span class="mono">01</span> {L(p["name"])}</h1>
        <span class="mono faint">{L(p["when"])}</span>
      </div>{logo}
      <p class="lead">{L(p["lead"])}</p>
      <dl class="facts mono{" wide" if len(p["facts"]) > 3 else ""}">{facts}</dl>{links}{background}
    </header>
'''
    media = p["media"](lang, A) if p.get("media") else ""
    chapters = NL.join(
        f'''        <li>
          <h2>{L(label)}</h2>
          <div class="txt">{L(text) if not callable(text) else text(lang, A)}</div>
        </li>''' for label, text in p["chapters"])
    pubs = ""
    if p.get("pubs"):
        pubs = (f'''
      <div class="group mono">{L(T("Publications", "Publikationen"))} · {len(p["pubs"])}</div>
      <ol class="pubs">
{pub_list(lang, p["pubs"])}
      </ol>
''')
    prev, nxt = PROJECTS[idx - 1], PROJECTS[(idx + 1) % len(PROJECTS)]
    pager = f'''
      <nav class="pager mono" aria-label="{L(T("More projects", "Weitere Projekte"))}">
        <a href="{file_of(prev["slug"])}"><span>← {L(T("previous", "vorheriges"))}</span><b>{L(prev["name"])}</b></a>
        <a href="{file_of(nxt["slug"])}"><span>{L(T("next", "nächstes"))} →</span><b>{L(nxt["name"])}</b></a>
      </nav>'''
    body = f'''
{head}{media}    <section>
      <ul class="story">
{chapters}
      </ul>
{pubs}{pager}
    </section>
'''
    scripts = f'<script src="{A}assets/project.js"></script>\n' if "data-yt" in body else ""
    return file_of(p["slug"]), p["name"], p["desc"], body, scripts
