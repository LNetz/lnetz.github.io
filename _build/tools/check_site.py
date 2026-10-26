"""Validate static routes, publication fallback and sharing metadata after building."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids, self.links, self.meta = [], [], {}
        self.canonical = None
        self.h1 = 0
        self.feed(path.read_text(encoding='utf8'))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'h1':
            self.h1 += 1
        for key in ('href', 'src'):
            if key in a:
                self.links.append(a[key])
        if tag == 'meta':
            self.meta[a.get('property', a.get('name'))] = a.get('content')
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonical = a['href']


paths = list(ROOT.glob('*.html')) + list((ROOT / 'de').glob('*.html'))
pages = {p.resolve(): Page(p) for p in paths}
for path, page in pages.items():
    assert page.h1 == 1, path
    assert len(page.ids) == len(set(page.ids)), (path, 'duplicate IDs')
    assert 'main' in page.ids, path
    assert page.canonical.startswith('https://lnetz.github.io/'), path
    assert page.meta['og:url'] == page.canonical, path
    image = page.meta['og:image'].removeprefix('https://lnetz.github.io/')
    assert (ROOT / image).is_file(), (path, image)
    for link in page.links:
        u = urlsplit(link)
        if u.scheme or u.netloc or not link or u.path.startswith('/'):
            continue
        dest = (path.parent / unquote(u.path)).resolve() if u.path else path
        assert dest.exists(), (path, link)
        if dest in pages and u.fragment:
            assert unquote(u.fragment) in pages[dest].ids, (path, link)

for path in (ROOT / 'research.html', ROOT / 'de/research.html'):
    page = pages[path.resolve()]
    assert sum(i.startswith('pub-') and i not in ('pub-count', 'pub-search', 'pub-results', 'pub-empty') for i in page.ids) == 32

urls = [e.text for e in ET.parse(ROOT / 'sitemap.xml').findall('.//{*}loc')]
assert len(urls) == 36 and len(set(urls)) == 36
assert 'https://lnetz.github.io/de/' in urls
assert all('404.html' not in u for u in urls)
print(f'{len(paths)} pages: local destinations and anchors, unique IDs, sharing images, canonical URLs and main landmarks OK')
print('Both research pages contain all 32 publications before JavaScript; sitemap contains 36 unique public routes')
