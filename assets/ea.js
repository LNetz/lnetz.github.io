// Interactive figures of the Evolutionary Algorithms article (research-ea.html, built by _build/ea.py + ea_figs.py).
// Data come from seeded runs in _build/ea_sim.py and are shipped as data-json; this script swaps states and draws.
// Only three things are computed live, because they are illustrations of chance: the draws of the selection demo
// (ea7), the mutations of ea9 and the wakes of a dragged turbine (ea6, a fixed formula).
//   ea2  — learning vs search; the LLM as the variation step (toggle)
//   ea3  — one generation of the toy run (stepper, ring + ranked population)
//   ea4  — genotype → phenotype at different resolutions (presets)
//   ea6  — wakes: drag a turbine
//   ea7  — selection: wheel, tournament, temperature
//   ea8  — crossover: ordered strips and One-Step on layouts
//   ea9  — mutation: three knobs
//   ea10 — convergence on two hills (presets × generations)
//   ea12 — the hybrid car: receding horizon and fitness weights
(() => {
  const NS = "http://www.w3.org/2000/svg";
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const json = fig => JSON.parse(fig.dataset.json);
  const press = (buttons, on) => buttons.forEach(b => b.setAttribute("aria-pressed", String(b === on)));
  const fmt = (v, d = 3) => v.toFixed(d).replace(".", document.documentElement.lang === "de" ? "," : ".");
  const SITE = 1000;

  // ---------------- a stepper (as in dt.js) ----------------
  function stepper(fig, count, render, delay, words) {
    const play = fig.querySelector(".play"), range = fig.querySelector("input.step");
    let k = 0, timer = null;
    range.max = count - 1;
    const show = i => { k = i; range.value = i; render(i); };
    const stop = () => { clearTimeout(timer); timer = null; play.textContent = k >= count - 1 ? "↺" : "▶"; play.setAttribute("aria-label", words.play); };
    const tick = () => { if (k >= count - 1) return stop(); show(k + 1); timer = setTimeout(tick, delay); };
    const start = () => { if (k >= count - 1) show(0); play.textContent = "❚❚"; play.setAttribute("aria-label", words.pause); timer = setTimeout(tick, delay); };
    play.addEventListener("click", () => (timer ? stop() : start()));
    range.addEventListener("input", () => { stop(); show(+range.value); stop(); });
    show(0); stop();
    return { show, start, stop, get k() { return k; }, render: () => render(k) };
  }

  // the toy site: metres → pixels of a square at (x0, y0) with side `size`, north up
  const px = (x, y, x0, y0, size) => [x0 + x / SITE * size, y0 + (SITE - y) / SITE * size];
  const cellXY = (c, rho) => [(c[0] + .5) * SITE / rho, (c[1] + .5) * SITE / rho];
  const scoreNE = (x, y) => (x + y) / (2 * SITE);
  const el = (tag, attrs, text) => {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    if (text != null) e.textContent = text;
    return e;
  };
  const isoLines = (x0, y0, size) => [.2, .4, .6, .8].map(c => {
    const t = 2 * SITE * c, a = [Math.max(0, t - SITE), Math.min(SITE, t)], b = [Math.min(SITE, t), Math.max(0, t - SITE)];
    const [ax, ay] = px(...a, x0, y0, size), [bx, by] = px(...b, x0, y0, size);
    return `<path class="iso" d="M${ax.toFixed(1)} ${ay.toFixed(1)}L${bx.toFixed(1)} ${by.toFixed(1)}"/>`;
  }).join("");

  // ranked rows: bars on a labelled fitness axis lo … hi (the differences within a population are small)
  const barW = (v, lo, hi) => Math.max(1, Math.min(100, 100 * (v - lo) / (hi - lo)));
  const axisRow = (lo, hi) => `<div class="rw ax" role="presentation"><span class="rn"></span><span class="axl"><i>${fmt(lo, 2)}</i><i>fitness</i><i>${fmt(hi, 2)}</i></span><span></span><span></span></div>`;

  // ---------------- ea2: learning vs search ----------------
  function pipes(fig) {
    const buttons = [...fig.querySelectorAll(".d1-presets button")];
    buttons.forEach(b => b.addEventListener("click", () => { press(buttons, b); fig.classList.toggle("llm", b.dataset.v === "1"); }));
  }

  // ---------------- ea3: the loop ----------------
  function loop(fig) {
    const { states, f, lay, rho, lo, hi, words } = json(fig);
    const rank = fig.querySelector(".rank"), say = fig.querySelector(".lp3-say"), where = fig.querySelector(".where");
    const nodes = [...fig.querySelectorAll(".nd")], cnt = fig.querySelector(".cnt"), cnt2 = fig.querySelector(".cnt2");
    const mini = fig.querySelector(".mini-dots"), miniL = fig.querySelector(".mini-l");
    const showLayout = (id, label) => {
      mini.innerHTML = (lay[id] || []).map(c => { const [x, y] = px(...cellXY(c, rho), 6, 4, 120); return `<circle class="tb hl" cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="2.6"/>`; }).join("");
      miniL.textContent = label;
    };
    const render = i => {
      const s = states[i];
      nodes.forEach(n => n.classList.toggle("on", s.node.includes(n.dataset.n)));
      cnt.textContent = s.cnt; cnt2.textContent = s.cnt2; say.textContent = s.say;
      where.textContent = `${words.step} ${i + 1} ${words.of} ${states.length}`;
      let n = 0, after = false;
      rank.innerHTML = axisRow(lo, hi) + s.rows.map(([id, cls, note]) => {
        if (cls === "div") { after = true; return '<div class="rw-div" role="presentation"></div>'; }
        n += 1;
        const pend = cls.includes("pending"), v = f[id];
        const no = after ? "+" : String(n);
        return `<div class="rw ${cls}" data-id="${id}" role="listitem" tabindex="0"><span class="rn">${no}</span>` +
               `<span class="bar"><i style="width:${pend ? 62 : barW(v, lo, hi)}%"></i></span>` +
               `<span class="fv">${pend ? "?" : fmt(v)}</span><span class="nt">${note}</span></div>`;
      }).join("");
      const first = s.rows.find(r => r[1] !== "div");
      showLayout(first[0], `#1 · ${fmt(f[first[0]])}`);
    };
    const pick = e => {
      const row = e.target.closest(".rw");
      if (!row) return;
      const idx = [...rank.querySelectorAll(".rw")].indexOf(row);
      rank.querySelectorAll(".rw").forEach(r => r.classList.toggle("shown", r === row));
      showLayout(row.dataset.id, `${row.querySelector(".rn").textContent} · ${row.querySelector(".fv").textContent}`);
      return idx;
    };
    rank.addEventListener("pointerover", pick);
    rank.addEventListener("click", pick);
    rank.addEventListener("focusin", pick);
    stepper(fig, states.length, render, 3200, words);
  }

  // ---------------- ea4: encoding ----------------
  function encoding(fig) {
    const { presets } = json(fig);
    const buttons = [...fig.querySelectorAll(".d1-presets button")];
    const gen = fig.querySelector(".enc-gen"), svg = fig.querySelector(".enc-site"), read = fig.querySelector(".enc-read"), note = fig.querySelector(".enc-note");
    const set = i => {
      const p = presets[i];
      press(buttons, buttons[i]);
      gen.textContent = p.gen.join("\n");
      svg.innerHTML = p.svg;
      read.innerHTML = p.read.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("");
      note.innerHTML = p.note;
    };
    buttons.forEach((b, i) => b.addEventListener("click", () => set(i)));
    set(0);
  }

  // ---------------- ea6: wakes ----------------
  function wake(fig) {
    const d = json(fig), start = d.pts.map(p => p.slice());
    let pts = start.map(p => p.slice()), sel = -1, drag = -1;
    const svg = fig.querySelector("svg.wake"), cones = fig.querySelector(".cones"), tbs = fig.querySelector(".tbs");
    const total = fig.querySelector(".wk-total"), nowake = fig.querySelector(".wk-nowake");
    const S = 260, X0 = 20, Y0 = 20;
    const deficit = dx => (1 - Math.sqrt(1 - d.ct)) / (1 + d.k * dx / d.R) ** 2;
    const scores = () => pts.map(([x, y], i) => {
      let d2 = 0;
      pts.forEach(([u, v], j) => { const dx = x - u; if (j !== i && dx > 0 && Math.abs(y - v) < d.R + d.k * dx) d2 += deficit(dx) ** 2; });
      return scoreNE(x, y) * (1 - Math.sqrt(d2)) ** 3;
    });
    const draw = () => {
      const sc = scores();
      cones.innerHTML = pts.map(([x, y]) => {
        const len = Math.min(500, SITE - x), w0 = d.R, w1 = d.R + d.k * len;      // drawn for 500 m downstream
        const a = px(x, y + w0, 0, 0, S), b = px(x + len, y + w1, 0, 0, S), c = px(x + len, y - w1, 0, 0, S), e = px(x, y - w0, 0, 0, S);
        return `<path class="cone" d="M${a[0].toFixed(1)} ${a[1].toFixed(1)}L${b[0].toFixed(1)} ${Math.max(0, b[1]).toFixed(1)}L${c[0].toFixed(1)} ${Math.min(S, c[1]).toFixed(1)}L${e[0].toFixed(1)} ${e[1].toFixed(1)}Z"/>`;
      }).join("");
      tbs.innerHTML = pts.map(([x, y], i) => {
        const [cx, cy] = px(x, y, 0, 0, S), loss = 1 - sc[i] / Math.max(1e-9, scoreNE(x, y));
        return `<g class="tw${i === sel ? " sel" : ""}${loss > .02 ? " hit" : ""}" data-i="${i}"><path class="rot" d="M${cx.toFixed(1)} ${(cy - 6).toFixed(1)}V${(cy + 6).toFixed(1)}"/>` +
               `<circle class="hit-area" cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="9"/><text class="s" x="${(cx + 5).toFixed(1)}" y="${(cy - 5).toFixed(1)}">${fmt(sc[i], 2)}</text></g>`;
      }).join("");
      const mean = sc.reduce((a, b) => a + b, 0) / sc.length, base = pts.reduce((a, p) => a + scoreNE(...p), 0) / pts.length;
      total.innerHTML = `${d.words.total} <b>${fmt(mean)}</b>`;
      nowake.textContent = `${d.words.nowake}: ${fmt(base)}`;
    };
    const toM = e => {
      const p = svg.createSVGPoint(); p.x = e.clientX; p.y = e.clientY;
      const q = p.matrixTransform(svg.getScreenCTM().inverse());
      const snap = v => Math.min(SITE - d.cell / 2, Math.max(d.cell / 2, Math.floor(v / d.cell) * d.cell + d.cell / 2));
      return [snap((q.x - X0) / S * SITE), snap(SITE - (q.y - Y0) / S * SITE)];
    };
    const ok = (i, m) => pts.every((p, j) => j === i || Math.hypot(p[0] - m[0], p[1] - m[1]) >= d.dmin - 1e-6);
    svg.addEventListener("pointerdown", e => {
      const g = e.target.closest(".tw");
      if (g) { drag = +g.dataset.i; sel = drag; svg.setPointerCapture(e.pointerId); draw(); e.preventDefault(); return; }
      if (sel >= 0) { const m = toM(e); if (ok(sel, m)) { pts[sel] = m; } sel = -1; draw(); }
    });
    svg.addEventListener("pointermove", e => { if (drag < 0) return; const m = toM(e); if (ok(drag, m)) { pts[drag] = m; draw(); } });
    const end = () => { if (drag >= 0) { drag = -1; } };
    svg.addEventListener("pointerup", end); svg.addEventListener("pointercancel", end);
    fig.querySelector(".wk-reset").addEventListener("click", () => { pts = start.map(p => p.slice()); sel = -1; draw(); });
    draw();
  }

  // ---------------- ea7: selection ----------------
  function selection(fig) {
    const { f, lo, hi, words } = json(fig);
    const n = f.length, modes = [...fig.querySelectorAll("[data-m]")];
    const kIn = fig.querySelector(".sl-k input"), kOut = fig.querySelector(".sl-k output");
    const tIn = fig.querySelector(".sl-t input"), tOut = fig.querySelector(".sl-t output");
    const off = fig.querySelector(".sl-off input"), wheel = fig.querySelector("svg.wheel"), rank = fig.querySelector(".sel-rank");
    const expect = fig.querySelector(".expect");
    let mode = "wheel", drawn = new Array(n).fill(0);
    const temp = () => .004 * Math.pow(10, +tIn.value / 20);           // 0.004 … 0.4
    const probs = () => {
      const g = f.map(v => v + (off.checked ? 1000 : 0));
      if (mode === "wheel") { const s = g.reduce((a, b) => a + b, 0); return g.map(v => v / s); }
      if (mode === "tour") { const k = +kIn.value; return g.map((_, i) => ((n - i) / n) ** k - ((n - i - 1) / n) ** k); }   // f is sorted, best first
      const T = temp(), m = Math.max(...g), e = g.map(v => Math.exp((v - m) / T)), s = e.reduce((a, b) => a + b, 0);
      return e.map(v => v / s);
    };
    const render = () => {
      const p = probs();
      fig.querySelector(".sl-k").hidden = mode !== "tour"; fig.querySelector(".sl-t").hidden = mode !== "temp";
      kOut.textContent = kIn.value; tOut.textContent = fmt(temp(), 3);
      let a = -Math.PI / 2, out = "";
      p.forEach((v, i) => {
        const b = a + v * 2 * Math.PI, large = b - a > Math.PI ? 1 : 0, R = 96, c = 110;
        const x1 = c + R * Math.cos(a), y1 = c + R * Math.sin(a), x2 = c + R * Math.cos(b), y2 = c + R * Math.sin(b);
        out += v > .9999 ? `<circle class="sl${i === 0 ? " best" : ""}" cx="${c}" cy="${c}" r="${R}"/>` :
          `<path class="sl${i === 0 ? " best" : ""}${drawn[i] ? " drawn" : ""}" d="M${c} ${c}L${x1.toFixed(2)} ${y1.toFixed(2)}A${R} ${R} 0 ${large} 1 ${x2.toFixed(2)} ${y2.toFixed(2)}Z"/>`;
        a = b;
      });
      wheel.innerHTML = out + `<circle class="hub" cx="110" cy="110" r="4"/>`;
      rank.innerHTML = axisRow(lo, hi) + f.map((v, i) => `<div class="rw${i === 0 ? " elite" : ""}${drawn[i] ? " sel" : ""}" role="listitem"><span class="rn">${i + 1}</span>` +
        `<span class="bar"><i style="width:${barW(v, lo, hi)}%"></i></span><span class="fv">${fmt(v)}</span>` +
        `<span class="nt">${fmt(100 * p[i], 1)} %${drawn[i] ? ` ×${drawn[i]}` : ""}</span></div>`).join("");
      expect.textContent = `${words.exp}: ${fmt(6 * p[0], 2)}`;
    };
    modes.forEach(b => b.addEventListener("click", () => { mode = b.dataset.m; press(modes, b); drawn.fill(0); render(); }));
    [kIn, tIn, off].forEach(x => x.addEventListener("input", () => { drawn.fill(0); render(); }));
    fig.querySelector(".draw").addEventListener("click", () => {
      const p = probs(); drawn.fill(0);
      for (let t = 0; t < 6; t++) { let r = Math.random(), i = 0; while (i < n - 1 && r >= p[i]) { r -= p[i]; i++; } drawn[i]++; }
      render();
    });
    render();
  }

  // ---------------- ea8: crossover ----------------
  function crossover(fig) {
    const d = json(fig), ops = [...fig.querySelectorAll("[data-o]")], strip = fig.querySelector("svg.xo-strip");
    let op = "one", cuts = [3, 5], mask = [0, 1, 1, 0, 1, 0, 0];
    const toss = () => {
      const r = () => 1 + Math.floor(Math.random() * 6);
      if (op === "one") cuts = [r()];
      if (op === "two") { let a = r(), b = r(); while (b === a) b = r(); cuts = [Math.min(a, b), Math.max(a, b)]; }
      if (op === "uni") mask = d.a.map(() => (Math.random() < .5 ? 0 : 1));
    };
    const from = i => (op === "uni" ? mask[i] : cuts.filter(c => c <= i).length % 2);     // 0 = from A, 1 = from B (for child 1)
    const draw = () => {
      const cw = 34, x0 = 74, rows = [["A", d.a, () => 0], ["B", d.b, () => 1], ["1", null, i => from(i)], ["2", null, i => 1 - from(i)]];
      let out = "";
      rows.forEach(([lab, vals, src], r) => {
        const y = 8 + r * 34 + (r >= 2 ? 10 : 0);
        out += `<text class="s" x="0" y="${y + 18}">${lab === "A" || lab === "B" ? (document.documentElement.lang === "de" ? "Elternteil " : "parent ") + lab : (document.documentElement.lang === "de" ? "Kind " : "child ") + lab}</text>`;
        d.a.forEach((_, i) => {
          const s = src(i), v = vals ? vals[i] : (s ? d.b[i] : d.a[i]);
          out += `<rect class="cell ${s ? "fb" : "fa"}" x="${x0 + i * cw}" y="${y}" width="${cw - 4}" height="26" rx="1"/>` +
                 `<rect class="lvl ${s ? "fb" : "fa"}" x="${x0 + i * cw}" y="${(y + 26 - 26 * v).toFixed(1)}" width="${cw - 4}" height="${(26 * v).toFixed(1)}"/>`;
        });
      });
      if (op !== "uni") cuts.forEach(c => { const x = x0 + c * cw - 2; out += `<path class="cut" d="M${x} 2V146"/>`; });
      strip.innerHTML = out;
    };
    ops.forEach(b => b.addEventListener("click", () => { op = b.dataset.o; press(ops, b); toss(); draw(); }));
    fig.querySelector(".retoss").addEventListener("click", () => { toss(); draw(); });
    draw();
    const g = fig.querySelector(".os-g"), say = fig.querySelector(".os-say"), where = fig.querySelector(".where");
    stepper(fig, d.states.length, i => { g.innerHTML = d.states[i].svg; say.textContent = d.states[i].say; where.textContent = `${d.words.step} ${i + 1} ${d.words.of} ${d.states.length}`; }, 3500, d.words);
  }

  // ---------------- ea9: mutation ----------------
  function mutation(fig) {
    const d = json(fig), svg = fig.querySelector("svg.mut");
    const P = fig.querySelector(".kn-p"), N = fig.querySelector(".kn-n"), Sx = fig.querySelector(".kn-s");
    const outs = [P, N, Sx].map(i => i.parentElement.querySelector("output"));
    const fit = l => l.reduce((a, c) => a + scoreNE(...cellXY(c, d.rho)), 0) / l.length;
    let result = null;
    const valid = (c, others) => others.every(o => { const a = cellXY(c, d.rho), b = cellXY(o, d.rho); return Math.hypot(a[0] - b[0], a[1] - b[1]) >= d.dmin - 1e-6; });
    const mutate = () => {
      const p = +P.value / 100, n = +N.value, s = +Sx.value / 100;
      result = d.kids.map(kid => {
        if (Math.random() >= p) return null;
        const order = kid.map((c, k) => k).sort((a, b) => scoreNE(...cellXY(kid[a], d.rho)) - scoreNE(...cellXY(kid[b], d.rho)));
        const picked = [];
        while (picked.length < Math.min(n, kid.length)) {
          const r = Math.random(), j = Math.min(kid.length - 1, Math.floor(kid.length * (r * r + r ** 4) / 2));
          if (!picked.includes(j)) picked.push(j);
        }
        const child = kid.map(c => c.slice()), moves = [];
        for (const j of picked) {
          const k = order[j], old = child[k];
          for (let t = 0; t < 20; t++) {
            const tx = Math.floor(Math.random() * d.rho), ty = Math.floor(Math.random() * d.rho);
            const c = [Math.round(old[0] * (1 - s) + tx * s), Math.round(old[1] * (1 - s) + ty * s)];
            if ((c[0] !== old[0] || c[1] !== old[1]) && valid(c, child.filter((_, q) => q !== k))) { child[k] = c; moves.push([old, c]); break; }
          }
        }
        return { child, moves };
      });
      draw();
    };
    const draw = () => {
      outs[0].textContent = `${P.value} %`; outs[1].textContent = N.value; outs[2].textContent = fmt(+Sx.value / 100, 2);
      let out = "";
      const cols = fig.clientWidth < 560 ? 3 : 6;                                  // 3 × 2 on phones
      svg.setAttribute("viewBox", `0 0 ${cols * 110} ${Math.ceil(d.kids.length / cols) * 128}`);
      d.kids.forEach((kid, i) => {
        const x0 = 4 + (i % cols) * 110, y0 = 4 + Math.floor(i / cols) * 128, S = 100, res = result && result[i];
        out += `<rect class="box" x="${x0}" y="${y0}" width="${S}" height="${S}"/>${isoLines(x0, y0, S)}`;
        const now = res ? res.child : kid;
        now.forEach(c => { const [x, y] = px(...cellXY(c, d.rho), x0, y0, S); out += `<circle class="tb" cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="2.4"/>`; });
        if (res) res.moves.forEach(([a, b]) => {
          const [x1, y1] = px(...cellXY(a, d.rho), x0, y0, S), [x2, y2] = px(...cellXY(b, d.rho), x0, y0, S);
          out += `<circle class="old" cx="${x1.toFixed(1)}" cy="${y1.toFixed(1)}" r="2.6"/><path class="ln hl" d="M${x1.toFixed(1)} ${y1.toFixed(1)}L${x2.toFixed(1)} ${y2.toFixed(1)}"/><circle class="tb hl" cx="${x2.toFixed(1)}" cy="${y2.toFixed(1)}" r="2.8"/>`;
        });
        const label = !result ? `${d.words.f} ${fmt(fit(kid))}` : res ? `${fmt(fit(kid))} → ${fmt(fit(res.child))}` : d.words.not;
        out += `<text class="s${res ? " a" : ""}" x="${x0 + S / 2}" y="${y0 + S + 16}" text-anchor="middle">${label}</text>`;
      });
      svg.innerHTML = out;
    };
    [P, N, Sx].forEach(x => x.addEventListener("input", () => { result = null; draw(); }));
    fig.querySelector(".mutate").addEventListener("click", mutate);
    let cols0 = fig.clientWidth < 560;
    addEventListener("resize", () => { if ((fig.clientWidth < 560) !== cols0) { cols0 = !cols0; draw(); } });
    draw();
  }

  // ---------------- ea10: convergence ----------------
  function converge(fig) {
    const { presets, words } = json(fig);
    const buttons = [...fig.querySelectorAll("[data-p]")], seeds = fig.querySelector(".cv-seeds input");
    const dots = fig.querySelector(".dots"), ch1 = fig.querySelector(".ch1"), ch2 = fig.querySelector(".ch2");
    const say = fig.querySelector(".cv-say"), count = fig.querySelector(".cv-count"), where = fig.querySelector(".where");
    let p = presets.balanced;
    const W = 280, H1 = 120, H2 = 54, G = 60;
    const X = g => g / G * W;
    const line = (vals, h, lo, hi) => "M" + vals.map((v, g) => `${X(g).toFixed(1)} ${(h - (v - lo) / (hi - lo) * h).toFixed(1)}`).join("L");
    const frame = gen => {
      const pts = p.pts[gen];
      let out = "";
      for (let i = 0; i < pts.length; i += 2) {
        const x = pts[i] / 999 * 260, y = (1 - pts[i + 1] / 999) * 260;
        out += `<circle class="${i === 0 ? "pd best" : "pd"}" cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${i === 0 ? 4 : 3}"/>`;
      }
      dots.innerHTML = out;
      const mk = (h) => `<path class="now" d="M${X(gen).toFixed(1)} 0V${h}"/>`;
      ch1.querySelector(".now")?.remove(); ch2.querySelector(".now")?.remove();
      ch1.insertAdjacentHTML("beforeend", mk(H1)); ch2.insertAdjacentHTML("beforeend", mk(H2));
      where.textContent = `${words.gen} ${gen} ${words.of} ${G} · ${20 + gen * (20 - p.cfg.elite)} ${words.evals}`;
    };
    const charts = () => {
      const band = "M" + p.best.map((v, g) => `${X(g).toFixed(1)} ${(H1 - v * H1).toFixed(1)}`).join("L") +
                   "L" + p.worst.map((v, g) => `${X(g).toFixed(1)} ${(H1 - v * H1).toFixed(1)}`).reverse().join("L") + "Z";
      const ax = (h, top, bottom) => `<path class="ln" d="M0 0V${h}H${W}"/><text class="s" x="-4" y="4" text-anchor="end">${top}</text><text class="s" x="-4" y="${h}" text-anchor="end">${bottom}</text>`;
      ch1.innerHTML = ax(H1, "1", "0") + `<path class="gap" d="${band}"/>` +
        (seeds.checked ? p.seeds.map(s => `<path class="seed" d="${line(s, H1, 0, 1)}"/>`).join("") : "") +
        `<path class="worst" d="${line(p.worst, H1, 0, 1)}"/><path class="mean" d="${line(p.mean, H1, 0, 1)}"/><path class="bestl" d="${line(p.best, H1, 0, 1)}"/>` +
        `<text class="s a" x="${W - 2}" y="${(H1 - p.best[G] * H1 - 4).toFixed(1)}" text-anchor="end">${words.best}</text>` +
        (p.best[30] - p.worst[30] > .25 ? `<text class="s" x="${X(30)}" y="${(H1 - (p.best[30] + p.worst[30]) / 2 * H1 + 3).toFixed(1)}" text-anchor="middle">${words.gap}</text>` : "");
      const dmax = .45;
      ch2.innerHTML = ax(H2, fmt(dmax, 2), "0") + `<path class="divl" d="${line(p.div.map(v => Math.min(v, dmax)), H2, 0, dmax)}"/>` +
        `<text class="s" x="${W - 2}" y="${-3}" text-anchor="end">${words.div}</text>` +
        `<text class="s" x="${W}" y="${H2 + 13}" text-anchor="end">${words.gen} 60</text><text class="s" x="0" y="${H2 + 13}">0</text>`;
      say.textContent = p.say; count.textContent = p.count;
    };
    const st = stepper(fig, G + 1, frame, 160, words);
    const set = b => { p = presets[b.dataset.p]; press(buttons, b); charts(); st.show(G); st.stop(); };
    buttons.forEach(b => b.addEventListener("click", () => { set(b); }));
    seeds.addEventListener("change", () => { charts(); frame(st.k); });
    charts(); st.show(G); st.stop();
  }

  // ---------------- ea12: the hybrid car ----------------
  function phev(fig) {
    const d = json(fig), g = fig.querySelector(".ph-g"), say = fig.querySelector(".ph-say"), where = fig.querySelector(".ph-a .where");
    stepper(fig, d.steps.length, i => { g.innerHTML = d.steps[i].svg; say.textContent = d.steps[i].say; where.textContent = `${d.words.step} ${i + 1} ${d.words.of} ${d.steps.length}`; }, 4000, d.words);
    const buttons = [...fig.querySelectorAll(".ph-b button")];
    const set = i => {
      const w = d.w[i]; press(buttons, buttons[i]);
      fig.querySelector(".ph-w").textContent = `(${w.wv.map(v => fmt(v, 1)).join(", ")})`;
      fig.querySelector(".ph-fuel").textContent = w.fuel; fig.querySelector(".ph-soc").textContent = w.soc;
      fig.querySelector(".ph-wsay").textContent = w.say;
    };
    buttons.forEach((b, i) => b.addEventListener("click", () => set(i)));
    set(0);
  }

  const kinds = { ea2: pipes, ea3: loop, ea4: encoding, ea6: wake, ea7: selection, ea8: crossover, ea9: mutation, ea10: converge, ea12: phev };
  document.querySelectorAll("figure.demo[data-demo]").forEach(fig => {
    try { kinds[fig.dataset.demo]?.(fig); } catch (e) { console.error(e); }
  });
})();
