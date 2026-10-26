"""
The shared shell of the article series (research-mde/-ai4se/-dt/-ea.html): one source for the names, part numbers
and dates of the four parts (SERIES), the article header, the chapter list, the literature block with in-page
citations, the "next in the series" block, the research-page cards and the figure source line.

Each article module keeps only its content (body) and calls `page(...)` from its own page(). The style guide and
the API of these helpers are documented in _build/STYLE.md.

Citations: `cite(KEY)` (ai4se.cite, own papers) links to `#pub-KEY` and `ref(n)` / `r(key)` (literature) to `#ref-n`,
both on the same page. `page()` renumbers the literature by first citation, lists uncited literature as "further
reading" and lists only the own papers that are actually cited — so thinning citations never leaves orphans.
"""
import re
import sys

import article_art

NL = "\n"


def T(en, de):
    return {"en": en, "de": de}


# ---------------------------------------------------------------------------------------------------------------
# The series: one entry per part. long = h1, <title> and card title; short = series line and "next" block;
# abbr = phone bar ("EA · 02 Selection"); date = the date the article was written or revised (card and header);
# card = the teaser on the research page and in the "next in the series" block.
# ---------------------------------------------------------------------------------------------------------------
SERIES = [
    dict(file="research-mde.html", module="mde", part=1, thumb="mde", abbr="MDE",
         long=T("Model-Driven Software Engineering", "Modellgetriebene Softwareentwicklung"),
         short=T("Model-driven engineering", "Modellgetriebene Entwicklung"),
         date=T("2026", "2026"),
         card=T("What models, DSLs and generators are — and how MontiGem and CD2GUI turn one class diagram into a running web application.",
                "Was Modelle, DSLs und Generatoren sind — und wie MontiGem und CD2GUI aus einem Klassendiagramm eine laufende Webanwendung machen.")),
    dict(file="research-ai4se.html", module="ai4se", part=2, thumb="ai4se", abbr="AI4SE",
         long=T("AI-Driven Software Engineering", "KI-getriebene Softwareentwicklung"),
         short=T("AI in software engineering", "KI in der Softwareentwicklung"),
         date=T("2024, revised 2026", "2024, überarbeitet 2026"),
         card=T("How a language model arrives at its answer, what agents and harnesses are — and how LLMs write models that a generator turns into software.",
                "Wie ein Sprachmodell zu seiner Antwort kommt, was Agenten und Harnesses sind — und wie LLMs Modelle schreiben, aus denen ein Generator Software macht.")),
    dict(file="research-dt.html", module="dt", part=3, thumb="dt", abbr="DT",
         long=T("Digital Twins", "Digitale Zwillinge"),
         short=T("Digital twins", "Digitale Zwillinge"),
         date=T("2026", "2026"),
         card=T("What a digital twin is — and what it is not: the definition of RWTH’s Software Engineering group, digital shadows, how a twin acts, and how to build twins with models.",
                "Was ein digitaler Zwilling ist — und was nicht: die Definition der Software-Engineering-Gruppe der RWTH, digitale Schatten, wie ein Zwilling handelt und wie man Zwillinge mit Modellen baut.")),
    dict(file="research-ea.html", module="ea", part=4, thumb="ea", abbr="EA",
         long=T("Evolutionary Algorithms", "Evolutionäre Algorithmen"),
         short=T("Evolutionary algorithms", "Evolutionäre Algorithmen"),
         date=T("2026", "2026"),
         card=T("What evolutionary and genetic algorithms are, where they sit next to machine learning, and how selection, crossover and mutation work — with a wind farm and a hybrid car as case studies.",
                "Was evolutionäre und genetische Algorithmen sind, wo sie neben maschinellem Lernen stehen und wie Selektion, Crossover und Mutation funktionieren — mit einem Windpark und einem Hybridauto als Fallstudien.")),
]
_PUBLISHED = {"research-dt.html": lambda: article_art.DT_PUBLISHED, "research-ea.html": lambda: article_art.EA_PUBLISHED}


def entry(file):
    return next(e for e in SERIES if e["file"] == file)


def published(here=None):
    """The parts that are linked from anywhere (an unpublished part still sees itself)."""
    return [e for e in SERIES if _PUBLISHED.get(e["file"], lambda: True)() or e["file"] == here]


# ---------------------------------------------------------------------------------------------------------------
# Small drawings for the cards (accent = the key idea). DT and EA come from their figure modules (lazy imports:
# those modules import ai4se, which imports this module).
# ---------------------------------------------------------------------------------------------------------------
_THUMBS = {
    # a class diagram → a generator (two interlocking gears) → three generated pages
    "mde": '''<rect class="b" x="14" y="30" width="62" height="58" rx="2"/><path d="M14 46H76M22 58H62M22 70H54"/>
      <path class="a" d="M80 64H102"/><path class="a" d="M96 58L102 64L96 70"/>
      <path class="a gear" d="M140.7 61.1L144.9 61.7L144.9 66.3L140.7 66.9L139.1 71.3L141.9 74.3L139.0 77.9L135.4 75.7L131.4 78.0L131.6 82.2L127.0 83.0L125.7 79.0L121.1 78.2L118.6 81.5L114.6 79.2L116.2 75.3L113.1 71.7L109.1 72.6L107.5 68.3L111.2 66.3L111.2 61.7L107.5 59.7L109.1 55.4L113.1 56.3L116.2 52.7L114.6 48.8L118.6 46.5L121.1 49.8L125.7 49.0L127.0 45.0L131.6 45.8L131.4 50.0L135.4 52.3L139.0 50.1L141.9 53.7L139.1 56.7Z"/><circle class="a" cx="126" cy="64" r="5"/>
      <path class="gear" d="M158.3 41.7L161.0 43.3L159.5 46.5L156.5 45.4L153.9 47.6L154.3 50.7L150.8 51.5L149.8 48.5L146.5 47.7L144.3 50.0L141.5 47.8L143.2 45.1L141.8 42.1L138.6 41.8L138.6 38.2L141.8 37.9L143.2 34.9L141.5 32.2L144.3 30.0L146.5 32.3L149.8 31.5L150.8 28.5L154.3 29.3L153.9 32.4L156.5 34.6L159.5 33.5L161.0 36.7L158.3 38.3Z"/><circle cx="150" cy="40" r="3"/>
      <path class="a" d="M150 64H170"/><path class="a" d="M164 58L170 64L164 70"/>
      <rect class="b" x="176" y="22" width="50" height="34" rx="2"/><rect class="b" x="182" y="44" width="50" height="34" rx="2"/><rect class="b f" x="188" y="66" width="44" height="30" rx="2"/>
      <path d="M194 76H224M194 84H216"/>''',
    # a small neural network → the probability of the next token
    "ai4se": '''<path d="M24 34L70 26M24 34L70 58M24 34L70 90M24 84L70 26M24 84L70 58M24 84L70 90M70 26L116 44M70 58L116 44M70 90L116 44M70 26L116 76M70 58L116 76M70 90L116 76"/>
      <circle class="b" cx="24" cy="34" r="6"/><circle class="b" cx="24" cy="84" r="6"/><circle class="b" cx="70" cy="26" r="6"/><circle class="b" cx="70" cy="58" r="6"/><circle class="b" cx="70" cy="90" r="6"/>
      <circle class="b f" cx="116" cy="44" r="7"/><circle class="b" cx="116" cy="76" r="7"/>
      <path class="a" d="M128 59H146"/><path class="a" d="M140 53L146 59L140 65"/>
      <rect class="f" x="156" y="28" width="68" height="9" rx="1"/><rect class="g" x="156" y="45" width="22" height="9" rx="1"/><rect class="g" x="156" y="62" width="12" height="9" rx="1"/><rect class="g" x="156" y="79" width="7" height="9" rx="1"/>''',
}


def thumb(key):
    if key == "dt":
        import dt_figs                          # a machine ⇄ its twin
        return dt_figs.thumb_dt()
    if key == "ea":
        import ea_figs                          # the running example and its stepped best-fitness curve
        return ea_figs.thumb_ea()
    return _THUMBS[key]


# ---------------------------------------------------------------------------------------------------------------
# Counting figures: the card says how many interactive figures (figure.demo) the page really has.
# ---------------------------------------------------------------------------------------------------------------
_PAGES = {}


def _page_html(file, lang):
    if (file, lang) not in _PAGES:
        import importlib
        _PAGES[(file, lang)] = importlib.import_module(entry(file)["module"]).page(lang)[3]
    return _PAGES[(file, lang)]


def count_demos(html_):
    return len(re.findall(r'<figure class="[^"]*\bdemo\b', html_))


def card(lang, e, figures=True):
    """A card of the research page (and of the next-in-the-series block)."""
    L = lambda x: x[lang]
    more = (f'{count_demos(_page_html(e["file"], lang))} {L(T("interactive figures", "interaktive Abbildungen"))} · ' if figures else "")
    return f'''        <li>
          <a href="{e["file"]}">
            <svg class="thumb" viewBox="0 0 240 118" aria-hidden="true">{thumb(e["thumb"])}</svg>
            <span class="meta mono">{L(T("Part", "Teil"))} {e["part"]} · {L(e["date"])}</span>
            <span class="title">{L(e["long"])}</span>
            <span class="text">{L(e["card"])}</span>
            <span class="more mono">{more}{L(T("read", "lesen"))} →</span>
          </a>
        </li>'''


def cards(lang):
    """All published parts as research-page cards."""
    return NL.join(card(lang, e) for e in published())


def link(file, lang, anchor=""):
    """'Part N · Title' for links from elsewhere (project pages, cross references)."""
    e = entry(file)
    return f'{T("Part", "Teil")[lang]} {e["part"]} · {e["long"][lang]}'


def art_link(lang, file, anchor=""):
    """The one component that points from a project page to an article: 'Background: Part N · Title →'."""
    e = entry(file)
    if e not in published():
        return ""
    return (f'<p class="art-link mono"><a href="{file}{"#" + anchor if anchor else ""}"><span>{T("Background", "Hintergrund")[lang]}:</span> '
            f'{link(file, lang)} →</a></p>')


# ---------------------------------------------------------------------------------------------------------------
# Sections: the article modules list (id, level, heading, html[, nav label]) and get the same markup everywhere.
#   level 2 = numbered chapter (h2 "01 …"), 3 = sub chapter (h3), 1 = closing chapter (h2, unnumbered: "In short"),
#   0 = untitled block (intro). The optional 5th element is a T() short label for the side nav (data-nav).
# ---------------------------------------------------------------------------------------------------------------
def sections(S, lang):
    out, n = [], 0
    for item in S:
        sid, level, head, html_ = item[:4]
        nav = item[4] if len(item) > 4 else None
        name = head[lang] if isinstance(head, dict) else head
        dn = f' data-nav="{(nav[lang] if isinstance(nav, dict) else nav)}"' if nav else ""
        if level == 2:
            n += 1
            out.append(f'      <section class="art-sec art-ch"><h2 id="{sid}"{dn}><span class="mono">{n:02d}</span>{name}</h2>{html_}</section>')
        elif level == 1:
            out.append(f'      <section class="art-sec art-ch"><h2 id="{sid}"{dn}>{name}</h2>{html_}</section>')
        else:
            h = f'<h3 id="{sid}"{dn}>{name}</h3>' if head else ""
            out.append(f'      <section class="art-sec">{h}{html_}</section>')
    return NL.join(out)


def _chapters(html_):
    """[(id, number or '', name)] of the h2s in the article, in order."""
    out = []
    for sid, attrs, num, name in re.findall(r'<h2 id="([^"]+)"([^>]*)>(?:<span class="mono">(\d+)</span>)?(.*?)</h2>', html_):
        m = re.search(r'data-nav="([^"]*)"', attrs)
        out.append((sid, num, m.group(1) if m else re.sub(r"<[^>]+>", "", name)))
    return out


# ---------------------------------------------------------------------------------------------------------------
# Figure source line (one format for every caption): After [KEY], Fig. 3 · Data: [KEY], Table 2 · Illustrative
# ---------------------------------------------------------------------------------------------------------------
_SRC = {"after": T("After", "Nach"), "data": T("Data:", "Daten:"), "from": T("From", "Aus"),
        "illustrative": T("Illustrative", "Illustrativ"), "fictional": T("Fictional data", "Fiktive Daten")}
_WHERE = [("Figs.", "Abb."), ("Fig.", "Abb."), ("Tables", "Tabellen"), ("Table", "Tabelle"), ("Listing", "Listing"),
          ("ch.", "Kap."), ("p.", "S.")]


def src(kind, *keys, where=None, note=None):
    """A figure's source line as T(): kind 'after' | 'data' | 'from' | 'illustrative' | 'fictional'.
    keys: own-paper keys (cited with cite()) or ints (literature numbers, ref()); where: 'Fig. 3', '§6.3', 'Table 2'
    (EN; translated to Abb./Tabelle/Kap. for DE) or a T(); note: an extra T() appended after ' · '.
    Examples: src('after', 'Net24', where='Fig. 2.4') · src('data', 'NWN+15', where='Table 2') · src('illustrative')."""
    from ai4se import cite, ref
    out = {}
    for lang in ("en", "de"):
        who = ", ".join(ref(k) if isinstance(k, int) else cite(k) for k in keys)
        w = where[lang] if isinstance(where, dict) else where
        if w and lang == "de":
            for en, de in _WHERE:
                w = w.replace(en, de)
        parts = [_SRC[kind][lang]] + ([who] if who else [])
        s = " ".join(parts) + (f", {w}" if w else "")
        if note:
            s += f" · {note[lang]}"
        out[lang] = s
    return out


def source_line(source, lang):
    """The final mono line of a caption (fig()/demo() add it when given source=)."""
    if not source:
        return ""
    return f'<span class="src">{source[lang] if isinstance(source, dict) else source}</span>'


# ---------------------------------------------------------------------------------------------------------------
# Literature: in-page numbering by first citation; own papers with an in-page id and a link to the full list.
# ---------------------------------------------------------------------------------------------------------------
_Q = r'(?:"|\\&quot;)'                      # a quote: plain, or as escaped inside a demo's data-json
_REF = r'#ref-(\d+)(?=' + _Q + ')'
_PUB = r'href=' + _Q + r'#pub-([^"\\&]+)'
_CITE = r'(class=' + _Q + 'cite' + _Q + ' href=' + _Q + r'#ref-)(\d+)(' + _Q + r'(?:>|&gt;)\[)\d+\]'
_ORDER = {}               # file → literature numbers in the order of first citation in the English text


def _warn(msg):
    print(f"article_common: {msg}", file=sys.stderr)


def _literature(lang, file, html_, refs, own):
    """Returns (html with renumbered [n], the literature section)."""
    from project_pages import pub_list
    L = lambda x: x[lang]
    items = dict((int(k), t) for k, t in re.findall(r'<li id="ref-(\d+)">(.*?)</li>', refs))
    order = []
    for k in re.findall(_REF, html_):
        k = int(k)
        if k not in order:
            order.append(k)
    # both languages share the numbers: German follows the English order (built first), extra cites go last
    if lang == "en":
        _ORDER[file] = order
    elif file in _ORDER:
        base = _ORDER[file]
        if set(base) != set(order):
            _warn(f"{file}: EN and DE cite different literature: {sorted(set(base) ^ set(order))}")
        order = [k for k in base if k in order] + [k for k in order if k not in base]
    missing = [k for k in order if k not in items]
    assert not missing, f"{file}: cited literature without an entry: {missing}"
    new = {old: i + 1 for i, old in enumerate(order)}
    # one pass for [n] links (number and text), one for any other link to #ref-n; "~" marks what is done.
    # Both also match the escaped form inside a demo's data-json (\&quot; instead of ").
    html_ = re.sub(_CITE, lambda m: f'{m[1]}~{new[int(m[2])]}{m[3]}{new[int(m[2])]}]', html_)
    html_ = re.sub(_REF, lambda m: f'#ref-~{new[int(m[1])]}', html_).replace("#ref-~", "#ref-")
    cited = "".join(f'<li id="ref-{new[k]}">{items[k]}</li>' for k in order)
    rest = [items[k] for k in sorted(items) if k not in new]
    further = (f'<div class="refs-more mono">{L(T("Further reading", "Weiterführend"))}</div><ul class="refs more mono">'
               + "".join(f"<li>{t}</li>" for t in rest) + "</ul>") if rest else ""

    keys = []
    for k in re.findall(_PUB, html_):
        if k not in keys:
            keys.append(k)
    stray = [k for k in keys if k not in own]
    if stray:
        _warn(f"{file}: cited own papers not in OWN (listed at the end): {stray}")
    dropped = [k for k in own if k not in keys]
    if dropped and lang == "en":
        _warn(f"{file}: own papers in OWN but never cited (not listed): {dropped}")
    listed = [k for k in own if k in keys] + stray
    eg = listed[0] if listed else "Net24"
    key_line = (f'<p class="refs-key mono">{L(T(f"[1] literature · [{eg}] my papers on the topic",
                                                 f"[1] Literatur · [{eg}] eigene Arbeiten zum Thema"))}</p>')
    pubs = (f'''        <div class="group mono">{L(T("My papers on the topic", "Eigene Arbeiten zum Thema"))}</div>
        <ol class="pubs">
{pub_list(lang, listed, id_prefix="pub-", full_list=True)}
        </ol>''') if listed else ""
    sec = f'''      <section class="art-sec art-ch art-refs">
        <h2 id="literature">{L(T("Literature", "Literatur"))}</h2>
        {key_line}
        <ol class="refs mono">{cited}</ol>
        {further}
{pubs}
      </section>'''
    return html_, sec


# ---------------------------------------------------------------------------------------------------------------
# Header, series line, end of the article
# ---------------------------------------------------------------------------------------------------------------
def series_line(lang, here):
    parts = published(here)
    items = []
    for e in parts:
        nm = f'<span class="n">{e["part"]}</span><span class="nm">{e["short"][lang]}</span>'
        if e["file"] == here:
            items.append(f'<span aria-current="page">{nm}</span>')
        else:
            items.append(f'<a href="{e["file"]}" title="{T("Part", "Teil")[lang]} {e["part"]} · {e["long"][lang]}">{nm}</a>')
    return f'<p class="art-series mono"><span class="k">{T("Series", "Reihe")[lang]}</span>{"".join(items)}</p>'


def header(lang, file, html_, lead):
    L = lambda x: x[lang]
    e, parts = entry(file), published(file)
    chap = "".join(f'<a href="#{sid}">{f"<span class=\"n\">{num}</span>" if num else ""}{name}</a>' for sid, num, name in _chapters(html_))
    return f'''
    <header class="page proj art-head" data-abbr="{e["abbr"]}">
      <a class="back mono" href="research.html#articles">← {L(T("all articles", "alle Artikel"))}</a>
      <div class="section-head">
        <h1><span class="mono">{e["part"]} / {len(parts)}</span>{L(e["long"])}</h1>
        <span class="mono faint">{L(T("article", "Artikel"))} · {L(e["date"])}</span>
      </div>
      <p class="lead">{L(lead)}</p>
      {series_line(lang, file)}
      <nav class="chapters mono" aria-label="{L(T("Chapters", "Kapitel"))}">{chap}</nav>
    </header>'''


def series_end(lang, file):
    """After the literature: the next part as a card, and a line back to the previous part and to all articles."""
    L = lambda x: x[lang]
    parts = published(file)
    i = next(k for k, e in enumerate(parts) if e["file"] == file)
    nxt = parts[i + 1] if i + 1 < len(parts) else None
    prev = parts[i - 1] if i > 0 else None
    show, label = (nxt, T("Next in the series", "Weiter in der Reihe")) if nxt else (parts[0], T("Back to the start of the series", "Zurück zum Anfang der Reihe"))
    links = []
    if prev:
        links.append(f'<a href="{prev["file"]}">← {L(T("previous part", "vorheriger Teil"))} · {L(prev["long"])}</a>')
    links.append(f'<a href="research.html#articles">← {L(T("all articles", "alle Artikel"))}</a>')
    return f'''
    <nav class="art-end" aria-label="{L(T("Article series", "Artikelreihe"))}">
      <div class="group mono">{L(label)}</div>
      <ul class="articles">
{card(lang, show, figures=False)}
      </ul>
      <p class="art-end-links mono">{"".join(links)}</p>
    </nav>'''


def scripts(lang, name, css=False):
    """The article's scripts: the shared demo helpers (assets/demo-common.js) first, then its own."""
    A = "../" if lang == "de" else ""
    return ((f'<link rel="stylesheet" href="{A}assets/{name}.css">\n' if css else "")
            + f'<script src="{A}assets/demo-common.js"></script>\n<script src="{A}assets/{name}.js"></script>\n')


# ---------------------------------------------------------------------------------------------------------------
# Share links: every chapter, sub chapter and figure gets a short anchor to pass on — mde-2 (chapter 02), mde-2.1
# (its first sub chapter), mde-f3 (third figure) — and a small link icon that shows on hover; site.js copies the
# link on click. The labels follow the order of the article, so they move when chapters or figures are added.
# ---------------------------------------------------------------------------------------------------------------
_SHARE = {"AI4SE": "ai"}
_SHARE_ICON = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M6.5 9.5l3-3M7 4.5l1.3-1.3a2.6 2.6 0 0 1 3.7 3.7L10.7 8.2'
               'M9 11.5l-1.3 1.3a2.6 2.6 0 0 1-3.7-3.7L5.3 7.8"/></svg>')


def share_links(lang, file, html_):
    e = entry(file)
    p = _SHARE.get(e["abbr"], e["abbr"].lower())
    what = {"sec": T("section", "Abschnitt")[lang], "fig": T("figure", "Abbildung")[lang]}
    ch, sub, fig = 0, 0, 0

    def link(key, kind):
        return (f'<a class="share" href="#{key}" data-share="{key}" aria-label="{T("Copy link to", "Link kopieren:")[lang]} '
                f'{what[kind]} {key}">{_SHARE_ICON}</a>')

    def heading(m):
        nonlocal ch, sub
        tag, attrs, num, inner = m.group(1), m.group(2), m.group(3), m.group(4)
        sid = re.search(r'id="([^"]+)"', attrs).group(1)
        if sid == "literature":
            return m.group(0)
        if tag == "h2":
            ch, sub = (int(num), 0) if num else (ch, sub)
            key = f"{p}-{ch}" if num else f"{p}-{sid}"
        else:
            sub += 1
            key = f"{p}-{ch}.{sub}"
        lead = f'<span class="mono">{num}</span>' if num else ""
        return f'<{tag}{attrs}>{lead}<span class="share-at" id="{key}"></span>{inner}{link(key, "sec")}</{tag}>'

    html_ = re.sub(r'<(h[23])( id="[^"]+"[^>]*)>(?:<span class="mono">(\d+)</span>)?(.*?)</\1>', heading, html_, flags=re.S)

    # figures: id on the <figure>, the link at the end of its caption (nested figures are left alone)
    out, pos = [], 0
    for m in re.finditer(r'<figure( class="([^"]*)")?[^>]*>', html_):
        if m.start() < pos or "art-hero" in (m.group(2) or ""):
            continue
        end = html_.find("</figure>", m.end())
        body = html_[m.end():end]
        cap = body.rfind("</figcaption>")
        if end < 0 or "<figure" in body or cap < 0:
            continue
        s = body.rfind('<span class="src"', body.rfind("<figcaption", 0, cap), cap)
        cap = s if s >= 0 else cap                                   # before the source line, if there is one
        fig += 1
        key = f"{p}-f{fig}"
        out.append(html_[pos:m.start()])
        out.append(m.group(0)[:-1] + f' id="{key}">' + body[:cap] + link(key, "fig") + body[cap:])
        pos = end
    out.append(html_[pos:])
    return "".join(out)


def page(lang, file, sections_html, refs, own, hero, lead, desc, script):
    """The whole article page for build.py: returns (file, title, description, body, scripts).
    sections_html: the rendered sections (sections()); refs: '<li id="ref-n">…</li>' items in the module's numbering;
    own: keys of own papers that may be cited; hero: the hero figure html; lead: T() with the lead sentence."""
    body_html, lit = _literature(lang, file, sections_html, refs, own)
    head = header(lang, file, body_html + lit, lead)
    body_html = share_links(lang, file, body_html)
    html_ = f'''{head}
    {hero}
    <article class="article">
{body_html}
{lit}
    </article>
{series_end(lang, file)}
'''
    return file, entry(file)["long"], desc, html_, script
