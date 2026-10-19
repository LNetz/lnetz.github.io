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


# Timeline on the project list: when each project ran (end None = still running).
SPANS = {"geneial": (2012, 2016), "smt-rat": (2015, 2015), "macoco": (2018, None), "add": (2018, 2022),
         "montigem": (2018, 2024), "ford": (2020, 2022), "epha": (2024, None), "golden-uml": (2025, 2025),
         "se-chatty": (2025, 2025), "esaca": (2025, None)}
TL_FROM, TL_TO = 2012, 2027                       # axis: Jan 2012 … Jan 2027 ("now" ends there)


def timeline(lang, A):
    """Project icons on a year axis; a thin line shows how long each ran. Each links to its row
    in the list below (#p-<slug>). Lanes are packed greedily; a label sits right of its icon,
    or left of it when the right edge is too close."""
    L = lambda x: x[lang] if isinstance(x, dict) else x
    by = {p["slug"]: p for p in PROJECTS}
    span = TL_TO - TL_FROM
    X = lambda y: (y - TL_FROM) / span * 100       # year → % of the rail
    PX = 720 / span                                # px per year at the rail's minimum width
    items = sorted(SPANS.items(), key=lambda kv: (kv[1][0], -(kv[1][1] or TL_TO)))
    lanes, out = [], []                            # lanes: occupied-until year per lane
    for slug, (y0, y1) in items:
        p, end = by[slug], (y1 + 1 if y1 else TL_TO)
        name = L(p["name"])
        label = (len(name) * 6.8 + 44) / PX        # icon + label width in years
        flip = y0 + label > TL_TO                  # label left of the icon near the right edge
        a, b = (y0 - label + 0.6, max(end, y0 + 0.6)) if flip else (y0, max(end, y0 + label))
        lane = next((i for i, until in enumerate(lanes) if until + 0.25 <= a), None)
        if lane is None:
            lanes.append(b); lane = len(lanes) - 1
        else:
            lanes[lane] = b
        icon = (f'<img src="{A}assets/logos/{p["logo"]}" alt="" width="26" height="26">' if p.get("logo")
                else f'<b class="mono">{p["mark"]}</b>')
        when = f'{y0}' + ("" if y1 == y0 else f' — {y1 if y1 else L(T("today", "heute"))}')
        out.append(f'        <a class="tl{" flip" if flip else ""}" href="#p-{slug}" style="--x:{X(y0):.2f}%;--w:{X(end) - X(y0):.2f}%;--lane:{lane}" '
                   f'title="{name} · {when}"><i class="bar"></i><span class="ico">{icon}</span><span class="nm mono">{name}</span></a>')
    years = "".join(f'<span style="--x:{X(y):.2f}%">{y}</span>' for y in range(TL_FROM, TL_TO, 2))
    return f'''      <div class="timeline" style="--lanes:{len(lanes)}">
        <div class="tl-rail">
{NL.join(out)}
          <div class="tl-axis mono" aria-hidden="true">{years}</div>
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
