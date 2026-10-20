"""
The 'one city, three maps' figure of the MDE article (section 'What is a model?').

One fictional city is built here once — terrain as a height field, a river, a road network with a hierarchy,
an old town with building blocks, a southern district, woods and six metro stations — and then drawn four times:
as the original (everything), and as three models that each keep only what their purpose needs:
a schematic metro map (topology, not geometry), a road map (road hierarchy, names, bridges) and a hiking map
(contour lines from the height field via marching squares, summit, trail, woods).
All coordinates are in a 300 × 200 city frame; panels scale it.
"""
import html
import json
import math

W, H = 300, 200

# ---------------- terrain ----------------
HILLS = [  # (x, y, sigma along, sigma across, angle in degrees, height above base)
    (236, 44, 46, 26, 30, 118), (268, 92, 28, 18, -20, 54), (206, 26, 22, 14, 70, 40),     # the eastern massif, two tops and a spur
    (48, 38, 40, 22, -35, 74), (92, 14, 30, 12, 10, 34),                                   # the western hill and a northern ridge
    (30, 186, 34, 18, 15, 26), (286, 186, 26, 16, -40, 22)]                                # low rises in the south
BASE = 40


def height(x, y):
    h = BASE
    for cx, cy, sa, sb, ang, a in HILLS:
        c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        u, v = (x - cx) * c + (y - cy) * s_, -(x - cx) * s_ + (y - cy) * c
        h += a * math.exp(-(u * u / (2 * sa * sa) + v * v / (2 * sb * sb)))
    h += 5 * math.sin(x / 23 + y / 31) + 3.5 * math.sin(x / 11.5 - y / 17) + 2 * math.sin((x + y) / 7.3)   # low-frequency relief
    return h - 16 * math.exp(-((y - river_y(x)) ** 2) / (2 * 15 ** 2))   # the river cuts a valley


def river_y(x):
    """The river's centre line as a function of x (smooth, gently meandering)."""
    return 140 - 10 * math.sin(x / 48) + 7 * math.sin(x / 19 + 1.2)


def _contours(level, step=3):
    """Marching squares over the height field: polylines where height == level, joined and smoothed."""
    nx, ny = W // step + 1, H // step + 1
    g = [[height(i * step, j * step) for i in range(nx)] for j in range(ny)]

    def lerp(p, q, a, b):
        t = (level - a) / (b - a)
        return (p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1]))
    segs = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            pts = [(i * step, j * step), ((i + 1) * step, j * step), ((i + 1) * step, (j + 1) * step), (i * step, (j + 1) * step)]
            v = [g[j][i], g[j][i + 1], g[j + 1][i + 1], g[j + 1][i]]
            cross = []
            for k in range(4):
                a, b = v[k], v[(k + 1) % 4]
                if (a < level) != (b < level):
                    cross.append(lerp(pts[k], pts[(k + 1) % 4], a, b))
            if len(cross) == 2:
                segs.append(tuple(cross))
            elif len(cross) == 4:                                    # saddle: pair them up by the centre value
                segs += [(cross[0], cross[1]), (cross[2], cross[3])]
    # join segments into polylines
    key = lambda p: (round(p[0], 3), round(p[1], 3))
    ends = {}
    for k, (a, b) in enumerate(segs):
        ends.setdefault(key(a), []).append((k, 0))
        ends.setdefault(key(b), []).append((k, 1))
    used, lines = set(), []
    for k in range(len(segs)):
        if k in used:
            continue
        used.add(k)
        line = [segs[k][0], segs[k][1]]
        for direction in (1, 0):
            while True:
                tip = line[-1] if direction else line[0]
                nxt = [(s, e) for s, e in ends.get(key(tip), []) if s not in used]
                if not nxt:
                    break
                s, e = nxt[0]
                used.add(s)
                other = segs[s][1 - e]
                if direction:
                    line.append(other)
                else:
                    line.insert(0, other)
        lines.append(_chaikin(line, 2))
    return lines


def _chaikin(pts, n):
    closed = len(pts) > 3 and math.dist(pts[0], pts[-1]) < 0.01
    for _ in range(n):
        out = [pts[0]] if not closed else []
        for a, b in zip(pts, pts[1:]):
            out += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]), (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        if not closed:
            out.append(pts[-1])
        else:
            out.append(out[0])
        pts = out
    return pts


def _path(pts):
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts)


# the crosshair drawn into every panel; assets/mde.js moves it (city coordinates)
CROSS = ('<g class="xh"><line class="xhv" y1="0" y2="200"/><line class="xhh" x1="0" x2="300"/>'
         '<circle class="xhc" r="3.2"/><text class="xht"></text></g>')
LEVELS = list(range(50, 200, 10))                                    # 10 m contours, every 50 m an index contour
CONTOURS = {lv: [_path(l) for l in _contours(lv) if len(l) > 3] for lv in LEVELS}
PEAK = max(((height(x, y), x, y) for x in range(180, 280, 2) for y in range(10, 100, 2)))
TRAIL = f"M166 76 C182 72 196 70 206 66 S 220 {PEAK[2] + 18} {PEAK[1] - 6} {PEAK[2] + 4}"    # from the cathedral up to the summit
TRAIL_W = "M142 86 C120 76 92 60 58 48"                                                     # to the viewpoint on the western hill

# ---------------- river, roads, town ----------------
RIVER = _path([(x, river_y(x)) for x in range(-4, W + 6, 4)])

MAIN = ["M-4 96 C50 95 96 90 142 86 S 232 70 304 76",               # the east–west road through town
        "M150 -4 C148 30 146 60 142 86 S 152 150 156 204"]            # north–south, crosses the river on a bridge
SECOND = ["M142 86 C120 76 92 60 58 48",                              # up to the western hill
          "M232 72 C240 100 250 125 268 150",                         # east, down to the river
          "M100 118 C120 116 135 114 146 112",                        # harbour road
          "M176 160 H272", "M200 152 V200", "M236 156 V200"]          # southern district
BRIDGES = [(river_y(152), 152), (river_y(266), 266)]

OLD_TOWN = (142, 88, -8)                                              # centre and rotation of the street grid


def _old_town(blocks_cls, street_cls, with_streets=True, casing=None):
    cx, cy, rot = OLD_TOWN
    bw, bh, gap = 15, 10, 4.5
    out = []
    for i in range(-3, 3):
        for j in range(-2, 2):
            x, y = cx + i * (bw + gap), cy + j * (bh + gap) - 2
            if (i, j) == (0, 0):                                      # the market square
                out.append(f'<rect class="sq" x="{x:.1f}" y="{y:.1f}" width="{bw}" height="{bh}"/>')
                continue
            out.append(f'<rect class="{blocks_cls}" x="{x + .8:.1f}" y="{y + .8:.1f}" width="{bw - 1.6}" height="{bh - 1.6}"/>')
    streets = ""
    if with_streets:
        for cls in ([casing] if casing else []) + [street_cls]:
            for i in range(-3, 4):
                x = cx + i * (bw + gap) - gap / 2
                streets += f'<path class="{cls}" d="M{x:.1f} {cy - 2 * (bh + gap) - 4:.1f}V{cy + 2 * (bh + gap):.1f}"/>'
            for j in range(-2, 3):
                y = cy + j * (bh + gap) - gap / 2 - 2
                streets += f'<path class="{cls}" d="M{cx - 3 * (bw + gap) - 4:.1f} {y:.1f}H{cx + 3 * (bw + gap):.1f}"/>'
    return f'<g transform="rotate({rot} {cx} {cy})">{streets}{"".join(out)}</g>'


def _south_houses(cls):
    out = ""
    for x in range(178, 270, 9):
        for y in (163, 168 + 0 * 1):
            if 196 < x < 204 or 232 < x < 240:
                continue
            out += f'<rect class="{cls}" x="{x}" y="{y if y == 163 else 150}" width="6" height="6"/>'
    for x in range(204, 232, 9):
        for y in range(170, 196, 9):
            out += f'<rect class="{cls}" x="{x}" y="{y}" width="6" height="6"/>'
    return out


def _trees():
    """Woods on the hill slopes, deterministic scatter (a small LCG), kept off town, roads and river."""
    seed, out = 7, []
    for _ in range(900):
        seed = (seed * 1103515245 + 12345) % 2 ** 31
        x = seed % W
        seed = (seed * 1103515245 + 12345) % 2 ** 31
        y = seed % H
        h = height(x, y)
        if h < 72 or abs(y - river_y(x)) < 16 or math.sin(x / 37) + math.cos(y / 29 + x / 53) < -.2:
            continue
        if 70 < x < 205 and 52 < y < 125:                             # town
            continue
        if abs(x - 148) < 7 or abs(y - (96 - (x / 300) * 20)) < 6:    # main roads (roughly)
            continue
        seed = (seed * 1103515245 + 12345) % 2 ** 31
        out.append((x, y, 1.6 + (seed % 100) / 70))
        if len(out) >= 300:
            break
    return out


TREES = _trees()
FIELDS = ["M8 150L44 146L48 170L10 176Z", "M52 150L84 152L80 176L50 172Z", "M10 180L60 178L58 198L8 199Z",
          "M276 108L298 104L298 126L280 128Z", "M180 98L214 96L216 112L182 116Z", "M96 160L130 158L134 182L100 186Z"]
LANES = ["M58 48 C70 30 84 20 100 14", "M232 72 C226 60 224 52 226 44", "M110 118 C100 104 92 98 80 96",
         "M176 160 C170 150 160 146 152 146", "M272 160 C282 150 290 140 300 136"]
STATIONS = {"park": (60, 96), "central": (142, 86), "cathedral": (166, 76), "university": (232, 72),
            "north": (148, 22), "harbour": (110, 118), "south": (156, 176)}
NAMES = {"en": {"park": "Park", "central": "Central", "cathedral": "Cathedral", "university": "University", "north": "North",
                "harbour": "Harbour", "south": "South"},
         "de": {"park": "Park", "central": "Hbf", "cathedral": "Dom", "university": "Uni", "north": "Nord", "harbour": "Hafen", "south": "Süd"}}
# metro map: octilinear layout — the topology is kept, distances are not
METRO = {"park": (34, 100), "central": (150, 100), "cathedral": (190, 100), "university": (232, 58), "north": (150, 26),
         "harbour": (150, 140), "south": (124, 178)}
LINES = [("a", ["park", "central", "cathedral", "university"], "M34 100H190L232 58"),
         ("b", ["north", "central", "harbour", "south"], "M150 26V140L124 166V178")]


# ---------------- the four panels ----------------

def _original():
    contours = "".join(f'<path class="ct" d="{d}"/>' for lv in LEVELS for d in CONTOURS[lv])
    lanes = "".join(f'<path class="lane" d="{d}"/>' for d in LANES)
    roads = lanes + "".join(f'<path class="rc1" d="{d}"/>' for d in MAIN) + "".join(f'<path class="rc2" d="{d}"/>' for d in SECOND)
    roads += "".join(f'<path class="ri1" d="{d}"/>' for d in MAIN) + "".join(f'<path class="ri2" d="{d}"/>' for d in SECOND)
    trees = "".join(f'<circle class="tree" cx="{x}" cy="{y}" r="{r:.1f}"/>' for x, y, r in TREES)
    fields = "".join(f'<path class="field" d="{d}"/>' for d in FIELDS)
    stations = "".join(f'<rect class="stn0" x="{x - 2.2}" y="{y - 2.2}" width="4.4" height="4.4"/>' for x, y in STATIONS.values())
    return (f'<rect class="land" width="{W}" height="{H}"/>{fields}{contours}<path class="river" d="{RIVER}"/>{trees}'
            f'<rect class="park0" x="44" y="100" width="34" height="18" rx="4"/>{roads}{_old_town("bld", "ri3")}{_south_houses("bld")}{stations}')


def _metro(lang):
    N = NAMES[lang]
    river = '<path class="mriver" d="M-4 154H96L118 132H170L192 154H304"/>'
    lines = "".join(f'<path class="ml {c}" d="{d}"/>' for c, _, d in LINES)
    anchor = {"park": ("middle", 0, -9), "central": ("start", 8, -7), "cathedral": ("middle", 0, 15), "university": ("start", 8, 4),
              "north": ("start", 8, 4), "harbour": ("start", 8, 4), "south": ("start", 8, 4)}
    st = ""
    for k, (x, y) in METRO.items():
        a, dx, dy = anchor[k]
        st += (f'<circle class="{"xchg" if k == "central" else "stn"}" cx="{x}" cy="{y}" r="{5.5 if k == "central" else 4}"/>'
               f'<text class="lbl" x="{x + dx}" y="{y + dy}" text-anchor="{a}">{N[k]}</text>')
    return f'<rect class="paper" width="{W}" height="{H}"/>{river}{lines}{st}'


def _roads(lang):
    blocks = _old_town("blk", "ri3", with_streets=True, casing="rs")
    roads = "".join(f'<path class="lane2" d="{d}"/>' for d in LANES) + "".join(f'<path class="rc1" d="{d}"/>' for d in MAIN) + "".join(f'<path class="rc2" d="{d}"/>' for d in SECOND)
    roads += "".join(f'<path class="rm" d="{d}"/>' for d in MAIN) + "".join(f'<path class="ri2" d="{d}"/>' for d in SECOND)
    bridges = "".join(f'<path class="bridge" d="M{x - 6} {y - 5}H{x + 6}M{x - 6} {y + 5}H{x + 6}"/>' for y, x in BRIDGES)
    labels = (f'<rect class="shield" x="30" y="86" width="20" height="10" rx="2"/><text class="sh" x="40" y="94" text-anchor="middle">B 7</text>'
              f'<rect class="shield" x="140" y="34" width="22" height="10" rx="2"/><text class="sh" x="151" y="42" text-anchor="middle">B 12</text>'
              f'<text class="lbl it" x="250" y="132">{"Ringstraße" if lang == "de" else "Ring Road"}</text>'
              f'<text class="lbl" x="120" y="70">{"Altstadt" if lang == "de" else "Old Town"}</text>')
    return (f'<rect class="paper" width="{W}" height="{H}"/><path class="river thin" d="{RIVER}"/><rect class="blk" x="44" y="100" width="34" height="18" rx="4"/>'
            f'{_south_houses("blk")}{blocks}{roads}{bridges}{labels}')


def _hiking(lang):
    out = ""
    for lv in LEVELS:
        cls = "ci" if lv % 100 == 0 else "cn"
        out += "".join(f'<path class="{cls}" d="{d}"/>' for d in CONTOURS[lv])
    # elevation labels: where the contours of every 20 m cross a ray from the summit down the south-western slope
    labels, (_, px, py) = "", PEAK
    last, placed = None, (px, py)
    for t in range(0, 200):
        x, y = px - t * .78, py + t * .62
        h = height(x, y)
        if last is not None:
            for lv in LEVELS:
                if lv % 20 == 0 and (h - lv) * (last - lv) < 0 and math.dist((x, y), placed) > 13:   # no crowding on steep slopes
                    labels += f'<text class="el" x="{x:.1f}" y="{y + 2:.1f}" text-anchor="middle">{lv}</text>'
                    placed = (x, y)
        last = h
    trees = "".join(f'<circle class="htree" cx="{x}" cy="{y}" r="{r * .6:.1f}"/>' for x, y, r in TREES)
    _, px, py = PEAK
    summit = (f'<path class="peak" d="M{px} {py - 5}L{px + 4.5} {py + 3}H{px - 4.5}Z"/>'
              f'<text class="lbl" x="{px + 7}" y="{py - 3}">{"Kuppe" if lang == "de" else "Summit"}</text><text class="el2" x="{px + 7}" y="{py + 7}">{PEAK[0]:.0f} m</text>')
    town = _old_town("bldf", None, with_streets=False)
    road = f'<path class="faint" d="{MAIN[0]}"/><path class="faint" d="{MAIN[1]}"/>'
    view = '<circle class="view" cx="58" cy="48" r="3"/><path class="view" d="M58 48l6 -6M58 48l7 1"/>'
    return (f'<rect class="paper" width="{W}" height="{H}"/>{trees}{out}<path class="river thin" d="{RIVER}"/>{town}{road}'
            f'<path class="trail" d="{TRAIL}"/><path class="trail" d="{TRAIL_W}"/><path class="trail" d="M142 86 C150 82 158 78 166 76"/>{view}{labels}{summit}')


def fig_maps(lang, fig, T):
    L = lambda x: x[lang]
    s = 1.38
    pw, ph = W * s, H * s
    panels = [
        (_original(), T("THE ORIGINAL · the city itself", "DAS ORIGINAL · die Stadt selbst"), None, None),
        (_metro(lang), T("MODEL 1 · metro map", "MODELL 1 · Liniennetzplan"), T("for: getting across town", "für: durch die Stadt kommen"),
         (T("keeps: stations, lines, changes", "behält: Haltestellen, Linien, Umstiege"), T("drops: distances, directions, streets, terrain", "lässt weg: Entfernungen, Richtungen, Straßen, Gelände"))),
        (_roads(lang), T("MODEL 2 · road map", "MODELL 2 · Straßenkarte"), T("for: driving", "für: Auto fahren"),
         (T("keeps: roads by importance, names, bridges", "behält: Straßen nach Rang, Namen, Brücken"), T("drops: stations, terrain, woods", "lässt weg: Haltestellen, Gelände, Wald"))),
        (_hiking(lang), T("MODEL 3 · hiking map", "MODELL 3 · Wanderkarte"), T("for: walking up the hill", "für: auf den Berg wandern"),
         (T("keeps: contour lines, summit, trails, woods", "behält: Höhenlinien, Gipfel, Wege, Wald"), T("drops: street names, stations, most roads", "lässt weg: Straßennamen, Haltestellen, die meisten Straßen"))),
    ]
    out = ""
    for k, (inner, title, purpose, keeps) in enumerate(panels):
        x, y = (k % 2) * (pw + 32), 22 + (k // 2) * (ph + 84)
        out += (f'<clipPath id="mpc{k}"><rect width="{W}" height="{H}" rx="4"/></clipPath>'
                f'<text class="s{"" if k == 0 else " a"}" x="{x}" y="{y - 8}">{L(title)}</text>'
                f'<g class="mp" data-k="{k}" data-x="{x:.1f}" data-y="{y:.1f}" transform="translate({x} {y}) scale({s})"><g clip-path="url(#mpc{k})">{inner}{CROSS}</g><rect class="frame" width="{W}" height="{H}" rx="4"/></g>')
        if purpose:
            out += (f'<text class="t" x="{x}" y="{y + ph + 20}">{L(purpose)}</text><text class="s" x="{x}" y="{y + ph + 36}">{L(keeps[0])}</text>'
                    f'<text class="s" x="{x}" y="{y + ph + 50}">{L(keeps[1])}</text>')
        else:
            out += f'<text class="s" x="{x}" y="{y + ph + 20}">{L(T("everything at once — and far too much for any single purpose", "alles auf einmal — und viel zu viel für jeden einzelnen Zweck"))}</text>'
    vh = 22 + 2 * (ph + 84) - 26
    # the synced crosshair (assets/mde.js): heights on a 5-unit grid for the hiking map, stations for the metro map
    data = {"s": s, "w": W, "h": H, "step": 5, "heights": [[round(height(i * 5, j * 5)) for i in range(W // 5 + 1)] for j in range(H // 5 + 1)],
            "geo": STATIONS, "metro": METRO, "names": NAMES[lang], "m": "m"}
    js = html.escape(json.dumps(data, separators=(",", ":")), quote=True)
    svg = (f'<svg class="dia citymap" data-map="{js}" viewBox="0 0 {2 * pw + 32:.0f} {vh:.0f}" role="img" aria-label="{L(T("A fictional city with hills, a river, roads, an old town and woods; next to it three maps of it: a schematic metro map, a road map and a hiking map with contour lines, each keeping only what its purpose needs", "Eine fiktive Stadt mit Hügeln, Fluss, Straßen, Altstadt und Wald; daneben drei Karten von ihr: ein schematischer Liniennetzplan, eine Straßenkarte und eine Wanderkarte mit Höhenlinien, jede behält nur, was ihr Zweck braucht"))}">{out}</svg>')
    return fig(svg, T("<b>One city, three models.</b> Each map <i>depicts</i> the city — a dot stands for a real station, a line for a real road. Each <i>leaves things out</i>: the metro map even gives up true distances and directions and keeps only who connects to whom. And what each keeps depends on its <i>purpose</i>. None of them is “the complete” map — and that is the point. Move the pointer over one map: the crosshair marks the same place in all of them — except on the metro map, which has no true positions and can only point to the nearest station. The three features go back to Herbert Stachowiak. Fictional city.",
                      "<b>Eine Stadt, drei Modelle.</b> Jede Karte <i>bildet</i> die Stadt <i>ab</i> — ein Punkt steht für eine echte Haltestelle, eine Linie für eine echte Straße. Jede <i>lässt etwas weg</i>: Der Liniennetzplan gibt sogar echte Entfernungen und Richtungen auf und behält nur, wer mit wem verbunden ist. Und was jede behält, hängt von ihrem <i>Zweck</i> ab. Keine ist „die vollständige“ Karte — und genau darum geht es. Bewegen Sie den Zeiger über eine Karte: Das Fadenkreuz markiert in allen dieselbe Stelle — außer im Liniennetzplan, der keine echten Positionen kennt und nur auf die nächste Haltestelle zeigen kann. Die drei Merkmale gehen auf Herbert Stachowiak zurück. Fiktive Stadt."), lang)
