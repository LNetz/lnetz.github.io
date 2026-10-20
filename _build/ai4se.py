"""
Research sub page: AI-driven software engineering (research-ai4se.html) — an article in the
manner of a blog post, based on the acronio page and the AI4SE / SE4AI talk (10 / 2024).
Imported by build.py. Diagrams are inline SVG with the .dia classes of style.css; the three
interactive figures (neural network, next token, grammar masking) are driven by assets/ai4se.js,
which reads its data from the figure's data-json attribute.

Three chapters (h2, listed at the top): how an LLM works · basic terms · LLMs and models.
Their sub chapters are h3 and stay out of the chapter list.
"""
import html
import json

from project_content import _arrow_defs, box, dia_scroll
from project_pages import pub_list

NL = "\n"
FILE = "research-ai4se.html"


def T(en, de):
    return {"en": en, "de": de}


def cite(key):
    """Own paper: a subtle reference into the research page's publication list."""
    return f'<a class="cite" href="research.html#pub-{key}">[{key}]</a>'


def ref(n):
    """Other literature: a numbered note at the end of this page."""
    return f'<a class="cite" href="#ref-{n}">[{n}]</a>'


def _link(label, url):
    return f'{label} <a href="{url}" target="_blank" rel="noopener">↗</a>'


REFS = [
    "A. M. Turing: Computing Machinery and Intelligence. Mind 59(236), 433–460 (1950).",
    "F. Rosenblatt: The perceptron: a probabilistic model for information storage and organization in the brain. Psychological Review 65(6), 386–408 (1958).",
    "A. Vaswani et al.: Attention is all you need. Advances in Neural Information Processing Systems 30 (2017).",
    "S. Barke, M. B. James, N. Polikarpova: Grounded Copilot: How programmers interact with code-generating models. arXiv:2206.15000 (2022).",
    "T. Brown et al.: Language models are few-shot learners. Advances in Neural Information Processing Systems 33, 1877–1901 (2020).",
    "G. Izacard et al.: Few-shot learning with retrieval augmented language models. arXiv:2208.03299 (2022).",
    "M. Nezhurina, L. Cipolina-Kun, M. Cherti, J. Jitsev: Alice in Wonderland: Simple tasks showing complete reasoning breakdown in state-of-the-art large language models. arXiv:2406.02061 (2024).",
    _link("S. Wolfram: What Is ChatGPT Doing … and Why Does It Work? Stephen Wolfram Writings (2023).", "https://writings.stephenwolfram.com/2023/02/what-is-chatgpt-doing-and-why-does-it-work/"),
    _link("E. Schluntz, B. Zhang: Building effective agents. Anthropic Engineering (2024).", "https://www.anthropic.com/engineering/building-effective-agents"),
    _link("S. Willison: on the definition of “agent”. simonwillison.net (2025).", "https://simonwillison.net/2025/Sep/18/agents/"),
    _link("B. Böckeler: Harness engineering for coding agent users. martinfowler.com.", "https://martinfowler.com/articles/harness-engineering.html"),
    _link("V. Trivedy: The Anatomy of an Agent Harness. LangChain Blog (2026).", "https://www.langchain.com/blog/the-anatomy-of-an-agent-harness"),
]
OWN = ["NMR24", "BDMN+24", "NRR24", "Net24", "NKR+25"]


def chat(lang, turns, source):
    """A dialogue with a model, set quietly: who speaks in mono, the text below."""
    rows = "".join(f'<div class="turn{" ai" if who != "user" else ""}"><span class="who mono">{(T("User", "Nutzer") if who == "user" else T(who, who))[lang]}</span>'
                   f'<div class="msg">{text}</div></div>' for who, text in turns)
    return f'<figure class="chat">{rows}<figcaption class="mono">{source}</figcaption></figure>'


def fig(svg, caption, lang, scroll=True):
    inner = dia_scroll(svg) if scroll else svg
    return f'<figure class="media art-fig">{inner}<figcaption class="mono">{caption[lang]}</figcaption></figure>'


def demo(kind, data, inner, caption, lang):
    """An interactive figure: assets/ai4se.js finds it by data-demo and reads data-json."""
    js = html.escape(json.dumps(data, ensure_ascii=False), quote=True)
    return (f'<figure class="media art-fig demo {kind}" data-demo="{kind}" data-json="{js}">{inner}'
            f'<figcaption class="mono">{caption[lang]}</figcaption></figure>')


def controls(lang, temperature=False):
    """Play button, step slider and the step label; optionally a temperature slider."""
    t = (f'<label class="temp">{T("temperature", "Temperatur")[lang]} <input type="range" min="0.1" max="2" step="0.1" value="1">'
         f'<output>1.0</output></label>') if temperature else ""
    return (f'<div class="demo-ctrl mono"><button type="button" class="play" aria-label="{T("play", "abspielen")[lang]}">▶</button>'
            f'<input class="step" type="range" min="0" max="1" value="0" aria-label="{T("step", "Schritt")[lang]}">'
            f'<span class="where" aria-live="polite"></span>{t}</div>')


# =====================================================================
# Diagrams
# =====================================================================

def dia_ai_terms(lang):
    """Slide 4: AI as an umbrella term — nested fields, each with a one-line definition."""
    L = lambda x: x[lang]
    levels = [
        (T("Artificial intelligence", "Künstliche Intelligenz"), T("research on intelligent machines that act and react like humans", "Forschung an intelligenten Maschinen, die wie Menschen handeln und reagieren")),
        ("Machine learning", T("statistical algorithms that learn from data and generalise to unseen data", "statistische Algorithmen, die aus Daten lernen und auf Ungesehenes verallgemeinern")),
        ("Deep learning", T("machine learning with neural networks that find complex patterns", "Machine Learning mit neuronalen Netzen, die komplexe Muster erkennen")),
        (T("Generative AI", "Generative KI"), T("AI that creates new content from patterns it has learned", "KI, die aus gelernten Mustern neue Inhalte erzeugt")),
        ("LLMs", T("large language models: process and produce human-like text", "große Sprachmodelle: verarbeiten und erzeugen menschenähnlichen Text")),
    ]
    parts = []
    for k, (name, desc) in enumerate(levels):
        x, y, w, h = 12 + k * 22, 12 + k * 46, 300 - k * 44, 300 - k * 46
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{22 - k * 2}" style="fill:var(--accent);fill-opacity:{.06 + k * .05};stroke:var(--accent);stroke-opacity:.35"/>')
        ty = y + 24
        parts.append(f'<text x="{x + w / 2}" y="{ty}" text-anchor="middle" class="t">{L(name) if isinstance(name, dict) else name}</text>')
        parts.append(f'<path class="ln" d="M{x + w / 2 + 70} {ty - 4}H340"/><circle cx="340" cy="{ty - 4}" r="2" class="dot"/>')
        words, line1 = L(desc).split(" "), ""
        while words and len(line1 + words[0]) < 52:
            line1 += words.pop(0) + " "
        parts.append(f'<text x="352" y="{ty}">{line1.strip()}</text>' + (f'<text x="352" y="{ty + 15}" class="s">{" ".join(words)}</text>' if words else ""))
    parts.append('<circle cx="124" cy="270" r="27" class="box hl"/><text x="124" y="274" text-anchor="middle" class="s" style="font-size:9px">ChatGPT</text>')
    parts.append('<circle cx="190" cy="270" r="27" class="box"/><text x="190" y="274" text-anchor="middle" class="s" style="font-size:9px">Copilot</text>')
    svg = f'<svg class="dia" viewBox="0 0 860 324" role="img" aria-label="{L(T("Artificial intelligence as an umbrella term: machine learning, deep learning, generative AI and LLMs nested inside each other", "Künstliche Intelligenz als Sammelbegriff: Machine Learning, Deep Learning, generative KI und LLMs ineinander geschachtelt"))}">{"".join(parts)}</svg>'
    return fig(svg, T("AI is an umbrella term. What is meant today is usually its innermost part: large language models such as ChatGPT or Copilot.",
                      "KI ist ein Sammelbegriff. Gemeint ist heute meist der innerste Teil: große Sprachmodelle wie ChatGPT oder Copilot."), lang)


# the five pixels the small network reads (column, row in the 16 × 16 image)
NN_PIXELS = [(6, 5), (4, 3), (12, 4), (7, 11), (9, 13)]
NN_IN = [36, 68, 100, 132, 164]          # y of the input, hidden and output neurons
NN_HID = [52, 84, 116, 148]
NN_OUT = [76, 124]
NN_X = (340, 470, 600)


def dia_neural_net(lang, A):
    """Slides 5–9: a picture becomes pixels, pixels feed a network, the network says dog or cat.
    Below it, one neuron in detail — the one the visitor points at (assets/ai4se.js)."""
    L = lambda x: x[lang]
    xi, xh, xo = NN_X
    cell = 7.5
    px = "".join(f'<rect class="nn-px" data-i="{k}" x="{140 + c * cell}" y="{40 + r * cell}" width="{cell}" height="{cell}"/>'
                 for k, (c, r) in enumerate(NN_PIXELS))
    feed = "".join(f'<path class="nn-feed" data-i="{k}" d="M{140 + (c + .5) * cell:.1f} {40 + (r + .5) * cell:.1f}L292 {y}"/>'
                   for k, ((c, r), y) in enumerate(zip(NN_PIXELS, NN_IN)))
    edges = "".join(f'<path class="nn-e" data-l="1" data-i="{a}" data-j="{b}" d="M{xi} {ya}L{xh} {yb}"/>' for a, ya in enumerate(NN_IN) for b, yb in enumerate(NN_HID))
    edges += "".join(f'<path class="nn-e" data-l="2" data-i="{a}" data-j="{b}" d="M{xh} {ya}L{xo} {yb}"/>' for a, ya in enumerate(NN_HID) for b, yb in enumerate(NN_OUT))

    def node(l, i, x, y, r, label, name):
        return (f'<g class="nn-n" data-l="{l}" data-i="{i}" tabindex="0" role="button" aria-label="{name}">'
                f'<circle class="box" cx="{x}" cy="{y}" r="{r}"/><circle class="nn-act" cx="{x}" cy="{y}" r="{r}"/>'
                f'<text x="{x}" y="{y + 3.5}" text-anchor="middle" class="s nn-lbl">{label}</text></g>')
    neuron = L(T("neuron", "Neuron"))
    nodes = "".join(node(0, k, xi, y, 8, "", f"{L(T('pixel', 'Pixel'))} x{k + 1}") + f'<text class="nn-v" data-i="{k}" x="324" y="{y + 4}" text-anchor="end"></text>' for k, y in enumerate(NN_IN))
    nodes += "".join(node(1, k, xh, y, 11, f"h{k + 1}", f"{neuron} h{k + 1}") for k, y in enumerate(NN_HID))
    outs = [T("dog", "Hund"), T("cat", "Katze")]
    nodes += "".join(node(2, k, xo, y, 12, "", f"{neuron} {L(o)}") for k, (y, o) in enumerate(zip(NN_OUT, outs)))
    labels = "".join(f'<text x="{xo + 22}" y="{y + 4}" class="t{" nn-win" if k == 0 else ""}">{L(o)}</text>'
                     f'<rect class="nn-track" x="{xo + 72}" y="{y - 4}" width="110" height="8" rx="2"/><rect class="nn-bar" data-i="{k}" x="{xo + 72}" y="{y - 4}" width="{[100, 10][k]}" height="8" rx="2"/>'
                     f'<text class="nn-pv s" data-i="{k}" x="{xo + 190}" y="{y + 4}">{["0.91", "0.09"][k]}</text>' for k, (y, o) in enumerate(zip(NN_OUT, outs)))
    labels += (f'<text x="{xi}" y="200" text-anchor="middle" class="s">{L(T("pixel values", "Pixelwerte"))}</text>'
               f'<text x="{xh}" y="200" text-anchor="middle" class="s">{L(T("hidden layer", "verdeckte Schicht"))}</text>'
               f'<text x="{xo}" y="200" text-anchor="middle" class="s">{L(T("output", "Ausgabe"))}</text>')
    # the static detail (no script): one neuron with symbolic inputs; ai4se.js redraws it with numbers
    ny = 362
    panel = "".join(f'<text x="306" y="{ny - 44 + k * 30}" class="s">x{k + 1}</text><path class="ln" d="M330 {ny - 48 + k * 30}H385"/>'
                    f'<circle cx="398" cy="{ny - 48 + k * 30}" r="13" class="box"/><text x="398" y="{ny - 44 + k * 30}" text-anchor="middle" class="s">w{k + 1}</text>'
                    f'<path class="ln" d="M411 {ny - 48 + k * 30}L480 {ny}"/>' for k in range(4))
    panel += (f'<circle cx="500" cy="{ny}" r="20" class="box hl"/><text x="500" y="{ny + 5}" text-anchor="middle" class="t">Σ</text>'
              f'<path class="ln" d="M520 {ny}H546" marker-end="url(#nna)"/><rect x="550" y="{ny - 20}" width="40" height="40" rx="3" class="box"/>'
              f'<text x="570" y="{ny + 5}" text-anchor="middle" class="t">φ</text><path class="ln" d="M590 {ny}H618" marker-end="url(#nna)"/>'
              f'<circle cx="638" cy="{ny}" r="16" class="box"/>')
    aria = L(T("A photo of a dog is reduced to pixels; five pixel values feed a small neural network whose output neuron for dog wins. Below: the neuron you point at, with its inputs, weights, weighted sum and activation function.",
               "Ein Hundefoto wird zu Pixeln; fünf Pixelwerte speisen ein kleines neuronales Netz, dessen Ausgabeneuron für Hund gewinnt. Darunter: das Neuron, auf das man zeigt, mit seinen Eingaben, Gewichten, gewichteter Summe und Aktivierungsfunktion."))
    svg = f'''<svg class="dia nn" viewBox="0 0 860 480" role="group" aria-label="{aria}">
  {_arrow_defs("nna")}
  <image href="{A}assets/ai4se/dog.jpg" x="0" y="40" width="120" height="120"/>
  <image href="{A}assets/ai4se/dog-pixels.png" x="140" y="40" width="120" height="120" style="image-rendering:pixelated"/>
  <text x="60" y="178" text-anchor="middle" class="s">{L(T("photo", "Foto"))}</text>
  <text x="200" y="178" text-anchor="middle" class="s">{L(T("16 × 16 pixels", "16 × 16 Pixel"))}</text>
  {feed}{px}{edges}{nodes}{labels}
  <path class="nn-lead" d="M{xo} {NN_OUT[0] + 12}V258"/>
  <text x="290" y="250" class="s nn-title">{L(T("ONE NEURON", "EIN NEURON"))}</text>
  <rect class="zone line" x="290" y="258" width="430" height="212" rx="4"/>
  <g class="nn-panel">{panel}</g>
</svg>'''
    data = {"px": f"{A}assets/ai4se/dog-pixels.png", "pixels": NN_PIXELS,
            "words": {k: L(v) for k, v in dict(
                one=T("ONE NEURON", "EIN NEURON"), inputs=T("input", "Eingabe"), weights=T("× weight", "× Gewicht"),
                sum=T("weighted sum", "gewichtete Summe"), out=T("output", "Ausgabe"),
                relu=T("ReLU: below 0 → 0", "ReLU: unter 0 → 0"), softmax=T("softmax: share of both outputs", "Softmax: Anteil an beiden Ausgaben"),
                silent=T("stays silent", "bleibt still"), dog=T("dog", "Hund"), cat=T("cat", "Katze"), pixel=T("pixel", "Pixel")).items()}}
    hint = L(T("Point at a neuron (or tap it) to see its calculation.", "Zeigen Sie auf ein Neuron (oder tippen Sie es an), um seine Rechnung zu sehen."))
    return demo("nn", data, f'{dia_scroll(svg)}<button type="button" class="replay mono">↺ {L(T("replay", "nochmal"))}</button>',
                T(f"A neural network sees numbers, not dogs: every pixel is an input, every connection a weight. Each neuron adds up its weighted inputs and passes the result on through an activation function; at the end, the stronger output wins. Training adjusts the weights until “dog” wins for dogs. {hint}",
                  f"Ein neuronales Netz sieht Zahlen, keine Hunde: Jeder Pixel ist eine Eingabe, jede Verbindung ein Gewicht. Jedes Neuron summiert seine gewichteten Eingaben und gibt das Ergebnis über eine Aktivierungsfunktion weiter; am Ende gewinnt die stärkere Ausgabe. Training passt die Gewichte an, bis bei Hunden „Hund“ gewinnt. {hint}"), lang)


def dia_transformer(lang):
    """Slides 100–106: the decoder stack of a GPT, simplified, with what each block does."""
    L = lambda x: x[lang]
    m = 'marker-end="url(#tra)"'
    stack = [
        (T("Output embedding", "Output-Embedding"), T("the text so far, as token vectors", "der bisherige Text als Token-Vektoren"), ""),
        (T("+ positional encoding", "+ Positionskodierung"), T("where in the text each token is", "wo im Text jedes Token steht"), ""),
        ("Masked multi-head attention", T("how the tokens relate to each other", "wie die Tokens zueinander in Beziehung stehen"), "hl"),
        ("Feed forward", T("a plain neural network per token", "ein einfaches neuronales Netz pro Token"), ""),
        ("Linear · Softmax", T("a probability for every possible next token", "eine Wahrscheinlichkeit für jedes mögliche nächste Token"), ""),
    ]
    parts = []
    for k, (name, what, cls) in enumerate(reversed(stack)):
        y = 20 + k * 58
        parts.append(box(110, y, 250, 40, L(name) if isinstance(name, dict) else name, cls=f"box {cls}".strip()))
        parts.append(f'<path class="ln dash" d="M370 {y + 20}H400"/><text x="410" y="{y + 24}">{L(what)}</text>')
        if k < len(stack) - 1:
            parts.append(f'<path class="ln" d="M235 {y + 56}V{y + 42}" {m}/>')
    parts.append('<rect class="zone line" x="96" y="70" width="278" height="114" rx="4"/>')
    parts.append(f'<text x="86" y="124" text-anchor="end" class="t">× N</text><text x="86" y="140" text-anchor="end" class="s">{L(T("layers", "Schichten"))}</text>')
    parts.append('<text x="86" y="154" text-anchor="end" class="s">GPT-3: 96</text>')
    svg = f'<svg class="dia" viewBox="0 0 900 300" role="img" aria-label="{L(T("Simplified transformer decoder: embeddings with positional encoding pass through attention and feed-forward layers, repeated N times; a linear layer and softmax produce next-token probabilities", "Vereinfachter Transformer-Decoder: Embeddings mit Positionskodierung durchlaufen Attention- und Feed-Forward-Schichten, N-mal wiederholt; eine lineare Schicht und Softmax liefern Wahrscheinlichkeiten für das nächste Token"))}">{_arrow_defs("tra")}{"".join(parts)}</svg>'
    return fig(svg, T(f"The core of a GPT, read from bottom to top. Attention is what made the difference in 2017: every token can look at every earlier token and weigh how much it matters. GPT-3 stacks 96 of these layers {ref(8)}.",
                      f"Der Kern eines GPT, von unten nach oben gelesen. Attention war 2017 der entscheidende Schritt: Jedes Token kann auf jedes frühere Token schauen und abwägen, wie wichtig es ist. GPT-3 stapelt 96 dieser Schichten {ref(8)}."), lang)


# Next-token prediction as a small tree: each node lists the five most likely next tokens and where each
# drawable one leads. Every node has a fixed "random" number r: the token whose share of the (temperature-
# reshaped) distribution contains r is drawn. At node 2, r falls on the second-most likely token for
# temperatures from about 0.4 upwards; below that the most likely one wins and the sentence takes the other
# branch. _check_nt() makes sure every token that can be drawn has a continuation.
NT = {
    "en": [([("The", .52), ("I", .14), ("Paris", .11), ("Hey", .06), ("A", .04)], None, {"The": 1}),
           ([("capital", .71), ("city", .12), ("answer", .07), ("correct", .04), ("French", .03)], None, {"capital": 2}),
           ([("of", .41), ("is", .38), ("city", .05), (",", .04), ("France", .02)], .55, {"is": 3, "of": 5}),
           ([("Paris", .81), ("Lyon", .07), ("Toulouse", .04), ("the", .03), ("Berlin", .01)], None, {"Paris": 4}),
           ([("<|END|>", .74), (".", .12), (",", .06), ("and", .04), ("because", .02)], None, {}),
           ([("France", .93), ("the", .02), ("Paris", .01), ("French", .01), (",", .01)], None, {"France": 6}),
           ([("is", .88), (",", .05), ("remains", .03), ("was", .02), ("has", .01)], None, {"is": 3})],
    "de": [([("Die", .48), ("Ich", .16), ("Du", .08), ("Hey", .05), ("Eine", .04)], None, {"Die": 1}),
           ([("Hauptstadt", .69), ("Stadt", .13), ("Antwort", .08), ("korrekte", .04), ("beste", .03)], None, {"Hauptstadt": 2}),
           ([("von", .41), ("ist", .38), ("der", .05), ("Frankreichs", .04), (",", .02)], .55, {"ist": 3, "von": 5}),
           ([("Paris", .81), ("Lyon", .07), ("Toulouse", .04), ("die", .03), ("Berlin", .01)], None, {"Paris": 4}),
           ([("<|END|>", .74), (",", .10), ("denn", .06), ("und", .04), ("weil", .02)], None, {}),
           ([("Frankreich", .93), ("Frankreichs", .02), ("Paris", .01), ("Europa", .01), (",", .01)], None, {"Frankreich": 6}),
           ([("ist", .88), (",", .05), ("heißt", .03), ("lautet", .02), ("war", .01)], None, {"ist": 3})],
}
NT_TEMPS = [k / 10 for k in range(1, 21)]          # the temperature slider: 0.1 … 2.0


def _nt_probs(cands, t):
    """Same as ai4se.js: p_i ∝ p_i^(1/T); the tokens not listed share the remaining mass as one bucket."""
    rest = max(0, 1 - sum(p for _, p in cands))
    w = [p ** (1 / t) for _, p in cands]
    wr = rest ** (1 / t) if rest else 0
    return [v / (sum(w) + wr) for v in w]


def _nt_draw(cands, t, r):
    acc = 0
    for j, p in enumerate(_nt_probs(cands, t)):
        acc += p
        if r < acc:
            return j
    return None


def _check_nt(nodes):
    """Without an own r, a node draws its most likely token at every temperature (r = 60 % of its smallest
    share, which it has at T = 2). Every token that can be drawn must lead somewhere (or be the end token)."""
    out = []
    for cands, r, nxt in nodes:
        r = r if r is not None else round(.6 * _nt_probs(cands, max(NT_TEMPS))[0], 3)
        for t in NT_TEMPS:
            j = _nt_draw(cands, t, r)
            assert j is not None and (cands[j][0] in nxt or cands[j][0] == "<|END|>"), (cands[0], t)
        out.append({"cands": cands, "r": r, "next": nxt})
    return out


def dia_next_token(lang):
    """Slides 12–28: the model only ever picks the next token — by drawing it. Stepped through with a slider;
    the temperature slider reshapes the distribution and can change what is drawn (assets/ai4se.js)."""
    L = lambda x: x[lang]
    prompt = [L(T("System: You are a helpful chatbot!", "System: Du bist ein hilfreicher Chatbot!")),
              L(T("User: What is the capital of France?", "Nutzer: Was ist die Hauptstadt von Frankreich?")),
              L(T("Assistant:", "Assistent:"))]
    data = {"nodes": _check_nt(NT[lang]), "words": {k: L(v) for k, v in dict(
        token=T("token", "Token"), dist=T("probabilities computed", "Wahrscheinlichkeiten berechnet"),
        drawn=T("drawn and appended", "gezogen und angehängt"), notTop=T("not the most likely one", "nicht das wahrscheinlichste"),
        done=T("end token drawn — the answer is complete", "End-Token gezogen — die Antwort ist fertig"),
        sampled=T("drawn", "gezogen"), random=T("random number", "Zufallszahl"), lands=T("lands on", "landet auf"),
        play=T("play", "abspielen"), pause=T("pause", "anhalten")).items()}}
    esc = html.escape
    inner = f'''<div class="nt-stage">
  <div class="nt-prompt"><span class="k mono">{L(T("INPUT PROMPT", "EINGABE-PROMPT"))}</span>
    <p>{esc(prompt[0])}</p><p>{esc(prompt[1])}</p><p>{esc(prompt[2])} <span class="nt-out"></span><span class="nt-cur" aria-hidden="true">▌</span></p>
    <span class="nt-loop mono">↺ {L(T("the drawn token is appended — and the whole text goes in again", "das gezogene Token wird angehängt — und der ganze Text geht erneut hinein"))}</span></div>
  <div class="nt-model"><b>GPT</b><span class="mono">{L(T("transformer", "Transformer"))}</span></div>
  <div class="nt-probs"><span class="k mono">{L(T("PROBABILITY OF THE NEXT TOKEN", "WAHRSCHEINLICHKEIT DES NÄCHSTEN TOKENS"))}</span><ol class="bars mono"></ol>
    <div class="nt-draw"><span class="k mono">{L(T("THE DRAW: A RANDOM NUMBER BETWEEN 0 AND 1", "DIE ZIEHUNG: EINE ZUFALLSZAHL ZWISCHEN 0 UND 1"))}</span>
      <div class="strip"><i class="mark" aria-hidden="true"></i></div><span class="nt-r mono"></span></div></div>
</div>{controls(lang, temperature=True)}'''
    return demo("nt", data, inner, T(
        "An LLM answers one token at a time: it computes a probability for every possible next token, one is <i>drawn</i> — like a random number landing on one of the shares — appended, and the whole text goes in again, until an end token is drawn. Usually the most likely token wins, but not always: in the third step the second one is drawn. Turn the temperature down and the most likely token wins every time — the answer changes. (The random numbers are fixed here so that the demo can be replayed.)",
        "Ein LLM antwortet Token für Token: Es berechnet für jedes mögliche nächste Token eine Wahrscheinlichkeit, eines wird <i>gezogen</i> — wie eine Zufallszahl, die auf einem der Anteile landet —, angehängt, und der ganze Text geht erneut hinein, bis ein End-Token gezogen wird. Meist gewinnt das wahrscheinlichste Token, aber nicht immer: Im dritten Schritt wird das zweite gezogen. Mit niedriger Temperatur gewinnt jedes Mal das wahrscheinlichste — und die Antwort ändert sich. (Die Zufallszahlen sind hier fest, damit sich die Demo wiederholen lässt.)"), lang)


def dia_formalize(lang):
    """Slide 46: from free text to a model — few-shot prompt, LLM, parser decides."""
    L = lambda x: x[lang]
    m, ma = 'marker-end="url(#fma)"', 'marker-end="url(#fmaa)"'
    svg = f'''<svg class="dia" viewBox="0 0 860 210" role="img" aria-label="{L(T("Pipeline: free text from the user is extended with examples (few-shot), the LLM writes a textual model, a parser accepts it or sends it back", "Pipeline: Freitext des Nutzers wird mit Beispielen erweitert (Few-Shot), das LLM schreibt ein textuelles Modell, ein Parser nimmt es an oder schickt es zurück"))}">
  {_arrow_defs("fma")}
  <rect class="box" x="0" y="50" width="170" height="70" rx="3"/>
  <text x="12" y="72" class="s">{L(T("FREE TEXT", "FREITEXT"))}</text>
  <text x="12" y="94">{L(T("“Design a library", "„Entwirf ein Bücherei-"))}</text><text x="12" y="110">{L(T("management system”", "verwaltungssystem“"))}</text>
  <path class="ln" d="M170 85H206" {m}/>
  {box(210, 60, 110, 50, "Few-shot", L(T("+ examples", "+ Beispiele")))}
  {box(210, 146, 110, 44, L(T("Examples", "Beispiele")), "(q, a)ᵢ")}
  <path class="ln" d="M265 146V114" {m}/>
  <path class="ln" d="M320 85H356" {m}/>
  {box(360, 60, 110, 50, "LLM", L(T("writes it", "schreibt es")), cls="box hl")}
  <path class="ln" d="M470 85H506" {m}/>
  {box(510, 60, 120, 50, L(T("Textual model", "Textuelles Modell")), "CD4A · SysML v2")}
  <path class="ln" d="M630 85H666" {m}/>
  {box(670, 60, 100, 50, "Parser", L(T("valid?", "gültig?")))}
  <path class="ln hl" d="M770 85H806" {ma}/><text x="814" y="90" class="t" style="fill:var(--accent)">✓</text>
  <path class="ln dash" d="M720 110V140H415V114" {m}/>
  <text x="566" y="156" text-anchor="middle" class="s">{L(T("✗ invalid: try again, with the parser's error", "✗ ungültig: neuer Versuch, mit der Fehlermeldung des Parsers"))}</text>
</svg>'''
    return fig(svg, T("Free text becomes a model in a modelling language. Few-shot examples teach the LLM the language; a parser — not the LLM — decides whether the result can be used.",
                      "Aus Freitext wird ein Modell in einer Modellierungssprache. Few-Shot-Beispiele bringen dem LLM die Sprache bei; ein Parser — nicht das LLM — entscheidet, ob das Ergebnis verwendbar ist."), lang)


# Grammar masking, stepped: a (much simplified) CD4A grammar as an automaton with a stack for the braces.
# States: 0 start · 1 after "classdiagram" · 2 after the diagram name · 3 in the diagram · 4 after "class" ·
# 5 after the class name · 6 in the class · 7 after a type · 8 after an attribute name · 9 all closed · 10 done.
GM_STEPS = [  # (from, to, candidates (token, p, allowed by the grammar), chosen)
    (0, 1, [("Here", .38, 0), ("classdiagram", .30, 1), ("```", .16, 0), ("Sure", .10, 0), ("class", .06, 0)], "classdiagram"),
    (1, 2, [("Shop", .52, 1), ("{", .18, 0), (":", .12, 0), ('"Shop"', .10, 0), ("Online", .08, 1)], "Shop"),
    (2, 3, [("{", .64, 1), ("(", .17, 0), (":", .11, 0), ("->", .05, 0), (";", .03, 0)], "{"),
    (3, 4, [("class", .46, 1), ("Order", .24, 0), ("table", .14, 0), ("<!--", .09, 0), ("}", .07, 1)], "class"),
    (4, 5, [("Order", .78, 1), ("{", .10, 0), ("(", .06, 0), (":", .04, 0), ("Orders", .02, 1)], "Order"),
    (5, 6, [("(", .41, 0), ("{", .39, 1), (":", .10, 0), ("->", .06, 0), (";", .04, 0)], "{"),
    (6, 7, [("-", .34, 0), ("int", .30, 1), ("+", .14, 0), ("String", .12, 1), ("}", .10, 1)], "int"),
    (7, 8, [("id", .72, 1), (":", .12, 0), ("=", .08, 0), ("[", .05, 0), (";", .03, 0)], "id"),
    (8, 6, [(",", .38, 0), (";", .36, 1), ("=", .12, 0), (":", .08, 0), ("}", .06, 0)], ";"),
    (6, 3, [("}", .48, 1), ("String", .22, 1), ("int", .14, 1), ("-", .10, 0), ("<!--", .06, 0)], "}"),
    (3, 9, [("<|END|>", .44, 0), ("}", .31, 1), ("class", .17, 1), ("```", .05, 0), ("Here", .03, 0)], "}"),
    (9, 10, [("<|END|>", .58, 1), ("```", .20, 0), ("This", .14, 0), ("}", .05, 0), ("class", .03, 0)], "<|END|>"),
]


def dia_grammar_mask(lang):
    """Slides 48–52: grammar masking, as a stepped animation (assets/ai4se.js). The automaton is
    static SVG; the script highlights the current state and the transition taken."""
    L = lambda x: x[lang]
    S = {0: (40, 64), 1: (150, 64), 2: (260, 64), 3: (370, 64), 4: (480, 64), 5: (590, 64), 6: (700, 64),
         7: (810, 64), 8: (810, 150), 9: (370, 150)}
    E = [(0, 1, "classdiagram"), (1, 2, L(T("name", "Name"))), (2, 3, "{"), (3, 4, "class"), (4, 5, L(T("name", "Name"))), (5, 6, "{"),
         (6, 7, L(T("type", "Typ"))), (7, 8, L(T("name", "Name"))), (8, 6, ";"), (6, 3, "}"), (3, 9, "}")]
    r = 15
    parts = [_arrow_defs("gma"), f'<path class="ln" d="M4 64H{40 - r - 3}" marker-end="url(#gma)"/>']
    for a, b, lab in E:
        (x1, y1), (x2, y2) = S[a], S[b]
        anchor = "middle"
        if (a, b) == (6, 3):     # back from the class to the diagram: an arc above the row
            d, lx, ly = f"M{x1 - 8} {y1 - r + 2}C{x1 - 60} 6 {x2 + 60} 6 {x2 + 8} {y2 - r + 2}", (x1 + x2) / 2, 16
        elif (a, b) == (8, 6):
            d, lx, ly = f"M{x1 - 11} {y1 - 11}L{x2 + 11} {y2 + 11}", (x1 + x2) / 2 - 10, (y1 + y2) / 2 + 12
        elif x1 == x2:
            d, lx, ly, anchor = f"M{x1} {y1 + r}V{y2 - r - 3}", x1 + 8, (y1 + y2) / 2 + 4, "start"
        else:
            d, lx, ly = f"M{x1 + r} {y1}H{x2 - r - 3}", (x1 + x2) / 2, y1 - 8
        parts.append(f'<g class="gm-e" data-e="{a}-{b}"><path class="ln" d="{d}" marker-end="url(#gma)"/>'
                     f'<text x="{lx}" y="{ly}" text-anchor="{anchor}">{html.escape(lab)}</text></g>')
    parts.append(f'<g class="gm-e" data-e="9-10"><path class="ln" d="M{370 - r} 150H286" marker-end="url(#gma)"/><text x="320" y="142" text-anchor="middle">{html.escape("<|END|>")}</text></g>')
    parts.append(f'<g class="gm-s" data-s="10"><text x="276" y="154" text-anchor="end" class="t">✓ {L(T("parses", "parst"))}</text></g>')
    names = {0: T("start", "Start"), 3: T("in the diagram", "im Diagramm"), 6: T("in a class", "in einer Klasse"), 9: T("all closed", "alles zu")}
    for s, (x, y) in S.items():
        ring = f'<circle class="box" cx="{x}" cy="{y}" r="{r - 4}"/>' if s == 9 else ""
        cap = f'<text x="{x}" y="{y + r + 14}" text-anchor="middle" class="s">{L(names[s])}</text>' if s in names else ""
        parts.append(f'<g class="gm-s" data-s="{s}"><circle class="box" cx="{x}" cy="{y}" r="{r}"/>{ring}'
                     f'<text x="{x}" y="{y + 4}" text-anchor="middle" class="s">{s}</text>{cap}</g>')
    svg = (f'<svg class="dia gm-auto" viewBox="0 0 860 186" role="img" aria-label="{L(T("The grammar as an automaton: from the start, classdiagram, a name and an opening brace lead into the diagram; class, a name and a brace into a class; type, name and semicolon repeat; closing braces lead back out, and only when all are closed may the model end.", "Die Grammatik als Automat: Vom Start führen classdiagram, ein Name und eine öffnende Klammer ins Diagramm; class, ein Name und eine Klammer in eine Klasse; Typ, Name und Semikolon wiederholen sich; schließende Klammern führen wieder hinaus, und erst wenn alle geschlossen sind, darf das Modell enden."))}">'
           + "".join(parts) + '</svg>')
    allowed = {0: "classdiagram", 1: T("a name", "ein Name"), 2: "{", 3: "class · }", 4: T("a name", "ein Name"), 5: "{",
               6: T("a type · }", "ein Typ · }"), 7: T("a name", "ein Name"), 8: ";", 9: "<|END|>", 10: "—"}
    data = {"steps": [{"from": a, "to": b, "cands": [[t, p, bool(ok)] for t, p, ok in c], "pick": pick} for a, b, c, pick in GM_STEPS],
            "allowed": {s: (L(v) if isinstance(v, dict) else v) for s, v in allowed.items()},
            "words": {k: L(v) for k, v in dict(
                p0=T("1 · The LLM proposes the next token. It knows nothing about the grammar.", "1 · Das LLM schlägt das nächste Token vor. Von der Grammatik weiß es nichts."),
                p1=T("2 · The grammar filters: every token that cannot follow here is removed, the rest is rescaled (the old share stays faint).", "2 · Die Grammatik filtert: Jedes Token, das hier nicht folgen kann, wird gestrichen, der Rest neu skaliert (der alte Anteil bleibt blass)."),
                p2=T("3 · The most likely remaining token is appended; the automaton moves on.", "3 · Das wahrscheinlichste verbleibende Token wird angehängt; der Automat geht weiter."),
                would=T("Without the mask the model would have written", "Ohne Maske hätte das Modell geschrieben"),
                masked=T("filtered", "gefiltert"), chosen=T("chosen", "gewählt"),
                agree=T("Here the most likely token was allowed anyway.", "Hier war das wahrscheinlichste Token ohnehin erlaubt."),
                allowed=T("allowed here", "hier erlaubt"), stack=T("open braces", "offene Klammern"), none=T("none", "keine"),
                step=T("token", "Token"), of=T("of", "von"), play=T("play", "abspielen"), pause=T("pause", "anhalten")).items()}}
    inner = f'''<div class="gm-stage">
  <div class="gm-code"><span class="k mono">{L(T("THE MODEL SO FAR", "DAS MODELL BIS HIER"))}</span><pre class="mono"><code></code><span class="nt-cur" aria-hidden="true">▌</span></pre></div>
  <div class="gm-cands"><span class="k mono">{L(T("NEXT-TOKEN CANDIDATES", "KANDIDATEN FÜR DAS NÄCHSTE TOKEN"))}</span><ol class="bars mono"></ol><p class="gm-phase mono" aria-live="polite"></p></div>
  <div class="gm-grammar"><span class="k mono">{L(T("THE GRAMMAR (SIMPLIFIED CD4A) AS AN AUTOMATON", "DIE GRAMMATIK (VEREINFACHTES CD4A) ALS AUTOMAT"))}</span>
    {dia_scroll(svg)}
    <p class="gm-status mono"><span class="gm-allowed"></span><span class="gm-stack"></span></p></div>
</div>{controls(lang)}'''
    return demo("gm", data, inner, T(
        f"Constrained decoding, token by token: the LLM proposes, the grammar filters, then a token is chosen. The grammar is checked by an automaton; for nested braces it needs a stack that remembers what is still open. That is exactly where LLMs are weak — even ChatGPT has trouble matching brackets in long texts {ref(8)}. With the mask the model cannot stop before every brace is closed.",
        f"Constrained Decoding, Token für Token: Das LLM schlägt vor, die Grammatik filtert, dann wird ein Token gewählt. Geprüft wird die Grammatik von einem Automaten; für verschachtelte Klammern braucht er einen Stapel, der sich merkt, was noch offen ist. Genau dort sind LLMs schwach — selbst ChatGPT hat Mühe, Klammern in langen Texten richtig zu schließen {ref(8)}. Mit der Maske kann das Modell nicht aufhören, bevor jede Klammer geschlossen ist."), lang)


def masking_table(lang):
    """Slide 53 / [NRR24]: share of parsing CD4A models, without and with grammar masking."""
    L = lambda x: x[lang]
    rows = [("Llama 3 8B · 4-bit", 416, 991, 5.71, 918, 991, 74.10), ("Phi-3 Mini · 4-bit", 357, 976, 4.63, 849, 976, 138.29),
            ("Gemma 7B · 4-bit", 2, 658, 2.46, 612, 658, 54.20), ("Mistral 7B · 3-bit", 190, 905, 4.89, 836, 905, 73.59)]
    fmt = (lambda n: f"{n:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")) if lang == "de" else (lambda n: f"{n:,.1f}")
    body = "".join(f'<tr><td>{name}</td><td class="n">{fmt(a / b * 100)} %</td><td class="n hl">{fmt(c / d * 100)} %</td><td class="n faint">{fmt(t0)} s → {fmt(t1)} s</td></tr>'
                   for name, a, b, t0, c, d, t1 in rows)
    head = f'<tr><th>{L(T("Model", "Modell"))}</th><th class="n">{L(T("without", "ohne"))}</th><th class="n">{L(T("with masking", "mit Masking"))}</th><th class="n">{L(T("time per model", "Zeit pro Modell"))}</th></tr>'
    return (f'<figure class="media art-fig"><div class="tbl-wrap"><table class="tbl mono">{head}{body}</table></div>'
            f'<figcaption class="mono">{L(T("Share of generated class diagrams that parse, for about 1,000 modelling tasks from a third-semester exam. For comparison, GPT-4o without masking: 76 % (100 tasks). Validity costs time.", "Anteil der erzeugten Klassendiagramme, die parsen, für rund 1.000 Modellierungsaufgaben aus einer Klausur im dritten Semester. Zum Vergleich GPT-4o ohne Masking: 76 % (100 Aufgaben). Gültigkeit kostet Zeit."))} {cite("NRR24")}</figcaption></figure>')


def dia_embeddings(lang):
    """Slides 55 / 56: word embeddings in two dimensions. The vectors sit at odd angles on purpose:
    the directions that carry meaning (royalty, gender) are not the axes."""
    L = lambda x: x[lang]
    cx, cy, u = 560, 160, 110
    words = [("King", .95, .72, "start", 12, 4), ("Queen", -.37, .87, "start", 8, 24), ("Man", .70, -.45, "start", 12, 12),
             ("Woman", -.62, -.30, "end", -12, 14), ("Princess", -.62, 1.02, "end", -14, 2)]
    P = {w: (cx + x * u, cy - y * u) for w, x, y, *_ in words}
    groups = []
    for k, (w, x, y, anchor, dx, dy) in enumerate(words):
        hl = w == "Princess"
        px, py = P[w]
        groups.append(f'<g class="w{" hl" if hl else ""}">'
                      f'<text x="10" y="{50 + k * 38}" class="t">{w}</text><text x="120" y="{50 + k * 38}" class="v">[ {x:+.2f}, {y:+.2f} ]</text>'
                      f'<path class="ln vec" d="M{cx} {cy}L{px:.1f} {py:.1f}" marker-end="url(#ema{"a" if hl else ""})"/>'
                      f'<text x="{px + dx:.1f}" y="{py + dy:.1f}" text-anchor="{anchor}" class="t">{w}</text></g>')
    m = lambda a, b, cls, mk="": f'<path class="ln {cls}" d="M{P[a][0]:.1f} {P[a][1]:.1f}L{P[b][0]:.1f} {P[b][1]:.1f}"{mk}/>'
    rel = (m("Man", "King", "hl dash", ' marker-end="url(#emaa)"') + m("Woman", "Queen", "hl dash", ' marker-end="url(#emaa)"')
           + m("Man", "Woman", "dash") + m("King", "Queen", "dash")
           + f'<text x="{(P["Man"][0] + P["King"][0]) / 2 + 12:.0f}" y="{(P["Man"][1] + P["King"][1]) / 2:.0f}" class="s a">+ {L(T("royalty", "Königlichkeit"))}</text>'
           + f'<text x="{(P["Man"][0] + P["Woman"][0]) / 2:.0f}" y="{(P["Man"][1] + P["Woman"][1]) / 2 + 18:.0f}" text-anchor="middle" class="s">{L(T("gender", "Geschlecht"))}</text>')
    svg = f'''<svg class="dia emb" viewBox="0 0 860 300" role="img" aria-label="{L(T("Words as vectors in two dimensions, at odd angles: king, queen, man, woman. The step from man to king is the same as from woman to queen; princess lies close to queen", "Wörter als Vektoren in zwei Dimensionen, in schiefen Winkeln: King, Queen, Man, Woman. Der Schritt von Man zu King ist derselbe wie von Woman zu Queen; Princess liegt nahe bei Queen"))}">
  {_arrow_defs("ema")}
  <path class="ln axis" d="M{cx - 190} {cy}H{cx + 190}"/><path class="ln axis" d="M{cx} {cy + 130}V{cy - 150}"/>
  <text x="{cx + 190}" y="{cy + 16}" text-anchor="end" class="s">{L(T("dimension 1", "Dimension 1"))}</text>
  <text x="{cx + 8}" y="{cy - 140}" class="s">{L(T("dimension 2", "Dimension 2"))}</text>
  {rel}{"".join(groups)}
  <ellipse cx="{(P["Princess"][0] + P["Queen"][0]) / 2:.0f}" cy="{(P["Princess"][1] + P["Queen"][1]) / 2:.0f}" rx="26" ry="17" style="fill:none;stroke:var(--accent);stroke-dasharray:3 4;opacity:.7"/>
  <text x="{P["Princess"][0] - 14:.0f}" y="{P["Princess"][1] + 18:.0f}" text-anchor="end" class="s a">{L(T("similar", "ähnlich"))}</text>
</svg>'''
    return fig(svg, T("Embeddings turn words and texts into vectors. Meaning does not sit in the axes but in directions: the step from “man” to “king” is the same as from “woman” to “queen” — king − man + woman ≈ queen. And “princess” lands right next to “queen”. Real models use thousands of dimensions — OpenAI’s text-embedding-3 has 3,072 — but the idea stays the same: similar meaning, nearby vectors.",
                      "Embeddings machen aus Wörtern und Texten Vektoren. Die Bedeutung steckt nicht in den Achsen, sondern in Richtungen: Der Schritt von „Man“ zu „King“ ist derselbe wie von „Woman“ zu „Queen“ — King − Man + Woman ≈ Queen. Und „Princess“ landet direkt neben „Queen“. Echte Modelle nutzen Tausende Dimensionen — OpenAIs text-embedding-3 hat 3.072 —, aber die Idee bleibt: ähnliche Bedeutung, benachbarte Vektoren."), lang)


def dia_rag(lang):
    """Slide 59: retrieval-augmented generation."""
    L = lambda x: x[lang]
    m, ma = 'marker-end="url(#rga)"', 'marker-end="url(#rgaa)"'
    num = lambda x, y, n: f'<text x="{x}" y="{y}" class="s a">0{n}</text>'
    svg = f'''<svg class="dia" viewBox="0 0 860 220" role="img" aria-label="{L(T("RAG: the question is embedded, compared with embedded entries of a knowledge base, and the closest snippets are handed to the LLM together with the question", "RAG: Die Frage wird eingebettet, mit eingebetteten Einträgen einer Wissensbasis verglichen, und die ähnlichsten Ausschnitte gehen zusammen mit der Frage an das LLM"))}">
  {_arrow_defs("rga")}
  {box(0, 30, 130, 50, L(T("Question", "Frage")), L(T("from the user", "vom Nutzer")))}{num(0, 22, 1)}
  <path class="ln" d="M130 55H186" {m}/>
  {box(190, 30, 130, 50, "Embedding", L(T("question → vector", "Frage → Vektor")))}{num(190, 22, 2)}
  <path class="ln" d="M255 80V126" {m}/>
  {box(190, 130, 130, 60, L(T("Knowledge base", "Wissensbasis")), L(T("embedded documents", "eingebettete Dokumente")))}{num(190, 210, 3)}
  <path class="ln" d="M320 160H376" {m}/>
  {box(380, 130, 130, 60, L(T("Snippets", "Ausschnitte")), L(T("nearest vectors", "nächste Vektoren")))}{num(380, 210, 4)}
  <path class="ln" d="M445 130V82" {m}/>
  <path class="ln" d="M320 55H426" />
  {box(380, 30, 130, 50, L(T("Prompt", "Prompt")), L(T("question + snippets", "Frage + Ausschnitte")))}
  <path class="ln" d="M510 55H566" {m}/>
  {box(570, 30, 120, 50, "LLM", L(T("answers", "antwortet")), cls="box hl")}{num(570, 22, 5)}
  <path class="ln hl" d="M690 55H736" {ma}/>
  {box(740, 30, 120, 50, L(T("Answer", "Antwort")), L(T("with sources", "mit Quellen")))}
</svg>'''
    return fig(svg, T("Retrieval-augmented generation lets an LLM answer from knowledge it was never trained on — lecture material, specifications, publications. The search is semantic: users describe their problem and find the right passage without knowing its terms. This is how <a href=\"projects-se-chatty.html\">SE-Chatty</a> works.",
                      "Retrieval-Augmented Generation lässt ein LLM aus Wissen antworten, auf das es nie trainiert wurde — Vorlesungsmaterial, Spezifikationen, Publikationen. Die Suche ist semantisch: Nutzer beschreiben ihr Problem und finden die passende Stelle, ohne ihre Begriffe zu kennen. So funktioniert <a href=\"projects-se-chatty.html\">SE-Chatty</a>."), lang)


def dia_agent(lang):
    """An agent: the LLM decides, acts through a tool, looks at the result — in a loop until the goal is met."""
    L = lambda x: x[lang]
    m, ma = 'marker-end="url(#aga)"', 'marker-end="url(#agaa)"'
    svg = f'''<svg class="dia" viewBox="0 0 860 236" role="img" aria-label="{L(T("An agent: a goal goes to the LLM, which decides on the next step, acts through a tool and looks at the result, in a loop, until the goal is reached", "Ein Agent: Ein Ziel geht an das LLM, das den nächsten Schritt wählt, über ein Werkzeug handelt und das Ergebnis betrachtet, in einer Schleife, bis das Ziel erreicht ist"))}">
  {_arrow_defs("aga")}
  {box(0, 86, 140, 50, L(T("Goal", "Ziel")), L(T("“fix the failing test”", "„behebe den roten Test“")))}
  <path class="ln" d="M140 111H206" {m}/>
  {box(210, 86, 150, 50, "LLM", L(T("decides the next step", "wählt den nächsten Schritt")), cls="box hl")}
  <path class="ln hl" d="M285 86V45H446" {ma}/>
  {box(450, 20, 160, 50, L(T("Act", "Handeln")), L(T("call a tool", "ein Werkzeug aufrufen")))}
  <path class="ln hl" d="M530 70V148" {ma}/>
  {box(450, 152, 160, 50, L(T("Observe", "Beobachten")), L(T("read the result", "das Ergebnis lesen")))}
  <path class="ln hl" d="M450 177H285V140" {ma}/>
  <text x="392" y="115" text-anchor="middle" class="s a">↻ {L(T("loop", "Schleife"))}</text>
  <path class="ln dash" d="M610 45H656"/>
  <text x="666" y="30" class="s">{L(T("TOOLS", "WERKZEUGE"))}</text>
  <text x="666" y="49">{L(T("read and write files", "Dateien lesen und schreiben"))}</text><text x="666" y="67">{L(T("run code and tests", "Code und Tests ausführen"))}</text>
  <text x="666" y="85">{L(T("search the web", "im Web suchen"))}</text><text x="666" y="103">{L(T("call APIs", "APIs aufrufen"))}</text>
  <path class="ln" d="M220 136L150 196" {m}/>
  <text x="120" y="210" text-anchor="middle" class="t">{L(T("done", "fertig"))}</text>
  <text x="120" y="226" text-anchor="middle" class="s">{L(T("when the goal is reached", "wenn das Ziel erreicht ist"))}</text>
</svg>'''
    return fig(svg, T("An agent is a loop: the LLM chooses a step, a tool carries it out, the result goes back to the LLM. Who decides the next step is what separates an agent from a fixed workflow.",
                      "Ein Agent ist eine Schleife: Das LLM wählt einen Schritt, ein Werkzeug führt ihn aus, das Ergebnis geht zurück an das LLM. Wer den nächsten Schritt bestimmt, unterscheidet einen Agenten von einem festen Workflow."), lang)


def dia_harness(lang):
    """Agent = model + harness: everything around the model that makes it a working agent."""
    L = lambda x: x[lang]
    m = 'marker-end="url(#hna)"'
    parts = [
        (190, 44, T("Instructions", "Anweisungen"), T("system prompt, rules", "System-Prompt, Regeln")),
        (355, 44, T("Tools", "Werkzeuge"), T("files, terminal, web", "Dateien, Terminal, Web")),
        (520, 44, T("The loop", "Die Schleife"), T("act, observe, repeat", "handeln, prüfen, weiter")),
        (190, 210, T("Context & memory", "Kontext & Gedächtnis"), T("what the model sees", "was das Modell sieht")),
        (355, 210, T("Guardrails", "Leitplanken"), T("permissions, sandbox", "Rechte, Sandbox")),
        (520, 210, T("Checks", "Prüfungen"), T("tests, linter, parser", "Tests, Linter, Parser")),
    ]
    comp = "".join(box(x, y, 150, 46, L(a), L(b)) for x, y, a, b in parts)
    svg = f'''<svg class="dia" viewBox="0 0 860 290" role="img" aria-label="{L(T("A harness around the model: instructions, tools, the agent loop, context and memory, guardrails and checks. The user gives the task; the harness acts on the environment", "Ein Harness um das Modell: Anweisungen, Werkzeuge, die Agenten-Schleife, Kontext und Gedächtnis, Leitplanken und Prüfungen. Der Nutzer gibt die Aufgabe; der Harness wirkt auf die Umgebung"))}">
  {_arrow_defs("hna")}
  <rect class="zone" x="172" y="26" width="516" height="246" rx="6"/>
  <text x="184" y="18" class="s a">HARNESS — {L(T("everything except the model", "alles außer dem Modell"))}</text>
  {comp}
  {box(355, 124, 150, 54, L(T("Model", "Modell")), "LLM", cls="box hl")}
  <path class="ln dash" d="M430 90V122"/><path class="ln dash" d="M430 180V208"/>
  <path class="ln dash" d="M330 90L370 122"/><path class="ln dash" d="M530 90L490 122"/>
  <path class="ln dash" d="M330 208L370 180"/><path class="ln dash" d="M530 208L490 180"/>
  {box(0, 126, 130, 50, L(T("You", "Sie")), L(T("the task", "die Aufgabe")))}
  <path class="ln" d="M130 151H168" {m}/>
  <path class="ln" d="M692 151H726" marker-start="url(#hna)" {m}/>
  {box(730, 126, 130, 50, L(T("Environment", "Umgebung")), L(T("code, files, apps", "Code, Dateien, Apps")))}
</svg>'''
    return fig(svg, T("Agent = model + harness. The model brings the language and the judgement; the harness brings everything else. Claude Code, Codex and Cursor are harnesses — with the same model inside they can still perform very differently.",
                      "Agent = Modell + Harness. Das Modell bringt Sprache und Urteilsvermögen, der Harness alles andere. Claude Code, Codex und Cursor sind Harnesses — mit demselben Modell darin können sie trotzdem sehr unterschiedlich gut arbeiten."), lang)


def dia_ai_mde(lang):
    """Slide 67: AI-driven MDE — the LLM writes the model, a deterministic generator the app."""
    L = lambda x: x[lang]
    m, ma = 'marker-end="url(#ama)"', 'marker-end="url(#amaa)"'
    svg = f'''<svg class="dia" viewBox="0 0 860 190" role="img" aria-label="{L(T("AI-driven MDE: an informal domain description becomes a class diagram via few-shot prompting and an LLM; a deterministic generator turns the model into a complete application", "AI-Driven MDE: Aus einer informellen Domänenbeschreibung wird per Few-Shot-Prompting und LLM ein Klassendiagramm; ein deterministischer Generator macht daraus eine vollständige Anwendung"))}">
  {_arrow_defs("ama")}
  <rect class="zone" x="140" y="30" width="250" height="110" rx="4"/><text x="152" y="22" class="s a">AI-DRIVEN</text>
  <rect class="zone" x="530" y="30" width="330" height="110" rx="4"/><text x="542" y="22" class="s">{L(T("DETERMINISTIC MDE", "DETERMINISTISCHES MDE"))}</text>
  {box(0, 60, 116, 50, L(T("Description", "Beschreibung")), L(T("informal", "informell")))}
  <path class="ln" d="M116 85H156" {m}/>
  {box(160, 60, 90, 50, "Few-shot")}
  <path class="ln" d="M250 85H270" {m}/>
  {box(274, 60, 100, 50, "LLM", cls="box hl")}
  <path class="ln hl" d="M374 85H412" {ma}/>
  {box(416, 55, 100, 60, L(T("Model", "Modell")), L(T("class diagram", "Klassendiagramm")), cls="box hl")}
  <path class="ln" d="M516 85H556" {m}/>
  {box(560, 60, 120, 50, "Generator", "MontiGem")}
  <path class="ln" d="M680 85H716" {m}/>
  {box(720, 60, 124, 50, L(T("Application", "Anwendung")), L(T("web app", "Web-App")))}
  <text x="466" y="160" text-anchor="middle" class="s">{L(T("the model can be read, checked and changed", "das Modell lässt sich lesen, prüfen und ändern"))}</text>
</svg>'''
    return fig(svg, T("The LLM only does what it is good at — turning language into a model. Everything after the model is deterministic, tested generator code. The model in between is the point where people can check what the AI understood.",
                      "Das LLM macht nur, was es gut kann — Sprache in ein Modell übersetzen. Alles nach dem Modell ist deterministischer, getesteter Generator-Code. Das Modell dazwischen ist die Stelle, an der Menschen prüfen können, was die KI verstanden hat."), lang)


def glossary(lang):
    """A handful of words that come up whenever LLMs are discussed."""
    L = lambda x: x[lang]
    terms = [
        ("Token", T(f"A piece of text the model reads and writes: a word, part of a word or a punctuation mark. GPT-3 knows about 50,000 different tokens; only a few thousand of them are whole words {ref(8)}.",
                    f"Ein Stück Text, das das Modell liest und schreibt: ein Wort, ein Wortteil oder ein Satzzeichen. GPT-3 kennt rund 50.000 verschiedene Tokens; nur einige Tausend davon sind ganze Wörter {ref(8)}.")),
        ("Prompt", T("Everything the model gets as input: the instructions (system prompt), the conversation so far, attached documents.",
                     "Alles, was das Modell als Eingabe bekommt: die Anweisungen (System-Prompt), das bisherige Gespräch, angehängte Dokumente.")),
        (T("Context window", "Kontextfenster"), T("How many tokens the model can take in at once. Whatever does not fit, it does not see.",
                                                "Wie viele Tokens das Modell auf einmal aufnehmen kann. Was nicht hineinpasst, sieht es nicht.")),
        (T("Temperature", "Temperatur"), T("How adventurous the choice of the next token is. At 0 it is always the most likely one; higher values bring variety — and more mistakes.",
                                           "Wie mutig das nächste Token gewählt wird. Bei 0 immer das wahrscheinlichste; höhere Werte bringen Abwechslung — und mehr Fehler.")),
        ("Few-shot", T("Examples of questions and answers in the prompt that show the model what is wanted — without training it again.",
                       "Beispiele für Fragen und Antworten im Prompt, die dem Modell zeigen, was gewünscht ist — ohne es neu zu trainieren.")),
        ("Fine-tuning", T("Training an existing model further on one’s own data. Needs good data and hardware, and the result stays fixed until the next training.",
                          "Ein bestehendes Modell auf eigenen Daten weitertrainieren. Braucht gute Daten und Hardware, und das Ergebnis steht fest bis zum nächsten Training.")),
    ]
    return '<dl class="gloss">' + "".join(f'<dt class="mono">{L(k) if isinstance(k, dict) else k}</dt><dd>{L(v)}</dd>' for k, v in terms) + "</dl>"


def definition(term, short, lang):
    """A definition set apart: the term in mono, one sentence."""
    return f'<div class="defn"><span class="mono">{term[lang] if isinstance(term, dict) else term}</span><p>{short[lang]}</p></div>'


# =====================================================================
# The article
# =====================================================================

def body(lang, A):
    L = lambda x: x[lang]
    gpts = [("CD4A Model Creator", "https://chatgpt.com/g/g-sRnmDgQvW-cd4a-class-diagram-creator", T("class diagrams in CD4A", "Klassendiagramme in CD4A")),
            ("SysML v2 Model Creator", "https://chatgpt.com/g/g-3DkGCDlNM-sysml-v2-model-creator", T("SysML v2 models", "SysML-v2-Modelle")),
            ("MontiCore Expert", "https://chatgpt.com/g/g-Pgayc5wzx-monticore-expert", T("questions on MontiCore", "Fragen zu MontiCore"))]
    tries = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{n} ↗</a><span class="mono faint">{L(d)}</span></li>' for n, u, d in gpts)
    kennel = ('classdiagram ' + L(T("KennelModel", "HundehüttenModell")) + ' {\n  class ' + L(T("Kennel", "Hundehütte")) + ' {\n    String ' + L(T("location", "standort")) + ';\n    double ' + L(T("width", "breite")) + ';\n    double ' + L(T("length", "länge")) + ';\n    double ' + L(T("height", "höhe")) + ';\n  }\n  class ' + L(T("Dog", "Hund")) + ' {\n    String name;\n    String ' + L(T("breed", "rasse")) + ';\n    int ' + L(T("age", "alter")) + ';\n  }\n  association [1] ' + L(T("Kennel", "Hundehütte")) + ' -> (' + L(T("resident", "bewohner")) + ') ' + L(T("Dog", "Hund")) + ' [*];\n}')
    S = []          # (id, level, heading, html): level 2 = chapter (listed at the top), 3 = sub chapter, 0 = no heading
    S.append(("intro", 0, None, L(T(
        f"""<p>Artificial intelligence is not a new topic. As early as 1950, Alan Turing introduced what would later be called the Turing test in his paper <i>Computing Machinery and Intelligence</i> {ref(1)}. Less than a decade later, the first neural networks followed {ref(2)}.</p>
<blockquote class="epigraph"><p>I propose to consider the question, “Can machines think?”</p><footer class="mono">Alan M. Turing · Computing Machinery and Intelligence, 1950</footer></blockquote>
<p>It took several more decades until 2017 laid the foundations for large language models (LLMs) {ref(3)}. Because they handle natural language so well, LLMs can be used for almost anything. You need not be an AI specialist or a computer scientist to work with them: an LLM places hardly any restrictions on its input and grasps its meaning remarkably well.</p>""",
        f"""<p>Künstliche Intelligenz ist kein neues Thema. Schon 1950 stellt Alan Turing in seinem Aufsatz <i>Computing Machinery and Intelligence</i> {ref(1)} den später nach ihm benannten Turing-Test vor. Kein Jahrzehnt später folgen die ersten neuronalen Netze {ref(2)}.</p>
<blockquote class="epigraph"><p>I propose to consider the question, “Can machines think?”</p><footer class="mono">Alan M. Turing · Computing Machinery and Intelligence, 1950</footer></blockquote>
<p>Es dauert wiederum einige Jahrzehnte, bis 2017 die Grundlagen für große Sprachmodelle (Large Language Models, LLMs) gelegt werden {ref(3)}. Weil sie natürliche Sprache so gut verarbeiten, sind LLMs sehr vielseitig einsetzbar. Man muss weder KI-Spezialist noch Informatiker sein, um mit ihnen zu arbeiten: Ein LLM stellt kaum Anforderungen an die Eingabe und erfasst ihre Bedeutung erstaunlich gut.</p>"""))
        + chat(lang, [("user", L(T("Why are ghosts such bad liars?", "Warum können Gespenster so schlecht lügen?"))),
                      ("ChatGPT", L(T("Because you can see right through them!", "Weil sie leicht zu durchschauen sind!")))], "GPT-4 · " + L(T("April 2024", "April 2024")))
        + L(T("<p>Three questions follow, and they give this article its three parts: how does such a model work? Which terms do you need to talk about it — up to agents and harnesses? And where can we put it to productive use in software engineering, with models?</p>",
              "<p>Daraus ergeben sich drei Fragen, und sie geben diesem Artikel seine drei Teile: Wie funktioniert so ein Modell? Welche Begriffe braucht man, um darüber zu sprechen — bis hin zu Agenten und Harnesses? Und wo können wir es in der Softwareentwicklung produktiv einsetzen, mit Modellen?</p>"))))

    # ---------------- 01 How an LLM works ----------------
    S.append(("llm", 2, T("How an LLM works", "Wie ein LLM funktioniert"), L(T(
        "<p>An LLM is a neural network that has learned one thing extremely well: to continue a text. Everything else — answering, translating, writing code — follows from that.</p>",
        "<p>Ein LLM ist ein neuronales Netz, das eine Sache außerordentlich gut gelernt hat: einen Text fortzusetzen. Alles andere — antworten, übersetzen, Code schreiben — folgt daraus.</p>"))))
    S.append(("neural", 3, T("How a neural network decides", "Wie ein neuronales Netz entscheidet"), L(T(
        "<p>The basis of every LLM is a neural network. The idea is easiest to see with a picture: is this a dog or a cat? The network does not see a dog, only pixel values. Each pixel is an input; each input is connected to neurons with a weight; each neuron adds up its weighted inputs and passes the result through an activation function to the next layer. At the end, two output neurons compete — “dog” and “cat”. During training, the weights are adjusted over many examples until the right neuron wins.</p>",
        "<p>Die Grundlage jedes LLMs ist ein neuronales Netz. Am einfachsten sieht man die Idee an einem Bild: Ist das ein Hund oder eine Katze? Das Netz sieht keinen Hund, nur Pixelwerte. Jeder Pixel ist eine Eingabe; jede Eingabe ist über ein Gewicht mit Neuronen verbunden; jedes Neuron summiert seine gewichteten Eingaben und gibt das Ergebnis über eine Aktivierungsfunktion an die nächste Schicht weiter. Am Ende konkurrieren zwei Ausgabeneuronen — „Hund“ und „Katze“. Beim Training werden die Gewichte über viele Beispiele so angepasst, bis das richtige Neuron gewinnt.</p>"))
        + dia_neural_net(lang, A)
        + L(T(f"<p>For scale: the roundworm <i>C. elegans</i> gets by with 302 neurons and about 7,000 synaptic connections. GPT-3 has 175 billion weights {ref(8)}; current LLMs are on the order of a trillion.</p>",
              f"<p>Zum Vergleich: Der Fadenwurm <i>C. elegans</i> kommt mit 302 Neuronen und rund 7.000 synaptischen Verbindungen aus. GPT-3 hat 175 Milliarden Gewichte {ref(8)}; aktuelle LLMs liegen in der Größenordnung von einer Billion.</p>"))))
    S.append(("genai", 3, T("Generative AI and the transformer", "Generative KI und der Transformer"), L(T(
        """<p>Generative AI means systems trained to create content that is hard to tell apart from human work — text, images, music and even code. Examples are GPT-4 (Generative Pretrained Transformer) for text, DALL-E for images and Codex for programming. All of them rest on the transformer architecture.</p>
<p>Two aspects make the difference. First, the neural network is trained on text in a way that captures not only the position of words but how they relate to each other. That lets a GPT resolve references — including implicit ones:</p>""",
        """<p>Generative KI meint Systeme, die darauf trainiert sind, Inhalte zu erzeugen, die von menschlichen kaum zu unterscheiden sind — Texte, Bilder, Musik und sogar Code. Beispiele sind GPT-4 (Generative Pretrained Transformer) für Text, DALL-E für Bilder und Codex für die Programmierung. Sie alle beruhen auf der Transformer-Architektur.</p>
<p>Zwei Aspekte sind ausschlaggebend. Erstens wird das neuronale Netz so auf Texten trainiert, dass es nicht nur die Position der Wörter erfasst, sondern auch ihren Bezug zueinander. Dadurch kann ein GPT Bezüge auflösen — auch implizite:</p>"""))
        + chat(lang, [("user", L(T("There is a car and a carriage. She is blue. What colour is the car?", "Es gibt ein Auto und eine Kutsche. Sie ist blau. Welche Farbe hat das Auto?"))),
                      ("ChatGPT", L(T("“She is blue” refers to one of the two objects. Since “she” usually refers to a feminine noun, I would look at the gender of the two nouns … only “the carriage” is feminine. So I would interpret that the carriage is blue — the colour of the car is not given.",
                                      "Die Information „sie ist blau“ bezieht sich auf eines der beiden Objekte. Da „sie“ typischerweise für weibliche Substantive verwendet wird, würde ich nach dem Genus der beiden Nomen schauen … nur „die Kutsche“ ist weiblich. Daher würde ich interpretieren, dass die Kutsche blau ist — die Farbe des Autos wurde nicht angegeben.")))],
               "GPT-4 · " + L(T("April 2024, shortened; the example only works in German, where “Kutsche” is feminine", "April 2024, gekürzt")))
        + dia_transformer(lang)
        + L(T("<p>The second aspect is the sheer amount of training. LLMs are trained on enormous amounts of data and therefore handle the nuances of human language very well. Input may be ungrammatical, misspelt and colloquial — the model has seen all of that before.</p>",
              "<p>Der zweite Aspekt ist der schiere Umfang des Trainings. LLMs werden auf enormen Datenmengen trainiert und verarbeiten die Nuancen menschlicher Sprache deshalb sehr gut. Eingaben dürfen grammatikalisch ungenau, voller Rechtschreibfehler und umgangssprachlich sein — das Modell kennt all das aus seinen Trainingsdaten.</p>"))
        + chat(lang, [("user", L(T("Correct the spelling and grammar of this sentence: “Modle-drivn sofware developmnt a very exiting topic is!!”",
                                   "Überführe den folgenden Satz in korrekte Rechtschreibung und Grammatik: „Modelgetibene Softwär Enticklunk ein sehr spannendes Thema ist!!“"))),
                      ("GPT-4", L(T("“Model-driven software development is a very exciting topic!”", "„Modellgetriebene Softwareentwicklung ist ein sehr spannendes Thema!“")))], "GPT-4 · " + L(T("April 2024", "April 2024")))))
    S.append(("tokens", 3, T("One token at a time", "Token für Token"), L(T(
        f"<p>To produce an answer, a GPT does one thing, over and over: given the text so far, it computes how likely each possible next word is — more precisely the next text fragment, a <i>token</i>. One is drawn, appended, and the whole text goes in again {ref(8)}:</p>",
        f"<p>Um eine Antwort zu erzeugen, macht ein GPT immer wieder nur eines: Zum bisherigen Text berechnet es, wie wahrscheinlich jedes mögliche nächste Wort ist — genauer: das nächste Textelement, ein <i>Token</i>. Eines wird gezogen, angehängt, und der ganze Text geht erneut hinein {ref(8)}:</p>"))
        + dia_next_token(lang)
        + L(T(f"<p>Why not always take the most likely token? Because then, as Stephen Wolfram observes, the text tends to become flat and repetitive; a little randomness makes it livelier {ref(8)}. The price: the same prompt can give different answers. GPTs are therefore neither transparent — you cannot trace how an output came about — nor deterministic.</p>",
              f"<p>Warum nicht immer das wahrscheinlichste Token? Weil der Text dann, wie Stephen Wolfram beobachtet, eher flach und repetitiv wird; ein wenig Zufall macht ihn lebendiger {ref(8)}. Der Preis: Derselbe Prompt kann unterschiedliche Antworten liefern. GPTs sind deshalb weder transparent — man kann nicht nachvollziehen, wie eine Ausgabe zustande kam — noch deterministisch.</p>"))))
    S.append(("hallucinations", 3, T("Hallucinations", "Halluzinationen"), L(T(
        """<p>LLMs are built on a stochastic model. So an LLM does not necessarily give the correct answer, but the most plausible one. As long as the requested information lies within the training data, the most plausible answer is often also the right one; the further outside the training data you go, the more likely it is that the LLM presents a wrong answer very plausibly.</p>
<p>Hallucinations are hard to spot, because they are hard to tell apart from correct statements: they always fit the context of the question and rarely contain obvious errors. The following example shows a mistake any human sees at once — and the model does not. Nothing in the answer reveals its uncertainty.</p>""",
        """<p>LLMs beruhen auf einem stochastischen Modell. Ein LLM gibt deshalb nicht zwingend die korrekte Antwort, sondern die plausibelste. Solange die gefragte Information innerhalb der Trainingsdaten liegt, ist die plausibelste Antwort oft auch die richtige; je weiter man sich aber außerhalb der Trainingsdaten bewegt, desto wahrscheinlicher präsentiert das LLM eine falsche Antwort sehr plausibel.</p>
<p>Halluzinationen sind schwer zu erkennen, weil sie sich kaum von korrekten Aussagen unterscheiden: Sie passen immer gut in den Kontext der Frage und enthalten selten offensichtliche Fehler. Das folgende Beispiel zeigt einen Fehler, den ein Mensch sofort sieht — das Modell nicht. Nichts an der Antwort verrät ihre Unsicherheit.</p>"""))
        + chat(lang, [("user", L(T("Create an image with exactly 17 blue dots.", "Erstelle ein Bild mit genau 17 blauen Punkten."))),
                      ("GPT-4", L(T("Here is the image with exactly 17 blue dots on a white background.", "Hier ist das Bild mit genau 17 blauen Punkten auf weißem Hintergrund."))
                       + f'<img class="chat-img" src="{A}assets/ai4se/dots.webp" alt="{L(T("Generated image with considerably more than 17 blue dots", "Generiertes Bild mit deutlich mehr als 17 blauen Punkten"))}" width="260" height="260" loading="lazy">'),
                      ("user", L(T("How many blue dots are in the image?", "Wie viele blaue Punkte sind in dem Bild?"))),
                      ("GPT-4", L(T("The image contains exactly 17 blue dots on a white background.", "Das Bild enthält genau 17 blaue Punkte auf weißem Hintergrund.")))], "GPT-4 · " + L(T("April 2024", "April 2024")))
        + L(T(f"<p>Reasoning is just as fragile. “Alice has 5 sisters and 3 brothers. How many sisters does a brother of Alice have?” — state-of-the-art models answered this correctly only a fraction of the time {ref(7)}. LLMs imitate language very well, but they have no concept of logic of their own. Tools close part of the gap: code interpreters, function calls, APIs. An LLM that uses such tools in a loop is called an <a href=\"#agent\">agent</a>.</p>",
              f"<p>Genauso brüchig ist das Schlussfolgern. „Alice hat 5 Schwestern und 3 Brüder. Wie viele Schwestern hat ein Bruder von Alice?“ — aktuelle Modelle beantworteten das nur in einem Bruchteil der Fälle richtig {ref(7)}. LLMs imitieren Sprache sehr gut, haben aber selbst kein Konzept von Logik. Werkzeuge schließen einen Teil der Lücke: Code-Interpreter, Function Calls, APIs. Ein LLM, das solche Werkzeuge in einer Schleife einsetzt, nennt man <a href=\"#agent\">Agent</a>.</p>"))))

    # ---------------- 02 Basic terms ----------------
    S.append(("terms", 2, T("Basic terms", "Grundbegriffe"), L(T(
        "<p>Talk about AI quickly fills up with words. Here are the ones you need — from the umbrella term down to agents and harnesses.</p>",
        "<p>Gespräche über KI füllen sich schnell mit Begriffen. Hier sind die, die man braucht — vom Sammelbegriff bis zu Agenten und Harnesses.</p>"))))
    S.append(("umbrella", 3, T("AI is an umbrella term", "KI ist ein Sammelbegriff"), L(T(
        "<p>“Artificial intelligence” is a very broad and loosely defined term. Besides neural networks, even simple decision trees are often called AI. Machine learning narrows it down to algorithms that learn from data; deep learning to those that use neural networks; generative AI to systems that create new content. Large language models are the innermost circle — and the one this article is about.</p>",
        "<p>„Künstliche Intelligenz“ ist ein sehr allgemeiner und unscharf definierter Überbegriff. Neben neuronalen Netzen werden auch einfache Entscheidungsbäume gern als KI bezeichnet. Machine Learning grenzt das auf Algorithmen ein, die aus Daten lernen; Deep Learning auf solche, die neuronale Netze nutzen; generative KI auf Systeme, die neue Inhalte erzeugen. Große Sprachmodelle sind der innerste Kreis — und um den geht es in diesem Artikel.</p>")) + dia_ai_terms(lang)))
    S.append(("words", 3, T("Words around the model", "Begriffe rund um das Modell"), glossary(lang)))
    S.append(("embeddings", 3, "Embeddings", L(T(
        f"<p>Inside, an LLM does not work with words but with vectors — long lists of numbers. These <i>embeddings</i> are learned so that words and texts with similar meaning end up close together, in a kind of meaning space {ref(8)}:</p>",
        f"<p>Im Inneren arbeitet ein LLM nicht mit Wörtern, sondern mit Vektoren — langen Zahlenlisten. Diese <i>Embeddings</i> werden so gelernt, dass Wörter und Texte mit ähnlicher Bedeutung nah beieinander landen, in einer Art Bedeutungsraum {ref(8)}:</p>"))
        + dia_embeddings(lang)
        + L(T("<p>That makes semantic search possible: users describe their problem and get the matching content, without having to know which terms to search for.</p>",
              "<p>Das ermöglicht semantische Suche: Nutzer umschreiben ihr Problem und erhalten passende Inhalte, ohne wissen zu müssen, nach welchen Begriffen sie suchen müssten.</p>"))))
    S.append(("rag", 3, "Retrieval-augmented generation (RAG)", L(T(
        "<p>An LLM only knows what was in its training data. To let it answer from your own documents, you do not train it again — you search first and hand it what you found. Combined with semantic search, this is retrieval-augmented generation:</p>",
        "<p>Ein LLM weiß nur, was in seinen Trainingsdaten stand. Damit es aus eigenen Dokumenten antwortet, trainiert man es nicht neu — man sucht zuerst und gibt ihm, was man gefunden hat. Zusammen mit semantischer Suche ergibt das Retrieval-Augmented Generation:</p>"))
        + dia_rag(lang)))
    S.append(("agent", 3, T("What is an agent?", "Was ist ein Agent?"),
        definition(T("Agent", "Agent"), T("An AI agent is a language model that uses tools in a loop to reach a goal — and decides for itself which step comes next.",
                                          "Ein KI-Agent ist ein Sprachmodell, das in einer Schleife Werkzeuge einsetzt, um ein Ziel zu erreichen — und dabei selbst entscheidet, welcher Schritt als Nächstes kommt."), lang)
        + L(T(f"<p>A chatbot answers a question and stops. An agent gets a goal, plans, acts — reads a file, runs a search, edits code —, looks at the result and decides what to do next, until the goal is reached. Simon Willison puts it in one line: “An LLM agent runs tools in a loop to achieve a goal.” {ref(10)}</p><p>Anthropic draws the line against <i>workflows</i>: in a workflow, LLMs and tools follow paths a programmer laid down in advance; in an agent, the LLM directs its own process and its use of tools {ref(9)}. That makes agents flexible — and harder to predict.</p>",
              f"<p>Ein Chatbot beantwortet eine Frage und hört auf. Ein Agent bekommt ein Ziel, plant, handelt — liest eine Datei, sucht im Web, ändert Code —, betrachtet das Ergebnis und entscheidet, was als Nächstes zu tun ist, bis das Ziel erreicht ist. Simon Willison fasst das in einem Satz: „An LLM agent runs tools in a loop to achieve a goal.“ {ref(10)}</p><p>Anthropic grenzt Agenten von <i>Workflows</i> ab: Im Workflow folgen LLMs und Werkzeuge Pfaden, die ein Programmierer vorher festgelegt hat; im Agenten steuert das LLM seinen Ablauf und seinen Werkzeuggebrauch selbst {ref(9)}. Das macht Agenten flexibel — und schwerer vorherzusagen.</p>"))
        + dia_agent(lang)))
    S.append(("harness", 3, T("What is a harness?", "Was ist ein Harness?"),
        definition("Harness", T("A harness is all the software around a language model that turns it into a working agent — everything in the agent except the model itself.",
                                "Ein Harness ist die gesamte Software rund um ein Sprachmodell, die daraus einen arbeitsfähigen Agenten macht — alles am Agenten außer dem Modell selbst."), lang)
        + L(T(f"""<p>The word comes from the harness of a horse. The horse brings the strength, but only the harness — collar, reins, the cart behind — turns that strength into directed, useful work. A language model on its own can only turn text into text. The harness runs the loop of gathering context, acting, checking the result and going again, and around it provides:</p>
<ul class="pts"><li><b>instructions</b> — the system prompt and the rules of the project,</li><li><b>tools</b> — files, a terminal, a browser, web search,</li><li><b>context and memory</b> — what the model gets to see, summarised when the context window fills up,</li><li><b>guardrails</b> — permissions, a sandbox, what needs a person’s approval,</li><li><b>checks</b> — tests, linters, parsers that tell the model when it went wrong.</li></ul>
<p>Hence the short formula: <i>agent = model + harness</i> {ref(12)}. Claude Code, Codex and Cursor are harnesses. Part of the harness comes built in; teams add their own on top — project rules, extra tools, their own checks. Birgitta Böckeler sorts these additions into <i>guides</i>, which steer the agent before it acts, and <i>sensors</i>, which observe afterwards and help it correct itself {ref(11)}.</p>""",
              f"""<p>Das Wort kommt vom Geschirr eines Pferdes. Das Pferd bringt die Kraft, aber erst das Geschirr — Kummet, Zügel, der Wagen dahinter — macht daraus gelenkte, nützliche Arbeit. Ein Sprachmodell allein kann nur Text in Text verwandeln. Der Harness führt die Schleife aus Kontext sammeln, handeln, Ergebnis prüfen und weitermachen, und stellt drumherum bereit:</p>
<ul class="pts"><li><b>Anweisungen</b> — den System-Prompt und die Regeln des Projekts,</li><li><b>Werkzeuge</b> — Dateien, ein Terminal, einen Browser, Websuche,</li><li><b>Kontext und Gedächtnis</b> — was das Modell zu sehen bekommt, zusammengefasst, wenn das Kontextfenster voll wird,</li><li><b>Leitplanken</b> — Berechtigungen, eine Sandbox, was die Freigabe eines Menschen braucht,</li><li><b>Prüfungen</b> — Tests, Linter, Parser, die dem Modell sagen, wann es danebenlag.</li></ul>
<p>Daher die kurze Formel: <i>Agent = Modell + Harness</i> {ref(12)}. Claude Code, Codex und Cursor sind Harnesses. Ein Teil des Harness ist eingebaut; Teams ergänzen ihren eigenen — Projektregeln, zusätzliche Werkzeuge, eigene Prüfungen. Birgitta Böckeler teilt diese Ergänzungen in <i>Guides</i>, die den Agenten steuern, bevor er handelt, und <i>Sensoren</i>, die danach beobachten und ihm helfen, sich selbst zu korrigieren {ref(11)}.</p>"""))
        + dia_harness(lang)
        + L(T("<p>For anyone building with AI, this is the practical lesson: much of what makes an agent good or bad sits in the harness, not in the model. <a href=\"projects-esaca.html\">ESACA</a>, the project I work on, is such a harness for companies — coding agents inside the company’s own perimeter. And the next chapter shows two harness parts for models: a parser as a sensor, a grammar as a guide.</p>",
              "<p>Für alle, die mit KI bauen, ist das die praktische Lehre: Vieles, was einen Agenten gut oder schlecht macht, steckt im Harness, nicht im Modell. <a href=\"projects-esaca.html\">ESACA</a>, das Projekt, an dem ich arbeite, ist so ein Harness für Unternehmen — Coding-Agenten innerhalb der eigenen Infrastruktur. Und das nächste Kapitel zeigt zwei Harness-Bausteine für Modelle: einen Parser als Sensor, eine Grammatik als Guide.</p>"))))

    # ---------------- 03 LLMs and models ----------------
    S.append(("mde", 2, T("LLMs and model-driven engineering", "LLMs und modellgetriebene Entwicklung"), L(T(
        f"""<p>Software engineering is a complex discipline with many hurdles: programming skills, experience in system modelling, domain knowledge and a lot of coordination between the stakeholders of the platform being built. Generative AI can already take over parts of this work and speed development up {ref(4)}. Assistants such as GitHub Copilot help programmers write parts of the source code. Far fewer approaches deal with modelling and generating whole systems.</p>
<p>Generative methods can create systems, or parts of them, from textual models: a generator reads a model and produces source code from it. Depending on what the code is for, different modelling languages fit — class diagrams for data structures, sequence diagrams for processes.</p>""",
        f"""<p>Softwareentwicklung ist eine komplexe Disziplin mit vielen Einstiegshürden: Programmierkenntnisse, Erfahrung in der Systemmodellierung, Domänenwissen und viel Abstimmung zwischen den Stakeholdern der zu entwickelnden Plattform. Generative KI kann uns schon heute Teile dieser Arbeit abnehmen und die Entwicklung beschleunigen {ref(4)}. Assistenten wie GitHub Copilot unterstützen Programmierer beim Schreiben von Teilen des Quellcodes. Deutlich weniger Ansätze befassen sich mit der Modellierung und Generierung ganzer Systeme.</p>
<p>Generative Methoden können aus textuellen Modellen Systeme oder Teile davon erzeugen: Ein Generator liest ein Modell und erzeugt daraus Quellcode. Je nachdem, wofür der Code gedacht ist, passen unterschiedliche Modellierungssprachen — Klassendiagramme für Datenstrukturen, Sequenzdiagramme für Abläufe.</p>"""))))
    S.append(("models", 3, T("Language models that write models", "Sprachmodelle, die Modelle schreiben"), L(T(
        f"""<p>Defining good models takes knowledge: of modelling concepts, of the syntax of the modelling language and of the use case. LLMs can help most with the first two. With prompt engineering we can teach an LLM a modelling language {cite("BDMN+24")} {cite("NMR24")} — combining few-shot learning {ref(5)}, retrieval-augmented generation {ref(6)} and instructions to turn natural-language input into a textual model in the language of our choice.</p>""",
        f"""<p>Gute Modelle zu definieren erfordert Vorwissen: über Modellierungskonzepte, über die Syntax der Modellierungssprache und über den Anwendungsfall. LLMs können vor allem bei den ersten beiden helfen. Mit Prompt Engineering können wir einem LLM eine Modellierungssprache beibringen {cite("BDMN+24")} {cite("NMR24")} — mit einer Kombination aus Few-Shot-Learning {ref(5)}, Retrieval-Augmented Generation {ref(6)} und Instruktionen, die natürlichsprachliche Eingaben in ein textuelles Modell in der Sprache unserer Wahl übersetzen.</p>"""))
        + chat(lang, [("user", L(T("Create a simple model of a dog kennel", "Erzeuge mir ein einfaches Modell einer Hundehütte"))),
                      ("CD4A Model Creator", f"<pre><code>{kennel}</code></pre>")], "CD4A Model Creator")
        + L(T("<p>Try the assistants yourself:</p>", "<p>Probieren Sie die Assistenten selbst aus:</p>"))
        + f'<ul class="tries">{tries}</ul>'
        + L(T("<p>LLMs tuned for a modelling language can do more than create new models: they can change existing ones, or extract a model from a picture. A model sketched on a whiteboard can be photographed and turned into proper syntax.</p><p>What makes this reliable is what happens <i>after</i> the LLM. A parser checks every model; an invalid one goes back with the error message:</p>",
              "<p>LLMs, die auf eine Modellierungssprache angepasst sind, können mehr als neue Modelle erstellen: Sie können bestehende Modelle anpassen oder ein Modell aus einem Bild extrahieren. Ein am Whiteboard skizziertes Modell lässt sich fotografieren und in die passende Syntax überführen.</p><p>Verlässlich wird das erst durch das, was <i>nach</i> dem LLM passiert. Ein Parser prüft jedes Modell; ein ungültiges geht mit der Fehlermeldung zurück:</p>"))
        + dia_formalize(lang)))
    S.append(("masking", 3, T("Constrained decoding: grammar masking", "Constrained Decoding: Grammar Masking"), L(T(
        f"<p>Even better is to not let invalid models arise at all. An LLM writes <a href=\"#tokens\">one token at a time</a> — so at every step, before a token is chosen, the grammar of the modelling language can filter the candidates. This is grammar masking {cite('NRR24')}:</p>",
        f"<p>Noch besser ist es, ungültige Modelle gar nicht erst entstehen zu lassen. Ein LLM schreibt <a href=\"#tokens\">Token für Token</a> — also kann die Grammatik der Modellierungssprache bei jedem Schritt die Kandidaten filtern, bevor eines gewählt wird. Das ist Grammar Masking {cite('NRR24')}:</p>"))
        + dia_grammar_mask(lang) + masking_table(lang)
        + L(T("<p>Small open models running locally then produce valid models more than nine times out of ten — instead of between almost never and four times out of ten. The price is runtime. Masking needs access to the token probabilities, which is why it works with open models running on one’s own hardware.</p>",
              "<p>Kleine, lokal laufende offene Modelle liefern dann in mehr als neun von zehn Fällen gültige Modelle — statt zwischen fast nie und vier von zehn Mal. Der Preis ist die Laufzeit. Masking braucht Zugriff auf die Token-Wahrscheinlichkeiten; deshalb funktioniert es mit offenen Modellen auf der eigenen Hardware.</p>"))))
    S.append(("app", 3, T("From a sentence to an application", "Vom Satz zur Anwendung"), L(T(
        f"""<p>Put together with model-driven engineering, this goes all the way: users describe their domain informally, an LLM derives the class diagrams, and a generator such as <a href="projects-montigem.html">MontiGem</a> turns them into a complete information system {cite("NMR24")} {cite("Net24")}.</p>""",
        f"""<p>Zusammen mit modellgetriebener Softwareentwicklung reicht das bis zum Ende: Nutzer beschreiben ihre Domäne informell, ein LLM leitet daraus Klassendiagramme ab, und ein Generator wie <a href="projects-montigem.html">MontiGem</a> macht daraus ein vollständiges Informationssystem {cite("NMR24")} {cite("Net24")}.</p>"""))
        + dia_ai_mde(lang)
        + L(T(f"<p>Models help far beyond generating software artefacts. Requirements can be translated from natural language into a formal language a computer can analyse; contradictions and redundancies found there can be translated back into natural language by an LLM. And because a generated model can be analysed and checked, many sources of error are ruled out before a single line of code exists {cite('NKR+25')}.</p>",
              f"<p>Modelle helfen weit über die Generierung von Software-Artefakten hinaus. Anforderungen lassen sich aus natürlicher Sprache in eine formale, vom Computer analysierbare Sprache übersetzen; dort gefundene Widersprüche und Redundanzen kann ein LLM wieder in natürliche Sprache zurückübersetzen. Und weil sich ein generiertes Modell analysieren und prüfen lässt, lassen sich viele Fehlerquellen ausschließen, bevor auch nur eine Zeile Code existiert {cite('NKR+25')}.</p>"))))
    S.append(("summary", 1, T("In short", "Kurz gesagt"), L(T(
        "<p>AI cannot replace a developer yet; it is best seen as a tool that speeds up the development process. Everything it produces needs checking and validation — it cannot be used blindly. That checking belongs in the harness, and where AI meets models it becomes possible: the model is the place where language turns into something a machine can verify.</p>",
        "<p>KI kann einen Entwickler noch nicht ersetzen; sie ist am besten als Werkzeug zu verstehen, das den Entwicklungsprozess beschleunigt. Alles, was sie erzeugt, braucht Prüfung und Validierung — blind einsetzen lässt sie sich nicht. Diese Prüfung gehört in den Harness, und wo KI auf Modelle trifft, wird sie möglich: Das Modell ist die Stelle, an der aus Sprache etwas wird, das eine Maschine verifizieren kann.</p>"))))
    out, n = [], 0
    for sid, level, head, html_ in S:
        name = L(head) if isinstance(head, dict) else head
        if level == 2:                                      # a numbered chapter
            n += 1
            out.append(f'      <section class="art-sec art-ch"><h2 id="{sid}"><span class="mono">0{n}</span>{name}</h2>{html_}</section>')
        elif level == 1:                                    # the closing words: a chapter heading without a number
            out.append(f'      <section class="art-sec art-ch"><h2 id="{sid}">{name}</h2>{html_}</section>')
        else:
            h = f'<h3 id="{sid}">{name}</h3>' if head else ""
            out.append(f'      <section class="art-sec">{h}{html_}</section>')
    toc = "".join(f'<a href="#{sid}">{L(head)}</a>' for sid, level, head, _ in S if level == 2)
    refs = "".join(f'<li id="ref-{k}">{r}</li>' for k, r in enumerate(REFS, 1))
    return toc, NL.join(out), refs


def page(lang):
    """Returns (file, title, description, body, scripts) for build.py."""
    L = lambda x: x[lang]
    A = "../" if lang == "de" else ""
    toc, sections, refs = body(lang, A)
    html_ = f'''
    <header class="page proj">
      <a class="back mono" href="research.html">← {L(T("research", "Forschung"))}</a>
      <div class="section-head">
        <h1><span class="mono">02</span>AI-driven Software Engineering</h1>
        <span class="mono faint">{L(T("article · 2024, revised 2026", "Artikel · 2024, überarbeitet 2026"))}</span>
      </div>
      <p class="lead">{L(T("What is this “new” AI, how does it work — and where does it actually help in building software? An introduction from neurons to agents and <em>language models that write models</em>.",
                          "Was ist diese „neue“ KI, wie funktioniert sie — und wo hilft sie beim Bauen von Software wirklich? Eine Einführung vom Neuron über Agenten bis zu <em>Sprachmodellen, die Modelle schreiben</em>."))}</p>
      <nav class="chapters mono" aria-label="{L(T("Chapters", "Kapitel"))}">{toc}</nav>
    </header>
    <article class="article">
{sections}
      <section class="art-sec art-refs">
        <h2 id="literature">{L(T("Literature", "Literatur"))}</h2>
        <ol class="refs mono">{refs}</ol>
        <div class="group mono">{L(T("My papers on the topic", "Eigene Arbeiten zum Thema"))}</div>
        <ol class="pubs">
{pub_list(lang, OWN)}
        </ol>
      </section>
    </article>
'''
    desc = T("AI-driven software engineering: how LLMs work, what agents and harnesses are, and how LLMs can write models that generators turn into software — an article by Lukas Netz.",
             "KI-getriebene Softwareentwicklung: wie LLMs funktionieren, was Agenten und Harnesses sind und wie LLMs Modelle schreiben, aus denen Generatoren Software machen — ein Artikel von Lukas Netz.")
    return FILE, T("AI-driven Software Engineering", "AI-driven Software Engineering"), desc, html_, f'<script src="{A}assets/ai4se.js"></script>\n'
