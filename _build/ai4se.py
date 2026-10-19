"""
Research sub page: AI-driven software engineering (research-ai4se.html) — an article in the
manner of a blog post, based on the acronio page and the AI4SE / SE4AI talk (10 / 2024).
Imported by build.py. Diagrams are inline SVG with the .dia classes of style.css.
"""
from project_content import _arrow_defs, box
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


REFS = [
    "A. M. Turing: Computing Machinery and Intelligence. Mind 59(236), 433–460 (1950).",
    "F. Rosenblatt: The perceptron: a probabilistic model for information storage and organization in the brain. Psychological Review 65(6), 386–408 (1958).",
    "A. Vaswani et al.: Attention is all you need. Advances in Neural Information Processing Systems 30 (2017).",
    "S. Barke, M. B. James, N. Polikarpova: Grounded Copilot: How programmers interact with code-generating models. arXiv:2206.15000 (2022).",
    "T. Brown et al.: Language models are few-shot learners. Advances in Neural Information Processing Systems 33, 1877–1901 (2020).",
    "G. Izacard et al.: Few-shot learning with retrieval augmented language models. arXiv:2208.03299 (2022).",
    "M. Nezhurina, L. Cipolina-Kun, M. Cherti, J. Jitsev: Alice in Wonderland: Simple tasks showing complete reasoning breakdown in state-of-the-art large language models. arXiv:2406.02061 (2024).",
]
OWN = ["NMR24", "BDMN+24", "NRR24", "Net24", "NKR+25"]


def chat(lang, turns, source):
    """A dialogue with a model, set quietly: who speaks in mono, the text below."""
    rows = "".join(f'<div class="turn{" ai" if who != "user" else ""}"><span class="who mono">{(T("User", "Nutzer") if who == "user" else T(who, who))[lang]}</span>'
                   f'<div class="msg">{text}</div></div>' for who, text in turns)
    return f'<figure class="chat">{rows}<figcaption class="mono">{source}</figcaption></figure>'


def fig(svg, caption, lang, scroll=True):
    inner = f'<div class="dia-scroll">{svg}</div>' if scroll else svg
    return f'<figure class="media art-fig">{inner}<figcaption class="mono">{caption[lang]}</figcaption></figure>'


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


def dia_neural_net(lang, A):
    """Slides 5–9: a picture becomes pixels, pixels feed a network, the network says dog or cat;
    one neuron in detail."""
    L = lambda x: x[lang]
    m = 'marker-end="url(#nna)"'
    xs_in, xs_h, xs_o = 300, 400, 500
    ins = [60, 100, 140, 180, 220]
    hid = [80, 125, 170, 215]
    outs = [118, 178]
    edges = "".join(f'<path class="ln" style="opacity:.35" d="M{xs_in} {a}L{xs_h} {b}"/>' for a in ins for b in hid)
    edges += "".join(f'<path class="ln" style="opacity:.35" d="M{xs_h} {a}L{xs_o} {b}"/>' for a in hid for b in outs)
    nodes = "".join(f'<circle cx="{xs_in}" cy="{y}" r="7" class="box"/>' for y in ins)
    nodes += "".join(f'<circle cx="{xs_h}" cy="{y}" r="9" class="box"/>' for y in hid)
    nodes += f'<circle cx="{xs_o}" cy="{outs[0]}" r="10" class="box hl"/><circle cx="{xs_o}" cy="{outs[1]}" r="10" class="box"/>'
    labels = (f'<text x="{xs_o + 22}" y="{outs[0] + 4}" class="t" style="fill:var(--accent)">{L(T("dog", "Hund"))}</text>'
              f'<text x="{xs_o + 22}" y="{outs[1] + 4}" class="t">{L(T("cat", "Katze"))}</text>'
              f'<text x="{xs_in}" y="250" text-anchor="middle" class="s">{L(T("pixels", "Pixel"))}</text>'
              f'<text x="{xs_h}" y="250" text-anchor="middle" class="s">{L(T("neurons", "Neuronen"))}</text>'
              f'<text x="{xs_o}" y="250" text-anchor="middle" class="s">{L(T("output", "Ausgabe"))}</text>')
    # one neuron: inputs × weights → Σ → φ → activation
    ny = 330
    neuron = "".join(f'<text x="560" y="{ny - 40 + k * 26}" class="s">x{k + 1}</text><path class="ln" d="M576 {ny - 44 + k * 26}H600"/>'
                     f'<circle cx="612" cy="{ny - 44 + k * 26}" r="11" class="box"/><text x="612" y="{ny - 40 + k * 26}" text-anchor="middle" class="s">w{k + 1}</text>'
                     f'<path class="ln" d="M623 {ny - 44 + k * 26}L682 {ny - 4}"/>' for k in range(4))
    neuron += (f'<circle cx="700" cy="{ny - 4}" r="18" class="box hl"/><text x="700" y="{ny + 1}" text-anchor="middle" class="t">Σ</text>'
               f'<path class="ln" d="M718 {ny - 4}H744" {m}/><rect x="748" y="{ny - 22}" width="36" height="36" rx="3" class="box"/>'
               f'<text x="766" y="{ny + 1}" text-anchor="middle" class="t">φ</text><path class="ln" d="M784 {ny - 4}H812" {m}/>'
               f'<text x="700" y="{ny + 38}" text-anchor="middle" class="s">{L(T("weighted sum", "gewichtete Summe"))}</text>'
               f'<text x="766" y="{ny - 30}" text-anchor="middle" class="s">{L(T("activation", "Aktivierung"))}</text>')
    svg = f'''<svg class="dia" viewBox="0 0 860 380" role="img" aria-label="{L(T("A photo of a dog is reduced to pixels; the pixel values feed a small neural network whose output neuron for dog lights up. Below: a single neuron forms a weighted sum of its inputs and passes it through an activation function.", "Ein Hundefoto wird zu Pixeln; die Pixelwerte speisen ein kleines neuronales Netz, dessen Ausgabeneuron für Hund aufleuchtet. Darunter: Ein einzelnes Neuron bildet eine gewichtete Summe seiner Eingaben und gibt sie durch eine Aktivierungsfunktion weiter."))}">
  {_arrow_defs("nna")}
  <image href="{A}assets/ai4se/dog.jpg" x="0" y="40" width="120" height="120"/>
  <image href="{A}assets/ai4se/dog-pixels.png" x="140" y="40" width="120" height="120" style="image-rendering:pixelated"/>
  <text x="60" y="180" text-anchor="middle" class="s">{L(T("photo", "Foto"))}</text>
  <text x="200" y="180" text-anchor="middle" class="s">{L(T("16 × 16 pixels", "16 × 16 Pixel"))}</text>
  <path class="ln" d="M262 100H288" {m}/>
  {edges}{nodes}{labels}
  <rect class="zone line" x="540" y="270" width="300" height="104" rx="4"/>
  <text x="552" y="262" class="s">{L(T("ONE NEURON", "EIN NEURON"))}</text>
  {neuron}
</svg>'''
    return fig(svg, T("A neural network sees numbers, not dogs: every pixel is an input, every connection a weight. Each neuron adds up its weighted inputs and passes the result on through an activation function. Training adjusts the weights until “dog” wins for dogs.",
                      "Ein neuronales Netz sieht Zahlen, keine Hunde: Jeder Pixel ist eine Eingabe, jede Verbindung ein Gewicht. Jedes Neuron summiert seine gewichteten Eingaben und gibt das Ergebnis über eine Aktivierungsfunktion weiter. Training passt die Gewichte so lange an, bis bei Hunden „Hund“ gewinnt."), lang)


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
    parts.append(f'<text x="86" y="154" text-anchor="end" class="s">Llama 3.1: 126</text>')
    svg = f'<svg class="dia" viewBox="0 0 900 300" role="img" aria-label="{L(T("Simplified transformer decoder: embeddings with positional encoding pass through attention and feed-forward layers, repeated N times; a linear layer and softmax produce next-token probabilities", "Vereinfachter Transformer-Decoder: Embeddings mit Positionskodierung durchlaufen Attention- und Feed-Forward-Schichten, N-mal wiederholt; eine lineare Schicht und Softmax liefern Wahrscheinlichkeiten für das nächste Token"))}">{_arrow_defs("tra")}{"".join(parts)}</svg>'
    return fig(svg, T("The core of a GPT, read from bottom to top. Attention is what made the difference in 2017: every token can look at every earlier token and weigh how much it matters.",
                      "Der Kern eines GPT, von unten nach oben gelesen. Attention war 2017 der entscheidende Schritt: Jedes Token kann auf jedes frühere Token schauen und abwägen, wie wichtig es ist."), lang)


def dia_next_token(lang):
    """Slides 12–28: the model only ever picks the next token."""
    L = lambda x: x[lang]
    m = 'marker-end="url(#nta)"'
    cands = [("Paris", 0.81), ("Lyon", 0.07), ("Toulouse", 0.04), ("die" if lang == "de" else "the", 0.03), ("Berlin", 0.01)]
    bars = "".join(f'<text x="560" y="{78 + k * 30}" text-anchor="end" class="{"t" if k == 0 else ""}">{w}</text>'
                   f'<rect x="572" y="{66 + k * 30}" width="{max(3, p * 220):.0f}" height="14" rx="2" style="fill:var(--{"accent" if k == 0 else "ink-3"});opacity:{1 if k == 0 else .45}"/>'
                   f'<text x="{580 + max(3, p * 220):.0f}" y="{78 + k * 30}" class="s">{p:.2f}</text>' for k, (w, p) in enumerate(cands))
    prompt = L(T("System: You are a helpful chatbot!", "System: Du bist ein hilfreicher Chatbot!")), L(T("User: What is the capital of France?", "Nutzer: Was ist die Hauptstadt von Frankreich?")), L(T("Assistant: The capital is", "Assistent: Die Hauptstadt ist"))
    svg = f'''<svg class="dia" viewBox="0 0 860 230" role="img" aria-label="{L(T("The prompt goes into the model, which returns a probability for each possible next token; the most likely, Paris, is sampled and appended", "Der Prompt geht in das Modell, das für jedes mögliche nächste Token eine Wahrscheinlichkeit liefert; das wahrscheinlichste, Paris, wird gezogen und angehängt"))}">
  {_arrow_defs("nta")}
  <rect class="box" x="0" y="40" width="326" height="150" rx="3"/>
  <text x="14" y="32" class="s">INPUT PROMPT</text>
  <text x="14" y="80">{prompt[0]}</text><text x="14" y="112">{prompt[1]}</text><text x="14" y="144">{prompt[2]} <tspan style="fill:var(--accent)">▌</tspan></text>
  <path class="ln" d="M326 115H338" {m}/>
  {box(342, 85, 120, 60, "GPT", L(T("transformer", "Transformer")), cls="box hl")}
  <path class="ln" d="M462 115H500" {m}/>
  <text x="572" y="40" class="s">{L(T("PROBABILITY OF THE NEXT TOKEN", "WAHRSCHEINLICHKEIT DES NÄCHSTEN TOKENS"))}</text>
  {bars}
  <path class="ln hl dash" d="M560 60V30H150V36" marker-end="url(#ntaa)"/>
  <text x="356" y="24" class="s a">{L(T("sampled and appended — then the next round", "gezogen und angehängt — dann die nächste Runde"))}</text>
</svg>'''
    return fig(svg, T("An LLM answers one token at a time: it computes a probability for every possible next token, one is drawn, appended, and the whole text goes in again — until an end token is drawn. The “temperature” sets how far the draw may stray from the most likely token.",
                      "Ein LLM antwortet Token für Token: Es berechnet für jedes mögliche nächste Token eine Wahrscheinlichkeit, eines wird gezogen und angehängt, und der ganze Text geht erneut hinein — bis ein End-Token gezogen wird. Die „Temperatur“ bestimmt, wie weit die Wahl vom wahrscheinlichsten Token abweichen darf."), lang)


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


def dia_grammar_mask(lang):
    """Slides 48–52: grammar masking — the grammar filters the token distribution."""
    L = lambda x: x[lang]
    m, ma = 'marker-end="url(#gma)"', 'marker-end="url(#gmaa)"'
    toks = [("class", True, .34), ("{", True, .22), ("abstract", True, .12), ("&&", False, .2), ("<!--", False, .12)]
    esc = lambda t: t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    rows = "".join(f'<text x="420" y="{58 + k * 26}" text-anchor="end" style="font-family:var(--mono)" class="{"" if ok else "s"}">{esc(t)}</text>'
                   f'<rect x="430" y="{47 + k * 26}" width="{p * 260:.0f}" height="13" rx="2" style="fill:var(--{"accent" if ok else "ink-3"});opacity:{.9 if ok else .25}"/>'
                   + ("" if ok else f'<path class="ln" style="opacity:.7" d="M{424 - len(t) * 7} {53 + k * 26}H{440 + p * 260:.0f}"/>') for k, (t, ok, p) in enumerate(toks))
    svg = f'''<svg class="dia" viewBox="0 0 860 206" role="img" aria-label="{L(T("Grammar masking: the LLM proposes a distribution over next tokens; tokens the grammar of the modelling language does not allow at this point are removed before one is chosen", "Grammar Masking: Das LLM schlägt eine Verteilung über nächste Tokens vor; Tokens, die die Grammatik der Modellierungssprache an dieser Stelle nicht erlaubt, werden vor der Wahl entfernt"))}">
  {_arrow_defs("gma")}
  {box(0, 50, 130, 50, "LLM", L(T("open source", "Open Source")), cls="box hl")}
  <path class="ln" d="M130 75H236" {m}/>
  <text x="300" y="30" class="s">{L(T("NEXT-TOKEN CANDIDATES", "KANDIDATEN FÜR DAS NÄCHSTE TOKEN"))}</text>
  {rows}
  {box(0, 140, 130, 44, L(T("Grammar", "Grammatik")), "CD4A")}
  <path class="ln hl" d="M130 162H330V186" />
  <text x="340" y="190" class="s a">{L(T("filters what cannot be valid here", "filtert, was hier nicht gültig sein kann"))}</text>
  <path class="ln" d="M720 75H756" {m}/>
  {box(760, 50, 100, 50, L(T("Model", "Modell")), L(T("always parses", "parst immer")))}
</svg>'''
    return fig(svg, T("Constrained decoding: before a token is chosen, the grammar of the modelling language removes every candidate that would make the model invalid. The LLM can then only write models that parse.",
                      "Constrained Decoding: Bevor ein Token gewählt wird, entfernt die Grammatik der Modellierungssprache jeden Kandidaten, der das Modell ungültig machen würde. Das LLM kann dann nur noch Modelle schreiben, die parsen."), lang)


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
    """Slides 55 / 56: word embeddings in two dimensions — royalty and gender."""
    L = lambda x: x[lang]
    cx, cy, u = 560, 150, 95
    words = [("King", 1, 1, ""), ("Queen", -1, 1, ""), ("Man", 1, -1, ""), ("Woman", -1, -1, ""), ("Princess", -1.1, 1.2, "hl")]
    vec = lambda x, y, cls: f'<path class="ln {cls}" d="M{cx} {cy}L{cx + x * u:.0f} {cy - y * u:.0f}" marker-end="url(#ema{"a" if cls else ""})"/>'
    arrows = "".join(vec(x, y, cls) for _, x, y, cls in words)
    dy = {"Queen": 18, "Princess": -8}
    names = "".join(f'<text x="{cx + x * u + (12 if x > 0 else -12):.0f}" y="{cy - y * u + dy.get(w, -6 if y > 0 else 16):.0f}" text-anchor="{"start" if x > 0 else "end"}" class="t"{" style=&quot;fill:var(--accent)&quot;" if cls else ""}>{w}</text>' for w, x, y, cls in words)
    names = names.replace("&quot;", '"')
    table = "".join(f'<text x="10" y="{50 + k * 40}" class="t"{" style=&quot;fill:var(--accent)&quot;" if cls else ""}>{w}</text><text x="120" y="{50 + k * 40}" style="font-family:var(--mono)">[ {x:+.1f}, {y:+.1f} ]</text>' for k, (w, x, y, cls) in enumerate(words)).replace("&quot;", '"')
    svg = f'''<svg class="dia" viewBox="0 0 860 300" role="img" aria-label="{L(T("Words as vectors on two axes, gender and royalty: king, queen, man, woman; princess lies close to queen", "Wörter als Vektoren auf zwei Achsen, Geschlecht und Königlichkeit: King, Queen, Man, Woman; Princess liegt nahe bei Queen"))}">
  {_arrow_defs("ema")}
  {table}
  <path class="ln" d="M{cx - 170} {cy}H{cx + 170}"/><path class="ln" d="M{cx} {cy + 140}V{cy - 140}"/>
  <text x="{cx + 172}" y="{cy - 8}" text-anchor="end" class="s">{L(T("gender", "Geschlecht"))}</text>
  <text x="{cx + 8}" y="{cy - 128}" class="s">{L(T("royalty", "Königlichkeit"))}</text>
  {arrows}{names}
  <ellipse cx="{cx - 1.05 * u:.0f}" cy="{cy - 1.1 * u:.0f}" rx="58" ry="26" style="fill:none;stroke:var(--accent);stroke-dasharray:3 4;opacity:.7"/>
  <text x="{cx - 1.05 * u - 66:.0f}" y="{cy - 1.1 * u + 4:.0f}" text-anchor="end" class="s a">{L(T("similar", "ähnlich"))}</text>
</svg>'''
    return fig(svg, T("Embeddings turn words and texts into vectors. Here two dimensions are enough: “princess” lands right next to “queen”. Real models use thousands of dimensions — OpenAI’s text-embedding-3 has 3,072 — but the idea stays the same: similar meaning, nearby vectors.",
                      "Embeddings machen aus Wörtern und Texten Vektoren. Hier genügen zwei Dimensionen: „Princess“ landet direkt neben „Queen“. Echte Modelle nutzen Tausende Dimensionen — OpenAIs text-embedding-3 hat 3.072 —, aber die Idee bleibt: ähnliche Bedeutung, benachbarte Vektoren."), lang)


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
    return fig(svg, T("Retrieval-augmented generation lets an LLM answer from knowledge it was never trained on — lecture material, specifications, publications. The search is semantic: users describe their problem and find the right passage without knowing its terms. This is how SE-Chatty works.",
                      "Retrieval-Augmented Generation lässt ein LLM aus Wissen antworten, auf das es nie trainiert wurde — Vorlesungsmaterial, Spezifikationen, Publikationen. Die Suche ist semantisch: Nutzer beschreiben ihr Problem und finden die passende Stelle, ohne ihre Begriffe zu kennen. So funktioniert SE-Chatty."), lang)


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
    S = []                                                  # (id, heading, html)
    S.append(("intro", None, L(T(
        f"""<p>Artificial intelligence is not a new topic. As early as 1950, Alan Turing introduced what would later be called the Turing test in his paper <i>Computing Machinery and Intelligence</i> {ref(1)}. Less than a decade later, the first neural networks followed {ref(2)}.</p>
<blockquote class="epigraph"><p>I propose to consider the question, “Can machines think?”</p><footer class="mono">Alan M. Turing · Computing Machinery and Intelligence, 1950</footer></blockquote>
<p>It took several more decades until 2017 laid the foundations for large language models (LLMs) {ref(3)}. Because they handle natural language so well, LLMs can be used for almost anything. You need not be an AI specialist or a computer scientist to work with them: an LLM places hardly any restrictions on its input and grasps its meaning remarkably well.</p>""",
        f"""<p>Künstliche Intelligenz ist kein neues Thema. Schon 1950 stellt Alan Turing in seinem Aufsatz <i>Computing Machinery and Intelligence</i> {ref(1)} den später nach ihm benannten Turing-Test vor. Kein Jahrzehnt später folgen die ersten neuronalen Netze {ref(2)}.</p>
<blockquote class="epigraph"><p>I propose to consider the question, “Can machines think?”</p><footer class="mono">Alan M. Turing · Computing Machinery and Intelligence, 1950</footer></blockquote>
<p>Es dauert wiederum einige Jahrzehnte, bis 2017 die Grundlagen für große Sprachmodelle (Large Language Models, LLMs) gelegt werden {ref(3)}. Weil sie natürliche Sprache so gut verarbeiten, sind LLMs sehr vielseitig einsetzbar. Man muss weder KI-Spezialist noch Informatiker sein, um mit ihnen zu arbeiten: Ein LLM stellt kaum Anforderungen an die Eingabe und erfasst ihre Bedeutung erstaunlich gut.</p>"""))
        + chat(lang, [("user", L(T("Why are ghosts such bad liars?", "Warum können Gespenster so schlecht lügen?"))),
                      ("ChatGPT", L(T("Because you can see right through them!", "Weil sie leicht zu durchschauen sind!")))], "GPT-4 · " + L(T("April 2024", "April 2024")))
        + L(T("<p>Two questions follow: what exactly is this “new” AI — and where can we put it to productive use in software engineering?</p>",
              "<p>Daraus ergeben sich zwei Fragen: Was genau ist diese „neue“ KI — und wo können wir sie in der Softwareentwicklung produktiv einsetzen?</p>"))))
    S.append(("terms", T("AI is an umbrella term", "KI ist ein Sammelbegriff"), L(T(
        "<p>“Artificial intelligence” is a very broad and loosely defined term. Besides neural networks, even simple decision trees are often called AI. Machine learning narrows it down to algorithms that learn from data; deep learning to those that use neural networks; generative AI to systems that create new content. Large language models are the innermost circle — and the one this article is about.</p>",
        "<p>„Künstliche Intelligenz“ ist ein sehr allgemeiner und unscharf definierter Überbegriff. Neben neuronalen Netzen werden auch einfache Entscheidungsbäume gern als KI bezeichnet. Machine Learning grenzt das auf Algorithmen ein, die aus Daten lernen; Deep Learning auf solche, die neuronale Netze nutzen; generative KI auf Systeme, die neue Inhalte erzeugen. Große Sprachmodelle sind der innerste Kreis — und um den geht es in diesem Artikel.</p>")) + dia_ai_terms(lang)))
    S.append(("neural", T("How a neural network decides", "Wie ein neuronales Netz entscheidet"), L(T(
        "<p>The basis of every LLM is a neural network. The idea is easiest to see with a picture: is this a dog or a cat? The network does not see a dog, only pixel values. Each pixel is an input; each input is connected to neurons with a weight; each neuron adds up its weighted inputs and passes the result through an activation function to the next layer. At the end, two output neurons compete — “dog” and “cat”. During training, the weights are adjusted over many examples until the right neuron wins.</p>",
        "<p>Die Grundlage jedes LLMs ist ein neuronales Netz. Am einfachsten sieht man die Idee an einem Bild: Ist das ein Hund oder eine Katze? Das Netz sieht keinen Hund, nur Pixelwerte. Jeder Pixel ist eine Eingabe; jede Eingabe ist über ein Gewicht mit Neuronen verbunden; jedes Neuron summiert seine gewichteten Eingaben und gibt das Ergebnis über eine Aktivierungsfunktion an die nächste Schicht weiter. Am Ende konkurrieren zwei Ausgabeneuronen — „Hund“ und „Katze“. Beim Training werden die Gewichte über viele Beispiele so angepasst, bis das richtige Neuron gewinnt.</p>"))
        + dia_neural_net(lang, A)
        + L(T("<p>For scale: the roundworm <i>C. elegans</i> gets by with 302 neurons and about 7,000 synaptic connections. Current LLMs have on the order of a trillion parameters.</p>",
              "<p>Zum Vergleich: Der Fadenwurm <i>C. elegans</i> kommt mit 302 Neuronen und rund 7.000 synaptischen Verbindungen aus. Aktuelle LLMs haben Parameter in der Größenordnung von einer Billion.</p>"))))
    S.append(("genai", T("Generative AI", "Generative KI"), L(T(
        """<p>Generative AI means systems trained to create content that is hard to tell apart from human work — text, images, music and even code. Examples are GPT-4 (Generative Pretrained Transformer) for text, DALL-E for images and Codex for programming. All of them rest on the transformer architecture.</p>
<p>Two aspects make the difference. First, the neural network is trained on text in a way that captures not only the position of words but how they relate to each other. That lets a GPT resolve references — including implicit ones:</p>""",
        """<p>Generative KI meint Systeme, die darauf trainiert sind, Inhalte zu erzeugen, die von menschlichen kaum zu unterscheiden sind — Texte, Bilder, Musik und sogar Code. Beispiele sind GPT-4 (Generative Pretrained Transformer) für Text, DALL-E für Bilder und Codex für die Programmierung. Sie alle beruhen auf der Transformer-Architektur.</p>
<p>Zwei Aspekte sind ausschlaggebend. Erstens wird das neuronale Netz so auf Texten trainiert, dass es nicht nur die Position der Wörter erfasst, sondern auch ihren Bezug zueinander. Dadurch kann ein GPT Bezüge auflösen — auch implizite:</p>"""))
        + chat(lang, [("user", L(T("There is a car and a carriage. She is blue. What colour is the car?", "Es gibt ein Auto und eine Kutsche. Sie ist blau. Welche Farbe hat das Auto?"))),
                      ("ChatGPT", L(T("“She is blue” refers to one of the two objects. Since “she” usually refers to a feminine noun, I would look at the gender of the two nouns … only “the carriage” is feminine. So I would interpret that the carriage is blue — the colour of the car is not given.",
                                      "Die Information „sie ist blau“ bezieht sich auf eines der beiden Objekte. Da „sie“ typischerweise für weibliche Substantive verwendet wird, würde ich nach dem Genus der beiden Nomen schauen … nur „die Kutsche“ ist weiblich. Daher würde ich interpretieren, dass die Kutsche blau ist — die Farbe des Autos wurde nicht angegeben.")))],
               "GPT-4 · " + L(T("April 2024, shortened; the example only works in German, where “Kutsche” is feminine", "April 2024, gekürzt")))
        + dia_transformer(lang)
        + L(T("<p>To produce an answer, a GPT outputs only the most likely next word — more precisely the next text fragment, a <i>token</i> — and repeats this for its own output until the answer is complete:</p>",
              "<p>Um eine Antwort zu erzeugen, gibt ein GPT nur das wahrscheinlichste nächste Wort aus — genauer: das nächste Textelement, ein <i>Token</i> — und wiederholt das für seine eigene Ausgabe, bis die Antwort fertig ist:</p>"))
        + dia_next_token(lang)
        + L(T("<p>The second aspect is the sheer amount of training. LLMs are trained on enormous amounts of data and therefore handle the nuances of human language very well. Input may be ungrammatical, misspelt and colloquial — the model has seen all of that before.</p>",
              "<p>Der zweite Aspekt ist der schiere Umfang des Trainings. LLMs werden auf enormen Datenmengen trainiert und verarbeiten die Nuancen menschlicher Sprache deshalb sehr gut. Eingaben dürfen grammatikalisch ungenau, voller Rechtschreibfehler und umgangssprachlich sein — das Modell kennt all das aus seinen Trainingsdaten.</p>"))
        + chat(lang, [("user", L(T("Correct the spelling and grammar of this sentence: “Modle-drivn sofware developmnt a very exiting topic is!!”",
                                   "Überführe den folgenden Satz in korrekte Rechtschreibung und Grammatik: „Modelgetibene Softwär Enticklunk ein sehr spannendes Thema ist!!“"))),
                      ("GPT-4", L(T("“Model-driven software development is a very exciting topic!”", "„Modellgetriebene Softwareentwicklung ist ein sehr spannendes Thema!“")))], "GPT-4 · " + L(T("April 2024", "April 2024")))
        + L(T("<p>GPTs are a powerful tool for processing natural language. But because they are neural networks, they are neither transparent — you cannot trace how an output came about — nor deterministic: running the same prompt twice can give different results.</p>",
              "<p>GPTs sind also ein mächtiges Werkzeug, um natürliche Sprache zu verarbeiten. Weil sie aber auf neuronalen Netzen beruhen, sind sie weder transparent — man kann nicht nachvollziehen, wie eine Ausgabe zustande kam — noch deterministisch: Derselbe Prompt kann zweimal unterschiedliche Ergebnisse liefern.</p>"))))
    S.append(("se", T("AI in software engineering", "KI in der Softwareentwicklung"), L(T(
        f"""<p>Software engineering is a complex discipline with many hurdles: programming skills, experience in system modelling, domain knowledge and a lot of coordination between the stakeholders of the platform being built. Generative AI can already take over parts of this work and speed development up {ref(4)}. Assistants such as GitHub Copilot help programmers write parts of the source code. Far fewer approaches deal with modelling and generating whole systems.</p>
<p>Generative methods can create systems, or parts of them, from textual models: a generator reads a model and produces source code from it. Depending on what the code is for, different modelling languages fit — class diagrams for data structures, sequence diagrams for processes.</p>""",
        f"""<p>Softwareentwicklung ist eine komplexe Disziplin mit vielen Einstiegshürden: Programmierkenntnisse, Erfahrung in der Systemmodellierung, Domänenwissen und viel Abstimmung zwischen den Stakeholdern der zu entwickelnden Plattform. Generative KI kann uns schon heute Teile dieser Arbeit abnehmen und die Entwicklung beschleunigen {ref(4)}. Assistenten wie GitHub Copilot unterstützen Programmierer beim Schreiben von Teilen des Quellcodes. Deutlich weniger Ansätze befassen sich mit der Modellierung und Generierung ganzer Systeme.</p>
<p>Generative Methoden können aus textuellen Modellen Systeme oder Teile davon erzeugen: Ein Generator liest ein Modell und erzeugt daraus Quellcode. Je nachdem, wofür der Code gedacht ist, passen unterschiedliche Modellierungssprachen — Klassendiagramme für Datenstrukturen, Sequenzdiagramme für Abläufe.</p>"""))))
    S.append(("models", T("Language models that write models", "Sprachmodelle, die Modelle schreiben"), L(T(
        f"""<p>Defining good models takes knowledge: of modelling concepts, of the syntax of the modelling language and of the use case. LLMs can help most with the first two. With prompt engineering we can teach an LLM a modelling language {cite("BDMN+24")} {cite("NMR24")} — combining few-shot learning {ref(5)}, retrieval-augmented generation {ref(6)} and instructions to turn natural-language input into a textual model in the language of our choice.</p>""",
        f"""<p>Gute Modelle zu definieren erfordert Vorwissen: über Modellierungskonzepte, über die Syntax der Modellierungssprache und über den Anwendungsfall. LLMs können vor allem bei den ersten beiden helfen. Mit Prompt Engineering können wir einem LLM eine Modellierungssprache beibringen {cite("BDMN+24")} {cite("NMR24")} — mit einer Kombination aus Few-Shot-Learning {ref(5)}, Retrieval-Augmented Generation {ref(6)} und Instruktionen, die natürlichsprachliche Eingaben in ein textuelles Modell in der Sprache unserer Wahl übersetzen.</p>"""))
        + chat(lang, [("user", L(T("Create a simple model of a dog kennel", "Erzeuge mir ein einfaches Modell einer Hundehütte"))),
                      ("CD4A Model Creator", f"<pre><code>{kennel}</code></pre>")], "CD4A Model Creator")
        + L(T("<p>Try the assistants yourself:</p>", "<p>Probieren Sie die Assistenten selbst aus:</p>"))
        + f'<ul class="tries">{tries}</ul>'
        + L(T("<p>LLMs tuned for a modelling language can do more than create new models: they can change existing ones, or extract a model from a picture. A model sketched on a whiteboard can be photographed and turned into proper syntax.</p><p>What makes this reliable is what happens <i>after</i> the LLM. A parser checks every model; an invalid one goes back with the error message:</p>",
              "<p>LLMs, die auf eine Modellierungssprache angepasst sind, können mehr als neue Modelle erstellen: Sie können bestehende Modelle anpassen oder ein Modell aus einem Bild extrahieren. Ein am Whiteboard skizziertes Modell lässt sich fotografieren und in die passende Syntax überführen.</p><p>Verlässlich wird das erst durch das, was <i>nach</i> dem LLM passiert. Ein Parser prüft jedes Modell; ein ungültiges geht mit der Fehlermeldung zurück:</p>"))
        + dia_formalize(lang)
        + L(T(f"<p>Even better is to not let invalid models arise at all. With grammar masking, the grammar of the modelling language filters the LLM's token candidates while it writes {cite('NRR24')}:</p>",
              f"<p>Noch besser ist es, ungültige Modelle gar nicht erst entstehen zu lassen. Beim Grammar Masking filtert die Grammatik der Modellierungssprache die Token-Kandidaten des LLMs, während es schreibt {cite('NRR24')}:</p>"))
        + dia_grammar_mask(lang) + masking_table(lang)
        + L(T("<p>Small open models running locally then produce valid models more than nine times out of ten — instead of between almost never and four times out of ten. The price is runtime.</p>",
              "<p>Kleine, lokal laufende offene Modelle liefern dann in mehr als neun von zehn Fällen gültige Modelle — statt zwischen fast nie und vier von zehn Mal. Der Preis ist die Laufzeit.</p>"))))
    S.append(("mde", T("From a sentence to an application", "Vom Satz zur Anwendung"), L(T(
        f"""<p>Put together with model-driven engineering, this goes all the way: users describe their domain informally, an LLM derives the class diagrams, and a generator such as <a href="projects-montigem.html">MontiGem</a> turns them into a complete information system {cite("NMR24")} {cite("Net24")}.</p>""",
        f"""<p>Zusammen mit modellgetriebener Softwareentwicklung reicht das bis zum Ende: Nutzer beschreiben ihre Domäne informell, ein LLM leitet daraus Klassendiagramme ab, und ein Generator wie <a href="projects-montigem.html">MontiGem</a> macht daraus ein vollständiges Informationssystem {cite("NMR24")} {cite("Net24")}.</p>"""))
        + dia_ai_mde(lang)))
    S.append(("embeddings", T("Further uses: requirements and semantic search", "Weitere Anwendungen: Anforderungen und semantische Suche"), L(T(
        "<p>Models help far beyond generating software artefacts. Requirements can be translated from natural language into a formal language a computer can analyse; contradictions and redundancies found there can be translated back into natural language by an LLM.</p><p>LLMs can also take in large collections of specifications. Because they turn their input into semantic vectors — <i>embeddings</i> — they recognise similarity between words and texts:</p>",
        "<p>Modelle helfen weit über die Generierung von Software-Artefakten hinaus. Anforderungen lassen sich aus natürlicher Sprache in eine formale, vom Computer analysierbare Sprache übersetzen; dort gefundene Widersprüche und Redundanzen kann ein LLM wieder in natürliche Sprache zurückübersetzen.</p><p>Auch große Spezifikationssammlungen können LLMs erfassen. Weil sie ihre Eingaben in semantische Vektoren übersetzen — <i>Embeddings</i> —, erkennen sie Ähnlichkeiten zwischen Wörtern und Texten:</p>"))
        + dia_embeddings(lang)
        + L(T("<p>That makes semantic search in knowledge bases possible: users describe their problem and get the matching content, without having to know which terms to search for. Combined with an LLM, this is retrieval-augmented generation:</p>",
              "<p>Das ermöglicht eine semantische Suche in Wissensdatenbanken: Nutzer umschreiben ihr Problem und erhalten passende Inhalte, ohne wissen zu müssen, nach welchen Begriffen sie suchen müssten. Zusammen mit einem LLM ergibt das Retrieval-Augmented Generation:</p>"))
        + dia_rag(lang)))
    S.append(("hallucinations", T("Hallucinations", "Halluzinationen"), L(T(
        """<p>LLMs are built on a stochastic model. So an LLM does not necessarily give the correct answer, but the most plausible one. As long as the requested information lies within the training data, the most plausible answer is often also the right one; the further outside the training data you go, the more likely it is that the LLM presents a wrong answer very plausibly.</p>
<p>Hallucinations are hard to spot, because they are hard to tell apart from correct statements: they always fit the context of the question and rarely contain obvious errors. The following example shows a mistake any human sees at once — and the model does not. Nothing in the answer reveals its uncertainty.</p>""",
        """<p>LLMs beruhen auf einem stochastischen Modell. Ein LLM gibt deshalb nicht zwingend die korrekte Antwort, sondern die plausibelste. Solange die gefragte Information innerhalb der Trainingsdaten liegt, ist die plausibelste Antwort oft auch die richtige; je weiter man sich aber außerhalb der Trainingsdaten bewegt, desto wahrscheinlicher präsentiert das LLM eine falsche Antwort sehr plausibel.</p>
<p>Halluzinationen sind schwer zu erkennen, weil sie sich kaum von korrekten Aussagen unterscheiden: Sie passen immer gut in den Kontext der Frage und enthalten selten offensichtliche Fehler. Das folgende Beispiel zeigt einen Fehler, den ein Mensch sofort sieht — das Modell nicht. Nichts an der Antwort verrät ihre Unsicherheit.</p>"""))
        + chat(lang, [("user", L(T("Create an image with exactly 17 blue dots.", "Erstelle ein Bild mit genau 17 blauen Punkten."))),
                      ("GPT-4", L(T("Here is the image with exactly 17 blue dots on a white background.", "Hier ist das Bild mit genau 17 blauen Punkten auf weißem Hintergrund."))
                       + f'<img class="chat-img" src="{A}assets/ai4se/dots.webp" alt="{L(T("Generated image with considerably more than 17 blue dots", "Generiertes Bild mit deutlich mehr als 17 blauen Punkten"))}" width="260" height="260" loading="lazy">'),
                      ("user", L(T("How many blue dots are in the image?", "Wie viele blaue Punkte sind in dem Bild?"))),
                      ("GPT-4", L(T("The image contains exactly 17 blue dots on a white background.", "Das Bild enthält genau 17 blaue Punkte auf weißem Hintergrund.")))], "GPT-4 · " + L(T("April 2024", "April 2024")))
        + L(T(f"<p>Reasoning is just as fragile. “Alice has 5 sisters and 3 brothers. How many sisters does a brother of Alice have?” — state-of-the-art models answered this correctly only a fraction of the time {ref(7)}. LLMs imitate language very well, but they have no concept of logic of their own. Tools close part of the gap: code interpreters, function calls, APIs.</p><p>This is the strongest argument for letting LLMs produce <i>models</i>: a generated model can be analysed and checked, which rules out many sources of error before a single line of code exists {cite('NKR+25')}.</p>",
              f"<p>Genauso brüchig ist das Schlussfolgern. „Alice hat 5 Schwestern und 3 Brüder. Wie viele Schwestern hat ein Bruder von Alice?“ — aktuelle Modelle beantworteten das nur in einem Bruchteil der Fälle richtig {ref(7)}. LLMs imitieren Sprache sehr gut, haben aber selbst kein Konzept von Logik. Werkzeuge schließen einen Teil der Lücke: Code-Interpreter, Function Calls, APIs.</p><p>Das ist das stärkste Argument dafür, LLMs <i>Modelle</i> erzeugen zu lassen: Ein generiertes Modell lässt sich analysieren und prüfen, und damit lassen sich viele Fehlerquellen ausschließen, bevor auch nur eine Zeile Code existiert {cite('NKR+25')}.</p>"))))
    S.append(("summary", T("In short", "Kurz gesagt"), L(T(
        "<p>AI cannot replace a developer yet; it is best seen as a tool that speeds up the development process. Everything it produces needs checking and validation — it cannot be used blindly. Where AI meets models, that check becomes possible: the model is the place where language turns into something a machine can verify.</p>",
        "<p>KI kann einen Entwickler noch nicht ersetzen; sie ist am besten als Werkzeug zu verstehen, das den Entwicklungsprozess beschleunigt. Alles, was sie erzeugt, braucht Prüfung und Validierung — blind einsetzen lässt sie sich nicht. Wo KI auf Modelle trifft, wird diese Prüfung möglich: Das Modell ist die Stelle, an der aus Sprache etwas wird, das eine Maschine verifizieren kann.</p>"))))
    out = []
    for sid, head, html in S:
        h = f'<h2 id="{sid}">{L(head)}</h2>' if head else ""
        out.append(f'      <section class="art-sec">{h}{html}</section>')
    toc = "".join(f'<a href="#{sid}">{L(head)}</a>' for sid, head, _ in S if head)
    refs = "".join(f'<li id="ref-{k}">{r}</li>' for k, r in enumerate(REFS, 1))
    return toc, NL.join(out), refs


def page(lang):
    """Returns (file, title, description, body) for build.py."""
    L = lambda x: x[lang]
    A = "../" if lang == "de" else ""
    toc, sections, refs = body(lang, A)
    html = f'''
    <header class="page proj">
      <a class="back mono" href="research.html">← {L(T("research", "Forschung"))}</a>
      <div class="section-head">
        <h1><span class="mono">02</span>AI-driven Software Engineering</h1>
        <span class="mono faint">{L(T("article · 2024, revised 2026", "Artikel · 2024, überarbeitet 2026"))}</span>
      </div>
      <p class="lead">{L(T("What is this “new” AI, how does it work — and where does it actually help in building software? An introduction from neurons to <em>language models that write models</em>.",
                          "Was ist diese „neue“ KI, wie funktioniert sie — und wo hilft sie beim Bauen von Software wirklich? Eine Einführung vom Neuron bis zu <em>Sprachmodellen, die Modelle schreiben</em>."))}</p>
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
    desc = T("AI-driven software engineering: how LLMs work, and how they can write models that generators turn into software — an article by Lukas Netz.",
             "KI-getriebene Softwareentwicklung: wie LLMs funktionieren und wie sie Modelle schreiben, aus denen Generatoren Software machen — ein Artikel von Lukas Netz.")
    return FILE, T("AI-driven Software Engineering", "AI-driven Software Engineering"), desc, html
