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
    """Same markup as the publication list on the research page (site.js)."""
    flags = {"Article": T("Article", "Artikel"), "Dissertation": T("Dissertation", "Dissertation")}
    items = []
    for k in keys:
        p = PUBS[k]
        links = []
        if p.get("pdf"): links.append(ext("pdf", p["pdf"]))
        if p.get("doi"): links.append(ext("doi", "https://doi.org/" + p["doi"]))
        if p.get("url"): links.append(ext(p.get("urlLabel", "link"), p["url"]))
        flag = f'<span class="flag mono">{flags[p["flag"]][lang]}</span>' if p.get("flag") else ""
        items.append(f'''        <li>
          <span class="key mono">{p["year"]}</span>
          <div>
            <div class="t">{p["title"]}{flag}</div>
            <div class="a">{p["authors"].replace("L. Netz", "<b>L. Netz</b>")}</div>
            <div class="v mono">{p["venue"]}</div>
            <div class="plinks mono">{"".join(links)}</div>
          </div>
        </li>''')
    return '      <ol class="pubs">' + NL + NL.join(items) + NL + '      </ol>'


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
{pub_list(lang, p["pubs"])}
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
