"""
Figures of the MDE article (research-mde.html, _build/mde.py). Static diagrams are inline SVG with the .dia classes
of style.css (article-specific styles in assets/mde.css); the interactive figures get all their states precomputed
here and shipped as data-json — assets/mde.js only swaps and highlights.

One running example from the first figure to the last: a small library (Book, Member, Loan). Figures redrawn after
figures of the MontiGem papers name their source in the caption's source line (article_common.src).

Wide figures are authored at viewBox width 784 (1 unit = 1 px on desktop); the ones that would be unreadable at
390 px get a stacked twin (class "v-wide" / "v-tall", swapped in mde.css below 600 px).
"""
import html
import re

from ai4se import T, fig, demo, controls, cite, ref
from article_common import src, source_line
from project_content import _arrow_defs, box

esc = html.escape

HB = 6            # number of the MontiCore handbook in mde.REFS (mde.py asserts it)

# ---------------------------------------------------------------------------------------------------------------
# The running example: a small library. Every figure uses these names.
# ---------------------------------------------------------------------------------------------------------------
CLASSES = {"Book": [("String", "title"), ("int", "pages"), ("boolean", "available")],
           "Member": [("String", "name")],
           "Loan": [("Date", "due")]}
# (line, key for the linked highlighting in d1)
EXAMPLE = [("classdiagram Library {", "cd"),
           ("  class Book {", "book"), ("    String title;", "book.title"), ("    int pages;", "book.pages"),
           ("    boolean available;", "book.available"), ("  }", "book"),
           ("  class Member {", "member"), ("    String name;", "member.name"), ("  }", "member"),
           ("  class Loan {", "loan"), ("    Date due;", "loan.due"), ("  }", "loan"),
           ("  association [1] Member -> (loans) Loan [*];", "a1"),
           ("  association [*] Loan -> (book) Book [1];", "a2"),
           ("}", "cd")]


def example_text():
    return "\n".join(esc(l) for l, _ in EXAMPLE)


def twin(wide, tall):
    """A wide figure and its stacked phone variant (mde.css shows one of them)."""
    return f'<div class="v-wide">{wide}</div><div class="v-tall">{tall}</div>'


def _uml(x, y, w, name, attrs, key="", akeys=None, hl=False):
    """A UML class box: name compartment, then one row per attribute. Returns (svg, height)."""
    h = 26 + 17 * len(attrs) + 8
    akeys = akeys or [""] * len(attrs)
    out = (f'<rect class="box{" hl" if hl else ""}" x="{x}" y="{y}" width="{w}" height="{h}" rx="2"/>'
           f'<path class="ln" d="M{x} {y + 26}H{x + w}"/>'
           f'<text x="{x + w / 2}" y="{y + 17}" text-anchor="middle" class="t">{name}</text>')
    for k, (a, ak) in enumerate(zip(attrs, akeys)):
        dk = f' data-k="{ak}"' if ak else ""
        out += f'<text x="{x + 10}" y="{y + 42 + 17 * k}"{dk}>{esc(a)}</text>'
    return out, h


def _attrs(c):
    return [f"{t} {n}" for t, n in CLASSES[c]]


# =====================================================================
# The hero: the same model as text and as a diagram, and the application generated from it
# =====================================================================

def _hero_code(x, y, w=264, lh=15):
    lines = ["classdiagram Library {", "  class Book {", "    String title; int pages;", "  }", "  class Member { String name; }",
             "  class Loan { Date due; }", "  association [1] Member -> Loan [*];", "  association [*] Loan -> Book [1];", "}"]
    return (f'<g transform="translate({x} {y})"><rect class="box" width="{w}" height="{20 + lh * 9}" rx="3"/>'
            + "".join(f'<text class="hc" x="12" y="{24 + lh * k}">{esc(l)}</text>' for k, l in enumerate(lines)) + '</g>')


def _hero_uml(x, y):
    m, _ = _uml(0, 0, 96, "Member", ["name"])
    lo, _ = _uml(0, 100, 96, "Loan", ["due"])
    b, _ = _uml(140, 100, 96, "Book", ["title", "pages"], hl=True)
    return (f'<g transform="translate({x} {y})">{m}{lo}{b}'
            '<path class="ln" d="M48 51V100"/><text class="s" x="54" y="64">1</text><text class="s" x="54" y="96">*</text>'
            '<path class="ln" d="M96 125H140"/><text class="s" x="100" y="120">*</text><text class="s" x="134" y="120" text-anchor="end">1</text></g>')


def _hero_app(x, y, books):
    return (f'<g transform="translate({x} {y})"><rect class="box hl" width="180" height="160" rx="4"/><path class="ln" d="M0 16H180"/>'
            '<circle class="dot" cx="9" cy="8" r="2"/><circle class="dot" cx="17" cy="8" r="2" opacity=".4"/>'
            f'<text class="t" x="12" y="38">{books}</text>'
            '<path class="ln" d="M12 52H168"/>'
            + "".join(f'<path class="ln" d="M12 {70 + 18 * k}H120"/><rect class="box" x="150" y="{63 + 18 * k}" width="10" height="10" rx="1"/>'
                      + (f'<path class="ln hl" d="M152 {68 + 18 * k}l3 3l4 -6"/>' if k != 1 else "") for k in range(4))
            + '<rect class="box" x="12" y="138" width="54" height="14" rx="2"/></g>')


def hero_mde(lang):
    """Top of the article: one model, two notations, and the application a generator makes of it. Not the
    abstract model → generator → application of d0 level 1, but the concrete running example."""
    L = lambda x: x[lang]
    books = L(T("Books", "Bücher"))
    h1, h2, h3 = L(T("THE MODEL · AS TEXT", "DAS MODELL · ALS TEXT")), L(T("· AS A DIAGRAM", "· ALS DIAGRAMM")), L(T("THE APPLICATION", "DIE ANWENDUNG"))
    gen = L(T("generated", "generiert"))
    wide = (f'<rect class="zone" width="860" height="220" rx="6"/>'
            f'<text class="s" x="36" y="26">{h1}</text><text class="s" x="330" y="26">{h2}</text><text class="s" x="640" y="26">{h3}</text>'
            f'{_hero_code(36, 40)}<path class="ln dash" d="M304 120H326"/>{_hero_uml(334, 50)}'
            f'<path class="ln hl" d="M584 120H628" marker-end="url(#mhra)"/><text class="s a" x="606" y="110" text-anchor="middle">{gen}</text>'
            f'{_hero_app(640, 40, books)}')
    tall = (f'<rect class="zone" width="430" height="652" rx="6"/>'
            f'<text class="s" x="24" y="26">{h1}</text>{_hero_code(24, 38, w=382, lh=17)}'
            f'<text class="s" x="24" y="242">{L(T("THE SAME MODEL AS A DIAGRAM", "DASSELBE MODELL ALS DIAGRAMM"))}</text>{_hero_uml(96, 256)}'
            f'<path class="ln hl" d="M215 442V474" marker-end="url(#mhta)"/><text class="s a" x="224" y="462">{gen}</text>'
            f'<text class="s" x="24" y="470">{h3}</text>{_hero_app(125, 482, books)}')
    # separate marker ids: the hidden wide svg would otherwise own the marker and the tall one shows no arrowhead
    return (f'<figure class="art-hero" aria-hidden="true"><svg class="dia hero hero-wide" viewBox="0 0 860 220">{_arrow_defs("mhr")}{wide}</svg>'
            f'<svg class="dia hero hero-tall" viewBox="0 0 430 652">{_arrow_defs("mht")}{tall}</svg></figure>')


# =====================================================================
# Static figures
# =====================================================================

def fig_intro(lang):
    """F0: the generator from far away (levels 1–2 of the morph in mde_levels.py)."""
    import mde_levels
    return mde_levels.fig_levels(lang, "intro")


def fig_inside(lang):
    """The generator from inside (levels 2–4), in the generator section."""
    import mde_levels
    return mde_levels.fig_levels(lang, "inside")


def fig_backend(lang):
    """Level 5 alone: MontiGem's back-end generator, for the curious box in chapter 03."""
    import mde_levels
    return mde_levels.fig_levels(lang, "full")


def fig_maps(lang):
    """F1: one city, three maps — mapping, reduction, purpose. The city and its maps are built in mde_map.py."""
    import mde_map
    return mde_map.fig_maps(lang, src("fictional"))


READ = {
    "member": T("<b>Member</b> is a class: a kind of thing in the library. Every member has a name.",
                "<b>Member</b> ist eine Klasse: eine Art von Ding in der Bibliothek. Jedes Mitglied hat einen Namen."),
    "loan": T("<b>Loan</b> is a class too: one book lent to one member, due on a date.",
              "<b>Loan</b> ist auch eine Klasse: ein Buch, an ein Mitglied verliehen, fällig an einem Datum."),
    "book": T("<b>Book</b> is a class: not one book, but what all books have in common.",
              "<b>Book</b> ist eine Klasse: nicht ein Buch, sondern das, was alle Bücher gemeinsam haben."),
    "attr": T("<b>Attributes</b> are fields every Book has: a title, a number of pages, and whether it is available.",
              "<b>Attribute</b> sind Felder, die jedes Book hat: einen Titel, eine Seitenzahl und ob es verfügbar ist."),
    "has": T("A <b>Member</b> has <b>any number of</b> Loans; every Loan belongs to <b>exactly one</b> Member.",
             "Ein <b>Member</b> hat <b>beliebig viele</b> Loans; jeder Loan gehört zu <b>genau einem</b> Member."),
    "for": T("A <b>Loan</b> is for <b>exactly one</b> Book; a Book can be in <b>any number of</b> Loans over time.",
             "Ein <b>Loan</b> gilt für <b>genau ein</b> Book; ein Book kann im Lauf der Zeit in <b>beliebig vielen</b> Loans stehen."),
    "mult": T("The numbers at the ends of a line say how many: <b>1</b> = exactly one, <b>*</b> = any number, none included.",
              "Die Zahlen an den Enden einer Linie sagen, wie viele: <b>1</b> = genau eins, <b>*</b> = beliebig viele, auch keins."),
}


def fig_classdiagram(lang):
    """F2: reading a class diagram — point at a part and the strip below reads it out as a sentence.
    Two layouts: a row (desktop) and a column (phone); the same data-k keys in both."""
    L = lambda x: x[lang]

    def cls(c, x, y, w=150):
        attrs = _attrs(c)
        h = 26 + 17 * len(attrs) + 8
        head = (f'<rect class="box{" hl" if c == "Book" else ""}" x="{x}" y="{y}" width="{w}" height="{h}" rx="2"/>'
                f'<path class="ln" d="M{x} {y + 26}H{x + w}"/><text x="{x + w / 2}" y="{y + 17}" text-anchor="middle" class="t">{c}</text>')
        rows = "".join(f'<text x="{x + 10}" y="{y + 42 + 17 * k}">{esc(a)}</text>' for k, a in enumerate(attrs))
        if c == "Book":                             # the attributes are a target of their own, inside the class
            rows = f'<g class="k" data-k="attr" tabindex="0">{rows}</g>'
        return f'<g class="k" data-k="{c.lower()}" tabindex="0">{head}{rows}</g>', h

    def mult(items):
        return '<g class="k" data-k="mult" tabindex="0">' + "".join(f'<text x="{x}" y="{y}" text-anchor="{a}" class="m">{t}</text>' for x, y, a, t in items) + '</g>'

    has, isfor = L(T("has", "hat")), L(T("is for", "gilt für"))
    # the row: Member — Loan — Book
    m, _ = cls("Member", 30, 30)
    lo, _ = cls("Loan", 317, 30)
    b, _ = cls("Book", 604, 30)
    y = 73
    wide = (f'<svg class="dia f2" viewBox="0 22 784 100" role="group" aria-label="{L(T("Class diagram of a library: a Member has any number of Loans, a Loan is for exactly one Book; Book has a title, pages and whether it is available", "Klassendiagramm einer Bibliothek: Ein Member hat beliebig viele Loans, ein Loan gilt für genau ein Book; Book hat Titel, Seitenzahl und Verfügbarkeit"))}">'
            f'{m}{lo}{b}'
            f'<g class="k" data-k="has" tabindex="0"><path class="ln" d="M180 {y}H317"/><text x="248" y="{y + 20}" text-anchor="middle" class="lab">{has}</text></g>'
            f'<g class="k" data-k="for" tabindex="0"><path class="ln" d="M467 {y}H604"/><text x="535" y="{y + 20}" text-anchor="middle" class="lab">{isfor}</text></g>'
            + mult([(188, y - 7, "start", "1"), (309, y - 7, "end", "*"), (475, y - 7, "start", "*"), (596, y - 7, "end", "1")]) + '</svg>')
    # the column: Member above Loan above Book
    m, mh = cls("Member", 100, 8, 180)
    lo, lh = cls("Loan", 100, 120, 180)
    b, _ = cls("Book", 100, 232, 180)
    x = 190
    tall = (f'<svg class="dia f2" viewBox="0 0 380 322" role="group" aria-label="{L(T("Class diagram of a library", "Klassendiagramm einer Bibliothek"))}">'
            f'{m}{lo}{b}'
            f'<g class="k" data-k="has" tabindex="0"><path class="ln" d="M{x} {8 + mh}V120"/><text x="{x + 10}" y="{(8 + mh + 120) / 2 + 4}" class="lab">{has}</text></g>'
            f'<g class="k" data-k="for" tabindex="0"><path class="ln" d="M{x} {120 + lh}V232"/><text x="{x + 10}" y="{(120 + lh + 232) / 2 + 4}" class="lab">{isfor}</text></g>'
            + mult([(x - 7, 8 + mh + 14, "end", "1"), (x - 7, 116, "end", "*"), (x - 7, 120 + lh + 14, "end", "*"), (x - 7, 228, "end", "1")]) + '</svg>')
    prompt = L(T("Point at a part of the diagram — it reads itself out here.", "Zeigen Sie auf einen Teil des Diagramms — hier steht, wie man ihn liest."))
    data = html.escape(__import__("json").dumps({"read": {k: L(v) for k, v in READ.items()}, "prompt": prompt}, ensure_ascii=False), quote=True)
    cap = T("<b>Read it as sentences.</b> A Member <i>has</i> any number of Loans, a Loan <i>is for</i> exactly one Book, and every Book has a title, a number of pages and whether it is available. This small library is the running example of the article.",
            "<b>Als Sätze lesen.</b> Ein Member <i>hat</i> beliebig viele Loans, ein Loan <i>gilt für</i> genau ein Book, und jedes Book hat einen Titel, eine Seitenzahl und ob es verfügbar ist. Diese kleine Bibliothek ist das laufende Beispiel des Artikels.")
    source = src("illustrative")
    return (f'<figure class="media art-fig f2-fig" data-read="{data}">{twin(wide, tall)}'
            f'<p class="f2-read" aria-live="polite">{prompt}</p>'
            f'<figcaption class="mono">{L(cap)}{source_line(source, lang)}</figcaption></figure>')


def fig_aspects(lang):
    """F3: divide the problem, one language per aspect — and where each aspect lands in the application."""
    L = lambda x: x[lang]
    rows = [(T("data", "Daten"), "CD4A", T("data model", "Datenmodell"), "Library.cd"),
            (T("pages", "Seiten"), "GUI-DSL", T("uses CD4A", "nutzt CD4A"), "BookDetails.gui"),
            (T("rules", "Regeln"), "OCL/P", T("uses CD4A", "nutzt CD4A"), "Library.ocl"),
            (T("who may see what", "wer was sehen darf"), "Tags", T("access rules", "Zugriffsregeln"), "Roles.tag")]
    ports = [92, 112, 132, 152]
    out = ""
    for k, (aspect, lg, sub, model) in enumerate(rows):
        y = 44 + k * 50
        out += (f'<rect class="box" x="14" y="{y}" width="140" height="30" rx="15"/><text x="84" y="{y + 19}" text-anchor="middle">{L(aspect)}</text>'
                f'<path class="ln" d="M154 {y + 15}H190" marker-end="url(#mdc)"/>'
                + box(194, y - 4, 118, 38, lg, L(sub)) +
                f'<path class="ln dash" d="M312 {y + 15}H350"/>'
                f'<path class="box" d="M354 {y}H488l10 10V{y + 30}H354Z"/><text x="364" y="{y + 19}" class="s">{model}</text>'
                f'<path class="ln" d="M498 {y + 15}H{520 + 6 * k}V{ports[k]}H566" marker-end="url(#mdc)"/>')
    # the solution: a page in which every aspect shows up
    sol = (f'<rect class="box hl" x="570" y="44" width="200" height="180" rx="3"/><path class="ln" d="M570 62H770"/>'
           f'<circle cx="580" cy="53" r="3" class="dot"/>'
           f'<text x="582" y="84" class="t">{L(T("Book details", "Buch-Details"))}</text>'
           f'<path class="ln" d="M582 98H758"/><text x="582" y="114" class="s">title</text><text x="640" y="114" class="s">pages</text>'
           f'<rect class="hidcol" x="698" y="103" width="58" height="46"/><text x="702" y="114" class="s">isbn</text>'
           f'<path class="ln" d="M582 122H758M582 140H758"/>'
           f'<text x="582" y="172" class="s">pages</text><rect class="box" x="624" y="161" width="44" height="16" rx="2"/><text x="630" y="173" class="s">0</text>'
           f'<text x="582" y="194" class="s err">✗ {L(T("needs at least one page", "mindestens eine Seite"))}</text>'
           f'<text x="702" y="162" class="s">{L(T("hidden", "verborgen"))}</text>')
    svg = f'''<svg class="dia" viewBox="0 0 784 240" role="img" aria-label="{L(T("A problem is split into aspects: data, pages, rules and who may see what. Each aspect gets its own modelling language, CD4A, GUI-DSL, OCL/P and Tags; each language has concrete models; in the generated page the data becomes a table, the page model its layout, the rule an error message and the access rule a hidden column", "Ein Problem wird in Aspekte zerlegt: Daten, Seiten, Regeln und wer was sehen darf. Jeder Aspekt bekommt eine eigene Modellierungssprache, CD4A, GUI-DSL, OCL/P und Tags; jede Sprache hat konkrete Modelle; in der generierten Seite wird aus den Daten eine Tabelle, aus dem Seitenmodell ihr Aufbau, aus der Regel eine Fehlermeldung und aus der Zugriffsregel eine verborgene Spalte"))}">
  {_arrow_defs("mdc")}
  <rect class="zone" x="0" y="30" width="168" height="206" rx="24"/>
  <text x="0" y="16" class="s">{L(T("ASPECTS", "ASPEKTE"))}</text>
  <text x="194" y="16" class="s">{L(T("ONE LANGUAGE EACH", "JE EINE SPRACHE"))}</text>
  <text x="354" y="16" class="s">{L(T("MODELS · conform to the language", "MODELLE · konform zur Sprache"))}</text>
  <text x="578" y="16" class="s">{L(T("THE APPLICATION", "DIE ANWENDUNG"))}</text>
  {out}{sol}
</svg>'''
    # phone: one row per aspect (language and model), the application below
    out_t = ""
    for k, (aspect, lg, sub, model) in enumerate(rows):
        y = 34 + k * 52
        out_t += (f'<text x="0" y="{y + 12}" class="s">{L(aspect)}</text>'
                  + box(0, y + 18, 120, 28, lg) +
                  f'<path class="ln dash" d="M120 {y + 32}H166"/>'
                  f'<path class="box" d="M170 {y + 18}H368l10 10V{y + 46}H170Z"/><text x="180" y="{y + 36}" class="s">{model}</text>')
    tall = (f'<svg class="dia" viewBox="0 0 380 272" role="img" aria-label="{L(T("Four aspects, four languages, four models", "Vier Aspekte, vier Sprachen, vier Modelle"))}">'
            f'<text x="0" y="14" class="s">{L(T("ASPECT · LANGUAGE", "ASPEKT · SPRACHE"))}</text><text x="170" y="14" class="s">{L(T("MODEL", "MODELL"))}</text>{out_t}'
            f'<text x="0" y="262" class="s">{L(T("all four use the names in Library.cd", "alle vier nutzen die Namen aus Library.cd"))}</text></svg>')
    return fig(twin(svg, tall), T("<b>Divide the problem, one language per aspect.</b> The data model is written in CD4A; the pages, the rules and the access rights each have their own small language, and all of them refer to the names in the data model. In the application each one leaves its trace: a table, its layout, an error message, a hidden column.",
                                  "<b>Das Problem zerlegen, eine Sprache je Aspekt.</b> Das Datenmodell ist in CD4A geschrieben; Seiten, Regeln und Zugriffsrechte haben je eine eigene kleine Sprache, und alle verweisen auf die Namen im Datenmodell. In der Anwendung hinterlässt jede ihre Spur: eine Tabelle, ihren Aufbau, eine Fehlermeldung, eine verborgene Spalte."),
               lang, scroll=False, source=src("after", "DGM+21", where="Fig. 5"))


# ---------------- mail merge: one template, three models ----------------
MM_TEMPLATE = ["public class ${name} {", "<#list attributes as a>", "  private ${a.type} ${a.name};", "</#list>", "}"]


def _mm_out(c):
    lines = [f'public class <b>{c}</b> {{'] + [f'  private <b>{t}</b> <b>{n}</b>;' for t, n in CLASSES[c]] + ["}"]
    return "".join(f'<span class="l">{l}</span>' for l in lines)


def _mm_model(c):
    lines = [f'class <b>{c}</b> {{'] + [f'  <b>{t}</b> <b>{n}</b>;' for t, n in CLASSES[c]] + ["}"]
    return "".join(f'<span class="l">{l}</span>' for l in lines)


def demo_mailmerge(lang):
    """New: a generator works like mail merge. The template stays, the model varies; the holes and what fills
    them are in the accent."""
    L = lambda x: x[lang]
    tpl = "".join(f'<span class="l">{_hole(l)}</span>' for l in MM_TEMPLATE)
    data = {"out": {c: _mm_out(c) for c in CLASSES}, "model": {c: _mm_model(c) for c in CLASSES}}
    chips = "".join(f'<button type="button" data-c="{c}" aria-pressed="{"true" if c == "Book" else "false"}"{" class=first" if c == "Member" else ""}>{c}</button>' for c in CLASSES)
    inner = f'''<div class="mm-grid">
  <div><span class="k mono">{L(T("TEMPLATE · written once", "TEMPLATE · einmal geschrieben"))}</span><pre class="mono mm-tpl">{tpl}</pre></div>
  <div class="mm-op mono" aria-hidden="true">+</div>
  <div><span class="k mono">{L(T("MODEL · pick one", "MODELL · eins wählen"))}</span><div class="chips mono mm-chips" role="group" aria-label="{L(T("Class from the model", "Klasse aus dem Modell"))}">{chips}</div><pre class="mono mm-model">{data["model"]["Book"]}</pre></div>
  <div class="mm-op mono" aria-hidden="true">=</div>
  <div><span class="k mono">{L(T("CODE · generated", "CODE · generiert"))}</span><pre class="mono mm-out" aria-live="polite">{data["out"]["Book"]}</pre></div>
</div>'''
    return demo("mm", data, inner, T("<b>Mail merge for code.</b> The template is the target code with holes; the model fills them. Pick another class: the template does not change, the code follows the model. The <code>&lt;#list&gt;</code> line repeats its body once per attribute.",
                                     "<b>Serienbrief für Code.</b> Das Template ist der Zielcode mit Lücken; das Modell füllt sie. Wählen Sie eine andere Klasse: Das Template ändert sich nicht, der Code folgt dem Modell. Die Zeile <code>&lt;#list&gt;</code> wiederholt ihren Inhalt für jedes Attribut."),
                lang, source=src("illustrative", note=T("template syntax after FreeMarker, as used by MontiCore", "Template-Syntax nach FreeMarker, wie in MontiCore")))


def fig_generator(lang):
    """For the MontiCore box: the language level (built once with MontiCore) and the tool level (read · transform ·
    generate). After [HB] Figs 3.1/3.2 and BGK+24 Fig.2. Wide; scrolls on phones."""
    L = lambda x: x[lang]
    m, ma = 'marker-end="url(#mde)"', 'marker-end="url(#mdea)"'
    chips = [T("parser", "Parser"), T("AST classes", "AST-Klassen"), T("symbol table", "Symboltabelle"), T("rule checker", "Regelprüfer"), T("tree walkers", "Baumläufer")]
    top = "".join(f'<rect class="box hl" x="{372 + k * 104}" y="48" width="96" height="30" rx="3"/><text x="{420 + k * 104}" y="67" text-anchor="middle" class="s">{L(c)}</text>' for k, c in enumerate(chips))
    hw = L(T("hand-written", "handgeschrieben"))
    svg = f'''<svg class="dia" viewBox="0 0 900 360" role="img" aria-label="{L(T("Top: from the CD4A grammar, MontiCore generates the skeleton of the tool — parser, AST classes, symbol table, rule checker, tree walkers. Bottom: the tool reads your model into an AST and checks it, transforms it into an output AST, and fills templates with it to produce code; your own code extends the result", "Oben: Aus der CD4A-Grammatik generiert MontiCore das Gerüst des Werkzeugs — Parser, AST-Klassen, Symboltabelle, Regelprüfer, Baumläufer. Unten: Das Werkzeug liest Ihr Modell in einen AST und prüft ihn, transformiert ihn in einen Ausgabe-AST und füllt damit Templates, die Code ergeben; Ihr eigener Code erweitert das Ergebnis"))}">
  {_arrow_defs("mde")}
  <rect class="zone" x="0" y="8" width="900" height="92" rx="4"/>
  <text x="12" y="26" class="s">{L(T("LANGUAGE · built once, by the language engineer", "SPRACHE · einmal gebaut, von der Sprachingenieurin"))}</text>
  {box(14, 42, 150, 42, L(T("CD4A grammar", "CD4A-Grammatik")))}
  <path class="ln" d="M164 63H202" {m}/>
  {box(206, 42, 130, 42, "MontiCore", L(T("language workbench", "Language Workbench")))}
  <path class="ln" d="M336 63H368" {m}/>
  <text x="372" y="42" class="s a">{L(T("generated", "generiert"))}</text>
  {top}
  <rect class="zone line" x="0" y="122" width="900" height="232" rx="4"/>
  <text x="12" y="140" class="s">{L(T("TOOL · runs on every model", "WERKZEUG · läuft auf jedem Modell"))}</text>
  <text x="14" y="168" class="s a">01 {L(T("READ", "LESEN"))}</text><text x="312" y="168" class="s a">02 {L(T("TRANSFORM", "TRANSFORMIEREN"))}</text><text x="592" y="168" class="s a">03 {L(T("GENERATE", "GENERIEREN"))}</text>
  {box(14, 180, 116, 42, "Library.cd", L(T("your model", "Ihr Modell")), cls="box hl")}
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
  <path class="ln dash" d="M431 258V228"/>
  <path class="ln" d="M508 182V170H780V186" {m}/>
  {box(592, 190, 130, 42, L(T("templates {…}", "Templates {…}")), hw)}
  <path class="ln" d="M722 211H736" {m}/>
  {box(740, 190, 150, 42, L(T("template engine", "Template-Engine")), cls="box hl")}
  <path class="ln" d="M815 232V246" {m}/>
  <rect class="box" x="740" y="250" width="150" height="24" rx="2"/><text x="750" y="266" class="s">Book.java</text>
  <rect class="box" x="740" y="278" width="150" height="24" rx="2"/><text x="750" y="294" class="s">BookDAO.java</text>
  <rect class="box" x="740" y="306" width="150" height="24" rx="2"/><text x="750" y="322" class="s">book.ts · …</text>
  {box(592, 262, 130, 42, L(T("your code/", "Ihr Code/")), L(T("extends it", "erweitert es")), cls="box dashbox")}
  <path class="ln dash" d="M722 290H736" {m}/>
</svg>'''
    return _wide_still(lang, svg, T("<b>Two levels.</b> Above: from one grammar, MontiCore generates the skeleton of a language tool. Below: that tool reads a model, checks it, transforms it and fills templates with it. The rules, the transformation and the templates are written by hand once; the model is what you write every day.",
                      "<b>Zwei Ebenen.</b> Oben: Aus einer Grammatik generiert MontiCore das Gerüst eines Sprachwerkzeugs. Unten: Dieses Werkzeug liest ein Modell, prüft es, transformiert es und füllt damit Templates. Regeln, Transformation und Templates werden einmal von Hand geschrieben; das Modell ist das, was Sie jeden Tag schreiben."),
               src("after", HB, where="Figs. 3.1/3.2"))


def _wide_still(lang, svg, caption, source):
    """A wide static figure kept at a legible scale: it scrolls sideways, also on desktop, with a hint."""
    from project_content import dia_scroll
    return (f'<figure class="media art-fig wide-still">{dia_scroll(svg)}<p class="mde-hint mono" aria-hidden="true">↔ {T("scroll", "scrollen")[lang]}</p>'
            f'<figcaption class="mono">{caption[lang]}{source_line(source, lang)}</figcaption></figure>')


def fig_evolution(lang):
    """When the model changes: version 1 → version 2; the code is regenerated, the data has to be migrated."""
    L = lambda x: x[lang]
    v1 = "class Book {\n  String title;\n  String author;\n}"
    v2 = "class Book {\n  String title;\n}\nclass Author {\n  String name;\n}\nassociation [*] Book -> Author [1];"
    rows = [(T("code", "Code"), T("regenerate — done", "neu generieren — fertig"), "ok"),
            (T("data", "Daten"), T("“Le Guin, Ursula K.” in every row has to become an Author and a link: a migration, written by hand", "„Le Guin, Ursula K.“ in jeder Zeile muss zu einem Author und einer Verknüpfung werden: eine Migration, von Hand geschrieben"), "todo")]
    out = "".join(f'<li class="{c}"><b>{L(a)}</b><span>{L(b)}</span></li>' for a, b, c in rows)
    inner = (f'<div class="ev-grid"><div><span class="k mono">{L(T("MODEL · VERSION 1", "MODELL · VERSION 1"))}</span><pre class="mono">{esc(v1)}</pre></div>'
             f'<div class="mm-op mono" aria-hidden="true">→</div>'
             f'<div><span class="k mono">{L(T("MODEL · VERSION 2", "MODELL · VERSION 2"))}</span><pre class="mono">{esc(v2)}</pre></div></div>'
             f'<ul class="ev-what mono">{out}</ul>')
    return (f'<figure class="media art-fig ev">{inner}<figcaption class="mono">'
            + L(T("<b>Code is derived, data is not.</b> The author becomes a class of its own. Everything generated simply follows the new model; the books already stored still hold the author as text.",
                  "<b>Code wird abgeleitet, Daten nicht.</b> Der Autor wird eine eigene Klasse. Alles Generierte folgt einfach dem neuen Modell; die schon gespeicherten Bücher enthalten den Autor aber noch als Text."))
            + source_line(src("illustrative"), lang) + '</figcaption></figure>')


def fig_retrofit(lang):
    """Case study: retrofitting MaCoCo step by step. After DGM+21, Fig.8 (p.10). Schematic shares, no numbers on the
    bars: the one measurement is the 2022 snapshot right above the figure (mde.py)."""
    L = lambda x: x[lang]
    steps = [(T("hand-written", "handgeschrieben"), T("application", "Anwendung"), (0, 0, 1.0)),
             (T("+ data &", "+ Daten &"), T("persistence · CD", "Persistenz · CD"), (.02, .30, .68)),
             (T("+ data", "+ Daten-"), T("transfer", "transfer"), (.02, .44, .54)),
             (T("+ validation", "+ Validierung"), "OCL", (.02, .56, .42)),
             (T("+ pages", "+ Seiten"), "GUI-DSL", (.02, .75, .23))]
    H, base, out = 150, 190, ""
    for k, (a, b, (mo, ge, hw)) in enumerate(steps):
        x = 20 + k * 154
        y = base
        for share, cls in ((hw, "rest"), (ge, "gen")):
            h = share * H
            if h:
                out += f'<rect class="{cls}" x="{x}" y="{y - h:.1f}" width="72" height="{h:.1f}"/>'
            y -= h
        if mo:
            out += f'<rect class="modcap" x="{x}" y="{y - 2:.1f}" width="72" height="2"/>'
        out += f'<text x="{x}" y="{base + 18}" class="t">{L(a)}</text><text x="{x}" y="{base + 33}" class="s">{L(b) if isinstance(b, dict) else b}</text>'
        if k < 4:
            out += f'<path class="ln" d="M{x + 80} 116H{x + 146}" marker-end="url(#mdf)"/>'
    svg = f'''<svg class="dia" viewBox="0 0 784 258" role="img" aria-label="{L(T("Five bars: a hand-written application to which generation is added step by step — data and persistence, data transfer, validation, pages. The generated share grows with every step", "Fünf Balken: Eine handgeschriebene Anwendung, der Schritt für Schritt Generierung hinzugefügt wird — Daten und Persistenz, Datentransfer, Validierung, Seiten. Der generierte Anteil wächst mit jedem Schritt"))}">
  {_arrow_defs("mdf")}
  <text x="20" y="16" class="s">{L(T("SCHEMATIC STEPS · share of the code", "SCHEMATISCHE SCHRITTE · Anteil am Code"))}</text>
  {out}
  <rect class="gen" x="20" y="242" width="12" height="12"/><text x="38" y="252" class="s">{L(T("generated", "generiert"))}</text>
  <rect class="rest" x="140" y="242" width="12" height="12"/><text x="158" y="252" class="s">{L(T("hand-written", "handgeschrieben"))}</text>
  <rect class="modcap" x="280" y="247" width="12" height="2"/><text x="298" y="252" class="s">{L(T("models (a thin layer)", "Modelle (eine dünne Schicht)"))}</text>
</svg>'''
    return fig(svg, T("<b>Generation was added to a running system, one aspect at a time.</b> MaCoCo started as a hand-written application; first the data structure and persistence were generated from a class diagram, then the data transfer, then the validation (OCL), then the pages (GUI-DSL). The bars are schematic; the measured state is the snapshot above.",
                      "<b>Generierung kam in ein laufendes System, ein Aspekt nach dem anderen.</b> MaCoCo begann als handgeschriebene Anwendung; zuerst wurden Datenstruktur und Persistenz aus einem Klassendiagramm generiert, dann der Datentransfer, dann die Validierung (OCL), dann die Seiten (GUI-DSL). Die Balken sind schematisch; den gemessenen Stand zeigt der Schnappschuss darüber."),
               lang, source=src("after", "DGM+21", where="Fig. 8"))


# =====================================================================
# Interactive figures (assets/mde.js)
# =====================================================================

def _mini_uml(variant):
    """The running example as a small UML (≤ 340 px) for d1. variant: ok | dangling | dup. Every text carries the
    key of its line in the CD4A text, so pointing at either lights up both."""
    m, mh = _uml(10, 8, 130, "Member", ["String name"], akeys=["member.name"])
    lo, lh = _uml(10, 112, 130, "Loan", ["Date due"], akeys=["loan.due"])
    if variant == "dangling":
        b = ('<rect class="box dashbox" x="200" y="112" width="130" height="44" rx="2"/>'
             '<text x="265" y="139" text-anchor="middle" class="t err">Bok ?</text>')
    else:
        attrs = ["String title", "String title ✗", "boolean available"] if variant == "dup" else _attrs("Book")
        keys = ["book.title", "book.pages", "book.available"]
        b, _ = _uml(200, 112, 130, "Book", attrs, akeys=keys)
        if variant == "dup":
            b = b.replace(f'>{esc("String title ✗")}<', ' class="err">String title ✗<')
    a2 = ('<path class="ln" d="M140 140H196"/><text x="146" y="134" class="s">*</text><text x="192" y="134" text-anchor="end" class="s">1</text>'
          if variant != "dangling" else '<path class="ln err" d="M140 140H196"/><text x="146" y="134" class="s">*</text>')
    return (f'<svg class="dia" viewBox="0 0 340 210" role="img" aria-hidden="true">'
            f'<g data-k="member">{m}</g><g data-k="loan">{lo}</g><g data-k="book">{b}</g>'
            f'<g data-k="a1"><path class="ln" d="M75 {8 + mh}V112"/><text x="81" y="{8 + mh + 14}" class="s">1</text><text x="81" y="108" class="s">*</text></g>'
            f'<g data-k="a2">{a2}</g></svg>')


def _tree(variant, lang):
    """The abstract syntax as an indented tree; keys as in EXAMPLE. variant: ok | dangling | dup."""
    L = lambda x: x[lang]
    A, C, At, As = L(T("Class", "Klasse")), "ClassDiagram", L(T("Attribute", "Attribut")), L(T("Association", "Assoziation"))
    book_attrs = [("book.title", "title : String"), ("book.pages", "pages : int"), ("book.available", "available : boolean")]
    if variant == "dup":
        book_attrs[1] = ("book.pages", "title : String")
    nodes = [(0, "cd", f"{C} Library", ""), (1, "book", f"{A} Book", "")]
    nodes += [(2, k, f"{At} {t}", "err" if variant == "dup" and k == "book.pages" else "") for k, t in book_attrs]
    nodes += [(1, "member", f"{A} Member", ""), (2, "member.name", f"{At} name : String", ""),
              (1, "loan", f"{A} Loan", ""), (2, "loan.due", f"{At} due : Date", ""),
              (1, "a1", f"{As} loans", ""), (2, "a1", "Member [1] → Loan [*]", "ref"),
              (1, "a2", f"{As} book", ""), (2, "a2", "Loan [*] → " + ("Bok ?" if variant == "dangling" else "Book [1]"), "ref err" if variant == "dangling" else "ref")]
    return '<ul class="d1-tree mono">' + "".join(f'<li class="{c}" style="--d:{d}" data-k="{k}">{esc(t)}</li>' for d, k, t, c in nodes) + "</ul>"


def demo_syntax(lang):
    """D1: one model, three views (text, tree, diagram) — and three gates. Four presets, each differing from the
    valid model in exactly one line (checked by _check_d1)."""
    L = lambda x: x[lang]
    variants = [
        ("valid", T("valid", "gültig"), None, None, [1, 1, 1], "ok",
         T("Well-formed: the parser built the tree, every name is known, every rule is kept. Tools may use it.",
           "Wohlgeformt: Der Parser hat den Baum gebaut, jeder Name ist bekannt, jede Regel eingehalten. Werkzeuge dürfen damit arbeiten.")),
        ("semi", T("missing ;", "fehlendes ;"), 7, "    String name", [0, -1, -1], "none",
         T("The parser rejects it: no tree, so no diagram and nothing to check further.",
           "Der Parser lehnt ab: kein Baum, also kein Diagramm und nichts weiter zu prüfen.")),
        ("typo", T("typo", "Tippfehler"), 13, "  association [*] Loan -> (book) Bok [1];", [1, 0, -1], "dangling",
         T("Readable — the grammar was happy, the tree exists. But “Bok” names nothing: the association points into the void.",
           "Lesbar — die Grammatik war zufrieden, der Baum existiert. Aber „Bok“ bezeichnet nichts: Die Assoziation zeigt ins Leere.")),
        ("dup", T("duplicate", "doppelt"), 3, "    String title;", [1, 1, 0], "dup",
         T("Readable, all names known. But Book now has two attributes called title: a rule fails.",
           "Lesbar, alle Namen bekannt. Aber Book hat jetzt zwei Attribute namens title: Eine Regel schlägt fehl.")),
    ]
    data = {"variants": []}
    for vid, label, line, text, gates, uml, msg in variants:
        lines = [l for l, _ in EXAMPLE]
        if line is not None:
            lines[line] = text
        data["variants"].append({"id": vid, "gates": gates, "uml": uml, "msg": L(msg),
                                 "tree": "" if uml == "none" else _tree(uml, lang),
                                 "code": "".join(f'<span class="l{" err" if k == line else ""}" data-k="{EXAMPLE[k][1]}">{esc(t)}</span>' for k, t in enumerate(lines))})
    _check_d1([v["code"] for v in data["variants"]])
    data["none"] = L(T("no tree", "kein Baum"))
    buttons = "".join(f'<button type="button" data-v="{k}" aria-pressed="{"true" if k == 0 else "false"}"{" class=first" if v[0] == "typo" else ""}>{L(v[1])}</button>' for k, v in enumerate(variants))
    gates = [(T("readable?", "lesbar?"), T("parser", "Parser")), (T("names known?", "Namen bekannt?"), T("symbol table", "Symboltabelle")),
             (T("rules kept?", "Regeln eingehalten?"), T("context conditions", "Kontextbedingungen"))]
    strip = "".join(f'<li class="gate ok"><b>{k + 1}</b> {L(a)} <span>{L(b)}</span></li>' for k, (a, b) in enumerate(gates))
    umls = "".join(f'<div class="d1-uml" data-uml="{u}"{"" if u == "ok" else " hidden"}>{_mini_uml(u)}</div>' for u in ("ok", "dangling", "dup"))
    umls += f'<div class="d1-uml d1-none" data-uml="none" hidden><span class="mono">{L(T("no tree, no diagram", "kein Baum, kein Diagramm"))}</span></div>'
    inner = f'''<div class="d1-presets"><span class="k mono">{L(T("TRY", "PROBIEREN"))}</span><div class="chips mono" role="group" aria-label="{L(T("Variants of the model", "Varianten des Modells"))}">{buttons}</div></div>
<ol class="d1-gates mono">{strip}</ol>
<div class="d1-grid">
  <div><span class="k mono">{L(T("TEXT · what you type", "TEXT · was Sie tippen"))}</span><pre class="mono d1-code">{data["variants"][0]["code"]}</pre></div>
  <div class="d1-right">
    <div><span class="k mono">{L(T("ABSTRACT SYNTAX · what the tool sees", "ABSTRAKTE SYNTAX · was das Werkzeug sieht"))}</span><div class="d1-treebox">{data["variants"][0]["tree"]}</div></div>
    <div><span class="k mono">{L(T("DIAGRAM · what you draw", "DIAGRAMM · was Sie zeichnen"))}</span>{umls}</div>
  </div>
</div>
<p class="d1-msg mono" aria-live="polite">{L(variants[0][6])}</p>'''
    return demo("d1", data, inner, T(
        "<b>The picture is not the model.</b> Text and diagram are two ways to show one tree; point at a line, a node or a box to find it in the other two. Choose a variant: each differs from the valid model in one line — and fails at a different gate. (In MontiCore, “cannot be resolved” is itself reported by a context condition that asks the symbol table; the gates are separated here for clarity.)",
        "<b>Das Bild ist nicht das Modell.</b> Text und Diagramm sind zwei Arten, einen Baum zu zeigen; zeigen Sie auf eine Zeile, einen Knoten oder einen Kasten, um ihn in den anderen beiden zu finden. Wählen Sie eine Variante: Jede unterscheidet sich vom gültigen Modell in einer Zeile — und scheitert an einer anderen Stelle. (In MontiCore meldet eine Kontextbedingung, die die Symboltabelle befragt, selbst das „kann nicht aufgelöst werden“; die Stufen sind hier der Klarheit halber getrennt.)"),
        lang, source=src("after", HB, where="Figs. 10.1/10.2"))


def _check_d1(codes):
    lines = [re.findall(r'<span[^>]*>(.*?)</span>', c) for c in codes]
    for v in lines[1:]:
        assert len(v) == len(lines[0]) and sum(a != b for a, b in zip(v, lines[0])) == 1


def _code(lines, new=()):
    """A code block as HTML lines; indices in `new` are marked as new."""
    return "".join(f'<span class="l{" new" if k in new else ""}">{esc(t) or " "}</span>' for k, t in enumerate(lines))


def demo_top(lang):
    """D2: edit the generated file, or extend it (TOP mechanism). Two lanes, one stepper. The right lane writes its
    hand-written file and regenerates in the same step, so it is never shown worse off than the left one."""
    L = lambda x: x[lang]
    gen = ["// generated — do not edit", "public class Loan {", "  Date due;", "  Date getDue() {…}", "}"]
    gen_top = ["// generated", "public abstract class LoanTOP {", "  Date due;", "  Date getDue() {…}", "}"]
    own = "  boolean isOverdue() {…}"
    hw = ["// your code/ · hand-written", "public class Loan", "    extends LoanTOP {", own, "}"]
    plus = "  int renewals;"

    def file(path, lines, new=(), cls=""):
        return f'<div class="d2-file {cls}"><span class="mono d2-path">{path}</span><pre class="mono">{_code(lines, new)}</pre></div>'
    steps = [
        (T("Generate", "Generieren"),
         file("out/Loan.java", gen), T("The generator writes Loan.java.", "Der Generator schreibt Loan.java."), "",
         file("out/Loan.java", gen), T("Same start.", "Derselbe Anfang."), ""),
        (T("Add your own method", "Eigene Methode ergänzen"),
         file("out/Loan.java", gen[:4] + [own, "}"], new=(4,)), T("You type isOverdue() into the generated file. It compiles.", "Sie tippen isOverdue() in die generierte Datei. Es kompiliert."), "",
         file("out/LoanTOP.java", gen_top, new=(1,)) + file("code/Loan.java", hw, new=(1, 2, 3), cls="hw"),
         T("You write code/Loan.java, which extends LoanTOP, and regenerate once: the generator finds your file and names its own class LoanTOP. It compiles.",
           "Sie schreiben code/Loan.java, das LoanTOP erweitert, und generieren einmal neu: Der Generator findet Ihre Datei und nennt seine eigene Klasse LoanTOP. Es kompiliert."), "good"),
        (T("Regenerate (model unchanged)", "Neu generieren (Modell unverändert)"),
         file("out/Loan.java", gen[:4] + [own, "}"], cls="lost"), T("The file is overwritten. Your method is gone — and the model did not even change.", "Die Datei wird überschrieben. Ihre Methode ist weg — dabei hat sich das Modell nicht einmal geändert."), "bad",
         file("out/LoanTOP.java", gen_top) + file("code/Loan.java", hw, cls="hw"),
         T("Nothing to see: code/ is never touched, your method stays.", "Nichts passiert: code/ wird nie angefasst, Ihre Methode bleibt."), "good"),
        (T("Model: + int renewals; → regenerate", "Modell: + int renewals; → neu generieren"),
         file("out/Loan.java", gen[:3] + [plus, gen[3], "}"], new=(3,)), T("renewals appears; your method is still gone.", "renewals erscheint; Ihre Methode bleibt verschwunden."), "bad",
         file("out/LoanTOP.java", gen_top[:3] + [plus, gen_top[3], "}"], new=(3,)) + file("code/Loan.java", hw, cls="hw"),
         T("LoanTOP gains renewals; your class is untouched. Regenerating is always safe.", "LoanTOP bekommt renewals; Ihre Klasse bleibt unberührt. Neu generieren ist immer sicher."), "good"),
    ]
    data = {"steps": [{"title": L(t), "a": a, "an": L(an), "ac": ac, "b": b, "bn": L(bn), "bc": bc} for t, a, an, ac, b, bn, bc in steps]}
    s0 = data["steps"][0]
    inner = f'''<div class="d2-grid">
  <div class="d2-lane" data-lane="a"><span class="k mono">{L(T("EDIT THE GENERATED CODE", "GENERIERTEN CODE BEARBEITEN"))}</span><div class="d2-files">{s0["a"]}</div><p class="d2-note mono">{s0["an"]}</p></div>
  <div class="d2-lane" data-lane="b"><span class="k mono">{L(T("EXTEND IT (TOP MECHANISM)", "ERWEITERN (TOP-MECHANISMUS)"))}</span><div class="d2-files">{s0["b"]}</div><p class="d2-note mono">{s0["bn"]}</p></div>
</div>{controls(lang)}'''
    return demo("d2", data, inner, T(
        "<b>Never edit generated code — extend it.</b> Left, a method typed into the generated file is lost at the next generation, even without any change to the model. Right, the TOP mechanism: when a hand-written class Loan exists, the generator emits LoanTOP instead, and Loan extends it. The price: after adding a hand-written file you regenerate once.",
        "<b>Generierten Code nie bearbeiten — erweitern.</b> Links geht eine in die generierte Datei getippte Methode bei der nächsten Generierung verloren, sogar ohne jede Modelländerung. Rechts der TOP-Mechanismus: Gibt es eine handgeschriebene Klasse Loan, erzeugt der Generator stattdessen LoanTOP, und Loan erweitert sie. Der Preis: Nach dem Anlegen einer handgeschriebenen Datei generiert man einmal neu."),
        lang, source=src("after", HB, where="Fig. 14.5"))


# D3: one line in the model, six files change. Illustrative, simplified — not literal MontiGem output.
D3_BASE = [("String", "title")]
D3_ADD = [("String", "isbn"), ("boolean", "available"), ("int", "pages")]
D3_SQL = {"String": "VARCHAR(255)", "int": "INT", "boolean": "BOOLEAN"}
D3_TS = {"String": "string", "int": "number", "boolean": "boolean"}


def _d3_files(attrs):
    cap = lambda s: s[0].upper() + s[1:]
    getter = lambda t, n: f"  public {t} {'is' if t == 'boolean' else 'get'}{cap(n)}() {{ return {n}; }}"
    widget = lambda t, n: (f'  <label><input type="checkbox" name="{n}"> {n}</label>' if t == "boolean"
                           else f'  <label>{n} <input type="{"number" if t == "int" else "text"}" name="{n}"></label>')
    return {
        "table": ["CREATE TABLE book (", "  id BIGINT PRIMARY KEY"] + [f"  , {n} {D3_SQL[t]}" for t, n in attrs] + [");"],
        "data": ["@Entity", "public class Book {"] + [f"  private {t} {n};" for t, n in attrs] + [getter(t, n) for t, n in attrs] + ["}"],
        "command": ["public class BookUpdate extends Command {", "  private long id;"] + [f"  private {t} {n};" for t, n in attrs] + ["}"],
        "dto": ["public class BookDTO extends DTO {", "  private long id;"] + [f"  private {t} {n};" for t, n in attrs] + ["}"],
        "ts": ["export interface Book {", "  id: number;"] + [f"  {n}: {D3_TS[t]};" for t, n in attrs] + ["}"],
        "form": ['<form class="book">'] + [widget(t, n) for t, n in attrs] + ["  <button>save</button>", "</form>"],
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
    are found by comparing with the previous state, so the counter is honest by construction (_check_d3). Each
    chip shows its new line, so all six changes are visible at once."""
    L = lambda x: x[lang]
    tiers = [("table", T("Table", "Tabelle"), T("rows on disk", "Zeilen auf der Platte"), "db"),
             ("data", T("Data class", "Datenklasse"), T("the server's object", "das Objekt im Server"), "server"),
             ("command", T("API action", "API-Aktion"), T("“Command”: one call the browser may make", "„Command“: ein Aufruf, den der Browser machen darf"), "server"),
             ("dto", "DTO", T("the package between server and browser", "das Paket zwischen Server und Browser"), "server"),
             ("ts", T("TS model", "TS-Modell"), T("the browser's copy", "die Kopie im Browser"), "browser"),
             ("form", T("Form", "Formular"), T("what the user sees", "was die Nutzerin sieht"), "browser")]
    states, prev = [], None
    for k in range(len(D3_ADD) + 1):
        attrs = D3_BASE + D3_ADD[:k]
        files = _d3_files(attrs)
        new_attr = D3_ADD[k - 1][1] if k else None
        st = {"model": _code(["class Book {"] + [f"  {t} {n};" for t, n in attrs] + ["}"], new=(len(attrs),) if k else ()),
              "files": {}, "changed": {}, "first": {}}
        for key, lines in files.items():
            changed = [i for i, l in enumerate(lines) if prev is not None and l not in prev[key]]
            st["files"][key] = _code(lines, new=changed)
            st["changed"][key] = len(changed)
            st["first"][key] = lines[changed[0]].strip() if changed else ""
        st["form"] = _form_html(attrs, new_attr)
        st["n"], st["m"] = sum(st["changed"].values()), sum(1 for v in st["changed"].values() if v)
        states.append(st)
        prev = files
    _check_d3(states)
    data = {"states": states, "templates": {k: "".join(f'<span class="l">{_hole(l)}</span>' for l in v) for k, v in D3_TEMPLATES.items()},
            "words": {k: L(v) for k, v in dict(
                count=T("1 model line → {n} lines in {m} files", "1 Modellzeile → {n} Zeilen in {m} Dateien"),
                start=T("every file on the right is generated from this", "jede Datei rechts wird hieraus generiert"),
                full=T("all three added", "alle drei ergänzt"),
                tpl=T("The template does not change — only the model does. The holes are filled from it.", "Das Template ändert sich nicht — nur das Modell. Die Lücken werden daraus gefüllt.")).items()}}
    chip = lambda key, name, sub: (f'<button type="button" class="d3-chip" data-f="{key}" aria-pressed="{"true" if key == "data" else "false"}">'
                                   f'<b>{L(name) if isinstance(name, dict) else name}</b><span>{L(sub)}</span><code class="d3-new"></code><em class="d3-badge"></em></button>')
    cols = [("db", T("DATABASE", "DATENBANK")), ("server", "SERVER"), ("browser", "BROWSER")]
    tier_html = "".join(f'<div class="d3-tier"><span class="k mono">{L(n) if isinstance(n, dict) else n}</span>'
                        + "".join(chip(k, nm, sub) for k, nm, sub, t in tiers if t == tid) + '</div>' for tid, n in cols)
    inner = f'''<div class="d3-grid">
  <div class="d3-model"><span class="k mono">{L(T("THE MODEL · CD4A", "DAS MODELL · CD4A"))}</span><pre class="mono">{states[0]["model"]}</pre>
    <div class="d3-ctrl mono"><button type="button" class="d3-add">+ {L(T("attribute", "Attribut"))}</button><button type="button" class="d3-reset">{L(T("reset", "zurücksetzen"))}</button></div>
    <p class="d3-count mono" aria-live="polite">{data["words"]["start"]}</p></div>
  <div class="d3-out">
    <div class="d3-tiers">{tier_html}</div>
    <div class="d3-view chips mono" role="group"><button type="button" data-view="code" aria-pressed="true">code</button><button type="button" data-view="template" aria-pressed="false">template</button></div>
    <div class="d3-panel"><pre class="mono d3-code">{states[0]["files"]["data"]}</pre>
    <div class="d3-form-wrap" hidden></div>
    <p class="d3-tplnote mono" hidden></p></div>
  </div>
</div>
<p class="d3-rte mono"><span>{L(T("not generated:", "nicht generiert:"))}</span> <i>{L(T("runtime environment (hand-built once)", "Laufzeitumgebung (einmal von Hand gebaut)"))}</i> · <i>{L(T("libraries (Hibernate, Angular)", "Bibliotheken (Hibernate, Angular)"))}</i></p>'''
    return demo("d3", data, inner, T(
        "<b>One added attribute updates every tier — nothing can drift apart.</b> Click <i>+ attribute</i>: every file shows its new line at once; pick one to read it whole. Switch to <i>template</i> to see where the code comes from. Simplified — MontiGem generates more per class (builder, DAO, validator, a loader that fills the transfer objects).",
        "<b>Ein zusätzliches Attribut ändert jede Schicht — nichts kann auseinanderlaufen.</b> Klicken Sie auf <i>+ Attribut</i>: Jede Datei zeigt sofort ihre neue Zeile; wählen Sie eine, um sie ganz zu lesen. Unter <i>template</i> sehen Sie, woher der Code kommt. Vereinfacht — MontiGem generiert pro Klasse mehr (Builder, DAO, Validator, einen Loader, der die Transferobjekte füllt)."),
        lang, source=src("illustrative"))


def _check_d3(states):
    for a, b in zip(states, states[1:]):
        for key in b["files"]:
            na = len(re.findall(r'<span class="l', a["files"][key]))
            nb = len(re.findall(r'<span class="l', b["files"][key]))
            assert nb - na == b["changed"][key] and b["changed"][key] > 0, key


# D4: CD2GUI — pages nobody drew. Fictional data throughout.
D4_ROWS = {
    "Book": [["Field Notes", "212", "yes"], ["Rivers", "96", "no"], ["Small Atlas", "48", "yes"]],
    "Member": [["Alice"], ["Bob"]],
    "Loan": [["2026-11-03"], ["2026-11-17"]],
}
D4_LOANS_OF = {"Alice": [["2026-11-03", "Rivers"]]}       # Member → loans (Member 1 → * Loan), Loan → book (* → 1)


def demo_cd2gui(lang):
    """D4: pick a class, see the dashboard / overview / details pages CD2GUI derives, and the GUI-model tree behind
    them; on Member → details, a hand-written delta adds a row of buttons. Book is selected from the start."""
    L = lambda x: x[lang]
    W = {k: L(v) for k, v in dict(details=T("details", "Details"), overview=T("overview", "Übersicht"), dash=T("Dashboard", "Dashboard"),
                                  inspect=T("inspect", "ansehen"), one=T("object", "Objekt"), many=T("objects", "Objekte"),
                                  key=T("Key", "Schlüssel"), value=T("Value", "Wert"), loans=T("Loans", "Ausleihen"), book=T("book", "Buch"),
                                  newloan=T("New loan", "Neue Ausleihe"), remind=T("Send reminder", "Erinnerung senden")).items()}

    def table(head, rows, link=True):
        th = "".join(f"<th>{h}</th>" for h in head) + ("<th></th>" if link else "")
        tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + (f'<td><span class="pill">{W["inspect"]}</span></td>' if link else "") + "</tr>" for r in rows)
        return f'<table><tr>{th}</tr>{tr}</table>'

    def card(title, body, cls=""):
        return f'<div class="gp-card {cls}"><div class="gp-head">{title}</div><div class="gp-body">{body}</div></div>'

    def tree(nodes):
        return '<ul class="d4-tree mono">' + "".join(f'<li style="--d:{d}"{f" class={c!r}" if c else ""}>{esc(t)}</li>' for d, t, c in nodes) + "</ul>"

    pages = {}
    count = lambda n: f'{n} {W["one"] if n == 1 else W["many"]}'
    dash = "".join(card(c, f'<p>{count(len(D4_ROWS[c]))}</p><span class="pill">{W["overview"]}</span>') for c in CLASSES)
    pages["dashboard"] = {"url": "/generated/dashboard", "html": f'<div class="gp-cards">{dash}</div>',
                          "tree": tree([(0, "«Page» Dashboard", "")] + [(1, f"Card {c}", "") for c in CLASSES])}
    for c in CLASSES:
        lc, cols, rows = c.lower(), [n for _, n in CLASSES[c]], D4_ROWS[c]
        pages[f"{c}/overview"] = {"url": f"/generated/{lc}/overview", "html": card(f"{c} {W['overview']}", table(cols, rows)),
                                  "tree": tree([(0, f"«Page» {c}Overview", ""), (1, "C1: card", ""), (2, "L1: label", ""), (2, "T1: datatable", "")])}
        kv_rows = [[n, r] for n, r in zip(cols, rows[0])]
        if c == "Loan":                                            # a reference to one Book: a link to its page
            kv_rows.append([W["book"], '<a class="gp-link">Rivers</a>'])
        kv = table([W["key"], W["value"]], kv_rows, link=False)
        nodes = [(0, f"«Page» {c}Details", ""), (1, "C1: card", ""), (2, "L1: label", ""), (2, f"T1: datatable “{c} attributes”", "")]
        body = kv
        if c == "Member":                                          # an association to many: a sub-table
            body += f'<h5>{W["loans"]}</h5>' + table(["due", "book"], D4_LOANS_OF["Alice"])
            nodes.append((2, "T2: datatable “Member loans”", ""))
        pages[f"{c}/details"] = {"url": f"/generated/{lc}/details/1", "html": card(f"{c} {W['details']}", body), "tree": tree(nodes)}
    kv = table([W["key"], W["value"]], [["name", "Alice"]], link=False)
    buttons = f'<div class="gp-row new"><span class="btn">{W["newloan"]}</span><span class="btn">{W["remind"]}</span></div>'
    pages["Member/details+delta"] = {
        "url": "/generated/member/details/1",
        "html": card(f"Member {W['details']}", buttons + kv + f'<h5>{W["loans"]}</h5>' + table(["due", "book"], D4_LOANS_OF["Alice"])),
        "tree": tree([(0, "«Page» MemberDetails", ""), (1, "C1: card", ""), (2, "L1: label", ""), (2, "R: row  (add_after @L1)", "new"),
                      (3, f"button ‘{W['newloan']}’ · button ‘{W['remind']}’", "new"), (2, "T1: datatable “Member attributes”", ""), (2, "T2: datatable “Member loans”", "")])}
    data = {"pages": pages, "start": "Book"}

    def cls_card(c):
        attrs = "".join(f"<span>{n} : {t}</span>" for t, n in CLASSES[c])
        return f'<button type="button" class="d4-cls" data-c="{c}" aria-pressed="{"true" if c == "Book" else "false"}"><b>{c}</b>{attrs}</button>'

    def assoc(a, label, b):
        return f'<span class="d4-as mono" aria-hidden="true"><i>{a}</i><em>{label}</em><i>{b}</i></span>'
    picker = (cls_card("Member") + assoc("1", L(T("has", "hat")), "*") + cls_card("Loan")
              + assoc("*", L(T("is for", "gilt für")), "1") + cls_card("Book"))
    p0 = pages["dashboard"]
    delta = f"add_after @L1 [\n  row {{\n    button '{W['newloan']}'\n    button '{W['remind']}'\n  }}\n]"
    inner = f'''<div class="d4-grid">
  <div class="d4-pick"><span class="k mono">{L(T("THE CLASS DIAGRAM · pick a class", "DAS KLASSENDIAGRAMM · Klasse wählen"))}</span><div class="d4-cd" role="group" aria-label="{L(T("Choose a class", "Klasse wählen"))}">{picker}</div>
    <label class="d4-delta mono"><input type="checkbox" disabled> {L(T("hand-written delta (Member → details)", "handgeschriebenes Delta (Member → Details)"))}</label>
    <pre class="mono d4-deltacode">{esc(delta)}</pre></div>
  <div class="d4-browser"><div class="d4-bar mono"><span class="d4-url" aria-live="polite">{p0["url"]}</span></div>
    <div class="d4-tabs chips mono" role="group"><button type="button" data-t="dashboard" aria-pressed="true">{W["dash"]}</button><button type="button" data-t="overview" aria-pressed="false">{L(T("Overview", "Übersicht"))}</button><button type="button" data-t="details" aria-pressed="false" class="first">{L(T("Details", "Details"))}</button></div>
    <div class="d4-page">{p0["html"]}</div></div>
  <details class="d4-treebox" open><summary class="k mono">{L(T("THE GUI MODEL BEHIND IT (a tree)", "DAS GUI-MODELL DAHINTER (ein Baum)"))}</summary><div class="d4-tree-wrap">{p0["tree"]}</div></details>
</div>'''
    return demo("d4", data, inner, T(
        "<b>Pages nobody drew.</b> From three classes, CD2GUI derives one dashboard and, per class, an overview and a details page — as GUI models, which MontiGem then turns into code. Pick a class and a page; the tree shows the GUI model behind it. On Member → details, switch on the hand-written delta: it adds a row of buttons. Because the change lives in a small model and not in generated HTML, it is re-applied on every regeneration. The delta syntax is simplified.",
        "<b>Seiten, die niemand gezeichnet hat.</b> Aus drei Klassen leitet CD2GUI ein Dashboard und je Klasse eine Übersichts- und eine Detailseite ab — als GUI-Modelle, aus denen MontiGem dann Code macht. Wählen Sie eine Klasse und eine Seite; der Baum zeigt das GUI-Modell dahinter. Bei Member → Details schalten Sie das handgeschriebene Delta ein: Es fügt eine Zeile mit Knöpfen hinzu. Weil die Änderung in einem kleinen Modell steckt und nicht im generierten HTML, wird sie bei jeder Neugenerierung erneut angewendet. Die Delta-Syntax ist vereinfacht."),
        lang, source=src("after", "GMN+20", where="Figs. 5–9", note=T("fictional data", "fiktive Daten")))


def mapping_table(lang):
    """Next to D4: how CD2GUI maps class-diagram elements to page components (Net24 Listing 6.3, §6.6; GMN+20 p.8)."""
    L = lambda x: x[lang]
    rows = [(T("Boolean attribute", "Boolean-Attribut"), T("checkbox", "Checkbox")),
            (T("text or number attribute", "Text- oder Zahlattribut"), T("text field", "Textfeld")),
            (T("enum", "Enum"), T("drop-down", "Auswahlliste")),
            (T("reference to a class with a details page", "Verweis auf eine Klasse mit Detailseite"), T("link to that page (Loan → its book)", "Link auf diese Seite (Loan → sein Buch)")),
            (T("association to many", "Assoziation zu vielen"), T("sub-table of linked objects (Member → its loans)", "Untertabelle verknüpfter Objekte (Member → seine Ausleihen)")),
            ("«key_attribute» · «invisible» · «hide_in_overview»", T("which columns show up (default: the first 8)", "welche Spalten erscheinen (Standard: die ersten 8)"))]
    body = "".join(f"<tr><td>{L(a) if isinstance(a, dict) else a}</td><td>{L(b)}</td></tr>" for a, b in rows)
    return (f'<figure class="media art-fig"><div class="tbl-wrap"><table class="tbl mono"><tr><th>{L(T("in the class diagram", "im Klassendiagramm"))}</th><th>{L(T("on the page", "auf der Seite"))}</th></tr>{body}</table></div>'
            f'<figcaption class="mono">{L(T("How CD2GUI maps the class diagram to page components; stereotypes in the class diagram steer the defaults.", "Wie CD2GUI das Klassendiagramm auf Seitenbausteine abbildet; Stereotypen im Klassendiagramm steuern die Voreinstellungen."))}'
            f'{source_line(src("from", "Net24", where="ch. 6"), lang)}</figcaption></figure>')


def fig_three_languages(lang):
    """F6: three languages, one screen (CSS :has() hover). After GLM+24 Fig.9 and BGK+24 Listing 2. Fictional data."""
    L = lambda x: x[lang]
    gui = 'webpage Books(all Book b) {\n  card {\n    head { label "Books" }\n    body {\n      datatable { rows <b {\n        column "Title", title\n        column "Pages", pages\n}}}}}'
    codes = [("data", T("DATA", "DATEN"), "CD4A", "class Book {\n  String title;\n  int pages;\n}"),
             ("page", T("PAGE", "SEITE"), "GUI-DSL", gui),
             ("rule", T("RULE", "REGEL"), "OCL/P", "context Book inv atLeastOnePage:\n  pages > 0;")]
    boxes = "".join(f'<div class="f6-code" data-k="{k}" tabindex="0"><span class="k mono">{L(a)} · {b}</span><pre class="mono">{esc(c)}</pre></div>' for k, a, b, c in codes)
    mock = f'''<div class="f6-page" aria-hidden="true">
  <div class="gp-card f6-reg" data-k="page"><div class="gp-head">{L(T("Books", "Bücher"))}</div><div class="gp-body">
    <table class="f6-reg" data-k="data"><tr><th>Title</th><th>Pages</th></tr><tr><td>Field Notes</td><td>212</td></tr><tr><td>Rivers</td><td>96</td></tr></table>
    <div class="f6-edit f6-reg" data-k="rule"><label>Pages <input type="text" value="0" disabled></label><span>{L(T("A book needs at least one page", "Ein Buch braucht mindestens eine Seite"))}</span></div>
  </div></div></div>'''
    inner = f'<div class="f6">{mock}<div class="f6-codes">{boxes}</div></div>'
    return (f'<figure class="media art-fig">{inner}<figcaption class="mono">{L(T("<b>Three languages, one screen.</b> The data model says what a Book is, the page model how books are listed, the rule what a valid book is — and the generated page enforces it in the browser and on the server. Point at a model to see its part of the page.", "<b>Drei Sprachen, ein Bildschirm.</b> Das Datenmodell sagt, was ein Book ist, das Seitenmodell, wie Bücher aufgelistet werden, die Regel, was ein gültiges Buch ist — und die generierte Seite setzt das im Browser und auf dem Server durch. Zeigen Sie auf ein Modell, um seinen Teil der Seite zu sehen."))}'
            f'{source_line(src("after", "GLM+24", where="Fig. 9", note=T("fictional data", "fiktive Daten")), lang)}</figcaption></figure>')


def fig_chain(lang):
    """F9: from a sentence to an application, the toolchain of Net24 (Fig.2.4): ① LLM → ② CD2GUI → ③ MontiGem.
    The numbers are links; pointing at one dims what it does not touch (CSS :has())."""
    L = lambda x: x[lang]
    model = "class Book {\n  String title;\n  int pages; }\nclass Member {\n  String name; }\nclass Loan {\n  Date due; }\nassociation\nMember -> Loan [*];\nassociation\nLoan -> Book [1];"
    panes = [("1", T("INFORMAL DESCRIPTION", "INFORMELLE BESCHREIBUNG"), f'<p class="f9-bubble">{L(T("“Create a model for a library that lends books to its members.”", "„Erstelle ein Modell für eine Bibliothek, die Bücher an ihre Mitglieder verleiht.“"))}</p>', T("domain expert", "Domänenexpertin")),
             ("1 2", T("DOMAIN MODEL", "DOMÄNENMODELL"), f'<pre class="mono">{esc(model)}</pre>', T("modeller · may merge own models", "Modelliererin · kann eigene Modelle einfügen")),
             ("2 3", T("APPLICATION MODELS", "ANWENDUNGSMODELLE"), '<p class="mono">BookOverview.gui<br>BookDetails.gui<br>MemberDetails.gui<br>…<br>Dashboard.gui</p>', T("pages, rules, roles", "Seiten, Regeln, Rollen")),
             ("3", T("GENERATED APPLICATION", "GENERIERTE ANWENDUNG"), f'<p class="f9-stack mono"><span class="g">{L(T("generated", "generiert"))}</span><span>{L(T("runtime environment", "Laufzeitumgebung"))}</span><span class="h">{L(T("hand-written (TOP)", "handgeschrieben (TOP)"))}</span></p>', T("programmer", "Programmiererin"))]
    steps = [("1", "LLM", "research-ai4se.html#models"), ("2", "CD2GUI", "#cd2gui"), ("3", "MontiGem", "#whygen")]
    out = ""
    for k, (ks, head, body, who) in enumerate(panes):
        out += f'<div class="f9-pane" data-k="{ks}"><span class="k mono">{L(head)}</span>{body}<span class="f9-who mono">{L(who)}</span></div>'
        if k < 3:
            n, name, href = steps[k]
            out += f'<a class="f9-step mono" data-k="{n}" href="{href}"><b>{"①②③"[k]}</b>{name}</a>'
    return (f'<figure class="media art-fig"><div class="f9">{out}</div><figcaption class="mono">{L(T("<b>AI only in step 1.</b> An LLM turns the description into a class diagram; everything after the model — CD2GUI and MontiGem — is deterministic, repeatable and checkable. Point at a step to see what it touches; click it to read more.", "<b>KI nur in Schritt 1.</b> Ein LLM macht aus der Beschreibung ein Klassendiagramm; alles nach dem Modell — CD2GUI und MontiGem — ist deterministisch, wiederholbar und prüfbar. Zeigen Sie auf einen Schritt, um zu sehen, was er berührt; ein Klick führt zur Erklärung."))}'
            f'{source_line(src("after", "Net24", where="Fig. 2.4"), lang)}</figcaption></figure>')
