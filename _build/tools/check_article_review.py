"""Check regenerated article structure and the numerical examples touched by the review.

Run from the repository root: python _build/tools/check_article_review.py
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import math
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '_build'))
import ai4se
import dt_figs
import ea_figs
import ea_sim


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids, self.links, self.markers, self.targets = [], [], [], []
        self.demos = 0
        self.feed(path.read_text(encoding='utf8'))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        for key in ('href', 'src'):
            if key in a:
                self.links.append(a[key])
        if 'data-json' in a:
            json.loads(a['data-json'])
            self.demos += 1
        for key in ('marker-end', 'marker-start', 'clip-path'):
            if a.get(key, '').startswith('url(#'):
                self.targets.append(a[key][5:-1])


for prefix in ('', 'de/'):
    for article in ('ai4se', 'dt', 'ea'):
        path = ROOT / f'{prefix}research-{article}.html'
        p = Page(path)
        assert len(p.ids) == len(set(p.ids)), (path, 'duplicate IDs')
        assert all(t in p.ids for t in p.targets), (path, 'missing SVG target')
        for link in p.links:
            u = urlsplit(link)
            if u.scheme or u.netloc or not link or link.startswith('data:'):
                continue
            dest = (path.parent / unquote(u.path)).resolve() if u.path else path
            assert dest.exists(), (path, 'missing local link', link)
            if u.fragment and dest.suffix == '.html':
                # research publication IDs are rendered by assets/pubs.js.
                if dest.name == 'research.html' and u.fragment.startswith('pub-'):
                    continue
                assert unquote(u.fragment) in Page(dest).ids, (path, 'missing anchor', link)
        print(f'{path.relative_to(ROOT)}: IDs, SVG references, local links, {p.demos} demo payloads OK')

assert math.comb(100, 12) == 1050421051106700
assert 10000**2 * 1000 // 8 == 12_500_000_000
assert round((1 - math.exp(-.5)) * 100, 2) == 39.35
for name, a, b, t0, c, d, t1 in ai4se.MASK_ROWS:
    assert b == d and 0 <= a <= b and 0 <= c <= d
    assert 12 < t1 / t0 < 31
results = ea_sim.starter_results()
assert all(n == 1100 for _, _, n in results)
assert results == ea_sim.starter_results(), 'starter seed reproducibility'
print('EA built-in simulation assertions, 10 starter seeds × 1100 evaluations, memory and Gaussian calculations OK')

db = sqlite3.connect(':memory:')
db.execute('CREATE TABLE telemetry (time TEXT, km INTEGER, charge REAL, battery REAL)')
db.executemany('INSERT INTO telemetry VALUES (?, ?, ?, ?)', dt_figs.TELEMETRY)
for view in dt_figs._shadow_views():
    db.executescript('\n'.join(view['sql']))
assert db.execute('SELECT * FROM charge_now').fetchone() == (79,)
assert db.execute('SELECT * FROM service_due').fetchone() == (0,)
assert db.execute('SELECT * FROM overheating').fetchone() == (1,)
print('All three shadow queries execute in SQLite and match the displayed data')
