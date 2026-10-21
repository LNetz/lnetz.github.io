"""
Figures of the Digital Twins article (research-dt.html, _build/dt.py). Static diagrams are inline SVG with the .dia
classes; the five interactive figures (ladder, anatomy, shadows, loop, roles) get all their states here and ship them
as data-json — assets/dt.js only swaps and highlights. Figures are redrawn after the chair's papers ("After …, Fig. x").
Also holds the article's literature list (REFS) so that figures and text cite the same numbers.
"""
import html
import json
import math

from ai4se import T, fig, demo, controls, cite, _link
from project_content import _arrow_defs, box, dia_scroll

esc = html.escape

# ---------------- literature (numbered) ----------------
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
    ("BH24", _link("A. Barbie, W. Hasselbring: From Digital Twins to Digital Twin Prototypes (2024), with the Grieves quotes.", "https://arxiv.org/abs/2401.07985")),
    ("DTC", _link("Digital Twin Consortium: Definition of a digital twin.", "https://www.digitaltwinconsortium.org/initiatives/the-definition-of-a-digital-twin/")),
    ("IBM", _link("IBM: What is a digital twin?", "https://www.ibm.com/think/topics/digital-twin")),
    ("list", _link("A. Wortmann: a collection of 112 digital-twin definitions.", "https://awortmann.github.io/research/digital_twin_definitions/")),
    ("sosym", _link("J. Gray, B. Rumpe: Modeling of, for, and with digital twins. SoSyM editorial (2022).", "https://www.se-rwth.de/sosym/Modeling-of-for-and-with-digital-twins/")),
]
_NUM = {k: n for n, (k, _) in enumerate(REFS, 1)}


def r(key):
    """A numbered reference into this article's literature list."""
    return f'<a class="cite" href="#ref-{_NUM[key]}">[{_NUM[key]}]</a>'


def _arrow(x1, y1, x2, y2, cls="ln"):
    """A straight arrow whose head is its own path, so it takes on the colour of the arrow (no SVG marker)."""
    a = math.atan2(y2 - y1, x2 - x1)
    h = [(x2 - 7 * math.cos(a - .45), y2 - 7 * math.sin(a - .45)), (x2 - 7 * math.cos(a + .45), y2 - 7 * math.sin(a + .45))]
    return (f'<path class="{cls}" d="M{x1} {y1}L{x2} {y2}"/>'
            f'<path class="{cls}" d="M{h[0][0]:.1f} {h[0][1]:.1f}L{x2} {y2}L{h[1][0]:.1f} {h[1][1]:.1f}"/>')


def _code(lines, new=()):
    return "".join(f'<span class="l{" new" if k in new else ""}">{esc(t) or " "}</span>' for k, t in enumerate(lines))


def _json(data):
    return html.escape(json.dumps(data, ensure_ascii=False), quote=True)


# glyphs used in several figures (drawn around their own origin)
IMM_W, IMM_H = 320, 120          # the machine's own size before scaling


def imm_parts(sensors=False, out=False):
    """The running example: an injection-moulding machine, drawn after the chair's papers (BDH20 and slides): control cabinet,
    clamping unit with the mould between tie bars, the user interface on its arm, injection unit with barrel, heater bands and
    hopper, all on the machine bed. 320 × 120 units, clamping unit left, injection unit right. Each part is a <g data-p>,
    so figures can light one up. sensors: accent dots where the twin's data comes from; out: a conveyor with moulded parts."""
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


def _person(x, y):
    return f'<g class="glyph person"><circle class="box" cx="{x}" cy="{y - 9}" r="4.5"/><path class="box" d="M{x - 7} {y + 6}c0-9 14-9 14 0z"/></g>'


# =====================================================================
# Static figures
# =====================================================================

def fig_lifespans(lang):
    """F9: how long the original systems live. After Michael [Mic25], printed p.2."""
    L = lambda x: x[lang]
    rows = [(T("industrial robots, production machines", "Industrieroboter, Produktionsmaschinen"), 10, 15, "10–15"),
            (T("wind parks", "Windparks"), 18, 22, "~20"), (T("bridges", "Brücken"), 45, 55, "~50"),
            (T("airplanes, incl. maintenance", "Flugzeuge, inkl. Wartung"), 55, 70, T("up to 70", "bis 70")), (T("buildings", "Gebäude"), 80, 100, "80–100")]
    x0, sc = 250, 5.6
    out = "".join(f'<path class="ln dash" d="M{x0 + t * sc} 14V{24 + len(rows) * 30}"/><text class="s" x="{x0 + t * sc}" y="10" text-anchor="middle">{t}</text>' for t in (0, 25, 50, 75, 100))
    for k, (name, a, b, lab) in enumerate(rows):
        y = 30 + k * 30
        out += (f'<text x="{x0 - 12}" y="{y + 4}" text-anchor="end">{L(name)}</text>'
                f'<rect class="lsbar" x="{x0 + a * sc}" y="{y - 6}" width="{(b - a) * sc}" height="12" rx="6"/>'
                f'<text class="s" x="{x0 + b * sc + 8}" y="{y + 4}">{L(lab) if isinstance(lab, dict) else lab}</text>')
    out += f'<text class="s" x="{x0 + 100 * sc}" y="{30 + len(rows) * 30 + 4}" text-anchor="end">{L(T("years", "Jahre"))}</text>'
    svg = f'<svg class="dia" viewBox="0 0 860 {50 + len(rows) * 30}" role="img" aria-label="{L(T("Lifespans: industrial robots and production machines 10 to 15 years, wind parks about 20, bridges about 50, airplanes up to 70, buildings 80 to 100 years", "Lebensdauern: Industrieroboter und Produktionsmaschinen 10 bis 15 Jahre, Windparks etwa 20, Brücken etwa 50, Flugzeuge bis 70, Gebäude 80 bis 100 Jahre"))}">{out}</svg>'
    return fig(svg, T(f"<b>Systems that outlive their software.</b> A twin has to keep up with its original system for decades — longer than most software stays maintainable. Estimates vary between sources. After Michael {r('Mic25')}, p. 2.",
                      f"<b>Systeme, die ihre Software überleben.</b> Ein Zwilling muss sein Originalsystem über Jahrzehnte begleiten — länger, als die meiste Software wartbar bleibt. Die Schätzungen schwanken je nach Quelle. Nach Michael {r('Mic25')}, S. 2."), lang)


def fig_lifecycle(lang):
    """F8: the development twin is a type; each built system gets its own instance twin. After the essay, FHM+23 p.5–6."""
    L = lambda x: x[lang]
    m = 'marker-end="url(#dtb)"'
    phases = [T("design", "Entwurf"), T("manufacture", "Fertigung"), T("operation", "Betrieb"), T("end of life", "Lebensende")]
    rail = "".join(f'<circle class="dot" cx="{120 + k * 210}" cy="110" r="5"/><text class="t" x="{120 + k * 210}" y="134" text-anchor="middle">{L(p)}</text>' for k, p in enumerate(phases))
    svg = f'''<svg class="dia" viewBox="0 0 860 250" role="img" aria-label="{L(T("Lifecycle from design to end of life. Above, during design, one development twin acts as the type; below, each manufactured system gets its own twin, as manufactured and as operated", "Lebenszyklus vom Entwurf bis zum Lebensende. Oben, im Entwurf, wirkt ein Entwicklungszwilling als Typ; unten bekommt jedes gefertigte System seinen eigenen Zwilling, wie gefertigt und wie betrieben"))}">
  {_arrow_defs("dtb")}
  <path class="ln" d="M60 110H800" {m}/>{rail}
  <rect class="box hl" x="40" y="24" width="250" height="50" rx="4"/><text class="t" x="56" y="46">{L(T("development twin", "Entwicklungszwilling"))}</text>
  <text class="s" x="56" y="62">{L(T("a type: development artefacts, no traces of a real system", "ein Typ: Entwicklungsartefakte, keine Spuren eines echten Systems"))}</text>
  <path class="ln dash" d="M200 74V165H326"/><path class="ln dash" d="M180 74V209H326"/>
  <rect class="box" x="330" y="150" width="440" height="30" rx="4"/><text x="344" y="169">{L(T("twin of system #1 · as manufactured → as operated", "Zwilling von System Nr. 1 · wie gefertigt → wie betrieben"))}</text>
  <rect class="box" x="330" y="194" width="440" height="30" rx="4"/><text x="344" y="213">{L(T("twin of system #2 · tolerances, wear and tear of this one instance", "Zwilling von System Nr. 2 · Toleranzen, Verschleiß genau dieses Exemplars"))}</text>
  <text class="s" x="40" y="186">{L(T("ONE TYPE", "EIN TYP"))}</text><text class="s" x="40" y="200">{L(T("MANY INSTANCES", "VIELE EXEMPLARE"))}</text>
</svg>'''
    return fig(svg, T(f"<b>Twin of what, and when?</b> During design there is no built system yet, so the twin is a <i>development twin</i>: a type, valid for all instances {r('essay')}. Every built system then gets a twin of its own that has to take in its manufacturing tolerances and its wear and tear {cite('FHM+23')}.",
                      f"<b>Zwilling wovon, und wann?</b> Im Entwurf gibt es noch kein gebautes System, also ist der Zwilling ein <i>Entwicklungszwilling</i>: ein Typ, gültig für alle Exemplare {r('essay')}. Jedes gebaute System bekommt dann einen eigenen Zwilling, der seine Fertigungstoleranzen und seinen Verschleiß aufnehmen muss {cite('FHM+23')}."), lang)


def fig_refarch(lang):
    """F15: the reference architecture that grew out of the self-adaptive loop. After Heithoff et al. [HJM24], Fig. 5.2."""
    L = lambda x: x[lang]
    m = 'marker-end="url(#dtc)"'
    svg = f'''<svg class="dia" viewBox="0 0 860 230" role="img" aria-label="{L(T("Reference architecture: gateways connect the machine; inside the twin, self-adaptivity services, process-awareness services and an optimizer work on a database; a cockpit backend and frontend connect the users", "Referenzarchitektur: Gateways verbinden die Maschine; im Zwilling arbeiten Selbstadaptivitäts-Services, prozessbewusste Services und ein Optimierer auf einer Datenbank; Cockpit-Backend und -Frontend verbinden die Nutzer"))}">
  {_arrow_defs("dtc")}
  {_machine(4, 94, .25)}
  <path class="ln" d="M84 110H112" {m}/>
  {box(116, 86, 96, 48, "Gateways", "OPC UA · MQTT")}
  <path class="ln" d="M212 110H238" {m}/>
  <rect class="zone" x="242" y="10" width="402" height="210" rx="6"/><text class="s" x="254" y="28">{L(T("THE TWIN · SERVICES", "DER ZWILLING · SERVICES"))}</text>
  <rect class="box hl" x="254" y="38" width="184" height="98" rx="3"/><text class="t" x="266" y="58">{L(T("self-adaptivity", "Selbstadaptivität"))}</text>
  <text class="s" x="266" y="78">data processor · evaluator</text><text class="s" x="266" y="94">reasoner · executor</text><text class="s" x="266" y="122">{L(T("the loop of the next section", "die Schleife des nächsten Abschnitts"))}</text>
  <rect class="box" x="448" y="38" width="184" height="98" rx="3"/><text class="t" x="460" y="58">{L(T("process awareness", "Prozessbewusstsein"))}</text>
  <text class="s" x="460" y="78">conformance checker</text><text class="s" x="460" y="94">process discovery</text><text class="s" x="460" y="110">process orchestrator</text>
  {box(254, 146, 184, 30, L(T("optimizer", "Optimierer")))}
  {box(448, 146, 184, 30, L(T("database · models · shadows", "Datenbank · Modelle · Schatten")))}
  <path class="ln" d="M644 110H668" {m}/>
  {box(672, 86, 96, 48, "Cockpit", L(T("backend · frontend", "Backend · Frontend")))}
  <path class="ln" d="M768 110H792" {m}/>{_person(820, 112)}<text class="s" x="820" y="140" text-anchor="middle">{L(T("users", "Nutzer"))}</text>
</svg>'''
    return fig(svg, T(f"<b>From one loop to many services.</b> The self-adaptive loop proved too rigid on its own — “MAPE-K is too restrictive regarding its connection between components” {r('Mic25')} — so later twins combine it with process-aware services (for example, noticing that opening a clamping unit takes too long), an optimizer and a cockpit. After Heithoff et al. {r('HJM24')}, Fig. 5.2, simplified.",
                      f"<b>Von einer Schleife zu vielen Services.</b> Die selbstadaptive Schleife allein erwies sich als zu starr — MAPE-K schränkt die Verbindungen zwischen den Komponenten zu sehr ein {r('Mic25')} —, deshalb kombinieren spätere Zwillinge sie mit prozessbewussten Services (die etwa bemerken, dass das Öffnen einer Schließeinheit zu lange dauert), einem Optimierer und einem Cockpit. Nach Heithoff et al. {r('HJM24')}, Abb. 5.2, vereinfacht."), lang)


def fig_mde4dt(lang):
    """F13: engineering models and domain knowledge become the twin's models; generators build the twin. After Michael [Mic25], Fig. 3.1."""
    L = lambda x: x[lang]
    m, ma = 'marker-end="url(#dtd)"', 'marker-end="url(#dtda)"'
    from article_art import gear
    svg = f'''<svg class="dia" viewBox="0 0 860 220" role="img" aria-label="{L(T("Engineering models such as CAD, SysML or Modelica and domain knowledge become application-specific and application-independent models; generators turn them into the digital twin with its models, shadows, services and cockpit", "Engineering-Modelle wie CAD, SysML oder Modelica und Domänenwissen werden zu anwendungsspezifischen und anwendungsunabhängigen Modellen; Generatoren machen daraus den digitalen Zwilling mit Modellen, Schatten, Services und Cockpit"))}">
  {_arrow_defs("dtd")}
  <text class="s" x="0" y="16">{L(T("WHAT EXISTS ALREADY", "WAS SCHON DA IST"))}</text>
  {box(0, 28, 180, 74, L(T("engineering models", "Engineering-Modelle")), "CAD · STEP · SysML", "Modelica · AutomationML")}
  {box(0, 116, 180, 50, L(T("domain knowledge", "Domänenwissen")), L(T("experts, processes", "Fachleute, Prozesse")))}
  <path class="ln" d="M180 65H232" {m}/><path class="ln" d="M180 141H232" {m}/>
  <text class="s" x="236" y="16">{L(T("MODELS FOR THE TWIN", "MODELLE FÜR DEN ZWILLING"))}</text>
  {box(236, 28, 200, 60, L(T("application-specific", "anwendungsspezifisch")), L(T("this machine, these sensors", "diese Maschine, diese Sensoren")))}
  {box(236, 100, 200, 60, L(T("application-independent", "anwendungsunabhängig")), L(T("libraries, architecture", "Bibliotheken, Architektur")))}
  <path class="ln hl" d="M436 94H486" {ma}/>
  <path class="gearf" d="{gear(530, 94, 34, 11)}"/><circle class="hubf" cx="530" cy="94" r="10"/><text class="s" x="530" y="150" text-anchor="middle">{L(T("generators", "Generatoren"))}</text>
  <path class="ln hl" d="M574 94H620" {ma}/>
  <rect class="box hl" x="624" y="20" width="236" height="150" rx="4"/><text class="t" x="640" y="42">{L(T("the digital twin", "der digitale Zwilling"))}</text>
  <text x="640" y="68">{L(T("models", "Modelle"))}</text><text x="640" y="88">{L(T("digital shadows", "digitale Schatten"))}</text>
  <text x="640" y="108">{L(T("services", "Services"))}</text><text x="640" y="128">{L(T("cockpit", "Cockpit"))}</text>
  <text class="s" x="640" y="156">{L(T("generated, then extended by hand", "generiert, dann von Hand erweitert"))}</text>
</svg>'''
    return fig(svg, T(f"<b>Do not start from scratch.</b> Much of what a twin needs to know already exists as engineering models. Generating from them “(1) reduces the development effort for DTs and (2) ensures consistency” {r('Mic25')}. After Michael {r('Mic25')}, Fig. 3.1, simplified.",
                      f"<b>Nicht bei null anfangen.</b> Vieles, was ein Zwilling wissen muss, existiert schon als Engineering-Modell. Daraus zu generieren verringert den Entwicklungsaufwand und sichert die Konsistenz {r('Mic25')}. Nach Michael {r('Mic25')}, Abb. 3.1, vereinfacht."), lang)


def fig_wind(lang):
    """F6s: the wind-turbine cooling system — CD, generated overview, Python API. After Michael et al. [MNN+22], Figs. 4–5, List. 2."""
    L = lambda x: x[lang]
    cd = ["class Radiator {", "  String name;", "  Double minimalVolumeFlow;", "  Double coolingCapacity;", "}", "class Pump {", "  String name;", "  Double idealPower;",
          "  Double minimalPower;", "  Double maximalPower;", "  Double VolumeFlow;", "}", "class CoolingSystem {", "  String name;", "  Double /overallPowerConsumption;",
          "  Double /overallCoolingCapacity;", "}", "<<ordered>>", "association CoolingSystem -> Radiator [*];", "<<ordered>>", "association CoolingSystem -> Pump [*];"]
    py = ['obj = Factory.new(type_name="Radiator",', '        data={"name": "DIA_AB",', '              "minimalVolumnFlow": 300,', '              "coolingCapacity": 4000})', "obj.push()"]
    rows = [("MK01", "20", "30"), ("MK12_13", "40", "300"), ("MK2000", "120", "600")]
    tbl = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td><span class=\"pill\">{L(T('details', 'Details'))}</span></td></tr>" for a, b, c in rows)
    inner = f'''<div class="wind">
  <div><span class="k mono">{L(T("1 · THE CLASS DIAGRAM (CD4A)", "1 · DAS KLASSENDIAGRAMM (CD4A)"))}</span><pre class="mono">{_code(cd)}</pre></div>
  <div><span class="k mono">{L(T("2 · GENERATED: THE PUMP OVERVIEW", "2 · GENERIERT: DIE PUMPEN-ÜBERSICHT"))}</span>
    <div class="gp-card"><div class="gp-head">Pump</div><div class="gp-body"><table><tr><th>name</th><th>VolumnFlow</th><th>idealPower</th><th></th></tr>{tbl}</table></div></div>
    <span class="k mono" style="margin-top:16px">{L(T("3 · THE TOOLS WRITE BACK (PYTHON API)", "3 · DIE WERKZEUGE SCHREIBEN ZURÜCK (PYTHON-API)"))}</span><pre class="mono">{_code(py)}</pre>
    <p class="mono wind-rail">draft › review › released › outdated</p></div>
</div>'''
    return (f'<figure class="media art-fig">{inner}<figcaption class="mono">{L(T(f"<b>A single source of truth for engineering parameters.</b> The cooling system of a wind turbine as a class diagram (derived attributes marked “/” are computed in hand-written Java); MontiGem with CD2GUI generates the pages; the engineering tools (Rhino, Ansys, MATLAB) read and write through a Python API; a release status protects what has been agreed. Spelling as in the paper’s figures (VolumeFlow in Fig. 4, VolumnFlow in Fig. 5 and List. 2). After Michael et al. {cite('MNN+22')}, Figs. 4–5 and List. 2.", f"<b>Eine einzige Quelle für Engineering-Parameter.</b> Das Kühlsystem einer Windkraftanlage als Klassendiagramm (mit „/“ markierte abgeleitete Attribute werden in handgeschriebenem Java berechnet); MontiGem mit CD2GUI generiert die Seiten; die Engineering-Werkzeuge (Rhino, Ansys, MATLAB) lesen und schreiben über eine Python-API; ein Freigabestatus schützt, was vereinbart ist. Schreibweisen wie in den Abbildungen der Arbeit (VolumeFlow in Abb. 4, VolumnFlow in Abb. 5 und Listing 2). Nach Michael et al. {cite('MNN+22')}, Abb. 4–5 und Listing 2."))}</figcaption></figure>')


def fig_sos(lang):
    """F14: twins of systems of systems. After Michael et al. [MPRW22], Fig. 1."""
    L = lambda x: x[lang]
    levels = [T("network", "Netzwerk"), T("factory", "Fabrik"), T("shop floor", "Werkhalle"), T("machine", "Maschine")]
    out = ""
    for k, lv in enumerate(levels):
        y = 20 + k * 46
        w = 220 - k * 40
        out += (f'<rect class="box" x="{200 - w / 2}" y="{y}" width="{w}" height="32" rx="3"/><text x="200" y="{y + 20}" text-anchor="middle">{L(lv)}</text>'
                f'<rect class="box hl" x="{660 - w / 2}" y="{y}" width="{w}" height="32" rx="3"/><text x="660" y="{y + 20}" text-anchor="middle">{L(T("twin of the ", "Zwilling der/des "))}{L(lv)}</text>'
                f'<path class="ln dash" d="M{200 + w / 2} {y + 16}H{660 - w / 2}"/>')
        if k:
            out += f'<path class="ln" d="M200 {y}V{y - 14}"/><path class="ln hl" d="M660 {y}V{y - 14}"/>'
    svg = f'<svg class="dia" viewBox="0 0 860 210" role="img" aria-label="{L(T("Machines form shop floors, factories and networks; their twins should be composed the same way", "Maschinen bilden Werkhallen, Fabriken und Netzwerke; ihre Zwillinge sollten genauso zusammengesetzt werden"))}">{out}<text class="s" x="80" y="206">{L(T("PHYSICAL", "PHYSISCH"))}</text><text class="s" x="560" y="206">{L(T("DIGITAL", "DIGITAL"))}</text></svg>'
    return fig(svg, T(f"<b>Twins of twins.</b> “When composing a car chassis with a motor, the corresponding digital twins should be composed as well” {cite('FHM+23')} — today they are mostly built one by one. Composing them raises open questions: integration across levels, intellectual property, rights and roles. After Michael et al. {r('MPRW22')}, Fig. 1.",
                      f"<b>Zwillinge von Zwillingen.</b> Wer ein Fahrgestell mit einem Motor kombiniert, sollte auch ihre digitalen Zwillinge kombinieren {cite('FHM+23')} — heute entstehen sie meist einzeln. Ihre Komposition wirft offene Fragen auf: Integration über Ebenen hinweg, geistiges Eigentum, Rechte und Rollen. Nach Michael et al. {r('MPRW22')}, Abb. 1."), lang)


# =====================================================================
# Interactive figures (assets/dt.js)
# =====================================================================

def demo_ladder(lang):
    """d1: model → shadow → twin, Kritzinger's data-flow view; and the human-in-the-loop case where definitions differ."""
    L = lambda x: x[lang]
    states = [
        ("model", T("digital model", "digitales Modell"), "manual", "manual", T("No automated data flow in either direction. Example: the CAD model of the mould — when the machine changes, someone updates the model by hand.", "Kein automatischer Datenfluss, in keine Richtung. Beispiel: das CAD-Modell der Form — ändert sich die Maschine, aktualisiert es jemand von Hand."), f"{L(T('levels after Kritzinger', 'Stufen nach Kritzinger'))} {r('Krit')} {L(T('via', 'über'))} {r('PZC25')} · {L(T('example: ours', 'Beispiel: unseres'))}"),
        ("shadow", T("digital shadow", "digitaler Schatten"), "auto", "manual", T("Data flows automatically from the machine to the digital object. Example: barrel temperatures and injection pressure on a live dashboard — but a new setting is still typed in at the machine.", "Daten fließen automatisch von der Maschine zum digitalen Objekt. Beispiel: Zylindertemperaturen und Einspritzdruck auf einem Live-Dashboard — eine neue Einstellung wird aber weiter an der Maschine eingetippt."), f"{L(T('levels after Kritzinger', 'Stufen nach Kritzinger'))} {r('Krit')} {L(T('via', 'über'))} {r('PZC25')} · {L(T('example: ours', 'Beispiel: unseres'))}"),
        ("twin", T("digital twin", "digitaler Zwilling"), "auto", "auto", T("Data also flows back automatically. Example: the twin lowers the setpoint of a heating band when the barrel runs too hot — nobody types it in.", "Daten fließen auch automatisch zurück. Beispiel: Der Zwilling senkt den Sollwert eines Heizbands, wenn der Zylinder zu heiß läuft — niemand tippt ihn ein."), f"{L(T('levels after Kritzinger', 'Stufen nach Kritzinger'))} {r('Krit')} {L(T('via', 'über'))} {r('PZC25')} · {L(T('example: ours', 'Beispiel: unseres'))}"),
        ("human", T("Kritzinger: shadow · the chair: twin", "Kritzinger: Schatten · der Lehrstuhl: Zwilling"), "auto", "human", T("The way back runs through a person who reads a proposal and acts on it. For Kritzinger that is only a shadow; the chair’s definition counts indirect control by informing users.", "Der Rückweg läuft über einen Menschen, der einen Vorschlag liest und handelt. Für Kritzinger ist das nur ein Schatten; die Definition des Lehrstuhls zählt indirekte Steuerung über informierte Nutzer mit."), f"{r('essay')} {r('Mic25')}"),
    ]
    data = {"states": [{"id": i, "label": L(lab), "up": up, "down": dn, "quote": L(q), "src": s} for i, lab, up, dn, q, s in states]}
    btn = [T("model", "Modell"), T("shadow", "Schatten"), T("twin", "Zwilling"), T("person in between", "Mensch dazwischen")]
    buttons = "".join(f'<button type="button" data-v="{k}" aria-pressed="{"true" if k == 1 else "false"}">{L(b)}</button>' for k, b in enumerate(btn))
    svg = f'''<svg class="dia ladder" viewBox="0 0 420 150" role="img" aria-label="{L(T("An injection-moulding machine and a digital object, connected by an arrow up and an arrow back", "Eine Spritzgießmaschine und ein digitales Objekt, verbunden durch einen Pfeil hin und einen zurück"))}">
  {_machine(0, 52, .5, sensors=True)}<text class="s" x="80" y="128" text-anchor="middle">{L(T("the original system", "das Originalsystem"))}</text>
  <rect class="box" x="290" y="34" width="120" height="78" rx="4"/><circle class="ln" cx="322" cy="66" r="16"/><path class="ln" d="M322 66l9-8"/><rect class="zone" x="346" y="54" width="52" height="10"/><rect class="zone" x="346" y="72" width="36" height="10"/>
  <text class="s" x="350" y="128" text-anchor="middle">{L(T("the digital object", "das digitale Objekt"))}</text>
  <g class="arr up" data-a="up">{_arrow(172, 56, 282, 56)}<text class="s alab" x="227" y="46" text-anchor="middle"></text></g>
  <g class="arr down" data-a="down">{_arrow(282, 98, 172, 98)}<text class="s alab" x="227" y="118" text-anchor="middle"></text>{_person(227, 100)}</g>
</svg>'''
    s0 = data["states"][1]
    words = {k: L(v) for k, v in dict(manual=T("manual", "manuell"), auto=T("automatic", "automatisch"), human=T("via a person", "über einen Menschen")).items()}
    data["words"] = words
    inner = f'''<div class="d1-presets mono" role="group"><span class="k">{L(T("DATA FLOW:", "DATENFLUSS:"))}</span>{buttons}</div>
<div class="dl-grid">{svg}<div class="dl-out"><p class="dl-label" aria-live="polite">{s0["label"]}</p><p class="dl-quote">{s0["quote"]}</p><p class="dl-src mono">{s0["src"]}</p></div></div>'''
    return demo("dt1", data, inner, T(f"<b>Three words on one axis: how automatically does data flow?</b> A model is updated by hand, a shadow follows the system automatically, a twin also acts back on it. The ladder is intuitive — but it says nothing about what is inside the box, and it disagrees with the chair’s definition as soon as a person sits in the loop. What is inside the box → the next figure. After Kritzinger et al. {r('Krit')}, as described in Becker et al. {r('BBD21')} and Pfeiffer et al. {r('PZC25')}.",
                                      f"<b>Drei Wörter auf einer Achse: Wie automatisch fließen die Daten?</b> Ein Modell wird von Hand aktualisiert, ein Schatten folgt dem System automatisch, ein Zwilling wirkt auch auf es zurück. Die Leiter ist eingängig — sie sagt aber nichts darüber, was in der Box steckt, und sie widerspricht der Definition des Lehrstuhls, sobald ein Mensch in der Schleife sitzt. Was in der Box steckt → die nächste Abbildung. Nach Kritzinger et al. {r('Krit')}, wie bei Becker et al. {r('BBD21')} und Pfeiffer et al. {r('PZC25')} beschrieben."), lang)


ANATOMY_KEYS = ["original", "software", "models", "shadows", "update", "purpose", "services", "cockpit", "info", "commands"]


def demo_anatomy(lang):
    """d2: the chair's definition (V2.2), clause by clause, mapped onto the parts of a twin; presets 'Is it a twin?'.
    After Heithoff et al. [HHMR23], Fig. 1 (users / services / models + data / connectivity / original system)."""
    L = lambda x: x[lang]
    tabs = [("svc-mon", T("monitoring", "Monitoring")), ("svc-pred", T("prediction", "Vorhersage")), ("svc-sim", T("simulation", "Simulation")),
            ("svc-ass", T("assistance", "Assistenz")), ("svc-ctl", T("control", "Steuerung"))]
    tabsvg = "".join(f'<g class="part" data-k="services {k}"><rect class="box" x="{36 + i * 62}" y="40" width="58" height="26" rx="3"/><text class="s" x="{65 + i * 62}" y="56" text-anchor="middle" style="font-size:8px">{L(n)}</text></g>' for i, (k, n) in enumerate(tabs))
    tabsvg += f'<g class="part" data-k="cockpit"><rect class="box hl" x="346" y="40" width="58" height="26" rx="3"/><text class="s" x="375" y="56" text-anchor="middle" style="font-size:8px">cockpit (UI)</text></g>'
    models = "".join(f'<rect class="box" x="{44 + k * 8}" y="{108 + k * 22}" width="128" height="40" rx="3"/>' for k in range(3))
    models += "".join(f'<text x="{56 + k * 8}" y="{124 + k * 22}" class="s">{L(n)}</text>' for k, n in enumerate([T("structure", "Struktur"), T("behaviour", "Verhalten"), T("geometry", "Geometrie")]))
    pills = [T("rejection rate", "Ausschussquote"), T("overheating", "Überhitzung"), T("energy", "Energie")]
    shadows = "".join(f'<rect class="box" x="236" y="{106 + k * 30}" width="168" height="24" rx="12"/>' for k in range(3))
    purpose = "".join(f'<text class="s a" x="250" y="{122 + k * 30}">{L(T("for: ", "für: "))}{L(p)}</text>' for k, p in enumerate(pills))
    svg = f'''<svg class="dia anat" viewBox="0 0 420 330" role="group" aria-label="{L(T("Anatomy of a digital twin: inside a software boundary, services with a cockpit on top, models and purpose-bound digital shadows below, both updated regularly; data comes up from the original system, information and commands go back down", "Anatomie eines digitalen Zwillings: in einer Softwaregrenze oben Services mit einem Cockpit, darunter Modelle und zweckgebundene digitale Schatten, beide regelmäßig aktualisiert; Daten kommen vom Originalsystem herauf, Informationen und Befehle gehen zurück"))}">
  <g class="part" data-k="software"><rect class="sw" x="22" y="14" width="392" height="226" rx="8"/><text class="s" x="34" y="30">{L(T("SOFTWARE", "SOFTWARE"))}</text></g>
  {tabsvg}
  <g class="part" data-k="models">{models}<text class="s" x="44" y="100">{L(T("MODELS", "MODELLE"))}</text></g>
  <g class="part" data-k="update"><circle class="box" cx="56" cy="216" r="11"/><path class="ln" d="M56 209v7l5 3"/><text class="s" x="72" y="220">{L(T("updated regularly", "regelmäßig aktualisiert"))}</text></g>
  <g class="part" data-k="shadows">{shadows}<text class="s" x="236" y="100">{L(T("DIGITAL SHADOWS", "DIGITALE SCHATTEN"))}</text></g>
  <g class="part" data-k="purpose">{purpose}</g>
  <g class="part" data-k="original"><rect class="box" x="22" y="276" width="392" height="44" rx="4"/>{_machine(32, 280, .3)}<text class="t" x="144" y="302">{L(T("the original system", "das Originalsystem"))}</text></g>
  <g class="part" data-k="shadows">{_arrow(300, 274, 300, 200)}<text class="s" x="306" y="262">{L(T("data", "Daten"))}</text></g>
  <g class="part" data-k="info">{_arrow(150, 240, 150, 272)}<text class="s" x="156" y="262">{L(T("information", "Information"))}</text></g>
  <g class="part" data-k="commands">{_arrow(240, 240, 240, 272, "ln hl")}<text class="s a" x="246" y="262">{L(T("commands", "Befehle"))}</text></g>
</svg>'''
    clauses = [("original", T("of an original system", "eines Originalsystems")), ("software", T("is a software", "ist eine Software")),
               ("models", T("a set of models", "eine Menge von Modellen")), ("shadows", T("a set of digital shadows", "eine Menge digitaler Schatten")),
               ("update", T("updated on a regular basis", "regelmäßig aktualisiert")), ("purpose", T("purposefully", "zweckgerichtet")),
               ("services", T("a set of services", "eine Menge von Services")), ("info", T("providing useful information", "nützliche Informationen liefern")),
               ("commands", T("sending it control commands", "ihm Steuerbefehle senden"))]
    chips = "".join(f'<button type="button" class="chip" data-k="{k}">{L(t)}</button>' for k, t in clauses)
    presets = [
        ("cad", T("a CAD file", "eine CAD-Datei"), ["models"], T("Models only — a “digital model” in Kritzinger’s terms. No data from the real system, no services, no way back.", "Nur Modelle — ein „digitales Modell“ im Sinne Kritzingers. Keine Daten aus dem realen System, keine Services, kein Rückweg.")),
        ("dash", T("a live dashboard", "ein Live-Dashboard"), ["shadows", "update", "purpose", "cockpit", "original", "info"], T("The machine’s temperatures and pressures, shown for one purpose — a digital shadow with a display. No models, no commands.", "Temperaturen und Drücke der Maschine, für einen Zweck angezeigt — ein digitaler Schatten mit Anzeige. Keine Modelle, keine Befehle.")),
        ("sim", T("a simulation", "eine Simulation"), ["models", "svc-sim", "software"], T("Models and one service, but no data from the real system: “not only a simulation model”.", "Modelle und ein Service, aber keine Daten aus dem realen System: „nicht nur ein Simulationsmodell“.")),
        ("wind", T("the wind-turbine cockpit", "das Windkraft-Cockpit"), ["models", "software", "cockpit", "update", "purpose"], T("Models, a cockpit and agreed parameters — but no traces of a real turbine and no commands yet: a development twin, a twin of a type.", "Modelle, ein Cockpit und vereinbarte Parameter — aber keine Spuren einer echten Anlage und noch keine Befehle: ein Entwicklungszwilling, ein Zwilling eines Typs.")),
        ("twin", T("the twin", "der Zwilling"), ANATOMY_KEYS + [k for k, _ in tabs], T("Everything the definition asks for: models and shadows, kept up to date for a purpose, services that use them, and a way back — information and commands.", "Alles, was die Definition verlangt: Modelle und Schatten, zweckgerichtet aktuell gehalten, Services, die sie nutzen, und ein Rückweg — Informationen und Befehle.")),
    ]
    data = {"presets": [{"id": i, "on": on, "verdict": L(v)} for i, _, on, v in presets]}
    pbtn = "".join(f'<button type="button" data-v="{k}" aria-pressed="{"true" if k == 4 else "false"}">{L(n)}</button>' for k, (_, n, _, _) in enumerate(presets))
    inner = f'''<div class="anat-chips" role="group" aria-label="{L(T("The clauses of the definition", "Die Teile der Definition"))}">{chips}</div>
<div class="anat-grid">{svg}<div class="anat-side"><div class="d1-presets mono" role="group"><span class="k">{L(T("IS IT A TWIN?", "IST ES EIN ZWILLING?"))}</span>{pbtn}</div>
<p class="anat-verdict" aria-live="polite">{L(presets[4][3])}</p></div></div>'''
    return demo("dt2", data, inner, T(f"<b>Every clause of the definition is a part of the twin.</b> Point at a clause to find its part — or at a part to find its clause. Then check everyday artefacts: a dashboard is only one tab, a CAD file only the model corner, and the wind-turbine cockpit is a twin of a type. Sources for the verdicts: Kritzinger {r('Krit')} via {r('PZC25')}; Michael {r('Mic25')}; the essay {r('essay')}; Michael et al. {cite('MNN+22')}. Layout after Heithoff et al. {r('HHMR23')}, Fig. 1.",
                                      f"<b>Jeder Teil der Definition ist ein Teil des Zwillings.</b> Zeigen Sie auf eine Formulierung, um ihren Teil zu finden — oder auf einen Teil, um seine Formulierung zu finden. Dann prüfen Sie Alltagsdinge: Ein Armaturenbrett ist nur ein Reiter, eine CAD-Datei nur die Modell-Ecke, und das Windkraft-Cockpit ist ein Zwilling eines Typs. Quellen der Urteile: Kritzinger {r('Krit')} über {r('PZC25')}; Michael {r('Mic25')}; der Essay {r('essay')}; Michael et al. {cite('MNN+22')}. Aufbau nach Heithoff et al. {r('HHMR23')}, Abb. 1."), lang)


def _trace(seed=11, n=48):
    """An illustrative temperature trace of machine B (48 hourly readings); the last two exceed 500. Plus 30 parts OK/NOK."""
    vals, s = [], seed
    for k in range(n):
        s = (s * 1103515245 + 12345) % 2 ** 31
        vals.append(440 + 30 * math.sin(k / 5) + 18 * math.sin(k / 2.3) + (s % 30) - 15 + (k - 36) * 2.6 * (k > 36))
    vals[-2], vals[-1] = max(vals[-2], 512), max(vals[-1], 524)
    parts, s = [], seed * 3
    for k in range(30):
        s = (s * 1103515245 + 12345) % 2 ** 31
        parts.append(0 if s % 9 == 0 else 1)
    return vals, parts


def demo_shadows(lang):
    """d3: one machine's data, three shadows. After Becker et al. [BBD21] p.7–8 (machines A and B) and Dalibor et al. [DHM+22] Figs. 14–15, 17."""
    L = lambda x: x[lang]
    vals, parts = _trace()
    W, H, x0, y0 = 400, 150, 20, 20
    lo, hi = 380, 560
    X = lambda k: x0 + k * (W - 2 * x0) / (len(vals) - 1)
    Y = lambda v: y0 + (hi - v) / (hi - lo) * 84
    line = "M" + "L".join(f"{X(k):.1f} {Y(v):.1f}" for k, v in enumerate(vals))
    thr = Y(500)
    mx = max(range(24, 48), key=lambda k: vals[k])
    ticks = "".join(f'<path class="tick{"" if ok else " nok"}" d="M{X(k * 47 / 29):.1f} 128v{6 if ok else 10}"/>' for k, ok in enumerate(parts))
    # above the trace: machine B, and where each shadow's data come from (parts on the conveyor · the barrel's temperature sensor)
    src = (f'{_machine(20, 6, .4, out=True)}'
           f'<circle class="ov ov1 ring" cx="142" cy="44" r="11"/><circle class="ov ov2 ov3 ring" cx="101" cy="29.2" r="7"/><circle class="sens" cx="101" cy="29.2" r="2.4"/>'
           f'<text class="s ov ov1" x="176" y="24">{L(T("A: rate typed in by hand", "A: Quote von Hand eingetippt"))}</text>'
           f'<text class="s ov ov1" x="176" y="38">{L(T("B: parts checked by sensors", "B: Teile per Sensor geprüft"))}</text>'
           f'<text class="s ov ov2 ov3" x="176" y="32">tempSensor[2] · {L(T("plasticising unit", "Plastifiziereinheit"))}</text>')
    svg = f'''<svg class="dia trace" viewBox="0 0 {W} {H + 64}" role="img" aria-label="{L(T("Illustrative data: the temperature of machine B over 48 hours with a threshold, and the parts it produced, marked OK or not OK", "Schematische Daten: die Temperatur von Maschine B über 48 Stunden mit einer Schwelle, und die produzierten Teile, als in Ordnung oder nicht in Ordnung markiert"))}">
  {src}<g transform="translate(0 64)">
  <g class="ov ov1">{"".join(f'<path class="nokhi" d="M{X(k * 47 / 29):.1f} 124v16"/>' for k, ok in enumerate(parts) if not ok)}</g>
  <rect class="ov ov2 win" x="{X(24):.1f}" y="14" width="{X(47) - X(24):.1f}" height="100"/>
  <path class="ln dash" d="M{x0} {thr:.1f}H{W - x0}"/><text class="s" x="{x0 + 2}" y="{thr - 4:.1f}">500</text>
  <path class="trl" d="{line}"/>
  <circle class="ov ov2 pt" cx="{X(mx):.1f}" cy="{Y(vals[mx]):.1f}" r="4"/>
  <circle class="ov ov3 pt" cx="{X(46):.1f}" cy="{Y(vals[46]):.1f}" r="4"/><circle class="ov ov3 pt" cx="{X(47):.1f}" cy="{Y(vals[47]):.1f}" r="4"/>
  <text class="s" x="{x0}" y="12">{L(T("MACHINE B · temperature, 48 h", "MASCHINE B · Temperatur, 48 h"))}</text>
  {ticks}<text class="s" x="{x0}" y="148">{L(T("parts: OK · not OK", "Teile: OK · nicht OK"))}</text>
</g></svg>'''
    states = [
        (T("Which machine for part X?", "Welche Maschine für Teil X?"),
         [("Asset", T("machines A and B", "Maschinen A und B")), ("Purpose", T("lowest expected rejection rate", "niedrigste erwartete Ausschussquote")),
          ("Model", "CalcMinRejectionRate"), ("Source", T("A: typed in by an operator · B: measured OK / not OK", "A: von einer Bedienerin eingetippt · B: gemessen OK / nicht OK"))],
         ["// machine A: rejection rate entered by hand", "// machine B: OK / NOK classified by sensors", "CalcMinRejectionRate(A, B)  →  machine id"],
         T("The answer is a machine id; the controller sets the schedule. The shadow itself does nothing.", "Die Antwort ist eine Maschinen-ID; die Steuerung legt den Plan fest. Der Schatten selbst tut nichts."), f"Becker et al. {r('BBD21')}"),
        (T("Rejection rate when temperatures run high", "Ausschussquote bei hohen Temperaturen"),
         [("Asset", "PlasticizingUnit"), ("Purpose", T("minimise the rejection rate", "Ausschussquote minimieren")), ("Model", T("production process", "Produktionsprozess")),
          ("Source", "tempSensor[2] · " + L(T("every 24 h", "alle 24 h")))],
         ["Temp2Max {", "  value = max(Temp2(now() - 24h, now()).value);", "  timestamp = now();", "}"],
         T("An aggregation over the last 24 hours, recomputed once a day.", "Eine Aggregation über die letzten 24 Stunden, einmal täglich neu berechnet."), f"Dalibor et al. {cite('DHM+22')}, Figs. 14–15"),
        (T("Overheating control", "Überhitzungskontrolle"),
         [("Asset", "PlasticizingPhase"), ("Purpose", T("keep the temperature in range", "Temperatur im Bereich halten")), ("Model", T("control behaviour", "Regelverhalten")),
          ("Source", T("the last two readings", "die letzten beiden Messwerte"))],
         ["checkTemp@(-1)   // the previous reading", "checkTemp@(0)    // the latest reading"],
         T("This is the state the data processor hands to the evaluator — the loop in the next section starts here.", "Das ist der Zustand, den der Datenprozessor an den Evaluator übergibt — hier beginnt die Schleife im nächsten Abschnitt."), f"Dalibor et al. {cite('DHM+22')}, Fig. 17"),
    ]
    data = {"states": [{"facts": "".join(f'<div><span class="mono">{a}</span><b>{L(b) if isinstance(b, dict) else b}</b></div>' for a, b in facts),
                        "code": _code(code), "note": L(note), "src": src} for _, facts, code, note, src in states]}
    buttons = "".join(f'<button type="button" data-v="{k}" aria-pressed="{"true" if k == 0 else "false"}">{L(n)}</button>' for k, (n, *_ ) in enumerate(states))
    s0 = data["states"][0]
    inner = f'''<div class="d1-presets mono" role="group"><span class="k">{L(T("PURPOSE:", "ZWECK:"))}</span>{buttons}</div>
<div class="sh-grid s1">{svg}<div class="sh-card"><div class="sh-facts">{s0["facts"]}</div><pre class="mono">{s0["code"]}</pre><p class="sh-note" aria-live="polite">{s0["note"]}</p><p class="dl-src mono">{s0["src"]}</p></div></div>'''
    return demo("dt3", data, inner, T(f"<b>The same data, three shadows.</b> Each purpose picks other data points and condenses them differently: a comparison of two machines, a daily maximum, the last two readings. None of them acts — a shadow answers a question; it “can be compared to a view in database systems” {r('BDJ22')}. Illustrative data, no real measurements.",
                                      f"<b>Dieselben Daten, drei Schatten.</b> Jeder Zweck wählt andere Datenpunkte und verdichtet sie anders: ein Vergleich zweier Maschinen, ein Tagesmaximum, die letzten beiden Messwerte. Keiner handelt — ein Schatten beantwortet eine Frage; er lässt sich mit einer Sicht in einer Datenbank vergleichen {r('BDJ22')}. Schematische Daten, keine echten Messungen."), lang)


LOOP_CODE = {
    "event": ["event TempTooHigh for PlasticizingPhase {", "  checkTemp@(-1) > 500", "  && checkTemp@(0) > 500", "}"],
    "goal": ["action ReduceTemp for PlasticizingPhase {", "  new ReduceTempGoal(checkTemp@(0), 500);", "}", "rule TempTooHigh => ReduceTemp;"],
    "case": ["case Overheating(ReduceTempGoal goal) {", "  if goal.currentValue > goal.targetValue;", "  do HeatingUnit.reduceTemp(targetValue);", "  yields", "    goal.currentValue <= goal.targetValue;", "}"],
}


def demo_loop(lang):
    """d4: the self-adaptive loop, one round, with or without a person approving. After Dalibor et al. [DHM+22] Fig. 2 and
    Fur et al. [FHM+23] Fig. 2, both after Bibow et al. [BDH20]; code from DHM+22 Figs. 17–18."""
    L = lambda x: x[lang]
    comps = {"ev": (24, 24, "Evaluator", T("notice a problem", "ein Problem bemerken")), "re": (226, 24, "Reasoner", T("choose a fix", "eine Lösung wählen")),
             "dp": (24, 128, "Data Processor", T("collect & prepare", "sammeln & aufbereiten")), "ex": (226, 128, "Executor", T("send the command", "den Befehl senden"))}
    boxes = "".join(f'<g class="lp" data-c="{k}"><rect class="box" x="{x}" y="{y}" width="150" height="52" rx="3"/><text class="t" x="{x + 75}" y="{y + 23}" text-anchor="middle">{n}</text>'
                    f'<text class="s" x="{x + 75}" y="{y + 40}" text-anchor="middle">{L(s)}</text></g>' for k, (x, y, n, s) in comps.items())
    conns = [("lake", (300, 252, 220, 252), "Data", 238, 246), ("lakedp", (146, 224, 112, 184), "Data", 92, 212), ("dpev", (70, 128, 70, 80), "CPPS State", 76, 108),
             ("evre", (174, 50, 222, 50), "List<Goal>", 168, 19), ("reex", (300, 76, 300, 124), "Solution", 306, 104), ("excpps", (330, 180, 342, 224), "Command", 268, 210),
             ("cppsex", (366, 224, 354, 182), "Feedback", 364, 214)]
    lines = "".join(f'<g class="lc" data-c="{k}">{_arrow(*xy)}<text class="s" x="{tx}" y="{ty}">{esc(lab)}</text></g>' for k, xy, lab, tx, ty in conns)
    svg = f'''<svg class="dia loop" viewBox="0 0 420 290" role="img" aria-label="{L(T("The self-adaptive loop: data processor, evaluator, reasoner and executor; below them the data lake and the machine", "Die selbstadaptive Schleife: Datenprozessor, Evaluator, Reasoner und Executor; darunter Data Lake und Maschine"))}">
  <rect class="zone line" x="10" y="10" width="380" height="186" rx="6"/>
  {boxes}
  <g class="lp" data-c="lake"><path class="box" d="M136 230v26c0 5 18 8 40 8s40-3 40-8v-26"/><ellipse class="box" cx="176" cy="230" rx="40" ry="8"/><text class="s" x="176" y="282" text-anchor="middle">data lake</text></g>
  <g class="lp" data-c="cpps">{_machine(286, 230, .28)}<text class="s" x="332" y="282" text-anchor="middle">{L(T("the machine", "die Maschine"))}</text></g>
  {lines}
</svg>'''
    states = [
        (["cpps"], ["lake"], ["// raw readings stream in"], T("The machine streams its raw data into the data lake.", "Die Maschine schickt ihre Rohdaten in den Data Lake.")),
        (["dp"], ["lakedp", "dpev"], ["checkTemp@(-1), checkTemp@(0)"], T("The data processor builds the shadow the evaluator needs: the last two temperature readings.", "Der Datenprozessor baut den Schatten, den der Evaluator braucht: die letzten beiden Temperaturwerte.")),
        (["ev"], [], LOOP_CODE["event"], T("The evaluator checks an event model: both readings above 500? Then the event fires.", "Der Evaluator prüft ein Ereignismodell: Beide Werte über 500? Dann tritt das Ereignis ein.")),
        (["ev"], ["evre"], LOOP_CODE["goal"], T("A rule turns the event into a goal: the temperature should come down to 500.", "Eine Regel macht aus dem Ereignis ein Ziel: Die Temperatur soll auf 500 sinken.")),
        (["re"], [], LOOP_CODE["case"], T("The reasoner finds a case that matches the goal — what to do, and what should be true afterwards.", "Der Reasoner findet einen passenden Fall — was zu tun ist und was danach gelten soll.")),
        (["re"], [], ["HeatingUnit.reduceTemp(targetValue)"], T("Proposal ready.", "Vorschlag fertig.")),
        (["ex"], ["reex", "excpps"], ["HeatingUnit.reduceTemp(targetValue)   // via a protocol plugin, e.g. OPC UA"], T("The executor sends the command to the machine.", "Der Executor sendet den Befehl an die Maschine.")),
        (["ex", "cpps"], ["cppsex"], ["yields goal.currentValue <= goal.targetValue"], T("Feedback: has the goal been reached? The loop runs on with the next readings.", "Rückmeldung: Ist das Ziel erreicht? Die Schleife läuft mit den nächsten Werten weiter.")),
    ]
    data = {"steps": [{"c": c, "l": l, "code": _code(code), "say": L(say)} for c, l, code, say in states], "hold": 5,
            "words": {k: L(v) for k, v in dict(step=T("step", "Schritt"), of=T("of", "von"), play=T("play", "abspielen"), pause=T("pause", "anhalten"),
                                                  auto=T("Automatic: nobody is asked.", "Automatisch: Niemand wird gefragt."),
                                                  human=T("Operator approves: the proposal waits in the cockpit.", "Bedienerin gibt frei: Der Vorschlag wartet im Cockpit.")).items()}}
    _check_loop(states)
    inner = f'''<div class="d1-presets mono" role="group"><span class="k">{L(T("MODE:", "MODUS:"))}</span><button type="button" data-m="auto" aria-pressed="true">{L(T("automatic", "automatisch"))}</button><button type="button" data-m="human" aria-pressed="false">{L(T("operator approves", "Bedienerin gibt frei"))}</button></div>
<div class="lp-grid">{svg}<div class="lp-side"><p class="lp-say" aria-live="polite">{data["steps"][0]["say"]}</p><pre class="mono lp-code">{data["steps"][0]["code"]}</pre>
<div class="lp-cockpit"><span class="k mono">COCKPIT</span><p class="lp-msg"></p><button type="button" class="approve mono" disabled>{L(T("approve", "freigeben"))} ✓</button></div></div></div>{controls(lang)}'''
    return demo("dt4", data, inner, T(f"<b>The twin’s intelligence is a chain of small, editable models.</b> An event model says when to act, a goal what should become true, a case how to get there. Switch to <i>operator approves</i>: the loop stops at the proposal until someone releases it in the cockpit — some users do not want automatic execution, “e.g., risking to stop a complete production line because of wrong parametrization” {r('Mic25')}. The architecture stays the same; one step changes. After Dalibor et al. {cite('DHM+22')}, Figs. 2, 17, 18, and Fur et al. {cite('FHM+23')}, Fig. 2, both after Bibow et al. {r('BDH20')}.",
                                      f"<b>Die Intelligenz des Zwillings ist eine Kette kleiner, änderbarer Modelle.</b> Ein Ereignismodell sagt, wann gehandelt wird, ein Ziel, was gelten soll, ein Fall, wie man hinkommt. Schalten Sie auf <i>Bedienerin gibt frei</i>: Die Schleife hält beim Vorschlag an, bis jemand ihn im Cockpit freigibt — manche Nutzer wollen keine automatische Ausführung, etwa wenn eine falsche Parametrierung eine ganze Produktionslinie stoppen könnte {r('Mic25')}. Die Architektur bleibt gleich; ein Schritt ändert sich. Nach Dalibor et al. {cite('DHM+22')}, Abb. 2, 17, 18, und Fur et al. {cite('FHM+23')}, Abb. 2, beide nach Bibow et al. {r('BDH20')}."), lang)


def _check_loop(states):
    joined = "\n".join(l for _, _, code, _ in states for l in code)
    for block in LOOP_CODE.values():
        for line in block:
            assert line in joined, line


def demo_roles(lang):
    """d5: who builds the twin? The two-stage method: MontiGem generates a low-code platform, the platform produces twins.
    After Dalibor et al. [DHM+22] Fig. 5 (quadrants), Fig. 7 (feature diagram), Fig. 8 (configuration), Figs. 12–13, 16a."""
    L = lambda x: x[lang]
    from article_art import gear
    svg = f'''<svg class="dia roles" viewBox="0 0 360 210" role="img" aria-label="{L(T("Four quadrants: design-time models and language plugins, generated by MontiGem into a low-code platform; the platform's twin models, generated into twin instances", "Vier Quadranten: Design-Time-Modelle und Sprach-Plugins, von MontiGem zu einer Low-Code-Plattform generiert; die Zwillingsmodelle der Plattform, zu Zwillings-Instanzen generiert"))}">
  <g class="q" data-q="0"><rect class="box" x="6" y="8" width="130" height="78" rx="4"/><text class="t" x="16" y="28">{L(T("design-time models", "Design-Time-Modelle"))}</text><text class="s" x="16" y="46">{L(T("+ language plugins", "+ Sprach-Plugins"))}</text><text class="s" x="16" y="74">CD · GUI · OCL · tags</text></g>
  <g class="q" data-q="g1"><path class="gearf" d="{gear(180, 47, 20, 9)}"/><circle class="hubf" cx="180" cy="47" r="6"/><text class="s" x="180" y="80" text-anchor="middle">MontiGem</text></g>
  <g class="q" data-q="1"><rect class="box" x="224" y="8" width="130" height="78" rx="4"/><text class="t" x="234" y="28">{L(T("low-code platform", "Low-Code-Plattform"))}</text><text class="s" x="234" y="46">{L(T("editors · viewers", "Editoren · Viewer"))}</text><text class="s" x="234" y="74">{L(T("model library", "Modellbibliothek"))}</text></g>
  <path class="ln dash" d="M289 86V120"/>
  <g class="q" data-q="2"><rect class="box" x="224" y="122" width="130" height="78" rx="4"/><text class="t" x="234" y="142">{L(T("twin models", "Zwillingsmodelle"))}</text><text class="s" x="234" y="160">{L(T("configured", "konfiguriert"))}</text><text class="s" x="234" y="188">OCL · comm · case</text></g>
  <g class="q" data-q="g2"><path class="gearf" d="{gear(180, 161, 20, 9)}"/><circle class="hubf" cx="180" cy="161" r="6"/><text class="s" x="180" y="196" text-anchor="middle">{L(T("twin generator", "Zwillingsgenerator"))}</text></g>
  <g class="q" data-q="3"><rect class="box" x="6" y="122" width="130" height="78" rx="4"/><text class="t" x="16" y="142">{L(T("twin instances", "Zwillings-Instanzen"))}</text><text class="s" x="16" y="160">{L(T("cockpits per machine", "Cockpits je Maschine"))}</text></g>
  <path class="ln" d="M136 47H156M204 47H220M224 161H204M156 161H140"/>
</svg>'''
    feat = [("DT Behavior", 0, "root"), ("DataProcessor · " + L(T("prepare data", "Daten aufbereiten")), 1, ""), ("Evaluator · " + L(T("exactly one", "genau einer")), 1, ""),
            ("SAT Evaluator · " + L(T("logic rules", "Logikregeln")), 2, "on"), ("Expression Evaluator", 2, ""), ("Reasoning · " + L(T("optional", "optional")), 1, ""),
            ("CBR · " + L(T("reuse past fixes", "frühere Lösungen wiederverwenden")), 2, "on"), ("PDDL · " + L(T("plan steps", "Schritte planen")), 2, ""),
            ("SCIP · " + L(T("optimiser", "Optimierer")), 2, ""), ("Communication", 1, ""), ("MQTT · localhost:1234 temperature", 2, "on"),
            ("MQTT · 192.168.1.1 pressure", 2, "on"), ("REST", 2, "on"), ("Executor · " + L(T("at least one", "mindestens einer")), 1, ""), ("Command Executor", 2, "on")]
    tree = '<ul class="feat mono">' + "".join(f'<li style="--d:{d}" class="{c}">{esc(t)}</li>' for t, d, c in feat) + "</ul>"
    ocl = ["context PlasticizingUnit inv pressureMax:", "  forall p in pressureSensor:", "    p.maxValue > 5.5"]
    comm = ["communicate temperature {", "  endpoint: localhost:1234", "  topic: temperature", "  protocol: MQTT", '  link: PlasticizingUnit["pu62"].tempSensor[2]', "}"]
    gui = ['card "State" {', '  head { label "Current State" }', '  body { datatable "State" {', "    rows < states {", '      column "Start", time(eventStart);',
           '      column "State", colorBox(state);', '      column "Report", message;', "  }}}", "}"]
    panels = [
        (T("1 · The platform engineer", "1 · Die Plattform-Ingenieurin"), T("chooses the building blocks of the platform — which kinds of evaluation, reasoning and communication it offers. MontiGem generates the low-code platform from that choice.", "wählt die Bausteine der Plattform — welche Arten von Auswertung, Schlussfolgern und Kommunikation sie anbietet. MontiGem generiert daraus die Low-Code-Plattform."), tree, [0, "g1", 1]),
        (T("2 · The twin designer", "2 · Der Zwillings-Designer"), T("configures one twin in the platform with small models: a rule for valid sensors, where the data comes from, how to fix overheating. No code.", "konfiguriert in der Plattform einen Zwilling mit kleinen Modellen: eine Regel für gültige Sensoren, woher die Daten kommen, wie Überhitzung behoben wird. Kein Code."),
         f'<pre class="mono">{_code(ocl)}</pre><pre class="mono">{_code(comm)}</pre><pre class="mono">{_code(LOOP_CODE["case"][:3] + ["  …"])}</pre>', [1, 2, "g2"]),
        (T("3 · The domain expert", "3 · Die Domänenexpertin"), T("uses the generated twin: its cockpit shows the machine’s states and what the twin did — this is the loop you just ran.", "nutzt den generierten Zwilling: Sein Cockpit zeigt die Zustände der Maschine und was der Zwilling getan hat — das ist die Schleife von eben."), f'<pre class="mono">{_code(gui)}</pre>', [3]),
    ]
    _check_features(feat)
    data = {"steps": [{"title": L(t), "text": L(x), "html": h, "q": [str(q) for q in qs]} for t, x, h, qs in panels],
            "words": {k: L(v) for k, v in dict(step=T("role", "Rolle"), of=T("of", "von"), play=T("play", "abspielen"), pause=T("pause", "anhalten")).items()}}
    p0 = data["steps"][0]
    inner = f'''<div class="ro-grid">{svg}<div class="ro-side"><p class="ro-title t">{p0["title"]}</p><p class="ro-text" aria-live="polite">{p0["text"]}</p><div class="ro-html">{p0["html"]}</div></div></div>{controls(lang)}'''
    return demo("dt5", data, inner, T(f"<b>Two generators, three roles.</b> First the platform is generated, then the platform produces twins — configured by people who do not write code, with small models that can even change while the twin runs. The domain model, by contrast, needs a regeneration (with data migration). After Dalibor et al. {cite('DHM+22')}, Figs. 5, 7, 8, 12, 13, 16a; the vision goes back to Michael and Wortmann {r('MW21')}.",
                                      f"<b>Zwei Generatoren, drei Rollen.</b> Erst wird die Plattform generiert, dann erzeugt die Plattform Zwillinge — konfiguriert von Menschen, die keinen Code schreiben, mit kleinen Modellen, die sich sogar ändern lassen, während der Zwilling läuft. Das Domänenmodell dagegen erfordert eine Neugenerierung (mit Datenmigration). Nach Dalibor et al. {cite('DHM+22')}, Abb. 5, 7, 8, 12, 13, 16a; die Vision geht auf Michael und Wortmann {r('MW21')} zurück."), lang)


def _check_features(feat):
    """The lit configuration must be valid for DHM+22 Fig. 7: exactly one evaluator, at least one executor."""
    on = [t for t, d, c in feat if c == "on"]
    assert sum(t.startswith(("SAT Evaluator", "Expression Evaluator")) for t in on) == 1
    assert sum(t.startswith(("Command Executor", "Local Executor")) for t in on) >= 1


def thumb_dt():
    """Small pictogram for the research page card: the injection-moulding machine ⇄ a twin with models, shadows and a cockpit."""
    return (f'<g class="imm" transform="translate(4 50) scale(.38)">{imm_parts(sensors=True)}</g>'
            '<path class="a" d="M128 62H144"/><path class="a" d="M139 57L144 62L139 67"/><path d="M144 80H128"/><path d="M133 75L128 80L133 85"/>'
            '<rect class="b" x="150" y="22" width="80" height="80" rx="4"/><rect class="f" x="158" y="30" width="64" height="10" rx="1"/>'
            '<rect class="b" x="156" y="48" width="28" height="20" rx="1"/><rect class="b" x="160" y="52" width="28" height="20" rx="1"/>'
            '<rect class="b" x="194" y="50" width="26" height="8" rx="4"/><rect class="b" x="194" y="62" width="26" height="8" rx="4"/><path d="M156 88H220M156 94H204"/>')
