"""
Figures of the Digital Twins article (research-dt.html, _build/dt.py). Static diagrams are inline SVG with the .dia
classes; the five interactive figures (ladder, anatomy, shadows, loop, roles) get all their states here and ship them
as data-json — assets/dt.js only swaps and highlights. Article-specific styles are in assets/dt.css.

Two running examples: a car (chapter 01, everyday concepts: ladder, anatomy, shadows as views, type vs instance,
composition) and the injection-moulding machine of the RWTH group's papers (chapter 02, the twin's loop; also the hero
in article_art.py). Figures redrawn after a paper say so in their source line (article_common.src).
Also holds the article's literature list (REFS) so that figures and text cite the same numbers.
"""
import html
import json
import math
import re
from datetime import date

from ai4se import T, fig, demo, controls, cite, _link
from article_common import src
from project_content import _arrow_defs, box

esc = html.escape

# ---------------- literature (numbered; article_common renumbers by first citation) ----------------
REFS = [
    ("essay", _link("B. Rumpe, J. Michael, A. Wortmann: Digital Twin Definition, v2.2. SE@RWTH essay (2024).", "https://www.se-rwth.de/essay/Digital-Twin-Definition/")),
    ("topic", _link("SE@RWTH: Digital Twins (research topic).", "https://www.se-rwth.de/research/Digital-Twins/")),
    ("DMR20", _link("M. Dalibor, J. Michael, B. Rumpe, S. Varga, A. Wortmann: Towards a Model-Driven Architecture for Interactive Digital Twin Cockpits. ER 2020, LNCS 12400, 377–387.", "https://www.se-rwth.de/publications/Towards-a-Model-Driven-Architecture-for-Interactive-Digital-Twin-Cockpits.pdf")),
    ("BBD21", _link("F. Becker, P. Bibow, M. Dalibor, … J. Michael, B. Rumpe, … A. Wortmann: A Conceptual Model for Digital Shadows in Industry and its Application. ER 2021, LNCS 13011, 271–281.", "https://www.se-rwth.de/publications/A-Conceptual-Model-for-Digital-Shadows-in-Industry-and-its-Application.pdf")),
    ("BMR22", _link("T. Bano, J. Michael, B. Rumpe, S. Varga, M. Weske: Process-Aware Digital Twin Cockpit Synthesis from Event Logs. Journal of Computer Languages 70 (2022).", "https://www.se-rwth.de/publications/Process-Aware-Digital-Twin-Cockpit-Synthesis-from-Event-Logs.pdf")),
    ("KMR20", "J. C. Kirchhof, J. Michael, B. Rumpe, S. Varga, A. Wortmann: Model-driven Digital Twin Construction: Synthesizing the Integration of Cyber-Physical Systems with Their Information Systems. MODELS 2020, 90–101."),
    ("HHMR23", "M. Heithoff, A. Hellwig, J. Michael, B. Rumpe: Digital Twins for Sustainable Software Systems. GREENS@ICSE 2023, 19–23."),
    ("HJM24", "M. Heithoff, N. Jansen, J. Michael, F. Rademacher, B. Rumpe: Model-Based Engineering of Multi-Purpose Digital Twins in Manufacturing. In: Digital Twins, Springer (2024), 89–126."),
    ("Mic25", "J. Michael: Model-Driven Engineering of Digital Twins with Informative and Assistive Services. Habilitation, Aachener Informatik-Berichte SE 60, Shaker (2025)."),
    ("PZC25", _link("J. Pfeiffer, C. Zhang, B. Combemale, J. Michael, B. Rumpe, M. Wimmer, A. Wortmann: Towards a Unifying Reference Model for Digital Twins of Cyber-Physical Systems. ETFA 2025.", "https://www.se-rwth.de/publications/Towards-a-Unifying-Reference-Model-for-Digital-Twins-of-Cyber-Physical-Systems.pdf")),
    ("DJR22", _link("M. Dalibor, N. Jansen, B. Rumpe, D. Schmalzing, L. Wachtmeister, M. Wimmer, A. Wortmann: A Cross-Domain Systematic Mapping Study on Software Engineering for Digital Twins. Journal of Systems and Software 193 (2022).", "https://doi.org/10.1016/j.jss.2022.111361")),
    ("BDJ22", _link("P. Brauner et al.: A Computer Science Perspective on Digital Transformation in Production. ACM Transactions on the Internet of Things (2022).", "https://www.se-rwth.de/publications/A-Computer-Science-Perspective-on-Digital-Transformation-in-Production.pdf")),
    ("ERCIM", _link("M. Jarke, G. Schuh, C. Brecher, M. Brockmann, J.-P. Prote: Digital Shadows in the Internet of Production. ERCIM News 115 (2018).", "https://ercim-news.ercim.eu/en115/special/digital-shadows-in-the-internet-of-production")),
    ("Krit", _link("W. Kritzinger, M. Karner, G. Traar, J. Henjes, W. Sihn: Digital Twin in manufacturing: A categorical literature review and classification. IFAC-PapersOnLine 51(11), 1016–1022 (2018).", "https://doi.org/10.1016/j.ifacol.2018.08.474")),
    ("MKD23", "J. Michael, I. Koren, I. Dimitriadis, … G. Schuh: A Digital Shadow Reference Model for Worldwide Production Labs. In: Internet of Production, Springer (2023)."),
    ("BDH20", "P. Bibow, M. Dalibor, C. Hopmann, B. Mainz, B. Rumpe, D. Schmalzing, M. Schmitz, A. Wortmann: Model-Driven Development of a Digital Twin for Injection Molding. CAiSE 2020."),
    ("MCZ25", "J. Michael, C. Cleophas, S. Zschaler, et al.: Model-Driven Engineering for Digital Twins: Opportunities and Challenges. Systems Engineering 28(5), 659–670 (2025)."),
    ("MPRW22", "J. Michael, J. Pfeiffer, B. Rumpe, A. Wortmann: Integration Challenges for Digital Twin Systems-of-Systems. SESoS 2022, 9–12."),
    ("MW21", "J. Michael, A. Wortmann: Towards Development Platforms for Digital Twins: A Model-Driven Low-Code Approach. APMS 2021, 333–341."),
    ("MBD24", "J. Michael, J. Blankenbach, et al.: Integrating Models of Civil Structures in Digital Twins. Journal of Intelligent Infrastructure Research 3(3) (2024)."),
    ("MSW24", "J. Michael, M. Schwammberger, A. Wortmann: Explaining Cyber-Physical System Behavior with Digital Twins. IEEE Software 41(1) (2024)."),
    ("NASA", _link("E. Glaessgen, D. Stargel: The Digital Twin Paradigm for Future NASA and U.S. Air Force Vehicles. 53rd AIAA SDM Conference (2012).", "https://ntrs.nasa.gov/citations/20120008178")),
    ("BH24", _link("A. Barbie, W. Hasselbring: From Digital Twins to Digital Twin Prototypes (2024).", "https://arxiv.org/abs/2401.07985")),
    ("GV17", _link("M. Grieves, J. Vickers: Digital Twin: Mitigating Unpredictable, Undesirable Emergent Behavior in Complex Systems. In: Transdisciplinary Perspectives on Complex Systems, Springer (2017), 85–113.", "https://doi.org/10.1007/978-3-319-38756-7_4")),
    ("DTC", _link("Digital Twin Consortium: Definition of a digital twin.", "https://www.digitaltwinconsortium.org/initiatives/the-definition-of-a-digital-twin/")),
    ("IBM", _link("IBM: What is a digital twin?", "https://www.ibm.com/think/topics/digital-twin")),
    ("list", _link("A. Wortmann: a collection of 112 digital-twin definitions.", "https://awortmann.github.io/research/digital_twin_definitions/")),
    ("sosym", _link("J. Gray, B. Rumpe: Modeling of, for, and with digital twins. SoSyM editorial (2022).", "https://www.se-rwth.de/sosym/Modeling-of-for-and-with-digital-twins/")),
    ("F1", _link("Formula 1 Dictionary: Telemetry (car-to-pit only; the rules do not allow sending data to the car).", "https://www.formula1-dictionary.net/telemetry.html")),
    ("W10", _link("Microsoft Lifecycle: Windows 10 Home and Pro (support 29 July 2015 – 14 October 2025).", "https://learn.microsoft.com/en-us/lifecycle/products/windows-10-home-and-pro")),
]
_NUM = {k: n for n, (k, _) in enumerate(REFS, 1)}


def r(key):
    """A numbered reference into this article's literature list."""
    return f'<a class="cite" href="#ref-{_NUM[key]}">[{_NUM[key]}]</a>'


def n(key):
    """The literature number of key, for article_common.src(...)."""
    return _NUM[key]


def _arrow(x1, y1, x2, y2, cls="ln"):
    """A straight arrow whose head is its own path, so it takes on the colour of the arrow (no SVG marker)."""
    a = math.atan2(y2 - y1, x2 - x1)
    h = [(x2 - 6 * math.cos(a - .5), y2 - 6 * math.sin(a - .5)), (x2 - 6 * math.cos(a + .5), y2 - 6 * math.sin(a + .5))]
    return (f'<path class="{cls}" d="M{x1} {y1}L{x2} {y2}"/>'
            f'<path class="{cls}" d="M{h[0][0]:.1f} {h[0][1]:.1f}L{x2} {y2}L{h[1][0]:.1f} {h[1][1]:.1f}"/>')


def _code(lines, new=()):
    return "".join(f'<span class="l{" new" if k in new else ""}">{esc(t) or " "}</span>' for k, t in enumerate(lines))


def _pair(wide, tall):
    """A static figure with a stacked phone variant (dt.css shows .dt-tall under 600 px)."""
    return f'<div class="dt-pair"><div class="dt-wide">{wide}</div><div class="dt-tall">{tall}</div></div>'


# ---------------- glyphs ----------------
IMM_W, IMM_H = 320, 120          # the machine's own size before scaling


def imm_parts(sensors=False, out=False):
    """The case study: an injection-moulding machine, drawn after the RWTH group's papers (BDH20 and slides): control
    cabinet, clamping unit with the mould between tie bars, the user interface on its arm, injection unit with barrel,
    heater bands and hopper, all on the machine bed. 320 × 120 units, clamping unit left, injection unit right. Each part
    is a <g data-p>, so figures can light one up. sensors: accent dots where the twin's data comes from; out: a conveyor
    with moulded parts. Also used by the hero (article_art.hero_dt) and the card thumbnail."""
    p = {
        "cabinet": '<rect class="box" x="0" y="50" width="34" height="62" rx="2"/><rect class="box" x="6" y="57" width="22" height="11" rx="1"/><path class="ln" d="M9 61h12M9 64h8"/>'
                   '<circle class="box" cx="11" cy="78" r="3"/><circle class="box" cx="23" cy="78" r="3"/><path class="ln" d="M6 92h22M6 98h22M34 96h8"/>',
        "bed": '<path class="box" d="M42 84H276V110H42Z"/><path class="ln" d="M42 92H276"/><rect class="box" x="98" y="96" width="62" height="10" rx="1"/>'
               '<path class="ln" d="M50 110v6M268 110v6M46 116h226"/>',
        "clamp": '<rect class="box" x="44" y="46" width="44" height="38" rx="2"/><path class="ln" d="M52 56h28M52 74h28"/><rect class="box" x="88" y="58" width="16" height="14" rx="1"/>'
                 '<rect class="box" x="104" y="32" width="70" height="52" rx="2"/><path class="ln dash" d="M110 38h58v40h-58z"/>',
        "mould": '<path class="ln" d="M108 48H170M108 68H170"/><rect class="box" x="122" y="42" width="14" height="32" rx="1"/><rect class="box" x="137" y="42" width="14" height="32" rx="1"/>'
                 '<path class="ln hl" d="M136.5 40V76"/>',
        "hmi": '<path class="ln" d="M151 26V32"/><rect class="box" x="134" y="6" width="34" height="20" rx="2"/><path class="ln" d="M139 12h20M139 16h14M139 20h17"/>',
        "inject": '<path class="box" d="M170 54H178V62H170Z"/><rect class="box" x="178" y="52" width="48" height="12" rx="1"/>'
                  '<path class="ln" d="M186 52v12M194 52v12M210 52v12M218 52v12"/>'
                  '<rect class="box" x="226" y="44" width="48" height="28" rx="2"/><path class="ln" d="M232 52h36M232 58h36M232 64h36"/>',
        "hopper": '<path class="box" d="M188 22H216L208 38H196Z"/><rect class="box" x="198" y="38" width="8" height="14"/>',
    }
    if sensors:
        p["sensors"] = ('<circle class="sens" cx="143.5" cy="58" r="3"/><circle class="sens" cx="202" cy="58" r="3"/><circle class="sens" cx="174" cy="58" r="3"/>')
    if out:
        p["out"] = ('<path class="ln" d="M278 100H318"/><circle class="box" cx="284" cy="103" r="3"/><circle class="box" cx="312" cy="103" r="3"/>'
                    '<rect class="box" x="288" y="90" width="9" height="9" rx="1"/><rect class="box" x="302" y="90" width="9" height="9" rx="1"/>')
    return "".join(f'<g data-p="{k}">{v}</g>' for k, v in p.items())


def _machine(x, y, s=1.0, cls="", sensors=False, out=False):
    """The injection-moulding machine (imm_parts), placed at (x, y) and scaled; strokes keep their width (.imm in style.css)."""
    return f'<g class="glyph imm {cls}" transform="translate({x} {y}) scale({s})">{imm_parts(sensors, out)}</g>'


CAR_W, CAR_H = 200, 62           # the car's own size before scaling


def car_parts(sensors=False):
    """The everyday example: a car in side view (front to the right), with its battery under the floor. 200 × 62 units."""
    out = ('<path class="box" d="M6 50V38c0-5 3-8 9-9l40-4 22-15c3-2 6-3 10-3h40c5 0 8 1 11 4l18 16 32 4c5 1 8 4 8 9v10h-24a14 14 0 0 0-28 0H72a14 14 0 0 0-28 0Z"/>'
           '<path class="ln" d="M62 25l18-12c2-1 4-2 7-2h16v14ZM109 11h17c4 0 6 1 8 3l12 11h-37Z"/>'
           '<rect class="box batt" x="72" y="40" width="64" height="6" rx="1"/>'
           '<circle class="box" cx="58" cy="50" r="11"/><circle class="ln" cx="58" cy="50" r="3"/>'
           '<circle class="box" cx="158" cy="50" r="11"/><circle class="ln" cx="158" cy="50" r="3"/>')
    if sensors:
        out += '<circle class="sens" cx="104" cy="43" r="3"/>'
    return out


def _car(x, y, s=1.0, cls="", sensors=False):
    return f'<g class="glyph car {cls}" transform="translate({x} {y}) scale({s})">{car_parts(sensors)}</g>'


def _person(x, y, cls=""):
    return f'<g class="glyph person {cls}"><circle class="box" cx="{x}" cy="{y - 9}" r="4.5"/><path class="box" d="M{x - 7} {y + 6}c0-9 14-9 14 0z"/></g>'


# =====================================================================
# Static figures
# =====================================================================

SUPPORT = round((date(2025, 10, 14) - date(2015, 7, 29)).days / 365.25)      # Windows 10 support period, in years
assert SUPPORT == 10


def fig_lifespans(lang):
    """How long the original systems live (after Michael [Mic25], p. 2), against one software support period
    (Windows 10: 2015–2025, [W10]): a long-lived system sees many software generations."""
    L = lambda x: x[lang]
    rows = [(T("production machines", "Produktionsmaschinen"), 10, 15, "10–15"), (T("bridges", "Brücken"), 45, 55, "~50"),
            (T("airplanes, incl. maintenance", "Flugzeuge, inkl. Wartung"), 55, 70, T("up to 70", "bis 70")), (T("buildings", "Gebäude"), 80, 100, "80–100")]
    lab = lambda v: L(v) if isinstance(v, dict) else v
    t_sys = L(T("how long the system lives", "wie lange das System lebt"))
    t_sw = L(T(f"one software support period ({SUPPORT} years)", f"eine Software-Supportzeit ({SUPPORT} Jahre)"))

    def legend(x1, y1, x2, y2):
        return (f'<rect class="rest" x="{x1}" y="{y1 - 9}" width="18" height="10"/><text class="s" x="{x1 + 24}" y="{y1}">{t_sys}</text>'
                f'<rect class="lsw" x="{x2}" y="{y2 - 6}" width="18" height="4"/><text class="s" x="{x2 + 24}" y="{y2}">{t_sw}</text>')

    def chart(W, x0, sc, label_above):
        if label_above:      # phone: the two legend entries on their own lines
            out, y = legend(0, 14, 0, 32), 62
        else:
            out, y = legend(x0, 14, x0 + 220, 14), 44
        top = y - 12
        for k, (name, a, b, lb) in enumerate(rows):
            if label_above:
                out += f'<text x="{x0}" y="{y - 6}">{L(name)}</text>'
                y += 6
            else:
                out += f'<text x="{x0 - 12}" y="{y + 4}" text-anchor="end">{L(name)}</text>'
            out += (f'<rect class="rest" x="{x0}" y="{y - 6}" width="{a * sc:.1f}" height="12"/>'
                    f'<rect class="rest lsr" x="{x0 + a * sc:.1f}" y="{y - 6}" width="{(b - a) * sc:.1f}" height="12"/>'
                    f'<text class="s" x="{x0 + b * sc + 6:.1f}" y="{y + 4}">{lab(lb)}</text>')
            t = 0
            while t < b:                     # software generations along the life of the system
                w = min(SUPPORT, b - t) * sc - 2
                out += f'<rect class="lsw" x="{x0 + t * sc:.1f}" y="{y + 10}" width="{max(w, 1):.1f}" height="4"/>'
                t += SUPPORT
            y += 44 if not label_above else 46
        bottom = y - 22
        out += "".join(f'<path class="ln dash-guide" d="M{x0 + t * sc:.1f} {top}V{bottom}"/><text class="s" x="{x0 + t * sc:.1f}" y="{bottom + 14}" text-anchor="middle">{t}</text>' for t in (0, 25, 50, 75, 100))
        out += f'<text class="s" x="{x0 + 100 * sc:.1f}" y="{bottom + 28}" text-anchor="end">{L(T("years", "Jahre"))}</text>'
        aria = L(T("Lifespans: production machines 10 to 15 years, bridges about 50, airplanes up to 70, buildings 80 to 100 years; under each bar, software support periods of 10 years each",
                   "Lebensdauern: Produktionsmaschinen 10 bis 15 Jahre, Brücken etwa 50, Flugzeuge bis 70, Gebäude 80 bis 100 Jahre; unter jedem Balken Software-Supportzeiten von je 10 Jahren"))
        return f'<svg class="dia lifespans" viewBox="0 0 {W} {bottom + 34}" style="max-width:{W}px" role="img" aria-label="{aria}">{out}</svg>'

    svg = _pair(chart(784, 196, 5.2, False), chart(358, 8, 2.96, True))
    return fig(svg, T(f"<b>Systems that outlive their software.</b> Grey: how long the original system lives. Accent: software support periods of {SUPPORT} years — as long as Microsoft supported Windows 10 {r('W10')}. A bridge sees about five of them; its twin has to survive every one. Estimates of the lifespans vary between sources.",
                      f"<b>Systeme, die ihre Software überleben.</b> Grau: wie lange das Originalsystem lebt. Akzent: Software-Supportzeiten von {SUPPORT} Jahren — so lange hat Microsoft Windows 10 unterstützt {r('W10')}. Eine Brücke erlebt etwa fünf davon; ihr Zwilling muss jede überstehen. Die Schätzungen der Lebensdauern schwanken je nach Quelle."), lang,
               scroll=False, source=src("after", n("Mic25"), where="p. 2"))


def _wear(seed, n_=24, drop=6.0):
    """An illustrative battery-health trace of one car (100 % → about 100 - drop), deterministic."""
    vals, s = [], seed
    for k in range(n_):
        s = (s * 1103515245 + 12345) % 2 ** 31
        vals.append(100 - drop * k / (n_ - 1) + ((s % 100) / 100 - .5) * 1.2)
    return vals


def _spark(vals, x, y, w, h, lo=90, hi=101):
    return "M" + "L".join(f"{x + k * w / (len(vals) - 1):.1f} {y + (hi - v) / (hi - lo) * h:.1f}" for k, v in enumerate(vals))


def fig_lifecycle(lang):
    """One type, many instances: the development twin of a car model (Grieves: Digital Twin Prototype) and one twin per
    built car (Digital Twin Instance), each with its own tolerances and wear. Concept after the essay and GV17; data
    illustrative."""
    L = lambda x: x[lang]
    cars = [("…417", T("your car", "Ihr Auto"), 7, 5.0, "+0.2 mm"), ("…418", None, 3, 7.5, "−0.1 mm"), ("…419", None, 5, 3.5, "+0.1 mm")]
    t_dev = L(T("development twin", "Entwicklungszwilling"))
    t_type = L(T("car model · the type", "Automodell · der Typ"))
    t_art = L(T("CAD · bill of materials", "CAD · Stückliste"))
    t_none = L(T("no data from a real car", "keine Daten eines echten Autos"))
    t_built = L(T("built as", "gebaut als"))
    t_health = L(T("battery health", "Batteriezustand"))
    t_tol = L(T("tolerance", "Toleranz"))

    def wide():
        out = (f'<rect class="box hl" x="0" y="34" width="216" height="104" rx="3"/><text class="s" x="14" y="56">{t_type.upper()}</text>'
               f'<text class="t" x="14" y="78">{t_dev}</text><text x="14" y="100">{t_art}</text><text class="s" x="14" y="122">{t_none}</text>')
        for k, (vin, who, seed, drop, tol) in enumerate(cars):
            y = 22 + k * 46
            cls = "box hl" if who else "box"
            out += (f'<path class="ln" d="M216 86H272V{y + 18}H294"/>'
                    f'<rect class="{cls}" x="300" y="{y}" width="484" height="36" rx="3"/>'
                    f'<text class="t" x="314" y="{y + 23}">VIN {vin}</text>'
                    + (f'<text class="s a" x="384" y="{y + 23}">{L(who)}</text>' if who else "")
                    + f'<text class="s" x="454" y="{y + 23}">{t_tol} {tol}</text>'
                    f'<path class="{"spk a" if who else "spk"}" d="{_spark(_wear(seed, drop=drop), 568, y + 7, 200, 22)}"/>')
        out += f'<text class="s halo" x="222" y="80">{t_built}</text><text class="s" x="568" y="16">{t_health.upper()}</text>'
        axis = 172
        phases = [(T("design", "Entwurf"), 108), (T("manufacture", "Fertigung"), 300), (T("operation", "Betrieb"), 568), (T("end of life", "Lebensende"), 784)]
        out += f'<path class="ln" d="M0 {axis}H784"/>' + "".join(
            f'<circle class="dot" cx="{x}" cy="{axis}" r="3.5"/><text class="s" x="{x}" y="{axis + 18}" text-anchor="{"end" if x == 784 else "middle"}">{L(p)}</text>' for p, x in phases)
        return f'<svg class="dia" viewBox="0 0 784 {axis + 26}" role="img" aria-label="{aria}">{out}</svg>'

    def tall():
        out = (f'<rect class="box hl" x="0" y="0" width="358" height="84" rx="3"/><text class="s" x="12" y="18">{t_type.upper()} · {L(T("DESIGN", "ENTWURF"))}</text>'
               f'<text class="t" x="12" y="40">{t_dev}</text><text x="12" y="58">{t_art}</text><text class="s" x="12" y="74">{t_none}</text>'
               f'<text class="s" x="22" y="114">{L(T("MANUFACTURE → OPERATION", "FERTIGUNG → BETRIEB"))}</text><text class="s" x="358" y="114" text-anchor="end">{t_health.upper()}</text>')
        for k, (vin, who, seed, drop, tol) in enumerate(cars):
            y = 122 + k * 50
            out += (f'<path class="ln" d="M10 84V{y + 20}H16"/>'
                    f'<rect class="{"box hl" if who else "box"}" x="18" y="{y}" width="340" height="40" rx="3"/>'
                    f'<text class="t" x="28" y="{y + 18}">VIN {vin}</text>'
                    + (f'<text class="s a" x="100" y="{y + 18}">{L(who)}</text>' if who else "")
                    + f'<text class="s" x="28" y="{y + 32}">{t_tol} {tol}</text>'
                    f'<path class="{"spk a" if who else "spk"}" d="{_spark(_wear(seed, drop=drop), 230, y + 8, 116, 24)}"/>')
        out += f'<text class="s halo" x="16" y="97">{t_built}</text>'
        return f'<svg class="dia" viewBox="0 0 358 {122 + 3 * 50}" style="max-width:358px" role="img" aria-label="{aria}">{out}</svg>'

    aria = L(T("A car model's development twin, the type, during design; at manufacture it is built as three cars, each with a twin of its own that records its tolerance and its battery health over time",
               "Der Entwicklungszwilling eines Automodells, der Typ, im Entwurf; bei der Fertigung wird er als drei Autos gebaut, jedes mit eigenem Zwilling, der seine Toleranz und seinen Batteriezustand über die Zeit festhält"))
    return fig(_pair(wide(), tall()),
               T(f"<b>One type, many instances — like a class and its objects.</b> During design there is no car yet, so the twin is a <i>development twin</i> of the car model, valid for every car built from it. At manufacture each car gets a twin of its own that takes in its tolerances and, on the road, its wear. Grieves and Vickers call the two the <i>Digital Twin Prototype</i> and the <i>Digital Twin Instance</i> {r('GV17')}.",
                 f"<b>Ein Typ, viele Exemplare — wie eine Klasse und ihre Objekte.</b> Im Entwurf gibt es noch kein Auto, also ist der Zwilling ein <i>Entwicklungszwilling</i> des Automodells, gültig für jedes daraus gebaute Auto. Bei der Fertigung bekommt jedes Auto einen eigenen Zwilling, der seine Toleranzen und, auf der Straße, seinen Verschleiß aufnimmt. Grieves und Vickers nennen die beiden <i>Digital Twin Prototype</i> und <i>Digital Twin Instance</i> {r('GV17')}."),
               lang, scroll=False, source=src("illustrative", note=T("VINs, tolerances and battery health invented", "Fahrgestellnummern, Toleranzen und Batteriezustand erfunden")))


def fig_refarch(lang):
    """The reference architecture that grew out of the self-adaptive loop. After Heithoff et al. [HJM24], Fig. 5.2."""
    L = lambda x: x[lang]
    m = 'marker-end="url(#dtc)"'
    svg = f'''<svg class="dia refarch" viewBox="0 0 784 226" role="img" aria-label="{L(T("Reference architecture: gateways connect the machine; inside the twin, self-adaptivity services, process-awareness services and an optimiser work on a database; a cockpit connects the users", "Referenzarchitektur: Gateways verbinden die Maschine; im Zwilling arbeiten Selbstadaptivitäts-Services, prozessbewusste Services und ein Optimierer auf einer Datenbank; ein Cockpit verbindet die Nutzer"))}">
  {_arrow_defs("dtc")}
  {_machine(0, 96, .22)}
  <path class="ln" d="M72 110H90" {m}/>
  {box(94, 86, 104, 48, "Gateways", "OPC UA · MQTT")}
  <path class="ln" d="M198 110H214" {m}/>
  <rect class="zone" x="218" y="8" width="392" height="210" rx="6"/><text class="s" x="230" y="26">{L(T("THE TWIN · SERVICES", "DER ZWILLING · SERVICES"))}</text>
  <rect class="box hl" x="230" y="38" width="180" height="98" rx="3"/><text class="t" x="242" y="58">{L(T("self-adaptivity", "Selbstadaptivität"))}</text>
  <text class="s" x="242" y="80">{L(T("the loop above:", "die Schleife oben:"))}</text><text class="s" x="242" y="98">{L(T("processor · evaluator", "Prozessor · Evaluator"))}</text><text class="s" x="242" y="116">reasoner · executor</text>
  <rect class="box" x="420" y="38" width="180" height="98" rx="3"/><text class="t" x="432" y="58">{L(T("process awareness", "Prozessbewusstsein"))}</text>
  <text class="s" x="432" y="80">{L(T("process on track?", "Prozess im Plan?"))}</text><text class="s" x="432" y="98">{L(T("which steps happen?", "was passiert wann?"))}</text><text class="s" x="432" y="116">{L(T("whose turn is it?", "wer ist dran?"))}</text>
  {box(230, 146, 180, 30, L(T("optimiser", "Optimierer")))}
  {box(420, 146, 180, 30, L(T("data · models · shadows", "Daten · Modelle · Schatten")))}
  <path class="ln" d="M610 110H632" {m}/>
  {box(636, 86, 120, 48, "Cockpit", "UI")}
  <path class="ln" d="M696 134V164" {m}/>{_person(696, 186)}<text class="s" x="696" y="214" text-anchor="middle">{L(T("users", "Nutzer"))}</text>
</svg>'''
    return fig(svg, T("<b>From one loop to many services.</b> The self-adaptive loop — a variant of the classic monitor–analyse–plan–execute loop of self-adaptive systems (MAPE-K) — proved too rigid on its own, so later twins combine it with process-aware services (for example, noticing that opening the clamping unit takes too long), an optimiser and a cockpit.",
                      "<b>Von einer Schleife zu vielen Services.</b> Die selbstadaptive Schleife — eine Variante der klassischen Schleife selbstadaptiver Systeme aus Überwachen, Analysieren, Planen und Ausführen (MAPE-K) — erwies sich allein als zu starr; spätere Zwillinge kombinieren sie deshalb mit prozessbewussten Services (die etwa bemerken, dass das Öffnen der Schließeinheit zu lange dauert), einem Optimierer und einem Cockpit."),
               lang, source=src("after", n("HJM24"), where="Fig. 5.2", note=T("simplified", "vereinfacht")))


def fig_mde4dt(lang):
    """Engineering models and domain knowledge become the twin's models; generators build the twin. After Michael [Mic25], Fig. 3.1."""
    L = lambda x: x[lang]
    m, ma = 'marker-end="url(#dtd)"', 'marker-end="url(#dtda)"'
    from article_art import gear
    aria = L(T("Engineering models such as CAD, SysML or Modelica and domain knowledge become application-specific and application-independent models; generators turn them into the digital twin with its models, shadows, services and cockpit", "Engineering-Modelle wie CAD, SysML oder Modelica und Domänenwissen werden zu anwendungsspezifischen und anwendungsunabhängigen Modellen; Generatoren machen daraus den digitalen Zwilling mit Modellen, Schatten, Services und Cockpit"))
    svg = f'''<svg class="dia" viewBox="0 0 784 196" role="img" aria-label="{aria}">
  {_arrow_defs("dtd")}
  <text class="s" x="0" y="14">{L(T("WHAT EXISTS ALREADY", "WAS SCHON DA IST"))}</text>
  {box(0, 26, 172, 74, L(T("engineering models", "Engineering-Modelle")), "CAD · STEP · SysML", sub2="Modelica · AutomationML")}
  {box(0, 112, 172, 56, L(T("domain knowledge", "Domänenwissen")), L(T("experts, processes", "Fachleute, Prozesse")))}
  <path class="ln" d="M172 63H210" {m}/><path class="ln" d="M172 140H210" {m}/>
  <text class="s" x="214" y="14">{L(T("MODELS FOR THE TWIN", "MODELLE FÜR DEN ZWILLING"))}</text>
  {box(214, 26, 184, 60, L(T("application-specific", "anwendungsspezifisch")), L(T("this machine, these sensors", "diese Maschine, Sensoren")))}
  {box(214, 108, 184, 60, L(T("application-independent", "anwendungsunabhängig")), L(T("libraries, architecture", "Bibliotheken, Architektur")))}
  <path class="ln" d="M398 56H418V97H436M398 138H418V97" /><path class="ln hl" d="M418 97H444" {ma}/>
  <path class="gearf" d="{gear(482, 97, 32, 11)}"/><circle class="hubf" cx="482" cy="97" r="10"/><text class="s" x="482" y="150" text-anchor="middle">{L(T("generators", "Generatoren"))}</text>
  <path class="ln hl" d="M520 97H554" {ma}/>
  <rect class="box hl" x="560" y="20" width="224" height="152" rx="3"/><text class="t" x="576" y="44">{L(T("the digital twin", "der digitale Zwilling"))}</text>
  <text x="576" y="70">{L(T("models", "Modelle"))}</text><text x="576" y="90">{L(T("digital shadows", "digitale Schatten"))}</text>
  <text x="576" y="110">{L(T("services", "Services"))}</text><text x="576" y="130">{L(T("cockpit", "Cockpit"))}</text>
  <text class="s" x="576" y="158">{L(T("generated, then extended by hand", "generiert, dann von Hand erweitert"))}</text>
</svg>'''
    from project_content import box as _b
    t = f'''<svg class="dia" viewBox="0 0 358 452" style="max-width:358px" role="img" aria-label="{aria}">
  {_arrow_defs("dte")}
  <text class="s" x="0" y="12">{L(T("WHAT EXISTS ALREADY", "WAS SCHON DA IST"))}</text>
  {_b(0, 22, 172, 74, L(T("engineering models", "Engineering-Modelle")), "CAD · STEP · SysML", sub2="Modelica · AutomationML")}
  {_b(186, 22, 172, 74, L(T("domain knowledge", "Domänenwissen")), L(T("experts, processes", "Fachleute, Prozesse")))}
  <path class="ln" d="M86 96V128" marker-end="url(#dte)"/><path class="ln" d="M272 96V128" marker-end="url(#dte)"/>
  <text class="s" x="0" y="146">{L(T("MODELS FOR THE TWIN", "MODELLE FÜR DEN ZWILLING"))}</text>
  {_b(0, 156, 172, 60, L(T("application-specific", "anwendungsspezifisch")), L(T("this machine, these sensors", "diese Maschine, Sensoren")))}
  {_b(186, 156, 172, 60, L(T("application-independent", "anwendungsunabhängig")), L(T("libraries, architecture", "Bibliotheken, Architektur")))}
  <path class="ln" d="M86 216V232H272V216M179 232V242"/><path class="ln hl" d="M179 242V250" marker-end="url(#dtea)"/>
  <path class="gearf" d="{gear(179, 282, 26, 11)}"/><circle class="hubf" cx="179" cy="282" r="8"/><text class="s" x="216" y="286">{L(T("generators", "Generatoren"))}</text>
  <path class="ln hl" d="M179 312V330" marker-end="url(#dtea)"/>
  <rect class="box hl" x="0" y="336" width="358" height="112" rx="3"/><text class="t" x="16" y="358">{L(T("the digital twin", "der digitale Zwilling"))}</text>
  <text x="16" y="382">{L(T("models · digital shadows", "Modelle · digitale Schatten"))}</text><text x="16" y="402">{L(T("services · cockpit", "Services · Cockpit"))}</text>
  <text class="s" x="16" y="432">{L(T("generated, then extended by hand", "generiert, dann von Hand erweitert"))}</text>
</svg>'''
    svg = _pair(svg, t)
    return fig(svg, T("<b>Do not start from scratch.</b> Much of what a twin needs to know already exists as engineering models. Generating the twin from them reduces the effort and keeps twin and engineering consistent.",
                      "<b>Nicht bei null anfangen.</b> Vieles, was ein Zwilling wissen muss, existiert schon als Engineering-Modell. Den Zwilling daraus zu generieren, spart Aufwand und hält Zwilling und Engineering konsistent."),
               lang, scroll=False, source=src("after", n("Mic25"), where="Fig. 3.1", note=T("simplified", "vereinfacht")))


def fig_wind(lang):
    """Case study: the wind-turbine cooling system — class diagram, generated overview, the tools write back.
    After Michael et al. [MNN+22], Figs. 4–5, List. 2 (shortened; spelling of VolumeFlow normalised)."""
    L = lambda x: x[lang]
    cd = ["class Radiator {", "  String name;", "  Double minimalVolumeFlow;", "  Double coolingCapacity;", "}", "class Pump {", "  String name;", "  Double idealPower;",
          "  Double VolumeFlow;", "}", "class CoolingSystem {", "  String name;", "  Double /overallCoolingCapacity;", "}",
          "association CoolingSystem -> Radiator [*];", "association CoolingSystem -> Pump [*];"]
    py = ['obj = Factory.new(type_name="Radiator",', '        data={"name": "DIA_AB",', '              "minimalVolumeFlow": 300,', '              "coolingCapacity": 4000})', "obj.push()"]
    rows = [("MK01", "20", "30"), ("MK12_13", "40", "300"), ("MK2000", "120", "600")]
    tbl = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td><span class=\"pill-o\">{L(T('details', 'Details'))}</span></td></tr>" for a, b, c in rows)
    inner = f'''<div class="wind">
  <div><span class="k mono">{L(T("1 · THE MODEL: A CLASS DIAGRAM", "1 · DAS MODELL: EIN KLASSENDIAGRAMM"))}</span><pre class="mono">{_code(cd)}</pre></div>
  <div><span class="k mono">{L(T("2 · GENERATED: THE PUMP OVERVIEW", "2 · GENERIERT: DIE PUMPEN-ÜBERSICHT"))}</span>
    <div class="gp-card"><div class="gp-head">Pump</div><div class="gp-body"><table><tr><th>name</th><th>VolumeFlow</th><th>idealPower</th><th></th></tr>{tbl}</table></div></div>
    <span class="k mono" style="margin-top:16px">{L(T("3 · THE TOOLS WRITE BACK (PYTHON API)", "3 · DIE WERKZEUGE SCHREIBEN ZURÜCK (PYTHON-API)"))}</span><pre class="mono">{_code(py)}</pre>
    <p class="mono wind-rail">draft › review › released › outdated</p></div>
</div>'''
    cap = T("<b>A single source of truth for engineering parameters.</b> The cooling system of a wind turbine as a class diagram (“/” marks a value computed in hand-written code); MontiGem with CD2GUI generates the pages from it; the engineering tools read and write through a Python API; a release status protects what has been agreed.",
            "<b>Eine einzige Quelle für Engineering-Parameter.</b> Das Kühlsystem einer Windkraftanlage als Klassendiagramm („/“ markiert einen Wert, den handgeschriebener Code berechnet); MontiGem mit CD2GUI generiert daraus die Seiten; die Engineering-Werkzeuge lesen und schreiben über eine Python-API; ein Freigabestatus schützt, was vereinbart ist.")
    from article_common import source_line
    s = src("after", "MNN+22", where="Figs. 4–5, Listing 2", note=T("shortened", "gekürzt"))
    return f'<figure class="media art-fig">{inner}<figcaption class="mono">{L(cap)}{source_line(s, lang)}</figcaption></figure>'


def fig_sos(lang):
    """Twins of systems of systems, nested like their originals: car ⊃ powertrain ⊃ battery; a fleet twin aggregates the
    twins of many cars. Idea after Michael et al. [MPRW22], Fig. 1 (redrawn for a car)."""
    L = lambda x: x[lang]
    names = [T("car", "Auto"), T("powertrain", "Antriebsstrang"), T("battery", "Batterie")]

    def nest(x0, y0, w, h, digital):
        out = ""
        for k, nm in enumerate(names):
            d = 18 * k
            cls = "box hl" if digital and k == 0 else ("box gen-s" if digital else "box")
            out += f'<rect class="{cls}" x="{x0 + d}" y="{y0 + 34 * k}" width="{w - 2 * d}" height="{h - 34 * k - d}" rx="3"/>'
            out += f'<text class="t" x="{x0 + d + 12}" y="{y0 + 34 * k + 20}">{L(nm)}</text>'
        # inside the battery: cells (physical) or models + shadows (digital)
        bx, by = x0 + 48, y0 + 68 + 30
        if digital:
            out += "".join(f'<rect class="box" x="{bx + k * 6}" y="{by + k * 5}" width="40" height="18" rx="2"/>' for k in range(2))
            out += "".join(f'<rect class="box" x="{bx + 70}" y="{by + k * 12}" width="56" height="8" rx="2"/>' for k in range(3))
        else:
            out += "".join(f'<rect class="box" x="{bx + k * 18}" y="{by}" width="14" height="26" rx="1"/>' for k in range(7))
        return out

    def wide():
        out = f'<text class="s" x="0" y="14">{L(T("PHYSICAL", "PHYSISCH"))}</text><text class="s" x="330" y="14">{L(T("DIGITAL", "DIGITAL"))}</text>'
        out += nest(0, 24, 270, 160, False) + nest(330, 24, 270, 160, True)
        for k in range(3):                     # correspondence: from each physical container to its twin
            y = 24 + 34 * k + 16
            out += f'<path class="ln dash-guide" d="M{270 - 18 * k} {y}H{330 + 18 * k}"/>'
        out += (f'<path class="ln" d="M600 104H640"/>'
                + "".join(f'<rect class="box{" hl" if k == 2 else ""}" x="{644 + k * 8}" y="{64 + k * 10}" width="124" height="64" rx="3"/>' for k in range(3))
                + f'<text class="t" x="672" y="96">{L(T("fleet twin", "Flottenzwilling"))}</text><text class="s" x="672" y="114">{L(T("all car twins,", "Zwillinge aller"))}</text>'
                f'<text class="s" x="672" y="128">{L(T("aggregated", "Autos, aggregiert"))}</text>')
        return f'<svg class="dia" viewBox="0 0 784 188" role="img" aria-label="{aria}">{out}</svg>'

    def tall():
        out = f'<text class="s" x="0" y="14">{L(T("PHYSICAL", "PHYSISCH"))}</text>' + nest(0, 24, 358, 160, False)
        out += f'<text class="s" x="0" y="208">{L(T("DIGITAL", "DIGITAL"))}</text>' + nest(0, 218, 358, 160, True)
        out += (f'<path class="ln" d="M179 378V396"/><rect class="box" x="60" y="400" width="238" height="44" rx="3"/>'
                f'<text class="t" x="74" y="420">{L(T("fleet twin", "Flottenzwilling"))}</text><text class="s" x="74" y="436">{L(T("all car twins, aggregated", "alle Auto-Zwillinge, aggregiert"))}</text>')
        return f'<svg class="dia" viewBox="0 0 358 446" style="max-width:358px" role="img" aria-label="{aria}">{out}</svg>'

    aria = L(T("A car contains a powertrain, which contains a battery; their twins are nested the same way; a fleet twin aggregates the twins of many cars",
               "Ein Auto enthält einen Antriebsstrang, der eine Batterie enthält; ihre Zwillinge sind genauso verschachtelt; ein Flottenzwilling fasst die Zwillinge vieler Autos zusammen"))
    return fig(_pair(wide(), tall()),
               T(f"<b>Twins of twins.</b> “When composing a car chassis with a motor, the corresponding digital twins should be composed as well” {cite('FHM+23')} — today they are mostly built one by one. A fleet twin goes one level up and aggregates the twins of many cars. Composing twins raises open questions: integration across levels, intellectual property, rights and roles.",
                 f"<b>Zwillinge von Zwillingen.</b> Wer ein Fahrgestell mit einem Motor kombiniert, sollte auch ihre digitalen Zwillinge kombinieren {cite('FHM+23')} — heute entstehen sie meist einzeln. Ein Flottenzwilling geht eine Ebene höher und fasst die Zwillinge vieler Autos zusammen. Zwillinge zusammenzusetzen wirft offene Fragen auf: Integration über Ebenen hinweg, geistiges Eigentum, Rechte und Rollen."),
               lang, scroll=False, source=src("after", n("MPRW22"), where="Fig. 1", note=T("redrawn for a car", "für ein Auto neu gezeichnet")))


# =====================================================================
# Interactive figures (assets/dt.js)
# =====================================================================

def demo_ladder(lang):
    """dt1: model → shadow → twin, Kritzinger's data-flow view, on a car; and the person-in-between case (Formula 1)
    where the ladder and the RWTH definition differ."""
    L = lambda x: x[lang]
    ex = L(T("example: ours", "Beispiel: unseres"))
    states = [
        ("model", T("digital model", "digitales Modell"), "manual", "manual", T("No automated data flow in either direction. Example: the CAD model of your car — when the car changes, someone updates the model by hand.", "Kein automatischer Datenfluss, in keine Richtung. Beispiel: das CAD-Modell Ihres Autos — ändert sich das Auto, aktualisiert jemand das Modell von Hand."), ex),
        ("shadow", T("digital shadow", "digitaler Schatten"), "auto", "manual", T("Data flows automatically from the car to the digital object. Example: the app on your phone shows charge level and range, live — but nothing in it changes the car by itself.", "Daten fließen automatisch vom Auto zum digitalen Objekt. Beispiel: Die App auf Ihrem Handy zeigt Ladestand und Reichweite, live — aber nichts darin ändert von sich aus etwas am Auto."), ex),
        ("twin", T("digital twin", "digitaler Zwilling"), "auto", "auto", T("Data also flows back automatically. Example: from the battery data, the twin computes a gentler charging limit and sends it to the car — nobody types it in.", "Daten fließen auch automatisch zurück. Beispiel: Aus den Batteriedaten berechnet der Zwilling ein schonenderes Ladelimit und schickt es ans Auto — niemand tippt es ein."), ex),
        ("human", T("Kritzinger: shadow · RWTH: twin", "Kritzinger: Schatten · RWTH: Zwilling"), "auto", "human", T("Formula 1: telemetry flows from the car to the pit wall automatically, but the rules allow no data back to the car. Engineers advise the driver, who changes the settings. For Kritzinger that is only a shadow; the RWTH definition counts control through people.", "Formel 1: Telemetrie fließt automatisch vom Auto an die Boxenmauer, aber die Regeln erlauben keine Daten zurück ins Auto. Ingenieure beraten den Fahrer, der die Einstellungen ändert. Für Kritzinger ist das nur ein Schatten; die RWTH-Definition zählt Steuerung über Menschen mit."), f"{r('F1')} · {r('essay')}"),
    ]
    data = {"states": [{"id": i, "label": L(lab), "up": up, "down": dn, "quote": L(q), "src": s} for i, lab, up, dn, q, s in states]}
    btn = [T("model", "Modell"), T("shadow", "Schatten"), T("twin", "Zwilling"), T("person in between", "Mensch dazwischen")]
    buttons = "".join(f'<button type="button" data-v="{k}" class="{"first" if k == 3 else ""}" aria-pressed="{"true" if k == 1 else "false"}">{L(b)}</button>' for k, b in enumerate(btn))
    svg = f'''<svg class="dia ladder" viewBox="0 0 380 140" role="img" aria-label="{L(T("A car and a digital object, connected by an arrow towards the digital object and an arrow back", "Ein Auto und ein digitales Objekt, verbunden durch einen Pfeil hin zum digitalen Objekt und einen zurück"))}">
  {_car(0, 54, .7, sensors=True)}<text class="s" x="70" y="122" text-anchor="middle">{L(T("the original system", "das Originalsystem"))}</text>
  <rect class="box" x="252" y="30" width="124" height="74" rx="3"/><circle class="ln" cx="282" cy="60" r="15"/><path class="ln" d="M282 60l9-8"/><rect class="zone" x="306" y="48" width="56" height="10"/><rect class="zone" x="306" y="66" width="38" height="10"/>
  <text class="s" x="314" y="122" text-anchor="middle">{L(T("the digital object", "das digitale Objekt"))}</text>
  <g class="arr up" data-a="up">{_arrow(150, 50, 244, 50)}<text class="s alab halo" x="197" y="40" text-anchor="middle"></text></g>
  <g class="arr down" data-a="down">{_arrow(244, 88, 150, 88)}<text class="s alab halo" x="197" y="110" text-anchor="middle"></text>{_person(197, 90)}</g>
</svg>'''
    s0 = data["states"][1]
    data["words"] = {k: L(v) for k, v in dict(manual=T("manual", "manuell"), auto=T("automatic", "automatisch"), human=T("via a person", "über einen Menschen")).items()}
    inner = f'''<div class="d1-presets chips mono" role="group"><span class="k">{L(T("DATA FLOW:", "DATENFLUSS:"))}</span>{buttons}</div>
<div class="dl-grid">{svg}<div class="dl-out"><p class="dl-label" aria-live="polite">{s0["label"]}</p><p class="dl-quote">{s0["quote"]}</p><p class="dl-src mono">{s0["src"]}</p></div></div>'''
    return demo("dt1", data, inner, T("<b>Three words on one axis: how automatically does data flow?</b> A model is updated by hand, a shadow follows the system automatically, a twin also acts back on it. The ladder is intuitive — but it says nothing about what is inside the box, and it disagrees with the RWTH definition as soon as a person sits in the loop. What is inside the box → the next figure.",
                                      "<b>Drei Wörter auf einer Achse: Wie automatisch fließen die Daten?</b> Ein Modell wird von Hand aktualisiert, ein Schatten folgt dem System automatisch, ein Zwilling wirkt auch auf es zurück. Die Leiter ist eingängig — sie sagt aber nichts darüber, was in der Box steckt, und sie widerspricht der RWTH-Definition, sobald ein Mensch in der Schleife sitzt. Was in der Box steckt → die nächste Abbildung."),
                lang, source=src("after", n("Krit"), note=T(f"levels as described in {r('PZC25')}", f"Stufen wie in {r('PZC25')} beschrieben")))


ANATOMY_KEYS = ["original", "software", "models", "shadows", "update", "purpose", "services", "cockpit", "info", "commands"]
SERVICES = [("svc-mon", T("monitor", "überwachen")), ("svc-pred", T("predict", "vorhersagen")), ("svc-ctl", T("control", "steuern"))]


def demo_anatomy(lang):
    """dt2: the RWTH definition (v2.2), clause by clause, mapped onto the parts of a twin of a car; presets 'Is it a twin?'.
    Layout after Heithoff et al. [HHMR23], Fig. 1 (users / services / models + data / connectivity / original system)."""
    L = lambda x: x[lang]
    tabsvg = f'<g class="part" data-k="cockpit"><rect class="box hl" x="20" y="34" width="340" height="24" rx="3"/><text class="s" x="190" y="50" text-anchor="middle">{L(T("cockpit (UI)", "Cockpit (UI)"))}</text></g>'
    tabsvg += "".join(f'<g class="part" data-k="services {k}"><rect class="box" x="{20 + i * 116}" y="66" width="108" height="24" rx="3"/><text class="s" x="{74 + i * 116}" y="82" text-anchor="middle">{L(nm)}</text></g>' for i, (k, nm) in enumerate(SERVICES))
    models = "".join(f'<rect class="box" x="{20 + k * 8}" y="{120 + k * 20}" width="128" height="36" rx="3"/>' for k in range(3))
    models += "".join(f'<text x="{32 + k * 8}" y="{135 + k * 20}" class="s">{L(nm)}</text>' for k, nm in enumerate([T("structure", "Struktur"), T("behaviour", "Verhalten"), T("geometry", "Geometrie")]))
    pills = [T("range", "Reichweite"), T("overheating", "Überhitzung"), T("service due", "Wartung fällig")]
    shadows = "".join(f'<rect class="box" x="200" y="{120 + k * 28}" width="160" height="22" rx="3"/>' for k in range(3))
    purpose = "".join(f'<text class="s a" x="212" y="{135 + k * 28}">{L(T("for: ", "für: "))}{L(p)}</text>' for k, p in enumerate(pills))
    svg = f'''<svg class="dia anat" viewBox="0 0 380 340" role="group" aria-label="{L(T("Anatomy of a digital twin: inside a software boundary, a cockpit on top, three services, models and purpose-bound digital shadows below, both updated regularly; data comes up from the original system, a car; information and commands go back down", "Anatomie eines digitalen Zwillings: in einer Softwaregrenze oben ein Cockpit, drei Services, darunter Modelle und zweckgebundene digitale Schatten, beide regelmäßig aktualisiert; Daten kommen vom Originalsystem herauf, einem Auto; Informationen und Befehle gehen zurück"))}">
  <g class="part" data-k="software"><rect class="sw" x="8" y="10" width="364" height="236" rx="6"/><text class="s" x="20" y="26">{L(T("SOFTWARE", "SOFTWARE"))}</text></g>
  {tabsvg}
  <g class="part" data-k="models">{models}<text class="s" x="20" y="112">{L(T("MODELS", "MODELLE"))}</text></g>
  <g class="part" data-k="update"><circle class="box" cx="30" cy="224" r="10"/><path class="ln" d="M30 217v7l5 3"/><text class="s" x="46" y="228">{L(T("updated regularly", "regelmäßig aktualisiert"))}</text></g>
  <g class="part" data-k="shadows">{shadows}<text class="s" x="200" y="112">{L(T("DIGITAL SHADOWS", "DIGITALE SCHATTEN"))}</text></g>
  <g class="part" data-k="purpose">{purpose}</g>
  <g class="part" data-k="original"><rect class="box" x="8" y="282" width="364" height="50" rx="3"/>{_car(20, 290, .42)}<text class="t" x="118" y="312">{L(T("the original system: a car", "das Originalsystem: ein Auto"))}</text></g>
  <g class="part" data-k="shadows">{_arrow(320, 280, 320, 204)}<text class="s halo" x="326" y="266">{L(T("data", "Daten"))}</text></g>
  <g class="part" data-k="info">{_arrow(150, 248, 150, 278)}<text class="s halo" x="156" y="268">{L(T("information", "Information"))}</text></g>
  <g class="part" data-k="commands">{_arrow(250, 248, 250, 278, "ln hl")}<text class="s a halo" x="256" y="268">{L(T("commands", "Befehle"))}</text></g>
</svg>'''
    c = lambda k, en, de: (k, T(en, de))
    sentence = [T("A digital twin ", "Ein digitaler Zwilling "), c("original", "of an original system", "eines Originalsystems"), " ", c("software", "is a software", "ist eine Software"),
                T(" that consists of ", ", die besteht aus "), c("models", "a set of models", "einer Menge von Modellen"), T(" … and ", " … und "),
                c("shadows", "a set of digital shadows", "einer Menge digitaler Schatten"), T(", both of which are ", ", die beide "), c("purpose", "purposefully", "zweckgerichtet"), " ",
                c("update", "updated on a regular basis", "regelmäßig aktualisiert"), T(", and provides ", " werden, und "), c("services", "a set of services", "eine Menge von Services"),
                T(" … It interacts with the original system by ", " bereitstellt … Er interagiert mit dem Originalsystem, indem er "), c("info", "providing useful information", "nützliche Informationen liefert"),
                T(" … and ", " … und "), c("commands", "sending it control commands", "ihm Steuerbefehle sendet"), "."]
    def piece(p):
        if isinstance(p, tuple):
            return f'<button type="button" class="cl" data-k="{p[0]}">{L(p[1])}</button>'
        return L(p) if isinstance(p, dict) else p
    # a clause and the punctuation after it stay on one line (a button is an atomic inline, so a line may break after it)
    clauses = re.sub(r'(<button [^>]*class="cl"[^>]*>[^<]*</button>)([,.])', lambda m: f'<span class="nw">{m[1]}{m[2]}</span>', "".join(piece(p) for p in sentence))
    presets = [
        ("cad", T("a CAD file", "eine CAD-Datei"), ["models"], T("Models only — a “digital model” on the ladder. No data from the real car, no services, no way back.", "Nur Modelle — ein „digitales Modell“ auf der Leiter. Keine Daten aus dem echten Auto, keine Services, kein Rückweg.")),
        ("dash", T("the live app", "die Live-App"), ["shadows", "update", "purpose", "cockpit", "original", "info"], T("Charge level and range, shown for one purpose — a digital shadow plus a display. No models, no commands.", "Ladestand und Reichweite, für einen Zweck angezeigt — ein digitaler Schatten plus Anzeige. Keine Modelle, keine Befehle.")),
        ("sim", T("a simulation", "eine Simulation"), ["models", "svc-pred", "software"], T("Models and a service that predicts — but no data from the real car: a twin is “not only a simulation model”.", "Modelle und ein Service, der vorhersagt — aber keine Daten aus dem echten Auto: Ein Zwilling ist „nicht nur ein Simulationsmodell“.")),
        ("type", T("a car model in design", "ein Automodell im Entwurf"), ["models", "software", "cockpit", "update", "purpose"], T("Models, a cockpit and agreed parameters — but no data from a real car and no commands yet: a development twin, the twin of a type.", "Modelle, ein Cockpit und vereinbarte Parameter — aber keine Daten eines echten Autos und noch keine Befehle: ein Entwicklungszwilling, der Zwilling eines Typs.")),
        ("twin", T("the twin", "der Zwilling"), ANATOMY_KEYS + [k for k, _ in SERVICES], T("Everything the definition asks for: models and shadows, kept up to date for a purpose, services that use them, and a way back — information and commands.", "Alles, was die Definition verlangt: Modelle und Schatten, zweckgerichtet aktuell gehalten, Services, die sie nutzen, und ein Rückweg — Informationen und Befehle.")),
    ]
    data = {"presets": [{"id": i, "on": on, "verdict": L(v)} for i, _, on, v in presets]}
    pbtn = "".join(f'<button type="button" data-v="{k}" class="{"first" if k == 1 else ""}" aria-pressed="{"true" if k == 4 else "false"}">{L(nm)}</button>' for k, (_, nm, _, _) in enumerate(presets))
    inner = f'''<div class="d1-presets chips mono" role="group"><span class="k">{L(T("IS IT A TWIN?", "IST ES EIN ZWILLING?"))}</span>{pbtn}</div>
<div class="anat-grid">{svg}<div class="anat-side"><p class="anat-def" role="group" aria-label="{L(T("The clauses of the definition", "Die Teile der Definition"))}">{clauses}</p>
<p class="anat-verdict" aria-live="polite">{L(presets[4][3])}</p></div></div>'''
    return demo("dt2", data, inner, T("<b>Every clause of the definition is a part of the twin.</b> Point at an underlined clause to find its part — or at a part to find its clause. Then check everyday artefacts: a dashboard is shadows plus a display, a CAD file only the model corner, and a car model in design is the twin of a type.",
                                      "<b>Jeder Teil der Definition ist ein Teil des Zwillings.</b> Zeigen Sie auf eine unterstrichene Formulierung, um ihren Teil zu finden — oder auf einen Teil, um seine Formulierung zu finden. Dann prüfen Sie Alltagsdinge: Ein Dashboard ist ein Schatten plus Anzeige, eine CAD-Datei nur die Modell-Ecke, und ein Automodell im Entwurf ist der Zwilling eines Typs."),
                lang, source=src("after", n("HHMR23"), where="Fig. 1", note=T("layout; verdicts ours", "Aufbau; Urteile von uns")))


# ---- dt3: one car's raw telemetry, three shadows (fictional data; the answers are computed from it) ----
TELEMETRY = [("07:40", 29812, 81, 24), ("08:05", 29836, 74, 29), ("12:10", 29836, 74, 22), ("17:30", 29861, 66, 27),
             ("17:55", 29870, 58, 31), ("18:20", 29870, 62, 38), ("18:35", 29870, 71, 47), ("18:50", 29870, 79, 49)]
HOT, SERVICE_AT = 45, 30000


def _shadow_views():
    rows = TELEMETRY
    charge = rows[-1][2]
    km = max(r_[1] for r_ in rows)
    last2 = [r_[3] for r_ in rows[-2:]]
    hot = all(t > HOT for t in last2)
    assert (charge, km, last2, hot) == (79, 29870, [47, 49], True)          # the texts below quote these numbers
    fmt = lambda v: f"{v:,}".replace(",", " ")
    return [
        dict(q=T("Charge now?", "Jetzt laden?"), rows=[len(rows) - 1], col=2,
             sql=["CREATE VIEW charge_now AS", "  SELECT charge FROM telemetry", "  ORDER BY time DESC LIMIT 1;"],
             a=T(f"{charge} % — no need to charge yet.", f"{charge} % — noch kein Laden nötig."),
             note=T("The latest value of one column.", "Der jüngste Wert einer Spalte.")),
        dict(q=T("Service due?", "Wartung fällig?"), rows=list(range(len(rows))), col=1,
             sql=["CREATE VIEW service_due AS", "  SELECT max(km) >= 30000", "  FROM telemetry;"],
             a=T(f"No — {fmt(km)} km; service at {fmt(SERVICE_AT)} km.", f"Nein — {fmt(km)} km; Wartung bei {fmt(SERVICE_AT)} km."),
             note=T("All rows, condensed to one number.", "Alle Zeilen, zu einer Zahl verdichtet.")),
        dict(q=T("Is the battery overheating?", "Überhitzt die Batterie?"), rows=[len(rows) - 2, len(rows) - 1], col=3,
             sql=["CREATE VIEW overheating AS", f"  SELECT min(battery) > {HOT} FROM (", "    SELECT battery FROM telemetry", "    ORDER BY time DESC LIMIT 2);"],
             a=T(f"Yes — the last two readings are {last2[0]} °C and {last2[1]} °C.", f"Ja — die letzten beiden Messwerte sind {last2[0]} °C und {last2[1]} °C."),
             note=T("The last two values, compared with a threshold.", "Die letzten beiden Werte, mit einer Schwelle verglichen.")),
    ]


def demo_shadows(lang):
    """dt3: one raw telemetry table of a car, three purposes, three views (CREATE VIEW). The idea that a shadow is like a
    database view is from Brauner et al. [BDJ22]; the data are fictional."""
    L = lambda x: x[lang]
    views = _shadow_views()
    head = [T("time", "Zeit"), "km", T("charge %", "Ladung %"), T("battery °C", "Batterie °C")]
    th = "".join(f'<th data-c="{k}">{L(h) if isinstance(h, dict) else h}</th>' for k, h in enumerate(head))
    trs = "".join(f'<tr data-r="{i}">' + "".join(f'<td data-c="{k}">{(f"{v:,}".replace(",", " ") if k == 1 else v)}</td>' for k, v in enumerate(row)) + "</tr>"
                  for i, row in enumerate(TELEMETRY))
    table = f'<div class="sh-raw"><span class="k mono">{L(T("RAW DATA · ONE TABLE", "ROHDATEN · EINE TABELLE"))}</span><table class="sh-tbl mono"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'
    data = {"states": [{"rows": v["rows"], "col": v["col"], "sql": _code(v["sql"]), "a": L(v["a"]), "note": L(v["note"])} for v in views]}
    buttons = "".join(f'<button type="button" data-v="{k}" class="{"first" if k == 2 else ""}" aria-pressed="{"true" if k == 0 else "false"}">{L(v["q"])}</button>' for k, v in enumerate(views))
    s0 = data["states"][0]
    inner = f'''<div class="d1-presets chips mono" role="group"><span class="k">{L(T("PURPOSE:", "ZWECK:"))}</span>{buttons}</div>
<div class="sh-grid">{table}<div class="sh-card"><span class="k mono">{L(T("THE SHADOW · A VIEW", "DER SCHATTEN · EINE SICHT"))}</span><pre class="mono">{s0["sql"]}</pre>
<p class="sh-ans" aria-live="polite">{s0["a"]}</p><p class="sh-note">{s0["note"]}</p></div></div>'''
    return demo("dt3", data, inner, T(f"<b>The same data, three shadows.</b> Each purpose picks other rows and columns of the same raw data and condenses them differently: the latest value, a maximum, the last two readings against a threshold. None of them acts — a shadow answers a question; it can be compared to a view in a database {r('BDJ22')}.",
                                      f"<b>Dieselben Daten, drei Schatten.</b> Jeder Zweck wählt andere Zeilen und Spalten derselben Rohdaten und verdichtet sie anders: der jüngste Wert, ein Maximum, die letzten beiden Messwerte gegen eine Schwelle. Keiner handelt — ein Schatten beantwortet eine Frage; er lässt sich mit einer Sicht in einer Datenbank vergleichen {r('BDJ22')}."),
                lang, source=src("fictional"))


LOOP_CODE = {
    "event": ["event TempTooHigh for PlasticizingPhase {", "  checkTemp@(-1) > 500", "  && checkTemp@(0) > 500", "}"],
    "goal": ["action ReduceTemp for PlasticizingPhase {", "  new ReduceTempGoal(checkTemp@(0), 500);", "}", "rule TempTooHigh => ReduceTemp;"],
    "case": ["case Overheating(ReduceTempGoal goal) {", "  if goal.currentValue > goal.targetValue;", "  do HeatingUnit.reduceTemp(targetValue);", "  yields", "    goal.currentValue <= goal.targetValue;", "}"],
}


def demo_loop(lang):
    """dt4: the self-adaptive loop of the injection-moulding twin, one round, automatic or with an operator approving in
    the cockpit (drawn in the loop). After Dalibor et al. [DHM+22] Fig. 2 and Fur et al. [FHM+23] Fig. 2, both after
    Bibow et al. [BDH20]; code from DHM+22 Figs. 17–18. Temperatures illustrative."""
    L = lambda x: x[lang]
    comps = {"ev": (16, 24, "Evaluator", T("notice a problem", "ein Problem bemerken")), "re": (224, 24, "Reasoner", T("choose a fix", "eine Lösung wählen")),
             "dp": (16, 128, L(T("Data processor", "Datenprozessor")), T("collect & prepare", "sammeln & aufbereiten")), "ex": (224, 128, "Executor", T("send the command", "den Befehl senden"))}
    boxes = "".join(f'<g class="lp" data-c="{k}"><rect class="box" x="{x}" y="{y}" width="140" height="52" rx="3"/><text class="t" x="{x + 70}" y="{y + 23}" text-anchor="middle">{nm}</text>'
                    f'<text class="s" x="{x + 70}" y="{y + 40}" text-anchor="middle">{L(s)}</text></g>' for k, (x, y, nm, s) in comps.items())
    conns = [("lake", (226, 246, 156, 246), T("data", "Daten"), 170, 240, "start"), ("lakedp", (86, 216, 86, 184), None, 0, 0, ""),
             ("dpev", (60, 128, 60, 80), T("machine state", "Maschinenzustand"), 66, 108, "start"), ("evre", (156, 50, 218, 50), T("goals", "Ziele"), 187, 42, "middle"),
             ("reck", (294, 76, 294, 86), None, 0, 0, ""), ("ckex", (294, 110, 294, 124), None, 0, 0, ""),
             ("excpps", (250, 180, 250, 214), T("command", "Befehl"), 244, 202, "end"), ("cppsex", (340, 214, 340, 184), T("feedback", "Rückmeldung"), 334, 202, "end")]
    lines = "".join(f'<g class="lc" data-c="{k}">{_arrow(*xy)}' + (f'<text class="s halo" x="{tx}" y="{ty}" text-anchor="{an}">{L(lab)}</text>' if lab else "") + "</g>"
                    for k, xy, lab, tx, ty, an in conns)
    svg = f'''<svg class="dia loop" viewBox="0 0 380 304" role="img" aria-label="{L(T("The self-adaptive loop: data processor, evaluator, reasoner, cockpit and executor; below them the raw data store and the machine", "Die selbstadaptive Schleife: Datenprozessor, Evaluator, Reasoner, Cockpit und Executor; darunter der Rohdatenspeicher und die Maschine"))}">
  <rect class="zone" x="6" y="8" width="368" height="190" rx="6"/><text class="s" x="190" y="20" text-anchor="middle">{L(T("THE TWIN", "DER ZWILLING"))}</text>
  {boxes}
  <g class="lp ck" data-c="cockpit"><rect class="box" x="249" y="88" width="90" height="22" rx="3"/><text class="s" x="294" y="103" text-anchor="middle">cockpit</text></g>
  <g class="lp" data-c="lake"><path class="box" d="M70 226v26c0 5 18 8 40 8s40-3 40-8v-26"/><ellipse class="box" cx="110" cy="226" rx="40" ry="8"/><text class="s" x="110" y="282" text-anchor="middle">{L(T("raw data store", "Rohdatenspeicher"))}</text></g>
  <g class="lp" data-c="cpps">{_machine(226, 220, .42)}<text class="s" x="293" y="284" text-anchor="middle">{L(T("the machine", "die Maschine"))}</text><text class="s a lp-temp" x="293" y="299" text-anchor="middle"></text></g>
  {lines}
</svg>'''
    hot, cool = L(T("barrel: 524 °C", "Zylinder: 524 °C")), L(T("barrel: 496 °C ✓", "Zylinder: 496 °C ✓"))
    states = [
        (["cpps"], ["lake"], ["// raw readings stream in"], T("The machine streams its raw data into the raw data store.", "Die Maschine schickt ihre Rohdaten in den Rohdatenspeicher."), hot),
        (["dp"], ["lakedp", "dpev"], ["checkTemp@(-1), checkTemp@(0)"], T("The data processor builds the shadow the evaluator needs: the last two temperature readings.", "Der Datenprozessor baut den Schatten, den der Evaluator braucht: die letzten beiden Temperaturwerte."), hot),
        (["ev"], [], LOOP_CODE["event"], T("The evaluator checks an event model: both readings above 500? Then the event fires.", "Der Evaluator prüft ein Ereignismodell: Beide Werte über 500? Dann tritt das Ereignis ein."), hot),
        (["ev"], ["evre"], LOOP_CODE["goal"], T("A rule turns the event into a goal: the temperature should come down to 500.", "Eine Regel macht aus dem Ereignis ein Ziel: Die Temperatur soll auf 500 sinken."), hot),
        (["re"], [], LOOP_CODE["case"], T("The reasoner finds a case that matches the goal — what to do, and what should be true afterwards.", "Der Reasoner findet einen passenden Fall — was zu tun ist und was danach gelten soll."), hot),
        (["re"], ["reck"], ["HeatingUnit.reduceTemp(targetValue)"], T("Proposal ready.", "Vorschlag fertig."), hot),
        (["ex"], ["reck", "ckex", "excpps"], ["HeatingUnit.reduceTemp(targetValue)   // via a protocol plugin, e.g. OPC UA"], T("The executor sends the command to the machine.", "Der Executor sendet den Befehl an die Maschine."), hot),
        (["ex", "cpps"], ["cppsex"], ["yields goal.currentValue <= goal.targetValue"], T("Feedback: the goal is reached. The loop runs on with the next readings.", "Rückmeldung: Das Ziel ist erreicht. Die Schleife läuft mit den nächsten Werten weiter."), cool),
    ]
    data = {"steps": [{"c": c, "l": l, "code": _code(code), "say": L(say), "temp": tmp} for c, l, code, say, tmp in states], "hold": 5,
            "words": {k: L(v) for k, v in dict(auto=T("Automatic: nobody is asked; the proposal passes the cockpit.", "Automatisch: Niemand wird gefragt; der Vorschlag läuft am Cockpit vorbei."),
                                                  human=T("Operator approves: the proposal waits in the cockpit.", "Bedienerin gibt frei: Der Vorschlag wartet im Cockpit.")).items()}}
    _check_loop(states)
    inner = f'''<div class="d1-presets chips mono" role="group"><span class="k">{L(T("MODE:", "MODUS:"))}</span><button type="button" data-m="auto" aria-pressed="true">{L(T("automatic", "automatisch"))}</button><button type="button" data-m="human" class="first" aria-pressed="false">{L(T("operator approves", "Bedienerin gibt frei"))}</button></div>
<div class="lp-grid">{svg}<div class="lp-side"><p class="lp-say" aria-live="polite">{data["steps"][0]["say"]}</p><pre class="mono lp-code">{data["steps"][0]["code"]}</pre>
<div class="lp-row"><button type="button" class="approve mono" disabled>{L(T("approve", "freigeben"))} ✓</button><p class="lp-msg mono"></p></div></div></div>{controls(lang)}'''
    return demo("dt4", data, inner, T(f"<b>The twin’s intelligence is a chain of small, editable models.</b> An event model says when to act, a goal what should become true, a case how to get there. Switch to <i>operator approves</i>: the loop stops at the cockpit until someone releases the proposal — some users do not want automatic execution, for fear of stopping a whole production line because of a wrong setting {r('Mic25')}. The architecture stays the same; one step changes.",
                                      f"<b>Die Intelligenz des Zwillings ist eine Kette kleiner, änderbarer Modelle.</b> Ein Ereignismodell sagt, wann gehandelt wird, ein Ziel, was gelten soll, ein Fall, wie man hinkommt. Schalten Sie auf <i>Bedienerin gibt frei</i>: Die Schleife hält am Cockpit, bis jemand den Vorschlag freigibt — manche Nutzer wollen keine automatische Ausführung, aus Sorge, eine falsche Einstellung könnte eine ganze Produktionslinie stoppen {r('Mic25')}. Die Architektur bleibt gleich; ein Schritt ändert sich."),
                lang, source=src("after", "DHM+22", where="Figs. 2, 17, 18", note=T("temperatures illustrative", "Temperaturen illustrativ")))


def _check_loop(states):
    joined = "\n".join(l for _, _, code, _, _ in states for l in code)
    for block in LOOP_CODE.values():
        for line in block:
            assert line in joined, line


# the platform's feature model (DHM+22 Fig. 7): (group, choice, plain label, acronym/tooltip, chosen)
FEATURES = [("evaluate", "SAT Evaluator", T("logic rules", "Logikregeln"), "SAT evaluator", True), ("evaluate", "Expression Evaluator", T("expressions", "Ausdrücke"), "", False),
            ("reason", "CBR", T("reuse past fixes", "frühere Lösungen wiederverwenden"), "case-based reasoning (CBR)", True), ("reason", "PDDL", T("plan steps", "Schritte planen"), "PDDL planner", False),
            ("reason", "SCIP", T("optimise", "optimieren"), "SCIP optimiser", False), ("communicate", "MQTT", T("MQTT · REST", "MQTT · REST"), "MQTT and REST endpoints", True),
            ("execute", "Command Executor", T("send commands", "Befehle senden"), "Command Executor", True)]
GROUPS = {"evaluate": T("evaluate", "auswerten"), "reason": T("reason", "schlussfolgern"), "communicate": T("communicate", "kommunizieren"), "execute": T("execute", "ausführen")}


def _check_features():
    """The lit configuration must be valid for DHM+22 Fig. 7: exactly one evaluator, at least one executor."""
    on = [f for f in FEATURES if f[4]]
    assert sum(f[0] == "evaluate" for f in on) == 1
    assert sum(f[0] == "execute" for f in on) >= 1
    assert len(on) == 4


def demo_roles(lang):
    """dt5: who builds the twin? MontiGem generates a low-code platform, the platform produces twins; three roles.
    After Dalibor et al. [DHM+22] Fig. 5 (quadrants), Fig. 7 (feature diagram), Figs. 12–13, 16a; values illustrative."""
    L = lambda x: x[lang]
    from article_art import gear
    designer = T("twin designer", "Zwillings-Designerin")
    svg = f'''<svg class="dia roles" viewBox="0 0 380 244" role="img" aria-label="{L(T("Four quadrants: design-time models, generated by MontiGem into a low-code platform; the platform's twin models, generated into twin instances; a person at the design-time models, at the twin models and at the twin instances", "Vier Quadranten: Design-Time-Modelle, von MontiGem zu einer Low-Code-Plattform generiert; die Zwillingsmodelle der Plattform, zu Zwillings-Instanzen generiert; je eine Person bei den Design-Time-Modellen, den Zwillingsmodellen und den Zwillings-Instanzen"))}">
  <g class="q" data-q="0"><rect class="box" x="4" y="8" width="142" height="80" rx="3"/><text class="t" x="14" y="28">{L(T("design-time models", "Design-Time-Modelle"))}</text><text class="s" x="14" y="46">{L(T("+ language plugins", "+ Sprach-Plugins"))}</text><text class="s" x="14" y="76"><title>CD · GUI · OCL</title>{L(T("data, GUI, rules", "Daten, GUI, Regeln"))}</text></g>
  <g class="q" data-q="0">{_person(16, 118)}<text class="s" x="28" y="118">{L(T("platform engineer", "Plattform-Ingenieurin"))}</text></g>
  <g class="q" data-q="g1"><path class="gearf" d="{gear(190, 48, 18, 9)}"/><circle class="hubf" cx="190" cy="48" r="6"/><text class="s" x="190" y="84" text-anchor="middle">MontiGem</text></g>
  <g class="q" data-q="1"><rect class="box" x="234" y="8" width="142" height="80" rx="3"/><text class="t" x="244" y="28">{L(T("low-code platform", "Low-Code-Plattform"))}</text><text class="s" x="244" y="46">{L(T("editors · viewers", "Editoren · Viewer"))}</text><text class="s" x="244" y="76">{L(T("model library", "Modellbibliothek"))}</text></g>
  <path class="ln" d="M370 88V128"/>
  <g class="q" data-q="2"><rect class="box" x="234" y="132" width="142" height="80" rx="3"/><text class="t" x="244" y="152">{L(T("twin models", "Zwillingsmodelle"))}</text><text class="s" x="244" y="170">{L(T("configured, no code", "kein Code nötig"))}</text><text class="s" x="244" y="200"><title>OCL · comm · case</title>{L(T("rules, cases, …", "Regeln, Fälle, …"))}</text></g>
  <g class="q" data-q="2">{_person(352 - 6.5 * len(L(designer)), 118)}<text class="s" x="362" y="118" text-anchor="end">{L(designer)}</text></g>
  <g class="q" data-q="g2"><path class="gearf" d="{gear(190, 172, 18, 9)}"/><circle class="hubf" cx="190" cy="172" r="6"/><text class="s" x="190" y="204" text-anchor="middle">{L(T("twin", "Zwillings-"))}</text><text class="s" x="190" y="216" text-anchor="middle">{L(T("generator", "generator"))}</text></g>
  <g class="q" data-q="3"><rect class="box" x="4" y="132" width="142" height="80" rx="3"/><text class="t" x="14" y="152">{L(T("twin instances", "Zwillings-Instanzen"))}</text><text class="s" x="14" y="170">{L(T("cockpit per machine", "Cockpit je Maschine"))}</text></g>
  <g class="q" data-q="3">{_person(16, 236)}<text class="s" x="28" y="236">{L(T("domain expert", "Domänenexpertin"))}</text></g>
  <path class="ln" d="M146 48H168M212 48H230M234 172H212M168 172H150"/>
</svg>'''
    _check_features()
    tree = (f'<ul class="feat mono"><li class="root">{L(T("the platform offers", "die Plattform bietet"))}</li>'
            + "".join(f'<li title="{esc(tip)}"><span>{L(GROUPS[g])}</span>{L(lab)}</li>' for g, _, lab, tip, on in FEATURES if on) + "</ul>")
    case = LOOP_CODE["case"][:3] + ["  …"]
    log = [("10:02", T("running", "läuft"), ""), ("10:14", T("overheating", "Überhitzung"), T("barrel set to 500 °C", "Zylinder auf 500 °C gesetzt")), ("10:31", T("running", "läuft"), "")]
    cockpit = (f'<div class="gp-card"><div class="gp-head">{L(T("Machine state", "Maschinenzustand"))}</div><div class="gp-body"><table><tr><th>{L(T("time", "Zeit"))}</th><th>{L(T("state", "Zustand"))}</th><th>{L(T("the twin did", "der Zwilling tat"))}</th></tr>'
               + "".join(f'<tr><td>{t}</td><td>{L(s)}</td><td>{L(d) if d else "—"}</td></tr>' for t, s, d in log) + "</table></div></div>")
    panels = [
        (T("1 · The platform engineer", "1 · Die Plattform-Ingenieurin"), T("chooses the building blocks of the platform — how it evaluates, reasons, communicates and acts. MontiGem generates the low-code platform from that choice.", "wählt die Bausteine der Plattform — wie sie auswertet, schlussfolgert, kommuniziert und handelt. MontiGem generiert daraus die Low-Code-Plattform."), tree, [0, "g1", 1]),
        (T("2 · The twin designer", "2 · Die Zwillings-Designerin"), T("configures one twin in the platform with small models — for example, how to fix overheating. No code.", "konfiguriert in der Plattform einen Zwilling mit kleinen Modellen — etwa, wie Überhitzung behoben wird. Kein Code."),
         f'<pre class="mono">{_code(case)}</pre>', [1, 2, "g2"]),
        (T("3 · The domain expert", "3 · Die Domänenexpertin"), T("uses the generated twin: its cockpit shows the machine’s states and what the twin did — the loop you just ran.", "nutzt den generierten Zwilling: Sein Cockpit zeigt die Zustände der Maschine und was der Zwilling getan hat — die Schleife von eben."), cockpit, [3]),
    ]
    data = {"steps": [{"title": L(t), "text": L(x), "html": h, "q": [str(q) for q in qs]} for t, x, h, qs in panels],
            "words": {k: L(v) for k, v in dict(step=T("role", "Rolle"), of=T("of", "von")).items()}}
    p0 = data["steps"][0]
    inner = f'''<div class="ro-grid">{svg}<div class="ro-side"><p class="ro-title t">{p0["title"]}</p><p class="ro-text" aria-live="polite">{p0["text"]}</p><div class="ro-html">{p0["html"]}</div></div></div>{controls(lang)}'''
    return demo("dt5", data, inner, T("<b>Two generators, three roles.</b> First the platform is generated, then the platform produces twins — configured by people who do not write code, with small models that can even change while the twin runs. Hover a choice for its technical name.",
                                      "<b>Zwei Generatoren, drei Rollen.</b> Erst wird die Plattform generiert, dann erzeugt die Plattform Zwillinge — konfiguriert von Menschen, die keinen Code schreiben, mit kleinen Modellen, die sich sogar ändern lassen, während der Zwilling läuft. Zeigen Sie auf eine Auswahl, um ihren Fachnamen zu sehen."),
                lang, source=src("after", "DHM+22", where="Figs. 5, 7, 12, 13", note=T("cockpit values illustrative", "Cockpit-Werte illustrativ")))


def thumb_dt():
    """Small pictogram for the research page card: the injection-moulding machine ⇄ a twin with models, shadows and a cockpit."""
    return (f'<g class="imm" transform="translate(4 50) scale(.38)">{imm_parts(sensors=True)}</g>'
            '<path class="a" d="M128 62H144"/><path class="a" d="M139 57L144 62L139 67"/><path d="M144 80H128"/><path d="M133 75L128 80L133 85"/>'
            '<rect class="b" x="150" y="22" width="80" height="80" rx="4"/><rect class="f" x="158" y="30" width="64" height="10" rx="1"/>'
            '<rect class="b" x="156" y="48" width="28" height="20" rx="1"/><rect class="b" x="160" y="52" width="28" height="20" rx="1"/>'
            '<rect class="b" x="194" y="50" width="26" height="8" rx="4"/><rect class="b" x="194" y="62" width="26" height="8" rx="4"/><path d="M156 88H220M156 94H204"/>')
