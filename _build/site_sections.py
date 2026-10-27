"""Small shared editorial sections; publication data remain in assets/pubs.js."""
from html import escape
from urllib.parse import quote
import json
from pathlib import Path
import project_pages


def T(en, de):
    return {"en": en, "de": de}


def featured(lang):
    A = "../" if lang == "de" else ""
    entries = [
        ("macoco", "MaCoCo", "macoco.png",
         T("Project lead · in production at RWTH", "Projektleitung · produktiv an der RWTH"),
         T("Finances, staff and projects in one model-driven system, used by more than 200 chairs and institutes.", "Finanzen, Personal und Projekte in einem modellgetriebenen System, genutzt von über 200 Lehrstühlen und Instituten."),
         T("MaCoCo finance dashboard with demonstration data", "MaCoCo-Finanzübersicht mit Demodaten")),
        ("ford", T("Ford Pro tool tracking", "Ford Pro Werkzeugverfolgung"), "ford.png",
         T("Technical lead · industry pilot", "Technische Leitung · Industriepilot"),
         T("A generated web application connecting tools, vans and job sites. Field-tested by three trade companies.", "Eine generierte Webanwendung verbindet Werkzeuge, Transporter und Baustellen. Im Feld von drei Handwerksbetrieben getestet."),
         T("Ford Pro tool-tracking pilot", "Pilotprojekt zur Ford Pro Werkzeugverfolgung")),
        ("esaca", "ESACA", None,
         T("Current work · mgm technology partners", "Aktuelle Arbeit · mgm technology partners"),
         T("Agentic coding inside the enterprise: an on-premises platform for sandboxed agents and reviewed changes.", "Agentisches Programmieren im Unternehmen: eine On-Premises-Plattform für Agenten in der Sandbox und geprüfte Änderungen."), None),
    ]
    L = lambda x: x[lang] if isinstance(x, dict) else x
    rows = []
    for slug, name, image, role, text, alt in entries:
        visual = f'<div class="work-mark" aria-hidden="true"><img src="{A}assets/logos/{image or "esaca.svg"}" alt="" loading="lazy" decoding="async" width="100" height="100"></div>'
        rows.append(f'<li><a href="projects-{slug}.html">{visual}<div><span class="mono faint">{L(role)}</span><h3>{L(name)}</h3><p>{L(text)}</p><span class="mono work-link">{T("Read the case study", "Fallstudie lesen")[lang]} →</span></div></a></li>')
    return f'<section class="selected-work" aria-label="{T("Selected work", "Ausgewählte Projekte")[lang]}"><h2 class="group mono">{T("Selected work", "Ausgewählte Projekte")[lang]}</h2><ul>{"".join(rows)}</ul></section>'


def publications(lang):
    pubs = list(project_pages.PUBS.values())
    source = Path(__file__).with_name("paper-abstracts.json")
    abstracts = json.loads(source.read_text(encoding="utf8")).get("papers", {}) if source.exists() else {}
    out = []
    for year in sorted({p['year'] for p in pubs}, reverse=True):
        items = []
        for p in pubs:
            if p['year'] != year:
                continue
            item = project_pages.pub_list(lang, [p['key']], id_prefix='pub-')
            item = item.replace(f'id="pub-{p["key"]}"', f'id="pub-{p["key"]}" data-tags="{escape(" ".join(p["tags"]), quote=True)}"')
            url = 'https://scholar.google.com/scholar?q=' + quote('"' + p['title'] + '"')
            item = item.replace('<div class="plinks mono">', f'<div class="plinks mono"><a href="{url}" target="_blank" rel="noopener">scholar ↗</a>')
            abstract = abstracts.get(p['key'], {})
            if abstract.get('abstract') and abstract.get('title') == p['title']:
                label = T('Abstract source', 'Abstract-Quelle')[lang]
                detail = (f'<details class="pub-abstract"><summary class="mono">Abstract · {escape(abstract.get("language", "en").upper())}</summary>'
                          f'<p lang="{escape(abstract.get("language", "en"))}">{escape(abstract["abstract"])}</p>'
                          f'<a class="mono" href="{escape(abstract["source"], quote=True)}" target="_blank" rel="noopener">{label} ↗</a></details>')
                item = item.replace('<div class="plinks mono">', detail + '<div class="plinks mono">', 1)
            items.append(item)
        out.append(f'<div class="year"><h3 class="y mono">{year}</h3><ol class="pubs">{"".join(items)}</ol></div>')
    return ''.join(out)


def research_routes(lang):
    routes = [
        ('articles', T('Understand the ideas', 'Die Ideen verstehen'), T('Four introductions with interactive examples.', 'Vier Einführungen mit interaktiven Beispielen.')),
        ('publications', T('Find a publication', 'Eine Publikation finden'), T('Search papers by title, author or year.', 'Paper nach Titel, Autor oder Jahr suchen.')),
        ('citation-map', T('Explore the connections', 'Verbindungen erkunden'), T('Follow references and citations, as a map or a list.', 'Referenzen und Zitationen als Karte oder Liste erkunden.')),
    ]
    return '<nav class="research-routes" aria-label="' + T('Explore research', 'Forschung erkunden')[lang] + '">' + ''.join(
        f'<a href="#{anchor}"><b>{title[lang]} →</b><span>{text[lang]}</span></a>' for anchor, title, text in routes) + '</nav>'
