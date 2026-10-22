"""
The first figure of the MDE article (research-mde.html): the generator, five levels deep.
  1  a model → the generator → an application
  2  several models → the generator → client, server, database
  3  inside: input ASTs → transformations → output ASTs → generated files (form, DTO, data class)
  4  + the grammars the parsers come from, the templates the code comes from        (after [Net24], Fig. 7.1)
  5  full detail: the MontiGem back-end data-structure generator        (after the MontiGem developer documentation)

The morph appears three times in the article (VIEWS): levels 1–2 in the intro, 2–4 in the generator section, level 5
alone in a curious box in chapter 03. Levels 2–5 share an aspect ratio; level 1 is flatter, so the stage grows when
leaving it (the controls sit above the picture and do not move). Every element has a box per level in that level's
frame (or none: it fades). The three containers — models, generator, application — exist on every level and only
move and grow. assets/mde.js (d0) tweens between the levels; this module renders the start level as the static picture.
"""
import html
import json

from ai4se import T, cite
from project_content import _arrow_defs

FRAMES = {1: (760, 250), 2: (740, 398), 3: (920, 495), 4: (1000, 538), 5: (1100, 592)}   # 2–5 ≈ 13 : 7; level 1 is flatter
LEVELS = (1, 2, 3, 4, 5)
FADED = .42                     # level 5: the GUI lane steps back, the back end is in focus


def _el(id_, kind, geo, t="", s="", cls="", x=None):
    """kind: zone (label top left) · box · doc · cyl · chip · label (text only). geo: {level: (x, y, w, h[, opacity])}.
    t / s: title and subtitle — a string, a T pair, or {level: …} (carried forward to later levels)."""
    return {"id": id_, "kind": kind, "geo": geo, "t": t, "s": s, "cls": cls, "x": x}


def _per_level(v, lang):
    """Resolve a text spec to five strings, one per level."""
    def one(u):
        return u[lang] if isinstance(u, dict) and "en" in u else u
    if isinstance(v, dict) and "en" not in v:
        out, cur = [], ""
        for lv in LEVELS:
            cur = one(v[lv]) if lv in v else cur
            out.append(cur)
        return out
    return [one(v)] * len(LEVELS)


# ---------------------------------------------------------------------
# The transformations panel of level 5 (DS-Trafo grows into it): a selection of the creators, by purpose
# ---------------------------------------------------------------------
TRAFOS = [
    (12, [("pre-transformations", ["DefaultVisibilitySetter", "CollectionTypesWrapper", "TypesConverter", "RenameDomainTrafo"]),
          ("data classes", ["DataClassTrafo", "AnnotationTrafo", "AccessMethodTrafo", "PackageTrafo"])]),
    (192, [("DTOs · DAOs", ["DaoCreator", "FullDtoCreator", "DTOListCreator"]),
           ("commands", ["CommandCreateCreator", "CommandGetAllCreator", "CommandDeleteCreator"]),
           ("tests", ["TestClassCreator", "DummyTestClassCreator"])]),
]


def _trafo_list():
    out = ""
    for x, groups in TRAFOS:
        y = 42
        for head, items in groups:
            out += f'<text x="{x}" y="{y}" class="s a">{head}</text>'
            y += 15
            for it in items:
                out += f'<text x="{x}" y="{y}" class="s">{it}</text>'
                y += 13
            y += 8
    out += '<text x="192" y="226" class="s">…</text>'
    return out


def elements():
    F = FADED
    P = T("Parser", "Parser")
    return [
        # ---------------- the three containers ----------------
        _el("zM", "zone", {1: (100, 26, 140, 170), 2: (16, 40, 150, 318), 3: (16, 40, 140, 415), 4: (16, 120, 120, 370), 5: (12, 40, 106, 540)},
            t={1: T("MODEL", "MODELL"), 2: T("MODELS", "MODELLE")}),
        _el("zG", "zone", {1: (300, 26, 160, 170), 2: (226, 40, 200, 318), 3: (176, 40, 372, 415), 4: (152, 20, 592, 500), 5: (130, 12, 770, 568)},
            t={1: "", 3: T("GENERATOR · MontiGem", "GENERATOR · MontiGem")}),
        _el("gT", "label", {1: (300, 26, 160, 170), 2: (226, 40, 200, 318)}, t="Generator", s="MontiGem"),
        _el("zA", "zone", {1: (520, 26, 140, 170), 2: (526, 40, 198, 318), 3: (668, 40, 236, 415), 4: (842, 120, 142, 370), 5: (1000, 40, 92, 540)},
            t={1: "", 2: T("APPLICATION", "ANWENDUNG")}),
        _el("aT", "label", {1: (520, 26, 140, 170)}, t=T("Application", "Anwendung"), s=T("web, running", "Web, laufend")),

        # ---------------- models ----------------
        _el("cd", "doc", {1: (120, 70, 100, 82), 2: (36, 167, 110, 64), 3: (36, 212, 100, 60), 4: (28, 276, 96, 56), 5: (18, 224, 88, 40)},
            t={1: T("Class diagram", "Klassendiagramm"), 5: "Domain CD"}, s={1: "Library.cd", 5: ""}, cls="hl"),
        _el("gui", "doc", {2: (36, 70, 110, 64), 3: (36, 92, 100, 60), 4: (28, 166, 96, 56), 5: (18, 526, 88, 44, F)},
            t=T("GUI model", "GUI-Modell"), s={2: "Books.gui", 4: ""}),
        _el("ocl", "doc", {2: (36, 264, 110, 64), 3: (36, 332, 100, 60), 4: (28, 386, 96, 56), 5: (18, 176, 88, 40)},
            t="OCL", s={2: T("constraints", "Bedingungen"), 4: ""}),
        _el("vcd", "doc", {5: (18, 272, 88, 40)}, t="View CD"),
        _el("tag", "doc", {5: (18, 320, 88, 40)}, t="Tags"),

        # ---------------- level 4/5: grammars, control scripts, workflow, loader ----------------
        _el("gz", "zone", {4: (168, 44, 236, 84), 5: (144, 374, 200, 62)}, t=T("GRAMMARS · MontiCore", "GRAMMATIKEN · MontiCore"), cls="line"),
        _el("gGui", "chip", {4: (180, 82, 64, 28), 5: (152, 402, 56, 24)}, t={4: "GUI.mc4", 5: "GUI"}),
        _el("gCd", "chip", {4: (252, 82, 70, 28), 5: (214, 402, 60, 24)}, t={4: "CD4A.mc4", 5: "CD4A"}),
        _el("gOcl", "chip", {4: (330, 82, 64, 28), 5: (280, 402, 56, 24)}, t={4: "OCL.mc4", 5: "OCL"}),
        _el("ctl", "zone", {5: (144, 36, 250, 66)}, t=T("CONTROL SCRIPTS · Groovy", "STEUERSKRIPTE · Groovy"), cls="line"),
        *[_el(f"c{k}", "chip", {5: (150 + 61 * k, 66, 60, 24)}, t=n) for k, n in enumerate(["aggregate", "domain", "tag", "tagging"])],
        _el("wf", "box", {5: (144, 112, 250, 40)}, t=T("Workflow execution", "Workflow-Ausführung")),
        _el("ld", "zone", {5: (144, 166, 100, 196)}, t=T("MODEL LOADER", "MODELL-LADER"), cls="line"),

        # ---------------- parsers and input ASTs ----------------
        _el("pGui", "box", {4: (168, 170, 80, 48), 5: (144, 542, 74, 30, F)}, t=P, s={4: "GUI", 5: ""}),
        _el("pCd", "box", {4: (168, 280, 80, 48), 5: (152, 246, 84, 40)}, t=P, s="CD4A"),
        _el("pOcl", "box", {4: (168, 390, 80, 48), 5: (152, 190, 84, 40)}, t=P, s="OCL/P"),
        _el("pTag", "box", {5: (152, 302, 84, 40)}, t=P, s="Tags"),
        _el("astGui", "box", {3: (196, 102, 88, 40), 4: (262, 174, 76, 40), 5: (230, 542, 70, 30, F)}, t={3: T("Input AST", "Eingabe-AST"), 5: "AST"}),
        _el("astCd", "box", {3: (196, 222, 88, 40), 4: (262, 284, 76, 40), 5: (258, 216, 96, 32)}, t={3: T("Input AST", "Eingabe-AST"), 5: "CD4A-AST"}),
        _el("astOcl", "box", {3: (196, 342, 88, 40), 4: (262, 394, 76, 40), 5: (258, 176, 96, 32)}, t={3: T("Input AST", "Eingabe-AST"), 5: "OCL-AST"}),
        _el("astVcd", "box", {5: (258, 256, 96, 32)}, t="CD4A-AST"),
        _el("astTag", "box", {5: (258, 296, 96, 32)}, t="Tagging-AST"),
        _el("tg1", "box", {5: (370, 300, 108, 36)}, t="Tagged CD4C"),
        _el("tg2", "box", {5: (370, 350, 108, 36)}, t="Tagged CD4C"),

        # ---------------- transformations, output ASTs, template engines, templates ----------------
        _el("trUI", "box", {3: (310, 102, 96, 40), 4: (352, 174, 82, 40), 5: (312, 542, 70, 30, F)}, t={3: T("Pages", "Seiten"), 5: T("pages", "Seiten")}, s={3: T("transform", "Umformung"), 5: ""}, cls="hl"),
        _el("trDS", "box", {3: (310, 222, 96, 40), 4: (352, 284, 82, 40), 5: (410, 36, 370, 236)},
            t={3: T("Data", "Daten"), 5: T("TRANSFORMATIONS · creators", "TRANSFORMATIONEN · Creators")}, s={3: T("transform", "Umformung"), 5: ""}, cls="hl", x=(5, _trafo_list())),
        _el("oastUI", "box", {3: (432, 102, 96, 40), 4: (448, 174, 84, 40), 5: (394, 542, 80, 30, F)}, t={3: T("Output AST", "Ausgabe-AST"), 5: "AST"}),
        # the class-diagram transformation writes several output ASTs: one each for DTOs, data classes and commands
        _el("oastDS", "box", {3: (432, 190, 96, 32), 4: (448, 252, 84, 32), 5: (600, 300, 118, 36)}, t={3: T("Output AST", "Ausgabe-AST"), 5: "Output CD4C"}),
        _el("oast2", "box", {3: (432, 226, 96, 32), 4: (448, 288, 84, 32), 5: (600, 350, 118, 36)}, t={3: T("Output AST", "Ausgabe-AST"), 5: "Output CD4C"}),
        _el("oast3", "box", {3: (432, 262, 96, 32), 4: (448, 324, 84, 32), 5: (600, 400, 118, 36)}, t={3: T("Output AST", "Ausgabe-AST"), 5: "Output CD4C"}),
        _el("teUI", "box", {4: (546, 168, 108, 52), 5: (486, 542, 90, 30, F)}, t="Template", s={4: "engine", 5: ""}),
        _el("teDS", "box", {4: (546, 278, 108, 52), 5: (742, 308, 110, 50)}, t="Template", s="engine"),
        _el("tz", "zone", {4: (546, 372, 184, 132), 5: (742, 374, 140, 150)},
            t={4: T("TEMPLATES · FreeMarker", "TEMPLATES · FreeMarker"), 5: T("BACK-END TEMPLATES", "BACKEND-TEMPLATES")}, cls="line"),
        _el("t1", "chip", {4: (558, 400, 160, 24), 5: (750, 400, 124, 24)}, t={4: "form.ftl", 5: "coretemplates/"}),
        _el("t2", "chip", {4: (558, 430, 160, 24), 5: (750, 430, 124, 24)}, t={4: "dto.ftl", 5: "commands/"}),
        _el("t3", "chip", {4: (558, 460, 160, 24), 5: (750, 460, 124, 24)}, t={4: "dataclass.ftl", 5: "dao/"}),
        _el("t4", "chip", {5: (750, 490, 124, 24)}, t="dtos/"),

        # ---------------- generated files ----------------
        _el("chA", "chip", {2: (444, 90, 64, 26), 3: (566, 108, 82, 28), 4: (758, 180, 72, 28), 5: (914, 530, 72, 26, F)}, t={2: "HTML · TS", 3: T("Form", "Formular")}, cls="hl"),
        _el("chDTO", "chip", {3: (566, 192, 82, 28), 4: (758, 254, 72, 28), 5: (914, 300, 72, 26)}, t="DTO", cls="hl"),
        _el("chB", "chip", {2: (444, 186, 64, 26), 3: (566, 228, 82, 28), 4: (758, 290, 72, 28), 5: (914, 334, 72, 26)}, t={2: "Java", 3: T("Data class", "Datenklasse")}, cls="hl"),
        _el("chCmd", "chip", {3: (566, 264, 82, 28), 4: (758, 326, 72, 28), 5: (914, 368, 72, 26)}, t="Command", cls="hl"),
        _el("chDao", "chip", {5: (914, 402, 72, 26)}, t="DAO", cls="hl"),

        # ---------------- the application ----------------
        _el("fe", "box", {2: (544, 72, 162, 62), 3: (688, 92, 196, 60), 4: (854, 166, 118, 56), 5: (1008, 516, 76, 52, F)}, t="Client", s=T("front end", "Frontend")),
        _el("be", "box", {2: (544, 168, 162, 62), 3: (688, 212, 196, 60), 4: (854, 276, 118, 56), 5: (1008, 316, 76, 52)}, t="Server", s=T("back end", "Backend")),
        _el("db", "cyl", {2: (544, 264, 162, 72), 3: (688, 332, 196, 76), 4: (854, 386, 118, 70), 5: (1008, 392, 76, 64)},
            t={2: T("Persistence", "Persistenz"), 5: "DB"}, s={2: T("database", "Datenbank"), 5: ""}),
    ]


def edges():
    """(from, to, route, levels, extra) — routes in _route(); extra: ty (target anchor, 0..1 of its height), dash."""
    A = (1, 2, 3, 4, 5)
    return [
        ("cd", "zG", "hs", (1, 2), {}), ("zG", "zA", "h", (1,), {}),
        ("gui", "zG", "hs", (2,), {}), ("ocl", "zG", "hs", (2,), {}),
        ("zG", "chA", "ht", (2,), {}), ("zG", "chB", "ht", (2,), {}),
        ("chA", "fe", "h", (2, 3, 4, 5), {}), ("chB", "be", "h", (2, 3, 4, 5), {}), ("be", "db", "v", (2, 3, 4, 5), {}),
        # level 3: straight from the models into the ASTs
        ("gui", "astGui", "h", (3,), {}), ("cd", "astCd", "h", (3,), {}), ("ocl", "astOcl", "h", (3,), {}),
        ("astGui", "trUI", "h", (3, 4, 5), {}), ("trUI", "oastUI", "h", (3, 4, 5), {}),
        ("astCd", "trDS", "h", (3, 4), {}), ("trDS", "oastDS", "h", (3, 4), {}), ("trDS", "oast2", "h", (3, 4), {}), ("trDS", "oast3", "h", (3, 4), {}), ("astOcl", "trDS", "hv", (3, 4), {}),
        ("oastUI", "chA", "h", (3,), {}), ("oastDS", "chDTO", "h", (3,), {}), ("oast2", "chB", "h", (3,), {}), ("oast3", "chCmd", "h", (3,), {}),
        ("chDTO", "fe", "h", (3, 4), {}), ("chDTO", "be", "h", (3, 4, 5), {}),
        # level 4: parsers from grammars, code from templates
        ("gui", "pGui", "h", (4, 5), {}), ("pGui", "astGui", "h", (4, 5), {}),
        ("cd", "pCd", "h", (4, 5), {}), ("pCd", "astCd", "h", (4, 5), {}),
        ("ocl", "pOcl", "h", (4, 5), {}), ("pOcl", "astOcl", "h", (4, 5), {}),
        ("oastUI", "teUI", "h", (4, 5), {}), ("teUI", "chA", "h", (4, 5), {}),
        ("oastDS", "teDS", "h", (4, 5), {}), ("oast2", "teDS", "h", (4, 5), {}), ("oast3", "teDS", "h", (4, 5), {}),
        ("teDS", "chDTO", "h", (4, 5), {}), ("teDS", "chB", "h", (4, 5), {}), ("teDS", "chCmd", "h", (4, 5), {}), ("chCmd", "be", "h", (3, 4, 5), {}),
        ("tz", "teDS", "vu", (4, 5), {}), ("gz", "pGui", "v", (4,), {"dash": 1}),
        # level 5: the back-end generator in full
        ("ctl", "wf", "v", (5,), {}), ("wf", "ld", "v", (5,), {}), ("wf", "trDS", "h", (5,), {"ty": .42}),
        ("gz", "ld", "vu", (5,), {"dash": 1}),
        ("vcd", "pCd", "h", (5,), {}), ("tag", "pTag", "h", (5,), {}),
        ("pCd", "astVcd", "h", (5,), {}), ("pTag", "astTag", "h", (5,), {}),
        ("astOcl", "trDS", "h", (5,), {"ty": .82}),
        ("astCd", "tg1", "h", (5,), {}), ("astTag", "tg1", "h", (5,), {}), ("astVcd", "tg2", "h", (5,), {}), ("astTag", "tg2", "h", (5,), {}),
        ("tg1", "trDS", "vx", (5,), {}), ("trDS", "oastDS", "vd", (5,), {}),
        ("tg1", "oastDS", "h", (5,), {}), ("tg2", "oast2", "h", (5,), {}), ("tg2", "oast3", "h", (5,), {}),
        ("teDS", "chDao", "h", (5,), {}), ("chDao", "be", "h", (5,), {}),
    ]


# ---------------------------------------------------------------------
# Rendering (the same geometry as assets/mde.js d0 — keep the two in step)
# ---------------------------------------------------------------------

def _shape(kind, w, h):
    if kind == "doc":
        return f'<path class="sh" d="M0 0H{w - 10}L{w} 10V{h}H0Z M{w - 10} 0V10H{w}"/>'
    if kind == "cyl":
        r = w / 2
        return f'<path class="sh" d="M0 8V{h - 8}A{r} 8 0 0 0 {w} {h - 8}V8A{r} 8 0 0 0 0 8A{r} 8 0 0 0 {w} 8"/>'
    if kind == "label":
        return ""
    return f'<rect class="sh" width="{w}" height="{h}" rx="{4 if kind == "zone" else 3}"/>'


def _texts(kind, w, h, t, s):
    if kind == "zone":
        return f'<text class="s zl" x="10" y="17">{t}</text><text class="s ss"></text>'
    cls = "s" if kind == "chip" else "t"
    if s:
        return f'<text class="{cls} tt" x="{w / 2}" y="{h / 2 - 3}" text-anchor="middle">{t}</text><text class="s ss" x="{w / 2}" y="{h / 2 + 12}" text-anchor="middle">{s}</text>'
    return f'<text class="{cls} tt" x="{w / 2}" y="{h / 2 + 4}" text-anchor="middle">{t}</text><text class="s ss" x="{w / 2}" text-anchor="middle"></text>'


def _route(r, a, b, ty=.5):
    ax, ay, aw, ah = a[:4]
    bx, by, bw, bh = b[:4]
    if r in ("h", "hs", "ht"):
        x1, x2 = ax + aw, bx
        y1 = ay + ah / 2
        y2 = by + bh * ty
        if r == "hs":
            y2 = y1
        if r == "ht":
            y1 = y2
        if abs(y1 - y2) < 1:
            return f"M{x1:.1f} {y1:.1f}H{x2:.1f}"
        xm = (x1 + x2) / 2
        return f"M{x1:.1f} {y1:.1f}H{xm:.1f}V{y2:.1f}H{x2:.1f}"
    if r == "hv":                                   # right, then up into the bottom of b
        y1 = ay + ah / 2
        x2 = bx + bw / 2
        return f"M{ax + aw:.1f} {y1:.1f}H{x2:.1f}V{by + bh:.1f}"
    if r == "vx":                                   # straight up from a into b
        return f"M{ax + aw / 2:.1f} {ay:.1f}V{by + bh:.1f}"
    if r == "vd":                                   # straight down from a into b, at b's centre
        return f"M{bx + bw / 2:.1f} {ay + ah:.1f}V{by:.1f}"
    up = r == "vu"
    x1, x2 = ax + aw / 2, bx + bw / 2
    y1, y2 = (ay, by + bh) if up else (ay + ah, by)
    if abs(x1 - x2) < 1:
        return f"M{x1:.1f} {y1:.1f}V{y2:.1f}"
    ym = (y1 + y2) / 2
    return f"M{x1:.1f} {y1:.1f}V{ym:.1f}H{x2:.1f}V{y2:.1f}"


WORDS = {
    1: T("<b>1</b> · A model goes in, an application comes out.",
         "<b>1</b> · Ein Modell geht hinein, eine Anwendung kommt heraus."),
    2: T("<b>2</b> · Several models, one generator — and the application has a client, a server and a database.",
         "<b>2</b> · Mehrere Modelle, ein Generator — und die Anwendung hat Client, Server und Datenbank."),
    3: T("<b>3</b> · Inside, each model becomes a syntax tree (AST); transformations turn it into new trees, one per kind of file.",
         "<b>3</b> · Drinnen wird jedes Modell ein Syntaxbaum (AST); Transformationen machen daraus neue Bäume, einen je Dateiart."),
    4: T("<b>4</b> · The parsers are generated from grammars; the code is printed by filling templates.",
         "<b>4</b> · Die Parser werden aus Grammatiken generiert; der Code entsteht, indem Templates gefüllt werden."),
    5: T("<b>5</b> · MontiGem’s back-end generator: control scripts, a model loader, tagged syntax trees and dozens of transformations.",
         "<b>5</b> · MontiGems Backend-Generator: Steuerskripte, ein Modell-Lader, getaggte Syntaxbäume und Dutzende Transformationen."),
}

# phones: levels 1–2 stacked (models above, generator in the middle, application below); mde.js swaps them in
TALL_FRAMES = {1: (380, 440), 2: (380, 660)}
TALL = {
    "zM": {1: (90, 10, 200, 130), 2: (10, 10, 360, 120)},
    "cd": {1: (140, 38, 100, 82), 2: (138, 40, 104, 64)},
    "gui": {2: (24, 40, 104, 64)},
    "ocl": {2: (252, 40, 104, 64)},
    "zG": {1: (90, 170, 200, 110), 2: (10, 165, 360, 150)},
    "gT": {1: (90, 170, 200, 110), 2: (10, 165, 360, 100)},
    "chA": {2: (60, 275, 110, 26)},
    "chB": {2: (210, 275, 110, 26)},
    "zA": {1: (90, 315, 200, 110), 2: (10, 350, 360, 300)},
    "aT": {1: (90, 315, 200, 110)},
    "fe": {2: (24, 384, 150, 62)},
    "be": {2: (206, 384, 150, 62)},
    "db": {2: (206, 486, 150, 72)},
}
TALL_ROUTE = {("zG", "chA"): None, ("zG", "chB"): None}       # the chips sit inside the generator there: no arrow


# the three places the morph appears: (levels, start level, caption, source line)
VIEWS = {
    "intro": ((1, 2), 1,
              T("<b>Model-driven, from far away.</b> A model goes in, a generator reads it, an application comes out. Step to <b>2</b>: usually there are several models, and the application has several tiers. What happens inside the generator follows in chapter 02.",
                "<b>Modellgetrieben, von Weitem.</b> Ein Modell geht hinein, ein Generator liest es, eine Anwendung kommt heraus. Auf Stufe <b>2</b>: Meist sind es mehrere Modelle, und die Anwendung hat mehrere Schichten. Was im Generator passiert, folgt in Kapitel 02."),
              None),
    "inside": ((2, 3, 4), 3,
               T("<b>Inside the generator.</b> Step with − and +: from the outside view (<b>2</b>) into the generator (<b>3</b>), where each model becomes a syntax tree and transformations derive one tree per kind of file, to where the parsers and the code come from (<b>4</b>).",
                 "<b>Im Generator.</b> Mit − und + von der Außensicht (<b>2</b>) in den Generator hinein (<b>3</b>), wo jedes Modell ein Syntaxbaum wird und Transformationen je Dateiart einen Baum ableiten, bis dahin, woher Parser und Code kommen (<b>4</b>)."),
               "net24"),
    "full": ((5,), 5,
             T("<b>The real thing.</b> MontiGem’s back-end generator with a selection of its transformations — the same three containers as before, filled in.",
               "<b>Das echte Werkzeug.</b> MontiGems Backend-Generator mit einer Auswahl seiner Transformationen — dieselben drei Behälter wie zuvor, ausgefüllt."),
             "docs"),
}


def _texts_top(t):
    """The level-5 panel: its title top left (the list is in .lv-x)."""
    return f'<text class="s a tt" x="10" y="18">{t}</text><text class="s ss"></text>'


def fig_levels(lang, view="intro"):
    from article_common import src, source_line
    L = lambda x: x[lang]
    levels, start, cap, source = VIEWS[view]
    els, eds = elements(), edges()
    mk = f"lv{view}"
    data = {"frames": {k: FRAMES[k] for k in levels}, "levels": list(levels), "start": start,
            "words": {k: L(WORDS[k]) for k in levels}, "els": [], "eds": []}
    by_id = {}
    for e in els:
        geo = {str(k): v for k, v in e["geo"].items()}
        d = {"id": e["id"], "k": e["kind"], "g": geo, "t": _per_level(e["t"], lang), "s": _per_level(e["s"], lang)}
        if e["x"]:
            d["xl"] = e["x"][0]
        data["els"].append(d)
        by_id[e["id"]] = e
    for a, b, r, lv, ex in eds:
        data["eds"].append({"a": a, "b": b, "r": r, "lv": list(lv), **ex})

    # static picture: the start level (what shows before the script runs, or without it)
    parts = []
    for e, d in zip(els, data["els"]):
        x = e["x"][1] if e["x"] else ""
        g = e["geo"].get(start)
        if g:
            gx, gy, gw, gh = g[:4]
            o = g[4] if len(g) > 4 else 1
            top = bool(e["x"]) and e["x"][0] == start
            texts = _texts_top(d["t"][start - 1]) if top else _texts(e["kind"], gw, gh, d["t"][start - 1], d["s"][start - 1])
            parts.append(f'<g class="lv-el k-{e["kind"]} {e["cls"]}" data-id="{e["id"]}" transform="translate({gx} {gy})" opacity="{o}">'
                         f'{_shape(e["kind"], gw, gh)}{texts}'
                         + (f'<g class="lv-x" opacity="{1 if top else 0}">{x}</g>' if x else "") + '</g>')
        else:
            parts.append(f'<g class="lv-el k-{e["kind"]} {e["cls"]}" data-id="{e["id"]}" opacity="0">{_shape(e["kind"], 10, 10)}{_texts(e["kind"], 10, 10, "", "")}'
                         + (f'<g class="lv-x" opacity="0">{x}</g>' if x else "") + '</g>')
    lines = []
    for k, (a, b, r, lv, ex) in enumerate(eds):
        cls = "ln dash" if ex.get("dash") else "ln"
        ga, gb = by_id[a]["geo"].get(start), by_id[b]["geo"].get(start)
        if start in lv and ga and gb:
            lines.append(f'<path class="{cls}" data-e="{k}" d="{_route(r, ga, gb, ex.get("ty", .5))}" marker-end="url(#{mk})"/>')
        else:
            lines.append(f'<path class="{cls}" data-e="{k}" d="M0 0" opacity="0" marker-end="url(#{mk})"/>')

    W, H = FRAMES[start]
    label = L(T("The generator at different levels of detail: from one model, a generator and an application, to several models and a client–server–database application, to syntax trees and transformations inside the generator, to grammars and templates, to the full MontiGem back-end generator",
                "Der Generator in verschiedenen Detailstufen: von einem Modell, einem Generator und einer Anwendung über mehrere Modelle und eine Anwendung aus Client, Server und Datenbank, Syntaxbäume und Transformationen im Generator, Grammatiken und Templates bis zum vollständigen Backend-Generator von MontiGem"))
    zones = "".join(p for e, p in zip(els, parts) if e["kind"] == "zone")
    rest = "".join(p for e, p in zip(els, parts) if e["kind"] != "zone")
    svg = (f'<svg class="dia lv-svg" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">{_arrow_defs(mk)}'
           f'{zones}<g class="lv-edges">{"".join(lines)}</g>{rest}</svg>')
    if view == "intro":
        data["tall"] = {"frames": TALL_FRAMES, "geo": {k: {str(l): g for l, g in v.items()} for k, v in TALL.items()},
                        "routes": [TALL_ROUTE.get((a, b), "v") for a, b, r, lv, ex in eds]}
    js = html.escape(json.dumps(data, ensure_ascii=False), quote=True)
    if source == "net24":
        source = src("after", "Net24", where="Fig. 7.1")
    elif source == "docs":
        source = T("After the MontiGem developer documentation (back-end data-structure generator)",
                   "Nach der MontiGem-Entwicklerdokumentation (Backend-Datenstruktur-Generator)")
    tail = f'<figcaption class="mono">{L(cap)}{source_line(source, lang)}</figcaption>'
    if len(levels) == 1:                         # a still picture, wide: it scrolls, also on desktop
        return (f'<figure class="media art-fig lv-full"><div class="dia-scroll lv-scroll" tabindex="0">{svg}</div>'
                f'<p class="mde-hint mono" aria-hidden="true">↔ {L(T("scroll", "scrollen"))}</p>{tail}</figure>')
    buttons = "".join(f'<button type="button" class="lv-b" aria-pressed="{str(k == start).lower()}" aria-label="{L(T("level", "Stufe"))} {k}">{k}</button>' for k in levels)
    ctrl = (f'<div class="demo-ctrl mono lv-ctrl"><span class="lv-bs" role="group" aria-label="{L(T("Level of detail", "Detailstufe"))}">'
            f'<button type="button" class="lv-prev" aria-label="{L(T("less detail", "weniger Details"))}">−</button>{buttons}'
            f'<button type="button" class="lv-next" aria-label="{L(T("more detail", "mehr Details"))}">+</button></span>'
            f'<span class="where" aria-live="polite"><span>{data["words"][start]}</span></span></div>')
    return (f'<figure class="media art-fig demo d0{" has-tall" if view == "intro" else ""}" data-demo="d0" data-json="{js}">'
            f'{ctrl}<div class="dia-scroll lv-scroll" tabindex="0">{svg}</div>'
            f'<p class="mde-hint mono" aria-hidden="true">↔ {L(T("scroll", "scrollen"))}</p>{tail}</figure>')
