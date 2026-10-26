"""
Figures of the Evolutionary Algorithms article (research-ea.html, _build/ea.py). Every mark comes from a real, seeded
run in ea_sim.py; static diagrams are inline SVG with the .dia classes (or small HTML grids that reflow on phones),
interactive ones ship their states (or the data for a small live computation) as data-json — assets/ea.js swaps,
highlights and draws. The literature list (REFS) lives here too.

Chapter 02 runs on the two-hills landscape (hills_ga, the starter at the end of the article); the wind farm of the
master's thesis [Net17] is the case study of chapter 03 (wake demo, grid vs float genes, One-Step crossover, runtimes).
New figures are authored for the series canvas: viewBox width 784 (full) or ≤ 380 (half, never stretched).
"""
import html
import json
import math

from ai4se import T, fig, demo, controls, cite, _link
from article_common import src, source_line
import ea_sim as sim

esc = html.escape

# ---------------- literature (numbered; article_common renumbers by first citation) ----------------
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
    ("Dav85", _link("L. Davis: Applying Adaptive Algorithms to Epistatic Domains. IJCAI 1985, 162–164.", "https://www.ijcai.org/Proceedings/85-1/Papers/029.pdf")),
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


def _dec(s, lang):
    return s.replace(".", ",") if lang == "de" else s


def _scroll(svg):
    from project_content import dia_scroll
    return dia_scroll(svg)


# =====================================================================
# The running example of chapter 02: the two-hills landscape
# =====================================================================
HILLS = sim.run_hills()
HILL_LEVELS = [.1, .2, .3, .4, .5, .55, .7, .8, .9]
HILL_PATHS = sim.contours(sim.hills, HILL_LEVELS, n=150)
STARTER_RES = sim.starter_results()


def _featured(name):
    """The seed shown for a preset: the first one that tells the preset's story."""
    runs = HILLS[name]["runs"]
    want = {"balanced": lambda r: sim.on_high(r[-1]), "pressure": lambda r: not sim.on_high(r[-1]),
            "closed": lambda r: not sim.on_high(r[-1]), "random": lambda r: True}[name]
    return next(k for k, r in enumerate(runs) if want(r))


def _hp(p, S, x0=0, y0=0):
    return x0 + p[0] * S, y0 + (1 - p[1]) * S


def land(S, x0=0, y0=0, quiet=False):
    """The two-hills map: a frame and the contour lines of sim.hills, north up."""
    out = [f'<rect class="box" x="{x0}" y="{y0}" width="{S}" height="{S}"/>']
    for lv, lines in HILL_PATHS:
        if quiet and lv not in (.1, .3, .5, .7, .9):
            continue
        d = "".join("M" + "L".join(f"{x0 + x * S:.1f} {y0 + (1 - y) * S:.1f}" for x, y in line) for line in lines if len(line) > 2)
        out.append(f'<path class="iso{" iso-i" if lv in (.5, .9) else ""}" d="{d}"/>')
    return "".join(out)


def land_paths(S):
    """Contour paths only (for figures that draw their own frame)."""
    return land(S)


# =====================================================================
# F1  What you give / what you get (an HTML grid: it reflows on phones)
# =====================================================================
def fig_map(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    rows = [
        (W("a formal model", "ein formales Modell"), W("rules, constraints", "Regeln, Bedingungen"),
         W("search and solvers", "Suche und Solver"), W("planners, SAT/SMT, integer programs", "Planer, SAT/SMT, ganzzahlige Programme"),
         W("an answer", "eine Antwort"), W("for this one problem", "für genau dieses Problem"), ""),
        (W("training data", "Trainingsdaten"), W("learning objective", "Lernzielfunktion"),
         W("machine learning", "Maschinelles Lernen"), W('regression, deep networks, LLMs <a href="research-ai4se.html#neural">→ part 2</a>', 'Regression, tiefe Netze, LLMs <a href="research-ai4se.html#neural">→ Teil 2</a>'),
         W("a reusable model", "ein wiederverwendbares Modell"), W("for new inputs", "für neue Eingaben"), ""),
        (W("only a score", "nur eine Bewertung"), W("a way to rate any candidate", "ein Weg, jeden Kandidaten zu benoten"),
         W("search with a score", "Suche mit einer Bewertung"), W("hill climbing, simulated annealing, <b>evolutionary algorithms</b>", "Hill Climbing, Simulated Annealing, <b>evolutionäre Algorithmen</b>"),
         W("good candidates", "gute Kandidaten"), W("for this one problem", "für genau dieses Problem"), "hl"),
    ]
    head = (f'<div class="gm-h mono">{W("you give", "Sie geben")}</div><div class="gm-a"></div><div class="gm-h mono">{W("the methods", "die Verfahren")}</div>'
            f'<div class="gm-a"></div><div class="gm-h mono">{W("you get", "Sie bekommen")}</div>')
    cell = lambda t, s, cls="": f'<div class="gm-c {cls}"><b>{t}</b><span class="mono">{s}</span></div>'
    body = "".join(cell(a, b) + '<div class="gm-a mono" aria-hidden="true">→</div>' + cell(c, d, "gm-m " + k) + '<div class="gm-a mono" aria-hidden="true">→</div>' + cell(e, f)
                   for a, b, c, d, e, f, k in rows)
    note = (f'<p class="gm-x mono">{W("Overlap: evolution can also tune or grow a model — neuroevolution, hyperparameter search.", "Überschneidung: Evolution kann auch ein Modell einstellen oder wachsen lassen — Neuroevolution, Hyperparameter-Suche.")}</p>')
    return (f'<figure class="media art-fig"><div class="gm">{head}{body}</div>{note}'
            f'<figcaption class="mono">{W("<b>Sort AI methods by what you give them and what you get back.</b> Typical interfaces, not disjoint categories: the basic EA needs a scalar evaluator. Multiobjective and quality-diversity variants need richer information; neuroevolution can return reusable models.", "<b>KI-Verfahren danach sortiert, was man ihnen gibt und was man zurückbekommt.</b> Typische Schnittstellen, keine disjunkten Klassen: Der einfache EA braucht eine skalare Bewertung. Mehrkriterielle und Quality-Diversity-Varianten brauchen mehr Information; Neuroevolution kann wiederverwendbare Modelle liefern.")}</figcaption></figure>')


# =====================================================================
# F2  Learning from data vs searching with a score (toggle: the LLM as the variation step)   viewBox 784
# =====================================================================
def demo_pipes(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))

    def b(x, y, w, t, s="", cls="box"):
        return (f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="44" rx="3"/>'
                f'<text class="t" x="{x + w / 2}" y="{y + (19 if s else 27)}" text-anchor="middle">{t}</text>'
                + (f'<text class="s" x="{x + w / 2}" y="{y + 35}" text-anchor="middle">{s}</text>' if s else ""))
    y1, y2 = 34, 140
    top = (b(20, y1, 140, W("training data", "Trainingsdaten"), W("learning objective", "Lernzielfunktion"))
           + _arrow(160, y1 + 22, 196, y1 + 22) + b(196, y1, 140, W("loss", "Fehler"), W("how wrong?", "wie falsch?"))
           + _arrow(336, y1 + 22, 372, y1 + 22) + b(372, y1, 180, W("gradient", "Gradient"), W("which way is better?", "welche Richtung ist besser?"))
           + _arrow(552, y1 + 22, 588, y1 + 22) + b(588, y1, 160, W("model", "Modell"), W("for new inputs", "für neue Eingaben"), "box hl")
           + _arrow(462, y1, 462, y1 - 16) + f'<text class="s" x="472" y="{y1 - 8}">{W("adjust the weights, repeat", "Gewichte anpassen, wiederholen")}</text>')
    bottom = (b(20, y2, 140, W("candidates", "Kandidaten"), W("a population", "eine Population"))
              + _arrow(160, y2 + 22, 196, y2 + 22) + b(196, y2, 170, W("score", "Bewertung"), W("e.g. a simulation", "z. B. eine Simulation"))
              + _arrow(366, y2 + 22, 402, y2 + 22) + b(402, y2, 150, W("keep the better", "die Besseren behalten"))
              + _arrow(552, y2 + 22, 588, y2 + 22)
              + '<g class="vary">' + b(588, y2, 176, "", "", "box hl")
              + f'<text class="t v-classic" x="676" y="{y2 + 19}" text-anchor="middle">{W("vary", "variieren")}</text>'
              + f'<text class="s v-classic" x="676" y="{y2 + 35}" text-anchor="middle">{W("recombine, mutate", "kreuzen, mutieren")}</text>'
              + f'<text class="t v-llm" x="676" y="{y2 + 19}" text-anchor="middle">{W("an LLM", "ein LLM")}</text>'
              + f'<text class="s v-llm" x="676" y="{y2 + 35}" text-anchor="middle">{W("rewrites good candidates", "schreibt gute Kandidaten um")}</text></g>'
              + f'<path class="ln" d="M676 {y2 + 44}V{y2 + 66}H90V{y2 + 45}"/>' + _arrow(90, y2 + 56, 90, y2 + 45)
              + f'<text class="s halo" x="383" y="{y2 + 62}" text-anchor="middle">{W("the next generation, repeat", "die nächste Generation, wiederholen")}</text>')
    lbl = (f'<text class="s" x="20" y="14">{W("LEARNING FROM DATA", "AUS DATEN LERNEN")}</text>'
           f'<text class="s" x="20" y="{y2 - 12}">{W("SEARCHING WITH A SCORE", "MIT EINER BEWERTUNG SUCHEN")}</text>')
    svg = (f'<svg class="dia pipes" viewBox="0 0 784 216" role="img" aria-label="{W("Two pipelines: data, loss, gradient, model; and candidates, score, keep the better, vary", "Zwei Abläufe: Daten, Fehler, Gradient, Modell; und Kandidaten, Bewertung, die Besseren behalten, variieren")}">{lbl}{top}{bottom}</svg>')
    btn = [W("classic", "klassisch"), W("LLM as the variation step", "LLM als Variationsschritt")]
    buttons = "".join(f'<button type="button" data-v="{k}" aria-pressed="{"true" if k == 0 else "false"}">{x}</button>' for k, x in enumerate(btn))
    inner = f'<div class="d1-presets chips mono" role="group"><span class="k">{W("VARIATION:", "VARIATION:")}</span>{buttons}</div>{_scroll(svg)}'
    return demo("ea2", {}, inner, T(
        f"<b>What each needs, what each gives.</b> Gradient-based learning uses data and a differentiable objective; the basic single-objective evolutionary search uses a scalar score — which may itself come from a simulation — and yields good candidates. Switch the variation step: in FunSearch {r('FunS')} and AlphaEvolve {r('AlphaE')} an LLM writes the variants, while the loop and the evaluator stay classical.",
        f"<b>Was jeder braucht, was jeder liefert.</b> Gradientenbasiertes Lernen nutzt Daten und eine differenzierbare Zielfunktion; die einfache einkriterielle evolutionäre Suche nutzt eine skalare Bewertung — die selbst aus einer Simulation stammen kann — und liefert gute Kandidaten. Schalten Sie den Variationsschritt um: Bei FunSearch {r('FunS')} und AlphaEvolve {r('AlphaE')} schreibt ein LLM die Varianten, Schleife und Bewertung bleiben klassisch."), lang)


# =====================================================================
# The loop as a ring of five steps (ea3, hero, thumb)
# =====================================================================
NODES = [  # clockwise from the top; the run enters at "stop?" (generation 0 is random and already scored)
    ("stop", T("stop? → the best", "Stopp? → das Beste")),
    ("select", T("select parents", "Eltern wählen")),
    ("vary", T("recombine + mutate", "kreuzen + mutieren")),
    ("eval", T("evaluate", "bewerten")),
    ("survive", T("select survivors", "Überlebende wählen")),
]


def _ring(lang, cx, cy, R, centre=True):
    L = lambda x: x[lang]
    out = [f'<circle class="ring" cx="{cx}" cy="{cy}" r="{R}"/>']
    n = len(NODES)
    for k in range(n):                                    # chevrons between the steps, clockwise
        a = -math.pi / 2 + 2 * math.pi * (k + .5) / n
        x, y, t = cx + R * math.cos(a), cy + R * math.sin(a), a + math.pi / 2
        p1 = (x - 6 * math.cos(t) + 4 * math.cos(a), y - 6 * math.sin(t) + 4 * math.sin(a))
        p2 = (x - 6 * math.cos(t) - 4 * math.cos(a), y - 6 * math.sin(t) - 4 * math.sin(a))
        out.append(f'<path class="ln" d="M{p1[0]:.1f} {p1[1]:.1f}L{x:.1f} {y:.1f}L{p2[0]:.1f} {p2[1]:.1f}"/>')
    for k, (key, name) in enumerate(NODES):
        a = -math.pi / 2 + 2 * math.pi * k / n
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        lx, ly = cx + (R + 12) * math.cos(a), cy + (R + 12) * math.sin(a)
        anchor = "middle" if abs(math.cos(a)) < .3 else ("start" if math.cos(a) > 0 else "end")
        dy = -4 if math.sin(a) < -.6 else (12 if math.sin(a) > .6 else 4)
        out.append(f'<g class="nd" data-n="{key}"><circle cx="{x:.1f}" cy="{y:.1f}" r="5"/>'
                   f'<text x="{lx:.1f}" y="{ly + dy:.1f}" text-anchor="{anchor}">{L(name)}</text></g>')
    if centre:
        out.append(f'<text class="cnt" x="{cx}" y="{cy + 4}" text-anchor="middle"></text><text class="s cnt2" x="{cx}" y="{cy + 22}" text-anchor="middle"></text>')
    return "".join(out)


# =====================================================================
# F3  The loop: one real generation of the starter's GA on the two hills (population 10)
# =====================================================================
LOOP_SEED = 13
BOOK = sim.hills_book(LOOP_SEED)


def demo_loop(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    B = BOOK
    n_pop, n_kids, elite = len(B["pop"]), len(B["kids"]), B["elite"]
    pos, f = {}, {}
    for k, g in enumerate(B["pop"]):
        pos[f"p{k}"], f[f"p{k}"] = g, B["fit"][k]
    for k, g in enumerate(B["kids"]):
        pos[f"c{k}"], f[f"c{k}"] = g, sim.hills(*g)
    for k, g in enumerate(B["fresh"]):
        pos[f"n{k}"], f[f"n{k}"] = g, sim.hills(*g)
    parents = {f"c{k}": (f"p{a}", f"p{b}") for k, (a, b) in enumerate(B["parents"])}
    before = {f"c{k}": g for k, g in enumerate(B["kids0"])}
    mut = {f"c{k}" for k, m in enumerate(B["mutated"]) if m}
    wins = {}
    for a, b in B["parents"]:
        for i in (a, b):
            wins[f"p{i}"] = wins.get(f"p{i}", 0) + 1
    kids = [f"c{k}" for k in range(n_kids)]
    news = [f"n{k}" for k in range(len(B["fresh"]))]
    ids = [f"p{k}" for k in range(n_pop)]
    eli = ids[:elite]
    better = [c for c in kids if f[c] > max(f[p] for p in parents[c]) + .01]
    top = max(kids, key=lambda c: f[c])
    nxt = sorted(eli + kids + news, key=lambda i: -f[i])
    assert len(better) == 2 and f[top] > f["p0"] and len(mut) == 3
    star = max(wins, key=wins.get)
    never = [i for i in ids if i not in wins]
    assert star in ("p0", "p1") and "p9" in never
    assert f["p0"] > 3 * f["p9"] + .1 and max(f.values()) < .6            # real spread; the axis ends at 0.6
    best0, best1 = f["p0"], f[nxt[0]]
    fx = lambda v: _dec(f"{v:.2f}", lang)
    pair = lambda c: f"#{int(parents[c][0][1:]) + 1} × #{int(parents[c][1][1:]) + 1}"
    rows_p = lambda cls=lambda i: "", note=lambda i: "": [[i, cls(i), note(i)] for i in ids]
    div = [["—", "div", ""]]
    states = [
        dict(node="stop", cnt=f"{n_pop}", cnt2=W("generation 0", "Generation 0"), rows=rows_p(),
             say=W(f"Generation 0: {n_pop} random points on the two hills, each scored by its height and ranked. Stop? Not yet — the budget allows more generations.",
                   f"Generation 0: {n_pop} zufällige Punkte auf den zwei Hügeln, jeder nach seiner Höhe bewertet und sortiert. Stopp? Noch nicht — das Budget erlaubt weitere Generationen.")),
        dict(node="select", cnt=f"{2 * n_kids}", cnt2=W("parents drawn", "Eltern gezogen"),
             rows=rows_p(lambda i: "sel" if i in wins else "", lambda i: f"×{wins[i]}" if i in wins else ""),
             say=W(f"Select parents by tournament: draw 3 at random, the highest wins. {n_kids} children need {2 * n_kids} parents. #{int(star[1:]) + 1} wins {wins[star]} times, #1 {wins['p0']} times, {len(never)} candidates never — better odds, not certainty.",
                   f"Eltern per Turnier wählen: 3 zufällig ziehen, der höchste gewinnt. {n_kids} Kinder brauchen {2 * n_kids} Eltern. #{int(star[1:]) + 1} gewinnt {wins[star]}-mal, #1 {wins['p0']}-mal, {len(never)} Kandidaten nie — bessere Chancen, keine Gewissheit.")),
        dict(node="vary", cnt=f"{n_kids}", cnt2=W("children", "Kinder"),
             rows=rows_p() + div + [[c, "pending" + (" mut" if c in mut else ""), pair(c)] for c in kids],
             say=W(f"Each child takes x from one parent and y from the other (uniform crossover): it lands on a corner of the rectangle its parents span. {len(mut)} of {n_kids} children are then mutated (*): one number is nudged a little. Hover a child to see its parents.",
                   f"Jedes Kind nimmt x von einem Elternteil und y vom anderen (gleichmäßiger Crossover): Es landet auf einer Ecke des Rechtecks, das seine Eltern aufspannen. {len(mut)} von {n_kids} Kindern werden dann mutiert (*): Eine Zahl wird ein wenig verschoben. Zeigen Sie auf ein Kind, um seine Eltern zu sehen.")),
        dict(node="eval", cnt=f"{n_kids}", cnt2=W("evaluated", "bewertet"),
             rows=rows_p() + div + [[c, "child" + (" mut" if c in mut else ""), pair(c)] for c in kids],
             say=W(f"Now the children are evaluated — in a real problem, the expensive part. {len(better)} of them stand higher than both their parents; the best reaches {fx(f[top])}, above anything in generation 0.",
                   f"Jetzt werden die Kinder bewertet — bei einem echten Problem der teure Teil. {len(better)} von ihnen stehen höher als beide Eltern; das beste erreicht {fx(f[top])}, mehr als alles in Generation 0.")),
        dict(node="survive", cnt=f"{elite} + {n_kids} + {len(news)}", cnt2=W("survivors", "Überlebende"),
             rows=[[i, "elite", W("elite", "Elite")] for i in eli] + [[c, "child" + (" mut" if c in mut else ""), pair(c)] for c in kids]
                  + [[i, "fresh", W("newcomer", "Neuling")] for i in news] + [[i, "struck", ""] for i in ids[elite:]],
             say=W(f"Select survivors: the {elite} best parents stay unchanged (the elite); the other {n_pop - elite} are replaced by the {n_kids} children and {len(news)} random newcomer.",
                   f"Überlebende wählen: Die {elite} besten Eltern bleiben unverändert (die Elite); die anderen {n_pop - elite} werden durch die {n_kids} Kinder und {len(news)} zufälligen Neuling ersetzt.")),
        dict(node="stop", cnt=f"{n_pop}", cnt2=W("generation 1", "Generation 1"),
             rows=[[i, ("child" if i[0] == "c" else "fresh" if i[0] == "n" else "elite") + (" mut" if i in mut else ""), ""] for i in nxt],
             say=W(f"Generation 1, re-ranked: best {fx(best1)} (before {fx(best0)}). Stop? Not yet — the starter at the end of the article runs this loop 60 times.",
                   f"Generation 1, neu sortiert: Bestwert {fx(best1)} (vorher {fx(best0)}). Stopp? Noch nicht — der Starter am Ende des Artikels läuft diese Schleife 60-mal.")),
    ]
    data = {"states": states, "f": {k: _n(v) for k, v in f.items()}, "pos": {k: [_n(v, 4) for v in p] for k, p in pos.items()},
            "parents": parents, "before": {k: [_n(v, 4) for v in p] for k, p in before.items() if k in mut}, "lo": 0, "hi": .6,
            "words": {"fit": W("height", "Höhe")}}
    ring = f'<svg class="dia ring-svg" viewBox="0 0 380 250" role="img" aria-label="{W("The loop of an evolutionary algorithm as a ring of five steps", "Die Schleife eines evolutionären Algorithmus als Ring aus fünf Schritten")}">{_ring(lang, 196, 122, 70)}</svg>'
    mini = (f'<svg class="dia lp-map" viewBox="0 0 196 196" role="img" aria-label="{W("The two-hills map with the population as dots", "Die Zwei-Hügel-Karte mit der Population als Punkten")}">'
            f'<g transform="translate(2 2)">{land(192, quiet=True)}<g class="lp-guides"></g><g class="lp-dots"></g></g></svg>')
    inner = (f'<div class="lp3"><div class="lp3-ring">{ring}{mini}</div>'
             f'<div class="lp3-side"><p class="lp3-say" aria-live="polite"></p>{controls(lang)}<div class="rank" role="list"></div></div></div>')
    return demo("ea3", data, inner, T(
        f"<b>One generation of a genetic algorithm.</b> {n_pop} candidates on the two-hills landscape; a candidate is a point (x, y), its fitness the height there. Each row is one candidate, the bar its height; the map shows where they stand. The settings are the starter’s at the end of the article (tournaments of 3, 30 % of the children mutated, an elite of 2), with half the population and one newcomer.",
        f"<b>Eine Generation eines genetischen Algorithmus.</b> {n_pop} Kandidaten auf der Zwei-Hügel-Landschaft; ein Kandidat ist ein Punkt (x, y), seine Fitness die Höhe dort. Jede Zeile ist ein Kandidat, der Balken seine Höhe; die Karte zeigt, wo sie stehen. Die Einstellungen sind die des Starters am Ende des Artikels (Turniere aus 3, 30 % der Kinder mutiert, eine Elite von 2), mit halber Population und einem Neuling."), lang,
        source=T(f"Data: a seeded run (seed {LOOP_SEED})", f"Daten: ein reproduzierbarer Lauf (Seed {LOOP_SEED})"))


# =====================================================================
# F4  Three encodings (HTML panels with small drawings; they stack on phones)
# =====================================================================
PHRASE_TARGET, PHRASE = "HELLO WORLD", "HELPO WOKLD"
TOUR = list("ABCDEGF")
POINT = (.74, .70)


def _tour_svg(tour, S=120, cls="tour", label=True, missing=(), pad=12):
    P = lambda c: (pad + sim.CITIES[c][0] * (S - 2 * pad), pad + (1 - sim.CITIES[c][1]) * (S - 2 * pad))
    pts = [P(c) for c in tour]
    out = []
    if len(tour) > 1:
        out.append(f'<path class="{cls}" d="M{"L".join(f"{x:.1f} {y:.1f}" for x, y in pts)}Z"/>')
    for c in sim.CITIES:
        x, y = P(c)
        out.append(f'<circle class="city{" miss" if c in missing else ""}" cx="{x:.1f}" cy="{y:.1f}" r="3.2"/>')
        if label:
            out.append(f'<text class="s halo" x="{x + (6 if x < S / 2 else -6):.1f}" y="{y + (12 if y > S / 2 else -5):.1f}" text-anchor="{"start" if x < S / 2 else "end"}">{c}</text>')
    return "".join(out)


def fig_encodings(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    right = sum(a == b for a, b in zip(PHRASE, PHRASE_TARGET))
    length = sim.tour_length(TOUR)
    h = sim.hills(*POINT)
    assert right == 9 and len(PHRASE) == len(PHRASE_TARGET) and abs(length - sim.tour_length(list("ABCDEFG"))) > .05
    letters = "".join(f'<span class="{"" if a == b else "bad"}">{"·" if a == " " else a}</span>' for a, b in zip(PHRASE, PHRASE_TARGET))
    tgt = "".join(f'<span>{"·" if a == " " else a}</span>' for a in PHRASE_TARGET)
    px, py = _hp(POINT, 112, 4, 4)
    panels = [
        (W("a phrase · letters", "ein Satz · Buchstaben"),
         f'<div class="enc3-str mono">{letters}</div><div class="enc3-str faint mono">{tgt}</div>',
         W(f"fitness: letters that match the target — {right} of {len(PHRASE)}", f"Fitness: Buchstaben, die zum Ziel passen — {right} von {len(PHRASE)}"),
         W("mutate: change one letter", "mutieren: einen Buchstaben ändern"),
         W("crossover: cut and splice — fine", "Crossover: schneiden und zusammensetzen — passt")),
        (W("a tour · a permutation", "eine Tour · eine Permutation"),
         f'<div class="enc3-str mono">{"".join(f"<span>{c}</span>" for c in TOUR)}</div>'
         f'<svg class="dia enc3-svg" viewBox="0 0 120 120" aria-hidden="true">{_tour_svg(TOUR)}</svg>',
         W(f"fitness: length of the round trip — {length:.2f}, shorter is better", f"Fitness: Länge der Rundreise — {_dec(f'{length:.2f}', lang)}, kürzer ist besser"),
         W("mutate: swap two cities", "mutieren: zwei Städte tauschen"),
         W("crossover: cut and splice breaks it — below", "Crossover: schneiden und zusammensetzen geht schief — unten")),
        (W("a point · two numbers", "ein Punkt · zwei Zahlen"),
         f'<div class="enc3-str mono"><span class="w">{_dec(f"{POINT[0]:.2f}", lang)}</span><span class="w">{_dec(f"{POINT[1]:.2f}", lang)}</span></div>'
         f'<svg class="dia enc3-svg" viewBox="0 0 120 120" aria-hidden="true">{land(112, 4, 4, quiet=True)}<circle class="pt" cx="{px:.1f}" cy="{py:.1f}" r="4"/></svg>',
         W(f"fitness: height of the landscape — {h:.2f}", f"Fitness: Höhe der Landschaft — {_dec(f'{h:.2f}', lang)}"),
         W("mutate: nudge a number", "mutieren: eine Zahl verschieben"),
         W("crossover: mix the coordinates — fine", "Crossover: Koordinaten mischen — passt")),
    ]
    cells = "".join(f'<div class="enc3-p"><p class="enc3-h mono">{t}</p>{g}<p class="enc3-f mono">{fi}</p>'
                    f'<ul class="enc3-ops mono"><li>{m}</li><li>{c}</li></ul></div>' for t, g, fi, m, c in panels)
    return (f'<figure class="media art-fig"><div class="enc3">{cells}</div><figcaption class="mono">'
            + W("<b>Three encodings, three sets of operators.</b> The genotype (top line) is what the algorithm changes; what it means — and therefore which mutation and crossover make sense — depends on the problem. Our running example is the third.",
                "<b>Drei Codierungen, drei Sätze von Operatoren.</b> Der Genotyp (obere Zeile) ist das, was der Algorithmus ändert; was er bedeutet — und damit, welche Mutation und welcher Crossover sinnvoll sind —, hängt vom Problem ab. Unser durchgehendes Beispiel ist das dritte.")
            + source_line(src("illustrative"), lang) + '</figcaption></figure>')


# =====================================================================
# F5  Same loop, different chromosomes (SE tools)
# =====================================================================
def fig_chromosomes(lang):
    L = lambda x: x[lang]
    cols = [
        ("EvoSuite", r("FA13"), T("a whole test suite", "eine ganze Test-Suite"),
         "test 1:\n  Stack s = new Stack();\n  s.push(5);\ntest 2:\n  Stack s = new Stack();\n  s.pop();",
         T("minimise: uncovered branches, and how far the tests miss each one", "minimieren: nicht erreichte Zweige und wie knapp die Tests jeden verfehlen")),
        ("GenProg", r("LeG12"), T("a patch: a list of edits", "ein Patch: eine Liste von Änderungen"),
         "Delete(12)\nInsert(40, 7)\nReplace(81, 44)",
         T("maximise: tests passed. Caution: a patch that deletes the failing feature can pass too", "maximieren: bestandene Tests. Vorsicht: Auch ein Patch, der die fehlerhafte Funktion löscht, kann bestehen")),
        ("PerOpteryx", r("PerOp"), T("an architecture: components → servers", "eine Architektur: Komponenten → Server"),
         "Frontend → server 1\nOrders   → server 1\nBilling  → server 2\nserver 2: 4 cores",
         T("several objectives at once: response time, cost, reliability (NSGA-II)", "mehrere Ziele zugleich: Antwortzeit, Kosten, Zuverlässigkeit (NSGA-II)")),
    ]
    cells = "".join(f'<div class="chr"><p class="mono chr-h">{n} {c}</p><p class="chr-k mono">{L(T("chromosome", "Chromosom"))}: {L(k)}</p>'
                    f'<pre class="mono">{esc(code)}</pre><p class="chr-f">{L(f)}</p></div>' for n, c, k, code, f in cols)
    return (f'<figure class="media art-fig"><div class="chr-grid">{cells}</div><figcaption class="mono">'
            + L(T("<b>And in software engineering.</b> Choosing what a candidate <i>is</i> — and how to score it — is the creative part; the loop is the same. Edit indices of the GenProg column are illustrative.",
                  "<b>Und in der Softwaretechnik.</b> Die Wahl, was ein Kandidat <i>ist</i> — und wie man ihn bewertet —, ist der kreative Teil; die Schleife bleibt dieselbe. Die Indizes der GenProg-Spalte sind illustrativ."))
            + '</figcaption></figure>')


# =====================================================================
# F7  Selection: wheel, tournament, temperature — on generation 0 of the convergence run
# =====================================================================
SEL_RUN = HILLS["balanced"]["runs"][_featured("balanced")]


def demo_selection(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    fs = sorted((sim.hills(*p) for p in SEL_RUN[0]), reverse=True)
    assert max(fs) < .6 and fs[0] / sum(fs) > 3 / len(fs)            # the best slice is more than 3× a fair share: real pressure
    modes = [("wheel", W("roulette wheel", "Glücksrad (Roulette)")), ("tour", W("tournament", "Turnier")), ("temp", W("temperature", "Temperatur"))]
    buttons = "".join(f'<button type="button" data-m="{k}" aria-pressed="{"true" if i == 0 else "false"}">{n}</button>' for i, (k, n) in enumerate(modes))
    inner = (f'<div class="d1-presets chips mono" role="group"><span class="k">{W("SELECTION:", "SELEKTION:")}</span>{buttons}</div>'
             f'<div class="sel-knobs mono"><label class="sl-k"><span>k</span> <input type="range" min="2" max="8" value="3" aria-label="{W("tournament size k", "Turniergröße k")}"> <output>3</output></label>'
             f'<label class="sl-t"><span>T</span> <input type="range" min="0" max="40" value="20" aria-label="{W("temperature", "Temperatur")}"> <output></output></label>'
             f'<label class="sl-off"><input type="checkbox"> {W("+1000 to every score", "+1000 auf jede Bewertung")}</label></div>'
             f'<div class="sl-wrap"><div class="sl-left"><svg class="dia wheel" viewBox="0 0 240 240" role="img" aria-label="{W("A roulette wheel with one slice per candidate", "Ein Glücksrad mit einem Stück je Kandidat")}"></svg>'
             f'<div class="sel-foot mono"><button type="button" class="act draw">{W("draw 6 parents", "6 Eltern ziehen")}</button></div>'
             f'<p class="sel-say mono" aria-live="polite"></p><pre class="sel-tour mono" aria-live="polite"></pre></div>'
             f'<div class="sel-side"><div class="rank sel-rank" role="list"></div></div></div>')
    data = {"f": [_n(v, 4) for v in fs], "lo": 0, "hi": .6,
            "words": {"best": W("best", "bester"), "worst": W("worst", "schlechtester"), "of": W("of the wheel", "des Rads"),
                      "none": W("almost no pressure", "fast kein Druck"), "some": W("some pressure", "etwas Druck"), "strong": W("strong pressure", "starker Druck"),
                      "chance": W("chance per draw", "Chance je Zug"), "tour": W("tournament", "Turnier"), "fit": W("height", "Höhe")}}
    return demo("ea7", data, inner, T(
        f"<b>Where selection pressure comes from.</b> The 20 random candidates of generation 0 in the convergence figure below, best first. The roulette wheel gives each a slice proportional to its height — add 1000 to every score and the wheel turns fair, all differences gone. A tournament (best of k) only compares, so the offset changes nothing; k is the pressure dial {r('GD91')}. Temperature works as in <a href=\"research-ai4se.html#tokens\">part 2</a>: a softmax over the scores, sharp when cold, flat when hot. “Draw” spins six equally spaced pointers once (stochastic universal sampling).",
        f"<b>Woher der Selektionsdruck kommt.</b> Die 20 zufälligen Kandidaten der Generation 0 aus der Konvergenz-Abbildung unten, der beste zuerst. Das Glücksrad gibt jedem ein Stück proportional zu seiner Höhe — addieren Sie 1000 auf jede Bewertung, und das Rad wird fair, alle Unterschiede sind weg. Ein Turnier (Bester aus k) vergleicht nur, der Versatz ändert also nichts; k ist der Regler für den Druck {r('GD91')}. Die Temperatur wirkt wie in <a href=\"research-ai4se.html#tokens\">Teil 2</a>: ein Softmax über die Bewertungen, scharf wenn kalt, flach wenn heiß. „Ziehen“ dreht sechs gleichmäßig verteilte Zeiger einmal (stochastisches universelles Stichprobenverfahren)."), lang)


# =====================================================================
# F8  Crossover: ordered strips · order crossover (OX) on a tour
# =====================================================================
OX_A, OX_B, OX_I, OX_J, OX_CUT = list("ABCDEGF"), list("ABCEDFG"), 2, 5, 4


def demo_crossover(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    A, B, i, j, cut = OX_A, OX_B, OX_I, OX_J, OX_CUT
    naive = sim.one_point(A, B, cut)
    child = sim.order_crossover(A, B, i, j)
    la, lb, lc = (sim.tour_length(t) for t in (A, B, child))
    dup = [c for c in sim.CITIES if naive.count(c) > 1]
    miss = [c for c in sim.CITIES if c not in naive]
    fill = [c for c in B[j:] + B[:j] if c not in A[i:j]]
    assert len(dup) == 1 and len(miss) == 1 and sorted(child) == sorted(A) and lc < min(la, lb)
    fx = lambda v: _dec(f"{v:.2f}", lang)
    cw, x0 = 30, 90

    def strip(y, label, letters, cls=lambda k: ""):
        out = f'<text class="s" x="0" y="{y + 17}">{label}</text>'
        for k, c in enumerate(letters):
            out += (f'<rect class="lt {cls(k)}" x="{x0 + k * cw}" y="{y}" width="{cw - 4}" height="24" rx="2"/>'
                    + (f'<text class="lt-t {cls(k)}" x="{x0 + k * cw + (cw - 4) / 2}" y="{y + 16}" text-anchor="middle">{c}</text>' if c else ""))
        return out

    def maps(t3, lab3, miss3=(), cls3="tour hl"):
        out = ""
        for k, (t, lab, mi, cls) in enumerate(((A, f"A · {fx(la)}", (), "tour"), (B, f"B · {fx(lb)}", (), "tour"), (t3, lab3, miss3, cls3))):
            out += (f'<g transform="translate({4 + k * 126} 120)"><rect class="box" width="118" height="118" rx="2"/>'
                    f'{_tour_svg(t, 118, cls, label=False, missing=mi, pad=12) if t else _tour_svg([], 118, label=False)}</g>'
                    f'<text class="s" x="{4 + k * 126}" y="252">{lab}</text>')
        return out
    pa, pb, ch = W("parent A", "Elternteil A"), W("parent B", "Elternteil B"), W("child", "Kind")
    keep = lambda k: "keep" if i <= k < j else ""
    states = [
        (strip(4, pa, A) + strip(34, pb, B) + strip(78, ch, [""] * 7, lambda k: "empty") + maps([], ""),
         W(f"Two tours through the same 7 cities; the genotype lists the order. Every city exactly once — a permutation. A is {fx(la)} long, B {fx(lb)}: each has one pair of cities in the wrong order.",
           f"Zwei Touren durch dieselben 7 Städte; der Genotyp listet die Reihenfolge. Jede Stadt genau einmal — eine Permutation. A ist {fx(la)} lang, B {fx(lb)}: Bei jeder steht ein Paar Städte falsch herum.")),
        (strip(4, pa, A, lambda k: "fa" if k < cut else "off") + strip(34, pb, B, lambda k: "fb" if k >= cut else "off")
         + strip(78, ch, naive, lambda k: ("bad " if naive[k] in dup else "") + ("fa" if k < cut else "fb"))
         + maps(naive, W(f"{dup[0]} twice, {miss[0]} missing", f"{dup[0]} doppelt, {miss[0]} fehlt"), miss3=miss, cls3="tour bad"),
         W(f"Naive one-point crossover, cut after position {cut}: the head of A, the tail of B. City {dup[0]} appears twice, {miss[0]} not at all — no longer a tour.",
           f"Naiver Ein-Punkt-Crossover, Schnitt nach Position {cut}: der Anfang von A, das Ende von B. Stadt {dup[0]} kommt doppelt vor, {miss[0]} gar nicht — keine Tour mehr.")),
        (strip(4, pa, A, lambda k: "fa keep" if i <= k < j else "off") + strip(34, pb, B, lambda k: "off")
         + strip(78, ch, [c if i <= k < j else "" for k, c in enumerate(A)], lambda k: "fa" if i <= k < j else "empty")
         + maps(A[i:j], W("the slice of A", "der Ausschnitt von A"), cls3="tour hl open"),
         W(f"Order crossover (OX) {r('Dav85')} instead: keep a slice of A in place — positions {i + 1} to {j}, {' '.join(A[i:j])}.",
           f"Stattdessen Order Crossover (OX) {r('Dav85')}: einen Ausschnitt von A an seinem Platz behalten — Positionen {i + 1} bis {j}, {' '.join(A[i:j])}.")),
        (strip(4, pa, A, lambda k: "fa keep" if i <= k < j else "off") + strip(34, pb, B, lambda k: "fb" if B[k] in fill else "off")
         + strip(78, ch, child, lambda k: "fa" if i <= k < j else "fb")
         + maps(child, W(f"child · {fx(lc)}", f"Kind · {fx(lc)}")),
         W(f"Fill the other positions, starting after the slice, with the missing cities in the order they appear in B: {', '.join(fill)}. A valid tour — and here, {fx(lc)}, shorter than both parents.",
           f"Die übrigen Positionen, beginnend hinter dem Ausschnitt, mit den fehlenden Städten in der Reihenfolge von B füllen: {', '.join(fill)}. Eine gültige Tour — und hier mit {fx(lc)} kürzer als beide Eltern.")),
    ]
    data = {"states": [{"svg": s, "say": t} for s, t in states],
            "a": [.20, .35, .35, .60, .80, .70, .40], "b": [.90, .85, .50, .30, .30, .15, .10],
            "words": {"parent": W("parent", "Elternteil"), "child": W("child", "Kind")}}
    ops = [("one", W("one-point", "Ein-Punkt")), ("two", W("two-point", "Zwei-Punkt")), ("uni", W("uniform", "gleichmäßig"))]
    obtn = "".join(f'<button type="button" data-o="{k}" aria-pressed="{"true" if n_ == 0 else "false"}">{n}</button>' for n_, (k, n) in enumerate(ops))
    strip_ = (f'<div class="xo-a"><p class="xo-k mono">{W("NUMBERS IN A FIXED ORDER", "ZAHLEN IN FESTER REIHENFOLGE")}</p>'
              f'<div class="d1-presets chips mono" role="group">{obtn}<button type="button" class="act retoss">{W("new cuts", "neue Schnitte")}</button></div>'
              f'<svg class="dia xo-strip" viewBox="0 0 380 156" role="img" aria-label="{W("Two parent strips of seven numbers and the two children", "Zwei Eltern-Streifen aus sieben Zahlen und die beiden Kinder")}"></svg>'
              f'<p class="xo-say">{W("A schedule of 7 numbers — say, how much of its torque a hybrid car’s engine delivers, second by second (chapter 03). The order means something, so a cut makes sense: children inherit whole stretches.", "Ein Zeitplan aus 7 Zahlen — etwa, welchen Anteil seines Drehmoments der Motor eines Hybridautos liefert, Sekunde für Sekunde (Kapitel 03). Die Reihenfolge bedeutet etwas, ein Schnitt ist also sinnvoll: Kinder erben ganze Abschnitte.")}</p></div>')
    ox = (f'<div class="xo-b"><p class="xo-k mono">{W("A TOUR: ORDER CROSSOVER", "EINE TOUR: ORDER CROSSOVER")}</p>'
          f'<svg class="dia ox" viewBox="0 0 380 258" role="img" aria-label="{W("Two parent tours, a broken one-point child and the order-crossover child", "Zwei Eltern-Touren, ein kaputtes Ein-Punkt-Kind und das Kind des Order Crossover")}"><g class="ox-g"></g></svg>'
          f'<p class="ox-say" aria-live="polite"></p>{controls(lang)}</div>')
    return demo("ea8", data, f'<div class="xo">{strip_}{ox}</div>', T(
        "<b>How to recombine depends on the encoding.</b> Left: the textbook operators on numbers in a fixed order (values illustrative). Right: on a permutation, cutting and splicing repeats and drops cities; order crossover keeps a slice of one parent and the order of the other. City positions illustrative, lengths computed.",
        "<b>Wie man kreuzt, hängt von der Codierung ab.</b> Links die Lehrbuch-Operatoren auf Zahlen in fester Reihenfolge (Werte illustrativ). Rechts: Auf einer Permutation wiederholt Schneiden und Zusammensetzen Städte und verliert andere; Order Crossover behält einen Ausschnitt des einen Elternteils und die Reihenfolge des anderen. Lage der Städte illustrativ, Längen berechnet."), lang)


# =====================================================================
# F9  Mutation: a σ circle on the landscape, sampled mutants (computed live: an illustration of chance)
# =====================================================================
MUT_SPOTS = [("slope", (.70, .62)), ("low", (sim.LOW[0], sim.LOW[1])), ("valley", (.52, .48))]


def demo_mutation(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    S = 300
    names = {"slope": W("on a slope", "am Hang"), "low": W("top of the low hill", "Gipfel des niedrigen Hügels"), "valley": W("in the valley", "im Tal")}
    chips = "".join(f'<button type="button" data-s="{k}" class="{"first" if k == "low" else ""}" aria-pressed="{"true" if k == "slope" else "false"}">{names[k]}</button>' for k, _ in MUT_SPOTS)
    knob = lambda cls, lab, aria, mn, mx, st, v: (f'<label class="{cls}"><span><code>{lab}</code> {aria}</span>'
                                                  f'<input type="range" min="{mn}" max="{mx}" step="{st}" value="{v}" aria-label="{lab}"><output></output></label>')
    knobs = (knob("kn-s", "sigma", W("step size σ", "Schrittweite σ"), .01, .25, .01, .08)
             + knob("kn-i", "indpb", W("chance per number", "Chance je Zahl"), 0, 1, .1, 1)
             + knob("kn-p", "mutpb", W("chance per child", "Chance je Kind"), 0, 1, .1, .5))
    svg = (f'<svg class="dia mu-svg" viewBox="0 0 {S + 8} {S + 8}" role="img" aria-label="{W("The two-hills map with one child, its step-size circle and sampled mutants; tap or use arrow keys to move the child (Shift: larger step)", "Die Zwei-Hügel-Karte mit einem Kind, seinem Schrittweiten-Kreis und gezogenen Mutanten; Tippen oder Pfeiltasten verschieben das Kind (Umschalt: größerer Schritt)")}">'
           f'<g transform="translate(4 4)">{land(S, quiet=True)}<g class="mu-g"></g></g></svg>')
    inner = (f'<div class="d1-presets chips mono" role="group"><span class="k">{W("THE CHILD:", "DAS KIND:")}</span>{chips}</div>'
             f'<div class="mu">{svg}<div class="mu-side"><div class="kn mono">{knobs}</div>'
             f'<p class="mu-count mono" aria-live="polite"></p><p class="mu-say"></p>'
             f'<button type="button" class="act mutate mono">{W("mutate again", "neu mutieren")}</button></div></div>')
    data = {"S": S, "spots": {k: list(p) for k, p in MUT_SPOTS}, "low": list(sim.LOW), "high": list(sim.HIGH), "n": 20,
            "words": {"changed": W("changed", "verändert"), "of": W("of", "von"), "better": W("higher", "höher"), "worse": W("lower", "tiefer"),
                      "same": W("unchanged", "unverändert"), "child": W("child", "Kind"),
                      "say": {"slope": W("On a slope, half the steps go up: small steps refine.", "Am Hang geht die Hälfte der Schritte bergauf: Kleine Schritte verfeinern."),
                              "low": W("On top of the low hill every small step goes down. Only a big σ — or a newcomer — reaches the high hill: that is exploration.", "Auf dem Gipfel des niedrigen Hügels geht jeder kleine Schritt bergab. Nur ein großes σ — oder ein Neuling — erreicht den hohen Hügel: Das ist Erkunden."),
                              "valley": W("In the flat valley most steps change almost nothing: the landscape gives no direction.", "Im flachen Tal ändern die meisten Schritte fast nichts: Die Landschaft gibt keine Richtung vor."),
                              "free": W("Tap the map, or focus it and use arrow keys (Shift: larger step).", "Tippen Sie auf die Karte oder fokussieren Sie sie und nutzen Sie Pfeiltasten (Umschalt: größerer Schritt).")}}}
    return demo("ea9", data, inner, T(
        "<b>Three knobs, not one.</b> Twenty copies of one child go through mutation. <code>mutpb</code>: the chance that a child is mutated at all; <code>indpb</code>: the chance per number (below 1, some mutants move only sideways or only up and down); <code>sigma</code>: the step size — the circle has radius σ, and before boundary clamping, 1 − exp(−1/2) ≈ 39.35 % of isotropic Gaussian steps lie inside it when both coordinates mutate. Coordinates are clamped to [0, 1]. Filled: higher than the child, hollow: lower. The names are those of DEAP; the starter at the end mutates exactly one of the two numbers. Mutants are drawn live.",
        "<b>Drei Regler, nicht einer.</b> Zwanzig Kopien eines Kindes durchlaufen die Mutation. <code>mutpb</code>: die Chance, dass ein Kind überhaupt mutiert wird; <code>indpb</code>: die Chance je Zahl (unter 1 bewegen sich manche Mutanten nur seitwärts oder nur auf und ab); <code>sigma</code>: die Schrittweite — der Kreis hat den Radius σ, und vor dem Begrenzen am Rand liegen 1 − exp(−1/2) ≈ 39,35 % isotroper Gauß-Schritte darin, wenn beide Koordinaten mutieren. Koordinaten werden auf [0, 1] begrenzt. Gefüllt: höher als das Kind, hohl: tiefer. Die Namen sind die von DEAP; der Starter am Ende mutiert genau eine der beiden Zahlen. Die Mutanten werden live gezogen."), lang)


# =====================================================================
# F10  Watching a population converge (two hills)
# =====================================================================
def demo_converge(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    S0 = 344
    labels = (f'<text class="s halo" x="{sim.LOW[0] * S0 - 60:.0f}" y="{(1 - sim.LOW[1]) * S0 - 132:.0f}">{W("broad low hill (0.6)", "breiter niedriger Hügel (0,6)")}</text>'
              f'<text class="s halo" x="{S0 - 6}" y="{(1 - sim.HIGH[1]) * S0 - 46:.0f}" text-anchor="end">{W("narrow high hill (1.0)", "schmaler hoher Hügel (1,0)")}</text>')
    tops = {k: sum(sim.hills(*r_[-1][0]) >= .99 for r_ in HILLS[k]["runs"]) for k in sim.PRESETS}
    assert tops["random"] < tops["balanced"] and HILLS["random"]["high"] == 10      # the texts say so
    presets, names = {}, {"balanced": W("balanced", "ausgewogen"), "pressure": W("high pressure, no mutation", "hoher Druck, keine Mutation"),
                          "closed": W("no newcomers", "keine Neulinge"), "random": W("random search", "Zufallssuche")}
    for name, cfg in sim.PRESETS.items():
        runs, k = HILLS[name]["runs"], _featured(name)
        run = runs[k]
        f_gen = [[sim.hills(*p) for p in gen] for gen in run]
        presets[name] = {
            "pts": [[int(round(v * 999)) for p in gen for v in p] for gen in run], "seed": k + 1, "high": HILLS[name]["high"],
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
    for name, p in presets.items():
        t = sum(f >= .99 for f in p["final"])
        p["say"] = say[name]
        p["count"] = W(f"10 seeds: {p['high']} ended on the high hill, {t} of them at its top (≥ 0.99). Shown: seed {p['seed']}.",
                       f"10 Seeds: {p['high']} endeten auf dem hohen Hügel, {t} davon auf seiner Spitze (≥ 0,99). Gezeigt: Seed {p['seed']}.")
    buttons = "".join(f'<button type="button" data-p="{k}" aria-pressed="{"true" if k == "balanced" else "false"}">{n}</button>' for k, n in names.items())
    land_svg = (f'<svg class="dia land" viewBox="-4 -4 {S0 + 8} {S0 + 8}" role="img" aria-label="{W("Contour lines of two hills with the population as dots", "Höhenlinien zweier Hügel mit der Population als Punkten")}">'
                f'{land(S0)}{labels}<g class="dots"></g></svg>')
    charts = (f'<svg class="dia conv" viewBox="0 0 400 290" role="img" aria-label="{W("Best, mean and worst fitness and the diversity per generation", "Beste, mittlere und schlechteste Fitness und die Vielfalt je Generation")}">'
              f'<g class="ch1" transform="translate(40 18)"></g><g class="ch2" transform="translate(40 196)"></g></svg>')
    inner = (f'<div class="d1-presets chips mono" role="group"><span class="k">{W("SETTINGS:", "EINSTELLUNGEN:")}</span>{buttons}'
             f'<label class="cv-seeds"><input type="checkbox"> {W("all 10 seeds", "alle 10 Seeds")}</label></div>'
             f'<div class="cv">{land_svg}<div class="cv-side">{charts}<p class="cv-say"></p><p class="cv-count mono"></p></div></div>' + controls(lang))
    data = {"presets": presets, "S": S0, "W": 340, "H1": 130, "H2": 56,
            "words": {"best": W("best", "beste"), "mean": W("mean", "Mittel"), "worst": W("worst (newcomers)", "schlechteste (Neulinge)"),
                      "gap": W("fitness gap", "Fitnesslücke"), "div": W("mean radial distance", "mittlerer Radius"), "gen": W("generation", "Generation"),
                      "evals": W("evaluations", "Bewertungen"), "of": W("of", "von")}}
    return demo("ea10", data, inner, T(
        "<b>Watching a population converge.</b> 20 candidates of two numbers on a landscape with a broad low hill and a narrow high one. Top chart: best, mean and worst fitness; the band between best and worst is the <i>fitness gap</i>. Bottom: diversity (mean distance to the centre of the population) — this mean radial distance can hide multiple clusters. Zero means collapsed positions, not proof of an optimum. Counts over 10 seeds each.",
        "<b>Einer Population beim Konvergieren zusehen.</b> 20 Kandidaten aus zwei Zahlen auf einer Landschaft mit einem breiten niedrigen und einem schmalen hohen Hügel. Oberes Diagramm: beste, mittlere und schlechteste Fitness; das Band zwischen bester und schlechtester ist die <i>Fitnesslücke</i>. Unten: mittlerer Abstand zum Zentrum der Population. Dieser mittlere Radius kann mehrere Cluster verbergen. Null bedeutet zusammengefallene Positionen, keinen Nachweis eines Optimums. Anzahlen über je 10 Seeds."), lang,
        source=T("Data: seeded runs · landscape illustrative", "Daten: reproduzierbare Läufe · Landschaft illustrativ"))


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
            f'<tr><td>{W("approximate Pareto set", "angenäherte Pareto-Menge")}</td><td colspan="4"><b>NSGA-II</b> {r("Deb02")} — {W("requires compatible variation and constraint handling", "braucht passende Variation und Nebenbedingungen")} · {se("Sapienz, PerOpteryx")}</td></tr>'
            f'<tr><td>{W("a diverse archive", "ein vielfältiges Archiv")}</td><td colspan="4"><b>MAP-Elites</b> {r("MC15")}, {W("novelty search", "Novelty Search")} {r("LS11")} — {W("likewise", "ebenso")} · {se("ELM, AlphaEvolve")}</td></tr>')
    return (f'<figure class="media art-fig"><div class="tbl-wrap"><table class="tbl mono ea-fam">{head}{rows}</table></div>'
            f'<figcaption class="mono">{W("<b>One loop, many dialects.</b> Columns: what a candidate is, which decides how to vary it. Rows: what you want back, which decides what survives. Rows are example goals and selection/archive strategies, not exclusive algorithm families. NSGA-II approximates a non-dominated set. MAP-Elites stores quality per behavior niche; novelty search rewards behavioral difference. Representation, variation and constraints must remain compatible. AlphaEvolve is related archive-based program search, not an identical algorithm. Grey: the software-engineering tools from this article.", "<b>Eine Schleife, viele Dialekte.</b> Spalten: was ein Kandidat ist — das entscheidet, wie man ihn variiert. Zeilen: was man zurückhaben will — das entscheidet, was überlebt. Die Zeilen zeigen beispielhafte Ziele und Selektions-/Archivstrategien, keine exklusiven Algorithmusfamilien. NSGA-II nähert eine nichtdominierte Menge an. MAP-Elites speichert Qualität je Verhaltensnische; Novelty Search belohnt Verhaltensunterschiede. Darstellung, Variation und Nebenbedingungen müssen zusammenpassen. AlphaEvolve ist verwandte archivbasierte Programmsuche, kein identischer Algorithmus. Grau: die Softwaretechnik-Werkzeuge aus diesem Artikel.")}</figcaption></figure>')


# =====================================================================
# Chapter 03, case: the wind farm (toy site after [Net17])
# =====================================================================
RHO = 20
TOY = sim.TOY
CELL = sim.SITE / RHO


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
                out.append(f'<text class="s iso-l halo" x="{ax + 4:.1f}" y="{ay + 12:.1f}">{c:.1f}</text>')
    for p in layout:
        x, y = (sim.centre(p, rho) if rho else p)
        px, py = P(x, y)
        out.append(f'<circle class="{cls}" cx="{px:.1f}" cy="{py:.1f}" r="{r_}"/>')
    return "".join(out) + extra


def site_xy(x, y, x0, y0, size):
    s = size / sim.SITE
    return x0 + x * s, y0 + (sim.SITE - y) * s


# ---- the wake: drag a turbine (uniform field: the labels are the share of power the wakes leave) ----
WAKE_START = [[125, 525], [375, 525], [625, 525], [125, 875], [625, 875], [375, 175], [875, 175]]
WAKE_KEEP = sim.wake_scores(WAKE_START, "uniform")


def demo_wake(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    ws = WAKE_KEEP
    keep2, keep3 = round(ws[1] * 100), round(ws[2] * 100)
    far = round((1 - sim.deficit(1000)) ** 3 * 100)
    assert (keep2, keep3, far) == (37, 30, 78) and round((1 - sim.deficit(250)) ** 3 * 100) == 37
    data = {"pts": WAKE_START, "k": sim.K_WAKE, "ct": sim.CT, "R": sim.R_ROTOR, "dmin": sim.D_MIN, "cell": CELL, "uniform": True,
            "words": {"total": W("farm output", "Parkleistung"), "nowake": W("without wakes", "ohne Nachlauf"), "too": W("too close", "zu nah"),
                      "now": W("now tap its new place · Esc cancels", "jetzt den neuen Platz antippen · Esc bricht ab"), "turbine": W("turbine", "Turbine")}}
    svg = (f'<svg class="dia wake" viewBox="0 0 300 300" role="img" aria-label="{W("A wind-farm site seen from above; turbines cast wake cones to the east", "Ein Windpark-Gelände von oben; Turbinen werfen Nachlaufkegel nach Osten")}">'
           '<defs><linearGradient id="wk-fade"><stop offset="0" stop-color="var(--accent)" stop-opacity=".2"/><stop offset="1" stop-color="var(--accent)" stop-opacity=".03"/></linearGradient>'
           '<clipPath id="wk-clip"><rect width="260" height="260"/></clipPath></defs>'
           f'<text class="s" x="20" y="13">{W("wind from the west →", "Wind aus Westen →")}</text>'
           f'<g transform="translate(20 20)">{site([], 0, 0, 260, iso=False)}<g class="cones"></g><g class="tbs"></g></g>'
           + _arrow(2, 150, 16, 150, "ln hl") + '</svg>')
    inner = (f'<div class="wk">{svg}<div class="wk-side mono"><p class="wk-total"></p><p class="wk-nowake"></p>'
             f'<p class="wk-hint">{W("The turbines in the middle row sit in a wake — drag one out of it.", "Die Turbinen der mittleren Reihe stehen im Nachlauf — ziehen Sie eine heraus.")}</p>'
             f'<p class="wk-legend">{W("▮ rotor, seen from above · shaded = slowed air · dashed = closer than 240 m", "▮ Rotor, von oben · schattiert = gebremste Luft · gestrichelt = näher als 240 m")}</p>'
             f'<button type="button" class="act wk-reset">{W("reset", "zurücksetzen")}</button></div></div>')
    return demo("ea6", data, inner, T(
        f"<b>Fitness is a simulation.</b> Here every spot of the site is equally windy, so each label is the share of its power a turbine keeps. With a west wind, every turbine slows the air behind it: in the middle row the second turbine keeps {keep2} %, the third {keep3} %, and even 1000 m downstream a wake still costs {100 - far} %. Move one turbine and <i>other</i> turbines’ numbers change — the genes are not independent. This is a simplified Jensen-inspired top-hat model with center-in-wake detection rather than rotor-area overlap, quadratic deficit superposition and cubic relative power, not sensor data or a full wind-farm energy calculation. Distances are metres; percentages are relative to each turbine’s no-wake output. Jensen’s wake model {r('Jen83')} (top-hat, k = 0.5 / ln(z/z₀), C<sub>T</sub> = 0.8); the farm output is the mean.",
        f"<b>Fitness ist eine Simulation.</b> Hier ist jede Stelle des Geländes gleich windig, jede Zahl ist also der Anteil seiner Leistung, den eine Turbine behält. Bei Westwind bremst jede Turbine die Luft hinter sich: In der mittleren Reihe behält die zweite Turbine {keep2} %, die dritte {keep3} %, und selbst 1000 m dahinter kostet ein Nachlauf noch {100 - far} %. Verschieben Sie eine Turbine, und die Zahlen <i>anderer</i> Turbinen ändern sich — die Gene sind nicht unabhängig. Dies ist ein vereinfachtes Jensen-inspiriertes Top-Hat-Modell mit Rotorzentrum-Prüfung statt Rotorflächenüberlappung, quadratischer Defizitüberlagerung und kubischer relativer Leistung, keine Sensordaten oder vollständige Windpark-Energierechnung. Abstände stehen in Metern; Prozentwerte beziehen sich auf jede Turbine ohne Nachlauf. Nachlaufmodell nach Jensen {r('Jen83')} (Top-Hat, k = 0,5 / ln(z/z₀), C<sub>T</sub> = 0,8); die Parkleistung ist der Mittelwert."), lang,
        source=src("after", "Net17", where="§3.3"))


# ---- grid genes vs float genes: three presets ----
def _log10_comb(n, k):
    return (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)) / math.log(10)


def _median(v):
    v = sorted(v)
    return v[len(v) // 2] if len(v) % 2 else (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2


GA_BY_RHO = {rho: [sim.toy_ga(s, rho=rho, gens=40)["hist"][-1][0] for s in range(1, 6)] for rho in (10, 20, 10000)}


def demo_encoding(lang):
    """ea4: the same layout idea at three resolutions — what fits, how big the space is, what a short run reaches."""
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    S0 = 168
    md = {k: _median(v) for k, v in GA_BY_RHO.items()}
    assert abs(md[10000] - md[20]) < .01 and md[10] < md[20] - .01, md                      # the notes say so
    m = {k: _dec(f"{v:.3f}", lang) for k, v in md.items()}
    e = {k: f"{_log10_comb(k * k, 12):.0f}" for k in GA_BY_RHO}
    notes = {10: W(f"100 m cells: two turbines in a row must keep 3 cells = 300 m instead of 240 m. The grid wastes space near the good corner — runs reach only {m[10]}.",
                   f"100-m-Zellen: Zwei Turbinen in einer Reihe müssen 3 Zellen = 300 m statt 240 m Abstand halten. Das Raster verschenkt Platz an der guten Ecke — die Läufe erreichen nur {m[10]}."),
             20: W(f"50 m cells, the grid of this case: 400 cells, about 10<sup>{e[20]}</sup> layouts — far too many to list, few enough to search. Runs reach {m[20]}.",
                   f"50-m-Zellen, das Raster dieses Falls: 400 Zellen, rund 10<sup>{e[20]}</sup> Layouts — viel zu viele zum Auflisten, wenige genug zum Suchen. Die Läufe erreichen {m[20]}."),
             10000: W(f"Floating-point positions look most precise. Here they reach {m[10000]} — about the same, in a space of about 10<sup>{e[10000]}</sup> layouts. This budgeted toy experiment shows no meaningful gain from finer resolution; it does not prove a mathematical optimum.",
                      f"Gleitkomma-Positionen wirken am genauesten. Hier erreichen sie {m[10000]} — etwa dasselbe, in einem Raum von rund 10<sup>{e[10000]}</sup> Layouts. Dieses budgetierte Spielzeugexperiment zeigt keinen wesentlichen Gewinn durch feinere Auflösung; es beweist kein mathematisches Optimum.")}
    presets = []
    for rho, name in ((10, W("10 × 10 grid", "Raster 10 × 10")), (20, W("20 × 20 grid", "Raster 20 × 20")), (10000, W("floats", "Gleitkomma"))):
        run = sim.toy_ga(1, rho=rho, gens=40)
        best = max(run["last"], key=lambda l: sim.fitness(l, rho))
        svg = site(best, 4, 4, S0, rho=rho, grid=rho <= 20, iso=True, label=False, cls="tb hl") + "".join(
            f'<circle class="disc" cx="{site_xy(*sim.centre(c, rho), 4, 4, S0)[0]:.1f}" cy="{site_xy(*sim.centre(c, rho), 4, 4, S0)[1]:.1f}" r="{120 * S0 / 1000:.1f}"/>' for c in best)
        if rho == 10000:
            gen = [f"({_dec(f'{sim.centre(c, rho)[0]:.1f}', lang)}, {_dec(f'{sim.centre(c, rho)[1]:.1f}', lang)})" for c in best[:6]] + ["…"]
            read = [(W("cell size", "Zellgröße"), W("— (0.1 m steps)", "— (0,1-m-Schritte)"))]
        else:
            gen = [f"({c[0]}, {c[1]})" for c in best[:6]] + ["…"]
            read = [(W("cell size", "Zellgröße"), f"{1000 / rho:.0f} m")]
        read += [(W("search space", "Suchraum"), f"≈ 10<sup>{e[rho]}</sup>"), (W("best after 40 gen.", "Bestwert nach 40 Gen."), m[rho])]
        presets.append(dict(label=name, svg=svg, gen=gen, read=read, note=notes[rho]))
    buttons = "".join(f'<button type="button" aria-pressed="{"true" if k == 1 else "false"}">{esc(p["label"])}</button>' for k, p in enumerate(presets))
    inner = (f'<div class="d1-presets chips mono" role="group"><span class="k">{W("GENES:", "GENE:")}</span>{buttons}</div>'
             f'<div class="enc"><pre class="enc-gen mono" aria-label="{W("genotype", "Genotyp")}"></pre>'
             f'<svg class="dia enc-site" viewBox="0 0 176 176" role="img" aria-label="{W("the site with the decoded turbines", "das Gelände mit den decodierten Turbinen")}"></svg>'
             f'<dl class="enc-read mono"></dl></div><p class="enc-note"></p>')
    return demo("ea4", {"presets": presets}, inner, T(
        "<b>Genotype → phenotype at three resolutions.</b> Left the genes, middle what they mean on the 1 km site (dashed circles: half the minimum distance, so overlapping circles are too close), right what it costs and what a short run reached (median of seeds 1–5, 40 generations, 12 turbines, 240 m minimum spacing, toy score “better toward the north-east”). Past a point, more precise is not better. Counts are “before the spacing rule”.",
        "<b>Genotyp → Phänotyp in drei Auflösungen.</b> Links die Gene, in der Mitte ihre Bedeutung auf dem 1-km-Gelände (gestrichelte Kreise: halber Mindestabstand, sich überlappende Kreise stehen also zu nah), rechts, was es kostet und was ein kurzer Lauf erreichte (Median der Seeds 1–5, 40 Generationen, 12 Turbinen, 240 m Mindestabstand, Spielzeug-Bewertung „besser nach Nordosten“). Ab einem Punkt ist genauer nicht besser. Anzahlen „vor der Abstandsregel“."), lang,
        source=src("after", "Net17", where="§4.2"))


# ---- One-Step crossover: a problem-aware operator ----
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


def demo_onestep(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    g, A, B, child, info, (fa, fb, fc) = ONESTEP
    S0 = 150
    fx = lambda v: _dec(f"{v:.3f}", lang)
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
                if k < 12:
                    x, y = site_xy(*sim.centre(c, RHO), 0, 0, S0)
                    out += f'<text class="s rk halo" x="{x + 5:.1f}" y="{y - 4:.1f}">{k + 1}</text>'
        return out
    kept_b = [c for c in B if c not in info["dropped"]]
    states = [
        (panel(A, []) + f'<g transform="translate({S0 + 24} 0)">{panel([], B)}</g>', W(f"Parent A (▼, fitness {fx(fa)}) and parent B (▲, {fx(fb)}): two layouts of 12 turbines. Which turbine is “gene 3”? There is no order — a cut in the middle means nothing.", f"Elternteil A (▼, Fitness {fx(fa)}) und B (▲, {fx(fb)}): zwei Layouts aus 12 Turbinen. Welche Turbine ist „Gen 3“? Es gibt keine Reihenfolge — ein Schnitt in der Mitte bedeutet nichts.")),
        (panel(A, B, rings=info["dropped"]), W(f"Merge both layouts: 24 turbines. {len(info['dropped'])} of B’s turbines are closer than 240 m to one of A’s (circled).", f"Beide Layouts zusammenlegen: 24 Turbinen. {len(info['dropped'])} Turbinen von B stehen näher als 240 m an einer von A (eingekreist).")),
        (panel(A, kept_b), W("Resolve each conflict by dropping B’s turbine. What remains is a valid layout — with too many turbines.", "Jeden Konflikt lösen, indem die Turbine von B wegfällt. Was bleibt, ist ein gültiges Layout — mit zu vielen Turbinen.")),
        (panel(A, kept_b, ranks=info["ranked"], keep=set(child)), W(f"Rank every turbine by its own score and keep the best 12. The child: fitness {fx(fc)} — better than both parents, without a single new position.", f"Jede Turbine nach ihrem eigenen Wert sortieren und die besten 12 behalten. Das Kind: Fitness {fx(fc)} — besser als beide Eltern, ohne eine einzige neue Position.")),
    ]
    assert fc > fa and fc > fb
    data = {"states": [{"svg": s, "say": t} for s, t in states]}
    inner = (f'<div class="os-wrap"><svg class="dia os" viewBox="0 0 328 156" role="img" aria-label="{W("Two parent layouts merged into one child", "Zwei Eltern-Layouts werden zu einem Kind verschmolzen")}"><g class="os-g" transform="translate(2 3)"></g></svg>'
             f'<div class="os-side"><p class="os-say" aria-live="polite"></p>{controls(lang)}</div></div>')
    return demo("ea13", data, inner, T(
        f"<b>A problem-aware operator.</b> A layout is a <i>set</i> of positions, not a sequence, so the thesis built its own crossover. A real crossover from generation {g} of the toy run (toy score “better toward the north-east”). Its trick needs a <b>score per turbine</b>.",
        f"<b>Ein problembewusster Operator.</b> Ein Layout ist eine <i>Menge</i> von Positionen, keine Folge, deshalb hat die Arbeit einen eigenen Crossover gebaut. Eine echte Kreuzung aus Generation {g} des Spielzeuglaufs (Spielzeug-Bewertung „besser nach Nordosten“). Sein Trick braucht einen <b>Wert je Turbine</b>."), lang,
        source=src("after", "Net17", where="Fig. 17"))


# ---- runtimes of grid genes vs float genes  [Net17] §6.3–6.5 ----
RUNTIMES = [("AEP", 48 * 60, 88732.62), ("NPV", 137 * 60, 73594.79), ("IRR", 49 * 60, 17768.83)]   # seconds: grid genes, float genes
assert [round(c / d, 2) for _, d, c in RUNTIMES] == [30.81, 8.95, 6.04]


def fig_runtimes(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    X0, X1 = 200, 560
    lx = lambda s: X0 + (math.log10(s) - 3) / (5 - 3) * (X1 - X0)       # 10^3 … 10^5 s
    out = []
    for e, lab in ((3, "17 min"), (4, "2.8 h"), (5, "28 h")):
        x = X0 + (e - 3) / 2 * (X1 - X0)
        out.append(f'<path class="gridl" d="M{x:.1f} 14V170"/><text class="s" x="{x:.1f}" y="186" text-anchor="middle">10{"³⁴⁵"[e - 3]} s · {_dec(lab, lang)}</text>')
    fmt = lambda s: _dec(f"{s / 60:.0f} min" if s < 3 * 3600 else f"{s / 3600:.1f} h", lang)
    names = {"AEP": W("energy per year", "Jahresenergie"), "NPV": W("net present value", "Kapitalwert"), "IRR": W("internal rate of return", "interner Zinsfuß")}
    for k, (obj, d, c) in enumerate(RUNTIMES):
        y = 22 + k * 52
        out.append(f'<text class="t" x="20" y="{y + 12}">{obj}</text><text class="s" x="20" y="{y + 26}">{names[obj]}</text>')
        out.append(f'<rect class="bar-g" x="{X0}" y="{y}" width="{lx(d) - X0:.1f}" height="12"/><text class="s" x="{lx(d) + 6:.1f}" y="{y + 10}">{W("grid genes", "Rastergene")} · {fmt(d)}</text>')
        out.append(f'<rect class="bar-c" x="{X0}" y="{y + 16}" width="{lx(c) - X0:.1f}" height="12"/>'
                   f'<text class="s" x="{lx(c) + 6:.1f}" y="{y + 26}">{W("float genes", "Gleitkomma-Gene")} · {fmt(c)} · <tspan class="a">×{_dec(f"{c / d:.1f}", lang)}</tspan></text>')
    svg = f'<svg class="dia rt" viewBox="0 0 784 196" role="img" aria-label="{W("Runtimes of the wind-farm optimisation with grid genes and with float genes", "Laufzeiten der Windpark-Optimierung mit Rastergenen und mit Gleitkomma-Genen")}">{"".join(out)}</svg>'
    return fig(svg, T("<b>Horns Rev 1, 80 turbines, three objectives: grid genes finished in 48 to 137 minutes, float genes needed 5 to 24 hours</b> (log scale). Fair warning: n = 1 per configuration on the same Intel Core i7; each encoding used its own recommended setup — 100 candidates for grid genes, 1000 for float genes — so the factor is not the encoding alone; most of the time went into crossover.",
                      "<b>Horns Rev 1, 80 Turbinen, drei Ziele: Rastergene waren nach 48 bis 137 Minuten fertig, Gleitkomma-Gene brauchten 5 bis 24 Stunden</b> (logarithmische Skala). Ehrlicher Hinweis: n = 1 je Konfiguration auf demselben Intel Core i7; jede Codierung nutzte ihre eigene empfohlene Einstellung — 100 Kandidaten für Rastergene, 1000 für Gleitkomma-Gene —, der Faktor liegt also nicht allein an der Codierung; die meiste Zeit ging in den Crossover."), lang,
               source=src("data", "Net17", where="§6.3–6.5"))


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
        (strip(1, hl_first=True), W("Optimise again, apply the first gene again — a receding horizon. A generation budget bounds search work, but execution time depends on evaluation costs and hardware. The paper allows holding a split for up to one second, while the vehicle model advances in 20 ms steps.",
                                    "Wieder optimieren, wieder das erste Gen anwenden — ein zurückweichender Horizont. Ein Generationenbudget begrenzt die Sucharbeit; die Laufzeit hängt von Bewertungskosten und Hardware ab. Das Paper erlaubt, eine Aufteilung bis zu einer Sekunde zu halten, während das Fahrzeugmodell in 20-ms-Schritten fortschreitet.")),
    ]
    weights = [
        (W("fuel only", "nur Kraftstoff"), PHEV_T2[0], W("Saving fuel is all that counts — yet this uses more fuel than the mixed weighting. Limited-horizon myopia is a possible interpretation, not a causal finding.", "Nur Kraftstoffsparen zählt — und doch braucht das mehr Kraftstoff als die gemischte Gewichtung. Kurzsichtigkeit durch den begrenzten Horizont ist eine mögliche Deutung, kein kausaler Befund.")),
        (W("fuel + battery near 60 %", "Kraftstoff + Batterie nahe 60 %"), PHEV_T2[1], W("Half fuel, half “keep the battery near its target”. The best result in the paper: 1.8 % less fuel than the best of the published reference controllers on this cycle.", "Halb Kraftstoff, halb „Batterie nahe am Ziel halten“. Das beste Ergebnis der Arbeit: 1,8 % weniger Kraftstoff als die beste der veröffentlichten Vergleichs-Steuerungen auf diesem Zyklus.")),
        (W("battery level only", "nur Batteriestand"), PHEV_T2[2], W("Only a full battery counts: the GA keeps the battery full and burns fuel — almost as much as driving with the engine alone (428.1 g).", "Nur eine volle Batterie zählt: Der GA hält die Batterie voll und verbrennt Kraftstoff — fast so viel wie mit dem Verbrennungsmotor allein (428,1 g).")),
    ]
    wnames = [W("fuel", "Kraftstoff"), W("battery level", "Batteriestand"), W("battery near target", "Batterie nahe Ziel"), W("smooth", "glatt"), W("very smooth", "sehr glatt")]
    data = {"steps": [{"svg": s, "say": t} for s, t in steps],
            "w": [{"name": nme, "fuel": _dec(f"{fuel:.1f} g", lang), "soc": _dec(f"{soc:.2f}", lang), "say": say, "wv": list(wv)} for nme, (wv, fuel, soc), say in weights],
            "wnames": wnames}
    wbtn = "".join(f'<button type="button" aria-pressed="{"true" if k == 0 else "false"}">{nme}</button>' for k, (nme, _, _) in enumerate(weights))
    inner = (f'<div class="ph"><div class="ph-a"><svg class="dia ph-strip" viewBox="0 0 330 100" role="img" aria-label="{W("A strip of 21 genes over the next 20 seconds", "Ein Streifen aus 21 Genen über die nächsten 20 Sekunden")}"><g class="ph-g"></g></svg>'
             f'<p class="ph-say" aria-live="polite"></p>{controls(lang)}</div>'
             f'<div class="ph-b"><div class="d1-presets chips mono" role="group"><span class="k">{W("FITNESS WEIGHTS:", "FITNESS-GEWICHTE:")}</span>{wbtn}</div>'
             f'<div class="ph-w mono" aria-label="{W("weights", "Gewichte")}"></div>'
             f'<dl class="ph-read mono"><dt>{W("fuel on the NEDC test cycle", "Kraftstoff im NEFZ-Testzyklus")}</dt><dd class="ph-fuel"></dd><dt>{W("battery charge at the end", "Ladestand am Ende")}</dt><dd class="ph-soc"></dd></dl>'
             f'<p class="ph-wsay"></p></div></div>')
    return demo("ea12", data, inner, T(
        "<b>A genetic algorithm inside a car’s controller.</b> Left: schematic receding horizon (seed 5, illustrative values): 20 s prediction, 20 ms vehicle simulation steps, split held for up to 1 s between optimization updates. Right: the same GA with three fitness weightings — real results (simulated parallel hybrid, NEDC cycle, 50 candidates, 100 generations).",
        "<b>Ein genetischer Algorithmus in der Steuerung eines Autos.</b> Links ein schematischer zurückweichender Horizont (Seed 5, illustrative Werte): 20 s Vorhersage, 20 ms Fahrzeug-Simulationsschritte, Aufteilung bis zu 1 s zwischen Optimierungen gehalten. Rechts derselbe GA mit drei Fitness-Gewichtungen — echte Ergebnisse (simulierter Parallelhybrid, NEFZ-Zyklus, 50 Kandidaten, 100 Generationen)."), lang,
        source=src("data", "NWN+15", where="Table 2"))


def fig_phev_tradeoff(lang):
    L = lambda x: x[lang]
    W = lambda en, de: L(T(en, de))
    X0, X1, Y0, Y1 = 70, 744, 36, 200                    # plot area
    fx = lambda s: X0 + (s - 20) / (130 - 20) * (X1 - X0)
    fy = lambda f: Y1 - (f - 384) / (390 - 384) * (Y1 - Y0)
    out = [f'<path class="ln" d="M{X0} {Y0}V{Y1}H{X1}"/>']
    for f in range(384, 391, 2):
        out.append(f'<path class="gridl" d="M{X0} {fy(f):.1f}H{X1}"/><text class="s" x="{X0 - 8}" y="{fy(f) + 4:.1f}" text-anchor="end">{f}</text>')
    for s in (25, 50, 75, 100, 125):
        out.append(f'<text class="s" x="{fx(s):.1f}" y="{Y1 + 16}" text-anchor="middle">{s}</text>')
    out.append(f'<text class="s" x="{X1}" y="{Y1 + 34}" text-anchor="end">{W("jerkiness: Σ |change of the split| over the cycle", "Unruhe: Σ |Änderung der Aufteilung| über den Zyklus")}</text>'
               f'<text class="s" x="{X0}" y="{Y0 - 18}" text-anchor="middle">{W("fuel [g]", "Kraftstoff [g]")}</text>')
    d = "M" + "L".join(f"{fx(s):.1f} {fy(f):.1f}" for _, f, s in PHEV_T4)
    out.append(f'<path class="ln hl" d="{d}"/>' + "".join(f'<circle class="dot" cx="{fx(s):.1f}" cy="{fy(f):.1f}" r="2.6"/>' for _, f, s in PHEV_T4))
    out.append(f'<text class="s a halo" x="{fx(35.19) + 8:.1f}" y="{fy(388.471) - 6:.1f}">{W("max change per step 0.1", "max. Änderung je Schritt 0,1")}</text>'
               f'<text class="s a halo" x="{fx(109.26):.1f}" y="{fy(385.400) - 10:.1f}" text-anchor="middle">{W("max change 1.0 (unrestricted)", "max. Änderung 1,0 (unbeschränkt)")}</text>')
    for (wv, f, s), lab in zip(PHEV_T3, (W("weight: fuel only", "Gewicht: nur Kraftstoff"), W("weight: smoothness only", "Gewicht: nur Glätte"))):
        x, y = fx(s), fy(f)
        out.append(f'<rect class="sq" x="{x - 3.5:.1f}" y="{y - 3.5:.1f}" width="7" height="7"/><text class="s halo" x="{x + (9 if s < 100 else -9):.1f}" y="{y + 4:.1f}" text-anchor="{"start" if s < 100 else "end"}">{lab}</text>')
    svg = f'<svg class="dia trade" viewBox="0 0 784 244" role="img" aria-label="{W("Fuel against jerkiness for different settings", "Kraftstoff gegen Unruhe für verschiedene Einstellungen")}">{"".join(out)}</svg>'
    return fig(svg, T("<b>A trade-off, not one answer.</b> Smooth driving costs fuel. Squares: two fitness weightings. Line: instead of weighting, restrict the search space — consecutive genes may differ by at most 0.1 … 1.0. A weighted sum picks one point on such a curve; NSGA-II seeks an approximation to the Pareto front. Here the line simply joins the finite parameter sweep in Table 4; it is not a computed Pareto front. Squares come from Table 3. The horizontal sum is dimensionless; fuel is in grams. Simulated parallel hybrid, NEDC cycle.",
                      "<b>Ein Zielkonflikt, nicht eine Antwort.</b> Ruhiges Fahren kostet Kraftstoff. Quadrate: zwei Fitness-Gewichtungen. Linie: statt zu gewichten den Suchraum einschränken — aufeinanderfolgende Gene dürfen sich um höchstens 0,1 … 1,0 unterscheiden. Eine gewichtete Summe wählt einen Punkt auf so einer Kurve; NSGA-II sucht eine Annäherung an die Pareto-Front. Hier verbindet die Linie nur den endlichen Parametersweep aus Tabelle 4; sie ist keine berechnete Pareto-Front. Quadrate stammen aus Tabelle 3. Die horizontale Summe ist dimensionslos; Kraftstoff steht in Gramm. Simulierter Parallelhybrid, NEFZ-Zyklus."), lang,
               source=src("data", "NWN+15", where="Tables 3–4"))


# =====================================================================
# Hero (the shared template: grey panel, three columns) and the research-page pictogram
# =====================================================================
def hero_ea(lang):
    L = lambda en, de: en if lang == "en" else de
    run = HILLS["balanced"]["runs"][_featured("balanced")]
    g0, g60 = run[0], run[-1]

    def pop(gen, x0, y0, S):
        best = max(gen, key=lambda p: sim.hills(*p))
        out = land(S, x0, y0, quiet=True)
        for p in gen:
            x, y = _hp(p, S, x0, y0)
            out += f'<circle class="{"hfill" if p is best else "gdot"}" cx="{x:.1f}" cy="{y:.1f}" r="{3.6 if p is best else 3}"/>'
        return out
    h1, h2, h3 = L("THE POPULATION", "DIE POPULATION"), L("THE LOOP", "DIE SCHLEIFE"), L("THE RESULT", "DAS ERGEBNIS")
    wide = (f'<rect class="zone" x="0" y="0" width="860" height="220" rx="6"/>'
            f'<text class="s hh" x="40" y="24">{h1}</text>{pop(g0, 40, 38, 160)}'
            + _arrow(214, 118, 258, 118, "ln hl")
            + f'<text class="s hh" x="418" y="24" text-anchor="middle">{h2}</text>{_ring(lang, 418, 122, 58, centre=False)}'
            + _arrow(608, 118, 652, 118, "ln hl")
            + f'<text class="s hh" x="666" y="24">{h3}</text>{pop(g60, 666, 38, 160)}')
    tall = (f'<rect class="zone" x="0" y="0" width="430" height="500" rx="6"/>'
            f'<text class="s hh" x="215" y="26" text-anchor="middle">{h2}</text>{_ring(lang, 215, 134, 68, centre=False)}'
            f'<text class="s hh" x="24" y="282">{h1}</text>{pop(g0, 24, 294, 180)}'
            f'<text class="s hh" x="226" y="282">{h3}</text>{pop(g60, 226, 294, 180)}'
            + _arrow(206, 384, 220, 384, "ln hl"))
    return (f'<figure class="art-hero" aria-hidden="true"><svg class="dia hero hero-wide" viewBox="0 0 860 220">{wide}</svg>'
            f'<svg class="dia hero hero-tall" viewBox="0 0 430 500">{tall}</svg></figure>')


def thumb_ea():
    """Research-page card: the loop as a ring of five steps (as in ea3 and the hero) and a DNA helix — the chromosome."""
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
        out.append(f'<circle class="{"f" if k == 0 else "b"}" cx="{cx + R * math.cos(a):.1f}" cy="{cy + R * math.sin(a):.1f}" r="3.6"/>')
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
        out.append(f'<path class="a" style="stroke-width:1;stroke-dasharray:3 3" d="M{xa + 2:.1f} {ya}L{xb - 2:.1f} {yb}"/>')
    return "".join(out)
