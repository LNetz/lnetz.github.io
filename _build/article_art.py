"""
Hero pictograms at the top of the article pages (research-mde.html, research-ai4se.html): one wide drawing each
in the style of the diagrams (.dia classes, one accent colour), between the header and the article.
The research page's article cards (build.py ARTICLE_THUMBS) are small versions of the same motifs.
"""
import math

# Part 3 (Digital Twins): False builds the page but links it from nowhere (no research-page card, no topic link,
# no entry in the series line).
DT_PUBLISHED = True
# Part 4 (Evolutionary Algorithms): same switch for research-ea.html (ea.py).
EA_PUBLISHED = True


def gear(cx, cy, r, teeth, phase=0.0, depth=.22):
    """An SVG path for a gear: `teeth` trapezoid teeth around a circle of outer radius r."""
    ro, ri, pts = r, r * (1 - depth), []
    for k in range(teeth):
        a, w = 2 * math.pi * k / teeth + phase, math.pi / teeth
        for ang, rr in ((a - w * .55, ri), (a - w * .32, ro), (a + w * .32, ro), (a + w * .55, ri)):
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"


def _arrow(x1, y, x2, cls="ln hl"):
    return f'<path class="{cls}" d="M{x1} {y}H{x2}"/><path class="{cls}" d="M{x2 - 7} {y - 6}L{x2} {y}L{x2 - 7} {y + 6}"/>'


def hero_mde(lang):
    """A textual model and its class diagram → the generator (gears) → database, server and browser."""
    L = lambda en, de: en if lang == "en" else de
    code = ["classdiagram Bank {", "  class Account {", "    String name;", "    int balance;", "  }",
            "  association [1]", "    Accountant -> Account [*];", "}"]
    code_svg = "".join(f'<text class="hc" x="52" y="{66 + 15 * k}">{l.replace("<", "&lt;").replace(">", "&gt;")}</text>' for k, l in enumerate(code))
    uml = ('<rect class="box" x="270" y="52" width="104" height="54" rx="2"/><path class="ln" d="M270 72H374"/><text class="t" x="322" y="67" text-anchor="middle">Accountant</text>'
           '<text x="280" y="90">bank</text>'
           '<rect class="box hl" x="270" y="140" width="104" height="62" rx="2"/><path class="ln" d="M270 160H374"/><text class="t" x="322" y="155" text-anchor="middle">Account</text>'
           '<text x="280" y="178">name</text><text x="280" y="194">balance</text>'
           '<path class="ln" d="M322 106V140"/><text class="s" x="330" y="120">1</text><text class="s" x="330" y="136">*</text>')
    gears = (f'<path class="gearbig" d="{gear(500, 122, 46, 12)}"/><circle class="hub" cx="500" cy="122" r="13"/>'
             f'<path class="gearsmall" d="{gear(556, 72, 26, 9, math.pi / 9)}"/><circle class="hub2" cx="556" cy="72" r="7"/>')
    db = ('<path class="box" d="M650 42v40c0 7 22 12 48 12s48-5 48-12v-40"/><ellipse class="box" cx="698" cy="42" rx="48" ry="12"/>'
          '<path class="ln" d="M650 58c0 7 22 12 48 12s48-5 48-12"/>')
    server = ('<rect class="box" x="650" y="112" width="96" height="24" rx="2"/><rect class="box" x="650" y="140" width="96" height="24" rx="2"/>'
              '<circle class="dot" cx="662" cy="124" r="2.5"/><circle class="dot" cx="662" cy="152" r="2.5"/><path class="ln" d="M676 124H730M676 152H720"/>')
    browser = ('<rect class="box hl" x="770" y="38" width="74" height="150" rx="4"/><path class="ln" d="M770 52H844"/>'
               '<circle class="dot" cx="778" cy="45" r="2"/><rect class="hfill" x="778" y="60" width="58" height="10" rx="1"/>'
               '<path class="ln" d="M778 84H836M778 98H836M778 112H836M778 126H836"/>'
               '<rect class="box" x="778" y="140" width="58" height="12" rx="1"/><rect class="box" x="778" y="158" width="58" height="12" rx="1"/>')
    labels = (f'<text class="s" x="40" y="26">{L("THE MODEL", "DAS MODELL")}</text><text class="s" x="452" y="26">GENERATOR</text>'
              f'<text class="s" x="650" y="26">{L("THE APPLICATION", "DIE ANWENDUNG")}</text>'
              f'<text class="s" x="650" y="182">{L("database · server", "Datenbank · Server")}</text><text class="s" x="770" y="204">browser</text>')
    body = (f'<rect class="zone" x="0" y="0" width="860" height="220" rx="6"/>'
            f'<rect class="box" x="40" y="40" width="200" height="150" rx="3"/>{code_svg}'
            f'<path class="ln dash" d="M240 115H262"/>{uml}'
            f'{_arrow(388, 122, 444)}{gears}{_arrow(560, 122, 636)}'
            f'<path class="ln hl" d="M600 122V70H640"/><path class="ln hl" d="M600 122V176H640"/>{db}{server}{browser}{labels}')
    return (f'<figure class="art-hero" aria-hidden="true"><svg class="dia hero" viewBox="0 0 860 220">{body}</svg></figure>')


def hero_ai4se(lang):
    """A question → a neural network → the probability of the next token → the answer, one token at a time."""
    L = lambda en, de: en if lang == "en" else de
    q = L("What is the capital", "Was ist die Hauptstadt")
    q2 = L("of France?", "von Frankreich?")
    layers = [(270, [70, 110, 150]), (340, [50, 90, 130, 170]), (410, [70, 110, 150]), (470, [90, 130])]
    edges = "".join(f'<path class="ln nn" d="M{x1} {a}L{x2} {b}"/>' for (x1, ys1), (x2, ys2) in zip(layers, layers[1:]) for a in ys1 for b in ys2)
    nodes = "".join(f'<circle class="box{" hl" if (x, y) == (470, 90) else ""}" cx="{x}" cy="{y}" r="{9 if x == 470 else 7}"/>' for x, ys in layers for y in ys)
    nodes += '<circle class="hfill" cx="470" cy="90" r="5"/>'
    toks = [("Paris", .81), ("Lyon", .07), ("Toulouse", .04), (L("the", "die"), .03)]
    bars = "".join(f'<text class="{"t" if k == 0 else ""}" x="600" y="{70 + k * 30}" text-anchor="end">{t}</text>'
                   f'<rect class="{"hfill" if k == 0 else "gbar"}" x="610" y="{60 + k * 30}" width="{max(4, p * 150):.0f}" height="12" rx="2"/>'
                   for k, (t, p) in enumerate(toks))
    body = (f'<rect class="zone" x="0" y="0" width="860" height="220" rx="6"/>'
            f'<rect class="box" x="40" y="62" width="170" height="70" rx="12"/><path class="box" d="M64 132l-8 16 22-16"/>'
            f'<text x="56" y="92">{q}</text><text x="56" y="110">{q2}</text>'
            f'{_arrow(214, 110, 256)}{edges}{nodes}{_arrow(486, 90, 530)}{bars}'
            f'<path class="ln hl dash" d="M690 66H806V200H125V154" marker-end=""/><path class="ln hl" d="M119 160L125 152L131 160"/>'
            f'<text class="s" x="40" y="26">PROMPT</text><text class="s" x="262" y="26">{L("THE MODEL", "DAS MODELL")}</text>'
            f'<text class="s" x="540" y="26">{L("THE NEXT TOKEN", "DAS NÄCHSTE TOKEN")}</text>'
            f'<text class="a" x="470" y="192" text-anchor="middle">{L("“The capital is Paris”", "„Die Hauptstadt ist Paris“")}▌</text>')
    return (f'<figure class="art-hero" aria-hidden="true"><svg class="dia hero" viewBox="0 0 860 220">{body}</svg></figure>')


def hero_dt(lang):
    """A machine and its twin: data goes up into shadows, the twin's models and services decide, information and commands come back."""
    from dt_figs import imm_parts
    L = lambda en, de: en if lang == "en" else de

    def machine(ox, oy, sx, below):
        """The running example (dt_figs.imm_parts) with its parts labelled as in the chair's drawings; labels below at `below`."""
        P = lambda x, y: (ox + x * sx, oy + y * sx)

        def callout(px, py, tx, ty, text, anchor="middle"):
            (x, y) = P(px, py)
            return f'<path class="ln callout" d="M{x:.0f} {y:.0f}V{ty + (-10 if ty > y else 4)}"/><text class="s" x="{tx:.0f}" y="{ty}" text-anchor="{anchor}">{text}</text>'
        return (f'<g class="glyph imm" transform="translate({ox} {oy}) scale({sx})">{imm_parts(sensors=True, out=True)}</g>'
                + callout(17, 112, P(0, 0)[0], below - 12, L("control cabinet", "Schaltschrank"), "start")
                + callout(136.5, 84, P(136.5, 0)[0], below, L("clamping unit · mould", "Schließeinheit · Form"))
                + callout(250, 84, P(250, 0)[0], below, L("injection unit", "Spritzeinheit"))
                + callout(151, 6, P(151, 0)[0] - 22, oy - 16, L("user interface", "Bedienoberfläche"))
                + callout(202, 22, P(202, 0)[0] + 18, oy - 16, L("hopper", "Trichter")))

    def twin(x, y, w):
        """The twin: service tabs, stacked models, shadows as pills (170 high)."""
        tabs = [L("monitor", "Monitor"), L("predict", "Prognose"), L("assist", "Assistenz"), L("control", "Steuerung")]
        tw = (w - 28 - 18) / 4
        return (f'<rect class="box hl" x="{x}" y="{y}" width="{w}" height="170" rx="8"/>'
                + "".join(f'<rect class="{"hfill" if k == 0 else "box"}" x="{x + 14 + k * (tw + 6):.1f}" y="{y + 14}" width="{tw:.1f}" height="18" rx="2"/>'
                          f'<text class="s{" on" if k == 0 else ""}" x="{x + 14 + k * (tw + 6) + tw / 2:.1f}" y="{y + 27}" text-anchor="middle">{t}</text>' for k, t in enumerate(tabs))
                + "".join(f'<rect class="box" x="{x + 16 + k * 6}" y="{y + 52 + k * 8}" width="104" height="30" rx="2"/>' for k in range(3))
                + f'<text class="s" x="{x + 38}" y="{y + 87}">{L("machine · mould", "Maschine · Form")}</text>'
                + "".join(f'<rect class="box" x="{x + w - 146}" y="{y + 52 + k * 22}" width="132" height="16" rx="8"/><text class="s" x="{x + w - 136}" y="{y + 63 + k * 22}">{t}</text>'
                          for k, t in enumerate(["Temp2Max", L("rejection rate", "Ausschussquote"), L("energy", "Energie")]))
                + f'<text class="s" x="{x + 16}" y="{y + 118}">{L("models", "Modelle")}</text><text class="s" x="{x + w - 146}" y="{y + 132}">{L("shadows", "Schatten")}</text>'
                f'<text class="s" x="{x + 16}" y="{y + 158}">{L("services · cockpit", "Services · Cockpit")}</text>')

    title_m = L("THE ORIGINAL SYSTEM · AN INJECTION-MOULDING MACHINE", "DAS ORIGINALSYSTEM · EINE SPRITZGIESSMASCHINE")
    title_t = L("THE DIGITAL TWIN", "DER DIGITALE ZWILLING")
    data, back = L("data → digital shadows", "Daten → Schatten"), L("information · commands", "Infos · Befehle")
    # wide screens: machine left, twin right
    wide = (f'<rect class="zone" x="0" y="0" width="860" height="220" rx="6"/>{machine(20, 50, 1.06, 206)}{twin(540, 28, 300)}'
            f'{_arrow(376, 96, 524)}<text class="s" x="384" y="86">{data}</text>'
            f'<path class="ln" d="M524 150H380"/><path class="ln" d="M387 144L380 150L387 156"/><text class="s" x="384" y="172">{back}</text>'
            f'<text class="s" x="20" y="18">{title_m}</text><text class="s" x="540" y="18">{title_t}</text>')
    # phones: the machine on top, the twin below — the wide drawing would shrink to unreadable labels
    tall = (f'<rect class="zone" x="0" y="0" width="430" height="496" rx="6"/>{machine(18, 64, 1.22, 236)}'
            f'<path class="ln hl" d="M60 252V290"/><path class="ln hl" d="M54 284L60 290L66 284"/><text class="s" x="70" y="276">{data}</text>'
            f'<path class="ln" d="M370 290V252"/><path class="ln" d="M364 258L370 252L376 258"/><text class="s" x="360" y="276" text-anchor="end">{back}</text>'
            f'<text class="s" x="18" y="22">{title_m}</text><text class="s" x="18" y="306">{title_t}</text>{twin(15, 314, 400)}')
    return (f'<figure class="art-hero" aria-hidden="true"><svg class="dia hero hero-wide" viewBox="0 0 860 220">{wide}</svg>'
            f'<svg class="dia hero hero-tall" viewBox="0 0 430 496">{tall}</svg></figure>')
