// Interactive figures of the Evolutionary Algorithms article (research-ea.html, built by _build/ea.py + ea_figs.py).
// Data come from seeded runs in _build/ea_sim.py and are shipped as data-json; this script swaps states and draws.
// Only a few things are computed live, because they are illustrations of chance or a fixed formula: the draws of the
// selection demo (ea7), the mutants of ea9 and the wakes of a dragged turbine (ea6).
// Steppers, height locks and the autoplay rule come from assets/demo-common.js (window.SiteDemo).
//   ea2  — learning vs search; the LLM as the variation step (toggle)
//   ea3  — one generation on the two hills (stepper: ring, ranked population, map)
//   ea7  — selection: wheel, tournament, temperature; six pointers (SUS)
//   ea8  — crossover: ordered strips; order crossover on a tour (stepper)
//   ea9  — mutation: a σ circle and twenty mutants on the landscape
//   ea10 — convergence on two hills (presets × generations)
//   ea6  — case wind farm: wakes, drag a turbine
//   ea4  — case wind farm: genotype → phenotype at three resolutions (presets)
//   ea13 — case wind farm: One-Step crossover (stepper)
//   ea12 — case hybrid car: receding horizon and fitness weights
(() => {
  const SD = window.SiteDemo;
  const NS = "http://www.w3.org/2000/svg";
  const reduce = SD.reduce;
  const json = fig => JSON.parse(fig.dataset.json);
  const press = SD.press;
  const de = document.documentElement.lang === "de";
  const fmt = (v, d = 3) => v.toFixed(d).replace(".", de ? "," : ".");
  const pct = v => `${fmt(100 * v, 1)} %`;
  const SITE = 1000;
  const el = (tag, attrs, text) => {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    if (text != null) e.textContent = text;
    return e;
  };

  // the toy site: metres → pixels of a square at (x0, y0) with side `size`, north up
  const px = (x, y, x0, y0, size) => [x0 + x / SITE * size, y0 + (SITE - y) / SITE * size];
  const scoreNE = (x, y) => (x + y) / (2 * SITE);

  // ranked rows: bars on a labelled fitness axis lo … hi
  const barW = (v, lo, hi) => Math.max(1, Math.min(100, 100 * (v - lo) / (hi - lo)));
  const axisRow = (lo, hi, label) => `<div class="rw ax" role="presentation"><span class="rn"></span><span class="axl"><i>${fmt(lo, 1)}</i><i>${label}</i><i>${fmt(hi, 1)}</i></span><span></span><span></span></div>`;

  // one roving tab stop in a list of rows: arrows move between them
  const roving = (list, onFocus) => {
    list.addEventListener("keydown", e => {
      const rows = [...list.querySelectorAll(".rw[data-id]")], i = rows.indexOf(e.target.closest(".rw"));
      if (i < 0) return;
      const j = { ArrowDown: i + 1, ArrowUp: i - 1, Home: 0, End: rows.length - 1 }[e.key];
      if (j == null || j < 0 || j >= rows.length) return;
      e.preventDefault();
      rows.forEach(r => r.tabIndex = -1); rows[j].tabIndex = 0; rows[j].focus(); onFocus?.(rows[j]);
    });
  };

  // ---------------- ea2: learning vs search ----------------
  function pipes(fig) {
    const buttons = [...fig.querySelectorAll(".d1-presets button")];
    buttons.forEach(b => b.addEventListener("click", () => { press(buttons, b); fig.classList.toggle("llm", b.dataset.v === "1"); }));
  }

  // ---------------- ea3: the loop on the two hills ----------------
  function loop(fig) {
    const { states, f, pos, parents, before, lo, hi, words } = json(fig);
    const rank = fig.querySelector(".rank"), say = fig.querySelector(".lp3-say");
    const nodes = [...fig.querySelectorAll(".nd")], cnt = fig.querySelector(".cnt"), cnt2 = fig.querySelector(".cnt2");
    const dots = fig.querySelector(".lp-dots"), guides = fig.querySelector(".lp-guides");
    const S = 192, P = p => [p[0] * S, (1 - p[1]) * S];
    let cur = 0, focus = null;
    const drawMap = () => {
      const rows = states[cur].rows.filter(r => r[1] !== "div");
      const order = [...rows].sort((a, b) => (a[0] === focus) - (b[0] === focus));
      dots.innerHTML = order.map(([id, cls]) => {
        const [x, y] = P(pos[id]);
        const c = ["lpd", cls.includes("struck") && "struck", (cls.includes("child") || cls.includes("pending")) && "kid",
                   cls.includes("pending") && "pend", cls.includes("fresh") && "fresh", cls.includes("elite") && "elite", cls.includes("sel") && "sel",
                   id === focus && "on"].filter(Boolean).join(" ");
        return `<circle class="${c}" data-id="${id}" cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${id === focus ? 5.5 : 4}"/>`;
      }).join("");
      let g = "";
      if (focus && parents[focus] && rows.some(r => r[0] === focus)) {
        const [a, b] = parents[focus].map(i => P(pos[i]));
        const x = Math.min(a[0], b[0]), y = Math.min(a[1], b[1]);
        g += `<rect class="lp-rect" x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${Math.abs(a[0] - b[0]).toFixed(1)}" height="${Math.abs(a[1] - b[1]).toFixed(1)}"/>`;
        g += [a, b].map(([u, v]) => `<circle class="lp-par" cx="${u.toFixed(1)}" cy="${v.toFixed(1)}" r="7"/>`).join("");
        if (before[focus]) {
          const [x0, y0] = P(before[focus]), [x1, y1] = P(pos[focus]);
          g += `<circle class="lp-was" cx="${x0.toFixed(1)}" cy="${y0.toFixed(1)}" r="3"/><path class="lp-mut" d="M${x0.toFixed(1)} ${y0.toFixed(1)}L${x1.toFixed(1)} ${y1.toFixed(1)}"/>`;
        }
      }
      guides.innerHTML = g;
      rank.querySelectorAll(".rw[data-id]").forEach(r => r.classList.toggle("shown", r.dataset.id === focus));
    };
    const render = i => {
      cur = i;
      const s = states[i];
      nodes.forEach(n => n.classList.toggle("on", s.node === n.dataset.n));
      cnt.textContent = s.cnt; cnt2.textContent = s.cnt2; say.textContent = s.say;
      let n = 0, after = false, first = true;
      rank.innerHTML = axisRow(lo, hi, words.fit) + s.rows.map(([id, cls, note]) => {
        if (cls === "div") { after = true; return '<div class="rw-div" role="presentation"></div>'; }
        n += 1;
        const pend = cls.includes("pending"), v = f[id], tab = first ? 0 : -1; first = false;
        return `<div class="rw ${cls}" data-id="${id}" role="listitem" tabindex="${tab}"><span class="rn">${after ? "+" : n}</span>` +
               `<span class="bar"><i style="width:${pend ? 0 : barW(v, lo, hi)}%"></i></span>` +
               `<span class="fv">${pend ? "?" : fmt(v, 2)}</span><span class="nt">${note}</span></div>`;
      }).join("");
      if (focus && !s.rows.some(r => r[0] === focus)) focus = null;
      drawMap();
    };
    const pick = id => { focus = id; drawMap(); };
    rank.addEventListener("pointerover", e => { const r = e.target.closest(".rw[data-id]"); if (r) pick(r.dataset.id); });
    rank.addEventListener("click", e => { const r = e.target.closest(".rw[data-id]"); if (r) pick(r.dataset.id); });
    rank.addEventListener("focusin", e => { const r = e.target.closest(".rw[data-id]"); if (r) pick(r.dataset.id); });
    dots.addEventListener("pointerover", e => { const c = e.target.closest("[data-id]"); if (c) pick(c.dataset.id); });
    dots.addEventListener("click", e => { const c = e.target.closest("[data-id]"); if (c) pick(c.dataset.id); });
    roving(rank);
    SD.stepper(fig, states.length, render, { delay: 3600, lock: [rank, say] });
  }

  // ---------------- ea7: selection ----------------
  function selection(fig) {
    const { f, lo, hi, words } = json(fig);
    const n = f.length, modes = [...fig.querySelectorAll("[data-m]")];
    const kIn = fig.querySelector(".sl-k input"), kOut = fig.querySelector(".sl-k output");
    const tIn = fig.querySelector(".sl-t input"), tOut = fig.querySelector(".sl-t output");
    const off = fig.querySelector(".sl-off input"), wheel = fig.querySelector("svg.wheel"), rank = fig.querySelector(".sel-rank");
    const say = fig.querySelector(".sel-say"), tourOut = fig.querySelector(".sel-tour"), drawBtn = fig.querySelector(".draw");
    const C = 120, R = 100;
    let mode = "wheel", drawn = new Array(n).fill(0), hov = -1, ptr = null, rot = 0, busy = false;
    const temp = () => .004 * Math.pow(10, +tIn.value / 20);           // 0.004 … 0.4
    const probs = () => {
      const g = f.map(v => v + (off.checked ? 1000 : 0));
      if (mode === "wheel") { const s = g.reduce((a, b) => a + b, 0); return g.map(v => v / s); }
      if (mode === "tour") { const k = +kIn.value; return g.map((_, i) => ((n - i) / n) ** k - ((n - i - 1) / n) ** k); }   // f is sorted, best first
      const T = temp(), m = Math.max(...g), e = g.map(v => Math.exp((v - m) / T)), s = e.reduce((a, b) => a + b, 0);
      return e.map(v => v / s);
    };
    const xy = (a, r) => [C + r * Math.sin(a), C - r * Math.cos(a)];          // angle from the top, clockwise
    const render = () => {
      const p = probs();
      fig.querySelector(".sl-k").hidden = mode !== "tour"; fig.querySelector(".sl-t").hidden = mode !== "temp";
      kOut.textContent = kIn.value; tOut.textContent = fmt(temp(), 3);
      let a = 0, out = "";
      p.forEach((v, i) => {
        const b = a + v * 2 * Math.PI, large = b - a > Math.PI ? 1 : 0;
        const [x1, y1] = xy(a, R), [x2, y2] = xy(b, R);
        const cls = `sl${i === 0 ? " best" : ""}${drawn[i] ? " drawn" : ""}${i === hov ? " hov" : ""}`;
        out += v > .9999 ? `<circle class="${cls}" data-i="${i}" cx="${C}" cy="${C}" r="${R}"/>` :
          `<path class="${cls}" data-i="${i}" d="M${C} ${C}L${x1.toFixed(2)} ${y1.toFixed(2)}A${R} ${R} 0 ${large} 1 ${x2.toFixed(2)} ${y2.toFixed(2)}Z"/>`;
        a = b;
      });
      if (ptr) out += `<g class="ptrs" transform="rotate(${rot.toFixed(1)} ${C} ${C})">` + ptr.map(t => {
        const [x, y] = xy(t, R + 4), [x1, y1] = xy(t - .06, R + 13), [x2, y2] = xy(t + .06, R + 13);
        return `<path class="ptr" d="M${x.toFixed(1)} ${y.toFixed(1)}L${x1.toFixed(1)} ${y1.toFixed(1)}L${x2.toFixed(1)} ${y2.toFixed(1)}Z"/>`;
      }).join("") + "</g>";
      wheel.innerHTML = out + `<circle class="hub" cx="${C}" cy="${C}" r="3"/>`;
      rank.innerHTML = axisRow(lo, hi, words.fit) + f.map((v, i) => `<div class="rw${i === 0 ? " elite" : ""}${drawn[i] ? " sel" : ""}${i === hov ? " shown" : ""}" data-i="${i}" role="listitem"><span class="rn">${i + 1}</span>` +
        `<span class="bar"><i style="width:${barW(v, lo, hi)}%"></i></span><span class="fv">${fmt(v, 2)}</span>` +
        `<span class="nt">${pct(p[i])}${drawn[i] ? ` <b>×${drawn[i]}</b>` : ""}</span></div>`).join("");
      const r = p[0] * n, verdict = r > 3 ? words.strong : r < 1.2 ? words.none : words.some;
      say.textContent = `${words.chance}: ${words.best} ${pct(p[0])} · ${words.worst} ${pct(p[n - 1])} — ${verdict}`;
    };
    const reset = () => { drawn.fill(0); ptr = null; tourOut.textContent = ""; };
    modes.forEach(b => b.addEventListener("click", () => { mode = b.dataset.m; press(modes, b); reset(); render(); }));
    // the knob row holds one slider or none: keep its height so the wheel below never moves (phones wrap it)
    SD.lock(fig.querySelector(".sel-knobs"), ["wheel", "tour", "temp"], m => {
      fig.querySelector(".sl-k").hidden = m !== "tour"; fig.querySelector(".sl-t").hidden = m !== "temp";
    }, () => mode);
    [kIn, tIn, off].forEach(x => x.addEventListener("input", () => { reset(); render(); }));
    const hover = e => { const t = e.target.closest("[data-i]"); const i = t ? +t.dataset.i : -1; if (i !== hov) { hov = i; render(); } };
    wheel.addEventListener("pointermove", hover); rank.addEventListener("pointermove", hover);
    wheel.addEventListener("pointerleave", () => { hov = -1; render(); }); rank.addEventListener("pointerleave", () => { hov = -1; render(); });
    drawBtn.addEventListener("click", () => {
      if (busy) return;
      const p = probs(); reset();
      if (mode === "tour") {                                         // six tournaments: k random candidates, the best wins
        const k = +kIn.value, lines = [];
        for (let t = 0; t < 6; t++) {
          const pick = Array.from({ length: k }, () => Math.floor(Math.random() * n)), w = Math.min(...pick);
          drawn[w]++; lines.push(`${words.tour} ${t + 1}: ${pick.map(i => "#" + (i + 1)).join(" · ")} → #${w + 1}`);
        }
        tourOut.textContent = lines.join("\n"); render(); return;
      }
      // stochastic universal sampling: six pointers 60° apart, one spin
      const u = Math.random() / 6, base = [0, 1, 2, 3, 4, 5].map(j => j / 6 * 2 * Math.PI);
      const hit = () => { const cum = []; p.reduce((a, v, i) => (cum[i] = a + v), 0);
        [0, 1, 2, 3, 4, 5].forEach(j => { const t = u + j / 6; let i = cum.findIndex(c => t < c); if (i < 0) i = n - 1; drawn[i]++; }); };
      ptr = base;
      const end = u * 360 + 360, t0 = performance.now(), dur = reduce ? 0 : 600;
      busy = true;
      const frame = () => {                                          // timer ticks, not rAF: the spin must finish even in a background tab
        const q = dur ? Math.min(1, (performance.now() - t0) / dur) : 1;
        rot = end * (1 - (1 - q) ** 3);
        if (q < 1) { render(); setTimeout(frame, 16); } else { rot = end; hit(); busy = false; render(); }
      };
      frame();
    });
    render();
  }

  // ---------------- ea8: crossover ----------------
  function crossover(fig) {
    const d = json(fig), ops = [...fig.querySelectorAll("[data-o]")], strip = fig.querySelector("svg.xo-strip");
    let op = "one", cuts = [3], mask = [0, 1, 1, 0, 1, 0, 0];
    const toss = () => {
      const r = () => 1 + Math.floor(Math.random() * 6);
      if (op === "one") cuts = [r()];
      if (op === "two") { let a = r(), b = r(); while (b === a) b = r(); cuts = [Math.min(a, b), Math.max(a, b)]; }
      if (op === "uni") mask = d.a.map(() => (Math.random() < .5 ? 0 : 1));
    };
    const from = i => (op === "uni" ? mask[i] : cuts.filter(c => c <= i).length % 2);     // 0 = from A, 1 = from B (for child 1)
    const draw = () => {
      const cw = 40, x0 = 92, rows = [["A", d.a, () => 0], ["B", d.b, () => 1], ["1", null, i => from(i)], ["2", null, i => 1 - from(i)]];
      let out = "";
      rows.forEach(([lab, vals, src], r) => {
        const y = 6 + r * 34 + (r >= 2 ? 10 : 0);
        out += `<text class="s" x="0" y="${y + 17}">${lab === "A" || lab === "B" ? d.words.parent : d.words.child} ${lab}</text>`;
        d.a.forEach((_, i) => {
          const s = src(i), v = vals ? vals[i] : (s ? d.b[i] : d.a[i]);
          out += `<rect class="cell ${s ? "fb" : "fa"}" x="${x0 + i * cw}" y="${y}" width="${cw - 5}" height="26" rx="1"/>` +
                 `<rect class="lvl ${s ? "fb" : "fa"}" x="${x0 + i * cw}" y="${(y + 26 - 26 * v).toFixed(1)}" width="${cw - 5}" height="${(26 * v).toFixed(1)}"/>`;
        });
      });
      if (op !== "uni") cuts.forEach(c => { const x = x0 + c * cw - 2.5; out += `<path class="cut" d="M${x} 1V152"/>`; });
      strip.innerHTML = out;
    };
    ops.forEach(b => b.addEventListener("click", () => { op = b.dataset.o; press(ops, b); toss(); draw(); }));
    fig.querySelector(".retoss").addEventListener("click", () => { toss(); draw(); });
    draw();
    const g = fig.querySelector(".ox-g"), say = fig.querySelector(".ox-say");
    SD.stepper(fig, d.states.length, i => { g.innerHTML = d.states[i].svg; say.innerHTML = d.states[i].say; }, { delay: 3800, lock: [say] });
  }

  // ---------------- ea9: mutation on the landscape ----------------
  function mutation(fig) {
    const d = json(fig), S = d.S, g = fig.querySelector(".mu-g"), svg = fig.querySelector("svg.mu-svg");
    const chips = [...fig.querySelectorAll("[data-s]")];
    const sIn = fig.querySelector(".kn-s input"), iIn = fig.querySelector(".kn-i input"), pIn = fig.querySelector(".kn-p input");
    const count = fig.querySelector(".mu-count"), sayEl = fig.querySelector(".mu-say");
    const hill = (x, y) => Math.max(.6 * Math.exp(-((x - d.low[0]) ** 2 + (y - d.low[1]) ** 2) / .08), Math.exp(-((x - d.high[0]) ** 2 + (y - d.high[1]) ** 2) / .006));
    const gauss = () => Math.sqrt(-2 * Math.log(Math.max(Math.random(), 1e-12))) * Math.cos(2 * Math.PI * Math.random());
    const clamp = v => Math.min(1, Math.max(0, v));
    let child = d.spots.slope.slice(), spot = "slope", draws = [];
    const resample = () => { draws = Array.from({ length: d.n }, () => ({ m: Math.random(), i1: Math.random(), i2: Math.random(), z1: gauss(), z2: gauss() })); };
    const P = (x, y) => [x * S, (1 - y) * S];
    const draw = () => {
      const s = +sIn.value, ip = +iIn.value, mp = +pIn.value, h0 = hill(...child);
      sIn.nextElementSibling.textContent = fmt(s, 2); iIn.nextElementSibling.textContent = fmt(ip, 1); pIn.nextElementSibling.textContent = fmt(mp, 1);
      let changed = 0, up = 0, down = 0, out = "";
      const [cx, cy] = P(...child);
      const marks = [];
      draws.forEach(r => {
        if (r.m >= mp) return;
        const dx = r.i1 < ip ? r.z1 * s : 0, dy = r.i2 < ip ? r.z2 * s : 0;
        if (!dx && !dy) return;
        const m = [clamp(child[0] + dx), clamp(child[1] + dy)], h = hill(...m), better = h > h0;
        changed++; better ? up++ : down++;
        const [x, y] = P(...m);
        out += `<path class="mu-ln" d="M${cx.toFixed(1)} ${cy.toFixed(1)}L${x.toFixed(1)} ${y.toFixed(1)}"/>`;
        marks.push(`<circle class="mu-m${better ? " up" : ""}" cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3.2"/>`);
      });
      const same = d.n - changed;
      out += `<circle class="mu-sig" cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="${(s * S).toFixed(1)}"/>` + marks.join("") +
             `<circle class="mu-c" cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="5"/>` +
             (same ? `<text class="s halo" x="${(cx + (cx > S - 60 ? -9 : 9)).toFixed(1)}" y="${(cy + (cy < 20 ? 16 : -8)).toFixed(1)}" text-anchor="${cx > S - 60 ? "end" : "start"}">${d.words.child} ×${same}</text>` : "");
      g.innerHTML = out;
      count.innerHTML = `${d.words.changed} <b>${changed}</b> ${d.words.of} ${d.n} · ${d.words.better} <b class="a">${up}</b> · ${d.words.worse} <b>${down}</b> · ${d.words.same} ${same}`;
      sayEl.textContent = d.words.say[spot];
    };
    chips.forEach(b => b.addEventListener("click", () => { spot = b.dataset.s; child = d.spots[spot].slice(); press(chips, b); draw(); }));
    [sIn, iIn, pIn].forEach(x => x.addEventListener("input", draw));
    fig.querySelector(".mutate").addEventListener("click", () => { resample(); draw(); });
    svg.addEventListener("click", e => {
      const p = svg.createSVGPoint(); p.x = e.clientX; p.y = e.clientY;
      const q = p.matrixTransform(svg.getScreenCTM().inverse());
      child = [clamp((q.x - 4) / S), clamp(1 - (q.y - 4) / S)]; spot = "free"; press(chips, null); draw();
    });
    resample(); draw();
    SD.lock(sayEl, Object.keys(d.words.say), k => { sayEl.textContent = d.words.say[k]; }, () => spot);
  }

  // ---------------- ea10: convergence ----------------
  function converge(fig) {
    const { presets, words, S, W, H1, H2 } = json(fig);
    const buttons = [...fig.querySelectorAll("[data-p]")], seeds = fig.querySelector(".cv-seeds input");
    const dots = fig.querySelector(".dots"), ch1 = fig.querySelector(".ch1"), ch2 = fig.querySelector(".ch2");
    const say = fig.querySelector(".cv-say"), count = fig.querySelector(".cv-count"), where = fig.querySelector(".where");
    let name = "balanced", p = presets[name];
    const G = p.best.length - 1, X = g => g / G * W;
    const line = (vals, h, lo, hi) => "M" + vals.map((v, g) => `${X(g).toFixed(1)} ${(h - (v - lo) / (hi - lo) * h).toFixed(1)}`).join("L");
    const frame = gen => {
      const pts = p.pts[gen];
      let out = "";
      for (let i = pts.length - 2; i >= 0; i -= 2) {
        const x = pts[i] / 999 * S, y = (1 - pts[i + 1] / 999) * S;
        out += `<circle class="${i === 0 ? "pd best" : "pd"}" cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${i === 0 ? 5 : 3.8}"/>`;
      }
      dots.innerHTML = out;
      const mk = h => `<path class="now" d="M${X(gen).toFixed(1)} 0V${h}"/>`;
      ch1.querySelector(".now")?.remove(); ch2.querySelector(".now")?.remove();
      ch1.insertAdjacentHTML("beforeend", mk(H1)); ch2.insertAdjacentHTML("beforeend", mk(H2));
      where.textContent = `${words.gen} ${gen} ${words.of} ${G} · ${20 + gen * (20 - p.cfg.elite)} ${words.evals}`;
    };
    const charts = () => {
      const band = "M" + p.best.map((v, g) => `${X(g).toFixed(1)} ${(H1 - v * H1).toFixed(1)}`).join("L") +
                   "L" + p.worst.map((v, g) => `${X(g).toFixed(1)} ${(H1 - v * H1).toFixed(1)}`).reverse().join("L") + "Z";
      const ax = (h, top, bottom) => `<path class="ln" d="M0 0V${h}H${W}"/><path class="ln" d="M-3 0H0"/><text class="s" x="-6" y="4" text-anchor="end">${top}</text><text class="s" x="-6" y="${h + 3}" text-anchor="end">${bottom}</text>`;
      const yb = H1 - p.best[G] * H1, yw = H1 - p.worst[G] * H1;
      ch1.innerHTML = ax(H1, fmt(1, 1), "0") + `<path class="gap" d="${band}"/>` +
        (seeds.checked ? p.seeds.map(s => `<path class="seed" d="${line(s, H1, 0, 1)}"/>`).join("") : "") +
        `<path class="worst" d="${line(p.worst, H1, 0, 1)}"/><path class="mean" d="${line(p.mean, H1, 0, 1)}"/><path class="bestl" d="${line(p.best, H1, 0, 1)}"/>` +
        `<text class="s a halo on-tile" x="${W - 2}" y="${(yb - 5).toFixed(1)}" text-anchor="end">${words.best}</text>` +
        (yw - yb > 24 ? `<text class="s halo on-tile" x="${W - 2}" y="${(yw - 5).toFixed(1)}" text-anchor="end">${words.worst}</text>` : "") +
        (p.best[30] - p.worst[30] > .25 ? `<text class="s halo on-tile" x="${X(30)}" y="${(H1 - (p.best[30] + p.worst[30]) / 2 * H1 + 3).toFixed(1)}" text-anchor="middle">${words.gap}</text>` : "");
      const dmax = .45;
      ch2.innerHTML = ax(H2, fmt(dmax, 2), "0") + `<path class="divl" d="${line(p.div.map(v => Math.min(v, dmax)), H2, 0, dmax)}"/>` +
        `<text class="s" x="${W - 2}" y="-5" text-anchor="end">${words.div}</text>` +
        `<text class="s" x="${W}" y="${H2 + 15}" text-anchor="end">${words.gen} ${G}</text><text class="s" x="0" y="${H2 + 15}">0</text>`;
      say.textContent = p.say; count.textContent = p.count;
    };
    SD.lock(say, Object.keys(presets), k => { say.textContent = presets[k].say; }, () => name);
    charts();
    const st = SD.stepper(fig, G + 1, frame, { delay: 140, label: false });
    if (reduce) st.show(G);
    const set = b => { name = b.dataset.p; p = presets[name]; press(buttons, b); charts(); st.stop(); if (reduce) st.show(G); else { st.show(0); st.start(); } };
    buttons.forEach(b => b.addEventListener("click", () => set(b)));
    seeds.addEventListener("change", () => { charts(); frame(st.k); });
  }

  // ---------------- ea6: wakes (case wind farm) ----------------
  function wake(fig) {
    const d = json(fig), start = d.pts.map(p => p.slice());
    let pts = start.map(p => p.slice()), sel = -1, drag = -1, focusI = -1;
    let down = null, moved = false, from = null, before = null;
    const svg = fig.querySelector("svg.wake"), cones = fig.querySelector(".cones"), tbs = fig.querySelector(".tbs");
    const total = fig.querySelector(".wk-total"), nowake = fig.querySelector(".wk-nowake");
    const hint = fig.querySelector(".wk-hint"), hint0 = hint.textContent;
    hint.setAttribute("aria-live", "polite");
    const S = 260, X0 = 20, Y0 = 20, R_ZONE = d.dmin / SITE * S, N = Math.round(SITE / d.cell);
    const base = d.uniform ? () => 1 : scoreNE;               // uniform field: labels show pure wake loss
    const zones = el("g", { class: "zones" }); cones.before(zones);
    const say = t => { hint.textContent = t || hint0; };
    const tooClose = () => say(`${d.words.too} (${d.dmin} m)`);
    const P = p => p.map(v => v.toFixed(1)).join(" ");
    const deficit = dx => (1 - Math.sqrt(1 - d.ct)) / (1 + d.k * dx / d.R) ** 2;
    const scores = () => pts.map(([x, y], i) => {
      let d2 = 0;
      pts.forEach(([u, v], j) => { const dx = x - u; if (j !== i && dx > 0 && Math.abs(y - v) < d.R + d.k * dx) d2 += deficit(dx) ** 2; });
      return base(x, y) * (1 - Math.sqrt(d2)) ** 3;
    });
    const ok = (i, m) => pts.every((p, j) => j === i || Math.hypot(p[0] - m[0], p[1] - m[1]) >= d.dmin - 1e-6);
    const clamp = v => Math.min(SITE - d.cell / 2, Math.max(d.cell / 2, v));
    const snap = v => clamp(Math.floor(v / d.cell) * d.cell + d.cell / 2);
    const nearestValid = (i, m) => {                           // nearest legal cell centre, at most dmin away
      let best = null, bd = Infinity;
      for (let a = 0; a < N; a++) for (let b = 0; b < N; b++) {
        const c = [(a + .5) * d.cell, (b + .5) * d.cell], dd = Math.hypot(c[0] - m[0], c[1] - m[1]);
        if (dd < bd && ok(i, c)) { bd = dd; best = c; }
      }
      return bd <= d.dmin ? best : null;
    };
    const settle = (i, m) => { const s = [snap(m[0]), snap(m[1])]; return ok(i, s) ? s : nearestValid(i, m); };

    const draw = () => {
      const sc = scores(), act = drag >= 0 ? drag : sel;
      zones.innerHTML = act < 0 ? "" : pts.map(([x, y], j) => j === act ? "" :
        `<circle class="zone" cx="${px(x, y, 0, 0, S)[0].toFixed(1)}" cy="${px(x, y, 0, 0, S)[1].toFixed(1)}" r="${R_ZONE.toFixed(1)}"/>`).join("");
      cones.innerHTML = pts.map(([x, y]) => {                 // to the site edge, like scores(); clipped + faded
        const w1 = d.R + d.k * (SITE - x);
        return `<path class="cone" d="M${P(px(x, y + d.R, 0, 0, S))}L${P(px(SITE, y + w1, 0, 0, S))}L${P(px(SITE, y - w1, 0, 0, S))}L${P(px(x, y - d.R, 0, 0, S))}Z"/>`;
      }).join("");
      tbs.innerHTML = pts.map(([x, y], i) => {
        const [cx, cy] = px(x, y, 0, 0, S), keep = sc[i] / Math.max(1e-9, base(x, y));
        const dl = before ? sc[i] - before[i] : 0, changed = Math.abs(dl) > .005 && i !== act;
        const lab = changed ? (dl > 0 ? "+" : "−") + (d.uniform ? `${Math.round(Math.abs(dl) * 100)} %` : fmt(Math.abs(dl), 2)) : d.uniform ? `${Math.round(keep * 100)} %` : fmt(sc[i], 2);
        const right = cx > S - 36, top = cy < 14;
        const cls = ["tw", i === act && "sel", keep < .98 && "hit", i === drag && !ok(i, pts[i]) && "bad", changed && "changed"].filter(Boolean).join(" ");
        return `<g class="${cls}" data-i="${i}" tabindex="0" role="button" aria-label="${d.words.turbine} ${i + 1}: ${lab}" transform="translate(${cx.toFixed(1)} ${cy.toFixed(1)})">` +
               `<circle class="hit-area" r="16"/><path class="rot" d="M0 -6V6"/><path class="nac" d="M0 0H5"/>` +
               `<text class="s" x="${right ? -8 : 8}" y="${top ? 13 : -6}" text-anchor="${right ? "end" : "start"}">${lab}</text></g>`;
      }).join("");
      if (focusI >= 0) tbs.querySelector(`[data-i="${focusI}"]`)?.focus({ preventScroll: true });
      const mean = sc.reduce((a, b) => a + b, 0) / sc.length, b0 = pts.reduce((a, p) => a + base(...p), 0) / pts.length;
      total.innerHTML = d.uniform ? `${d.words.total} <b>${Math.round(mean * 100)} %</b>` : `${d.words.total} <b>${fmt(mean)}</b>`;
      nowake.textContent = d.uniform ? `${d.words.nowake}: ${Math.round(b0 * 100)} %` : `${d.words.nowake}: ${fmt(b0)}`;
    };
    const toM = e => {                                          // raw position, no snapping while dragging
      const p = svg.createSVGPoint(); p.x = e.clientX; p.y = e.clientY;
      const q = p.matrixTransform(svg.getScreenCTM().inverse());
      return [clamp((q.x - X0) / S * SITE), clamp(SITE - (q.y - Y0) / S * SITE)];
    };

    svg.addEventListener("pointerdown", e => {
      const g = e.target.closest(".tw");
      if (g) {
        drag = +g.dataset.i; from = pts[drag].slice(); down = [e.clientX, e.clientY]; moved = false; before = scores();
        svg.setPointerCapture(e.pointerId); e.preventDefault(); draw(); return;
      }
      if (sel < 0) return;                                      // empty field, nothing armed: do nothing
      before = scores();
      const m = settle(sel, toM(e));
      if (m) { pts[sel] = m; say(); } else tooClose();
      sel = -1; draw();
    });
    svg.addEventListener("pointermove", e => {
      if (drag < 0) return;
      if (!moved && Math.hypot(e.clientX - down[0], e.clientY - down[1]) < 4) return;   // a tap, not a drag
      moved = true; pts[drag] = toM(e);                         // always follows the pointer
      if (ok(drag, pts[drag])) say(); else tooClose();
      draw();
    });
    svg.addEventListener("pointerup", () => {
      if (drag < 0) return;
      if (moved) {                                              // a drag never leaves a turbine armed
        const m = settle(drag, pts[drag]);
        pts[drag] = m || from; if (m) say(); else tooClose();
        sel = -1;
      } else {                                                  // a tap arms / disarms tap-to-move
        sel = sel === drag ? -1 : drag;
        say(sel >= 0 ? d.words.now : "");
      }
      drag = -1; draw();
    });
    svg.addEventListener("pointercancel", () => { if (drag >= 0) { pts[drag] = from; drag = -1; sel = -1; say(); draw(); } });
    document.addEventListener("pointerdown", e => { if (sel >= 0 && !svg.contains(e.target)) { sel = -1; say(); draw(); } });

    // keyboard (WCAG 2.5.7): Tab to a turbine, arrows move it to the next legal cell, Esc cancels
    document.addEventListener("focusin", e => { const g = tbs.contains(e.target) && e.target.closest(".tw"); focusI = g ? +g.dataset.i : -1; });
    tbs.addEventListener("keydown", e => {
      const g = e.target.closest(".tw"); if (!g) return;
      if (e.key === "Escape") { sel = -1; say(); draw(); return; }
      const dir = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, 1], ArrowDown: [0, -1] }[e.key];
      if (!dir) return;
      e.preventDefault();
      const i = +g.dataset.i; before = scores();
      for (let s = 1; s <= N; s++) {
        const m = [pts[i][0] + dir[0] * d.cell * s, pts[i][1] + dir[1] * d.cell * s];
        if (m[0] < 0 || m[0] > SITE || m[1] < 0 || m[1] > SITE) break;
        if (ok(i, m)) { pts[i] = m; say(); break; }
      }
      draw();
    });
    fig.querySelector(".wk-reset").addEventListener("click", () => { pts = start.map(p => p.slice()); sel = -1; before = null; say(); draw(); });
    draw();
  }

  // ---------------- ea4: encoding at three resolutions (case wind farm) ----------------
  function encoding(fig) {
    const { presets } = json(fig);
    const buttons = [...fig.querySelectorAll(".d1-presets button")];
    const gen = fig.querySelector(".enc-gen"), svg = fig.querySelector(".enc-site"), read = fig.querySelector(".enc-read"), note = fig.querySelector(".enc-note");
    let active = buttons.findIndex(b => b.getAttribute("aria-pressed") === "true");
    const set = i => {
      const p = presets[i];
      gen.textContent = p.gen.join("\n");
      svg.innerHTML = p.svg;
      read.innerHTML = p.read.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("");
      note.innerHTML = p.note;
    };
    buttons.forEach((b, i) => b.addEventListener("click", () => { active = i; press(buttons, b); set(i); }));
    SD.lock(note, presets.length, set, () => active);
    set(active);
  }

  // ---------------- ea13: One-Step crossover (case wind farm) ----------------
  function onestep(fig) {
    const d = json(fig), g = fig.querySelector(".os-g"), say = fig.querySelector(".os-say");
    SD.stepper(fig, d.states.length, i => { g.innerHTML = d.states[i].svg; say.textContent = d.states[i].say; }, { delay: 3800, lock: [say] });
  }

  // ---------------- ea12: the hybrid car ----------------
  function phev(fig) {
    const d = json(fig), g = fig.querySelector(".ph-g"), say = fig.querySelector(".ph-say");
    SD.stepper(fig, d.steps.length, i => { g.innerHTML = d.steps[i].svg; say.textContent = d.steps[i].say; }, { delay: 4200, lock: [say] });
    const buttons = [...fig.querySelectorAll(".ph-b button")], wsay = fig.querySelector(".ph-wsay");
    let active = 0;
    const set = i => {
      const w = d.w[i];
      fig.querySelector(".ph-w").innerHTML = w.wv.map((v, k) => `<div class="wrow${v ? " on" : ""}"><span>${d.wnames[k]}</span><span class="wb"><i style="width:${v * 100}%"></i></span><span>${fmt(v, 1)}</span></div>`).join("");
      fig.querySelector(".ph-fuel").textContent = w.fuel; fig.querySelector(".ph-soc").textContent = w.soc;
      wsay.textContent = w.say;
    };
    buttons.forEach((b, i) => b.addEventListener("click", () => { active = i; press(buttons, b); set(i); }));
    SD.lock(wsay, d.w.length, set, () => active);
    set(0);
  }

  const kinds = { ea2: pipes, ea3: loop, ea4: encoding, ea6: wake, ea7: selection, ea8: crossover, ea9: mutation, ea10: converge, ea12: phev, ea13: onestep };
  document.querySelectorAll("figure.demo[data-demo]").forEach(fig => {
    try { kinds[fig.dataset.demo]?.(fig); } catch (e) { console.error(e); }
  });
})();
