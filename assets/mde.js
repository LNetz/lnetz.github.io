// Interactive figures of the MDE article (research-mde.html, built by _build/mde.py + mde_figs.py).
// All states are precomputed at build time and shipped as data-json; this script only swaps and highlights.
// Shared helpers (stepper, height lock, autoplay rule, chips) come from assets/demo-common.js (window.SiteDemo).
//   d0 — the generator at several levels of detail (morph; three instances: intro, inside, —)
//   f2 — reading a class diagram: point at a part, the strip reads it out
//   map — one city, three maps: one crosshair through all four
//   d1 — one model, three views (text · tree · diagram), three gates (presets; linked highlighting)
//   mm — mail merge: one template, three models
//   d3 — one line in the model, six files change (+ attribute, file chips, code | template)
//   d2 — edit the generated file, or extend it (TOP mechanism; stepper, plays once when seen)
//   d4 — CD2GUI: pages nobody drew (class picker, dashboard / overview / details, hand-written delta)
(() => {
  const D = window.SiteDemo;
  const reduce = D.reduce, press = D.press;
  const json = fig => JSON.parse(fig.dataset.json);

  // ---------------- f2: a class diagram that reads itself out ----------------
  function readAloud(fig) {
    const { read, prompt } = JSON.parse(fig.dataset.read);
    const strip = fig.querySelector(".f2-read"), parts = [...fig.querySelectorAll("g.k[data-k]")];
    const light = k => {
      parts.forEach(g => g.classList.toggle("on", g.dataset.k === k));
      strip.innerHTML = k ? read[k] : prompt;
      strip.classList.toggle("on", !!k);
    };
    // the innermost part under the pointer wins (the attributes sit inside the Book class)
    fig.addEventListener("pointerover", e => { const g = e.target.closest("g.k[data-k]"); if (g) light(g.dataset.k); });
    fig.addEventListener("pointerleave", e => { if (e.pointerType === "mouse") light(null); });
    parts.forEach(g => {
      g.addEventListener("focus", e => { e.stopPropagation(); light(g.dataset.k); });
      g.addEventListener("blur", () => light(null));
    });
    D.lock(strip, [null, ...Object.keys(read)], k => { strip.innerHTML = k ? read[k] : prompt; }, () => null);
  }

  // ---------------- d1: text, tree, diagram — and the three gates ----------------
  function syntax(fig) {
    const { variants, none } = json(fig);
    const code = fig.querySelector(".d1-code"), msg = fig.querySelector(".d1-msg"), treeBox = fig.querySelector(".d1-treebox");
    const gates = [...fig.querySelectorAll(".gate")], umls = [...fig.querySelectorAll(".d1-uml")];
    const buttons = [...fig.querySelectorAll(".d1-presets button")];
    let cur = 0;
    const render = i => {
      const v = variants[i];
      code.innerHTML = v.code;
      gates.forEach((g, k) => { g.className = "gate " + (v.gates[k] === 1 ? "ok" : v.gates[k] === 0 ? "fail" : "skip"); });
      umls.forEach(u => { u.hidden = u.dataset.uml !== v.uml; });
      treeBox.innerHTML = v.tree || `<p class="d1-notree mono">${none}</p>`;
      treeBox.classList.toggle("none", !v.tree);
      msg.textContent = v.msg;
    };
    const set = i => { cur = i; press(buttons, buttons[i]); render(i); };
    buttons.forEach((b, i) => b.addEventListener("click", () => set(i)));
    // pointing at a line, a tree node or a part of the diagram lights up the same element in the other two
    const light = k => {
      fig.querySelectorAll(".d1-code .l, .d1-tree li, .d1-uml [data-k]").forEach(el => el.classList.toggle("hi", !!k && el.dataset.k === k));
    };
    const over = e => { const el = e.target.closest("[data-k]"); light(el && el.dataset.k); };
    for (const el of [code, treeBox, ...umls]) {
      el.addEventListener("pointerover", over);
      el.addEventListener("pointerleave", () => light(null));
    }
    D.lock(msg, variants.length, render, () => cur);
    D.lock(fig.querySelector(".d1-right"), variants.length, render, () => cur);
  }

  // ---------------- mm: mail merge ----------------
  function mailmerge(fig) {
    const { out, model } = json(fig);
    const o = fig.querySelector(".mm-out"), m = fig.querySelector(".mm-model"), chips = [...fig.querySelectorAll(".mm-chips button")];
    let cur = "Book";
    const render = c => {
      o.innerHTML = out[c]; m.innerHTML = model[c];
      if (!reduce) for (const el of [o, m]) { el.classList.remove("flash"); void el.offsetWidth; el.classList.add("flash"); }
    };
    chips.forEach(b => b.addEventListener("click", () => { cur = b.dataset.c; press(chips, b); b.classList.remove("first"); render(cur); }));
    const keys = Object.keys(out);
    D.lock(o, keys, c => { o.innerHTML = out[c]; }, () => cur);
    D.lock(m, keys, c => { m.innerHTML = model[c]; }, () => cur);
  }

  // ---------------- d2: the TOP mechanism ----------------
  function top(fig) {
    const { steps } = json(fig);
    const lanes = { a: fig.querySelector('[data-lane="a"]'), b: fig.querySelector('[data-lane="b"]') };
    const where = fig.querySelector(".where"), W = D.words;
    const render = i => {
      const s = steps[i];
      for (const l of ["a", "b"]) {
        lanes[l].querySelector(".d2-files").innerHTML = s[l];
        const note = lanes[l].querySelector(".d2-note");
        note.textContent = s[l + "n"];
        note.className = "d2-note mono " + (s[l + "c"] || "");
      }
      where.textContent = `${W.step} ${i + 1} ${W.of} ${steps.length} · ${s.title}`;
    };
    D.stepper(fig, steps.length, render, { delay: 2600, narrated: true, lock: [lanes.a, lanes.b], label: false });
  }

  // ---------------- d3: one line, six files ----------------
  function files(fig) {
    const { states, templates, words } = json(fig);
    const model = fig.querySelector(".d3-model pre"), count = fig.querySelector(".d3-count");
    const out = fig.querySelector(".d3-code"), form = fig.querySelector(".d3-form-wrap"), note = fig.querySelector(".d3-tplnote");
    const chips = [...fig.querySelectorAll(".d3-chip")], views = [...fig.querySelectorAll(".d3-view button")];
    const add = fig.querySelector(".d3-add");
    let k = 0, file = "data", view = "code";
    const panel = ([kk, f, v]) => {                 // the variable part: the code, the form, the template note
      const s = states[kk], tpl = v === "template";
      out.innerHTML = tpl ? templates[f] : s.files[f];
      out.classList.toggle("tpl", tpl);
      form.hidden = tpl || f !== "form";
      if (!form.hidden) form.innerHTML = s.form;
      note.hidden = !tpl;
      note.textContent = words.tpl;
    };
    const render = flash => {
      const s = states[k];
      model.innerHTML = s.model;
      chips.forEach(c => {
        const n = k ? s.changed[c.dataset.f] : 0;
        c.querySelector(".d3-badge").textContent = n ? `+${n}` : "";
        c.querySelector(".d3-new").textContent = n ? s.first[c.dataset.f] : "";
        c.classList.toggle("touched", n > 0);
        if (flash && n && !reduce) { c.classList.remove("flash"); void c.offsetWidth; c.classList.add("flash"); }
      });
      press(chips, chips.find(c => c.dataset.f === file));
      press(views, views.find(v => v.dataset.view === view));
      panel([k, file, view]);
      count.textContent = k ? words.count.replace("{n}", s.n).replace("{m}", s.m) + (k === states.length - 1 ? ` · ${words.full}` : "") : words.start;
      add.disabled = k >= states.length - 1;
      add.classList.toggle("hint", k === 0);
    };
    add.addEventListener("click", () => { if (k < states.length - 1) { k++; render(true); } });
    fig.querySelector(".d3-reset").addEventListener("click", () => { k = 0; render(); });
    chips.forEach(c => c.addEventListener("click", () => { file = c.dataset.f; render(); }));
    views.forEach(v => v.addEventListener("click", () => { view = v.dataset.view; render(); }));
    render();
    // the panel never changes height: lock it over every state, file and view
    const all = [];
    states.forEach((_, kk) => chips.forEach(c => ["code", "template"].forEach(v => all.push([kk, c.dataset.f, v]))));
    D.lock(fig.querySelector(".d3-panel"), all, panel, () => [k, file, view]);
    // and the chips keep their height when their new line appears
    D.lock(fig.querySelector(".d3-tiers"), states.map((_, kk) => kk), kk => {
      chips.forEach(c => { const n = kk ? states[kk].changed[c.dataset.f] : 0; c.querySelector(".d3-new").textContent = n ? states[kk].first[c.dataset.f] : ""; });
    }, () => k);
  }

  // ---------------- d4: CD2GUI ----------------
  function cd2gui(fig) {
    const { pages, start } = json(fig);
    const url = fig.querySelector(".d4-url"), page = fig.querySelector(".d4-page"), tree = fig.querySelector(".d4-tree-wrap");
    const tabs = [...fig.querySelectorAll(".d4-tabs button")], classes = [...fig.querySelectorAll(".d4-cls")];
    const delta = fig.querySelector(".d4-delta input"), deltaCode = fig.querySelector(".d4-deltacode");
    let cls = start, tab = "dashboard";
    const key = (c, t, dl) => (t === "dashboard" ? "dashboard" : `${c}/${t}${dl ? "+delta" : ""}`);
    const render = () => {
      const canDelta = cls === "Member" && tab === "details";
      delta.disabled = !canDelta;
      if (!canDelta) delta.checked = false;
      deltaCode.classList.toggle("on", delta.checked);
      const p = pages[key(cls, tab, delta.checked)];
      url.textContent = p.url;
      page.innerHTML = p.html;
      tree.innerHTML = p.tree;
      press(tabs, tabs.find(t => t.dataset.t === tab));
      press(classes, classes.find(g => g.dataset.c === cls));
    };
    classes.forEach(g => g.addEventListener("click", () => { cls = g.dataset.c; if (tab === "dashboard") tab = "details"; render(); }));
    tabs.forEach(t => t.addEventListener("click", () => { tab = t.dataset.t; t.classList.remove("first"); render(); }));
    delta.addEventListener("change", render);
    render();
    const all = Object.keys(pages);
    D.lock(page, all, k => { page.innerHTML = pages[k].html; }, () => key(cls, tab, delta.checked));
    D.lock(tree, all, k => { tree.innerHTML = pages[k].tree; }, () => key(cls, tab, delta.checked));   // stacked on phones
  }

  // ---------------- the city map: one crosshair marks the same place in every map ----------------
  // Original, road map and hiking map share the city's geography; the metro map does not — pointing at it can
  // only pick the nearest station, and the other maps then ring that station's true position.
  function citymap(box) {
    const d = JSON.parse(box.dataset.map), w = d.words;
    const svgs = [...box.querySelectorAll("svg.cm")].map(s => ({ k: +s.dataset.k, s, g: s.querySelector(".xh") }));
    const read = box.closest("figure").querySelector(".cm-read");
    const heightAt = (x, y) => {                       // bilinear on the precomputed grid
      const i = Math.min(Math.max(x, 0) / d.step, d.heights[0].length - 1.001), j = Math.min(Math.max(y, 0) / d.step, d.heights.length - 1.001);
      const i0 = Math.floor(i), j0 = Math.floor(j), fi = i - i0, fj = j - j0, h = d.heights;
      return (h[j0][i0] * (1 - fi) + h[j0][i0 + 1] * fi) * (1 - fj) + (h[j0 + 1][i0] * (1 - fi) + h[j0 + 1][i0 + 1] * fi) * fj;
    };
    const riverAt = x => { const i = Math.min(Math.max(x / 4, 0), d.river.length - 1.001), i0 = Math.floor(i); return d.river[i0] + (d.river[i0 + 1] - d.river[i0]) * (i - i0); };
    const nearest = (pts, x, y) => Object.keys(pts).reduce((a, k) => (Math.hypot(pts[k][0] - x, pts[k][1] - y) < Math.hypot(pts[a][0] - x, pts[a][1] - y) ? k : a));
    // the road map's roads, sampled once (city coordinates)
    const roadSvg = svgs.find(p => p.k === 2).s, roads = [];
    roadSvg.querySelectorAll("path[data-road]").forEach(p => {
      const n = p.getTotalLength(), pts = [];
      for (let t = 0; t <= n; t += 3) { const q = p.getPointAtLength(t); pts.push([q.x, q.y]); }
      roads.push({ name: p.dataset.road || w.road, pts });
    });
    const roadAt = (x, y) => {
      let best = null, dist = 9;
      for (const r of roads) for (const [px, py] of r.pts) { const dd = Math.hypot(px - x, py - y); if (dd < dist) { dist = dd; best = r.name; } }
      return best;
    };
    const oldTown = (x, y) => x > 78 && x < 204 && y > 56 && y < 118;
    const place = (x, y, h) => {
      if (Math.abs(y - riverAt(x)) < 5) return w.river;
      if (oldTown(x, y)) return w.oldtown;
      if (x > 42 && x < 80 && y > 98 && y < 120) return w.park;
      if (x > 172 && x < 276 && y > 146) return w.south;
      return h > 95 ? w.hills : w.edge;
    };
    const put = (p, x, y, label, ring) => {
      const [v, hl, c, t] = p.g.children;
      v.setAttribute("x1", x); v.setAttribute("x2", x);
      hl.setAttribute("y1", y); hl.setAttribute("y2", y);
      c.setAttribute("cx", x); c.setAttribute("cy", y);
      c.setAttribute("r", ring ? 7 : 3.2);
      c.classList.toggle("ring", !!ring);
      const right = x > d.w - 90, below = y < 24;
      t.setAttribute("x", right ? x - 7 : x + 7); t.setAttribute("y", below ? y + 15 : y - 7);
      t.setAttribute("text-anchor", right ? "end" : "start");
      t.textContent = label;
    };
    let pos = null, snapped = null;
    const show = (x, y, station) => {
      pos = [x, y];
      const h = Math.round(heightAt(x, y)), st = station || nearest(d.geo, x, y);
      const where = station ? d.names[station] : place(x, y, h);
      const road = oldTown(x, y) && !station ? w.oldtown : (roadAt(x, y) || w.noroad);
      for (const p of svgs) {
        if (p.k === 1) { const [mx, my] = d.metro[st]; put(p, mx, my, ""); }
        else put(p, x, y, p.k === 0 ? `${where} · ${h} m` : p.k === 2 ? road : `≈ ${h} m`, station && p.k !== 3);
      }
      svgs[1].s.querySelectorAll("[data-st]").forEach(el => el.classList.toggle("pulse", el.dataset.st === st));
      snapped = st;
      read.textContent = `${w.orig}: ${where} · ${h} m — ${w.roads}: ${road} — ${w.hike}: ≈ ${h} m — ${w.metro}: ${station ? d.names[st] : `${w.nearest} ${d.names[st]}`}`;
      box.classList.add("live");
    };
    const hide = () => { box.classList.remove("live"); svgs[1].s.querySelectorAll(".pulse").forEach(el => el.classList.remove("pulse")); };
    const at = (p, e) => {
      const pt = p.s.createSVGPoint();
      pt.x = e.clientX; pt.y = e.clientY;
      return pt.matrixTransform(p.s.getScreenCTM().inverse());
    };
    for (const p of svgs) {
      const move = e => {
        if (e.pointerType !== "mouse" && e.type === "pointermove" && !e.buttons) return;
        const q = at(p, e);
        if (q.x < 0 || q.y < 0 || q.x > d.w || q.y > d.h) return;
        if (p.k === 1) { const st = nearest(d.metro, q.x, q.y); show(d.geo[st][0], d.geo[st][1], st); }    // the metro map has no geography
        else show(q.x, q.y, null);
      };
      p.s.addEventListener("pointermove", move);
      p.s.addEventListener("pointerdown", move);
      p.s.addEventListener("pointerleave", e => { if (e.pointerType === "mouse") hide(); });   // a tap keeps its crosshair
    }
    box.addEventListener("keydown", e => {
      const step = { ArrowLeft: [-10, 0], ArrowRight: [10, 0], ArrowUp: [0, -10], ArrowDown: [0, 10] }[e.key];
      if (!step) return;
      e.preventDefault();
      const [x, y] = pos || [d.w / 2, d.h / 2];
      show(Math.min(d.w - 2, Math.max(2, x + step[0])), Math.min(d.h - 2, Math.max(2, y + step[1])), null);
    });
    box.addEventListener("blur", hide);
  }
  document.querySelectorAll(".citymap[data-map]").forEach(box => { try { citymap(box); } catch (e) { console.error(e); } });

  // ---------------- d0: the generator at several levels of detail (_build/mde_levels.py) ----------------
  // Boxes move and grow between levels, what is new fades in after the move has begun, what goes fades out first.
  // Geometry rules as in the Python. One instance per figure; each knows only its own levels.
  function levels(fig) {
    const d = json(fig), svg = fig.querySelector("svg"), L = d.levels;
    if (d.tall && matchMedia("(max-width: 600px)").matches) {        // phones: the stacked layout of levels 1–2
      d.frames = d.tall.frames;
      d.els.forEach(e => { e.g = d.tall.geo[e.id] || {}; });
      d.eds.forEach((ed, i) => { const r = d.tall.routes[i]; if (r) ed.r = r; else ed.lv = []; });
    }
    const els = d.els.map(e => ({ ...e, node: svg.querySelector(`[data-id="${e.id}"]`) }));
    const byId = Object.fromEntries(els.map(e => [e.id, e]));
    const paths = [...svg.querySelectorAll(".lv-edges path")];
    const geo = (e, l) => e.g[l] ? [...e.g[l].slice(0, 4), e.g[l][4] ?? 1] : null;
    const lerp = (a, b, k) => a + (b - a) * k;
    const shape = (k, w, h) => k === "doc" ? `M0 0H${w - 10}L${w} 10V${h}H0Z M${w - 10} 0V10H${w}`
      : k === "cyl" ? `M0 8V${h - 8}A${w / 2} 8 0 0 0 ${w} ${h - 8}V8A${w / 2} 8 0 0 0 0 8A${w / 2} 8 0 0 0 ${w} 8` : null;
    const route = (r, a, b, ty = .5) => {
      const [ax, ay, aw, ah] = a, [bx, by, bw, bh] = b, f = n => n.toFixed(1);
      if (r === "h" || r === "hs" || r === "ht") {
        const x1 = ax + aw, x2 = bx;
        let y1 = ay + ah / 2, y2 = by + bh * ty;
        if (r === "hs") y2 = y1;
        if (r === "ht") y1 = y2;
        if (Math.abs(y1 - y2) < 1) return `M${f(x1)} ${f(y1)}H${f(x2)}`;
        const xm = (x1 + x2) / 2;
        return `M${f(x1)} ${f(y1)}H${f(xm)}V${f(y2)}H${f(x2)}`;
      }
      if (r === "hv") return `M${f(ax + aw)} ${f(ay + ah / 2)}H${f(bx + bw / 2)}V${f(by + bh)}`;
      if (r === "vx") return `M${f(ax + aw / 2)} ${f(ay)}V${f(by + bh)}`;
      if (r === "vd") return `M${f(bx + bw / 2)} ${f(ay + ah)}V${f(by)}`;
      const up = r === "vu", x1 = ax + aw / 2, x2 = bx + bw / 2;
      const y1 = up ? ay : ay + ah, y2 = up ? by + bh : by;
      if (Math.abs(x1 - x2) < 1) return `M${f(x1)} ${f(y1)}V${f(y2)}`;
      const ym = (y1 + y2) / 2;
      return `M${f(x1)} ${f(y1)}V${f(ym)}H${f(x2)}V${f(y2)}`;
    };

    // one frame of the morph from level a to level b at progress k (0..1); texts switch at the middle
    const draw = (a, b, k) => {
      const [wa, ha] = d.frames[a], [wb, hb] = d.frames[b];
      svg.setAttribute("viewBox", `0 0 ${lerp(wa, wb, k).toFixed(1)} ${lerp(ha, hb, k).toFixed(1)}`);
      const lv = k < .5 ? a : b, now = {};
      for (const e of els) {
        const g0 = geo(e, a), g1 = geo(e, b);
        if (!g0 && !g1) { e.node.setAttribute("opacity", 0); continue; }
        const s = g0 || g1, t = g1 || g0;
        const [x, y, w, h] = [0, 1, 2, 3].map(i => lerp(s[i], t[i], k));
        const o = g0 && g1 ? lerp(g0[4], g1[4], k) : g1 ? g1[4] * Math.max(0, k * 2 - 1) : g0[4] * Math.max(0, 1 - k * 2);
        now[e.id] = [x, y, w, h, o];
        const n = e.node;
        n.setAttribute("transform", `translate(${x.toFixed(1)} ${y.toFixed(1)})`);
        n.setAttribute("opacity", o.toFixed(3));
        const sh = n.querySelector(".sh");
        if (sh) {
          const p = shape(e.k, w, h);
          if (p) sh.setAttribute("d", p); else { sh.setAttribute("width", w.toFixed(1)); sh.setAttribute("height", h.toFixed(1)); }
        }
        const tt = n.querySelector(".tt, .zl"), ss = n.querySelector(".ss"), title = e.t[lv - 1], sub = e.s[lv - 1];
        const top = e.xl === lv;                      // the panel of level 5: title top left, the list below
        if (tt.textContent !== title) tt.textContent = title;
        if (ss && ss.textContent !== sub) ss.textContent = sub;
        if (e.k !== "zone") {
          tt.setAttribute("text-anchor", top ? "start" : "middle");
          tt.setAttribute("class", top ? "s a tt" : (e.k === "chip" ? "s tt" : "t tt"));
          tt.setAttribute("x", top ? 10 : (w / 2).toFixed(1));
          tt.setAttribute("y", top ? 18 : (h / 2 + (sub ? -3 : 4)).toFixed(1));
          ss?.setAttribute("x", (w / 2).toFixed(1)); ss?.setAttribute("y", (h / 2 + 12).toFixed(1));
        }
        const x2 = n.querySelector(".lv-x");
        if (x2) x2.setAttribute("opacity", e.xl === b ? (e.xl === a ? 1 : Math.max(0, k * 2 - 1)) : e.xl === a ? Math.max(0, 1 - k * 2) : 0);
      }
      d.eds.forEach((ed, i) => {
        const p = paths[i], A = now[ed.a], B = now[ed.b];
        const inA = ed.lv.includes(a), inB = ed.lv.includes(b);
        if (!A || !B || (!inA && !inB)) { p.setAttribute("opacity", 0); return; }
        const v = inA && inB ? 1 : inB ? Math.max(0, k * 2 - 1) : Math.max(0, 1 - k * 2);
        p.setAttribute("d", route(ed.r, A, B, ed.ty ?? .5));
        p.setAttribute("opacity", (v * Math.min(A[4], B[4])).toFixed(3));
      });
    };

    const buttons = [...fig.querySelectorAll(".lv-b")], where = fig.querySelector(".where");
    const prev = fig.querySelector(".lv-prev"), next = fig.querySelector(".lv-next");
    let cur = d.start, anim = 0;
    const set = l => {
      press(buttons, buttons[L.indexOf(l)]);
      prev.disabled = l === L[0]; next.disabled = l === L[L.length - 1];
      where.innerHTML = `<span>${d.words[l]}</span>`;
    };
    // the flow: dots run along the arrows of the current level in a wave from left to right — the models
    // go in, the code comes out. Only while the figure is on screen and no level change is under way.
    const NS = "http://www.w3.org/2000/svg", flowG = document.createElementNS(NS, "g");
    flowG.setAttribute("class", "lv-flow");
    svg.querySelector(".lv-edges").after(flowG);
    const dots = paths.map(() => {
      const c = document.createElementNS(NS, "circle");
      c.setAttribute("r", 3.8); c.setAttribute("opacity", 0); c.setAttribute("cx", -20); c.setAttribute("cy", -20);   // hidden until the first frame
      flowG.appendChild(c); return c;
    });
    let flowing = false, flowRaf = 0, t0f = 0;
    const WAVE = 2600, RUN = 700, REST = 900;              // ms: the wave crosses the frame, one dot runs, pause
    const flow = t => {
      const w = d.frames[cur][0], k = (t - t0f) % (WAVE + RUN + REST);
      d.eds.forEach((ed, i) => {
        const p = paths[i], c = dots[i], o = +p.getAttribute("opacity");
        if (!ed.lv.includes(cur) || o < .05) { c.setAttribute("opacity", 0); return; }
        const box = byId[ed.a].g[cur], start = (box[0] + box[2]) / w * WAVE, q = (k - start) / RUN;
        if (q < 0 || q > 1) { c.setAttribute("opacity", 0); return; }
        const len = p.getTotalLength(), pt = p.getPointAtLength(len * q);
        c.setAttribute("cx", pt.x.toFixed(1)); c.setAttribute("cy", pt.y.toFixed(1));
        c.setAttribute("opacity", (o * Math.sin(Math.PI * q)).toFixed(3));
      });
      flowRaf = requestAnimationFrame(flow);
    };
    const flowOn = on => {
      if (reduce || on === flowing) return;
      flowing = on; cancelAnimationFrame(flowRaf);
      if (on) { t0f = performance.now(); flowRaf = requestAnimationFrame(flow); }
      else dots.forEach(c => c.setAttribute("opacity", 0));
    };
    let seen = false;
    if ("IntersectionObserver" in window)
      new IntersectionObserver(([e]) => { seen = e.isIntersecting; flowOn(seen); }, { threshold: .25 }).observe(svg);

    const go = to => {
      if (!L.includes(to) || to === cur) return;
      cancelAnimationFrame(anim); flowOn(false);
      const from = cur; cur = to; set(to);
      if (reduce) return draw(from, to, 1);
      const t0 = performance.now(), dur = 900;
      const step = t => {
        const k = Math.min(1, (t - t0) / dur), e = k < .5 ? 4 * k * k * k : 1 - (-2 * k + 2) ** 3 / 2;
        draw(from, to, e);
        if (k < 1) anim = requestAnimationFrame(step); else if (seen) flowOn(true);
      };
      anim = requestAnimationFrame(step);
    };
    buttons.forEach((b, i) => b.addEventListener("click", () => go(L[i])));
    prev.addEventListener("click", () => go(L[L.indexOf(cur) - 1]));
    next.addEventListener("click", () => go(L[L.indexOf(cur) + 1]));
    draw(cur, cur, 1); set(cur);
    // height lock (STYLE.md): the viewBox morphs, so reserve the tallest level's height below the controls
    const lockH = () => {
      const W = svg.getBoundingClientRect().width; if (!W) return;
      const box = svg.parentElement;                      // a smaller level sits in the middle of the reserved height
      box.style.minHeight = `${Math.ceil(Math.max(...L.map(l => W * d.frames[l][1] / d.frames[l][0])))}px`;
      box.style.display = "flex"; box.style.flexDirection = "column"; box.style.justifyContent = "center";
    };
    lockH();
    if ("ResizeObserver" in window) { let w0 = 0; new ResizeObserver(() => { const w = svg.getBoundingClientRect().width; if (Math.abs(w - w0) > 1) { w0 = w; lockH(); } }).observe(svg.parentElement); }
  }

  document.querySelectorAll("figure.f2-fig[data-read]").forEach(fig => { try { readAloud(fig); } catch (e) { console.error(e); } });
  const kinds = { d0: levels, d1: syntax, d2: top, d3: files, d4: cd2gui, mm: mailmerge };
  document.querySelectorAll("figure.demo[data-demo]").forEach(fig => {
    try { kinds[fig.dataset.demo]?.(fig); } catch (e) { console.error(e); }
  });
})();
