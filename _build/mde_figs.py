"""
Figures of the MDE article (research-mde.html, _build/mde.py). Static diagrams are inline SVG with the
.dia classes of style.css; the four interactive figures (D1 syntax gates, D2 TOP mechanism, D3 one line →
six files, D4 CD2GUI pages) get all their states precomputed here and shipped as data-json — assets/mde.js
only swaps and highlights. Most figures are redrawn after figures of the MontiGem papers ("After [KEY], Fig. x").
"""
import html

from ai4se import T, fig, demo, controls, cite
from project_content import _arrow_defs, box, dia_scroll

esc = html.escape

# The running example: GMN+20, Table 1 (p.5), verbatim.
EXAMPLE = [
    "classdiagram Example {",
    "  class Account {",
    "    String name;",
    "    int balance;",
    "  }",
    "  class Person {",
    "    String name;",
    "  }",
    "  class Accountant extends Person {",
    "    String bank;",
    "  }",
    "  association [1] Accountant -> (account) Account [*];",
    "}",
]


def _uml(x, y, w, name, attrs, cls="box", gname="", gattr=""):
    """A UML class box: name compartment, then one row per attribute. Returns (svg, height)."""
    h = 26 + 17 * len(attrs) + 8
    out = (f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="2"/>'
           f'<path class="ln" d="M{x} {y + 26}H{x + w}"/>'
           f'<text x="{x + w / 2}" y="{y + 17}" text-anchor="middle" class="t{gname}">{name}</text>')
    out += "".join(f'<text x="{x + 10}" y="{y + 42 + 17 * k}" class="{gattr}">{esc(a)}</text>' for k, a in enumerate(attrs))
    return out, h


# =====================================================================
# Static figures
# =====================================================================

def fig_teaser(lang):
    """F0: one model line, six files in three tiers (after Lukas's MontiGem documentation slides, 'data → generator → EIS')."""
    L = lambda x: x[lang]
    files = [(T("Table", "Tabelle"), T("DATABASE", "DATENBANK")), (T("Data class", "Datenklasse"), "SERVER"), ("Command", "SERVER"),
             ("DTO", "SERVER ↔ BROWSER"), (T("TS model", "TS-Modell"), "BROWSER"), (T("Form", "Formular"), "BROWSER")]
    chips = ""
    for k, (name, tier) in enumerate(files):
        x, y = 430 + (k % 3) * 145, 16 + (k // 3) * 56
        chips += box(x, y, 135, 44, L(name) if isinstance(name, dict) else name, L(tier) if isinstance(tier, dict) else tier)
        chips += f'<circle cx="{x + 126}" cy="{y + 9}" r="3" class="dot"/>'
    svg = f'''<svg class="dia" viewBox="0 0 860 130" role="img" aria-label="{L(T("One added line in the model goes through the generator and changes six files: a table, a data class, a command, a transfer object, a browser model and a form", "Eine hinzugefügte Zeile im Modell läuft durch den Generator und ändert sechs Dateien: eine Tabelle, eine Datenklasse, ein Command, ein Transferobjekt, ein Browser-Modell und ein Formular"))}">
  {_arrow_defs("mda")}
  <rect class="box hl" x="0" y="36" width="180" height="58" rx="3"/>
  <text x="12" y="54" class="s">{L(T("THE MODEL · Account.cd", "DAS MODELL · Account.cd"))}</text>
  <text x="12" y="80" class="a">+ String iban;</text>
  <path class="ln" d="M180 65H222" marker-end="url(#mda)"/>
  <rect class="zone" x="226" y="26" width="150" height="78" rx="4"/>
  <text x="238" y="44" class="s">GENERATOR</text><text x="301" y="80" text-anchor="middle" class="t">MontiGem</text>
  <path class="ln" d="M376 65H422" marker-end="url(#mda)"/>
  {chips}
</svg>'''
    return fig(svg, T('<b>One line in the model, six files in three tiers.</b> You change the data model; the generator rewrites table, server classes, transfer objects and browser code so that they fit together again. <a href="#whygen">Try it in chapter 03 →</a>',
                      '<b>Eine Zeile im Modell, sechs Dateien in drei Schichten.</b> Sie ändern das Datenmodell; der Generator schreibt Tabelle, Serverklassen, Transferobjekte und Browser-Code so neu, dass sie wieder zusammenpassen. <a href="#whygen">In Kapitel 03 ausprobieren →</a>'), lang)


def fig_maps(lang):
    """F1: one city, three maps — mapping, reduction, purpose. The city and its maps are built in mde_map.py."""
    import mde_map
    return mde_map.fig_maps(lang, fig, T)


def fig_classdiagram(lang):
    """F2: reading a class diagram — hover or focus a part, its plain-language reading lights up.
    After GMN+20, Fig.3 (p.5); wording after BGK+24, lesson 6 (inheritance 'A is a B', association 'A knows a B')."""
    L = lambda x: x[lang]
    pb, ph = _uml(120, 18, 180, "Person", ["String name"], gname=" nm", gattr="at")
    ab, ah = _uml(120, 168, 180, "Accountant", ["String bank"], gname=" nm", gattr="at")
    cb, ch = _uml(500, 168, 180, "Account", ["String name", "int balance"], gname=" nm", gattr="at")
    pbot = 18 + ph
    groups = [
        ("cls", "", f'<text x="312" y="34" class="co">{L(T("class — a kind of thing", "Klasse — eine Art von Ding"))}</text>'),
        ("attr", "", f'<text x="692" y="214" class="co">{L(T("attribute — a field", "Attribut — ein Feld"))}</text><text x="692" y="228" class="co">{L(T("every Account has", "das jedes Account hat"))}</text>'),
        ("isa", f'<path class="ln" d="M210 168V{pbot + 14}"/><path class="box" d="M210 {pbot}L202 {pbot + 14}H218Z"/>',
         f'<text x="222" y="{(pbot + 168) / 2 + 4}" class="co">{L(T("is a — an Accountant is a Person", "ist ein — ein Accountant ist eine Person"))}</text>'),
        ("knows", '<path class="ln" d="M300 200H496" marker-end="url(#mdca)"/><text x="490" y="214" text-anchor="end" class="s">account</text>',
         f'<text x="398" y="178" text-anchor="middle" class="co">{L(T("knows — an Accountant knows Accounts", "kennt — ein Accountant kennt Konten"))}</text>'),
        ("mult", '<text x="308" y="194">1</text><text x="486" y="194" text-anchor="end">*</text>',
         f'<text x="398" y="250" text-anchor="middle" class="co">{L(T("1 = exactly one · * = any number", "1 = genau eins · * = beliebig viele"))}</text>'),
    ]
    g = "".join(f'<g class="k" data-k="{k}" tabindex="0">{shape}{co}</g>' for k, shape, co in groups)
    svg = f'''<svg class="dia f2" viewBox="0 0 860 262" role="group" aria-label="{L(T("Class diagram: Accountant is a Person; an Accountant knows any number of Accounts; Account has a name and a balance", "Klassendiagramm: Accountant ist eine Person; ein Accountant kennt beliebig viele Accounts; Account hat einen Namen und einen Kontostand"))}">
  <defs><marker id="mdca" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1L9 5L0 9" fill="none" stroke="currentColor" stroke-width="1.4"/></marker></defs>
  {pb}{ab}{cb}{g}
</svg>'''
    return fig(svg, T(f"<b>Read it as sentences:</b> an Accountant <i>is a</i> Person, an Accountant <i>knows</i> any number of Accounts, every Account has a name and a balance. Point at a part of the diagram to see how to read it. This is the running example of the article: an accountant at a bank manages several accounts. After {cite('GMN+20')}, Fig. 3.",
                      f"<b>Als Sätze lesen:</b> Ein Accountant <i>ist eine</i> Person, ein Accountant <i>kennt</i> beliebig viele Accounts, jedes Account hat einen Namen und einen Kontostand. Zeigen Sie auf einen Teil des Diagramms, um zu sehen, wie man ihn liest. Das ist das laufende Beispiel des Artikels: Ein Buchhalter einer Bank verwaltet mehrere Konten. Nach {cite('GMN+20')}, Abb. 3."), lang)


def fig_aspects(lang):
    """F3: divide the problem, one language per aspect. After DGM+21, Fig.5 (p.6)."""
    L = lambda x: x[lang]
    rows = [(T("data", "Daten"), "CD4A", T("data model", "Datenmodell"), "Bank.cd"),
            (T("pages", "Seiten"), "GUI-DSL", T("uses CD4A", "nutzt CD4A"), "AccountDetails.gui"),
            (T("rules", "Regeln"), "OCL/P", T("uses CD4A", "nutzt CD4A"), "Bank.ocl"),
            (T("who may see what", "wer was sehen darf"), "Tagging", T("uses CD4A", "nutzt CD4A"), "Roles.tag")]
    out = ""
    for k, (aspect, lang_, sub, model) in enumerate(rows):
        y = 40 + k * 50
        out += (f'<rect class="box" x="22" y="{y}" width="150" height="30" rx="15"/><text x="97" y="{y + 19}" text-anchor="middle">{L(aspect)}</text>'
                f'<path class="ln" d="M172 {y + 15}H246" marker-end="url(#mdc)"/>'
                + box(250, y - 4, 130, 38, lang_, L(sub)) +
                f'<path class="ln dash" d="M380 {y + 15}H452"/>'
                f'<path class="box" d="M456 {y}H{590}l10 10V{y + 30}H456Z"/><text x="466" y="{y + 19}" class="s">{model}</text>'
                f'<path class="ln" d="M600 {y + 15}L652 125"/>')
    svg = f'''<svg class="dia" viewBox="0 0 860 240" role="img" aria-label="{L(T("A problem is split into aspects: data, pages, rules and who may see what. Each aspect gets its own modelling language, CD4A, GUI-DSL, OCL/P and Tagging; each language has concrete models; together they produce the solution", "Ein Problem wird in Aspekte zerlegt: Daten, Seiten, Regeln und wer was sehen darf. Jeder Aspekt bekommt eine eigene Modellierungssprache, CD4A, GUI-DSL, OCL/P und Tagging; jede Sprache hat konkrete Modelle; zusammen ergeben sie die Lösung"))}">
  {_arrow_defs("mdc")}
  <rect class="zone" x="0" y="22" width="194" height="210" rx="30"/>
  <text x="14" y="14" class="s">{L(T("THE PROBLEM · ITS ASPECTS", "DAS PROBLEM · SEINE ASPEKTE"))}</text>
  <text x="250" y="14" class="s">{L(T("ONE LANGUAGE EACH", "JE EINE SPRACHE"))}</text>
  <text x="456" y="14" class="s">{L(T("CONCRETE MODELS", "KONKRETE MODELLE"))}</text>
  <text x="384" y="50" class="s">{L(T("conforms to", "ist konform zu"))}</text>
  <text x="680" y="14" class="s">{L(T("THE SOLUTION", "DIE LÖSUNG"))}</text>
  {out}
  <path class="ln" d="M652 125H664" marker-end="url(#mdc)"/>
  <rect class="box hl" x="668" y="40" width="190" height="170" rx="3"/><path class="ln" d="M668 58H858"/>
  <circle cx="678" cy="49" r="3" class="dot"/><rect class="zone" x="680" y="70" width="80" height="10"/>
  <path class="ln" d="M680 96H846M680 114H846M680 132H846M680 150H846"/><rect class="box" x="680" y="172" width="60" height="22" rx="2"/>
</svg>'''
    return fig(svg, T(f"<b>Divide the problem, one language per aspect.</b> The data model is written in CD4A; the pages, the rules and the access rights each have their own small language — and all of them refer to the names in the data model. After {cite('DGM+21')}, Fig. 5.",
                      f"<b>Das Problem zerlegen, eine Sprache je Aspekt.</b> Das Datenmodell ist in CD4A geschrieben; Seiten, Regeln und Zugriffsrechte haben jeweils eine eigene kleine Sprache — und alle verweisen auf die Namen im Datenmodell. Nach {cite('DGM+21')}, Abb. 5."), lang)


def fig_generator(lang):
    """F5: how a generator works — the language level (built once with MontiCore) and the tool level
    (read · transform · generate). After the se-rwth DSL figure, [HKR21] Figs 3.1/3.2 and BGK+24 Fig.2."""
    L = lambda x: x[lang]
    m, ma = 'marker-end="url(#mde)"', 'marker-end="url(#mdea)"'
    chips = [T("parser", "Parser"), T("AST classes", "AST-Klassen"), T("symbol table", "Symboltabelle"), T("CoCo framework", "CoCo-Rahmen"), "visitors"]
    top = "".join(f'<rect class="box hl" x="{372 + k * 104}" y="48" width="96" height="30" rx="3"/><text x="{420 + k * 104}" y="67" text-anchor="middle" class="s">{L(c) if isinstance(c, dict) else c}</text>' for k, c in enumerate(chips))
    hw = L(T("hand-written", "handgeschrieben"))
    svg = f'''<svg class="dia" viewBox="0 0 900 360" role="img" aria-label="{L(T("Top: from the CD4A grammar, MontiCore generates the skeleton of the tool — parser, AST classes, symbol table, context-condition framework, visitors. Bottom: the tool reads your model into an AST and checks it, transforms it into an output AST, and fills templates with it to produce code; hand-written code extends the result", "Oben: Aus der CD4A-Grammatik generiert MontiCore das Gerüst des Werkzeugs — Parser, AST-Klassen, Symboltabelle, Kontextbedingungs-Rahmen, Visitors. Unten: Das Werkzeug liest Ihr Modell in einen AST und prüft ihn, transformiert ihn in einen Ausgabe-AST und füllt damit Templates, die Code ergeben; handgeschriebener Code erweitert das Ergebnis"))}">
  {_arrow_defs("mde")}
  <rect class="zone" x="0" y="8" width="900" height="92" rx="4"/>
  <text x="12" y="26" class="s">{L(T("LANGUAGE · built once, by the language engineer", "SPRACHE · einmal gebaut, von der Sprachingenieurin"))}</text>
  {box(14, 42, 150, 42, L(T("CD4A grammar", "CD4A-Grammatik")))}
  <path class="ln" d="M164 63H202" {m}/>
  {box(206, 42, 130, 42, "MontiCore", L(T("language workbench", "Language Workbench")))}
  <path class="ln" d="M336 63H368" {m}/>
  <text x="372" y="42" class="s a">{L(T("generated", "generiert"))}</text>
  {top}
  <path class="ln dash" d="M420 80V172"/><text x="428" y="112" class="s">{L(T("the skeleton of the tool", "das Gerüst des Werkzeugs"))}</text>
  <rect class="zone line" x="0" y="122" width="900" height="232" rx="4"/>
  <text x="12" y="140" class="s">{L(T("TOOL · runs on every model", "WERKZEUG · läuft auf jedem Modell"))}</text>
  <text x="14" y="168" class="s a">01 {L(T("READ", "LESEN"))}</text><text x="312" y="168" class="s a">02 {L(T("TRANSFORM", "TRANSFORMIEREN"))}</text><text x="592" y="168" class="s a">03 {L(T("GENERATE", "GENERIEREN"))}</text>
  {box(14, 180, 116, 42, "Account.cd", L(T("your model", "Ihr Modell")), cls="box hl")}
  <text x="14" y="240" class="s a">{L(T("← you write this", "← das schreiben Sie"))}</text>
  <path class="ln" d="M130 201H156" {m}/>
  {box(160, 180, 110, 42, "Parser")}
  <path class="ln" d="M215 222V250" {m}/>
  {box(160, 254, 110, 38, "AST")}
  <path class="ln" d="M160 273H134" {m}/>
  {box(14, 254, 116, 38, L(T("checks", "Prüfungen")), L(T("names · rules", "Namen · Regeln")))}
  <text x="14" y="308" class="s">{L(T("rules: hand-written", "Regeln: handgeschrieben"))}</text>
  <path class="ln" d="M270 273H288V203H306" {m}/>
  {box(310, 182, 104, 42, L(T("input AST", "Eingabe-AST")))}
  <path class="ln hl" d="M414 203H448" {ma}/>
  {box(452, 182, 112, 42, L(T("output AST", "Ausgabe-AST")), "+ id : long", cls="box hl")}
  {box(310, 258, 254, 38, L(T("transformation", "Transformation")), hw)}
  <path class="ln dash" d="M431 258V206"/>
  <path class="ln" d="M508 182V170H780V186" {m}/>
  {box(592, 190, 130, 42, L(T("templates {…}", "Templates {…}")), hw)}
  <path class="ln" d="M722 211H736" {m}/>
  {box(740, 190, 150, 42, L(T("template engine", "Template-Engine")), cls="box hl")}
  <path class="ln" d="M815 232V246" {m}/>
  <rect class="box" x="740" y="250" width="150" height="24" rx="2"/><text x="750" y="266" class="s">Account.java</text>
  <rect class="box" x="740" y="278" width="150" height="24" rx="2"/><text x="750" y="294" class="s">AccountDAO.java</text>
  <rect class="box" x="740" y="306" width="150" height="24" rx="2"/><text x="750" y="322" class="s">account.ts · …</text>
  {box(592, 262, 130, 42, "hwc/", L(T("your own code", "Ihr eigener Code")), cls="box dashbox")}
  <path class="ln dash" d="M722 290H736" {m}/><text x="600" y="322" class="s">extends ▷</text>
</svg>'''
    return fig(svg, T(f"<b>Two levels.</b> Above: from one grammar, MontiCore generates the skeleton of a language tool. Below: that tool reads a model, checks it, transforms it and fills templates with it — the model carries the domain, the templates carry the technology. The rules, the transformation and the templates are written by hand once; the model is what you write every day. After the se-rwth.de DSL figure, the MontiCore handbook {ref_hb()}, Figs. 3.1/3.2, and {cite('BGK+24')}, Fig. 2.",
                      f"<b>Zwei Ebenen.</b> Oben: Aus einer Grammatik generiert MontiCore das Gerüst eines Sprachwerkzeugs. Unten: Dieses Werkzeug liest ein Modell, prüft es, transformiert es und füllt damit Templates — das Modell trägt die Domäne, die Templates tragen die Technik. Regeln, Transformation und Templates werden einmal von Hand geschrieben; das Modell ist das, was Sie jeden Tag schreiben. Nach der DSL-Abbildung von se-rwth.de, dem MontiCore-Handbuch {ref_hb()}, Abb. 3.1/3.2, und {cite('BGK+24')}, Abb. 2."), lang)


def ref_hb():
    return '<a class="cite" href="#ref-8">[8]</a>'


def fig_retrofit(lang):
    """F7: retrofitting MaCoCo step by step. After DGM+21, Fig.8 (p.10). Only the last bar carries numbers."""
    L = lambda x: x[lang]
    steps = [(T("hand-written", "handgeschrieben"), T("application", "Anwendung"), (0, 0, 1.0)),
             (T("+ data &", "+ Daten &"), T("persistence · CD", "Persistenz · CD"), (.03, .30, .67)),
             (T("+ data", "+ Daten-"), T("transfer", "transfer"), (.03, .44, .53)),
             (T("+ validation", "+ Validierung"), "OCL", (.04, .55, .41)),
             (T("+ pages", "+ Seiten"), "GUI-DSL", (9 / 514, 390 / 514, 115 / 514))]
    H, base, out = 180, 230, ""
    for k, (a, b, (mo, ge, hw)) in enumerate(steps):
        x = 20 + k * 140
        y = base
        for share, cls in ((hw, "hw"), (ge, "gen"), (mo, "mod")):
            h = share * H
            if h:
                out += f'<rect class="rb {cls}" x="{x}" y="{y - h:.1f}" width="76" height="{h:.1f}"/>'
            y -= h
        out += f'<text x="{x}" y="{base + 18}" class="t" style="font-size:12px">{L(a)}</text><text x="{x}" y="{base + 33}" class="s">{L(b) if isinstance(b, dict) else b}</text>'
        if k < 4:
            out += f'<path class="ln" d="M{x + 84} 140H{x + 132}" marker-end="url(#mdf)"/>'
    lines = [(54, T("models ~9k lines", "Modelle ~9k Zeilen"), "s"), (80, T("generated ~390k", "generiert ~390k"), "s a"), (94, T("back end ~250k", "Backend ~250k"), "s"),
             (108, T("front end ~140k", "Frontend ~140k"), "s"), (200, T("hand-written ~115k", "handgeschrieben ~115k"), "s"), (214, T("back end ~55k", "Backend ~55k"), "s"),
             (228, T("front end ~60k", "Frontend ~60k"), "s")]
    g = "".join(f'<text x="668" y="{y}" class="{c}">{L(t)}</text>' for y, t, c in lines)
    g += f'<text x="580" y="38" class="t">{L(T("≈ 78 % generated · 2021", "≈ 78 % generiert · 2021"))}</text>'
    svg = f'''<svg class="dia" viewBox="0 0 860 300" role="img" aria-label="{L(T("Five bars: a hand-written application to which generation is added step by step — data and persistence, data transfer, validation, pages. In the last bar, 2021, about 78 percent of the code is generated", "Fünf Balken: Eine handgeschriebene Anwendung, der Schritt für Schritt Generierung hinzugefügt wird — Daten und Persistenz, Datentransfer, Validierung, Seiten. Im letzten Balken, 2021, sind rund 78 Prozent des Codes generiert"))}">
  {_arrow_defs("mdf")}
  <text x="20" y="38" class="s">{L(T("ILLUSTRATIVE STEPS", "SCHRITTE (SCHEMATISCH)"))}</text>
  {out}{g}
  <rect class="rb gen" x="20" y="284" width="10" height="8"/><text x="36" y="292" class="s">{L(T("generated", "generiert"))}</text>
  <rect class="rb hw" x="130" y="284" width="10" height="8"/><text x="146" y="292" class="s">{L(T("hand-written", "handgeschrieben"))}</text>
  <rect class="rb mod" x="270" y="284" width="10" height="8"/><text x="286" y="292" class="s">{L(T("models", "Modelle"))}</text>
</svg>'''
    return fig(svg, T(f"<b>Generation was added to a running system, one aspect at a time.</b> MaCoCo started as a hand-written application; first the data structure and persistence were generated from a class diagram, then the data transfer, then the validation (OCL), then the pages (GUI-DSL). Only the last bar shows measured numbers (lines of code, 2021); the steps before are schematic. The 2022 figures above use a different counting basis. After {cite('DGM+21')}, Fig. 8.",
                      f"<b>Generierung kam in ein laufendes System, ein Aspekt nach dem anderen.</b> MaCoCo begann als handgeschriebene Anwendung; zuerst wurden Datenstruktur und Persistenz aus einem Klassendiagramm generiert, dann der Datentransfer, dann die Validierung (OCL), dann die Seiten (GUI-DSL). Nur der letzte Balken zeigt gemessene Zahlen (Codezeilen, 2021); die Schritte davor sind schematisch. Die Zahlen von 2022 oben zählen anders. Nach {cite('DGM+21')}, Abb. 8."), lang)


# =====================================================================
# Interactive figures (assets/mde.js)
# =====================================================================

def _mini_uml(variant):
    """Small UML of the running example (≤340 px), for D1. variant: ok | dangling | dup."""
    pb, _ = _uml(10, 8, 130, "Person", ["String name"])
    ab, _ = _uml(10, 112, 130, "Accountant", ["String bank"])
    if variant == "dangling":
        cb = ('<rect class="box dashbox" x="200" y="112" width="130" height="44" rx="2"/>'
              '<text x="265" y="139" text-anchor="middle" class="t">Acount ?</text>')
    else:
        attrs = ["String name", "String name ✗" if variant == "dup" else "int balance"]
        cb, _ = _uml(200, 112, 130, "Account", attrs)
        if variant == "dup":
            cb = cb.replace(f'>{esc("String name ✗")}<', ' class="a">String name ✗<')
    return (f'<svg class="dia" viewBox="0 0 340 180" role="img" aria-hidden="true">'
            f'<g data-k="person">{pb}</g><g data-k="accountant">{ab}</g><g data-k="account">{cb}</g>'
            f'<g data-k="isa"><path class="ln" d="M75 112V72"/><path class="box" d="M75 59L68 72H82Z"/></g>'
            f'<g data-k="assoc"><path class="ln" d="M140 140H196"/><text x="146" y="134" class="s">1</text><text x="192" y="134" text-anchor="end" class="s">*</text></g>'
            f'</svg>')


def demo_syntax(lang):
    """D1: one model, two notations — and three gates. Four presets, each differing from the valid model in
    exactly one line (checked by _check_d1). After GMN+20 Table 1 / Fig.3 and [HKR21] Figs 10.1/10.2."""
    L = lambda x: x[lang]
    keys = ["", "", "account", "account", "account", "person", "person", "person", "accountant", "accountant", "accountant", "assoc", ""]
    variants = [
        ("valid", T("valid", "gültig"), None, None, [1, 1, 1], "ok",
         T("Well-formed: the parser built the tree, every name is known, every rule is kept. Tools may use it.",
           "Wohlgeformt: Der Parser hat den Baum gebaut, jeder Name ist bekannt, jede Regel eingehalten. Werkzeuge dürfen damit arbeiten.")),
        ("semi", T("missing ;", "fehlendes ;"), 9, "    String bank", [0, -1, -1], "none",
         T("The parser rejects it: no tree, so no picture and nothing to check further.",
           "Der Parser lehnt ab: kein Baum, also kein Bild und nichts weiter zu prüfen.")),
        ("typo", T("typo", "Tippfehler"), 11, "  association [1] Accountant -> (account) Acount [*];", [1, 0, -1], "dangling",
         T("Readable — the grammar was happy. But “Acount” names nothing: the symbol table cannot resolve it.",
           "Lesbar — die Grammatik war zufrieden. Aber „Acount“ bezeichnet nichts: Die Symboltabelle kann es nicht auflösen.")),
        ("dup", T("duplicate", "doppelt"), 3, "    String name;", [1, 1, 0], "dup",
         T("Readable, all names resolve — the grammar was happy. But Account now has two attributes called name: a context condition fails.",
           "Lesbar, alle Namen lösen sich auf — die Grammatik war zufrieden. Aber Account hat jetzt zwei Attribute namens name: Eine Kontextbedingung schlägt fehl.")),
    ]
    data = {"variants": [], "words": {}}
    for vid, label, line, text, gates, uml, msg in variants:
        lines = list(EXAMPLE)
        if line is not None:
            lines[line] = text
        data["variants"].append({"id": vid, "err": line if line is not None else -1, "gates": gates, "uml": uml, "msg": L(msg),
                                 "code": "".join(f'<span class="l{" err" if k == line else ""}" data-k="{keys[k]}">{esc(t)}</span>' for k, t in enumerate(lines))})
    _check_d1([v["code"] for v in data["variants"]])
    buttons = "".join(f'<button type="button" data-v="{k}" aria-pressed="{"true" if k == 0 else "false"}">{L(v[1])}</button>' for k, v in enumerate(variants))
    gates = [(T("readable?", "lesbar?"), T("parser", "Parser")), (T("names known?", "Namen bekannt?"), T("symbol table", "Symboltabelle")),
             (T("rules kept?", "Regeln eingehalten?"), T("context conditions", "Kontextbedingungen"))]
    strip = "".join(f'<li class="gate ok"><b>{k + 1}</b> {L(a)} <span>{L(b)}</span></li>' for k, (a, b) in enumerate(gates))
    umls = "".join(f'<div class="d1-uml" data-uml="{u}"{"" if u == "ok" else " hidden"}>{_mini_uml(u)}</div>' for u in ("ok", "dangling", "dup"))
    umls += f'<div class="d1-uml d1-none" data-uml="none" hidden><span class="mono">{L(T("no tree, no picture", "kein Baum, kein Bild"))}</span></div>'
    inner = f'''<div class="d1-presets mono" role="group" aria-label="{L(T("Variants of the model", "Varianten des Modells"))}"><span class="k">{L(T("TRY:", "PROBIEREN:"))}</span>{buttons}</div>
<ol class="d1-gates mono">{strip}</ol>
<div class="d1-grid">
  <div><span class="k mono">{L(T("TEXT · CD4A", "TEXT · CD4A"))}</span><pre class="mono d1-code">{data["variants"][0]["code"]}</pre></div>
  <div><span class="k mono">{L(T("DIAGRAM · UML", "DIAGRAMM · UML"))}</span>{umls}</div>
</div>
<p class="d1-msg mono" aria-live="polite">{L(variants[0][6])}</p>'''
    return demo("d1", data, inner, T(
        f"<b>The picture is not the model.</b> Text and diagram are two <i>concrete syntaxes</i> of the same structure; point at a line to find it in the diagram. Behind both, the tool works on the <i>abstract syntax</i>, a tree. Choose a variant: each differs from the valid model in one line — and fails at a different gate. (In MontiCore, “cannot be resolved” is itself reported by a context condition that asks the symbol table; the gates are separated here for clarity.) After {cite('GMN+20')}, Table 1 and Fig. 3, and {ref_hb()}, Figs. 10.1/10.2.",
        f"<b>Das Bild ist nicht das Modell.</b> Text und Diagramm sind zwei <i>konkrete Syntaxen</i> derselben Struktur; zeigen Sie auf eine Zeile, um sie im Diagramm zu finden. Hinter beiden arbeitet das Werkzeug auf der <i>abstrakten Syntax</i>, einem Baum. Wählen Sie eine Variante: Jede unterscheidet sich vom gültigen Modell in einer Zeile — und scheitert an einer anderen Stelle. (In MontiCore meldet eine Kontextbedingung, die die Symboltabelle befragt, selbst das „kann nicht aufgelöst werden“; die Stufen sind hier der Klarheit halber getrennt.) Nach {cite('GMN+20')}, Tabelle 1 und Abb. 3, und {ref_hb()}, Abb. 10.1/10.2."), lang)


def _check_d1(codes):
    import re
    lines = [re.findall(r'<span[^>]*>(.*?)</span>', c) for c in codes]
    for v in lines[1:]:
        assert len(v) == len(lines[0]) and sum(a != b for a, b in zip(v, lines[0])) == 1


def _code(lines, new=()):
    """A code block as HTML lines; indices in `new` are marked as new; strike: list of (index) struck."""
    return "".join(f'<span class="l{" new" if k in new else ""}">{esc(t) or " "}</span>' for k, t in enumerate(lines))


def demo_top(lang):
    """D2: edit the generated file, or extend it (TOP mechanism). Two lanes, one stepper.
    After [HKR21] Fig.14.5 / Tip 5.30 and GMNR21 Fig.1C."""
    L = lambda x: x[lang]
    gen = ["// generated — do not edit", "public class Account {", "  String name; int balance;", "  int getBalance() {…}", "}"]
    gen_top = ["// generated", "public abstract class AccountTOP {", "  String name; int balance;", "  int getBalance() {…}", "}"]
    euro = "  double getBalanceInEuro() {…}"
    hw = ["// hwc/ · yours", "public class Account", "    extends AccountTOP {", euro, "}"]

    def file(path, lines, new=(), cls=""):
        return f'<div class="d2-file {cls}"><span class="mono d2-path">{path}</span><pre class="mono">{_code(lines, new)}</pre></div>'
    steps = [
        (T("Generate", "Generieren"),
         file("out/Account.java", gen), T("The generator writes Account.java.", "Der Generator schreibt Account.java."), "",
         file("out/Account.java", gen), T("Same start.", "Derselbe Anfang."), ""),
        (T("Add your own method", "Eigene Methode ergänzen"),
         file("out/Account.java", gen[:4] + [euro, "}"], new=(4,)), T("You type getBalanceInEuro() into the generated file. It compiles.", "Sie tippen getBalanceInEuro() in die generierte Datei. Es kompiliert."), "",
         file("out/Account.java", gen) + file("hwc/Account.java", hw, new=(1, 2, 3, 4), cls="hw"),
         T("You write hwc/Account.java, which extends AccountTOP. It does not compile yet: AccountTOP does not exist — regenerate.", "Sie schreiben hwc/Account.java, das AccountTOP erweitert. Es kompiliert noch nicht: AccountTOP gibt es nicht — neu generieren."), "warn"),
        (T("Regenerate (model unchanged)", "Neu generieren (Modell unverändert)"),
         file("out/Account.java", gen[:4] + [euro, "}"], cls="lost"), T("The file is overwritten. Your method is gone — and the model did not even change.", "Die Datei wird überschrieben. Ihre Methode ist weg — dabei hat sich das Modell nicht einmal geändert."), "bad",
         file("out/AccountTOP.java", gen_top, new=(1,)) + file("hwc/Account.java", hw, cls="hw"),
         T("The generator finds hwc/Account.java and emits the abstract AccountTOP instead. Everything compiles; your class is the one used.", "Der Generator findet hwc/Account.java und erzeugt stattdessen das abstrakte AccountTOP. Alles kompiliert; verwendet wird Ihre Klasse."), "good"),
        (T("Model: + String currency; → regenerate", "Modell: + String currency; → neu generieren"),
         file("out/Account.java", gen[:3] + ["  String currency;", gen[3], "}"], new=(3,)), T("currency appears; your hand-written method is still gone.", "currency erscheint; Ihre handgeschriebene Methode bleibt verschwunden."), "bad",
         file("out/AccountTOP.java", gen_top[:3] + ["  String currency;", gen_top[3], "}"], new=(3,)) + file("hwc/Account.java", hw, cls="hw"),
         T("AccountTOP gains currency; hwc/ is never touched. Regenerating is always safe.", "AccountTOP bekommt currency; hwc/ wird nie angefasst. Neu generieren ist immer sicher."), "good"),
    ]
    data = {"steps": [{"title": L(t), "a": a, "an": L(an), "ac": ac, "b": b, "bn": L(bn), "bc": bc} for t, a, an, ac, b, bn, bc in steps],
            "words": {k: L(v) for k, v in dict(step=T("step", "Schritt"), of=T("of", "von"), play=T("play", "abspielen"), pause=T("pause", "anhalten")).items()}}
    s0 = data["steps"][0]
    inner = f'''<div class="d2-grid">
  <div class="d2-lane" data-lane="a"><span class="k mono">{L(T("EDIT THE GENERATED CODE", "GENERIERTEN CODE BEARBEITEN"))}</span><div class="d2-files">{s0["a"]}</div><p class="d2-note mono">{s0["an"]}</p></div>
  <div class="d2-lane" data-lane="b"><span class="k mono">{L(T("TOP MECHANISM", "TOP-MECHANISMUS"))}</span><div class="d2-files">{s0["b"]}</div><p class="d2-note mono">{s0["bn"]}</p></div>
</div>{controls(lang)}'''
    return demo("d2", data, inner, T(
        f"<b>Never edit generated code — extend it.</b> Left, a method typed into the generated file is lost at the next generation, even without any change to the model. Right, the TOP mechanism: when a hand-written class Account exists, the generator emits AccountTOP instead, and Account extends it. The price: after adding a hand-written file you must regenerate once. After the MontiCore handbook {ref_hb()}, Tip 5.30 and Fig. 14.5, and {cite('GMNR21')}, Fig. 1.",
        f"<b>Generierten Code nie bearbeiten — erweitern.</b> Links geht eine in die generierte Datei getippte Methode bei der nächsten Generierung verloren, sogar ohne jede Modelländerung. Rechts der TOP-Mechanismus: Gibt es eine handgeschriebene Klasse Account, erzeugt der Generator stattdessen AccountTOP, und Account erweitert sie. Der Preis: Nach dem Anlegen einer handgeschriebenen Datei muss einmal neu generiert werden. Nach dem MontiCore-Handbuch {ref_hb()}, Tipp 5.30 und Abb. 14.5, und {cite('GMNR21')}, Abb. 1."), lang)


# D3: one line in the model, six files change. Illustrative, simplified — not literal MontiGem output.
D3_BASE = [("String", "name"), ("int", "balance")]
D3_ADD = [("String", "iban"), ("boolean", "active"), ("int", "limit")]
D3_SQL = {"String": "VARCHAR(255)", "int": "INT", "boolean": "BOOLEAN"}
D3_TS = {"String": "string", "int": "number", "boolean": "boolean"}


def _d3_files(attrs):
    cap = lambda s: s[0].upper() + s[1:]
    getter = lambda t, n: f"  public {t} {'is' if t == 'boolean' else 'get'}{cap(n)}() {{ return {n}; }}"
    widget = lambda t, n: (f'  <label><input type="checkbox" name="{n}"> {n}</label>' if t == "boolean"
                           else f'  <label>{n} <input type="{"number" if t == "int" else "text"}" name="{n}"></label>')
    return {
        "table": ["CREATE TABLE account (", "  id BIGINT PRIMARY KEY"] + [f"  , {n} {D3_SQL[t]}" for t, n in attrs] + [");"],
        "data": ["@Entity", "public class Account {"] + [f"  private {t} {n};" for t, n in attrs] + [getter(t, n) for t, n in attrs] + ["}"],
        "command": ["public class AccountUpdate extends Command {", "  private long id;"] + [f"  private {t} {n};" for t, n in attrs] + ["}"],
        "dto": ["public class AccountDTO extends DTO {", "  private long id;"] + [f"  private {t} {n};" for t, n in attrs] + ["}"],
        "ts": ["export interface Account {", "  id: number;"] + [f"  {n}: {D3_TS[t]};" for t, n in attrs] + ["}"],
        "form": ['<form class="account">'] + [widget(t, n) for t, n in attrs] + ["  <button>save</button>", "</form>"],
    }


D3_TEMPLATES = {
    "table": ["CREATE TABLE ${class.name?lower_case} (", "  id BIGINT PRIMARY KEY", "<#list class.attributes as a>", "  , ${a.name} ${sqlType(a)}", "</#list>", ");"],
    "data": ["@Entity", "public class ${class.name} {", "<#list class.attributes as a>", "  private ${a.type} ${a.name};", "</#list>", "<#list class.attributes as a>",
             "  public ${a.type} ${getter(a)}() { return ${a.name}; }", "</#list>", "}"],
    "command": ["public class ${class.name}Update extends Command {", "  private long id;", "<#list class.attributes as a>", "  private ${a.type} ${a.name};", "</#list>", "}"],
    "dto": ["public class ${class.name}DTO extends DTO {", "  private long id;", "<#list class.attributes as a>", "  private ${a.type} ${a.name};", "</#list>", "}"],
    "ts": ["export interface ${class.name} {", "  id: number;", "<#list class.attributes as a>", "  ${a.name}: ${tsType(a)};", "</#list>", "}"],
    "form": ['<form class="${class.name?lower_case}">', "<#list class.attributes as a>", "  ${widget(a)}", "</#list>", "  <button>save</button>", "</form>"],
}


def _hole(line):
    """Template line as HTML with the ${…} holes and <#…> directives in accent."""
    import re
    return re.sub(r'(\$\{[^}]*\}|&lt;#[^&]*&gt;|&lt;/#[^&]*&gt;)', r'<b>\1</b>', esc(line))


def _form_html(attrs, new):
    rows = ""
    for t, n in attrs:
        cls = ' class="new"' if n == new else ""
        inp = '<input type="checkbox" disabled>' if t == "boolean" else f'<input type="text" value="" placeholder="{D3_TS[t]}" disabled>'
        rows += f'<label{cls}><span>{n}</span>{inp}</label>'
    return f'<div class="d3-form">{rows}<button type="button" disabled>save</button></div>'


def demo_files(lang):
    """D3: + attribute in the model, every tier follows. Each state's files are rendered here; the changed lines
    are found by comparing with the previous state, so the counter is honest by construction (_check_d3)."""
    L = lambda x: x[lang]
    tiers = [("table", T("Table", "Tabelle"), T("rows on disk", "Zeilen auf der Platte"), "db"),
             ("data", T("Data class", "Datenklasse"), T("the server's object", "das Objekt im Server"), "server"),
             ("command", "Command", T("one action the browser may ask for", "eine Aktion, die der Browser anfragen darf"), "server"),
             ("dto", "DTO", T("the package between server and browser", "das Paket zwischen Server und Browser"), "server"),
             ("ts", T("TS model", "TS-Modell"), T("the browser's copy", "die Kopie im Browser"), "browser"),
             ("form", T("Form", "Formular"), T("what the user sees", "was die Nutzerin sieht"), "browser")]
    states, prev = [], None
    for k in range(len(D3_ADD) + 1):
        attrs = D3_BASE + D3_ADD[:k]
        files = _d3_files(attrs)
        new_attr = D3_ADD[k - 1][1] if k else None
        st = {"model": _code(["class Account {"] + [f"  {t} {n};" for t, n in attrs] + ["}"], new=(len(attrs),) if k else ()), "files": {}, "changed": {}}
        for key, lines in files.items():
            changed = [i for i, l in enumerate(lines) if prev is not None and l not in prev[key]]
            st["files"][key] = _code(lines, new=changed)
            st["changed"][key] = len(changed)
        st["form"] = _form_html(attrs, new_attr)
        st["n"], st["m"] = sum(st["changed"].values()), sum(1 for v in st["changed"].values() if v)
        states.append(st)
        prev = files
    _check_d3(states)
    data = {"states": states, "templates": {k: "".join(f'<span class="l">{_hole(l)}</span>' for l in v) for k, v in D3_TEMPLATES.items()},
            "words": {k: L(v) for k, v in dict(
                count=T("1 model line → {n} lines in {m} files", "1 Modellzeile → {n} Zeilen in {m} Dateien"),
                start=T("try: + attribute", "probieren: + Attribut"), full=T("all three added — reset to start over", "alle drei ergänzt — von vorn mit „zurücksetzen“"),
                tpl=T("The template does not change — only the model does. The holes are filled from it.", "Das Template ändert sich nicht — nur das Modell. Die Lücken werden daraus gefüllt.")).items()}}
    chip = lambda key, name, sub: (f'<button type="button" class="d3-chip" data-f="{key}" aria-pressed="{"true" if key == "data" else "false"}">'
                                   f'<b>{L(name) if isinstance(name, dict) else name}</b><span>{L(sub)}</span><em class="d3-badge"></em></button>')
    cols = [("db", T("DATABASE", "DATENBANK")), ("server", "SERVER"), ("browser", "BROWSER")]
    tier_html = "".join(f'<div class="d3-tier"><span class="k mono">{L(n) if isinstance(n, dict) else n}</span>'
                        + "".join(chip(k, nm, sub) for k, nm, sub, t in tiers if t == tid) + '</div>' for tid, n in cols)
    inner = f'''<div class="d3-grid">
  <div class="d3-model"><span class="k mono">{L(T("THE MODEL · CD4A", "DAS MODELL · CD4A"))}</span><pre class="mono">{states[0]["model"]}</pre>
    <div class="d3-ctrl mono"><button type="button" class="d3-add">+ {L(T("attribute", "Attribut"))}</button><button type="button" class="d3-reset">{L(T("reset", "zurücksetzen"))}</button></div>
    <p class="d3-count mono" aria-live="polite">{L(T("try: + attribute", "probieren: + Attribut"))}</p></div>
  <div class="d3-out">
    <div class="d3-tiers">{tier_html}</div>
    <div class="d3-view mono" role="group"><button type="button" data-view="code" aria-pressed="true">code</button><button type="button" data-view="template" aria-pressed="false">template</button></div>
    <pre class="mono d3-code">{states[0]["files"]["data"]}</pre>
    <div class="d3-form-wrap" hidden></div>
    <p class="d3-tplnote mono" hidden></p>
  </div>
</div>
<p class="d3-rte mono"><span>{L(T("not generated:", "nicht generiert:"))}</span> <i>{L(T("runtime environment (hand-built once)", "Laufzeitumgebung (einmal von Hand gebaut)"))}</i> · <i>{L(T("libraries (Hibernate, Angular)", "Bibliotheken (Hibernate, Angular)"))}</i></p>'''
    return demo("d3", data, inner, T(
        f"<b>One added attribute updates every tier — nothing can drift apart.</b> Click <i>+ attribute</i> and pick a file; changed lines are marked. Switch to <i>template</i> to see where the code comes from: the template stays the same, the model fills its holes. Illustrative and simplified — not literal MontiGem output; MontiGem generates more per class (builder, DAO, validator, a loader that fills the transfer objects). After {cite('GHK+20')}, Fig. 3, and {cite('Net24')}, ch. 5.",
        f"<b>Ein zusätzliches Attribut ändert jede Schicht — nichts kann auseinanderlaufen.</b> Klicken Sie auf <i>+ Attribut</i> und wählen Sie eine Datei; geänderte Zeilen sind markiert. Unter <i>template</i> sehen Sie, woher der Code kommt: Das Template bleibt gleich, das Modell füllt seine Lücken. Schematisch und vereinfacht — keine wörtliche MontiGem-Ausgabe; MontiGem generiert pro Klasse mehr (Builder, DAO, Validator, einen Loader, der die Transferobjekte füllt). Nach {cite('GHK+20')}, Abb. 3, und {cite('Net24')}, Kap. 5."), lang)


def _check_d3(states):
    import re
    for a, b in zip(states, states[1:]):
        for key in b["files"]:
            na = len(re.findall(r'<span class="l', a["files"][key]))
            nb = len(re.findall(r'<span class="l', b["files"][key]))
            assert nb - na == b["changed"][key] and b["changed"][key] > 0, key


# D4: CD2GUI — pages nobody drew. Fictional data throughout.
D4_DATA = {
    "Account": {"attrs": [("name", "String"), ("balance", "int")], "rows": [["Account_1", "500"], ["Account_2", "1200"]]},
    "Person": {"attrs": [("name", "String")], "rows": [["Alice"], ["Bob"]]},
    "Accountant": {"attrs": [("name", "String"), ("bank", "String")], "rows": [["Bob", "ExampleBank"]]},
}


def demo_cd2gui(lang):
    """D4: pick a class, see the dashboard / overview / details pages CD2GUI derives, and the GUI-model tree
    behind them; on Accountant → Details, a hand-written delta removes a table and adds a row of buttons.
    After GMN+20 Figs 5–9, Tables 2/3, MNN+22 Fig.3 and Net24 ch.6."""
    L = lambda x: x[lang]
    W = {k: L(v) for k, v in dict(details=T("details", "Details"), overview=T("overview", "Übersicht"), dash=T("Dashboard", "Dashboard"),
                                  inspect=T("inspect", "ansehen"), instances=T("objects", "Objekte"), save=T("save", "speichern"),
                                  key=T("Key", "Schlüssel"), value=T("Value", "Wert"), accounts=T("Accounts", "Konten")).items()}

    def table(head, rows, link=True):
        th = "".join(f"<th>{h}</th>" for h in head) + ("<th></th>" if link else "")
        tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + (f'<td><span class="pill">{W["inspect"]}</span></td>' if link else "") + "</tr>" for r in rows)
        return f'<table><tr>{th}</tr>{tr}</table>'

    def card(title, body, cls=""):
        return f'<div class="gp-card {cls}"><div class="gp-head">{title}</div><div class="gp-body">{body}</div></div>'

    def tree(nodes):
        return '<ul class="d4-tree mono">' + "".join(f'<li style="--d:{d}"{f" class={c!r}" if c else ""}>{esc(t)}</li>' for d, t, c in nodes) + "</ul>"

    pages = {}
    dash = "".join(card(c, f'<p>{len(v["rows"])} {W["instances"]}</p><span class="pill">{W["overview"]}</span>') for c, v in D4_DATA.items())
    pages["dashboard"] = {"url": "/generated/dashboard", "html": f'<div class="gp-cards">{dash}</div>',
                          "tree": tree([(0, "«Page» Dashboard", "")] + [(1, f"Card {c}", "") for c in D4_DATA])}
    for c, v in D4_DATA.items():
        lc = c.lower()
        cols = [a for a, _ in D4_DATA["Person"]["attrs"]] if c == "Person" else [a for a, _ in v["attrs"]]
        rows = [["Alice"], ["Bob"]] if c == "Person" else v["rows"]
        pages[f"{c}/overview"] = {"url": f"/generated/{lc}/overview", "html": card(f"{c} {W['overview']}", table(cols, rows)),
                                  "tree": tree([(0, f"«Page» {c}Overview", ""), (1, "C1: card", ""), (2, "L1: label", ""), (2, "T1: datatable", "")])}
        kv = table([W["key"], W["value"]], [[a, r] for (a, _), r in zip(v["attrs"], v["rows"][0])], link=False)
        body = kv
        nodes = [(0, f"A: «Page» {c}Details", ""), (1, "C1: card", ""), (2, "L1: label", ""), (2, f"T1: datatable “{c} attributes”", "")]
        if c == "Accountant":
            body += f'<h5>{W["accounts"]}</h5>' + table(["name"], [["Account_1"], ["Account_2"]])
            nodes.append((2, "T2: datatable “Accountant accounts”", ""))
        pages[f"{c}/details"] = {"url": f"/generated/{lc}/details/42", "html": card(f"{c} {W['details']}", body), "tree": tree(nodes)}
    v = D4_DATA["Accountant"]
    kv = table([W["key"], W["value"]], [[a, r] for (a, _), r in zip(v["attrs"], v["rows"][0])], link=False)
    pages["Accountant/details+delta"] = {
        "url": "/generated/accountant/details/42",
        "html": '<div class="gp-row new"><span class="pill">B2</span><b>Accountant details</b><span class="pill">B3</span></div>' + card(f"Accountant {W['details']}", kv),
        "tree": tree([(0, "A: «Page» AccountantDetails", ""), (1, "R: row  (add_before @C1)", "new"), (2, "B2 · @L1 · B3", "new"), (1, "C1: card", ""),
                      (2, "L1: label", ""), (2, "T1: datatable “Accountant attributes”", ""), (2, "T2: datatable  (remove @T2)", "gone")])}
    data = {"pages": pages, "words": W}
    uml = (f'<svg class="dia d4-uml" viewBox="0 0 330 170" role="group" aria-label="{L(T("Choose a class", "Klasse wählen"))}">'
           + "".join(f'<g class="d4-cls" data-c="{c}" tabindex="0" role="button" aria-pressed="false">{_uml(x, y, 130, c, [f"{t} {a}" for a, t in D4_DATA[c]["attrs"] if not (c == "Accountant" and a == "name")])[0]}</g>'
                     for c, x, y in (("Person", 10, 6), ("Accountant", 10, 100), ("Account", 196, 100)))
           + '<path class="ln" d="M75 100V66"/><path class="box" d="M75 54L68 66H82Z"/><path class="ln" d="M140 128H192"/>'
           + '<text x="146" y="122" class="s">1</text><text x="188" y="122" text-anchor="end" class="s">*</text></svg>')
    p0 = pages["dashboard"]
    inner = f'''<div class="d4-grid">
  <div class="d4-pick"><span class="k mono">{L(T("THE CLASS DIAGRAM · pick a class", "DAS KLASSENDIAGRAMM · Klasse wählen"))}</span>{uml}
    <label class="d4-delta mono"><input type="checkbox" disabled> {L(T("hand-written delta (Accountant → details)", "handgeschriebenes Delta (Accountant → Details)"))}</label>
    <pre class="mono d4-deltacode" hidden>remove @T2
add_before @C1 [
  row {{ button 'B2'  @L1  button 'B3' }}
]</pre></div>
  <div class="d4-browser"><div class="d4-bar mono"><span class="d4-url" aria-live="polite">{p0["url"]}</span></div>
    <div class="d4-tabs mono" role="group"><button type="button" data-t="dashboard" aria-pressed="true">{W["dash"]}</button><button type="button" data-t="overview" aria-pressed="false" disabled>{L(T("Overview", "Übersicht"))}</button><button type="button" data-t="details" aria-pressed="false" disabled>{L(T("Details", "Details"))}</button></div>
    <div class="d4-page">{p0["html"]}</div></div>
  <details class="d4-treebox" open><summary class="k mono">{L(T("THE GUI MODEL BEHIND IT (a tree)", "DAS GUI-MODELL DAHINTER (ein Baum)"))}</summary><div class="d4-tree-wrap">{p0["tree"]}</div></details>
</div>'''
    return demo("d4", data, inner, T(
        f"<b>Pages nobody drew.</b> From three classes, CD2GUI derives one dashboard and, per class, an overview and a details page — as GUI models, which MontiGem then turns into code. Pick a class and a page; the tree on the right is the GUI model. On Accountant → details, switch on the hand-written delta: it removes the accounts table and adds a row of buttons. Because the change lives in a small model and not in generated HTML, it is re-applied on every regeneration. Fictional data. After {cite('GMN+20')}, Figs. 5–9 and Tables 2/3, and {cite('MNN+22')}, Fig. 3.",
        f"<b>Seiten, die niemand gezeichnet hat.</b> Aus drei Klassen leitet CD2GUI ein Dashboard und je Klasse eine Übersichts- und eine Detailseite ab — als GUI-Modelle, aus denen MontiGem dann Code macht. Wählen Sie eine Klasse und eine Seite; der Baum rechts ist das GUI-Modell. Bei Accountant → Details schalten Sie das handgeschriebene Delta ein: Es entfernt die Kontentabelle und fügt eine Zeile mit Knöpfen hinzu. Weil die Änderung in einem kleinen Modell steckt und nicht im generierten HTML, wird sie bei jeder Neugenerierung erneut angewendet. Fiktive Daten. Nach {cite('GMN+20')}, Abb. 5–9 und Tabellen 2/3, und {cite('MNN+22')}, Abb. 3."), lang)


def mapping_table(lang):
    """Next to D4: how CD2GUI maps class-diagram elements to page components (Net24 Listing 6.3, §6.6; GMN+20 p.8)."""
    L = lambda x: x[lang]
    rows = [(T("Boolean attribute", "Boolean-Attribut"), T("checkbox", "Checkbox")),
            (T("text or number attribute", "Text- oder Zahlattribut"), T("text field", "Textfeld")),
            (T("enum", "Enum"), T("drop-down", "Auswahlliste")),
            (T("reference to a class with a details page", "Verweis auf eine Klasse mit Detailseite"), T("link to that page", "Link auf diese Seite")),
            (T("association to many", "Assoziation zu vielen"), T("sub-table of linked objects", "Untertabelle verknüpfter Objekte")),
            ("«key_attribute» · «invisible» · «hide_in_overview»", T("which columns show up (default: the first 8)", "welche Spalten erscheinen (Standard: die ersten 8)"))]
    body = "".join(f"<tr><td>{L(a) if isinstance(a, dict) else a}</td><td>{L(b)}</td></tr>" for a, b in rows)
    return (f'<figure class="media art-fig"><div class="tbl-wrap"><table class="tbl mono"><tr><th>{L(T("in the class diagram", "im Klassendiagramm"))}</th><th>{L(T("on the page", "auf der Seite"))}</th></tr>{body}</table></div>'
            f'<figcaption class="mono">{L(T("How CD2GUI maps the class diagram to page components; stereotypes in the class diagram steer the defaults.", "Wie CD2GUI das Klassendiagramm auf Seitenbausteine abbildet; Stereotypen im Klassendiagramm steuern die Voreinstellungen."))} {cite("Net24")}, {L(T("ch. 6", "Kap. 6"))}; {cite("GMN+20")}</figcaption></figure>')


def fig_three_languages(lang):
    """F6: three languages, one screen (CSS :has() hover). After GLM+24 Fig.9 and BGK+24 Listing 2. Fictional data."""
    L = lambda x: x[lang]
    gui = 'webpage Staff(all Person p) {\n  card {\n    head { label "Staff" }\n    body {\n      datatable { rows <p {\n        column "Name", name\n        column "Age", age\n}}}}}'
    codes = [("data", T("DATA", "DATEN"), "CD4A", "class Person {\n  String name;\n  int age;\n}"),
             ("page", T("PAGE", "SEITE"), "GUI-DSL", gui),
             ("rule", T("RULE", "REGEL"), "OCL/P", "context Person inv isAgeNotNegative:\n  age >= 0;")]
    boxes = "".join(f'<div class="f6-code" data-k="{k}" tabindex="0"><span class="k mono">{L(a)} · {b}</span><pre class="mono">{esc(c)}</pre></div>' for k, a, b, c in codes)
    mock = f'''<div class="f6-page" aria-hidden="true">
  <div class="gp-card f6-reg" data-k="page"><div class="gp-head">Staff</div><div class="gp-body">
    <table class="f6-reg" data-k="data"><tr><th>Name</th><th>Age</th></tr><tr><td>Alice</td><td>34</td></tr><tr><td>Bob</td><td>41</td></tr></table>
    <div class="f6-edit f6-reg" data-k="rule"><label>Age <input type="text" value="-10" disabled></label><span>{L(T("Age has to be positive", "Age has to be positive"))}</span></div>
  </div></div></div>'''
    inner = f'<div class="f6">{mock}<div class="f6-codes">{boxes}</div></div>'
    return (f'<figure class="media art-fig">{inner}<figcaption class="mono">{L(T("<b>Three languages, one screen.</b> The data model says what a Person is, the page model how persons are listed, the rule what a valid age is — and the generated page enforces it in the browser and on the server. Point at a model to see its part of the page. Fictional data.", "<b>Drei Sprachen, ein Bildschirm.</b> Das Datenmodell sagt, was eine Person ist, das Seitenmodell, wie Personen aufgelistet werden, die Regel, was ein gültiges Alter ist — und die generierte Seite setzt das im Browser und auf dem Server durch. Zeigen Sie auf ein Modell, um seinen Teil der Seite zu sehen. Fiktive Daten."))} '
            f'{L(T("After", "Nach"))} {cite("GLM+24")}, {L(T("Fig. 9", "Abb. 9"))}, {L(T("and", "und"))} {cite("BGK+24")}, Listing 2.</figcaption></figure>')


def fig_chain(lang):
    """F9: from a sentence to an application, the toolchain of Net24 (Fig.2.4): ① LLM → ② CD2GUI → ③ MontiGem.
    The numbers are links; pointing at one dims what it does not touch (CSS :has())."""
    L = lambda x: x[lang]
    panes = [("1", T("INFORMAL DESCRIPTION", "INFORMELLE BESCHREIBUNG"), f'<p class="f9-bubble">{L(T("“Create a model for a library management system.”", "„Erstelle ein Modell für ein Bibliotheksverwaltungssystem.“"))}</p>', T("domain expert", "Domänenexpertin")),
             ("1 2", T("DOMAIN MODEL", "DOMÄNENMODELL"), '<pre class="mono">class Book {\n  String title;\n  Long pages;\n  String author;\n}\nclass Visitor {\n  String name;\n  Long id;\n}</pre>', T("system modeler · may merge own models", "Systemmodelliererin · kann eigene Modelle einfügen")),
             ("2 3", T("APPLICATION MODELS", "ANWENDUNGSMODELLE"), f'<p class="mono">BookOverview.gui<br>BookDetails.gui<br>VisitorOverview.gui<br>…<br>Dashboard.gui</p>', T("pages, rules, roles", "Seiten, Regeln, Rollen")),
             ("3", T("GENERATED APPLICATION", "GENERIERTE ANWENDUNG"), f'<p class="f9-stack mono"><span class="g">{L(T("generated", "generiert"))}</span><span>{L(T("runtime environment", "Laufzeitumgebung"))}</span><span class="h">{L(T("hand-written (TOP)", "handgeschrieben (TOP)"))}</span></p>', T("programmer · tool smith", "Programmiererin · Werkzeugbauer"))]
    steps = [("1", "LLM", "research-ai4se.html#models"), ("2", "CD2GUI", "#cd2gui"), ("3", "MontiGem", "#whygen")]
    out = ""
    for k, (ks, head, body, who) in enumerate(panes):
        out += f'<div class="f9-pane" data-k="{ks}"><span class="k mono">{L(head)}</span>{body}<span class="f9-who mono">{L(who)}</span></div>'
        if k < 3:
            n, name, href = steps[k]
            out += f'<a class="f9-step mono" data-k="{n}" href="{href}"><b>{"①②③"[k]}</b>{name}</a>'
    return (f'<figure class="media art-fig"><div class="f9">{out}</div><figcaption class="mono">{L(T("<b>AI only in step 1.</b> An LLM turns the description into a class diagram; everything after the model — CD2GUI and MontiGem — is deterministic, repeatable and checkable. Point at a step to see what it touches; click it to read more. After", "<b>KI nur in Schritt 1.</b> Ein LLM macht aus der Beschreibung ein Klassendiagramm; alles nach dem Modell — CD2GUI und MontiGem — ist deterministisch, wiederholbar und prüfbar. Zeigen Sie auf einen Schritt, um zu sehen, was er berührt; ein Klick führt zur Erklärung. Nach"))} {cite("Net24")}, {L(T("Fig. 2.4", "Abb. 2.4"))}.</figcaption></figure>')
