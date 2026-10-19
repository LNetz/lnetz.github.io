"""
Content of the project pages (rendered by project_pages.py). Order = order on the project list.
Every user-facing text is T("english", "deutsch"); a chapter text may also be a function (lang, A) -> html.
"""
import os
import re


def T(en, de):
    return {"en": en, "de": de}


def ext(label, url):
    return f'<a href="{url}" target="_blank" rel="noopener">{label} ↗</a>'


def stats(lang, items):
    return '<div class="stats">' + "".join(f'<div><b>{n}</b><span>{l[lang]}</span></div>' for n, l in items) + '</div>'


def pts(lang, items):
    return '<ul class="pts">' + "".join(f"<li>{i[lang]}</li>" for i in items) + "</ul>"


def video(yt, thumb, title, caption):
    def render(lang, A):
        from project_pages import video as v      # late import: project_pages imports this module
        return v(lang, A, yt, thumb, title, caption)
    return render


ROLE = T("Role", "Rolle")
PERIOD = T("Period", "Zeitraum")
PARTNER = T("Partner", "Partner")
STATUS = T("Status", "Status")
PROD = T("In production", "Produktiv")


# =====================================================================
# Diagrams (inline SVG, colours from the theme — see .dia in style.css)
# =====================================================================

def _arrow_defs(id_):
    return (f'<defs><marker id="{id_}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0 1L9 5L0 9" fill="none" stroke="currentColor" stroke-width="1.4"/></marker>'
            f'<marker id="{id_}a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0 1L9 5L0 9" fill="none" style="stroke:var(--accent)" stroke-width="1.4"/></marker></defs>')


def box(x, y, w, h, title, sub="", cls="box", sub2=""):
    """A labelled box; the text is centred."""
    cx = x + w / 2
    lines = [l for l in (sub, sub2) if l]
    ty = y + h / 2 + 4 - 8 * len(lines)
    out = f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/><text x="{cx}" y="{ty}" text-anchor="middle" class="t">{title}</text>'
    for k, l in enumerate(lines):
        out += f'<text x="{cx}" y="{ty + 17 + 14 * k}" text-anchor="middle" class="s">{l}</text>'
    return out


def chip(x, y, label="AST"):
    return f'<rect class="box" x="{x}" y="{y}" width="40" height="22" rx="11"/><text x="{x + 20}" y="{y + 15}" text-anchor="middle" class="s">{label}</text>'


def figure(svg, caption, lang):
    return f'''    <figure class="media"><div class="dia-scroll">{svg}</div>
      <figcaption class="mono">{caption[lang]}</figcaption>
    </figure>
'''


def montigem_diagram(lang, A):
    L = lambda x: x[lang]
    m, ma = 'marker-end="url(#ma)"', 'marker-end="url(#maa)"'
    rows = []
    for y, parser, trafo in ((56, "GUI", "UI-Trafo"), (156, "CD4A", "DS-Trafo")):
        rows.append(box(176, y, 92, 50, f"{parser}", "parser")
                    + f'<path class="ln" d="M268 {y + 25}H280" />' + chip(280, y + 14) + f'<path class="ln" d="M320 {y + 25}H330" {m}/>'
                    + box(332, y, 92, 50, trafo, "M2M")
                    + f'<path class="ln" d="M424 {y + 25}H436" />' + chip(436, y + 14) + f'<path class="ln" d="M476 {y + 25}H486" {m}/>'
                    + box(488, y, 104, 50, "Templates", "FreeMarker"))
    svg = f'''<svg class="dia" viewBox="0 0 960 370" role="img" aria-label="{L(T("MontiGem generator architecture: models are parsed, transformed and printed into a Java back end and an Angular front end; handwritten code extends the generated code", "MontiGem-Generatorarchitektur: Modelle werden geparst, transformiert und in ein Java-Backend und ein Angular-Frontend übersetzt; handgeschriebener Code erweitert den generierten"))}">
  {_arrow_defs("ma")}
  <text x="0" y="16" class="s">{L(T("MODELS", "MODELLE"))}</text>
  {box(0, 56, 128, 50, L(T("GUI models", "GUI-Modelle")), L(T("one per page", "eins pro Seite")))}
  {box(0, 146, 128, 70, L(T("Class diagrams", "Klassendiagramme")), L(T("domain · view ·", "Domäne · View ·")), sub2=L(T("command (CD4A)", "Command (CD4A)")))}
  {box(0, 266, 128, 50, "OCL", "optional", cls="box dashbox")}

  <rect class="zone" x="150" y="26" width="466" height="310" rx="4"/>
  <text x="166" y="330" class="s">{L(T("GENERATOR · MontiCore", "GENERATOR · MontiCore"))}</text>
  {"".join(rows)}
  {box(176, 266, 92, 50, "OCL/P", "parser")}
  <path class="ln" d="M268 291H280"/>{chip(280, 280)}
  <path class="ln" d="M320 291H378V210" {m}/>
  <rect class="box hl" x="436" y="250" width="156" height="66" rx="3" style="stroke-dasharray:4 3"/>
  <text x="514" y="276" text-anchor="middle" class="t">CD2GUI</text>
  <text x="514" y="293" text-anchor="middle" class="s">{L(T("derives GUI models", "leitet GUI-Modelle"))}</text>
  <text x="514" y="306" text-anchor="middle" class="s">{L(T("from the classes", "aus den Klassen ab"))}</text>
  <path class="ln hl dash" d="M222 206V232H514V250" />
  <path class="ln hl dash" d="M592 270H606V40H300V66" {ma}/>

  <path class="ln" d="M128 81H172" {m}/>
  <path class="ln" d="M128 181H172" {m}/>
  <path class="ln" d="M128 291H172" {m}/>

  <rect class="zone" x="660" y="26" width="300" height="310" rx="4"/>
  <text x="676" y="44" class="s">{L(T("APPLICATION", "ANWENDUNG"))}</text>
  <text x="676" y="72" class="s">{L(T("generated", "generiert"))}</text>
  <text x="832" y="72" class="s">{L(T("handwritten", "handgeschrieben"))}</text>
  {box(676, 82, 124, 54, "Client", "Angular · TS/HTML")}
  {box(676, 176, 124, 54, "Server", "Java · REST")}
  {box(832, 82, 112, 54, "Client", "TOP", cls="box hl")}
  {box(832, 176, 112, 54, "Server", "TOP", cls="box hl")}
  <path class="ln hl" d="M832 109H804" {ma}/>
  <path class="ln hl" d="M832 203H804" {ma}/>
  <text x="816" y="152" text-anchor="middle" class="s a">extends</text>
  <path class="ln" d="M738 136V172" {m}/>
  <path d="M676 270a62 9 0 0 1 124 0v34a62 9 0 0 1 -124 0z" class="box"/><path d="M676 270a62 9 0 0 0 124 0" class="ln"/>
  <text x="738" y="300" text-anchor="middle" class="t">{L(T("Database", "Datenbank"))}</text>
  <path class="ln" d="M738 230V258" {m}/>
  <text x="832" y="290" class="s">{L(T("+ runtime: Angular,", "+ Laufzeit: Angular,"))}</text>
  <text x="832" y="304" class="s">TomEE, Hibernate,</text>
  <text x="832" y="318" class="s">Shiro, Docker</text>

  <path class="ln" d="M592 81H640V100H672" {m}/>
  <text x="598" y="74" class="s">HTML · TS</text>
  <path class="ln" d="M592 172H640V120H672" {m}/>
  <path class="ln" d="M592 190H672" {m}/>
  <text x="620" y="166" class="s">TS</text>
  <text x="612" y="204" class="s">Java</text>
</svg>'''
    return figure(svg, T("<b>From models to a running application.</b> Each model language has a parser generated by MontiCore; the syntax trees are transformed and printed by FreeMarker templates into an Angular front end and a Java back end. CD2GUI (dashed) can derive the GUI models from the class diagram. Handwritten code lives in separate folders and <i>extends</i> the generated classes (TOP mechanism), so everything can be regenerated at any time. After <a class=\"cite\" href=\"#Net24\">[Net24]</a>, Fig. 7.1.",
                           "<b>Von Modellen zur laufenden Anwendung.</b> Jede Modellsprache hat einen von MontiCore generierten Parser; die Syntaxbäume werden transformiert und über FreeMarker-Templates in ein Angular-Frontend und ein Java-Backend übersetzt. CD2GUI (gestrichelt) kann die GUI-Modelle aus dem Klassendiagramm ableiten. Handgeschriebener Code liegt in eigenen Ordnern und <i>erweitert</i> die generierten Klassen (TOP-Mechanismus), sodass jederzeit neu generiert werden kann. Nach <a class=\"cite\" href=\"#Net24\">[Net24]</a>, Abb. 7.1."), lang)


def epha_diagram(lang, A):
    L = lambda x: x[lang]
    m, ma = 'marker-end="url(#pa)"', 'marker-end="url(#paa)"'
    steps = [
        (T("Doctoral office", "Promotionsbüro"), T("creates the display:", "legt die Auslage an:"), T("thesis, reviews, period", "Arbeit, Gutachten, Frist")),
        (T("Professors", "Professor:innen"), T("are notified — at once", "werden benachrichtigt —"), T("or weekly, by subject", "sofort oder wöchentlich")),
        (T("Display period", "Auslagefrist"), T("read thesis, summary", "Arbeit, Zusammenfassung"), T("and reviews online", "und Gutachten online lesen")),
        (T("Dean’s office", "Dekanat"), T("receives comments:", "erhält Kommentare:"), T("praise · criticism · neutral", "Lob · Kritik · neutral")),
    ]
    parts = []
    for k, (t, s1, s2) in enumerate(steps):
        x = k * 188
        parts.append(box(x, 40, 172, 76, L(t), L(s1), cls="box hl" if k == 2 else "box", sub2=L(s2)))
        parts.append(f'<text x="{x}" y="24" class="s a">0{k + 1}</text>')
        if k < 3:
            parts.append(f'<path class="ln{" hl" if k == 1 else ""}" d="M{x + 172} 78H{x + 184}" {ma if k == 1 else m}/>')
    svg = f'''<svg class="dia" viewBox="0 0 740 160" role="img" aria-label="{L(T("How a dissertation is displayed in ePHA, in four steps", "Wie eine Dissertation in ePHA ausgelegt wird, in vier Schritten"))}">
  {_arrow_defs("pa")}
  {"".join(parts)}
  <path class="ln dash" d="M86 116V140H650V120" {m}/>
  <text x="365" y="154" text-anchor="middle" class="s">{L(T("then: invitations to the defence", "danach: Einladungen zur Disputation"))}</text>
</svg>'''
    return figure(svg, T("The display of a thesis, from the doctoral office to the dean’s office — what used to be paper copies in a room is now a web application.",
                         "Die Auslage einer Arbeit, vom Promotionsbüro bis zum Dekanat — was früher Papierexemplare in einem Raum waren, ist jetzt eine Webanwendung."), lang)


def smtrat_diagram(lang, A):
    """The dependency problem: the same polynomial on x ∈ [0, 1], evaluated three ways."""
    L = lambda x: x[lang]
    X = lambda v: 260 + (v + 1) * 220                 # value → x coordinate (−1 … 1 → 260 … 700)
    rows = [
        ("x² − x", L(T("as written", "wie geschrieben")), -1, 1, "box", "[−1, 1]"),
        ("x · (x − 1)", L(T("Horner scheme", "Horner-Schema")), -1, 0, "box hl", "[−1, 0]"),
        (L(T("true range", "tatsächlich")), L(T("what we want", "das Ziel")), -0.25, 0, "zone", "[−¼, 0]"),
    ]
    out = []
    for k, (f, sub, lo, hi, cls, lbl) in enumerate(rows):
        y = 40 + k * 46
        out.append(f'<text x="0" y="{y + 13}" class="t">{f}</text><text x="120" y="{y + 13}" class="s">{sub}</text>'
                   f'<rect class="{cls}" x="{X(lo)}" y="{y}" width="{X(hi) - X(lo)}" height="18" rx="2"'
                   f'{" style=\"fill:var(--accent);opacity:.35\"" if cls == "zone" else ""}/>'
                   f'<text x="{X(hi) + 10}" y="{y + 13}" class="s">{lbl}</text>')
    ticks = "".join(f'<path class="ln" d="M{X(v)} 172V178"/><text x="{X(v)}" y="194" text-anchor="middle" class="s">{t}</text>'
                    for v, t in ((-1, "−1"), (-0.5, "−½"), (0, "0"), (0.5, "½"), (1, "1")))
    svg = f'''<svg class="dia" viewBox="0 0 760 200" role="img" aria-label="{L(T("Interval evaluation of x squared minus x for x between 0 and 1: as written the result is minus 1 to 1, as a Horner scheme minus 1 to 0, the true range is minus a quarter to 0", "Intervallauswertung von x Quadrat minus x für x zwischen 0 und 1: wie geschrieben ergibt sich minus 1 bis 1, als Horner-Schema minus 1 bis 0, tatsächlich minus ein Viertel bis 0"))}">
  <text x="0" y="16" class="s">{L(T("EVALUATED ON THE INTERVAL x ∈ [0, 1]", "AUSGEWERTET AUF DEM INTERVALL x ∈ [0, 1]"))}</text>
  <path class="ln dash" d="M{X(0)} 30V172"/>
  {"".join(out)}
  <path class="ln" d="M{X(-1) - 10} 172H{X(1) + 10}"/>{ticks}
</svg>'''
    return figure(svg, T("<b>The dependency problem.</b> Interval arithmetic treats every occurrence of <i>x</i> as an independent value from [0, 1], so <i>x² − x</i> comes out as [−1, 1] — eight times wider than the true range. Rewritten as a Horner scheme, <i>x</i> appears less often and the result tightens to [−1, 0]. Tighter intervals let ICP cut away more of the search space in each step.",
                         "<b>Das Abhängigkeitsproblem.</b> Intervallarithmetik behandelt jedes Vorkommen von <i>x</i> als unabhängigen Wert aus [0, 1], daher ergibt <i>x² − x</i> das Intervall [−1, 1] — achtmal breiter als der tatsächliche Wertebereich. Als Horner-Schema umgeschrieben kommt <i>x</i> seltener vor, und das Ergebnis schrumpft auf [−1, 0]. Engere Intervalle lassen ICP in jedem Schritt mehr vom Suchraum wegschneiden."), lang)


def shot(lang, A, src, w, h, alt, caption):
    return f'''<figure class="media"><div class="paper"><img src="{A}assets/projects/{src}" alt="{alt[lang]}" width="{w}" height="{h}" loading="lazy"></div>
            <figcaption class="mono">{caption[lang]}</figcaption></figure>'''


def esaca_diagram(lang, A):
    L = lambda x: x[lang]
    m = 'marker-end="url(#ea)"'
    ma = 'marker-end="url(#eaa)"'
    svg = f'''<svg class="dia" viewBox="0 0 760 330" role="img" aria-label="{L(T("ESACA architecture: everything runs inside the organisation’s own perimeter", "ESACA-Architektur: alles läuft innerhalb der eigenen Infrastruktur"))}">
  {_arrow_defs("ea")}
  <rect class="zone line" x="1" y="1" width="598" height="326" rx="4"/>
  <text x="16" y="22" class="s">{L(T("YOUR DATA CENTRE · ON-PREM OR AIR-GAPPED", "EIGENES RECHENZENTRUM · ON-PREM ODER AIR-GAPPED"))}</text>

  <rect class="box" x="20" y="44" width="560" height="62" rx="3"/>
  <text x="34" y="66" class="t">Workbench</text>
  <text x="34" y="86" class="s">{L(T("ticket → plan → agents → human review → merge request", "Ticket → Plan → Agenten → menschliches Review → Merge-Request"))}</text>

  <rect class="zone" x="20" y="124" width="380" height="132" rx="3"/>
  <text x="34" y="144" class="s">SANDBOX</text>
  <rect class="box hl" x="34" y="156" width="160" height="84" rx="3"/>
  <text x="48" y="178" class="t">{L(T("Workspace", "Workspace"))}</text>
  <text x="48" y="198">{L(T("coding agent", "Coding-Agent"))}</text>
  <text x="48" y="214">{L(T("+ repository", "+ Repository"))}</text>
  <text x="48" y="230" class="s">{L(T("sees placeholders only", "sieht nur Platzhalter"))}</text>
  <rect class="box" x="226" y="156" width="160" height="84" rx="3"/>
  <text x="240" y="178" class="t">Egress</text>
  <text x="240" y="198">deny by default</text>
  <text x="240" y="214">{L(T("injects secrets", "setzt Secrets ein"))}</text>
  <text x="240" y="230" class="s">{L(T("every call logged", "jeder Aufruf geloggt"))}</text>
  <path class="ln hl" d="M194 198H222" {ma}/>

  <rect class="box" x="420" y="124" width="160" height="58" rx="3"/>
  <text x="434" y="146" class="t">{L(T("Sovereign model", "Souveränes Modell"))}</text>
  <text x="434" y="166" class="s">{L(T("on own hardware", "auf eigener Hardware"))}</text>
  <rect class="box" x="420" y="198" width="160" height="58" rx="3"/>
  <text x="434" y="220" class="t">{L(T("Git · artifacts", "Git · Artefakte"))}</text>
  <text x="434" y="240" class="s">{L(T("internal services", "interne Dienste"))}</text>
  <path class="ln" d="M386 186L416 160" {m}/>
  <path class="ln" d="M386 214L416 226" {m}/>
  <path class="ln" d="M300 106V124" {m}/>

  <rect class="box" x="20" y="272" width="270" height="40" rx="3"/>
  <text x="34" y="296"><tspan class="t" style="font-family:var(--sans);font-weight:500;fill:var(--ink)">Config</tspan>  {L(T("one file, versioned", "eine Datei, versioniert"))}</text>
  <rect class="box" x="310" y="272" width="270" height="40" rx="3"/>
  <text x="324" y="296"><tspan style="font-family:var(--sans);font-weight:500;fill:var(--ink)">Hub · Benchmark</tspan>  {L(T("share · measure", "teilen · messen"))}</text>

  <path class="ln dash" d="M600 165H664"/>
  <text x="626" y="161" class="a" style="font-size:16px">×</text>
  <rect class="box" x="668" y="140" width="88" height="50" rx="25" style="stroke-dasharray:3 4"/>
  <text x="712" y="161" text-anchor="middle" class="s">{L(T("public", "öffentliche"))}</text>
  <text x="712" y="176" text-anchor="middle" class="s">cloud APIs</text>
</svg>'''
    return f'''    <figure class="media"><div class="dia-scroll">{svg}</div>
      <figcaption class="mono">{L(T("Agents, code, secrets and models stay inside the organisation’s perimeter. The agent works in a sandbox and only ever sees placeholder credentials; a second container decides — and logs — what may leave.",
                                    "Agenten, Code, Secrets und Modelle bleiben innerhalb der eigenen Infrastruktur. Der Agent arbeitet in einer Sandbox und sieht nur Platzhalter-Zugangsdaten; ein zweiter Container entscheidet — und protokolliert —, was nach außen darf."))}</figcaption>
    </figure>
'''


def chatty_diagram(lang, A):
    L = lambda x: x[lang]
    m = 'marker-end="url(#ca)"'
    ma = 'marker-end="url(#caa)"'
    svg = f'''<svg class="dia" viewBox="0 0 760 210" role="img" aria-label="{L(T("How SE-Chatty works", "So funktioniert SE-Chatty"))}">
  {_arrow_defs("ca")}
  <rect class="box" x="1" y="30" width="170" height="150" rx="3"/>
  <text x="16" y="54" class="s">{L(T("LECTURE MATERIAL", "VORLESUNGSMATERIAL"))}</text>
  <text x="16" y="80">{L(T("script · book", "Skript · Buch"))}</text>
  <text x="16" y="100">{L(T("slides", "Folien"))}</text>
  <text x="16" y="120">{L(T("lecture videos", "Vorlesungsvideos"))}</text>
  <text x="16" y="140">{L(T("exercises", "Übungen"))}</text>
  <path class="ln" d="M171 105H215" {m}/>
  <rect class="box hl" x="219" y="60" width="200" height="90" rx="3"/>
  <text x="235" y="86" class="t">SE-Chatty</text>
  <text x="235" y="108">{L(T("retrieves the passages", "sucht die passenden Stellen"))}</text>
  <text x="235" y="124">{L(T("then lets the LLM answer", "und lässt das LLM antworten"))}</text>
  <text x="235" y="140" class="s">RAG</text>
  <path class="ln hl" d="M419 84H495" {ma}/>
  <path class="ln" d="M495 126H423" {m}/>
  <rect class="box" x="499" y="30" width="260" height="70" rx="3"/>
  <text x="515" y="56" class="t">{L(T("Students", "Studierende"))}</text>
  <text x="515" y="76">{L(T("ask questions · train with", "stellen Fragen · üben mit"))}</text>
  <text x="515" y="91">{L(T("generated questionnaires", "generierten Fragebögen"))}</text>
  <rect class="box" x="499" y="112" width="260" height="70" rx="3"/>
  <text x="515" y="138" class="t">{L(T("Lecturers", "Dozierende"))}</text>
  <text x="515" y="158">{L(T("see which topics are understood", "sehen, welche Themen verstanden"))}</text>
  <text x="515" y="173">{L(T("— and which aren’t", "werden — und welche nicht"))}</text>
</svg>'''
    return f'''    <figure class="media"><div class="dia-scroll">{svg}</div>
      <figcaption class="mono">{L(T("Answers come from the lecture’s own material, not from the model’s general knowledge — and the questions students ask flow back to the lecturer.",
                                    "Antworten stammen aus dem Material der Vorlesung, nicht aus dem Allgemeinwissen des Modells — und die Fragen der Studierenden fließen zurück an die Dozierenden."))}</figcaption>
    </figure>
'''


def uml_svg(name, label):
    """The model set's own PlantUML SVG, inlined so style.css (.uml) can recolour it for the theme."""
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "projects", name), encoding="utf8").read()
    head, rest = src.split(">", 1)
    vb = re.search(r'viewBox="([^"]+)"', head).group(1)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{label}">{rest}'


def golden_media(lang, A):
    L = lambda x: x[lang]
    desc = ("A university consists of several faculties, which are made up of various institutes. Each faculty and institute has a name. "
            "The address of each institute is known. Each faculty is headed by a dean, who is an employee of the university. "
            "The total number of employees is known. Employees have a social security number, a name, and an email address. "
            "A distinction is made between research and administrative staff. Research assistants (RA) are assigned to at least one institute. "
            "The field of research of each RA is known. In addition, RAs can be involved in projects for a certain number of hours, whereby the name, "
            "start and end dates of the projects are known. Some RAs teach courses. In this case, they are referred to as lecturers. "
            "Courses have a unique number (ID), a name and a weekly duration in hours.")
    return f'''    <figure class="media golden">
      <div class="pair">
        <blockquote>
          <div class="mono faint">{L(T("description", "Beschreibung"))} · University</div>
          <p>{desc}</p>
        </blockquote>
        <div class="uml">{uml_svg("golden-university.svg", L(T("UML class diagram of the University case: abstract class Employee with AdministrativeEmployee and ResearchAssociate, Lecturer as a subclass of ResearchAssociate, Faculty composed of Institutes, Projects linked through the association class Participation, and Lecturer teaches Course", "UML-Klassendiagramm des Falls University: abstrakte Klasse Employee mit AdministrativeEmployee und ResearchAssociate, Lecturer als Unterklasse von ResearchAssociate, Faculty aus Institutes zusammengesetzt, Projects über die Assoziationsklasse Participation verbunden, Lecturer teaches Course")))}</div>
      </div>
      <figcaption class="mono">{L(T("One of the 45 cases: the natural-language description (left) and the reviewed reference model (right). Case <b>University</b>, contributed by the Business Informatics Group, TU Wien — CC BY 4.0.",
                                    "Einer der 45 Fälle: die natürlichsprachliche Beschreibung (links) und das geprüfte Referenzmodell (rechts). Fall <b>University</b>, beigetragen von der Business Informatics Group, TU Wien — CC BY 4.0."))}
        {ext(L(T("open the case", "Fall öffnen")), "https://golden-uml-modelset.vercel.app/model/University")}</figcaption>
    </figure>
'''


def geneial_media(lang, A):
    L = lambda x: x[lang]
    return f'''    <figure class="media">
      <div class="cutout"><img src="{A}assets/projects/geneial-ea-loop.webp" alt="{L(T("Cycle diagram of one generation of an evolutionary algorithm: stopping criteria, selection with elitism, coupling, crossover, choosing, mutation and replenishment from the chromosome factory", "Kreisdiagramm einer Generation eines evolutionären Algorithmus: Abbruchkriterien, Selektion mit Elitismus, Kopplung, Crossover, Auswahl, Mutation und Auffüllen aus der Chromosomen-Fabrik"))}" width="1400" height="1266" loading="lazy"></div>
      <figcaption class="mono">{L(T("One generation of an evolutionary algorithm — every box is an exchangeable operator in geneial. From <a class=\"cite\" href=\"#Net17\">[Net17]</a>.",
                                    "Eine Generation eines evolutionären Algorithmus — jeder Kasten ist ein austauschbarer Operator in geneial. Aus <a class=\"cite\" href=\"#Net17\">[Net17]</a>."))}</figcaption>
    </figure>
'''


GENEIAL_CODE = '''auto evaluator = std::make_shared&lt;DemoChromosomeEvaluator&gt;();

ContinousMultiValueChromosomeFactory&lt;int,double&gt;::Builder factoryBuilder(evaluator);
factoryBuilder.getSettings().setNum(20);
factoryBuilder.getSettings().setRandomMin(20);
factoryBuilder.getSettings().setRandomMax(130);

auto algorithm = SteadyStateAlgorithm&lt;double&gt;::Builder()
    .setChromosomeFactory(factoryBuilder.create()).create();
algorithm-&gt;getPopulationSettings().setMaxChromosomes(100);
algorithm-&gt;solve();

std::cout &lt;&lt; *algorithm-&gt;getHighestFitnessChromosome() &lt;&lt; std::endl;'''


# =====================================================================
# The projects
# =====================================================================

PROJECTS = [
    dict(
        slug="esaca", name="ESACA", when=T("since 2025", "seit 2025"), logo="esaca.png",
        desc=T("ESACA — a sovereign, on-premises platform for agentic coding in regulated organisations.",
               "ESACA — eine souveräne On-Premises-Plattform für agentisches Programmieren in regulierten Organisationen."),
        lead=T("AI coding agents are fast — and they read code, run commands and send data wherever they like. ESACA lets <em>regulated organisations</em> use them anyway: inside their own data centre, under their own rules.",
               "KI-Coding-Agenten sind schnell — und sie lesen Code, führen Befehle aus und schicken Daten, wohin sie wollen. ESACA macht sie für <em>regulierte Organisationen</em> trotzdem nutzbar: im eigenen Rechenzentrum, nach eigenen Regeln."),
        facts=[(T("Organisation", "Organisation"), "mgm × Fsas Technologies"), (T("Runs", "Betrieb"), T("on-prem · air-gapped", "on-prem · air-gapped")),
               (T("Models", "Modelle"), T("model-independent", "modellunabhängig"))],
        links=[("esaca.eu", "https://esaca.eu")],
        media=esaca_diagram,
        chapters=[
            (T("The problem", "Das Problem"), T(
                "<p>Banks, utilities, public authorities and defence suppliers face the same dilemma. Agentic coding promises large productivity gains, but a cloud-based agent can send source code and secrets to a foreign provider, delete data or pull in a malicious extension — and it ties the organisation to one vendor’s model, prices and roadmap. Banning the tools only pushes teams into shadow IT, where nobody measures what the agents actually deliver.</p>",
                "<p>Banken, Versorger, Behörden und Rüstungszulieferer stehen vor demselben Dilemma. Agentisches Programmieren verspricht große Produktivitätsgewinne, aber ein cloudbasierter Agent kann Quellcode und Secrets an einen fremden Anbieter schicken, Daten löschen oder eine bösartige Erweiterung nachladen — und er bindet die Organisation an das Modell, die Preise und die Roadmap eines Anbieters. Ein Verbot treibt Teams nur in die Schatten-IT, wo niemand misst, was die Agenten wirklich leisten.</p>")),
            (T("The idea", "Die Idee"), T(
                "<p>ESACA — the <b>European Sovereign Agentic Coding Appliance</b> — is a standardised system that brings coding agents into the organisation’s own perimeter: on-premises or fully air-gapped, with no data egress, no external API calls and no hidden telemetry. It is model-independent and favours sovereign models running on the customer’s own hardware. ESACA is an initiative of mgm technology partners and Fsas Technologies, a Fujitsu company.</p>",
                "<p>ESACA — die <b>European Sovereign Agentic Coding Appliance</b> — ist ein standardisiertes System, das Coding-Agenten in die eigene Infrastruktur holt: on-premises oder vollständig air-gapped, ohne Datenabfluss, ohne externe API-Aufrufe, ohne versteckte Telemetrie. Es ist modellunabhängig und setzt bevorzugt auf souveräne Modelle auf der eigenen Hardware des Kunden. ESACA ist eine Initiative von mgm technology partners und Fsas Technologies, einem Fujitsu-Unternehmen.</p>")),
            (T("The building blocks", "Die Bausteine"), lambda lang, A: pts(lang, [
                T("<b>Sandbox</b> — the agent and the project run in one container, all outbound traffic goes through a second one. Access is deny-by-default, the agent only sees placeholder credentials, real secrets are injected on the way out, every decision is logged.",
                  "<b>Sandbox</b> — Agent und Projekt laufen in einem Container, der gesamte ausgehende Verkehr über einen zweiten. Zugriffe sind standardmäßig verboten, der Agent sieht nur Platzhalter-Zugangsdaten, echte Secrets werden erst auf dem Weg nach draußen eingesetzt, jede Entscheidung wird protokolliert."),
                T("<b>Configuration</b> — one versionable file describes the whole environment: access rules, agents, skills, plugins, tools and versions.",
                  "<b>Konfiguration</b> — eine versionierbare Datei beschreibt die ganze Umgebung: Zugriffsregeln, Agenten, Skills, Plugins, Werkzeuge und Versionen."),
                T("<b>Hub</b> — proven configurations are shared and reused across projects.",
                  "<b>Hub</b> — bewährte Konfigurationen werden projektübergreifend geteilt und wiederverwendet."),
                T("<b>Benchmark</b> — measures the complete system (agent + model + hardware) on the organisation’s own repositories, keeping hard metrics such as builds and tests apart from LLM-as-judge scores.",
                  "<b>Benchmark</b> — misst das Gesamtsystem (Agent + Modell + Hardware) auf den eigenen Repositories und trennt harte Metriken wie Builds und Tests von LLM-as-Judge-Bewertungen."),
                T("<b>Workbench</b> — a guided path from ticket to plan to agents in isolated workspaces, ending in a mandatory human review before the normal merge process.",
                  "<b>Workbench</b> — ein geführter Weg vom Ticket über den Plan zu Agenten in isolierten Workspaces, mit verpflichtendem menschlichem Review vor dem normalen Merge-Prozess."),
            ])),
            (T("Who it is for", "Für wen"), T(
                "<p>Critical infrastructure and utilities, the public sector, and regulated industries such as defence, legal and healthcare — organisations that work under NIS-2, BaFin, ISO 27001 and GDPR. The adoption path goes step by step, from assistants to agents, multi-agent workflows and finally AI-native development, with people staying in the decision seat.</p>",
                "<p>Kritische Infrastruktur und Versorger, die öffentliche Verwaltung und regulierte Branchen wie Verteidigung, Recht und Gesundheitswesen — Organisationen, die unter NIS-2, BaFin, ISO 27001 und DSGVO arbeiten. Der Einstieg erfolgt schrittweise, von Assistenten über Agenten und Multi-Agenten-Workflows bis zur KI-nativen Entwicklung, wobei der Mensch die Entscheidungen trifft.</p>")),
        ],
    ),
    dict(
        slug="macoco", name="MaCoCo", when="2018 — 2026", logo="macoco.png",
        desc=T("MaCoCo — a management cockpit for controlling university chairs, largely generated from models. In production at RWTH Aachen.",
               "MaCoCo — ein Management-Cockpit für das Lehrstuhl-Controlling, größtenteils aus Modellen generiert. Produktiv an der RWTH Aachen."),
        lead=T("Every university chair manages real money — grants, contracts, staff paid from several projects — but the university’s ERP system is built for the central administration. MaCoCo gives the chairs <em>their own cockpit</em>, and most of its code was never written by hand.",
               "Jeder Lehrstuhl verwaltet echtes Geld — Drittmittel, Verträge, Personal aus mehreren Projekten finanziert —, doch das ERP-System der Hochschule ist für die zentrale Verwaltung gebaut. MaCoCo gibt den Lehrstühlen <em>ihr eigenes Cockpit</em>, und der Großteil seines Codes wurde nie von Hand geschrieben."),
        facts=[(ROLE, T("Project lead", "Projektleitung")), (PARTNER, T("Chair of Management Accounting", "Lehrstuhl für Controlling")),
               (STATUS, T("In production at RWTH", "Produktiv an der RWTH")), (T("Generated", "Generiert"), T("~ 3/4 of the code", "~ 3/4 des Codes"))],
        links=[(T("project", "Projekt"), "https://www.se-rwth.de/projects/MaCoCo/"),
               (T("controlling chair", "Lehrstuhl Controlling"), "https://www.controlling.rwth-aachen.de/cms/controlling/forschung/forschungsprojekte/laufende-projekte/~mgaz/macoco-lehrstuhlcontrolling/"),
               (T("android app", "Android-App"), "https://play.google.com/store/apps/details?id=macoco.stundenzettel.timetracker&amp;hl=de")],
        media=video("2AibynH6Bm0", "macoco-video.jpg", T("MaCoCo image film", "MaCoCo-Imagefilm"),
                    T("<b>MaCoCo image film</b> — what the cockpit does for a chair, in a few minutes.",
                      "<b>MaCoCo-Imagefilm</b> — was das Cockpit für einen Lehrstuhl leistet, in wenigen Minuten.")),
        chapters=[
            (T("The problem", "Das Problem"), T(
                "<p>When RWTH moved its administration to SAP, the system served the central offices well — but not the roughly 400 chairs and institutes that each run their own budgets. They need to know how much money is left on which grant, which contract is financed from which project, and whether the project’s time sheets are complete. Most kept this in spreadsheets or home-grown tools: error-prone, single-user and invisible to everyone else.</p>",
                "<p>Als die RWTH ihre Verwaltung auf SAP umstellte, war das System für die zentralen Stellen gemacht — nicht für die rund 400 Lehrstühle und Institute, die jeweils eigene Budgets führen. Sie müssen wissen, wie viel Geld auf welchem Drittmittelprojekt übrig ist, welcher Vertrag aus welchem Projekt finanziert wird und ob die Stundenzettel des Projekts vollständig sind. Die meisten führten das in Tabellen oder Eigenbauten: fehleranfällig, einzelplatzfähig und für niemanden sonst sichtbar.</p>")),
            (T("The cockpit", "Das Cockpit"), lambda lang, A: pts(lang, [
                T("<b>Finances</b> — budgets, income and expenses across all accounts and projects, with planned spending and forecasts.",
                  "<b>Finanzen</b> — Budgets, Einnahmen und Ausgaben über alle Konten und Projekte, mit geplanten Ausgaben und Prognosen."),
                T("<b>Staff</b> — master data, contracts and their financing; staff costs flow automatically into the projects that pay them.",
                  "<b>Personal</b> — Stammdaten, Verträge und ihre Finanzierung; Personalkosten fließen automatisch in die Projekte, die sie tragen."),
                T("<b>Projects</b> — time sheets for funders that require them (with a companion Android app), staffing plans and org charts.",
                  "<b>Projekte</b> — Stundenzettel für Geldgeber, die sie verlangen (mit begleitender Android-App), Besetzungsplanung und Organigramme."),
            ]) + shot(lang, A, "macoco-dashboard.jpg", 1600, 1007,
                      T("MaCoCo dashboard with a finance overview donut chart, a budget breakdown table and lists of accounts with high remaining budget or negative balance (demo data)",
                        "MaCoCo-Dashboard mit Finanzübersicht als Ringdiagramm, Budgetaufteilung und Listen von Konten mit hohem Restbudget oder negativem Saldo (Demodaten)"),
                      T("The dashboard of a chair (demo data): budget, spending, planned spending and the accounts that need attention.",
                        "Das Dashboard eines Lehrstuhls (Demodaten): Budget, Ausgaben, Planausgaben und die Konten, die Aufmerksamkeit brauchen."))),
            (T("Built from models", "Aus Modellen gebaut"), lambda lang, A: T(
                "<p>MaCoCo started in 2016 as a hand-written prototype. Step by step, generated code replaced it — first the data classes and persistence, then the commands, the validation from OCL constraints and finally the whole front end from GUI models. The generator that grew out of this work became <a href=\"projects-montigem.html\">MontiGem</a>. Today the domain is described in class diagrams and GUI models; hand-written business logic is plugged in where it is needed, without ever being overwritten by the generator.</p>",
                "<p>MaCoCo begann 2016 als handgeschriebener Prototyp. Schritt für Schritt ersetzte generierter Code ihn — zuerst Datenklassen und Persistenz, dann die Commands, die Validierung aus OCL-Constraints und schließlich das ganze Frontend aus GUI-Modellen. Der Generator, der dabei entstand, wurde zu <a href=\"projects-montigem.html\">MontiGem</a>. Heute ist die Domäne in Klassendiagrammen und GUI-Modellen beschrieben; handgeschriebene Geschäftslogik wird dort eingehängt, wo sie nötig ist, ohne je vom Generator überschrieben zu werden.</p>")[lang]
                + stats(lang, [("~1.1 M", T("lines of code", "Zeilen Code")), ("74 %", T("of it generated", "davon generiert")),
                               ("~150", T("domain classes", "Domänenklassen")), ("60", T("GUI models", "GUI-Modelle"))])
                + T('<p class="mono faint"><a class="cite" href="#Net24">[Net24]</a></p>', '<p class="mono faint"><a class="cite" href="#Net24">[Net24]</a></p>')[lang]),
            (T("Agile, with its users", "Agil, mit den Nutzern"), T(
                "<p>MaCoCo is developed in a Scrum-like cycle together with lead users from all faculties. A steering committee — data protection, staff councils, finance and HR administration, IT Center and deans — meets twice a year; users meet monthly. Critical fixes ship on demand, everything else every two to three months. Because the system is regenerated from models, even large changes to the domain stay affordable.</p>",
                "<p>MaCoCo wird in einem Scrum-ähnlichen Zyklus gemeinsam mit Lead-Usern aus allen Fakultäten entwickelt. Ein Lenkungskreis — Datenschutz, Personalräte, Finanz- und Personalverwaltung, IT Center und Dekanate — tagt zweimal im Jahr, die Nutzer treffen sich monatlich. Kritische Korrekturen gehen sofort live, alles andere alle zwei bis drei Monate. Weil das System aus Modellen neu generiert wird, bleiben auch große Änderungen an der Domäne bezahlbar.</p>")),
            (T("In production", "Im Einsatz"), lambda lang, A: T(
                "<p>MaCoCo is hosted by the RWTH IT Center and connected to SAP; every chair gets its own database. It is used across the university every working day.</p>",
                "<p>MaCoCo wird vom IT Center der RWTH betrieben und ist an SAP angebunden; jeder Lehrstuhl bekommt eine eigene Datenbank. Es wird an jedem Arbeitstag hochschulweit genutzt.</p>")[lang]
                + stats(lang, [("200+", T("chairs &amp; institutes", "Lehrstühle &amp; Institute")), ("~200", T("logins per working day", "Logins pro Arbeitstag")), ("2016", T("in development since", "in Entwicklung seit"))])),
        ],
        pubs=["GLM+24", "Net24", "DGM+21", "GMN+20", "AMN+20a", "GHK+20", "ANV+18"],
    ),
    dict(
        slug="golden-uml", name="Golden UML Model Set", when="2025", logo="uml.png",
        desc=T("The Golden UML Model Set — a community-curated, reviewed dataset of UML models with natural-language domain descriptions.",
               "Das Golden UML Model Set — ein von der Community kuratierter, geprüfter Datensatz von UML-Modellen mit natürlichsprachlichen Domänenbeschreibungen."),
        lead=T("If an LLM turns a text into a UML model — is the model any good? To answer that you need <em>reference solutions</em>: descriptions paired with models that people have actually checked.",
               "Wenn ein LLM aus einem Text ein UML-Modell macht — ist das Modell gut? Um das zu beantworten, braucht man <em>Referenzlösungen</em>: Beschreibungen mit Modellen, die Menschen tatsächlich geprüft haben."),
        facts=[(T("Cases", "Fälle"), "45"), (T("Universities", "Universitäten"), "RWTH · TU Wien · KU Leuven · McGill"),
               (T("Type", "Art"), T("Dataset + web platform", "Datensatz + Webplattform"))],
        links=[(T("explore the dataset", "Datensatz erkunden"), "https://golden-uml-modelset.vercel.app/search"),
               ("GitHub", "https://github.com/Charlotte-Verbruggen/GoldenUMLmodelset"),
               ("Zenodo", "https://doi.org/10.5281/zenodo.16985872")],
        media=golden_media,
        chapters=[
            (T("The problem", "Das Problem"), T(
                "<p>The large existing UML collections were built by crawling GitHub and online modelling platforms. They are full of syntactically broken, semantically wrong, duplicate and placeholder models — and almost none of them come with the text that says what the model is supposed to represent. Without that text you cannot tell whether a model is right, so they are weak as exercises and weak as benchmarks. The text-to-UML datasets built for LLMs, on the other hand, contain at most a dozen models or no reference solutions at all.</p>",
                "<p>Die großen bestehenden UML-Sammlungen sind durch Crawlen von GitHub und Online-Modellierungsplattformen entstanden. Sie sind voller syntaktisch kaputter, semantisch falscher, doppelter und Platzhalter-Modelle — und fast keines kommt mit dem Text, der sagt, was das Modell abbilden soll. Ohne diesen Text lässt sich nicht beurteilen, ob ein Modell richtig ist; als Übungen und als Benchmark taugen sie daher wenig. Die Text-zu-UML-Datensätze für LLMs wiederum enthalten höchstens ein Dutzend Modelle oder gar keine Referenzlösungen.</p>")),
            (T("The dataset", "Der Datensatz"), lambda lang, A: T(
                "<p>The Golden UML Model Set goes the other way: fewer models, all of them reviewed. It starts with 45 cases from modelling courses and exams at RWTH Aachen, TU Wien, KU Leuven and McGill, plus a database textbook — exercises refined over years of student feedback. Every case pairs a requirements text with a class diagram in PlantUML; many add extra material such as alternative or deliberately wrong solutions with explanations. Cases are labelled by domain, from sales and logistics to healthcare and education.</p>",
                "<p>Das Golden UML Model Set geht den umgekehrten Weg: weniger Modelle, dafür alle geprüft. Es beginnt mit 45 Fällen aus Modellierungsvorlesungen und Klausuren der RWTH Aachen, TU Wien, KU Leuven und McGill sowie aus einem Datenbank-Lehrbuch — Übungen, die über Jahre mit studentischem Feedback verbessert wurden. Jeder Fall verbindet einen Anforderungstext mit einem Klassendiagramm in PlantUML; viele bringen Zusatzmaterial mit, etwa alternative oder absichtlich falsche Lösungen mit Erklärung. Die Fälle sind nach Domänen gelabelt, von Vertrieb und Logistik bis Gesundheitswesen und Lehre.</p>")[lang]
                + stats(lang, [("45", T("cases", "Fälle")), ("5", T("sources", "Quellen")), ("28", T("with inheritance", "mit Vererbung")), ("17", T("with association classes", "mit Assoziationsklassen"))])),
            (T("Growing it together", "Gemeinsam wachsen"), T(
                "<p>Anyone can contribute a case through a web form or a GitHub pull request. At least one reviewer checks it against a checklist — completeness and duplicates, metadata, clarity of the description, UML syntax, and whether the model actually matches the text. Approved cases appear immediately on a searchable web platform with filters for domain, size and modelling constructs; versioned snapshots go to Zenodo and Hugging Face so that research can cite an exact release.</p>",
                "<p>Jede und jeder kann einen Fall über ein Webformular oder einen GitHub-Pull-Request beitragen. Mindestens eine Reviewerin oder ein Reviewer prüft ihn anhand einer Checkliste — Vollständigkeit und Duplikate, Metadaten, Verständlichkeit der Beschreibung, UML-Syntax und ob das Modell wirklich zum Text passt. Angenommene Fälle erscheinen sofort auf einer durchsuchbaren Webplattform mit Filtern nach Domäne, Größe und Modellierungskonstrukten; versionierte Stände gehen an Zenodo und Hugging Face, damit Forschung eine exakte Version zitieren kann.</p>")),
            (T("What it is for", "Wofür"), lambda lang, A: pts(lang, [
                T("<b>Teaching</b> — a shared pool of modelling exercises with solutions, and variants of a case to train students in judging solutions against requirements.",
                  "<b>Lehre</b> — ein gemeinsamer Pool von Modellierungsaufgaben mit Lösungen, und Varianten eines Falls, an denen Studierende üben, Lösungen gegen Anforderungen zu beurteilen."),
                T("<b>LLM evaluation</b> — generative AI almost always produces <i>some</i> model; the question is its quality. Reviewed reference solutions make it possible to compare generated models semantically against a ground truth.",
                  "<b>Evaluation von LLMs</b> — generative KI liefert fast immer <i>irgendein</i> Modell; die Frage ist seine Qualität. Geprüfte Referenzlösungen ermöglichen den semantischen Vergleich generierter Modelle mit einer Ground Truth."),
            ])),
        ],
        pubs=["VNG+25"],
    ),
    dict(
        slug="se-chatty", name="SE-Chatty", when="2025", logo="se-chatty.png",
        desc=T("SE-Chatty — an LLM-based teaching assistant that answers from the lecture’s own material.",
               "SE-Chatty — ein LLM-basierter Lehrassistent, der aus dem Material der Vorlesung antwortet."),
        lead=T("A teaching assistant that knows <em>this</em> lecture — not just the internet. It answers with the depth of the course material and tells the lecturer where students struggle.",
               "Ein Lehrassistent, der <em>diese</em> Vorlesung kennt — nicht nur das Internet. Er antwortet mit der Tiefe des Kursmaterials und zeigt den Dozierenden, wo Studierende hängen."),
        facts=[(T("Type", "Art"), T("Tool", "Werkzeug")), (T("Built at", "Entstanden"), "RWTH SE"), (T("Technique", "Technik"), "LLM · RAG")],
        links=[("ai.se.rwth-aachen.de/se-chatty", "https://ai.se.rwth-aachen.de/se-chatty/")],
        media=chatty_diagram,
        chapters=[
            (T("The problem", "Das Problem"), T(
                "<p>General-purpose chatbots answer lecture questions with general knowledge: plausible, but often at the wrong level, with different notation than the course, and sometimes simply wrong. Lecturers, meanwhile, only find out what students did not understand when they grade the exam.</p>",
                "<p>Allgemeine Chatbots beantworten Fragen zur Vorlesung mit Allgemeinwissen: plausibel, aber oft auf dem falschen Niveau, mit anderer Notation als im Kurs und manchmal schlicht falsch. Dozierende erfahren dagegen erst bei der Klausurkorrektur, was nicht verstanden wurde.</p>")),
            (T("How it works", "So funktioniert es"), T(
                "<p>SE-Chatty is fed with the lecture’s own material — scripts, books, slides and videos. For every question it first retrieves the relevant passages and then lets the language model answer on that basis (retrieval-augmented generation). The answers therefore follow the course: its terms, its examples, its depth.</p>",
                "<p>SE-Chatty wird mit dem Material der Vorlesung gefüttert — Skripte, Bücher, Folien und Videos. Zu jeder Frage sucht es zuerst die passenden Stellen heraus und lässt das Sprachmodell auf dieser Grundlage antworten (Retrieval-Augmented Generation). Die Antworten folgen so dem Kurs: seinen Begriffen, seinen Beispielen, seiner Tiefe.</p>")),
            (T("For students and lecturers", "Für Studierende und Dozierende"), lambda lang, A: pts(lang, [
                T("<b>Students</b> ask questions at any time and prepare for the exam with generated questionnaires.",
                  "<b>Studierende</b> stellen jederzeit Fragen und bereiten sich mit generierten Fragebögen auf die Prüfung vor."),
                T("<b>Lecturers</b> see which parts of the material are understood — and which aren’t — while the course is still running.",
                  "<b>Dozierende</b> sehen, welche Teile des Stoffs verstanden werden — und welche nicht —, solange die Vorlesung noch läuft."),
            ])),
        ],
    ),
    dict(
        slug="epha", name="ePHA", when="2024 — 2026", logo="epha.png",
        desc=T("ePHA — RWTH’s model-driven application for publishing dissertations and habilitations.",
               "ePHA — die modellgetriebene Anwendung der RWTH für die Auslage von Dissertationen und Habilitationen."),
        lead=T("Before a doctorate is awarded, the thesis and its reviews are <em>laid out</em> for the faculty’s professors to inspect. ePHA moves this from a room full of paper copies to the web.",
               "Bevor eine Promotion abgeschlossen wird, werden die Arbeit und ihre Gutachten für die Professorinnen und Professoren der Fakultät <em>ausgelegt</em>. ePHA holt das aus einem Raum voller Papierexemplare ins Web."),
        facts=[(ROLE, T("Lead developer", "Leitende Entwicklung")), (T("Users", "Nutzer"), T("Faculty 1, RWTH", "Fakultät 1, RWTH")),
               (STATUS, PROD), (T("Built with", "Gebaut mit"), "MontiGem")],
        links=[("epha.rwth-aachen.de", "https://epha.rwth-aachen.de/")],
        media=epha_diagram,
        chapters=[
            (T("The problem", "Das Problem"), T(
                "<p>At a German faculty, a dissertation or habilitation is not just accepted by the reviewers: for a fixed period, every professor of the faculty may read the thesis and the reviews and raise concerns before the faculty decides. Traditionally that meant paper copies in the dean’s office — professors had to come by during opening hours to read them.</p>",
                "<p>An einer deutschen Fakultät wird eine Dissertation oder Habilitation nicht allein von den Gutachtern angenommen: Für eine feste Frist darf jede Professorin und jeder Professor der Fakultät die Arbeit und die Gutachten lesen und Einwände erheben, bevor die Fakultät entscheidet. Früher hieß das: Papierexemplare im Dekanat — wer sie lesen wollte, musste zu den Öffnungszeiten vorbeikommen.</p>")),
            (T("How it works", "So funktioniert es"), T(
                "<p>The doctoral office creates a display for each thesis: candidate, title, subject group, reviewers and examiners, the documents as PDFs — thesis, summary, bibliography, reviews — and the display period. Professors are notified by e-mail, either immediately or in a weekly digest, filtered by the subject groups they care about. During the period they read everything online and can send a comment — praise, criticism or a neutral note — directly to the dean’s office. Invitations to the defence go out from the same application.</p>",
                "<p>Das Promotionsbüro legt für jede Arbeit eine Auslage an: Kandidat:in, Titel, Fachgruppe, Gutachter und Prüfer, die Dokumente als PDF — Arbeit, Zusammenfassung, Literaturverzeichnis, Gutachten — und die Auslagefrist. Professor:innen werden per E-Mail benachrichtigt, sofort oder in einer wöchentlichen Zusammenfassung, gefiltert nach den Fachgruppen, die sie interessieren. Während der Frist lesen sie alles online und können einen Kommentar — Lob, Kritik oder eine neutrale Anmerkung — direkt ans Dekanat schicken. Auch die Einladungen zur Disputation gehen aus derselben Anwendung heraus.</p>")),
            (T("Model-driven", "Modellgetrieben"), T(
                "<p>ePHA is a small application by design, and that is exactly where model-driven development pays off: the domain — theses, documents, reviewers, displays, comments, notification settings — is described as a class diagram, and the application is generated from it with the <a href=\"projects-montigem.html\">MontiGem</a> tool chain. The result runs in production for the Faculty of Mathematics, Computer Science and Natural Sciences.</p>",
                "<p>ePHA ist bewusst eine kleine Anwendung — und genau dort zahlt sich modellgetriebene Entwicklung aus: Die Domäne — Arbeiten, Dokumente, Gutachter, Auslagen, Kommentare, Benachrichtigungseinstellungen — ist als Klassendiagramm beschrieben, und die Anwendung wird daraus mit der <a href=\"projects-montigem.html\">MontiGem</a>-Werkzeugkette generiert. Das Ergebnis läuft produktiv für die Fakultät für Mathematik, Informatik und Naturwissenschaften.</p>")),
        ],
    ),
    dict(
        slug="ford", name=T("Ford Pro tool tracking", "Ford Pro Werkzeugverfolgung"), when="2020 — 2022", mark="FORD",
        desc=T("Ford Pro tool tracking — a pilot with Ford Research &amp; Innovation Center Aachen: tools tracked across vans and job sites, web app generated with MontiGem.",
               "Ford Pro Werkzeugverfolgung — ein Pilot mit dem Ford Research &amp; Innovation Center Aachen: Werkzeuge über Transporter und Baustellen verfolgt, Webanwendung mit MontiGem generiert."),
        lead=T("Tradespeople lose tools: left behind on a site, or stolen from the van. Together with Ford we built a system that <em>knows where every tool is</em> — and reminds you before you drive off without it.",
               "Handwerker verlieren Werkzeug: auf der Baustelle vergessen oder aus dem Transporter gestohlen. Gemeinsam mit Ford haben wir ein System gebaut, das <em>weiß, wo jedes Werkzeug ist</em> — und erinnert, bevor man ohne es losfährt."),
        facts=[(ROLE, T("Technical lead", "Technische Leitung")), (PARTNER, "Ford R&amp;I Center Aachen"),
               (T("Field test", "Feldtest"), T("3 companies · ~11 months", "3 Betriebe · ~11 Monate")), (T("Built with", "Gebaut mit"), "MontiGem")],
        links=[(T("RWTH news", "RWTH-Meldung"), "https://www.se-rwth.de/projects/22.09.MontiGem.Ford.Press.Release/")],
        media=video("ODuvZ6AahzI", "ford-video.jpg", T("Ford helps businesses keep track of work tools", "Ford hilft Betrieben, ihr Werkzeug im Blick zu behalten"),
                    T("<b>Ford Europe:</b> “Ford Helps Businesses Keep Track of Work Tools” — the pilot in use at one of the test companies.",
                      "<b>Ford Europe:</b> „Ford Helps Businesses Keep Track of Work Tools“ — der Pilot im Einsatz bei einem der Testbetriebe.")),
        chapters=[
            (T("The problem", "Das Problem"), lambda lang, A: T(
                "<p>Gardeners, plumbers and renovation crews carry expensive tools and machines in their vans. Tools get left behind on site or stolen, and every loss costs money and working time — searching, re-buying, waiting.</p>",
                "<p>Gärtner, Installateure und Sanierungsbetriebe haben teure Werkzeuge und Maschinen im Transporter. Werkzeug bleibt auf der Baustelle liegen oder wird gestohlen, und jeder Verlust kostet Geld und Arbeitszeit — suchen, nachkaufen, warten.</p>")[lang]
                + stats(lang, [("€450", T("lost per van and year", "Verlust pro Transporter und Jahr")), ("€38", T("saved per vehicle and month", "Ersparnis pro Fahrzeug und Monat")),
                               ("~1 h", T("per week saved by workers", "pro Woche für Mitarbeitende")), ("~2 h", T("per week saved by admins", "pro Woche für die Verwaltung"))])
                + T('<p class="mono faint">Estimates from the field test, RWTH Chair of Marketing.</p>', '<p class="mono faint">Schätzungen aus dem Feldtest, Lehrstuhl für Marketing der RWTH.</p>')[lang]),
            (T("The system", "Das System"), T(
                "<p>Every tool gets a small, heat- and water-resistant Bluetooth tag; every vehicle a tracking module that knows which tools are on board and reports their positions via GPS to a central server. If a tool is missing when the van is about to leave, the driver is reminded; if one moves when it shouldn’t, the owner is alerted. A web application shows everything on desktops, phones and a tablet in the vehicle: search by vehicle, storage place, tool type or name, photo tiles of the tools, and a live map of where each one was last seen.</p>",
                "<p>Jedes Werkzeug bekommt einen kleinen, hitze- und wasserfesten Bluetooth-Tag, jedes Fahrzeug ein Tracking-Modul, das weiß, welche Werkzeuge an Bord sind, und ihre Positionen per GPS an einen zentralen Server meldet. Fehlt beim Losfahren ein Werkzeug, wird der Fahrer erinnert; bewegt sich eines, wenn es das nicht sollte, bekommt der Inhaber eine Warnung. Eine Webanwendung zeigt alles auf Desktop, Smartphone und einem Tablet im Fahrzeug: Suche nach Fahrzeug, Lagerort, Werkzeugtyp oder Name, Kacheln mit Fotos der Werkzeuge und eine Live-Karte mit dem letzten bekannten Standort.</p>")),
            (T("Generated, not hand-written", "Generiert, nicht handgeschrieben"), T(
                "<p>The web application was largely generated with our <a href=\"projects-montigem.html\">MontiGem</a> framework from UML models of the data, the user interface and standard behaviour. That made fast iterations possible, and the models became a shared language between Ford’s marketing experts, engineers, designers and the craftspeople. Two extensions grew out of the project and went back into the generator: multi-language support (German for the craftspeople, English for Ford’s managers) with an in-app translation editor, and a driving-safe tablet UI that shows less information while the vehicle is moving, based on its measured acceleration.</p>",
                "<p>Die Webanwendung wurde größtenteils mit unserem Framework <a href=\"projects-montigem.html\">MontiGem</a> aus UML-Modellen der Daten, der Oberfläche und des Standardverhaltens generiert. Das ermöglichte schnelle Iterationen, und die Modelle wurden zur gemeinsamen Sprache zwischen Fords Marketing-Expertinnen, Ingenieuren, Designern und den Handwerkern. Zwei Erweiterungen sind aus dem Projekt entstanden und in den Generator zurückgeflossen: Mehrsprachigkeit (Deutsch für die Handwerker, Englisch für Fords Management) mit einem Übersetzungseditor in der Anwendung, und eine fahrsichere Tablet-Oberfläche, die während der Fahrt — anhand der gemessenen Beschleunigung — weniger Informationen zeigt.</p>")),
            (T("Field test", "Feldtest"), T(
                "<p>Three trade companies of different sizes around Cologne — construction and renovation, plumbing, gardening and landscaping — used the system for about eleven months. The application was improved continuously from their feedback and from usage data. Ford presented the results in 2022; the project also taught us where generated web apps reach their limits — patchy mobile coverage on site later led to a native Android app.</p>",
                "<p>Drei Handwerksbetriebe unterschiedlicher Größe im Raum Köln — Bau und Sanierung, Sanitär, Garten- und Landschaftsbau — haben das System rund elf Monate genutzt. Die Anwendung wurde laufend anhand ihres Feedbacks und der Nutzungsdaten verbessert. Ford hat die Ergebnisse 2022 vorgestellt; das Projekt hat uns auch gezeigt, wo generierte Webanwendungen an Grenzen stoßen — lückenhafter Mobilfunk auf Baustellen führte später zu einer nativen Android-App.</p>")),
        ],
        pubs=["BGK+24"],
    ),
    dict(
        slug="add", name="Agile Data Development", when="2018 — 2022", mark="ADD",
        desc=T("Agile Data Development — generated digital-twin cockpits for parameter management in wind-turbine engineering.",
               "Agile Data Development — generierte Digital-Twin-Cockpits für das Parametermanagement in der Windkraftanlagenentwicklung."),
        lead=T("Designing a wind turbine means thousands of parameters, CAD files and simulation results passed between specialists — often by e-mail. We built a <em>single point of truth</em> for this engineering data, generated from a model the customer can change on their own.",
               "Eine Windkraftanlage zu entwickeln heißt: Tausende Parameter, CAD-Dateien und Simulationsergebnisse wandern zwischen Spezialisten hin und her — oft per E-Mail. Wir haben dafür eine <em>zentrale Datenquelle</em> gebaut, generiert aus einem Modell, das der Kunde selbst ändern kann."),
        facts=[(ROLE, T("Lead developer", "Leitende Entwicklung")), (PARTNER, "WZL · MSE · Bewind"),
               (T("Funding", "Förderung"), T("Cluster of Excellence IoP", "Exzellenzcluster IoP")), (T("Built with", "Gebaut mit"), "MontiGem · CD2GUI")],
        media=lambda lang, A: f'''    <figure class="media"><div class="paper"><img src="{A}assets/projects/add-cd2gui-page.jpg" alt="{T("Generated detail page of a pitch configuration in the wind-turbine cockpit, listing linked and available safety systems", "Generierte Detailseite einer Pitch-Konfiguration im Windkraft-Cockpit mit verknüpften und verfügbaren Sicherheitssystemen")[lang]}" width="1600" height="875" loading="lazy"></div>
      <figcaption class="mono">{T("A page nobody drew: the detail view of a pitch configuration, generated by CD2GUI straight from the class diagram (2021).", "Eine Seite, die niemand gezeichnet hat: die Detailansicht einer Pitch-Konfiguration, von CD2GUI direkt aus dem Klassendiagramm generiert (2021).")[lang]}</figcaption>
    </figure>
''',
        chapters=[
            (T("The problem", "Das Problem"), T(
                "<p>In wind-turbine engineering many disciplines work on the same machine: mechanics, electrics, control, simulation. Their parameters depend on each other, and a value changed in one place has to reach every other. In practice it travelled as e-mail attachments and files on individual laptops — outdated values crept in, and past simulation results were hard to find again. Agile and plan-driven development had to come together on one reliable data basis.</p>",
                "<p>In der Entwicklung einer Windkraftanlage arbeiten viele Disziplinen an derselben Maschine: Mechanik, Elektrik, Regelung, Simulation. Ihre Parameter hängen voneinander ab, und ein an einer Stelle geänderter Wert muss alle anderen erreichen. In der Praxis wanderte er als E-Mail-Anhang und Datei auf einzelnen Laptops — veraltete Werte schlichen sich ein, alte Simulationsergebnisse waren schwer wiederzufinden. Agile und plangetriebene Entwicklung mussten auf einer verlässlichen Datenbasis zusammenkommen.</p>")),
            (T("The cockpit", "Das Cockpit"), T(
                "<p>The result is a web cockpit — an engineering digital twin “as designed” — where engineers look up, edit, version and release parameters, CAD files and simulation results. A change history and archive, a release lifecycle (draft → review → released → outdated) with a check that released objects only point to released objects, and a diff view keep every value traceable. A Python library connects the engineering tools themselves — Rhino, Ansys, SpaceClaim — so they read and write the data through the API instead of local files.</p>",
                "<p>Das Ergebnis ist ein Web-Cockpit — ein digitaler Zwilling der Entwicklung, „as designed“ —, in dem Ingenieur:innen Parameter, CAD-Dateien und Simulationsergebnisse nachschlagen, bearbeiten, versionieren und freigeben. Änderungshistorie und Archiv, ein Freigabe-Lebenszyklus (Entwurf → Review → freigegeben → veraltet) mit der Prüfung, dass freigegebene Objekte nur auf freigegebene verweisen, und eine Diff-Ansicht machen jeden Wert nachvollziehbar. Eine Python-Bibliothek bindet die Engineering-Werkzeuge selbst an — Rhino, Ansys, SpaceClaim —, sodass sie die Daten über die API statt über lokale Dateien lesen und schreiben.</p>")),
            (T("Generated from one class diagram", "Aus einem Klassendiagramm generiert"), lambda lang, A: T(
                "<p>ADD was the first real project for <b>CD2GUI</b>, an extension of <a href=\"projects-montigem.html\">MontiGem</a> that derives the user interface from the class diagram: for every class, a navigation, an overview and an editing page. Engineers had a clickable prototype within days, and the customer could extend the data schema — which grew to more than 120 classes and 200 relations — and simply regenerate. Where generic pages were not enough, hand-written GUI models and charts were added on top, such as the views of simulation results below.</p>",
                "<p>ADD war das erste echte Projekt für <b>CD2GUI</b>, eine Erweiterung von <a href=\"projects-montigem.html\">MontiGem</a>, die die Oberfläche aus dem Klassendiagramm ableitet: für jede Klasse eine Navigations-, eine Übersichts- und eine Bearbeitungsseite. Die Ingenieur:innen hatten nach wenigen Tagen einen klickbaren Prototyp, und der Kunde konnte das Datenschema erweitern — es wuchs auf über 120 Klassen und 200 Beziehungen — und einfach neu generieren. Wo generische Seiten nicht reichten, kamen handgeschriebene GUI-Modelle und Diagramme hinzu, etwa die Ansichten von Simulationsergebnissen unten.</p>")[lang]
                + stats(lang, [("120+", T("classes", "Klassen")), ("200+", T("relations", "Beziehungen")), ("3", T("generated pages per class", "generierte Seiten pro Klasse"))])
                + shot(lang, A, "add-simulation-charts.jpg", 1118, 751,
                       T("Four charts of simulated loads Fx to Mz: a polar plot, a pie chart, a heat map and a 3D surface", "Vier Diagramme simulierter Lasten Fx bis Mz: Polardiagramm, Tortendiagramm, Heatmap und 3D-Fläche"),
                       T("Simulation results of the turbine loads, visualised in the cockpit.", "Simulationsergebnisse der Anlagenlasten, im Cockpit visualisiert."))),
        ],
        pubs=["MNN+22", "BGK+24", "DHM+22"],
    ),
    dict(
        slug="montigem", name="MontiGem", when="2018 — 2024", logo="montigem.png",
        desc=T("MontiGem — a generator framework that turns class diagrams and GUI models into complete web-based information systems.",
               "MontiGem — ein Generator-Framework, das aus Klassendiagrammen und GUI-Modellen vollständige webbasierte Informationssysteme erzeugt."),
        lead=T("Describe the data and the pages in small, precise models — and get a complete web application: database, Java back end, API and Angular front end. MontiGem is the generator behind <em>most of my projects</em>.",
               "Daten und Seiten in kleinen, präzisen Modellen beschreiben — und eine vollständige Webanwendung bekommen: Datenbank, Java-Backend, API und Angular-Frontend. MontiGem ist der Generator hinter <em>den meisten meiner Projekte</em>."),
        facts=[(ROLE, T("Co-creator", "Mitbegründer")), (T("Based on", "Basis"), "MontiCore"),
               (T("Used in", "Eingesetzt in"), T("5 domains", "5 Domänen")), (T("Output", "Ausgabe"), "Java · TypeScript · HTML")],
        links=[("MontiCore", "https://monticore.github.io/monticore/")],
        media=montigem_diagram,
        chapters=[
            (T("The idea", "Die Idee"), T(
                "<p>Business information systems look different on the surface but are built from the same parts again and again: data classes, persistence, validation, an API, lists, forms and detail pages. Writing these by hand is slow, repetitive and error-prone — and every change to the domain ripples through all layers. MontiGem (MontiCore-based <b>Ge</b>nerator for <b>E</b>nterprise <b>M</b>anagement) generates them instead, from a class diagram for the data, GUI models for the pages and optional OCL constraints for validation.</p>",
                "<p>Betriebliche Informationssysteme sehen von außen verschieden aus, bestehen aber immer wieder aus denselben Teilen: Datenklassen, Persistenz, Validierung, eine API, Listen, Formulare und Detailseiten. Diese von Hand zu schreiben ist langsam, repetitiv und fehleranfällig — und jede Änderung an der Domäne zieht sich durch alle Schichten. MontiGem (MontiCore-based <b>Ge</b>nerator for <b>E</b>nterprise <b>M</b>anagement) generiert sie stattdessen, aus einem Klassendiagramm für die Daten, GUI-Modellen für die Seiten und optionalen OCL-Constraints für die Validierung.</p>")),
            (T("How it works", "So funktioniert es"), T(
                "<p>The generator follows the classic compiler pipeline (figure above). MontiCore-generated parsers turn each model into a syntax tree; model-to-model transformations reshape it into the structure of the target code; FreeMarker templates print it as Java, TypeScript and HTML. For every domain class this yields a JPA data class, a DAO, a builder, a validator, DTOs and the commands of the API — on the server and, identically, on the client. Each GUI model becomes an Angular page. The generic parts — runtime components, styling, authentication with Apache Shiro — come from a hand-written runtime environment that is never regenerated.</p>",
                "<p>Der Generator folgt der klassischen Compiler-Pipeline (Abbildung oben). Von MontiCore generierte Parser machen aus jedem Modell einen Syntaxbaum; Modell-zu-Modell-Transformationen formen ihn in die Struktur des Zielcodes um; FreeMarker-Templates geben ihn als Java, TypeScript und HTML aus. Für jede Domänenklasse entstehen so eine JPA-Datenklasse, ein DAO, ein Builder, ein Validator, DTOs und die Commands der API — auf dem Server und identisch auf dem Client. Jedes GUI-Modell wird zu einer Angular-Seite. Die generischen Teile — Laufzeitkomponenten, Styling, Authentifizierung mit Apache Shiro — stammen aus einer handgeschriebenen Laufzeitumgebung, die nie neu generiert wird.</p>")),
            (T("Generated and handwritten", "Generiert und handgeschrieben"), lambda lang, A: T(
                "<p>No generator covers everything, so the interesting question is how hand-written code fits in. MontiGem uses the <b>TOP mechanism</b>: if a developer writes a class with the name of a generated one, the generator emits its version as <code>…TOP</code> instead, and the hand-written class extends it. Generated and hand-written code live in separate folders; the whole application can be regenerated at any time without losing a single line.</p>",
                "<p>Kein Generator deckt alles ab — die spannende Frage ist also, wie handgeschriebener Code hineinpasst. MontiGem nutzt den <b>TOP-Mechanismus</b>: Schreibt eine Entwicklerin eine Klasse mit dem Namen einer generierten, gibt der Generator seine Version stattdessen als <code>…TOP</code> aus, und die handgeschriebene Klasse erbt davon. Generierter und handgeschriebener Code liegen in getrennten Ordnern; die ganze Anwendung kann jederzeit neu generiert werden, ohne eine einzige Zeile zu verlieren.</p>")[lang]
                + '<pre><code>// generated, because Account.java exists in the handwritten folder\npublic class AccountTOP { … }\n\n// handwritten — survives every regeneration\npublic class Account extends AccountTOP {\n  @Override\n  public BigDecimal getBalance() { … }\n}</code></pre>'),
            (T("Five domains", "Fünf Domänen"), lambda lang, A: T(
                "<p>MontiGem grew inside <a href=\"projects-macoco.html\">MaCoCo</a> and was later extracted into a framework of its own — I built its first version together with Simon Varga and Kai Adam. It has since been used in five domains, each of which pushed new features back into the generator:</p>",
                "<p>MontiGem entstand innerhalb von <a href=\"projects-macoco.html\">MaCoCo</a> und wurde später zu einem eigenständigen Framework herausgelöst — die erste Version habe ich gemeinsam mit Simon Varga und Kai Adam gebaut. Seitdem wurde es in fünf Domänen eingesetzt, die jeweils neue Funktionen in den Generator zurückgebracht haben:</p>")[lang]
                + pts(lang, [
                    T('<a href="projects-macoco.html">MaCoCo</a> — financial, staff and project management for university chairs; OCL validation.',
                      '<a href="projects-macoco.html">MaCoCo</a> — Finanz-, Personal- und Projektmanagement für Lehrstühle; OCL-Validierung.'),
                    T('<a href="projects-ford.html">Ford</a> — IoT tool tracking; multi-language UIs and a driving-safe tablet view.',
                      '<a href="projects-ford.html">Ford</a> — IoT-Werkzeugverfolgung; mehrsprachige Oberflächen und eine fahrsichere Tablet-Ansicht.'),
                    T('<a href="projects-add.html">Agile Data Development</a> — wind-turbine engineering; CD2GUI generates the pages from the class diagram.',
                      '<a href="projects-add.html">Agile Data Development</a> — Windkraftanlagen-Entwicklung; CD2GUI generiert die Seiten aus dem Klassendiagramm.'),
                    T("Energy management of buildings, and InviDas — comparing the privacy policies of wearables.",
                      "Energiemanagement von Gebäuden und InviDas — der Vergleich von Datenschutzerklärungen von Wearables."),
                ])
                + T("<p>In <a class=\"cite\" href=\"#Net24\">[Net24]</a>, MontiGem is the last link of a chain: an LLM turns a natural-language description into a class diagram, CD2GUI derives the GUI models, and MontiGem generates the application — from text to a running web app.</p>",
                    "<p>In <a class=\"cite\" href=\"#Net24\">[Net24]</a> ist MontiGem das letzte Glied einer Kette: Ein LLM macht aus einer natürlichsprachlichen Beschreibung ein Klassendiagramm, CD2GUI leitet die GUI-Modelle ab, und MontiGem generiert die Anwendung — vom Text zur laufenden Web-App.</p>")[lang]),
        ],
        pubs=["BGK+24", "Net24", "NMR24", "CMNR24", "DHM+22", "GMNR21", "DGM+21", "GHK+20", "ANV+18"],
    ),
    dict(
        slug="geneial", name="geneial", when="2012 — 2017", logo="geneial.png",
        desc=T("geneial — a template-based C++11 library for genetic algorithms, and how it helped to lay out offshore wind farms.",
               "geneial — eine template-basierte C++11-Bibliothek für genetische Algorithmen, und wie sie half, Offshore-Windparks anzuordnen."),
        lead=T("Some problems are too big to solve exactly — so you let solutions <em>evolve</em>. geneial is a C++ library for genetic algorithms in which every step of evolution is an exchangeable building block.",
               "Manche Probleme sind zu groß, um sie exakt zu lösen — also lässt man Lösungen <em>evolvieren</em>. geneial ist eine C++-Bibliothek für genetische Algorithmen, in der jeder Schritt der Evolution ein austauschbarer Baustein ist."),
        facts=[(T("Type", "Art"), T("C++11 library", "C++11-Bibliothek")), (T("License", "Lizenz"), "MIT"),
               (T("Authors", "Autoren"), "Wolters · Netz · Nellen")],
        links=[("github", "https://github.com/geneial/geneial"), ("OASys", "https://ths.rwth-aachen.de/research/projects/oasys/")],
        media=geneial_media,
        chapters=[
            (T("The idea", "Die Idee"), T(
                "<p>A genetic algorithm imitates evolution. A population of candidate solutions — chromosomes — is rated by a fitness function; the best are selected, paired, recombined and randomly mutated, and the next generation is formed from the offspring, an elite of the old generation and a few fresh random candidates. Repeated over many generations, the population drifts towards good solutions, even for problems that cannot be solved exactly in reasonable time.</p>",
                "<p>Ein genetischer Algorithmus ahmt die Evolution nach. Eine Population von Lösungskandidaten — Chromosomen — wird durch eine Fitnessfunktion bewertet; die besten werden ausgewählt, gepaart, rekombiniert und zufällig mutiert, und die nächste Generation entsteht aus den Nachkommen, einer Elite der alten Generation und einigen neuen Zufallskandidaten. Über viele Generationen wandert die Population so zu guten Lösungen, auch bei Problemen, die sich in vernünftiger Zeit nicht exakt lösen lassen.</p>")),
            (T("Where it comes from", "Woher es kommt"), T(
                "<p>geneial was created at RWTH’s Theory of Hybrid Systems group in the context of the DFG project OASys — online algorithms for the optimal control of hybrid propulsion systems. There it served as the framework for a genetic-algorithm-based control strategy for the energy management of plug-in hybrid vehicles: when should the combustion engine run, when the electric motor?</p>",
                "<p>geneial entstand am Lehr- und Forschungsgebiet Theorie der hybriden Systeme der RWTH im Kontext des DFG-Projekts OASys — Online-Algorithmen zur optimalen Steuerung hybrider Antriebe. Dort diente es als Framework für eine auf genetischen Algorithmen basierende Steuerungsstrategie für das Energiemanagement von Plug-in-Hybridfahrzeugen: Wann soll der Verbrennungsmotor laufen, wann der Elektromotor?</p>")),
            (T("The library", "Die Bibliothek"), lambda lang, A: T(
                "<p>geneial is a template-based C++11 library. Each stage of the loop in the figure above — stopping criteria, selection, coupling, crossover, choosing, mutation, replacement — is an operator with its own builder, so users plug in their own chromosome types, operators and fitness functions. Fitness evaluation can run multi-threaded, and observers and bookkeepers make runs analysable. The project comes with a CMake build, Boost unit tests, benchmarks, Doxygen documentation and CI. A minimal run:</p>",
                "<p>geneial ist eine template-basierte C++11-Bibliothek. Jede Stufe des Kreislaufs aus der Abbildung oben — Abbruchkriterien, Selektion, Kopplung, Crossover, Auswahl, Mutation, Ersetzung — ist ein Operator mit eigenem Builder; eigene Chromosomentypen, Operatoren und Fitnessfunktionen lassen sich einstecken. Die Fitnessbewertung kann mehrfädig laufen, Observer und Bookkeeper machen Läufe auswertbar. Dazu gehören ein CMake-Build, Boost-Unit-Tests, Benchmarks, Doxygen-Dokumentation und CI. Ein minimaler Lauf:</p>")[lang]
                + f"<pre><code>{GENEIAL_CODE}</code></pre>"),
            (T("Wind farms", "Windparks"), T(
                "<p>Later I used geneial for a different problem <a class=\"cite\" href=\"#Net17\">[Net17]</a>: placing the turbines of an offshore wind farm, rated by annual energy production, net present value and internal rate of return on the Horns Rev test cases. The question was whether turbine positions should be free continuous coordinates or points on a grid. The answer was clear: as long as the grid is fine enough, <b>discretised gene parameters converge faster and reach better results</b> in every test case.</p>",
                "<p>Später habe ich geneial für ein anderes Problem eingesetzt <a class=\"cite\" href=\"#Net17\">[Net17]</a>: die Platzierung der Turbinen eines Offshore-Windparks, bewertet nach Jahresenergieertrag, Kapitalwert und internem Zinsfuß an den Testfällen von Horns Rev. Die Frage war, ob Turbinenpositionen freie, kontinuierliche Koordinaten oder Punkte auf einem Raster sein sollten. Die Antwort war eindeutig: Solange das Raster fein genug ist, <b>konvergieren diskretisierte Genparameter schneller und erreichen bessere Ergebnisse</b> — in allen Testfällen.</p>")),
        ],
        pubs=["Net17", "NWN+15", "GJN+15a"],
    ),
    dict(
        slug="smt-rat", name="SMT-RAT", when="2015", logo="smt-rat.png",
        desc=T("SMT-RAT — a modular C++ toolbox for SMT solving over non-linear real arithmetic, and my work on its interval constraint propagation.",
               "SMT-RAT — ein modularer C++-Werkzeugkasten für SMT-Solving über nichtlinearer reeller Arithmetik, und meine Arbeit an seiner Intervall-Constraint-Propagation."),
        lead=T("Does a set of polynomial inequalities over the real numbers have a solution? SMT-RAT answers questions like this from <em>modules</em> that can be combined into a solver — I worked on the one that narrows the search space with interval arithmetic.",
               "Hat ein System polynomieller Ungleichungen über den reellen Zahlen eine Lösung? SMT-RAT beantwortet solche Fragen mit <em>Modulen</em>, die sich zu einem Solver kombinieren lassen — ich habe an dem gearbeitet, das den Suchraum mit Intervallarithmetik eingrenzt."),
        facts=[(T("Type", "Art"), T("SMT solver toolbox · C++", "SMT-Solver-Baukasten · C++")), (T("Group", "Lehrstuhl"), T("Theory of Hybrid Systems, RWTH", "Theorie der hybriden Systeme, RWTH")),
               (T("My part", "Mein Teil"), T("ICP module", "ICP-Modul"))],
        links=[(T("documentation", "Dokumentation"), "https://ths-rwth.github.io/smtrat/"), ("github", "https://github.com/ths-rwth/smtrat")],
        media=lambda lang, A: smtrat_diagram(lang, A),
        chapters=[
            (T("The problem", "Das Problem"), T(
                "<p>Many questions in verification and engineering boil down to one: is there an assignment of real numbers that satisfies a Boolean combination of polynomial constraints? Can this hybrid system reach an unsafe state, does this rewrite system terminate, does this inequality hold? Such formulas of <b>non-linear real arithmetic</b> are decidable, but the complete methods are expensive — at least exponential in the worst case.</p>",
                "<p>Viele Fragen aus Verifikation und Ingenieurwesen laufen auf eine hinaus: Gibt es eine Belegung mit reellen Zahlen, die eine boolesche Kombination polynomieller Bedingungen erfüllt? Kann dieses hybride System einen unsicheren Zustand erreichen, terminiert dieses Termersetzungssystem, gilt diese Ungleichung? Solche Formeln <b>nichtlinearer reeller Arithmetik</b> sind entscheidbar, aber die vollständigen Verfahren sind teuer — im schlimmsten Fall mindestens exponentiell.</p>")),
            (T("SMT-RAT", "SMT-RAT"), T(
                "<p>SMT solvers combine a fast SAT solver for the Boolean structure with theory solvers for the arithmetic. <b>SMT-RAT</b> (Satisfiability-Modulo-Theories Real Algebra Toolbox), developed at RWTH’s Theory of Hybrid Systems group, makes the theory part modular: each method — simplex, virtual substitution, interval constraint propagation, cylindrical algebraic decomposition and more — is a module, and a <i>strategy</i> chains modules into a solver. Cheap, incomplete methods go first and hand a smaller problem to the expensive, complete ones. The toolbox is open source, reads SMT-LIB 2 and builds on the CArL library for polynomials.</p>",
                "<p>SMT-Solver kombinieren einen schnellen SAT-Solver für die boolesche Struktur mit Theorie-Solvern für die Arithmetik. <b>SMT-RAT</b> (Satisfiability-Modulo-Theories Real Algebra Toolbox), entwickelt am Lehr- und Forschungsgebiet Theorie der hybriden Systeme der RWTH, macht den Theorie-Teil modular: Jedes Verfahren — Simplex, virtuelle Substitution, Intervall-Constraint-Propagation, zylindrisch-algebraische Zerlegung und mehr — ist ein Modul, und eine <i>Strategie</i> verkettet Module zu einem Solver. Günstige, unvollständige Verfahren kommen zuerst und reichen ein kleineres Problem an die teuren, vollständigen weiter. Der Werkzeugkasten ist Open Source, liest SMT-LIB 2 und baut für Polynome auf der Bibliothek CArL auf.</p>")),
            (T("Interval constraint propagation", "Intervall-Constraint-Propagation"), T(
                "<p>Interval constraint propagation (ICP) works on boxes of intervals, one per variable. It uses each constraint to cut away parts of the box that cannot contain a solution — <i>contraction</i> — until the box is empty (unsatisfiable) or small enough to hand on. Its weak spot is interval arithmetic itself: it does not know that two occurrences of <code>x</code> are the same number. That <b>dependency problem</b> makes results wider than necessary (figure above), so ICP contracts less and needs more iterations.</p>",
                "<p>Intervall-Constraint-Propagation (ICP) arbeitet auf Boxen aus Intervallen, eines pro Variable. Sie nutzt jede Bedingung, um Teile der Box wegzuschneiden, die keine Lösung enthalten können — <i>Kontraktion</i> —, bis die Box leer (unerfüllbar) oder klein genug zur Weitergabe ist. Ihre Schwachstelle ist die Intervallarithmetik selbst: Sie weiß nicht, dass zwei Vorkommen von <code>x</code> dieselbe Zahl sind. Dieses <b>Abhängigkeitsproblem</b> macht Ergebnisse breiter als nötig (Abbildung oben), sodass ICP weniger kontrahiert und mehr Iterationen braucht.</p>")),
            (T("My contribution", "Mein Beitrag"), lambda lang, A: T(
                "<p>I improved SMT-RAT’s ICP module in two ways <a class=\"cite\" href=\"#Net15\">[Net15]</a>. First, a new contraction method — interval <b>propagation</b> through the constraint — in addition to the existing Newton-based contraction. Second, a data structure for <b>multivariate Horner schemes</b>: polynomials are rewritten in nested form, which needs fewer operations and repeats variables less often, so the intervals stay tighter. Two heuristics choose the variable to factor out next — one fast, one aimed at the smallest over-approximation — and a simplification step compresses the result.</p>"
                "<p>Evaluated on the standard SMT-LIB benchmark sets, the propagation clearly paid off: on <i>keymaera</i> (hybrid-systems verification) more instances were solved with fewer timeouts in little more than half the time, and on <i>hong</i> nearly twice as many test cases could be solved in the same time frame. The Horner schemes did make ICP more precise — up to 46&nbsp;% fewer contractions on some instances — but building them cost more time than the tighter intervals saved. An honest result that pointed to the next steps: choosing the heuristic per input, and evaluating polynomials from the perspective of a single variable.</p>",
                "<p>Ich habe das ICP-Modul von SMT-RAT auf zwei Wegen verbessert <a class=\"cite\" href=\"#Net15\">[Net15]</a>. Erstens eine neue Kontraktionsmethode — <b>Propagation</b> von Intervallen durch die Bedingung — zusätzlich zur bestehenden, Newton-basierten Kontraktion. Zweitens eine Datenstruktur für <b>multivariate Horner-Schemata</b>: Polynome werden verschachtelt umgeschrieben, brauchen so weniger Operationen und wiederholen Variablen seltener, wodurch die Intervalle enger bleiben. Zwei Heuristiken wählen die nächste auszuklammernde Variable — eine schnelle, eine auf möglichst geringe Überapproximation ausgelegte —, und ein Vereinfachungsschritt komprimiert das Ergebnis.</p>"
                "<p>Auf den üblichen SMT-LIB-Benchmarks hat sich die Propagation klar ausgezahlt: Auf <i>keymaera</i> (Verifikation hybrider Systeme) wurden mehr Instanzen mit weniger Timeouts in kaum mehr als der halben Zeit gelöst, und auf <i>hong</i> ließen sich im selben Zeitrahmen fast doppelt so viele Testfälle lösen. Die Horner-Schemata machten ICP zwar präziser — auf einzelnen Instanzen bis zu 46&nbsp;% weniger Kontraktionen —, ihr Aufbau kostete aber mehr Zeit, als die engeren Intervalle einsparten. Ein ehrliches Ergebnis, das die nächsten Schritte zeigte: die Heuristik je Eingabe wählen und Polynome aus der Sicht einer einzelnen Variable auswerten.</p>")[lang]),
        ],
        pubs=["Net15"],
    ),
]
