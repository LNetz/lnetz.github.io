"""
Figures of the Evolutionary Algorithms article (research-ea.html, _build/ea.py). Every mark comes from a real, seeded
run in ea_sim.py; static diagrams are inline SVG with the .dia classes, interactive ones ship their states (or the
data for a small live computation) as data-json — assets/ea.js swaps, highlights and draws. Figures are redrawn after
the master's thesis [Net17] and [NWN+15] ("After …, Fig. x"); the article's literature list (REFS) lives here too.
"""
import html
import json
import math

from ai4se import T, fig, demo, controls, cite, _link
import ea_sim as sim

esc = html.escape

# ---------------- literature (numbered) ----------------
REFS = [
    ("ES15", _link("A. E. Eiben, J. E. Smith: Introduction to Evolutionary Computing, 2nd ed. Springer (2015).", "https://doi.org/10.1007/978-3-662-44874-8")),
    ("Hol75", "J. H. Holland: Adaptation in Natural and Artificial Systems. University of Michigan Press (1975)."),
    ("Gol89", "D. E. Goldberg: Genetic Algorithms in Search, Optimization, and Machine Learning. Addison-Wesley (1989)."),
    ("AIMA", _link("S. Russell, P. Norvig: Artificial Intelligence: A Modern Approach, 4th ed. (2020), §4.1.4 Evolutionary algorithms.", "https://aima.cs.berkeley.edu/contents.html")),
    ("NFL", _link("D. H. Wolpert, W. G. Macready: No Free Lunch Theorems for Optimization. IEEE TEVC 1(1), 67–82 (1997).", "https://doi.org/10.1109/4235.585893")),
    ("GD91", _link("D. E. Goldberg, K. Deb: A Comparative Analysis of Selection Schemes Used in Genetic Algorithms. FOGA 1991.", "https://www.cse.unr.edu/~sushil/class/gas/papers/Select.pdf")),
    ("Sal17", _link("T. Salimans, J. Ho, X. Chen, S. Sidor, I. Sutskever: Evolution Strategies as a Scalable Alternative to Reinforcement Learning (2017).", "https://arxiv.org/abs/1703.03864")),
    ("HJ01", _link("M. Harman, B. F. Jones: Search-based software engineering. Information and Software Technology 43(14), 833–839 (2001).", "https://doi.org/10.1016/S0950-5849(01)00189-6")),
    ("FA13", _link("G. Fraser, A. Arcuri: Whole Test Suite Generation. IEEE TSE 39(2), 276–291 (2013).", "https://doi.org/10.1109/TSE.2012.14")),
    ("LeG12", _link("C. Le Goues, M. Dewey-Vogt, S. Forrest, W. Weimer: A Systematic Study of Automated Program Repair: Fixing 55 out of 105 Bugs for $8 Each. ICSE 2012.", "https://doi.org/10.1109/ICSE.2012.6227211")),
    ("Qi15", _link("Z. Qi, F. Long, S. Achour, M. Rinard: An Analysis of Patch Plausibility and Correctness for Generate-and-Validate Patch Generation Systems. ISSTA 2015.", "https://doi.org/10.1145/2771783.2771791")),
    ("LH15", _link("W. B. Langdon, M. Harman: Optimizing Existing Software With Genetic Programming. IEEE TEVC 19(1), 118–135 (2015).", "https://doi.org/10.1109/TEVC.2013.2281544")),
    ("Mao16", _link("K. Mao, M. Harman, Y. Jia: Sapienz: Multi-objective Automated Testing for Android Applications. ISSTA 2016.", "https://doi.org/10.1145/2931037.2931054")),
    ("PerOp", _link("PerOpteryx: architecture optimisation for Palladio component models.", "https://www.palladio-simulator.com/tools/peropteryx/")),
    ("ELM", _link("J. Lehman et al.: Evolution through Large Models (2022).", "https://arxiv.org/abs/2206.08896")),
    ("FunS", _link("B. Romera-Paredes et al.: Mathematical discoveries from program search with large language models. Nature 625, 468–475 (2024).", "https://doi.org/10.1038/s41586-023-06924-6")),
    ("AlphaE", _link("A. Novikov et al. (Google DeepMind): AlphaEvolve: A coding agent for scientific and algorithmic discovery (2025).", "https://arxiv.org/abs/2506.13131")),
    ("BS02", _link("H.-G. Beyer, H.-P. Schwefel: Evolution strategies — A comprehensive introduction. Natural Computing 1, 3–52 (2002).", "https://doi.org/10.1023/A:1015059928466")),
    ("Han16", _link("N. Hansen: The CMA Evolution Strategy: A Tutorial (2016).", "https://arxiv.org/abs/1604.00772")),
    ("SP97", _link("R. Storn, K. Price: Differential Evolution. Journal of Global Optimization 11, 341–359 (1997).", "https://doi.org/10.1023/A:1008202821328")),
    ("Deb02", _link("K. Deb, A. Pratap, S. Agarwal, T. Meyarivan: A fast and elitist multiobjective genetic algorithm: NSGA-II. IEEE TEVC 6(2), 182–197 (2002).", "https://doi.org/10.1109/4235.996017")),
    ("MC15", _link("J.-B. Mouret, J. Clune: Illuminating search spaces by mapping elites (2015).", "https://arxiv.org/abs/1504.04909")),
    ("SM02", _link("K. O. Stanley, R. Miikkulainen: Evolving Neural Networks through Augmenting Topologies. Evolutionary Computation 10(2), 99–127 (2002).", "https://doi.org/10.1162/106365602320169811")),
    ("LS11", _link("J. Lehman, K. O. Stanley: Abandoning Objectives: Evolution Through the Search for Novelty Alone. Evolutionary Computation 19(2), 189–223 (2011).", "https://doi.org/10.1162/EVCO_a_00025")),
    ("ST5", _link("J. D. Lohn, D. S. Linden, G. S. Hornby, W. F. Kraus, A. Rodriguez-Arroyo, S. E. Seufert: Evolutionary Design of an X-Band Antenna for NASA’s Space Technology 5 Mission. NASA/DoD Conference on Evolvable Hardware (2003).", "https://ntrs.nasa.gov/citations/20030067398")),
    ("HLL11", _link("G. S. Hornby, J. D. Lohn, D. S. Linden: Computer-Automated Evolution of an X-Band Antenna for NASA’s Space Technology 5 Mission. Evolutionary Computation 19(1), 1–23 (2011).", "https://doi.org/10.1162/EVCO_a_00005")),
    ("Jen83", "N. O. Jensen: A Note on Wind Generator Interaction. Risø-M-2411, Risø National Laboratory (1983)."),
    ("Gra05", _link("S. A. Grady, M. Y. Hussaini, M. M. Abdullah: Placement of wind turbines using genetic algorithms. Renewable Energy 30(2), 259–270 (2005).", "https://doi.org/10.1016/j.renene.2004.05.007")),
    ("Ha17", _link("D. Ha: A Visual Guide to Evolution Strategies (2017).", "https://blog.otoro.net/2017/10/29/visual-evolution-strategies/")),
    ("geneial", _link("geneial: a template-based C++11 library for genetic algorithms (MIT).", "https://github.com/geneial/geneial")),
]
_NUM = {k: n for n, (k, _) in enumerate(REFS, 1)}


def r(key):
    """A numbered reference into this article's literature list."""
    return f'<a class="cite" href="#ref-{_NUM[key]}">[{_NUM[key]}]</a>'


def _arrow(x1, y1, x2, y2, cls="ln"):
    """A straight arrow whose head is its own path (takes on the arrow's colour)."""
    a = math.atan2(y2 - y1, x2 - x1)
    h = [(x2 - 7 * math.cos(a - .45), y2 - 7 * math.sin(a - .45)), (x2 - 7 * math.cos(a + .45), y2 - 7 * math.sin(a + .45))]
    return (f'<path class="{cls}" d="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}"/>'
            f'<path class="{cls}" d="M{h[0][0]:.1f} {h[0][1]:.1f}L{x2:.1f} {y2:.1f}L{h[1][0]:.1f} {h[1][1]:.1f}"/>')


def _n(v, d=3):
    return round(v, d)


# ---------------- the shared run on the toy site ----------------
RHO = 20
TOY = sim.TOY
GEN = 7                                           # the generation the loop figure dissects (7 → 8)
BOOK = TOY["books"][GEN]
CELL = sim.SITE / RHO


def _m(cell, rho=RHO):
    return sim.centre(cell, rho)


def site(layout, x0, y0, size, rho=RHO, grid=False, iso=True, cls="tb", extra="", r_=3.0, label=True):
    """The toy site (1000 m square, north up): optional grid, the iso-score lines of 'better toward the
    north-east', and turbines as dots. `layout` is a list of cells (grid genes) or of (x, y) metres if rho is None."""
    s = size / sim.SITE
    P = lambda x, y: (x0 + x * s, y0 + (sim.SITE - y) * s)
    out = [f'<rect class="box" x="{x0}" y="{y0}" width="{size}" height="{size}"/>']
    if grid:
        step = size / rho
        out.append('<path class="gridl" d="' + "".join(f"M{x0 + k * step:.1f} {y0}V{y0 + size}M{x0} {y0 + k * step:.1f}H{x0 + size}" for k in range(1, rho)) + '"/>')
    if iso:
        for c in (.2, .4, .6, .8):                # x + y = 2000·c
            t = 2 * sim.SITE * c
            a = (max(0, t - sim.SITE), min(sim.SITE, t))
            b = (min(sim.SITE, t), max(0, t - sim.SITE))
            (ax, ay), (bx, by) = P(*a), P(*b)
            out.append(f'<path class="iso" d="M{ax:.1f} {ay:.1f}L{bx:.1f} {by:.1f}"/>')
            if label:
                lx, ly = P(*b)
                out.append(f'<text class="s iso-l" x="{lx + 3:.1f}" y="{ly - 3:.1f}">{c:.1f}</text>' if c > .5 else
                           f'<text class="s iso-l" x="{ax + 3:.1f}" y="{ay + 10:.1f}">{c:.1f}</text>')
    for p in layout:
        x, y = (_m(p, rho) if rho else p)
        px, py = P(x, y)
        out.append(f'<circle class="{cls}" cx="{px:.1f}" cy="{py:.1f}" r="{r_}"/>')
    return "".join(out) + extra


def site_xy(x, y, x0, y0, size):
    s = size / sim.SITE
    return x0 + x * s, y0 + (sim.SITE - y) * s


# =====================================================================
# F1  What you give / what you get
# =====================================================================
def fig_map(lang):
    L = lambda x: x[lang]
    a4 = r("AIMA")
    rows = [
        (T("a formal model of the problem<br><span class=\"faint\">rules, constraints</span>", "ein formales Modell des Problems<br><span class=\"faint\">Regeln, Bedingungen</span>"),
         T("search and solvers: A*, planners, SAT/SMT, integer programming", "Suche und Solver: A*, Planer, SAT/SMT, ganzzahlige Optimierung"), "—", ""),
        (T("examples<br><span class=\"faint\">data</span>", "Beispiele<br><span class=\"faint\">Daten</span>"), "—",
         T('machine learning: regression, deep networks, LLMs <a href="research-ai4se.html#neural">→ part 2</a>', 'Maschinelles Lernen: Regression, tiefe Netze, LLMs <a href="research-ai4se.html#neural">→ Teil 2</a>'), ""),
        (T("only a score<br><span class=\"faint\">a way to rate a candidate</span>", "nur eine Bewertung<br><span class=\"faint\">ein Weg, Kandidaten zu benoten</span>"),
         T(f"hill climbing, simulated annealing, <b>evolutionary algorithms</b> {a4}", f"Bergsteigen, Simulated Annealing, <b>evolutionäre Algorithmen</b> {a4}"),
         T("neuroevolution, hyperparameter search — evolving the settings of a model", "Neuroevolution, Hyperparameter-Suche — die Einstellungen eines Modells evolvieren"), "ea"),
    ]
    head = f'<tr><th>{L(T("You give …", "Sie geben …"))}</th><th>{L(T("… and get an answer for this one problem", "… und bekommen eine Antwort für genau dieses Problem"))}</th><th>{L(T("… and get a reusable model", "… und bekommen ein wiederverwendbares Modell"))}</th></tr>'
    body = "".join(f'<tr><td>{L(a)}</td><td class="{"hl" if k == "ea" else ""}">{L(b) if isinstance(b, dict) else b}</td><td>{L(c) if isinstance(c, dict) else c}</td></tr>' for a, b, c, k in rows)
    return (f'<figure class="media art-fig"><div class="tbl-wrap"><table class="tbl mono ea-map">{head}{body}</table></div>'
            f'<figcaption class="mono">{L(T(f"<b>Sort AI methods by what you give them and what you get back.</b> Evolutionary algorithms need neither a formal model nor training data — only a way to score a candidate — and they return a good candidate, not a model. One cell overlaps with machine learning: evolution can also tune or grow the model itself. Russell and Norvig file EAs under search and optimisation, next to hill climbing {a4}.", f"<b>KI-Verfahren danach sortiert, was man ihnen gibt und was man zurückbekommt.</b> Evolutionäre Algorithmen brauchen weder ein formales Modell noch Trainingsdaten — nur einen Weg, einen Kandidaten zu bewerten — und sie liefern einen guten Kandidaten, kein Modell. Eine Zelle überschneidet sich mit maschinellem Lernen: Evolution kann auch das Modell selbst einstellen oder wachsen lassen. Russell und Norvig ordnen EAs bei Suche und Optimierung ein, neben dem Bergsteigen {a4}."))}</figcaption></figure>')


# =====================================================================
# F2  Learning from data vs searching with a score (toggle: the LLM as the variation step)
# =====================================================================
def demo_pipes(lang):
    L = lambda x: x[lang]
    b = lambda x, y, w, t, s="", cls="box": (f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="40" rx="3"/>'
                                             f'<text class="t" x="{x + w / 2}" y="{y + (17 if s else 24)}" text-anchor="middle">{t}</text>'
                                             + (f'<text class="s" x="{x + w / 2}" y="{y + 32}" text-anchor="middle">{s}</text>' if s else ""))
    top = (b(10, 30, 110, L(T("examples", "Beispiele")), L(T("data with answers", "Daten mit Antworten")))
           + _arrow(120, 50, 160, 50) + b(160, 30, 120, L(T("loss", "Fehler")), L(T("how wrong?", "wie falsch?")))
           + _arrow(280, 50, 320, 50) + b(320, 30, 130, L(T("gradient", "Gradient")), L(T("which way is better?", "welche Richtung ist besser?")))
           + _arrow(450, 50, 490, 50) + b(490, 30, 120, L(T("model", "Modell")), L(T("for new inputs", "für neue Eingaben")), "box hl")
           + _arrow(385, 30, 385, 14, "ln") + f'<text class="s" x="393" y="18">{L(T("adjust the weights, repeat", "Gewichte anpassen, wiederholen"))}</text>')
    y = 130
    chain = L(T("wind → wake → power → cost", "Wind → Nachlauf → Leistung → Kosten"))
    bottom = (b(10, y, 110, L(T("candidates", "Kandidaten")), L(T("a population", "eine Population")))
              + _arrow(120, y + 20, 160, y + 20) + b(160, y, 160, L(T("score", "Bewertung")), chain)
              + _arrow(320, y + 20, 350, y + 20) + b(350, y, 110, L(T("keep the better", "die Besseren behalten")))
              + _arrow(460, y + 20, 490, y + 20)
              + '<g class="vary">' + b(490, y, 120, "", "", "box hl")
              + f'<text class="t v-classic" x="550" y="{y + 17}" text-anchor="middle">{L(T("vary", "variieren"))}</text>'
              + f'<text class="s v-classic" x="550" y="{y + 32}" text-anchor="middle">{L(T("recombine, mutate", "kreuzen, mutieren"))}</text>'
              + f'<text class="t v-llm" x="550" y="{y + 17}" text-anchor="middle">{L(T("an LLM", "ein LLM"))}</text>'
              + f'<text class="s v-llm" x="550" y="{y + 32}" text-anchor="middle">{L(T("writes a variant of k parents", "schreibt eine Variante von k Eltern"))}</text></g>'
              + f'<path class="ln" d="M550 {y + 40}V{y + 62}H65V{y + 40}"/>' + _arrow(65, y + 50, 65, y + 41)
              + f'<text class="s" x="300" y="{y + 56}" text-anchor="middle">{L(T("the next generation, repeat", "die nächste Generation, wiederholen"))}</text>')
    lbl = (f'<text class="s" x="10" y="16">{L(T("LEARNING FROM DATA", "AUS DATEN LERNEN"))}</text>'
           f'<text class="s" x="10" y="{y - 14}">{L(T("SEARCHING WITH A SCORE", "MIT EINER BEWERTUNG SUCHEN"))}</text>')
    svg = f'<svg class="dia pipes" viewBox="0 0 620 210" role="img" aria-label="{L(T("Two pipelines: data, loss, gradient, model; and candidates, score, keep the better, vary", "Zwei Abläufe: Daten, Fehler, Gradient, Modell; und Kandidaten, Bewertung, die Besseren behalten, variieren"))}">{lbl}{top}{bottom}</svg>'
    btn = [T("classic", "klassisch"), T("LLM as the variation step", "LLM als Variationsschritt")]
    buttons = "".join(f'<button type="button" data-v="{k}" aria-pressed="{"true" if k == 0 else "false"}">{L(x)}</button>' for k, x in enumerate(btn))
    inner = f'<div class="d1-presets mono" role="group"><span class="k">{L(T("VARIATION:", "VARIATION:"))}</span>{buttons}</div>{_scroll(svg)}'
    return demo("ea2", {}, inner, T(
        f"<b>What each needs, what each gives.</b> Learning needs examples and a differentiable loss and yields a model; evolutionary search needs only a score — which may itself come from a simulation, here the wind-farm chain of [Net17] Fig. 3 — and yields good candidates. Switch the variation step: in FunSearch {r('FunS')} and AlphaEvolve {r('AlphaE')} an LLM writes the variants, while the loop and the evaluator stay classical.",
        f"<b>Was jeder braucht, was jeder liefert.</b> Lernen braucht Beispiele und eine differenzierbare Fehlerfunktion und liefert ein Modell; evolutionäre Suche braucht nur eine Bewertung — die selbst aus einer Simulation stammen kann, hier die Windpark-Kette aus [Net17] Abb. 3 — und liefert gute Kandidaten. Schalten Sie den Variationsschritt um: Bei FunSearch {r('FunS')} und AlphaEvolve {r('AlphaE')} schreibt ein LLM die Varianten, Schleife und Bewertung bleiben klassisch."), lang)


def _scroll(svg):
    from project_content import dia_scroll
    return dia_scroll(svg)


# =====================================================================
# F3  The loop: one real generation, step by step
# =====================================================================
NODES = [  # (key, plain name, thesis / geneial name)
    ("stop", T("stop? → return the best", "Stopp? → das Beste zurück"), T("stopping criteria", "Abbruchkriterien")),
    ("select", T("select parents", "Eltern wählen"), T("selection", "Selektion")),
    ("pair", T("pair up", "Paare bilden"), T("coupling", "Kopplung")),
    ("cross", T("recombine", "kreuzen"), T("crossover", "Crossover")),
    ("choose", T("pick children", "Kinder auswählen"), T("choosing", "Auswahl")),
    ("mutate", T("mutate", "mutieren"), T("mutation", "Mutation")),
    ("eval", T("score", "bewerten"), T("fitness", "Fitness")),
    ("replace", T("drop the worst", "aussortieren"), T("replacement", "Ersetzung")),
    ("new", T("add newcomers", "Neulinge hinzu"), T("replenish", "Auffüllen")),
]


def _loop_ring(lang, cnt="", cnt2="", inner=False):
    """The ring after Net17 Fig. 13; `inner` returns only the drawing (for the hero), with a fixed centre text."""
    L = lambda x: x[lang]
    cx, cy, R = 220, 160, 104
    out = [f'<circle class="ring" cx="{cx}" cy="{cy}" r="{R}"/>']
    pos = {}
    for k, (key, name, th) in enumerate(NODES):
        a = -math.pi / 2 + 2 * math.pi * k / len(NODES)
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        pos[key] = (x, y)
        lx, ly = cx + (R + 14) * math.cos(a), cy + (R + 14) * math.sin(a)
        anchor = "middle" if abs(math.cos(a)) < .3 else ("start" if math.cos(a) > 0 else "end")
        dy = -14 if math.sin(a) < -.6 else (6 if math.sin(a) > .6 else -2)
        out.append(f'<g class="nd" data-n="{key}"><circle cx="{x:.1f}" cy="{y:.1f}" r="5"/>'
                   f'<text x="{lx:.1f}" y="{ly + dy:.1f}" text-anchor="{anchor}">{L(name)}</text>'
                   f'<text class="s" x="{lx:.1f}" y="{ly + dy + 12:.1f}" text-anchor="{anchor}">{L(th)}</text></g>')
    # arrowheads along the ring (clockwise)
    for k in range(len(NODES)):
        a = -math.pi / 2 + 2 * math.pi * (k + .5) / len(NODES)
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        t = a + math.pi / 2
        p1 = (x - 6 * math.cos(t) + 4 * math.cos(a), y - 6 * math.sin(t) + 4 * math.sin(a))
        p2 = (x - 6 * math.cos(t) - 4 * math.cos(a), y - 6 * math.sin(t) - 4 * math.sin(a))
        out.append(f'<path class="ln" d="M{p1[0]:.1f} {p1[1]:.1f}L{x:.1f} {y:.1f}L{p2[0]:.1f} {p2[1]:.1f}"/>')
    # elitism: a dashed chord from 'select' to 'drop the worst' (the elite skips everything in between)
    (x1, y1), (x2, y2) = pos["select"], pos["replace"]
    pid = f"elite-{lang}-{'h' if inner else 'f'}"                    # the label runs along the chord
    out.append(f'<path id="{pid}" class="ln dash" d="M{x2:.1f} {y2:.1f}Q{cx + 10} {cy + 6} {x1:.1f} {y1:.1f}"/>'
               f'<text class="s" dy="-5"><textPath href="#{pid}" startOffset="52%" text-anchor="middle">{L(T("the elite skips all", "die Elite überspringt alles"))}</textPath></text>')
    # the factory feeding newcomers
    xn, yn = pos["new"]
    out.append(f'<rect class="box" x="{xn - 110:.1f}" y="{yn + 16:.1f}" width="70" height="22" rx="2"/><text class="s" x="{xn - 75:.1f}" y="{yn + 31:.1f}" text-anchor="middle">{L(T("factory", "Fabrik"))}</text>'
               + _arrow(xn - 40, yn + 20, xn - 6, yn + 4))
    out.append(f'<text class="cnt" x="{cx}" y="{cy + 36}" text-anchor="middle">{cnt}</text><text class="s cnt2" x="{cx}" y="{cy + 52}" text-anchor="middle">{cnt2}</text>')
    if inner:
        return "".join(out)
    return f'<svg class="dia ring-svg" viewBox="0 0 440 300" role="img" aria-label="{L(T("The loop of an evolutionary algorithm as a ring of nine steps", "Die Schleife eines evolutionären Algorithmus als Ring aus neun Schritten"))}">{"".join(out)}</svg>'


def demo_loop(lang):
    """ea3: generation 7 → 8 of the toy run, after Net17 Fig. 13 and NWN+15 Fig. 2."""
    L = lambda x: x[lang]
    B = BOOK
    pop, fit = B["pop"], B["fit"]
    ids = [f"p{k}" for k in range(len(pop))]
    lay = {f"p{k}": l for k, l in enumerate(pop)}
    fv = {f"p{k}": fit[k] for k in range(len(pop))}
    for k, l in enumerate(B["kids"]):
        lay[f"c{k}"] = l
        fv[f"c{k}"] = sim.fitness(l, RHO)
    for k, l in enumerate(B["fresh"]):
        lay[f"n{k}"] = l
        fv[f"n{k}"] = sim.fitness(l, RHO)
    sel_count = {i: B["sel"].count(i) for i in set(B["sel"])}
    elite = {"p0", "p1"}
    mut = {k for k, _ in B["mutated"]}
    pair_lbl = {f"c{k}": f"#{a + 1} × #{b + 1}" for k, (a, b) in enumerate(B["pairs"])}
    kids = [f"c{k}" for k in range(len(B["kids"]))]
    merged = [f"{w}{k}" for w, k in B["merged"]]
    keep = merged[:len(pop) - len(B["fresh"])]
    struck = merged[len(keep):]
    final = sorted(keep + [f"n{k}" for k in range(len(B["fresh"]))], key=lambda i: -fv[i])
    n_sel, n_kids, n_mut, n_new = len(B["sel"]), len(kids), len(mut), len(B["fresh"])
    assert max(sel_count.values()) == 3                     # "… three times" in the text below
    W = lambda en, de: L(T(en, de))

    def row(i, cls="", note=""):
        return [i, cls, note]
    base = [row(i, "elite" if i in elite else "") for i in ids]
    states = []
    states.append(dict(node=["stop"], rows=base, cnt=f"{len(pop)}", cnt2=W(f"generation {GEN}", f"Generation {GEN}"),
        say=W(f"Generation {GEN}: 20 layouts, ranked by fitness. Stop? Not yet — the best possible score is unknown, so only the budget of 60 generations ends this run.",
              f"Generation {GEN}: 20 Layouts, nach Fitness sortiert. Stopp? Noch nicht — die bestmögliche Bewertung ist unbekannt, also beendet nur das Budget von 60 Generationen diesen Lauf.")))
    states.append(dict(node=["select"], rows=[row(i, ("elite " if i in elite else "") + ("sel" if int(i[1:]) in sel_count else ""), f"×{sel_count[int(i[1:])]}" if int(i[1:]) in sel_count else "") for i in ids],
        cnt=f"20 → {n_sel}", cnt2=W("parents", "Eltern"),
        say=W(f"Roulette wheel: each layout gets a slice proportional to its fitness, the wheel is spun {n_sel} times. Good layouts are drawn more often — #{max(sel_count, key=sel_count.get) + 1} three times — but weaker ones get a chance, too. The two best (outlined) are the elite: they will survive unchanged.",
              f"Glücksrad: Jedes Layout bekommt ein Stück proportional zu seiner Fitness, das Rad wird {n_sel}-mal gedreht. Gute Layouts werden öfter gezogen — #{max(sel_count, key=sel_count.get) + 1} dreimal —, aber auch schwächere haben eine Chance. Die beiden besten (umrandet) sind die Elite: Sie überleben unverändert.")))
    pend = [row(i, "pending", pair_lbl[i]) for i in kids]
    states.append(dict(node=["pair", "cross"], rows=base + [["—", "div", ""]] + pend, cnt=f"{n_sel} → {n_kids}", cnt2=W("pairs → children", "Paare → Kinder"),
        say=W(f"The parents are paired at random — one parent may appear in several pairs — and each pair is recombined into one child. The children are not scored yet.",
              f"Die Eltern werden zufällig zu Paaren — ein Elternteil kann in mehreren Paaren stehen —, und jedes Paar wird zu einem Kind gekreuzt. Die Kinder sind noch nicht bewertet.")))
    states.append(dict(node=["choose", "mutate"], rows=base + [["—", "div", ""]] + [row(i, "pending" + (" mut" if int(i[1:]) in mut else ""), pair_lbl[i]) for i in kids],
        cnt=f"{n_kids} → {n_mut}", cnt2=W("mutated", "mutiert"),
        say=W(f"Each child is picked for mutation with a probability of 30 % — here {n_mut} of {n_kids}. Mutation moves one to three of its turbines, preferably the badly placed ones.",
              f"Jedes Kind wird mit 30 % Wahrscheinlichkeit zur Mutation ausgewählt — hier {n_mut} von {n_kids}. Die Mutation verschiebt eine bis drei seiner Turbinen, bevorzugt die schlecht platzierten.")))
    states.append(dict(node=["eval"], rows=base + [["—", "div", ""]] + [row(i, "child" + (" mut" if int(i[1:]) in mut else ""), pair_lbl[i]) for i in kids],
        cnt=f"{n_kids}", cnt2=W("scored", "bewertet"),
        say=W("Now the children are scored — in the real wind farm, this is the expensive simulation. Some children beat both their parents, some do not.",
              "Jetzt werden die Kinder bewertet — im echten Windpark ist das die teure Simulation. Manche Kinder schlagen beide Eltern, manche nicht.")))
    states.append(dict(node=["replace"], rows=[row(i, ("child " if i[0] == "c" else "") + ("elite " if i in elite else "") + ("struck" if i in struck else "")) for i in merged],
        cnt=f"{len(merged)} → {len(keep)}", cnt2=W("survivors", "Überlebende"),
        say=W(f"Parents and children in one ranking: the {len(struck)} worst are dropped. The elite cannot drop out — they are at the top.",
              f"Eltern und Kinder in einer Rangliste: Die {len(struck)} schlechtesten fallen weg. Die Elite kann nicht herausfallen — sie steht oben.")))
    states.append(dict(node=["new"], rows=[row(i, ("child " if i[0] == "c" else "") + ("elite " if i in elite else "")) for i in keep] + [row(f"n{k}", "new") for k in range(n_new)],
        cnt=f"{len(keep)} + {n_new}", cnt2=W("newcomers", "Neulinge"),
        say=W(f"{n_new} random layouts from the factory join — after the culling, so they get in although they are weak. They keep the population diverse.",
              f"{n_new} zufällige Layouts aus der Fabrik kommen dazu — nach dem Aussieben, damit sie trotz ihrer Schwäche hineinkommen. Sie halten die Population vielfältig.")))
    states.append(dict(node=["stop"], rows=[row(i, ("child " if i[0] == "c" else "") + ("new" if i[0] == "n" else "")) for i in final],
        cnt="20", cnt2=W(f"generation {GEN + 1}", f"Generation {GEN + 1}"),
        say=W(f"Generation {GEN + 1}, re-ranked. The newcomers sit at the bottom, the shortest bars — and they stay anyway. Best fitness {fv[final[0]]:.3f} (before: {fit[0]:.3f}).",
              f"Generation {GEN + 1}, neu sortiert. Die Neulinge stehen unten, die kürzesten Balken — und sie bleiben trotzdem. Beste Fitness {fv[final[0]]:.3f} (vorher: {fit[0]:.3f}).")))
    assert .45 <= min(fv.values()) and max(fv.values()) <= .65
    data = {"states": states, "f": {k: _n(v) for k, v in fv.items()}, "lay": lay, "rho": RHO, "lo": .45, "hi": .65,
            "words": {"play": W("play", "abspielen"), "pause": W("pause", "anhalten"), "step": W("step", "Schritt"), "of": W("of", "von"),
                      "tap": W("tap a row to see its layout", "Zeile antippen zeigt das Layout")}}
    mini = f'<svg class="dia lp-mini" viewBox="0 0 132 140" aria-hidden="true">{site([], 6, 4, 120, iso=True, label=False)}<g class="mini-dots"></g><text class="s mini-l" x="66" y="138" text-anchor="middle"></text></svg>'
    inner = (f'<div class="lp3"><div class="lp3-ring">{_loop_ring(lang)}</div>'
             f'<div class="lp3-side"><p class="lp3-say" aria-live="polite"></p><div class="lp3-pane"><div class="rank" role="list"></div>{mini}</div></div></div>'
             + controls(lang))
    return demo("ea3", data, inner, T(
        f"<b>One generation of a genetic algorithm, on 20 wind-farm layouts.</b> Each row is a whole layout of 12 turbines; the bar is its fitness. Every number comes from a seeded run of the toy problem (generation {GEN} → {GEN + 1}). Plain names on the ring; underneath, the names in my master’s thesis and in geneial. After [Net17] Fig. 13 and [NWN+15] Fig. 2.",
        f"<b>Eine Generation eines genetischen Algorithmus, an 20 Windpark-Layouts.</b> Jede Zeile ist ein ganzes Layout aus 12 Turbinen; der Balken ist seine Fitness. Jede Zahl stammt aus einem reproduzierbaren Lauf des Spielzeugproblems (Generation {GEN} → {GEN + 1}). Auf dem Ring die einfachen Namen, darunter die Namen aus meiner Masterarbeit und aus geneial. Nach [Net17] Abb. 13 und [NWN+15] Abb. 2."), lang)


# =====================================================================
# F4  Genotype → phenotype: cells per axis
# =====================================================================
def _log10_comb(n, k):
    return (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)) / math.log(10)


def _median(v):
    v = sorted(v)
    return v[len(v) // 2] if len(v) % 2 else (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2


GA_BY_RHO = {rho: [sim.toy_ga(s, rho=rho, gens=40)["hist"][-1][0] for s in range(1, 6)] for rho in (4, 10, 20, 100, 10000)}


def demo_encoding(lang):
    """ea4: the same idea at different resolutions — what fits, what is reachable, how big the space is."""
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    S0 = 168
    presets = []
    # 1. the thesis example, ρ = 5, five positions → bits
    pts = [(248, 183), (572, 301), (893, 520), (312, 621), (741, 952)]
    cells = [(int(x * 5 / 1000), int(y * 5 / 1000)) for x, y in pts]
    idx = sorted(c[0] + c[1] * 5 for c in cells)
    bits = "".join("1" if i in idx else "0" for i in range(25))
    gen = [f"p{k + 1} = ({x}, {y})  → {W('cell', 'Zelle')} {c[0] + 5 * c[1]}" for k, ((x, y), c) in enumerate(zip(pts, cells))]
    gen += ["", W("one bit per cell:", "ein Bit je Zelle:"), " ".join(bits[k:k + 5] for k in range(0, 25, 5))]
    svg = site(cells, 4, 4, S0, rho=5, grid=True, iso=False, cls="tb hl") + "".join(
        f'<text class="s" x="{4 + (c[0] + .5) * S0 / 5:.1f}" y="{4 + (5 - c[1] - .5) * S0 / 5 + 14:.1f}" text-anchor="middle">{c[0] + 5 * c[1]}</text>' for c in cells)
    presets.append(dict(label="ρ = 5", svg=svg, gen=gen, read=[(W("cells per axis", "Zellen je Achse"), "5"), (W("cell size", "Zellgröße"), "200 m"),
                    (W("turbines", "Turbinen"), "5 (" + W("thesis example", "Beispiel der Arbeit") + ")"), (W("bits", "Bits"), "25")],
                    note=W("The worked example of my thesis: five positions on a 5 × 5 grid become the bits 1, 7, 14, 16 and 23. Simple — but at ρ = 10,000 one chromosome would need 10⁸ bits.",
                           "Das Rechenbeispiel meiner Arbeit: Fünf Positionen auf einem 5 × 5-Raster werden zu den Bits 1, 7, 14, 16 und 23. Einfach — aber bei ρ = 10.000 bräuchte ein Chromosom 10⁸ Bits.")))
    # 2. ρ = 6: too dense — the factory gives up
    log = []
    rng = sim.Rng(11)
    lay6 = sim.factory(rng, 6, log=log, tries=40)
    placed = [p for ok, p in log if ok == "ok"]
    assert lay6 is None and len(placed) <= sim.max_fit(6) == 9
    reverted = sum(1 for ok, _ in log if ok == "rev")
    svg = site(placed, 4, 4, S0, rho=6, grid=True, iso=False, cls="tb") + "".join(
        f'<circle class="disc" cx="{4 + (c[0] + .5) * S0 / 6:.1f}" cy="{4 + (6 - c[1] - .5) * S0 / 6:.1f}" r="{120 * S0 / 1000:.1f}"/>' for c in placed)
    presets.append(dict(label="ρ = 6", svg=svg, gen=[f"({c[0]}, {c[1]})" for c in placed] + ["", W(f"{reverted} insertions reverted", f"{reverted} Einfügungen zurückgenommen"), W("→ gives up: layout too dense", "→ gibt auf: Layout zu dicht")],
                    read=[(W("cells per axis", "Zellen je Achse"), "6"), (W("cell size", "Zellgröße"), "167 m"), (W("turbines that fit (exact)", "passende Turbinen (exakt)"), "9"),
                          (W("search space", "Suchraum"), "—")],
                    note=W(f"Neighbouring cells are only 167 m apart, diagonal ones 236 m — both closer than 240 m. At most 9 turbines fit; the factory placed {len(placed)} and then found no free cell. 12 turbines cannot be encoded at all.",
                           f"Benachbarte Zellen liegen nur 167 m auseinander, diagonale 236 m — beides näher als 240 m. Höchstens 9 Turbinen passen; die Fabrik setzte {len(placed)} und fand dann keine freie Zelle mehr. 12 Turbinen lassen sich gar nicht codieren.")))
    # 3. ρ = 4, 10, 100, floats: GA results
    for rho, name in ((4, "ρ = 4"), (10, "ρ = 10"), (20, "ρ = 20"), (100, "ρ = 100"), (10000, W("floats", "Gleitkomma"))):
        run = sim.toy_ga(1, rho=rho, gens=40)
        best = max(run["last"], key=lambda l: sim.fitness(l, rho))
        med = _median(GA_BY_RHO[rho])
        fitn = sim.max_fit(rho) if rho <= 5 else None
        space = _log10_comb(rho * rho, 12)
        svg = site(best, 4, 4, S0, rho=rho, grid=rho <= 20, iso=True, label=False, cls="tb hl") + "".join(
            f'<circle class="disc" cx="{site_xy(*sim.centre(c, rho), 4, 4, S0)[0]:.1f}" cy="{site_xy(*sim.centre(c, rho), 4, 4, S0)[1]:.1f}" r="{120 * S0 / 1000:.1f}"/>' for c in best)
        if rho == 10000:
            gen = [f"({sim.centre(c, rho)[0]:.1f}, {sim.centre(c, rho)[1]:.1f})" for c in best[:6]] + ["…"]
            read = [(W("cells per axis", "Zellen je Achse"), W("— (0.1 m steps)", "— (0,1-m-Schritte)")), (W("cell size", "Zellgröße"), "0.1 m"),
                    (W("search space", "Suchraum"), f"≈ 10<sup>{space:.0f}</sup>"), (W("best after 40 gen.", "Bestwert nach 40 Gen."), f"{med:.3f}")]
        else:
            gen = [f"({c[0]}, {c[1]})" for c in best[:6]] + ["…"]
            read = [(W("cells per axis", "Zellen je Achse"), str(rho)), (W("cell size", "Zellgröße"), f"{1000 / rho:.0f} m")]
            read.append((W("turbines that fit (exact)", "passende Turbinen (exakt)"), str(fitn)) if fitn else (W("turbines that fit", "passende Turbinen"), W("more than 12", "mehr als 12")))
            read += [(W("search space", "Suchraum"), f"≈ 10<sup>{space:.0f}</sup>"), (W("best after 40 gen.", "Bestwert nach 40 Gen."), f"{med:.3f}")]
        m = {k: f"{_median(v):.3f}" for k, v in GA_BY_RHO.items()}
        e = {k: f"{_log10_comb(k * k, 12):.0f}" for k in GA_BY_RHO}
        grow = f"{_log10_comb(100 ** 2, 12) - _log10_comb(400, 12):.0f}"
        md = {k: _median(v) for k, v in GA_BY_RHO.items()}
        assert abs(md[100] - md[20]) < .01 and abs(md[10000] - md[20]) < .01 and md[10] < md[20] and md[4] < md[20], md   # the notes say so
        notes = {4: W(f"Coarser, yet denser: at 250 m per cell even neighbours keep the distance, so 16 turbines fit. But each turbine must sit on one of only 16 spots — the best reachable layout is fixed, and runs reach {m[4]}.",
                      f"Gröber, und doch dichter: Bei 250 m je Zelle halten selbst Nachbarn den Abstand, also passen 16 Turbinen. Aber jede Turbine muss auf einem von nur 16 Plätzen stehen — das beste erreichbare Layout liegt fest, die Läufe erreichen {m[4]}."),
                 10: W(f"100 m cells: two turbines in a row must now keep 3 cells = 300 m instead of 240 m. The grid wastes space near the good corner — runs reach only {m[10]}.",
                       f"100-m-Zellen: Zwei Turbinen in einer Reihe müssen jetzt 3 Zellen = 300 m statt 240 m Abstand halten. Das Raster verschenkt Platz an der guten Ecke — die Läufe erreichen nur {m[10]}."),
                 20: W(f"50 m cells, the grid used throughout this article: 400 cells, about 10<sup>{e[20]}</sup> layouts — far too many to list, few enough to search. Runs reach {m[20]}.",
                       f"50-m-Zellen, das Raster in diesem ganzen Artikel: 400 Zellen, rund 10<sup>{e[20]}</sup> Layouts — viel zu viele zum Auflisten, wenige genug zum Suchen. Die Läufe erreichen {m[20]}."),
                 100: W(f"Five times finer per axis: the space grows by {grow} orders of magnitude — and the runs reach {m[100]}, about what 50 m cells reach.",
                        f"Fünfmal feiner je Achse: Der Suchraum wächst um {grow} Größenordnungen — und die Läufe erreichen {m[100]}, etwa so viel wie mit 50-m-Zellen."),
                 10000: W(f"Floating-point positions look most precise. Here they reach {m[10000]} — about the same again, in a space of about 10<sup>{e[10000]}</sup> layouts. In the real wind farm of my thesis, the same held, and grid genes were also much faster (chapter 03).",
                          f"Gleitkomma-Positionen wirken am genauesten. Hier erreichen sie {m[10000]} — wieder etwa dasselbe, in einem Raum von rund 10<sup>{e[10000]}</sup> Layouts. Im echten Windpark meiner Arbeit galt dasselbe, und Rastergene waren zudem viel schneller (Kapitel 03).")}
        presets.append(dict(label=name, svg=svg, gen=gen, read=read, note=notes[rho]))
    order = [0, 2, 1, 3, 4, 5, 6]            # ρ=5 (thesis), ρ=4, ρ=6, ρ=10, ρ=20, ρ=100, floats
    presets = [presets[k] for k in order]
    buttons = "".join(f'<button type="button" aria-pressed="{"true" if k == 0 else "false"}">{esc(p["label"])}</button>' for k, p in enumerate(presets))
    inner = (f'<div class="d1-presets mono" role="group"><span class="k">{W("CELLS PER AXIS:", "ZELLEN JE ACHSE:")}</span>{buttons}</div>'
             f'<div class="enc"><pre class="enc-gen mono" aria-label="{W("genotype", "Genotyp")}"></pre>'
             f'<svg class="dia enc-site" viewBox="0 0 176 176" role="img" aria-label="{W("the site with the decoded turbines", "das Gelände mit den decodierten Turbinen")}"></svg>'
             f'<dl class="enc-read mono"></dl></div><p class="enc-note"></p>')
    return demo("ea4", {"presets": presets}, inner, T(
        "<b>Genotype → phenotype.</b> Left the genes, middle what they mean on the 1 km site (dashed circles: half the minimum distance, so overlapping circles are too close), right what it costs and what a short run reached (median of 5 runs, 40 generations). Finer is not denser, and past a point more precise is not better. The thesis example after [Net17] §4.2, Fig. 15a; counts are “before the spacing rule”.",
        "<b>Genotyp → Phänotyp.</b> Links die Gene, in der Mitte ihre Bedeutung auf dem 1-km-Gelände (gestrichelte Kreise: halber Mindestabstand, sich überlappende Kreise stehen also zu nah), rechts, was es kostet und was ein kurzer Lauf erreichte (Median aus 5 Läufen, 40 Generationen). Feiner ist nicht dichter, und ab einem Punkt ist genauer nicht besser. Das Beispiel der Arbeit nach [Net17] §4.2, Abb. 15a; Anzahlen „vor der Abstandsregel“."), lang)


# =====================================================================
# F5  Same loop, different chromosomes (SE tools)
# =====================================================================
def fig_chromosomes(lang):
    L = lambda x: x[lang]
    cols = [
        ("EvoSuite", r("FA13"), T("a whole test suite", "eine ganze Test-Suite"),
         "test 1:\n  Stack s = new Stack();\n  s.push(5);\ntest 2:\n  Stack s = new Stack();\n  s.pop();",
         T("minimise: uncovered methods + branch distance. For <code>x &gt;= 10</code> with x = 5 the distance is 10 − 5 + k", "minimieren: nicht erreichte Methoden + Zweig-Distanz. Für <code>x &gt;= 10</code> mit x = 5 ist die Distanz 10 − 5 + k")),
        ("GenProg", r("LeG12"), T("a patch: a list of edits", "ein Patch: eine Liste von Änderungen"),
         "Delete(12)\nInsert(40, 7)\nReplace(81, 44)",
         T("maximise: tests passed. Caution: a patch that deletes the failing feature can pass too [Qi15]", "maximieren: bestandene Tests. Vorsicht: Auch ein Patch, der die fehlerhafte Funktion löscht, kann bestehen [Qi15]")),
        ("PerOpteryx", r("PerOp"), T("an architecture: components → servers", "eine Architektur: Komponenten → Server"),
         "Frontend → server 1\nOrders   → server 1\nBilling  → server 2\nserver 2: 4 cores",
         T("several objectives at once: response time, cost, reliability (NSGA-II)", "mehrere Ziele zugleich: Antwortzeit, Kosten, Zuverlässigkeit (NSGA-II)")),
    ]
    cells = "".join(f'<div class="chr"><p class="mono chr-h">{n} {c}</p><p class="chr-k mono">{L(T("chromosome", "Chromosom"))}: {L(k)}</p>'
                    f'<pre class="mono">{esc(code)}</pre><p class="chr-f">{L(f).replace("[Qi15]", r("Qi15"))}</p></div>' for n, c, k, code, f in cols)
    return (f'<figure class="media art-fig"><div class="chr-grid">{cells}</div><figcaption class="mono">'
            + L(T("<b>Same loop, different chromosomes.</b> In software engineering, choosing what a candidate <i>is</i> — and how to score it — is the creative part; the loop is the same. Edit indices of the GenProg column are illustrative.",
                  "<b>Dieselbe Schleife, andere Chromosomen.</b> In der Softwaretechnik ist die Wahl, was ein Kandidat <i>ist</i> — und wie man ihn bewertet —, der kreative Teil; die Schleife bleibt dieselbe. Die Indizes der GenProg-Spalte sind illustrativ."))
            + '</figcaption></figure>')


# =====================================================================
# F6  Fitness is a simulation: drag a turbine, watch the wakes
# =====================================================================
def demo_wake(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    best = max(TOY["last"], key=lambda l: sim.fitness(l, RHO))
    pts = [list(sim.centre(c, RHO)) for c in best]
    ws = sim.wake_scores(pts)
    data = {"pts": pts, "k": sim.K_WAKE, "ct": sim.CT, "R": sim.R_ROTOR, "dmin": sim.D_MIN, "cell": CELL,
            "words": {"total": W("fitness", "Fitness"), "nowake": W("without wakes", "ohne Nachlauf"), "too": W("too close", "zu nah")}}
    svg = (f'<svg class="dia wake" viewBox="0 0 340 300" role="img" aria-label="{W("A wind-farm site seen from above; turbines cast wake cones to the east", "Ein Windpark-Gelände von oben; Turbinen werfen Nachlaufkegel nach Osten")}">'
           f'<g transform="translate(20 20)">{site([], 0, 0, 260, iso=True)}<g class="cones"></g><g class="tbs"></g></g>'
           + _arrow(2, 150, 16, 150, "ln hl") + f'<text class="s" x="2" y="140">{W("wind", "Wind")}</text>'
           '</svg>')
    inner = (f'<div class="wk">{svg}<div class="wk-side mono"><p class="wk-total"></p><p class="wk-nowake"></p>'
             f'<p class="wk-hint">{W("Drag a turbine (or tap one, then tap its new place).", "Ziehen Sie eine Turbine (oder tippen Sie eine an und dann ihren neuen Platz).")}</p>'
             f'<button type="button" class="wk-reset">{W("reset", "zurücksetzen")}</button></div></div>')
    keep = round((1 - sim.deficit(240)) ** 3 * 100)
    return demo("ea6", data, inner, T(
        f"<b>Fitness is a simulation.</b> The layout is the best of the run in chapter 02 (scored without wakes). With a west wind, every turbine slows the air behind it; a turbine 240 m downstream keeps only {keep} % of its score. Move one turbine and <i>other</i> turbines’ scores change — the genes are not independent. Jensen’s wake model {r('Jen83')} (top-hat, k = 0.5 / ln(z/z₀), C_T = 0.8), as in [Net17] §3.3, Fig. 7; the score is “better toward the north-east”, the mean over turbines is our choice.",
        f"<b>Fitness ist eine Simulation.</b> Das Layout ist das beste aus dem Lauf in Kapitel 02 (ohne Nachlauf bewertet). Bei Westwind bremst jede Turbine die Luft hinter sich; eine Turbine 240 m dahinter behält nur {keep} % ihres Werts. Verschieben Sie eine Turbine, und die Werte <i>anderer</i> Turbinen ändern sich — die Gene sind nicht unabhängig. Nachlaufmodell nach Jensen {r('Jen83')} (Top-Hat, k = 0,5 / ln(z/z₀), C_T = 0,8), wie in [Net17] §3.3, Abb. 7; die Bewertung ist „besser nach Nordosten“, der Mittelwert über die Turbinen ist unsere Wahl."), lang)


# =====================================================================
# F7  Selection: wheel, tournament, temperature
# =====================================================================
def demo_selection(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    fs = sorted((sim.fitness(l, RHO) for l in TOY["first"]), reverse=True)
    modes = [("wheel", W("roulette wheel", "Glücksrad")), ("tour", W("tournament", "Turnier")), ("temp", W("temperature", "Temperatur"))]
    buttons = "".join(f'<button type="button" data-m="{k}" aria-pressed="{"true" if i == 0 else "false"}">{n}</button>' for i, (k, n) in enumerate(modes))
    inner = (f'<div class="d1-presets mono" role="group"><span class="k">{W("SELECTION:", "SELEKTION:")}</span>{buttons}'
             f'<label class="sl-k"><span>k</span> <input type="range" min="2" max="8" value="3"> <output>3</output></label>'
             f'<label class="sl-t"><span>T</span> <input type="range" min="0" max="40" value="20"> <output></output></label>'
             f'<label class="sl-off"><input type="checkbox"> {W("+1000 to every score", "+1000 auf jede Bewertung")}</label></div>'
             f'<div class="sl-wrap"><svg class="dia wheel" viewBox="0 0 220 220" role="img" aria-label="{W("A roulette wheel with one slice per layout", "Ein Glücksrad mit einem Stück je Layout")}"></svg>'
             f'<div class="sel-side"><div class="rank sel-rank" role="list"></div></div></div>'
             f'<div class="sel-foot mono"><button type="button" class="draw">{W("draw 6 parents", "6 Eltern ziehen")}</button><span class="expect"></span></div>')
    assert .40 <= min(fs) and max(fs) <= .60
    data = {"f": [_n(v, 4) for v in fs], "lo": .40, "hi": .60, "words": {"exp": W("expected copies of the best among 6 parents", "erwartete Kopien des Besten unter 6 Eltern"),
                                                    "drawn": W("drawn", "gezogen")}}
    return demo("ea7", data, inner, T(
        f"<b>Where selection pressure comes from.</b> The 20 random layouts of generation 0, best first. Roulette gives each a slice proportional to its fitness [Net17] §4.5 — add 1000 to every score and the wheel turns fair, all differences gone. A tournament (best of k) only compares, so the offset changes nothing; k is the pressure dial {r('GD91')}. Temperature works like in <a href=\"research-ai4se.html#tokens\">part 2</a>: a softmax over the scores, sharp when cold, flat when hot.",
        f"<b>Woher der Selektionsdruck kommt.</b> Die 20 zufälligen Layouts der Generation 0, das beste zuerst. Das Glücksrad gibt jedem ein Stück proportional zu seiner Fitness [Net17] §4.5 — addieren Sie 1000 auf jede Bewertung, und das Rad wird fair, alle Unterschiede sind weg. Ein Turnier (Bester aus k) vergleicht nur, der Versatz ändert also nichts; k ist der Regler für den Druck {r('GD91')}. Die Temperatur wirkt wie in <a href=\"research-ai4se.html#tokens\">Teil 2</a>: ein Softmax über die Bewertungen, scharf wenn kalt, flach wenn heiß."), lang)


# =====================================================================
# F8  Crossover: ordered genes vs unordered layouts (One-Step)
# =====================================================================
def _find_onestep():
    """A real crossover from the toy run where the child beats both parents and conflicts had to be resolved."""
    run = sim.toy_ga(sim.MAIN_SEED, keep=set(range(60)))
    for g in sorted(run["books"]):
        b = run["books"][g]
        for k, (i, j) in enumerate(b["pairs"]):
            A, B = b["pop"][i], b["pop"][j]
            child, info = sim.one_step(A, B, RHO)
            fa, fb, fc = sim.fitness(A, RHO), sim.fitness(B, RHO), sim.fitness(child, RHO)
            if fc > max(fa, fb) + .005 and len(info["dropped"]) <= 9 and A != B:
                return g, A, B, child, info, (fa, fb, fc)
    raise AssertionError("no instructive One-Step example")


ONESTEP = _find_onestep()


def demo_crossover(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    g, A, B, child, info, (fa, fb, fc) = ONESTEP
    S0 = 150
    tri = lambda c, cls, up: (lambda x, y: f'<path class="{cls}" d="M{x - 4.5:.1f} {y + (3 if up else -3):.1f}L{x + 4.5:.1f} {y + (3 if up else -3):.1f}L{x:.1f} {y + (-5 if up else 5):.1f}Z"/>')(*site_xy(*sim.centre(c, RHO), 0, 0, S0))

    def panel(cells_a, cells_b, rings=(), ranks=None, keep=None):
        out = site([], 0, 0, S0, iso=True, label=False)
        for c in cells_a:
            out += tri(c, "ta" + ("" if keep is None or c in keep else " off"), False)
        for c in cells_b:
            out += tri(c, "tb2" + ("" if keep is None or c in keep else " off"), True)
        for c in rings:
            x, y = site_xy(*sim.centre(c, RHO), 0, 0, S0)
            out += f'<circle class="conf" cx="{x:.1f}" cy="{y:.1f}" r="8"/>'
        if ranks:
            for k, c in enumerate(ranks):
                x, y = site_xy(*sim.centre(c, RHO), 0, 0, S0)
                out += f'<text class="s rk{"" if k < 12 else " off"}" x="{x + 5:.1f}" y="{y - 4:.1f}">{k + 1}</text>'
        return out
    kept_b = [c for c in B if c not in info["dropped"]]
    states = [
        (panel(A, []) + f'<g transform="translate({S0 + 20} 0)">{panel([], B)}</g>', W(f"Parent A (▼, fitness {fa:.3f}) and parent B (▲, {fb:.3f}): two layouts of 12 turbines. Which turbine is “gene 3”? There is no order — a cut in the middle means nothing.", f"Elternteil A (▼, Fitness {fa:.3f}) und B (▲, {fb:.3f}): zwei Layouts aus 12 Turbinen. Welche Turbine ist „Gen 3“? Es gibt keine Reihenfolge — ein Schnitt in der Mitte bedeutet nichts.")),
        (panel(A, B, rings=info["dropped"]), W(f"Merge both layouts: 24 turbines. {len(info['dropped'])} of B’s turbines are closer than 240 m to one of A’s (circled).", f"Beide Layouts zusammenlegen: 24 Turbinen. {len(info['dropped'])} Turbinen von B stehen näher als 240 m an einer von A (eingekreist).")),
        (panel(A, kept_b), W("Resolve each conflict by dropping B’s turbine. What remains is a valid layout — with too many turbines.", "Jeden Konflikt lösen, indem B’s Turbine wegfällt. Was bleibt, ist ein gültiges Layout — mit zu vielen Turbinen.")),
        (panel(A, kept_b, ranks=info["ranked"], keep=set(child)), W(f"Rank every turbine by its own score and keep the best 12. The child: fitness {fc:.3f} — better than both parents, without a single new position.", f"Jede Turbine nach ihrem eigenen Wert sortieren und die besten 12 behalten. Das Kind: Fitness {fc:.3f} — besser als beide Eltern, ohne eine einzige neue Position.")),
    ]
    assert fc > fa and fc > fb
    data = {"states": [{"svg": s, "say": t} for s, t in states],
            "a": [.20, .35, .35, .60, .80, .70, .40], "b": [.90, .85, .50, .30, .30, .15, .10],
            "words": {"step": W("step", "Schritt"), "of": W("of", "von"), "play": W("play", "abspielen"), "pause": W("pause", "anhalten")}}
    ops = [("one", W("one-point", "Ein-Punkt")), ("two", W("two-point", "Zwei-Punkt")), ("uni", W("uniform", "gleichmäßig"))]
    obtn = "".join(f'<button type="button" data-o="{k}" aria-pressed="{"true" if i == 0 else "false"}">{n}</button>' for i, (k, n) in enumerate(ops))
    strip = (f'<div class="xo-a"><div class="d1-presets mono" role="group"><span class="k">{W("ORDERED GENES:", "GEORDNETE GENE:")}</span>{obtn}<button type="button" class="retoss">{W("new cuts", "neue Schnitte")}</button></div>'
             f'<svg class="dia xo-strip" viewBox="0 0 360 150" role="img" aria-label="{W("Two parent strips of seven numbers and the two children", "Zwei Eltern-Streifen aus sieben Zahlen und die beiden Kinder")}"></svg>'
             f'<p class="xo-say">{W("A schedule of 7 numbers — e.g. how much of the torque the engine delivers, second by second. The order means something, so a cut makes sense: children inherit whole stretches. (Illustrative values.)", "Ein Zeitplan aus 7 Zahlen — etwa welchen Anteil des Drehmoments der Motor liefert, Sekunde für Sekunde. Die Reihenfolge bedeutet etwas, ein Schnitt ist also sinnvoll: Kinder erben ganze Abschnitte. (Illustrative Werte.)")}</p></div>')
    one = (f'<div class="xo-b"><p class="k mono xo-k">{W("UNORDERED LAYOUTS: ONE-STEP CROSSOVER", "UNGEORDNETE LAYOUTS: ONE-STEP-CROSSOVER")}</p>'
           f'<svg class="dia os" viewBox="0 0 320 156" role="img" aria-label="{W("Two parent layouts merged into one child", "Zwei Eltern-Layouts werden zu einem Kind verschmolzen")}"><g class="os-g" transform="translate(4 3)"></g></svg>'
           f'<p class="os-say" aria-live="polite"></p>{controls(lang)}</div>')
    inner = f'<div class="xo">{strip}{one}</div>'
    return demo("ea8", data, inner, T(
        f"<b>How to recombine depends on the encoding.</b> Left: the textbook operators on ordered genes, after [Net17] Fig. 16 and the engine schedules of [NWN+15] Fig. 4. Right: a real crossover from generation {g} of the toy run with the One-Step crossover of [Net17] Fig. 17. Its trick needs a <b>score per turbine</b>; if your evaluator returns only one number per candidate, use a generic operator.",
        f"<b>Wie man kreuzt, hängt von der Codierung ab.</b> Links die Lehrbuch-Operatoren auf geordneten Genen, nach [Net17] Abb. 16 und den Motor-Zeitplänen aus [NWN+15] Abb. 4. Rechts eine echte Kreuzung aus Generation {g} des Spielzeuglaufs mit dem One-Step-Crossover aus [Net17] Abb. 17. Sein Trick braucht einen <b>Wert je Turbine</b>; liefert Ihre Bewertung nur eine Zahl je Kandidat, nehmen Sie einen generischen Operator."), lang)


# =====================================================================
# F9  Mutation: three separate knobs
# =====================================================================
def demo_mutation(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    kids = BOOK["kids0"]
    data = {"kids": kids, "rho": RHO, "dmin": sim.D_MIN, "seed": 7,
            "words": {"mut": W("mutated", "mutiert"), "not": W("not chosen", "nicht gewählt"), "f": W("fitness", "Fitness")}}
    knobs = (f'<label><span>{W("share of children mutated", "Anteil mutierter Kinder")}</span><input class="kn-p" type="range" min="0" max="100" step="10" value="30"><output></output></label>'
             f'<label><span>{W("genes moved per child", "verschobene Gene je Kind")}</span><input class="kn-n" type="range" min="1" max="6" value="2"><output></output></label>'
             f'<label><span>{W("step size s", "Schrittweite s")}</span><input class="kn-s" type="range" min="0" max="100" step="5" value="30"><output></output></label>')
    inner = (f'<div class="kn mono">{knobs}<button type="button" class="mutate">{W("mutate", "mutieren")}</button></div>'
             f'<svg class="dia mut" viewBox="0 0 660 128" role="img" aria-label="{W("Six children of one generation, some mutated", "Sechs Kinder einer Generation, einige mutiert")}"></svg>')
    return demo("ea9", data, inner, T(
        "<b>Three knobs, not one.</b> The six children of the generation shown above, before mutation. <i>Share</i>: how many children are touched at all — mutation can also spoil a good one. <i>Genes</i>: how many turbines move; the badly placed ones (low on the dotted iso-lines) are picked more often, as in [Net17] Eq. 30. <i>Step size</i>: s = 1 jumps anywhere, s = 0.1 nudges — new = old · (1 − s) + random · s, snapped to the grid, after [Net17] Eq. 31. In my thesis s is called the “mutation rate”; textbooks use that word for the share of genes.",
        "<b>Drei Regler, nicht einer.</b> Die sechs Kinder der Generation von oben, vor der Mutation. <i>Anteil</i>: wie viele Kinder überhaupt verändert werden — Mutation kann auch ein gutes verderben. <i>Gene</i>: wie viele Turbinen sich bewegen; schlecht platzierte (tief an den gepunkteten Linien) werden öfter gewählt, wie in [Net17] Gl. 30. <i>Schrittweite</i>: s = 1 springt irgendwohin, s = 0,1 schubst — neu = alt · (1 − s) + Zufall · s, aufs Raster gerundet, nach [Net17] Gl. 31. In meiner Arbeit heißt s „Mutationsrate“; Lehrbücher nennen so den Anteil der Gene."), lang)


# =====================================================================
# F10  Watching a population converge (two hills)
# =====================================================================
HILLS = sim.run_hills()
HILL_LEVELS = [.1, .2, .3, .4, .5, .55, .7, .8, .9]
HILL_PATHS = sim.contours(sim.hills, HILL_LEVELS, n=150)
STARTER_RES = sim.starter_results()
STARTER_DECOY = [s for s, f, _ in STARTER_RES if f < .9]


def _featured(name):
    """The seed shown for a preset: the first one that tells the preset's story."""
    runs = HILLS[name]["runs"]
    want = {"balanced": lambda r: sim.on_high(r[-1]), "pressure": lambda r: not sim.on_high(r[-1]),
            "closed": lambda r: not sim.on_high(r[-1]), "random": lambda r: True}[name]
    return next(k for k, r in enumerate(runs) if want(r))


def demo_converge(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    S0 = 260
    paths = []
    for lv, lines in HILL_PATHS:
        d = "".join("M" + "L".join(f"{x * S0:.1f} {(1 - y) * S0:.1f}" for x, y in line) for line in lines if len(line) > 2)
        paths.append(f'<path class="iso{" iso-i" if lv in (.5, .9) else ""}" d="{d}"/>')
    labels = (f'<text class="s" x="{sim.LOW[0] * S0 - 50:.0f}" y="{(1 - sim.LOW[1]) * S0 - 104:.0f}">{W("broad low hill (0.6)", "breiter niedriger Hügel (0,6)")}</text>'
              f'<text class="s" x="{S0 - 4}" y="{(1 - sim.HIGH[1]) * S0 - 38:.0f}" text-anchor="end">{W("narrow high hill (1.0)", "schmaler hoher Hügel (1,0)")}</text>')
    tops = {k: sum(r_[-1] and sim.hills(*r_[-1][0]) >= .99 for r_ in HILLS[k]["runs"]) for k in sim.PRESETS}
    assert tops["random"] < tops["balanced"] and HILLS["random"]["high"] == 10      # the texts say so
    presets, names = {}, {"balanced": W("balanced", "ausgewogen"), "pressure": W("high pressure, no mutation", "hoher Druck, keine Mutation"),
                          "closed": W("no newcomers", "keine Neulinge"), "random": W("random search", "Zufallssuche")}
    for name, cfg in sim.PRESETS.items():
        runs, k = HILLS[name]["runs"], _featured(name)
        run = runs[k]
        pts = [[int(round(v * 999)) for p in gen for v in p] for gen in run]
        f_gen = [[sim.hills(*p) for p in gen] for gen in run]
        presets[name] = {
            "pts": pts, "seed": k + 1, "high": HILLS[name]["high"],
            "best": [_n(max(f)) for f in f_gen], "mean": [_n(sum(f) / len(f)) for f in f_gen], "worst": [_n(min(f)) for f in f_gen],
            "div": [_n(sim.diversity(g)) for g in run],
            "seeds": [[_n(max(sim.hills(*p) for p in g)) for g in r] for r in runs],
            "final": [_n(sim.hills(*r[-1][0])) for r in runs], "cfg": cfg}
    say = {"balanced": W("Tournament of 3, 30 % of children mutated, 2 elite, 2 random newcomers per generation — the starter at the end of this article.",
                         "Turnier aus 3, 30 % der Kinder mutiert, 2 Elite, 2 zufällige Neulinge je Generation — der Starter am Ende dieses Artikels."),
           "pressure": W("Tournament of 8, no mutation, no newcomers: the population collapses onto whatever is best early — often the wrong hill. The best curve looks healthy; the dots and the diversity tell the truth.",
                         "Turnier aus 8, keine Mutation, keine Neulinge: Die Population fällt auf das zusammen, was früh am besten ist — oft der falsche Hügel. Die Bestkurve sieht gesund aus; die Punkte und die Vielfalt sagen die Wahrheit."),
           "closed": W("Like balanced, but without newcomers: mutation alone rarely carries a candidate across the valley.",
                       "Wie ausgewogen, aber ohne Neulinge: Mutation allein trägt selten einen Kandidaten über das Tal."),
           "random": W("The baseline: 18 fresh random candidates per generation, only the 2 best kept. It finds the right hill — but rarely its top: nothing refines what it has found.",
                       "Die Vergleichslinie: 18 neue Zufallskandidaten je Generation, nur die 2 besten bleiben. Sie findet den richtigen Hügel — aber selten seine Spitze: Nichts verfeinert, was sie gefunden hat.")}
    for name in presets:
        p = presets[name]
        tops = sum(f >= .99 for f in p["final"])
        p["say"] = say[name]
        p["count"] = W(f"10 seeds: {p['high']} ended on the high hill, {tops} of them at its top (≥ 0.99). Shown: seed {p['seed']}.",
                       f"10 Seeds: {p['high']} endeten auf dem hohen Hügel, {tops} davon auf seiner Spitze (≥ 0,99). Gezeigt: Seed {p['seed']}.")
    buttons = "".join(f'<button type="button" data-p="{k}" aria-pressed="{"true" if k == "balanced" else "false"}">{n}</button>' for k, n in names.items())
    land = (f'<svg class="dia land" viewBox="-4 -4 {S0 + 8} {S0 + 8}" role="img" aria-label="{W("Contour lines of two hills with the population as dots", "Höhenlinien zweier Hügel mit der Population als Punkten")}">'
            f'<rect class="box" x="0" y="0" width="{S0}" height="{S0}"/>{"".join(paths)}{labels}<g class="dots"></g></svg>')
    charts = (f'<svg class="dia conv" viewBox="0 0 330 250" role="img" aria-label="{W("Best, mean and worst fitness and the diversity per generation", "Beste, mittlere und schlechteste Fitness und die Vielfalt je Generation")}">'
              f'<g class="ch1" transform="translate(34 10)"></g><g class="ch2" transform="translate(34 160)"></g></svg>')
    inner = (f'<div class="d1-presets mono" role="group"><span class="k">{W("SETTINGS:", "EINSTELLUNGEN:")}</span>{buttons}'
             f'<label class="cv-seeds"><input type="checkbox"> {W("all 10 seeds", "alle 10 Seeds")}</label></div>'
             f'<div class="cv">{land}<div class="cv-side">{charts}<p class="cv-say"></p><p class="cv-count mono"></p></div></div>' + controls(lang))
    data = {"presets": presets, "words": {"best": W("best", "beste"), "mean": W("mean", "Mittel"), "worst": W("worst", "schlechteste"),
                                          "gap": W("fitness gap", "Fitnesslücke"), "div": W("diversity", "Vielfalt"), "gen": W("generation", "Generation"),
                                          "evals": W("evaluations", "Bewertungen"), "play": W("play", "abspielen"), "pause": W("pause", "anhalten"), "of": W("of", "von")}}
    return demo("ea10", data, inner, T(
        "<b>Watching a population converge.</b> 20 candidates of two numbers on a landscape with a broad low hill and a narrow high one (illustrative). Top chart: best, mean and worst fitness; the band between best and worst is the <i>fitness gap</i> of [Net17] Fig. 18. Bottom: diversity (mean distance to the centre of the population) — when it hits zero, the run has converged, right or wrong. Seeded runs; counts over 10 seeds each.",
        "<b>Einer Population beim Konvergieren zusehen.</b> 20 Kandidaten aus zwei Zahlen auf einer Landschaft mit einem breiten niedrigen und einem schmalen hohen Hügel (illustrativ). Oberes Diagramm: beste, mittlere und schlechteste Fitness; das Band zwischen bester und schlechtester ist die <i>Fitnesslücke</i> aus [Net17] Abb. 18. Unten: Vielfalt (mittlerer Abstand zum Zentrum der Population) — erreicht sie null, ist der Lauf konvergiert, richtig oder falsch. Reproduzierbare Läufe; Anzahlen über je 10 Seeds."), lang)


# =====================================================================
# F11  The family
# =====================================================================
def fig_family(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    head = (f'<tr><th></th><th>{W("bits, integers", "Bits, ganze Zahlen")}</th><th>{W("real numbers", "reelle Zahlen")}</th>'
            f'<th>{W("programs, trees", "Programme, Bäume")}</th><th>{W("networks", "Netze")}</th></tr>')
    se = lambda t: f'<span class="faint">{t}</span>'
    rows = (f'<tr><td>{W("one best solution", "eine beste Lösung")}</td>'
            f'<td><b>GA</b> {r("Hol75")}</td><td><b>ES</b> {r("BS02")}, <b>CMA-ES</b> {r("Han16")}, <b>DE</b> {r("SP97")}</td>'
            f'<td><b>GP</b> · {se("GenProg, EvoSuite")}</td><td><b>NEAT</b> {r("SM02")}</td></tr>'
            f'<tr><td>{W("a Pareto front", "eine Pareto-Front")}</td><td colspan="4" class="band"><b>NSGA-II</b> {r("Deb02")} — {W("works with any of the encodings above", "funktioniert mit jeder Codierung oben")} · {se("Sapienz, PerOpteryx")}</td></tr>'
            f'<tr><td>{W("a diverse archive", "ein vielfältiges Archiv")}</td><td colspan="4" class="band"><b>MAP-Elites</b> {r("MC15")}, {W("novelty search", "Novelty Search")} {r("LS11")} — {W("likewise", "ebenso")} · {se("ELM, AlphaEvolve")}</td></tr>')
    return (f'<figure class="media art-fig"><div class="tbl-wrap"><table class="tbl mono ea-fam"><tr><th></th><th colspan="4" class="axis">{W("what a candidate is → decides the variation operators", "was ein Kandidat ist → entscheidet die Variationsoperatoren")}</th></tr>{head}{rows}</table></div>'
            f'<figcaption class="mono">{W("<b>One loop, many dialects.</b> Columns: what a candidate is, which decides how to vary it. Rows: what you want back, which decides what survives. NSGA-II and MAP-Elites change only selection and archive, so they span every encoding. Grey: the software-engineering tools from this article.", "<b>Eine Schleife, viele Dialekte.</b> Spalten: was ein Kandidat ist — das entscheidet, wie man ihn variiert. Zeilen: was man zurückhaben will — das entscheidet, was überlebt. NSGA-II und MAP-Elites ändern nur Selektion und Archiv, sie überspannen also jede Codierung. Grau: die Softwaretechnik-Werkzeuge aus diesem Artikel.")}</figcaption></figure>')


# =====================================================================
# F12  PHEV: a schedule as chromosome; the weights are the specification  [NWN+15]
# =====================================================================
PHEV_T2 = [  # (w_f, w_sl, w_sd, w_ud, w_ut) → NEDC fuel [g], end SoC   (NWN+15 Table 2, p. 206)
    ((1.0, 0, 0, 0, 0), 384.806, .6260),
    ((.5, 0, .5, 0, 0), 380.123, .6263),
    ((0, 1.0, 0, 0, 0), 424.075, .7000),
]
PHEV_T1 = {"ICE only": 428.101, "RDP": 387.081, "ADP": 388.726, "A-ECMS": 390.239, "T-ECMS": 391.641}   # NEDC, Table 1
PHEV_T3 = [((1.0, 0, 0, 0, 0), 384.845, 116.64), ((0, 0, 0, 1.0, 0), 389.325, 51.13)]                   # NEDC, Table 3
PHEV_T4 = [(.1, 388.471, 35.19), (.2, 386.700, 46.06), (.3, 386.155, 50.45), (.4, 386.030, 55.59), (.5, 385.980, 63.01),
           (.6, 385.753, 67.13), (.7, 385.520, 76.05), (.8, 385.385, 84.87), (.9, 385.289, 93.57), (1.0, 385.400, 109.26)]   # NEDC, Table 4
assert round((1 - PHEV_T2[1][1] / min(PHEV_T1[k] for k in ("RDP", "ADP", "A-ECMS", "T-ECMS"))) * 100, 1) == 1.8


def demo_phev(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    n, x0, cw = 21, 30, 13.6
    rnd = sim.Rng(5)
    vals = [round(.5 + .4 * math.sin(k / 3.2) * (.6 + .4 * rnd.random()), 2) for k in range(n + 4)]

    def strip(shift, y=40, hl_first=False, new_last=False):
        out = []
        for k in range(n):
            v = vals[k + shift]
            cls = "cell" + (" first" if hl_first and k == 0 else "") + (" fresh" if new_last and k == n - 1 else "")
            out.append(f'<rect class="{cls}" x="{x0 + k * cw:.1f}" y="{y}" width="{cw - 2:.1f}" height="34" rx="1"/>'
                       f'<rect class="lvl" x="{x0 + k * cw:.1f}" y="{y + 34 - 34 * v:.1f}" width="{cw - 2:.1f}" height="{34 * v:.1f}"/>')
        out.append(f'<text class="s" x="{x0}" y="{y + 50}">u(t)</text><text class="s" x="{x0 + (n - 1) * cw - 6:.0f}" y="{y + 50}" text-anchor="middle">u(t+20)</text>')
        return "".join(out)
    steps = [
        (strip(0), W("The chromosome is a schedule: the share of the torque the engine delivers (the rest comes from the electric motor), one gene per second for the next 20 seconds; each gene one of 101 levels 0 … 1.",
                     "Das Chromosom ist ein Zeitplan: der Anteil des Drehmoments, den der Verbrennungsmotor liefert (den Rest liefert der Elektromotor), ein Gen je Sekunde für die nächsten 20 Sekunden; jedes Gen eine von 101 Stufen 0 … 1.")),
        (strip(0, hl_first=True), W("The GA optimises the whole schedule — 50 candidates, 100 generations — but the car applies only the first gene.",
                                    "Der GA optimiert den ganzen Zeitplan — 50 Kandidaten, 100 Generationen —, aber das Auto wendet nur das erste Gen an.")),
        (strip(1, new_last=True), W("Next step: every candidate is shifted one gene to the left and a random gene is appended. The population is not thrown away — the search continues where it was (warm start).",
                                    "Nächster Schritt: Jeder Kandidat wird um ein Gen nach links geschoben, ein zufälliges Gen wird angehängt. Die Population wird nicht verworfen — die Suche macht dort weiter, wo sie war (Warmstart).")),
        (strip(1, hl_first=True), W("Optimise again, apply the first gene again — a receding horizon. A fixed budget of generations keeps the time per step fixed: the controller must answer in real time.",
                                    "Wieder optimieren, wieder das erste Gen anwenden — ein zurückweichender Horizont. Ein festes Budget an Generationen hält die Zeit je Schritt fest: Die Steuerung muss in Echtzeit antworten.")),
    ]
    weights = [
        (W("fuel only", "nur Kraftstoff"), PHEV_T2[0], W("Saving fuel is all that counts — yet this uses more fuel than the mixed weighting below. Optimising a 20-second window for fuel alone is short-sighted.", "Nur Kraftstoffsparen zählt — und doch braucht das mehr Kraftstoff als die gemischte Gewichtung unten. Ein 20-Sekunden-Fenster nur auf Kraftstoff zu optimieren, ist kurzsichtig.")),
        (W("fuel + battery near 60 %", "Kraftstoff + Batterie nahe 60 %"), PHEV_T2[1], W("Half fuel, half “keep the battery near its target”. The best result in the paper: 1.8 % less fuel than the best of the published reference controllers on this cycle.", "Halb Kraftstoff, halb „Batterie nahe am Ziel halten“. Das beste Ergebnis der Arbeit: 1,8 % weniger Kraftstoff als die beste der veröffentlichten Vergleichs-Steuerungen auf diesem Zyklus.")),
        (W("battery level only", "nur Batteriestand"), PHEV_T2[2], W("Only a full battery counts: the GA keeps the battery full and burns fuel — almost as much as driving with the engine alone (428.1 g).", "Nur eine volle Batterie zählt: Der GA hält die Batterie voll und verbrennt Kraftstoff — fast so viel wie mit dem Verbrennungsmotor allein (428,1 g).")),
    ]
    data = {"steps": [{"svg": s, "say": t} for s, t in steps],
            "w": [{"name": nme, "fuel": f"{fuel:.3f} g".replace(".", "," if lang == "de" else "."), "soc": f"{soc:.2f}".replace(".", "," if lang == "de" else "."), "say": say, "wv": list(wv)} for nme, (wv, fuel, soc), say in weights],
            "words": {"step": W("step", "Schritt"), "of": W("of", "von"), "play": W("play", "abspielen"), "pause": W("pause", "anhalten")}}
    wbtn = "".join(f'<button type="button" aria-pressed="{"true" if k == 0 else "false"}">{nme}</button>' for k, (nme, _, _) in enumerate(weights))
    inner = (f'<div class="ph"><div class="ph-a"><svg class="dia ph-strip" viewBox="0 0 330 100" role="img" aria-label="{W("A strip of 21 genes over the next 20 seconds", "Ein Streifen aus 21 Genen über die nächsten 20 Sekunden")}"><g class="ph-g"></g></svg>'
             f'<p class="ph-say" aria-live="polite"></p>{controls(lang)}</div>'
             f'<div class="ph-b"><div class="d1-presets mono" role="group"><span class="k">{W("FITNESS WEIGHTS:", "FITNESS-GEWICHTE:")}</span>{wbtn}</div>'
             f'<dl class="ph-read mono"><dt>{W("weights (fuel, battery level, battery near target, smooth, very smooth)", "Gewichte (Kraftstoff, Batteriestand, Batterie nahe Ziel, glatt, sehr glatt)")}</dt><dd class="ph-w"></dd>'
             f'<dt>{W("fuel on the NEDC test cycle", "Kraftstoff im NEFZ-Testzyklus")}</dt><dd class="ph-fuel"></dd><dt>{W("battery charge at the end", "Ladestand am Ende")}</dt><dd class="ph-soc"></dd></dl>'
             f'<p class="ph-wsay"></p></div></div>')
    return demo("ea12", data, inner, T(
        "<b>A genetic algorithm inside a car’s controller.</b> Left: the chromosome and the receding horizon (schedule values illustrative), after [NWN+15] §4 and Fig. 4. Right: the same GA with three fitness weightings — real results from [NWN+15] Table 2 (simulated parallel hybrid, NEDC cycle, GA configuration 50 / 0.75 / 0.1 / 100).",
        "<b>Ein genetischer Algorithmus in der Steuerung eines Autos.</b> Links das Chromosom und der zurückweichende Horizont (Werte des Zeitplans illustrativ), nach [NWN+15] §4 und Abb. 4. Rechts derselbe GA mit drei Fitness-Gewichtungen — echte Ergebnisse aus [NWN+15] Tabelle 2 (simulierter Parallelhybrid, NEFZ-Zyklus, GA-Konfiguration 50 / 0,75 / 0,1 / 100)."), lang)


def fig_phev_tradeoff(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    X0, X1, Y0, Y1 = 60, 600, 20, 190                    # plot area
    fx = lambda s: X0 + (s - 20) / (130 - 20) * (X1 - X0)
    fy = lambda f: Y1 - (f - 384) / (390 - 384) * (Y1 - Y0)
    out = [f'<path class="ln" d="M{X0} {Y0}V{Y1}H{X1}"/>']
    for f in range(384, 391, 2):
        out.append(f'<path class="gridl" d="M{X0} {fy(f):.1f}H{X1}"/><text class="s" x="{X0 - 6}" y="{fy(f) + 4:.1f}" text-anchor="end">{f}</text>')
    for s in (25, 50, 75, 100, 125):
        out.append(f'<text class="s" x="{fx(s):.1f}" y="{Y1 + 14}" text-anchor="middle">{s}</text>')
    out.append(f'<text class="s" x="{X1}" y="{Y1 + 28}" text-anchor="end">{W("jerkiness: Σ |change of the split| over the cycle", "Unruhe: Σ |Änderung der Aufteilung| über den Zyklus")}</text>'
               f'<text class="s" x="{X0 - 44}" y="{Y0 - 6}">{W("fuel [g]", "Kraftstoff [g]")}</text>')
    d = "M" + "L".join(f"{fx(s):.1f} {fy(f):.1f}" for _, f, s in PHEV_T4)
    out.append(f'<path class="ln hl" d="{d}"/>' + "".join(f'<circle class="dot" cx="{fx(s):.1f}" cy="{fy(f):.1f}" r="2.6"/>' for _, f, s in PHEV_T4))
    out.append(f'<text class="s a" x="{fx(35.19) + 6:.1f}" y="{fy(388.471) - 6:.1f}">{W("max change per step 0.1", "max. Änderung je Schritt 0,1")}</text>'
               f'<text class="s a" x="{fx(109.26):.1f}" y="{fy(385.400) - 8:.1f}" text-anchor="middle">1.0</text>')
    for (wv, f, s), lab in zip(PHEV_T3, (W("weight: fuel only", "Gewicht: nur Kraftstoff"), W("weight: smoothness only", "Gewicht: nur Glätte"))):
        x, y = fx(s), fy(f)
        out.append(f'<rect class="sq" x="{x - 3:.1f}" y="{y - 3:.1f}" width="6" height="6"/><text class="s" x="{x + (8 if s < 100 else -8):.1f}" y="{y + 4:.1f}" text-anchor="{"start" if s < 100 else "end"}">{lab}</text>')
    svg = f'<svg class="dia trade" viewBox="0 0 640 230" role="img" aria-label="{W("Fuel against jerkiness for different settings", "Kraftstoff gegen Unruhe für verschiedene Einstellungen")}">{"".join(out)}</svg>'
    return fig(svg, T("<b>A trade-off, not one answer.</b> Smooth driving costs fuel. Squares: two fitness weightings ([NWN+15] Table 3). Line: instead of weighting, restrict the search space — consecutive genes may differ by at most 0.1 … 1.0 ([NWN+15] Table 4). A weighted sum picks one point on such a curve; multi-objective algorithms like NSGA-II return the whole curve. NEDC cycle.",
                      "<b>Ein Zielkonflikt, nicht eine Antwort.</b> Ruhiges Fahren kostet Kraftstoff. Quadrate: zwei Fitness-Gewichtungen ([NWN+15] Tabelle 3). Linie: statt zu gewichten den Suchraum einschränken — aufeinanderfolgende Gene dürfen sich um höchstens 0,1 … 1,0 unterscheiden ([NWN+15] Tabelle 4). Eine gewichtete Summe wählt einen Punkt auf so einer Kurve; mehrkriterielle Algorithmen wie NSGA-II liefern die ganze Kurve. NEFZ-Zyklus."), lang)


# =====================================================================
# F13  Wind farm: runtimes of grid genes vs float genes  [Net17] §6.3–6.5
# =====================================================================
RUNTIMES = [("AEP", 48 * 60, 88732.62), ("NPV", 137 * 60, 73594.79), ("IRR", 49 * 60, 17768.83)]   # seconds: grid genes, float genes
assert [round(c / d, 2) for _, d, c in RUNTIMES] == [30.81, 8.95, 6.04]


def fig_runtimes(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    X0, X1 = 170, 430
    lx = lambda s: X0 + (math.log10(s) - 3) / (5 - 3) * (X1 - X0)       # 10^3 … 10^5 s
    out = []
    for e, lab in ((3, "17 min"), (4, "2.8 h"), (5, "28 h")):
        x = X0 + (e - 3) / 2 * (X1 - X0)
        out.append(f'<path class="gridl" d="M{x:.1f} 14V176"/><text class="s" x="{x:.1f}" y="190" text-anchor="middle">10{"³⁴⁵"[e - 3]} s · {lab if lang == "en" else lab.replace(".", ",")}</text>')
    fmt = lambda s: (f"{s / 60:.0f} min" if s < 3 * 3600 else f"{s / 3600:.1f} h")
    for k, (obj, d, c) in enumerate(RUNTIMES):
        y = 22 + k * 52
        names = {"AEP": W("energy per year", "Jahresenergie"), "NPV": W("net present value", "Kapitalwert"), "IRR": W("internal rate of return", "interner Zinsfuß")}
        out.append(f'<text class="t" x="0" y="{y + 12}">{obj}</text><text class="s" x="0" y="{y + 26}">{names[obj]}</text>')
        out.append(f'<rect class="bar-g" x="{X0}" y="{y}" width="{lx(d) - X0:.1f}" height="12"/><text class="s" x="{lx(d) + 6:.1f}" y="{y + 10}">{W("grid genes", "Rastergene")} · {fmt(d)}</text>')
        out.append(f'<rect class="bar-c" x="{X0}" y="{y + 16}" width="{lx(c) - X0:.1f}" height="12"/>'
                   f'<text class="s" x="{lx(c) + 6:.1f}" y="{y + 26}">{W("float genes", "Gleitkomma-Gene")} · {fmt(c)} · <tspan class="a">×{c / d:.1f}</tspan></text>')
    svg = f'<svg class="dia rt" viewBox="0 0 600 200" role="img" aria-label="{W("Runtimes of the wind-farm optimisation with grid genes and with float genes", "Laufzeiten der Windpark-Optimierung mit Rastergenen und mit Gleitkomma-Genen")}">{"".join(out)}</svg>'
    return fig(svg, T("<b>Horns Rev 1, 80 turbines, three objectives: grid genes finished in 48 to 137 minutes, float genes needed 5 to 24 hours</b> (log scale). Fair warning: each encoding ran once, with its own recommended setup — 100 candidates for grid genes, 1000 for float genes — so the factor is not the encoding alone. From [Net17] §6.3–6.5; most of the time went into crossover.",
                      "<b>Horns Rev 1, 80 Turbinen, drei Ziele: Rastergene waren nach 48 bis 137 Minuten fertig, Gleitkomma-Gene brauchten 5 bis 24 Stunden</b> (logarithmische Skala). Ehrlicher Hinweis: Jede Codierung lief einmal, mit ihrer eigenen empfohlenen Einstellung — 100 Kandidaten für Rastergene, 1000 für Gleitkomma-Gene —, der Faktor liegt also nicht allein an der Codierung. Aus [Net17] §6.3–6.5; die meiste Zeit ging in den Crossover."), lang)


# =====================================================================
# Hero and the research-page pictogram
# =====================================================================
def _cloud(layouts, x0, y0, size, cls, r_=1.6):
    out = []
    for l in layouts:
        for c in l:
            x, y = site_xy(*sim.centre(c, RHO), x0, y0, size)
            out.append(f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{r_}"/>')
    return "".join(out)


def _curve(x0, y0, w, h, vals, lo, hi, cls):
    n = len(vals) - 1
    pts = [(x0 + k / n * w, y0 + h - (v - lo) / (hi - lo) * h) for k, v in enumerate(vals)]
    d = "M" + "".join((f"{x:.1f} {y:.1f}" if k == 0 else f"H{x:.1f}V{y:.1f}") for k, (x, y) in enumerate(pts))
    return f'<path class="{cls}" d="{d}"/>'


def hero_ea(lang):
    L = lambda en, de: en if lang == "en" else de
    hist = TOY["hist"]
    best_last = max(TOY["last"], key=lambda l: sim.fitness(l, RHO))

    def panel(x0, y0, size, layouts, cls, title):
        return (site([], x0, y0, size, iso=True, label=False) + _cloud(layouts, x0, y0, size, cls)
                + f'<text class="s" x="{x0}" y="{y0 + size + 16}">{title}</text>')

    def chart(x0, y0, w, h, short=False):
        lo, hi = .4, .65
        out = [f'<path class="ln" d="M{x0} {y0}V{y0 + h}H{x0 + w}"/>']
        out.append(_curve(x0, y0, w, h, [v[2] for v in hist], lo, hi, "ln worst"))
        out.append(_curve(x0, y0, w, h, [v[1] for v in hist], lo, hi, "ln mean"))
        out.append(_curve(x0, y0, w, h, [v[0] for v in hist], lo, hi, "ln hl"))
        out.append(f'<text class="s" x="{x0}" y="{y0 + h + 16}">{L("fitness: best, mean, worst", "Fitness: beste, Mittel, schlechteste") if short else L("fitness over 60 generations: best, mean, worst", "Fitness über 60 Generationen: beste, mittlere, schlechteste")}</text>')
        return "".join(out)
    dots = lambda x0, y0, size: "".join(f'<circle class="hfill" cx="{site_xy(*sim.centre(c, RHO), x0, y0, size)[0]:.1f}" cy="{site_xy(*sim.centre(c, RHO), x0, y0, size)[1]:.1f}" r="3"/>' for c in best_last)
    ring = _loop_ring(lang, "20", L("layouts · 60 generations", "Layouts · 60 Generationen"), inner=True)
    wide = (f'<g transform="translate(0 4) scale(.72)">{ring}</g>'
            + panel(330, 24, 150, TOY["first"], "gdot", L("generation 0", "Generation 0"))
            + _arrow(488, 99, 510, 99, "ln hl")
            + panel(518, 24, 150, TOY["last"], "gdot", L("generation 60, best in colour", "Generation 60, bestes farbig")) + dots(518, 24, 150)
            + chart(700, 30, 150, 144, short=True))
    tall = (f'<g transform="translate(-5 0)">{ring}</g>'
            + panel(20, 320, 180, TOY["first"], "gdot", L("generation 0", "Generation 0"))
            + panel(230, 320, 180, TOY["last"], "gdot", L("generation 60", "Generation 60")) + dots(230, 320, 180)
            + chart(40, 550, 360, 120))
    return (f'<figure class="art-hero" aria-hidden="true"><svg class="dia hero hero-wide" viewBox="0 0 860 220">{wide}</svg>'
            f'<svg class="dia hero hero-tall" viewBox="0 0 430 700">{tall}</svg></figure>')


def thumb_ea():
    """Research-page card: the loop as a ring of nine steps (as in ea3 and the hero) and a DNA helix — the chromosome."""
    cx, cy, R, n = 60, 59, 38, len(NODES)
    out = [f'<circle cx="{cx}" cy="{cy}" r="{R}"/>']
    for k in range(n):                                   # chevrons between the steps, clockwise
        a = -math.pi / 2 + 2 * math.pi * (k + .5) / n
        x, y, t = cx + R * math.cos(a), cy + R * math.sin(a), a + math.pi / 2
        p1 = (x - 4 * math.cos(t) + 3 * math.cos(a), y - 4 * math.sin(t) + 3 * math.sin(a))
        p2 = (x - 4 * math.cos(t) - 3 * math.cos(a), y - 4 * math.sin(t) - 3 * math.sin(a))
        out.append(f'<path d="M{p1[0]:.1f} {p1[1]:.1f}L{x:.1f} {y:.1f}L{p2[0]:.1f} {p2[1]:.1f}"/>')
    for k in range(n):
        a = -math.pi / 2 + 2 * math.pi * k / n
        out.append(f'<circle class="{"f" if k == 0 else "b"}" cx="{cx + R * math.cos(a):.1f}" cy="{cy + R * math.sin(a):.1f}" r="3.2"/>')
    # two helices side by side (vertical), rungs = alleles; accent lines map specific alleles of one onto the other
    y0, y1, A, P = 14, 104, 11, 45.0
    def helix(xc):
        rungs = []
        for k, y in enumerate(range(y0 + 3, y1 - 1, 7)):
            xa = xc + A * math.sin(2 * math.pi * (y - y0) / P)
            if abs(2 * (xa - xc)) > 4:
                rungs.append((k, y, min(xa, 2 * xc - xa), max(xa, 2 * xc - xa)))
        strand = lambda ph: "M" + "L".join(f"{xc + A * math.sin(2 * math.pi * (y - y0) / P + ph):.1f} {y:.1f}" for y in [y0 + k * 1.5 for k in range(int((y1 - y0) / 1.5) + 1)])
        return rungs, strand
    L_, R_ = 138, 210
    rl, sl = helix(L_)
    rr, sr = helix(R_)
    pick_l, pick_r = {r[0]: r for r in rl}, {r[0]: r for r in rr}
    links = [(k1, k2) for k1, k2 in ((1, 4), (5, 2), (8, 8), (11, 10)) if k1 in pick_l and k2 in pick_r]
    hot_l, hot_r = {a for a, _ in links}, {b for _, b in links}
    for k, y, xa, xb in rl:
        out.append(f'<path{" class=\"a\"" if k in hot_l else ""} d="M{xa:.1f} {y}H{xb:.1f}"/>')
    for k, y, xa, xb in rr:
        out.append(f'<path{" class=\"a\"" if k in hot_r else ""} d="M{xa:.1f} {y}H{xb:.1f}"/>')
    out.append(f'<path d="{sl(0)}"/><path d="{sl(math.pi)}"/><path d="{sr(0)}"/><path d="{sr(math.pi)}"/>')
    for a, b in links:                                   # the mapping, from the right end of one allele to the left end of the other
        _, ya, _, xa = pick_l[a]
        _, yb, xb, _ = pick_r[b]
        out.append(f'<path class="a" style="stroke-width:1;stroke-dasharray:2 2" d="M{xa + 2:.1f} {ya}L{xb - 2:.1f} {yb}"/>')
    return "".join(out)
