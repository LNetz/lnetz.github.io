"""
Research sub page: AI-driven software engineering (research-ai4se.html) — an article in the
manner of a blog post, based on the acronio page and the AI4SE / SE4AI talk (10 / 2024), revised 2026.
Imported by build.py. Diagrams are inline SVG with the .dia classes of style.css; the article's own styles are in
assets/ai4se.css. The interactive figures (next token, embeddings-free: neural network, attention, agent trace,
grammar masking) are driven by assets/ai4se.js, which reads its data from the figure's data-json attribute.

Three chapters: what an LLM does (from the outside in) · what is built around the model · making output reliable
(LLMs and models, the case study). Running example of chapter 03: the library (Book / Member / Loan) of part 1.

Shared helpers used by the other articles (keep their signatures): T, cite, ref, _link, fig, demo, controls,
curious, definition.
"""
import html
import json

from project_content import _arrow_defs, box, dia_scroll
import article_art
import article_common

NL = "\n"
FILE = "research-ai4se.html"


def T(en, de):
    return {"en": en, "de": de}


def cite(key):
    """Own paper: a reference to its entry under "My papers on the topic" on the same page (#pub-KEY; that entry
    links on to the research page's full list). article_common.page() lists exactly the cited papers."""
    return f'<a class="cite" href="#pub-{key}">[{key}]</a>'


def ref(n):
    """Other literature: a numbered note at the end of this page."""
    return f'<a class="cite" href="#ref-{n}">[{n}]</a>'


def _link(label, url):
    return f'{label} <a href="{url}" target="_blank" rel="noopener">↗</a>'


# Literature of this article, by key; article_common.page() renumbers by first citation.
REFS = [
    ("turing", "A. M. Turing: Computing Machinery and Intelligence. Mind 59(236), 433–460 (1950)."),
    ("rosenblatt", "F. Rosenblatt: The perceptron: a probabilistic model for information storage and organization in the brain. Psychological Review 65(6), 386–408 (1958)."),
    ("vaswani", "A. Vaswani et al.: Attention is all you need. Advances in Neural Information Processing Systems 30 (2017)."),
    ("brown", "T. Brown et al.: Language models are few-shot learners. Advances in Neural Information Processing Systems 33, 1877–1901 (2020)."),
    ("alice", "M. Nezhurina, L. Cipolina-Kun, M. Cherti, J. Jitsev: Alice in Wonderland: Simple tasks showing complete reasoning breakdown in state-of-the-art large language models. arXiv:2406.02061 (2024)."),
    ("wolfram", _link("S. Wolfram: What Is ChatGPT Doing … and Why Does It Work? Stephen Wolfram Writings (2023).", "https://writings.stephenwolfram.com/2023/02/what-is-chatgpt-doing-and-why-does-it-work/")),
    ("anthropic", _link("E. Schluntz, B. Zhang: Building effective agents. Anthropic Engineering (2024).", "https://www.anthropic.com/engineering/building-effective-agents")),
    ("willison", _link("S. Willison: on the definition of “agent”. simonwillison.net (2025).", "https://simonwillison.net/2025/Sep/18/agents/")),
    ("boeckeler", _link("B. Böckeler: Harness engineering for coding agent users. martinfowler.com.", "https://martinfowler.com/articles/harness-engineering.html")),
    ("trivedy", _link("V. Trivedy: The Anatomy of an Agent Harness. LangChain Blog (2026).", "https://www.langchain.com/blog/the-anatomy-of-an-agent-harness")),
    ("cf-harness", _link("Cloudflare: Harnesses. Agents documentation (accessed October 2026).", "https://developers.cloudflare.com/agents/harnesses/")),
    ("anthropic-harness", _link("Anthropic: Effective harnesses for long-running agents (2025).", "https://www.anthropic.com/research/effective-harnesses-for-long-running-agents")),
    ("anthropic-layers", _link("Anthropic: Trustworthy agents in practice (2026).", "https://www.anthropic.com/research/trustworthy-agents")),
    ("rumelhart", "D. E. Rumelhart, G. E. Hinton, R. J. Williams: Learning representations by back-propagating errors. Nature 323, 533–536 (1986)."),
    ("ouyang", "L. Ouyang et al.: Training language models to follow instructions with human feedback. Advances in Neural Information Processing Systems 35 (2022)."),
    ("sennrich", "R. Sennrich, B. Haddow, A. Birch: Neural machine translation of rare words with subword units. Proc. ACL, 1715–1725 (2016)."),
    ("holtzman", "A. Holtzman, J. Buys, L. Du, M. Forbes, Y. Choi: The curious case of neural text degeneration. ICLR (2020)."),
    ("kalai", "A. T. Kalai, O. Nachum, S. S. Vempala, E. Zhang: Why language models hallucinate. arXiv:2509.04664 (2025)."),
    ("mikolov", "T. Mikolov, W. Yih, G. Zweig: Linguistic regularities in continuous space word representations. Proc. NAACL-HLT, 746–751 (2013)."),
    ("geng", "S. Geng, M. Josifoski, M. Peyrard, R. West: Grammar-constrained decoding for structured NLP tasks without finetuning. Proc. EMNLP (2023)."),
    ("lewis", "P. Lewis et al.: Retrieval-augmented generation for knowledge-intensive NLP tasks. Advances in Neural Information Processing Systems 33 (2020)."),
    ("spracklen", _link("J. Spracklen, R. Wijewickrama, A. H. M. N. Sakib, A. Maiti, B. Viswanath, M. Jadliwala: We Have a Package for You! A Comprehensive Analysis of Package Hallucinations by Code Generating LLMs. USENIX Security (2025).", "https://arxiv.org/abs/2406.10279")),
    ("levesque", "H. J. Levesque, E. Davis, L. Morgenstern: The Winograd Schema Challenge. Proc. KR, 552–561 (2012)."),
    ("openai-cfg", _link("OpenAI: Function calling — custom tools with context-free grammars. OpenAI API documentation (accessed October 2026).", "https://developers.openai.com/api/docs/guides/function-calling")),
]
_RK = {k: n for n, (k, _) in enumerate(REFS, 1)}
OWN = ["NMR24", "BDMN+24", "NRR24", "Net24", "NKR+25"]


def r(key):
    """A literature reference by key (see REFS)."""
    return ref(_RK[key])


def chat(lang, turns, source):
    """A dialogue with a model, set quietly: who speaks in mono, the text below."""
    rows = "".join(f'<div class="turn{" ai" if who != "user" else ""}"><span class="who mono">{(T("User", "Nutzer") if who == "user" else T(who, who))[lang]}</span>'
                   f'<div class="msg">{text}</div></div>' for who, text in turns)
    return f'<figure class="chat">{rows}<figcaption class="mono">{source}</figcaption></figure>'


def fig(svg, caption, lang, scroll=True, source=None):
    """A static figure. source: the caption's final source line, built with article_common.src(...)
    (e.g. src("after", "Net24", where="Fig. 2.4")) or any T()."""
    from article_common import source_line
    inner = dia_scroll(svg) if scroll else svg
    return f'<figure class="media art-fig">{inner}<figcaption class="mono">{caption[lang]}{source_line(source, lang)}</figcaption></figure>'


def demo(kind, data, inner, caption, lang, source=None):
    """An interactive figure: assets/ai4se.js finds it by data-demo and reads data-json. source: as in fig()."""
    from article_common import source_line
    js = html.escape(json.dumps(data, ensure_ascii=False), quote=True)
    return (f'<figure class="media art-fig demo {kind}" data-demo="{kind}" data-json="{js}">{inner}'
            f'<figcaption class="mono">{caption[lang]}{source_line(source, lang)}</figcaption></figure>')


def controls(lang, temperature=False):
    """Play button, step slider and the step label; optionally a temperature slider."""
    t = (f'<label class="temp">{T("temperature", "Temperatur")[lang]} <input type="range" min="0.1" max="2" step="0.1" value="1">'
         f'<output>1.0</output></label>') if temperature else ""
    return (f'<div class="demo-ctrl mono"><button type="button" class="play" aria-label="{T("play", "abspielen")[lang]}">▶</button>'
            f'<input class="step" type="range" min="0" max="1" value="0" aria-label="{T("step", "Schritt")[lang]}">'
            f'<span class="where" aria-live="polite"></span>{t}</div>')


def side_fig(svg, w, caption, lang, source=None, cls=""):
    """A narrow figure (viewBox width w ≤ 360, drawn 1:1, never stretched) with its caption beside it on wide
    screens and below it on phones. Narrow figures need no phone variant: they fit 358 px."""
    from article_common import source_line
    return (f'<figure class="media art-fig side {cls}" style="--w:{w}px"><div class="side-art">{svg}</div>'
            f'<figcaption class="mono">{caption[lang]}{source_line(source, lang)}</figcaption></figure>')


def src(*a, **k):
    return article_common.src(*a, **k)


# =====================================================================
# 01 · What an LLM does
# =====================================================================

# Next-token prediction as a small graph: every node lists its candidates (token, probability, next node).
# Only the listed candidates can be drawn (top-k); several candidates may lead to the same node. The demo draws
# real random numbers ("draw again"); the first, autoplayed answer uses the fixed numbers NT_SEED.
NT = {
    "en": {"start": [("The", .56, "the"), ("Paris", .20, "paris"), ("It", .14, "it"), ("France's", .10, "france")],
           "the": [("capital", .88, "cap"), ("answer", .12, "ans")],
           "cap": [("is", .58, "city"), ("city", .42, "capcity")],
           "capcity": [("is", .93, "city"), (":", .07, "city")],
           "ans": [("is", .80, "city"), (":", .20, "city")],
           "it": [("is", .97, "city"), ("'s", .03, "city")],
           "france": [("capital", 1.0, "capcity")]},
    "de": {"start": [("Die", .56, "the"), ("Paris", .20, "paris"), ("Es", .14, "it"), ("Frankreichs", .10, "france")],
           "the": [("Hauptstadt", .88, "cap"), ("Antwort", .12, "ans")],
           "cap": [("ist", .58, "city"), ("heißt", .42, "city")],
           "ans": [("ist", .80, "city"), (":", .20, "city")],
           "it": [("ist", .97, "city"), ("heißt", .03, "city")],
           "france": [("Hauptstadt", 1.0, "capcity")],
           "capcity": [("ist", .93, "city"), (":", .07, "city")]},
}
for _l in NT.values():
    _l.update({"city": [("Paris", .96, "after"), ("Lyon", .015, "after"), ("Marseille", .01, "after"), ("Toulouse", .01, "after"), ("Berlin", .005, "after")],
               "after": [("<|END|>", .70, None), (".", .30, "end")],
               "paris": [("<|END|>", .55, None), (".", .35, "end"), ("!", .10, "end")],
               "end": [("<|END|>", 1.0, None)]})
NT_SEED = [.30, .20, .62, .15, .40, .50, .50, .50]


def _nt_probs(cands, t):
    """Same as ai4se.js: p_i ∝ p_i^(1/T) over the listed candidates."""
    w = [c[1] ** (1 / t) for c in cands]
    return [v / sum(w) for v in w]


def _nt_answers(nodes, t):
    """{answer text: probability} at temperature t, by walking every path."""
    out = {}

    def walk(n, toks, p):
        for (tok, _, nxt), q in zip(nodes[n], _nt_probs(nodes[n], t)):
            if nxt is None:
                a = _nt_join(toks)
                out[a] = out.get(a, 0) + p * q
            else:
                walk(nxt, toks + [tok], p * q)
    walk("start", [], 1)
    return out


def _nt_join(toks):
    s = ""
    for t in toks:
        s += t if (not s or t[0] in ".,!:;'") else " " + t
    return s


def _nt_seeded(nodes, t):
    n, toks, k = "start", [], 0
    while n:
        ps, acc = _nt_probs(nodes[n], t), 0
        for (tok, _, nxt), p in zip(nodes[n], ps):
            acc += p
            if NT_SEED[k] < acc:
                break
        toks.append(tok)
        n, k = nxt, k + 1
    return _nt_join([x for x in toks if x != "<|END|>"])


def _check_nt():
    """The numbers the caption and the text quote."""
    for lang, nodes in NT.items():
        for n, cands in nodes.items():
            assert abs(sum(c[1] for c in cands) - 1) < 1e-9, (lang, n)
            assert all(c[2] is None or c[2] in nodes for c in cands), (lang, n)
        cold, warm, hot = (_nt_answers(nodes, t) for t in (.1, 1.0, 2.0))
        assert max(cold.values()) > .95                                      # "at 0.1 the answer hardly ever changes"
        wrong = lambda d: sum(p for a, p in d.items() if "Paris" not in a)
        assert .18 < wrong(hot) < .25, wrong(hot)                            # "at 2.0 about one answer in five … wrong city"
        assert wrong(warm) < .05                                             # "at 1.0 almost always Paris"
        assert sum(p ** 10 for p in hot.values()) < .01                      # ten draws at 2.0 give different answers
        assert _nt_seeded(nodes, 1.0) != _nt_seeded(nodes, .1)               # the fixed first answer changes when cold
    assert _nt_seeded(NT["en"], 1.0) == "The capital city is Paris" and _nt_seeded(NT["de"], 1.0) == "Die Hauptstadt heißt Paris"


_check_nt()


def dia_next_token(lang):
    """Slides 12–28: the model only ever picks the next token — by drawing it. Stepped through with the stepper;
    the temperature slider reshapes the distribution; "draw again" draws fresh random numbers and the tally counts
    the answers (assets/ai4se.js)."""
    L = lambda x: x[lang]
    nodes = NT[lang]
    names = list(nodes)
    data = {"nodes": [{"cands": [[t, p] for t, p, _ in nodes[n]], "next": [names.index(x) if x else -1 for _, _, x in nodes[n]]} for n in names],
            "seed": NT_SEED, "words": {k: L(v) for k, v in dict(
                token=T("token", "Token"), dist=T("probabilities computed", "Wahrscheinlichkeiten berechnet"),
                drawn=T("drawn and appended", "gezogen und angehängt"), notTop=T("not the most likely one", "nicht das wahrscheinlichste"),
                done=T("end token drawn — the answer is complete", "End-Token gezogen — die Antwort ist fertig"),
                random=T("random number", "Zufallszahl"), lands=T("lands on", "landet auf"),
                answers=T("answers", "Antworten"), at=T("at temperature", "bei Temperatur"), empty=T("no answers yet — draw a few", "noch keine Antworten — ziehen Sie ein paar"),
                others=T("other answers", "weitere Antworten"), wrong=T("wrong city", "falsche Stadt")).items()}}
    prompt = [L(T("System: You are a helpful chatbot!", "System: Du bist ein hilfreicher Chatbot!")),
              L(T("User: What is the capital of France?", "Nutzer: Was ist die Hauptstadt von Frankreich?")),
              L(T("Assistant:", "Assistent:"))]
    esc = html.escape
    inner = f'''<div class="nt-stage">
  <div class="nt-prompt"><span class="k mono">{L(T("INPUT PROMPT", "EINGABE-PROMPT"))}</span>
    <p>{esc(prompt[0])}</p><p>{esc(prompt[1])}</p><p>{esc(prompt[2])} <span class="nt-out"></span><span class="nt-cur" aria-hidden="true">▌</span></p>
    <span class="nt-loop mono">↺ {L(T("the drawn token is appended — and generation continues with that context (usually reusing cached attention keys and values)", "das gezogene Token wird angehängt — und die Erzeugung läuft mit diesem Kontext weiter (meist mit zwischengespeicherten Attention-Keys und -Values)"))}</span></div>
  <div class="nt-model"><b>LLM</b><span class="mono">{L(T("next token", "nächstes Token"))}</span></div>
  <div class="nt-probs"><span class="k mono">{L(T("PROBABILITY OF THE NEXT TOKEN", "WAHRSCHEINLICHKEIT DES NÄCHSTEN TOKENS"))}</span><ol class="bars mono"></ol>
    <div class="nt-draw"><span class="k mono">{L(T("THE DRAW: A RANDOM NUMBER BETWEEN 0 AND 1", "DIE ZIEHUNG: EINE ZUFALLSZAHL ZWISCHEN 0 UND 1"))}</span>
      <div class="strip"><i class="mark" aria-hidden="true"></i></div><span class="nt-r mono"></span></div></div>
</div>
<div class="nt-tally"><div class="nt-tally-head"><span class="k mono">{L(T("ANSWERS SO FAR", "BISHERIGE ANTWORTEN"))}</span>
  <span class="chips"><button type="button" class="nt-again first" aria-pressed="false">{L(T("draw again", "neu ziehen"))}</button><button type="button" class="nt-ten" aria-pressed="false">{L(T("draw 10 ×", "10 × ziehen"))}</button></span></div>
  <ol class="nt-list mono" aria-live="polite"></ol></div>
{controls(lang, temperature=True)}'''
    return demo("nt", data, inner, T(
        "The model computes a probability for every candidate, a random number picks one, the token is appended, and generation continues with that context (usually reusing cached attention keys and values) — until the end token is drawn. Draw a few answers, then move the temperature: at 0.1 the answer hardly ever changes; at 1.0 the wording varies; at 2.0 about one answer in five names the wrong city.",
        "Das Modell berechnet für jeden Kandidaten eine Wahrscheinlichkeit, eine Zufallszahl wählt einen aus, das Token wird angehängt, und die Erzeugung läuft mit diesem Kontext weiter (meist mit zwischengespeicherten Attention-Keys und -Values) — bis das End-Token gezogen wird. Ziehen Sie ein paar Antworten und verschieben Sie dann die Temperatur: Bei 0,1 ändert sich die Antwort fast nie; bei 1,0 wechselt die Formulierung; bei 2,0 nennt etwa jede fünfte Antwort die falsche Stadt."), lang,
        source=src("illustrative", note=T("made-up probabilities; only the listed candidates can be drawn (top-k)", "ausgedachte Wahrscheinlichkeiten; gezogen wird nur unter den gezeigten Kandidaten (Top-k)")))


EMB_WORDS = [(T("king", "König"), .95, .72), (T("queen", "Königin"), -.37, .87), (T("man", "Mann"), .70, -.45),
             (T("woman", "Frau"), -.62, -.30), (T("princess", "Prinzessin"), -.62, 1.02)]
assert all(abs((EMB_WORDS[0][i] - EMB_WORDS[2][i]) - (EMB_WORDS[1][i] - EMB_WORDS[3][i])) < 1e-9 for i in (1, 2))   # king − man = queen − woman


def dia_embeddings(lang):
    """Slides 55 / 56: word embeddings in two dimensions, as points. Accent only on the two equal steps
    man → king and woman → queen. The vectors as numbers sit beside the plot (HTML, so it stacks on phones)."""
    L = lambda x: x[lang]
    cx, cy, u = 186, 168, 104
    P = {L(w): (cx + x * u, cy - y * u) for w, x, y in EMB_WORDS}
    king, queen, man, woman, princess = (L(w) for w, *_ in EMB_WORDS)
    # label offsets (dx, dy, anchor), chosen so that no label sits on a step arrow
    off = {king: (10, 4, "start"), queen: (10, 14, "start"), man: (10, 14, "start"), woman: (-10, 14, "end"), princess: (-10, -6, "end")}
    step = lambda a, b: (f'<path class="ln hl sw-em" d="M{P[a][0]:.1f} {P[a][1]:.1f}L{P[b][0]:.1f} {P[b][1] + 8:.1f}" marker-end="url(#emaa)"/>')
    pts = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" class="{"dot" if w in (king, queen) else "emb-pt"}"/>'
                  f'<text class="halo{" t" if w in (king, queen) else ""}" x="{x + off[w][0]:.1f}" y="{y + off[w][1]:.1f}" text-anchor="{off[w][2]}">{w}</text>' for w, (x, y) in P.items())
    mx, my = (P[man][0] + P[king][0]) / 2, (P[man][1] + P[king][1]) / 2
    svg = f'''<svg class="dia emb" viewBox="0 0 360 300" role="img" aria-label="{L(T("Five words as points in two dimensions. The step from man to king is the same as from woman to queen; princess lies close to queen.", "Fünf Wörter als Punkte in zwei Dimensionen. Der Schritt von Mann zu König ist derselbe wie von Frau zu Königin; Prinzessin liegt nahe bei Königin."))}">
  {_arrow_defs("ema")}
  <path class="ln dash-guide sw-hair" d="M{cx - 170} {cy}H{cx + 170}M{cx} {cy + 120}V{cy - 160}"/>
  <text class="s" x="{cx + 170}" y="{cy + 16}" text-anchor="end">{L(T("dimension 1", "Dimension 1"))}</text>
  <text class="s" x="{cx + 8}" y="{cy - 150}">{L(T("dimension 2", "Dimension 2"))}</text>
  {step(man, king)}{step(woman, queen)}
  <text class="a halo" x="{mx + 8:.0f}" y="{my + 4:.0f}">+ {L(T("royal", "königlich"))}</text>
  <text class="a halo" x="{(P[woman][0] + P[queen][0]) / 2 - 8:.0f}" y="{(P[woman][1] + P[queen][1]) / 2 + 4:.0f}" text-anchor="end">+ {L(T("royal", "königlich"))}</text>
  {pts}
</svg>'''
    num = (lambda v: f"{v:+.2f}".replace(".", ",")) if lang == "de" else (lambda v: f"{v:+.2f}")
    sep = "; " if lang == "de" else ", "
    rows = "".join(f'<tr{" class=\"hl\"" if k < 2 else ""}><td>{L(w)}</td><td class="n">[ {num(x)}{sep}{num(y)} ]</td></tr>' for k, (w, x, y) in enumerate(EMB_WORDS))
    table = f'<table class="emb-tbl mono"><caption class="k">{L(T("EACH WORD IS A LIST OF NUMBERS", "JEDES WORT IST EINE ZAHLENLISTE"))}</caption>{rows}</table>'
    from article_common import source_line
    cap = T("Meaning sits in directions, not in the axes: the step from “man” to “king” is the same as from “woman” to “queen” — king − man + woman ≈ queen. Real models use hundreds to thousands of dimensions instead of two.",
            "Die Bedeutung steckt in Richtungen, nicht in den Achsen: Der Schritt von „Mann“ zu „König“ ist derselbe wie von „Frau“ zu „Königin“ — König − Mann + Frau ≈ Königin. Echte Modelle nutzen Hunderte bis Tausende Dimensionen statt zwei.")
    return (f'<figure class="media art-fig emb-fig"><div class="emb-row">{table}<div class="emb-plot">{svg}</div></div>'
            f'<figcaption class="mono">{cap[lang]}{source_line(src("illustrative"), lang)}</figcaption></figure>')


# the five pixels the small network reads (column, row in the 16 × 16 image)
NN_PIXELS = [(6, 5), (4, 3), (12, 4), (7, 11), (9, 13)]
NN_IN = [36, 68, 100, 132, 164]          # y of the input, hidden and output neurons
NN_HID = [52, 84, 116, 148]
NN_OUT = [76, 124]
NN_X = (330, 420, 510)
NN_PANEL = (300, 250)                    # top left of the "one neuron" panel (368 × 210); ai4se.js draws into it


def dia_neural_net(lang, A):
    """Slides 5–9: a picture becomes pixels, pixels feed a network, the network says dog or cat. Below it, one
    neuron in detail — the one the visitor points at (assets/ai4se.js). Three groups (source, network, panel) that
    ai4se.js stacks on phones: the network is 368 units wide, so each part fits a phone at full size."""
    L = lambda x: x[lang]
    xi, xh, xo = NN_X
    cell = 7.5
    px = "".join(f'<rect class="nn-px" data-i="{k}" x="{140 + c * cell}" y="{40 + r * cell}" width="{cell}" height="{cell}"/>'
                 for k, (c, r) in enumerate(NN_PIXELS))
    feed = "".join(f'<path class="nn-feed" data-i="{k}" d="M{140 + (c + .5) * cell:.1f} {40 + (r + .5) * cell:.1f}L{xi - 30} {y}"/>'
                   for k, ((c, r), y) in enumerate(zip(NN_PIXELS, NN_IN)))
    edges = "".join(f'<path class="nn-e" data-l="1" data-i="{a}" data-j="{b}" d="M{xi} {ya}L{xh} {yb}"/>' for a, ya in enumerate(NN_IN) for b, yb in enumerate(NN_HID))
    edges += "".join(f'<path class="nn-e" data-l="2" data-i="{a}" data-j="{b}" d="M{xh} {ya}L{xo} {yb}"/>' for a, ya in enumerate(NN_HID) for b, yb in enumerate(NN_OUT))

    def node(l, i, x, y, r, label, name):
        return (f'<g class="nn-n" data-l="{l}" data-i="{i}" tabindex="0" role="button" aria-label="{name}">'
                f'<circle class="nn-hit" cx="{x}" cy="{y}" r="14"/><circle class="box" cx="{x}" cy="{y}" r="{r}"/><circle class="nn-act" cx="{x}" cy="{y}" r="{r}"/>'
                f'<text x="{x}" y="{y + 3.5}" text-anchor="middle" class="s nn-lbl">{label}</text></g>')
    neuron = L(T("neuron", "Neuron"))
    nodes = "".join(node(0, k, xi, y, 8, "", f"{L(T('pixel', 'Pixel'))} x{k + 1}") + f'<text class="nn-v" data-i="{k}" x="{xi - 14}" y="{y + 4}" text-anchor="end"></text>' for k, y in enumerate(NN_IN))
    nodes += "".join(node(1, k, xh, y, 11, f"h{k + 1}", f"{neuron} h{k + 1}") for k, y in enumerate(NN_HID))
    outs = [T("dog", "Hund"), T("cat", "Katze")]
    nodes += "".join(node(2, k, xo, y, 12, "", f"{neuron} {L(o)}") for k, (y, o) in enumerate(zip(NN_OUT, outs)))
    labels = "".join(f'<text x="{xo + 20}" y="{y + 4}" class="t">{L(o)}</text>'
                     f'<rect class="nn-track" x="{xo + 66}" y="{y - 6}" width="56" height="12"/><rect class="nn-bar" data-i="{k}" x="{xo + 66}" y="{y - 6}" width="{[50, 6][k]}" height="12"/>'
                     f'<text class="nn-pv s" data-i="{k}" x="{xo + 128}" y="{y + 4}">{["0.91", "0.09"][k]}</text>' for k, (y, o) in enumerate(zip(NN_OUT, outs)))
    labels += (f'<text x="{xi}" y="196" text-anchor="middle" class="s">{L(T("inputs", "Eingaben"))}</text>'
               f'<text x="{xh}" y="196" text-anchor="middle" class="s">{L(T("hidden", "verdeckt"))}</text>'
               f'<text x="{xo}" y="196" text-anchor="middle" class="s">{L(T("output", "Ausgabe"))}</text>')
    x0, y0 = NN_PANEL
    aria = L(T("A photo of a dog is reduced to pixels; five pixel values feed a small neural network whose output neuron for dog wins. Below: the neuron you point at, with its inputs, weights, weighted sum and activation.",
               "Ein Hundefoto wird zu Pixeln; fünf Pixelwerte speisen ein kleines neuronales Netz, dessen Ausgabeneuron für Hund gewinnt. Darunter: das Neuron, auf das man zeigt, mit seinen Eingaben, Gewichten, gewichteter Summe und Aktivierung."))
    svg = f'''<svg class="dia nn" viewBox="0 0 784 470" data-wide="0 0 784 470" role="group" aria-label="{aria}">
  {_arrow_defs("nna")}
  <g class="nn-src">
    <image href="{A}assets/ai4se/dog.jpg" x="0" y="40" width="120" height="120"/>
    <image href="{A}assets/ai4se/dog-pixels.png" x="140" y="40" width="120" height="120" style="image-rendering:pixelated"/>
    <text x="60" y="178" text-anchor="middle" class="s">{L(T("photo", "Foto"))}</text>
    <text x="200" y="178" text-anchor="middle" class="s">{L(T("16 × 16 pixels", "16 × 16 Pixel"))}</text>
    {px}
  </g>
  <g class="nn-feeds">{feed}</g>
  <path class="nn-lead" d="M{xo} {NN_OUT[0] + 12}V{y0}"/>
  <g class="nn-net">{edges}{nodes}{labels}</g>
  <g class="nn-cal" data-x="{x0}" data-y="{y0}">
    <rect class="zone" x="{x0}" y="{y0}" width="368" height="210" rx="4"/>
    <text x="{x0 + 12}" y="{y0 + 20}" class="s nn-title on-tile">{L(T("ONE NEURON", "EIN NEURON"))}</text>
    <g class="nn-panel"></g>
  </g>
</svg>'''
    data = {"px": f"{A}assets/ai4se/dog-pixels.png", "pixels": NN_PIXELS, "panel": NN_PANEL,
            "words": {k: L(v) for k, v in dict(
                one=T("ONE NEURON", "EIN NEURON"), inputs=T("input", "Eingabe"), weights=T("× weight", "× Gewicht"),
                sum=T("sum", "Summe"), out=T("output", "Ausgabe"),
                relu=T("negative → 0", "negativ → 0"), share=T("share of both outputs", "Anteil an beiden Ausgaben"),
                silent=T("stays silent", "bleibt still"), dog=T("dog", "Hund"), cat=T("cat", "Katze")).items()}}
    hint = L(T("Point at a neuron (or tap it) to see its calculation.", "Zeigen Sie auf ein Neuron (oder tippen Sie es an), um seine Rechnung zu sehen."))
    ctrl = f'<div class="demo-ctrl mono"><button type="button" class="play replay" aria-label="{L(T("replay the forward pass", "Durchlauf noch einmal abspielen"))}">↺</button><span>{L(T("replay the forward pass", "Durchlauf noch einmal abspielen"))}</span></div>'
    return demo("nn", data, f'<div class="nn-wrap">{svg}</div>{ctrl}',
                T(f"Every pixel value is an input, every connection a weight; each neuron adds up its weighted inputs, and the stronger output wins. {hint}",
                  f"Jeder Pixelwert ist eine Eingabe, jede Verbindung ein Gewicht; jedes Neuron summiert seine gewichteten Eingaben, und die stärkere Ausgabe gewinnt. {hint}"), lang,
                source=src("illustrative", note=T("a toy: five pixels and made-up weights; real image networks read every pixel and have millions of weights",
                                                  "ein Spielzeug: fünf Pixel und ausgedachte Gewichte; echte Bildnetze lesen jeden Pixel und haben Millionen Gewichte")))


# The Winograd pair: one word decides what "it" refers to. Attention of the deciding word to the earlier words
# (illustrative numbers: real models spread this over many heads and layers).
WG = {
    "en": {"words": ["The", "trophy", "doesn’t", "fit", "into", "the", "suitcase", "because", "it", "is", "too", "{}."],
           "adj": ["big", "small"], "who": ["the trophy", "the suitcase"], "src": 11, "nouns": [1, 6]},
    "de": {"words": ["Der", "Pokal", "passt", "nicht", "in", "den", "Koffer,", "weil", "er", "zu", "{}", "ist."],
           "adj": ["groß", "klein"], "who": ["der Pokal", "der Koffer"], "src": 10, "nouns": [1, 6]},
}


def _wg_weights(n_before, nouns, it, pick):
    """Illustrative attention of the deciding word to the n_before earlier words: most of it to the referent."""
    w = [.02] * n_before
    w[nouns[pick]], w[nouns[1 - pick]], w[it] = .52, .12, .14
    rest = 1 - (.52 + .12 + .14)
    small = [k for k in range(n_before) if k not in (nouns[0], nouns[1], it)]
    for k in small:
        w[k] = rest / len(small)
    assert abs(sum(w) - 1) < 1e-9
    return [round(v, 3) for v in w]


def dia_attention(lang):
    """A Winograd pair as a small demo: chips switch big / small; the bars show how strongly the deciding word
    attends to each earlier word, and the referent flips (assets/ai4se.js)."""
    L = lambda x: x[lang]
    d = WG[lang]
    it = d["words"].index("it" if lang == "en" else "er")
    n = d["src"]
    data = {"words": d["words"], "adj": d["adj"], "who": d["who"], "src": n, "it": it,
            "w": [_wg_weights(n, d["nouns"], it, k) for k in (0, 1)],
            "words2": {k: L(v) for k, v in dict(means=T("interpretation: “it” means", "Deutung: „er“ meint"), reads=T("the word", "das Wort"),
                                                  looks=T("looks back at", "schaut zurück auf")).items()}}
    chips = "".join(f'<button type="button" aria-pressed="{str(k == 0).lower()}"{" class=\"first\"" if k == 0 else ""}>{L(T("too ", "zu "))}{a}</button>' for k, a in enumerate(d["adj"]))
    inner = (f'<div class="wg-head"><span class="k mono">{L(T("THE LAST WORD DECIDES", "DAS EINE WORT ENTSCHEIDET"))}</span><span class="chips">{chips}</span></div>'
             f'<p class="wg-sent" aria-live="polite"></p><p class="wg-say mono"></p>')
    return demo("wg", data, inner, T(
        "Change one word and the reference flips: with “big”, “it” is the trophy; with “small”, the suitcase. The bars are hand-made: one possible attention pattern from the later adjective back to earlier tokens. They are not model measurements or a causal explanation of the interpretation. The pronoun itself cannot attend forward to the adjective in a causal decoder.",
        "Ein Wort ändern, und der Bezug kippt: Bei „groß“ ist „er“ der Pokal, bei „klein“ der Koffer. Die Balken sind von Hand gesetzt: ein mögliches Attention-Muster vom späteren Adjektiv zurück zu früheren Tokens. Sie sind keine Modellmessungen und keine kausale Erklärung der Interpretation. Das Pronomen selbst kann in einem kausalen Decoder nicht auf das spätere Adjektiv vorausblicken."), lang,
        source=src("after", _RK["levesque"], note=T('weights illustrative; <a href="https://aclanthology.org/N19-1357/">attention is not explanation</a>', 'Gewichte illustrativ; <a href="https://aclanthology.org/N19-1357/">Attention ist keine Erklärung</a>')))


def dia_transformer_simple(lang):
    """The transformer in three plain steps (HTML, so it stacks on phones)."""
    L = lambda x: x[lang]
    steps = [(T("text → numbers", "Text → Zahlen"), T("every token becomes an embedding", "jedes Token wird ein Embedding")),
             (T("tokens look at each other", "Tokens schauen einander an"), T("attention, 96 layers deep in GPT-3", "Attention, bei GPT-3 96 Schichten tief")),
             (T("score every next token", "jedes nächste Token bewerten"), T("one probability per token", "eine Wahrscheinlichkeit pro Token"))]
    io = lambda t: f'<span class="tf-io mono">{L(t)}</span>'
    boxes = "".join(f'<li class="tf-box{" hl" if k == 1 else ""}"><b>{L(a)}</b><span class="mono">{L(b)}</span></li>' for k, (a, b) in enumerate(steps))
    from article_common import source_line
    cap = T("A GPT in three steps. The middle one is the transformer’s idea; the full stack is in the box below.",
            "Ein GPT in drei Schritten. Der mittlere ist die Idee des Transformers; den vollständigen Stapel zeigt der Kasten unten.")
    return (f'<figure class="media art-fig"><div class="tf-row">{io(T("the text so far", "der bisherige Text"))}<ol class="tf">{boxes}</ol>{io(T("the next token", "das nächste Token"))}</div>'
            f'<figcaption class="mono">{cap[lang]}{source_line(src("after", _RK["vaswani"], _RK["brown"]), lang)}</figcaption></figure>')


def dia_transformer(lang):
    """Slides 100–106: the decoder stack of a GPT, simplified, with what each block does (in the curious box)."""
    L = lambda x: x[lang]
    m = 'marker-end="url(#tra)"'
    stack = [
        (T("Token embedding", "Token-Embedding"), T("the text so far, as vectors", "der bisherige Text als Vektoren"), ""),
        (T("+ position", "+ Position"), T("where in the text each token is", "wo im Text jedes Token steht"), ""),
        ("Masked multi-head attention", T("each token looks at the earlier ones", "jedes Token schaut auf die früheren"), "hl"),
        ("Feed forward", T("a plain neural network per token", "ein einfaches neuronales Netz pro Token"), ""),
        ("Linear · Softmax", T("a probability for every next token", "eine Wahrscheinlichkeit pro möglichem Token"), ""),
    ]
    # one narrow column (viewBox 380, never stretched): each block carries its name and, below it, what it does,
    # so the figure keeps 10 px labels on a phone instead of shrinking a wide drawing
    parts = []
    for k, (name, what, cls) in enumerate(reversed(stack)):
        y = 16 + k * 60
        parts.append(f'<rect class="box {cls}" x="78" y="{y}" width="290" height="44" rx="3"/>'
                     f'<text class="t" x="223" y="{y + 19}" text-anchor="middle">{L(name) if isinstance(name, dict) else name}</text>'
                     f'<text class="s" x="223" y="{y + 35}" text-anchor="middle">{L(what)}</text>')
        if k < len(stack) - 1:
            parts.append(f'<path class="ln" d="M223 {y + 60}V{y + 46}" {m}/>')
    parts.append('<rect class="zone line" x="70" y="70" width="306" height="116" rx="4"/>')
    parts.append(f'<text x="62" y="122" text-anchor="end" class="t">× N</text><text x="62" y="140" text-anchor="end">{L(T("layers", "Schichten"))}</text>')
    parts.append('<text x="62" y="156" text-anchor="end">GPT-3: 96</text>')
    svg = f'<svg class="dia tf-stack" viewBox="0 0 380 312" style="max-width:380px" role="img" aria-label="{L(T("Simplified transformer decoder: token embeddings with positions pass through attention and feed-forward layers, repeated N times; a linear layer and softmax produce next-token probabilities", "Vereinfachter Transformer-Decoder: Token-Embeddings mit Positionen durchlaufen Attention- und Feed-Forward-Schichten, N-mal wiederholt; eine lineare Schicht und Softmax liefern Wahrscheinlichkeiten für das nächste Token"))}">{_arrow_defs("tra")}{"".join(parts)}</svg>'
    return fig(svg, T("The core of a GPT, read from bottom to top.", "Der Kern eines GPT, von unten nach oben gelesen."), lang, scroll=False, source=src("after", _RK["vaswani"]))


# =====================================================================
# 02 · Around the model
# =====================================================================

def dia_ai_terms(lang):
    """Slide 4: AI as an umbrella term — nested fields in grey, accent only on the LLMs; the definitions beside
    it as a list (HTML, so it stacks on phones)."""
    L = lambda x: x[lang]
    levels = [
        (T("Artificial intelligence", "Künstliche Intelligenz"), T("research on machines that act and react intelligently", "Forschung an Maschinen, die intelligent handeln und reagieren")),
        (T("Machine learning", "Machine Learning"), T("algorithms that learn from data and generalise to unseen data", "Algorithmen, die aus Daten lernen und auf Ungesehenes verallgemeinern")),
        (T("Deep learning", "Deep Learning"), T("machine learning with neural networks", "Machine Learning mit neuronalen Netzen")),
        (T("Generative AI", "Generative KI"), T("creates new content from learned patterns", "erzeugt neue Inhalte aus gelernten Mustern")),
        (T("LLMs", "LLMs"), T("large language models: read and write text", "große Sprachmodelle: lesen und schreiben Text")),
    ]
    svg = f'''<svg class="dia" viewBox="0 0 360 320" role="img" aria-label="{L(T("AI contains machine learning and deep learning; generative AI is a cross-cutting capability. LLMs combine deep learning and generation. Products use models.", "KI umfasst Machine Learning und Deep Learning; generative KI ist eine übergreifende Fähigkeit. LLMs verbinden Deep Learning und Generierung. Produkte nutzen Modelle."))}">
      <rect class="zone" x="4" y="4" width="352" height="252" rx="6"/>
      <text class="t" x="18" y="26">{L(T("Artificial intelligence", "Künstliche Intelligenz"))}</text>
      <rect class="box" x="18" y="40" width="324" height="152" rx="3"/>
      <text class="t" x="30" y="62">Machine learning</text>
      <rect class="box" x="30" y="76" width="300" height="102" rx="3"/>
      <text class="t" x="42" y="98">Deep learning</text>
      {box(42, 112, 276, 52, "LLMs", L(T("deep + generative models", "tiefe + generative Modelle")), cls="box hl")}
      <text class="t" x="18" y="216">{L(T("Generative AI: a capability", "Generative KI: eine Fähigkeit"))}</text>
      <text class="s" x="18" y="238">{L(T("also includes non-deep methods", "auch mit nicht-tiefen Verfahren"))}</text>
      <text class="s" x="18" y="280">{L(T("Models: e.g. GPT, Llama", "Modelle: z. B. GPT, Llama"))}</text>
      <text class="s" x="18" y="302">{L(T("Products: ChatGPT, Copilot", "Produkte: ChatGPT, Copilot"))}</text>
    </svg>'''
    dl = "".join(f'<dt class="mono{" a" if k == len(levels) - 1 else ""}">{L(n)}</dt><dd>{L(d)}</dd>' for k, (n, d) in enumerate(levels))
    from article_common import source_line
    cap = T("AI is the umbrella; generative AI describes content production across methods. LLMs are a deep-learning-based generative class. Products add software around models.",
            "KI ist der Oberbegriff; generative KI beschreibt Inhaltserzeugung über verschiedene Verfahren. LLMs sind eine generative Deep-Learning-Klasse. Produkte ergänzen Software um Modelle.")
    return (f'<figure class="media art-fig umb-fig"><div class="umb-row"><div class="umb-art">{svg}</div><dl class="umb-dl">{dl}</dl></div>'
            f'<figcaption class="mono">{cap[lang]}{source_line(None, lang)}</figcaption></figure>')


def glossary(lang):
    """The words around the model that chapter 01 did not need yet."""
    L = lambda x: x[lang]
    terms = [
        ("Prompt", T("Everything the model gets as input: the instructions (system prompt), the conversation so far, attached documents.",
                     "Alles, was das Modell als Eingabe bekommt: die Anweisungen (System-Prompt), das bisherige Gespräch, angehängte Dokumente.")),
        (T("Context window", "Kontextfenster"), T("How many tokens the model can take in at once. Whatever does not fit, it does not see.",
                                                "Wie viele Tokens das Modell auf einmal aufnehmen kann. Was nicht hineinpasst, sieht es nicht.")),
        ("Few-shot", T("Examples of questions and answers in the prompt that show the model what is wanted — without training it again.",
                       "Beispiele für Fragen und Antworten im Prompt, die dem Modell zeigen, was gewünscht ist — ohne es neu zu trainieren.")),
        ("Fine-tuning", T("Training an existing model further on one’s own data. Needs good data and hardware, and the result stays fixed until the next training.",
                          "Ein bestehendes Modell auf eigenen Daten weitertrainieren. Braucht gute Daten und Hardware, und das Ergebnis steht fest bis zum nächsten Training.")),
    ]
    return '<dl class="gloss">' + "".join(f'<dt class="mono">{L(k) if isinstance(k, dict) else k}</dt><dd>{L(v)}</dd>' for k, v in terms) + "</dl>"


def dia_rag(lang):
    """Slide 59: retrieval-augmented generation, numbered 1–5 in the order of a question. The question text (not
    its vector) goes into the prompt; the index is built beforehand. 360 wide: fits a phone as it is."""
    L = lambda x: x[lang]
    m, ma = 'marker-end="url(#rga)"', 'marker-end="url(#rgaa)"'
    num = lambda x, y, n: f'<text x="{x}" y="{y}" class="s a">0{n}</text>'
    svg = f'''<svg class="dia" viewBox="0 0 360 352" role="img" aria-label="{L(T("RAG: 1 the question is 2 turned into a vector, 3 the index returns the nearest chunks, 4 the question text and the chunks form the prompt, 5 the LLM answers with sources. The index of document chunks is built beforehand.", "RAG: 1 Die Frage wird 2 in einen Vektor übersetzt, 3 der Index liefert die nächstgelegenen Abschnitte, 4 Fragetext und Abschnitte bilden den Prompt, 5 das LLM antwortet mit Quellen. Der Index der Dokumentabschnitte wird vorher gebaut."))}">
  {_arrow_defs("rga")}
  {num(0, 12, 1)}{box(0, 18, 150, 50, L(T("Question", "Frage")), L(T("from the user", "vom Nutzer")))}
  <path class="ln" d="M150 43H206" {m}/>
  {num(210, 12, 2)}{box(210, 18, 150, 50, "Embedding", L(T("question → vector", "Frage → Vektor")))}
  <path class="ln" d="M285 68V100" {m}/>
  {num(210, 98, 3)}{box(210, 104, 150, 50, L(T("Search", "Suche")), L(T("nearest chunks", "nächste Abschnitte")))}
  <path class="ln dash-opt" d="M285 206V158" {m}/>
  {box(210, 210, 150, 62, L(T("Index", "Index")), L(T("built beforehand:", "vorher gebaut:")), cls="box dashbox", sub2=L(T("chunks → vectors", "Abschnitte → Vektoren")))}
  <path class="ln" d="M210 129H120V200" {m}/>
  <text class="s halo" x="165" y="122" text-anchor="middle">{L(T("chunks", "Abschnitte"))}</text>
  <path class="ln" d="M40 68V200" {m}/>
  <text class="s halo" x="46" y="140">{L(T("the text", "der Text"))}</text>
  {num(0, 198, 4)}{box(0, 204, 150, 50, "Prompt", L(T("question + chunks", "Frage + Abschnitte")))}
  <path class="ln" d="M75 254V286" {m}/>
  {num(0, 284, 5)}{box(0, 290, 150, 50, "LLM", L(T("answers", "antwortet")), cls="box hl")}
  <path class="ln hl" d="M150 315H206" {ma}/>
  {box(210, 290, 150, 50, L(T("Answer", "Antwort")), L(T("sources requested", "Quellen angefragt")))}
</svg>'''
    return side_fig(svg, 360, T("Retrieval-augmented generation: search first, then hand the LLM the question together with what was found. The vector is only used for the search; the prompt gets the text.",
                                "Retrieval-Augmented Generation: erst suchen, dann dem LLM die Frage zusammen mit den Fundstellen geben. Der Vektor dient nur der Suche; in den Prompt kommt der Text."),
                    lang, source=src("after", _RK["lewis"]))


# The agent trace: "fix the failing test" in the library code of part 1 (fictional, but a typical run).
AG_STEPS = [  # (action, tool call, observation)
    (T("run the tests", "Tests ausführen"), "pytest", T("1 failed: test_loan_due_date", "1 fehlgeschlagen: test_loan_due_date")),
    (T("read the test", "den Test lesen"), "tests/test_loan.py", T("expects: due = lent + 14 days", "erwartet: fällig = verliehen + 14 Tage")),
    (T("read the code", "den Code lesen"), "src/loan.py", T("LOAN_DAYS = 7", "LOAN_DAYS = 7")),
    (T("edit the code", "den Code ändern"), "LOAN_DAYS = 14", T("file saved", "Datei gespeichert")),
    (T("run the tests", "Tests ausführen"), "pytest", T("12 passed", "12 bestanden")),
]


def dia_agent(lang):
    """An agent as a stepped trace: the loop on the left lights up Act or Observe, the trace on the right grows
    (assets/ai4se.js, SiteDemo.stepper)."""
    L = lambda x: x[lang]
    m, ma = 'marker-end="url(#aga)"', 'marker-end="url(#agaa)"'
    svg = f'''<svg class="dia ag-loop" viewBox="0 0 360 214" role="img" aria-label="{L(T("The agent loop: a goal goes to the LLM, which decides the next step; a tool carries it out; the result goes back to the LLM; when the goal is reached, the loop ends.", "Die Agenten-Schleife: Ein Ziel geht an das LLM, das den nächsten Schritt wählt; ein Werkzeug führt ihn aus; das Ergebnis geht zurück an das LLM; ist das Ziel erreicht, endet die Schleife."))}">
  {_arrow_defs("aga")}
  <text x="20" y="18" class="s">{L(T("GOAL", "ZIEL"))}</text><text x="20" y="34">{L(T("“fix the failing test”", "„behebe den roten Test“"))}</text>
  <path class="ln" d="M60 42V76" {m}/>
  <g class="ag-n" data-n="llm">{box(20, 80, 130, 46, "LLM", L(T("picks a step", "wählt den Schritt")), cls="box")}</g>
  <path class="ln ag-e" data-e="act" d="M150 96H180V33H206" {m}/>
  <g class="ag-n" data-n="act">{box(210, 10, 140, 46, L(T("Act", "Handeln")), L(T("a tool runs", "ein Werkzeug läuft")))}</g>
  <path class="ln ag-e" data-e="obs" d="M280 56V146" {m}/>
  <g class="ag-n" data-n="obs">{box(210, 150, 140, 46, L(T("Observe", "Beobachten")), L(T("read the result", "Ergebnis lesen")))}</g>
  <path class="ln ag-e" data-e="back" d="M210 173H115V130" {m}/>
  <text x="214" y="118" class="s a">↻ {L(T("loop", "Schleife"))}</text>
  <path class="ln ag-e" data-e="done" d="M50 126V186" {m}/>
  <g class="ag-n" data-n="done"><text x="50" y="204" text-anchor="middle" class="t">{L(T("done", "fertig"))} ✓</text></g>
</svg>'''
    rows = "".join(f'<li><span class="ag-act"><b>{L(a)}</b> <code>{html.escape(c)}</code></span><span class="ag-obs">→ {L(o)}</span></li>' for a, c, o in AG_STEPS)
    data = {"n": len(AG_STEPS), "words": {k: L(v) for k, v in dict(
        goal=T("The goal arrives; the LLM decides what to do first.", "Das Ziel kommt an; das LLM entscheidet, was zuerst zu tun ist."),
        act=T("Act: the LLM calls a tool", "Handeln: Das LLM ruft ein Werkzeug auf"), obs=T("Observe: the result goes back to the LLM", "Beobachten: Das Ergebnis geht zurück an das LLM"),
        done=T("All tests pass — the goal is reached, the loop ends.", "Alle Tests grün — das Ziel ist erreicht, die Schleife endet."),
        step=T("step", "Schritt"), of=T("of", "von")).items()}}
    inner = (f'<div class="ag-stage"><div class="ag-art">{svg}</div><div class="ag-side"><span class="k mono">{L(T("THE TRACE", "DER VERLAUF"))}</span>'
             f'<ol class="ag-trace mono">{rows}</ol><p class="ag-say mono" aria-live="polite"></p></div></div>{controls(lang)}')
    return demo("ag", data, inner, T(
        "An agent is a loop: the LLM chooses a step, a tool carries it out, the result goes back to the LLM. Who decides the next step is what separates an agent from a fixed workflow.",
        "Ein Agent ist eine Schleife: Das LLM wählt einen Schritt, ein Werkzeug führt ihn aus, das Ergebnis geht zurück an das LLM. Wer den nächsten Schritt bestimmt, unterscheidet einen Agenten von einem festen Workflow."), lang,
        source=src("illustrative", note=T("a typical run, shortened", "ein typischer Lauf, gekürzt")))


def dia_harness(lang):
    """Responsibility boundaries, not deployment boundaries. Separate phone geometry keeps type at 1:1."""
    L = lambda x: html.escape(x[lang], quote=True)
    def icon(kind, x, y):
        # Small, consistent line glyphs; labels carry the meaning without relying on icons.
        paths = {
            "context": '<path d="M4 1H13V12H4Z M1 4V15H10"/>',
            "control": '<path d="M2 3H8V13H14 M8 3H14 M11 0L14 3L11 6 M11 10L14 13L11 16"/>',
            "tool": '<rect x="1" y="2" width="14" height="12" rx="1"/><path d="M4 6L7 8L4 10 M9 11H12"/>',
            "model": '<rect x="3" y="3" width="10" height="10" rx="1"/><path d="M6 0V3 M10 0V3 M6 13V16 M10 13V16 M0 6H3 M0 10H3 M13 6H16 M13 10H16"/>',
        }
        return f'<g class="harness-icon" transform="translate({x} {y})" aria-hidden="true">{paths[kind]}</g>'
    def drawing(phone):
        w, hx, hw, mx, mw = (358, 40, 180, 278, 68) if phone else (640, 56, 264, 432, 176)
        end, tx, cx = hx + hw, hx + 16, mx + mw / 2
        ident = "hn-phone" if phone else "hn-wide"
        marker = f'marker-end="url(#{ident})"'
        # One marker per visible variant; a hidden SVG must never own the other's arrowheads.
        defs = f'<defs><marker id="{ident}" viewBox="0 0 6 6" refX="5" refY="3" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L6 3L0 6" fill="currentColor"/></marker></defs>'
        rows = [
            (150, "context", T("Context & state", "Kontext & Zustand"), T("rules · history", "Regeln · Verlauf"), T("memory · tool definitions", "Speicher · Tool-Definitionen") if not phone else T("memory · tools", "Speicher · Werkzeuge")),
            (230, "control", T("Turn control", "Ablaufsteuerung"), T("continue · stop · ask", "weiter · Ende · fragen"), T("limits · retries · log", "Limits · Versuche · Log")),
            (310, "tool", T("Tool execution", "Werkzeugausführung"), T("permissions · checks", "Rechte · Prüfungen"), T("run · return results", "ausführen · Ergebnis")),
        ]
        ruled = "".join(icon(kind, tx, y + 3) + f'<text class="t" x="{tx + 24}" y="{y + 16}">{L(title)}</text><text x="{tx}" y="{y + 38}">{L(a)}</text><text x="{tx}" y="{y + 54}">{L(b)}</text>' for y, kind, title, a, b in rows)
        model = (f'<rect class="box hl" x="{mx}" y="150" width="{mw}" height="144" rx="3"/>'
                 + icon("model", cx - 8, 180)
                 + f'<text class="t" text-anchor="middle" x="{cx}" y="220">{L(T("Model", "Modell"))}</text>'
                 + f'<text text-anchor="middle" x="{cx}" y="242">LLM</text>'
                 + f'<text class="s" text-anchor="middle" x="{cx}" y="278">{L(T("proposal", "Vorschlag") if phone else T("proposes", "schlägt vor"))}</text>')
        tools_x = end - 32
        svg = f'''<svg class="dia harness-{'tall' if phone else 'wide'}" viewBox="0 0 {w} 524" role="img" aria-labelledby="{ident}-title {ident}-desc">
          <title id="{ident}-title">{L(T("Model, harness and agent", "Modell, Harness und Agent"))}</title>
          <desc id="{ident}-desc">{L(T("The agent combines model and harness. The harness assembles context for the model, handles its response and executes authorized tool calls. Tool results return as context for the next turn. Tools and the environment are shown separately.", "Der Agent verbindet Modell und Harness. Der Harness stellt Kontext für das Modell zusammen, verarbeitet dessen Ausgabe und führt erlaubte Werkzeugaufrufe aus. Ergebnisse fließen als Kontext in den nächsten Schritt. Werkzeuge und Umgebung sind getrennt dargestellt."))}</desc>
          {defs}
          {box(hx + (hw - 184) / 2, 0, 184, 40, L(T("You: set the goal", "Sie: das Ziel setzen")))}
          <rect class="zone" x="0" y="64" width="{w}" height="348" rx="4"/>
          <path class="ln" d="M{hx + hw / 2} 40V62" {marker}/>
          <text class="harness-head" x="{hx}" y="86">{L(T("AGENT = MODEL + HARNESS", "AGENT = MODELL + HARNESS"))}</text>
          <rect class="box" x="{hx}" y="106" width="{hw}" height="284" rx="3"/>
          <text class="t" x="{tx}" y="132">Harness</text>
          <path class="ln sw-hair dash-opt" d="M{hx + 8} 146H{end - 8}M{hx + 8} 222H{end - 8}M{hx + 8} 302H{end - 8}"/>
          {ruled}
          {model}
          <path class="ln" d="M{end} 180H{mx}" {marker}/>
          <text class="harness-wire" text-anchor="middle" x="{(end + mx) / 2}" y="169">{L(T("context", "Kontext"))}</text>
          <path class="ln" d="M{mx} 260H{end}" {marker}/>
          <text class="harness-wire" text-anchor="middle" x="{(end + mx) / 2}" y="249">{L(T("response", "Ausgabe"))}</text>
          <path class="ln" d="M{end - 16} 286V314" {marker}/>
          <path class="ln" d="M{tools_x} 390V456" {marker}/>
          <text class="harness-wire halo" x="{tools_x + 10}" y="444">{L(T("call", "Aufruf"))}</text>
          <path class="ln" d="M20 456V188H{hx}" {marker}/>
          <text class="harness-wire halo" text-anchor="middle" transform="translate(20 326) rotate(-90)">{L(T("results → next turn", "Ergebnisse → nächster Schritt"))}</text>
          {box(0, 456, w, 64, L(T("Tools & environment", "Werkzeuge & Umgebung")), L(T("terminal · tests · APIs · files", "Terminal · Tests · APIs · Dateien")))}
        </svg>'''
        explanations = [
            T("Selects what the model sees: the task, project instructions, conversation history and tool definitions. It stores run state and brings relevant information back into context.",
              "Wählt aus, was das Modell sieht: Aufgabe, Projektanweisungen, Gesprächsverlauf und Werkzeugdefinitionen. Hält den Zustand des Ablaufs fest und bringt relevante Informationen zurück in den Kontext."),
            T("Handles each model response: continue with a tool call, return an answer or ask a person. Applies limits, handles retries and records the run.",
              "Verarbeitet jede Modellausgabe: mit einem Werkzeugaufruf fortfahren, eine Antwort zurückgeben oder einen Menschen fragen. Beachtet Limits, behandelt erneute Versuche und protokolliert den Ablauf."),
            T("Checks a proposed call against tool schemas and permissions, obtains approval when required, invokes the tool and returns its result or error. The model cannot grant itself permission.",
              "Prüft einen vorgeschlagenen Aufruf gegen Werkzeugschemata und Rechte, holt nötige Freigaben ein, führt das Werkzeug aus und gibt Ergebnis oder Fehler zurück. Das Modell kann sich keine Rechte selbst erteilen."),
            T("The learned component. Given the context supplied by the harness, it generates a response: a proposed tool call, an answer or a question. Generating a tool call does not execute it; the harness handles execution.",
              "Die gelernte Komponente. Erzeugt aus dem vom Harness gelieferten Kontext eine Ausgabe: einen vorgeschlagenen Werkzeugaufruf, eine Antwort oder eine Frage. Ein erzeugter Werkzeugaufruf ist noch keine Ausführung; dafür sorgt der Harness."),
            T("The systems the agent works with: test runners, terminals, APIs and files. Tools perform operations and return observations; the environment determines where they run and which resources are reachable. They remain separate from the model and the harness’s control logic.",
              "Die Systeme, mit denen der Agent arbeitet: Test-Runner, Terminals, APIs und Dateien. Werkzeuge führen Operationen aus und liefern Beobachtungen; die Umgebung bestimmt Ausführungsort und erreichbare Ressourcen. Sie bleiben von Modell und Ablaufsteuerung des Harness getrennt."),
        ]
        regions = [(title, hx, y - 4, hw, 72) for y, _, title, _, _ in rows]
        regions += [(T("Model", "Modell"), mx, 150, mw, 144),
                    (T("Tools & environment", "Werkzeuge & Umgebung"), 0, 456, w, 64)]
        notes = "".join(
            f'<details class="harness-note">'
            f'<summary style="left:{100 * x / w:.4f}%;top:{100 * y / 524:.4f}%;width:{100 * rw / w:.4f}%;height:{100 * rh / 524:.4f}%" aria-label="{L(title)}: {L(T("explanation", "Erklärung"))}"></summary>'
            f'<div class="harness-explain"><strong>{L(title)}</strong><span>{L(explanation)}</span></div></details>'
            for (title, x, y, rw, rh), explanation in zip(regions, explanations))
        hint = L(T("Hover, focus or tap a harness section, the model or the tools to read its explanation here.",
                   "Mit Maus, Tastatur oder Antippen einen Harness-Abschnitt, das Modell oder die Werkzeuge wählen: Die Erklärung erscheint hier."))
        return (f'<div class="harness-stage harness-{"tall" if phone else "wide"}"><div class="harness-canvas">'
                f'{svg}<div class="harness-hint">{hint}</div>{notes}</div></div>')
    return fig(drawing(False) + drawing(True), T(
        "The model proposes; the harness runs the process. A tool call only becomes an action when the harness executes it. Results enter the next model call as context. The boundary separates responsibilities, even if everything runs in one application. Turn control also handles final answers, approval requests and limits.",
        "Das Modell schlägt vor; der Harness führt den Ablauf aus. Ein Werkzeugaufruf wird erst zur Handlung, wenn der Harness ihn ausführt. Ergebnisse gehen als Kontext in den nächsten Modellaufruf ein. Die Grenze trennt Zuständigkeiten, auch wenn alles in einer Anwendung läuft. Die Ablaufsteuerung behandelt auch Antworten, Freigaben und Limits."), lang, scroll=False,
        source=T(f"Conceptual synthesis; see {r('cf-harness')} and {r('trivedy')}.", f"Begriffliche Synthese; siehe {r('cf-harness')} und {r('trivedy')}."))


# =====================================================================
# 03 · Making output reliable (case study)
# =====================================================================

def dia_pipeline(lang, stage):
    """Slides 46 + 67 merged: description → (few-shot) LLM → model → parser ✓ / ✗ with the error message →
    generator → application. Stage 1 (#check) greys out the generator part; stage 2 (#app) shows all of it.
    360 wide: fits a phone as it is."""
    L = lambda x: x[lang]
    m, ma = 'marker-end="url(#pp' + str(stage) + ')"', 'marker-end="url(#pp' + str(stage) + 'a)"'
    later = ' class="pp-later"' if stage == 1 else ""
    offset = 76 if stage == 2 else 0
    semantic = (box(0, 334, 190, 50, L(T("Semantic checks", "Semantikprüfungen")), L(T("references · CoCos", "Referenzen · CoCos"))) + f'<path class="ln" d="M95 384V406" {m}/>') if stage == 2 else ""
    svg = f'''<svg class="dia pp" viewBox="0 0 360 {470 + offset}" role="img" aria-label="{L(T("Pipeline: an informal description and a few example pairs go to the LLM, which writes a class diagram; a parser checks it and sends it back with the error message if it is invalid; semantic checks validate references and context conditions before a generator, which produces the web application.", "Pipeline: Eine informelle Beschreibung und einige Beispielpaare gehen an das LLM, das ein Klassendiagramm schreibt; ein Parser prüft es und schickt es bei Fehlern mit der Fehlermeldung zurück; Semantikprüfungen validieren Referenzen und Kontextbedingungen vor einem Generator, der die Web-Anwendung erzeugt."))}">
  {_arrow_defs("pp" + str(stage))}
  {box(0, 0, 190, 60, L(T("Description", "Beschreibung")), L(T("“A library lends books", "„Eine Bibliothek verleiht")), sub2=L(T("to its members.”", "Bücher an Mitglieder.“")))}
  <path class="ln" d="M95 60V84" {m}/>
  {box(240, 88, 120, 50, L(T("Examples", "Beispiele")), L(T("few-shot pairs", "Few-Shot-Paare")))}
  <path class="ln" d="M240 104H194" {m}/>
  {box(0, 88, 190, 50, "LLM", L(T("writes the model", "schreibt das Modell")), cls="box hl")}
  <path class="ln hl" d="M95 138V164" {ma}/>
  {box(0, 168, 190, 56, L(T("Model", "Modell")), L(T("class diagram · CD4A", "Klassendiagramm · CD4A")), cls="box hl")}
  <text x="232" y="194" class="s">{L(T("people can read", "Menschen können es"))}</text><text x="232" y="208" class="s">{L(T("and check it", "lesen und prüfen"))}</text>
  <path class="ln" d="M95 224V250" {m}/>
  {box(0, 254, 190, 50, "Parser", L(T("syntax valid?", "Syntax gültig?")))}
  <path class="ln dash-opt" d="M190 279H216V122H194" {m}/>
  <text x="224" y="270" class="s a">✗ {L(T("error message", "Fehlermeldung"))}</text>
  <text x="224" y="284" class="s">{L(T("→ try again", "→ neuer Versuch"))}</text>
  <path class="ln hl" d="M95 304V330" {ma}/><text x="104" y="322" class="t a">✓</text>
  <g{later}>{semantic}
    {box(0, 334 + offset, 190, 50, "Generator", "MontiGem")}
    <text x="232" y="{356 + offset}" class="s">{L(T("deterministic,", "deterministisch,"))}</text><text x="232" y="{370 + offset}" class="s">{L(T("test templates", "Vorlagen testen"))}</text>
    <path class="ln" d="M95 {384 + offset}V{410 + offset}" {m}/>
    {box(0, 414 + offset, 190, 50, L(T("Application", "Anwendung")), L(T("web app", "Web-App")))}
  </g>
</svg>'''
    if stage == 1:
        cap = T("Free text becomes a model in a modelling language. A few example pairs teach the LLM the language; a parser checks syntax. References, context conditions and domain requirements need further validation. The generator part follows in section 3.4.",
                "Aus Freitext wird ein Modell in einer Modellierungssprache. Einige Beispielpaare bringen dem LLM die Sprache bei; ein Parser prüft die Syntax. Referenzen, Kontextbedingungen und fachliche Anforderungen brauchen weitere Validierung. Der Generator-Teil folgt in Abschnitt 3.4.")
        return side_fig(svg, 360, cap, lang, source=src("after", "BDMN+24"))
    cap = T("The full pipeline adds semantic checks before generation. Parsing alone cannot establish that Book, Member and Loan meet the requirements. Generation yields a runnable prototype, whose templates and extensions still need testing.",
            "Die vollständige Pipeline ergänzt Semantikprüfungen vor der Generierung. Parsen allein belegt nicht, dass Book, Member und Loan die Anforderungen erfüllen. Die Generierung liefert einen lauffähigen Prototyp; Vorlagen und Erweiterungen brauchen weiterhin Tests.")
    return side_fig(svg, 360, cap, lang, source=src("after", "NMR24"))


# Grammar masking, stepped: first JSON (every developer knows it), then CD4A (the case study). Each step:
# (state before, state after, candidates (token, p, allowed by the grammar), chosen token). Greedy: the chosen
# token is the most likely allowed one (checked below).
GM = {
    "json": {
        "states": {"start": (T("before the first token", "vor dem ersten Token"), T("{  (the grammar asks for an object)", "{  (die Grammatik verlangt ein Objekt)")),
                   "key": (T("in the object › a key", "im Objekt › ein Schlüssel"), T('a key in "…"  ·  }', 'ein Schlüssel in "…"  ·  }')),
                   "val": (T("after a key › a value", "nach einem Schlüssel › ein Wert"), T('"text"  ·  number  ·  true / false  ·  null  ·  {  ·  [', '"Text"  ·  Zahl  ·  true / false  ·  null  ·  {  ·  [')),
                   "next": (T("after a value › more, or close", "nach einem Wert › weiter oder schließen"), T(",  ·  }", ",  ·  }")),
                   "key2": (T("after a comma › a key", "nach einem Komma › ein Schlüssel"), T('a key in "…"  (no } after a comma)', 'ein Schlüssel in "…"  (kein } nach einem Komma)')),
                   "done": (T("the object is closed", "das Objekt ist geschlossen"), T("only the end", "nur noch das Ende")),
                   "end": (T("✓ valid JSON", "✓ gültiges JSON"), T("—", "—"))},
        "steps": [("start", "key", [("Here", .41, 0), ("```json", .27, 0), ("{", .22, 1), ("Sure", .07, 0), ("[", .03, 0)], "{"),
                  ("key", "val", [("title:", .38, 0), ('"title":', .35, 1), ("'title':", .14, 0), ('"name":', .08, 1), ("}", .05, 1)], '"title":'),
                  ("val", "next", [('"Dune"', .62, 1), ("Dune", .21, 0), ("'Dune'", .09, 0), ("null", .05, 1), ("unknown", .03, 0)], '"Dune"'),
                  ("next", "key2", [(",", .71, 1), ("}", .20, 1), (";", .05, 0), (".", .04, 0)], ","),
                  ("key2", "val", [('"pages":', .52, 1), ('"author":', .31, 1), ("pages:", .12, 0), ("}", .05, 0)], '"pages":'),
                  ("val", "next", [("412", .48, 1), ('"412"', .30, 1), ("four", .12, 0), ("~400", .06, 0), ("NaN", .04, 0)], "412"),
                  ("next", "done", [("<|END|>", .45, 0), ("}", .33, 1), (",", .17, 1), ("//", .05, 0)], "}"),
                  ("done", "end", [("```", .52, 0), ("<|END|>", .30, 1), ("This", .13, 0), (",", .05, 0)], "<|END|>")]},
    "cd4a": {
        "states": {0: (T("before the first token", "vor dem ersten Token"), "classdiagram"),
                   1: (T("after classdiagram › a name", "nach classdiagram › ein Name"), T("a name", "ein Name")),
                   2: (T("after the name › {", "nach dem Namen › {"), "{"),
                   3: (T("in the diagram › class, or }", "im Diagramm › class oder }"), "class  ·  }"),
                   4: (T("after class › a name", "nach class › ein Name"), T("a name", "ein Name")),
                   5: (T("after the class name › {", "nach dem Klassennamen › {"), "{"),
                   6: (T("in a class › a type, or }", "in einer Klasse › ein Typ oder }"), T("a type  ·  }", "ein Typ  ·  }")),
                   7: (T("after a type › a name", "nach einem Typ › ein Name"), T("a name", "ein Name")),
                   8: (T("after a name › ;", "nach einem Namen › ;"), ";"),
                   9: (T("all braces closed › the end", "alle Klammern zu › das Ende"), "<|END|>"),
                   10: (T("✓ the model parses", "✓ das Modell parst"), "—")},
        "steps": [(0, 1, [("Here", .38, 0), ("classdiagram", .30, 1), ("```", .16, 0), ("Sure", .10, 0), ("class", .06, 0)], "classdiagram"),
                  (1, 2, [("Library", .52, 1), ("{", .18, 0), (":", .12, 0), ('"Library"', .10, 0), ("City", .08, 1)], "Library"),
                  (2, 3, [("{", .64, 1), ("(", .17, 0), (":", .11, 0), ("->", .05, 0), (";", .03, 0)], "{"),
                  (3, 4, [("class", .46, 1), ("Book", .24, 0), ("table", .14, 0), ("<!--", .09, 0), ("}", .07, 1)], "class"),
                  (4, 5, [("Book", .78, 1), ("{", .10, 0), ("(", .06, 0), (":", .04, 0), ("Books", .02, 1)], "Book"),
                  (5, 6, [("(", .41, 0), ("{", .39, 1), (":", .10, 0), ("->", .06, 0), (";", .04, 0)], "{"),
                  (6, 7, [("-", .34, 0), ("String", .30, 1), ("+", .14, 0), ("int", .12, 1), ("}", .10, 1)], "String"),
                  (7, 8, [("title", .72, 1), (":", .12, 0), ("=", .08, 0), ("[", .05, 0), (";", .03, 0)], "title"),
                  (8, 6, [(",", .38, 0), (";", .36, 1), ("=", .12, 0), (":", .08, 0), ("}", .06, 0)], ";"),
                  (6, 3, [("}", .48, 1), ("int", .22, 1), ("String", .14, 1), ("-", .10, 0), ("<!--", .06, 0)], "}"),
                  (3, 9, [("<|END|>", .44, 0), ("}", .31, 1), ("class", .17, 1), ("```", .05, 0), ("Here", .03, 0)], "}"),
                  (9, 10, [("<|END|>", .58, 1), ("```", .20, 0), ("This", .14, 0), ("}", .05, 0), ("class", .03, 0)], "<|END|>")]},
}
for _g in GM.values():
    for _a, _b, _c, _pick in _g["steps"]:
        assert abs(sum(p for _, p, _ in _c) - 1) < 1e-9 and _pick == max((c for c in _c if c[2]), key=lambda c: c[1])[0], (_a, _pick)
        assert _a in _g["states"] and _b in _g["states"]
assert GM["json"]["steps"][0][2][0][2] == 0 and GM["json"]["steps"][-2][2][0][0] == "<|END|>"   # the mask matters at the start and the end


def dia_grammar_mask(lang):
    """Slides 48–52: grammar masking, stepped (assets/ai4se.js): the LLM proposes, the grammar removes, the most
    likely remaining token is appended. Two grammars: JSON first, CD4A (the library model) as the case study.
    No automaton drawing: a "where am I" line and the allowed tokens say the same in words, and fit a phone."""
    L = lambda x: x[lang]
    v = lambda x: L(x) if isinstance(x, dict) else x
    data = {"g": {name: {"states": {str(s): [v(a), v(b)] for s, (a, b) in g["states"].items()},
                         "steps": [{"from": str(a), "to": str(b), "cands": [[t, p, bool(ok)] for t, p, ok in c], "pick": pick} for a, b, c, pick in g["steps"]]}
                  for name, g in GM.items()},
            "words": {k: L(x) for k, x in dict(
                p0=T("1 · The LLM proposes the next token. It knows nothing about the grammar.", "1 · Das LLM schlägt das nächste Token vor. Von der Grammatik weiß es nichts."),
                p1=T("2 · The grammar removes what cannot follow here; the most likely remaining token is appended.", "2 · Die Grammatik streicht, was hier nicht folgen kann; das wahrscheinlichste verbleibende Token wird angehängt."),
                would=T("Without the mask the model would have written", "Ohne Maske hätte das Modell geschrieben"),
                masked=T("removed", "gestrichen"),
                agree=T("Here the most likely token was allowed anyway.", "Hier war das wahrscheinlichste Token ohnehin erlaubt."),
                where=T("where", "wo"), allowed=T("allowed here", "hier erlaubt"), stack=T("open braces", "offene Klammern"), none=T("none", "keine"),
                step=T("token", "Token"), of=T("of", "von")).items()}}
    chips = (f'<button type="button" class="first" aria-pressed="true" data-g="json">JSON</button>'
             f'<button type="button" aria-pressed="false" data-g="cd4a">{L(T("CD4A · the library", "CD4A · die Bibliothek"))}</button>')
    inner = f'''<div class="gm-head"><span class="k mono">{L(T("GRAMMAR", "GRAMMATIK"))}</span><span class="chips">{chips}</span></div>
<div class="gm-stage">
  <div class="gm-code"><span class="k mono">{L(T("THE OUTPUT SO FAR", "DIE AUSGABE BIS HIER"))}</span><pre class="mono"><code></code><span class="nt-cur" aria-hidden="true">▌</span></pre>
    <p class="gm-status mono"><span class="gm-where"></span><span class="gm-allowed"></span><span class="gm-stack"></span></p></div>
  <div class="gm-cands"><span class="k mono">{L(T("NEXT-TOKEN CANDIDATES", "KANDIDATEN FÜR DAS NÄCHSTE TOKEN"))}</span><ol class="bars mono"></ol><p class="gm-phase mono" aria-live="polite"></p></div>
</div>{controls(lang)}'''
    return demo("gm", data, inner, T(
        "Constrained decoding, token by token: the LLM proposes, the grammar removes what cannot follow, the most likely remaining token is appended (here always the top one; sampling works the same way). Normal completion requires the entire grammar to accept; balanced braces alone are insufficient.",
        "Constrained Decoding, Token für Token: Das LLM schlägt vor, die Grammatik streicht, was nicht folgen kann, das wahrscheinlichste verbleibende Token wird angehängt (hier immer das oberste; mit Ziehen funktioniert es genauso). Ein regulärer Abschluss erfordert Akzeptanz durch die gesamte Grammatik; geschlossene Klammern allein genügen nicht."), lang,
        source=src("illustrative", note=T("made-up probabilities", "ausgedachte Wahrscheinlichkeiten")))


MASK_ROWS = [("Llama 3 8B · 4-bit", 416, 991, 5.71, 918, 991, 74.10), ("Phi-3 Mini · 4-bit", 357, 976, 4.63, 849, 976, 138.29),
             ("Gemma 7B · 4-bit", 2, 658, 2.46, 612, 658, 54.20), ("Mistral 7B · 3-bit", 190, 905, 4.89, 836, 905, 73.59)]
_without = [a / b * 100 for _, a, b, *_ in MASK_ROWS]
_with = [c / d * 100 for *_, c, d, _ in MASK_ROWS]
_slower = [t1 / t0 for *_, t0, _, _, t1 in MASK_ROWS]
assert round(min(_with)) == 87 and round(max(_with)) == 93                 # text: "87 to 93 %"
assert round(min(_without), 1) == .3 and round(max(_without)) == 42        # text: "0.3 to 42 %"
assert round(min(_slower)) == 13 and round(max(_slower)) == 30             # text: "13 to 30 times slower"


def masking_table(lang):
    """Slide 53 / [NRR24]: share of parsing CD4A models, without and with grammar masking. Gemma is the hero row."""
    L = lambda x: x[lang]
    fmt = (lambda n: f"{n:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")) if lang == "de" else (lambda n: f"{n:,.1f}")
    body = "".join(f'<tr{" class=\"hero\"" if name.startswith("Gemma") else ""}><td>{name}</td><td class="n">{a}/{b} ({fmt(a / b * 100)} %)</td><td class="n hl">{c}/{d} ({fmt(c / d * 100)} %)</td><td class="n faint">{fmt(t0)} s → {fmt(t1)} s</td></tr>'
                   for name, a, b, t0, c, d, t1 in MASK_ROWS)
    head = (f'<tr><th>{L(T("Model", "Modell"))}</th><th class="n">{L(T("parses without mask", "parst ohne Maske"))}</th>'
            f'<th class="n">{L(T("parses with mask", "parst mit Maske"))}</th><th class="n">{L(T("time per model", "Zeit pro Modell"))}</th></tr>')
    from article_common import source_line
    cap = T("Share of generated class diagrams that parse, for 1,000 LLM-synthesized prompts based on university exam-task templates (2024). Denominators exclude token-limit failures and differ by model. Gemma’s 2/658 is 0.3 %, correcting the percentage typo in the paper. GPT-4o: 76/100 without masking, a separate service-based reference rather than a matched comparison.",
            "Anteil der erzeugten Klassendiagramme, die parsen, für 1.000 LLM-synthetisierte Prompts nach Vorlagen universitärer Klausuraufgaben (2024). Die Nenner schließen Tokenlimit-Abbrüche aus und unterscheiden sich je Modell. Gemmas 2/658 entsprechen 0,3 %; die Prozentangabe im Paper ist ein Tippfehler. GPT-4o: 76/100 ohne Masking, eine separate Dienst-Referenz statt eines direkt vergleichbaren Versuchs.")
    return (f'<figure class="media art-fig"><div class="tbl-wrap"><table class="tbl mono mask-tbl">{head}{body}</table></div>'
            f'<figcaption class="mono">{cap[lang]}{source_line(src("data", "NRR24"), lang)}</figcaption></figure>')


def curious(lang, body, title=None):
    """A collapsed box for the curious: depth that the main text does without. The summary is always
    "For the curious · <topic>": pass the topic only as title (a T()); without a title only the eyebrow shows."""
    k = T("For the curious", "Für Neugierige")[lang]
    t = f'<span class="cu-k">{k}</span>' + (f'<span class="cu-t">{title[lang]}</span>' if title else "")
    return f'<details class="curious"><summary class="mono">{t}</summary>{body[lang]}</details>'


def definition(term, short, lang):
    """A definition set apart: the term in mono, one sentence."""
    return f'<div class="defn"><span class="mono">{term[lang] if isinstance(term, dict) else term}</span><p>{short[lang]}</p></div>'


# =====================================================================
# The article
# =====================================================================

def body(lang, A):
    L = lambda x: x[lang]
    gpts = [("CD4A Class Diagram Creator", "https://chatgpt.com/g/g-sRnmDgQvW-cd4a-class-diagram-creator", T("class diagrams in CD4A", "Klassendiagramme in CD4A")),
            ("GUI-DSL2 Model Creator", "https://chatgpt.com/g/g-OOGsSd6sA-gui-dsl2-model-creator", T("page models in GUI-DSL 2", "Seitenmodelle in GUI-DSL 2")),
            ("SysML v2 Model Creator", "https://chatgpt.com/g/g-3DkGCDlNM-sysml-v2-model-creator", T("SysML v2 models", "SysML-v2-Modelle")),
            ("MontiCore Expert", "https://chatgpt.com/g/g-Pgayc5wzx-monticore-expert", T("questions on MontiCore", "Fragen zu MontiCore"))]
    tries = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{n} ↗</a><span class="mono faint">{L(d)}</span></li>' for n, u, d in gpts)
    kennel = ('classdiagram ' + L(T("KennelModel", "HundehüttenModell")) + ' {\n  class ' + L(T("Kennel", "Hundehütte")) + ' {\n    String ' + L(T("location", "standort")) + ';\n    double ' + L(T("width", "breite")) + ';\n    double ' + L(T("length", "länge")) + ';\n    double ' + L(T("height", "höhe")) + ';\n  }\n  class ' + L(T("Dog", "Hund")) + ' {\n    String name;\n    String ' + L(T("breed", "rasse")) + ';\n    int ' + L(T("age", "alter")) + ';\n  }\n  association [1] ' + L(T("Kennel", "Hundehütte")) + ' -> (' + L(T("resident", "bewohner")) + ') ' + L(T("Dog", "Hund")) + ' [*];\n}')
    ex2024 = L(T("2024 example", "Beispiel von 2024"))
    hook = ('{\n  "Book":   { "title": "string", "pages": "int" },\n  "Member": { "name": "string" },\n  "Loan":   { "due": "date", "book": "Book" }\n'
            )
    S = []          # (id, level, heading, html[, nav]): level 2 = chapter, 3 = sub chapter, 1 = closing chapter, 0 = no heading
    S.append(("intro", 0, None, L(T(
        """<p>Ask a chatbot for the data model of a small library app — books, members, loans — as JSON. What comes back looks right at first glance. Hand it to a program, and sometimes it fails: a closing brace is missing, a key has lost its quotes, or a friendly sentence comes before the JSON.</p>""",
        """<p>Bitten Sie einen Chatbot um das Datenmodell einer kleinen Bibliotheks-App — Bücher, Mitglieder, Ausleihen — als JSON. Was zurückkommt, sieht auf den ersten Blick richtig aus. Gibt man es einem Programm, scheitert es manchmal: Eine schließende Klammer fehlt, ein Schlüssel hat seine Anführungszeichen verloren, oder vor dem JSON steht ein freundlicher Satz.</p>"""))
        + f'<figure class="media art-fig hook"><pre class="art-pre mono">{hook}</pre><p class="hook-miss mono">{L(T("← one closing brace short (syntax only)", "← eine schließende Klammer fehlt (nur Syntax)"))}</p><figcaption class="mono">{L(T("Almost right is not good enough for a program.", "Fast richtig reicht einem Programm nicht."))}<span class="src">{L(T("Illustrative", "Illustrativ"))}</span></figcaption></figure>'
        + L(T("""<p>AI4SE also includes requirements work, testing, review and debugging. This article focuses on LLM-assisted modeling and model-driven generation, and answers three questions about that case. How does a language model produce such text? Why is it sometimes wrong — and just as confident when it is? And how do we make its output reliably right, so that a program, such as the generators of <a href="research-mde.html">part 1</a>, can build on it?</p>""",
              """<p>AI4SE umfasst auch Anforderungsarbeit, Tests, Reviews und Fehlersuche. Dieser Artikel konzentriert sich auf LLM-gestützte Modellierung und modellgetriebene Generierung und beantwortet dazu drei Fragen. Wie erzeugt ein Sprachmodell solchen Text? Warum liegt es manchmal falsch — und klingt dabei genauso sicher? Und wie machen wir seine Ausgabe verlässlich richtig, sodass ein Programm, etwa die Generatoren aus <a href="research-mde.html">Teil 1</a>, darauf aufbauen kann?</p>"""))))

    # ---------------- 01 What an LLM does ----------------
    S.append(("llm", 2, T("What an LLM does", "Was ein LLM tut"), L(T(
        "<p>An LLM — a large language model — has learned one thing extremely well: to continue a text. Answering, translating and writing code all follow from that. This chapter goes from the outside in: first what you see in the chat window, then what happens inside.</p>",
        "<p>Ein LLM — ein großes Sprachmodell (Large Language Model) — hat eine Sache außerordentlich gut gelernt: einen Text fortzusetzen. Antworten, übersetzen, Code schreiben — alles folgt daraus. Dieses Kapitel geht von außen nach innen: erst, was man im Chatfenster sieht, dann, was darin passiert.</p>"))))
    S.append(("tokens", 3, T("One token at a time", "Token für Token"), L(T(
        f"<p>To answer, an LLM does one thing over and over: given the text so far, it computes how likely each possible next piece of text is. Such a piece is called a <i>token</i> — a word, part of a word or a punctuation mark. One token is drawn, appended, and generation continues with that context (usually reusing cached attention keys and values) {r('wolfram')}:</p>",
        f"<p>Um zu antworten, macht ein LLM immer wieder nur eines: Zum bisherigen Text berechnet es, wie wahrscheinlich jedes mögliche nächste Textstück ist. So ein Stück heißt <i>Token</i> — ein Wort, ein Wortteil oder ein Satzzeichen. Ein Token wird gezogen, angehängt, und die Erzeugung läuft mit diesem Kontext weiter (meist mit zwischengespeicherten Attention-Keys und -Values) {r('wolfram')}:</p>"))
        + dia_next_token(lang)
        + L(T("<p>Why not always take the most likely token? Because then the text tends to become flat and repetitive; a little randomness makes it livelier. The price: the same prompt can give different answers, and nothing in the output says <i>why</i> a token was chosen. The <i>temperature</i> sets how much randomness there is — turn it up, and the variety grows, first in the wording, then in the facts.</p>",
              "<p>Warum nicht immer das wahrscheinlichste Token? Weil der Text dann eher flach und repetitiv wird; ein wenig Zufall macht ihn lebendiger. Der Preis: Derselbe Prompt kann unterschiedliche Antworten liefern, und nichts in der Ausgabe verrät, <i>warum</i> ein Token gewählt wurde. Die <i>Temperatur</i> regelt, wie viel Zufall im Spiel ist — dreht man sie hoch, wächst die Vielfalt, erst in der Formulierung, dann in den Fakten.</p>"))
        + curious(lang, T(f"""<ul class="pts"><li><b>Where tokens come from.</b> The vocabulary is not designed by hand. <i>Byte-pair encoding</i> starts from character or byte units, depending on the tokenizer and keeps merging the most frequent neighbouring pair into a new token {r('sennrich')}. Frequent words end up as one token, rare ones as several pieces. That is also why LLMs are clumsy at counting letters: variable token boundaries make character counting less direct.</li><li><b>Temperature.</b> The model actually outputs a score per token; the probabilities come from them by a <i>softmax</i>, after dividing every score by the temperature. Below 1 the likely tokens get even likelier; above 1 the distribution flattens and rare tokens get a chance. At temperature 0 the most likely token is always taken.</li><li><b>Top-k and top-p.</b> Most systems also cut off the long tail before drawing: only the k best tokens, or only the smallest set whose probabilities add up to p (“nucleus sampling”) {r('holtzman')}. That keeps the variety of sampling without the occasional absurd token. The demo above keeps only the candidates it shows.</li></ul>""",
                          f"""<ul class="pts"><li><b>Woher die Tokens kommen.</b> Das Vokabular entwirft niemand von Hand. <i>Byte-Pair-Encoding</i> beginnt je nach Tokenizer mit Zeichen- oder Byte-Einheiten und verschmilzt immer wieder das häufigste benachbarte Paar zu einem neuen Token {r('sennrich')}. Häufige Wörter werden ein Token, seltene mehrere Stücke. Deshalb tun sich LLMs auch schwer, Buchstaben zu zählen: Variable Tokengrenzen machen das zeichenweise Zählen weniger direkt.</li><li><b>Temperatur.</b> Eigentlich gibt das Modell pro Token einen Wert aus; die Wahrscheinlichkeiten entstehen daraus per <i>Softmax</i>, nachdem jeder Wert durch die Temperatur geteilt wurde. Unter 1 werden die wahrscheinlichen Tokens noch wahrscheinlicher; über 1 wird die Verteilung flacher, und seltene Tokens bekommen eine Chance. Bei Temperatur 0 wird immer das wahrscheinlichste Token genommen.</li><li><b>Top-k und Top-p.</b> Die meisten Systeme schneiden vor dem Ziehen außerdem den langen Schwanz ab: nur die k besten Tokens, oder nur die kleinste Menge, deren Wahrscheinlichkeiten zusammen p ergeben („Nucleus Sampling“) {r('holtzman')}. So bleibt die Vielfalt des Ziehens, ohne gelegentliches absurdes Token. Die Demo oben zieht nur unter den gezeigten Kandidaten.</li></ul>"""),
                  T("Tokens and sampling", "Tokens und Ziehen"))))
    S.append(("embeddings", 3, T("Words become numbers: embeddings", "Aus Wörtern werden Zahlen: Embeddings"), L(T(
        "<p>Inside, the model works with numbers, not words. Every token becomes a vector — a long list of numbers — called an <i>embedding</i>. The following two-dimensional toy illustration is inspired by classic static word embeddings, not a measured GPT token space:</p>",
        "<p>Im Inneren arbeitet das Modell mit Zahlen, nicht mit Wörtern. Jedes Token wird zu einem Vektor — einer langen Zahlenliste —, dem <i>Embedding</i>. Die folgende zweidimensionale Spielzeugdarstellung ist von klassischen statischen Wort-Embeddings inspiriert, kein gemessener GPT-Tokenraum:</p>"))
        + dia_embeddings(lang)
        + L(T("<p>Transformer token representations become context-dependent across layers. Semantic search commonly uses a separate embedding model for whole queries and passages: a sentence about a happy dog and one about a playful hound land close together, although they share no word. That makes <i>semantic search</i> possible — finding a passage by what it means, not by its exact words. Chapter 02 builds on it.</p>",
              "<p>Tokenrepräsentationen im Transformer werden über die Schichten kontextabhängig. Semantische Suche nutzt meist ein separates Embedding-Modell für ganze Fragen und Textabschnitte: Ein Satz über einen fröhlichen Hund und einer über einen verspielten Vierbeiner landen nah beieinander, obwohl sie kein Wort teilen. Das ermöglicht <i>semantische Suche</i> — eine Stelle nach ihrer Bedeutung finden, nicht nach ihren genauen Wörtern. Kapitel 02 baut darauf auf.</p>"))
        + curious(lang, T(f"""<ul class="pts"><li><b>How many dimensions?</b> The figure has two; real embeddings have hundreds to thousands — GPT-3 works with 12,288 numbers per token {r('brown')}. Nobody chose what each number means; the axes are whatever the training found useful.</li><li><b>Close means similar.</b> Closeness is usually measured as the angle between two vectors (cosine similarity), not their distance — a long and a short text on the same topic point the same way.</li><li><b>Arithmetic with meaning.</b> In word embeddings of 2013, the vector of <i>king</i> minus <i>man</i> plus <i>woman</i> landed closest to <i>queen</i> {r('mikolov')}.</li></ul>""",
                          f"""<ul class="pts"><li><b>Wie viele Dimensionen?</b> Die Abbildung hat zwei; echte Embeddings haben Hunderte bis Tausende — GPT-3 arbeitet mit 12.288 Zahlen pro Token {r('brown')}. Niemand hat festgelegt, was jede Zahl bedeutet; die Achsen sind, was das Training nützlich fand.</li><li><b>Nah heißt ähnlich.</b> Nähe misst man meist als Winkel zwischen zwei Vektoren (Kosinus-Ähnlichkeit), nicht als Abstand — ein langer und ein kurzer Text zum selben Thema zeigen in dieselbe Richtung.</li><li><b>Rechnen mit Bedeutung.</b> In Wort-Embeddings von 2013 lag der Vektor <i>king</i> minus <i>man</i> plus <i>woman</i> am nächsten an <i>queen</i> {r('mikolov')}.</li></ul>"""),
                  T("Dimensions and distance", "Dimensionen und Abstand")), T("Embeddings", "Embeddings")))
    S.append(("neural", 3, T("Inside: a neural network", "Im Inneren: ein neuronales Netz"), L(T(
        f"<p>What turns those numbers into the next token is a neural network. The idea is older than it looks — the first one, the perceptron, dates from 1958 {r('rosenblatt')} — and easiest to see with a picture: is this a dog or a cat?</p><p>The network does not see a dog, only pixel values, one number per input. Every connection has a <i>weight</i>: a number saying how much one input counts. In this toy network, hidden neurons use ReLU: negative weighted sums become zero. Softmax converts the two output scores into probabilities.</p>",
        f"<p>Was aus diesen Zahlen das nächste Token macht, ist ein neuronales Netz. Die Idee ist älter, als sie aussieht — das erste, das Perzeptron, stammt von 1958 {r('rosenblatt')} — und am einfachsten an einem Bild zu sehen: Ist das ein Hund oder eine Katze?</p><p>Das Netz sieht keinen Hund, nur Pixelwerte, eine Zahl pro Eingabe. Jede Verbindung hat ein <i>Gewicht</i>: eine Zahl, die sagt, wie viel eine Eingabe zählt. In diesem Spielzeugnetz nutzen die versteckten Neuronen ReLU: Negative gewichtete Summen werden null. Softmax wandelt die zwei Ausgabewerte in Wahrscheinlichkeiten um.</p>"))
        + dia_neural_net(lang, A)
        + L(T(f"<p>Training adjusts the weights over many examples until the right output wins. For scale: the roundworm <i>C. elegans</i> gets by with 302 neurons; GPT-3 has 175 billion weights (parameters and biological neurons are different quantities) {r('brown')}.</p>",
              f"<p>Training passt die Gewichte über viele Beispiele an, bis die richtige Ausgabe gewinnt. Zum Vergleich: Der Fadenwurm <i>C. elegans</i> kommt mit 302 Neuronen aus; GPT-3 hat 175 Milliarden Gewichte (Parameter und biologische Neuronen sind verschiedene Größen) {r('brown')}.</p>"))
        + curious(lang, T(f"""<ul class="pts"><li><b>How the weights move.</b> After each example the network compares its output with the right answer. <i>Backpropagation</i> works out, layer by layer from the back, how much each weight contributed to the error {r('rumelhart')}; every weight is then nudged a tiny step in the direction that makes the error smaller (gradient descent). Repeat that billions of times.</li><li><b>Pre-training.</b> An LLM needs no labelled pictures: the right answer is simply the next token of a real text. This enables learning from large collections of unlabelled text.</li><li><b>Becoming an assistant.</b> A pre-trained model only continues text. Possible post-training stages include instruction tuning and preference optimization such as RLHF: people rank answers, a reward model learns those preferences, and the LLM is tuned towards them (RLHF). In the InstructGPT study, people preferred the answers of a tuned model with 1.3 billion weights over those of GPT-3 with 175 billion {r('ouyang')}.</li></ul>""",
                          f"""<ul class="pts"><li><b>Wie sich die Gewichte bewegen.</b> Nach jedem Beispiel vergleicht das Netz seine Ausgabe mit der richtigen Antwort. <i>Backpropagation</i> rechnet Schicht für Schicht von hinten aus, wie viel jedes Gewicht zum Fehler beigetragen hat {r('rumelhart')}; dann wird jedes Gewicht ein winziges Stück in die Richtung verschoben, die den Fehler kleiner macht (Gradientenabstieg). Das Ganze milliardenfach.</li><li><b>Pre-Training.</b> Ein LLM braucht keine beschrifteten Bilder: Die richtige Antwort ist einfach das nächste Token eines echten Textes. Das ermöglicht Lernen aus großen Sammlungen unbeschrifteter Texte.</li><li><b>Vom Textfortsetzer zum Assistenten.</b> Ein vortrainiertes Modell setzt nur Text fort. Mögliche Nachtrainingsschritte sind Instruction Tuning und Präferenzoptimierung wie RLHF: Menschen bewerten Antworten, ein Belohnungsmodell lernt diese Vorlieben, und das LLM wird darauf hin angepasst (RLHF). In der InstructGPT-Studie zogen Menschen die Antworten eines so angepassten Modells mit 1,3 Milliarden Gewichten denen von GPT-3 mit 175 Milliarden vor {r('ouyang')}.</li></ul>"""),
                  T("How the weights are learned", "Wie die Gewichte gelernt werden")), T("Neural network", "Neuronales Netz")))
    S.append(("attention", 3, T("What made it work: attention and scale", "Was den Durchbruch brachte: Attention und Größe"), L(T(
        f"<p>Which earlier words matter for the next one? In 2017 a new architecture, the <i>transformer</i>, made that question its core {r('vaswani')}: every token gets to look at every earlier token and weigh how much it matters. This is called <i>attention</i>. It is what lets a model resolve references like this one, where a single word decides what “it” means:</p>",
        f"<p>Welche früheren Wörter zählen für das nächste? 2017 machte eine neue Architektur, der <i>Transformer</i>, diese Frage zu ihrem Kern {r('vaswani')}: Jedes Token darf auf jedes frühere Token schauen und abwägen, wie wichtig es ist. Das heißt <i>Attention</i>. Damit löst ein Modell Bezüge wie diesen auf, bei dem ein einziges Wort entscheidet, was „er“ meint:</p>"))
        + dia_attention(lang)
        + L(T("<p>A GPT repeats this step many times over, in layers. In plain words it does three things:</p>",
              "<p>Ein GPT wiederholt diesen Schritt viele Male, in Schichten. In einfachen Worten tut es drei Dinge:</p>"))
        + dia_transformer_simple(lang)
        + L(T("<p>The second ingredient is scale. LLMs are trained on enormous amounts of text, so they handle the nuances of language very well. Input may be ungrammatical, misspelt and colloquial — the model has seen all of that before:</p>",
              "<p>Die zweite Zutat ist die Größe. LLMs werden auf enormen Textmengen trainiert und verarbeiten die Nuancen der Sprache deshalb sehr gut. Eingaben dürfen grammatikalisch ungenau, voller Rechtschreibfehler und umgangssprachlich sein — das Modell kennt all das aus seinen Trainingsdaten:</p>"))
        + chat(lang, [("user", L(T("Correct the spelling and grammar of this sentence: “Modle-drivn sofware developmnt a very exiting topic is!!”",
                                   "Überführe den folgenden Satz in korrekte Rechtschreibung und Grammatik: „Modelgetibene Softwär Enticklunk ein sehr spannendes Thema ist!!“"))),
                      ("GPT-4", L(T("“Model-driven software development is a very exciting topic!”", "„Modellgetriebene Softwareentwicklung ist ein sehr spannendes Thema!“")))], f"GPT-4 · {ex2024}")
        + curious(lang, T(f"""{dia_transformer('en')}<ul class="pts"><li><b>What attention computes.</b> Every token is turned into three vectors: a <i>query</i> (what am I looking for?), a <i>key</i> (what do I offer?) and a <i>value</i> (what do I pass on?). A token compares its query with the keys of all earlier tokens; the better they match, the more of their value it takes in. In the toy illustration, this is the backward-looking relation shown for “big”, not a measured explanation.</li><li><b>Many heads, many layers.</b> Several such attention “heads” run side by side, each free to learn a different kind of relation, and the layers are stacked — 96 of them in GPT-3, each 12,288 numbers wide.</li><li><b>The context window.</b> Standard full attention over an input sequence has quadratic cost. Cached decoding and sparse or sliding attention have different costs. Context limits also reflect training, architecture and serving choices — 2,048 for GPT-3, hundreds of thousands for current models. Whatever does not fit, the model does not see.</li></ul>""",
                          f"""{dia_transformer('de')}<ul class="pts"><li><b>Was Attention berechnet.</b> Jedes Token wird in drei Vektoren übersetzt: eine <i>Query</i> (wonach suche ich?), einen <i>Key</i> (was biete ich an?) und einen <i>Value</i> (was gebe ich weiter?). Ein Token vergleicht seine Query mit den Keys aller früheren Tokens; je besser sie passen, desto mehr von deren Value nimmt es auf. Die Spielzeugdarstellung zeigt für „groß“ eine solche rückwärts gerichtete Beziehung, keine gemessene Erklärung.</li><li><b>Viele Köpfe, viele Schichten.</b> Mehrere solcher Attention-„Köpfe“ arbeiten nebeneinander, jeder kann eine andere Art von Bezug lernen, und die Schichten sind gestapelt — 96 bei GPT-3, jede 12.288 Zahlen breit.</li><li><b>Das Kontextfenster.</b> Volle Standard-Attention über eine Eingabesequenz hat quadratischen Aufwand. Decoding mit Cache und sparse oder gleitende Attention haben andere Kosten. Kontextlimits hängen auch von Training, Architektur und Betrieb ab — 2.048 bei GPT-3, Hunderttausende bei aktuellen Modellen. Was nicht hineinpasst, sieht das Modell nicht.</li></ul>"""),
                  T("Inside the transformer", "Im Inneren des Transformers")), T("Attention", "Attention")))
    S.append(("hallucinations", 3, T("Plausible, not true: hallucinations", "Plausibel, nicht wahr: Halluzinationen"), L(T(
        f"""<p>An LLM picks the most <i>plausible</i> continuation, not the <i>true</i> one. Models can generalize beyond training examples, and can also fail on familiar facts. Fluent wording and training-data coverage do not establish factual correctness.</p>
<p>For developers the best-documented case is code that imports packages that do not exist. A study generated 576,000 code samples in Python and JavaScript with 16 models: on average, at least 5.2 % of the packages that commercial models referenced did not exist, and 21.7 % for open-source models — 205,474 different invented names {r('spracklen')}. Anyone can register such a name in a package registry and put malicious code behind it.</p>
<p>Reasoning is just as fragile. “Alice has 5 sisters and 3 brothers. How many sisters does a brother of Alice have?” — the best models of 2024 often got this wrong {r('alice')}. Tools close part of the gap: a code interpreter, a lookup in the package index, a test run. An LLM that uses tools in a loop is an <a href="#agent">agent</a>.</p>""",
        f"""<p>Ein LLM wählt die <i>plausibelste</i> Fortsetzung, nicht die <i>wahre</i>. Modelle können über Trainingsbeispiele hinaus verallgemeinern und auch bei vertrauten Fakten scheitern. Flüssige Formulierungen und Abdeckung in Trainingsdaten belegen keine faktische Richtigkeit.</p>
<p>Für Entwickler ist der am besten belegte Fall Code, der Pakete importiert, die es nicht gibt. Eine Studie erzeugte mit 16 Modellen 576.000 Code-Beispiele in Python und JavaScript: Im Schnitt existierten mindestens 5,2 % der Pakete, auf die kommerzielle Modelle verwiesen, gar nicht, bei Open-Source-Modellen 21,7 % — 205.474 verschiedene erfundene Namen {r('spracklen')}. Jeder kann so einen Namen in einem Paketverzeichnis registrieren und Schadcode dahinterlegen.</p>
<p>Genauso brüchig ist das Schlussfolgern. „Alice hat 5 Schwestern und 3 Brüder. Wie viele Schwestern hat ein Bruder von Alice?“ — die besten Modelle von 2024 lagen hier oft falsch {r('alice')}. Werkzeuge schließen einen Teil der Lücke: ein Code-Interpreter, ein Blick ins Paketverzeichnis, ein Testlauf. Ein LLM, das Werkzeuge in einer Schleife einsetzt, ist ein <a href="#agent">Agent</a>.</p>"""))
        + curious(lang, T(f"""<p>Why does a model not simply say “I don’t know”? One answer: training and evaluation reward guessing. In a test that scores right answers and gives nothing for “I don’t know”, a guess is always the better bet — for students in an exam and for language models in a benchmark. Kalai et al. argue that hallucinations follow from exactly this, and that fewer of them need different scoring: wrong answers must cost more than an honest “I don’t know” {r('kalai')}.</p>""",
                          f"""<p>Warum sagt ein Modell nicht einfach „Weiß ich nicht“? Eine Antwort: Training und Bewertung belohnen das Raten. In einem Test, der richtige Antworten zählt und für „Weiß ich nicht“ nichts gibt, ist Raten immer die bessere Wette — für Studierende in der Klausur wie für Sprachmodelle im Benchmark. Kalai et al. argumentieren, dass Halluzinationen genau daraus folgen und dass es für weniger davon eine andere Bewertung braucht: Falsche Antworten müssen mehr kosten als ein ehrliches „Weiß ich nicht“ {r('kalai')}.</p>"""),
                  T("Why models guess", "Warum Modelle raten"))
        + L(T("""<div class="take"><span class="k mono">THREE THINGS TO KEEP</span><ul class="pts"><li>An LLM writes one token at a time, each one drawn from a probability distribution.</li><li>Plausible is not true: expect confident mistakes, especially beyond the training data.</li><li>Because it writes token by token, every single token can be checked — chapter 03 uses exactly that.</li></ul></div>""",
              """<div class="take"><span class="k mono">DREI DINGE ZUM MITNEHMEN</span><ul class="pts"><li>Ein LLM schreibt Token für Token, jedes aus einer Wahrscheinlichkeitsverteilung gezogen.</li><li>Plausibel ist nicht wahr: Rechnen Sie mit selbstsicheren Fehlern, besonders jenseits der Trainingsdaten.</li><li>Weil es Token für Token schreibt, lässt sich jedes einzelne Token prüfen — genau das nutzt Kapitel 03.</li></ul></div>""")),
        T("Hallucinations", "Halluzinationen")))

    # ---------------- 02 Around the model ----------------
    S.append(("around", 2, T("Building around the model", "Was um das Modell herum entsteht"), L(T(
        "<p>A model alone turns text into text. Most of what makes AI useful in practice is built around it: search, tools, loops and checks. First, the vocabulary.</p>",
        "<p>Ein Modell allein verwandelt Text in Text. Das meiste, was KI in der Praxis nützlich macht, entsteht drumherum: Suche, Werkzeuge, Schleifen und Prüfungen. Zuerst die Begriffe.</p>")), T("Around the model", "Rund um das Modell")))
    S.append(("umbrella", 3, T("The vocabulary", "Die Begriffe"),
        '<blockquote class="epigraph"><p>I propose to consider the question, “Can machines think?”</p><footer class="mono">Alan M. Turing · Computing Machinery and Intelligence, 1950</footer></blockquote>'
        + L(T(f"<p>The question is older than computers as we know them {r('turing')}, and “artificial intelligence” has stayed a broad and loosely defined term: even simple decision trees are often called AI. Machine learning narrows it to algorithms that learn from data, deep learning to those that use neural networks, generative AI to systems that create new content. Generative AI describes a capability, including non-deep-learning methods. LLMs are a major class of deep-learning-based generative models; ChatGPT and Copilot are products combining models and software:</p>",
              f"<p>Die Frage ist älter als Computer, wie wir sie kennen {r('turing')}, und „Künstliche Intelligenz“ ist ein breiter, unscharf definierter Begriff geblieben: Auch einfache Entscheidungsbäume werden gern KI genannt. Machine Learning grenzt das auf Algorithmen ein, die aus Daten lernen; Deep Learning auf solche mit neuronalen Netzen; generative KI auf Systeme, die neue Inhalte erzeugen. Generative KI beschreibt eine Fähigkeit, auch mit Verfahren außerhalb von Deep Learning. LLMs sind eine wichtige Klasse generativer Deep-Learning-Modelle; ChatGPT und Copilot sind Produkte aus Modellen und Software:</p>"))
        + dia_ai_terms(lang)
        + L(T("<p>And four words that come up whenever LLMs are used:</p>", "<p>Und vier Begriffe, die beim Arbeiten mit LLMs immer wieder fallen:</p>"))
        + glossary(lang)))
    S.append(("rag", 3, T("RAG: give it your documents", "RAG: eigene Dokumente mitgeben"), L(T(
        f"<p>An LLM can use both learned patterns and information supplied in its context or through tools. To let it answer from your own documents, you do not train it again — you search first and hand it what you found. Combined with the semantic search of chapter 01, this is <i>retrieval-augmented generation</i> (RAG) {r('lewis')}:</p>",
        f"<p>Ein LLM kann gelernte Muster ebenso wie Informationen im Kontext oder aus Werkzeugen nutzen. Damit es aus eigenen Dokumenten antwortet, trainiert man es nicht neu — man sucht zuerst und gibt ihm, was man gefunden hat. Zusammen mit der semantischen Suche aus Kapitel 01 ergibt das <i>Retrieval-Augmented Generation</i> (RAG) {r('lewis')}:</p>"))
        + dia_rag(lang)
        + L(T("<p>Users can describe their problem in their own words and still find the right passage. <a href=\"projects-se-chatty.html\">SE-Chatty</a>, a chatbot on lecture material, works this way.</p>",
              "<p>Nutzer können ihr Problem in eigenen Worten beschreiben und finden trotzdem die passende Stelle. <a href=\"projects-se-chatty.html\">SE-Chatty</a>, ein Chatbot zu Vorlesungsmaterial, arbeitet so.</p>"))
        + curious(lang, T("""<ul class="pts"><li><b>Before the first question.</b> The documents are cut into chunks of a few paragraphs, each chunk is turned into an embedding, and the embeddings go into a vector index.</li><li><b>At every question.</b> The question is embedded the same way; the index returns the nearest chunks; they are pasted into the prompt together with the question and the instruction to answer from them and to name the source.</li><li><b>Where it goes wrong.</b> Both retrieval and generation can fail. The model can ignore relevant evidence or invent citations; retrieval can fail through chunks cut in the wrong place, a question that uses other words than the documents, a table that loses its structure. Many systems therefore combine semantic search with plain keyword search and let a second model re-rank the hits.</li></ul>""",
                          """<ul class="pts"><li><b>Vor der ersten Frage.</b> Die Dokumente werden in Abschnitte von ein paar Absätzen zerlegt, jeder Abschnitt wird in ein Embedding übersetzt, und die Embeddings kommen in einen Vektorindex.</li><li><b>Bei jeder Frage.</b> Die Frage wird genauso eingebettet; der Index liefert die nächstgelegenen Abschnitte; sie werden in den Prompt kopiert, zusammen mit der Frage und der Anweisung, daraus zu antworten und die Quelle zu nennen.</li><li><b>Wo es schiefgeht.</b> Suche und Generierung können scheitern. Das Modell kann relevante Belege ignorieren oder Quellen erfinden; Suchprobleme entstehen durch Abschnitte an der falschen Stelle geschnitten, eine Frage mit anderen Wörtern als die Dokumente, eine Tabelle, die ihre Struktur verliert. Viele Systeme kombinieren deshalb semantische Suche mit einfacher Stichwortsuche und lassen ein zweites Modell die Treffer neu sortieren.</li></ul>"""),
                  T("Chunks, index, re-ranking", "Abschnitte, Index, Neusortierung")), T("RAG", "RAG")))
    S.append(("agent", 3, T("Agents: tools in a loop", "Agenten: Werkzeuge in einer Schleife"),
        definition(T("Agent", "Agent"), T("An AI agent is a system in which a language model directs the use of tools in a loop to reach a goal, choosing its next steps from the results it observes.",
                                          "Ein KI-Agent ist ein System, in dem ein Sprachmodell den Einsatz von Werkzeugen in einer Schleife steuert, um ein Ziel zu erreichen, und seine nächsten Schritte anhand der beobachteten Ergebnisse wählt."), lang)
        + L(T(f"<p>Chatbots may also use tools. Here, an agent means a goal-directed system whose LLM chooses its next steps. An agent gets a goal, acts — reads a file, runs the tests, edits code —, looks at the result and decides what to do next, until the goal is reached. Simon Willison puts it in one line: “An LLM agent runs tools in a loop to achieve a goal.” {r('willison')}</p>",
              f"<p>Auch Chatbots können Werkzeuge nutzen. Hier bezeichnet Agent ein zielgerichtetes System, dessen LLM die nächsten Schritte wählt. Ein Agent bekommt ein Ziel, handelt — liest eine Datei, führt die Tests aus, ändert Code —, betrachtet das Ergebnis und entscheidet, was als Nächstes zu tun ist, bis das Ziel erreicht ist. Simon Willison fasst das in einem Satz: „An LLM agent runs tools in a loop to achieve a goal.“ {r('willison')}</p>"))
        + dia_agent(lang)
        + L(T(f"<p>Anthropic draws the line against <i>workflows</i>: in a workflow, LLMs and tools follow paths a programmer laid down in advance; in an agent, the LLM directs its own process and its use of tools {r('anthropic')}. That makes agents flexible — and harder to predict.</p>",
              f"<p>Anthropic grenzt Agenten von <i>Workflows</i> ab: Im Workflow folgen LLMs und Werkzeuge Pfaden, die ein Programmierer vorher festgelegt hat; im Agenten steuert das LLM seinen Ablauf und seinen Werkzeuggebrauch selbst {r('anthropic')}. Das macht Agenten flexibel — und schwerer vorherzusagen.</p>")), T("Agents", "Agenten")))
    S.append(("harness", 3, T("Harness: running the agent", "Harness: den Agenten betreiben"),
        definition("Harness", T("An agent harness is the software and configuration that run the loop around a model: assemble context, call the model, execute permitted tool calls, and feed results into the next turn.",
                                "Ein Agent-Harness ist die Software samt Konfiguration, die die Schleife um ein Modell betreibt: Kontext zusammenstellen, das Modell aufrufen, erlaubte Werkzeugaufrufe ausführen und Ergebnisse in den nächsten Schritt zurückführen."), lang)
        + L(T(f"""<p><b>Why a separate term?</b> A model can generate a request to run a test; something else must actually run it, keep the result and call the model again. That machinery has its own design decisions and failure modes. Changing it can change the agent’s behaviour without changing the model’s weights. Cloudflare puts this execution loop at the centre of its definition {r('cf-harness')}.</p>
<p><b>Model, harness, agent.</b> The <i>model</i> is the learned component: given context, it generates a response, which may contain tool calls. The <i>harness</i> manages the run: context and state, tool execution, permissions, continuation and stopping. The <i>agent</i> is the resulting goal-directed system in which the model chooses the next steps. The model proposes what to do; the harness determines what can execute and carries it out.</p>""",
              f"""<p><b>Warum ein eigener Begriff?</b> Ein Modell kann einen Aufruf zum Ausführen eines Tests erzeugen; etwas anderes muss ihn tatsächlich ausführen, das Ergebnis festhalten und das Modell erneut aufrufen. Diese Software hat eigene Entwurfsentscheidungen und Fehlerquellen. Änderungen daran können das Verhalten des Agenten verändern, ohne die Modellgewichte anzutasten. Cloudflare stellt diese Ausführungsschleife ins Zentrum seiner Definition {r('cf-harness')}.</p>
<p><b>Modell, Harness, Agent.</b> Das <i>Modell</i> ist die gelernte Komponente: Es erzeugt aus Kontext eine Ausgabe, die Werkzeugaufrufe enthalten kann. Der <i>Harness</i> verwaltet den Ablauf: Kontext und Zustand, Werkzeugausführung, Rechte, Fortsetzung und Abbruch. Der <i>Agent</i> ist das daraus entstehende zielgerichtete System, in dem das Modell die nächsten Schritte wählt. Das Modell schlägt vor, was zu tun ist; der Harness bestimmt, was ausgeführt werden darf, und führt es aus.</p>"""))
        + dia_harness(lang)
        + L(T("""<p><b>One iteration: fix a failing test.</b> The harness supplies the task, project instructions and available tools. The model requests a test run. The harness checks permission, invokes the test runner and returns its output. The model uses that output to propose an edit or another test. The harness repeats the process, or ends it on a final response, a limit or a request for human input. A tool call is a request, not yet an executed action.</p>
<p><b>Where is the boundary?</b> Here, the harness includes tool adapters and the rules for calling them; the test runner, repository and external services are the tools and environment it connects to. An <code>AGENTS.md</code> file configures the harness when it is loaded as project instructions. A source file read to fix a bug is task data. A test supplies feedback when the harness runs it and returns the result. A prompt alone does not provide an execution loop; an SDK or framework supplies a harness only insofar as it implements that loop.</p>""",
              """<p><b>Ein Durchlauf: einen fehlschlagenden Test reparieren.</b> Der Harness stellt Aufgabe, Projektanweisungen und verfügbare Werkzeuge bereit. Das Modell fordert einen Testlauf an. Der Harness prüft die Berechtigung, ruft den Test-Runner auf und gibt dessen Ausgabe zurück. Das Modell nutzt diese Ausgabe, um eine Änderung oder einen weiteren Test vorzuschlagen. Der Harness wiederholt den Ablauf oder beendet ihn bei einer abschließenden Antwort, einem Limit oder einer Rückfrage an den Menschen. Ein Werkzeugaufruf ist eine Anforderung, noch keine ausgeführte Handlung.</p>
<p><b>Wo verläuft die Grenze?</b> Hier umfasst der Harness die Werkzeugadapter und ihre Aufrufregeln; Test-Runner, Repository und externe Dienste sind die angebundenen Werkzeuge und die Umgebung. Eine <code>AGENTS.md</code>-Datei konfiguriert den Harness, wenn sie als Projektanweisung geladen wird. Eine Quelldatei, die zur Fehlersuche gelesen wird, ist Aufgabendaten. Ein Test liefert Feedback, wenn der Harness ihn ausführt und das Ergebnis zurückgibt. Ein Prompt allein stellt keine Ausführungsschleife bereit; ein SDK oder Framework liefert einen Harness nur insoweit, wie es diese Schleife implementiert.</p>"""))
        + curious(lang, T(f"""<p>There is no single agreed boundary. Trivedy uses the broad shorthand <i>agent = model + harness</i>, including bundled infrastructure {r('trivedy')}. Anthropic’s safety account separates model, harness, tools and environment {r('anthropic-layers')}. This article uses an operational boundary: the harness controls the run and connects to tools and an environment. These are responsibilities, not necessarily separate processes or products. A coding product can bundle all of them.</p>
<p>Nor does every harness feature belong in every agent. Persistent memory, context compaction, subagents and recovery are extensions, not defining requirements. Anthropic’s long-running-agent example shows why continuity across context windows needs deliberate support {r('anthropic-harness')}. A fixed workflow can use the same machinery; what makes it an agent here is the model’s control over the next steps.</p>""",
                          f"""<p>Es gibt keine allgemein vereinbarte Grenze. Trivedy verwendet die breite Kurzform <i>Agent = Modell + Harness</i>, einschließlich mitgelieferter Infrastruktur {r('trivedy')}. Anthropics Sicherheitsbetrachtung trennt Modell, Harness, Werkzeuge und Umgebung {r('anthropic-layers')}. Dieser Artikel zieht eine betriebliche Grenze: Der Harness steuert den Ablauf und bindet Werkzeuge und Umgebung an. Das sind Zuständigkeiten, nicht zwingend getrennte Prozesse oder Produkte. Ein Coding-Produkt kann alles bündeln.</p>
<p>Auch braucht nicht jeder Agent jede Harness-Funktion. Dauerhafter Speicher, Kontextkomprimierung, Subagenten und Wiederanlauf sind Erweiterungen, keine Definitionsmerkmale. Anthropics Beispiel für lang laufende Agenten zeigt, weshalb die Fortsetzung über Kontextfenster hinweg gezielte Unterstützung braucht {r('anthropic-harness')}. Ein fester Workflow kann dieselbe Technik nutzen; zum Agenten wird das System hier dadurch, dass das Modell die nächsten Schritte steuert.</p>"""),
                  T("One term, different boundaries", "Ein Begriff, verschiedene Grenzen"))
        + L(T(f"""<p><b>Why it matters in practice.</b> The same model can behave differently under different harnesses: it sees different context, has different tools and receives different feedback. Teams can improve the built-in harness through project rules and checks. Böckeler calls these <i>guides</i> before an action and <i>sensors</i> afterwards {r('boeckeler')}. Instructions ask the model to behave; permissions and isolation constrain what can execute. Retrieved content remains task data, and passing a syntax check does not establish safety or correctness.</p>
<p><a href="projects-esaca.html">ESACA</a>, the project I work on, brings coding agents into a company’s own infrastructure. The next chapter examines two concrete ways of steering and checking model output: a grammar as a guide and a parser as a sensor.</p>""",
              f"""<p><b>Warum das praktisch zählt.</b> Dasselbe Modell kann sich mit verschiedenen Harnesses unterschiedlich verhalten: Es sieht anderen Kontext, hat andere Werkzeuge und erhält anderes Feedback. Teams können den eingebauten Harness durch Projektregeln und Prüfungen ergänzen. Böckeler nennt diese <i>Guides</i> vor einer Handlung und <i>Sensoren</i> danach {r('boeckeler')}. Anweisungen bitten das Modell um ein Verhalten; Rechte und Isolation begrenzen, was ausgeführt werden kann. Abgerufene Inhalte bleiben Aufgabendaten, und eine bestandene Syntaxprüfung belegt weder Sicherheit noch Korrektheit.</p>
<p><a href="projects-esaca.html">ESACA</a>, das Projekt, an dem ich arbeite, bringt Coding-Agenten in die unternehmenseigene Infrastruktur. Das nächste Kapitel betrachtet zwei konkrete Wege, Modellausgaben zu lenken und zu prüfen: eine Grammatik als Guide und einen Parser als Sensor.</p>""")), T("Harness", "Harness")))

    # ---------------- 03 Making output reliable ----------------
    S.append(("mde", 2, T("Making output reliable: LLMs and models", "Verlässliche Ausgaben: LLMs und Modelle"), L(T(
        """<p>Copilot-style assistants write lines of code. This chapter goes one level up: the LLM writes the <i>model</i>, and a generator writes the code. What models, languages and generators are is explained in <a href="research-mde.html">part 1</a>; here the question is how to make the LLM’s part reliable. The example is the one from part 1: a small library with books, members and loans.</p>""",
        """<p>Assistenten wie Copilot schreiben Codezeilen. Dieses Kapitel geht eine Ebene höher: Das LLM schreibt das <i>Modell</i>, und ein Generator schreibt den Code. Was Modelle, Sprachen und Generatoren sind, erklärt <a href="research-mde.html">Teil 1</a>; hier geht es darum, wie der Teil des LLMs verlässlich wird. Das Beispiel ist das aus Teil 1: eine kleine Bibliothek mit Büchern, Mitgliedern und Ausleihen.</p>""")), T("LLMs and models", "LLMs und Modelle")))
    S.append(("models", 3, T("Language models that write models", "Sprachmodelle, die Modelle schreiben"), L(T(
        f"""<p>A modelling language is a language like any other, so you can teach it to an LLM without retraining: put a few example models into the prompt (few-shot) and let it look up the language reference when it needs it (RAG) {cite("BDMN+24")}. The examples here use <b>CD4A</b>, a compact text notation for UML class diagrams (see <a href="research-mde.html">part 1</a>). In 2024 we built custom GPTs this way; here is one of their answers, from before the library became our example:</p>""",
        f"""<p>Eine Modellierungssprache ist eine Sprache wie jede andere, also kann man sie einem LLM ohne neues Training beibringen: einige Beispielmodelle in den Prompt geben (Few-Shot) und es bei Bedarf in der Sprachreferenz nachschlagen lassen (RAG) {cite("BDMN+24")}. Die Beispiele hier nutzen <b>CD4A</b>, eine kompakte Textnotation für UML-Klassendiagramme (siehe <a href="research-mde.html">Teil 1</a>). 2024 haben wir so eigene GPTs gebaut; hier eine ihrer Antworten, aus der Zeit, bevor die Bibliothek unser Beispiel wurde:</p>"""))
        + chat(lang, [("user", L(T("Create a simple model of a dog kennel", "Erzeuge mir ein einfaches Modell einer Hundehütte"))),
                      ("CD4A Model Creator", f"<pre><code>{kennel}</code></pre>")], L(T(f"custom GPT “CD4A Model Creator” · {ex2024}", f"eigenes GPT „CD4A Model Creator“ · {ex2024}")))
        + L(T("<p>Try the assistants yourself:</p>", "<p>Probieren Sie die Assistenten selbst aus:</p>"))
        + f'<ul class="tries">{tries}</ul>'
        + L(T(f"<p>LLMs tuned for a modelling language can do more than create new models: they can change existing ones, or turn a whiteboard sketch into proper syntax. When they edit, though, they sometimes change things nobody asked for — and sometimes repair errors along the way {cite('NKR+25')}. Either way, something has to check the result.</p>",
              f"<p>LLMs, die auf eine Modellierungssprache angepasst sind, können mehr als neue Modelle erstellen: Sie können bestehende ändern oder eine Whiteboard-Skizze in die passende Syntax überführen. Beim Ändern ändern sie allerdings manchmal Dinge, nach denen niemand gefragt hat — und reparieren manchmal nebenbei Fehler {cite('NKR+25')}. So oder so muss etwas das Ergebnis prüfen.</p>")), T("Models from LLMs", "Modelle vom LLM")))
    S.append(("check", 3, T("Check afterwards: the parser", "Danach prüfen: der Parser"), L(T(
        "<p>What makes this reliable is what happens <i>after</i> the LLM. A parser — the same one the generator uses — checks every model. If it fails, the model goes back to the LLM together with the parser’s error message, and the LLM tries again:</p>",
        "<p>Verlässlich wird das erst durch das, was <i>nach</i> dem LLM passiert. Ein Parser — derselbe, den der Generator nutzt — prüft jedes Modell. Scheitert es, geht das Modell mit der Fehlermeldung des Parsers zurück an das LLM, und das LLM versucht es erneut:</p>"))
        + dia_pipeline(lang, 1)
        + L(T("<p>This is the harness idea from chapter 02, applied to models: the parser is a <i>sensor</i>. It catches every syntax error — but only afterwards, and every new attempt costs time.</p>",
              "<p>Das ist die Harness-Idee aus Kapitel 02, angewandt auf Modelle: Der Parser ist ein <i>Sensor</i>. Er findet jeden Syntaxfehler — aber erst hinterher, und jeder neue Versuch kostet Zeit.</p>")), T("The parser", "Der Parser")))
    S.append(("masking", 3, T("Prevent upfront: constrained decoding", "Vorab verhindern: Constrained Decoding"), L(T(
        "<p>Syntax errors can also be prevented during generation. An LLM writes <a href=\"#tokens\">one token at a time</a>, so before each token is chosen, a grammar can remove every candidate that cannot follow at this point. This is called <i>constrained decoding</i>. It is easiest to see with JSON: after an opening brace, only a quoted key or a closing brace may follow.</p>",
        "<p>Syntaxfehler lassen sich auch während der Erzeugung verhindern. Ein LLM schreibt <a href=\"#tokens\">Token für Token</a> — also kann eine Grammatik vor jedem Token jeden Kandidaten streichen, der an dieser Stelle nicht folgen kann. Das heißt <i>Constrained Decoding</i>. Am einfachsten sieht man es an JSON: Nach einer öffnenden Klammer darf nur ein Schlüssel in Anführungszeichen oder eine schließende Klammer folgen.</p>"))
        + dia_grammar_mask(lang)
        + L(T(f"<p>Candidates in this demo are schematic readable fragments, not actual tokenizer units. JSON needs quotes, colons, commas and valid values, not just balanced braces. The CD4A tab shows the same mechanism with the grammar of a modelling language, building the <code>Book</code> class of the library. For nested braces the grammar keeps a count of what is still open — exactly where LLMs are weak: even ChatGPT has trouble closing brackets correctly in long texts {r('wolfram')}.</p>",
              f"<p>Die Kandidaten hier sind schematische lesbare Fragmente, keine tatsächlichen Tokenizer-Einheiten. JSON braucht Anführungszeichen, Doppelpunkte, Kommas und gültige Werte, nicht nur geschlossene Klammern. Der Reiter CD4A zeigt denselben Mechanismus mit der Grammatik einer Modellierungssprache und baut die Klasse <code>Book</code> der Bibliothek. Für verschachtelte Klammern führt die Grammatik Buch darüber, was noch offen ist — genau dort sind LLMs schwach: Selbst ChatGPT hat Mühe, Klammern in langen Texten richtig zu schließen {r('wolfram')}.</p>"))
        + L(T(f"<p><b>Case study: grammar masking for CD4A.</b> We tried this with small open models that run on a single computer, on about 1,000 modelling tasks {cite('NRR24')}:</p>",
              f"<p><b>Fallstudie: Grammar Masking für CD4A.</b> Wir haben das mit kleinen offenen Modellen ausprobiert, die auf einem einzelnen Rechner laufen, an rund 1.000 Modellierungsaufgaben {cite('NRR24')}:</p>"))
        + masking_table(lang)
        + L(T("<p>With masking, parser acceptance rises to 87–93 %, from 0.3–42 %. Our 2024 MontiCore → Lark → Guidance prototype did not reach 100 %: converted grammar constructs differed from the target parser; token limits and nonterminating repetitions also caused failures. Runs reaching the token limit are excluded from the table. In this Guidance-based setup, generation took 13–30 times as long; this is not a general cost of constrained decoding. Semantic well-formedness and requirements still need separate checks.</p>",
              "<p>Mit Masking steigt die Parser-Akzeptanz auf 87–93 % statt 0,3–42 %. Unser MontiCore-→-Lark-→-Guidance-Prototyp von 2024 erreichte keine 100 %: Konvertierte Grammatikkonstrukte wichen vom Zielparser ab; Tokenlimits und endlose Wiederholungen verursachten weitere Fehler. Läufe am Tokenlimit sind aus der Tabelle ausgeschlossen. In diesem Guidance-Aufbau dauerte die Erzeugung 13–30-mal so lange; das ist kein allgemeiner Aufwand von Constrained Decoding. Semantische Wohlgeformtheit und Anforderungen brauchen eigene Prüfungen.</p>"))
        + L(T(f"<p>The mask needs control over the decoding loop. With open models you have it yourself. Hosted APIs now do part of it on their side: several can guarantee output that follows a JSON schema, and OpenAI’s API also accepts a context-free grammar for custom tools {r('openai-cfg')}.</p>",
              f"<p>Die Maske braucht Kontrolle über die Schleife, die Token für Token erzeugt. Bei offenen Modellen hat man sie selbst. Gehostete APIs übernehmen inzwischen einen Teil davon: Mehrere garantieren Ausgaben nach einem JSON-Schema, und die API von OpenAI nimmt für eigene Werkzeuge auch eine kontextfreie Grammatik an {r('openai-cfg')}.</p>"))
        + curious(lang, T(f"""<ul class="pts"><li><b>Why it is a guarantee.</b> A parser afterwards can only reject; the mask decides beforehand. With a sound constraint engine, an exact target grammar and normal termination at an accepting state, the output belongs to the enforced grammar. Truncation and grammar-conversion errors break these preconditions; syntax alone does not establish semantics {r('geng')}.</li><li><b>Tokens do not match the grammar.</b> A token can contain half a keyword, or a brace plus a space plus the next name. So the mask cannot simply look up grammar symbols; it checks for every candidate whether its characters can continue the text so far. Doing that fast for tens of thousands of tokens at every step is the engineering part.</li><li><b>Syntax, not meaning.</b> Under those preconditions the mask ensures syntactic acceptance. Whether the classes are the right ones, or whether a referenced class exists at all, still needs checks afterwards — and the model can be pushed into valid but awkward text when it “wanted” something else.</li></ul>""",
                          f"""<ul class="pts"><li><b>Warum es eine Garantie ist.</b> Ein Parser danach kann nur ablehnen; die Maske entscheidet vorher. Mit korrekter Constraint-Implementierung, exakter Zielgrammatik und regulärem Ende in einem akzeptierenden Zustand gehört die Ausgabe zur erzwungenen Grammatik. Abschneiden und Konvertierungsfehler verletzen diese Voraussetzungen; Syntax allein belegt keine Semantik {r('geng')}.</li><li><b>Tokens passen nicht zur Grammatik.</b> Ein Token kann ein halbes Schlüsselwort enthalten, oder eine Klammer plus Leerzeichen plus den nächsten Namen. Die Maske kann deshalb nicht einfach Grammatiksymbole nachschlagen; sie prüft für jeden Kandidaten, ob seine Zeichen den bisherigen Text fortsetzen können. Das bei jedem Schritt für Zehntausende Tokens schnell zu tun, ist der Ingenieursteil.</li><li><b>Syntax, nicht Bedeutung.</b> Unter diesen Voraussetzungen sichert die Maske syntaktische Akzeptanz. Ob die Klassen die richtigen sind oder eine referenzierte Klasse überhaupt existiert, braucht weiter Prüfungen danach — und das Modell kann in gültigen, aber ungeschickten Text gedrängt werden, wenn es eigentlich etwas anderes „wollte“.</li></ul>"""),
                  T("Why the mask is a guarantee", "Warum die Maske eine Garantie ist")), T("Constrained decoding", "Constrained Decoding")))
    S.append(("app", 3, T("From model to application", "Vom Modell zur Anwendung"), L(T(
        f"""<p>Put together with model-driven engineering, this goes all the way: users describe their domain informally, an LLM derives the class diagram, syntax and semantic checks validate the model, and a generator such as <a href="research-mde.html#montigem">MontiGem</a> turns it into a runnable data-centric web prototype {cite("Net24")}:</p>""",
        f"""<p>Zusammen mit modellgetriebener Softwareentwicklung reicht das bis zum Ende: Nutzer beschreiben ihre Domäne informell, ein LLM leitet das Klassendiagramm ab, Syntax- und Semantikprüfungen validieren das Modell, und ein Generator wie <a href="research-mde.html#montigem">MontiGem</a> macht daraus einen lauffähigen datenzentrierten Web-Prototyp {cite("Net24")}:</p>"""))
        + dia_pipeline(lang, 2)
        + L(T("<p>The LLM only does what it is good at: turning language into a model. Reproducible generation can still reproduce template defects. Business rules, workflows, authorization and integrations may require additional models and extensions. Accurate grammar conversion, timeouts, contextual constraints and generator maintenance remain engineering tasks. The explicit intermediate model lets people check what the AI understood — before a single line of code exists.</p>",
              "<p>Das LLM macht nur, was es gut kann: Sprache in ein Modell übersetzen. Reproduzierbare Generierung kann auch Vorlagenfehler reproduzieren. Geschäftsregeln, Abläufe, Berechtigungen und Integrationen können weitere Modelle und Erweiterungen erfordern. Exakte Grammatikkonvertierung, Zeitlimits, Kontextbedingungen und Generatorwartung bleiben Engineering-Aufgaben. Das explizite Zwischenmodell lässt Menschen prüfen, was die KI verstanden hat — bevor auch nur eine Zeile Code existiert.</p>"))))
    S.append(("summary", 1, T("In short", "Kurz gesagt"), L(T(
        """<ul class="pts"><li>An LLM continues text, one token at a time, each drawn from a probability distribution.</li><li>It writes the plausible text, not the true one — expect confident mistakes, such as packages that do not exist.</li><li>RAG, agents and harnesses are built around the model; much of an agent’s quality sits in the harness.</li><li>Checking belongs in the harness: tests, linters, parsers.</li><li>A sound decoder can guarantee syntax for the enforced grammar if it finishes normally; semantics and requirements remain separate checks.</li></ul>
<div class="fit"><div><span class="k mono">WORTH IT WHEN</span><ul class="pts"><li>the output is in a formal language — JSON, a DSL, code — that a parser or a grammar can check</li><li>a program builds on the output</li></ul></div><div><span class="k mono">SOMETHING ELSE IS ENOUGH WHEN</span><ul class="pts"><li>the text is for people only: then a careful human review does the job</li></ul></div></div>""",
        """<ul class="pts"><li>Ein LLM setzt Text fort, Token für Token, jedes aus einer Wahrscheinlichkeitsverteilung gezogen.</li><li>Es schreibt den plausiblen Text, nicht den wahren — rechnen Sie mit selbstsicheren Fehlern, etwa Paketen, die es nicht gibt.</li><li>RAG, Agenten und Harnesses entstehen rund um das Modell; viel von der Qualität eines Agenten steckt im Harness.</li><li>Prüfen gehört in den Harness: Tests, Linter, Parser.</li><li>Ein korrekter Decoder kann bei regulärem Abschluss Syntax gemäß der erzwungenen Grammatik garantieren; Semantik und Anforderungen bleiben eigene Prüfungen.</li></ul>
<div class="fit"><div><span class="k mono">LOHNT SICH, WENN</span><ul class="pts"><li>die Ausgabe in einer formalen Sprache vorliegt — JSON, eine DSL, Code —, die ein Parser oder eine Grammatik prüfen kann</li><li>ein Programm auf der Ausgabe aufbaut</li></ul></div><div><span class="k mono">ETWAS ANDERES REICHT, WENN</span><ul class="pts"><li>der Text nur für Menschen ist: Dann reicht eine sorgfältige Durchsicht durch einen Menschen</li></ul></div></div>"""))))
    refs = "".join(f'<li id="ref-{k}">{t}</li>' for k, (_, t) in enumerate(REFS, 1))
    fallback = T('<noscript><style>.demo button,.demo input{display:none!important}</style><p class="mono">Interactive figures require JavaScript. Static diagrams, captions and source tables remain available; displayed demo values are illustrative unless labeled as publication data.</p></noscript>',
                 '<noscript><style>.demo button,.demo input{display:none!important}</style><p class="mono">Interaktive Abbildungen benötigen JavaScript. Statische Diagramme, Bildunterschriften und Quelltabellen bleiben verfügbar; Demo-Werte sind illustrativ, sofern sie nicht als Publikationsdaten gekennzeichnet sind.</p></noscript>')
    return None, fallback[lang] + article_common.sections(S, lang), refs


def page(lang):
    """Returns (file, title, description, body, scripts) for build.py; header, literature and series end come from
    article_common (the same for all four parts)."""
    A = "../" if lang == "de" else ""
    _, sections, refs = body(lang, A)
    lead = T("How does a language model produce text, why is it sometimes confidently wrong — and how do we make its output reliable enough for software to build on? From tokens to agents to <em>language models that write models</em>.",
             "Wie erzeugt ein Sprachmodell Text, warum liegt es manchmal selbstsicher falsch — und wie wird seine Ausgabe verlässlich genug, dass Software darauf aufbauen kann? Von Tokens über Agenten bis zu <em>Sprachmodellen, die Modelle schreiben</em>.")
    desc = T("AI-driven software engineering: how LLMs work, what agents and harnesses are, and how parsers and grammars make LLM output reliable enough for generators — an article by Lukas Netz.",
             "KI-getriebene Softwareentwicklung: wie LLMs funktionieren, was Agenten und Harnesses sind und wie Parser und Grammatiken LLM-Ausgaben verlässlich genug für Generatoren machen — ein Artikel von Lukas Netz.")
    return article_common.page(lang, FILE, sections, refs, OWN, article_art.hero_ai4se(lang), lead, desc,
                               article_common.scripts(lang, "ai4se", css=True))
