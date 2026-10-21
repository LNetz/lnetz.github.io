"""
The computations behind the figures of the Evolutionary Algorithms article (research-ea.html, _build/ea.py):
a small genetic algorithm on a toy wind-farm site and one on the two-hills function, both with a seeded random
number generator, so that every bar, dot and curve in the figures comes from a real, replayable run.

The toy site follows the master's thesis [Net17] in a reduced form: 12 turbines on a 1000 m square, a minimum
distance of 240 m (3 rotor diameters of a V80), grid genes (ρ cells per axis), and the thesis toy objectives
TRIANGLE ("better toward the north-east") and CORNER ("four good corners"), normalised to [0, 1] per turbine; the
fitness of a layout is the mean of its turbines (our choice). The operators are the thesis ones: roulette-wheel
selection, random pairing, One-Step crossover, choosing + worst-biased mutation, replace-worst, random newcomers.
_check() runs at import and fails the build if a number quoted in the text no longer matches.
"""
import math

SITE, N_T, D_MIN = 1000.0, 12, 240.0


# ---------------- a small seeded RNG (mulberry32), identical in assets/ea.js ----------------
class Rng:
    def __init__(self, seed):
        self.a = seed & 0xffffffff

    def random(self):
        self.a = (self.a + 0x6D2B79F5) & 0xffffffff
        t = self.a
        t = ((t ^ (t >> 15)) * (t | 1)) & 0xffffffff
        t ^= (t + (((t ^ (t >> 7)) * (t | 61)) & 0xffffffff)) & 0xffffffff
        return ((t ^ (t >> 14)) & 0xffffffff) / 4294967296

    def int(self, n):
        return int(self.random() * n)

    def gauss(self):
        u, v = max(self.random(), 1e-12), self.random()
        return math.sqrt(-2 * math.log(u)) * math.cos(2 * math.pi * v)


# ---------------- the toy site ----------------
def centre(cell, rho):
    """Phenotype of a grid gene: the cell (i, j) → the coordinates of its centre in metres (Net17 Eq. 42)."""
    c = SITE / rho
    return ((cell[0] + .5) * c, (cell[1] + .5) * c)


def score_ne(x, y):
    """TRIANGLE (Net17 Eq. 24), normalised: 0 at the south-west corner, 1 at the north-east corner."""
    return (x + y) / (2 * SITE)


def score_corners(x, y):
    """CORNER (Net17 Eq. 22), normalised: distance from the centre, 1 in the corners."""
    return math.hypot(x - SITE / 2, y - SITE / 2) / math.hypot(SITE / 2, SITE / 2)


FIELDS = {"ne": score_ne, "corners": score_corners}


def fits(p, others, rho):
    a = centre(p, rho)
    for q in others:
        b = centre(q, rho)
        if (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 < D_MIN ** 2 - 1e-6:
            return False
    return True


def gene_scores(layout, rho, field="ne"):
    f = FIELDS[field]
    return [f(*centre(p, rho)) for p in layout]


def fitness(layout, rho, field="ne"):
    s = gene_scores(layout, rho, field)
    return sum(s) / len(s)


def factory(rng, rho, n=N_T, log=None, tries=400, restarts=30):
    """The chromosome factory (Net17 §4.3): insert positions one at a time; a position that breaks the spacing is
    reverted and another is drawn. When `tries` draws in a row fail, start over (up to `restarts` times; with a log,
    for the figure, only once) and finally give up ("layout too dense")."""
    for _ in range(1 if log is not None else restarts):
        layout = _factory_once(rng, rho, n, log, tries)
        if layout is not None:
            return layout
    return None


def _factory_once(rng, rho, n, log, tries):
    layout = []
    while len(layout) < n:
        for _ in range(tries):
            p = (rng.int(rho), rng.int(rho))
            if p not in layout and fits(p, layout, rho):
                layout.append(p)
                if log is not None:
                    log.append(("ok", p))
                break
            if log is not None:
                log.append(("rev", p))
        else:
            return None
    return layout


def max_fit(rho):
    """The exact maximum number of turbines that fit on a ρ×ρ grid with the spacing rule (branch and bound)."""
    cells = [(i, j) for j in range(rho) for i in range(rho)]
    best = [0]

    def go(k, chosen):
        if len(chosen) + len(cells) - k <= best[0]:
            return
        if k == len(cells):
            best[0] = len(chosen)
            return
        p = cells[k]
        if fits(p, chosen, rho):
            go(k + 1, chosen + [p])
        go(k + 1, chosen)
    go(0, [])
    return best[0]


# ---------------- the operators (Net17 §4.5–4.10) ----------------
def roulette(rng, fit, n):
    """Roulette-wheel selection p_i = f_i / Σf (Net17 §4.5): n draws with replacement, returns indices."""
    total, out = sum(fit), []
    for _ in range(n):
        r, acc = rng.random() * total, 0.0
        for i, f in enumerate(fit):
            acc += f
            if r < acc:
                out.append(i)
                break
        else:
            out.append(len(fit) - 1)
    return out


def one_step(a, b, rho, field="ne"):
    """One-Step crossover (Net17 Fig. 17): merge both layouts, drop parent B's position on every conflict, rank all
    remaining positions by their own score and keep the N best. Returns the child and the intermediate states."""
    dropped = [q for q in b if q in a or not fits(q, a, rho)]
    merged = list(a) + [q for q in b if q not in dropped]
    f = FIELDS[field]
    ranked = sorted(merged, key=lambda p: -f(*centre(p, rho)))
    return ranked[:len(a)], {"dropped": dropped, "ranked": ranked}


def pick_genes(rng, n_genes, n_m):
    """Which genes to mutate (Net17 Eq. 30): genes sorted from worst to best; index ⌊N·(r′²+r′⁴)/2⌋ favours the
    worst. Already chosen indices are drawn again."""
    out = []
    while len(out) < n_m:
        r = rng.random()
        j = min(n_genes - 1, int(n_genes * (r * r + r ** 4) / 2))
        if j not in out:
            out.append(j)
    return out


def mutate(rng, layout, rho, n_min=1, n_max=3, step=.5, field="ne"):
    """Move n_m genes toward a random position by the fraction `step` (Net17 Eq. 31, simplified: s = 1 jumps
    anywhere, s = 0 changes nothing), snap to the grid, keep the spacing (otherwise the gene stays)."""
    f = FIELDS[field]
    order = sorted(range(len(layout)), key=lambda k: f(*centre(layout[k], rho)))      # worst first
    n_m = n_min + rng.int(n_max - n_min + 1)
    child = list(layout)
    moved = []
    for j in pick_genes(rng, len(layout), n_m):
        k = order[j]
        old = child[k]
        for _ in range(20):
            tx, ty = rng.int(rho), rng.int(rho)
            p = (round(old[0] * (1 - step) + tx * step), round(old[1] * (1 - step) + ty * step))
            if p != old and fits(p, child[:k] + child[k + 1:], rho):
                child[k] = p
                moved.append((k, old, p))
                break
    return child, moved


def toy_ga(seed, rho=20, gens=60, pop=20, n_sel=6, p_choose=.3, step=.5, newcomers=2, field="ne", keep=None):
    """One run on the toy site. Returns per-generation best/mean/worst fitness, and the full bookkeeping of the
    generations listed in `keep` (for the loop figure)."""
    rng = Rng(seed)
    P = [factory(rng, rho) for _ in range(pop)]
    P.sort(key=lambda l: -fitness(l, rho, field))
    hist, books, first = [], {}, [list(l) for l in P]
    for g in range(gens + 1):
        fs = [fitness(l, rho, field) for l in P]
        hist.append((max(fs), sum(fs) / len(fs), min(fs)))
        if g == gens:
            break
        sel = roulette(rng, fs, n_sel)
        pairs = []
        for _ in range(n_sel):                                     # random pairing; a parent may be in several pairs
            a = sel[rng.int(n_sel)]
            b = sel[rng.int(n_sel)]
            while b == a and len(set(sel)) > 1:
                b = sel[rng.int(n_sel)]
            pairs.append((a, b))
        kids, kid_info = [], []
        for a, b in pairs:
            child, info = one_step(P[a], P[b], rho, field)
            kids.append(child)
            kid_info.append(info)
        kids0 = [list(l) for l in kids]
        mutated = []
        for k in range(len(kids)):
            if rng.random() < p_choose:
                kids[k], moved = mutate(rng, kids[k], rho, step=step, field=field)
                mutated.append((k, moved))
        merged = [(l, ("p", k)) for k, l in enumerate(P)] + [(l, ("c", k)) for k, l in enumerate(kids)]
        merged.sort(key=lambda t: -fitness(t[0], rho, field))
        survivors = merged[:pop - newcomers]
        fresh = [factory(rng, rho) for _ in range(newcomers)]
        if keep and g in keep:
            books[g] = {"pop": [list(l) for l in P], "fit": fs, "sel": sel, "pairs": pairs, "kids": [list(l) for l in kids], "kids0": kids0,
                        "kid_info": kid_info, "mutated": mutated, "merged": [t[1] for t in merged],
                        "fresh": [list(l) for l in fresh]}
        P = [l for l, _ in survivors] + fresh
        P.sort(key=lambda l: -fitness(l, rho, field))
    return {"hist": hist, "books": books, "first": first, "last": [list(l) for l in P]}


# ---------------- the wake (Jensen top-hat, one west wind) ----------------
K_WAKE, CT, R_ROTOR = .5 / math.log(70 / .03), .8, 40.0


def deficit(dx):
    """Velocity deficit of the Jensen model at distance dx downstream (k = 0.5 / ln(z/z0), z = 70 m, z0 = 0.03 m)."""
    return (1 - math.sqrt(1 - CT)) / (1 + K_WAKE * dx / R_ROTOR) ** 2


def wake_scores(pts, field="ne"):
    """Each turbine's score × (1 − δ)³, δ = root-sum-square of the deficits of the turbines upstream (west) whose
    wake cone (radius R + k·dx) covers it."""
    f, out = FIELDS[field], []
    for i, (x, y) in enumerate(pts):
        d2 = 0.0
        for j, (u, v) in enumerate(pts):
            dx = x - u
            if j != i and dx > 0 and abs(y - v) < R_ROTOR + K_WAKE * dx:
                d2 += deficit(dx) ** 2
        out.append(f(x, y) * (1 - math.sqrt(d2)) ** 3)
    return out


# ---------------- the two-hills function ----------------
LOW, HIGH = (.25, .30), (.80, .75)


def hills(x, y):
    """A broad low hill and a narrow high one on [0,1]² (illustrative)."""
    low = .6 * math.exp(-((x - LOW[0]) ** 2 + (y - LOW[1]) ** 2) / .08)
    high = 1.0 * math.exp(-((x - HIGH[0]) ** 2 + (y - HIGH[1]) ** 2) / .006)
    return max(low, high)


PRESETS = {      # tournament size, mutation share, step, elite, newcomers
    "balanced": dict(k=3, p_mut=.3, sigma=.05, elite=2, imm=2),
    "pressure": dict(k=8, p_mut=0, sigma=.05, elite=2, imm=0),
    "closed": dict(k=3, p_mut=.3, sigma=.05, elite=2, imm=0),
    "random": dict(k=3, p_mut=0, sigma=.05, elite=2, imm=18),
}


def hills_ga(seed, k=3, p_mut=.3, sigma=.05, elite=2, imm=2, pop=20, gens=60):
    """The starter of the article on the two-hills function: tournament selection, uniform crossover, Gaussian
    mutation on a share of the children, elitism and random newcomers. Returns the population of every generation."""
    rng = Rng(seed)
    new = lambda: [rng.random(), rng.random()]
    P = sorted(([hills(*g), g] for g in (new() for _ in range(pop))), key=lambda t: -t[0])
    gens_out = [[g for _, g in P]]
    for _ in range(gens):
        def pick():
            best = None
            for _ in range(k):
                c = P[rng.int(pop)]
                if best is None or c[0] > best[0]:
                    best = c
            return best[1]
        kids = []
        for _ in range(pop - elite - imm):
            a, b = pick(), pick()
            child = [a[i] if rng.random() < .5 else b[i] for i in range(2)]
            if rng.random() < p_mut:
                i = rng.int(2)
                child[i] = min(1.0, max(0.0, child[i] + sigma * rng.gauss()))
            kids.append(child)
        kids += [new() for _ in range(imm)]
        P = sorted(P[:elite] + [[hills(*g), g] for g in kids], key=lambda t: -t[0])
        gens_out.append([g for _, g in P])
    return gens_out


def diversity(pts):
    """Mean distance to the centroid."""
    cx, cy = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
    return sum(math.hypot(p[0] - cx, p[1] - cy) for p in pts) / len(pts)


def on_high(pts):
    return hills(*pts[0]) > .6


def contours(f, levels, n=120, size=1.0):
    """Marching squares over f on [0,size]²: a list of (level, [polyline, …])."""
    st = size / n
    g = [[f(i * st, j * st) for i in range(n + 1)] for j in range(n + 1)]
    out = []
    for lv in levels:
        segs = []
        for j in range(n):
            for i in range(n):
                pts = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
                v = [g[j][i], g[j][i + 1], g[j + 1][i + 1], g[j + 1][i]]
                cr = []
                for k in range(4):
                    a, b = v[k], v[(k + 1) % 4]
                    if (a < lv) != (b < lv):
                        t = (lv - a) / (b - a)
                        p, q = pts[k], pts[(k + 1) % 4]
                        cr.append(((p[0] + t * (q[0] - p[0])) * st, (p[1] + t * (q[1] - p[1])) * st))
                if len(cr) == 2:
                    segs.append(cr)
                elif len(cr) == 4:
                    segs += [cr[:2], cr[2:]]
        # join
        key = lambda p: (round(p[0], 6), round(p[1], 6))
        ends = {}
        for k, (a, b) in enumerate(segs):
            ends.setdefault(key(a), []).append((k, 0))
            ends.setdefault(key(b), []).append((k, 1))
        used, lines = set(), []
        for k in range(len(segs)):
            if k in used:
                continue
            used.add(k)
            line = list(segs[k])
            for forward in (True, False):
                while True:
                    tip = line[-1] if forward else line[0]
                    nxt = [(s, e) for s, e in ends.get(key(tip), []) if s not in used]
                    if not nxt:
                        break
                    s, e = nxt[0]
                    used.add(s)
                    other = segs[s][1 - e]
                    line = line + [other] if forward else [other] + line
            lines.append(line)
        out.append((lv, lines))
    return out


# ---------------- what the article and the figures use ----------------
SEEDS = list(range(1, 11))
MAIN_SEED = 3


def run_hills():
    """All presets × 10 seeds; returns {preset: {"runs": [...], "high": count}}."""
    out = {}
    for name, cfg in PRESETS.items():
        runs = [hills_ga(s, **cfg) for s in SEEDS]
        out[name] = {"runs": runs, "high": sum(on_high(r[-1]) for r in runs)}
    return out


def _check():
    # the thesis worked example (Net17 p. 21): ρ = 5 on a 1000 m square
    pts = [(248, 183), (572, 301), (893, 520), (312, 621), (741, 952)]
    cells = sorted(int(x * 5 / 1000) + int(y * 5 / 1000) * 5 for x, y in pts)
    assert cells == [1, 7, 14, 16, 23], cells
    # finer is not denser: 9 fit at ρ = 6, but 16 at the coarser ρ = 4
    assert max_fit(6) == 9 and max_fit(4) == 16
    # the wake: 240 m downstream a turbine keeps 36 % of its score
    assert round((1 - deficit(240)) ** 3, 2) == .36
    # elitism (replace-worst keeps the best): the best fitness never drops
    run = toy_ga(MAIN_SEED, keep={7})
    best = [h[0] for h in run["hist"]]
    assert all(b2 >= b1 - 1e-12 for b1, b2 in zip(best, best[1:])), best
    return run


TOY = _check()


# ---------------- the starter printed in the article (plain Python, standard library only) ----------------
STARTER = '''import math, random

def fitness(g):  # two hills: broad and low, narrow and high
    x, y = g
    low = 0.6 * math.exp(-((x - 0.25)**2 + (y - 0.30)**2) / 0.08)
    high = 1.0 * math.exp(-((x - 0.80)**2 + (y - 0.75)**2) / 0.006)
    return max(low, high)

def new():  # initialisation: a random candidate
    return [random.random(), random.random()]

def run(seed, size=20, gens=60, elite=2, newcomers=2, k=3, p_mut=0.3, step=0.05):
    random.seed(seed)
    evals = 0
    def score(cands):  # evaluate each candidate once
        nonlocal evals
        evals += len(cands)
        return [(fitness(g), g) for g in cands]
    pop = sorted(score([new() for _ in range(size)]), reverse=True)
    for gen in range(gens):  # stop: a fixed budget of generations
        def pick():  # tournament selection
            return max(random.sample(pop, k))[1]
        kids = []
        for _ in range(size - elite - newcomers):
            a, b = pick(), pick()
            # uniform crossover: each gene from one of the two parents
            child = [random.choice(p) for p in zip(a, b)]
            if random.random() < p_mut:  # mutate some children
                i = random.randrange(2)
                child[i] = min(1, max(0, child[i] + random.gauss(0, step)))
            kids.append(child)
        kids += [new() for _ in range(newcomers)]  # random newcomers
        # elitism + replacement: the best survive, the rest is replaced
        pop = sorted(pop[:elite] + score(kids), reverse=True)
    return pop[0], evals

for seed in range(1, 11):
    (f, best), evals = run(seed)
    print(seed, [round(v, 2) for v in best], round(f, 3), evals)
'''


def starter_results():
    """Runs the starter exactly as printed: [(seed, best fitness, evaluations)]."""
    ns = {}
    exec(STARTER.split("for seed in range(1, 11):")[0], ns)
    return [(s, ns["run"](s)[0][0], ns["run"](s)[1]) for s in range(1, 11)]
