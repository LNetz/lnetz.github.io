"""Build-time anchors and a static, language-specific search index. No crawling at runtime."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from article_common import _SHARE_ICON

PAGES = {}
PREFIXES = {"index": "about", "photography": "photo", "research-ai4se": "ai",
            "research-mde": "mde", "research-dt": "dt", "research-ea": "ea"}


def prefix(file):
    stem = file.removesuffix(".html")
    return PREFIXES.get(stem, stem.removeprefix("projects-"))


def anchors(body, file, lang):
    """Keep existing destinations; add short aliases to non-article headings and figures."""
    if file.startswith("research-") or file == "404.html":
        return body
    p, n, f = prefix(file), 0, 0

    def link(key):
        label = "Copy link to" if lang == "en" else "Link kopieren:"
        return f'<a class="share global-share" href="#{key}" data-share="{key}" aria-label="{label} {key}">{_SHARE_ICON}</a>'

    def heading(m):
        nonlocal n
        if re.search(r'class="[^"]*\by\b', m.group(2) or ""):
            return m.group(0)  # Publication year labels are not sections.
        n += 1
        tag, attrs, inner = m.groups()
        key = f"{p}-{n}"
        inside_link = body.rfind("<a ", 0, m.start()) > body.rfind("</a>", 0, m.start())
        return f'<{tag}{attrs or ""}><span class="share-at" id="{key}"></span>{inner}{"" if inside_link else link(key)}</{tag}>'

    body = re.sub(r'<(h[123])(\s[^>]*)?>(.*?)</\1>', heading, body, flags=re.S)

    def figure(m):
        nonlocal f
        attrs, content = m.groups()
        if "<figure" in content or "</figcaption>" not in content:
            return m.group(0)
        f += 1
        key = f"{p}-f{f}"
        if 'id="' in attrs:
            content = f'<span class="share-at" id="{key}"></span>' + content
        else:
            attrs += f' id="{key}"'
        # Photo tiles already open a lightbox; do not add a second invisible link inside them.
        if "data-full=" not in content:
            content = content.replace("</figcaption>", link(key) + "</figcaption>", 1)
        return f'<figure{attrs}>{content}</figure>'

    return re.sub(r'<figure([^>]*)>(.*?)</figure>', figure, body, flags=re.S)


class Node:
    def __init__(self, tag="", attrs=(), parent=None):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs), parent, []

    def find(self, predicate):
        if predicate(self):
            return self
        return next((found for child in self.children if isinstance(child, Node)
                     if (found := child.find(predicate))), None)


class Tree(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, body):
        super().__init__(convert_charrefs=True)
        self.root = self.current = Node()
        self.feed(body)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.current.children.append(node)
        if tag not in self.VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        node = self.current
        while node.parent:
            if node.tag == tag:
                self.current = node.parent
                return
            node = node.parent

    def handle_data(self, data):
        self.current.children.append(data)


SKIP = {"script", "style", "svg", "nav", "button", "form", "select", "input", "iframe"}
SKIP_CLASSES = {"share", "harness-hint", "harness-tall", "demo-ctrl", "cu-k", "plinks"}


def excluded(node):
    definition_label = node.tag == "span" and node.parent and "defn" in node.parent.attrs.get("class", "").split()
    return node.tag in SKIP or definition_label or bool(set(node.attrs.get("class", "").split()) & SKIP_CLASSES)


def clean(value):
    return re.sub(r"\s+", " ", value).strip()


def text(node):
    if isinstance(node, str):
        return node
    if excluded(node):
        return ""
    return clean(" ".join(text(child) for child in node.children))


def records(body, file, page, pubs, abstracts=None):
    root = Tree(body).root
    items = []
    current = None
    photos = set()

    def add(title, anchor="", kind="section", section="", content=""):
        item = {"page": page, "title": title, "anchor": anchor, "kind": kind,
                "url": file + ("#" + anchor if anchor else ""), "section": section, "text": content}
        items.append(item)
        return item

    def walk(node):
        nonlocal current
        if isinstance(node, str):
            if current:
                current["text"] += " " + node
            return
        if excluded(node):
            return
        if node.tag == "section":
            previous = current
            for child in node.children:
                walk(child)
            current = previous
            return
        if node.tag in {"h1", "h2", "h3"} and "y" not in node.attrs.get("class", "").split():
            anchor = node.find(lambda n: "share-at" in n.attrs.get("class", "").split())
            key = anchor.attrs.get("id", "") if anchor else node.attrs.get("id", "")
            if not key:
                parent = node.parent
                while parent and not key:
                    key = parent.attrs.get("id", "")
                    parent = parent.parent
            title = re.sub(r"^\d+\s+", "", text(node))
            current = add(title or page, key, "page" if node.tag == "h1" else "section")
            return
        if node.tag == "figure":
            image = node.find(lambda n: n.tag == "img" and "data-full" in n.attrs)
            if image:
                src = image.attrs["data-full"]
                if src in photos:
                    return
                photos.add(src)
            caption = node.find(lambda n: n.tag == "figcaption")
            alias = node.find(lambda n: "share-at" in n.attrs.get("class", "").split())
            key = alias.attrs["id"] if alias else node.attrs.get("id", "")
            if caption and key:
                caption_text = re.split(r"\s+(?:After|Nach|Conceptual synthesis|Begriffliche Synthese)\b", text(caption))[0]
                sentence = re.split(r"(?<=[.!?])\s+", caption_text, maxsplit=1)[0]
                title = sentence[:107].rsplit(" ", 1)[0].rstrip(".,;") + "…" if len(sentence) > 110 else sentence
                body_text = text(node).replace(caption_text, "", 1)
                item = add(title, key, "figure", current["title"] if current else "",
                           caption_text + " " + body_text + (" " + image.attrs.get("alt", "") if image else ""))
                if current:
                    item["parent"] = current["url"]
            return
        if node.tag == "li" and node.attrs.get("id", "").startswith("pub-"):
            key = node.attrs["id"][4:]
            if file == "research.html" and key in pubs:
                paper = pubs[key]
                item = add(paper["title"], node.attrs["id"], "publication", str(paper["year"]),
                           " ".join(str(paper.get(k, "")) for k in ("title", "authors", "venue", "year")))
                abstract = (abstracts or {}).get(key, {})
                if abstract.get("abstract") and abstract.get("title") == paper["title"]:
                    item.update(abstract=abstract["abstract"], abstractLanguage=abstract.get("language", "en"),
                                abstractSource=abstract["source"], abstractSourceType=abstract["sourceType"])
            return
        for child in node.children:
            walk(child)

    walk(root)
    # Headings nested in project cards may resolve to one containing section: merge those passages.
    unique = {}
    for item in items:
        item["text"] = clean(item["text"])
        if item["url"] in unique:
            unique[item["url"]]["text"] += " " + item["title"] + " " + item["text"]
        else:
            unique[item["url"]] = item
    return list(unique.values())


def remember(lang, file, title, body):
    if file != "404.html":
        PAGES.setdefault(lang, {})[file] = (title, body)


def index(lang, pubs):
    source = Path(__file__).with_name("paper-abstracts.json")
    abstracts = json.loads(source.read_text(encoding="utf8")).get("papers", {}) if source.exists() else {}
    if set(abstracts) - set(pubs):
        raise ValueError("Abstract cache contains papers outside assets/pubs.js")
    return [item for file, (title, body) in PAGES[lang].items() for item in records(body, file, title, pubs, abstracts)]


def dumps(lang, pubs):
    return json.dumps(index(lang, pubs), ensure_ascii=False, separators=(",", ":")) + "\n"
