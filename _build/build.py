"""
Builds the static site in two languages.

    python _build/build.py

English pages go to the repository root, German pages to /de/.
Every user-facing text is written as T("english", "deutsch").
Publications live in assets/pubs.js; shared behaviour in assets/site.js.
(GitHub Pages ignores folders starting with "_", so this script is not published.)
"""
import os

import project_pages

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = {"en": "", "de": "de"}          # language -> output sub-folder
NL = "\n"


def T(en, de):
    return {"en": en, "de": de}


# =====================================================================
# Page shell (identical frame on every page)
# =====================================================================

PAGES = [
    ("index.html", "00", T("About", "Über mich")),
    ("projects.html", "01", T("Projects", "Projekte")),
    ("research.html", "02", T("Research", "Forschung")),
    ("photography.html", "03", T("Photography", "Fotografie")),
]

SOCIAL = [
    ("LinkedIn", "https://www.linkedin.com/in/lukas-netz/"),
    ("Google Scholar", "https://scholar.google.com/citations?user=5mVkoWsAAAAJ&amp;hl=en"),
    ("ResearchGate", "https://www.researchgate.net/profile/Lukas-Netz"),
    ("ORCID", "https://orcid.org/0000-0003-2013-2919"),
    ("dblp", "https://dblp.org/pid/170/5042.html"),
    ("GitHub", "https://github.com/LNetz"),
]


def shell(lang, file, title, desc, body, scripts=""):
    L = lambda x: x[lang] if isinstance(x, dict) else x
    A = "../" if lang == "de" else ""                 # path back to the shared assets
    en_url, de_url = (file, f"de/{file}") if lang == "en" else (f"../{file}", file)

    nav = NL.join(
        f'        <li><a href="{f}"{" class=\"active\" aria-current=\"page\"" if file.split("-")[0].removesuffix(".html") == f.removesuffix(".html") else ""}>'
        f'<span>{n}</span><span>{L(t)}</span></a></li>'
        for f, n, t in PAGES)
    social = NL.join(f'      <a href="{u}" target="_blank" rel="noopener">{name} ↗</a>' for name, u in SOCIAL)
    full_title = "Lukas Netz" if file == "index.html" else f"{L(title)} — Lukas Netz"
    foot_icons = "".join(f'<a href="{f}" title="{L(t)}" aria-label="{L(t)}">{ICONS[i]}</a>' for f, i, t in QUICK)
    # easter egg: Connect Four, not in the navigation — only this little diagonal of four dots
    foot_icons += (f'<a class="egg" href="{A}vier-gewinnt/" title="{L(T("Play", "Spielen"))}" '
                   f'aria-label="{L(T("Play", "Spielen"))}">{ICONS["game"]}</a>')
    langs = (f'<a href="{"" if lang == "en" else "../"}{file}" hreflang="en" lang="en"{" aria-current=\"true\"" if lang == "en" else ""}>EN</a>'
             f'<a href="{"de/" if lang == "en" else ""}{file}" hreflang="de" lang="de"{" aria-current=\"true\"" if lang == "de" else ""}>DE</a>')

    return f'''<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{full_title}</title>
  <meta name="description" content="{L(desc)}">
  <meta property="og:title" content="{full_title}">
  <meta property="og:description" content="{L(desc)}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="{"en_US" if lang == "en" else "de_DE"}">
  <link rel="alternate" hreflang="en" href="{en_url}">
  <link rel="alternate" hreflang="de" href="{de_url}">
  <link rel="icon" href="{A}assets/favicon.svg" type="image/svg+xml">
  <script>
    // Theme preference in localStorage: "light" (default), "dark" or "auto" (follows the OS).
    // Applied before first paint (no flash); re-applied on pageshow (back/forward cache)
    // and whenever the OS switches while "auto" is chosen.
    (function () {{
      var os = matchMedia("(prefers-color-scheme: dark)");
      function apply() {{
        var p = null;
        try {{ p = localStorage.getItem("theme"); }} catch (_) {{}}
        if (p !== "dark" && p !== "auto") p = "light";
        var root = document.documentElement;
        root.dataset.themePref = p;
        root.dataset.theme = p === "auto" ? (os.matches ? "dark" : "light") : p;
      }}
      window.applyTheme = apply;
      apply();
      // build-up animation (style.css, .anim) unless the OS asks for reduced motion;
      // the index column only builds up on the first page of a visit (.returning afterwards)
      if (!matchMedia("(prefers-reduced-motion: reduce)").matches) document.documentElement.classList.add("anim");
      try {{
        if (sessionStorage.getItem("seen")) document.documentElement.classList.add("returning");
        sessionStorage.setItem("seen", "1");
      }} catch (_) {{}}
      addEventListener("pageshow", apply);
      os.addEventListener("change", apply);
    }})();
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{A}assets/style.css">
</head>
<body id="top">
<div class="backdrop" aria-hidden="true"></div>
<div class="frame">

  <!-- ============ index column (identical on every page) ============
       Desktop: sticky left column.  ≤ 900px: sticky top bar; the menu
       (pages, profiles, language, theme) opens as a full-screen sheet. -->
  <aside class="index" id="index">
    <div class="bar">
      <div class="who">
        <a class="name" href="index.html">Lukas Netz</a>
        <span class="here mono" aria-hidden="true">{L(title)}</span>
        <div class="role">Dr. rer. nat.<br>{L(T("IT Specialist", "IT-Spezialist"))}<br>mgm technology partners</div>
      </div>
      <button class="menu-toggle mono" type="button" id="menu-toggle" aria-expanded="false" aria-controls="menu">{L(T("menu", "Menü"))}</button>
    </div>

    <div class="menu" id="menu">
      <nav aria-label="{L(T("Pages", "Seiten"))}">
        <ol class="mono">
{nav}
        </ol>
      </nav>

      <div class="contact mono">
{social}
      </div>

      <div class="prefs mono">
        <div class="lang" aria-label="{L(T("Language", "Sprache"))}">{langs}</div>
        <button class="theme-toggle" type="button" id="theme">◐ <span>{L(T("light", "hell"))}</span></button>
      </div>
    </div>
  </aside>

  <!-- ============ content ============ -->
  <main>
{body}
    <footer class="mono">
      <span>© 2026 Lukas Netz.</span>
      <nav class="foot-icons" aria-label="{L(T("Sections", "Bereiche"))}">{foot_icons}</nav>
      <a href="#top">↑ {L(T("top", "nach oben"))}</a>
    </footer>
  </main>
</div>
{scripts}<script src="{A}assets/site.js"></script>
</body>
</html>
'''


# =====================================================================
# Building blocks
# =====================================================================

def page_head(n, title, right, lead, extra="", count_id=False, top=""):
    rid = ' id="pub-count"' if count_id else ''
    return f'''    <header class="page">
      <div class="section-head">
        <h1><span class="mono">{n}</span>{title}</h1>
        <span class="mono faint"{rid}>{right}</span>
      </div>{top}
      <p class="lead">{lead}</p>{extra}
    </header>
'''


def quick_nav(lang):
    """The three section icons (Projects, Research, Photography) as links — About page."""
    links = NL.join(
        f'        <a href="{href}" title="{label[lang]}" aria-label="{label[lang]}">{ICONS[icon]}</a>'
        for href, icon, label in QUICK)
    return f'''
      <nav class="quick" aria-label="{T("Sections", "Bereiche")[lang]}">
{links}
      </nav>'''


def page_icon(icon):
    """A sub-page's own icon under its title (decorative)."""
    return f'\n      <div class="page-icon" aria-hidden="true">{ICONS[icon]}</div>'


def banner(A, src, alt, w, h):
    """Panorama hero; phones get a taller 4:3 crop (same name with a -m suffix)."""
    mobile = src.replace(".jpg", "-m.jpg")
    return (f'    <figure class="banner"><picture>'
            f'<source media="(max-width: 600px)" srcset="{A}assets/photos/{mobile}" width="1200" height="900">'
            f'<img src="{A}assets/photos/{src}" alt="{alt}" width="{w}" height="{h}">'
            f'</picture></figure>\n')


def link(label, url):
    return f'<a href="{url}" target="_blank" rel="noopener">{label} ↗</a>'


def spec(A, when, name, what, tags, meta, links=(), href=None, logo=None, mark=None, more=None):
    # more = the project's own page (projects-<slug>.html): the name links there, plus a "more" link
    h = f'<a href="{href}" target="_blank" rel="noopener">{name}</a>' if href else name
    if more:
        h = f'<a class="int" href="{more[0]}">{name}</a>'
    t = "".join(f"<span>{x}</span>" for x in tags)
    l = "".join(link(lbl, u) for lbl, u in links)
    if more:
        l = f'<a class="more" href="{more[0]}">{more[1]} →</a>' + l
    m = "".join(f"<div>{x}</div>" for x in meta)
    extra = ""
    if t: extra += f'\n            <div class="tags mono">{t}</div>'
    if l: extra += f'\n            <div class="links mono">{l}</div>'
    if logo:
        badge = f'<span class="logo"><img src="{A}assets/logos/{logo}" alt="" width="48" height="48"></span>'
    else:
        badge = f'<span class="logo mark mono" aria-hidden="true">{mark}</span>' if mark else ''
    return f'''        <li>
          <div class="side">{badge}<span class="mono faint">{when}</span></div>
          <div>
            <h3>{h}</h3>
            <p class="what">{what}</p>{extra}
          </div>
          <div class="meta mono">{m}</div>
        </li>'''


def row(label, title, text, role="", links=()):
    r = f' <span class="mono faint role">{role}</span>' if role else ""
    l = f'\n            <div class="links mono">{"".join(link(a, b) for a, b in links)}</div>' if links else ""
    return f'''        <li>
          <div class="mono faint">{label}</div>
          <div>
            <h3>{title}{r}</h3>
            <p>{text}</p>{l}
          </div>
        </li>'''


# =====================================================================
# 00 About
# =====================================================================

# Line icons on a 24px grid, round caps, stroke = currentColor (works in both themes).
_SVG = '<svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">{}</svg>'
ICONS = {
    # gamepad — footer easter egg (leads to the Connect Four game)
    "game": '<svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M7 7.5h10a4.5 4.5 0 0 1 4.5 4.5v1.8a3.2 3.2 0 0 1-5.8 1.9l-1.2-1.7h-5l-1.2 1.7a3.2 3.2 0 0 1-5.8-1.9V12A4.5 4.5 0 0 1 7 7.5z"/>'
            '<path d="M7.5 10v3.5M5.75 11.75h3.5"/><path d="M15.5 10.75h.01M17.5 12.75h.01" stroke-width="2.4"/></svg>',
    # </>  — software projects
    # optically matched to the other two (~19x15 of the 24 grid): compact brackets, air around the slash
    "code": _SVG.format('<path d="M7.5 7L2.5 12l5 5"/><path d="M16.5 7l5 5-5 5"/><path d="M14 4.5l-4 15"/>'),
    # √x  — research
    "sqrt": _SVG.format('<path d="M2.5 13.5H5l3.5 6.5L13.5 4h8"/><path d="M14.5 10l5 6"/><path d="M19.5 10l-5 6"/>'),
    # camera (Camera01) — photography
    # scaled to 90% (stroke compensated): its closed body otherwise reads as the largest of the three
    "camera": _SVG.format('<g transform="translate(12 12) scale(.9) translate(-12 -12)" stroke-width="1.95"><path d="M12.697 3.5h-1.394c-.715 0-1.072 0-1.392.112a2 2 0 0 0-.545.292c-.271.204-.47.501-.866 1.096c-.203.305-.502.753-.621.879a2 2 0 0 1-1.106.591c-.17.03-.353.03-.72.03c-.98 0-1.47 0-1.87.113a3 3 0 0 0-2.07 2.07C2 9.083 2 9.573 2 10.553V14.5c0 2.828 0 4.243.879 5.121S5.172 20.5 8 20.5h8c2.829 0 4.243 0 5.122-.879C22 18.743 22 17.328 22 14.5v-3.946c0-.98 0-1.47-.113-1.871a3 3 0 0 0-2.07-2.07c-.4-.113-.89-.113-1.87-.113c-.366 0-.55 0-.72-.03a2 2 0 0 1-1.105-.591c-.12-.126-.419-.574-.622-.879c-.396-.595-.594-.892-.865-1.096a2 2 0 0 0-.545-.292c-.32-.112-.678-.112-1.393-.112"/>'
                          '<path d="M16 13a4 4 0 1 1-8 0a4 4 0 0 1 8 0"/><path d="M19.125 9.5H19m.25 0a.25.25 0 1 1-.5 0a.25.25 0 0 1 .5 0Z"/></g>'),
}


QUICK = [("projects.html", "code", T("Projects", "Projekte")),
         ("research.html", "sqrt", T("Research", "Forschung")),
         ("photography.html", "camera", T("Photography", "Fotografie"))]


def about(lang):
    L = lambda x: x[lang]
    A = "../" if lang == "de" else ""
    facts = f'''
      <dl class="facts mono">
        <div><dt>{L(T("Now", "Jetzt"))}</dt><dd>mgm technology partners</dd></div>
        <div><dt>{L(T("PhD", "Promotion"))}</dt><dd>RWTH Aachen, 2024</dd></div>
        <div><dt>{L(T("Focus", "Fokus"))}</dt><dd>MDE × LLM</dd></div>
      </dl>'''
    esaca = link("ESACA", "https://esaca.eu")
    mdei = link("MDE Intelligence", "https://mde-intelligence.github.io/")
    bio = [
        T(f"I am an IT specialist at <b>mgm technology partners</b>, working on {esaca} — a sovereign, on-premises platform for agentic coding in regulated enterprises.",
          f"Ich bin IT-Spezialist bei <b>mgm technology partners</b> und arbeite an {esaca} — einer souveränen On-Premises-Plattform für agentisches Programmieren in regulierten Unternehmen."),
        T("Before that I spent several years at the <b>Software Engineering chair of RWTH Aachen University</b>, where I received my doctorate in 2024 with a thesis on model-driven development of full-size web-based information systems. I led the MaCoCo project, built generator-based systems that are still in production, and researched how LLMs can produce syntactically and semantically valid models.",
          "Davor war ich mehrere Jahre am <b>Lehrstuhl für Software Engineering der RWTH Aachen</b>, wo ich 2024 mit einer Arbeit über die modellgetriebene Entwicklung vollwertiger webbasierter Informationssysteme promoviert habe. Ich habe das Projekt MaCoCo geleitet, generatorbasierte Systeme gebaut, die bis heute produktiv laufen, und erforscht, wie LLMs syntaktisch und semantisch valide Modelle erzeugen können."),
        T(f"In 2026 I co-organized {mdei}, the workshop on AI and model-driven engineering at MODELS. Outside of work I enjoy photography and flying my drone.",
          f"2026 habe ich {mdei} mitorganisiert, den Workshop zu KI und modellgetriebener Softwareentwicklung auf der MODELS. In meiner Freizeit fotografiere ich gern und fliege Drohne."),
    ]
    head = page_head("00", L(T("About", "Über mich")), "",
        L(T("I build software that builds software. My work sits between <em>model-driven engineering</em> and <em>large language models</em>: generators, DSLs and agentic tooling that turn models and intent into full-size, maintainable applications.",
            "Ich baue Software, die Software baut. Meine Arbeit liegt zwischen <em>modellgetriebener Softwareentwicklung</em> und <em>großen Sprachmodellen</em>: Generatoren, DSLs und agentische Werkzeuge, die aus Modellen und Absichten vollwertige, wartbare Anwendungen machen.")),
        facts)
    return f'''
{head}    <section>{quick_nav(lang)}
      <div class="bio">
{NL.join(f"        <p>{L(p)}</p>" for p in bio)}
      </div>
    </section>
'''


# =====================================================================
# 01 Projects
# =====================================================================

def projects(lang):
    L = lambda x: x[lang] if isinstance(x, dict) else x
    A = "../" if lang == "de" else ""
    S = lambda when, name, what, tags, meta, **kw: spec(
        A, L(when), L(name), L(what), [L(t) for t in tags], [L(m) for m in meta],
        links=[(L(a), b) for a, b in kw.pop("links", ())],
        more=(f"projects-{kw.pop('page')}.html", L(T("more about the project", "mehr zum Projekt"))) if "page" in kw else None, **kw)

    PROD = T("In production", "Produktiv")
    IND = T("Industry partner", "Industriepartner")
    LEAD = T("Lead developer", "Leitende Entwicklung")
    INFOSYS = T("Information system", "Informationssystem")

    esaca = S(T("now", "jetzt"), "ESACA",
        T("European Sovereign Agentic Coding Appliance — a standardised, on-premises platform that runs AI coding agents inside an organisation’s own data centre: sandboxed agents, versionable configuration, a shared hub, benchmarks on your own repositories and a guided ticket-to-reviewed-code workbench. Air-gapped capable, no external API calls.",
          "European Sovereign Agentic Coding Appliance — eine standardisierte On-Premises-Plattform, die KI-Coding-Agenten im eigenen Rechenzentrum betreibt: Agenten in der Sandbox, versionierbare Konfiguration, ein gemeinsamer Hub, Benchmarks auf den eigenen Repositories und eine geführte Workbench vom Ticket bis zum reviewten Code. Air-gapped-fähig, keine externen API-Aufrufe."),
        [T("Agentic coding", "Agentisches Coding"), "On-prem", T("Sovereign AI", "Souveräne KI")],
        [T("Platform", "Plattform"), "mgm × Fsas"], links=[("esaca.eu", "https://esaca.eu")], logo="esaca.png", page="esaca")

    research = [
        S("2018 — 2026", "MaCoCo",
          T("Management cockpit for controlling university chairs and institutes — finances, staff and projects in one multi-user information system, largely generated from MontiCore DSLs. Built jointly with the Chair of Management Accounting; <b>in production at RWTH</b>, with a companion Android time-tracking app.",
            "Management-Cockpit für das Controlling von Lehrstühlen und Instituten — Finanzen, Personal und Projekte in einem mehrbenutzerfähigen Informationssystem, größtenteils aus MontiCore-DSLs generiert. Gemeinsam mit dem Lehrstuhl für Controlling entwickelt; <b>produktiv im Einsatz an der RWTH</b>, mit begleitender Android-App zur Zeiterfassung."),
          ["MontiGem", INFOSYS, T("Agile", "Agil"), "Android"], [T("Project lead", "Projektleitung"), PROD],
          links=[(T("project", "Projekt"), "https://www.se-rwth.de/projects/MaCoCo/"),
                 (T("controlling chair", "Lehrstuhl Controlling"), "https://www.controlling.rwth-aachen.de/cms/controlling/forschung/forschungsprojekte/laufende-projekte/~mgaz/macoco-lehrstuhlcontrolling/"),
                 (T("android app", "Android-App"), "https://play.google.com/store/apps/details?id=macoco.stundenzettel.timetracker&amp;hl=de")],
          logo="macoco.png", page="macoco"),
        S("2025", "Golden UML Model Set",
          T("A community-curated dataset of UML models, each paired with a natural-language description of the modelled domain. Crawled model collections are full of invalid and placeholder models; this one is reviewed, searchable on a public web platform, and grows through a structured contribution and review process — a benchmark for UML research, education and LLM evaluation.",
            "Ein von der Community kuratierter Datensatz von UML-Modellen, jeweils mit einer natürlichsprachlichen Beschreibung der modellierten Domäne. Gecrawlte Modellsammlungen sind voller ungültiger Platzhalter-Modelle; dieser Datensatz ist geprüft, über eine öffentliche Webplattform durchsuchbar und wächst über einen strukturierten Beitrags- und Review-Prozess — ein Benchmark für UML-Forschung, Lehre und die Evaluation von LLMs."),
          [T("Dataset", "Datensatz"), "UML", "Benchmark", T("Web platform", "Webplattform")], [T("Dataset", "Datensatz"), T("Multi-university", "Mehrere Unis")],
          links=[(T("explore the dataset", "Datensatz erkunden"), "https://golden-uml-modelset.vercel.app/search"),
                 ("paper", "https://doi.org/10.1109/MODELS-C68889.2025.00012")],
          logo="uml.png", page="golden-uml"),
        S("2025", "SE-Chatty",
          T("A teaching assistant for lecturers. Fed with scripts, books, slides and videos, it answers with lecture-specific depth, helps students train for exams with generated questionnaires, and shows lecturers which parts of the material are understood — and which aren’t.",
            "Ein Lehrassistent für Dozierende. Mit Skripten, Büchern, Folien und Videos gefüttert, antwortet er mit vorlesungsspezifischer Tiefe, hilft Studierenden mit generierten Fragebögen bei der Prüfungsvorbereitung und zeigt Dozierenden, welche Teile des Stoffs verstanden werden — und welche nicht."),
          ["LLM", "RAG", T("Education", "Lehre")], [T("Tool", "Werkzeug"), "RWTH SE"], logo="se-chatty.png", page="se-chatty"),
        S("2024 — 2026", "ePHA",
          T("Electronic dissertation and habilitation repository. A model-driven application generated with MontiGem that supports the publishing process for dissertations and habilitations at RWTH; <b>in production</b>.",
            "Elektronische Promotions- und Habilitationsauslage. Eine modellgetriebene, mit MontiGem generierte Anwendung, die den Veröffentlichungsprozess von Dissertationen und Habilitationen an der RWTH unterstützt; <b>produktiv im Einsatz</b>."),
          ["MontiGem", INFOSYS], [LEAD, PROD],
          links=[("epha.rwth-aachen.de", "https://epha.rwth-aachen.de/")], logo="epha.png", page="epha"),
        S("2020 — 2022", T("Ford Pro tool tracking", "Ford Pro Werkzeugverfolgung"),
          T("Pilot with the Ford Research &amp; Innovation Center Aachen: an integrated information system that tracks tools and machines across vans and job sites via Bluetooth, GPS and AI — reminders for tools left behind, theft alerts, a live map and search by vehicle or tool. The web application was generated from UML models with MontiGem and field-tested by three trade companies around Cologne.",
            "Pilotprojekt mit dem Ford Research &amp; Innovation Center Aachen: ein integriertes Informationssystem, das Werkzeuge und Maschinen über Transporter und Baustellen hinweg per Bluetooth, GPS und KI verfolgt — Erinnerung an vergessenes Werkzeug, Diebstahlwarnungen, Live-Karte und Suche nach Fahrzeug oder Werkzeug. Die Webanwendung wurde mit MontiGem aus UML-Modellen generiert und von drei Handwerksbetrieben im Raum Köln im Feld getestet."),
          ["MontiGem", "IoT", T("Industry", "Industrie")], [T("Technical lead", "Technische Leitung"), IND],
          links=[(T("Ford press release", "Ford-Pressemitteilung"), "https://media.ford.com/content/fordmedia/feu/en/news/2022/08/31/ford-pro-tool-tracking-tech-could-save-firms-1000s.html"),
                 (T("RWTH news", "RWTH-Meldung"), "https://www.se-rwth.de/projects/22.09.MontiGem.Ford.Press.Release/")],
          mark="FORD", page="ford"),
        S("2018 — 2022", "Agile Data Development",
          T("Model-driven tooling for a wind-turbine manufacturer (with WZL, MSE and Bewind): integrating agile and plan-driven development with data-based decision support, including generated digital-twin cockpits for parameter management in turbine engineering.",
            "Modellgetriebene Werkzeuge für einen Windkraftanlagenhersteller (mit WZL, MSE und Bewind): Verzahnung agiler und plangetriebener Entwicklung mit datenbasierter Entscheidungsunterstützung, inklusive generierter Digital-Twin-Cockpits für das Parametermanagement in der Anlagenentwicklung."),
          ["MontiGem", T("Digital twin", "Digitaler Zwilling"), T("Industry", "Industrie")], [LEAD, IND], mark="ADD", page="add"),
        S("2018 — 2024", "MontiGem",
          T("Generator framework for enterprise information systems, built on the MontiCore language workbench. Class diagrams and GUI models in, a complete web application out — applied across five domains, from university controlling to digital-twin cockpits.",
            "Generator-Framework für betriebliche Informationssysteme auf Basis der MontiCore Language Workbench. Klassendiagramme und GUI-Modelle rein, eine vollständige Webanwendung raus — eingesetzt in fünf Domänen, vom Lehrstuhl-Controlling bis zu Digital-Twin-Cockpits."),
          ["MontiCore", "Java", "TypeScript", T("Code generation", "Codegenerierung")], ["Framework", "RWTH SE"], logo="montigem.png", page="montigem"),
        S("2012 — 2016", "geneial",
          T("A template-based C++11 genetic-algorithm library, developed within the DFG project OASys (online algorithms for optimal control of hybrid propulsion systems). CMake build, Boost unit tests, benchmarks and Doxygen docs.",
            "Eine template-basierte C++11-Bibliothek für genetische Algorithmen, entstanden im DFG-Projekt OASys (Online-Algorithmen zur optimalen Steuerung hybrider Antriebe). CMake-Build, Boost-Unit-Tests, Benchmarks und Doxygen-Dokumentation."),
          ["C++11", T("Evolutionary algorithms", "Evolutionäre Algorithmen"), "MIT"], [T("Library", "Bibliothek"), T("Open source", "Open Source")],
          links=[("github", "https://github.com/geneial/geneial"), ("OASys", "https://ths.rwth-aachen.de/research/projects/oasys/")],
          logo="geneial.png", page="geneial"),
        S("2015", "SMT-RAT",
          T("A modular C++ toolbox for SMT solving over non-linear real arithmetic, developed at RWTH’s Theory of Hybrid Systems group. In my bachelor’s thesis I extended its interval-constraint-propagation module with a propagation contractor and multivariate Horner schemes.",
            "Ein modularer C++-Werkzeugkasten für SMT-Solving über nichtlinearer reeller Arithmetik, entwickelt am Lehr- und Forschungsgebiet Theorie der hybriden Systeme der RWTH. In meiner Bachelorarbeit habe ich sein Modul für Intervall-Constraint-Propagation um einen Propagations-Kontraktor und multivariate Horner-Schemata erweitert."),
          ["C++", "SMT", T("Interval arithmetic", "Intervallarithmetik")], [T("Bachelor’s thesis", "Bachelorarbeit"), T("Open source", "Open Source")],
          links=[("github", "https://github.com/ths-rwth/smtrat"), (T("documentation", "Dokumentation"), "https://ths-rwth.github.io/smtrat/")],
          mark="SMT", page="smt-rat"),
    ]
    gpts = [
        S("GPT", "SysML v2 Model Creator",
          T("Creates SysML v2 models from natural-language descriptions.",
            "Erstellt SysML-v2-Modelle aus natürlichsprachlichen Beschreibungen."),
          [], ["SysML v2"], href="https://chatgpt.com/g/g-3DkGCDlNM-sysml-v2-model-creator"),
        S("GPT", "MontiCore Expert",
          T("Answers questions on grammars, symbol tables and generators in the MontiCore language workbench.",
            "Beantwortet Fragen zu Grammatiken, Symboltabellen und Generatoren in der MontiCore Language Workbench."),
          [], ["MontiCore"], href="https://chatgpt.com/g/g-Pgayc5wzx-monticore-expert"),
        S("GPT", "CD4A Class Diagram Creator",
          T("Writes class diagrams in CD4A, the MontiCore class-diagram language.",
            "Schreibt Klassendiagramme in CD4A, der Klassendiagrammsprache von MontiCore."),
          [], ["CD4A"], href="https://chatgpt.com/g/g-sRnmDgQvW-cd4a-class-diagram-creator"),
    ]
    n = 1 + len(research) + len(gpts)
    head = page_head("01", L(T("Projects", "Projekte")), L(T(f"{n} entries", f"{n} Einträge")),
        L(T("Software I have built or led — from generator frameworks and production information systems to <em>agentic coding</em> platforms.",
            "Software, die ich gebaut oder geleitet habe — von Generator-Frameworks und produktiven Informationssystemen bis zu Plattformen für <em>agentisches Programmieren</em>.")),
        top=page_icon("code"))
    pic = banner(A, "banner-factory.jpg", L(T("Model factory in the lab, with MontiCore-generated dashboards on three screens behind it",
                                              "Modellfabrik im Labor, dahinter MontiCore-generierte Dashboards auf drei Bildschirmen")), 2400, 769)
    return f'''
{head}{pic}    <section>
      <div class="group mono">{L(T("Industry", "Industrie"))} · mgm technology partners</div>
      <ul class="spec">
{esaca}
      </ul>

      <div class="group mono">{L(T("Research software", "Forschungssoftware"))} · RWTH Aachen</div>
      <ul class="spec">
{NL.join(research)}
      </ul>

      <div class="group mono">{L(T("Assistants", "Assistenten"))} · ChatGPT</div>
      <ul class="spec">
{NL.join(gpts)}
      </ul>
    </section>
'''


# =====================================================================
# 02 Research
# =====================================================================

TALKS = [   # date, title EN, title DE (original), venue EN, venue DE
    ("12 / 2025", "AI, Agents &amp; Software Engineering", "Künstliche Intelligenz, Agenten &amp; Software Engineering",
     "Guest lecture, Software Engineering course · RWTH Aachen", "Gastvortrag, Vorlesung Softwaretechnik · RWTH Aachen"),
    ("09 / 2025", "AI in Engineering", "KI im Engineering",
     "Software Engineering Congress · Frankfurt", "Software Engineering Congress · Frankfurt"),
    ("03 / 2025", "GenAI in Teaching, Research and Software Development", "GenAI in Lehre, Forschung und Software-Entwicklung",
     "Gesellschaft für Informatik · Cologne", "Gesellschaft für Informatik · Köln"),
    ("12 / 2024", "AI &amp; Software Engineering", "Künstliche Intelligenz &amp; Software Engineering",
     "Guest lecture, Software Engineering course · RWTH Aachen", "Gastvortrag, Vorlesung Softwaretechnik · RWTH Aachen"),
    ("11 / 2024", "AI — A Look Behind the Hype", "KI – Ein Blick hinter den Hype",
     "SOPTIM user days · Cologne", "SOPTIM Anwendertage · Köln"),
    ("10 / 2024", "Integrating LLMs into Software Engineering: AI as a Component", "Integrating LLMs into Software Engineering: AI as a Component",
     "Gesellschaft für Informatik · Cologne", "Gesellschaft für Informatik · Köln"),
    ("07 / 2023", "MDE for Financial Management", "MDE for Financial Management", "MDENet", "MDENet"),
]


# Citation metrics from Google Scholar — static, update by hand (and the date with them).
SCHOLAR = "https://scholar.google.com/citations?user=5mVkoWsAAAAJ&amp;hl=en"
METRICS = {
    lang: f'''
      <dl class="facts mono">
        <div><dt>{T("Citations", "Zitationen")[lang]}</dt><dd>587</dd></div>
        <div><dt>h-index</dt><dd>14</dd></div>
        <div><dt>i10-index</dt><dd>17</dd></div>
      </dl>
      <p class="facts-note mono"><a href="{SCHOLAR}" target="_blank" rel="noopener">Google Scholar ↗</a> · {T("as of", "Stand")[lang]} 10 / 2026</p>'''
    for lang in ("en", "de")
}


def research(lang):
    L = lambda x: x[lang]
    A = "../" if lang == "de" else ""
    golden_links = [(L(T("explore the dataset", "Datensatz erkunden")), "https://golden-uml-modelset.vercel.app/search"),
                    ("paper", "https://doi.org/10.1109/MODELS-C68889.2025.00012")]
    community = [
        row("2026", "MDE Intelligence",
            L(T("The international Workshop on Artificial Intelligence and Model-Driven Engineering, held with the ACM/IEEE MODELS conference since 2019. It is the forum for both directions of the integration: AI techniques that make modeling and model management smarter, and MDE concepts — DSLs, metamodels, transformations — that make AI systems easier to build and to trust. I co-organized its 8th edition at MODELS 2026 in Málaga, together with Dominik Bork (TU Wien) and Boqi Chen (University of Ottawa).",
                "Der internationale Workshop zu Künstlicher Intelligenz und modellgetriebener Softwareentwicklung, seit 2019 Teil der ACM/IEEE-Konferenz MODELS. Er ist das Forum für beide Richtungen der Integration: KI-Techniken, die Modellierung und Modellmanagement intelligenter machen, und MDE-Konzepte — DSLs, Metamodelle, Transformationen —, die KI-Systeme leichter baubar und vertrauenswürdiger machen. Die 8. Ausgabe auf der MODELS 2026 in Málaga habe ich gemeinsam mit Dominik Bork (TU Wien) und Boqi Chen (University of Ottawa) organisiert.")),
            L(T("Co-organizer", "Co-Organisator")), [("mde-intelligence.github.io", "https://mde-intelligence.github.io/")]),
        row("2024 — 2026", L(T("AI4RSE working groups", "Arbeitskreise AI4RSE")),
            L(T("Spokesperson of the working groups on AI for research software engineering in the German Informatics Society (GI) and in de-RSE, the German association for research software engineering.",
                "Sprecher der Arbeitskreise zu KI für Research Software Engineering in der Gesellschaft für Informatik (GI) und bei de-RSE, dem deutschen Verein für Research Software Engineering.")),
            L(T("Spokesperson", "Sprecher"))),
        row("2026", L(T("AI in RSE workshop", "Workshop AI in RSE")),
            L(T("Program committee member of the workshop on AI in research software engineering.",
                "Mitglied im Programmkomitee des Workshops zu KI im Research Software Engineering.")),
            L(T("Program committee", "Programmkomitee"))),
        row("2023 — 2026", "LLM-Café",
            L(T("A recurring discussion panel on large language models at the computer science centre of RWTH Aachen.",
                "Ein regelmäßiges Diskussionspanel zu großen Sprachmodellen im Informatikzentrum der RWTH Aachen.")),
            L(T("Organizer", "Organisator"))),
        row("2025", "Golden UML Model Set",
            L(T("A community-curated, quality-assured dataset of UML models with natural-language domain descriptions — built as a benchmark for modeling research, education and LLM evaluation.",
                "Ein von der Community kuratierter, qualitätsgesicherter Datensatz von UML-Modellen mit natürlichsprachlichen Domänenbeschreibungen — als Benchmark für Modellierungsforschung, Lehre und die Evaluation von LLMs.")),
            L(T("Dataset", "Datensatz")), golden_links),
    ]
    talks = [row(d, ten if lang == "en" else tde, ven if lang == "en" else vde) for d, ten, tde, ven, vde in TALKS]
    themes = [
        T(("LLMs for modeling", "Model synthesis in DSLs, grammar masking for syntactically valid output, how LLMs corrupt and repair textual models."),
          ("LLMs für die Modellierung", "Modellsynthese in DSLs, Grammar Masking für syntaktisch valide Ausgaben, wie LLMs textuelle Modelle beschädigen und reparieren.")),
        T(("Model-driven engineering", "Generators and DSLs that stay maintainable when the model evolves."),
          ("Modellgetriebene Entwicklung", "Generatoren und DSLs, die wartbar bleiben, wenn sich das Modell weiterentwickelt.")),
        T(("Low-code &amp; digital twins", "Generating customized low-code platforms and cockpits for digital twins."),
          ("Low-Code &amp; digitale Zwillinge", "Generierung maßgeschneiderter Low-Code-Plattformen und Cockpits für digitale Zwillinge.")),
        T(("Information systems", "From model-driven prototype to full-size enterprise application — and retrofitting generation into existing systems."),
          ("Informationssysteme", "Vom modellgetriebenen Prototyp zur vollwertigen Unternehmensanwendung — und die nachträgliche Einführung von Generierung in bestehende Systeme.")),
    ]
    filters = [("all", T("all", "alle")), ("llm", T("llm", "llm")), ("mde", T("mde", "mde")),
               ("twin", T("digital twins", "digitale Zwillinge")), ("eis", T("information systems", "Informationssysteme")),
               ("a11y", T("accessibility", "Barrierefreiheit")), ("ga", T("genetic algorithms", "genetische Algorithmen"))]
    head = page_head("02", L(T("Research", "Forschung")), "",
        L(T("I research how <em>large language models</em> and <em>model-driven engineering</em> can make each other better: LLMs that write valid models, and models that keep LLM output in check.",
            "Ich erforsche, wie <em>große Sprachmodelle</em> und <em>modellgetriebene Softwareentwicklung</em> sich gegenseitig besser machen: LLMs, die valide Modelle schreiben, und Modelle, die LLM-Ausgaben im Zaum halten.")),
        METRICS[lang], count_id=True, top=page_icon("sqrt"))
    pic = banner(A, "banner-lecture.jpg", L(T("Lukas Netz lecturing in a large RWTH Aachen lecture hall",
                                              "Lukas Netz bei einer Vorlesung in einem großen Hörsaal der RWTH Aachen")), 1659, 532)
    return f'''
{head}{pic}    <section>
      <div class="group mono">{L(T("Topics", "Themen"))}</div>
      <div class="themes">
{NL.join(f"        <div><h4>{L(t)[0]}</h4><p>{L(t)[1]}</p></div>" for t in themes)}
      </div>

      <div class="group mono">Community</div>
      <ul class="rows">
{NL.join(community)}
      </ul>

      <div class="group mono">{L(T("Invited talks", "Eingeladene Vorträge"))}</div>
      <ul class="rows tight">
{NL.join(talks)}
      </ul>

      <div class="group mono">{L(T("Publications", "Publikationen"))}</div>
      <div class="filters mono" role="group" aria-label="{L(T("Filter publications", "Publikationen filtern"))}">
{NL.join(f'        <button type="button" data-f="{k}" aria-pressed="{"true" if k == "all" else "false"}">{L(v)}</button>' for k, v in filters)}
      </div>

      <div id="pubs"></div>
    </section>
'''


# =====================================================================
# 03 Photography
# =====================================================================

def P(f, w, h, alt, title, exif=""):
    """One photo. The grid uses assets/photos/thumbs/<f>.jpg, the lightbox the full file."""
    return dict(f=f, r=round(w / h, 4), w=w, h=h, alt=alt, title=title, exif=exif)


def X(f, r, alt, title=T("", "")):          # older portfolio images: 1800px long edge
    w, h = (1800, round(1800 / r)) if r >= 1 else (round(1800 * r), 1800)
    return P(f, w, h, alt, title)


AERIAL = T(", aerial", ", Luftbild")


def A_(en, de):                               # title of an aerial photo
    return T(en + AERIAL["en"], de + AERIAL["de"])


SERIES = [  # (anchor, name, note, photos)
    ("selected", T("Selected", "Auswahl"), "2019 — 2025", [
        P("p07", 2000, 1125, T("Aerial view of a coastal road curving above rocks and surf", "Luftbild einer Küstenstraße über Felsen und Brandung"), T("Coast road, aerial", "Küstenstraße, Luftbild"), "f/1.7 · 1/730 · 2023"),
        P("p02", 1333, 2000, T("Bride standing in a tall arched palace window, black and white", "Braut in einem hohen Bogenfenster eines Palasts, schwarzweiß"), T("Window", "Fenster")),
        P("p03", 2000, 1333, T("Dog running towards the camera with leaves in its mouth", "Hund rennt mit Laub im Maul auf die Kamera zu"), T("Retrieve", "Apport"), "85mm · f/1.4 · 2024"),
        P("p05", 1333, 2000, T("Silhouette of a wedding couple holding hands", "Silhouette eines Hochzeitspaars, Hand in Hand"), T("Silhouette", "Silhouette"), "24mm · f/2.8"),
        P("p08", 2000, 1408, T("City lights at night seen from above", "Lichter einer Stadt bei Nacht von oben"), T("City at night, aerial", "Stadt bei Nacht, Luftbild"), "1/5 · ISO 1270 · 2025"),
        P("p01", 2000, 1333, T("Black and white portrait with skull face paint", "Schwarzweiß-Porträt mit Totenkopf-Schminke"), T("Portrait", "Porträt")),
        P("p10", 2000, 1333, T("Alpine valley with winding roads under dramatic clouds", "Alpental mit Serpentinen unter dramatischen Wolken"), T("Alps", "Alpen"), "26mm · f/11 · 2019"),
        P("p06", 2000, 1125, T("Wet dog shaking off water in the sun", "Nasser Hund schüttelt sich in der Sonne"), T("Shake", "Schütteln"), "24mm · 1/4000 · 2025"),
        P("p11", 2000, 1333, T("Couple embracing in an autumn forest", "Paar umarmt sich im Herbstwald"), T("Autumn", "Herbst"), "85mm · f/2 · 2019"),
        P("p09", 2000, 1333, T("Wedding couple playfully posing in sand dunes", "Hochzeitspaar posiert verspielt in den Dünen"), T("Dunes", "Dünen"), "24mm · f/4 · 2019"),
    ]),
    ("landscape", T("Landscape", "Landschaft"), "", [
        P("land_18", 2400, 873, T("Panorama of a wide river bend under a low sun", "Panorama einer weiten Flussschleife bei tiefer Sonne"), T("River bend, panorama", "Flussschleife, Panorama")),
        P("land_07", 1800, 1012, T("Bridges linking small islands across the sea, seen from above", "Brücken verbinden kleine Inseln im Meer, von oben"), A_("Island bridges", "Inselbrücken")),
        P("land_13", 1800, 1012, T("Glowing lava veins in black rock, seen from above", "Glühende Lavaadern in schwarzem Gestein, von oben"), A_("Lava", "Lava")),
        P("land_15", 1800, 1013, T("Crevassed glacier surface seen from above", "Zerklüftete Gletscheroberfläche von oben"), A_("Glacier", "Gletscher")),
        P("land_17", 1800, 1012, T("River cutting through a moss-green canyon, seen from above", "Fluss in einer moosgrünen Schlucht, von oben"), A_("Canyon", "Schlucht")),
        P("land_16", 1800, 1012, T("Road winding through moss-covered hills, seen from above", "Straße durch moosbedeckte Hügel, von oben"), A_("Road through moss", "Straße durchs Moos")),
        P("land_14", 1800, 1012, T("Waterfall plunging into a gorge, seen from above", "Wasserfall stürzt in eine Schlucht, von oben"), A_("Waterfall", "Wasserfall")),
        P("land_11", 1800, 1012, T("Steam rising from a crater in red earth, seen from above", "Dampf steigt aus einem Krater in roter Erde, von oben"), A_("Crater", "Krater")),
        P("land_12", 1800, 1013, T("Dark rocks in white surf, seen from above", "Dunkle Felsen in weißer Brandung, von oben"), A_("Rocks in surf", "Felsen in der Brandung")),
        P("land_00", 1800, 1012, T("Turquoise sea breaking on rocks, seen from above", "Türkisfarbenes Meer bricht an Felsen, von oben"), A_("Surf", "Brandung")),
        P("land_10", 1800, 1013, T("Small boat drawing a wake across turquoise water, seen from above", "Kleines Boot zieht eine Spur durch türkisfarbenes Wasser, von oben"), A_("Boat", "Boot")),
        P("land_08", 1800, 1012, T("Turquoise river winding through dense forest, seen from above", "Türkisfarbener Fluss durch dichten Wald, von oben"), A_("River", "Fluss")),
        P("land_19", 2000, 1125, T("Lakeshore of Chicago at night, seen from high above", "Seeufer von Chicago bei Nacht, von hoch oben"), T("Lakeshore, Chicago", "Seeufer, Chicago")),
        P("land_20", 2000, 1122, T("Light trails along the lakeshore road at night, seen from above", "Lichtspuren entlang der Uferstraße bei Nacht, von oben"), T("Lake Shore Drive, Chicago", "Lake Shore Drive, Chicago")),
        P("land_21", 2000, 1125, T("Street grid of Chicago lit up at night, seen from above", "Erleuchtetes Straßenraster von Chicago bei Nacht, von oben"), T("Grid, Chicago", "Raster, Chicago")),
        P("land_09", 2400, 655, T("Panorama of a city at night from the air", "Nachtpanorama einer Stadt aus der Luft"), T("City at night, panorama", "Stadt bei Nacht, Panorama")),
        P("land_22", 2000, 1333, T("Waterfall seen from the cave behind it, black and white", "Wasserfall aus der Höhle dahinter gesehen, schwarzweiß"), T("Behind the falls", "Hinter dem Wasserfall")),
        P("land_04", 1800, 1200, T("Mountain wrapped in clouds, black and white", "Berg in Wolken, schwarzweiß"), T("Clouds", "Wolken")),
        P("land_02", 1800, 1011, T("Layered forested hills at dusk", "Gestaffelte bewaldete Hügel in der Dämmerung"), T("Dusk", "Dämmerung")),
        P("land_03", 1800, 1011, T("Path through a tall green forest", "Weg durch einen hohen grünen Wald"), T("Forest", "Wald")),
        P("land_06", 1800, 1013, T("Lone walker on a backlit shore below mountains", "Einzelner Spaziergänger am Ufer im Gegenlicht unter Bergen"), T("Shore", "Ufer")),
        P("land_05", 1800, 1013, T("City skyline across the water under streaked clouds", "Skyline einer Stadt über dem Wasser unter Schleierwolken"), T("Skyline", "Skyline")),
        P("land_01", 1200, 1800, T("Woman in white walking down a long red-pillared corridor", "Frau in Weiß in einem langen Säulengang mit roten Säulen"), T("Corridor", "Säulengang")),
        X("printhno_04", 0.8, T("Rock tower in the Dolomites under heavy clouds", "Felsturm in den Dolomiten unter schweren Wolken"), T("Dolomites", "Dolomiten")),
        X("printhno_05", 1.25, T("Jagged Dolomite peaks at dusk", "Zackige Dolomitengipfel in der Dämmerung"), T("Dolomites", "Dolomiten")),
        X("printhno_07", 1.25, T("Dolomite massif above a scree slope", "Dolomitenmassiv über einem Geröllhang"), T("Dolomites", "Dolomiten")),
        X("printhno_02", 1.5, T("Alpine valley with layered mountain ridges", "Alpental mit gestaffelten Bergrücken"), T("Valley", "Tal")),
        X("printhno_03", 1.5, T("Snow-capped peak above dark ridges and clouds", "Schneebedeckter Gipfel über dunklen Graten und Wolken"), T("Peaks", "Gipfel")),
        X("printhno_10", 1.5, T("Vineyard rows seen from above", "Rebzeilen eines Weinbergs von oben"), T("Vineyard, aerial", "Weinberg, Luftbild")),
        X("printhno_12", 1.5, T("Wooden jetty on a calm misty lake", "Holzsteg an einem ruhigen, nebligen See"), T("Jetty", "Steg")),
        X("printhno_08", 2.6277, T("Tree-lined canal with calm water", "Von Bäumen gesäumter Kanal mit ruhigem Wasser"), T("Canal du Midi, France", "Canal du Midi, Frankreich")),
        P("land_23", 2000, 2000, T("Crescent moon over a city skyline with church spires at night", "Mondsichel über einer Stadtsilhouette mit Kirchtürmen bei Nacht"), T("Crescent", "Mondsichel")),
    ]),
    ("people", T("People", "Menschen"), "", [
        P("peop_06", 1012, 1800, T("A baby's hand holding an adult's finger, black and white", "Babyhand hält einen Finger, schwarzweiß"), T("Hold", "Halt")),
        P("peop_00", 1800, 1205, T("Woman under water with floating red hair", "Frau unter Wasser mit schwebenden roten Haaren"), T("Under water", "Unter Wasser")),
        P("peop_02", 1800, 1013, T("Two faces head to toe with playing-card face paint, black and white", "Zwei Gesichter gegenläufig mit Spielkarten-Schminke, schwarzweiß"), T("Cards", "Karten")),
        P("peop_01", 1200, 1800, T("Young woman hugging a tabby cat, black and white", "Junge Frau umarmt eine getigerte Katze, schwarzweiß"), T("Cat", "Katze")),
        P("peop_03", 1800, 1200, T("Person standing on a rocky summit above mountain ranges", "Person auf einem felsigen Gipfel über Bergketten"), T("Summit", "Gipfel")),
        P("peop_04", 1800, 1200, T("Smiling woman, black and white portrait", "Lächelnde Frau, Schwarzweiß-Porträt"), T("Smile", "Lächeln")),
        P("peop_07", 1280, 1920, T("Wedding couple jumping hand in hand in front of a tall window", "Hochzeitspaar springt Hand in Hand vor einem hohen Fenster"), T("Leap", "Sprung")),
        P("peop_08", 1280, 1920, T("Man lifting a laughing woman in a sunlit forest", "Mann hebt eine Frau im sonnigen Wald hoch"), T("Lift", "Hoch")),
        P("peop_05", 1200, 1800, T("Fine-art nude study of a torso, black and white", "Aktstudie eines Torsos, schwarzweiß"), T("Form", "Form")),
        P("peop_09", 1280, 1920, T("Fine-art study of a curled-up tattooed figure from above, black and white", "Aktstudie einer zusammengerollten, tätowierten Figur von oben, schwarzweiß"), T("Curl", "Rund")),
        P("peop_10", 2048, 1365, T("Silhouette of a man in a hat exhaling smoke against black", "Silhouette eines Mannes mit Hut, der Rauch ausatmet, vor Schwarz"), T("Smoke", "Rauch")),
        P("peop_11", 1370, 2048, T("Man with hat and suitcase walking along railway tracks, black and white", "Mann mit Hut und Koffer auf Bahngleisen, schwarzweiß"), T("Tracks", "Gleise")),
        P("peop_12", 1370, 2048, T("Young man playing the guitar, eyes down, black and white", "Junger Mann spielt Gitarre, Blick gesenkt, schwarzweiß"), T("Guitar", "Gitarre")),
        P("peop_13", 2048, 1136, T("Couple in white helmets on a scooter, black and white", "Paar mit weißen Helmen auf einem Motorroller, schwarzweiß"), T("Vespa", "Vespa")),
        P("peop_14", 2048, 1153, T("Woman in profile with a cigarette and curling smoke, black and white", "Frau im Profil mit Zigarette und Rauchschwaden, schwarzweiß"), T("Profile", "Profil")),
        P("peop_15", 2048, 1153, T("Two women in sixties styling, one with large glasses, one with a wide hat", "Zwei Frauen im Sechziger-Stil, eine mit großer Brille, eine mit breitem Hut"), T("Sixties", "Sechziger")),
        P("peop_16", 2048, 1365, T("Woman lying with wet hair and water drops, smiling into the camera, black and white", "Liegende Frau mit nassem Haar und Wassertropfen, lächelt in die Kamera, schwarzweiß"), T("Drops", "Tropfen")),
        P("peop_17", 1365, 2048, T("Rider galloping a pony through water, black and white", "Reiterin galoppiert mit einem Pony durchs Wasser, schwarzweiß"), T("Gallop", "Galopp")),
        P("peop_18", 2048, 1365, T("Fine-art study of a back with hands pointing to the shoulders, black and white", "Aktstudie eines Rückens, die Hände zeigen auf die Schultern, schwarzweiß"), T("Back", "Rücken")),
        P("peop_19", 1365, 2048, T("Smiling woman with long hair against black", "Lächelnde Frau mit langen Haaren vor Schwarz"), T("Portrait", "Porträt")),
        P("peop_20", 1638, 2048, T("Dog licking the face of a woman in a cap, black and white", "Hund leckt das Gesicht einer Frau mit Kappe, schwarzweiß"), T("Kiss", "Kuss")),
        P("peop_27", 1333, 2000, T("Father kissing his laughing baby, on white", "Vater küsst sein lachendes Baby, vor Weiß"), T("Father", "Vater")),
        P("peop_28", 2000, 1333, T("Young couple looking at each other under blossoming branches", "Junges Paar sieht sich unter blühenden Zweigen an"), T("Blossom", "Blüte")),
        P("peop_29", 1333, 2000, T("Newborn held in two hands, gripping a finger", "Neugeborenes in zwei Händen, greift nach einem Finger"), T("Newborn", "Neugeboren")),
        P("peop_35", 1920, 1280, T("Hands forming a heart on a pregnant belly, black and white", "Hände formen ein Herz auf einem Babybauch, schwarzweiß"), T("Expecting", "Erwartung")),
        P("peop_25", 1332, 2000, T("Wedding couple in an arched doorway, black and white", "Hochzeitspaar in einem Torbogen, schwarzweiß"), T("Archway", "Torbogen")),
        P("peop_23", 1920, 1280, T("Woman in profile, lit from the side against black", "Frau im Profil, seitlich beleuchtet vor Schwarz"), T("Side light", "Seitenlicht")),
        P("peop_31", 1333, 2000, T("Woman with long hair against dark grey, black and white", "Frau mit langen Haaren vor dunklem Grau, schwarzweiß"), T("Long hair", "Lange Haare")),
        P("peop_32", 1333, 2000, T("Fine-art study of a seated figure hugging her knees, black and white", "Aktstudie einer sitzenden Figur, die ihre Knie umarmt, schwarzweiß"), T("Folded", "Gefaltet")),
        P("peop_24", 2000, 1333, T("Crowd looking up into the mirrored underside of Cloud Gate", "Menschenmenge blickt in die verspiegelte Unterseite von Cloud Gate"), T("Cloud Gate, Chicago", "Cloud Gate, Chicago")),
        P("peop_22", 1333, 2000, T("Young man in a cap crouching against a weathered concrete wall, black and white", "Junger Mann mit Kappe hockt vor einer verwitterten Betonwand, schwarzweiß"), T("Concrete", "Beton")),
        P("peop_34", 1333, 2000, T("Woman in a pink traditional Chinese costume with a flowered hat in a courtyard", "Frau in rosafarbenem traditionellem chinesischem Gewand mit Blütenhut in einem Hof"), T("Costume", "Gewand")),
        P("peop_33", 1333, 2000, T("Man in a hoodie leaning on a blue sports car on a country road", "Mann im Kapuzenpulli lehnt an einem blauen Sportwagen auf einer Landstraße"), T("Driver", "Fahrer")),
        P("peop_21", 1920, 1280, T("Athlete peeking through bright yellow hurdles in dewy grass", "Sportlerin blickt durch leuchtend gelbe Hürden im taunassen Gras"), T("Hurdles", "Hürden")),
        P("peop_26", 1920, 1280, T("Woman holding a side plank in a suspension trainer in a park", "Frau im seitlichen Unterarmstütz im Schlingentrainer im Park"), T("Plank", "Stütz")),
        P("peop_30", 1920, 1280, T("Woman training with battle ropes in a sunny park", "Frau trainiert mit Battle Ropes in einem sonnigen Park"), T("Ropes", "Seile")),
        X("portfolio_07", 1.25, T("Woman with curly hair in low-key studio light", "Frau mit Locken im Low-Key-Studiolicht"), T("Studio", "Studio")),
        X("portfolio_13", 0.6667, T("Smiling woman in black and white", "Lächelnde Frau in Schwarzweiß"), T("Light", "Licht")),
        X("portfolio_16", 1.5, T("Smiling elderly woman, black and white close-up", "Lächelnde ältere Frau, Schwarzweiß-Nahaufnahme"), T("Laugh lines", "Lachfalten")),
        X("portfolio_09", 0.6667, T("Rider and horse jumping in the dark", "Reiterin und Pferd beim Sprung im Dunkeln"), T("Jump", "Sprung")),
        X("portfolio_15", 0.6667, T("Basketball player mid-dunk, black and white", "Basketballspieler beim Dunk, schwarzweiß"), T("Dunk", "Dunk")),
        X("portfolio_25", 0.6667, T("Athlete throwing a ball in backlight", "Sportler wirft einen Ball im Gegenlicht"), T("Throw", "Wurf")),
        X("portfolio_60", 0.6667, T("Low-key black and white profile with hair falling forward", "Low-Key-Profil in Schwarzweiß mit nach vorn fallendem Haar"), T("Low key", "Low Key")),
        X("portfolio_14", 1.5, T("Street scene with silhouettes against the sun", "Straßenszene mit Silhouetten im Gegenlicht"), T("Street", "Straße")),
        X("portfolio_48", 1.5, T("Woman lying on a dark surface, black and white", "Frau liegt auf dunklem Untergrund, schwarzweiß"), T("Rest", "Ruhe")),
        X("portfolio_59", 0.6667, T("Woman covering her face with her hands in warm light", "Frau verbirgt das Gesicht in den Händen, warmes Licht"), T("Shy", "Scheu")),
    ]),
    ("animals", T("Animals", "Tiere"), "", [
        P("p04", 2000, 1333, T("Woman embracing a dark horse against a blue sky", "Frau umarmt ein dunkles Pferd vor blauem Himmel"), T("Trust", "Vertrauen"), "135mm · f/2.8 · 2023"),
        P("anim_02", 1800, 1200, T("White horse's mane in low-key light", "Mähne eines Schimmels im Low-Key-Licht"), T("Mane", "Mähne")),
        P("anim_01", 1200, 1800, T("Horse grazing, seen from below against the sky", "Grasendes Pferd von unten vor dem Himmel"), T("Grazing", "Grasen")),
        P("anim_04", 1800, 1201, T("Horse rolling in the sand of a dark arena", "Pferd wälzt sich im Sand einer dunklen Halle"), T("Roll", "Wälzen")),
        P("anim_00", 1620, 1080, T("Girl hugging a horse's neck, black and white", "Mädchen umarmt den Hals eines Pferdes, schwarzweiß"), T("Embrace", "Umarmung")),
        P("anim_03", 1800, 1200, T("Rider leading a horse through a dark stable", "Reiter führt ein Pferd durch einen dunklen Stall"), T("Stable", "Stall")),
        P("anim_06", 2000, 1124, T("Eagle owl in flight with spread wings", "Uhu im Flug mit ausgebreiteten Flügeln"), T("Owl", "Uhu")),
        P("anim_07", 2000, 1122, T("Ring-tailed lemur looking up against a warm background", "Katta blickt nach oben vor warmem Hintergrund"), T("Lemur", "Katta")),
        P("anim_08", 2000, 1124, T("Barbary macaque holding its young", "Berberaffe hält sein Junges"), T("Macaques", "Berberaffen")),
        P("anim_05", 1333, 2000, T("Black dog lying on a rug, looking up", "Schwarzer Hund liegt auf einem Teppich und schaut hoch"), T("Look up", "Aufblick")),
        X("baily_00", 1.25, T("Dog splashing through water", "Hund springt durchs Wasser"), T("Splash", "Spritzer")),
        X("baily_02", 0.8, T("Border collie sitting in golden grass", "Border Collie sitzt im goldenen Gras"), T("Golden hour", "Goldene Stunde")),
        X("baily_13", 0.8, T("Dog with closed eyes on white background", "Hund mit geschlossenen Augen vor weißem Hintergrund"), T("Calm", "Gelassen")),
        X("baily_06", 0.6667, T("Shepherd dog in low-key light", "Schäferhund im Low-Key-Licht"), T("Low key", "Low Key")),
        X("baily_11", 0.6667, T("Border collie catching a ball on white", "Border Collie fängt einen Ball, weißer Hintergrund"), T("Catch", "Fang")),
        X("baily_08", 1.5, T("Shepherd dog lying in the dark", "Schäferhund liegt im Dunkeln"), T("Rest", "Ruhe")),
    ]),
]


def photography(lang):
    L = lambda x: x[lang] if isinstance(x, dict) else x
    A = "../" if lang == "de" else ""

    # compact justified grid: each tile grows in proportion to its aspect ratio (--r),
    # thumbnails in the grid, full-size file for the lightbox (data-full);
    # captions are visually hidden in the grid and shown in the lightbox
    def fig(p):
        return (f'          <figure style="--r:{p["r"]}"><img src="{A}assets/photos/thumbs/{p["f"]}.jpg" '
                f'data-full="{A}assets/photos/{p["f"]}.jpg" alt="{L(p["alt"])}" loading="lazy" decoding="async" '
                f'width="{p["w"]}" height="{p["h"]}"><figcaption class="mono"><span>{L(p["title"])}</span><span>{p["exif"]}</span></figcaption></figure>')

    def series(anchor, name, note, photos):
        right = (note + " · " if note else "") + str(len(photos))
        return (f'      <div class="group mono series" id="{anchor}"><span>{L(name)}</span><span>{right}</span></div>' + NL +
                '      <div class="grid">' + NL + NL.join(fig(p) for p in photos) + NL + '      </div>')

    n = sum(len(photos) for *_, photos in SERIES)
    nav = "".join(f'<a href="#{a}">{L(name).lower()}</a>' for a, name, _, _ in SERIES)
    extra = f'''
      <div class="bio">
        <p>{L(T("By playing with an extraordinarily complex high-tech instrument that exploits the limits of physics in the most ingenious way, you can hold on to the most beautiful moments forever — in a fraction of a second.",
               "Durch das Spielen mit einem ausgefallen-komplexen Hightech-Instrument, das auf raffinierteste Weise die Grenzen der Physik ausnutzt, kann man die schönsten Momente in einem Bruchteil einer Sekunde für immer festhalten."))}</p>
      </div>'''
    head = page_head("03", L(T("Photography", "Fotografie")), L(T(f"{n} photographs", f"{n} Fotografien")),
        L(T("Photography has fascinated me from the very first moment. The camera is one of the few tools that lets you not only show a very particular perspective on the world, but also capture and share <em>memories and emotions</em>.",
            "Die Fotografie hat mich vom ersten Moment an begeistert. Die Kamera ist eines der wenigen Werkzeuge, die es einem ermöglichen, nicht nur einen ganz bestimmten Blickwinkel auf die Welt zu zeigen, sondern auch <em>Erinnerungen und Emotionen</em> einzufangen und zu teilen.")),
        extra, top=page_icon("camera"))
    pic = banner(A, "about-dolomites.jpg", L(T("Lukas Netz with a camera, looking out over the Dolomites",
                                               "Lukas Netz mit Kamera, Blick über die Dolomiten")), 2400, 769)
    return f'''
{head}{pic}
    <section>
      <div class="gallery-bar mono">
        <nav class="filters" aria-label="{L(T("Series", "Serien"))}">{nav}</nav>
        <button type="button" class="slideshow" data-slideshow>▶ {L(T("slideshow", "Diashow"))}</button>
      </div>
{NL.join(series(*s) for s in SERIES)}
    </section>
'''


# =====================================================================
# Write both languages
# =====================================================================

DESC = {
    "index.html": T("Lukas Netz — IT specialist at mgm technology partners. Model-driven engineering, LLMs for modeling, agentic coding.",
                    "Lukas Netz — IT-Spezialist bei mgm technology partners. Modellgetriebene Softwareentwicklung, LLMs für die Modellierung, agentisches Programmieren."),
    "projects.html": T("Software projects by Lukas Netz: ESACA, MaCoCo, MontiGem, the Golden UML Model Set and more.",
                       "Softwareprojekte von Lukas Netz: ESACA, MaCoCo, MontiGem, das Golden UML Model Set und mehr."),
    "research.html": T("Research and publications of Lukas Netz on model-driven engineering and large language models.",
                       "Forschung und Publikationen von Lukas Netz zu modellgetriebener Softwareentwicklung und großen Sprachmodellen."),
    "photography.html": T("Photography by Lukas Netz — landscapes, people, animals and cars.",
                          "Fotografie von Lukas Netz — Landschaften, Menschen, Tiere und Autos."),
}


def main():
    for lang, sub in LANGS.items():
        out = os.path.join(ROOT, sub)
        os.makedirs(out, exist_ok=True)
        A = "../" if lang == "de" else ""
        pub_js = f'<script src="{A}assets/pubs.js"></script>\n'
        L = lambda x: x[lang]
        # canvas = WebGL noise-dissolve between photos (site.js); img = the resting photo
        lightbox = f'''<div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="{L(T("Photo", "Foto"))}">
  <canvas aria-hidden="true"></canvas>
  <img alt="">
  <div class="cap mono">
    <span class="nav"><button type="button" class="prev" aria-label="{L(T("Previous photo", "Vorheriges Foto"))}">←</button><span class="count"></span><button type="button" class="next" aria-label="{L(T("Next photo", "Nächstes Foto"))}">→</button></span>
    <span class="title" aria-live="polite"></span>
    <span class="tools">
      <svg class="progress" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.5"/></svg>
      <button type="button" class="play" aria-pressed="false"><i aria-hidden="true">▶</i> <span>{L(T("slideshow", "Diashow"))}</span></button>
      <button type="button" class="fs"><i aria-hidden="true">⤢</i> <span>{L(T("full screen", "Vollbild"))}</span></button>
      <button type="button" class="close">{L(T("close", "schließen"))} ×</button>
    </span>
  </div>
</div>
'''
        pages = {
            "index.html": (T("About", "Über mich"), about(lang), ""),
            "projects.html": (T("Projects", "Projekte"), projects(lang), ""),
            "research.html": (T("Research", "Forschung"), research(lang), pub_js),
            "photography.html": (T("Photography", "Fotografie"), photography(lang), lightbox),
        }
        for file, (title, body, scripts) in pages.items():
            html = shell(lang, file, title, DESC[file], body, scripts)
            with open(os.path.join(out, file), "w", encoding="utf8", newline="\n") as fh:
                fh.write(html)
            print(f"wrote {os.path.join(sub, file) if sub else file}  ({len(html)} bytes)")
        # one deeper page per project (project_pages.py, content in project_content.py)
        for i in range(len(project_pages.PROJECTS)):
            file, title, desc, body, scripts = project_pages.page(lang, i)
            html = shell(lang, file, title, desc, body, scripts)
            with open(os.path.join(out, file), "w", encoding="utf8", newline="\n") as fh:
                fh.write(html)
            print(f"wrote {os.path.join(sub, file) if sub else file}  ({len(html)} bytes)")


if __name__ == "__main__":
    main()
