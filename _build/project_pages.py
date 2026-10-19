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


def pub_list(lang, keys):
    """Same markup as the publication list on the research page (site.js); the <li>s only."""
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
        items.append(f'''        <li id="{k}">
          <span class="key mono">{k}</span>
          <div>
            <div class="t">{p["title"]}{flag}</div>
            <div class="a">{p["authors"].replace("L. Netz", "<b>L. Netz</b>")}</div>
            <div class="v mono">{p["venue"]}</div>
            <div class="plinks mono">{"".join(links)}</div>
          </div>
        </li>''')
    return NL.join(items)


# Lifeline on the project list: a horizontal, sideways-scrolling year rail. Years with a project
# start get a wide column with the project (icon, name, years, one line); empty years stay narrow.
SPANS = {"geneial": (2012, 2016), "smt-rat": (2015, 2015), "macoco": (2018, None), "add": (2018, 2022),
         "montigem": (2018, 2024), "ford": (2020, 2022), "epha": (2024, None), "golden-uml": (2025, 2025),
         "se-chatty": (2025, 2025), "esaca": (2025, None)}
LINES = {
    "geneial": T("C++ library for genetic algorithms", "C++-Bibliothek für genetische Algorithmen"),
    "smt-rat": T("Interval propagation in an SMT solver", "Intervall-Propagation in einem SMT-Solver"),
    "macoco": T("Controlling cockpit for university chairs", "Controlling-Cockpit für Lehrstühle"),
    "add": T("Digital-twin cockpits for wind turbines", "Digital-Twin-Cockpits für Windkraftanlagen"),
    "montigem": T("Generator for web information systems", "Generator für Web-Informationssysteme"),
    "ford": T("Tool tracking with Ford", "Werkzeugverfolgung mit Ford"),
    "epha": T("Online display of dissertations", "Online-Auslage von Dissertationen"),
    "golden-uml": T("Curated UML benchmark dataset", "Kuratierter UML-Benchmark-Datensatz"),
    "se-chatty": T("Teaching assistant on lecture material", "Lehrassistent auf Vorlesungsmaterial"),
    "esaca": T("Sovereign agentic coding, on-prem", "Souveränes agentisches Coding, on-prem"),
}
TL_FROM, TL_NOW = 2012, 2026


def timeline(lang, A):
    """Each project sits under its start year and links to its row in the list (#p-<slug>).
    The upper row counts the projects running that year. Scrolling: assets/site.js (lifeline)."""
    L = lambda x: x[lang] if isinstance(x, dict) else x
    by = {p["slug"]: p for p in PROJECTS}
    cols = []
    for k, year in enumerate(range(TL_FROM, TL_NOW + 1)):
        starts = [s for s, (y0, _) in SPANS.items() if y0 == year]
        active = sum(1 for y0, y1 in SPANS.values() if y0 <= year <= (y1 or TL_NOW))
        items = []
        for slug in starts:
            p, (y0, y1) = by[slug], SPANS[slug]
            icon = (f'<img src="{A}assets/logos/{p["logo"]}" alt="" width="22" height="22">' if p.get("logo")
                    else f'<b class="mono">{p["mark"]}</b>')
            when = f'{y0}' + ("" if y1 == y0 else f' — {y1 if y1 else L(T("today", "heute"))}')
            items.append(f'<li><a href="#p-{slug}"><span class="ico">{icon}</span><span class="nm">{L(p["name"])}</span></a>'
                         f'<span class="when mono">{when}</span><span class="ln">{L(LINES[slug])}</span></li>')
        ev = f'<ul class="ll-ev">{"".join(items)}</ul>' if items else ""
        cols.append(f'          <div class="ll-col{" has" if items else ""}{" now" if year == TL_NOW else ""}" style="--i:{k}">'
                    f'<span class="ll-n mono">{active or ""}</span><span class="ll-y">{year}</span><i class="ll-tick"></i>{ev}</div>')
    return f'''      <div class="lifeline" tabindex="0" role="region" aria-label="{L(T("Timeline of my projects, scrolls sideways", "Zeitleiste meiner Projekte, seitlich scrollbar"))}">
        <div class="ll-track">
          <div class="ll-head mono" aria-hidden="true"><span>{L(T("Active", "Aktiv"))}</span><span>{L(T("Years", "Jahre"))}</span></div>
{NL.join(cols)}
        </div>
      </div>
'''


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
    head = f'''    <header class="page proj">
      <a class="back mono" href="projects.html">← {L(T("all projects", "alle Projekte"))}</a>
      <div class="section-head">
        <h1><span class="mono">01</span>{L(p["name"])}</h1>
        <span class="mono faint">{L(p["when"])}</span>
      </div>{logo}
      <p class="lead">{L(p["lead"])}</p>
      <dl class="facts mono{" wide" if len(p["facts"]) > 3 else ""}">{facts}</dl>{links}
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
