"""Check generated search destinations: python -I _build/tools/check_search.py."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_build"))
from search_index import Node, Tree, anchors, records
BASELINE = json.loads((ROOT / "_build/search-anchor-baseline.json").read_text(encoding="utf8"))


def inspect(node, ids, links, inside_link=False):
    if not isinstance(node, Node):
        return
    if "id" in node.attrs:
        ids.append(node.attrs["id"])
    assert not (inside_link and node.tag == "a"), "Nested link"
    if node.tag == "a" and node.attrs.get("href", "").startswith("#"):
        links.append(node.attrs["href"][1:])
    for child in node.children:
        inspect(child, ids, links, inside_link or node.tag == "a")


for lang in ("en", "de"):
    base = ROOT / ("de" if lang == "de" else "")
    index = json.loads((ROOT / "assets" / f"search-{lang}.json").read_text(encoding="utf8"))
    destinations = {}
    assert len({item["url"] for item in index}) == len(index), "Duplicate results"
    for item in index:
        file, _, anchor = item["url"].partition("#")
        if file not in destinations:
            ids, links = [], []
            inspect(Tree((base / file).read_text(encoding="utf8")).root, ids, links)
            assert len(set(ids)) == len(ids), (file, "Duplicate IDs")
            assert all(link in ids for link in links), (file, "Broken local link")
            assert set(BASELINE.get(file, [])) <= set(ids), (file, "Existing public anchor removed")
            destinations[file] = set(ids)
        assert not anchor or anchor in destinations[file], item["url"]
        assert item["title"], item["url"]
    assert sum(item["kind"] == "publication" for item in index) > 20
    assert any(item["anchor"] == "ai-f12" for item in index)
    abstract_items = [item for item in index if item.get("abstract")]
    assert len(abstract_items) == 29
    assert all(item["kind"] == "publication" and item["abstractSource"].startswith(("https://", "http://")) for item in abstract_items)
    print(f"{lang}: {len(index)} destinations across {len(destinations)} pages passed")

# Aliases must retain existing destinations and never nest a copy link inside a card link.
fixture = '<h1>Page</h1><section id="original"><h2>Section</h2><a href="elsewhere.html"><h3>Card</h3></a></section>'
output = anchors(fixture, "projects-example.html", "en")
ids, links = [], []
inspect(Tree(output).root, ids, links)
assert "original" in ids and "example-3" in ids
result = records(output, "projects-example.html", "Example", {})
assert any(item["anchor"] == "example-3" for item in result)
print("Global alias and linked-card regression checks passed")
