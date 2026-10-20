// Interactive figures of the AI4SE article (research-ai4se.html, built by _build/ai4se.py).
// Each figure carries its data in data-json; without this script the static SVG stays.
//   nn — a small neural network: plays a forward pass when it comes into view, shows the
//        calculation of the neuron the visitor points at
//   nt — next-token prediction, stepped with a slider; temperature reshapes the distribution
//   gm — grammar masking: the LLM proposes, the grammar filters, a token is appended
(() => {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const NS = "http://www.w3.org/2000/svg";
  const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const fix = n => n.toFixed(2);
  const svgEl = (tag, attrs, text) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    return e;
  };
  // run once, when at least a third of the element is visible
  const whenSeen = (el, fn) => {
    if (!("IntersectionObserver" in window)) return fn();
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { io.disconnect(); fn(); } }, { threshold: .35 });
    io.observe(el);
  };

  // ---------------- a stepper: play button, step slider, label ----------------
  function stepper(fig, count, render, delay) {
    const play = fig.querySelector(".play"), range = fig.querySelector("input.step");
    let k = 0, timer = null;
    range.max = count - 1;
    const words = JSON.parse(fig.dataset.json).words;
    const show = i => { k = i; range.value = i; render(i); };
    const stop = () => { clearTimeout(timer); timer = null; play.textContent = k >= count - 1 ? "↺" : "▶"; play.setAttribute("aria-label", words.play); };
    const tick = () => {
      if (k >= count - 1) return stop();
      show(k + 1);
      timer = setTimeout(tick, delay(k));
    };
    const start = () => {
      if (k >= count - 1) show(0);
      play.textContent = "❚❚"; play.setAttribute("aria-label", words.pause);
      timer = setTimeout(tick, delay(k));
    };
    play.addEventListener("click", () => (timer ? stop() : start()));
    range.addEventListener("input", () => { if (timer) stop(); show(+range.value); stop(); });
    show(0); stop();
    // the number of steps can change (nt: another temperature, another path); stay on the step, re-render
    const setCount = n => { count = n; range.max = n - 1; show(Math.min(k, n - 1)); if (!timer) stop(); };
    return { start, show, setCount, get k() { return k; } };
  }

  // ---------------- nn: the dog network ----------------
  function neural(fig) {
    const data = JSON.parse(fig.dataset.json), W = data.words;
    const svg = fig.querySelector("svg.nn"), panel = svg.querySelector(".nn-panel"), lead = svg.querySelector(".nn-lead");
    const title = svg.querySelector(".nn-title");
    // weights: hidden (4 × 5 inputs), output (2 × 4 hidden). Hand-picked so that h4 stays silent (ReLU)
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

    const values = show => {
      svg.querySelectorAll(".nn-v").forEach(t => { t.textContent = show ? fix(x[+t.dataset.i]) : ""; });
    };
    const bars = show => {
      svg.querySelectorAll(".nn-bar").forEach(b => b.setAttribute("width", show ? (y[+b.dataset.i] * 110).toFixed(1) : 0));
      svg.querySelectorAll(".nn-pv").forEach(t => { t.textContent = show ? fix(y[+t.dataset.i]) : ""; });
    };
    // edges of one layer: weight as width, sign as colour
    const weightEdges = () => edges.forEach(e => {
      const l = +e.dataset.l, w = (l === 1 ? W1 : W2)[+e.dataset.j][+e.dataset.i];
      e.style.strokeWidth = (.4 + Math.abs(w) * 1.6).toFixed(2);
      e.classList.toggle("neg", w < 0);
    });
    weightEdges();

    function select(l, i) {
      if (l === 0) return;
      sel = [l, i];
      nodes.forEach(n => n.classList.toggle("sel", +n.dataset.l === l && +n.dataset.i === i));
      edges.forEach(e => {
        const into = +e.dataset.l === l && +e.dataset.j === i;
        e.classList.toggle("in", into);
        e.classList.toggle("dim", !into);
      });
      const c = node(l, i).querySelector("circle");
      lead.setAttribute("d", `M${c.getAttribute("cx")} ${+c.getAttribute("cy") + +c.getAttribute("r")}V258`);
      drawPanel(l, i);
    }
    function unselect() {
      edges.forEach(e => e.classList.remove("in", "dim"));
    }

    // the calculation of one neuron, below the network
    function drawPanel(l, i) {
      panel.replaceChildren();
      const ins = l === 1 ? x : h, w = (l === 1 ? W1 : W2)[i], z = (l === 1 ? z1 : z2)[i], out = value(l)[i];
      const names = ins.map((_, k) => (l === 1 ? `x${k + 1}` : `h${k + 1}`));
      const who = l === 1 ? `h${i + 1}` : [W.dog, W.cat][i];
      title.textContent = `${W.one} · ${who}`;
      const cy = 364, n = ins.length, gap = 32;
      const add = (tag, a, t) => panel.append(svgEl(tag, a, t));
      add("text", { x: 306, y: 280, class: "s" }, W.inputs);
      add("text", { x: 398, y: 280, class: "s", "text-anchor": "middle" }, W.weights);
      add("text", { x: 500, y: 280, class: "s", "text-anchor": "middle" }, "Σ");
      add("text", { x: 638, y: 280, class: "s", "text-anchor": "middle" }, W.out);
      ins.forEach((v, k) => {
        const ry = cy + (k - (n - 1) / 2) * gap;
        add("text", { x: 306, y: ry + 4, class: "s" }, names[k]);
        add("text", { x: 362, y: ry + 4, "text-anchor": "end" }, fix(v));
        add("path", { class: "ln", d: `M366 ${ry}H384` });
        add("circle", { class: `box${w[k] < 0 ? " neg" : " pos"}`, cx: 398, cy: ry, r: 14 });
        add("text", { x: 398, y: ry + 3.5, "text-anchor": "middle", class: "s", style: "font-size:9px" }, (w[k] > 0 ? "+" : "") + w[k].toFixed(1));
        const p = svgEl("path", { class: "ln", d: `M412 ${ry}L480 ${cy}` });
        p.style.strokeWidth = (.4 + Math.abs(w[k] * v) * 2.4).toFixed(2);
        panel.append(p);
      });
      add("circle", { class: "box hl", cx: 500, cy, r: 20 });
      add("text", { x: 500, y: cy + 5, "text-anchor": "middle", class: "t" }, "Σ");
      add("text", { x: 500, y: cy + 36, "text-anchor": "middle" }, fix(z));
      add("path", { class: "ln", d: `M520 ${cy}H546`, "marker-end": "url(#nna)" });
      add("rect", { class: "box", x: 550, y: cy - 20, width: 40, height: 40, rx: 3 });
      add("text", { x: 570, y: cy + 5, "text-anchor": "middle", class: "t" }, "φ");
      add("text", { x: 570, y: cy + 56, "text-anchor": "middle", class: "s" }, l === 1 ? W.relu : W.softmax);
      add("path", { class: "ln", d: `M590 ${cy}H618`, "marker-end": "url(#nna)" });
      add("circle", { class: "box", cx: 638, cy, r: 16 });
      const o = svgEl("circle", { class: "nn-act", cx: 638, cy, r: 16 });
      o.style.opacity = Math.min(1, out).toFixed(2);
      panel.append(o);
      add("text", { x: 662, y: cy + 4, class: "t" }, fix(out));
      if (l === 1 && out === 0) add("text", { x: 662, y: cy + 20, class: "s" }, W.silent);
    }

    // the final, resting state
    function settle() {
      x.forEach((v, i) => act(0, i, v)); h.forEach((v, i) => act(1, i, v / 1.2)); y.forEach((v, i) => act(2, i, v));
      values(true); bars(true);
      svg.querySelectorAll(".nn-px, .nn-feed").forEach(e => e.classList.remove("on"));
      select(...sel);
    }
    // a forward pass: pixels → inputs → hidden → output
    function playPass() {
      timers.forEach(clearTimeout); timers = [];
      playing = true;
      unselect(); nodes.forEach(n => n.classList.remove("sel"));
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
          edges.forEach(e => { const out = e.dataset.l === "1" && +e.dataset.i === i; e.classList.toggle("in", out); e.classList.toggle("dim", !out); });
        } else select(l, i);
      };
      const leave = () => {
        if (playing || l !== 0) return;
        svg.querySelectorAll(".nn-px, .nn-feed").forEach(e => e.classList.remove("on"));
        select(...sel);
      };
      n.addEventListener("pointerenter", enter);
      n.addEventListener("pointerleave", leave);
      n.addEventListener("focus", enter);
      n.addEventListener("blur", leave);
      n.addEventListener("click", enter);
      n.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); enter(); } });
    });
    fig.querySelector(".replay").addEventListener("click", playPass);
    settle();
    if (!reduce) whenSeen(svg, playPass);
  }

  // ---------------- shared: a list of probability bars ----------------
  function barRows(ol, rows) {
    // rows: [{tok, p, ghost, cls, tag, label}] — reuses the <li>s so the widths can transition.
    // ghost: a faint second bar behind (gm: the share before the grammar filtered)
    while (ol.children.length < rows.length) {
      const li = document.createElement("li");
      li.innerHTML = '<span class="tok"></span><span class="bar"><b></b><i></i></span><span class="p"></span>';
      ol.append(li);
    }
    while (ol.children.length > rows.length) ol.lastChild.remove();
    rows.forEach((r, k) => {
      const li = ol.children[k];
      li.className = r.cls || "";
      li.querySelector(".tok").innerHTML = esc(r.tok) + (r.tag ? ` <em>${esc(r.tag)}</em>` : "");
      li.querySelector(".bar i").style.width = `${(r.p * 100).toFixed(1)}%`;
      li.querySelector(".bar b").style.width = `${((r.ghost || 0) * 100).toFixed(1)}%`;
      li.querySelector(".p").textContent = r.label ?? fix(r.p);
    });
  }
  const quote = t => (document.documentElement.lang === "de" ? `„${t}“` : `“${t}”`);
  const num = x => (document.documentElement.lang === "de" ? fix(x).replace(".", ",") : fix(x));

  // ---------------- nt: one token at a time ----------------
  function nextToken(fig) {
    const data = JSON.parse(fig.dataset.json), W = data.words, nodes = data.nodes;
    const out = fig.querySelector(".nt-out"), ol = fig.querySelector(".nt-probs ol"), where = fig.querySelector(".where");
    const cur = fig.querySelector(".nt-cur"), temp = fig.querySelector(".temp input"), tOut = fig.querySelector(".temp output");
    const strip = fig.querySelector(".strip"), mark = strip.querySelector(".mark"), rOut = fig.querySelector(".nt-r");
    // temperature: p_i ∝ p_i^(1/T); the tokens not shown share the remaining mass as one bucket (as in ai4se.py)
    const reshape = (cands, T) => {
      const rest = Math.max(0, 1 - cands.reduce((s, c) => s + c[1], 0));
      const w = cands.map(c => Math.pow(c[1], 1 / T)), wr = rest ? Math.pow(rest, 1 / T) : 0;
      const sum = w.reduce((s, v) => s + v, 0) + wr;
      return w.map(v => v / sum);
    };
    // the token whose share contains the node's random number r
    const draw = (ps, r) => { let acc = 0; for (let j = 0; j < ps.length; j++) { acc += ps[j]; if (r < acc) return j; } return 0; };
    // the answer at this temperature: walk the tree, one draw per node
    const walk = () => {
      const path = []; let n = 0;
      while (n != null && path.length < 12) {
        const node = nodes[n], ps = reshape(node.cands, +temp.value), j = draw(ps, node.r);
        path.push({ node, ps, j, tok: node.cands[j][0] });
        n = node.next[node.cands[j][0]];
      }
      return path;
    };
    let path = walk(), k = 0;
    function render(i) {
      k = i;
      const s = Math.floor(i / 2), drawn = i % 2 === 1, step = path[s], N = path.length;
      const toks = path.slice(0, s + (drawn ? 1 : 0)).map(t => t.tok).filter(t => t !== "<|END|>");
      out.innerHTML = toks.map((t, j) => `<span${drawn && j === toks.length - 1 ? ' class="new"' : ""}>${esc(t)}</span>`).join(" ");
      cur.hidden = drawn && s === N - 1;
      barRows(ol, step.node.cands.map(([tok], j) => ({
        tok, p: step.ps[j], cls: drawn ? (j === step.j ? "pick" : "off") : (j === 0 ? "top" : ""),
        tag: drawn && j === step.j ? W.sampled : "",
      })));
      // the draw: the shares side by side from 0 to 1, the random number as a mark
      while (strip.children.length < step.ps.length) strip.insertBefore(document.createElement("span"), mark);
      step.ps.forEach((p, j) => {
        const seg = strip.children[j];
        seg.style.width = `${(p * 100).toFixed(2)}%`;
        seg.className = drawn && j === step.j ? "pick" : "";
        seg.title = step.node.cands[j][0];
      });
      mark.style.left = `${(step.node.r * 100).toFixed(1)}%`;
      strip.classList.toggle("drawn", drawn);
      rOut.textContent = drawn ? `${W.random} ${num(step.node.r)} ${W.lands} ${quote(step.tok)}` : `${W.random}: …`;
      where.textContent = `${W.token} ${s + 1} · ` + (drawn
        ? (step.tok === "<|END|>" ? W.done : `${quote(step.tok)} ${W.drawn}${step.j > 0 ? ` — ${W.notTop}` : ""}`)
        : W.dist);
    }
    const st = stepper(fig, 2 * path.length, render, i => (i % 2 ? 1300 : 1000));
    temp.addEventListener("input", () => {
      tOut.textContent = (+temp.value).toFixed(1);
      path = walk();
      st.setCount(2 * path.length);
    });
    if (!reduce) whenSeen(fig, st.start);
  }

  // ---------------- gm: grammar masking ----------------
  function grammar(fig) {
    const data = JSON.parse(fig.dataset.json), W = data.words, steps = data.steps;
    const code = fig.querySelector(".gm-code code"), cur = fig.querySelector(".gm-code .nt-cur");
    const ol = fig.querySelector(".gm-cands ol"), phase = fig.querySelector(".gm-phase"), where = fig.querySelector(".where");
    const allowed = fig.querySelector(".gm-allowed"), stack = fig.querySelector(".gm-stack");
    const states = [...fig.querySelectorAll(".gm-s")], trans = [...fig.querySelectorAll(".gm-e")];
    const N = steps.length, count = 3 * N;           // per token: propose, filter, choose
    // pretty-print the tokens written so far as a CD4A model
    const format = toks => {
      let s = "", ind = 0, bol = true;
      for (const t of toks) {
        if (t === "<|END|>") continue;
        if (t === "}") { ind--; if (!bol) s += "\n"; s += "  ".repeat(ind) + "}\n"; bol = true; continue; }
        if (bol) s += "  ".repeat(ind); else if (t !== ";") s += " ";
        s += t; bol = false;
        if (t === "{") { s += "\n"; ind++; bol = true; } else if (t === ";") { s += "\n"; bol = true; }
      }
      return s;
    };
    function render(i) {
      const s = Math.floor(i / 3), ph = i % 3, step = steps[s];
      const done = steps.slice(0, s + (ph === 2 ? 1 : 0)).map(t => t.pick);
      code.innerHTML = esc(format(done));
      if (ph === 2) {     // the newest token stands out
        const last = esc(step.pick === "<|END|>" ? "" : step.pick);
        const at = code.innerHTML.lastIndexOf(last);
        if (last && at >= 0) code.innerHTML = code.innerHTML.slice(0, at) + `<span class="new">${last}</span>` + code.innerHTML.slice(at + last.length);
      }
      cur.hidden = ph === 2 && s === N - 1;
      // the candidates stay in the LLM's order: 1 its shares · 2 the grammar strikes some, the rest is
      // rescaled (the old share stays as a ghost) · 3 the most likely remaining one is chosen
      const okSum = step.cands.reduce((a, c) => a + (c[2] ? c[1] : 0), 0);
      const top = step.cands[0];
      ol.classList.toggle("filtered", ph > 0);
      barRows(ol, step.cands.map(([tok, p, ok]) => {
        if (ph === 0) return { tok, p, cls: "raw" };
        if (!ok) return { tok, p: 0, ghost: p, cls: "masked", label: "✗", tag: W.masked };
        const chosen = ph === 2 && tok === step.pick;
        return { tok, p: p / okSum, ghost: p, cls: chosen ? "pick" : "ok", tag: chosen ? W.chosen : "" };
      }));
      let msg = W["p" + ph];
      if (ph === 2) msg += " " + (top[2] ? W.agree : `${W.would} ${quote(top[0])}.`);
      phase.textContent = msg;
      phase.classList.toggle("hit", ph > 0 && !top[2]);
      // the automaton: current state, the transition just taken
      const at = ph === 2 ? step.to : step.from;
      states.forEach(g => g.classList.toggle("on", +g.dataset.s === at));
      trans.forEach(g => g.classList.toggle("on", ph === 2 && g.dataset.e === `${step.from}-${step.to}`));
      const depth = done.filter(t => t === "{").length - done.filter(t => t === "}").length;
      allowed.textContent = `${W.allowed}: ${data.allowed[at]}`;
      stack.textContent = `${W.stack}: ${depth ? "{ ".repeat(depth).trim() : W.none}`;
      where.textContent = `${W.step} ${s + 1} ${W.of} ${N}`;
    }
    const st = stepper(fig, count, render, i => (i % 3 === 2 ? 1300 : 1100));
    if (!reduce) whenSeen(fig, st.start);
  }

  const kinds = { nn: neural, nt: nextToken, gm: grammar };
  document.querySelectorAll("figure.demo[data-demo]").forEach(fig => {
    try { kinds[fig.dataset.demo]?.(fig); } catch (e) { console.error(e); }
  });
})();
