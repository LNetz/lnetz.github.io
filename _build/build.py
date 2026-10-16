"""
Builds the static site in two languages.

    python _build/build.py

English pages go to the repository root, German pages to /de/.
Every user-facing text is written as T("english", "deutsch").
Publications live in assets/pubs.js; shared behaviour in assets/site.js.
(GitHub Pages ignores folders starting with "_", so this script is not published.)
"""
import os

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
    other = "de" if lang == "en" else "en"
    other_href = (f"de/{file}" if lang == "en" else f"../{file}")
    en_url, de_url = (file, f"de/{file}") if lang == "en" else (f"../{file}", file)

    nav = NL.join(
        f'        <li><a href="{f}"{" class=\"active\" aria-current=\"page\"" if f == file else ""}>'
        f'<span>{n}</span><span>{L(t)}</span></a></li>'
        for f, n, t in PAGES)
    social = NL.join(f'      <a href="{u}" target="_blank" rel="noopener">{name} ↗</a>' for name, u in SOCIAL)
    full_title = "Lukas Netz" if file == "index.html" else f"{L(title)} — Lukas Netz"
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
    // Theme from localStorage, applied before first paint (no flash).
    // Re-applied on pageshow so back/forward (bfcache) pages pick up a newer choice.
    (function () {{
      function apply() {{
        var t = null;
        try {{ t = localStorage.getItem("theme"); }} catch (_) {{}}
        document.documentElement.dataset.theme = t === "dark" ? "dark" : "light";
      }}
      apply();
      addEventListener("pageshow", apply);
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

  <!-- ============ index column (identical on every page) ============ -->
  <aside class="index">
    <div>
      <a class="name" href="index.html">Lukas Netz</a>
      <div class="role">Dr. rer. nat.<br>{L(T("IT Specialist", "IT-Spezialist"))}<br>mgm technology partners</div>
    </div>

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
      <button class="theme-toggle" type="button" id="theme" aria-label="{L(T("Toggle dark mode", "Dunkelmodus umschalten"))}">◐ <span>{L(T("dark mode", "Dunkelmodus"))}</span></button>
    </div>
  </aside>

  <!-- ============ content ============ -->
  <main>
{body}
    <footer class="mono">
      <span>© 2026 Lukas Netz</span>
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

def page_head(n, title, right, lead, extra="", count_id=False):
    rid = ' id="pub-count"' if count_id else ''
    return f'''    <header class="page">
      <div class="section-head">
        <h1><span class="mono">{n}</span>{title}</h1>
        <span class="mono faint"{rid}>{right}</span>
      </div>
      <p class="lead">{lead}</p>{extra}
    </header>
'''


def banner(A, src, alt, w, h):
    return f'    <figure class="banner"><img src="{A}assets/photos/{src}" alt="{alt}" width="{w}" height="{h}"></figure>\n'


def link(label, url):
    return f'<a href="{url}" target="_blank" rel="noopener">{label} ↗</a>'


def spec(A, when, name, what, tags, meta, links=(), href=None, logo=None, mark=None):
    h = f'<a href="{href}" target="_blank" rel="noopener">{name}</a>' if href else name
    t = "".join(f"<span>{x}</span>" for x in tags)
    l = "".join(link(lbl, u) for lbl, u in links)
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
{head}    <section>
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
        links=[(L(a), b) for a, b in kw.pop("links", ())], **kw)

    PROD = T("In production", "Produktiv")
    IND = T("Industry partner", "Industriepartner")
    LEAD = T("Lead developer", "Leitende Entwicklung")
    INFOSYS = T("Information system", "Informationssystem")

    esaca = S(T("now", "jetzt"), "ESACA",
        T("European Sovereign Agentic Coding Appliance — a standardised, on-premises platform that runs AI coding agents inside an organisation’s own data centre: sandboxed agents, versionable configuration, a shared hub, benchmarks on your own repositories and a guided ticket-to-reviewed-code workbench. Air-gapped capable, no external API calls.",
          "European Sovereign Agentic Coding Appliance — eine standardisierte On-Premises-Plattform, die KI-Coding-Agenten im eigenen Rechenzentrum betreibt: Agenten in der Sandbox, versionierbare Konfiguration, ein gemeinsamer Hub, Benchmarks auf den eigenen Repositories und eine geführte Workbench vom Ticket bis zum reviewten Code. Air-gapped-fähig, keine externen API-Aufrufe."),
        [T("Agentic coding", "Agentisches Coding"), "On-prem", T("Sovereign AI", "Souveräne KI")],
        [T("Platform", "Plattform"), "mgm × Fsas"], links=[("esaca.eu", "https://esaca.eu")], logo="esaca.png")

    research = [
        S("2018 — 2026", "MaCoCo",
          T("Management cockpit for controlling university chairs and institutes — finances, staff and projects in one multi-user information system, largely generated from MontiCore DSLs. Built jointly with the Chair of Management Accounting; <b>in production at RWTH</b>, with a companion Android time-tracking app.",
            "Management-Cockpit für das Controlling von Lehrstühlen und Instituten — Finanzen, Personal und Projekte in einem mehrbenutzerfähigen Informationssystem, größtenteils aus MontiCore-DSLs generiert. Gemeinsam mit dem Lehrstuhl für Controlling entwickelt; <b>produktiv im Einsatz an der RWTH</b>, mit begleitender Android-App zur Zeiterfassung."),
          ["MontiGem", INFOSYS, T("Agile", "Agil"), "Android"], [T("Project lead", "Projektleitung"), PROD],
          links=[(T("project", "Projekt"), "https://www.se-rwth.de/projects/MaCoCo/"),
                 (T("controlling chair", "Lehrstuhl Controlling"), "https://www.controlling.rwth-aachen.de/cms/controlling/forschung/forschungsprojekte/laufende-projekte/~mgaz/macoco-lehrstuhlcontrolling/"),
                 (T("android app", "Android-App"), "https://play.google.com/store/apps/details?id=macoco.stundenzettel.timetracker&amp;hl=de")],
          logo="macoco.png"),
        S("2025", "Golden UML Model Set",
          T("A community-curated dataset of UML models, each paired with a natural-language description of the modelled domain. Crawled model collections are full of invalid and placeholder models; this one is reviewed, searchable on a public web platform, and grows through a structured contribution and review process — a benchmark for UML research, education and LLM evaluation.",
            "Ein von der Community kuratierter Datensatz von UML-Modellen, jeweils mit einer natürlichsprachlichen Beschreibung der modellierten Domäne. Gecrawlte Modellsammlungen sind voller ungültiger Platzhalter-Modelle; dieser Datensatz ist geprüft, über eine öffentliche Webplattform durchsuchbar und wächst über einen strukturierten Beitrags- und Review-Prozess — ein Benchmark für UML-Forschung, Lehre und die Evaluation von LLMs."),
          [T("Dataset", "Datensatz"), "UML", "Benchmark", T("Web platform", "Webplattform")], [T("Dataset", "Datensatz"), T("Multi-university", "Mehrere Unis")],
          links=[(T("explore the dataset", "Datensatz erkunden"), "https://golden-uml-modelset.vercel.app/search"),
                 ("paper", "https://doi.org/10.1109/MODELS-C68889.2025.00012")],
          logo="uml.png"),
        S("2025", "SE-Chatty",
          T("A teaching assistant for lecturers. Fed with scripts, books, slides and videos, it answers with lecture-specific depth, helps students train for exams with generated questionnaires, and shows lecturers which parts of the material are understood — and which aren’t.",
            "Ein Lehrassistent für Dozierende. Mit Skripten, Büchern, Folien und Videos gefüttert, antwortet er mit vorlesungsspezifischer Tiefe, hilft Studierenden mit generierten Fragebögen bei der Prüfungsvorbereitung und zeigt Dozierenden, welche Teile des Stoffs verstanden werden — und welche nicht."),
          ["LLM", "RAG", T("Education", "Lehre")], [T("Tool", "Werkzeug"), "RWTH SE"], logo="se-chatty.png"),
        S("2024 — 2026", "ePHA",
          T("Electronic dissertation and habilitation repository. A model-driven application generated with MontiGem that supports the publishing process for dissertations and habilitations at RWTH; <b>in production</b>.",
            "Elektronische Promotions- und Habilitationsauslage. Eine modellgetriebene, mit MontiGem generierte Anwendung, die den Veröffentlichungsprozess von Dissertationen und Habilitationen an der RWTH unterstützt; <b>produktiv im Einsatz</b>."),
          ["MontiGem", INFOSYS], [LEAD, PROD],
          links=[("epha.rwth-aachen.de", "https://epha.rwth-aachen.de/")], logo="epha.png"),
        S("2020 — 2022", T("Ford Pro tool tracking", "Ford Pro Werkzeugverfolgung"),
          T("Pilot with the Ford Research &amp; Innovation Center Aachen: an integrated information system that tracks tools and machines across vans and job sites via Bluetooth, GPS and AI — reminders for tools left behind, theft alerts, a live map and search by vehicle or tool. The web application was generated from UML models with MontiGem and field-tested by three trade companies around Cologne.",
            "Pilotprojekt mit dem Ford Research &amp; Innovation Center Aachen: ein integriertes Informationssystem, das Werkzeuge und Maschinen über Transporter und Baustellen hinweg per Bluetooth, GPS und KI verfolgt — Erinnerung an vergessenes Werkzeug, Diebstahlwarnungen, Live-Karte und Suche nach Fahrzeug oder Werkzeug. Die Webanwendung wurde mit MontiGem aus UML-Modellen generiert und von drei Handwerksbetrieben im Raum Köln im Feld getestet."),
          ["MontiGem", "IoT", T("Industry", "Industrie")], [T("Technical lead", "Technische Leitung"), IND],
          links=[(T("Ford press release", "Ford-Pressemitteilung"), "https://media.ford.com/content/fordmedia/feu/en/news/2022/08/31/ford-pro-tool-tracking-tech-could-save-firms-1000s.html"),
                 (T("RWTH news", "RWTH-Meldung"), "https://www.se-rwth.de/projects/22.09.MontiGem.Ford.Press.Release/")],
          mark="FORD"),
        S("2018 — 2022", "Agile Data Development",
          T("Model-driven tooling for a wind-turbine manufacturer (with WZL, MSE and Bewind): integrating agile and plan-driven development with data-based decision support, including generated digital-twin cockpits for parameter management in turbine engineering.",
            "Modellgetriebene Werkzeuge für einen Windkraftanlagenhersteller (mit WZL, MSE und Bewind): Verzahnung agiler und plangetriebener Entwicklung mit datenbasierter Entscheidungsunterstützung, inklusive generierter Digital-Twin-Cockpits für das Parametermanagement in der Anlagenentwicklung."),
          ["MontiGem", T("Digital twin", "Digitaler Zwilling"), T("Industry", "Industrie")], [LEAD, IND], mark="ADD"),
        S("2018 — 2024", "MontiGem",
          T("Generator framework for enterprise information systems, built on the MontiCore language workbench. Class diagrams and GUI models in, a complete web application out — applied across five domains, from university controlling to digital-twin cockpits.",
            "Generator-Framework für betriebliche Informationssysteme auf Basis der MontiCore Language Workbench. Klassendiagramme und GUI-Modelle rein, eine vollständige Webanwendung raus — eingesetzt in fünf Domänen, vom Lehrstuhl-Controlling bis zu Digital-Twin-Cockpits."),
          ["MontiCore", "Java", "TypeScript", T("Code generation", "Codegenerierung")], ["Framework", "RWTH SE"], logo="montigem.png"),
        S("2012 — 2016", "geneial",
          T("A template-based C++11 genetic-algorithm library, developed within the DFG project OASys (online algorithms for optimal control of hybrid propulsion systems). CMake build, Boost unit tests, benchmarks and Doxygen docs.",
            "Eine template-basierte C++11-Bibliothek für genetische Algorithmen, entstanden im DFG-Projekt OASys (Online-Algorithmen zur optimalen Steuerung hybrider Antriebe). CMake-Build, Boost-Unit-Tests, Benchmarks und Doxygen-Dokumentation."),
          ["C++11", T("Evolutionary algorithms", "Evolutionäre Algorithmen"), "MIT"], [T("Library", "Bibliothek"), T("Open source", "Open Source")],
          links=[("github", "https://github.com/geneial/geneial"), ("OASys", "https://ths.rwth-aachen.de/research/projects/oasys/")],
          logo="geneial.png"),
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
            "Software, die ich gebaut oder geleitet habe — von Generator-Frameworks und produktiven Informationssystemen bis zu Plattformen für <em>agentisches Programmieren</em>.")))
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
        row("2024 —", L(T("AI4RSE working groups", "Arbeitskreise AI4RSE")),
            L(T("Spokesperson of the working groups on AI for research software engineering in the German Informatics Society (GI) and in de-RSE, the German association for research software engineering.",
                "Sprecher der Arbeitskreise zu KI für Research Software Engineering in der Gesellschaft für Informatik (GI) und bei de-RSE, dem deutschen Verein für Research Software Engineering.")),
            L(T("Spokesperson", "Sprecher"))),
        row("2026", L(T("AI in RSE workshop", "Workshop AI in RSE")),
            L(T("Program committee member of the workshop on AI in research software engineering.",
                "Mitglied im Programmkomitee des Workshops zu KI im Research Software Engineering.")),
            L(T("Program committee", "Programmkomitee"))),
        row("2023 —", "LLM-Café",
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
        count_id=True)
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

def P(f, r, w, h, alt, title, exif=""):
    return dict(f=f, r=r, w=w, h=h, alt=alt, title=title, exif=exif)


def X(f, r, alt, title=T("", "")):          # portfolio images: 1800px long edge, no EXIF
    w, h = (1800, round(1800 / r)) if r >= 1 else (round(1800 * r), 1800)
    return P(f, r, w, h, alt, title)


SERIES = [  # (anchor, name, note, rows)
    ("selected", T("Selected", "Auswahl"), "2019 — 2025", [
        [P("p07", 1.778, 2000, 1125, T("Aerial view of a coastal road curving above rocks and surf", "Luftbild einer Küstenstraße über Felsen und Brandung"), T("Coast road, aerial", "Küstenstraße, Luftbild"), "f/1.7 · 1/730 · 2023"),
         P("p02", 0.6665, 1333, 2000, T("Bride standing in a tall arched palace window, black and white", "Braut in einem hohen Bogenfenster eines Palasts, schwarzweiß"), T("Window", "Fenster"))],
        [P("p03", 1.5, 2000, 1333, T("Dog running towards the camera with leaves in its mouth", "Hund rennt mit Laub im Maul auf die Kamera zu"), T("Retrieve", "Apport"), "85mm · f/1.4 · 2024"),
         P("p05", 0.6665, 1333, 2000, T("Silhouette of a wedding couple holding hands", "Silhouette eines Hochzeitspaars, Hand in Hand"), T("Silhouette", "Silhouette"), "24mm · f/2.8"),
         P("p04", 1.5, 2000, 1333, T("Woman embracing a dark horse against a blue sky", "Frau umarmt ein dunkles Pferd vor blauem Himmel"), T("Trust", "Vertrauen"), "135mm · f/2.8 · 2023")],
        [P("p08", 1.4205, 2000, 1408, T("City lights at night seen from above", "Lichter einer Stadt bei Nacht von oben"), T("City at night, aerial", "Stadt bei Nacht, Luftbild"), "1/5 · ISO 1270 · 2025"),
         P("p01", 1.5, 2000, 1333, T("Black and white portrait with skull face paint", "Schwarzweiß-Porträt mit Totenkopf-Schminke"), T("Portrait", "Porträt"))],
        [P("p10", 1.5, 2000, 1333, T("Alpine valley with winding roads under dramatic clouds", "Alpental mit Serpentinen unter dramatischen Wolken"), T("Alps", "Alpen"), "26mm · f/11 · 2019"),
         P("p06", 1.778, 2000, 1125, T("Wet dog shaking off water in the sun", "Nasser Hund schüttelt sich in der Sonne"), T("Shake", "Schütteln"), "24mm · 1/4000 · 2025")],
        [P("p11", 1.5, 2000, 1333, T("Couple embracing in an autumn forest", "Paar umarmt sich im Herbstwald"), T("Autumn", "Herbst"), "85mm · f/2 · 2019"),
         P("p09", 1.5, 2000, 1333, T("Wedding couple playfully posing in sand dunes", "Hochzeitspaar posiert verspielt in den Dünen"), T("Dunes", "Dünen"), "24mm · f/4 · 2019")],
    ]),
    ("landscape", T("Landscape", "Landschaft"), "", [
        [X("printhno_04", 0.8, T("Rock tower in the Dolomites under heavy clouds", "Felsturm in den Dolomiten unter schweren Wolken"), T("Dolomites", "Dolomiten")),
         X("printhno_05", 1.25, T("Jagged Dolomite peaks at dusk", "Zackige Dolomitengipfel in der Dämmerung"), T("Dolomites", "Dolomiten")),
         X("printhno_07", 1.25, T("Dolomite massif above a scree slope", "Dolomitenmassiv über einem Geröllhang"), T("Dolomites", "Dolomiten"))],
        [X("printhno_02", 1.5, T("Alpine valley with layered mountain ridges", "Alpental mit gestaffelten Bergrücken"), T("Valley", "Tal")),
         X("printhno_03", 1.5, T("Snow-capped peak above dark ridges and clouds", "Schneebedeckter Gipfel über dunklen Graten und Wolken"), T("Peaks", "Gipfel"))],
        [X("printhno_10", 1.5, T("Vineyard rows seen from above", "Rebzeilen eines Weinbergs von oben"), T("Vineyard, aerial", "Weinberg, Luftbild")),
         X("printhno_12", 1.5, T("Wooden jetty on a calm misty lake", "Holzsteg an einem ruhigen, nebligen See"), T("Jetty", "Steg"))],
        [X("printhno_08", 2.6277, T("Tree-lined canal with calm water", "Von Bäumen gesäumter Kanal mit ruhigem Wasser"), T("Canal du Midi, France", "Canal du Midi, Frankreich"))],
    ]),
    ("people", T("People", "Menschen"), "", [
        [X("portfolio_07", 1.25, T("Woman with curly hair in low-key studio light", "Frau mit Locken im Low-Key-Studiolicht"), T("Studio", "Studio")),
         X("portfolio_13", 0.6667, T("Smiling woman in black and white", "Lächelnde Frau in Schwarzweiß"), T("Light", "Licht")),
         X("portfolio_33", 0.6667, T("Black and white portrait of a woman with long hair", "Schwarzweiß-Porträt einer Frau mit langen Haaren"), T("Portrait", "Porträt"))],
        [X("portfolio_16", 1.5, T("Smiling elderly woman, black and white close-up", "Lächelnde ältere Frau, Schwarzweiß-Nahaufnahme"), T("Laugh lines", "Lachfalten")),
         X("portfolio_34", 1.5, T("Close portrait of a woman against a dark background", "Nahes Porträt einer Frau vor dunklem Hintergrund"), T("Gaze", "Blick"))],
        [X("portfolio_09", 0.6667, T("Rider and horse jumping in the dark", "Reiterin und Pferd beim Sprung im Dunkeln"), T("Jump", "Sprung")),
         X("portfolio_15", 0.6667, T("Basketball player mid-dunk, black and white", "Basketballspieler beim Dunk, schwarzweiß"), T("Dunk", "Dunk")),
         X("portfolio_25", 0.6667, T("Athlete throwing a ball in backlight", "Sportler wirft einen Ball im Gegenlicht"), T("Throw", "Wurf")),
         X("portfolio_60", 0.6667, T("Low-key black and white profile with hair falling forward", "Low-Key-Profil in Schwarzweiß mit nach vorn fallendem Haar"), T("Low key", "Low Key"))],
        [X("portfolio_14", 1.5, T("Street scene with silhouettes against the sun", "Straßenszene mit Silhouetten im Gegenlicht"), T("Street", "Straße")),
         X("portfolio_48", 1.5, T("Woman lying on a dark surface, black and white", "Frau liegt auf dunklem Untergrund, schwarzweiß"), T("Rest", "Ruhe")),
         X("portfolio_59", 0.6667, T("Woman covering her face with her hands in warm light", "Frau verbirgt das Gesicht in den Händen, warmes Licht"), T("Shy", "Scheu"))],
    ]),
    ("animals", T("Animals", "Tiere"), "", [
        [X("baily_00", 1.25, T("Dog splashing through water", "Hund springt durchs Wasser"), T("Splash", "Spritzer")),
         X("baily_02", 0.8, T("Border collie sitting in golden grass", "Border Collie sitzt im goldenen Gras"), T("Golden hour", "Goldene Stunde")),
         X("baily_13", 0.8, T("Dog with closed eyes on white background", "Hund mit geschlossenen Augen vor weißem Hintergrund"), T("Calm", "Gelassen"))],
        [X("baily_06", 0.6667, T("Shepherd dog in low-key light", "Schäferhund im Low-Key-Licht"), T("Low key", "Low Key")),
         X("baily_11", 0.6667, T("Border collie catching a ball on white", "Border Collie fängt einen Ball, weißer Hintergrund"), T("Catch", "Fang")),
         X("baily_08", 1.5, T("Shepherd dog lying in the dark", "Schäferhund liegt im Dunkeln"), T("Rest", "Ruhe"))],
    ]),
    ("automotive", T("Automotive", "Automobil"), "", [
        [X("polo_01", 1.25, T("Light trails around a white car at night", "Lichtspuren um ein weißes Auto bei Nacht"), T("Light painting", "Lichtmalerei")),
         X("polo_13", 0.6667, T("Racing stripes on a car roof, close-up", "Rennstreifen auf einem Autodach, Nahaufnahme"), T("Stripes", "Streifen")),
         X("polo_18", 1.25, T("White car with headlights on in the dark", "Weißes Auto mit eingeschalteten Scheinwerfern im Dunkeln"), T("Headlights", "Scheinwerfer"))],
        [X("polo_07", 1.5, T("Car headlights glowing in darkness", "Leuchtende Autoscheinwerfer in der Dunkelheit"), T("Night", "Nacht")),
         X("polo_09", 1.5, T("Car under a starry sky on a dark field", "Auto unter Sternenhimmel auf einem dunklen Feld"), T("Stars", "Sterne")),
         X("polo_14", 0.6667, T("Car on a country road at sunset", "Auto auf einer Landstraße bei Sonnenuntergang"), T("Road", "Landstraße"))],
    ]),
]


def photography(lang):
    L = lambda x: x[lang] if isinstance(x, dict) else x
    A = "../" if lang == "de" else ""

    def fig(p):
        return (f'          <figure style="--r:{p["r"]}"><img src="{A}assets/photos/{p["f"]}.jpg" alt="{L(p["alt"])}" loading="lazy" '
                f'width="{p["w"]}" height="{p["h"]}"><figcaption class="mono"><span>{L(p["title"])}</span><span>{p["exif"]}</span></figcaption></figure>')

    def series(anchor, name, note, rows):
        body = NL.join('        <div class="row">' + NL + NL.join(fig(p) for p in r) + NL + "        </div>" for r in rows)
        n = sum(len(r) for r in rows)
        right = (note + " · " if note else "") + str(n)
        return (f'      <div class="group mono series" id="{anchor}"><span>{L(name)}</span><span>{right}</span></div>' + NL +
                '      <div class="photos">' + NL + body + NL + '      </div>')

    n = sum(len(r) for _, _, _, rows in SERIES for r in rows)
    nav = "".join(f'<a href="#{a}">{L(name).lower()}</a>' for a, name, _, _ in SERIES)
    extra = f'''
      <div class="bio">
        <p>{L(T("By playing with an extraordinarily complex high-tech instrument that exploits the limits of physics in the most ingenious way, you can hold on to the most beautiful moments forever — in a fraction of a second.",
               "Durch das Spielen mit einem ausgefallen-komplexen Hightech-Instrument, das auf raffinierteste Weise die Grenzen der Physik ausnutzt, kann man die schönsten Momente in einem Bruchteil einer Sekunde für immer festhalten."))}</p>
      </div>'''
    head = page_head("03", L(T("Photography", "Fotografie")), L(T(f"{n} photographs", f"{n} Fotografien")),
        L(T("Photography has fascinated me from the very first moment. The camera is one of the few tools that lets you not only show a very particular perspective on the world, but also capture and share <em>memories and emotions</em>.",
            "Die Fotografie hat mich vom ersten Moment an begeistert. Die Kamera ist eines der wenigen Werkzeuge, die es einem ermöglichen, nicht nur einen ganz bestimmten Blickwinkel auf die Welt zu zeigen, sondern auch <em>Erinnerungen und Emotionen</em> einzufangen und zu teilen.")),
        extra)
    pic = banner(A, "about-dolomites.jpg", L(T("Lukas Netz with a camera, looking out over the Dolomites",
                                               "Lukas Netz mit Kamera, Blick über die Dolomiten")), 2400, 769)
    return f'''
{head}{pic}
    <section>
      <nav class="filters mono" aria-label="{L(T("Series", "Serien"))}">{nav}</nav>
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
        lightbox = '<div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="Photo"><img alt=""><div class="cap mono"></div></div>\n'
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


if __name__ == "__main__":
    main()
