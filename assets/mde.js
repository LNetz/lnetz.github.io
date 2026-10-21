// Interactive figures of the MDE article (research-mde.html, built by _build/mde.py + mde_figs.py).
// All states are precomputed at build time and shipped as data-json; this script only swaps and highlights.
//   d1 — one model, two notations, three gates (presets; hover a line ↔ diagram)
//   d2 — edit the generated file, or extend it (TOP mechanism; stepper, plays once when seen)
//   d3 — one line in the model, six files change (+ attribute, file chips, code | template)
//   d4 — CD2GUI: pages nobody drew (class picker, dashboard / overview / details, hand-written delta)
(() => {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const json = fig => JSON.parse(fig.dataset.json);
  const press = (buttons, on) => buttons.forEach(b => b.setAttribute("aria-pressed", String(b === on)));
  const whenSeen = (el, fn) => {
    if (!("IntersectionObserver" in window)) return fn();
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { io.disconnect(); fn(); } }, { threshold: .4 });
    io.observe(el);
  };

  // ---------------- a stepper: play button, step slider, label (as in ai4se.js) ----------------
  function stepper(fig, count, render, delay) {
    const play = fig.querySelector(".play"), range = fig.querySelector("input.step"), words = json(fig).words;
    let k = 0, timer = null;
    range.max = count - 1;
    const show = i => { k = i; range.value = i; render(i); };
    const stop = () => { clearTimeout(timer); timer = null; play.textContent = k >= count - 1 ? "↺" : "▶"; play.setAttribute("aria-label", words.play); };
    const tick = () => { if (k >= count - 1) return stop(); show(k + 1); timer = setTimeout(tick, delay); };
    const start = () => { if (k >= count - 1) show(0); play.textContent = "❚❚"; play.setAttribute("aria-label", words.pause); timer = setTimeout(tick, delay); };
    play.addEventListener("click", () => (timer ? stop() : start()));
    range.addEventListener("input", () => { stop(); show(+range.value); stop(); });
    show(0); stop();
    return { start };
  }

  // ---------------- d1: syntax and the three gates ----------------
  function syntax(fig) {
    const { variants } = json(fig);
    const code = fig.querySelector(".d1-code"), msg = fig.querySelector(".d1-msg");
    const gates = [...fig.querySelectorAll(".gate")], umls = [...fig.querySelectorAll(".d1-uml")];
    const buttons = [...fig.querySelectorAll(".d1-presets button")];
    const set = i => {
      const v = variants[i];
      press(buttons, buttons[i]);
      code.innerHTML = v.code;
      gates.forEach((g, k) => { g.className = "gate " + (v.gates[k] === 1 ? "ok" : v.gates[k] === 0 ? "fail" : "skip"); });
      umls.forEach(u => { u.hidden = u.dataset.uml !== v.uml; });
      msg.textContent = v.msg;
    };
    buttons.forEach((b, i) => b.addEventListener("click", () => set(i)));
    // pointing at a line lights up its element in the diagram, and the other way round
    const light = k => {
      code.querySelectorAll(".l").forEach(l => l.classList.toggle("hi", !!k && l.dataset.k === k));
      fig.querySelectorAll(".d1-uml g[data-k]").forEach(g => g.classList.toggle("hi", !!k && g.dataset.k === k));
    };
    code.addEventListener("pointerover", e => light(e.target.closest(".l")?.dataset.k));
    code.addEventListener("pointerleave", () => light(null));
    fig.querySelectorAll(".d1-uml g[data-k]").forEach(g => {
      g.addEventListener("pointerenter", () => light(g.dataset.k));
      g.addEventListener("pointerleave", () => light(null));
    });
  }

  // ---------------- d2: the TOP mechanism ----------------
  function top(fig) {
    const { steps, words } = json(fig);
    const lanes = { a: fig.querySelector('[data-lane="a"]'), b: fig.querySelector('[data-lane="b"]') };
    const where = fig.querySelector(".where");
    const render = i => {
      const s = steps[i];
      for (const l of ["a", "b"]) {
        lanes[l].querySelector(".d2-files").innerHTML = s[l];
        const note = lanes[l].querySelector(".d2-note");
        note.textContent = s[l + "n"];
        note.className = "d2-note mono " + (s[l + "c"] || "");
      }
      where.textContent = `${words.step} ${i + 1} ${words.of} ${steps.length} · ${s.title}`;
    };
    const st = stepper(fig, steps.length, render, 2600);
    if (!reduce) whenSeen(fig, st.start);
  }

  // ---------------- d3: one line, six files ----------------
  function files(fig) {
    const { states, templates, words } = json(fig);
    const model = fig.querySelector(".d3-model pre"), count = fig.querySelector(".d3-count");
    const out = fig.querySelector(".d3-code"), form = fig.querySelector(".d3-form-wrap"), note = fig.querySelector(".d3-tplnote");
    const chips = [...fig.querySelectorAll(".d3-chip")], views = [...fig.querySelectorAll(".d3-view button")];
    const add = fig.querySelector(".d3-add");
    let k = 0, file = "data", view = "code";
    const render = () => {
      const s = states[k];
      model.innerHTML = s.model;
      chips.forEach(c => {
        const n = k ? s.changed[c.dataset.f] : 0;
        c.querySelector(".d3-badge").textContent = n ? `+${n}` : "";
        c.classList.toggle("touched", n > 0);
      });
      press(chips, chips.find(c => c.dataset.f === file));
      press(views, views.find(v => v.dataset.view === view));
      const tpl = view === "template";
      out.innerHTML = tpl ? templates[file] : s.files[file];
      out.classList.toggle("tpl", tpl);
      form.hidden = tpl || file !== "form";
      if (!form.hidden) form.innerHTML = s.form;
      note.hidden = !tpl;
      note.textContent = words.tpl;
      count.textContent = k ? words.count.replace("{n}", s.n).replace("{m}", s.m) : words.start;
      add.disabled = k >= states.length - 1;
      add.classList.toggle("hint", k === 0);
    };
    add.addEventListener("click", () => { if (k < states.length - 1) { k++; render(); if (k === states.length - 1) count.textContent += " · " + words.full; } });
    fig.querySelector(".d3-reset").addEventListener("click", () => { k = 0; render(); });
    chips.forEach(c => c.addEventListener("click", () => { file = c.dataset.f; render(); }));
    views.forEach(v => v.addEventListener("click", () => { view = v.dataset.view; render(); }));
    render();
  }

  // ---------------- d4: CD2GUI ----------------
  function cd2gui(fig) {
    const { pages } = json(fig);
    const url = fig.querySelector(".d4-url"), page = fig.querySelector(".d4-page"), tree = fig.querySelector(".d4-tree-wrap");
    const tabs = [...fig.querySelectorAll(".d4-tabs button")], classes = [...fig.querySelectorAll(".d4-cls")];
    const delta = fig.querySelector(".d4-delta input"), deltaCode = fig.querySelector(".d4-deltacode");
    let cls = null, tab = "dashboard";
    const render = () => {
      const canDelta = cls === "Accountant" && tab === "details";
      delta.disabled = !canDelta;
      if (!canDelta) delta.checked = false;
      deltaCode.hidden = !delta.checked;
      const key = tab === "dashboard" ? "dashboard" : `${cls}/${tab}${delta.checked ? "+delta" : ""}`;
      const p = pages[key];
      url.textContent = p.url;
      page.innerHTML = p.html;
      tree.innerHTML = p.tree;
      press(tabs, tabs.find(t => t.dataset.t === tab));
      tabs.forEach(t => { if (t.dataset.t !== "dashboard") t.disabled = !cls; });
      classes.forEach(g => { g.classList.toggle("on", g.dataset.c === cls); g.setAttribute("aria-pressed", String(g.dataset.c === cls)); });
    };
    const pick = c => { cls = c; if (tab === "dashboard") tab = "details"; render(); };
    classes.forEach(g => {
      g.addEventListener("click", () => pick(g.dataset.c));
      g.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(g.dataset.c); } });
    });
    tabs.forEach(t => t.addEventListener("click", () => { tab = t.dataset.t; render(); }));
    delta.addEventListener("change", render);
    render();
  }

  // ---------------- the city map: one crosshair marks the same place in every map ----------------
  // Original, road map and hiking map share the city's geography; the metro map does not — there the
  // crosshair can only snap to the nearest station (and pointing at the metro map snaps the others to it).
  function citymap(svg) {
    const d = JSON.parse(svg.dataset.map);
    const parts = [...svg.querySelectorAll(".mp")].map(g => ({ k: +g.dataset.k, x: +g.dataset.x, y: +g.dataset.y, g: g.querySelector(".xh") }));
    const W = d.w, H = d.h, S = d.s;
    const heightAt = (x, y) => {            // bilinear on the precomputed grid
      const i = Math.min(x / d.step, d.heights[0].length - 1.001), j = Math.min(y / d.step, d.heights.length - 1.001);
      const i0 = Math.floor(i), j0 = Math.floor(j), fi = i - i0, fj = j - j0, h = d.heights;
      return (h[j0][i0] * (1 - fi) + h[j0][i0 + 1] * fi) * (1 - fj) + (h[j0 + 1][i0] * (1 - fi) + h[j0 + 1][i0 + 1] * fi) * fj;
    };
    const nearest = (pts, x, y) => Object.keys(pts).reduce((a, k) => (Math.hypot(pts[k][0] - x, pts[k][1] - y) < Math.hypot(pts[a][0] - x, pts[a][1] - y) ? k : a));
    const put = (p, x, y, label) => {
      const [v, h, c, t] = p.g.children;
      v.setAttribute("x1", x); v.setAttribute("x2", x);
      h.setAttribute("y1", y); h.setAttribute("y2", y);
      c.setAttribute("cx", x); c.setAttribute("cy", y);
      const right = x > W - 70, below = y < 22;
      t.setAttribute("x", right ? x - 6 : x + 6); t.setAttribute("y", below ? y + 12 : y - 6);
      t.setAttribute("text-anchor", right ? "end" : "start");
      t.textContent = label;
    };
    const show = (x, y) => {
      const st = nearest(d.geo, x, y);
      for (const p of parts) {
        if (p.k === 1) { const [mx, my] = d.metro[st]; put(p, mx, my, `→ ${d.names[st]}`); }
        else put(p, x, y, p.k === 3 ? `≈ ${Math.round(heightAt(x, y))} ${d.m}` : `${Math.round(x)} · ${Math.round(y)}`);
      }
      svg.classList.add("live");
    };
    const move = e => {
      const pt = svg.createSVGPoint();
      pt.x = e.clientX; pt.y = e.clientY;
      const q = pt.matrixTransform(svg.getScreenCTM().inverse());
      const p = parts.find(p => q.x >= p.x && q.x <= p.x + W * S && q.y >= p.y && q.y <= p.y + H * S);
      if (!p) return svg.classList.remove("live");
      let x = (q.x - p.x) / S, y = (q.y - p.y) / S;
      if (p.k === 1) { const st = nearest(d.metro, x, y); [x, y] = d.geo[st]; }    // the metro map has no geography
      show(x, y);
    };
    svg.addEventListener("pointermove", move);
    svg.addEventListener("pointerdown", move);
    svg.addEventListener("pointerleave", () => svg.classList.remove("live"));
  }
  document.querySelectorAll("svg.citymap[data-map]").forEach(svg => { try { citymap(svg); } catch (e) { console.error(e); } });

  // ---------------- d0: the generator, five levels deep (_build/mde_levels.py) ----------------
  // Every level has its own frame of the same shape, so the figure keeps its height; boxes move and grow,
  // what is new fades in after the move has begun, what goes fades out first. Geometry rules as in the Python.
  function levels(fig) {
    const d = json(fig), svg = fig.querySelector("svg"), N = 5;
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
    let cur = 1, anim = 0;
    const set = l => {
      press(buttons, buttons[l - 1]);
      prev.disabled = l === 1; next.disabled = l === N;
      where.innerHTML = `<span>${d.words[l - 1]}</span>`;
    };
    // the flow: dots run along the arrows of the current level in a wave from left to right — the models
    // go in, the code comes out. Only while the figure is on screen and no level change is under way.
    const NS = "http://www.w3.org/2000/svg", flowG = document.createElementNS(NS, "g");
    flowG.setAttribute("class", "lv-flow");
    svg.querySelector(".lv-edges").after(flowG);
    const dots = paths.map(() => { const c = document.createElementNS(NS, "circle"); c.setAttribute("r", 3.8); flowG.appendChild(c); return c; });
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
      if (to < 1 || to > N || to === cur) return;
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
    buttons.forEach((b, i) => b.addEventListener("click", () => go(i + 1)));
    prev.addEventListener("click", () => go(cur - 1));
    next.addEventListener("click", () => go(cur + 1));
    draw(1, 1, 1); set(1);
  }

  const kinds = { d0: levels, d1: syntax, d2: top, d3: files, d4: cd2gui };
  document.querySelectorAll("figure.demo[data-demo]").forEach(fig => {
    try { kinds[fig.dataset.demo]?.(fig); } catch (e) { console.error(e); }
  });
})();
