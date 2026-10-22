// Interactive figures of the AI4SE article (research-ai4se.html, built by _build/ai4se.py).
// Each figure carries its data in data-json; without this script the static content stays.
// Uses the shared helpers of assets/demo-common.js (window.SiteDemo: stepper, autoplay rule, height lock).
//   nt — next-token prediction: stepped; temperature reshapes the distribution; "draw again" draws real random
//        numbers, the tally counts the answers
//   nn — a small neural network: a forward pass when it comes into view; the calculation of the neuron the
//        visitor points at; stacked layout on phones
//   wg — attention on a Winograd pair: one word flips the referent (chips, no autoplay)
//   ag — an agent run as a stepped trace
//   gm — grammar masking: the LLM proposes, the grammar removes, a token is appended (JSON · CD4A)
(() => {
  const D = window.SiteDemo;
  const reduce = D.reduce;
  const de = document.documentElement.lang === "de";
  const NS = "http://www.w3.org/2000/svg";
  const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const fix = n => (de ? n.toFixed(2).replace(".", ",") : n.toFixed(2));
  const quote = t => (de ? `„${t}“` : `“${t}”`);
  const svgEl = (tag, attrs, text) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    return e;
  };

  // ---------------- shared: a list of probability bars ----------------
  function barRows(ol, rows) {
    // rows: [{tok, p, ghost, cls, label}] — reuses the <li>s so the widths can transition.
    // ghost: a faint second bar behind (gm: the share before the grammar removed some)
    while (ol.children.length < rows.length) {
      const li = document.createElement("li");
      li.innerHTML = '<span class="tok"></span><span class="bar"><b></b><i></i></span><span class="p"></span>';
      ol.append(li);
    }
    while (ol.children.length > rows.length) ol.lastChild.remove();
    rows.forEach((r, k) => {
      const li = ol.children[k];
      li.className = r.cls || "";
      li.querySelector(".tok").textContent = r.tok;
      li.querySelector(".bar i").style.width = `${(r.p * 100).toFixed(1)}%`;
      li.querySelector(".bar b").style.width = `${((r.ghost || 0) * 100).toFixed(1)}%`;
      li.querySelector(".p").textContent = r.label ?? fix(r.p);
    });
  }
  // tokens → text: no space before punctuation
  const join = toks => toks.reduce((s, t) => (!s || /^[.,!:;']/.test(t) ? s + t : `${s} ${t}`), "");

  // ---------------- nt: one token at a time ----------------
  function nextToken(fig) {
    const data = JSON.parse(fig.dataset.json), W = data.words, nodes = data.nodes;
    const out = fig.querySelector(".nt-out"), ol = fig.querySelector(".nt-probs ol"), where = fig.querySelector(".where");
    const cur = fig.querySelector(".nt-cur"), temp = fig.querySelector(".temp input"), tOut = fig.querySelector(".temp output");
    const strip = fig.querySelector(".strip"), mark = strip.querySelector(".mark"), rOut = fig.querySelector(".nt-r");
    const list = fig.querySelector(".nt-list"), again = fig.querySelector(".nt-again"), ten = fig.querySelector(".nt-ten");
    const T = () => +temp.value;
    // temperature: p_i ∝ p_i^(1/T) over the listed candidates (as in ai4se.py)
    const reshape = cands => {
      const w = cands.map(c => Math.pow(c[1], 1 / T())), sum = w.reduce((s, v) => s + v, 0);
      return w.map(v => v / sum);
    };
    const draw = (ps, r) => { let acc = 0; for (let j = 0; j < ps.length; j++) { acc += ps[j]; if (r < acc) return j; } return ps.length - 1; };
    // one answer: walk the graph, one random number per token
    const walk = rs => {
      const path = []; let n = 0, k = 0;
      while (n >= 0 && path.length < 12) {
        const node = nodes[n], ps = reshape(node.cands), r = rs[k] ?? Math.random(), j = draw(ps, r);
        path.push({ node, ps, j, r, tok: node.cands[j][0] });
        n = node.next[j]; k++;
      }
      return path;
    };
    const answer = path => join(path.map(s => s.tok).filter(t => t !== "<|END|>"));
    const fresh = () => Array.from({ length: 12 }, Math.random);
    let rs = data.seed.slice(), path = walk(rs);

    // the tally of answers at the current temperature
    let tally = new Map(), last = "";
    const count = a => { tally.set(a, (tally.get(a) || 0) + 1); last = a; };
    function showTally() {
      const n = [...tally.values()].reduce((s, v) => s + v, 0);
      if (!n) { list.innerHTML = `<li class="empty">${esc(W.empty)}</li>`; return; }
      const rows = [...tally].sort((a, b) => b[1] - a[1]);
      const shown = rows.slice(0, 4), rest = rows.slice(4).reduce((s, r) => s + r[1], 0);
      list.innerHTML = shown.map(([a, c]) => {
        const wrong = !/Paris/.test(a);
        return `<li class="${a === last ? "last" : ""}${wrong ? " wrong" : ""}"><span class="a">${esc(a)}</span><span class="c">× ${c}</span>${wrong ? `<span class="w">${esc(W.wrong)}</span>` : ""}</li>`;
      }).join("") + (rest ? `<li class="more"><span class="a">${esc(W.others)}</span><span class="c">× ${rest}</span></li>` : "")
        + `<li class="sum">${n} ${esc(W.answers)} · ${esc(W.at)} ${fix(T()).replace(/0$/, "")}</li>`;
    }

    function render(i) {
      const s = Math.floor(i / 2), drawn = i % 2 === 1, step = path[s], N = path.length;
      const toks = path.slice(0, s + (drawn ? 1 : 0)).map(t => t.tok).filter(t => t !== "<|END|>");
      const text = join(toks), newest = drawn && step.tok !== "<|END|>" ? step.tok : "";
      out.innerHTML = newest ? `${esc(text.slice(0, text.length - newest.length))}<span class="new">${esc(newest)}</span>` : esc(text);
      cur.hidden = drawn && s === N - 1;
      barRows(ol, step.node.cands.map(([tok], j) => ({
        tok, p: step.ps[j], cls: drawn ? (j === step.j ? "pick" : "off") : (j === 0 ? "top" : ""),
      })));
      // the draw: the shares side by side from 0 to 1, the random number as a mark
      while (strip.children.length - 1 < step.ps.length) strip.insertBefore(document.createElement("span"), mark);
      while (strip.children.length - 1 > step.ps.length) strip.firstChild.remove();
      step.ps.forEach((p, j) => {
        const seg = strip.children[j];
        seg.style.width = `${(p * 100).toFixed(2)}%`;
        seg.className = drawn && j === step.j ? "pick" : "";
        seg.title = step.node.cands[j][0];
      });
      mark.style.left = `${(step.r * 100).toFixed(1)}%`;
      strip.classList.toggle("drawn", drawn);
      rOut.textContent = drawn ? `${W.random} ${fix(step.r)} ${W.lands} ${quote(step.tok)}` : `${W.random}: …`;
      where.textContent = `${W.token} ${s + 1} · ` + (drawn
        ? (step.tok === "<|END|>" ? W.done : `${quote(step.tok)} ${W.drawn}${step.j > 0 ? ` — ${W.notTop}` : ""}`)
        : W.dist);
      if (drawn && s === N - 1 && !counted) { counted = true; count(answer(path)); showTally(); }
    }
    let counted = false;
    const st = D.stepper(fig, 2 * path.length, render, { delay: i => (i % 2 ? 900 : 700), label: false });
    const replace = newRs => { rs = newRs; path = walk(rs); counted = false; st.stop(); st.setCount(2 * path.length); st.show(0); };
    temp.addEventListener("input", () => {
      tOut.textContent = (de ? (+temp.value).toFixed(1).replace(".", ",") : (+temp.value).toFixed(1));
      tally = new Map(); last = "";
      // same random numbers, other temperature: the answer may change
      path = walk(rs); st.setCount(2 * path.length);
      counted = st.k >= 2 * path.length - 1;
      if (counted) count(answer(path));
      showTally();
    });
    again.addEventListener("click", () => { replace(fresh()); st.start(); });
    ten.addEventListener("click", () => {
      for (let k = 0; k < 9; k++) count(answer(walk(fresh())));
      replace(fresh()); st.show(2 * path.length - 1);   // the tenth one is shown in full
    });
    tOut.textContent = de ? "1,0" : "1.0";
    showTally();
  }

  // ---------------- nn: the dog network ----------------
  function neural(fig) {
    const data = JSON.parse(fig.dataset.json), W = data.words;
    const svg = fig.querySelector("svg.nn"), panel = svg.querySelector(".nn-panel"), lead = svg.querySelector(".nn-lead");
    const title = svg.querySelector(".nn-title"), gSrc = svg.querySelector(".nn-src"), gNet = svg.querySelector(".nn-net"), gCal = svg.querySelector(".nn-cal");
    const [px0, py0] = data.panel;
    // weights: hidden (4 × 5 inputs), output (2 × 4 hidden). Hand-picked so that h4 stays silent
    const W1 = [[.6, -.4, .5, .2, -.3], [-.2, .7, .3, -.5, .6], [.4, .1, -.6, .8, .2], [-.5, -.3, .2, .4, -.6]];
    const W2 = [[1.4, 1.1, -.6, .5], [-.8, -.5, .9, .7]];
    let x = [.6, .35, .85, .7, .4];            // replaced by the real pixel brightness once the image is read
    let z1, h, z2, y;
    const forward = () => {
      z1 = W1.map(w => w.reduce((s, wi, i) => s + wi * x[i], 0));
      h = z1.map(v => Math.max(0, v));
      z2 = W2.map(w => w.reduce((s, wi, i) => s + wi * h[i], 0));
      const e = z2.map(v => Math.exp(v)), sum = e[0] + e[1];
      y = e.map(v => v / sum);
    };
    forward();
    const img = new Image();
    img.onload = () => {
      try {
        const c = document.createElement("canvas"); c.width = img.naturalWidth; c.height = img.naturalHeight;
        const g = c.getContext("2d"); g.drawImage(img, 0, 0);
        const cw = c.width / 16, ch = c.height / 16;
        x = data.pixels.map(([col, row]) => {
          const [r, gr, b] = g.getImageData(Math.floor((col + .5) * cw), Math.floor((row + .5) * ch), 1, 1).data;
          return Math.round((.299 * r + .587 * gr + .114 * b) / 255 * 100) / 100;
        });
        forward(); if (!playing) settle();
      } catch (_) { /* tainted canvas: keep the stand-in values */ }
    };
    img.src = data.px;

    const nodes = [...svg.querySelectorAll(".nn-n")], edges = [...svg.querySelectorAll(".nn-e")];
    const node = (l, i) => nodes.find(n => +n.dataset.l === l && +n.dataset.i === i);
    const act = (l, i, a) => { node(l, i).querySelector(".nn-act").style.opacity = Math.min(1, a).toFixed(2); };
    const value = l => (l === 0 ? x : l === 1 ? h : y);
    let sel = [2, 0], playing = false, timers = [];

    // ---- layout: wide (as built) or stacked for phones; the feed lines and the lead are drawn in root coordinates
    const off = { src: [0, 0], net: [0, 0], cal: [0, 0] };
    const pixelAt = i => { const [c, r] = data.pixels[i]; return [140 + (c + .5) * 7.5 + off.src[0], 40 + (r + .5) * 7.5 + off.src[1]]; };
    const nodeAt = (l, i) => { const c = node(l, i).querySelector("circle.box"); return [+c.getAttribute("cx") + off.net[0], +c.getAttribute("cy") + off.net[1], +c.getAttribute("r")]; };
    function layout() {
      const narrow = matchMedia("(max-width: 600px)").matches;
      if (narrow) { off.src = [56, -32]; off.net = [-290, 150]; off.cal = [-298, 112]; svg.setAttribute("viewBox", "0 0 372 580"); }
      else { off.src = [0, 0]; off.net = [0, 0]; off.cal = [0, 0]; svg.setAttribute("viewBox", svg.dataset.wide); }
      gSrc.setAttribute("transform", `translate(${off.src})`);
      gNet.setAttribute("transform", `translate(${off.net})`);
      gCal.setAttribute("transform", `translate(${off.cal})`);
      fig.classList.toggle("nn-tall", narrow);
      svg.querySelectorAll(".nn-feed").forEach(p => {
        const i = +p.dataset.i, [a, b] = pixelAt(i), [c, d, r] = nodeAt(0, i);
        p.setAttribute("d", `M${a} ${b}L${c - 30} ${d}`);
      });
      drawLead();
    }
    const drawLead = () => {
      if (sel[0] === 0) return;
      const [cx, cy, r] = nodeAt(sel[0], sel[1]);
      lead.setAttribute("d", `M${cx} ${cy + r}V${py0 + off.cal[1]}`);
    };
    matchMedia("(max-width: 600px)").addEventListener("change", layout);

    const values = show => svg.querySelectorAll(".nn-v").forEach(t => { t.textContent = show ? fix(x[+t.dataset.i]) : ""; });
    const bars = show => {
      svg.querySelectorAll(".nn-bar").forEach(b => b.setAttribute("width", show ? (y[+b.dataset.i] * 56).toFixed(1) : 0));
      svg.querySelectorAll(".nn-pv").forEach(t => { t.textContent = show ? fix(y[+t.dataset.i]) : ""; });
    };
    // edges: weight as width, sign as dash
    edges.forEach(e => {
      const l = +e.dataset.l, w = (l === 1 ? W1 : W2)[+e.dataset.j][+e.dataset.i];
      e.style.strokeWidth = (.5 + Math.abs(w) * 1.2).toFixed(2);
      e.classList.toggle("neg", w < 0);
    });

    function select(l, i) {
      if (l === 0) return;
      sel = [l, i];
      nodes.forEach(n => n.classList.toggle("sel", +n.dataset.l === l && +n.dataset.i === i));
      edges.forEach(e => {
        const into = +e.dataset.l === l && +e.dataset.j === i;
        e.classList.toggle("in", into);
        e.classList.toggle("dim", !into);
      });
      drawLead();
      drawPanel(l, i);
    }

    // the calculation of one neuron, in the panel (368 × 210 at px0, py0)
    function drawPanel(l, i) {
      panel.replaceChildren();
      const ins = l === 1 ? x : h, w = (l === 1 ? W1 : W2)[i], z = (l === 1 ? z1 : z2)[i], out = value(l)[i];
      const names = ins.map((_, k) => (l === 1 ? `x${k + 1}` : `h${k + 1}`));
      title.textContent = `${W.one} · ${l === 1 ? `h${i + 1}` : [W.dog, W.cat][i]}`;
      const X = px0, cy = py0 + 118, n = ins.length, gap = n > 4 ? 26 : 30;
      const add = (tag, a, t) => panel.append(svgEl(tag, a, t));
      add("text", { x: X + 14, y: py0 + 44, class: "s" }, W.inputs);
      add("text", { x: X + 108, y: py0 + 44, class: "s", "text-anchor": "middle" }, W.weights);
      add("text", { x: X + 200, y: py0 + 44, class: "s", "text-anchor": "middle" }, W.sum);
      add("text", { x: X + 318, y: py0 + 44, class: "s", "text-anchor": "middle" }, W.out);
      ins.forEach((v, k) => {
        const ry = cy + (k - (n - 1) / 2) * gap;
        add("text", { x: X + 14, y: ry + 4, class: "s" }, names[k]);
        add("text", { x: X + 76, y: ry + 4, "text-anchor": "end" }, fix(v));
        add("path", { class: "ln sw-hair", d: `M${X + 80} ${ry}H${X + 92}` });
        add("circle", { class: `box${w[k] < 0 ? " neg" : " pos"}`, cx: X + 108, cy: ry, r: 14 });
        add("text", { x: X + 108, y: ry + 3.5, "text-anchor": "middle", class: "s nn-w" }, (w[k] > 0 ? "+" : "−") + Math.abs(w[k]).toFixed(1).replace(".", de ? "," : "."));
        const p = svgEl("path", { class: "ln", d: `M${X + 122} ${ry}L${X + 180} ${cy}` });
        p.style.strokeWidth = (.5 + Math.abs(w[k] * v) * 2).toFixed(2);
        panel.append(p);
      });
      add("circle", { class: "box hl", cx: X + 200, cy, r: 20 });
      add("text", { x: X + 200, y: cy + 5, "text-anchor": "middle", class: "t" }, "Σ");
      add("text", { x: X + 200, y: cy + 36, "text-anchor": "middle" }, fix(z));
      add("path", { class: "ln", d: `M${X + 220} ${cy}H${X + 236}`, "marker-end": "url(#nna)" });
      add("rect", { class: "box", x: X + 240, y: cy - 18, width: 40, height: 36, rx: 3 });
      add("text", { x: X + 260, y: cy + 5, "text-anchor": "middle", class: "t" }, l === 1 ? "≥ 0" : "%");
      add("text", { x: X + 260, y: cy - 26, "text-anchor": "middle", class: "s" }, l === 1 ? W.relu : W.share);
      add("path", { class: "ln", d: `M${X + 280} ${cy}H${X + 298}`, "marker-end": "url(#nna)" });
      add("circle", { class: "box", cx: X + 318, cy, r: 16 });
      const o = svgEl("circle", { class: "nn-act", cx: X + 318, cy, r: 16 });
      o.style.opacity = Math.min(1, out).toFixed(2);
      panel.append(o);
      add("text", { x: X + 318, y: cy + 36, "text-anchor": "middle", class: "t" }, fix(out));
      if (l === 1 && out === 0) add("text", { x: X + 318, y: cy + 50, "text-anchor": "middle", class: "s a" }, W.silent);
    }

    // the final, resting state
    function settle() {
      x.forEach((v, i) => act(0, i, v)); h.forEach((v, i) => act(1, i, v / 1.2)); y.forEach((v, i) => act(2, i, v));
      values(true); bars(true);
      svg.querySelectorAll(".nn-px, .nn-feed").forEach(e => e.classList.remove("on"));
      select(...sel);
    }
    const stop = () => { if (!playing) return; timers.forEach(clearTimeout); timers = []; playing = false; settle(); };
    // a forward pass: pixels → inputs → hidden → output
    function playPass() {
      timers.forEach(clearTimeout); timers = [];
      playing = true;
      edges.forEach(e => e.classList.remove("in")); nodes.forEach(n => n.classList.remove("sel"));
      nodes.forEach(n => { n.querySelector(".nn-act").style.opacity = 0; });
      values(false); bars(false);
      edges.forEach(e => e.classList.add("dim"));
      const at = (ms, fn) => timers.push(setTimeout(fn, ms));
      x.forEach((v, i) => at(150 + i * 140, () => {
        svg.querySelectorAll(`.nn-px[data-i="${i}"], .nn-feed[data-i="${i}"]`).forEach(e => e.classList.add("on"));
        act(0, i, v);
        svg.querySelector(`.nn-v[data-i="${i}"]`).textContent = fix(v);
      }));
      at(950, () => edges.forEach(e => { if (e.dataset.l === "1") { e.classList.remove("dim"); e.classList.add("flow"); } }));
      at(1700, () => { h.forEach((v, i) => act(1, i, v / 1.2)); edges.forEach(e => { if (e.dataset.l === "1") e.classList.replace("flow", "dim"); }); });
      at(1900, () => edges.forEach(e => { if (e.dataset.l === "2") { e.classList.remove("dim"); e.classList.add("flow"); } }));
      at(2650, () => { y.forEach((v, i) => act(2, i, v)); bars(true); edges.forEach(e => e.classList.remove("flow")); });
      at(3300, () => { playing = false; sel = [2, 0]; settle(); });
    }

    nodes.forEach(n => {
      const l = +n.dataset.l, i = +n.dataset.i;
      const enter = () => {
        if (playing) return;
        if (l === 0) {
          svg.querySelectorAll(`.nn-px[data-i="${i}"], .nn-feed[data-i="${i}"]`).forEach(e => e.classList.add("on"));
          edges.forEach(e => { const o = e.dataset.l === "1" && +e.dataset.i === i; e.classList.toggle("in", o); e.classList.toggle("dim", !o); });
        } else select(l, i);
      };
      const leave = () => {
        if (playing || l !== 0) return;
        svg.querySelectorAll(".nn-px, .nn-feed").forEach(e => e.classList.remove("on"));
        select(...sel);
      };
      n.addEventListener("pointerenter", enter);
      n.addEventListener("pointerleave", e => { if (e.pointerType === "mouse") leave(); });
      n.addEventListener("focus", enter);
      n.addEventListener("blur", leave);
      n.addEventListener("click", enter);
      n.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); enter(); } });
    });
    fig.querySelector(".replay").addEventListener("click", playPass);
    layout();
    settle();
    D.autoplay(fig, { start: playPass, stop });
  }

  // ---------------- wg: one word flips the reference ----------------
  function winograd(fig) {
    const data = JSON.parse(fig.dataset.json), W = data.words2;
    const sent = fig.querySelector(".wg-sent"), say = fig.querySelector(".wg-say");
    const chips = [...fig.querySelectorAll(".chips button")];
    let pick = 0;
    function render(k) {
      pick = k;
      const w = data.w[k], max = Math.max(...w);
      sent.innerHTML = data.words.map((word, i) => {
        const t = word.replace("{}", data.adj[k]);
        const cls = i === data.src ? "src" : i > data.src ? "after" : w[i] === max ? "ref" : i === data.it ? "it" : "";
        const bar = i < data.src ? `<i style="height:${Math.round(4 + w[i] * 46)}px" title="${fix(w[i])}"></i>` : "<i></i>";
        return `<span class="wg-w ${cls}">${bar}<b>${esc(t)}</b></span>`;
      }).join("");
      say.innerHTML = `${esc(W.reads)} ${quote(esc(data.adj[k]))} ${esc(W.looks)} ${quote(esc(data.words[data.w[k].indexOf(max)].replace(/,$/, "")))} — ${esc(W.means)} <b>${esc(data.who[k])}</b>.`;
      D.press(chips, chips[k]);
    }
    chips.forEach((b, k) => b.addEventListener("click", () => render(k)));
    D.lock(sent.parentElement, [0, 1], render, () => pick);
    render(0);
  }

  // ---------------- ag: an agent run ----------------
  function agent(fig) {
    const data = JSON.parse(fig.dataset.json), W = data.words, n = data.n;
    const rows = [...fig.querySelectorAll(".ag-trace li")], say = fig.querySelector(".ag-say"), where = fig.querySelector(".where");
    const box = id => fig.querySelector(`.ag-n[data-n="${id}"]`), edge = id => fig.querySelector(`.ag-e[data-e="${id}"]`);
    const count = 2 * n + 2;            // goal · (act, observe) × n · done
    function render(i) {
      const on = new Set();
      let text;
      if (i === 0) { on.add("llm"); text = W.goal; }
      else if (i === count - 1) { on.add("done"); on.add("e:done"); text = W.done; }
      else {
        const s = Math.floor((i - 1) / 2), obs = (i - 1) % 2 === 1;
        if (obs) { on.add("obs"); on.add("e:obs"); on.add("e:back"); text = W.obs; }
        else { on.add("llm"); on.add("act"); on.add("e:act"); text = W.act; }
      }
      ["llm", "act", "obs", "done"].forEach(id => box(id).classList.toggle("on", on.has(id)));
      ["act", "obs", "back", "done"].forEach(id => edge(id).classList.toggle("on", on.has("e:" + id)));
      rows.forEach((li, k) => {
        const a = 1 + 2 * k;                 // the step at which row k's action appears
        li.classList.toggle("shown", i >= a);
        li.classList.toggle("seen", i >= a + 1);
        li.classList.toggle("now", i === a || i === a + 1);
      });
      say.textContent = text;
      where.textContent = `${W.step} ${i + 1} ${W.of} ${count}`;
    }
    D.stepper(fig, count, render, { delay: i => (i === 0 ? 1100 : 900), label: false, lock: [say] });
  }

  // ---------------- gm: grammar masking ----------------
  function grammar(fig) {
    const data = JSON.parse(fig.dataset.json), W = data.words;
    const code = fig.querySelector(".gm-code code"), cur = fig.querySelector(".gm-code .nt-cur");
    const ol = fig.querySelector(".gm-cands ol"), phase = fig.querySelector(".gm-phase"), where = fig.querySelector(".where");
    const wEl = fig.querySelector(".gm-where"), allowed = fig.querySelector(".gm-allowed"), stack = fig.querySelector(".gm-stack");
    const chips = [...fig.querySelectorAll(".gm-head button")];
    let g = data.g.json, name = "json";
    // pretty-print the tokens written so far (JSON and CD4A alike)
    const format = toks => {
      let s = "", ind = 0, bol = true;
      for (const t of toks) {
        if (t === "<|END|>") continue;
        if (t === "}") { ind--; if (!bol) s += "\n"; s += "  ".repeat(Math.max(0, ind)) + "}"; bol = false; continue; }
        if (bol) s += "  ".repeat(ind); else if (t !== ";" && t !== ",") s += " ";
        s += t; bol = false;
        if (t === "{") { s += "\n"; ind++; bol = true; } else if (t === ";" || t === ",") { s += "\n"; bol = true; }
      }
      return s;
    };
    function render(i) {
      const s = Math.floor(i / 2), ph = i % 2, step = g.steps[s], N = g.steps.length;
      const done = g.steps.slice(0, s + ph).map(t => t.pick);
      let html = esc(format(done));
      if (ph === 1 && step.pick !== "<|END|>") {     // the newest token stands out
        const last = esc(step.pick), at = html.lastIndexOf(last);
        if (at >= 0) html = html.slice(0, at) + `<span class="new">${last}</span>` + html.slice(at + last.length);
      }
      code.innerHTML = html;
      cur.hidden = ph === 1 && s === N - 1;
      // the candidates stay in the LLM's order: 1 its shares · 2 the grammar removes some, the rest is rescaled
      // (the old share stays as a ghost) and the most likely remaining one is appended
      const okSum = step.cands.reduce((a, c) => a + (c[2] ? c[1] : 0), 0), top = step.cands[0];
      barRows(ol, step.cands.map(([tok, p, ok]) => {
        if (ph === 0) return { tok, p, cls: "raw" };
        if (!ok) return { tok, p: 0, ghost: p, cls: "masked", label: "✗" };
        return { tok, p: p / okSum, ghost: p, cls: tok === step.pick ? "pick" : "ok" };
      }));
      phase.textContent = ph === 0 ? W.p0 : `${W.p1} ${top[2] ? W.agree : `${W.would} ${quote(top[0])}.`}`;
      phase.classList.toggle("hit", ph === 1 && !top[2]);
      const at = g.states[ph === 1 ? step.to : step.from];
      wEl.textContent = `${W.where}: ${at[0]}`;
      allowed.textContent = `${W.allowed}: ${at[1]}`;
      const depth = done.filter(t => t === "{").length - done.filter(t => t === "}").length;
      stack.textContent = `${W.stack}: ${depth ? "{ ".repeat(depth).trim() : W.none}`;
      where.textContent = `${W.step} ${s + 1} ${W.of} ${N}`;
    }
    const st = D.stepper(fig, 2 * g.steps.length, render, { delay: i => (i % 2 ? 1300 : 900), label: false });
    // the phase text and the status lines must not change the figure's height: lock over both grammars
    const all = Object.keys(data.g).flatMap(k => data.g[k].steps.flatMap((_, s) => [[k, 2 * s], [k, 2 * s + 1]]));
    const as = ([k, i]) => { g = data.g[k]; render(i); };
    [phase, fig.querySelector(".gm-status"), fig.querySelector(".gm-code pre")].forEach(el =>
      D.lock(el, all, as, () => [name, st.k]));
    chips.forEach(b => b.addEventListener("click", () => {
      if (b.dataset.g === name) return;
      name = b.dataset.g; g = data.g[name];
      D.press(chips, b);
      st.stop(); st.setCount(2 * g.steps.length); st.show(0); st.start();
    }));
  }

  const kinds = { nt: nextToken, nn: neural, wg: winograd, ag: agent, gm: grammar };
  document.querySelectorAll("figure.demo[data-demo]").forEach(fig => {
    try { kinds[fig.dataset.demo]?.(fig); } catch (e) { console.error(e); }
  });
})();
